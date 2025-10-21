"""
Physics Constraint Functions

Constraint functions modify particle state to enforce physical rules:
- boundary_collision: Bounce particles off walls
- boundary_wrap: Wrap particles around edges (toroidal)
- particle_particle_collision: Handle particle-particle collisions
"""

import numpy as np
from .engine import PhysicsState
from collections import defaultdict


def boundary_collision(bounds_min: np.ndarray, bounds_max: np.ndarray, restitution: float = 0.8):
    """
    Create boundary collision constraint with bounce.

    Particles that hit walls reverse velocity (with energy loss).

    Args:
        bounds_min: (3,) minimum XYZ bounds
        bounds_max: (3,) maximum XYZ bounds
        restitution: Coefficient of restitution (0=inelastic, 1=elastic)
            0.8 = bouncy (typical)
            0.3 = soft landing
            1.0 = perfectly elastic (no energy loss)

    Returns:
        Constraint function: (state) -> state

    Example:
        # Bouncy walls
        engine.add_constraint(boundary_collision(
            bounds_min=[0, 0, 0],
            bounds_max=[16, 16, 16],
            restitution=0.9
        ))
    """
    bounds_min = np.array(bounds_min, dtype=float)
    bounds_max = np.array(bounds_max, dtype=float)

    def constraint_func(state: PhysicsState) -> PhysicsState:
        # Only process active particles
        active_mask = state.active

        for axis in range(3):
            # Check lower bound
            below_min = active_mask & (state.position[:, axis] < bounds_min[axis])
            if np.any(below_min):
                state.position[below_min, axis] = bounds_min[axis]
                state.velocity[below_min, axis] *= -restitution

            # Check upper bound
            above_max = active_mask & (state.position[:, axis] > bounds_max[axis])
            if np.any(above_max):
                state.position[above_max, axis] = bounds_max[axis]
                state.velocity[above_max, axis] *= -restitution

        return state

    constraint_func.__name__ = 'boundary_collision'
    return constraint_func


def boundary_wrap(bounds_min: np.ndarray, bounds_max: np.ndarray):
    """
    Create boundary wrap constraint (toroidal topology).

    Particles that exit one edge appear at the opposite edge.
    Creates illusion of infinite space.

    Args:
        bounds_min: (3,) minimum XYZ bounds
        bounds_max: (3,) maximum XYZ bounds

    Returns:
        Constraint function: (state) -> state

    Example:
        # Wrap-around boundaries (pac-man style)
        engine.add_constraint(boundary_wrap(
            bounds_min=[0, 0, 0],
            bounds_max=[16, 16, 16]
        ))
    """
    bounds_min = np.array(bounds_min, dtype=float)
    bounds_max = np.array(bounds_max, dtype=float)
    bounds_size = bounds_max - bounds_min

    def constraint_func(state: PhysicsState) -> PhysicsState:
        # Only process active particles
        active_mask = state.active

        for axis in range(3):
            # Wrap particles that go below min
            below_min = active_mask & (state.position[:, axis] < bounds_min[axis])
            if np.any(below_min):
                state.position[below_min, axis] += bounds_size[axis]

            # Wrap particles that go above max
            above_max = active_mask & (state.position[:, axis] > bounds_max[axis])
            if np.any(above_max):
                state.position[above_max, axis] -= bounds_size[axis]

        return state

    constraint_func.__name__ = 'boundary_wrap'
    return constraint_func


def particle_particle_collision(enabled: bool = True, restitution: float = 0.7, spatial_hash: bool = True):
    """
    Detect and resolve particle-particle collisions.

    Uses spatial hashing for performance with many particles.
    Collision detection is O(N) with spatial hash vs O(N^2) naive.

    Args:
        enabled: Whether collision detection is active
        restitution: Bounce coefficient (0-1)
        spatial_hash: Use spatial hashing optimization (recommended for >100 particles)

    Returns:
        Constraint function: (state) -> state

    Example:
        # Enable particle collisions
        engine.add_constraint(particle_particle_collision(
            enabled=True,
            restitution=0.8
        ))

        # Disable (no-op)
        engine.add_constraint(particle_particle_collision(enabled=False))
    """
    if not enabled:
        # Return no-op function
        def noop(state: PhysicsState) -> PhysicsState:
            return state
        noop.__name__ = 'particle_particle_collision_disabled'
        return noop

    if spatial_hash:
        return _particle_collision_spatial_hash(restitution)
    else:
        return _particle_collision_naive(restitution)


def _particle_collision_naive(restitution: float):
    """Naive O(N^2) particle collision detection."""

    def constraint_func(state: PhysicsState) -> PhysicsState:
        active_indices = np.where(state.active)[0]
        n = len(active_indices)

        if n < 2:
            return state  # Need at least 2 particles

        # Compute pairwise distances (vectorized)
        positions = state.position[active_indices]
        radii = state.radius[active_indices]

        # Broadcasting: (N, 1, 3) - (1, N, 3) = (N, N, 3)
        diff = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
        distances = np.linalg.norm(diff, axis=2)

        # Sum of radii for each pair
        radii_sum = radii[:, np.newaxis] + radii[np.newaxis, :]

        # Find colliding pairs (distance < sum of radii, exclude self-collision)
        colliding = (distances < radii_sum) & (distances > 0)

        # For each colliding pair, resolve collision
        i_indices, j_indices = np.where(colliding)

        for idx in range(len(i_indices)):
            i_local = i_indices[idx]
            j_local = j_indices[idx]

            if i_local >= j_local:  # Only process each pair once
                continue

            i = active_indices[i_local]
            j = active_indices[j_local]

            # Collision normal (from i to j)
            normal = diff[i_local, j_local] / distances[i_local, j_local]

            # Relative velocity
            rel_vel = state.velocity[j] - state.velocity[i]

            # Velocity along normal
            vel_normal = np.dot(rel_vel, normal)

            # Only resolve if moving toward each other
            if vel_normal < 0:
                # Impulse magnitude (simplified elastic collision)
                impulse = -(1 + restitution) * vel_normal / (1/state.mass[i] + 1/state.mass[j])

                # Apply impulse
                state.velocity[i] -= impulse * normal / state.mass[i]
                state.velocity[j] += impulse * normal / state.mass[j]

                # Separate overlapping particles
                overlap = radii_sum[i_local, j_local] - distances[i_local, j_local]
                separation = normal * overlap / 2
                state.position[i] -= separation
                state.position[j] += separation

        return state

    constraint_func.__name__ = 'particle_particle_collision'
    return constraint_func


