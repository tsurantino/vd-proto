# TouchDesigner Documentation

Complete implementation guides for the Hybrid Morph volumetric display system in TouchDesigner.

---

## Documentation Overview

### 📘 [TOUCHDESIGNER_IMPLEMENTATION.md](TOUCHDESIGNER_IMPLEMENTATION.md)
**Main implementation guide for the Hybrid Morph particle system**

Complete reference for building the core particle-based volumetric display system using TouchDesigner POPs (Particle Operators). Covers:

- POP Network architecture
- Particle system setup and configuration
- Shape attractor construction (sphere, helix, torus, cube, pyramid, plane)
- Flow forces and directional motion
- Turbulence and noise systems
- Coherence and visibility control
- Scene implementations:
  - Shape morphing
  - Particle flows (rain, fountain, stars, spiral)
  - Vortex effects (tornado, whirlpool, galaxy)
  - Wave fields (ripple, standing, interference)
  - Plasma volumetrics
- Parameter control and presets
- Rendering techniques
- Performance optimization

**Start here** if you're building the system from scratch.

---

### 🎨 [TOUCHDESIGNER_COLOR_EFFECTS.md](TOUCHDESIGNER_COLOR_EFFECTS.md)
**Color system implementation and effects guide**

Comprehensive guide for implementing color management, palettes, and dynamic color effects. Covers:

- Color system architecture
- Palette management (gradients, discrete colors, procedural)
- Color mapping strategies (position, velocity, noise-based)
- Color effects library
- Integration with Hybrid Morph system
- Performance optimization for colored particles

Use this guide to add color to your particle systems.

---

### 👁️ [TOUCHDESIGNER_ILLUSIONS.md](TOUCHDESIGNER_ILLUSIONS.md)
**Optical illusion implementations using Hybrid Morph**

**NEW** - Specialized guide for creating 12 classic optical illusions adapted for the particle-based system. Each illusion includes:

- Conceptual explanation
- Hybrid parameter configurations (formCoherence, attractorStrength, turbulence, etc.)
- Complete POP network setup
- Python SOP attractor generators
- VEX wrangle code
- Parameter ranges and presets

#### Included Illusions:

1. **Rotating Ames Room** - Forced perspective trapezoid
2. **Infinite Corridor** - Nested scrolling rectangles (Droste effect)
3. **Kinetic Depth Effect** - 2D sine waves appearing 3D
4. **Waterfall Illusion** - Motion aftereffect with scrolling stripes
5. **Penrose Triangle** - Impossible geometric structure
6. **Necker Cube** - Ambiguous depth wireframe
7. **Fraser Spiral** - Concentric circles appearing as spirals
8. **Café Wall Illusion** - Offset checkerboard appearing tilted
9. **Pulfrich Effect** - Brightness-based depth perception
10. **Rotating Snakes** - Independently rotating concentric patterns
11. **Breathing Square** - Pulsing 3D checkerboard
12. **Moiré Pattern** - Interference patterns from overlapping grids

Use this guide to create perceptually striking volumetric illusions.

---

## Quick Start

### For New Users

1. **Read the [main implementation guide](TOUCHDESIGNER_IMPLEMENTATION.md)** to understand the Hybrid Morph architecture
2. **Build the basic POP network** following the Core Particle System Setup section
3. **Add shape attractors** starting with a simple sphere
4. **Add color** using the [color effects guide](TOUCHDESIGNER_COLOR_EFFECTS.md)
5. **Experiment with illusions** from the [illusions guide](TOUCHDESIGNER_ILLUSIONS.md)

### For Experienced Users

- Jump directly to specific scene implementations in the main guide
- Use the illusions guide as a reference for advanced attractor techniques
- Refer to the color guide for palette and gradient systems

---

## System Requirements

### TouchDesigner Version
- TouchDesigner 2022.28000 or newer
- GPU POPs recommended for particle counts > 1000

### Hardware Recommendations
- **Minimum:** Modern GPU with 2GB VRAM, 8GB system RAM
- **Recommended:** NVIDIA RTX series or equivalent, 16GB+ system RAM
- **Optimal:** High-end GPU for 2000+ particles at 60fps

---

## File Organization

