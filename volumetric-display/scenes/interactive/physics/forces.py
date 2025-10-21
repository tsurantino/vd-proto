"""
Physics Force Functions

Modular force functions for particle physics:
- gravity: Uniform gravitational acceleration
- drag: Air resistance proportional to velocity
- wind: Directional wind with optional turbulence
- gravity_well: Point attractor (inverse square law)
- spring: Hooke's law spring forces
"""

import numpy as np
from .engine import PhysicsState


def gravity(g: float = -9.8, axis: int = 2):
    """
    Create a uniform gravity force in the specified axis direction.

    Args:
        g: Gravitational acceleration (default -9.8 m/s^2)
            Negative = downward, positive = upward
        axis: Axis index (0=X, 1=Y, 2=Z)

    Returns:
        Force function: (state, t) -> force_array (N, 3)

    Example:
        # Z-axis downward gravity
        engine.add_force(gravity(g=-9.8, axis=2))

        # Y-axis upward anti-gravity
        engine.add_force(gravity(g=5.0, axis=1))
    """
    def force_func(state: PhysicsState, t: float) -> np.ndarray:
        force = np.zeros_like(state.position, dtype=float)
        # F = m * g (only for active particles)
        force[state.active, axis] = state.mass[state.active] * g
        return force

    force_func.__name__ = 'gravity'
    return force_func


def drag(coefficient: float = 0.1):
    """
    Create air resistance/drag force.

    Drag is proportional to velocity (linear drag model).
    F_drag = -k * v

    Args:
        coefficient: Drag coefficient (higher = more resistance)
            Typical values: 0.01-0.5
            0.1 = moderate air resistance
            0.5 = thick fluid (honey)

    Returns:
        Force function: (state, t) -> force_array (N, 3)

    Example:
        # Light air resistance
        engine.add_force(drag(coefficient=0.05))

        # Heavy damping
        engine.add_force(drag(coefficient=0.3))
    """
    def force_func(state: PhysicsState, t: float) -> np.ndarray:
        # F_drag = -k * v
        force = -coefficient * state.velocity
        # Only apply to active particles
        force[~state.active] = 0
        return force

    force_func.__name__ = 'drag'
    return force_func


def gravity_well(center: np.ndarray, strength: float = 10.0, min_distance: float = 0.1):
    """
    Create a gravitational attraction point (inverse square law).

    Simulates point mass attraction (planets, black holes, etc.)
    F = G * m / r^2, direction toward center

    Args:
        center: (3,) array of well center position
        strength: Gravitational strength (G*M combined constant)
            Typical values: 10-200
            Higher = stronger pull
        min_distance: Minimum distance to prevent singularity
            Clamps force at very close distances

    Returns:
        Force function: (state, t) -> force_array (N, 3)

    Example:
        # Central attractor at volume center
        center = np.array([gridX/2, gridY/2, gridZ/2])
        engine.add_force(gravity_well(center=center, strength=50.0))

        # Binary star system (add two wells)
        engine.add_force(gravity_well(center=[5, 5, 5], strength=30.0))
        engine.add_force(gravity_well(center=[10, 10, 10], strength=30.0))
    """
    center = np.array(center, dtype=float)

    def force_func(state: PhysicsState, t: float) -> np.ndarray:
        # Vector from particle to center
        r_vec = center - state.position
        r_mag = np.linalg.norm(r_vec, axis=1, keepdims=True)

        # Prevent division by zero
        r_mag = np.maximum(r_mag, min_distance)

        # F = G * m / r^2, direction toward center
        force_magnitude = (strength * state.mass[:, np.newaxis]) / (r_mag ** 2)
        force_direction = r_vec / r_mag

        force = force_magnitude * force_direction

        # Only apply to active particles
        force[~state.active] = 0
        return force

    force_func.__name__ = 'gravity_well'
    return force_func


