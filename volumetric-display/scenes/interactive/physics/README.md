# Physics Engine for Volumetric Display

A complete physics simulation system for creating dynamic, particle-based scenes on your volumetric display.

## Overview

The physics engine provides realistic particle dynamics with:
- **Verlet integration** for stable, energy-conserving simulation
- **Modular force system** (gravity, drag, wind, gravity wells, springs, vortex)
- **Collision detection** (boundaries, particle-particle with spatial hashing)
- **Particle emitters** (point, cone, volume)
- **Motion blur rendering** for velocity-based particle trails

## Architecture

```
physics/
├── engine.py          # Core PhysicsEngine + PhysicsState
├── forces.py          # Force functions (gravity, drag, wind, etc.)
├── constraints.py     # Collision & boundary handling
├── emitters.py        # Particle emission systems
├── rendering.py       # Particle → voxel conversion
└── test_physics.py    # Test suite
```

## Quick Start

### Running Physics Scenes

```bash
# Start the interactive scene server
python sender.py --scene scenes/interactive_scene.py --web-server --web-port 5001

# Open web UI
open http://localhost:5001/scenes/interactive/web/
```

Then select one of the physics scenes from the dropdown:
- **Physics Fountain** - Particle fountain with gravity and bouncing
- **Physics Bouncing** - Elastic bouncing balls
- **Physics Orbital** - Gravitational orbital mechanics
- **Physics Rain** - Rain/snow with wind

### Creating Custom Physics Scenes

```python
from scenes.interactive.scenes.base import BaseScene
from scenes.interactive.physics import (
    PhysicsEngine, create_particle_pool,
    gravity, drag, boundary_collision,
    ParticleEmitter, particles_to_voxels
)

class MyPhysicsScene(BaseScene):
    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)

        # Create physics engine
        self.engine = PhysicsEngine(
            bounds_min=[0, 0, 0],
            bounds_max=grid_shape,
            dt=0.016,
            boundary_mode='bounce'  # or 'wrap'
        )

        # Add forces
        self.engine.add_force(gravity(g=-9.8, axis=0))
        self.engine.add_force(drag(coefficient=0.1))

        # Add constraints
        self.engine.add_constraint(boundary_collision(
            bounds_min=[0, 0, 0],
            bounds_max=grid_shape,
            restitution=0.8
        ))

        # Create particle pool
        self.state = create_particle_pool(max_particles=100, grid_shape=grid_shape)

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        # Step physics simulation
        self.state = self.engine.step(self.state, time)

        # Render particles to voxels
        mask = particles_to_voxels(
            self.state,
            self.grid_shape,
            render_mode='sphere',
            motion_blur=True
        )

        return mask
```

## Core Components

### 1. PhysicsEngine

The main simulation engine using Verlet integration.

```python
engine = PhysicsEngine(
    bounds_min=[0, 0, 0],
    bounds_max=[16, 16, 16],
    dt=0.016,                # Time step (60fps)
    boundary_mode='bounce'   # 'bounce' or 'wrap'
)

# Add forces
engine.add_force(gravity(g=-9.8, axis=0))
engine.add_force(drag(coefficient=0.1))

# Add constraints
engine.add_constraint(boundary_collision(...))

# Step simulation
state = engine.step(state, t=current_time)
```

### 2. PhysicsState

Container for particle data:

```python
state = PhysicsState(
    position=...,        # (N, 3) continuous coordinates
    velocity=...,        # (N, 3) velocity vectors
    acceleration=...,    # (N, 3) acceleration vectors
    mass=...,            # (N,) particle masses
    radius=...,          # (N,) collision/rendering radii
    active=...,          # (N,) bool - active particle mask
    age=...,             # (N,) particle age in seconds
    prev_position=...    # (N, 3) for motion blur
)
```

### 3. Force Functions

**Available Forces:**
- `gravity(g, axis)` - Uniform gravity in one axis
- `drag(coefficient)` - Air resistance (F = -k * v)
- `wind(direction, strength, turbulence)` - Directional wind with gusts
- `gravity_well(center, strength)` - Point attractor (inverse square law)
- `spring(anchors, stiffness, damping)` - Hooke's law springs
- `vortex(center, axis, strength, radius)` - Tornado/vortex force

**Example:**
```python
# Downward gravity
engine.add_force(gravity(g=-9.8, axis=0))

# Light air resistance
engine.add_force(drag(coefficient=0.05))

# Central attractor
engine.add_force(gravity_well(
    center=[8, 8, 8],
    strength=50.0
))

# Wind with turbulence
engine.add_force(wind(
    direction=[1, 0, 0],
    strength=3.0,
    turbulence=0.3
))
```

### 4. Constraints

