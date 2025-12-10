"""
Unified Physics Scene

Single scene with multiple physics types (fountain, bouncing, orbital, rain).
Maps to existing parameter structure for consistency.
"""

import numpy as np
from .base import BaseScene
from ..physics import (
    PhysicsEngine, PhysicsState, create_particle_pool,
    gravity, drag, wind, gravity_well,
    boundary_collision, boundary_wrap, particle_particle_collision,
    ParticleEmitter, VolumeEmitter,
    particles_to_voxels,
    despawn_old_particles, despawn_out_of_bounds
)
from ..transforms.scrolling import apply_object_scrolling


class PhysicsScene(BaseScene):
    """
    Unified physics scene with multiple types.

    Physics Type: fountain, bouncing, orbital, rain

    Parameter Mapping:
    - size -> particle_radius (all types)
    - density -> particle_count (bouncing/orbital) or emission_rate (fountain/rain)
    - frequency -> velocity (fountain) or attractor_strength (orbital)
    - amplitude -> gravity_strength (all types)
    - rotationX/Y/Z -> emitter direction (fountain/rain)
    """

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)
        self.grid_shape = grid_shape

        # Physics engine (will be reconfigured per type)
        bounds_min = np.array([0, 0, 0], dtype=float)
        bounds_max = np.array(grid_shape, dtype=float) - 1
        self.bounds_min = bounds_min
        self.bounds_max = bounds_max

        self.engine = PhysicsEngine(
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            dt=0.016,
            boundary_mode='bounce'
        )

        # Particle state
        self.state = create_particle_pool(max_particles=400, grid_shape=grid_shape)

        # Emitters (created per type)
        self.emitter = None

        # Current physics type
        self.current_type = 'fountain'

        # Initialize fountain by default
        self._setup_fountain()

    def _apply_rotation(self, positions, params, time):
        """
        Apply rotation transform to particle positions.

        Args:
            positions: (N, 3) array of particle positions
            params: Scene parameters with rotation settings
            time: Current animation time

        Returns:
            Rotated positions (N, 3)
        """
        # Get rotation parameters
        rx = params.rotationX
        ry = params.rotationY
        rz = params.rotationZ
        speed = params.rotation_speed
        offset = params.rotation_offset

        # No rotation needed
        if rx == 0 and ry == 0 and rz == 0 and speed == 0:
            return positions

        # Calculate total rotation with animation
        animated_rotation = (time * speed + offset) * 2 * np.pi
        total_rx = (rx + animated_rotation) * np.pi / 180
        total_ry = (ry + animated_rotation) * np.pi / 180
        total_rz = (rz + animated_rotation) * np.pi / 180

        # Center of rotation (center of grid)
        center = np.array(self.grid_shape, dtype=float) / 2

        # Translate to origin
        translated = positions - center

        # Rotation matrices
        if total_rx != 0:
            # Rotate around X axis
            cos_x, sin_x = np.cos(total_rx), np.sin(total_rx)
            rot_x = np.array([
                [1, 0, 0],
                [0, cos_x, -sin_x],
                [0, sin_x, cos_x]
            ])
            translated = translated @ rot_x.T

        if total_ry != 0:
            # Rotate around Y axis
            cos_y, sin_y = np.cos(total_ry), np.sin(total_ry)
            rot_y = np.array([
                [cos_y, 0, sin_y],
                [0, 1, 0],
                [-sin_y, 0, cos_y]
            ])
            translated = translated @ rot_y.T

        if total_rz != 0:
            # Rotate around Z axis
            cos_z, sin_z = np.cos(total_rz), np.sin(total_rz)
            rot_z = np.array([
                [cos_z, -sin_z, 0],
                [sin_z, cos_z, 0],
                [0, 0, 1]
            ])
            translated = translated @ rot_z.T

        # Translate back
        rotated = translated + center

        return rotated

    def _render_with_transforms(self, raster, params, time, motion_blur, trail_length=0.0):
        """
        Render particles with rotation and scrolling transforms applied.

        Args:
            raster: Raster object
            params: Scene parameters
            time: Current time
            motion_blur: Whether to render motion blur
            trail_length: Length of particle trails (0=no trail, 1=full path)

        Returns:
            Final mask with all transforms applied
        """
        # Apply rotation to particle positions for rendering
        render_state = self.state
        if params.rotationX != 0 or params.rotationY != 0 or params.rotationZ != 0 or params.rotation_speed != 0:
            # Create a copy for rendering with rotated positions
            import copy
            render_state = copy.copy(self.state)
            active_mask = self.state.active
            render_state.position = self.state.position.copy()
            render_state.position[active_mask] = self._apply_rotation(
                self.state.position[active_mask], params, time
            )
            if motion_blur:
                render_state.prev_position = self.state.prev_position.copy()
                render_state.prev_position[active_mask] = self._apply_rotation(
                    self.state.prev_position[active_mask], params, time
                )

        # Render
        # Use motion_blur for short trails, trail_length for longer trails
        use_motion_blur = motion_blur or trail_length > 0
        mask = particles_to_voxels(
            render_state, self.grid_shape,
            render_mode='sphere',
            motion_blur=use_motion_blur
        )

        # Add extended trails if trail_length > 0
        if trail_length > 0.05:  # Only render trails if significantly above 0
            from ..physics.rendering import draw_line_3d, draw_sphere
            active_indices = np.where(render_state.active)[0]

            for i in active_indices:
                pos = render_state.position[i]
                prev_pos = render_state.prev_position[i]

                # Calculate trail direction and length
                trail_vec = pos - prev_pos
                movement = np.linalg.norm(trail_vec)

                if movement > 0.01:  # Only draw if particle moved
                    # Only draw trails for particles that have existed for at least 2 frames
                    # This prevents jump cuts when particles despawn
                    if self.state.age[i] > 1:
                        # Extend trail based on velocity and trail_length
                        # Use quadratic scaling (trail_length^2) to reduce sensitivity at low values
                        # trail_length = 1.0 means show ~10-12 frames of history
                        base_multiplier = 12.0  # More reasonable trail length

                        # Apply quadratic curve for less sensitivity at low values
                        sensitivity_curve = trail_length * trail_length  # Quadratic instead of sqrt
                        trail_multiplier = base_multiplier * sensitivity_curve

                        # Calculate extended trail start position
                        trail_start = pos - (trail_vec * trail_multiplier)

                        # Don't clamp - if trail goes out of bounds, skip it to avoid artifacts
                        # Check if trail would be in bounds
                        in_bounds = (trail_start[0] >= 0 and trail_start[0] < self.grid_shape[0] and
                                   trail_start[1] >= 0 and trail_start[1] < self.grid_shape[1] and
                                   trail_start[2] >= 0 and trail_start[2] < self.grid_shape[2])

                        if in_bounds:
                            # Draw trail - use line for efficiency, only add spheres for visibility
                            mask |= draw_line_3d(trail_start, pos, self.grid_shape)

                            # Add a few spheres along the trail for visibility
                            num_trail_spheres = max(2, min(6, int(trail_length * 6)))  # Max 6 spheres for performance

                            for j in range(num_trail_spheres):
                                t = j / (num_trail_spheres - 1) if num_trail_spheres > 1 else 0
                                trail_pos = trail_start + (pos - trail_start) * t
                                # Use smaller radius for trail spheres
                                trail_radius = render_state.radius[i] * 0.5
                                mask |= draw_sphere(trail_pos, trail_radius, self.grid_shape)

        # Apply object scrolling
        mask = apply_object_scrolling(mask, raster, params, time)

        return mask

    def _setup_fountain(self):
        """Setup fountain physics."""
        self.engine.boundary_mode = 'despawn'
        self.engine.clear_forces()
        self.engine.clear_constraints()

        # Forces
        self.engine.add_force(gravity(g=-9.8, axis=0))
        self.engine.add_force(drag(coefficient=0.05))

        # Constraints
        self.engine.add_constraint(boundary_collision(
            self.bounds_min, self.bounds_max, restitution=0.8
        ))

        # Emitter at bottom center
        emitter_pos = [self.grid_shape[0]/2, self.grid_shape[1]/2, 0]
        self.emitter = ParticleEmitter(
            position=emitter_pos,
            rate=10.0,
            velocity_min=5.0,
            velocity_max=8.0,
            direction=[0, 0, 1],
            spread_angle=15.0,
            particle_lifetime=10.0,
            particle_radius=1.5
        )

        # Reset particles
        self.state.active[:] = False

    def _setup_bouncing(self):
        """Setup bouncing balls physics."""
        self.engine.boundary_mode = 'despawn'
        self.engine.clear_forces()
        self.engine.clear_constraints()

        # Forces
        self.engine.add_force(gravity(g=-9.8, axis=0))
        self.engine.add_force(drag(coefficient=0.02))

        # Constraints
        self.engine.add_constraint(boundary_collision(
            self.bounds_min, self.bounds_max, restitution=0.95
        ))

        self.emitter = None

        # Initialize bouncing balls
        n_balls = 20
        positions = np.random.rand(n_balls, 3)
        positions[:, 0] *= self.grid_shape[0]
        positions[:, 1] *= self.grid_shape[1]
        positions[:, 2] = positions[:, 2] * (self.grid_shape[2] / 2) + (self.grid_shape[2] / 2)

        velocities = (np.random.rand(n_balls, 3) - 0.5) * 8.0
        radii = np.random.uniform(1.0, 2.5, n_balls)
        masses = (4.0/3.0) * np.pi * (radii ** 3)

        self.state.position[:n_balls] = positions
        self.state.velocity[:n_balls] = velocities
        self.state.acceleration[:n_balls] = 0
        self.state.mass[:n_balls] = masses
        self.state.radius[:n_balls] = radii
        self.state.active[:n_balls] = True
        self.state.active[n_balls:] = False
        self.state.age[:] = 0
        self.state.prev_position[:n_balls] = positions

    def _setup_orbital(self):
        """Setup orbital mechanics physics."""
        self.engine.boundary_mode = 'despawn'
        self.engine.clear_forces()
        self.engine.clear_constraints()

        # Central gravity well
        center = np.array(self.grid_shape, dtype=float) / 2
        self.engine.add_force(gravity_well(center=center, strength=50.0))

        # Wrap boundaries
        self.engine.add_constraint(boundary_wrap(self.bounds_min, self.bounds_max + 1))

        self.emitter = None

        # Initialize orbital particles
        n_particles = 50
        G_M = 50.0
        positions = []
        velocities = []

        for i in range(n_particles):
            radius = np.random.uniform(5, min(self.grid_shape) / 2.5)
            angle = np.random.uniform(0, 2 * np.pi)
            z_offset = np.random.uniform(-2, 2)

            pos = center + np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                z_offset
            ])

            orbital_speed = np.sqrt(G_M / radius) * np.random.uniform(0.85, 1.15)
            vel = np.array([
                -orbital_speed * np.sin(angle),
                orbital_speed * np.cos(angle),
                np.random.uniform(-0.5, 0.5)
            ])

            positions.append(pos)
            velocities.append(vel)

        self.state.position[:n_particles] = positions
        self.state.velocity[:n_particles] = velocities
        self.state.acceleration[:n_particles] = 0
        self.state.mass[:n_particles] = 1.0
        self.state.radius[:n_particles] = 1.0
        self.state.active[:n_particles] = True
        self.state.active[n_particles:] = False
        self.state.age[:] = 0
        self.state.prev_position[:n_particles] = positions

    def _setup_rain(self):
        """Setup rain/snow physics."""
        self.engine.boundary_mode = 'despawn'
        self.engine.clear_forces()
        self.engine.clear_constraints()

        # Forces (falling along Z-axis, the shorter edge/depth)
        self.engine.add_force(gravity(g=-5.0, axis=0))  # Fall along Z (axis 0)
        self.engine.add_force(drag(coefficient=0.15))
        self.engine.add_force(wind(
            direction=[0, 1, 0],  # Wind along Y-axis (horizontal)
            strength=2.0,
            turbulence=0.3
        ))

        # Boundary collision (minimal bounce)
        self.engine.add_constraint(boundary_collision(
            self.bounds_min, self.bounds_max, restitution=0.1
        ))

        # Volume emitter at top (max Z position)
        # Position indexing is [Z, Y, X]
        self.emitter = VolumeEmitter(
            bounds_min=[self.grid_shape[0] - 2, 0, 0],  # Top of Z, full Y and X
            bounds_max=[self.grid_shape[0], self.grid_shape[1], self.grid_shape[2]],
            rate=25.0,
            velocity_mean=[-3.0, 0, 0],  # Falling in -Z direction (index 0)
            velocity_variance=0.5,
            particle_lifetime=20.0,
            particle_radius=1.0
        )

        # Reset particles
        self.state.active[:] = False

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate physics scene."""
        # Get physics type
        physics_type = params.scene_params.get('physicsType', 'fountain')

        # Switch type if changed
        if physics_type != self.current_type:
            self.current_type = physics_type
            if physics_type == 'fountain':
                self._setup_fountain()
            elif physics_type == 'bouncing':
                self._setup_bouncing()
            elif physics_type == 'orbital':
                self._setup_orbital()
            elif physics_type == 'rain':
                self._setup_rain()

        # Map parameters based on type
        if physics_type == 'fountain':
            mask = self._generate_fountain(raster, params, time)
        elif physics_type == 'bouncing':
            mask = self._generate_bouncing(raster, params, time)
        elif physics_type == 'orbital':
            mask = self._generate_orbital(raster, params, time)
        elif physics_type == 'rain':
            mask = self._generate_rain(raster, params, time)
        else:
            mask = np.zeros(self.grid_shape, dtype=bool)

        return mask, None  # No copy indices for physics

    def _generate_fountain(self, raster, params, time):
        """Generate fountain using mapped parameters."""
        # Parameter mapping:
        # size -> particle_radius
        # density -> emission_rate (scaled)
        # frequency -> velocity_max (scaled)
        # amplitude -> gravity_strength (scaled and inverted)

        particle_radius = params.size
        emission_rate = params.density * 50  # 0-1 -> 0-50 particles/sec
        velocity_max = 3 + params.frequency * 5  # 0.5-5 -> 5.5-28
        velocity_min = velocity_max * 0.6
        gravity_strength = -params.amplitude * 20  # 0-1 -> 0 to -20

        # Physics-specific params (from scene_params)
        restitution = params.scene_params.get('restitution', 0.8)
        air_resistance = params.scene_params.get('air_resistance', 0.05)
        spread_angle = params.scene_params.get('spread_angle', 15.0)
        motion_blur = params.scene_params.get('motion_blur', False)
        boundary_mode = params.scene_params.get('boundary_mode', 'despawn')

        # Update emitter
        self.emitter.rate = max(1, emission_rate)
        self.emitter.velocity_min = velocity_min
        self.emitter.velocity_max = velocity_max
        self.emitter.particle_radius = particle_radius
        self.emitter.spread_angle = np.deg2rad(spread_angle)

        # Update forces
        self.engine.forces[0] = gravity(g=gravity_strength, axis=0)
        self.engine.forces[1] = drag(coefficient=air_resistance)

        # Update boundary constraint
        if boundary_mode == 'bounce':
            self.engine.constraints[0] = boundary_collision(
                self.bounds_min, self.bounds_max, restitution=restitution
            )
        else:  # despawn mode
            self.engine.constraints[0] = lambda state: state  # no-op constraint

        # Scale physics timestep by animation speed
        base_dt = 0.016
        scaled_dt = base_dt * params.animationSpeed

        # Emit and step
        self.emitter.emit(self.state, time, dt=scaled_dt)
        despawn_old_particles(self.state, max_lifetime=10.0)

        # Apply size variation to newly spawned particles only (age == 0)
        size_variation = params.scene_params.get('particle_size_variation', 0.0)
        new_particles = self.state.active & (self.state.age == 0)
        if np.any(new_particles):
            if size_variation > 0:
                min_size = particle_radius * (1.0 - size_variation)
                max_size = particle_radius * (1.0 + size_variation)
                self.state.radius[new_particles] = np.random.uniform(
                    min_size, max_size, size=np.sum(new_particles)
                )
            else:
                # Ensure all new particles have the correct base size
                self.state.radius[new_particles] = particle_radius

        # Despawn particles outside bounds if in despawn mode
        if boundary_mode == 'despawn':
            despawn_out_of_bounds(self.state, self.bounds_min, self.bounds_max)

        # Temporarily set engine dt for this step
        original_dt = self.engine.dt
        self.engine.dt = scaled_dt
        self.state = self.engine.step(self.state, time)
        self.engine.dt = original_dt

        # Render with transforms
        trail_length = params.scene_params.get('trail_length', 0.0)
        return self._render_with_transforms(raster, params, time, motion_blur, trail_length)

    def _generate_bouncing(self, raster, params, time):
        """Generate bouncing balls using mapped parameters."""
        # Parameter mapping:
        # size -> particle_radius (average)
        # density -> particle_count (scaled)
        # amplitude -> gravity_strength

        particle_count = int(5 + params.density * 95)  # 5-100
        gravity_strength = -params.amplitude * 20

        # Physics-specific params
        restitution = params.scene_params.get('restitution', 0.95)
        air_resistance = params.scene_params.get('air_resistance', 0.02)
        enable_collisions = params.scene_params.get('enable_particle_collisions', False)
        motion_blur = params.scene_params.get('motion_blur', False)
        energy_boost = params.scene_params.get('energy_boost', 0.0)
        trail_length = params.scene_params.get('trail_length', 0.0)
        # Bouncing scene ALWAYS uses bounce mode - that's the whole point!
        boundary_mode = 'bounce'

        # Adjust particle count without full reinitialization
        current_count = np.sum(self.state.active)
        if particle_count < current_count:
            # Remove excess particles
            self.state.active[particle_count:] = False
        elif particle_count > current_count:
            # Add new particles
            n_new = particle_count - current_count
            new_pos = np.random.rand(n_new, 3)
            new_pos[:, 0] *= self.grid_shape[0]
            new_pos[:, 1] *= self.grid_shape[1]
            new_pos[:, 2] = self.grid_shape[2] * 0.75
            self.state.position[current_count:particle_count] = new_pos
            self.state.velocity[current_count:particle_count] = (np.random.rand(n_new, 3) - 0.5) * 8
            self.state.active[current_count:particle_count] = True
            self.state.age[current_count:particle_count] = 0

            # Set masses based on radii (will be set properly after size variation below)
            temp_radii = np.full(n_new, params.size)
            masses = (4.0/3.0) * np.pi * (temp_radii ** 3)
            self.state.mass[current_count:particle_count] = masses

        # Apply size variation to newly added particles only
        size_variation = params.scene_params.get('particle_size_variation', 0.0)
        if current_count < particle_count:
            # New particles were just added
            new_indices = np.arange(current_count, particle_count)
            if size_variation > 0:
                min_size = params.size * (1.0 - size_variation)
                max_size = params.size * (1.0 + size_variation)
                self.state.radius[new_indices] = np.random.uniform(
                    min_size, max_size, size=len(new_indices)
                )
            else:
                self.state.radius[new_indices] = params.size

            # Update masses for new particles based on their radii
            self.state.mass[new_indices] = (4.0/3.0) * np.pi * (self.state.radius[new_indices] ** 3)

        # Ensure all active particles have at least the base size if size param changed
        # (but don't re-randomize existing particles)
        active_indices = np.where(self.state.active)[0]
        if size_variation == 0:
            self.state.radius[active_indices] = params.size
            # Also update masses when size changes
            self.state.mass[active_indices] = (4.0/3.0) * np.pi * (self.state.radius[active_indices] ** 3)

        # Update forces
        self.engine.forces[0] = gravity(g=gravity_strength, axis=0)
        self.engine.forces[1] = drag(coefficient=air_resistance)

        # Update boundary constraint
        if boundary_mode == 'bounce':
            self.engine.constraints[0] = boundary_collision(
                self.bounds_min, self.bounds_max, restitution=restitution
            )
        else:  # despawn mode
            self.engine.constraints[0] = lambda state: state  # no-op constraint

        # Particle collisions (rebuild if changed)
        if len(self.engine.constraints) > 1:
            self.engine.constraints.pop()
        if enable_collisions:
            self.engine.add_constraint(particle_particle_collision(
                enabled=True, restitution=restitution, spatial_hash=True
            ))

        # Scale physics timestep by animation speed
        base_dt = 0.016
        scaled_dt = base_dt * params.animationSpeed

        # Step physics
        original_dt = self.engine.dt
        self.engine.dt = scaled_dt
        self.state = self.engine.step(self.state, time)
        self.engine.dt = original_dt

        # Apply energy boost to prevent balls from slowing down
        if energy_boost > 0:
            active_mask = self.state.active
            if np.any(active_mask):
                # Calculate speed for each particle
                speeds = np.linalg.norm(self.state.velocity[active_mask], axis=1)

                # Boost slow-moving particles
                min_speed = 3.0  # Minimum desirable speed
                slow_particles = speeds < min_speed

                if np.any(slow_particles):
                    # Create mask for active AND slow particles
                    slow_mask = np.zeros(len(self.state.active), dtype=bool)
                    slow_mask[active_mask] = slow_particles

                    # Add energy proportional to boost setting
                    boost_amount = energy_boost * 5.0  # Scale to reasonable range

                    # Add random velocity in current direction or random if nearly stopped
                    for idx in np.where(slow_mask)[0]:
                        current_vel = self.state.velocity[idx]
                        current_speed = np.linalg.norm(current_vel)

                        if current_speed < 0.5:
                            # Nearly stopped - add random direction
                            direction = np.random.randn(3)
                            direction = direction / (np.linalg.norm(direction) + 1e-6)
                        else:
                            # Moving - boost in current direction
                            direction = current_vel / (current_speed + 1e-6)

                        self.state.velocity[idx] += direction * boost_amount

        # Despawn particles outside bounds if in despawn mode
        if boundary_mode == 'despawn':
            despawn_out_of_bounds(self.state, self.bounds_min, self.bounds_max)

        # Render with transforms
        return self._render_with_transforms(raster, params, time, motion_blur, trail_length)

    def _generate_orbital(self, raster, params, time):
        """Generate orbital system using mapped parameters."""
        # Parameter mapping:
        # size -> particle_radius
        # density -> particle_count (scaled)
        # frequency -> attractor_strength (scaled)
        # amplitude -> num_attractors (discrete)

        particle_radius = params.size
        particle_count = int(10 + params.density * 190)  # 10-200
        attractor_strength = 10 + params.frequency * 50  # 15-260
        num_attractors = 1 + int(params.amplitude * 3)  # 1-4

        # Physics-specific params
        air_resistance = params.scene_params.get('air_resistance', 0.0)
        motion_blur = params.scene_params.get('motion_blur', True)
        boundary_mode = params.scene_params.get('boundary_mode', 'despawn')
        energy_boost = params.scene_params.get('energy_boost', 0.3)  # Controls variation/kick strength

        # Dynamically adjust particle count
        current_count = np.sum(self.state.active)
        if particle_count != current_count:
            if particle_count < current_count:
                # Remove excess particles
                self.state.active[particle_count:] = False
            elif particle_count > current_count:
                # Add new particles in orbital positions
                n_new = particle_count - current_count
                center = np.array(self.grid_shape, dtype=float) / 2
                orbit_radius = min(self.grid_shape) / 3

                for i in range(n_new):
                    idx = current_count + i
                    # Random orbital position
                    theta = np.random.rand() * 2 * np.pi
                    phi = np.random.rand() * np.pi

                    offset = orbit_radius * np.array([
                        np.sin(phi) * np.cos(theta),
                        np.sin(phi) * np.sin(theta),
                        np.cos(phi)
                    ])

                    self.state.position[idx] = center + offset
                    # Orbital velocity (perpendicular to radius)
                    direction = np.cross(offset, [0, 0, 1])
                    direction = direction / (np.linalg.norm(direction) + 1e-6)
                    self.state.velocity[idx] = direction * 5.0
                    self.state.active[idx] = True
                    self.state.age[idx] = 0

        # Apply size variation to newly spawned particles only (age == 0)
        size_variation = params.scene_params.get('particle_size_variation', 0.0)
        new_particles = self.state.active & (self.state.age == 0)
        if np.any(new_particles):
            if size_variation > 0:
                min_size = particle_radius * (1.0 - size_variation)
                max_size = particle_radius * (1.0 + size_variation)
                self.state.radius[new_particles] = np.random.uniform(
                    min_size, max_size, size=np.sum(new_particles)
                )
            else:
                self.state.radius[new_particles] = particle_radius

        # Update all particle sizes if variation is 0 (user changed base size)
        if size_variation == 0:
            self.state.radius[:] = particle_radius

        # Update forces (rebuild gravity wells based on num_attractors)
        self.engine.clear_forces()
        center = np.array(self.grid_shape, dtype=float) / 2

        if num_attractors == 1:
            self.engine.add_force(gravity_well(center=center, strength=attractor_strength))
        else:
            radius = min(self.grid_shape) / 4
            for i in range(num_attractors):
                angle = (i / num_attractors) * 2 * np.pi
                attractor_pos = center + np.array([
                    radius * np.cos(angle),
                    radius * np.sin(angle),
                    0
                ])
                self.engine.add_force(gravity_well(
                    center=attractor_pos,
                    strength=attractor_strength / num_attractors
                ))

        if air_resistance > 0:
            self.engine.add_force(drag(coefficient=air_resistance))

        # Update boundary constraint based on mode
        self.engine.clear_constraints()
        if boundary_mode == 'bounce':
            self.engine.add_constraint(boundary_collision(
                self.bounds_min, self.bounds_max, restitution=0.7
            ))

        # Scale physics timestep by animation speed
        base_dt = 0.016
        scaled_dt = base_dt * params.animationSpeed

        # Step physics
        original_dt = self.engine.dt
        self.engine.dt = scaled_dt
        self.state = self.engine.step(self.state, time)
        self.engine.dt = original_dt

        # Add periodic particle refresh to prevent stagnation
        # Frequency and amount controlled by energy_boost
        # Higher energy_boost = more orbital variation and gentle transitions
        if energy_boost > 0.05:
            # More moderate refresh rate
            refresh_multiplier = 1.0 + energy_boost * 4.0  # 1x to 5x faster
            refresh_interval = max(60, int(180 / refresh_multiplier))  # As fast as every 60 frames (1 sec)

            if int(time * 60) % refresh_interval == 0:
                active_mask = self.state.active
                if np.any(active_mask):
                    # Moderate refresh percentage (10-25%)
                    refresh_percent = 0.1 + energy_boost * 0.15  # 10-25%
                    active_indices = np.where(active_mask)[0]
                    num_to_refresh = max(1, int(len(active_indices) * refresh_percent))

                    # Sort by age and get oldest
                    ages = self.state.age[active_indices]
                    oldest_indices = active_indices[np.argsort(ages)[-num_to_refresh:]]

                    # Respawn these particles at new orbital positions
                    center = np.array(self.grid_shape, dtype=float) / 2
                    orbit_radius = min(self.grid_shape) / 3

                    for idx in oldest_indices:
                        # Gentle orbital position variation
                        theta = np.random.rand() * 2 * np.pi
                        phi = np.random.rand() * np.pi
                        # Moderate variation (0.6-1.6x radius)
                        radius_variation = 0.6 + energy_boost * 1.0
                        radius_var = orbit_radius * (0.8 + np.random.rand() * (radius_variation - 0.8))

                        offset = radius_var * np.array([
                            np.sin(phi) * np.cos(theta),
                            np.sin(phi) * np.sin(theta),
                            np.cos(phi)
                        ])

                        self.state.position[idx] = center + offset
                        # Smooth orbital velocity with gentle variation
                        direction = np.cross(offset, [0, 0, 1])
                        direction = direction / (np.linalg.norm(direction) + 1e-6)
                        # Add small random component for variety (not chaos)
                        random_component = np.random.randn(3) * energy_boost * 0.5
                        direction = direction + random_component
                        direction = direction / (np.linalg.norm(direction) + 1e-6)

                        speed_variation = 2.0 + energy_boost * 5.0  # 2-7 units/sec
                        speed_var = 3.0 + np.random.rand() * speed_variation
                        self.state.velocity[idx] = direction * speed_var
                        self.state.age[idx] = 0

        # Gently nudge slow particles to keep them moving
        if energy_boost > 0.05:
            active_mask = self.state.active
            if np.any(active_mask):
                speeds = np.linalg.norm(self.state.velocity[active_mask], axis=1)
                # Moderate detection threshold
                stuck_threshold = 1.0 + energy_boost * 2.0  # Up to 3 units/sec
                stuck_particles = speeds < stuck_threshold

                if np.any(stuck_particles):
                    stuck_mask = np.zeros(len(self.state.active), dtype=bool)
                    stuck_mask[active_mask] = stuck_particles

                    # Gentle nudges to transition orbits
                    center = np.array(self.grid_shape, dtype=float) / 2
                    for idx in np.where(stuck_mask)[0]:
                        to_center = center - self.state.position[idx]
                        to_center_norm = to_center / (np.linalg.norm(to_center) + 1e-6)

                        # Mostly orbital kicks (perpendicular to radius)
                        # Only occasionally random
                        if np.random.rand() < energy_boost * 0.3:
                            # Occasional random nudge (30% chance at max energy)
                            direction = np.random.randn(3) * 0.5
                            direction = direction / (np.linalg.norm(direction) + 1e-6)
                        else:
                            # Mostly perpendicular kicks to change orbit
                            direction = to_center_norm if np.random.rand() > 0.6 else -to_center_norm

                        # Add strong perpendicular component for smooth orbit transitions
                        perp = np.cross(direction, [0, 0, 1])
                        perp = perp / (np.linalg.norm(perp) + 1e-6)

                        # Gentle kicks (2-8 units) - mostly perpendicular
                        kick_strength = 2.0 + energy_boost * 6.0
                        kick = direction * kick_strength * 0.3 + perp * kick_strength
                        self.state.velocity[idx] += kick  # Add to existing velocity

        # Despawn particles outside bounds if in despawn mode
        if boundary_mode == 'despawn':
            despawn_out_of_bounds(self.state, self.bounds_min, self.bounds_max)

        # Render with transforms
        trail_length = params.scene_params.get('trail_length', 0.0)
        return self._render_with_transforms(raster, params, time, motion_blur, trail_length)

    def _generate_rain(self, raster, params, time):
        """Generate rain using mapped parameters."""
        # Parameter mapping:
        # size -> particle_radius
        # density -> emission_rate (scaled)
        # frequency -> wind_speed (scaled)
        # amplitude -> gravity_strength (scaled and inverted)

        particle_radius = params.size
        emission_rate = 5 + params.density * 45  # 5-50
        wind_speed = params.frequency * 2  # 1-10
        gravity_strength = -params.amplitude * 10  # 0 to -10

        # Physics-specific params
        turbulence = params.scene_params.get('turbulence', 0.3)
        motion_blur = params.scene_params.get('motion_blur', True)
        boundary_mode = params.scene_params.get('boundary_mode', 'despawn')

        # Update emitter
        self.emitter.rate = emission_rate
        self.emitter.particle_radius = particle_radius

        # Update forces (falling along Z-axis)
        self.engine.forces[0] = gravity(g=gravity_strength, axis=0)  # Fall along Z (axis 0)
        self.engine.forces[2] = wind(
            direction=[0, 1, 0],  # Wind along Y-axis (horizontal)
            strength=wind_speed,
            turbulence=turbulence
        )

        # Update boundary constraint based on mode
        # Clear and re-add constraint to ensure correct behavior
        self.engine.constraints.clear()
        if boundary_mode == 'bounce':
            # Add boundary collision for bouncing
            self.engine.add_constraint(boundary_collision(
                self.bounds_min, self.bounds_max, restitution=0.1
            ))

        # Scale physics timestep by animation speed
        base_dt = 0.016
        scaled_dt = base_dt * params.animationSpeed

        # Emit and step
        self.emitter.emit(self.state, time, dt=scaled_dt)

        # Apply size variation to newly spawned particles only (age == 0)
        size_variation = params.scene_params.get('particle_size_variation', 0.0)
        new_particles = self.state.active & (self.state.age == 0)
        if np.any(new_particles):
            if size_variation > 0:
                min_size = particle_radius * (1.0 - size_variation)
                max_size = particle_radius * (1.0 + size_variation)
                self.state.radius[new_particles] = np.random.uniform(
                    min_size, max_size, size=np.sum(new_particles)
                )
            else:
                # Ensure all new particles have the correct base size
                self.state.radius[new_particles] = particle_radius

        # Step physics with scaled dt
        original_dt = self.engine.dt
        self.engine.dt = scaled_dt
        self.state = self.engine.step(self.state, time)
        self.engine.dt = original_dt

        # Handle particles that hit ground (bottom of Z-axis, which is position index 0)
        hit_ground = self.state.active & (self.state.position[:, 0] < 1.0)
        if np.any(hit_ground):
            if boundary_mode == 'despawn':
                # Despawn particles that hit ground
                self.state.active[hit_ground] = False
            else:
                # Respawn particles at top (bounce mode default behavior)
                # Position indexing: [Z, Y, X]
                n_respawn = np.sum(hit_ground)
                self.state.position[hit_ground, 0] = raster.length - 1  # Top of Z
                self.state.position[hit_ground, 1] = np.random.uniform(0, raster.height, n_respawn)
                self.state.position[hit_ground, 2] = np.random.uniform(0, raster.width, n_respawn)
                self.state.velocity[hit_ground] = [-3, 0, 0] + np.random.randn(n_respawn, 3) * 0.5
                self.state.age[hit_ground] = 0

        # Despawn particles outside bounds if in despawn mode
        if boundary_mode == 'despawn':
            despawn_out_of_bounds(self.state, self.bounds_min, self.bounds_max)

        # Render with transforms
        trail_length = params.scene_params.get('trail_length', 0.0)
        return self._render_with_transforms(raster, params, time, motion_blur, trail_length)

    @classmethod
    def get_enabled_parameters(cls):
        # Use standard parameters that get mapped to physics
        return [
            'size', 'density', 'frequency', 'amplitude',
            # Physics-specific toggles
            'restitution', 'air_resistance', 'spread_angle',
            'enable_particle_collisions', 'motion_blur', 'turbulence'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        # Could enable rotation for emitter direction in future
        return []

    @classmethod
    def get_defaults(cls):
        return {
            'size': 1.5,
            'density': 0.3,
            'frequency': 2.0,
            'amplitude': 0.5,
            'restitution': 0.8,
            'air_resistance': 0.05,
            'spread_angle': 15.0,
            'enable_particle_collisions': False,
            'motion_blur': False,
            'turbulence': 0.3,
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'size': 'Particle size (fountain/orbital/rain) or avg size (bouncing)',
            'density': 'Emission rate (fountain/rain) or particle count (bouncing/orbital)',
            'frequency': 'Velocity (fountain), attractor strength (orbital), wind speed (rain)',
            'amplitude': 'Gravity strength (fountain/bouncing/rain) or num attractors (orbital)',
            'restitution': 'Bounciness (0=no bounce, 1=perfect bounce)',
            'air_resistance': 'Air drag (0=none, 1=heavy)',
            'spread_angle': 'Fountain cone angle (degrees)',
            'enable_particle_collisions': 'Ball-to-ball collisions (bouncing only, expensive)',
            'motion_blur': 'Velocity-based particle trails',
            'turbulence': 'Wind turbulence/gusts (rain only)',
        }