def wind(direction: np.ndarray, strength: float = 1.0, turbulence: float = 0.0):
    """
    Create directional wind force with optional turbulence.

    Args:
        direction: (3,) wind direction vector (will be normalized)
        strength: Wind strength/speed
            Typical values: 0-10
        turbulence: Random turbulence magnitude (0-1)
            0 = smooth wind
            1 = chaotic gusts

    Returns:
        Force function: (state, t) -> force_array (N, 3)

    Example:
        # Smooth wind in +X direction
        engine.add_force(wind(direction=[1, 0, 0], strength=2.0))

        # Turbulent diagonal wind
        engine.add_force(wind(
            direction=[1, 1, 0],
            strength=3.0,
            turbulence=0.4
        ))
    """
    direction = np.array(direction, dtype=float)
    direction = direction / np.linalg.norm(direction)  # Normalize

    def force_func(state: PhysicsState, t: float) -> np.ndarray:
        # Base wind force
        base_force = direction * strength

        n_particles = len(state.position)
        force = np.tile(base_force, (n_particles, 1))

        # Add turbulence (Perlin-like noise)
        if turbulence > 0:
            # Time-varying noise for organic motion
            noise_seed = int(t * 10)  # Change noise pattern over time
            np.random.seed(noise_seed)
            noise = np.random.randn(n_particles, 3) * turbulence * strength
            force += noise

        # Only apply to active particles
        force[~state.active] = 0
        return force

    force_func.__name__ = 'wind'
    return force_func


def spring(anchor_positions: np.ndarray, stiffness: float = 10.0, damping: float = 0.5):
    """
    Create spring forces connecting particles to anchor points.

    Implements Hooke's law with damping:
    F = -k * (x - x0) - c * v

    Useful for:
    - Cloth simulation (spring networks)
    - Tethered particles
    - Soft body dynamics

    Args:
        anchor_positions: (N, 3) array of anchor point positions
            One anchor per particle
        stiffness: Spring stiffness constant (k)
            Higher = stiffer spring
            Typical values: 5-50
        damping: Damping coefficient (c)
            Higher = more energy loss
            Typical values: 0.1-2.0

    Returns:
        Force function: (state, t) -> force_array (N, 3)

    Example:
        # Particles tethered to initial positions
        initial_positions = state.position.copy()
        engine.add_force(spring(
            anchor_positions=initial_positions,
            stiffness=20.0,
            damping=0.8
        ))
    """
    anchor_positions = np.array(anchor_positions, dtype=float)

    def force_func(state: PhysicsState, t: float) -> np.ndarray:
        # Hooke's law: F = -k * (x - x0) - c * v
        displacement = state.position - anchor_positions
        spring_force = -stiffness * displacement
        damping_force = -damping * state.velocity

        force = spring_force + damping_force

        # Only apply to active particles
        force[~state.active] = 0
        return force

    force_func.__name__ = 'spring'
    return force_func


def vortex(center: np.ndarray, axis: np.ndarray, strength: float = 5.0, radius: float = 10.0):
    """
    Create a vortex/tornado force field.

    Particles are pulled toward the axis and swirled around it.

    Args:
        center: (3,) center point of vortex
        axis: (3,) axis direction (will be normalized)
        strength: Vortex strength (tangential velocity)
        radius: Effective radius of vortex

    Returns:
        Force function: (state, t) -> force_array (N, 3)

    Example:
        # Vertical tornado
        engine.add_force(vortex(
            center=[gridX/2, gridY/2, 0],
            axis=[0, 0, 1],
            strength=8.0,
            radius=5.0
        ))
    """
    center = np.array(center, dtype=float)
    axis = np.array(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)  # Normalize

    def force_func(state: PhysicsState, t: float) -> np.ndarray:
        # Vector from center to particle
        r_vec = state.position - center

        # Project onto axis
        r_parallel = np.dot(r_vec, axis)[:, np.newaxis] * axis
        r_perp = r_vec - r_parallel

        # Distance from axis
        r_perp_mag = np.linalg.norm(r_perp, axis=1, keepdims=True)
        r_perp_mag = np.maximum(r_perp_mag, 0.1)  # Prevent division by zero

        # Tangential direction (perpendicular to both axis and radius)
        tangent = np.cross(axis, r_perp)

        # Force magnitude decreases with distance from axis
        falloff = np.exp(-r_perp_mag / radius)
        force_magnitude = strength * falloff

        # Tangential force (swirl)
        force = force_magnitude * tangent

        # Add inward pull toward axis
        inward_strength = strength * 0.3
        force -= inward_strength * falloff * (r_perp / r_perp_mag)

        # Only apply to active particles
        force[~state.active] = 0
        return force

    force_func.__name__ = 'vortex'
    return force_func
