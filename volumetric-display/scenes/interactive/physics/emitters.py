"""
Particle Emitters

Systems for spawning and managing particle lifecycle:
- ParticleEmitter: Point/cone emitter (fountains, jets)
- VolumeEmitter: Spawn particles in a volume (rain, fog)
- Lifecycle management (spawn, age, despawn)
"""

import numpy as np
from .engine import PhysicsState


class ParticleEmitter:
    """
    Point or cone emitter for continuous particle emission.

    Useful for:
    - Fountains (upward cone)
    - Jets/thrusters (directional cone)
    - Explosions (spherical emission)
    """

    def __init__(self, position: np.ndarray, rate: float = 10.0,
                 velocity_min: float = 3.0, velocity_max: float = 8.0,
                 direction: np.ndarray = None, spread_angle: float = 15.0,
                 particle_lifetime: float = 10.0, particle_radius: float = 1.5):
        """
        Initialize particle emitter.

        Args:
            position: (3,) emission point position
            rate: Particles per second to emit
            velocity_min: Minimum initial velocity magnitude
            velocity_max: Maximum initial velocity magnitude
            direction: (3,) emission direction (default [0, 0, 1] = upward)
                       Will be normalized
            spread_angle: Cone spread in degrees (0 = straight, 90 = hemisphere)
            particle_lifetime: Max lifetime in seconds before despawn
            particle_radius: Radius for newly spawned particles

        Example:
            # Upward fountain
            emitter = ParticleEmitter(
                position=[8, 8, 0],
                rate=15,
                velocity_min=5.0,
                velocity_max=8.0,
                direction=[0, 0, 1],
                spread_angle=20.0
            )
        """
        self.position = np.array(position, dtype=float)
        self.rate = rate
        self.velocity_min = velocity_min
        self.velocity_max = velocity_max

        if direction is None:
            self.direction = np.array([0.0, 0.0, 1.0])
        else:
            self.direction = np.array(direction, dtype=float)
            self.direction = self.direction / np.linalg.norm(self.direction)

        self.spread_angle = np.deg2rad(spread_angle)
        self.particle_lifetime = particle_lifetime
        self.particle_radius = particle_radius

        # Emission timing
        self.last_emit_time = 0.0
        self.emit_accumulator = 0.0

    def emit(self, state: PhysicsState, t: float, dt: float) -> int:
        """
        Emit particles into the particle pool.

        Args:
            state: PhysicsState to modify
            t: Current simulation time
            dt: Time delta since last emit

        Returns:
            Number of particles emitted

        Example:
            n_spawned = emitter.emit(state, time, 0.016)
        """
        # Accumulate time for fractional emission
        self.emit_accumulator += self.rate * dt

        # Emit whole particles
        n_to_emit = int(self.emit_accumulator)
        self.emit_accumulator -= n_to_emit

        if n_to_emit == 0:
            return 0

        # Find inactive particle slots
        inactive_indices = np.where(~state.active)[0]

        if len(inactive_indices) == 0:
            # No free slots, recycle oldest particles
            inactive_indices = np.argsort(state.age)[-n_to_emit:]

        # Limit to available slots
        n_to_emit = min(n_to_emit, len(inactive_indices))
        spawn_indices = inactive_indices[:n_to_emit]

        # Spawn particles
        for idx in spawn_indices:
            # Random velocity magnitude
            vel_mag = np.random.uniform(self.velocity_min, self.velocity_max)

            # Random direction within cone
            vel_dir = self._random_cone_direction()

            # Set particle state
            state.position[idx] = self.position
            state.velocity[idx] = vel_dir * vel_mag
            state.acceleration[idx] = [0, 0, 0]
            state.radius[idx] = self.particle_radius
            state.active[idx] = True
            state.age[idx] = 0.0
            state.prev_position[idx] = self.position

        return n_to_emit

    def _random_cone_direction(self) -> np.ndarray:
        """
        Generate a random direction within the emission cone.

        Returns:
            (3,) normalized direction vector
        """
        # Random angle from cone axis (0 to spread_angle)
        theta = np.random.uniform(0, self.spread_angle)

        # Random rotation around cone axis
        phi = np.random.uniform(0, 2 * np.pi)

        # Convert to Cartesian (cone coordinates)
        # Start with cone pointing along Z-axis
        cone_dir = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])

        # Rotate to align with emission direction
        return self._rotate_to_direction(cone_dir)

    def _rotate_to_direction(self, vec: np.ndarray) -> np.ndarray:
        """
        Rotate a vector from Z-axis alignment to emission direction.

        Args:
            vec: (3,) vector in cone coordinates

        Returns:
            (3,) rotated vector
        """
        # If direction is already Z-axis, no rotation needed
        z_axis = np.array([0.0, 0.0, 1.0])
        if np.allclose(self.direction, z_axis):
            return vec

        # Rotation axis (perpendicular to both)
        axis = np.cross(z_axis, self.direction)
        axis_norm = np.linalg.norm(axis)

        if axis_norm < 1e-6:
            # Direction is opposite to Z (pointing down)
            return -vec

        axis = axis / axis_norm

        # Rotation angle
        angle = np.arccos(np.dot(z_axis, self.direction))

        # Rodrigues' rotation formula
        rotated = (vec * np.cos(angle) +
                  np.cross(axis, vec) * np.sin(angle) +
                  axis * np.dot(axis, vec) * (1 - np.cos(angle)))

        return rotated


