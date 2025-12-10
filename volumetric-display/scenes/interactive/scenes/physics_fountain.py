"""
Physics Fountain Scene

Continuous particle fountain with gravity, emission, and bouncing.
Demonstrates physics-based particle system with emitter.
"""

import numpy as np
from .base import BaseScene
from ..physics import (
    PhysicsEngine, create_particle_pool,
    gravity, drag,
    boundary_collision,
    ParticleEmitter,
    particles_to_voxels,
    despawn_old_particles
)


class PhysicsFountainScene(BaseScene):
    """
    Particle fountain scene with continuous emission.

    Features:
    - Point emitter at bottom center
    - Upward cone emission with spread
    - Gravity pulls particles down
    - Bouncing off boundaries
    - Air resistance for realistic arcs
    """

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)

        # Physics engine setup with bounce boundaries
        bounds_min = np.array([0, 0, 0], dtype=float)
        bounds_max = np.array(grid_shape, dtype=float) - 1
        self.engine = PhysicsEngine(
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            dt=0.016,
            boundary_mode='bounce'
        )

        # Create particle pool
        self.state = create_particle_pool(max_particles=300, grid_shape=grid_shape)

        # Emitter at bottom center
        emitter_pos = [grid_shape[0]/2, grid_shape[1]/2, 0]
        self.emitter = ParticleEmitter(
            position=emitter_pos,
            rate=10.0,
            velocity_min=5.0,
            velocity_max=8.0,
            direction=[0, 0, 1],  # Upward
            spread_angle=15.0,
            particle_lifetime=10.0,
            particle_radius=1.5
        )

        # Setup forces (will be updated from params)
        self._setup_forces(gravity_strength=-9.8, air_resistance=0.05)

        # Setup constraints
        self._setup_constraints(bounds_min, bounds_max, restitution=0.8)

    def _setup_forces(self, gravity_strength=-9.8, air_resistance=0.05):
        """Setup force functions with given parameters."""
        self.engine.clear_forces()
        self.engine.add_force(gravity(g=gravity_strength, axis=0))  # Z-axis gravity
        self.engine.add_force(drag(coefficient=air_resistance))

    def _setup_constraints(self, bounds_min, bounds_max, restitution=0.8):
        """Setup constraint functions with given parameters."""
        self.engine.clear_constraints()
        self.engine.add_constraint(boundary_collision(
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            restitution=restitution
        ))

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate fountain by stepping physics simulation."""
        # Update emitter parameters from UI
        self.emitter.rate = params.scene_params.get('emission_rate', 10.0)
        self.emitter.velocity_min = params.scene_params.get('velocity_min', 5.0)
        self.emitter.velocity_max = params.scene_params.get('velocity_max', 8.0)
        self.emitter.spread_angle = np.deg2rad(params.scene_params.get('velocity_spread', 15.0))
        self.emitter.particle_lifetime = params.scene_params.get('particle_lifetime', 10.0)
        self.emitter.particle_radius = params.scene_params.get('particle_radius', 1.5)

        # Update emitter position
        emitter_x = params.scene_params.get('emitter_x', self.grid_shape[0]/2)
        emitter_y = params.scene_params.get('emitter_y', self.grid_shape[1]/2)
        emitter_z = params.scene_params.get('emitter_z', 0.0)
        self.emitter.position = np.array([emitter_x, emitter_y, emitter_z])

        # Update forces if parameters changed
        gravity_strength = params.scene_params.get('gravity_strength', -9.8)
        air_resistance = params.scene_params.get('air_resistance', 0.05)
        self._setup_forces(gravity_strength, air_resistance)

        # Update constraints if restitution changed
        restitution = params.scene_params.get('restitution', 0.8)
        bounds_min = np.array([0, 0, 0], dtype=float)
        bounds_max = np.array(self.grid_shape, dtype=float) - 1
        self._setup_constraints(bounds_min, bounds_max, restitution)

        # Emit new particles
        self.emitter.emit(self.state, time, dt=0.016)

        # Despawn old particles
        despawn_old_particles(self.state, max_lifetime=self.emitter.particle_lifetime)

        # Step physics simulation
        self.state = self.engine.step(self.state, time)

        # Render particles to voxels
        render_mode = params.scene_params.get('render_mode', 'sphere')
        motion_blur = params.scene_params.get('motion_blur', False)

        mask = particles_to_voxels(
            self.state,
            self.grid_shape,
            render_mode=render_mode,
            motion_blur=motion_blur
        )

        return mask, None  # No copy indices for physics

    @classmethod
    def get_enabled_parameters(cls):
        return [
            # Emitter
            'emission_rate', 'velocity_min', 'velocity_max', 'velocity_spread',
            'emitter_x', 'emitter_y', 'emitter_z',
            # Particle
            'particle_lifetime', 'particle_radius',
            # Physics
            'gravity_strength', 'air_resistance', 'restitution',
            # Rendering
            'render_mode', 'motion_blur'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return []  # No standard tabs (rotation, copy, etc.)

    @classmethod
    def get_defaults(cls):
        return {
            # Emitter defaults
            'emission_rate': 10.0,
            'velocity_min': 5.0,
            'velocity_max': 8.0,
            'velocity_spread': 15.0,  # degrees
            'emitter_x': 8.0,
            'emitter_y': 8.0,
            'emitter_z': 0.0,

            # Particle defaults
            'particle_lifetime': 10.0,
            'particle_radius': 1.5,

            # Physics defaults
            'gravity_strength': -9.8,
            'air_resistance': 0.05,
            'restitution': 0.8,

            # Rendering defaults
            'render_mode': 'sphere',
            'motion_blur': False,
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'emission_rate': 'Particles emitted per second (1-50)',
            'velocity_min': 'Minimum launch velocity (0-20)',
            'velocity_max': 'Maximum launch velocity (0-20)',
            'velocity_spread': 'Emission cone angle in degrees (0-90)',
            'emitter_x': 'Emitter X position',
            'emitter_y': 'Emitter Y position',
            'emitter_z': 'Emitter Z position (height)',
            'particle_lifetime': 'Max particle age before despawn (seconds)',
            'particle_radius': 'Particle size in voxels (0.5-3.0)',
            'gravity_strength': 'Gravity acceleration (-20 to 20)',
            'air_resistance': 'Air drag coefficient (0-1)',
            'restitution': 'Bounce elasticity (0=no bounce, 1=perfect bounce)',
            'render_mode': 'Rendering style (point or sphere)',
            'motion_blur': 'Enable velocity-based motion trails',
        }
