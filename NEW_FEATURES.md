# New Features Documentation

## Overview
Three major enhancements have been added to the volumetric display system:

1. **Parameter Automation with LFO** - Automatically animate any scene parameter
2. **3D Gradient Mapping** - Advanced color gradients in 3D space
3. **Advanced Color Effects** - New color effects (sparkle, fire, plasma, etc.)

---

## 1. Parameter Automation with LFO

### Description
Automatically animate any scene parameter using Low-Frequency Oscillators (LFOs). This creates dynamic, evolving visuals without manual control.

### How to Use

#### Activating Automation:
1. **Right-click** any parameter slider in the UI
2. A modal will appear with automation controls
3. Configure the automation:
   - **Wave Type**: Sine, Triangle, Square, Sawtooth, or Random
   - **Frequency**: 0.1 - 10 Hz (how fast the parameter oscillates)
   - **Depth**: 0 - 100% (how much the parameter varies)
   - **Phase**: 0 - 100% (offset for wave timing)
4. Click **Apply** to activate

#### Visual Indicators:
- Automated sliders have a **pulsing purple-cyan gradient**
- Active automations appear in the "Parameter Automation" section at the bottom

#### Managing Automations:
- **Pause/Resume**: Click the ⏸/▶ button next to an automation
- **Remove**: Right-click the slider again and click "Remove"
- **Clear All**: Click "Clear All" button in automation section

### Technical Details
**File**: `src/js/automation/ParameterAutomation.js`

**Wave Types:**
- `sine`: Smooth oscillation (most natural)
- `triangle`: Linear rise and fall
- `square`: Instant switching between min/max
- `sawtooth`: Linear rise, instant drop
- `random`: Smooth random values

**API:**
```javascript
display.parameterAutomation.setAutomation(parameterId, {
    waveType: 'sine',
    frequency: 1.0,    // Hz
    amplitude: 0.5,    // 0-1 (percentage of range)
    phase: 0,          // 0-1
    min: 0,
    max: 1,
    baseValue: 0.5,
    enabled: true
});
```

### Use Cases
- **Breathing Effects**: Slow sine wave on size/opacity
- **Pulsing Patterns**: Fast square wave on object count
- **Evolving Noise**: Random wave on procedural threshold
- **Complex Motion**: Multiple automations on different parameters

---

## 2. 3D Gradient Mapping

### Description
Map colors in 3D space instead of just vertically. Creates depth, focus points, and spatial relationships that enhance 3D perception.

### How to Use

#### Activating 3D Mapping:
1. In the **Colors** section, scroll to "3D Gradient Mapping"
2. Check **"Enable 3D Mapping"**
3. Additional controls will appear:
   - **Type**: Linear X/Y/Z, Radial, Spherical, or Cylindrical
   - **Origin X/Y/Z**: Center point for gradient (0-1, normalized)
   - **Falloff**: Linear, Quadratic, Cubic, or Smoothstep
   - **Invert**: Reverse gradient direction

#### Gradient Types:
- **Linear Y** (default): Vertical gradient (same as original)
- **Linear X**: Horizontal gradient left-to-right
- **Linear Z**: Depth gradient front-to-back
- **Radial**: Color based on distance from origin point
- **Spherical**: Same as radial (3D distance from origin)
- **Cylindrical**: Radial in XZ plane, ignores Y

#### Adjusting Origin:
- Origin controls where the gradient starts (0.5 = center)
- For radial/spherical: origin is the center point
- Move origin to create off-center glows or directional fades

#### Falloff Types:
- **Linear**: Even color distribution
- **Quadratic**: Faster transition at edges
- **Cubic**: Very fast transition at edges
- **Smoothstep**: Smooth, S-curved transition

### Technical Details
**File**: `src/js/color/ColorMapper3D.js`

**Color Stops:**
The system uses the current gradient colors (2-color gradients by default). When 3D mapping is enabled, these colors are mapped to 3D space instead of just Y-axis.

**API:**
```javascript
display.renderer.colorMapper3D.setEnabled(true);
display.renderer.colorMapper3D.setGradientType('radial');
display.renderer.colorMapper3D.setOrigin(0.5, 0.5, 0.5);
display.renderer.colorMapper3D.setFalloff('smoothstep');
display.renderer.colorMapper3D.setInvert(false);
```

### Use Cases
- **Center Glow**: Radial gradient from center (origin: 0.5, 0.5, 0.5)
- **Spotlight**: Radial gradient off-center (origin: 0.3, 0.7, 0.5)
- **Depth Fade**: Linear Z gradient (simulates fog/depth)
- **Cylindrical Tunnel**: Cylindrical gradient (walls one color, center another)

---

## 3. Advanced Color Effects

### Description
Seven new color effects that create dynamic, evolving color patterns. These effects operate independently from GlobalEffects (strobe, pulse) and can be combined with them.

