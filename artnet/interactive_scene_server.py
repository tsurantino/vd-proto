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
    """Main rendering loop @ 60 FPS"""
    logger.info("🎬 Starting render loop...")

    target_fps = 60
    frame_time = 1.0 / target_fps
    state.start_time = time.time()
    last_stats_time = time.time()
    last_frame_count = 0

    # Timing instrumentation
    timing_samples = []

    while state.is_running:
        loop_start = time.time()
        current_time = time.time() - state.start_time

        timings = {}

        # Render scene
        t0 = time.perf_counter()
        with state.lock:
            if state.scene and state.world_raster:
                try:
                    state.scene.render(state.world_raster, current_time)
                except Exception as e:
                    logger.error(f"Error rendering scene: {e}", exc_info=True)
        timings['render'] = (time.perf_counter() - t0) * 1000

        # Send to ArtNet
        t0 = time.perf_counter()
        try:
            artnet_timings = send_to_artnet()
            timings['artnet'] = (time.perf_counter() - t0) * 1000
            # Merge detailed ArtNet timings
            if artnet_timings:
                timings.update(artnet_timings)
        except Exception as e:
            logger.error(f"Error sending to ArtNet: {e}", exc_info=True)
            timings['artnet'] = (time.perf_counter() - t0) * 1000

        timing_samples.append(timings)

        # Update stats every second
        state.frame_count += 1
        now = time.time()
        if now - last_stats_time >= 1.0:
            frames_delta = state.frame_count - last_frame_count
            fps = frames_delta / (now - last_stats_time)
            avg_frame_time = (now - last_stats_time) / frames_delta * 1000 if frames_delta > 0 else 0

            # Calculate average timings
            if timing_samples:
                avg_render = sum(t.get('render', 0) for t in timing_samples) / len(timing_samples)
                avg_artnet = sum(t.get('artnet', 0) for t in timing_samples) / len(timing_samples)
                avg_slice = sum(t.get('slice_transform', 0) for t in timing_samples) / len(timing_samples)
                avg_submit = sum(t.get('submit_jobs', 0) for t in timing_samples) / len(timing_samples)
                avg_rgb = sum(t.get('rgb_conversion', 0) for t in timing_samples) / len(timing_samples)
                avg_udp = sum(t.get('udp_send', 0) for t in timing_samples) / len(timing_samples)
                # Detailed UDP breakdown
                avg_udp_copy = sum(t.get('udp_job_copy', 0) for t in timing_samples) / len(timing_samples)
                avg_udp_dmx = sum(t.get('udp_job_dmx', 0) for t in timing_samples) / len(timing_samples)
                avg_udp_job = sum(t.get('udp_job_total', 0) for t in timing_samples) / len(timing_samples)
                timing_samples.clear()
            else:
                avg_render = avg_artnet = avg_slice = avg_submit = avg_rgb = avg_udp = 0
                avg_udp_copy = avg_udp_dmx = avg_udp_job = 0

            with state.lock:
                state.fps_stats = {
                    'fps': round(fps, 1),
                    'active_leds': count_active_leds(state.world_raster),
                    'frame_time_ms': round(avg_frame_time, 2)
                }

            socketio.emit('stats', state.fps_stats)
            logger.info(f"📊 FPS: {fps:.1f} | Frame: {avg_frame_time:.2f}ms | Render: {avg_render:.2f}ms | ArtNet: {avg_artnet:.2f}ms (Slice: {avg_slice:.2f}ms, RGB: {avg_rgb:.2f}ms, UDP: {avg_udp:.2f}ms [Copy={avg_udp_copy:.2f}ms DMX={avg_udp_dmx:.2f}ms Total={avg_udp_job:.2f}ms]) | LEDs: {state.fps_stats['active_leds']:,}")

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
    """Send world raster to ArtNet (using parallel RGB conversion)"""
    if not state.artnet_manager or not state.world_raster:
        return {}

    import dataclasses
    from artnet import RGB

    timings = {}
    world_data = state.world_raster.data
    min_coord = (0, 0, 0)

    # Process each cube only once (track which cubes we've processed)
    processed_cubes = set()
    conversion_cache = {}

    # First pass: slice and transform cube data
    t0 = time.perf_counter()
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
    timings['slice_transform'] = (time.perf_counter() - t0) * 1000

    # Second pass: parallel RGB conversion for unique rasters
    t0 = time.perf_counter()
    unique_rasters = {}
    for job in state.artnet_manager.send_jobs:
        cube_raster = job["cube_raster"]
        raster_id = id(cube_raster)
        if raster_id not in conversion_cache and raster_id not in unique_rasters:
            unique_rasters[raster_id] = cube_raster

    # Submit all cube conversions in parallel (one cube per worker)
    # We have 4 cubes and 5 workers, so we get good parallelization
    if unique_rasters:
        futures = {}
        for raster_id, cube_raster in unique_rasters.items():
            # Get raw bytes directly from NumPy array (zero-copy with tobytes())
            numpy_data = cube_raster.data.reshape(-1, 3)
            num_pixels = len(numpy_data)

            # Submit entire cube to one worker process
            # Pass raw bytes to avoid NumPy import in worker
            future = state.conversion_executor.submit(
                convert_cube_to_rgb_tuples,
                numpy_data.tobytes(),
                num_pixels
            )
            futures[raster_id] = future
    timings['submit_jobs'] = (time.perf_counter() - t0) * 1000

    # Collect results and convert tuples to RGB objects
    # This tuple→RGB step MUST happen on main thread (RGB objects aren't picklable)
    t0 = time.perf_counter()
    if unique_rasters:
        for raster_id, future in futures.items():
            rgb_tuples = future.result()  # Get all tuples for this cube

            # Check if we have cached RGB list for this raster
            if raster_id in state.rgb_cache:
                # Reuse existing RGB list, just update values
                rgb_list = state.rgb_cache[raster_id]
                for i, (r, g, b) in enumerate(rgb_tuples):
                    rgb_list[i] = RGB(r, g, b)
            else:
                # Create new RGB objects and cache the list
                rgb_list = [RGB(r, g, b) for r, g, b in rgb_tuples]
                state.rgb_cache[raster_id] = rgb_list

            conversion_cache[raster_id] = rgb_list
    timings['rgb_conversion'] = (time.perf_counter() - t0) * 1000

    # Third pass: send to ArtNet controllers (sequential)
    t0_total = time.perf_counter()

    job_timings = []
    for job in state.artnet_manager.send_jobs:
        t_job_start = time.perf_counter()

        cube_raster = job["cube_raster"]
        raster_id = id(cube_raster)

        t_copy = time.perf_counter()
        temp_raster = dataclasses.replace(cube_raster)
        temp_raster.data = conversion_cache[raster_id]
        copy_time = (time.perf_counter() - t_copy) * 1000

        controller = job["controller"]
        z_indices = job["z_indices"]
        universes_per_layer = 3
        base_universe_offset = min(z_indices) * universes_per_layer

        t_dmx = time.perf_counter()
        try:
            controller.send_dmx(
                base_universe=base_universe_offset,
                raster=temp_raster,
                z_indices=z_indices,
                channels_per_universe=510,
                universes_per_layer=universes_per_layer,
                channel_span=1,
            )
        except Exception as e:
            logger.error(f"Error sending DMX: {e}", exc_info=True)
        dmx_time = (time.perf_counter() - t_dmx) * 1000

        job_time = (time.perf_counter() - t_job_start) * 1000
        job_timings.append({'copy': copy_time, 'dmx': dmx_time, 'total': job_time})

    # Calculate averages
    if job_timings:
        avg_copy = sum(r['copy'] for r in job_timings) / len(job_timings)
        avg_dmx = sum(r['dmx'] for r in job_timings) / len(job_timings)
        avg_job = sum(r['total'] for r in job_timings) / len(job_timings)
    else:
        avg_copy = avg_dmx = avg_job = 0

    total_udp_time = (time.perf_counter() - t0_total) * 1000

    timings['udp_send'] = total_udp_time
    timings['udp_job_copy'] = avg_copy
    timings['udp_job_dmx'] = avg_dmx
    timings['udp_job_total'] = avg_job

    return timings


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
