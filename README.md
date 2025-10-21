# Volumetric Display Prototype

A complete volumetric display system with web-based simulator, ArtNet DMX transmission, and interactive scene control.

## Overview

This project provides:
- **Web-based 3D Simulator** - Real-time volumetric visualization with 10+ effects
- **ArtNet DMX Control** - Python-based sender with Rust performance optimizations
- **Interactive Scene System** - Web UI for real-time parameter control
- **Hardware Integration** - Display configuration for physical LED cube hardware

## Quick Start

### Web Simulator (Standalone)

For quick visualization and effect testing:

```bash
npm start
# or
python3 -m http.server 8000
```

Then open: http://localhost:8000

### Full System with ArtNet

For hardware control or simulation with ArtNet:

1. **Install dependencies:**
   ```bash
   cd volumetric-display
   pip3 install -r requirements.txt
   cd ../artnet
   ./install_deps.sh
   ```

2. **Run interactive scene with web control:**
   ```bash
   cd volumetric-display
   python3 sender.py \
     --config display_config/sim_config.json \
     --scene scenes/interactive_scene.py \
     --web-server \
     --web-port 5001
   ```

3. **Access the web UI:**
   - Open http://localhost:5001 for scene controls
   - Adjust effects, colors, speeds, and parameters in real-time

### Configuration Files

Display configurations are located in `volumetric-display/display_config/`:
- `sim_config.json` - 20×20×20 single cube (simulator)
- `sim_config_4.json` - 4-cube configuration
- `sim_config_8.json` - 8-cube configuration

Each config defines:
- World geometry (total display dimensions)
- Cube positions and dimensions
- ArtNet IP/port mappings
- Axis orientation transforms

## Project Structure

```
vd-proto/
├── index.html                              # Web simulator entry point
├── src/                                    # Web simulator frontend
│   ├── css/styles.css                      # UI styles
│   └── js/
│       ├── main.js                         # Application entry point
│       ├── VolumetricDisplay.js            # Main controller
│       ├── VolumetricRenderer.js           # 3D rendering engine
│       ├── effects/EffectLibrary.js        # All 10+ effects
│       └── utils/                          # Perlin noise, particle systems
├── volumetric-display/                     # ArtNet transmission system
│   ├── sender.py                           # Main ArtNet sender application
│   ├── display_config/                     # Hardware configuration files
│   │   ├── sim_config.json                 # 20×20×20 single cube config
│   │   ├── sim_config_4.json               # 4-cube configuration
│   │   └── sim_config_8.json               # 8-cube configuration
│   └── scenes/                             # Scene implementations
│       ├── interactive_scene.py            # Web-controllable scene wrapper
│       └── interactive/                    # Interactive scene module
│           ├── scene.py                    # Main scene logic
│           └── web/index.html              # Web control interface
├── artnet/                                 # ArtNet Rust library
│   ├── src/artnet/                         # Rust bindings for performance
│   ├── build.sh                            # Build Rust components
│   └── install_deps.sh                     # Install all dependencies
└── legacy/                                 # Archived files (see below)
```

## System Components

### 1. Web Simulator (Standalone)
- **Frontend:** Modular ES6 JavaScript with Canvas 2D rendering
- **VolumetricDisplay:** Main controller managing state and orchestration
- **VolumetricRenderer:** 3D projection, camera controls, depth-sorted rendering
- **EffectLibrary:** 10+ volumetric effects (spheres, helixes, waves, noise, etc.)
- **Resolution:** 40×40×20 voxels (32,000 total LEDs)

### 2. ArtNet Transmission System
- **sender.py:** Main application for ArtNet DMX transmission
  - Loads display configuration from JSON
  - Renders scenes to volumetric raster
  - Transmits RGB data via ArtNet protocol
  - Supports multi-cube configurations with orientation transforms
  - Optional web server for real-time scene control

- **Display Configuration:**
  - Define world geometry and cube layout
  - Map physical cubes to ArtNet IP addresses
  - Configure axis orientations per cube
  - Support for multiple universes and Z-layer slicing

- **Scene System:**
  - `interactive_scene.py` - Web-controllable scene with UI
  - Custom scenes implement `render(raster, time)` method
  - Optional `update_parameters()` for web UI integration
  - Optional `get_web_ui_path()` for custom HTML interfaces

### 3. ArtNet Rust Library
- **High-performance bindings:** Rust implementation for speed-critical operations
- **Zero-copy transmission:** Direct byte buffer transfer to network
- **Python interface:** PyO3 bindings for seamless Python integration
- Build with `./artnet/build.sh`

## Usage Examples

### Web Simulator Controls
- **Mouse Drag:** Rotate the 3D view
- **Effect Buttons:** Switch between effects
- **Speed Slider:** Control animation speed (0.1x - 3x)
- **Density Slider:** Adjust effect density/intensity
- **LED Size Slider:** Change LED point size
- **Brightness Slider:** Adjust LED brightness
- **Grid Opacity Slider:** Show/hide wireframe grid

### Running sender.py

**Basic usage:**
```bash
python3 sender.py \
  --config display_config/sim_config.json \
  --scene scenes/interactive_scene.py
```

**With web server for real-time control:**
```bash
python3 sender.py \
  --config display_config/sim_config.json \
  --scene scenes/interactive_scene.py \
  --web-server \
  --web-port 5001
```

**Common options:**
- `--config <path>` - Display configuration JSON (required)
- `--scene <path>` - Scene Python file (required)
- `--web-server` - Enable web UI for scene control
- `--web-port <port>` - Web server port (default: 5001)
- `--brightness <0.0-1.0>` - Global brightness multiplier
- `--max-fps <fps>` - Target frame rate (default: 80)

### Display Configuration Format

Example `sim_config.json`:
```json
{
  "world_geometry": "20x20x20",
  "orientation": ["-Z", "Y", "X"],
  "cubes": [
    {
      "position": [0, 0, 0],
      "dimensions": "20x20x20",
      "artnet_mappings": [
        {
          "ip": "127.0.0.1",
          "port": "6454",
          "z_idx": [0, 1, 2, 3, 4, 5, ...],
          "universe": 0
        }
      ]
    }
  ]
}
```

## Legacy Folder

The `legacy/` directory contains archived files from previous development iterations:

- **Refactor Documentation:**
  - Progress tracking, guides, and summaries from the major refactoring effort
  - `REFACTOR_COMPLETE.md`, `FRONTEND_REFACTOR_GUIDE.md`, etc.

- **Backup Files:**
  - `scene.py.backup` - Original 2,025-line monolithic scene implementation
  - `index.html.backup` - Original 1,373-line HTML with inline JavaScript

- **Superseded Implementations:**
  - `artnet-bridge-js/` - JavaScript ArtNet bridge (replaced by Rust)
  - `standalone-js-simulator/` - Old JavaScript simulator
  - `test-files/` - Historical test files
  - `docs/` - Archived documentation

**Note:** Legacy files are excluded from active development via `.claudeignore`

## Performance

- **Web Simulator:** 60 FPS target with depth-sorted rendering
- **ArtNet Sender:** 80 FPS default (configurable 1-120 FPS)
- **Network:** Zero-copy transmission via Rust bindings
- **Rendering:** NumPy vectorized operations for scene calculations

## License

MIT
