# TouchDesigner Optical Illusions Guide
## Hybrid Morph System Implementation

This guide provides detailed instructions for implementing optical illusion scenes in TouchDesigner using the Hybrid Morph particle system. Each illusion is adapted to work with the particle-based attractor approach.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Illusion Implementations](#illusion-implementations)
   - [1. Rotating Ames Room](#1-rotating-ames-room)
   - [2. Infinite Corridor](#2-infinite-corridor)
   - [3. Kinetic Depth Effect](#3-kinetic-depth-effect)
   - [4. Waterfall Illusion](#4-waterfall-illusion)
   - [5. Penrose Triangle](#5-penrose-triangle)
   - [6. Necker Cube](#6-necker-cube)
   - [7. Fraser Spiral](#7-fraser-spiral)
   - [8. Café Wall Illusion](#8-café-wall-illusion)
   - [9. Pulfrich Effect](#9-pulfrich-effect)
   - [10. Rotating Snakes](#10-rotating-snakes)
   - [11. Breathing Square](#11-breathing-square)
   - [12. Moiré Pattern](#12-moiré-pattern)
3. [Parameter Configuration](#parameter-configuration)
4. [Performance Optimization](#performance-optimization)

---

## System Overview

### Grid Specifications

- **Default Dimensions:** 40 (X) × 20 (Y) × 40 (Z)
- **Coordinate System:**
  - X: Width (left to right)
  - Y: Height (bottom to top)
  - Z: Depth (back to front)
- **Center Point:** (gridX/2, gridY/2, gridZ/2)

### Hybrid System Integration

All illusions are implemented using:
- **Particle Attractors:** Custom SOP geometry defines particle target positions
- **Force Modulation:** Flow forces and turbulence add motion dynamics
- **Coherence Control:** formCoherence parameter controls solidity vs particle cloud appearance
- **Time Animation:** absTime.seconds drives all animations

### Common POP Network Structure

```
popsource1
  → popattract1 (custom illusion attractor)
  → popwrangle_illusion (illusion-specific logic)
  → popwrangle_coherence (visibility control)
  → poplimit1
  → output1
```

---

## Illusion Implementations

### 1. Rotating Ames Room

**Concept:** A trapezoid that rotates but maintains the illusion of a rectangular room through forced perspective.

#### Hybrid Parameters

```python
formCoherence: 0.9          # Solid edges
attractorStrength: 0.8      # Particles locked to trapezoid edges
turbulence: 0.1             # Minimal chaos
particleDensity: 0.4        # Sparse wireframe
flowDirection: none
```

#### Attractor SOP Construction

**Node Chain:** `python1` → `resample1` → `transform1` → `null_ames_attractor`

**Python SOP (Trapezoid Generator):**
```python
import math

geo = hou.pwd().geo

# Parameters
size = hou.evalParm('../../size')
depth = hou.evalParm('../../depth')
gridY = hou.evalParm('../../gridY')
time = hou.frame() / hou.fps()
speed = hou.evalParm('../../animationSpeed')

angle = time * speed * 0.3
trapezoidScale = 0.6 + 0.4 * depth

# Create rotating trapezoid
for y in range(int(gridY)):
    yNorm = y / gridY
    scaleAtY = 1.0 - yNorm * (1.0 - trapezoidScale)

    # 4 edges of square at this Y level
    for i in range(4):
        edgeAngle = angle + (i * math.pi / 2)
        nextAngle = angle + ((i + 1) * math.pi / 2)

        # Create edge line
        for t in [x * 0.1 for x in range(11)]:
            lerpAngle = edgeAngle + (nextAngle - edgeAngle) * t
            radius = 10 * size * scaleAtY

            x = math.cos(lerpAngle) * radius
            z = math.sin(lerpAngle) * radius

            pt = geo.createPoint()
            pt.setPosition((x, y - gridY/2, z))
```

**Resample Settings:**
- Length: 0.5 (smooth edges)

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0) - overall scale
- **animationSpeed:** 0.0 - 3.0 (default 1.0) - rotation speed
- **depth:** 0.0 - 2.0 (default 1.0) - trapezoid distortion amount

---

### 2. Infinite Corridor

**Concept:** Nested rectangles scrolling from back to front creating a Droste/tunnel effect.

#### Hybrid Parameters

```python
formCoherence: 0.85         # Solid frames
attractorStrength: 0.9      # Locked to frame edges
turbulence: 0.05            # Very minimal
particleDensity: 0.5        # Medium density
flowDirection: none         # Handled by custom attractor animation
```

#### Attractor SOP Construction

**Node Chain:** `python1` → `resample1` → `null_corridor_attractor`

**Python SOP (Scrolling Frames):**
```python
import math

geo = hou.pwd().geo

# Parameters
size = hou.evalParm('../../size')
depth = hou.evalParm('../../depth')
spacing_param = hou.evalParm('../../spacing')
speed = hou.evalParm('../../animationSpeed')
gridX = hou.evalParm('../../gridX')
gridY = hou.evalParm('../../gridY')
gridZ = hou.evalParm('../../gridZ')
time = hou.frame() / hou.fps()

# Calculate spacing
frameSpacing = max(3, int(4 * spacing_param))
numFrames = int(5 + depth * 5)
scrollOffset = (time * speed * 3) % frameSpacing

for frame in range(numFrames):
    # Position from back to front with scrolling
    baseZ = gridZ - 1 - (frame * frameSpacing) + scrollOffset
    z = baseZ % gridZ

    # Scale increases toward front
    normalizedPos = (baseZ / gridZ + 1) % 1
    scale = 0.2 + normalizedPos * 0.8 * size

    if scale <= 0:
        continue

    width = int(gridX / 2 * scale)
    height = int(gridY / 2 * scale)

    # Draw rectangle outline
    # Top edge
    for x in range(-width, width + 1):
        pt = geo.createPoint()
        pt.setPosition((x, height, z - gridZ/2))

    # Bottom edge
    for x in range(-width, width + 1):
        pt = geo.createPoint()
        pt.setPosition((x, -height, z - gridZ/2))

    # Left edge
    for y in range(-height, height + 1):
        pt = geo.createPoint()
        pt.setPosition((-width, y, z - gridZ/2))

    # Right edge
    for y in range(-height, height + 1):
        pt = geo.createPoint()
        pt.setPosition((width, y, z - gridZ/2))
```

**Resample Settings:**
- Length: 0.3 (smooth frames)

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0)
- **depth:** 0.0 - 2.0 (default 1.0) - number of frames
- **spacing:** 0.0 - 2.0 (default 1.0) - frame separation
- **animationSpeed:** 0.0 - 3.0 (default 1.0)

---

### 3. Kinetic Depth Effect

**Concept:** 2D sine wave pattern that appears 3D when rotating.

#### Hybrid Parameters

```python
formCoherence: 0.7          # Medium solidity
attractorStrength: 0.8      # Strong lock to wave pattern
turbulence: 0.15            # Slight shimmer
particleDensity: 0.6        # Medium density
flowDirection: none
rotationY: 0.5              # Use global rotation parameter
```

#### Attractor SOP Construction

**Node Chain:** `python1` → `resample1` → `transform1` → `null_kinetic_attractor`

**Python SOP (Rotating Sine Waves):**
```python
import math

geo = hou.pwd().geo

size = hou.evalParm('../../size')
speed = hou.evalParm('../../animationSpeed')
time = hou.frame() / hou.fps()

angle = time * speed * 0.5
numWaves = 8
radius = 12 * size

for i in range(numWaves):
    wavePhase = (i / float(numWaves)) * math.pi * 2

    # Create wave curve
    steps = 50
    for step in range(steps):
        t = step / float(steps)
        theta = t * math.pi * 2
        sinValue = math.sin(theta * 3 + wavePhase)

        # 2D projection
        x2d = math.cos(theta) * radius
        y2d = sinValue * 5

        # Rotate in 3D
        x3d = x2d * math.cos(angle)
        z3d = x2d * math.sin(angle)

        pt = geo.createPoint()
        pt.setPosition((x3d, y2d, z3d))
```

**Transform (for rotation):**
- Use parent().par.rotationY to continue rotation

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0)
- **animationSpeed:** 0.0 - 3.0 (default 1.0)
- **rotationY:** 0.0 - 1.0 - adds continuous rotation

---

### 4. Waterfall Illusion

**Concept:** Vertical scrolling stripes with stationary reference grid creating motion aftereffect.

#### Hybrid Parameters

```python
formCoherence: 0.8          # Solid stripes
attractorStrength: 0.9      # Locked to stripe positions
turbulence: 0.0             # No chaos needed
particleDensity: 0.8        # Dense for visible stripes
flowDirection: none         # Custom flow in wrangle
```

#### Implementation Approach

This illusion uses **particle position modulation** rather than attractor SOP.

**Node Chain:** `popsource1` → `popwrangle_waterfall` → `popwrangle_coherence` → `output1`

**POP Wrangle (Waterfall Pattern):**
```c
float speed = chf('../animationSpeed');
float density = chf('../density');
float time = chf('absTime.seconds');
float offset = time * speed * 10;

float gridX = chf('../gridX');
float gridY = chf('../gridY');
float gridZ = chf('../gridZ');

int stripeSpacing = int(max(2, 5 - density * 3));

// Position particles in volume
if (@age < 0.01) { // Initialize
    v@P.x = random(@id * 1.234) * gridX - gridX/2;
    v@P.y = random(@id * 2.345) * gridY - gridY/2;
    v@P.z = random(@id * 3.456) * gridZ - gridZ/2;
}

// Moving stripe pattern
float pattern = fmod((v@P.z + gridZ/2 + offset), stripeSpacing * 2);
int isStripe = pattern < stripeSpacing;

// Stationary reference grid
int isRefGrid = (int(v@P.y + gridY/2) % 5) == 0;

if (isStripe) {
    f@Alpha = 1.0;
    v@Cd = set(1, 1, 1);
} else if (isRefGrid) {
    f@Alpha = 0.3;
    v@Cd = set(0.5, 0.5, 0.5);
} else {
    f@Alpha = 0.0;
}
```

#### Key Parameters

- **animationSpeed:** 0.0 - 3.0 (default 1.0)
- **density:** 0.0 - 1.0 (default 0.5) - stripe spacing

---

### 5. Penrose Triangle

**Concept:** Impossible triangle created by three bars that appear connected but violate 3D geometry.

#### Hybrid Parameters

```python
formCoherence: 0.85         # Solid bars
attractorStrength: 0.9      # Locked to bar geometry
turbulence: 0.05            # Minimal
particleDensity: 0.5        # Medium
flowDirection: none
rotationY: 0.3              # Rotating illusion
```

#### Attractor SOP Construction

**Node Chain:** `python1` → `resample1` → `transform1` → `null_penrose_attractor`

**Python SOP (Impossible Triangle Bars):**
```python
import math

geo = hou.pwd().geo

size = hou.evalParm('../../size')
speed = hou.evalParm('../../animationSpeed')
time = hou.frame() / hou.fps()

angle = time * speed * 0.3
scale = 8 * size
thickness = 2

# Three bars forming impossible triangle
bars = [
    {'start': [0, 0, 0], 'end': [1, 0, 0], 'offset': [0, 0, 0.5]},
    {'start': [1, 0, 0], 'end': [0.5, 1, 0], 'offset': [0, 0, 0]},
    {'start': [0.5, 1, 0], 'end': [0, 0, 0], 'offset': [0.5, 0, 0]}
]

for bar in bars:
    steps = 20
    for step in range(steps):
        t = step / float(steps)

        # Interpolate along bar
        x = (bar['start'][0] + (bar['end'][0] - bar['start'][0]) * t - 0.5) * scale
        y = (bar['start'][1] + (bar['end'][1] - bar['start'][1]) * t - 0.5) * scale
        z = (bar['start'][2] + (bar['end'][2] - bar['start'][2]) * t + bar['offset'][2] * t) * scale

        # Rotate
        xRot = x * math.cos(angle) - z * math.sin(angle)
        zRot = x * math.sin(angle) + z * math.cos(angle)

        # Create thick bar (multiple points for thickness)
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                pt = geo.createPoint()
                pt.setPosition((xRot + dx, y + dy, zRot))
```

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0)
- **animationSpeed:** 0.0 - 3.0 (default 1.0)

---

### 6. Necker Cube

**Concept:** Wireframe cube with ambiguous depth perception.

#### Hybrid Parameters

```python
formCoherence: 0.9          # Solid wireframe
attractorStrength: 0.95     # Very locked
turbulence: 0.0             # No turbulence
particleDensity: 0.3        # Sparse wireframe
flowDirection: none
baseShape: cube             # Use built-in cube as base
shapeThickness: 0.1         # Thin wireframe
```

#### Attractor SOP Construction

**Node Chain:** `box1` → `divide1` → `wireframe1` → `resample1` → `null_necker_attractor`

**Box Settings:**
- Size: ch('../../size') * 20 (all axes)

**Divide Settings:**
- Size: 1 (creates edge subdivisions)

**Wireframe Settings:**
- Width: ch('../../thickness') * 0.5
- Profile: 4 sides

**Resample:**
- Length: 0.5

**Alternative: Python SOP for precise control:**
```python
import math

geo = hou.pwd().geo

size = hou.evalParm('../../size')
thickness = max(1, int(hou.evalParm('../../thickness') * 2))
cubeSize = 10 * size

# 8 corners
corners = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
]

# 12 edges
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Back
    (4, 5), (5, 6), (6, 7), (7, 4),  # Front
    (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting
]

for edge in edges:
    start = corners[edge[0]]
    end = corners[edge[1]]

    steps = 20
    for step in range(steps):
        t = step / float(steps)

        x = (start[0] + (end[0] - start[0]) * t) * cubeSize
        y = (start[1] + (end[1] - start[1]) * t) * cubeSize
        z = (start[2] + (end[2] - start[2]) * t) * cubeSize

        # Add thickness
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                for dz in range(-thickness, thickness + 1):
                    pt = geo.createPoint()
                    pt.setPosition((x + dx, y + dy, z + dz))
```

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0)
- **thickness:** 0.0 - 2.0 (default 0.5)

---

### 7. Fraser Spiral

**Concept:** Concentric circles with diagonal patterns appearing as a spiral.

#### Hybrid Parameters

```python
formCoherence: 0.75         # Medium-solid
attractorStrength: 0.8      # Strong circle lock
turbulence: 0.1             # Slight variation
particleDensity: 0.7        # Dense pattern
flowDirection: none
rotationZ: 0.2              # Slow rotation enhances illusion
```

#### Attractor SOP Construction

**Node Chain:** `python1` → `resample1` → `transform1` → `null_fraser_attractor`

**Python SOP (Spiral Circles with Diagonal Pattern):**
```python
import math

geo = hou.pwd().geo

size = hou.evalParm('../../size')
frequency = hou.evalParm('../../frequency')
speed = hou.evalParm('../../animationSpeed')
gridX = hou.evalParm('../../gridX')
gridY = hou.evalParm('../../gridY')
time = hou.frame() / hou.fps()

numCircles = int(8 * size)
rotation = time * speed * 0.2

for circle in range(1, numCircles + 1):
    radius = (circle / float(numCircles)) * (gridX / 2 - 2)
    numSegments = int(circle * 8 * frequency)

    for seg in range(numSegments):
        angle = (seg / float(numSegments)) * math.pi * 2 + rotation

        # Alternating brightness (use color attribute)
        brightness = 1.0 if seg % 2 == 0 else 0.3

        x = math.cos(angle) * radius
        z = math.sin(angle) * radius

        # Diagonal segments in Y
        for y_step in range(int(gridY)):
            yOffset = int((math.sin(angle * 4) * 3 + y_step / 2.0)) % int(gridY)

            pt = geo.createPoint()
            pt.setPosition((x, yOffset - gridY/2, z))
            pt.setAttribValue('Cd', (brightness, brightness, brightness))
```

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0)
- **frequency:** 0.0 - 3.0 (default 1.0) - segments per circle
- **animationSpeed:** 0.0 - 3.0 (default 1.0)

---

### 8. Café Wall Illusion

**Concept:** Offset checkerboard with gray mortar lines appearing tilted.

#### Hybrid Parameters

```python
formCoherence: 1.0          # Completely solid
attractorStrength: 1.0      # Fully locked
turbulence: 0.0             # No variation
particleDensity: 0.9        # Very dense for solid tiles
flowDirection: none
```

#### Implementation Approach

Best implemented as **volumetric particle distribution** rather than attractor.

**Node Chain:** `popsource1` → `popwrangle_cafewall` → `output1`

**POP Wrangle (Café Wall Pattern):**
```c
float size_param = chf('../size');
float spacing_param = chf('../spacing');
float gridX = chf('../gridX');
float gridY = chf('../gridY');
float gridZ = chf('../gridZ');

int tileSize = int(max(2, 3 * size_param));
int offset = int(tileSize * 0.5);

// Initialize particle in grid
if (@age < 0.01) {
    v@P.x = random(@id * 1.1) * gridX - gridX/2;
    v@P.y = random(@id * 2.2) * gridY - gridY/2;
    v@P.z = random(@id * 3.3) * gridZ - gridZ/2;
}

int x = int(v@P.x + gridX/2);
int y = int(v@P.y + gridY/2);

// Row offset (alternating)
int rowOffset = ((y / tileSize) % 2 == 0) ? 0 : offset;

// Tile color
int adjustedX = x + rowOffset;
int tileColor = ((adjustedX / tileSize) % 2) == 0 ? 1 : 0;

// Mortar lines (gray)
int isMortar = (y % tileSize) == 0 && y > 0;

if (isMortar) {
    v@Cd = set(0.5, 0.5, 0.5);
    f@Alpha = 1.0;
} else if (tileColor) {
    v@Cd = set(1, 1, 1);
    f@Alpha = 1.0;
} else {
    v@Cd = set(0, 0, 0);
    f@Alpha = 1.0;
}
```

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0) - tile size
- **spacing:** 0.0 - 2.0 (default 1.0)

---

### 9. Pulfrich Effect

**Concept:** Objects moving in a circle with varying brightness creating 3D depth illusion.

#### Hybrid Parameters

```python
formCoherence: 0.8          # Solid spheres
attractorStrength: 0.9      # Locked to orbital positions
turbulence: 0.1             # Slight shimmer
particleDensity: 0.6        # Medium
flowDirection: none         # Custom orbital motion
```

#### Attractor SOP Construction

**Node Chain:** `python1` → `copy1` → `null_pulfrich_attractor`

**Python SOP (Single Sphere):**
```python
geo = hou.pwd().geo

# Create small sphere
sphere = geo.createSphere(radius=2)
```

**Copy to Points (Orbital Path):**
```python
# In a separate Python SOP for copy points
import math

geo = hou.pwd().geo

speed = hou.evalParm('../../animationSpeed')
size = hou.evalParm('../../size')
time = hou.frame() / hou.fps()

angle = time * speed
radius = 12 * size
numObjects = 8

for i in range(numObjects):
    objAngle = angle + (i / float(numObjects)) * math.pi * 2

    x = math.cos(objAngle) * radius
    z = math.sin(objAngle) * radius

    # Brightness varies with position
    brightness = 0.5 + 0.5 * math.sin(objAngle)

    pt = geo.createPoint()
    pt.setPosition((x, 0, z))
    pt.setAttribValue('Cd', (brightness, brightness, brightness))
```

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0)
- **animationSpeed:** 0.0 - 3.0 (default 1.0)

---

### 10. Rotating Snakes

**Concept:** Concentric rings with alternating patterns appearing to rotate independently.

#### Hybrid Parameters

```python
formCoherence: 0.7          # Medium solidity
attractorStrength: 0.75     # Moderate lock
turbulence: 0.2             # Some variation
particleDensity: 0.75       # Dense rings
flowDirection: none
```

#### Implementation Approach

**Node Chain:** `popsource1` → `popwrangle_snakes` → `output1`

**POP Wrangle (Rotating Snake Pattern):**
```c
float size_param = chf('../size');
float speed = chf('../animationSpeed');
float time = chf('absTime.seconds');
float gridX = chf('../gridX');
float gridY = chf('../gridY');
float gridZ = chf('../gridZ');

int numRings = int(4 * size_param);
float rotation = time * speed * 0.1;

// Pattern brightness lookup
float patternBrightness[] = {1.0, 0.7, 0.3, 0.7};

// Initialize particle in volume
if (@age < 0.01) {
    v@P.x = random(@id * 1.5) * gridX - gridX/2;
    v@P.y = random(@id * 2.5) * gridY - gridY/2;
    v@P.z = random(@id * 3.5) * gridZ - gridZ/2;
}

// Calculate distance from center (XZ plane)
float distXZ = length(set(v@P.x, 0, v@P.z));

// Determine which ring
int ring = int(distXZ / 5.0);

if (ring < numRings) {
    float angle = atan2(v@P.z, v@P.x);
    float ringRotation = rotation + ring * 0.5;

    int numSegments = 16;
    int seg = int(fmod((angle + ringRotation) / (2 * PI) * numSegments, numSegments));

    int pattern = (seg / 4) % 4;
    float brightness = patternBrightness[pattern];

    // Y pattern variation
    int yPattern = (int(v@P.y + gridY/2) + seg) % 4;
    float yBrightness = yPattern < 2 ? brightness : brightness * 0.5;

    v@Cd = set(yBrightness, yBrightness, yBrightness);
    f@Alpha = 1.0;
} else {
    f@Alpha = 0.0;
}
```

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0)
- **animationSpeed:** 0.0 - 3.0 (default 1.0)

---

### 11. Breathing Square

**Concept:** 3D checkerboard that pulses based on distance from center.

#### Hybrid Parameters

```python
formCoherence: 0.9          # Solid checkerboard
attractorStrength: 0.9      # Locked to grid
turbulence: 0.05            # Minimal
particleDensity: 0.85       # Very dense
flowDirection: none
```

#### Implementation Approach

**Node Chain:** `popsource1` → `popwrangle_breathing` → `output1`

**POP Wrangle (Breathing Checkerboard):**
```c
float size_param = chf('../size');
float frequency = chf('../frequency');
float time = chf('absTime.seconds');
float gridX = chf('../gridX');
float gridY = chf('../gridY');
float gridZ = chf('../gridZ');

int checkSize = int(max(2, 4 * size_param));
float pulse = sin(time * frequency * 2) * 0.2 + 1.0;

// Initialize in volume
if (@age < 0.01) {
    v@P.x = random(@id * 1.6) * gridX - gridX/2;
    v@P.y = random(@id * 2.6) * gridY - gridY/2;
    v@P.z = random(@id * 3.6) * gridZ - gridZ/2;
}

// Checkerboard with scrolling
int checkX = int((v@P.x + gridX/2 + time * 2) / checkSize);
int checkY = int((v@P.y + gridY/2) / checkSize);
int checkZ = int((v@P.z + gridZ/2) / checkSize);

int isLight = (checkX + checkY + checkZ) % 2 == 0;

// Distance from center for pulsing
float dx = v@P.x;
float dy = v@P.y;
float dz = v@P.z;
float distSq = dx*dx + dy*dy + dz*dz;
float distNorm = distSq / ((gridX/2) * (gridX/2));

float brightness = isLight ? pulse : (1.0 - distNorm * 0.1);
float value = brightness * (isLight ? 1.0 : 0.3);

v@Cd = set(value, value, value);
f@Alpha = 1.0;
```

#### Key Parameters

- **size:** 0.0 - 2.0 (default 1.0)
- **frequency:** 0.0 - 3.0 (default 1.0)

---

### 12. Moiré Pattern

**Concept:** Two overlapping grids, one rotating, creating interference patterns.

#### Hybrid Parameters

```python
formCoherence: 0.85         # Solid grids
attractorStrength: 0.9      # Locked to grid lines
turbulence: 0.0             # No variation
particleDensity: 0.8        # Dense for visible grids
flowDirection: none
```

#### Implementation Approach

**Node Chain:** `popsource1` → `popwrangle_moire` → `output1`

**POP Wrangle (Moiré Interference):**
```c
float spacing_param = chf('../spacing');
float speed = chf('../animationSpeed');
float time = chf('absTime.seconds');
float gridX = chf('../gridX');
float gridY = chf('../gridY');
float gridZ = chf('../gridZ');

int gridSpacing = int(max(2, 3 * spacing_param));
float angle = time * speed * 0.1;
float cosAngle = cos(angle);
float sinAngle = sin(angle);

// Initialize
if (@age < 0.01) {
    v@P.x = random(@id * 1.7) * gridX - gridX/2;
    v@P.y = random(@id * 2.7) * gridY - gridY/2;
    v@P.z = random(@id * 3.7) * gridZ - gridZ/2;
}

float value = 0.0;

// First grid (stationary vertical lines)
int xGrid = int(v@P.x + gridX/2);
if (xGrid % gridSpacing == 0) {
    value += 0.5;
}

// Second grid (rotating)
float cx = v@P.x;
float cz = v@P.z;

// Rotate coordinates
float rx = cx * cosAngle - cz * sinAngle;
float rotatedX = rx + gridX/2;

if (int(rotatedX) % gridSpacing == 0) {
    value += 0.5;
}

value = min(1.0, value);
v@Cd = set(value, value, value);
f@Alpha = value > 0 ? 1.0 : 0.0;
```

#### Key Parameters

- **spacing:** 0.0 - 2.0 (default 1.0) - grid line spacing
- **animationSpeed:** 0.0 - 3.0 (default 1.0)

---

## Parameter Configuration

### Recommended Control Panel Setup

Create a **Custom Parameter COMP** with illusion-specific parameters:

```python
# Base Parameters (all illusions)
size: Float, 0.0-2.0, default 1.0
animationSpeed: Float, 0.0-3.0, default 1.0

# Hybrid System Core
formCoherence: Float, 0.0-1.0, default 0.8
attractorStrength: Float, 0.0-1.0, default 0.8
turbulence: Float, 0.0-1.0, default 0.1
particleDensity: Float, 0.0-1.0, default 0.6

# Illusion-Specific
depth: Float, 0.0-2.0, default 1.0          # Ames, Corridor
spacing: Float, 0.0-2.0, default 1.0        # Corridor, Café Wall, Moiré
thickness: Float, 0.0-2.0, default 0.5      # Necker Cube
frequency: Float, 0.0-3.0, default 1.0      # Fraser, Breathing, Plasma
density: Float, 0.0-1.0, default 0.5        # Waterfall
amplitude: Float, 0.0-2.0, default 1.0      # Waves

# Grid Dimensions
gridX: Int, default 40
gridY: Int, default 20
gridZ: Int, default 40
```

### Preset Table

Create a **Table DAT** with recommended presets:

| Illusion | formCoherence | attractorStrength | turbulence | particleDensity | Notes |
|----------|---------------|-------------------|------------|-----------------|-------|
| Ames Room | 0.9 | 0.8 | 0.1 | 0.4 | Sparse wireframe |
| Corridor | 0.85 | 0.9 | 0.05 | 0.5 | Solid frames |
| Kinetic Depth | 0.7 | 0.8 | 0.15 | 0.6 | Medium with shimmer |
| Waterfall | 0.8 | 0.9 | 0.0 | 0.8 | Dense stripes |
| Penrose | 0.85 | 0.9 | 0.05 | 0.5 | Solid bars |
| Necker Cube | 0.9 | 0.95 | 0.0 | 0.3 | Thin wireframe |
| Fraser Spiral | 0.75 | 0.8 | 0.1 | 0.7 | Dense pattern |
| Café Wall | 1.0 | 1.0 | 0.0 | 0.9 | Completely solid |
| Pulfrich | 0.8 | 0.9 | 0.1 | 0.6 | Solid spheres |
| Snakes | 0.7 | 0.75 | 0.2 | 0.75 | Dense rings |
| Breathing | 0.9 | 0.9 | 0.05 | 0.85 | Dense grid |
| Moiré | 0.85 | 0.9 | 0.0 | 0.8 | Clear grids |

---

## Performance Optimization

### Particle Count Guidelines

- **Sparse wireframes** (Necker, Ames): 200-500 particles
- **Medium density** (Kinetic, Penrose, Fraser): 500-800 particles
- **Dense patterns** (Café Wall, Breathing, Moiré): 800-1200 particles
- **Volumetric** (Waterfall, Snakes): 1000-2000 particles

### Optimization Strategies

1. **Use GPU POPs** whenever possible for particle counts > 1000
2. **Resample attractor geometry** to reduce point count while maintaining shape
3. **Limit particle birth rate** based on particleDensity parameter
4. **Cache static attractors** using File Cache SOP
5. **Use POP Limit** to cap maximum particles
6. **Optimize POP Wrangle code**:
   - Minimize conditional branches
   - Use vector operations
   - Avoid expensive functions (sqrt, pow) when possible
   - Pre-calculate constants outside loops

### LOD System

Implement level-of-detail based on performance:

```c
// In POP Wrangle
float performanceScale = chf('../performanceScale'); // 0.5 = half particles

float cullChance = 1.0 - performanceScale;
if (random(@id + 5000) < cullChance) {
    removepoint(0, @ptnum);
}
```

---

## Rendering Recommendations

### Material Setup

**For solid illusions** (Café Wall, Necker Cube):
- Use **Constant MAT** with emissive color
- High formCoherence (0.9-1.0)
- Unlit rendering for crisp edges

**For dynamic illusions** (Kinetic Depth, Rotating Snakes):
- Use **Point Sprite MAT** for performance
- Medium formCoherence (0.6-0.8)
- Additive blending for glow effect

**For wireframe illusions** (Ames, Penrose):
- Use **Phong MAT** with thin geometry
- Wire material or instanced cylinders
- Edge detection post-processing

### Post-Processing

Enhance illusions with:
- **Bloom** for glowing effects (Pulfrich, Kinetic)
- **Edge detection** for crisp lines (Necker, Penrose)
- **Motion blur** for flow illusions (Waterfall, Snakes)
- **Chromatic aberration** for depth illusions (Pulfrich)

---

## Troubleshooting

### Illusion Not Visible

- Check **particleDensity** is high enough (> 0.5)
- Verify **formCoherence** is appropriate (0.6-1.0 for solid)
- Ensure **attractorStrength** is sufficient (> 0.7)
- Check POP Source birth rate

### Pattern Breaking Apart

- Increase **attractorStrength** (0.8-1.0)
- Reduce **turbulence** (< 0.2)
- Increase **formCoherence** (> 0.8)
- Check attractor geometry is valid

### Poor Performance

- Reduce **particleDensity** (< 0.6)
- Lower particle count in POP Limit
- Use GPU POPs instead of CPU
- Simplify attractor geometry
- Reduce resample resolution

### Animation Too Fast/Slow

- Adjust **animationSpeed** parameter (0.3-2.0)
- Check TimeScale in POP network
- Verify absTime.seconds is being used correctly

---

## Complete Example Network

**Full Rotating Ames Room Implementation:**

```
Control Panel COMP (parameters)
  ↓
┌─────────────────────────────────────────┐
│ Attractor SOP Level                     │
│   python_ames_generator                 │
│     → resample1 (smooth edges)          │
│     → transform1 (center)               │
│     → null_ames_attractor               │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ POP Level                               │
│   popsource1                            │
│     Birth Rate: particleDensity * 400   │
│     → popattract1                       │
│         Goal: null_ames_attractor       │
│         Weight: attractorStrength       │
│     → popwind1 (if turbulence > 0)      │
│         Amplitude: turbulence * 5       │
│     → popwrangle_coherence              │
│         Cull by formCoherence           │
│     → poplimit1                         │
│         Max: particleDensity * 500      │
│     → output1                           │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ Render                                  │
│   geometry1 (instance spheres)          │
│     → constantMAT1 (emissive white)     │
│     → render1                           │
└─────────────────────────────────────────┘
```

---

## Next Steps

1. **Start with simple illusions** (Necker Cube, Café Wall)
2. **Build custom parameter interface** with all controls
3. **Test performance** with different particle counts
4. **Create preset system** for quick switching
5. **Add color effects** based on position/velocity
6. **Experiment with hybrid parameters** for new variations
7. **Add UI for live parameter control**

---

## Conclusion

These optical illusion implementations leverage the Hybrid Morph system's particle-based approach to create dynamic, performant volumetric illusions. By using attractors for geometric precision and flow forces for dynamic motion, each illusion maintains its core perceptual effect while gaining the flexibility of the particle system.

The key to successful implementation is balancing **formCoherence** (visibility), **attractorStrength** (geometric fidelity), and **turbulence** (organic variation) to achieve the desired visual effect while maintaining real-time performance.

**Key Advantages of Hybrid Approach:**
- Smooth transitions between illusions
- Dynamic particle behaviors add life to static patterns
- Efficient rendering with GPU POPs
- Flexible parameter space for experimentation
- Easy integration with existing Hybrid Morph scenes

Happy illusion building!
