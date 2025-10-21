"""
Physics Engine Core

Implements Verlet integration for particle physics simulation.
Supports forces, constraints, and configurable boundary conditions.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Callable, Optional


@dataclass
class PhysicsState:
    """
    Physical state of particles.

    All arrays are (N, 3) or (N,) where N is the number of particles.
    Supports particle pooling via active mask.
    """
    position: np.ndarray          # (N, 3) - continuous coordinates
    velocity: np.ndarray          # (N, 3) - velocity vectors
    acceleration: np.ndarray      # (N, 3) - acceleration vectors
    mass: np.ndarray              # (N,) - particle masses
    radius: np.ndarray            # (N,) - particle radii for collisions/rendering
    active: np.ndarray            # (N,) bool - active particle mask
    age: np.ndarray               # (N,) float - particle age in seconds
    prev_position: np.ndarray     # (N, 3) - previous position for motion blur

    def __post_init__(self):
        """Ensure all arrays have consistent shape."""
        self.n_particles = len(self.position)
        assert self.velocity.shape == (self.n_particles, 3), "velocity shape mismatch"
        assert self.acceleration.shape == (self.n_particles, 3), "acceleration shape mismatch"
        assert self.mass.shape == (self.n_particles,), "mass shape mismatch"
        assert self.radius.shape == (self.n_particles,), "radius shape mismatch"
        assert self.active.shape == (self.n_particles,), "active shape mismatch"
        assert self.age.shape == (self.n_particles,), "age shape mismatch"
        assert self.prev_position.shape == (self.n_particles, 3), "prev_position shape mismatch"


class PhysicsEngine:
    """
    Particle physics engine using Verlet integration.

    Features:
    - Modular force system (gravity, drag, wind, etc.)
    - Constraint system (collisions, boundaries)
    - Configurable boundary modes (bounce, wrap)
    - Vectorized NumPy operations for performance
    """

    def __init__(self, bounds_min: np.ndarray, bounds_max: np.ndarray,
                 dt: float = 0.016, boundary_mode: str = 'bounce'):
        """
        Initialize physics engine.

        Args:
            bounds_min: (3,) array of minimum XYZ bounds
            bounds_max: (3,) array of maximum XYZ bounds
            dt: Time step in seconds (default 60fps = 0.016s)
            boundary_mode: 'bounce' or 'wrap' for boundary handling
        """
        self.bounds_min = np.array(bounds_min, dtype=float)
        self.bounds_max = np.array(bounds_max, dtype=float)
        self.dt = dt
        self.boundary_mode = boundary_mode

        # Force and constraint lists
        self.forces: List[Callable] = []
        self.constraints: List[Callable] = []

    def add_force(self, force_func: Callable[[PhysicsState, float], np.ndarray]):
        """
        Add a force function to the simulation.

        Force function signature:
            (state: PhysicsState, t: float) -> np.ndarray (N, 3)

        Args:
            force_func: Function that computes forces given state and time
        """
        self.forces.append(force_func)

    def remove_force(self, force_func: Callable):
        """
        Remove a force function from the simulation.

        Args:
            force_func: Force function to remove
        """
        if force_func in self.forces:
            self.forces.remove(force_func)

    def add_constraint(self, constraint_func: Callable[[PhysicsState], PhysicsState]):
        """
        Add a constraint function to the simulation.

        Constraint function signature:
            (state: PhysicsState) -> PhysicsState

        Args:
            constraint_func: Function that modifies state (e.g., collision response)
        """
        self.constraints.append(constraint_func)

    def remove_constraint(self, constraint_func: Callable):
        """
        Remove a constraint function from the simulation.

        Args:
            constraint_func: Constraint function to remove
        """
        if constraint_func in self.constraints:
            self.constraints.remove(constraint_func)

    def step(self, state: PhysicsState, t: float) -> PhysicsState:
        """
        Advance simulation by one timestep using Verlet integration.

        Verlet integration is:
        - 2nd order accurate
        - Symplectic (energy conserving)
        - Stable for oscillatory systems

        Args:
            state: Current physics state
            t: Current simulation time

        Returns:
            Updated physics state
        """
        # Only simulate active particles
        active_mask = state.active

        if not np.any(active_mask):
            return state  # No active particles

        # Store previous position for motion blur
        state.prev_position[active_mask] = state.position[active_mask]

        # Compute net force from all force functions
        net_force = np.zeros_like(state.position)
        for force_func in self.forces:
            net_force += force_func(state, t)

        # Compute acceleration (F = ma)
        # Avoid division by zero
        mass_safe = np.where(state.mass > 0, state.mass, 1.0)
        state.acceleration = net_force / mass_safe[:, np.newaxis]

        # Verlet integration (velocity form)
        # v(t + dt/2) = v(t) + a(t) * dt/2
        half_vel = state.velocity + state.acceleration * (self.dt / 2)

        # x(t + dt) = x(t) + v(t + dt/2) * dt
        state.position = state.position + half_vel * self.dt

        # v(t + dt) = v(t + dt/2) + a(t) * dt/2
        # (This will be updated again in the next step, but we store for other uses)
        state.velocity = half_vel + state.acceleration * (self.dt / 2)

        # Apply constraints (collisions, boundaries, etc.)
        for constraint_func in self.constraints:
            state = constraint_func(state)

        # Update particle age
        state.age[active_mask] += self.dt

        return state

    def clear_forces(self):
        """Remove all force functions."""
        self.forces.clear()

    def clear_constraints(self):
        """Remove all constraint functions."""
        self.constraints.clear()

    def reset(self):
        """Clear all forces and constraints."""
        self.clear_forces()
        self.clear_constraints()


def create_particle_pool(max_particles: int, grid_shape: tuple) -> PhysicsState:
    """
    Create a particle pool for efficient particle management.

    Particles start inactive and can be activated by emitters.

    Args:
        max_particles: Maximum number of particles
        grid_shape: (length, height, width) of the volumetric grid

    Returns:
        PhysicsState with inactive particles
    """
    return PhysicsState(
        position=np.zeros((max_particles, 3), dtype=float),
        velocity=np.zeros((max_particles, 3), dtype=float),
        acceleration=np.zeros((max_particles, 3), dtype=float),
        mass=np.ones(max_particles, dtype=float),
        radius=np.ones(max_particles, dtype=float) * 1.5,
        active=np.zeros(max_particles, dtype=bool),
        age=np.zeros(max_particles, dtype=float),
        prev_position=np.zeros((max_particles, 3), dtype=float)
    )
