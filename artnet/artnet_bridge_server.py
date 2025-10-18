"""
ArtNet Bridge Server
Bridges web UI to ArtNet volumetric display via WebSocket/HTTP interface
"""

import argparse
import json
import logging
import time
from threading import Thread, Lock
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from artnet import RGB, ArtNetController, DisplayProperties, Raster, Scene
from sender import ArtNetManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'volumetric-display-secret'
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
class BridgeState:
    def __init__(self):
        self.lock = Lock()
        self.connected_clients = 0
        self.is_running = False
        self.artnet_manager = None
        self.config = None
        self.world_raster = None
        self.fps_stats = {'fps': 0, 'frame_time_ms': 0, 'active_leds': 0}
        self.frames_received = 0
        self.last_frame_time = 0

bridge_state = BridgeState()

# ============================================================================
# HTTP API Endpoints
# ============================================================================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get bridge server status"""
    with bridge_state.lock:
        return jsonify({
            'connected': bridge_state.is_running,
            'clients': bridge_state.connected_clients,
            'config': {
                'gridX': bridge_state.config.get('world_geometry', '40x20x40').split('x')[0] if bridge_state.config else 0,
                'gridY': bridge_state.config.get('world_geometry', '40x20x40').split('x')[1] if bridge_state.config else 0,
                'gridZ': bridge_state.config.get('world_geometry', '40x20x40').split('x')[2] if bridge_state.config else 0,
                'cubes': len(bridge_state.config.get('cubes', [])) if bridge_state.config else 0
            },
            'stats': bridge_state.fps_stats
        })


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    bridge_state.connected_clients += 1
    logger.info(f"Client connected. Total clients: {bridge_state.connected_clients}")

    # Send status to new client
    with bridge_state.lock:
        emit('status', {
            'connected': bridge_state.is_running,
            'stats': bridge_state.fps_stats
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    bridge_state.connected_clients -= 1
    logger.info(f"Client disconnected. Total clients: {bridge_state.connected_clients}")

@socketio.on('frame')
def handle_frame(data):
    """Handle incoming pixel frame from web UI

    Expected data format:
    {
        'pixels': <base64 encoded binary data or array>,
        'width': int,
        'height': int,
        'length': int
    }
    """
    try:
        import numpy as np
        import base64

        # Decode pixel data
        if isinstance(data.get('pixels'), str):
            # Base64 encoded binary
            pixel_bytes = base64.b64decode(data['pixels'])
            pixels = np.frombuffer(pixel_bytes, dtype=np.uint8)
        else:
            # Direct array
            pixels = np.array(data['pixels'], dtype=np.uint8)

        width = data['width']
        height = data['height']
        length = data['length']

        # Reshape to (Z, Y, X, RGB)
        pixels = pixels.reshape((length, height, width, 3))

        # Update world raster
        with bridge_state.lock:
            if bridge_state.world_raster:
                bridge_state.world_raster.data[:] = pixels
                bridge_state.frames_received += 1
                bridge_state.last_frame_time = time.time()

        # Send to ArtNet immediately
        send_to_artnet(bridge_state.world_raster)

    except Exception as e:
        logger.error(f"Error handling frame: {e}", exc_info=True)

# ============================================================================
# Stats Monitoring Loop
# ============================================================================

def stats_loop():
    """Monitor and broadcast stats"""
    logger.info("📊 Starting stats monitoring...")

    last_frame_count = 0
    last_log_time = time.time()

    while bridge_state.is_running:
        try:
            current_time = time.time()

            if current_time - last_log_time >= 1.0:
                with bridge_state.lock:
                    frames_delta = bridge_state.frames_received - last_frame_count
                    fps = frames_delta / (current_time - last_log_time)

                    bridge_state.fps_stats = {
                        'fps': round(fps, 1),
                        'frame_time_ms': round(1000.0 / fps if fps > 0 else 0, 2),
                        'active_leds': count_active_leds(bridge_state.world_raster) if bridge_state.world_raster else 0
                    }

                    last_frame_count = bridge_state.frames_received

                # Broadcast stats to clients
                socketio.emit('stats', bridge_state.fps_stats)
                last_log_time = current_time

            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in stats loop: {e}", exc_info=True)
            time.sleep(0.1)

    logger.info("🛑 Stats monitoring stopped")

# Global conversion cache for NumPy -> RGB list (persists across frames)
_conversion_cache = {}

def send_to_artnet(raster):
    """Send raster data to ArtNet controllers"""
    if not bridge_state.artnet_manager:
        return

    try:
        import dataclasses

        # Use existing sender infrastructure
        min_coord = (0, 0, 0)

        # Process each cube only once (track which cubes we've processed)
        processed_cubes = set()

        for job in bridge_state.artnet_manager.send_jobs:
            cube_pos_tuple = tuple(job["cube_position"])

            # Only slice cube data once per frame (even if multiple ArtNet mappings)
            if cube_pos_tuple not in processed_cubes:
                # Get cube position relative to world origin
                cube_position = (
                    job["cube_position"][0] - min_coord[0],
                    job["cube_position"][1] - min_coord[1],
                    job["cube_position"][2] - min_coord[2],
                )

                # Get cube dimensions
                cube_raster = job["cube_raster"]
                cube_dimensions = (
                    cube_raster.width,
                    cube_raster.height,
                    cube_raster.length,
                )

                # Get cube orientation
                cube_orientation = bridge_state.artnet_manager.cube_orientations.get(
                    cube_pos_tuple, ["X", "Y", "Z"]
                )

                # Apply orientation transformation
                transformed_slice = apply_orientation_transform(
                    raster.data, cube_position, cube_dimensions, cube_orientation
                )

                # Copy transformed data to cube raster
                cube_raster.data[:] = transformed_slice

                processed_cubes.add(cube_pos_tuple)

            # Convert NumPy array to RGB list for Rust controller (same as sender.py)
            cube_raster = job["cube_raster"]
            raster_id = id(cube_raster)

            if raster_id not in _conversion_cache:
                # Convert NumPy array to list of RGB objects
                import numpy as np
                numpy_data = cube_raster.data.reshape(-1, 3)
                _conversion_cache[raster_id] = [
                    RGB(int(r), int(g), int(b)) for r, g, b in numpy_data
                ]
            else:
                # Update existing RGB objects in-place (faster than recreating)
                import numpy as np
                numpy_data = cube_raster.data.reshape(-1, 3)
                rgb_list = _conversion_cache[raster_id]
                for i, (r, g, b) in enumerate(numpy_data):
                    rgb_list[i] = RGB(int(r), int(g), int(b))

            # Create temporary raster with converted data
            temp_raster = dataclasses.replace(cube_raster)
            temp_raster.data = _conversion_cache[raster_id]

            # Send via ArtNet with converted data
            try:
                controller_ip = job["controller"].get_ip()
                controller_port = job["controller"].get_port()

                job["controller"].send_dmx(
                    base_universe=min(job["z_indices"]) * 3,
                    raster=temp_raster,
                    z_indices=job["z_indices"],
                    channels_per_universe=510,
                    universes_per_layer=3,
                    channel_span=1
                )
            except Exception as e:
                # Log individual controller errors but continue
                controller_ip = job["controller"].get_ip() if hasattr(job["controller"], 'get_ip') else 'unknown'
                controller_port = job["controller"].get_port() if hasattr(job["controller"], 'get_port') else 'unknown'
                logger.error(f"Error sending to controller {controller_ip}:{controller_port}: {e}")

    except Exception as e:
        logger.error(f"Error in send_to_artnet: {e}", exc_info=True)

def apply_orientation_transform(world_data, cube_position, cube_dimensions, orientation):
    """
    Apply orientation transformation to slice world data for a cube.

    Args:
        world_data: 3D numpy array of world raster data
        cube_position: (x, y, z) position of cube in world coordinates
        cube_dimensions: (width, height, length) of cube
        orientation: List of 3 strings like ["-Z", "Y", "X"] defining axis mapping

    Returns:
        3D numpy array of transformed cube data
    """
    import numpy as np

    # Extract cube slice from world data
    start_x, start_y, start_z = cube_position
    cube_width, cube_height, cube_length = cube_dimensions

    # Get the raw slice from world data
    world_slice = world_data[
        start_z : start_z + cube_length,
        start_y : start_y + cube_height,
        start_x : start_x + cube_width,
    ]

    # Apply orientation transformation
    transformed_slice = world_slice.copy()

    # Map orientation to numpy array axes (numpy uses [Z, Y, X] indexing)
    axis_mapping = {"X": 2, "Y": 1, "Z": 0}  # numpy array indexing: [Z, Y, X]

    for i, axis in enumerate(orientation):
        if axis.startswith("-"):
            # Flip the axis
            axis_name = axis[1:]
            if axis_name in axis_mapping:
                numpy_axis = axis_mapping[axis_name]
                transformed_slice = np.flip(transformed_slice, axis=numpy_axis)

    # Apply axis reordering/rotation
    # Since we've already handled axis flipping, now we need to reorder axes
    # according to the orientation specification

    # Extract axis names without signs for lookup
    axis_names = [axis.lstrip("-") for axis in orientation]

    # Get the numpy axis indices for the reordered axes
    reordered_axes = [axis_mapping[name] for name in axis_names]

    # Transpose the array to reorder axes according to orientation
    # numpy.transpose expects where each original axis should go
    # We need to find the inverse mapping
    # Handle RGB dimension (last dimension) - it should stay in place
    transpose_axes = [0, 1, 2, 3]  # Default: no reordering, keep RGB at end
    for i, target_axis in enumerate(reordered_axes):
        # Flip order from world axis order to numpy axis order with 2 - i
        transpose_axes[target_axis] = 2 - i

    transformed_slice = np.transpose(transformed_slice, axes=transpose_axes)

    return transformed_slice

def count_active_leds(raster):
    """Count non-zero LEDs in raster"""
    import numpy as np
    return int(np.sum(np.any(raster.data > 0, axis=-1)))

# ============================================================================
# Server Initialization
# ============================================================================

def initialize_artnet(config_path):
    """Initialize ArtNet manager and raster"""
    logger.info(f"📡 Initializing ArtNet from config: {config_path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    bridge_state.config = config

    # Create ArtNet manager
    bridge_state.artnet_manager = ArtNetManager(config)

    # Parse world geometry
    world_width, world_height, world_length = map(
        int, config["world_geometry"].split("x")
    )

    # Create world raster
    bridge_state.world_raster = Raster(world_width, world_height, world_length)

    logger.info(f"✅ ArtNet initialized: {world_width}x{world_height}x{world_length}")
    logger.info(f"   Cubes: {len(config['cubes'])}, Controllers: {len(bridge_state.artnet_manager.controllers_cache)}")

def main():
    parser = argparse.ArgumentParser(description="ArtNet Bridge Server")
    parser.add_argument('--config', required=True, help='Path to ArtNet config JSON')
    parser.add_argument('--port', type=int, default=5000, help='WebSocket server port')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')

    args = parser.parse_args()

    # Initialize ArtNet
    initialize_artnet(args.config)
    bridge_state.is_running = True

    # Start stats monitoring thread
    stats_thread = Thread(target=stats_loop, daemon=True)
    stats_thread.start()

    # Start Flask-SocketIO server
    logger.info(f"\n🚀 ArtNet Bridge Server starting on {args.host}:{args.port}")
    logger.info(f"📊 WebSocket endpoint: ws://{args.host}:{args.port}")
    logger.info(f"🔌 Ready for web UI connections\n")

    try:
        socketio.run(app, host=args.host, port=args.port, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        bridge_state.is_running = False
        stats_thread.join(timeout=2.0)
        logger.info("✅ Server stopped")

if __name__ == '__main__':
    main()
