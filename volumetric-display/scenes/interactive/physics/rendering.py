"""
Particle Rendering

Convert particle positions to voxel masks with various rendering modes:
- Point: Single voxel per particle
- Sphere: Small sphere around position
- Motion blur: Draw line from previous position
"""

import numpy as np
from .engine import PhysicsState


def particles_to_voxels(state: PhysicsState, grid_shape: tuple,
                        render_mode: str = 'sphere',
                        motion_blur: bool = False) -> np.ndarray:
    """
    Convert particle positions to voxel boolean mask.

    Args:
        state: PhysicsState with particle data
        grid_shape: (length, height, width) of voxel grid
        render_mode: 'point' or 'sphere'
            'point' - single voxel per particle (fastest)
            'sphere' - small sphere using state.radius (more visible)
        motion_blur: If True, draw line from prev_position to position

    Returns:
        Boolean mask array of shape grid_shape

    Example:
        # Render particles as spheres with motion blur
        mask = particles_to_voxels(
            state,
            grid_shape=(16, 16, 16),
            render_mode='sphere',
            motion_blur=True
        )
    """
    mask = np.zeros(grid_shape, dtype=bool)
    active_indices = np.where(state.active)[0]

    if len(active_indices) == 0:
        return mask

    for i in active_indices:
        pos = state.position[i]

        # Render particle at current position
        if render_mode == 'sphere':
            mask |= draw_sphere(pos, state.radius[i], grid_shape)
        else:  # 'point'
            voxel = np.round(pos).astype(int)
            if in_bounds(voxel, grid_shape):
                mask[tuple(voxel)] = True

        # Add motion blur trail
        if motion_blur:
            prev_pos = state.prev_position[i]
            # Only draw trail if particle moved significantly
            movement = np.linalg.norm(pos - prev_pos)
            if movement > 0.1:  # Lowered threshold for more visible trails
                mask |= draw_line_3d(prev_pos, pos, grid_shape)

    return mask


def draw_sphere(center: np.ndarray, radius: float, grid_shape: tuple) -> np.ndarray:
    """
    Draw a filled sphere in voxel space.

    Uses efficient bounding box approach to avoid checking all voxels.

    Args:
        center: (3,) center position (continuous coordinates)
        radius: Sphere radius in voxels
        grid_shape: (length, height, width) of grid

    Returns:
        Boolean mask with sphere voxels set to True

    Example:
        sphere_mask = draw_sphere(
            center=[8.5, 8.5, 8.5],
            radius=2.0,
            grid_shape=(16, 16, 16)
        )
    """
    mask = np.zeros(grid_shape, dtype=bool)

    # Bounding box (clipped to grid)
    min_bounds = np.maximum(np.floor(center - radius).astype(int), [0, 0, 0])
    max_bounds = np.minimum(np.ceil(center + radius).astype(int), grid_shape)

    # Check bounds validity
    if np.any(min_bounds >= max_bounds):
        return mask

    # Create coordinate grids for bounding box
    z_range = np.arange(min_bounds[0], max_bounds[0])
    y_range = np.arange(min_bounds[1], max_bounds[1])
    x_range = np.arange(min_bounds[2], max_bounds[2])

    if len(z_range) == 0 or len(y_range) == 0 or len(x_range) == 0:
        return mask

    # Create meshgrid
    zz, yy, xx = np.meshgrid(z_range, y_range, x_range, indexing='ij')

    # Distance from center
    dist = np.sqrt((xx - center[2])**2 +
                   (yy - center[1])**2 +
                   (zz - center[0])**2)

    # Voxels within radius
    sphere_voxels = dist <= radius

    # Set mask
    mask[min_bounds[0]:max_bounds[0],
         min_bounds[1]:max_bounds[1],
         min_bounds[2]:max_bounds[2]] = sphere_voxels

    return mask


def draw_line_3d(p0: np.ndarray, p1: np.ndarray, grid_shape: tuple) -> np.ndarray:
    """
    Draw a line between two points in 3D voxel space.

    Uses 3D Bresenham-style algorithm for efficient line rasterization.

    Args:
        p0: (3,) start position (continuous coordinates)
        p1: (3,) end position (continuous coordinates)
        grid_shape: (length, height, width) of grid

    Returns:
        Boolean mask with line voxels set to True

    Example:
        # Draw motion blur trail
        trail_mask = draw_line_3d(
            p0=[5.2, 5.8, 5.1],
            p1=[6.7, 7.3, 6.9],
            grid_shape=(16, 16, 16)
        )
    """
    mask = np.zeros(grid_shape, dtype=bool)

    # Convert to integer voxel coordinates
    p0_int = np.round(p0).astype(int)
    p1_int = np.round(p1).astype(int)

    # Check if start/end are in bounds
    if not in_bounds(p0_int, grid_shape) and not in_bounds(p1_int, grid_shape):
        return mask  # Both out of bounds

    # 3D DDA (Digital Differential Analyzer) algorithm
    delta = p1 - p0
    distance = np.linalg.norm(delta)

    if distance < 0.5:
        # Very short line, just set start point
        if in_bounds(p0_int, grid_shape):
            mask[tuple(p0_int)] = True
        return mask

    # Number of steps (at least as many as the longest axis)
    num_steps = int(np.ceil(distance * 2))  # Oversample for smooth line
    num_steps = max(num_steps, 2)

    # Interpolate positions
    t_values = np.linspace(0, 1, num_steps)
    positions = p0 + t_values[:, np.newaxis] * delta

    # Round to voxel coordinates
    voxel_positions = np.round(positions).astype(int)

    # Set all in-bounds voxels
    for voxel in voxel_positions:
        if in_bounds(voxel, grid_shape):
            mask[tuple(voxel)] = True

    return mask


def in_bounds(voxel: np.ndarray, grid_shape: tuple) -> bool:
    """
    Check if a voxel coordinate is within grid bounds.

    Args:
        voxel: (3,) voxel coordinate (z, y, x) as integers
        grid_shape: (length, height, width) of grid

    Returns:
        True if voxel is in bounds, False otherwise

    Example:
        if in_bounds([5, 7, 3], (16, 16, 16)):
            # Safe to access grid[5, 7, 3]
    """
    return (0 <= voxel[0] < grid_shape[0] and
            0 <= voxel[1] < grid_shape[1] and
            0 <= voxel[2] < grid_shape[2])


def draw_particles_with_trails(state: PhysicsState, grid_shape: tuple,
                                trail_length: int = 5) -> np.ndarray:
    """
    Advanced rendering: draw particles with persistent trails.

    Maintains a history of positions to create comet-like trails.
    Note: Requires state to maintain position history (not in base PhysicsState).

    Args:
        state: PhysicsState with particle data
        grid_shape: (length, height, width)
        trail_length: Number of previous positions to render

    Returns:
        Boolean mask with particles and trails

    Example:
        # This would require extending PhysicsState with position_history
        # mask = draw_particles_with_trails(state, (16, 16, 16), trail_length=8)
    """
    # This is a more advanced feature that would require
    # PhysicsState to maintain a position history buffer
    # For now, we'll use the simpler motion blur approach
    return particles_to_voxels(state, grid_shape, render_mode='sphere', motion_blur=True)
