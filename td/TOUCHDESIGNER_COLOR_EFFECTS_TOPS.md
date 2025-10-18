# TouchDesigner Color Effects - TOP-Based Implementation
## Recreating ColorEffects.js using Texture Operators

This guide demonstrates how to recreate all color effects from `ColorEffects.js` using TouchDesigner's TOP (Texture Operator) network instead of GLSL shaders. Effects are applied uniformly across geometry using standard texture mapping, without requiring precise position information.

---

## Table of Contents

1. [Overview](#overview)
2. [Base Architecture](#base-architecture)
3. [Core Building Blocks](#core-building-blocks)
4. [Effect Implementations](#effect-implementations)
5. [Parameter Control](#parameter-control)
6. [Optimization Tips](#optimization-tips)

---

## Overview

### Why TOPs Instead of Shaders?

**Advantages:**
- Visual, node-based workflow
- Real-time parameter tweaking
- Easier debugging (preview at any stage)
- No shader compilation required
- Accessible to non-programmers
- Built-in operators for common effects

**Disadvantages:**
- Slightly lower performance than optimized GLSL
- More nodes in network (can get messy)
- Some effects require multiple passes

### Pipeline Architecture

```
[Texture Coordinates (UV)]
         ↓
[Effect Processing (TOPs)]
         ↓
[Color Output (RGB TOP)]
         ↓
[Apply to Geometry via Material]
```

**Key Concept:** All effects use standard UV coordinates (0-1 range) and apply uniformly across any geometry through texture mapping.

---

## Base Architecture

### 1. UV Coordinate System

TouchDesigner automatically provides UV coordinates for geometry. Effects use these as their spatial reference.

**Standard UV Layout:**
- U (horizontal): 0 (left) to 1 (right)
- V (vertical): 0 (bottom) to 1 (top)

**For 3D effects**, create a third dimension using techniques like:
- Noise patterns
- Radial gradients from center
- Time-based variation

### 2. Time Control

**Network:**
```
[Timer CHOP]
    Settings:
    - Initialize: On
    - Length: 10000 (or large value)
    - Speed: Link to control parameter
    ↓
[Null CHOP: 'time_out']
```

**Usage in TOPs:**
- Reference as: `op('time_out')[0]`
- Or use built-in: `absTime.seconds`

### 3. Base Color

**Network:**
```
[Constant TOP]
    Settings:
    - Resolution: 512×512 (or desired size)
    - Color: Base RGB color
    ↓
[Null TOP: 'baseColor']
```

---

## Core Building Blocks

### Utility 1: HSL Converter Components

Since TOPs work in RGB, we need HSL conversion for saturation/hue effects.

#### RGB to HSL (using Lookup TOP)

**Alternative to scripting - using built-in TOPs:**

```
[RGB Input]
    ↓
[HSV Convert TOP]
    Settings:
    - Convert: RGB to HSV
    - Output: HSV in RGB channels
    ↓
[HSL approximation (HSV with adjusted saturation)]
```

**Note:** For most effects, HSV works as a close approximation to HSL.

#### HSL to RGB

```
[HSL/HSV Input]
    ↓
[HSV Convert TOP]
    Settings:
    - Convert: HSV to RGB
    ↓
[RGB Output]
```

### Utility 2: Distance from Center

**Network:**
```
[Ramp TOP (Horizontal: 0 to 1)]
    ↓
[Math TOP: (value - 0.5) → centered_u]

[Ramp TOP (Vertical: 0 to 1)]
    ↓
[Math TOP: (value - 0.5) → centered_v]

[Composite TOP]
    - Add: centered_u² + centered_v²
    ↓
[Math TOP: sqrt()]
    ↓
[Distance TOP (0 = center, ~0.707 = corners)]
```

### Utility 3: Angle from Center

**Network:**
```
[Ramp TOP (Horizontal: 0 to 1)]
    ↓
[Math TOP: value - 0.5]
    ↓
[u_centered]

[Ramp TOP (Vertical: 0 to 1)]
    ↓
[Math TOP: value - 0.5]
    ↓
[v_centered]

[Edge TOP or GLSL TOP with atan2]
    ↓
[Angle TOP (0 to 2π or 0 to 1 normalized)]
```

---

## Effect Implementations

### Effect 1: Sparkle

Random pixels flash white briefly.

**Network:**
```
[Noise TOP]
    Settings:
    - Type: White Noise (or Random)
    - Seed: absTime.seconds × 100 (animated)
    - Monochrome: On
    ↓
[Threshold TOP]
    Settings:
    - Threshold: 0.98 (only top 2% pass)
    - Soft Edge: 0.02
    ↓
[Trail TOP]
    Settings:
    - Trail Length: 0.3 seconds (fade duration)
    ↓
[Level TOP]
    Settings:
    - Output Black: 0
    - Output White: 1
    - Gamma: 2 (sharpen sparkles)
    ↓
[Composite TOP (Over base color)]
```

---

### Effect 2: Rainbow Sweep

Full spectrum sweeps across space.

**Network:**
```
[Ramp TOP (Horizontal)]
    ↓
[u_coord]

[Ramp TOP (Vertical)]
    ↓
[v_coord]

[Composite TOP (Add: u + v)]
    ↓
[Math TOP]
    Expression: (value + absTime.seconds × speed × 2) × 0.5
    ↓
[Math TOP (fract - get fractional part)]
    ↓
[Ramp TOP (Rainbow gradient: ROYGBIV)]
    Settings:
    - Type: Horizontal Gradient
    - Colors: Red → Orange → Yellow → Green → Cyan → Blue → Magenta → Red
    ↓
[Lookup TOP]
    Input: fract result
    Lookup: Rainbow Ramp
```

**Simpler Version:**
```
[Ramp TOP (Rainbow gradient)]
    ↓
[Transform TOP]
    Settings:
    - Translate X: absTime.seconds × speed × -0.1
    - Extend: Repeat
    ↓
[Output]
```

---

### Effect 3: Fire

Flickering warm colors with upward bias.

**Network:**
```
[Ramp TOP (Vertical)]
    Settings:
    - Bottom: 1 (hot)
    - Top: 0 (cool)
    ↓
[height_gradient]

[Noise TOP]
    Settings:
    - Type: Turbulence
    - Amplitude: 0.3
    - Period: 5, 5, absTime.seconds × 5
    - Harmonics: 3
    ↓
[flicker_noise]

[Composite TOP (Add)]
    Input 1: height_gradient
    Input 2: flicker_noise
    ↓
[Ramp TOP - Fire Gradient]
    Position 0.0: RGB(0.3, 0, 0)      - Dark Red
    Position 0.3: RGB(1, 0.2, 0)      - Red
    Position 0.7: RGB(1, 0.6, 0.2)    - Orange
    Position 1.0: RGB(1, 1, 0.4)      - Yellow
    ↓
[Lookup TOP]
    ↓
[Level TOP (Brightness modulation)]
```

---

### Effect 4: Plasma

Multi-sine wave interference pattern.

**Network:**
```
[Ramp TOP (Horizontal)] → [Math: × 10 + time] → [Pattern: Sine] → wave1

[Ramp TOP (Vertical)] → [Math: × 10 - time × 0.7] → [Pattern: Sine] → wave2

[Ramp (Horizontal + Vertical)] → [Math: × 8 + time × 0.5] → [Pattern: Sine] → wave3

[Distance from center] → [Math: × 20 + time] → [Pattern: Sine] → wave4

[Composite TOP (Add all waves)]
    ↓
[Level TOP]
    Settings:
    - Input Range: -4 to 4 (4 waves: -1 to 1 each)
    - Output Range: 0 to 1
    ↓
[Ramp TOP (Rainbow gradient)]
    ↓
[Lookup TOP]
```

**Pattern TOP Settings:**
- Type: Sine
- Period: 1 (waves are pre-scaled in Math TOP)
- Phase: 0

---

### Effect 5: Kaleidoscope

Mirror colors with rotational symmetry.

**Network:**
```
[Ramp TOP (Horizontal)]
    ↓
[Math TOP: abs(value - 0.5)]
    ↓
[mirror_u]

[Ramp TOP (Vertical)]
    ↓
[Math TOP: abs(value - 0.5)]
    ↓
[mirror_v]

[Angle from Center TOP]
    ↓
[Math TOP]
    Expression: (angle × 6) mod (2π)  ← 6-fold symmetry
    Then normalize to 0-1
    ↓
[segmented_angle]

[Distance from center]
    ↓
[Math TOP: × 0.1]
    ↓
[distance_component]

[Composite TOP (Add)]
    Input: segmented_angle + distance_component
    ↓
[Math TOP (mod 1.0)]
    ↓
[Ramp TOP (Hue gradient)]
    Settings:
    - Saturation: 0.9
    ↓
[Lookup TOP]
```

---

### Effect 6: Breath

Slow saturation oscillation.

**Network:**
```
[Timer CHOP]
    ↓
[Math CHOP]
    Expression: sin(absTime.seconds × speed × 0.5)
    ↓
[Math CHOP]
    Expression: (value + 1) / 2  ← Range 0-1
    ↓
[Math CHOP]
    Expression: 0.3 + value × 0.7  ← Range 0.3-1.0
    ↓
[CHOP to TOP: breath_cycle]

[Base Color]
    ↓
[HSV Convert TOP (RGB → HSV)]
    ↓
[Channel Mix TOP]
    Settings:
    - R: Pass through (Hue)
    - G: Replace with breath_cycle (Saturation)
    - B: Pass through (Value)
    ↓
[HSV Convert TOP (HSV → RGB)]
```

---

### Effect 7: Color Chase

Moving wave of color across grid.

**Network:**
```
[Ramp TOP (Horizontal)]
    ↓
[Math TOP: × 3 + absTime.seconds × speed × 3]
    ↓
[Pattern TOP (Sine)]
    ↓
[wave_u]

[Ramp TOP (Vertical)]
    ↓
[Math TOP: × 3 + absTime.seconds × speed × 3 + π]
    ↓
[Pattern TOP (Sine)]
    ↓
[wave_v]

[Composite TOP (Average)]
    Input: wave_u + wave_v, Output: / 2
    ↓
[Level TOP (Map to 0-1)]
    ↓
[Ramp TOP (Hue gradient)]
    ↓
[Lookup TOP]
```

---

### Effect 8-11: Wave Effects

#### Wave Multi (Multiple Interference Sources)

**Concept:** Create distance fields from multiple points, apply sine waves, average results.

**Network:**
```
[Create 3 distance fields from different UV points]
    Point 1: (0.25, 0.25)
    Point 2: (0.75, 0.25)
    Point 3: (0.5, 0.75)

For each:
    [Distance from point]
        ↓
    [Math: × 10 - time × 2]
        ↓
    [Pattern: Sine]

[Composite TOP (Add all 3)]
    ↓
[Math TOP: / 3 (average)]
    ↓
[Level TOP (to 0-1 range)]
    ↓
[Lookup (Hue ramp)]
```

#### Wave Vertical

**Network:**
```
[Ramp TOP (Vertical)]
    ↓
[Math TOP: × 10 - absTime.seconds × speed × 2]
    ↓
[Pattern TOP (Sine)]
    ↓
[Level TOP (to 0-1)]
    ↓
[Lookup (Hue ramp)]
```

#### Wave Circular

**Network:**
```
[Distance from center (0.5, 0.5)]
    ↓
[Math TOP: × 15 - absTime.seconds × speed × 3]
    ↓
[Pattern TOP (Sine)]
    ↓
[Level TOP (to 0-1)]
    ↓
[Lookup (Hue ramp)]
```

#### Wave Standing

**Network:**
```
[Ramp (Horizontal)]
    ↓
[Math: × 10]
    ↓
[Pattern (Sine)]
    ↓
[wave_u]

[Ramp (Vertical)]
    ↓
[Math: × 10]
    ↓
[Pattern (Sine)]
    ↓
[wave_v]

[Timer CHOP]
    ↓
[Math CHOP: sin(time × speed × 2)]
    ↓
[CHOP to TOP: time_factor]

[Multiply TOP]
    Input: wave_u × wave_v × time_factor
    ↓
[Level TOP (to 0-1)]
    ↓
[Lookup (Hue ramp)]
```

---

### Effect 12: Cycle Hue

Smooth hue rotation over time.

**Network:**
```
[Base Color]
    ↓
[HSV Convert TOP (RGB → HSV)]
    ↓
[Channel Mix TOP]
    Extract H channel (R)
    ↓
[Math TOP]
    Expression: (value + absTime.seconds × speed × 0.2) mod 1.0
    ↓
[Channel Mix TOP]
    Replace H channel (R) with result
    ↓
[HSV Convert TOP (HSV → RGB)]
```

---

### Effect 13-16: Pulse Effects

#### Pulse Radial

Pulse emanating from center.

**Network:**
```
[Distance from center]
    ↓
[Math TOP]
    Expression: sin(absTime.seconds × speed × 3 - value × 0.2)
    ↓
[Level TOP]
    Input Range: -1 to 1
    Output Range: 0.2 to 1.0 (brightness range)
    ↓
[Base Color]
    ↓
[HSV Convert (RGB → HSV)]
    ↓
[Multiply TOP]
    Apply brightness to V channel
    ↓
[HSV Convert (HSV → RGB)]
```

#### Pulse Alternating

Different sectors pulse out of phase.

**Network:**
```
[Angle from center]
    ↓
[Math TOP]
    Expression: floor(angle / (π/4))  ← 8 sectors
    Then: sector × π/4 = phase offset
    ↓
[Math TOP]
    Expression: sin(absTime.seconds × speed × 2 + phase)
    ↓
[Apply to brightness (same as Pulse Radial)]
```

#### Pulse Layered

Each vertical layer pulses with different phase.

**Network:**
```
[Ramp TOP (Vertical: 0-1)]
    ↓
[Math TOP]
    Expression: sin(absTime.seconds × speed × 2 + value × 15)
    ↓
[Level TOP (to 0.2-1.0 brightness)]
    ↓
[Apply to base color brightness]
```

#### Pulse Beat

Double-pulse heartbeat effect.

**Network:**
```
[Timer CHOP]
    ↓
[Script CHOP]
    def onCook(chopOp):
        t = (absTime.seconds * parent().par.Speed) % 2.0

        if t < 0.3:
            pulse = sin(t * 33.333)  # First beat
        elif t < 0.7:
            pulse = sin((t - 0.3) * 26.666)  # Second beat
        else:
            pulse = 0  # Rest

        chopOp[0][0] = (pulse + 1) / 2
    ↓
[CHOP to TOP: beat_brightness]
    ↓
[Apply to base color brightness]
```

---

### Effect 17-19: Static/Noise Effects

#### Static Color

Random color per pixel, animated.

**Network:**
```
[Noise TOP]
    Settings:
    - Type: White Noise
    - Seed: floor(absTime.seconds × speed × 10)
    - Monochrome: Off
    ↓
[Ramp TOP (Hue spectrum)]
    ↓
[Lookup TOP]
```

#### Static Dynamic

Static that pulses in brightness.

**Network:**
```
[Noise TOP]
    Settings:
    - Type: White Noise
    - Seed: Fixed (non-animated)
    - Monochrome: On
    ↓
[noise_pattern]

[Timer CHOP]
    ↓
[Math CHOP: sin(time × speed × 3)]
    ↓
[Math CHOP: (value + 1) / 2]
    ↓
[CHOP to TOP: pulse]

[Multiply TOP]
    Input: noise_pattern × pulse
    ↓
[Apply to brightness]
```

#### Static Wave

Traveling noise pattern.

**Network:**
```
[Noise TOP]
    Settings:
    - Type: Perlin
    - Period: 5, 5, 1
    - Animated: Off
    ↓
[Transform TOP]
    Settings:
    - Translate X: absTime.seconds × speed × 0.3
    - Extend: Repeat
    ↓
[Ramp TOP (Hue gradient)]
    ↓
[Lookup TOP]
```

---

### Effect 20-21: Scrolling Effects

#### Scrolling Strobe

Moving bright/dark band.

**Network:**
```
[Ramp TOP]
    Direction: Based on scroll direction parameter
    - Y: Vertical
    - X: Horizontal
    - Diagonal: Custom
    ↓
[position_gradient]

[Timer CHOP]
    ↓
[Math CHOP]
    Expression: (absTime.seconds × speed × 0.2) mod 1.0
    ↓
[CHOP to TOP: band_position]

[Math TOP]
    Expression: abs(position_gradient - band_position)
    ↓
[distance_from_band]

[Threshold TOP]
    Settings:
    - Threshold: thickness_param / 100
    - Above Threshold: 0
    - Below Threshold: 1
    ↓
[in_band_mask]

[Switch TOP or Composite]
    If scrollInvert = 0:
        in_band = white, outside = base_color
    If scrollInvert = 1:
        in_band = black, outside = base_color
```

**For multiple directions:**
```
[Select CHOP: direction parameter]
    ↓
[Switch TOP]
    Input 0: Vertical Ramp
    Input 1: Horizontal Ramp
    Input 2: Diagonal Ramp (U+V)/2
    Input 3: Radial (distance from center)
```

#### Scrolling Pulse

Scrolling band with soft falloff and brightness pulse.

**Network:**
```
[distance_from_band] (from Scrolling Strobe)
    ↓
[Math TOP]
    Expression: 1 - (value / thickness)
    ↓
[Math TOP: clamp(value, 0, 1)]
    ↓
[falloff]

[Timer CHOP]
    ↓
[Math CHOP: sin(absTime.seconds × speed × 5)]
    ↓
[Math CHOP: 0.5 + (value + 1) × 0.25]  ← Range 0.5-1.0
    ↓
[CHOP to TOP: pulse]

[Multiply TOP]
    Input: falloff × pulse
    ↓
[brightness_modulation]

[Apply to base color]
    If scrollInvert = 0: Brighten in band
    If scrollInvert = 1: Darken in band
```

---

## Parameter Control

### Master Control Panel

**Create Container COMP:** `colorEffects_control`

**Custom Parameters:**

```python
# In the component's parameter panel, create custom pages

# Effect Page
page = comp.appendCustomPage('Effect')

p = page.appendMenu('Effecttype', label='Effect Type')
p.menuNames = ['none', 'sparkle', 'rainbowSweep', 'fire', 'plasma',
               'kaleidoscope', 'breath', 'colorChase', 'waveMulti',
               'waveVertical', 'waveCircular', 'waveStanding', 'cycleHue',
               'pulseRadial', 'pulseAlternating', 'pulseLayered', 'pulseBeat',
               'staticColor', 'staticDynamic', 'staticWave',
               'scrollingStrobe', 'scrollingPulse']
p.menuLabels = [n.title() for n in p.menuNames]
p.default = 0

p = page.appendFloat('Intensity', label='Intensity')
p.min = 0.0
p.max = 1.0
p.default = 1.0
p.clampMin = True
p.clampMax = True

p = page.appendFloat('Speed', label='Speed')
p.min = 0.1
p.max = 5.0
p.default = 1.0

# Scrolling Page
page = comp.appendCustomPage('Scrolling')

p = page.appendFloat('Scrollthickness', label='Scroll Thickness')
p.min = 1
p.max = 100
p.default = 10

p = page.appendMenu('Scrolldirection', label='Scroll Direction')
p.menuNames = ['vertical', 'horizontal', 'diagonal', 'radial']
p.menuLabels = ['Vertical', 'Horizontal', 'Diagonal', 'Radial']
p.default = 0

p = page.appendToggle('Scrollinvert', label='Scroll Invert')
p.default = False

# Base Color Page
page = comp.appendCustomPage('Color')

p = page.appendRGB('Basecolor', label='Base Color')
p.default = (0.5, 0.5, 0.5)
```

### Effect Selector Switch

**Network:**
```
/effects
    /sparkle [OUT: sparkle_out]
    /rainbowSweep [OUT: rainbow_out]
    /fire [OUT: fire_out]
    ... (all effects)

    /switch_effects [Switch TOP]
        Input 0: null (none)
        Input 1: sparkle_out
        Input 2: rainbow_out
        Input 3: fire_out
        ... (all effects)

        Index: parent.colorEffects_control.par.Effecttype.menuIndex

    /composite_final [Composite TOP]
        Input 1: base_color
        Input 2: switch_effects output
        Operation: Over
        Opacity: parent.colorEffects_control.par.Intensity
```

---

## Applying to Geometry

### Method 1: Material MAT

**Network:**
```
[Effect Output TOP]
    ↓
[Phong MAT or PBR MAT]
    Color Map: effect_output_TOP
    ↓
[Geometry COMP]
    Material: phong1
```

### Method 2: Instance Color

For instanced geometry:

```
[Effect Output TOP]
    ↓
[TOP to CHOP]
    ↓
[Instance SOP]
    Color: CHOP reference
```

### Method 3: Vertex Colors

```
[Effect Output TOP]
    ↓
[UV Unwrap SOP] (if needed)
    ↓
[Attribute Create SOP]
    Name: Cd (color)
    Value: Sample from TOP
```

---

## Optimization Tips

### 1. Resolution Management

**Recommendation:**
- Effect TOPs: 512×512 (balanced quality/performance)
- Noise TOPs: 256×256 (sufficient detail)
- Final composite: 1024×1024 (if needed for quality)

**Network:**
```
[Low-res effects (512×512)]
    ↓
[Composite/Process]
    ↓
[Resize TOP to final resolution]
```

### 2. Cooking Optimization

**Cook on Demand:**
```
[Effect TOPs]
    Settings:
    - Cooking: Selective (only cooks when output is used)

[Switch TOP]
    - Only active input cooks
    - Inactive effects don't waste GPU
```

### 3. Caching Static Elements

**For non-time-dependent parts:**
```
[Ramp TOP (UV gradient)]
    ↓
[Cache TOP]
    Settings:
    - Cache Mode: Current Frame
    - Only updates when upstream changes
```

### 4. Network Organization

**Recommended structure:**
```
/project1
    /control
        colorEffects_control (COMP with parameters)

    /utilities
        hsv_convert (reusable converters)
        distance_calc
        angle_calc
        time_control

    /effects
        sparkle (COMP)
        rainbowSweep (COMP)
        fire (COMP)
        ... (each effect as container)

    /output
        switch_effects
        composite_final
        output_null
```

### 5. GPU Memory Management

**Monitor usage:**
- Open Performance Monitor (Alt+Y)
- Check GPU Memory tab
- Aim for <50% usage for stable performance

**Reduce memory:**
- Use 8-bit textures (not 16-bit) unless needed
- Enable texture compression where applicable
- Limit simultaneous active effects

---

## Troubleshooting

### Issue: Colors look washed out
**Solutions:**
- Check Level TOP output ranges (0-1)
- Verify composite blend modes
- Use HSV instead of HSL if conversion looks off
- Check Gamma settings (should be 1.0 unless intentional)

### Issue: Effects not animating
**Solutions:**
- Verify Timer CHOP is playing
- Check absTime.seconds is being used correctly
- Ensure speed parameter is applied
- Check for Manual Cook mode (should be Selective)

### Issue: Banding or artifacts
**Solutions:**
- Increase texture resolution
- Enable dithering in Level TOPs
- Use 16-bit textures if 8-bit shows banding
- Check for proper normalization (0-1 ranges)

### Issue: Performance drops
**Solutions:**
- Lower texture resolution (512×512 or 256×256)
- Use Cache TOPs on static elements
- Disable unused effect branches with Switch TOP
- Check GPU usage in Performance Monitor
- Reduce noise octaves/harmonics

### Issue: UV mapping incorrect
**Solutions:**
- Check geometry has proper UVs (UV Unwrap SOP)
- Verify UV layout in Geometry Viewer
- Use default UVs for simple effects
- Check Material MAP settings reference correct TOP

---

## Complete Workflow Example

### Setup: Rainbow Sweep Effect

**Step 1: Create structure**
```
/effects/rainbowSweep (Container COMP)
```

**Step 2: Inside rainbowSweep, create network**

```
1. [Ramp TOP: 'ramp_u']
   - Direction: Horizontal
   - Output: Mono

2. [Ramp TOP: 'ramp_v']
   - Direction: Vertical
   - Output: Mono

3. [Composite TOP: 'combine_uv']
   - Input 1: ramp_u
   - Input 2: ramp_v
   - Operation: Add
   - Monochrome: On

4. [Math TOP: 'add_time']
   - Input: combine_uv
   - Expression: (absTime.seconds × parent.parent.colorEffects_control.par.Speed × 2)
   - Combine: Add

5. [Math TOP: 'scale']
   - Input: add_time
   - Expression: 0.5
   - Combine: Multiply

6. [Math TOP: 'fract']
   - Input: scale
   - Expression: fract(input)  # Get fractional part

7. [Ramp TOP: 'rainbow']
   - Type: Gradient
   - Colors:
     Position 0.0: Red (1, 0, 0)
     Position 0.17: Orange (1, 0.5, 0)
     Position 0.33: Yellow (1, 1, 0)
     Position 0.5: Green (0, 1, 0)
     Position 0.67: Cyan (0, 1, 1)
     Position 0.83: Blue (0, 0, 1)
     Position 1.0: Red (1, 0, 0)

8. [Lookup TOP: 'apply_rainbow']
   - Input: fract
   - Lookup: rainbow

9. [Null TOP: 'OUT']
   - Input: apply_rainbow
```

**Step 3: Wire to master switch**

In `/effects`:
```
[Switch TOP: 'effects_switch']
    Input 2: rainbowSweep/OUT
    Index: parent.colorEffects_control.par.Effecttype.menuIndex
```

**Step 4: Final composite**

```
[Constant TOP: 'base_color']
    Color: parent.colorEffects_control.par.Basecolor
    ↓
[Composite TOP: 'final']
    Input 1: base_color
    Input 2: effects_switch
    Operation: Over
    Opacity: parent.colorEffects_control.par.Intensity
    ↓
[Null TOP: 'OUTPUT']
```

**Step 5: Apply to geometry**

```
[Geometry COMP]
    ↓
[Phong MAT: 'color_mat']
    Color Map: effects/OUTPUT
    ↓
[Render TOP]
```

---

### Example 2: Plasma Effect (Wave Interference)

**Demonstrates:** Multiple wave sources, composite blending, pattern generation

**Step 1: Create structure**
```
/effects/plasma (Container COMP)
```

**Step 2: Build wave sources**

Inside `/effects/plasma`:

```
1. [Ramp TOP: 'ramp_u']
   - Direction: Horizontal
   - Output: Mono

2. [Ramp TOP: 'ramp_v']
   - Direction: Vertical
   - Output: Mono

3. [Composite TOP: 'ramp_uv']
   - Operation: Add
   - Input 1: ramp_u
   - Input 2: ramp_v
   - Monochrome: On

4. [Math TOP: 'wave1_prep']
   - Input: ramp_u
   - Expression: absTime.seconds * parent.parent.colorEffects_control.par.Speed
   - Combine: Add
   - Then multiply by 10

5. [Pattern TOP: 'wave1']
   - Input: wave1_prep
   - Type: Sine
   - Period: 1
   - Phase: 0

6. [Math TOP: 'wave2_prep']
   - Input: ramp_v
   - Expression: absTime.seconds * parent.parent.colorEffects_control.par.Speed * -0.7
   - Combine: Add
   - Then multiply by 10

7. [Pattern TOP: 'wave2']
   - Input: wave2_prep
   - Type: Sine

8. [Math TOP: 'wave3_prep']
   - Input: ramp_uv
   - Expression: absTime.seconds * parent.parent.colorEffects_control.par.Speed * 0.5
   - Combine: Add
   - Then multiply by 8

9. [Pattern TOP: 'wave3']
   - Input: wave3_prep
   - Type: Sine
```

**Step 3: Create radial wave (use utility component)**

```
10. [Reference: '/utilities/distance_calc' → 'dist_center']
    (Reuse utility from base architecture)

11. [Math TOP: 'wave4_prep']
    - Input: dist_center
    - Expression: absTime.seconds * parent.parent.colorEffects_control.par.Speed
    - Combine: Add
    - Then multiply by 20

12. [Pattern TOP: 'wave4']
    - Input: wave4_prep
    - Type: Sine
```

**Step 4: Combine all waves**

```
13. [Composite TOP: 'combine_waves']
    - Operation: Add
    - Input 1: wave1
    - Input 2: wave2
    - Input 3: wave3
    - Input 4: wave4
    - Monochrome: On

14. [Level TOP: 'normalize']
    - Input: combine_waves
    - Input Range: -4 to 4 (4 waves @ -1 to 1 each)
    - Output Range: 0 to 1
    - Output Black: 0
    - Output White: 1
```

**Step 5: Apply rainbow gradient**

```
15. [Ramp TOP: 'rainbow']
    - Type: Gradient
    - Direction: Horizontal
    - Colors (same as rainbow sweep example)

16. [Lookup TOP: 'apply_color']
    - Input: normalize
    - Lookup: rainbow
    - Extend U: Repeat

17. [Null TOP: 'OUT']
    - Input: apply_color
```

**Key Technique:** This demonstrates wave interference - when multiple sine waves combine, they create complex patterns. Adjust wave frequencies and speeds for different plasma styles.

---

### Example 3: Pulse Radial (Distance-Based Animation)

**Demonstrates:** Distance field usage, brightness modulation, HSV manipulation

**Step 1: Create structure**
```
/effects/pulseRadial (Container COMP)
```

**Step 2: Calculate distance from center**

```
1. [Reference: '/utilities/distance_calc' → 'distance']
   (Or build inline:)

   [Ramp TOP: 'ramp_u']
   - Direction: Horizontal
   ↓
   [Math TOP: 'center_u']
   - Expression: 0.5
   - Combine: Subtract (input - 0.5)

   [Ramp TOP: 'ramp_v']
   - Direction: Vertical
   ↓
   [Math TOP: 'center_v']
   - Expression: 0.5
   - Combine: Subtract

   [Composite TOP: 'squared']
   - Operation: Custom
   - Custom: (center_u)² + (center_v)²
   ↓
   [Math TOP: 'distance']
   - Function: sqrt(input)
```

**Step 3: Create pulse wave**

```
2. [Math TOP: 'phase_offset']
   - Input: distance
   - Expression: 0.2
   - Combine: Multiply
   - (This creates spatial phase offset)

3. [Timer CHOP: 'time']
   - Speed: parent.colorEffects_control.par.Speed
   ↓
   [Math CHOP: 'time_scaled']
   - Expression: input * 3
   ↓
   [CHOPto TOP: 'time_top']

4. [Composite TOP: 'combine_phase']
   - Operation: Subtract
   - Input 1: time_top
   - Input 2: phase_offset
   - (time - distance creates outward pulse)

5. [Pattern TOP: 'pulse_wave']
   - Input: combine_phase
   - Type: Sine
   - Period: 6.28318 (2π for full wave)
```

**Step 4: Convert to brightness (0.2 to 1.0 range)**

```
6. [Level TOP: 'brightness']
   - Input: pulse_wave
   - Input Range: -1 to 1
   - Output Range: 0.2 to 1.0
   - Output Black: 0.2
   - Output White: 1.0
```

**Step 5: Apply to base color**

```
7. [Constant TOP: 'base']
   - Color: parent.parent.colorEffects_control.par.Basecolor
   - Resolution: 512×512

8. [HSV Convert TOP: 'rgb_to_hsv']
   - Input: base
   - Convert: RGB to HSV
   - Output: HSV

9. [Channel Mix TOP: 'apply_brightness']
   - Input: rgb_to_hsv
   - Red: Pass (H channel)
   - Green: Pass (S channel)
   - Blue: brightness (V channel - multiply or replace)
   - Operation: Multiply Blue

10. [HSV Convert TOP: 'hsv_to_rgb']
    - Input: apply_brightness
    - Convert: HSV to RGB

11. [Null TOP: 'OUT']
    - Input: hsv_to_rgb
```

**Key Technique:** Distance fields create spatial variation. Subtracting distance from time creates waves that radiate outward from center.

---

### Example 4: Scrolling Strobe (Band Movement)

**Demonstrates:** Threshold masking, direction switching, parametric control

**Step 1: Create structure**
```
/effects/scrollingStrobe (Container COMP)
```

**Step 2: Create direction ramps**

```
1. [Ramp TOP: 'ramp_vertical']
   - Direction: Vertical
   - Output: Mono
   - Name: ramp_v

2. [Ramp TOP: 'ramp_horizontal']
   - Direction: Horizontal
   - Output: Mono
   - Name: ramp_h

3. [Composite TOP: 'ramp_diagonal']
   - Operation: Add
   - Input 1: ramp_v
   - Input 2: ramp_h
   - Monochrome: On
   ↓
   [Math TOP: 'diagonal_normalized']
   - Expression: 0.5
   - Combine: Multiply

4. [Reference: '/utilities/distance_calc' → 'ramp_radial']

5. [Switch TOP: 'direction_selector']
   - Input 0: ramp_v
   - Input 1: ramp_h
   - Input 2: diagonal_normalized
   - Input 3: ramp_radial
   - Index: parent.parent.colorEffects_control.par.Scrolldirection.menuIndex
```

**Step 3: Create moving band position**

```
6. [Timer CHOP: 'time']
   - Speed: parent.parent.colorEffects_control.par.Speed
   ↓
   [Math CHOP: 'band_pos']
   - Expression: (absTime.seconds * 0.2) % 1.0
   ↓
   [CHOPto TOP: 'band_position']
```

**Step 4: Calculate distance from band**

```
7. [Math TOP: 'dist_from_band']
   - Input 1: direction_selector
   - Input 2: band_position
   - Combine: Subtract
   ↓
   [Math TOP: 'abs_dist']
   - Function: abs(input)
```

**Step 5: Create threshold mask**

```
8. [Math TOP: 'thickness_normalized']
   - Constant: parent.parent.colorEffects_control.par.Scrollthickness
   - Combine: Divide by 100
   - (Converts thickness param 1-100 to 0-1 range)

9. [Threshold TOP: 'band_mask']
   - Input: abs_dist
   - Threshold: thickness_normalized
   - Above Threshold: 0 (black - outside band)
   - Below Threshold: 1 (white - inside band)
   - Soft Edge: 0.01
```

**Step 6: Apply invert and composite**

```
10. [Math TOP: 'invert_check']
    - Input: band_mask
    - If parent.parent.colorEffects_control.par.Scrollinvert == 1:
      - Function: 1 - input (invert)
    - Else:
      - Pass through

11. [Constant TOP: 'base']
    - Color: parent.parent.colorEffects_control.par.Basecolor

12. [Constant TOP: 'white']
    - Color: RGB(1, 1, 1)

13. [Switch TOP: 'color_select']
    - Input 0: white (normal - band is bright)
    - Input 1: Constant(0,0,0) (inverted - band is dark)
    - Index: parent.parent.colorEffects_control.par.Scrollinvert

14. [Composite TOP: 'final']
    - Input 1: base
    - Input 2: color_select
    - Operation: Over (or Mix)
    - Mask: invert_check (band mask)

15. [Null TOP: 'OUT']
    - Input: final
```

**Key Technique:** Threshold creates hard-edged masks. Switch TOPs enable parametric direction control without duplicating networks.

---

### Example 5: Fire Effect (Noise + Gradient)

**Demonstrates:** Noise animation, gradient lookup, vertical bias

**Step 1: Create structure**
```
/effects/fire (Container COMP)
```

**Step 2: Create vertical gradient (hot at bottom)**

```
1. [Ramp TOP: 'height_ramp']
   - Direction: Vertical
   - Type: Linear
   - Start: 1 (bottom - hot)
   - End: 0 (top - cool)
   - Output: Mono
```

**Step 3: Create animated turbulent noise**

```
2. [Noise TOP: 'turbulence']
   - Type: Turbulence
   - Amplitude: 0.3
   - Frequency: 5, 5, 1
   - Harmonics: 3
   - Period X: 5
   - Period Y: 5
   - Period Z: absTime.seconds * parent.parent.colorEffects_control.par.Speed * 5
   - (Animate period Z for moving flicker)
   - Resolution: 512×512
   - Monochrome: On
```

**Step 4: Combine height gradient with noise**

```
3. [Composite TOP: 'combine']
   - Operation: Add
   - Input 1: height_ramp (70% weight)
   - Input 2: turbulence (30% weight)
   - Blend: Can adjust via Level TOPs

   Alternative using Level TOP:
   [Level TOP: 'scale_noise']
   - Input: turbulence
   - Brightness: 0.3
   ↓
   [Composite TOP: 'combine']
   - Operation: Add
   - Input 1: height_ramp
   - Input 2: scale_noise
```

**Step 5: Create fire color gradient**

```
4. [Ramp TOP: 'fire_colors']
   - Type: Gradient
   - Direction: Horizontal
   - Colors:
     Position 0.0: RGB(0.3, 0.0, 0.0)    # Dark red/ember
     Position 0.3: RGB(1.0, 0.2, 0.0)    # Red
     Position 0.7: RGB(1.0, 0.6, 0.2)    # Orange
     Position 1.0: RGB(1.0, 1.0, 0.4)    # Yellow/white hot
   - Interpolation: Cubic
```

**Step 6: Apply color lookup**

```
5. [Lookup TOP: 'apply_fire']
   - Input: combine
   - Lookup: fire_colors
   - Extend U: Clamp
   - Extend V: Clamp

6. [Level TOP: 'brightness_adjust']
   - Input: apply_fire
   - Brightness: 1.1 (slightly brighten)
   - Contrast: 1.2 (increase contrast)

7. [Null TOP: 'OUT']
   - Input: brightness_adjust
```

**Key Technique:** Combining gradient (spatial) with noise (detail) creates organic movement. Turbulence noise with animated Z-period creates flickering effect.

---

### Example 6: Wave Circular (Radial Expansion)

**Demonstrates:** Distance field, sine patterns, expanding circles

**Step 1: Create structure**
```
/effects/waveCircular (Container COMP)
```

**Step 2: Calculate distance from center (reuse utility)**

```
1. [Reference: '/utilities/distance_calc' → 'distance']
   (Creates 0 at center, ~0.707 at corners)
```

**Step 3: Scale and animate distance**

```
2. [Math TOP: 'scale_distance']
   - Input: distance
   - Expression: 15
   - Combine: Multiply
   - (Controls wave frequency - higher = more rings)

3. [Timer CHOP: 'time']
   ↓
   [Math CHOP: 'time_scaled']
   - Expression: absTime.seconds * parent.colorEffects_control.par.Speed * 3
   ↓
   [CHOPto TOP: 'time_top']

4. [Composite TOP: 'animated_distance']
   - Operation: Subtract
   - Input 1: scale_distance
   - Input 2: time_top
   - (distance - time creates outward expansion)
```

**Step 4: Create sine wave pattern**

```
5. [Pattern TOP: 'wave']
   - Input: animated_distance
   - Type: Sine
   - Period: 6.28318 (2π)
   - Amplitude: 1.0
   - Offset: 0
```

**Step 5: Normalize and apply color**

```
6. [Level TOP: 'normalize']
   - Input: wave
   - Input Range: -1 to 1
   - Output Range: 0 to 1

7. [Ramp TOP: 'hue_gradient']
   - Type: Gradient
   - Rainbow spectrum or custom

8. [Lookup TOP: 'apply_color']
   - Input: normalize
   - Lookup: hue_gradient
   - Extend U: Repeat

9. [Null TOP: 'OUT']
   - Input: apply_color
```

**Variation: Contracting Circles**
```
Change step 4 to:
[Composite TOP: 'animated_distance']
- Operation: Add (instead of Subtract)
- Input 1: scale_distance
- Input 2: time_top
- (distance + time creates inward contraction)
```

**Key Technique:** Subtracting time from distance creates outward motion. Multiplier on distance controls ring density.

---

### Example 7: Complete Utility Setup

**For reusable components referenced in examples above**

**Create:** `/utilities` (Container COMP)

**Inside `/utilities`:**

#### Distance Calculator

```
/utilities/distance_calc (Container COMP)

Inside:
1. [Ramp TOP: 'u']
   - Direction: Horizontal
   - Resolution: 512×512

2. [Math TOP: 'u_centered']
   - Input: u
   - Expression: 0.5
   - Combine: Subtract

3. [Math TOP: 'u_squared']
   - Input: u_centered
   - Function: input²

4. [Ramp TOP: 'v']
   - Direction: Vertical

5. [Math TOP: 'v_centered']
   - Input: v
   - Expression: 0.5
   - Combine: Subtract

6. [Math TOP: 'v_squared']
   - Input: v_centered
   - Function: input²

7. [Composite TOP: 'sum_squares']
   - Operation: Add
   - Input 1: u_squared
   - Input 2: v_squared
   - Monochrome: On

8. [Math TOP: 'distance']
   - Input: sum_squares
   - Function: sqrt(input)

9. [Null TOP: 'OUT']
   - Input: distance
```

**Usage in effects:**
```
[In /effects/anyEffect]
[In TOP: 'my_distance']
- Reference: /utilities/distance_calc/OUT
```

#### Time Controller

```
/utilities/time_control (Container COMP)

Inside:
1. [Timer CHOP: 'timer']
   - Initialize: On
   - Play: On
   - Speed: 1.0
   - Length: 10000

2. [Null CHOP: 'time_out']
   - Input: timer

3. [CHOPto TOP: 'time_top']
   - CHOP: time_out
   - Channel: seconds
   - Resolution: 1×1

4. [Null TOP: 'OUT']
   - Input: time_top
```

**Usage:** Reference `absTime.seconds` or `op('/utilities/time_control/time_out')[0]`

---

## Next Steps

1. **Start Simple:** Build Rainbow Sweep effect following example above
2. **Build Utilities:** Create distance_calc and time_control components first
3. **Try Plasma:** Demonstrates wave interference - visually impressive
4. **Test Each:** Apply to a basic sphere or box geometry
5. **Build Library:** Create one effect at a time as separate COMPs
6. **Master Control:** Set up parameter panel for all effects
7. **Optimize:** Use Switch TOP to disable inactive effects
8. **Experiment:** Modify parameters in real-time to understand behavior

**Recommended Build Order:**
1. Rainbow Sweep (simplest - ramps + lookup)
2. Wave Circular (distance field basics)
3. Pulse Radial (brightness modulation)
4. Plasma (multiple waves + interference)
5. Fire (noise + gradients)
6. Scrolling Strobe (masking + parameters)

This TOP-based approach provides full visual control and makes it easy to experiment with color effects without shader programming!
