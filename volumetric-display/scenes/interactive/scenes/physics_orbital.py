"""
Physics Orbital Mechanics Scene

Gravitational n-body simulation with wrap-around boundaries.
Demonstrates orbital dynamics and gravity wells.
"""

import numpy as np
from .base import BaseScene
from ..physics import (
    PhysicsEngine, PhysicsState,
    gravity_well, drag,
    boundary_wrap,
    particles_to_voxels
)


class PhysicsOrbitalScene(BaseScene):
    """
    Orbital mechanics scene with gravity wells.

    Features:
    - Central gravity well (star/planet)
    - Particles in stable orbits
    - Wrap-around boundaries (toroidal topology)
    - Optional multiple attractors (binary/ternary systems)
    - Minimal drag for long-term stability
    """

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)

        # Physics engine with wrap boundaries (infinite space illusion)
        bounds_min = np.array([0, 0, 0], dtype=float)
        bounds_max = np.array(grid_shape, dtype=float)
        self.engine = PhysicsEngine(
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            dt=0.016,
            boundary_mode='wrap'
        )

        # Setup forces (will be updated from params)
        self.center = np.array(grid_shape, dtype=float) / 2
        self._setup_forces(attractor_strength=50.0, num_attractors=1)

        # Setup wrap boundary constraint
        self.engine.add_constraint(boundary_wrap(bounds_min, bounds_max))

        # Initialize orbital system
        self.state = self._init_orbital_system(n_particles=50)

    def _setup_forces(self, attractor_strength=50.0, num_attractors=1, air_resistance=0.0):
        """Setup force functions with gravity wells."""
        self.engine.clear_forces()

        if num_attractors == 1:
            # Single central attractor
            self.engine.add_force(gravity_well(
                center=self.center,
                strength=attractor_strength,
                min_distance=1.0
            ))
        elif num_attractors == 2:
            # Binary system (two attractors orbiting each other)
            offset = min(self.grid_shape) / 4
            attractor1 = self.center + np.array([offset, 0, 0])
            attractor2 = self.center + np.array([-offset, 0, 0])

            self.engine.add_force(gravity_well(
                center=attractor1,
                strength=attractor_strength / 2,
                min_distance=1.0
            ))
            self.engine.add_force(gravity_well(
                center=attractor2,
                strength=attractor_strength / 2,
                min_distance=1.0
            ))
        elif num_attractors >= 3:
            # Ternary/quad system (attractors in a ring)
            radius = min(self.grid_shape) / 4
            for i in range(num_attractors):
                angle = (i / num_attractors) * 2 * np.pi
                attractor_pos = self.center + np.array([
                    radius * np.cos(angle),
                    radius * np.sin(angle),
                    0
                ])
                self.engine.add_force(gravity_well(
                    center=attractor_pos,
                    strength=attractor_strength / num_attractors,
                    min_distance=1.0
                ))

        # Minimal drag for stability (optional)
        if air_resistance > 0:
            self.engine.add_force(drag(coefficient=air_resistance))

    def _init_orbital_system(self, n_particles=50):
        """Initialize particles in stable circular orbits."""
        positions = []
        velocities = []

        # Attractor strength (for orbital velocity calculation)
        G_M = 50.0  # Matches default gravity well strength

        for i in range(n_particles):
            # Random orbital radius (avoid too close to center)
            min_radius = 3.0
            max_radius = min(self.grid_shape) / 2.5
            radius = np.random.uniform(min_radius, max_radius)

            # Random angle in XY plane
            angle = np.random.uniform(0, 2 * np.pi)

            # Random Z-axis offset (orbital plane variation)
            z_offset = np.random.uniform(-2, 2)

            # Position on circular orbit
            pos = self.center + np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                z_offset
            ])

            # Orbital velocity for circular orbit: v = sqrt(GM/r)
            # Perpendicular to radius vector
            orbital_speed = np.sqrt(G_M / radius)

            # Add some randomness for elliptical orbits
            speed_variation = np.random.uniform(0.85, 1.15)
            orbital_speed *= speed_variation

            # Velocity perpendicular to radius (tangent to orbit)
            vel = np.array([
                -orbital_speed * np.sin(angle),
                orbital_speed * np.cos(angle),
                np.random.uniform(-0.5, 0.5)  # Small Z velocity
            ])

            positions.append(pos)
            velocities.append(vel)

        positions = np.array(positions)
        velocities = np.array(velocities)

        return PhysicsState(
            position=positions,
            velocity=velocities,
            acceleration=np.zeros((n_particles, 3)),
            mass=np.ones(n_particles),
            radius=np.ones(n_particles) * 1.0,
            active=np.ones(n_particles, dtype=bool),
            age=np.zeros(n_particles),
            prev_position=positions.copy()
        )

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate orbital system by stepping physics simulation."""
        # Get parameters
        n_particles = params.scene_params.get('particle_count', 50)
        attractor_strength = params.scene_params.get('attractor_strength', 50.0)
        num_attractors = params.scene_params.get('num_attractors', 1)
        air_resistance = params.scene_params.get('air_resistance', 0.0)
        particle_radius = params.scene_params.get('particle_radius', 1.0)

        # Reinitialize if particle count changed significantly
        current_count = np.sum(self.state.active)
        if abs(n_particles - current_count) > 5:  # Allow small tolerance
            self.state = self._init_orbital_system(n_particles)

        # Update particle radius
        self.state.radius[:] = particle_radius

        # Update forces if parameters changed
        self._setup_forces(attractor_strength, num_attractors, air_resistance)

        # Step physics simulation
        self.state = self.engine.step(self.state, time)

        # Render particles
        render_mode = params.scene_params.get('render_mode', 'sphere')
        motion_blur = params.scene_params.get('motion_blur', True)  # Default ON for orbital

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
            'particle_count', 'particle_radius',
            'attractor_strength', 'num_attractors',
            'air_resistance',
            'render_mode', 'motion_blur'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return []

    @classmethod
    def get_defaults(cls):
        return {
            'particle_count': 50,
            'particle_radius': 1.0,
            'attractor_strength': 50.0,
            'num_attractors': 1,
            'air_resistance': 0.0,
            'render_mode': 'sphere',
            'motion_blur': True,  # Motion blur looks great for orbits
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'particle_count': 'Number of orbiting particles (10-200)',
            'particle_radius': 'Particle size in voxels (0.5-2.0)',
            'attractor_strength': 'Gravitational pull strength (10-200)',
            'num_attractors': 'Number of gravity wells (1=single, 2=binary, 3+=multi)',
            'air_resistance': 'Drag coefficient (0=stable orbits, 0.01+=decay)',
            'render_mode': 'Rendering style (point or sphere)',
            'motion_blur': 'Enable orbital trail streaks (recommended)',
        }
