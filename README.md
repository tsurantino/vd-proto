# Volumetric Display Simulator

A web-based simulator for a 40×40×20 LED volumetric cube display with 10 different visual effects.

## Features

- **10 Volumetric Effects** optimized for low-resolution displays
- **Interactive 3D View** - drag to rotate
- **Real-time Parameter Controls** - speed, density, LED size, brightness, grid opacity
- **Performance Monitoring** - FPS and active LED count

## Effects

1. **Rotating Plane Slice** - Solid plane rotating through volume
2. **Pulsing Sphere** - Expanding/contracting hollow sphere
3. **Rain/Waterfall** - Particles falling through Z-axis
4. **Wave Ripple** - Sine wave propagating through height
5. **Helix Spiral** - Multi-strand rotating spiral
6. **Corner-to-Corner Sweep** - Diagonal plane transition
7. **Concentric Boxes** - Nested expanding boxes
8. **Starfield Depth** - Moving stars with Z-depth
9. **Perlin Noise Clouds** - Smooth 3D noise animation
10. **Layer Sequence** - Z-layer patterns with different designs

## Quick Start

### Option 1: Python (Recommended)

```bash
npm start
# or
python3 -m http.server 8000
```

Then open: http://localhost:8000

### Option 2: Node.js

If you have Node.js installed, you can use `npx`:

```bash
npx http-server -p 8000
```

Then open: http://localhost:8000

### Option 3: PHP

```bash
php -S localhost:8000
```

Then open: http://localhost:8000

## Project Structure

```
vd-proto/
├── index.html                              # Main HTML entry point
├── src/
│   ├── css/
│   │   └── styles.css                      # UI styles
│   └── js/
│       ├── main.js                         # Application entry point
│       ├── VolumetricDisplay.js            # Main controller
│       ├── VolumetricRenderer.js           # 3D rendering engine
│       ├── effects/
│       │   └── EffectLibrary.js            # All 10 effects
│       └── utils/
│           ├── PerlinNoise.js              # Perlin noise generator
│           └── ParticleSystems.js          # Particle systems
```

## Architecture

The simulator uses a modular ES6 architecture:

- **VolumetricDisplay** - Main controller managing state and orchestration
- **VolumetricRenderer** - 3D projection, camera controls, and rendering
- **EffectLibrary** - All volumetric effects with metadata
- **Utils** - Reusable components (Perlin noise, particle systems)

## Controls

- **Mouse Drag** - Rotate the 3D view
- **Effect Buttons** - Switch between effects
- **Speed Slider** - Control animation speed (0.1x - 3x)
- **Density Slider** - Adjust effect density/intensity
- **LED Size Slider** - Change LED point size
- **Brightness Slider** - Adjust LED brightness
- **Grid Opacity Slider** - Show/hide wireframe grid

## Technical Details

- **Resolution**: 40×40×20 voxels (32,000 total LEDs)
- **Rendering**: Canvas 2D with custom 3D projection
- **Effects**: Real-time procedural generation
- **Performance**: 60 FPS target with depth-sorted rendering

## License

MIT
