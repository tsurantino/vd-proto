"""
Physics Rain/Snow Scene

Atmospheric precipitation with wind and turbulence.
Demonstrates volume emission and environmental effects.
"""

import numpy as np
from .base import BaseScene
from ..physics import (
    PhysicsEngine, create_particle_pool,
    gravity, drag, wind,
    boundary_collision,
    VolumeEmitter,
    particles_to_voxels,
    despawn_out_of_bounds
)


class PhysicsRainScene(BaseScene):
    """
    Rain/snow scene with continuous volume emission.

    Features:
    - Particles spawn at top of volume
    - Downward gravity (rainfall)
    - Wind with turbulence (drift and gusts)
    - Respawn at top when hitting ground
    - Adjustable density and speed
    """

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)

        # Physics engine with bounce boundaries (but we respawn instead)
        bounds_min = np.array([0, 0, 0], dtype=float)
        bounds_max = np.array(grid_shape, dtype=float) - 1
        self.engine = PhysicsEngine(
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            dt=0.016,
            boundary_mode='bounce'
        )

        # Create particle pool (larger for rain effect)
        self.state = create_particle_pool(max_particles=400, grid_shape=grid_shape)

        # Volume emitter at top of display
        self.emitter = VolumeEmitter(
            bounds_min=[0, 0, grid_shape[0] - 2],
            bounds_max=[grid_shape[2], grid_shape[1], grid_shape[0]],
            rate=25.0,
            velocity_mean=[0, 0, -3.0],  # Downward
            velocity_variance=0.5,
            particle_lifetime=20.0,
            particle_radius=1.0
        )

        # Setup forces (will be updated from params)
        self._setup_forces(
            gravity_strength=-5.0,
            air_resistance=0.15,
            wind_speed=2.0,
            wind_direction=[1, 0, 0],
            turbulence=0.3
        )

        # Boundary collision (light bounce for ground interaction)
        self.engine.add_constraint(boundary_collision(
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            restitution=0.1  # Minimal bounce (rain splatter)
        ))

        # Track ground level for respawn
        self.ground_level = 1.0

    def _setup_forces(self, gravity_strength=-5.0, air_resistance=0.15,
                     wind_speed=2.0, wind_direction=[1, 0, 0], turbulence=0.3):
        """Setup force functions."""
        self.engine.clear_forces()

        # Downward gravity
        self.engine.add_force(gravity(g=gravity_strength, axis=0))

        # Air resistance (terminal velocity)
        self.engine.add_force(drag(coefficient=air_resistance))

        # Wind with turbulence
        if wind_speed > 0:
            self.engine.add_force(wind(
                direction=np.array(wind_direction, dtype=float),
                strength=wind_speed,
                turbulence=turbulence
            ))

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate rain by stepping physics simulation."""
        # Get parameters
        emission_rate = params.scene_params.get('emission_rate', 25.0)
        gravity_strength = params.scene_params.get('gravity_strength', -5.0)
        air_resistance = params.scene_params.get('air_resistance', 0.15)
        wind_speed = params.scene_params.get('wind_speed', 2.0)
        turbulence = params.scene_params.get('turbulence', 0.3)
        particle_radius = params.scene_params.get('particle_radius', 1.0)

        # Wind direction from UI
        wind_dir_x = params.scene_params.get('wind_direction_x', 1.0)
        wind_dir_y = params.scene_params.get('wind_direction_y', 0.0)
        wind_direction = [wind_dir_x, wind_dir_y, 0]

        # Update emitter parameters
        self.emitter.rate = emission_rate
        self.emitter.particle_radius = particle_radius

        # Update emitter velocity (falling speed)
        fall_speed = params.scene_params.get('fall_speed', -3.0)
        self.emitter.velocity_mean = np.array([0, 0, fall_speed])

        # Update forces
        self._setup_forces(
            gravity_strength=gravity_strength,
            air_resistance=air_resistance,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            turbulence=turbulence
        )

        # Emit new particles from top
        self.emitter.emit(self.state, time, dt=0.016)

        # Step physics simulation
        self.state = self.engine.step(self.state, time)

        # Respawn particles that hit ground (instead of despawning)
        hit_ground = self.state.active & (self.state.position[:, 0] < self.ground_level)
        if np.any(hit_ground):
            # Respawn at top with random XY position
            n_respawn = np.sum(hit_ground)
            self.state.position[hit_ground, 2] = np.random.uniform(
                0, raster.width, n_respawn
            )
            self.state.position[hit_ground, 1] = np.random.uniform(
                0, raster.height, n_respawn
            )
            self.state.position[hit_ground, 0] = raster.length - 1

            # Reset velocity (falling + small random)
            self.state.velocity[hit_ground, 0] = fall_speed + np.random.uniform(-0.5, 0.5, n_respawn)
            self.state.velocity[hit_ground, 1] = np.random.uniform(-0.5, 0.5, n_respawn)
            self.state.velocity[hit_ground, 2] = np.random.uniform(-0.5, 0.5, n_respawn)

            # Reset age
            self.state.age[hit_ground] = 0

        # Render particles with motion blur (streaks)
        render_mode = params.scene_params.get('render_mode', 'sphere')
        motion_blur = params.scene_params.get('motion_blur', True)  # Default ON for rain

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
            'emission_rate', 'particle_radius',
            'fall_speed', 'gravity_strength', 'air_resistance',
            'wind_speed', 'wind_direction_x', 'wind_direction_y', 'turbulence',
            'render_mode', 'motion_blur'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return []

    @classmethod
    def get_defaults(cls):
        return {
            'emission_rate': 25.0,
            'particle_radius': 1.0,
            'fall_speed': -3.0,
            'gravity_strength': -5.0,
            'air_resistance': 0.15,
            'wind_speed': 2.0,
            'wind_direction_x': 1.0,
            'wind_direction_y': 0.0,
            'turbulence': 0.3,
            'render_mode': 'sphere',
            'motion_blur': True,  # Rain streaks look better with blur
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'emission_rate': 'Particles spawned per second (5-50)',
            'particle_radius': 'Raindrop size in voxels (0.5-2.0)',
            'fall_speed': 'Initial downward velocity (-1 to -10)',
            'gravity_strength': 'Gravity acceleration (-10 to 0)',
            'air_resistance': 'Drag for terminal velocity (0-0.5)',
            'wind_speed': 'Horizontal wind strength (0-10)',
            'wind_direction_x': 'Wind X component (-1 to 1)',
            'wind_direction_y': 'Wind Y component (-1 to 1)',
            'turbulence': 'Random wind gusts (0-1)',
            'render_mode': 'Rendering style (point or sphere)',
            'motion_blur': 'Enable rain streak trails (recommended)',
        }