### Effects List

#### **Sparkle**
Random voxels briefly flash bright white
- **Best for**: Adding life to static scenes
- **Intensity**: Controls flash frequency

#### **Rainbow Sweep**
Full spectrum sweep across 3D space
- **Best for**: Psychedelic, colorful displays
- **Intensity**: Controls color saturation

#### **Fire**
Flickering warm colors (orange/yellow/red) with upward bias
- **Best for**: Fire, lava, heat effects
- **Intensity**: Controls flicker amount

#### **Plasma**
Multi-sine wave interference pattern creating smooth color blending
- **Best for**: Organic, flowing color patterns
- **Intensity**: Controls effect strength

#### **Kaleidoscope**
Mirror colors across axes with 6-fold symmetry
- **Best for**: Symmetrical, mandala-like patterns
- **Intensity**: Controls symmetry strength

#### **Breath**
Slow saturation oscillation (NOT brightness - that's GlobalEffects pulse)
- **Best for**: Calm, meditative effects
- **Intensity**: Controls saturation range

#### **Color Chase**
Moving wave of color across the grid
- **Best for**: Dynamic, racing effects
- **Intensity**: Controls chase visibility

### How to Use

1. In the **Colors** section, scroll to "Advanced Effects"
2. Click the effect you want (buttons turn **magenta** when active)
3. Adjust **Effect Intensity** slider (0-100%)
   - 0% = no effect (base colors only)
   - 100% = full effect
4. Click **Off** to disable

### Combining Effects
Advanced effects can be layered with:
- Basic color effects (cycle, pulse, wave)
- Global effects (decay, strobe, pulse, invert)
- 3D gradient mapping

**Example Stack:**
1. 3D Radial Gradient (center glow)
2. Fire effect at 70% intensity
3. Slow pulse from GlobalEffects
= Pulsing fire with radial color spread

### Technical Details
**File**: `src/js/effects/ColorEffects.js`

**No Duplication with GlobalEffects:**
- GlobalEffects operates on voxel brightness (post-scene)
- ColorEffects operates on RGB color values (during render)
- They work together without conflicts

**API:**
```javascript
display.renderer.colorEffects.setEffect('fire');
display.renderer.colorEffects.setIntensity(0.8);
```

**Effect Implementation:**
Each effect is a function that modifies RGB color based on:
- Voxel position (x, y, z)
- Current time (animated effects)
- Base color (blended with intensity)

### Performance
All effects are optimized for real-time performance:
- **Sparkle**: Moderate cost (random checks + map lookup)
- **Rainbow Sweep**: Low cost (simple math)
- **Fire**: Low cost (sine waves)
- **Plasma**: Moderate cost (multiple sine waves)
- **Kaleidoscope**: Low cost (coordinate math)
- **Breath**: Very low cost (single oscillation)
- **Color Chase**: Low cost (dual sine waves)

Target: **60 FPS** maintained on standard hardware (40×20×40 grid)

---

## System Architecture

### File Structure
```
src/js/
├── automation/
│   └── ParameterAutomation.js      # LFO engine
├── color/
│   └── ColorMapper3D.js            # 3D gradient system
├── effects/
│   └── ColorEffects.js             # Advanced color effects
├── VolumetricDisplay.js            # Integrated automation
├── VolumetricRenderer.js           # Integrated 3D colors + effects
└── main.js                         # UI controls
```

### Integration Points

**VolumetricDisplay.js:**
- Imports `ParameterAutomation`
- Updates automations each frame
- Applies automated values before scene generation

**VolumetricRenderer.js:**
- Imports `ColorMapper3D` and `ColorEffects`
- `getColorForVoxel()` checks 3D mapping first, then falls back to standard coloring
- Applies advanced effects after basic color is determined
- Updates effect time each frame

**main.js:**
- Sets up right-click handlers for automation
- Manages automation modal and list
- Connects 3D mapping controls
- Connects advanced effect buttons

---

## Testing

### Test Page
Open `test-features.html` in your browser to verify all features work correctly.

Tests:
1. ParameterAutomation - Creates automation, updates, gets value
2. ColorMapper3D - Creates mapper, sets radial gradient, gets color
3. ColorEffects - Tests all 7 effects with intensity

### Manual Testing Checklist

**Parameter Automation:**
- [ ] Right-click a slider opens modal
- [ ] Applying automation adds purple gradient to slider
- [ ] Automation appears in list
- [ ] Parameter value oscillates automatically
- [ ] Pause/resume works
- [ ] Remove automation works
- [ ] Clear all works

**3D Gradient Mapping:**
- [ ] Enabling 3D mapping shows controls
- [ ] Changing gradient type updates colors
- [ ] Origin controls shift gradient center
- [ ] Falloff types change gradient curve
- [ ] Invert reverses gradient
- [ ] Works with existing gradient colors

**Advanced Color Effects:**
- [ ] Each effect button activates correctly
- [ ] Active effect shows magenta highlight
- [ ] Intensity slider adjusts effect strength
- [ ] Effects are visually distinct
- [ ] Turning off removes effect
- [ ] Effects work with other color systems

---

## Performance Optimization

### Implemented Optimizations

1. **ColorMapper3D**:
   - Caches origin grid coordinates
   - Pre-calculates max distances
   - Only updates cache when settings change

2. **ParameterAutomation**:
   - Simple math operations (no heavy computation)
   - Map-based storage (O(1) lookup)
   - Only calculates enabled automations

3. **ColorEffects**:
   - Sparkle uses Map for state (efficient lookup/cleanup)
   - All effects use optimized math (no expensive operations)
   - Early exit when intensity = 0

### Performance Targets
- **60 FPS** with all features active
- **< 17ms** frame time
- Tested with 40×20×40 grid (32,000 voxels max)

---

## Future Enhancements

### Potential Additions

**Parameter Automation:**
- [ ] Record manual slider movements as automation
- [ ] Save/load automation presets
- [ ] Automation timeline (sequence automations)
- [ ] More wave types (exponential, logarithmic)

**3D Gradient Mapping:**
- [ ] Support 3+ color stops (not just 2)
- [ ] Visual 3D preview of gradient
- [ ] Animated origin (move gradient center over time)
- [ ] Multiple gradient layers

**Advanced Color Effects:**
- [ ] Combine 2 effects simultaneously
- [ ] Per-effect speed control
- [ ] Custom effect builder
- [ ] Effect presets

---

## Troubleshooting

### Automation Not Working
**Problem**: Right-clicking slider doesn't open modal
**Solution**: Make sure slider has proper ID attribute. Check console for errors.

**Problem**: Automation appears in list but parameter not changing
**Solution**: Check automation is enabled (play button, not pause). Verify min/max range is correct.

### 3D Gradient Not Visible
**Problem**: Enabling 3D mapping doesn't change colors
**Solution**: Make sure checkbox is actually checked. Try changing gradient type. Verify gradient colors are set (not solid color mode).

### Advanced Effects Not Working
**Problem**: Effect button active but no visual change
**Solution**: Increase intensity slider. Some effects are subtle at low intensity. Try different scene types (effects work better with more voxels).

### Performance Issues
**Problem**: FPS drops below 30
**Solution**:
1. Disable sparkle effect (most expensive)
2. Reduce number of active voxels (lower scene density)
3. Disable 3D gradient mapping if not needed
4. Check browser console for errors

---

## API Reference

### ParameterAutomation

```javascript
// Create instance
const automation = new ParameterAutomation();

// Set automation
automation.setAutomation(parameterId, {
    waveType: 'sine',
    frequency: 1.0,
    amplitude: 0.5,
    phase: 0,
    min: 0,
    max: 1,
    baseValue: 0.5,
    enabled: true
});

// Get automated value
const value = automation.getAutomatedValue(parameterId);

// Remove automation
automation.removeAutomation(parameterId);

// Toggle enabled
automation.toggleAutomation(parameterId);

// Clear all
automation.clear();

// Export/import
const data = automation.export();
automation.import(data);
```

### ColorMapper3D

```javascript
// Create instance
const mapper = new ColorMapper3D(gridX, gridY, gridZ);

// Configure
mapper.setEnabled(true);
mapper.setGradientType('radial'); // linear-x/y/z, radial, spherical, cylindrical
mapper.setColorStops([
    { position: 0, color: { r: 255, g: 0, b: 0 } },
    { position: 1, color: { r: 0, g: 0, b: 255 } }
]);
mapper.setOrigin(0.5, 0.5, 0.5);
mapper.setFalloff('smoothstep'); // linear, quadratic, cubic, smoothstep
mapper.setInvert(false);

// Get color for voxel
const color = mapper.getColorForVoxel(x, y, z);

// Export/import
const data = mapper.export();
mapper.import(data);
```

### ColorEffects

```javascript
// Create instance
const effects = new ColorEffects(gridX, gridY, gridZ);

// Set effect
effects.setEffect('fire'); // sparkle, rainbowSweep, fire, plasma, kaleidoscope, breath, colorChase, none
effects.setIntensity(0.8); // 0-1

// Update (call each frame)
effects.update(deltaTime);

// Apply effect to color
const modifiedColor = effects.applyEffect(baseColor, x, y, z, val);

// Reset
effects.reset();
```

---

## Credits

**Implementation Date**: October 2025
**Framework**: Vanilla JavaScript ES6
**Architecture**: Modular, plugin-based
**Performance**: Optimized for real-time 60 FPS

These features maintain backward compatibility with existing code and add zero overhead when disabled.
