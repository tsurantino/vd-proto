"""
Physics Engine Module

Provides physics simulation capabilities for volumetric display scenes:
- PhysicsEngine: Core simulation engine with Verlet integration
- PhysicsState: Particle state container
- Force functions: gravity, drag, wind, gravity wells, springs
- Constraints: boundary collision/wrap, particle collisions
- Emitters: particle emission systems
- Rendering: particle to voxel conversion with motion blur
"""

from .engine import PhysicsEngine, PhysicsState, create_particle_pool
from .forces import gravity, drag, wind, gravity_well, spring, vortex
from .constraints import boundary_collision, boundary_wrap, particle_particle_collision, sphere_collision
from .emitters import ParticleEmitter, VolumeEmitter, despawn_old_particles, despawn_out_of_bounds
from .rendering import particles_to_voxels, draw_sphere, draw_line_3d, in_bounds

__all__ = [
    # Core engine
    'PhysicsEngine',
    'PhysicsState',
    'create_particle_pool',

    # Forces
    'gravity',
    'drag',
    'wind',
    'gravity_well',
    'spring',
    'vortex',

    # Constraints
    'boundary_collision',
    'boundary_wrap',
    'particle_particle_collision',
    'sphere_collision',

    # Emitters
    'ParticleEmitter',
    'VolumeEmitter',
    'despawn_old_particles',
    'despawn_out_of_bounds',

    # Rendering
    'particles_to_voxels',
    'draw_sphere',
    'draw_line_3d',
    'in_bounds',
]
