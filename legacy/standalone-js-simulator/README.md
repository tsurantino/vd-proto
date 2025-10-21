# Standalone JavaScript Volumetric Display Simulator

A browser-based volumetric display simulator with no hardware dependencies. Purely for visualization and testing scene effects.

## Features

- Full 3D volumetric rendering in the browser using Three.js
- Complete scene library (shapes, waves, particles, procedural noise)
- Color effects and gradient mapping
- Global effects (decay, strobe, pulse, scrolling masks)
- Parameter automation
- Interactive 3D camera controls
- No ArtNet output - visualization only

## Running the Simulator

### Prerequisites

- Node.js (v14 or higher)
- npm

### Installation

```bash
cd legacy/standalone-js-simulator
npm install
```

### Start the Server

```bash
npm start
```

Or directly:
```bash
node server.js
```

The server will start on http://localhost:8000

### Available Pages

- **Main Simulator**: http://localhost:8000/
  - Full volumetric display with scene controls
  - Imports JavaScript modules from `../artnet-bridge-js/src/`

- **Documentation Viewer**: http://localhost:8000/docs.html
  - Browse and view all markdown documentation files
  - Renders markdown in a clean, readable format

- **Feature Test Page**: http://localhost:8000/test-features.html
  - Test specific features and effects

- **Alternative Simulator**: http://localhost:8000/volumetric-simulator.html
  - Alternative interface for the volumetric display

## Architecture

This simulator uses the JavaScript codebase located in `../artnet-bridge-js/src/`:
- Scene generation (`src/js/effects/SceneLibrary.js`)
- Color effects (`src/js/effects/ColorEffects.js`)
- Global effects (`src/js/effects/GlobalEffects.js`)
- 3D rendering (`src/js/VolumetricRenderer.js`)

The main difference from `artnet-bridge-js` is that this version:
1. Has no ArtNet bridge connection
2. Includes a Node.js server for serving files and documentation
3. Is completely standalone - no Python backend required

## File Structure

```
standalone-js-simulator/
├── index.html              # Main simulator interface
├── server.js               # Node.js Express server
├── package.json            # Node dependencies
├── docs.html               # Documentation viewer
├── test-features.html      # Feature testing page
├── volumetric-simulator.html  # Alternative interface
└── README.md               # This file

# Shared JavaScript code (in artnet-bridge-js/):
../artnet-bridge-js/src/
├── js/
│   ├── VolumetricDisplay.js
│   ├── VolumetricRenderer.js
│   ├── effects/
│   │   ├── SceneLibrary.js
│   │   ├── ColorEffects.js
│   │   ├── GlobalEffects.js
│   │   └── ScrollingEffect.js
│   └── utils/
└── css/
    └── styles.css
```

## Relationship to Current Implementation

This is a **legacy** implementation. The current active codebase uses:
- Python for scene computation (`artnet/scenes/interactive_scene.py`)
- Flask/SocketIO server (`artnet/interactive_scene_server.py`)
- Mobile-friendly PWA controller UI (`web/controller.html`)
- Direct ArtNet output to hardware

The current implementation is more performant and maintainable, with all scene logic centralized in Python rather than split between JavaScript and Python.

## Use Cases

This legacy simulator is still useful for:
- Quick visualization without setting up the Python environment
- Testing scene ideas in the browser
- Demonstrating the volumetric display concept
- Reference implementation for JavaScript-based rendering