def _particle_collision_spatial_hash(restitution: float):
    """
    Spatial hash grid collision detection (O(N) average case).

    Divides space into cells and only checks collisions within
    same cell + neighboring cells.
    """

    def constraint_func(state: PhysicsState) -> PhysicsState:
        active_indices = np.where(state.active)[0]
        n = len(active_indices)

        if n < 2:
            return state

        # Determine cell size (use max particle radius * 2)
        max_radius = np.max(state.radius[active_indices])
        cell_size = max_radius * 2.5

        # Build spatial hash grid
        # Key: (cell_x, cell_y, cell_z), Value: list of particle indices
        hash_grid = defaultdict(list)

        for idx in active_indices:
            pos = state.position[idx]
            cell = tuple((pos / cell_size).astype(int))
            hash_grid[cell].append(idx)

        # Check collisions within each cell and neighbors
        checked_pairs = set()

        for cell, particles in hash_grid.items():
            # Get neighboring cells (3x3x3 = 27 cells including self)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        neighbor_cell = (cell[0] + dx, cell[1] + dy, cell[2] + dz)
                        if neighbor_cell not in hash_grid:
                            continue

                        neighbor_particles = hash_grid[neighbor_cell]

                        # Check all pairs between cell and neighbor
                        for i in particles:
                            for j in neighbor_particles:
                                if i >= j:  # Only check each pair once
                                    continue

                                pair = (i, j)
                                if pair in checked_pairs:
                                    continue
                                checked_pairs.add(pair)

                                # Check collision
                                diff = state.position[j] - state.position[i]
                                distance = np.linalg.norm(diff)
                                radii_sum = state.radius[i] + state.radius[j]

                                if distance < radii_sum and distance > 0:
                                    # Collision detected - resolve
                                    normal = diff / distance

                                    # Relative velocity
                                    rel_vel = state.velocity[j] - state.velocity[i]
                                    vel_normal = np.dot(rel_vel, normal)

                                    # Only resolve if moving toward each other
                                    if vel_normal < 0:
                                        # Impulse
                                        impulse = -(1 + restitution) * vel_normal / \
                                                 (1/state.mass[i] + 1/state.mass[j])

                                        # Apply impulse
                                        state.velocity[i] -= impulse * normal / state.mass[i]
                                        state.velocity[j] += impulse * normal / state.mass[j]

                                        # Separate overlapping particles
                                        overlap = radii_sum - distance
                                        separation = normal * overlap / 2
                                        state.position[i] -= separation
                                        state.position[j] += separation

        return state

    constraint_func.__name__ = 'particle_particle_collision_spatial_hash'
    return constraint_func


def sphere_collision(center: np.ndarray, radius: float, restitution: float = 0.9, inside: bool = False):
    """
    Create collision with spherical boundary.

    Can be used for either:
    - Containing particles inside a sphere (inside=True)
    - Keeping particles outside a sphere (inside=False)

    Args:
        center: (3,) sphere center
        radius: Sphere radius
        restitution: Bounce coefficient
        inside: If True, keep particles inside sphere. If False, keep outside.

    Returns:
        Constraint function: (state) -> state

    Example:
        # Particles bounce inside a sphere
        engine.add_constraint(sphere_collision(
            center=[8, 8, 8],
            radius=7.0,
            inside=True
        ))

        # Particles bounce off a solid sphere
        engine.add_constraint(sphere_collision(
            center=[8, 8, 8],
            radius=3.0,
            inside=False
        ))
    """
    center = np.array(center, dtype=float)

    def constraint_func(state: PhysicsState) -> PhysicsState:
        active_mask = state.active

        # Vector from center to particle
        r_vec = state.position - center
        r_mag = np.linalg.norm(r_vec, axis=1, keepdims=True)

        if inside:
            # Particles outside sphere (should be inside)
            outside = active_mask & (r_mag.squeeze() > radius)
        else:
            # Particles inside sphere (should be outside)
            outside = active_mask & (r_mag.squeeze() < radius)

        if np.any(outside):
            # Normal vector at collision point
            normal = r_vec[outside] / r_mag[outside]

            if inside:
                # Project position back onto sphere surface (from outside)
                state.position[outside] = center + normal * radius
            else:
                # Push position away from sphere center (from inside)
                state.position[outside] = center + normal * radius

            # Reflect velocity (v' = v - 2(v·n)n) * restitution
            v_dot_n = np.sum(state.velocity[outside] * normal, axis=1, keepdims=True)
            state.velocity[outside] = (state.velocity[outside] - 2 * v_dot_n * normal) * restitution

        return state

    constraint_func.__name__ = 'sphere_collision'
    return constraint_func
