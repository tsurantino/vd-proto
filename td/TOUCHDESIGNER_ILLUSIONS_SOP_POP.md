# TouchDesigner Optical Illusions - SOP/POP Implementation
## Recreating Volumetric Display Illusions using Geometry & Particle Systems

This guide demonstrates how to recreate the optical illusions from the volumetric display prototype using TouchDesigner's native SOPs (Surface Operators) and POPs (Particle Operators) instead of a hybrid particle system.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Comparison](#architecture-comparison)
3. [Core Building Blocks](#core-building-blocks)
4. [Illusion Implementations](#illusion-implementations)
5. [Optimization & Performance](#optimization--performance)
6. [Integration with Color Effects](#integration-with-color-effects)

---

## Overview

### Why SOPs/POPs Instead of Hybrid Systems?

**SOP-Based Approach (Surface Operators):**
- Direct geometry manipulation
- Precise control over vertex positions
- Easy to animate transformations
- Better for structured, geometric illusions
- Native instancing for performance

**POP-Based Approach (Particle Operators):**
- Fluid, organic motion
- Natural handling of large point clouds
- Built-in forces and dynamics
- Better for flow-based, emergent patterns
- Excellent for density-based effects

**When to Use Each:**
- **SOPs**: Rotating Ames Room, Necker Cube, Café Wall, Moiré Pattern, Infinite Corridor
- **POPs**: Kinetic Depth, Waterfall Illusion, Pulfrich Effect
- **Hybrid**: Complex scenes requiring both structured geometry and particle dynamics

---

## Architecture Comparison

### Original JavaScript (Hybrid Particle System)
```
[Voxel Grid Array (30×50×30)]
    ↓
[Scene Rendering Functions]
    ↓
[Color Effects Applied Per-Voxel]
    ↓
[3D Projection & Canvas Rendering]
```

### TouchDesigner SOP Approach
```
[SOP Chain: Generate → Transform → Instance]
    ↓
[Attribute Manipulation (Color, Position)]
    ↓
[Geometry COMP → Material]
    ↓
[Render TOP or Direct 3D Output]
```

### TouchDesigner POP Approach
```
[POP Network: Source → Forces → Attributes]
    ↓
[Convert to Geometry (if needed)]
    ↓
[Instance/Render]
    ↓
[Output]
```

---

## Core Building Blocks

### Utility 1: Voxel Grid Generator (SOP)

**Purpose:** Create a 3D grid of points matching the volumetric display resolution

**Network:**
```
[Grid SOP: 'grid_xy']
    Settings:
    - Rows: 30
    - Columns: 30
    - Size: 30, 30
    - Orientation: XY
    ↓
[Copy SOP: 'copy_to_z']
    Target: grid_xy
    Template: Line (Z-axis, 50 points)
    Settings:
    - Number of Copies: 50
    - Translate Z: $CY (copy number)
    ↓
[Attribute Create SOP: 'voxel_coords']
    Add attributes:
    - voxelX = floor($TX + 15)
    - voxelY = floor($TY + 25)
    - voxelZ = floor($TZ + 15)
    - gridID = voxelX + voxelY * 30 + voxelZ * 1500
    ↓
[Null SOP: 'VOXEL_GRID']
```

**Usage:** This creates a 30×50×30 grid of points, each with voxel coordinates as attributes.

### Utility 2: Voxel Activation System

**Method A: Group-Based (for discrete on/off)**
```
[VOXEL_GRID]
    ↓
[Group SOP: 'active_voxels']
    Settings:
    - Group Name: active
    - Keep in Group: By Expression
    - Expression: (see per-illusion)
    ↓
[Delete SOP: 'delete_inactive']
    Settings:
    - Delete: Non-Selected Points
    - Group: active
```

**Method B: Attribute-Based (for brightness/intensity)**
```
[VOXEL_GRID]
    ↓
[Attribute Wrangle SOP: 'voxel_brightness']
    VEXpression:
    ```vex
    // Calculate brightness (0-1) per voxel
    f@brightness = 0.0; // default off

    // Illusion-specific logic here
    // Set @brightness based on position, time, etc.

    // Set color based on brightness
    @Cd = vector(@brightness); // grayscale
    ```
```

### Utility 3: Time & Animation Control

**Network:**
```
[Timer CHOP: 'timer']
    Settings:
    - Play: On
    - Speed: 1.0 (controllable)
    - Length: 10000
    ↓
[Math CHOP: 'time_scaled']
    - Multiply by speed parameter
    ↓
[Null CHOP: 'TIME']
```

**Usage in SOPs:**
- Reference as: `chop('TIME')[0]`
- Or via Python: `op('TIME')[0]`

### Utility 4: Rotation Matrices (for 3D transformations)

**Network:**
```
[Transform SOP: 'rotate_xyz']
    Settings:
    - Rotate:
      X: chop('TIME')[0] * rotSpeedX
      Y: chop('TIME')[0] * rotSpeedY
      Z: chop('TIME')[0] * rotSpeedZ
    - Pivot: Grid center
```

---

## Illusion Implementations

### 1. Rotating Ames Room

**Concept:** A trapezoid-shaped room that appears to rotate, creating a depth illusion

**SOP Implementation:**

```
[Grid SOP: 'base_square']
    - Rows: 1
    - Columns: 1
    - Size: 20, 20
    ↓
[PolyExtrude SOP: 'walls']
    - Distance: 50 (height)
    ↓
[Attribute Wrangle SOP: 'trapezoid_deform']
    VEXpression:
    ```vex
    // Normalize Y position (0 at bottom, 1 at top)
    float yNorm = (@P.y + 25) / 50.0;

    // Scale factor decreases with height (trapezoid)
    float depthParam = ch('../depth'); // 0-1
    float trapezoidScale = 0.6 + 0.4 * depthParam;
    float scaleAtY = 1.0 - yNorm * (1.0 - trapezoidScale);

    // Apply scale to X and Z
    @P.x *= scaleAtY;
    @P.z *= scaleAtY;
    ```
    ↓
[Resample SOP: 'to_points']
    - Convert to: Points
    - Max Segment Length: 1
    ↓
[Delete SOP: 'keep_edges']
    - Delete: Primitive except edges
    ↓
[Transform SOP: 'rotate']
    Settings:
    - Rotate Y: chop('TIME')[0] * ch('animationSpeed') * 0.3
    - Pivot: 0, 0, 0 (center)
    ↓
[Point SOP or Copy SOP: 'spheres']
    - Copy small spheres to each point (LED representation)
```

**Key Technique:** The trapezoid deformation creates false perspective. As it rotates, the brain interprets varying scales as depth changes.

**Parameters:**
- `size`: Overall scale multiplier
- `depth`: Trapezoid intensity (0.0-1.0)
- `animationSpeed`: Rotation speed

---

### 2. Infinite Corridor

**Concept:** Nested rectangles scroll toward viewer, creating endless tunnel illusion

**SOP Implementation:**

```
[For-Each SOP: 'corridor_frames']
    Method: Fetch Feedback
    Number of Iterations: ch('numFrames')
    ↓
    Inside For-Each:

    [Attribute Wrangle SOP: 'frame_calc']
    VEXpression:
    ```vex
    // Get iteration number
    int frame = detail(1, 'iteration', 0);

    float time = chop('TIME')[0];
    float speed = ch('../animationSpeed');
    float spacing = ch('../spacing');
    float frameSpacing = max(3, floor(4 * spacing));

    // Calculate Z position with scrolling
    float scrollOffset = (time * speed * 3) % frameSpacing;
    float baseZ = 30 - (frame * frameSpacing) + scrollOffset;

    // Wrap Z
    float wrappedZ = (baseZ % 30 + 30) % 30;

    // Scale based on normalized position
    float normalizedPos = (baseZ / 30.0 + 1.0) % 1.0;
    float scale = 0.2 + normalizedPos * 0.8 * ch('../size');

    // Store for next node
    f@frameZ = wrappedZ - 15; // centered
    f@frameScale = scale;
    ```
    ↓
    [Box SOP: 'rectangle']
        - Size: 30, 50, 1
        - Center: 0, 0, 0
        ↓
    [Facet SOP: 'to_outline']
        - Unique Points: On
        - Remove Inline Points: On
        (Creates wireframe)
        ↓
    [Transform SOP: 'scale_and_position']
        - Scale: point(0, 'frameScale', 0)
        - Translate Z: point(0, 'frameZ', 0)
        ↓
    [Resample SOP: 'to_points']
        - Max Segment Length: 1
    ↓
[Merge SOP: 'combine_all_frames']
    - Merge all iterations
    ↓
[Copy SOP: 'spheres']
    - Copy LED spheres to points
```

**Alternative POP Implementation:**

```
[POP Network: 'corridor_particles']
    ↓
    [POP Source: 'spawn']
        - Birth Rate: 100
        - Life Expectancy: 5
        - Const Birth Rate: On
        ↓
    [POP Wrangle: 'corridor_motion']
    VEXpression:
    ```vex
    // Initialize on birth
    if (f@age < 0.01) {
        // Random position in rectangle at far plane
        float scale = fit01(rand(@ptnum * 0.1), 0.2, 1.0);
        @P.x = fit01(rand(@ptnum * 0.2), -15 * scale, 15 * scale);
        @P.y = fit01(rand(@ptnum * 0.3), -25 * scale, 25 * scale);
        @P.z = -15; // far plane

        f@birthScale = scale;
    }

    // Move toward viewer
    float speed = ch('../animationSpeed') * 3;
    @P.z += @TimeInc * speed;

    // Scale grows as approaching
    float normalizedZ = (@P.z + 15) / 30.0;
    float currentScale = 0.2 + normalizedZ * 0.8;
    @pscale = currentScale * 0.5;

    // Wrap to far plane when reaching front
    if (@P.z > 15) {
        @P.z = -15;
        // Respawn with new random position
        float scale = fit01(rand(@ptnum * @Frame), 0.2, 1.0);
        @P.x = fit01(rand(@ptnum * @Frame + 0.1), -15 * scale, 15 * scale);
        @P.y = fit01(rand(@ptnum * @Frame + 0.2), -25 * scale, 25 * scale);
    }
    ```
```

**Key Technique:** Continuous scrolling with size scaling creates motion parallax. The brain perceives forward motion even in a static volume.

---

### 3. Kinetic Depth Effect

**Concept:** 2D sinusoidal waves rotated in 3D reveal apparent depth structure

**SOP Implementation:**

```
[Attribute Wrangle SOP: 'wave_curves']
    Run Over: Points
    VEXpression:
    ```vex
    // Parameters
    int numWaves = 8;
    float size = ch('size');
    float speed = ch('animationSpeed');
    float time = chop('TIME')[0];
    float angle = time * speed * 0.5;
    float radius = 12 * size;

    // Determine which wave this point belongs to
    int waveID = @ptnum / 100; // 100 points per wave
    int localPt = @ptnum % 100;

    float wavePhase = (float(waveID) / numWaves) * PI * 2;
    float t = float(localPt) / 99.0;
    float theta = t * PI * 2;

    // Create 2D sinusoidal wave
    float sinValue = sin(theta * 3 + wavePhase);
    float x2d = cos(theta) * radius;
    float y2d = sinValue * 5;

    // Rotate in 3D
    float x3d = x2d * cos(angle);
    float z3d = x2d * sin(angle);

    // Set position
    @P = set(x3d, y2d, z3d);

    @Cd = vector(1); // white
    ```
    ↓
[Add SOP: 'create_polyline']
    - Polygons: By Group
    - Close Polygons: On
    ↓
[Resample SOP: 'densify']
    - Max Segment Length: 0.5
    ↓
[Copy SOP: 'spheres']
```

**Alternative POP Implementation (more organic):**

```
[POP Network: 'kinetic_depth']
    ↓
    [POP Source: 'emit']
        - Emission Type: Geometry
        - Source: Circle (radius 12 * size)
        - Birth Rate: 50 per wave
        ↓
    [POP Wrangle: 'wave_motion']
    VEXpression:
    ```vex
    float time = chop('TIME')[0];
    float speed = ch('../animationSpeed');
    float angle = time * speed * 0.5;

    // Wave ID stored as attribute
    int waveID = i@waveID;
    float wavePhase = (float(waveID) / 8.0) * PI * 2;

    // Calculate angle around circle
    float theta = atan2(@P.z, @P.x);
    float radius = length(set(@P.x, 0, @P.z));

    // Sinusoidal height
    float sinValue = sin(theta * 3 + wavePhase);
    @P.y = sinValue * 5;

    // Rotate entire structure
    float x2d = radius * cos(theta);
    @P.x = x2d * cos(angle);
    @P.z = x2d * sin(angle);

    @pscale = 0.3;
    ```
```

**Key Technique:** Rotation disambiguates 2D → 3D structure. The kinetic depth effect makes flat patterns appear volumetric through motion.

---

### 4. Waterfall Illusion (Motion Aftereffect)

**Concept:** Continuous downward motion creates adaptation, making static objects appear to move upward

**SOP Implementation (Stripes):**

```
[Grid SOP: 'base_grid']
    - Rows: 30
    - Columns: 30
    - Orientation: XZ (horizontal plane)
    ↓
[Attribute Wrangle SOP: 'moving_stripes']
    VEXpression:
    ```vex
    float time = chop('TIME')[0];
    float speed = ch('animationSpeed');
    float density = ch('density');
    float offset = time * speed * 10;

    // Calculate stripe spacing
    float stripeSpacing = max(2, floor(5 - density * 3));

    // Create moving stripe pattern in Z
    float pattern = (@P.z + 15 + offset) % (stripeSpacing * 2);
    float isStripe = (pattern < stripeSpacing) ? 1.0 : 0.0;

    f@brightness = isStripe;
    @Cd = vector(isStripe);
    ```
    ↓
[Copy SOP: 'extrude_to_y']
    Template: Line (Y-axis, 50 points)
    - Copy to Points: grid points where brightness > 0
    ↓
[Point SOP: 'add_horizontal_markers']
    (Add horizontal reference lines every 5 units in Y)
```

**POP Implementation (More Dynamic):**

```
[POP Network: 'waterfall']
    ↓
    [POP Source: 'rain']
        - Birth Rate: 500
        - Scatter on: Grid (XZ plane at top)
        - Life Expectancy: 5
        ↓
    [POP Force: 'gravity']
        - Force: 0, -10, 0
        ↓
    [POP Wrangle: 'stripe_pattern']
    VEXpression:
    ```vex
    float density = ch('../density');
    float stripeSpacing = max(2, floor(5 - density * 3));

    // Stripe pattern based on Z position
    float pattern = (@P.z + 15) % (stripeSpacing * 2);
    float isStripe = (pattern < stripeSpacing) ? 1.0 : 0.3;

    @Cd = vector(isStripe);
    @pscale = 0.3 * isStripe;
    ```
    ↓
    [POP Kill: 'reset_at_bottom']
        - Kill if: @P.y < -25
        (Respawns at top due to Birth Rate)
    ↓
[POP Output: 'to_geometry']
```

**Key Technique:** Sustained downward motion adapts direction-selective neurons. When motion stops, aftereffect creates perceived upward motion.

---

### 5. Necker Cube

**Concept:** Wireframe cube with ambiguous depth - can be perceived from two perspectives

**SOP Implementation:**

```
[Box SOP: 'cube']
    - Size: ch('size') * 10
    - Center: 0, 0, 0
    ↓
[Facet SOP: 'wireframe']
    - Make Unique Points: On
    - Remove Inline Points: On
    ↓
[Resample SOP: 'edge_points']
    - Treat Polygons As: Subdivision Curves
    - Max Segment Length: 0.5
    ↓
[Point SOP: 'thicken_edges']
    (Or use Copy SOP to place small spheres)
    ↓
[Attribute Wrangle SOP: 'adjust_thickness']
    VEXpression:
    ```vex
    float thickness = ch('thickness');
    @pscale = thickness * 0.5;
    @Cd = vector(1); // white for ambiguity
    ```
```

**Advanced: Ambiguous Shading**

```
[Above network]
    ↓
[Attribute Wrangle SOP: 'remove_depth_cues']
    VEXpression:
    ```vex
    // Equal brightness everywhere - removes depth cues
    @Cd = vector(1);

    // Optional: Add slight occlusion ambiguity
    // Make some vertices slightly brighter
    float noise = rand(@ptnum);
    if (noise > 0.7) {
        @Cd *= 1.2;
    }
    ```
```

**Key Technique:** Removing depth cues (no perspective scaling, uniform color) allows brain to flip between interpretations.

---

### 6. Café Wall Illusion

**Concept:** Offset checkerboard with horizontal lines creates perception of non-parallel lines

**SOP Implementation:**

```
[Grid SOP: 'base']
    - Rows: 50
    - Columns: 30
    - Orientation: XY
    ↓
[Attribute Wrangle SOP: 'checkerboard_pattern']
    VEXpression:
    ```vex
    float size = ch('size');
    float spacing = ch('spacing');

    // Tile size
    int tileSize = max(2, int(floor(3 * size)));

    // Determine tile coordinates
    int tileX = int(floor((@P.x + 15) / tileSize));
    int tileY = int(floor((@P.y + 25) / tileSize));

    // Offset every other row
    int offset = (tileY % 2 == 0) ? 0 : int(tileSize * 0.5);
    int adjustedTileX = tileX + int(floor(float(offset) / tileSize));

    // Checkerboard color
    int tileColor = (adjustedTileX % 2 == 0) ? 1 : 0;

    @Cd = vector(tileColor);
    f@brightness = tileColor;
    ```
    ↓
[Copy SOP: 'extrude_to_z']
    Template: Line (Z-axis, 30 points)
    ↓
[Attribute Wrangle SOP: 'add_mortar_lines']
    VEXpression:
    ```vex
    // Add gray horizontal lines between rows
    int tileSize = max(2, int(floor(3 * ch('size'))));
    float yMod = (@P.y + 25) % tileSize;

    if (yMod < 0.5) {
        @Cd = vector(0.5); // gray mortar line
        f@brightness = 0.5;
    }
    ```
```

**Key Technique:** The offset creates local contrast gradients at mortar lines, causing illusory wedge perception. Lines appear slanted when they're parallel.

---

### 7. Pulfrich Effect

**Concept:** Objects moving at constant speed in 2D appear to move in 3D with brightness variation

**POP Implementation:**

```
[POP Network: 'pulfrich']
    ↓
    [POP Source: 'objects']
        - Birth Rate: 8 (total objects)
        - Const Birth Rate: Off
        - Impulse Activation: Frame 1
        ↓
    [POP Wrangle: 'circular_orbit']
    VEXpression:
    ```vex
    float time = chop('TIME')[0];
    float speed = ch('../animationSpeed');
    float size = ch('../size');
    float radius = 12 * size;

    // Each particle has fixed offset
    if (f@age < 0.01) {
        // Assign angular offset on birth
        f@angularOffset = float(@ptnum) / 8.0 * PI * 2;
    }

    // Circular motion
    float angle = time * speed + f@angularOffset;
    @P.x = cos(angle) * radius;
    @P.z = sin(angle) * radius;
    @P.y = 0; // constant height

    // Brightness varies with angle (key for Pulfrich)
    float brightness = 0.5 + 0.5 * sin(angle);
    @Cd = vector(brightness);
    f@brightness = brightness;

    @pscale = 2;
    ```
```

**SOP Alternative (Instanced Spheres):**

```
[Circle SOP: 'orbit_path']
    - Radius: 12 * ch('size')
    - Divisions: 8
    - Arc Type: Closed Arc
    ↓
[Attribute Wrangle SOP: 'position_objects']
    VEXpression:
    ```vex
    float time = chop('TIME')[0];
    float speed = ch('animationSpeed');
    float radius = 12 * ch('size');

    float angle = time * speed + float(@ptnum) / 8.0 * PI * 2;
    @P.x = cos(angle) * radius;
    @P.z = sin(angle) * radius;
    @P.y = 0;

    // Brightness modulation
    float brightness = 0.5 + 0.5 * sin(angle);
    @Cd = vector(brightness);

    @pscale = 2;
    ```
    ↓
[Copy SOP: 'spheres']
    Target: Sphere
```

**Key Technique:** Brightness variation simulates temporal delay (as if one eye sees dimmer/delayed image). Creates depth perception from 2D motion.

---

### 8. Moiré Pattern

**Concept:** Two overlapping grids create interference patterns that appear to move

**SOP Implementation:**

```
// Grid 1: Static vertical lines
[Grid SOP: 'grid1']
    - Rows: 1
    - Columns: 30
    - Size: 30, 50
    - Orientation: XY
    ↓
[Copy SOP: 'extrude_grid1']
    Template: Line (Z-axis, 30 points)
    Settings:
    - Copy to: grid1 columns
    ↓
[Attribute Wrangle SOP: 'grid1_color']
    VEXpression:
    ```vex
    float spacing = ch('../spacing');
    int gridSpacing = max(2, int(floor(3 * spacing)));

    // Only activate every Nth column
    int xIndex = int(floor(@P.x + 15));
    if (xIndex % gridSpacing == 0) {
        @Cd = vector(0.5);
        f@brightness = 0.5;
    } else {
        @Cd = vector(0);
        f@brightness = 0;
    }
    ```
    ↓
[Null SOP: 'GRID1_OUT']

// Grid 2: Rotating vertical lines
[Grid SOP: 'grid2']
    - Rows: 1
    - Columns: 30
    - Size: 30, 50
    - Orientation: XY
    ↓
[Copy SOP: 'extrude_grid2']
    Template: Line (Z-axis, 30 points)
    ↓
[Transform SOP: 'rotate_grid2']
    Settings:
    - Rotate Y: chop('TIME')[0] * ch('animationSpeed') * 0.1
    - Pivot: 0, 0, 0 (center)
    ↓
[Attribute Wrangle SOP: 'grid2_color']
    VEXpression:
    ```vex
    float spacing = ch('../spacing');
    int gridSpacing = max(2, int(floor(3 * spacing)));

    // Project rotated position to find active columns
    int xIndex = int(floor(@P.x + 15));
    if (xIndex % gridSpacing == 0) {
        @Cd = vector(0.5);
        f@brightness = 0.5;
    } else {
        @Cd = vector(0);
        f@brightness = 0;
    }
    ```
    ↓
[Null SOP: 'GRID2_OUT']

// Merge grids
[Merge SOP: 'combine']
    Input 1: GRID1_OUT
    Input 2: GRID2_OUT
    ↓
[Attribute Wrangle SOP: 'combine_brightness']
    VEXpression:
    ```vex
    // Additive blending creates moiré interference
    // (handled automatically by overlapping geometry)

    // Optional: boost intersection brightness
    if (@Cd.r > 0.8) {
        @Cd = vector(1);
    }
    ```
```

**Key Technique:** Interference between two slightly offset patterns creates emergent low-frequency patterns. Rotation makes moiré bands appear to move faster than grids.

---

## Optimization & Performance

### SOP Optimization Techniques

**1. Point Count Management**
```
// Instead of dense grid, use sparse activation
[Scatter SOP: 'sparse_points']
    - Scatter on: Volume
    - Number of Points: controllable
    - Better than full 45,000 point grid
```

**2. Instancing for LED Rendering**
```
[VOXEL_GRID or effect output]
    ↓
[Instance SOP: 'led_instances']
    Target: Sphere (low poly: 2-3 divisions)
    Settings:
    - Instance: On Point
    - Attributes: pscale, Cd, N
    ↓
[Material SOP]
```

**3. LOD (Level of Detail)**
```
[Switch SOP: 'lod_selector']
    Input 0: High-res geometry (preview)
    Input 1: Low-res geometry (realtime)
    Index: based on performance metric or user toggle
```

**4. Cook Optimization**
```
[Time Blend SOP: 'smooth_animation']
    - Reduce cook frequency for expensive operations
    - Blend between cached frames
```

### POP Optimization Techniques

**1. Birth Rate Control**
```
[POP Source]
    - Const Birth Rate: Off (for fixed count)
    - Life Expectancy: Set to reasonable value
    - Max Particles: Limit total count
```

**2. Solver Optimization**
```
[POP Solver]
    Settings:
    - Sub Steps: Reduce if not critical
    - Cache Simulation: On (for playback)
```

**3. Conditional Forces**
```
[POP Wrangle: 'optimized_forces']
    VEXpression:
    ```vex
    // Only calculate expensive operations when needed
    if (@age > 0.1 && @age < @life - 0.1) {
        // Apply forces/calculations
    }
    ```
```

**4. GPU Acceleration**
```
[POP Solver]
    - Use OpenCL: On (if available)
    - Accelerates force calculations
```

### General Performance Tips

**1. Resolution Balancing**
- Start with lower grid resolution (15×25×15)
- Increase only if visual quality requires it
- Use expression to link resolution: `ch('master_resolution')`

**2. Geometry Types**
- **Points**: Fastest (1 vertex per voxel)
- **Spheres (Low Poly)**: Good balance (12-20 vertices)
- **Spheres (High Poly)**: Beautiful but slow (100+ vertices)

**3. Render Optimization**
- Use Geometry COMP with LOD
- Enable instancing in material
- Use sprite rendering for distant points

**4. Network Organization**
```
/project
    /utilities
        voxel_grid (base grid generator)
        time_control
        color_effects (TOP-based, from previous doc)
    /illusions
        rotating_ames (COMP)
        infinite_corridor (COMP)
        kinetic_depth (COMP)
        ...
    /output
        instance_renderer
        composite_final
```

---

## Integration with Color Effects

### Method 1: Attribute-Based Color (SOP → TOP → SOP)

**Workflow:**
```
[SOP: Voxel positions with UVs]
    ↓
[TOP: Color effects from previous guide]
    ↓
[Attribute from Map SOP]
    - Apply color from TOP to SOP points
    - Lookup using UV coordinates
```

**Example:**
```
[Illusion SOP output]
    ↓
[Attribute Create SOP: 'add_uvs']
    VEXpression:
    ```vex
    // Create UV coordinates from voxel position
    @uv.x = (@P.x + 15) / 30.0;
    @uv.y = (@P.y + 25) / 50.0;
    // Could use Z for 3D texture lookup
    ```
    ↓
[Attribute from Map SOP: 'apply_color']
    Settings:
    - Texture: op('/effects/OUTPUT') from TOP network
    - Class: Point
    - Attribute: Cd (color)
    - UV Attribute: uv
```

### Method 2: CHOP-Based Color (Direct Lookup)

**Workflow:**
```
[SOP: Voxel grid]
    ↓
[SOP to CHOP: 'positions']
    - Export: P (position)
    ↓
[CHOP: Color effect calculations]
    - Process position data
    - Generate RGB channels
    ↓
[CHOP to SOP: 'color_attributes']
    - Import Cd attribute
```

### Method 3: Hybrid (TOP Effects + SOP Selection)

**Workflow:**
```
[TOP Network: Rainbow/Plasma/Fire effects]
    ↓
[CHOP Sampling]
    ↓
[SOP: Illusion geometry]
    ↓
[Attribute Wrangle SOP: 'apply_effect_color']
    VEXpression:
    ```vex
    // Sample color from TOP effect
    vector uvw = set(
        (@P.x + 15) / 30.0,
        (@P.y + 25) / 50.0,
        (@P.z + 15) / 30.0
    );

    vector effectColor = colormap(
        'op:/effects/rainbow_out',
        uvw.x,
        uvw.y
    );

    // Apply to active points only
    if (f@brightness > 0) {
        @Cd = effectColor * f@brightness;
    } else {
        @Cd = vector(0);
    }
    ```
```

### Complete Example: Kinetic Depth + Rainbow Sweep

**Network:**
```
// Illusion geometry
[Kinetic Depth SOP network from above]
    ↓
[Attribute Create SOP: 'uvs']
    VEXpression:
    ```vex
    @uv.x = (@P.x + 15) / 30.0;
    @uv.y = (@P.y + 25) / 50.0;
    ```
    ↓
[Null SOP: 'GEOMETRY']

// Color effect (TOP network)
[Rainbow Sweep effect from TOUCHDESIGNER_COLOR_EFFECTS_TOPS.md]
    ↓
[Null TOP: 'COLOR_EFFECT']

// Combine
[Attribute from Map SOP: 'final_color']
    Geometry: GEOMETRY
    Texture: COLOR_EFFECT
    ↓
[Instance SOP or Copy SOP: 'spheres']
    ↓
[Material MAT: 'led_material']
    - Color Map: point Cd attribute
    - Emit: On (self-illuminated LEDs)
    - Emit Intensity: 2.0
    ↓
[Geometry COMP: 'render']
```

---

## Advanced Techniques

### Technique 1: Hybrid SOP + POP

**Use Case:** Infinite Corridor with particle dust

```
// Structured corridor (SOP)
[Infinite Corridor SOP network]
    ↓
[Null SOP: 'CORRIDOR_GEO']

// Particle ambiance (POP)
[POP Network: 'dust']
    [POP Source]
        - Scatter in: Bounding box of corridor
        - Birth Rate: 50
    [POP Advect by Volume]
        - Velocity field pointing toward viewer
    [POP Wrangle: 'fade_with_distance']
    ↓
[Null SOP: 'DUST_GEO']

// Combine
[Merge SOP: 'final']
    Input 1: CORRIDOR_GEO
    Input 2: DUST_GEO
```

### Technique 2: Feedback Loops (Temporal Effects)

**Use Case:** Waterfall with persistent trails

```
[POP Network with Feedback SOP]
    ↓
[Trail SOP: 'motion_trail']
    - Result Type: Compute Velocity
    - Trail Length: 10 frames
    ↓
[Add SOP: 'connect_trails']
    - Connect particles over time
```

### Technique 3: Volume-Based Activation

**Use Case:** Soft, organic voxel activation

```
[Volume SOP: 'activation_field']
    (Build custom SDF or noise volume)
    ↓
[Scatter SOP: 'voxel_points']
    - Scatter on: Volume
    - Density attribute: based on illusion logic
    ↓
[Point Cloud operations]
```

---

## Comparison Table: SOP vs POP

| Aspect | SOP Approach | POP Approach |
|--------|-------------|--------------|
| **Best For** | Geometric illusions, structured patterns | Organic motion, flow effects |
| **Performance** | Generally faster for static/simple transforms | Can be slower with many forces |
| **Control** | Precise, deterministic | Dynamic, emergent behavior |
| **Animation** | Transform nodes, expressions | Forces, fields, attractors |
| **Memory** | Lower (just geometry) | Higher (solver state) |
| **Examples** | Necker Cube, Café Wall, Ames Room | Waterfall, Pulfrich (moving objects) |

---

## Troubleshooting

### Issue: Voxel grid points not aligning
**Solution:**
```vex
// In Attribute Wrangle, ensure consistent centering
@P.x = floor(@P.x) + 0.5; // Snap to voxel centers
@P.y = floor(@P.y) + 0.5;
@P.z = floor(@P.z) + 0.5;
```

### Issue: Animation stuttering
**Solution:**
- Check Time CHOP is playing
- Reduce geometry complexity
- Enable caching in SOP/POP solver
- Use Time Blend SOP for smoothing

### Issue: Color effects not matching geometry
**Solution:**
- Verify UV coordinates are in 0-1 range
- Check TOP resolution matches SOP detail needs
- Use `colormap()` VEX function instead of Attribute from Map for debugging

### Issue: POP particles clumping
**Solution:**
```
[POP Interact]
    - Add inter-particle force
    - Radius: 0.5-1.0
    - Force: repel
```

---

## Complete Workflow Example: Rotating Ames Room

**Step 1: Create base utilities**
```
/project/utilities/time_control (Timer CHOP setup)
/project/utilities/voxel_params (Control parameters)
```

**Step 2: Build SOP network**
```
/project/illusions/rotating_ames (Container COMP)
    Inside:
    [Grid SOP → PolyExtrude → Wrangle (trapezoid) → Resample → Delete (edges) → Transform (rotate) → Attribute (UVs) → Null: 'GEO_OUT']
```

**Step 3: Add color effects**
```
/project/color_effects/plasma (TOP network from previous guide)
    → [Null TOP: 'COLOR_OUT']
```

**Step 4: Combine**
```
[Attribute from Map SOP]
    Geometry: /project/illusions/rotating_ames/GEO_OUT
    Texture: /project/color_effects/plasma/COLOR_OUT
    ↓
[Copy SOP]
    Target: Sphere (2 divisions)
    ↓
[Material MAT]
    Color Map: Cd
    Emit: On
```

**Step 5: Render**
```
[Geometry COMP]
    Render: /project/illusions/rotating_ames/final
    ↓
[Render TOP or Direct 3D output]
```

---

## Next Steps

1. **Start with simplest illusion**: Necker Cube (static geometry)
2. **Add animation**: Rotating Ames Room (transform-based)
3. **Try particles**: Waterfall Illusion (POP network)
4. **Integrate colors**: Combine with TOP effects from previous guide
5. **Optimize**: Profile performance, reduce point counts
6. **Build library**: Create reusable illusion COMPs with parameters

**Recommended Build Order:**
1. Necker Cube (SOP basics)
2. Café Wall (attribute-based patterns)
3. Rotating Ames Room (time-based animation)
4. Infinite Corridor (For-Each loops, feedback)
5. Waterfall Illusion (POP introduction)
6. Kinetic Depth (SOP + rotation + color integration)
7. Moiré Pattern (multi-layer compositing)
8. Pulfrich Effect (POP + brightness modulation)

This SOP/POP approach provides native TouchDesigner workflows for recreating volumetric display illusions, offering more direct control over geometry and particles than hybrid systems!
