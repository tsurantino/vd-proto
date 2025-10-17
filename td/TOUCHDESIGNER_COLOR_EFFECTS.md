# TouchDesigner Color Effects Implementation
## GLSL Shaders & Component Networks

This guide provides complete GLSL shader implementations and TouchDesigner network architectures for all color effects used in the volumetric display system.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Network Architecture](#network-architecture)
3. [GLSL Shader Library](#glsl-shader-library)
4. [3D Gradient Mapping](#3d-gradient-mapping)
5. [Effect Implementations](#effect-implementations)
6. [Parameter Control](#parameter-control)
7. [Optimization](#optimization)

---

## System Overview

### Color Effect Pipeline

```
[Particle System / Volume]
         ↓
[Instance/Geometry Rendering]
         ↓
[GLSL Pixel Shader - Color Effects]
         ↓
[Post-Processing (optional)]
         ↓
[Final Output]
```

### Effect Categories

1. **Gradient Mapping** - Spatial color mapping (linear, radial, cylindrical)
2. **Wave Effects** - Sine-wave based color animations
3. **Cycle Effects** - Color cycling and rotation
4. **Pulse Effects** - Brightness/saturation pulsing
5. **Noise Effects** - Procedural noise patterns
6. **Combination Effects** - Multi-layered effects
7. **Scrolling Effects** - Moving bands of color/brightness

---

## Network Architecture

### Master Color Effect Network

```
┌─────────────────────────────────────────────┐
│ Control Panel COMP                          │
│  - Effect Type Menu                         │
│  - Intensity (0-1)                          │
│  - Speed (0-5)                              │
│  - Effect-specific params                   │
└──────────────┬──────────────────────────────┘
               ↓ (CHOPs)
┌─────────────────────────────────────────────┐
│ Parameter Mapper CHOP                       │
│  - Maps UI params to shader uniforms        │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ GLSL Material                               │
│  ┌────────────────────────────────────────┐ │
│  │ Vertex Shader                          │ │
│  │  - Pass through position               │ │
│  │  - Pass UVs and world position         │ │
│  └────────────┬───────────────────────────┘ │
│               ↓                              │
│  ┌────────────────────────────────────────┐ │
│  │ Pixel Shader                           │ │
│  │  - Effect selection (switch)           │ │
│  │  - Color calculation                   │ │
│  │  - Intensity blending                  │ │
│  └────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────┘
               ↓
         [Render Output]
```

---

## GLSL Shader Library

### Base Vertex Shader

**File:** `colorEffects_vertex.glsl`

```glsl
// ColorEffects Vertex Shader
// Pass-through with world position

uniform mat4 uTDMats[4];

in vec3 P; // Position
in vec3 N; // Normal
in vec2 uv; // UV coordinates

out vec3 worldPos;
out vec3 normal;
out vec2 texCoord;

void main() {
    // World position for 3D effects
    vec4 worldPosition = uTDMats[2] * vec4(P, 1.0);
    worldPos = worldPosition.xyz;

    // Transform normal
    normal = normalize((uTDMats[3] * vec4(N, 0.0)).xyz);

    // Pass through UV
    texCoord = uv;

    // Final position
    gl_Position = uTDMats[0] * vec4(P, 1.0);
}
```

### Master Pixel Shader

**File:** `colorEffects_pixel.glsl`

```glsl
// ColorEffects Master Pixel Shader

uniform float uTime;
uniform int uEffectType; // 0=none, 1=sparkle, 2=rainbowSweep, etc.
uniform float uIntensity; // 0-1
uniform float uSpeed; // Speed multiplier

// Grid dimensions
uniform vec3 uGridSize; // (gridX, gridY, gridZ)
uniform vec3 uGridCenter; // Center point

// Effect-specific parameters
uniform float uScrollThickness;
uniform int uScrollDirection; // 0=x, 1=y, 2=z, 3=diagonal-xz, etc.
uniform int uScrollInvert; // 0=false, 1=true

// 3D Gradient parameters
uniform int uGradientEnabled;
uniform int uGradientType; // 0=linear-y, 1=linear-x, 2=radial, etc.
uniform vec3 uGradientOrigin;
uniform int uGradientInvert;

// Color stops (up to 8 stops)
uniform int uNumColorStops;
uniform float uColorStopPositions[8];
uniform vec3 uColorStopColors[8]; // RGB normalized 0-1

in vec3 worldPos;
in vec3 normal;
in vec2 texCoord;

out vec4 fragColor;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

// HSL to RGB conversion
vec3 hsl2rgb(vec3 hsl) {
    float h = hsl.x;
    float s = hsl.y;
    float l = hsl.z;

    vec3 rgb;

    if (s == 0.0) {
        rgb = vec3(l);
    } else {
        float q = l < 0.5 ? l * (1.0 + s) : l + s - l * s;
        float p = 2.0 * l - q;

        rgb.r = hue2rgb(p, q, h + 1.0/3.0);
        rgb.g = hue2rgb(p, q, h);
        rgb.b = hue2rgb(p, q, h - 1.0/3.0);
    }

    return rgb;
}

float hue2rgb(float p, float q, float t) {
    if (t < 0.0) t += 1.0;
    if (t > 1.0) t -= 1.0;
    if (t < 1.0/6.0) return p + (q - p) * 6.0 * t;
    if (t < 1.0/2.0) return q;
    if (t < 2.0/3.0) return p + (q - p) * (2.0/3.0 - t) * 6.0;
    return p;
}

// RGB to HSL conversion
vec3 rgb2hsl(vec3 rgb) {
    float maxC = max(max(rgb.r, rgb.g), rgb.b);
    float minC = min(min(rgb.r, rgb.g), rgb.b);
    float l = (maxC + minC) / 2.0;

    float h = 0.0;
    float s = 0.0;

    if (maxC != minC) {
        float d = maxC - minC;
        s = l > 0.5 ? d / (2.0 - maxC - minC) : d / (maxC + minC);

        if (maxC == rgb.r) {
            h = (rgb.g - rgb.b) / d + (rgb.g < rgb.b ? 6.0 : 0.0);
        } else if (maxC == rgb.g) {
            h = (rgb.b - rgb.r) / d + 2.0;
        } else {
            h = (rgb.r - rgb.g) / d + 4.0;
        }
        h /= 6.0;
    }

    return vec3(h, s, l);
}

// Pseudo-random hash function
float hash(vec3 p) {
    p = fract(p * 0.3183099 + 0.1);
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

// 3D Perlin-like noise
float noise3D(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    return mix(
        mix(mix(hash(i + vec3(0,0,0)), hash(i + vec3(1,0,0)), f.x),
            mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
        mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x),
            mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y),
        f.z
    );
}

// ============================================================================
// 3D GRADIENT MAPPING
// ============================================================================

vec3 apply3DGradient(vec3 baseColor) {
    if (uGradientEnabled == 0) {
        return baseColor;
    }

    // Normalize position to 0-1
    vec3 normPos = (worldPos - (uGridCenter - uGridSize * 0.5)) / uGridSize;

    // Calculate gradient parameter t (0-1)
    float t = 0.0;

    if (uGradientType == 0) { // linear-y
        t = normPos.y;
    } else if (uGradientType == 1) { // linear-x
        t = normPos.x;
    } else if (uGradientType == 2) { // linear-z
        t = normPos.z;
    } else if (uGradientType == 3) { // radial/spherical
        vec3 diff = normPos - uGradientOrigin;
        float maxDist = length(max(uGradientOrigin, 1.0 - uGradientOrigin));
        t = min(1.0, length(diff) / maxDist);
    } else if (uGradientType == 4) { // cylindrical
        vec3 diff = normPos - uGradientOrigin;
        float maxDist = length(max(vec2(uGradientOrigin.xz), vec2(1.0) - uGradientOrigin.xz));
        t = min(1.0, length(diff.xz) / maxDist);
    }

    // Apply invert
    if (uGradientInvert == 1) {
        t = 1.0 - t;
    }

    // Interpolate color stops
    vec3 gradientColor = uColorStopColors[0];
    for (int i = 0; i < uNumColorStops - 1; i++) {
        if (t >= uColorStopPositions[i] && t <= uColorStopPositions[i + 1]) {
            float range = uColorStopPositions[i + 1] - uColorStopPositions[i];
            float localT = (t - uColorStopPositions[i]) / range;
            gradientColor = mix(uColorStopColors[i], uColorStopColors[i + 1], localT);
            break;
        }
    }

    return gradientColor;
}

// ============================================================================
// EFFECT FUNCTIONS
// ============================================================================

// SPARKLE: Random voxels flash white
vec3 effectSparkle(vec3 baseColor) {
    float sparkleNoise = noise3D(worldPos * 10.0 + uTime * 100.0);
    float threshold = 0.98; // Only 2% sparkle at any time

    if (sparkleNoise > threshold) {
        float intensity = (sparkleNoise - threshold) / (1.0 - threshold);
        return mix(baseColor, vec3(1.0), intensity);
    }
    return baseColor;
}

// RAINBOW SWEEP: Full spectrum sweep across space
vec3 effectRainbowSweep(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;
    float wave = (normPos.x + normPos.y + normPos.z + uTime * uSpeed * 2.0) * 0.5;
    float hue = fract(wave);
    return hsl2rgb(vec3(hue, 1.0, 0.5));
}

// FIRE: Flickering warm colors with upward bias
vec3 effectFire(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;
    float heightFactor = 1.0 - normPos.y;

    // Flicker using noise
    float flicker = sin(uTime * 5.0 + normPos.x * 3.0 + normPos.z * 3.0) * 0.3 +
                   sin(uTime * 8.0 + normPos.x * 5.0) * 0.2;

    float intensity = (heightFactor * 0.7 + 0.3) + flicker;

    // Fire colors based on height
    float temp = heightFactor + sin(uTime * 3.0 + normPos.y * 10.0) * 0.3;

    vec3 color;
    if (temp > 0.7) {
        color = vec3(1.0, 1.0, 0.4); // Yellow (hot)
    } else if (temp > 0.3) {
        color = vec3(1.0, 0.6, 0.2); // Orange
    } else {
        color = vec3(1.0, 0.2, 0.0); // Red (cooler)
    }

    return color * intensity;
}

// PLASMA: Multi-sine wave interference
vec3 effectPlasma(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;

    float v1 = sin(normPos.x * 10.0 + uTime * uSpeed);
    float v2 = sin(normPos.y * 10.0 - uTime * uSpeed * 0.7);
    float v3 = sin((normPos.x + normPos.y + normPos.z) * 8.0 + uTime * uSpeed * 0.5);

    vec2 center = vec2(0.5);
    float v4 = sin(length(normPos.xz - center) * 20.0 + uTime * uSpeed);

    float plasma = (v1 + v2 + v3 + v4) / 4.0;
    float hue = (plasma + 1.0) * 0.5;

    return hsl2rgb(vec3(hue, 1.0, 0.5));
}

// KALEIDOSCOPE: Mirror colors with symmetry
vec3 effectKaleidoscope(vec3 baseColor) {
    vec3 center = uGridCenter;
    vec3 fromCenter = abs(worldPos - center);

    float angle = atan(fromCenter.y, fromCenter.x) + uTime * uSpeed * 0.5;
    float radius = length(fromCenter.xz);

    int segments = 6;
    float segmentAngle = mod(angle * float(segments), 6.28318530718);

    float hue = fract(segmentAngle / 6.28318530718 + radius * 0.1);

    return hsl2rgb(vec3(hue, 0.9, 0.5));
}

// BREATH: Saturation oscillation
vec3 effectBreath(vec3 baseColor) {
    vec3 hsl = rgb2hsl(baseColor);
    float breathCycle = (sin(uTime * uSpeed * 0.5) + 1.0) / 2.0;
    float newSaturation = 0.3 + breathCycle * 0.7;
    return hsl2rgb(vec3(hsl.x, newSaturation, hsl.z));
}

// COLOR CHASE: Moving wave of color
vec3 effectColorChase(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;

    float wave1 = sin(normPos.x * 3.0 + uTime * uSpeed * 3.0) * 0.5 + 0.5;
    float wave2 = sin(normPos.z * 3.0 + uTime * uSpeed * 3.0 + 3.14159) * 0.5 + 0.5;

    float combined = (wave1 + wave2) / 2.0;
    float hue = combined;

    return hsl2rgb(vec3(hue, 1.0, 0.5));
}

// WAVE MULTI: Multiple interference sources
vec3 effectWaveMulti(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;

    vec2 source1 = vec2(0.25, 0.25);
    vec2 source2 = vec2(0.75, 0.25);
    vec2 source3 = vec2(0.5, 0.75);

    float dist1 = length(normPos.xz - source1);
    float dist2 = length(normPos.xz - source2);
    float dist3 = length(normPos.xz - source3);

    float wave1 = sin(dist1 * 10.0 - uTime * uSpeed * 2.0);
    float wave2 = sin(dist2 * 10.0 - uTime * uSpeed * 2.0);
    float wave3 = sin(dist3 * 10.0 - uTime * uSpeed * 2.0);

    float totalWave = (wave1 + wave2 + wave3) / 3.0;
    float hue = (totalWave + 1.0) * 0.5;

    return hsl2rgb(vec3(hue, 1.0, 0.5));
}

// WAVE VERTICAL: Vertical waves
vec3 effectWaveVertical(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;
    float wave = sin(normPos.y * 10.0 - uTime * uSpeed * 2.0);
    float hue = (wave + 1.0) * 0.5;
    return hsl2rgb(vec3(hue, 1.0, 0.5));
}

// WAVE CIRCULAR: Expanding circles
vec3 effectWaveCircular(vec3 baseColor) {
    vec3 center = vec3(0.5);
    float dist = length((worldPos / uGridSize).xz - center.xz);
    float wave = sin(dist * 15.0 - uTime * uSpeed * 3.0);
    float hue = (wave + 1.0) * 0.5;
    return hsl2rgb(vec3(hue, 1.0, 0.5));
}

// WAVE STANDING: Standing wave pattern
vec3 effectWaveStanding(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;
    float waveX = sin(normPos.x * 10.0);
    float waveZ = sin(normPos.z * 10.0);
    float timeFactor = sin(uTime * uSpeed * 2.0);
    float combined = (waveX * waveZ * timeFactor + 1.0) / 2.0;
    float hue = combined;
    return hsl2rgb(vec3(hue, 1.0, 0.5));
}

// CYCLE HUE: Smooth hue rotation
vec3 effectCycleHue(vec3 baseColor) {
    vec3 hsl = rgb2hsl(baseColor);
    float hue = fract(hsl.x + uTime * uSpeed * 0.2);
    return hsl2rgb(vec3(hue, hsl.y, hsl.z));
}

// PULSE RADIAL: Pulse from center
vec3 effectPulseRadial(vec3 baseColor) {
    vec3 center = uGridCenter;
    float dist = length(worldPos - center);
    float pulse = sin(uTime * uSpeed * 3.0 - dist * 0.2);
    float brightness = (pulse + 1.0) / 2.0;

    vec3 hsl = rgb2hsl(baseColor);
    return hsl2rgb(vec3(hsl.x, hsl.y, brightness * 0.8 + 0.2));
}

// PULSE ALTERNATING: Sectored pulsing
vec3 effectPulseAlternating(vec3 baseColor) {
    vec3 center = uGridCenter;
    vec3 diff = worldPos - center;
    float angle = atan(diff.z, diff.x);
    int sector = int(floor((angle + 3.14159) / (3.14159 / 4.0)));
    float phase = float(sector) * 3.14159 / 4.0;

    float pulse = sin(uTime * uSpeed * 2.0 + phase);
    float brightness = (pulse + 1.0) / 2.0;

    vec3 hsl = rgb2hsl(baseColor);
    return hsl2rgb(vec3(hsl.x, hsl.y, brightness * 0.8 + 0.2));
}

// PULSE LAYERED: Y-layer pulsing
vec3 effectPulseLayered(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;
    float pulse = sin(uTime * uSpeed * 2.0 + normPos.y * 15.0);
    float brightness = (pulse + 1.0) / 2.0;

    vec3 hsl = rgb2hsl(baseColor);
    return hsl2rgb(vec3(hsl.x, hsl.y, brightness * 0.8 + 0.2));
}

// PULSE BEAT: Double-pulse heartbeat
vec3 effectPulseBeat(vec3 baseColor) {
    float t = mod(uTime * uSpeed, 2.0);
    float pulse;

    if (t < 0.3) {
        pulse = sin(t * 33.333); // First beat
    } else if (t < 0.7) {
        pulse = sin((t - 0.3) * 26.666); // Second beat
    } else {
        pulse = 0.0; // Rest
    }

    float brightness = (pulse + 1.0) / 2.0;
    vec3 hsl = rgb2hsl(baseColor);
    return hsl2rgb(vec3(hsl.x, hsl.y, brightness * 0.8 + 0.2));
}

// STATIC COLOR: Random color per voxel
vec3 effectStaticColor(vec3 baseColor) {
    float timeSnap = floor(uTime * uSpeed * 10.0);
    float noiseVal = hash(worldPos + vec3(timeSnap));
    return hsl2rgb(vec3(noiseVal, 1.0, 0.5));
}

// STATIC DYNAMIC: Pulsing static
vec3 effectStaticDynamic(vec3 baseColor) {
    float noiseVal = hash(worldPos);
    float pulse = sin(uTime * uSpeed * 3.0);
    float brightness = noiseVal * ((pulse + 1.0) / 2.0);

    vec3 hsl = rgb2hsl(baseColor);
    return hsl2rgb(vec3(hsl.x, hsl.y, brightness * 0.8 + 0.2));
}

// STATIC WAVE: Traveling noise
vec3 effectStaticWave(vec3 baseColor) {
    vec3 noisePos = worldPos * 2.0 + vec3(uTime * uSpeed * 3.0, 0, 0);
    float noiseVal = noise3D(noisePos);
    float hue = noiseVal;
    return hsl2rgb(vec3(hue, 1.0, 0.5));
}

// SCROLLING STROBE: Moving bright band
vec3 effectScrollingStrobe(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;

    // Calculate position along scroll direction
    float scrollPos = 0.0;
    if (uScrollDirection == 0) scrollPos = normPos.x;
    else if (uScrollDirection == 1) scrollPos = normPos.y;
    else if (uScrollDirection == 2) scrollPos = normPos.z;
    else if (uScrollDirection == 3) scrollPos = (normPos.x + normPos.z) / 2.0;

    // Scrolling band position
    float bandPos = fract(uTime * uSpeed * 0.2);
    float thickness = uScrollThickness / uGridSize.y;

    float distFromBand = abs(scrollPos - bandPos);

    if (uScrollInvert == 1) {
        // Inverted: turn OFF in band
        if (distFromBand < thickness) {
            return vec3(0.0);
        }
    } else {
        // Normal: turn ON in band
        if (distFromBand < thickness) {
            return vec3(1.0);
        }
    }

    return baseColor;
}

// SCROLLING PULSE: Pulsing band
vec3 effectScrollingPulse(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;

    float scrollPos = 0.0;
    if (uScrollDirection == 0) scrollPos = normPos.x;
    else if (uScrollDirection == 1) scrollPos = normPos.y;
    else if (uScrollDirection == 2) scrollPos = normPos.z;
    else if (uScrollDirection == 3) scrollPos = (normPos.x + normPos.z) / 2.0;

    float bandPos = fract(uTime * uSpeed * 0.2);
    float thickness = uScrollThickness / uGridSize.y;

    float distFromBand = abs(scrollPos - bandPos);

    if (distFromBand < thickness) {
        float bandProgress = distFromBand / thickness;
        float falloff = 1.0 - bandProgress;
        float pulse = sin(uTime * uSpeed * 5.0);
        float brightness = 0.5 + (pulse + 1.0) * 0.25;
        float finalBrightness = brightness * falloff;

        vec3 hsl = rgb2hsl(baseColor);

        if (uScrollInvert == 1) {
            return hsl2rgb(vec3(hsl.x, hsl.y, max(0.0, hsl.z * (1.0 - finalBrightness))));
        } else {
            return hsl2rgb(vec3(hsl.x, hsl.y, max(0.2, hsl.z * (1.0 + finalBrightness))));
        }
    }

    return baseColor;
}

// ============================================================================
// MAIN SHADER
// ============================================================================

void main() {
    // Start with 3D gradient or base color
    vec3 baseColor = apply3DGradient(vec3(0.5, 0.5, 0.5));

    // Apply selected effect
    vec3 effectColor = baseColor;

    if (uEffectType == 1) effectColor = effectSparkle(baseColor);
    else if (uEffectType == 2) effectColor = effectRainbowSweep(baseColor);
    else if (uEffectType == 3) effectColor = effectFire(baseColor);
    else if (uEffectType == 4) effectColor = effectPlasma(baseColor);
    else if (uEffectType == 5) effectColor = effectKaleidoscope(baseColor);
    else if (uEffectType == 6) effectColor = effectBreath(baseColor);
    else if (uEffectType == 7) effectColor = effectColorChase(baseColor);
    else if (uEffectType == 8) effectColor = effectWaveMulti(baseColor);
    else if (uEffectType == 9) effectColor = effectWaveVertical(baseColor);
    else if (uEffectType == 10) effectColor = effectWaveCircular(baseColor);
    else if (uEffectType == 11) effectColor = effectWaveStanding(baseColor);
    else if (uEffectType == 12) effectColor = effectCycleHue(baseColor);
    else if (uEffectType == 13) effectColor = effectPulseRadial(baseColor);
    else if (uEffectType == 14) effectColor = effectPulseAlternating(baseColor);
    else if (uEffectType == 15) effectColor = effectPulseLayered(baseColor);
    else if (uEffectType == 16) effectColor = effectPulseBeat(baseColor);
    else if (uEffectType == 17) effectColor = effectStaticColor(baseColor);
    else if (uEffectType == 18) effectColor = effectStaticDynamic(baseColor);
    else if (uEffectType == 19) effectColor = effectStaticWave(baseColor);
    else if (uEffectType == 20) effectColor = effectScrollingStrobe(baseColor);
    else if (uEffectType == 21) effectColor = effectScrollingPulse(baseColor);

    // Blend effect with base color using intensity
    vec3 finalColor = mix(baseColor, effectColor, uIntensity);

    // Output with full opacity
    fragColor = vec4(finalColor, 1.0);
}
```

---

## 3D Gradient Mapping

### Gradient Control Network

```
┌────────────────────────────────────────┐
│ Gradient Control COMP                  │
│  - Enabled (toggle)                    │
│  - Type: linear-x/y/z, radial, etc.   │
│  - Origin (XYZ 0-1)                    │
│  - Invert (toggle)                     │
│  - Falloff: linear/quadratic/etc.      │
└──────────────┬─────────────────────────┘
               ↓
┌────────────────────────────────────────┐
│ Color Ramp COMP                        │
│  - Visual gradient editor              │
│  - Add/remove color stops              │
│  - Position stops along ramp           │
└──────────────┬─────────────────────────┘
               ↓
┌────────────────────────────────────────┐
│ Color Stop Exporter (Python)           │
│  - Extracts stop positions & colors    │
│  - Formats for shader uniforms         │
└──────────────┬─────────────────────────┘
               ↓ (CHOPs)
          [GLSL Material]
```

### Color Ramp Component Setup

**Custom Parameter Component:** `gradientRamp`

**Python Script** to export color stops:

```python
# gradientRamp_export.py

def exportColorStops():
    """Export color ramp stops to CHOPs for shader"""
    comp = op('gradientRamp')

    # Get all color stop parameters
    stops = []
    for i in range(8):  # Max 8 stops
        if hasattr(comp.par, f'stop{i}enabled'):
            if comp.par[f'stop{i}enabled'].eval():
                pos = comp.par[f'stop{i}position'].eval()
                r = comp.par[f'stop{i}colorr'].eval()
                g = comp.par[f'stop{i}colorg'].eval()
                b = comp.par[f'stop{i}colorb'].eval()
                stops.append({'position': pos, 'color': (r, g, b)})

    # Sort by position
    stops.sort(key=lambda x: x['position'])

    # Output to CHOP
    chopOut = op('colorStops_out')
    chopOut.clear()

    # Positions channel
    posChannel = chopOut.appendChan('positions')
    # Color channels
    rChannel = chopOut.appendChan('colors_r')
    gChannel = chopOut.appendChan('colors_g')
    bChannel = chopOut.appendChan('colors_b')

    for i, stop in enumerate(stops):
        posChannel[i] = stop['position']
        rChannel[i] = stop['color'][0]
        gChannel[i] = stop['color'][1]
        bChannel[i] = stop['color'][2]

    return len(stops)
```

---

## Effect Implementations

### Effect 1: Sparkle

**TouchDesigner Network:**

```
[Noise TOP (3D)]
    ↓
[Threshold TOP] (threshold > 0.98)
    ↓
[Lookup TOP] (white on sparkles)
    ↓
[Composite with base color]
```

**GLSL Parameters:**
- No additional uniforms needed
- Uses built-in noise function

### Effect 2: Rainbow Sweep

**TouchDesigner Network:**

```
[Ramp TOP] (horizontal rainbow gradient)
    ↓
[Transform TOP] (translate X by time)
    ↓
[Apply to geometry via UV mapping]
```

**GLSL Parameters:**
- Uses world position for automatic 3D sweep

### Effect 3: Fire

**TouchDesigner Network:**

```
[Noise TOP (turbulent)]
    ↓
[Ramp TOP] (yellow→orange→red gradient)
    ↓
[Multiply by height gradient]
    ↓
[Over composite]
```

**GLSL Parameters:**
- Fire intensity controlled by `uIntensity`
- Height bias built into shader

### Effect 4: Plasma

**TouchDesigner Network:**

```
[Math CHOP] (4 sine waves)
    ↓
[Combine waves (addition)]
    ↓
[Ramp TOP] (hue spectrum)
    ↓
[Lookup based on combined wave value]
```

**GLSL Parameters:**
- Uses 4 sine wave sources
- Automatic 3D interference

### Wave Effects (5-8)

**Shared Network:**

```
[Wave Generator CHOP]
    ↓
[3D Position Mapper]
    ↓
[Hue Lookup]
    ↓
[Color Output]
```

**Effect-specific settings:**

- **waveMulti**: 3 point sources, interference
- **waveVertical**: Y-axis sine wave
- **waveCircular**: Radial distance from center
- **waveStanding**: X * Z * time product

### Pulse Effects (13-16)

**Network Template:**

```
[Timer CHOP] (sine wave)
    ↓
[Distance/Position Calculation]
    ↓
[Brightness Modulation]
    ↓
[Apply to HSL lightness]
```

**Pulse types:**
- **pulseRadial**: Distance-based phase offset
- **pulseAlternating**: Angular sector phase
- **pulseLayered**: Y-position phase
- **pulseBeat**: Double-pulse timing

### Scrolling Effects (20-21)

**Network:**

```
[Timer CHOP] (linear ramp)
    ↓
[Position Comparison]
    ↓
[Band Threshold]
    ↓
[Color/Brightness Override]
```

**Parameters:**
- `scrollThickness`: Band width (1-20 voxels)
- `scrollDirection`: X/Y/Z/diagonal/radial
- `scrollInvert`: Normal/inverted mode

---

## Parameter Control

### Master Control Panel

**Component:** `colorEffects_control`

**Parameters:**

```python
# Effect Selection
effectType: Menu
  - none
  - sparkle
  - rainbowSweep
  - fire
  - plasma
  - kaleidoscope
  - breath
  - colorChase
  - waveMulti
  - waveVertical
  - waveCircular
  - waveStanding
  - cycleHue
  - pulseRadial
  - pulseAlternating
  - pulseLayered
  - pulseBeat
  - staticColor
  - staticDynamic
  - staticWave
  - scrollingStrobe
  - scrollingPulse

# Universal Parameters
intensity: Float (0-1), default 1.0
speed: Float (0.1-5.0), default 1.0

# Scrolling Parameters
scrollThickness: Float (1-20), default 5
scrollDirection: Menu (x/y/z/diagonal-xz/diagonal-yz/diagonal-xy/radial)
scrollInvert: Toggle (0/1)

# 3D Gradient Parameters
gradientEnabled: Toggle
gradientType: Menu (linear-x/linear-y/linear-z/radial/cylindrical)
gradientOriginX: Float (0-1), default 0.5
gradientOriginY: Float (0-1), default 0.5
gradientOriginZ: Float (0-1), default 0.5
gradientInvert: Toggle
falloffType: Menu (linear/quadratic/cubic/smoothstep)
```

### CHOP Export Mapping

**Constant CHOPs** for each parameter → **Null CHOP** → Export to GLSL uniforms

```python
# In GLSL MAT Parameters tab:
# Uniform Name: uEffectType
# Value: op('control_panel').par.effectType.menuIndex

# Uniform Name: uIntensity
# Value: op('control_panel').par.intensity

# Uniform Name: uSpeed
# Value: op('control_panel').par.speed

# ... etc for all parameters
```

### Preset System

**Table DAT:** `effect_presets`

| Name | effectType | intensity | speed | scrollThickness | scrollDirection | ... |
|------|-----------|-----------|-------|----------------|----------------|-----|
| Fire Wall | fire | 0.8 | 1.5 | 5 | y | ... |
| Rainbow Flow | rainbowSweep | 1.0 | 2.0 | 5 | x | ... |
| Pulse Ring | pulseRadial | 0.9 | 1.2 | 5 | y | ... |
| Strobe Scan | scrollingStrobe | 1.0 | 0.8 | 3 | y | ... |

**Load Preset Script:**

```python
def loadPreset(presetName):
    """Load effect preset from table"""
    table = op('effect_presets')
    ctrl = op('colorEffects_control')

    # Find preset row
    row = None
    for r in range(1, table.numRows):
        if table[r, 0].val == presetName:
            row = r
            break

    if row is None:
        print(f"Preset '{presetName}' not found")
        return

    # Apply parameters
    for col in range(1, table.numCols):
        paramName = table[0, col].val
        value = table[row, col].val

        if hasattr(ctrl.par, paramName):
            # Check parameter type
            par = getattr(ctrl.par, paramName)
            if par.isMenu:
                par.val = value
            elif par.isToggle:
                par.val = int(value)
            else:
                par.val = float(value)
```

---

## Optimization

### Performance Tips

1. **Shader Optimization:**
   - Use `if` statements sparingly (GPU branching is expensive)
   - Consider using lookup textures instead of complex math
   - Pre-calculate constants on CPU side

2. **Effect Switching:**
   - Instead of `if/else` chain, use function pointer arrays (if supported)
   - Or create separate shaders per effect and switch materials

3. **Uniform Updates:**
   - Only update uniforms when parameters change
   - Use CHOP `Change` callback to detect changes

4. **Texture Caching:**
   - Cache noise textures instead of calculating per-frame
   - Use `Noise TOP` pre-rendered

5. **LOD System:**
   - Reduce effect complexity at distance
   - Disable expensive effects when not visible

### Memory Management

**Texture Resolution:**
- Noise textures: 256x256x256 (3D) or 1024x1024 (2D)
- Gradient ramps: 256 samples max
- Limit simultaneous effects to 2-3

### GPU vs CPU

**GPU (Shader):**
- Real-time effects (waves, pulses, scrolling)
- Per-pixel calculations
- Color transformations

**CPU (CHOPs/TOPs):**
- Parameter animation
- Preset management
- Effect sequencing

---

## Advanced Techniques

### Multi-Pass Effects

Layer multiple effects:

```
[Pass 1: Base Gradient]
    ↓
[Pass 2: Wave Effect] (additive blend)
    ↓
[Pass 3: Pulse Modulation] (multiply blend)
    ↓
[Final Output]
```

### Custom Effect Creation

**Template for new effect:**

```glsl
vec3 effectCustom(vec3 baseColor) {
    vec3 normPos = worldPos / uGridSize;

    // Your effect logic here
    // Example: diagonal sweep
    float sweep = normPos.x + normPos.z + uTime * uSpeed;
    float hue = fract(sweep);

    return hsl2rgb(vec3(hue, 1.0, 0.5));
}
```

Add to main shader switch:

```glsl
else if (uEffectType == 22) effectColor = effectCustom(baseColor);
```

### Effect Sequencing

**Timeline-based effect changes:**

```python
# effectSequencer.py

def updateEffect(currentTime):
    """Change effects based on timeline"""
    sequences = [
        {'start': 0, 'end': 10, 'effect': 'rainbowSweep'},
        {'start': 10, 'end': 20, 'effect': 'fire'},
        {'start': 20, 'end': 30, 'effect': 'plasma'},
        {'start': 30, 'end': 40, 'effect': 'pulseRadial'}
    ]

    ctrl = op('colorEffects_control')

    for seq in sequences:
        if seq['start'] <= currentTime < seq['end']:
            ctrl.par.effectType = seq['effect']
            break
```

### Audio-Reactive Effects

**Use Audio Analysis CHOPs:**

```
[Audio Device In]
    ↓
[Audio Spectrum]
    ↓
[Band Select] (bass/mid/high)
    ↓
[Map to effect parameter]
```

**Example: Pulse beat synced to audio:**

```python
# Audio-reactive pulse speed
audioLevel = op('audioAnalysis')['bass_level']
ctrl = op('colorEffects_control')
ctrl.par.speed = 1.0 + audioLevel * 2.0
```

---

## Troubleshooting

### Common Issues

**1. Colors not appearing:**
- Check `uIntensity` is > 0
- Verify shader is compiled (check Info DAT)
- Ensure uniforms are properly connected

**2. Performance drops:**
- Reduce noise texture resolution
- Simplify shader (remove unused effects)
- Use LOD system

**3. Flickering/aliasing:**
- Enable anti-aliasing in render settings
- Use smoother transitions (smoothstep)
- Increase time precision

**4. Colors look wrong:**
- Check HSL↔RGB conversion functions
- Verify color space (linear vs sRGB)
- Test with simple gradients first

---

## Complete Example Network

**Full Color Effect Chain:**

```
┌─────────────────────────────────────────────┐
│ Control Panel COMP                          │
│  - effectType: pulseRadial                  │
│  - intensity: 0.8                           │
│  - speed: 1.5                               │
└──────────────┬──────────────────────────────┘
               ↓ (via expressions)
┌─────────────────────────────────────────────┐
│ GLSL Material: colorEffects                 │
│                                             │
│  Uniforms:                                  │
│   - uTime: absTime.seconds                  │
│   - uEffectType: 13 (pulseRadial)           │
│   - uIntensity: 0.8                         │
│   - uSpeed: 1.5                             │
│   - uGridSize: (48, 24, 48)                 │
│   - uGridCenter: (24, 12, 24)               │
│                                             │
│  Vertex Shader: colorEffects_vertex.glsl    │
│  Pixel Shader: colorEffects_pixel.glsl      │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ Geometry COMP                               │
│  - Render with instances                    │
│  - Material: colorEffects                   │
└──────────────┬──────────────────────────────┘
               ↓
         [Render TOP]
               ↓
      [Final Output]
```

---

## Conclusion

This TouchDesigner implementation provides a complete GLSL-based color effects system that matches the JavaScript ColorEffects library. The shader-based approach offers:

- **GPU acceleration** for real-time performance
- **Unified architecture** for all effect types
- **Flexible parameter control** via CHOPs
- **3D gradient mapping** for spatial color control
- **Extensible framework** for custom effects

The GLSL shaders handle all color transformations at the pixel level, while TouchDesigner's CHOP network manages parameters, presets, and sequencing. This creates a powerful, efficient system for volumetric color effects.

**Next Steps:**
1. Copy GLSL shaders into TouchDesigner
2. Create control panel with all parameters
3. Set up CHOP→uniform connections
4. Test each effect individually
5. Create preset library
6. Optimize for target framerate

Happy shader coding!
