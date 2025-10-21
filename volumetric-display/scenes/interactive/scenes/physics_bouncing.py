"""
Physics Bouncing Balls Scene

Elastic bouncing balls with optional particle-particle collisions.
Demonstrates rigid body dynamics and collision response.
"""

import numpy as np
from .base import BaseScene
from ..physics import (
    PhysicsEngine, PhysicsState,
    gravity, drag,
    boundary_collision, particle_particle_collision,
    particles_to_voxels
)


class PhysicsBouncingScene(BaseScene):
    """
    Bouncing balls scene with elastic collisions.

    Features:
    - Random initial positions and velocities
    - Gravity and air resistance
    - Bouncy wall collisions
    - Optional particle-particle collisions
    - Variable ball sizes and masses
    """

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)

        # Physics engine with bounce boundaries
        bounds_min = np.array([0, 0, 0], dtype=float)
        bounds_max = np.array(grid_shape, dtype=float) - 1
        self.engine = PhysicsEngine(
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            dt=0.016,
            boundary_mode='bounce'
        )

        # Setup forces
        self._setup_forces(gravity_strength=-9.8, air_resistance=0.02)

        # Setup constraints
        self._setup_constraints(bounds_min, bounds_max, restitution=0.95,
                               enable_particle_collisions=False)

        # Initialize bouncing balls
        self.state = self._init_bouncing_balls(n_balls=20)

        # Track collision state for UI updates
        self.particle_collisions_enabled = False

    def _setup_forces(self, gravity_strength=-9.8, air_resistance=0.02):
        """Setup force functions."""
        self.engine.clear_forces()
        self.engine.add_force(gravity(g=gravity_strength, axis=0))
        self.engine.add_force(drag(coefficient=air_resistance))

    def _setup_constraints(self, bounds_min, bounds_max, restitution=0.95,
                          enable_particle_collisions=False):
        """Setup constraint functions."""
        self.engine.clear_constraints()

        # Boundary collision (always enabled)
        self.engine.add_constraint(boundary_collision(
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            restitution=restitution
        ))

        # Particle-particle collision (optional)
        if enable_particle_collisions:
            self.engine.add_constraint(particle_particle_collision(
                enabled=True,
                restitution=restitution,
                spatial_hash=True  # Use spatial hashing for performance
            ))

    def _init_bouncing_balls(self, n_balls=20):
        """Initialize balls with random positions and velocities."""
        # Random positions in upper half of volume
        positions = np.random.rand(n_balls, 3)
        positions[:, 0] *= self.grid_shape[0]
        positions[:, 1] *= self.grid_shape[1]
        positions[:, 2] = positions[:, 2] * (self.grid_shape[2] / 2) + (self.grid_shape[2] / 2)

        # Random velocities (moderate initial motion)
        velocities = (np.random.rand(n_balls, 3) - 0.5) * 8.0

        # Variable ball sizes (1.0 to 2.5 voxels)
        radii = np.random.uniform(1.0, 2.5, n_balls)

        # Mass proportional to volume (4/3 * pi * r^3)
        masses = (4.0/3.0) * np.pi * (radii ** 3)

        return PhysicsState(
            position=positions,
            velocity=velocities,
            acceleration=np.zeros((n_balls, 3)),
            mass=masses,
            radius=radii,
            active=np.ones(n_balls, dtype=bool),
            age=np.zeros(n_balls),
            prev_position=positions.copy()
        )

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate bouncing balls by stepping physics simulation."""
        # Get parameters
        n_balls = params.scene_params.get('particle_count', 20)
        gravity_strength = params.scene_params.get('gravity_strength', -9.8)
        air_resistance = params.scene_params.get('air_resistance', 0.02)
        restitution = params.scene_params.get('restitution', 0.95)
        enable_collisions = params.scene_params.get('enable_particle_collisions', False)

        # Reinitialize if particle count changed
        current_count = np.sum(self.state.active)
        if n_balls != current_count:
            self.state = self._init_bouncing_balls(n_balls)

        # Update forces
        self._setup_forces(gravity_strength, air_resistance)

        # Update constraints if collision state changed
        bounds_min = np.array([0, 0, 0], dtype=float)
        bounds_max = np.array(self.grid_shape, dtype=float) - 1

        if enable_collisions != self.particle_collisions_enabled:
            self.particle_collisions_enabled = enable_collisions
            self._setup_constraints(bounds_min, bounds_max, restitution, enable_collisions)
        else:
            # Just update restitution
            self._setup_constraints(bounds_min, bounds_max, restitution, enable_collisions)

        # Step physics simulation
        self.state = self.engine.step(self.state, time)

        # Render particles
        render_mode = params.scene_params.get('render_mode', 'sphere')
        motion_blur = params.scene_params.get('motion_blur', False)

        mask = particles_to_voxels(
            self.state,
            self.grid_shape,
            render_mode=render_mode,
            motion_blur=motion_blur
        )

        return mask

    @classmethod
    def get_enabled_parameters(cls):
        return [
            'particle_count',
            'gravity_strength', 'air_resistance', 'restitution',
            'enable_particle_collisions',
            'render_mode', 'motion_blur'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return []

    @classmethod
    def get_defaults(cls):
        return {
            'particle_count': 20,
            'gravity_strength': -9.8,
            'air_resistance': 0.02,
            'restitution': 0.95,
            'enable_particle_collisions': False,
            'render_mode': 'sphere',
            'motion_blur': False,
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'particle_count': 'Number of bouncing balls (5-100)',
            'gravity_strength': 'Gravity acceleration (-20 to 20)',
            'air_resistance': 'Air drag coefficient (0-1)',
            'restitution': 'Bounce elasticity (0.5-1.0 for bouncy)',
            'enable_particle_collisions': 'Enable ball-to-ball collisions (expensive)',
            'render_mode': 'Rendering style (point or sphere)',
            'motion_blur': 'Enable velocity-based motion trails',
        }
