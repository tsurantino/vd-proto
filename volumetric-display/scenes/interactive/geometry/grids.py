"""
Grid Geometry Generators
Full volume, dots, cross, and wireframe patterns
"""

import numpy as np
from .shapes import generate_cross_grid


def generate_full(grid_shape):
    """
    Full volume - all voxels lit.

    Args:
        grid_shape: Tuple of (length, height, width)

    Returns:
        Boolean mask of all voxels (fully lit)
    """
    return np.ones(grid_shape, dtype=bool)


def generate_dots(coords, grid_shape, params, time):
    """
    Grid of dots/points at intersections - optimized vectorized version.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, scaling_amount, scaling_speed
        time: Animation time

    Returns:
        Boolean mask of dot grid voxels
    """
    z_coords, y_coords, x_coords = coords

    # Density controls dot spacing
    spacing = max(2, int(8 - params.density * 6))  # 2-8 voxels apart

    # Apply pulsing/scaling effect to dot size
    pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(time * params.scaling_speed)
    dot_radius = (0.5 + params.size * 2) * pulse  # 0.5-2.5 voxels

    # Use modulo to create repeating pattern instead of loops
    # This is much faster than iterating through each dot position

    # For each axis, find the distance to the nearest grid line
    x_dist_to_grid = np.minimum(x_coords % spacing, spacing - (x_coords % spacing))
    y_dist_to_grid = np.minimum(y_coords % spacing, spacing - (y_coords % spacing))
    z_dist_to_grid = np.minimum(z_coords % spacing, spacing - (z_coords % spacing))

    # Distance from nearest grid intersection point (3D)
    distance = np.sqrt(x_dist_to_grid**2 + y_dist_to_grid**2 + z_dist_to_grid**2)

    # Create mask where distance is less than dot radius
    mask = distance < dot_radius

    return mask


def generate_cross(coords, grid_shape, params, time, center):
    """
    Cross pattern through center with adjustable thickness.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, scaling_amount, scaling_speed
        time: Animation time
        center: Tuple of (cx, cy, cz)

    Returns:
        Boolean mask of cross pattern voxels
    """
    # Apply size parameter and pulsing/scaling effect to cross size
    # params.size controls base size (0-3 range, typically around 1-2)
    base_size = min(center) * (0.3 + params.size * 0.6)  # Scale from 30% to 90% of display
    pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(time * params.scaling_speed)
    size = base_size * pulse
    # Use density to control cross line thickness (1-10 pixels)
    line_thickness = 1 + params.density * 9
    return generate_cross_grid(coords, center, size, line_thickness)


def generate_wireframe(coords, grid_shape, params, time):
    """
    Wireframe cube/box edges only.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, scaling_amount, scaling_speed, rotationX, rotationY, rotationZ, animationSpeed
        time: Animation time

    Returns:
        Boolean mask of wireframe voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    # Apply pulsing/scaling effect to box size
    pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(time * params.scaling_speed)
    size_factor = (0.3 + params.size * 0.65) * pulse

    # Density controls edge thickness
    thickness = max(1, int(1 + params.density * 3))

    # Calculate box boundaries with clamping
    x_min = max(0, int(width * (1 - size_factor) / 2))
    x_max = min(width, int(width * (1 + size_factor) / 2))
    y_min = max(0, int(height * (1 - size_factor) / 2))
    y_max = min(height, int(height * (1 + size_factor) / 2))
    z_min = max(0, int(length * (1 - size_factor) / 2))
    z_max = min(length, int(length * (1 + size_factor) / 2))

    mask = np.zeros(grid_shape, dtype=bool)

    # Draw 12 edges of the cube
    # Bottom face (4 edges)
    mask[z_min:z_min+thickness, y_min:y_min+thickness, x_min:x_max] = True  # Bottom-front edge
    mask[z_min:z_min+thickness, y_max-thickness:y_max, x_min:x_max] = True  # Bottom-back edge
    mask[z_min:z_min+thickness, y_min:y_max, x_min:x_min+thickness] = True  # Bottom-left edge
    mask[z_min:z_min+thickness, y_min:y_max, x_max-thickness:x_max] = True  # Bottom-right edge

    # Top face (4 edges)
    mask[z_max-thickness:z_max, y_min:y_min+thickness, x_min:x_max] = True  # Top-front edge
    mask[z_max-thickness:z_max, y_max-thickness:y_max, x_min:x_max] = True  # Top-back edge
    mask[z_max-thickness:z_max, y_min:y_max, x_min:x_min+thickness] = True  # Top-left edge
    mask[z_max-thickness:z_max, y_min:y_max, x_max-thickness:x_max] = True  # Top-right edge

    # Vertical edges (4 edges)
    mask[z_min:z_max, y_min:y_min+thickness, x_min:x_min+thickness] = True  # Front-left edge
    mask[z_min:z_max, y_min:y_min+thickness, x_max-thickness:x_max] = True  # Front-right edge
    mask[z_min:z_max, y_max-thickness:y_max, x_min:x_min+thickness] = True  # Back-left edge
    mask[z_min:z_max, y_max-thickness:y_max, x_max-thickness:x_max] = True  # Back-right edge

    # Note: Rotation animation would require transforming the wireframe geometry,
    # which is complex. The current version creates a static rotated box.
    # For true rotation, the scene class should apply rotation to coordinates first.

    return mask