class VolumeEmitter:
    """
    Volume emitter for spawning particles in a region.

    Useful for:
    - Rain (spawn at top of volume)
    - Fog (spawn throughout volume)
    - Ambient particles
    """

    def __init__(self, bounds_min: np.ndarray, bounds_max: np.ndarray,
                 rate: float = 20.0, velocity_mean: np.ndarray = None,
                 velocity_variance: float = 1.0, particle_lifetime: float = 10.0,
                 particle_radius: float = 1.5):
        """
        Initialize volume emitter.

        Args:
            bounds_min: (3,) minimum XYZ of emission volume
            bounds_max: (3,) maximum XYZ of emission volume
            rate: Particles per second to emit
            velocity_mean: (3,) mean initial velocity (default [0, 0, -2] = downward)
            velocity_variance: Random velocity variance
            particle_lifetime: Max lifetime before despawn
            particle_radius: Radius for newly spawned particles

        Example:
            # Rain from ceiling
            emitter = VolumeEmitter(
                bounds_min=[0, 0, 15],
                bounds_max=[16, 16, 16],
                rate=25,
                velocity_mean=[0, 0, -3],
                velocity_variance=0.5
            )
        """
        self.bounds_min = np.array(bounds_min, dtype=float)
        self.bounds_max = np.array(bounds_max, dtype=float)
        self.rate = rate

        if velocity_mean is None:
            self.velocity_mean = np.array([0.0, 0.0, -2.0])
        else:
            self.velocity_mean = np.array(velocity_mean, dtype=float)

        self.velocity_variance = velocity_variance
        self.particle_lifetime = particle_lifetime
        self.particle_radius = particle_radius

        # Emission timing
        self.emit_accumulator = 0.0

    def emit(self, state: PhysicsState, t: float, dt: float) -> int:
        """
        Emit particles into the volume.

        Args:
            state: PhysicsState to modify
            t: Current simulation time
            dt: Time delta since last emit

        Returns:
            Number of particles emitted
        """
        # Accumulate time for fractional emission
        self.emit_accumulator += self.rate * dt

        # Emit whole particles
        n_to_emit = int(self.emit_accumulator)
        self.emit_accumulator -= n_to_emit

        if n_to_emit == 0:
            return 0

        # Find inactive particle slots
        inactive_indices = np.where(~state.active)[0]

        if len(inactive_indices) == 0:
            # No free slots, recycle oldest particles
            inactive_indices = np.argsort(state.age)[-n_to_emit:]

        # Limit to available slots
        n_to_emit = min(n_to_emit, len(inactive_indices))
        spawn_indices = inactive_indices[:n_to_emit]

        # Spawn particles at random positions in volume
        for idx in spawn_indices:
            # Random position in volume
            pos = np.random.uniform(self.bounds_min, self.bounds_max)

            # Random velocity (mean + variance)
            vel = self.velocity_mean + np.random.randn(3) * self.velocity_variance

            # Set particle state
            state.position[idx] = pos
            state.velocity[idx] = vel
            state.acceleration[idx] = [0, 0, 0]
            state.radius[idx] = self.particle_radius
            state.active[idx] = True
            state.age[idx] = 0.0
            state.prev_position[idx] = pos

        return n_to_emit


def despawn_old_particles(state: PhysicsState, max_lifetime: float):
    """
    Deactivate particles that exceed maximum lifetime.

    Args:
        state: PhysicsState to modify
        max_lifetime: Maximum age in seconds

    Example:
        # Remove particles older than 10 seconds
        despawn_old_particles(state, max_lifetime=10.0)
    """
    old_particles = state.active & (state.age > max_lifetime)
    state.active[old_particles] = False


def despawn_out_of_bounds(state: PhysicsState, bounds_min: np.ndarray, bounds_max: np.ndarray):
    """
    Deactivate particles that leave the specified bounds.

    Useful for rain (despawn at ground) or open systems.

    Args:
        state: PhysicsState to modify
        bounds_min: (3,) minimum bounds
        bounds_max: (3,) maximum bounds

    Example:
        # Despawn particles that hit the ground
        despawn_out_of_bounds(state, [0, 0, 0], [16, 16, 16])
    """
    bounds_min = np.array(bounds_min, dtype=float)
    bounds_max = np.array(bounds_max, dtype=float)

    out_of_bounds = state.active & (
        (state.position[:, 0] < bounds_min[0]) |
        (state.position[:, 0] > bounds_max[0]) |
        (state.position[:, 1] < bounds_min[1]) |
        (state.position[:, 1] > bounds_max[1]) |
        (state.position[:, 2] < bounds_min[2]) |
        (state.position[:, 2] > bounds_max[2])
    )

    state.active[out_of_bounds] = False
