"""
Interactive Scene Server
Runs Python scene computation with real-time parameter updates from web UI
Uses existing sender.py infrastructure for ArtNet output
"""

import argparse
import json
import logging
import time
from threading import Thread, Lock
from concurrent.futures import ProcessPoolExecutor
from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import numpy as np

from artnet import DisplayProperties, Raster
from sender import ArtNetManager, apply_orientation_transform
from interactive_web_scene import InteractiveWebScene

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../web', static_url_path='')
app.config['SECRET_KEY'] = 'interactive-scene-server'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


class ServerState:
    def __init__(self, num_workers=None):
        self.lock = Lock()
        self.scene = None
        self.artnet_manager = None
        self.world_raster = None
        self.config = None
        self.is_running = False
        self.fps_stats = {'fps': 0, 'active_leds': 0, 'frame_time_ms': 0}
        self.frame_count = 0
        self.start_time = None

        # Worker count optimization
        # Testing shows 5 workers is optimal for this workload:
        # - 4 workers: 37.1 FPS (27.0ms/frame)
        # - 5 workers: 38.0 FPS (26.3ms/frame) ✅ BEST
        # - 6 workers: 34.7 FPS (28.8ms/frame)
        # More workers = more IPC overhead, diminishing returns
        import os
        default_workers = 5  # Empirically tested optimal value
        self.num_workers = num_workers or default_workers

        self.conversion_executor = ProcessPoolExecutor(max_workers=self.num_workers)
        self.rgb_cache = {}  # Cache RGB lists (reuse list slots for speed)


state = ServerState()