**Available Constraints:**
- `boundary_collision(bounds_min, bounds_max, restitution)` - Bounce off walls
- `boundary_wrap(bounds_min, bounds_max)` - Toroidal wrap-around
- `particle_particle_collision(enabled, restitution, spatial_hash)` - Ball collisions
- `sphere_collision(center, radius, restitution, inside)` - Sphere boundary

**Example:**
```python
# Bouncy walls
engine.add_constraint(boundary_collision(
    bounds_min=[0, 0, 0],
    bounds_max=[16, 16, 16],
    restitution=0.9  # Very bouncy
))

# Particle-particle collisions (with spatial hashing)
engine.add_constraint(particle_particle_collision(
    enabled=True,
    restitution=0.8,
    spatial_hash=True  # For >100 particles
))
```

### 5. Particle Emitters

**ParticleEmitter** (point/cone emission):
```python
emitter = ParticleEmitter(
    position=[8, 8, 0],
    rate=15.0,               # particles/sec
    velocity_min=5.0,
    velocity_max=8.0,
    direction=[0, 0, 1],     # Upward
    spread_angle=20.0,       # degrees
    particle_lifetime=10.0,
    particle_radius=1.5
)

# Emit particles each frame
emitter.emit(state, time, dt=0.016)
```

**VolumeEmitter** (spawn in region):
```python
emitter = VolumeEmitter(
    bounds_min=[0, 0, 15],
    bounds_max=[16, 16, 16],
    rate=25.0,
    velocity_mean=[0, 0, -3],  # Downward
    velocity_variance=0.5
)

emitter.emit(state, time, dt=0.016)
```

### 6. Rendering

Convert particles to voxel masks:

```python
mask = particles_to_voxels(
    state,
    grid_shape=(16, 16, 16),
    render_mode='sphere',    # 'point' or 'sphere'
    motion_blur=True         # Draw trails
)
```

**Render Modes:**
- `'point'` - Single voxel per particle (fastest)
- `'sphere'` - Small sphere using particle radius (more visible)

**Motion Blur:**
- Draws line from `prev_position` to `position`
- Creates comet-like trails for fast-moving particles
- Great for orbital scenes and rain

## Example Scenes

### 1. Fountain (physicsFountain)

Continuous upward emission with gravity and bouncing.

**Features:**
- Point emitter at bottom
- Cone spread emission
- Gravity + air resistance
- Bouncy boundary collision

**Parameters:**
- `emission_rate` - Particles/second (1-50)
- `velocity_min/max` - Launch speed (0-20)
- `velocity_spread` - Cone angle (0-90°)
- `gravity_strength` - Gravity (-20 to 20)
- `restitution` - Bounciness (0-1)

### 2. Bouncing Balls (physicsBouncing)

Elastic bouncing balls with optional particle-particle collisions.

**Features:**
- Random initial positions/velocities
- Variable ball sizes and masses
- Optional ball-to-ball collisions
- High restitution for bouncy physics

**Parameters:**
- `particle_count` - Number of balls (5-100)
- `enable_particle_collisions` - Ball-to-ball collisions (expensive)
- `restitution` - Bounciness (0.5-1.0)

**Note:** Particle collisions use spatial hashing for performance with >100 particles.

### 3. Orbital Mechanics (physicsOrbital)

Gravitational n-body simulation with stable orbits.

**Features:**
- Central gravity well(s)
- Particles in circular/elliptical orbits
- Wrap-around boundaries (infinite space)
- Multiple attractor modes (single, binary, ternary)

**Parameters:**
- `attractor_strength` - Gravitational pull (10-200)
- `num_attractors` - Number of gravity wells (1-4)
- `particle_count` - Orbiting particles (10-200)
- `air_resistance` - Orbit decay (0=stable)

**Modes:**
- 1 attractor: Single star system
- 2 attractors: Binary star system
- 3+ attractors: Multi-star system (chaotic orbits)

### 4. Rain/Snow (physicsRain)

Atmospheric precipitation with wind and turbulence.

**Features:**
- Volume emitter at top of display
- Downward gravity
- Wind with turbulent gusts
- Auto-respawn at top when hitting ground

**Parameters:**
- `emission_rate` - Rain density (5-50)
- `fall_speed` - Initial downward velocity (-1 to -10)
- `wind_speed` - Horizontal drift (0-10)
- `wind_direction_x/y` - Wind direction (-1 to 1)
- `turbulence` - Random gusts (0-1)

## Performance

**Particle Budget:**
- **Target:** 100-300 particles @ 60fps
- **Maximum:** 500 particles @ 30fps

**Optimization Tips:**
1. **Spatial Hashing** - Enable for >100 particles with collisions
2. **Vectorization** - All math is NumPy vectorized
3. **Particle Pooling** - Pre-allocate arrays, use `active` mask
4. **Reduce Motion Blur** - Disable for simple scenes
5. **Lower Particle Count** - Fewer particles = higher FPS

