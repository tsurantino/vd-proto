# ArtNet Bridge for Volumetric Display

This directory contains the ArtNet bridge system that connects the web UI to physical or simulated volumetric displays via ArtNet protocol.

## Overview

The ArtNet bridge consists of:

- **Python Backend Server** (`artnet_bridge_server.py`) - Receives effect state from web UI and renders to ArtNet
- **Scene Adapters** (`artnet_web_scenes.py`) - Translates web UI scenes to Python Scene classes
- **JavaScript Client** (`../src/js/ArtNetBridge.js`) - WebSocket client for real-time communication
- **C++ Simulator** (`volumetric_display`) - Volumetric display simulator that receives ArtNet data

## Quick Start

### 1. Install Python Dependencies

```bash
cd artnet
pip3 install -r requirements.txt
```

### 2. Start the C++ ArtNet Simulator (Optional)

If you want to visualize the output:

```bash
cd artnet
./volumetric_display sim_config_4.json
```

Or use npm script from project root:
```bash
npm run artnet-sim
```

### 3. Start the ArtNet Bridge Server

```bash
python3 artnet/artnet_bridge_server.py --config artnet/sim_config_4.json
```

Or use npm script from project root:
```bash
npm run artnet
```

### 4. Start the Web Server

In a separate terminal:

```bash
npm start
```

### 5. Enable ArtNet Mode in Browser

1. Navigate to `http://localhost:8000`
2. Click the **"ArtNet"** button in the top-right corner
3. The web UI should connect to the Python bridge
4. The canvas will be replaced with an ArtNet status display
5. All controls continue to work, sending data to ArtNet instead of rendering locally

## Architecture

```
┌─────────────────┐     WebSocket      ┌──────────────────────┐
│   Web Browser   │ ◄───────────────► │  Python Bridge       │
│   (UI Controls) │    Socket.IO      │  artnet_bridge_      │
│                 │                    │  server.py           │
└─────────────────┘                    │                      │
                                       │  ┌────────────────┐  │
                                       │  │ Scene Adapters │  │
                                       │  │ artnet_web_    │  │
                                       │  │ scenes.py      │  │
                                       │  └────────────────┘  │
                                       │                      │
                                       │  ┌────────────────┐  │
                                       │  │ ArtNet Sender  │  │
                                       │  │ sender.py      │  │
                                       │  └────────────────┘  │
                                       └──────────┬───────────┘
                                                  │ ArtNet/UDP
                                                  ▼
                                       ┌──────────────────────┐
                                       │  C++ Simulator or    │
                                       │  Physical Display    │
                                       │  volumetric_display  │
                                       └──────────────────────┘
```

## Features

### Supported from Web UI

✅ **All Scene Types**
- Shape Morph (sphere, cube, helix, torus, pyramid, plane)
- Particle Flow (particles, spiral, tornado, whirlpool, galaxy)
- Wave Field (ripple, plane wave, standing, interference)
- Procedural (Perlin noise)
- Grid patterns
- Text 3D

✅ **All Global Parameters**
- Size, density, object count, arrangements
- Rotation (X, Y, Z)
- Translation and movement
- Oscillation (bounce, pulse)
- Path motion (orbit, spiral, figure-8, ellipse)
- Advanced movement (wobble, scroll)
- Wave & procedural (frequency, amplitude, detail)

✅ **Color Controls**
- Single colors
- Gradient colors
- Color effects (static, cycle, pulse, wave)
- Advanced color effects

✅ **Global Effects**
- Animation speed
- Decay/blur
- Strobe (off, slow, medium, fast)
- Pulse (off, slow, medium, fast)
- Invert

✅ **Scrolling Effects**
- Multiple directions
- Strobe/pulse modes
- Variable thickness and speed
- Invert mode

### Configuration

The bridge uses `sim_config_4.json` which defines:

```json
{
  "world_geometry": "40x40x20",  // Overall grid dimensions
  "cubes": [ ... ],              // Individual cube configurations
  "orientation": ["X", "Y", "Z"], // Coordinate system
  "controller_addresses": { ... } // ArtNet controller IPs/ports
}
```

## Communication Protocol

### WebSocket Events

**Client → Server:**
- `update_scene` - Scene type and parameters change
- `update_global_params` - Global parameter changes
- `update_colors` - Color settings change
- `update_color_effect` - Color effect changes
- `update_display_params` - Display parameters (speed, brightness)
- `update_global_effects` - Global effects (decay, strobe, pulse, invert)
- `update_scrolling` - Scrolling effect settings

**Server → Client:**
- `stats` - Performance stats (FPS, frame time, active LEDs)
- `status` - Connection and configuration status
- `state` - Full effect state (on connect)

### HTTP API

**GET /api/status**
- Returns bridge status, configuration, and stats

**POST /api/effect**
- Update effect state via HTTP (alternative to WebSocket)

## Performance

- **Target Frame Rate:** 60 FPS
- **Update Throttling:** WebSocket updates throttled to 20 updates/sec
- **Scene Rendering:** Python with NumPy for performance
- **ArtNet Transmission:** Optimized using existing sender infrastructure

## Troubleshooting

### "Could not connect to ArtNet bridge"

1. Make sure Python bridge server is running:
   ```bash
   python3 artnet/artnet_bridge_server.py --config artnet/sim_config_4.json
   ```

2. Check if port 5000 is available:
   ```bash
   lsof -i :5000
   ```

3. Check for Python dependency issues:
   ```bash
   pip3 install -r artnet/requirements.txt
   ```

### "No visual output in simulator"

1. Ensure C++ simulator is compiled and running:
   ```bash
   cd artnet
   ./volumetric_display sim_config_4.json
   ```

2. Check ArtNet ports match in configuration (default: 6454-6457)

3. Verify firewall isn't blocking UDP traffic

### "Slow/laggy updates"

1. Check Python server FPS in console output
2. Reduce grid resolution if needed
3. Disable advanced color effects temporarily
4. Check network latency between browser and Python server

## Development

### Adding New Scene Types

1. Create scene class in `artnet_web_scenes.py`:
   ```python
   class WebMyNewScene(Scene):
       def __init__(self, params, global_params, color_state):
           # Initialize
           pass

       def render(self, raster: Raster, time: float):
           # Render logic
           pass
   ```

2. Add to scene map in `create_scene_from_state()`:
   ```python
   scene_map = {
       'myNewScene': WebMyNewScene,
       ...
   }
   ```

3. No JavaScript changes needed - scenes auto-sync!

### Debugging

Enable debug logging in Python server:
```bash
python3 artnet/artnet_bridge_server.py --config artnet/sim_config_4.json --log-level DEBUG
```

Monitor WebSocket traffic in browser console (enabled by default)

## Files

- `artnet_bridge_server.py` - Main Python server with Flask-SocketIO
- `artnet_web_scenes.py` - Scene adapters for web UI
- `artnet_bridge_config.json` - Server configuration
- `requirements.txt` - Python dependencies
- `sender.py` - ArtNet transmission logic (existing)
- `artnet.py` - Core ArtNet classes (existing)
- `sim_config_4.json` - 4-cube display configuration (existing)
- `volumetric_display` - C++ simulator binary (existing)

## License

MIT