@app.route('/')
def index():
    """Serve the web UI"""
    return send_from_directory('../web', 'controller.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status"""
    with state.lock:
        return jsonify({
            'connected': state.is_running,
            'config': {
                'gridX': state.world_raster.width if state.world_raster else 0,
                'gridY': state.world_raster.height if state.world_raster else 0,
                'gridZ': state.world_raster.length if state.world_raster else 0,
                'cubes': len(state.config.get('cubes', [])) if state.config else 0
            },
            'stats': state.fps_stats
        })


@socketio.on('connect')
def handle_connect():
    """Client connected"""
    logger.info("🌐 Web UI connected")
    with state.lock:
        emit('status', {
            'connected': state.is_running,
            'config': {
                'gridX': state.world_raster.width if state.world_raster else 0,
                'gridY': state.world_raster.height if state.world_raster else 0,
                'gridZ': state.world_raster.length if state.world_raster else 0
            }
        })


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    logger.info("🌐 Web UI disconnected")


@socketio.on('update_params')
def handle_update_params(data):
    """Update scene parameters from web UI

    Expected data:
    {
        'scene_type': 'shapeMorph',
        'size': 1.5,
        'density': 0.8,
        ...
    }
    """
    with state.lock:
        if state.scene:
            state.scene.update_parameters(data)
            logger.debug(f"Updated params: scene={data.get('scene_type')}")


def render_loop():
    """Main rendering loop @ 80 FPS"""
    logger.info("🎬 Starting render loop...")

    target_fps = 80
    frame_time = 1.0 / target_fps
    state.start_time = time.time()
    last_stats_time = time.time()
    last_frame_count = 0

    while state.is_running:
        loop_start = time.time()
        current_time = time.time() - state.start_time

        # Render scene
        with state.lock:
            if state.scene and state.world_raster:
                try:
                    state.scene.render(state.world_raster, current_time)
                except Exception as e:
                    logger.error(f"Error rendering scene: {e}", exc_info=True)

        # Send to ArtNet
        try:
            send_to_artnet()
        except Exception as e:
            logger.error(f"Error sending to ArtNet: {e}", exc_info=True)

        # Update stats every second
        state.frame_count += 1
        now = time.time()
        if now - last_stats_time >= 1.0:
            frames_delta = state.frame_count - last_frame_count
            fps = frames_delta / (now - last_stats_time)
            avg_frame_time = (now - last_stats_time) / frames_delta * 1000 if frames_delta > 0 else 0

            with state.lock:
                state.fps_stats = {
                    'fps': round(fps, 1),
                    'active_leds': count_active_leds(state.world_raster),
                    'frame_time_ms': round(avg_frame_time, 2)
                }

            socketio.emit('stats', state.fps_stats)
            logger.info(f"📊 FPS: {fps:.1f} | Frame: {avg_frame_time:.2f}ms | LEDs: {state.fps_stats['active_leds']:,}")

            last_stats_time = now
            last_frame_count = state.frame_count

        # Sleep to maintain target FPS
        elapsed = time.time() - loop_start
        sleep_time = max(0, frame_time - elapsed)
        time.sleep(sleep_time)

    logger.info("🛑 Render loop stopped")


def convert_cube_to_rgb_tuples(data_bytes, num_pixels):
    """Convert cube bytes directly to RGB tuples (multiprocess worker)

    This runs in a separate process to bypass Python's GIL.
    Avoids NumPy entirely for maximum speed.

    Args:
        data_bytes: Raw bytes (r, g, b, r, g, b, ...)
        num_pixels: Number of pixels (bytes / 3)

    Returns:
        List of (r, g, b) tuples for entire cube

    Note: Returns tuples instead of RGB objects because RGB objects from
    the Rust library cannot be pickled across process boundaries.
    """
    # Use memoryview for zero-copy access to bytes
    mem = memoryview(data_bytes)

    # Process 3 bytes at a time directly, no NumPy overhead
    result = []
    for i in range(0, len(mem), 3):
        result.append((mem[i], mem[i+1], mem[i+2]))

    return result


def send_to_artnet():
    """Send world raster to ArtNet (using send_dmx_bytes - no RGB object conversion!)"""
    if not state.artnet_manager or not state.world_raster:
        return

    world_data = state.world_raster.data
    min_coord = (0, 0, 0)

    # Process each cube only once (track which cubes we've processed)
    processed_cubes = set()

    # First pass: slice and transform cube data
    for job in state.artnet_manager.send_jobs:
        cube_pos_tuple = tuple(job["cube_position"])

        if cube_pos_tuple not in processed_cubes:
            cube_position = (
                job["cube_position"][0] - min_coord[0],
                job["cube_position"][1] - min_coord[1],
                job["cube_position"][2] - min_coord[2],
            )

            cube_raster = job["cube_raster"]
            cube_dimensions = (cube_raster.width, cube_raster.height, cube_raster.length)

            cube_orientation = state.artnet_manager.cube_orientations.get(
                cube_pos_tuple, ["X", "Y", "Z"]
            )

            transformed_slice = apply_orientation_transform(
                world_data, cube_position, cube_dimensions, cube_orientation
            )

            cube_raster.data[:] = transformed_slice
            processed_cubes.add(cube_pos_tuple)

    # Second pass: send to ArtNet controllers directly with raw bytes
    for job in state.artnet_manager.send_jobs:
        cube_raster = job["cube_raster"]
        controller = job["controller"]
        z_indices = job["z_indices"]
        universes_per_layer = 3
        base_universe_offset = min(z_indices) * universes_per_layer

        # Get raw bytes directly from NumPy array (C-contiguous, zero-copy)
        pixel_bytes = cube_raster.data.tobytes()

        try:
            # Use new send_dmx_bytes method - passes bytes directly to Rust!
            controller.send_dmx_bytes(
                base_universe=base_universe_offset,
                pixel_bytes=pixel_bytes,
                width=cube_raster.width,
                height=cube_raster.height,
                length=cube_raster.length,
                brightness=1.0,
                channels_per_universe=510,
                universes_per_layer=universes_per_layer,
                channel_span=1,
                z_indices=z_indices,
            )
        except Exception as e:
            logger.error(f"Error sending DMX bytes: {e}", exc_info=True)


def count_active_leds(raster):
    """Count non-black voxels"""
    if raster is None:
        return 0
    return int(np.sum(np.any(raster.data > 0, axis=-1)))


def main():
    parser = argparse.ArgumentParser(description='Interactive Scene Server')
    parser.add_argument('--config', required=True, help='Config JSON file (e.g., sim_config_4.json)')
    parser.add_argument('--port', type=int, default=5001, help='Server port')
    parser.add_argument('--workers', type=int, default=None, help='Number of parallel workers (default: CPU count - 2)')
    args = parser.parse_args()

    # Initialize state with worker count
    global state
    state = ServerState(num_workers=args.workers)

    logger.info("="*60)
    logger.info("🚀 Interactive Scene Server")
    logger.info("="*60)
    logger.info(f"⚙️  Using {state.num_workers} parallel workers for RGB conversion")

    # Load config
    logger.info(f"📄 Loading config: {args.config}")
    with open(args.config) as f:
        config = json.load(f)

    state.config = config

    # Create world raster
    width, height, length = map(int, config['world_geometry'].split('x'))
    logger.info(f"🌍 World grid: {width}×{height}×{length}")
    state.world_raster = Raster(width, height, length)

    # Create ArtNet manager
    logger.info("🎛️  Initializing ArtNet manager...")
    state.artnet_manager = ArtNetManager(config)

    # Create interactive scene
    properties = DisplayProperties(width, height, length)
    state.scene = InteractiveWebScene(properties=properties)

    state.is_running = True

    # Start render loop in background thread
    render_thread = Thread(target=render_loop, daemon=True)
    render_thread.start()

    logger.info("="*60)
    logger.info(f"✨ Server running on http://localhost:{args.port}")
    logger.info(f"🎮 Open browser to http://localhost:{args.port}")
    logger.info("="*60)

    # Run Flask server
    try:
        socketio.run(app, host='0.0.0.0', port=args.port, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        state.is_running = False
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        state.is_running = False
    finally:
        # Shutdown process pool
        state.conversion_executor.shutdown(wait=True)
        logger.info("✅ Cleanup complete")


if __name__ == '__main__':
    main()