**Collision Performance:**
- Without spatial hash: O(N²) - suitable for <50 particles
- With spatial hash: O(N) average - suitable for >100 particles

## Coordinate System

The volumetric display uses this coordinate system:

```
Axis 0 (Z) = Length (depth/height in display)
Axis 1 (Y) = Height (Y in display)
Axis 2 (X) = Width (X in display)
```

**Gravity Examples:**
- `gravity(g=-9.8, axis=0)` - Downward (most natural)
- `gravity(g=-9.8, axis=1)` - Side gravity
- `gravity(g=-9.8, axis=2)` - Front-to-back gravity

## Testing

Run the test suite to verify installation:

```bash
python3 volumetric-display/scenes/interactive/physics/test_physics.py
```

Expected output:
```
Testing Force Functions...
✓ Gravity force works
✓ Drag force works
✓ Force functions test passed!

Testing Physics Engine...
✓ Physics engine test passed!

✅ All physics tests passed!
```

## Troubleshooting

**Particles disappear immediately:**
- Check that particles are being activated: `state.active[i] = True`
- Verify emitter is calling `emit()` each frame
- Check `particle_lifetime` isn't too short

**Particles fly out of bounds:**
- Add `boundary_collision` or `boundary_wrap` constraint
- Check bounds match grid_shape: `[0, 0, 0]` to `[L-1, H-1, W-1]`

**Low FPS / Slow simulation:**
- Reduce particle count
- Disable motion blur
- Disable particle-particle collisions
- Use spatial hashing for collisions

**Particles don't bounce:**
- Check `restitution` value (should be >0 for bouncing)
- Verify `boundary_collision` is added to constraints
- Ensure particles have non-zero velocity

**Unstable simulation (particles jitter):**
- Reduce timestep: `dt=0.008` (120fps)
- Lower force magnitudes
- Increase damping/air resistance
- Check for conflicting forces

## Advanced Topics

### Custom Force Functions

Create your own forces by following this signature:

```python
def my_force(param1, param2):
    """Custom force description."""
    def force_func(state: PhysicsState, t: float) -> np.ndarray:
        force = np.zeros_like(state.position, dtype=float)

        # Compute force based on state and time
        # Example: radial force
        center = np.array([8, 8, 8])
        r_vec = state.position - center
        r_mag = np.linalg.norm(r_vec, axis=1, keepdims=True)
        force = param1 * r_vec / r_mag

        # Only apply to active particles
        force[~state.active] = 0
        return force

    force_func.__name__ = 'my_force'
    return force_func
```

### Particle Lifecycle Management

```python
# Despawn old particles
from scenes.interactive.physics import despawn_old_particles
despawn_old_particles(state, max_lifetime=10.0)

# Despawn out of bounds particles
from scenes.interactive.physics import despawn_out_of_bounds
despawn_out_of_bounds(state, bounds_min, bounds_max)

# Manual deactivation
state.active[condition] = False

# Recycle oldest particles (for continuous emission)
inactive_indices = np.where(~state.active)[0]
if len(inactive_indices) == 0:
    # No free slots, recycle oldest
    inactive_indices = np.argsort(state.age)[-n_to_emit:]
```

### Per-Particle Colors

The physics state doesn't currently support per-particle colors, but you can extend it:

```python
# In your scene
self.particle_colors = np.zeros((max_particles, 3), dtype=np.uint8)

# In generate_geometry()
mask = particles_to_voxels(state, grid_shape)
# Apply colors manually
for i in active_indices:
    voxel_pos = np.round(state.position[i]).astype(int)
    if in_bounds(voxel_pos, grid_shape):
        raster.data[tuple(voxel_pos)] = self.particle_colors[i]
```

## Future Enhancements

Potential additions to the physics engine:

1. **Rigid Body Dynamics** - Rotating 3D shapes with torque
2. **Soft Body Physics** - Spring networks for cloth/jelly
3. **Fluid Simulation** - SPH (Smoothed Particle Hydrodynamics)
4. **Boids Flocking** - Steering behaviors for organic swarms
5. **GPU Acceleration** - CuPy/PyTorch for thousands of particles
6. **Force Fields** - Precomputed force grids for complex fields
7. **Mesh Colliders** - Collision with arbitrary 3D meshes

## References

- [Verlet Integration](https://en.wikipedia.org/wiki/Verlet_integration)
- [Position Based Dynamics](http://matthias-mueller-fischer.ch/publications/posBasedDyn.pdf)
- [Real-Time Collision Detection](https://www.amazon.com/Real-Time-Collision-Detection-Interactive-Technology/dp/1558607323) - Christer Ericson
- [Game Physics Engine Development](https://www.amazon.com/Game-Physics-Engine-Development-Commercial-Grade/dp/0123819768) - Ian Millington

## License

Same as parent project - see root LICENSE file.
