# ColorEffects Python Port - Implementation Guide

This document describes the modular color effects system that accurately ports the JavaScript ColorEffects.js implementation to Python.

## Architecture

```
artnet/scenes/colors/effects/
├── __init__.py                  # Module exports
├── color_utils.py               # HSL/RGB conversion (COMPLETED)
├── color_effects.py             # Main ColorEffects class with state
├── base_effects.py              # Basic effects (cycle, pulse, wave)
├── wave_effects.py              # Wave-based effects
├── cycle_effects.py             # Cycle effects
├── pulse_effects.py             # Pulse effects
├── static_effects.py            # Static/noise effects
├── combo_effects.py             # Combination effects
├── spatial_effects.py           # 3D spatial effects
├── procedural_effects.py        # Procedural effects (Perlin, Voronoi)
├── interference_effects.py      # Interference patterns
├── geometric_effects.py         # Geometric patterns
├── symmetry_effects.py          # Symmetry effects
└── classic_effects.py           # Classic effects (sparkle, fire, plasma)
```

## Key Differences from JavaScript

### 1. State Management
JavaScript version maintains:
- `sparkleMap` - Map of sparkling voxels with timestamps
- `voronoiSeeds` - Moving Voronoi cell centers
- `time` - Accumulated time for animation
- `perlinPerm` - Perlin noise permutation table

Python version must maintain these as instance variables.

### 2. Color Generation vs. Modification
**JavaScript** has two modes:
- `colorMode = 'rainbow'`: Generate new colors from scratch
- `colorMode = 'base'`: Modulate existing colors

**Python** must replicate this exactly - many effects generate full rainbow colors, not just modify existing ones.

### 3. Critical Effect Implementations

#### waveMulti (CURRENTLY BROKEN)
**JavaScript (Correct)**:
```javascript
const sources = [
    {x: this.gridX / 4, z: this.gridZ / 4},
    {x: 3 * this.gridX / 4, z: this.gridZ / 4},
    {x: this.gridX / 2, z: 3 * this.gridZ / 4}
];
let totalWave = 0;
sources.forEach(source => {
    const dx = x - source.x;
    const dz = z - source.z;
    const dist = Math.sqrt(dx * dx + dz * dz);
    totalWave += Math.sin(dist * 0.3 - this.time * this.speed * 2);
});
```

**Current Python (WRONG)**:
```python
wave_y = np.sin(y_coords[mask] * 0.3 + time * 2)
wave_x = np.sin(x_coords[mask] * 0.3 + time * 1.5)
combined = (wave_y + wave_x) * 64
```

#### sparkle (CURRENTLY BROKEN)
**JavaScript**: Maintains per-voxel state with fade in/out timing
**Python**: Just randomly whites out 10% - no state tracking

## Integration with interactive_scene.py

Replace line 416-420 in interactive_scene.py:

```python
# OLD (simple function call):
from .colors.all_effects import apply_color_effect
apply_color_effect(raster.data, mask, self.coords_cache,
                  self.color_time, effect, intensity)

# NEW (use ColorEffects class):
from .colors.effects import ColorEffects

# In __init__:
self.color_effects = ColorEffects(
    raster.width, raster.height, raster.length
)

# In _apply_color_effect:
self.color_effects.set_effect(effect)
self.color_effects.set_intensity(intensity)
self.color_effects.apply_to_raster(
    raster.data, mask, self.coords_cache, self.color_time
)
```

## Next Steps

1. Complete `color_effects.py` with full state management
2. Implement all effect modules matching JavaScript algorithms exactly
3. Update interactive_scene.py to use the new class
4. Test each effect category against JavaScript output

## Testing Approach

For each effect:
1. Set same parameters in both JS and Python
2. Capture frame at t=5.0 seconds
3. Compare color values at sample coordinates
4. Ensure visual output matches

Priority order:
1. Basic effects (cycle, pulse, wave) - most common
2. Classic effects (sparkle, fire, plasma) - visually distinctive
3. Wave effects - complex but high visual impact
4. Everything else
