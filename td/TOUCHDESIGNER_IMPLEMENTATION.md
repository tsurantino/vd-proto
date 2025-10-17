# TouchDesigner POPs Implementation Guide
## Hybrid Morph System

This guide provides detailed instructions for implementing the Hybrid Morph particle system in TouchDesigner using the Particle Operator (POP) network.

---

## Table of Contents

1. [Network Overview](#network-overview)
2. [Core Particle System Setup](#core-particle-system-setup)
3. [Shape Attractor System](#shape-attractor-system)
4. [Flow Forces](#flow-forces)
5. [Turbulence System](#turbulence-system)
6. [Coherence & Visibility](#coherence--visibility)
7. [Scene Implementations](#scene-implementations)
   - [ShapeMorph](#shapemorph-scenes)
   - [ParticleFlow](#particleflow-scenes)
   - [Vortex](#vortex-scenes)
   - [WaveField](#wavefield-scenes)
   - [Plasma](#plasma-scenes)
8. [Parameter Control](#parameter-control)
9. [Rendering & Output](#rendering--output)
10. [Optimization](#optimization)

## Additional Documentation

- **[Optical Illusions Guide](TOUCHDESIGNER_ILLUSIONS.md)** - 12 optical illusion implementations using the Hybrid Morph system
- **[Color Effects Guide](TOUCHDESIGNER_COLOR_EFFECTS.md)** - Color system implementation and effects

---

## Network Overview

### High-Level Architecture

```
[Control Panel COMP]
    ↓ (CHOPs)
[Parameter Mapper]
    ↓
┌─────────────────────────────────────┐
│  POP Network                        │
│  ┌───────────────┐                  │
│  │ POP Source    │ ← Particle birth │
│  └───────┬───────┘                  │
│          ↓                           │
│  ┌───────────────┐                  │
│  │ Attractor SOP │ ← Shape geometry │
│  │ (via POP      │                  │
│  │  Attract)     │                  │
│  └───────┬───────┘                  │
│          ↓                           │
│  ┌───────────────┐                  │
│  │ POP Force     │ ← Flow direction │
│  └───────┬───────┘                  │
│          ↓                           │
│  ┌───────────────┐                  │
│  │ POP Wind      │ ← Turbulence     │
│  │ (Noise)       │                  │
│  └───────┬───────┘                  │
│          ↓                           │
│  ┌───────────────┐                  │
│  │ POP Wrangle   │ ← Coherence      │
│  │ (Visibility)  │   filtering      │
│  └───────┬───────┘                  │
│          ↓                           │
│  ┌───────────────┐                  │
│  │ POP Output    │                  │
│  └───────────────┘                  │
└─────────────────────────────────────┘
          ↓
[Render TOP / Instancing]
```

---

## Core Particle System Setup

### 1. POP Network Base

Create a new `particleGPU1` or standard `geo1` with POP context.

### 2. POP Source

**Node:** `popsource1`

**Settings:**
- **Birth Type:** Constant Birth Rate
- **Birth Rate:** `ch('../particleDensity') * 1000`
- **Life Expectancy:** 100 (effectively infinite for persistent particles)
- **Variance:** 0 (consistent lifetime)

**Initial Position:**
- **Emission Type:** Box
- **Size:**
  - X: `me.parent().parent().par.gridX`
  - Y: `me.parent().parent().par.gridY`
  - Z: `me.parent().parent().par.gridZ`

**Initial Velocity:**
- **Velocity Type:** None (velocity handled by forces)

### 3. POP Limit

**Node:** `poplimit1`

**Settings:**
- **Max Points:** `int(ch('../particleDensity') * 1000)`
- **Kill:** Oldest (maintain constant particle count)

---

## Shape Attractor System

### Overview

Shape attractors are created as SOP geometry and fed into POP Attract nodes. Each shape type has its own SOP chain.

### Base SOP Generator (for each shape)

#### Sphere Attractor

**Node Chain:** `sphere1` → `resample1` → `null_sphere_attractor`

```
sphere1:
  - Radius: ch('../../size') * 10
  - Rows: 20
  - Columns: 40
  - Type: Polygon

resample1:
  - Length: 1.0 (creates evenly distributed points)
  - Randomize: OFF (deterministic placement)
```

#### Helix Attractor

**Node Chain:** `circle1` → `sweep1` → `resample1` → `null_helix_attractor`

```
circle1 (profile):
  - Radius: ch('../../size') * 2
  - Divisions: 16

curve1 (spine):
  - Type: NURBS
  - Points: Create spiral path using Python SOP

Python SOP for spiral:
```python
import math

n = geo.createNode('add')
numPoints = 200
height = parent().par.gridY
turns = 5
radius = parent().par.size * 8

for i in range(numPoints):
    t = i / float(numPoints)
    angle = t * turns * 2 * math.pi
    x = math.cos(angle) * radius
    y = t * height
    z = math.sin(angle) * radius
    n.createPoint(x, y, z)
```

```
sweep1:
  - Spine: curve1
  - Cross Section: circle1

resample1:
  - Length: 1.0
```

#### Torus Attractor

**Node Chain:** `torus1` → `resample1` → `null_torus_attractor`

```
torus1:
  - Radius: ch('../../size') * 15
  - Core Radius: ch('../../shapeThickness') * 3
  - Rows: 24
  - Columns: 48

resample1:
  - Length: 1.0
```

#### Cube Attractor

**Node Chain:** `box1` → `resample1` → `null_cube_attractor`

```
box1:
  - Size: ch('../../size') * 20 (XYZ)
  - Type: Polygon Mesh

resample1:
  - Length: 1.0
```

#### Pyramid Attractor

**Node Chain:** `grid1` → `polyextrude1` → `facet1` → `resample1` → `null_pyramid_attractor`

```
grid1 (base):
  - Size: ch('../../size') * 15 (XZ)
  - Rows: 1, Columns: 1

polyextrude1:
  - Distance: ch('../../size') * 20
  - Scale: 0.0 (converge to point)

resample1:
  - Length: 1.0
```

#### Plane Attractor

**Node Chain:** `grid1` → `resample1` → `null_plane_attractor`

```
grid1:
  - Size X: parent().par.gridX
  - Size Z: parent().par.gridZ
  - Rows: 20, Columns: 20

resample1:
  - Length: 2.0
```

### Shape Selection Switch

**Node:** `switch_shape`

**Settings:**
- **Input 0:** null_sphere_attractor
- **Input 1:** null_helix_attractor
- **Input 2:** null_torus_attractor
- **Input 3:** null_cube_attractor
- **Input 4:** null_pyramid_attractor
- **Input 5:** null_plane_attractor

**Select Index:**
```python
# In parameter expression
shape_map = {
    'sphere': 0,
    'helix': 1,
    'torus': 2,
    'cube': 3,
    'pyramid': 4,
    'plane': 5
}
parent().par.baseShape.eval() in shape_map and shape_map[parent().par.baseShape.eval()] or 0
```

### Global Transformations on Attractor

Apply movement parameters to attractor geometry before it reaches POP Attract:

**Node:** `transform_attractor`

**Parameters:**
```python
# Translation X
tx = sin(absTime.seconds * parent().par.translateX * 2) * parent().par.translateAmplitude * 10

# Translation Z
tz = cos(absTime.seconds * parent().par.translateZ * 2) * parent().par.translateAmplitude * 10

# Orbit
orbitAngle = absTime.seconds * parent().par.orbitSpeed * 2
tx += cos(orbitAngle) * parent().par.orbitRadius * 10
tz += sin(orbitAngle) * parent().par.orbitRadius * 10

# Bounce
ty = abs(sin(absTime.seconds * parent().par.bounceSpeed * 3)) * parent().par.bounceHeight * 8

# Rotation X, Y, Z
rx = absTime.seconds * parent().par.rotationX * 30
ry = absTime.seconds * parent().par.rotationY * 30
rz = absTime.seconds * parent().par.rotationZ * 30

# Wobble (add to rotations)
wobbleAmount = parent().par.wobbleAmount * 30
rx += sin(absTime.seconds * parent().par.wobbleSpeed * 2.3) * wobbleAmount
ry += sin(absTime.seconds * parent().par.wobbleSpeed * 1.7) * wobbleAmount
rz += sin(absTime.seconds * parent().par.wobbleSpeed * 2.9) * wobbleAmount
```

### POP Attract

**Node:** `popattract1`

**Settings:**
- **Goal SOP:** `transform_attractor`
- **Goal Weight:** `ch('../attractorStrength')`
- **Force:** 0.5
- **Match Method:** Closest Point on Surface
- **Calculate Normals:** ON
- **Max Points:** Use All Points
- **Goal Blend:** 1.0

**VEXpression (optional, for fine control):**
```c
// In popattract1's VEXpression
float strength = chf('../attractorStrength');
vector goalpos = v@goalP; // Set by attractor
vector diff = goalpos - v@P;
v@force += diff * strength * 0.1;
```

---

## Flow Forces

### POP Force (Directional Flow)

**Node:** `popforce_flow`

**Base Settings:**
- **Force:** `ch('../flowIntensity') * ch('../flowVelocity')`

**Direction by flowDirection parameter:**

Use a switch or Python to set force direction:

**Python Expression in Force parameters:**

```python
# FX (Force X):
flow_dir = parent().par.flowDirection.eval()
flow_intensity = parent().par.flowIntensity.eval()
flow_velocity = parent().par.flowVelocity.eval()

if flow_dir == 'none':
    result = 0
elif flow_dir == 'drift':
    result = sin(absTime.seconds * 0.5) * flow_intensity * flow_velocity * 0.2
else:
    result = 0

# FY (Force Y):
if flow_dir == 'fall':
    result = -flow_intensity * flow_velocity * 2.0
elif flow_dir == 'rise':
    result = flow_intensity * flow_velocity * 2.0
else:
    result = 0

# FZ (Force Z):
if flow_dir in ['none', 'fall', 'rise', 'drift']:
    result = 0
else:
    result = 0
```

### Specialized Flow Patterns

For complex flow like `spiral`, `explode`, `implode`:

**Node:** `popwrangle_flow`

**VEXpression:**
```c
string flowDir = chs('../flowDirection');
float intensity = chf('../flowIntensity');
float velocity = chf('../flowVelocity');
float time = chf('absTime.seconds');

vector center = set(chf('../gridX') / 2, chf('../gridY') / 2, chf('../gridZ') / 2);
vector fromCenter = v@P - center;
float dist = length(fromCenter);

if (flowDir == 'spiral') {
    // Spiraling upward
    float angle = atan2(fromCenter.z, fromCenter.x);
    float newAngle = angle + velocity * 0.1;
    vector tangent = set(-sin(newAngle), 0, cos(newAngle));
    v@force += tangent * intensity * 0.5;
    v@force.y += intensity * velocity * 0.3; // Upward component

} else if (flowDir == 'explode') {
    // Radial outward
    vector dir = normalize(fromCenter);
    v@force += dir * intensity * velocity * 0.5;

} else if (flowDir == 'implode') {
    // Radial inward
    vector dir = normalize(fromCenter);
    v@force -= dir * intensity * velocity * 0.5;
}
```

---

## Turbulence System

### POP Wind (Noise-based Turbulence)

**Node:** `popwind_turbulence`

**Settings:**
- **Wind Type:** Noise
- **Amplitude:** `ch('../turbulence') * 5.0`
- **Noise Type:** Perlin
- **Frequency:**
  - X: `0.1 + ch('../turbulence') * 0.3`
  - Y: `0.1 + ch('../turbulence') * 0.3`
  - Z: `0.1 + ch('../turbulence') * 0.3`
- **Offset:**
  - X: `$T * 0.5` (evolves over time)
  - Y: `$T * 0.3`
  - Z: `$T * 0.4`
- **Turbulence:** `ch('../turbulence') * 2`
- **Swirl Size:** 0.5

**Alternative: Custom POP Wrangle**

**Node:** `popwrangle_turbulence`

**VEXpression:**
```c
float turbulence = chf('../turbulence');

// 3D Perlin noise for turbulence
vector noisePos = v@P * 0.1 + set($T * 0.5, $T * 0.3, $T * 0.4);
vector noiseForce = noise(noisePos) - 0.5; // Center around 0

// Scale by turbulence parameter
v@force += noiseForce * turbulence * 3.0;

// Add curl noise for swirling effect
if (turbulence > 0.3) {
    vector curl = curlnoise(v@P * 0.05 + set($T * 0.2, 0, 0));
    v@force += curl * turbulence * 2.0;
}
```

---

## Coherence & Visibility

### Coherence Filtering

Coherence controls which particles are visible/active.

**Method 1: POP Wrangle (Stochastic Culling)**

**Node:** `popwrangle_coherence`

**VEXpression:**
```c
float coherence = chf('../formCoherence');

// Random visibility based on coherence
// Use particle id for deterministic randomness
float rnd = random(i@id + 1000);

if (rnd > coherence) {
    // Hide particle by setting Alpha to 0
    f@Alpha = 0;
    // Or remove from simulation
    removepoint(0, i@ptnum);
} else {
    f@Alpha = 1;
}
```

**Method 2: Noise Displacement (Physics-based)**

**Node:** `popwrangle_coherence_displacement`

**VEXpression:**
```c
float coherence = chf('../formCoherence');

// Displace particles based on low coherence
float noiseAmount = (1.0 - coherence) * 5.0;
vector noiseOffset = noise(v@P * 0.2 + i@id * 0.1);
v@P += (noiseOffset - 0.5) * noiseAmount;
```

**Method 3: Combination (Recommended)**

Use both: displacement during physics, culling during render.

---

## Scene Implementations

### ShapeMorph Scenes

**Configuration:**
- **formCoherence:** 1.0 (solid shape)
- **attractorStrength:** 0.8-1.0 (particles locked to shape)
- **turbulence:** 0.0-0.2 (minimal chaos)
- **flowDirection:** none
- **baseShape:** sphere/helix/torus/cube/pyramid/plane
- **shapeThickness:** 0.3-0.8

**POP Network:**
```
popsource1 → popattract1 (high strength) → popwrangle_coherence → output
```

**Key Nodes:**
- Strong POP Attract to shape
- Minimal/no flow forces
- High coherence
- All global movement applied to attractor SOP

**Special Handling:**
- **Multiple Objects (objectCount > 1):**
  - Duplicate attractor geometry at different positions
  - Use `copy1` SOP with circular/linear arrangement
  - Feed all copies into POP Attract

---

### ParticleFlow Scenes

**Configuration:**
- **formCoherence:** 0.1-0.4 (sparse particles)
- **attractorStrength:** 0.0-0.2 (minimal shape influence)
- **turbulence:** 0.3-0.6 (organic motion)
- **flowDirection:** fall/rise/spiral/explode
- **flowVelocity:** 1.0-2.0

#### Rain Pattern

**Settings:**
- **flowDirection:** fall
- **flowVelocity:** 1.5
- **turbulence:** 0.2
- **formCoherence:** 0.2

**POP Network:**
```
popsource1 → popforce_flow (downward) → popwind_turbulence → popwrangle_coherence → output
```

**Additional POP Wrangle (recycling):**
```c
// Recycle particles at bottom
if (v@P.y < 0) {
    v@P.y = chf('../gridY');
    v@P.x = random(i@id * 2) * chf('../gridX');
    v@P.z = random(i@id * 3) * chf('../gridZ');
}
```

#### Stars Pattern

**Settings:**
- **flowDirection:** fall (Z-axis direction)
- **flowVelocity:** 1.0
- **turbulence:** 0.1

**POP Wrangle (Z-axis motion):**
```c
v@force.z -= chf('../flowVelocity') * 0.5;

// Recycle
if (v@P.z < 0) {
    v@P.z = chf('../gridZ');
    v@P.x = random(i@id * 4) * chf('../gridX');
    v@P.y = random(i@id * 5) * chf('../gridY');
}
```

#### Fountain Pattern

**Settings:**
- **flowDirection:** rise
- **flowVelocity:** 1.5
- **turbulence:** 0.3

**POP Wrangle (with gravity):**
```c
// Start from center bottom
if (@age < 0.1) {
    v@P = set(chf('../gridX')/2, 0, chf('../gridZ')/2);

    // Random upward velocity
    float angle = random(i@id) * 2 * PI;
    v@v.x = cos(angle) * 2;
    v@v.y = 5 + random(i@id + 10) * 3;
    v@v.z = sin(angle) * 2;
}

// Apply gravity
v@force.y -= 1.0;

// Recycle when particles fall back down
if (v@P.y < 0) {
    v@age = 0;
}
```

#### Spiral Pattern

**Settings:**
- **baseShape:** helix (low strength attractor)
- **attractorStrength:** 0.3
- **flowDirection:** spiral
- **turbulence:** 0.4

**Uses spiral flow wrangle from Flow Forces section**

#### Explode Pattern

**Settings:**
- **flowDirection:** explode
- **flowVelocity:** 1.0
- **turbulence:** 0.5

**POP Wrangle (pulsing expansion):**
```c
vector center = set(chf('../gridX')/2, chf('../gridY')/2, chf('../gridZ')/2);
vector fromCenter = v@P - center;
float dist = length(fromCenter);

// Pulsing expansion
float expansion = (sin($T * 2) + 1) * 0.5; // 0 to 1
vector dir = normalize(fromCenter);
v@force += dir * expansion * 2.0;

// Reset when too far
if (dist > chf('../gridX') * 0.7) {
    v@P = center;
}
```

---

### Vortex Scenes

#### Tornado

**Configuration:**
- **baseShape:** helix (vertical stretch)
- **attractorStrength:** 0.4
- **flowDirection:** spiral + rise
- **turbulence:** 0.6
- **particleDensity:** 0.7

**Custom Helix for Tornado:**
- Height: gridY * 0.9
- Radius: Tapers from bottom (larger) to top (smaller)

**POP Wrangle (tornado forces):**
```c
vector center = set(chf('../gridX')/2, 0, chf('../gridZ')/2);
vector toCenterXZ = set(center.x - v@P.x, 0, center.z - v@P.z);
float distXZ = length(toCenterXZ);

// Height-based radius (cone shape)
float heightRatio = v@P.y / chf('../gridY');
float targetRadius = 5 + (1.0 - heightRatio) * 10; // Wider at bottom

// Radial force (toward target radius)
if (distXZ < targetRadius) {
    v@force += normalize(toCenterXZ) * -0.5; // Push outward
} else {
    v@force += normalize(toCenterXZ) * 0.5; // Pull inward
}

// Rotational force
float angle = atan2(v@P.z - center.z, v@P.x - center.x);
float newAngle = angle + chf('../flowVelocity') * 0.1;
vector tangent = set(-sin(newAngle), 0, cos(newAngle));
v@force += tangent * 2.0;

// Upward force
v@force.y += chf('../flowIntensity') * 0.5;

// Recycle at top
if (v@P.y > chf('../gridY')) {
    v@P.y = 0;
}
```

#### Whirlpool

**Configuration:**
- **baseShape:** helix (horizontal, XZ plane)
- **attractorStrength:** 0.5
- **flowDirection:** spiral (horizontal) + fall (toward center)
- **turbulence:** 0.4

**POP Wrangle:**
```c
vector center = set(chf('../gridX')/2, chf('../gridY')/2, chf('../gridZ')/2);
vector fromCenter = v@P - center;
float dist2D = length(set(fromCenter.x, 0, fromCenter.z));

// Spiral inward
float angle = atan2(fromCenter.z, fromCenter.x);
float newAngle = angle + chf('../flowVelocity') * 0.15;
vector tangent = set(-sin(newAngle), 0, cos(newAngle));
v@force += tangent * 1.5;

// Pull toward center
vector dirXZ = normalize(set(fromCenter.x, 0, fromCenter.z));
v@force -= dirXZ * 0.3;

// Downward force (stronger near center)
float centerPull = 1.0 - saturate(dist2D / 15.0);
v@force.y -= centerPull * 1.0;
```

#### Galaxy (Dual Spiral)

**Configuration:**
- **objectCount:** 2
- **baseShape:** helix (two instances, rotated 180°)
- **attractorStrength:** 0.3
- **flowDirection:** spiral
- **turbulence:** 0.5

**Attractor Setup:**
- Create two helix SOPs rotated 180° apart
- Merge with `merge1`
- Feed into POP Attract

---

### WaveField Scenes

#### Ripple Wave

**Configuration:**
- **baseShape:** plane (custom animated)
- **attractorStrength:** 0.8
- **turbulence:** 0.2
- **formCoherence:** 0.8

**Animated Plane Attractor:**

**Node:** `grid1` → `pointwrangle1` → `null_wave_attractor`

**Point Wrangle:**
```c
float centerX = chf('../../gridX') / 2;
float centerZ = chf('../../gridZ') / 2;

float dx = v@P.x - centerX;
float dz = v@P.z - centerZ;
float dist = sqrt(dx*dx + dz*dz);

float frequency = chf('../../frequency') * 0.3;
float amplitude = chf('../../amplitude') * 3;
float time = chf('absTime.seconds') * 2;

float wave = sin(dist * frequency - time) * amplitude;

v@P.y = chf('../../gridY') / 2 + wave;
```

#### Standing Wave

**Point Wrangle:**
```c
float frequency = chf('../../frequency') * 0.5;
float amplitude = chf('../../amplitude') * 3;
float time = chf('absTime.seconds');

// Standing wave pattern
float waveX = sin(v@P.x * frequency) * cos(time);
float waveZ = sin(v@P.z * frequency) * cos(time * 1.3);

v@P.y = chf('../../gridY') / 2 + (waveX + waveZ) * amplitude;
```

#### Interference Wave

**Point Wrangle:**
```c
float centerX = chf('../../gridX') / 2;
float centerZ = chf('../../gridZ') / 2;
float time = chf('absTime.seconds') * 2;
float frequency = chf('../../frequency') * 0.3;
float amplitude = chf('../../amplitude') * 2;

// Two wave sources
vector source1 = set(centerX - 10, 0, centerZ);
vector source2 = set(centerX + 10, 0, centerZ);

float dist1 = distance(set(v@P.x, 0, v@P.z), source1);
float dist2 = distance(set(v@P.x, 0, v@P.z), source2);

float wave1 = sin(dist1 * frequency - time);
float wave2 = sin(dist2 * frequency - time);

v@P.y = chf('../../gridY') / 2 + (wave1 + wave2) * amplitude;
```

---

### Plasma Scenes

**Approach:** Volumetric noise field determines particle visibility

**Configuration:**
- **particleDensity:** 0.8 (fill volume with particles)
- **turbulence:** 0.3 (shimmering)
- **flowDirection:** drift (slow evolution)
- **attractorStrength:** 0.0 (no shape)

**Particle Distribution:**

**POP Source:**
- **Emission Type:** Volume (Box)
- **Fill entire grid space**

**POP Wrangle (Plasma Visibility):**
```c
float scale = chf('../size') * 0.1;
float complexity = chf('../frequency') * 2;
float threshold = chf('../amplitude');
int layers = chi('../detailLevel');
float time = chf('absTime.seconds');

// Multi-layered sine waves (plasma function)
float value = 0;
value += sin((v@P.x * scale + time) * complexity);
value += sin((v@P.y * scale + time * 0.8) * complexity);
value += sin((v@P.z * scale + time * 0.6) * complexity);
value += sin(length(set(v@P.x, v@P.y, 0)) * scale * complexity + time);

if (layers > 1) {
    value += sin((v@P.x + v@P.y) * scale * 0.5 + time * 1.2) * 0.5;
}
if (layers > 2) {
    value += sin((v@P.y + v@P.z) * scale * 0.5 + time * 0.9) * 0.5;
}
if (layers > 3) {
    value += sin((v@P.x + v@P.z) * scale * 0.5 + time * 0.7) * 0.5;
}

// Normalize
float maxValue = 4.0 + (layers - 1) * 0.5;
value = (value + maxValue) / (maxValue * 2);

// Threshold visibility
if (value < threshold) {
    f@Alpha = 0;
    // Or remove
    removepoint(0, i@ptnum);
} else {
    f@Alpha = 1;

    // Optional: Color based on value
    v@Cd = set(value, value * 0.5, 1.0 - value);
}
```

**Alternative: Use Volume SOP**

Create a volume with plasma function, then scatter points based on density:

1. `volumevop1` - Generate plasma volume
2. `scatter1` - Scatter points by density
3. `add1` - Add to POP network

---

## Parameter Control

### Control Panel Setup

Create a **Custom Parameter COMP** to house all parameters:

**Parameters:**

```python
# Morphology
formCoherence: Float, 0-1, default 0.8
particleDensity: Float, 0-1, default 0.6
flowIntensity: Float, 0-1, default 0.5
turbulence: Float, 0-1, default 0.3
attractorStrength: Float, 0-1, default 0.7

# Shape
baseShape: Menu (sphere, helix, torus, cube, pyramid, plane), default sphere
shapeThickness: Float, 0.1-1, default 0.5

# Flow
flowDirection: Menu (none, fall, rise, spiral, explode, implode, drift), default none
flowVelocity: Float, 0-2, default 1.0

# Size/Scale
size: Float, 0.1-3, default 1.0

# Grid dimensions
gridX: Int, default 48
gridY: Int, default 24
gridZ: Int, default 48

# Movement (all Float 0-1, default 0)
rotationX, rotationY, rotationZ
translateX, translateZ, translateAmplitude
bounceSpeed, bounceHeight
orbitSpeed, orbitRadius
pulseSpeed, pulseAmount
spiralSpeed, spiralRadius, spiralHeight
wobbleSpeed, wobbleAmount
figure8Speed, figure8Size
ellipseSpeed, ellipseRadiusX, ellipseRadiusZ
scrollSpeed
scrollDirection: Menu (x, y, z, diagonal)
objectArrangement: Menu (circular, linear)
objectOffset: Float, 0-1

# Object count
objectCount: Int, 1-4, default 1
```

### CHOP Export

Use **Select CHOP** or **Null CHOP** to export parameters to POP network:

```
constant1 (for each parameter) → null_params → Export to POP nodes
```

Or reference directly:
```python
op('control_panel').par.formCoherence
```

### Preset System

Create **Table DAT** with presets:

| Preset Name | formCoherence | attractorStrength | turbulence | flowDirection | ... |
|-------------|---------------|-------------------|------------|---------------|-----|
| Solid Sphere | 1.0 | 1.0 | 0.0 | none | ... |
| Dissolve | 0.3 | 0.2 | 0.7 | none | ... |
| Rain | 0.2 | 0.0 | 0.3 | fall | ... |
| Tornado | 0.5 | 0.4 | 0.6 | spiral | ... |

**Python Script** to load presets:
```python
def LoadPreset(presetName):
    table = op('presets')
    row = table.row(presetName)

    for i, cellValue in enumerate(row[1:]): # Skip name column
        paramName = table[0, i+1].val
        parent().par[paramName] = float(cellValue)
```

---

## Rendering & Output

### Instance Rendering

**Method 1: Geometry COMP Instancing**

```
POP Output → Geometry COMP → Material → Render
```

**Geometry COMP:**
- **Instance:** Point instancing
- **Instance Geometry:** sphere/box (small primitive)
- **Scale:** Use `pscale` attribute from particles

**Set pscale in POP Wrangle:**
```c
f@pscale = 0.5; // Particle size
```

### Point Sprites

**Method 2: Point Sprite TOP**

```
POP Output → Point Sprite MAT
```

Better for large particle counts, GPU-accelerated.

### Volumetric Rendering

**Method 3: Convert to Volume**

```
POP Output → Volume SOP → Volume Select SOP → Raymarching shader
```

**Volume SOP:**
- **Mode:** Particles to Volume
- **Particle Scale:** Based on pscale
- **Voxel Size:** Match grid resolution

### Color Attributes

**POP Wrangle (Color by position):**
```c
// Color based on height
float heightRatio = v@P.y / chf('../gridY');
v@Cd = set(heightRatio, 0.5, 1.0 - heightRatio);
```

**POP Wrangle (Color by velocity):**
```c
float speed = length(v@v);
float speedNorm = fit(speed, 0, 5, 0, 1);
v@Cd = set(speedNorm, 0.3, 1.0 - speedNorm);
```

---

## Optimization

### Performance Tips

1. **Use GPU POPs** (`particleGPU`) when possible
2. **Particle count limits:**
   - CPU POPs: ~50k particles max
   - GPU POPs: ~500k particles max
3. **Reduce POP Wrangle calls:** Combine logic into fewer wrangles
4. **Use compiled blocks:** Wrap SOPs in compiled blocks
5. **Cache attractors:** If shape doesn't change, use `fileCache` SOP
6. **LOD system:** Reduce particle count when not in focus

### Memory Management

**POP Limit:** Always use to cap particle count

**Particle Recycling:** Reuse particles instead of birth/death

```c
// Reset position instead of killing
if (v@P.y < 0) {
    v@P.y = chf('../gridY');
}
```

### Multi-threading

Enable **Multi-threading** in:
- POP Solver settings
- Individual POP nodes where available

### Caching

**File Cache SOP** for attractor geometry:
```
Shape SOPs → File Cache → POP Attract
```

Only recalculate when parameters change.

---

## Advanced Techniques

### Particle Trails

**Trail SOP** after POP Output:
```
POP Output → Trail SOP → Render
```

**Trail SOP settings:**
- **Result Type:** Add Trails
- **Trail Length:** 10-20 frames
- **Compute Velocity:** ON

### Inter-Particle Forces

**POP Interact:**
```
popattract1 → popinteract1 → ...
```

**Settings:**
- **Force:** -0.1 (repulsion) or 0.1 (attraction)
- **Radius:** 2.0

For flocking behavior.

### Force Field Visualization

**POP Force Visualize:**
Show force vectors for debugging.

### Custom Attributes

**Store custom data in POP Wrangle:**
```c
// Store distance from center
vector center = set(chf('../gridX')/2, chf('../gridY')/2, chf('../gridZ')/2);
f@distFromCenter = distance(v@P, center);

// Use in rendering
v@Cd = set(f@distFromCenter / 20, 0.5, 1.0);
```

---

## Troubleshooting

### Particles Not Appearing
- Check birth rate in POP Source
- Verify POP Limit isn't set too low
- Check coherence wrangle isn't culling all particles

### Particles Exploding
- Reduce force magnitudes
- Add **POP Limit** with max speed
- Check for divide-by-zero in wrangles

### Slow Performance
- Reduce particle count
- Simplify attractor geometry (fewer points)
- Use GPU POPs
- Reduce number of POP Wrangle nodes

### Shape Not Forming
- Increase `attractorStrength`
- Reduce `turbulence`
- Verify attractor geometry exists
- Check POP Attract goal weight

---

## Complete Example Network

**Full chain for Hybrid Morph Sphere:**

```
Control Panel COMP
  ↓
┌─────────────────────────────────────────────────┐
│ SOP Level (Attractor)                           │
│   sphere1                                       │
│     → resample1                                 │
│     → transform1 (global movements)             │
│     → null_attractor                            │
└─────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────┐
│ POP Level                                       │
│   popsource1 (birth rate from density)          │
│     → popattract1 (to null_attractor)           │
│          - Goal Weight: attractorStrength       │
│     → popforce_flow                             │
│          - Direction/velocity from params       │
│     → popwind_turbulence                        │
│          - Amplitude from turbulence param      │
│     → popwrangle_coherence                      │
│          - Stochastic culling by formCoherence  │
│     → poplimit1 (cap max particles)             │
│     → output1                                   │
└─────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────┐
│ Render                                          │
│   Geometry COMP (instancing)                    │
│     → Phong MAT                                 │
│     → Render TOP                                │
└─────────────────────────────────────────────────┘
```

---

## Conclusion

This TouchDesigner implementation provides a complete particle-based system that unifies shape morphing and particle flow behaviors. By leveraging POP forces, attractors, and custom wrangles, you can achieve smooth transitions between solid geometric forms and organic particle effects.

The key to the hybrid approach is **force composition**: particles respond to multiple simultaneous influences (shape attraction, flow direction, turbulence) with parameters controlling the strength of each. This creates a rich, expressive system for real-time volumetric art.

**Next Steps:**
1. Build the basic POP network with sphere attractor
2. Add parameter control panel
3. Implement remaining shape types
4. Add flow patterns and turbulence
5. Create preset system
6. Optimize and test performance

Happy particle wrangling!