```
td/
├── README.md                           # This file
├── TOUCHDESIGNER_IMPLEMENTATION.md     # Main implementation guide
├── TOUCHDESIGNER_COLOR_EFFECTS.md      # Color system guide
└── TOUCHDESIGNER_ILLUSIONS.md          # Optical illusions guide
```

---

## Related Documentation

### Project Root Documentation

Located in the main project directory:

- **[HYBRID_MORPH_SPEC.md](../HYBRID_MORPH_SPEC.md)** - Complete specification for the Hybrid Morph system concept and architecture
- **[NEW_FEATURES.md](../NEW_FEATURES.md)** - Latest features and updates
- **[DOCS_SERVER_README.md](../DOCS_SERVER_README.md)** - Documentation server setup

### Source Code Reference

JavaScript implementation (for concept reference):
- `src/js/effects/IllusionSceneLibrary.js` - Original illusion implementations
- `src/js/effects/SceneLibrary.js` - Scene and effect library
- `src/js/VolumetricDisplay.js` - Main display controller
- `src/js/color/` - Color system implementation

---

## Key Concepts

### Hybrid Morph System

The Hybrid Morph approach treats all visual elements as **particles influenced by attractors and forces**:

- **Shape Attractors** - Geometric equations defining target positions
- **Flow Forces** - Directional motion (fall, rise, spiral, explode, etc.)
- **Turbulence** - Noise-based chaotic motion
- **Coherence** - Visibility/solidity control

### Core Parameters

All scenes and illusions are controlled by these fundamental parameters:

- **formCoherence** (0-1) - Solid shape ↔ particle cloud
- **attractorStrength** (0-1) - Geometric fidelity ↔ free motion
- **turbulence** (0-1) - Smooth ↔ chaotic
- **particleDensity** (0-1) - Sparse ↔ dense
- **flowIntensity** (0-1) - Static ↔ flowing
- **flowDirection** (enum) - Motion pattern type

These parameters work harmoniously together to create smooth transitions between any visual state.

---

## Performance Guidelines

### Particle Count Targets

- **Wireframe illusions** (Necker, Ames): 200-500 particles
- **Medium patterns** (Kinetic, Fraser, Penrose): 500-800 particles
- **Dense volumetric** (Café Wall, Breathing, Moiré): 800-1200 particles
- **Flow effects** (Waterfall, Snakes): 1000-2000 particles

### Optimization Checklist

✅ Use GPU POPs for counts > 1000
✅ Resample attractors to minimize point count
✅ Cache static geometry with File Cache SOP
✅ Use POP Limit to cap particle count
✅ Combine multiple POP Wrangles when possible
✅ Implement LOD system for performance scaling

---

## Common Patterns

### Creating Custom Attractors

All illusions use custom SOP geometry as attractors. The general pattern:

```
Python SOP (generate geometry)
  → Resample (smooth/optimize)
  → Transform (apply global movement)
  → Null (output for POP Attract)
```

### Particle Visibility Control

Two complementary methods:

1. **Stochastic culling** (POP Wrangle) - Remove particles randomly based on formCoherence
2. **Noise displacement** (POP Wrangle) - Displace particles based on coherence value

### Parameter-Driven Animation

Use `absTime.seconds` for smooth time-based animation:
```python
angle = absTime.seconds * speed * multiplier
```

---

## Contributing

When adding new illusions or effects:

1. Follow the established parameter naming conventions
2. Use the Hybrid Morph parameter set (coherence, attractor, turbulence)
3. Provide both Python SOP and VEX Wrangle examples
4. Include parameter ranges and recommended presets
5. Document performance characteristics

---

## Support & Resources

### Official TouchDesigner Resources
- [TouchDesigner Documentation](https://docs.derivative.ca/)
- [TouchDesigner Forum](https://forum.derivative.ca/)
- [Derivative YouTube Channel](https://www.youtube.com/user/derivativeCA)

### Recommended Learning
- TouchDesigner POPs fundamentals
- VEX scripting basics
- Python SOP usage
- Point instancing and rendering

---

## Version History

- **v1.2** (2025-10-17) - Added optical illusions guide with 12 implementations
- **v1.1** (2025-10-17) - Added color effects guide
- **v1.0** (2025-10-17) - Initial implementation guide release

---

## License

This documentation is part of the vd-proto volumetric display project.

---

**Happy Building!** 🎨✨

For questions or suggestions, refer to the main project documentation.
