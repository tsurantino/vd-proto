"""
Procedural Geometry Generators
Noise, clouds, cellular, and fractal patterns
"""

import numpy as np


def generate_noise(coords, grid_shape, params, time, center, angles=None):
    """
    Multi-octave sine-based noise pattern.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays (potentially rotated)
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, amplitude, scaling_amount, scaling_speed
        time: Animation time
        center: Tuple of (cx, cy, cz) for rotation center
        angles: Optional tuple of (angle_x, angle_y, angle_z) if rotation already applied

    Returns:
        Boolean mask of noise voxels
    """
    z_coords, y_coords, x_coords = coords

    # Apply pulsing/scaling effect to pattern scale
    pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(time * params.scaling_speed)
    scale = params.size * 0.1 * pulse
    threshold = params.amplitude * 0.5

    # Base noise
    noise = (
        np.sin(x_coords * scale + time) *
        np.cos(y_coords * scale - time * 0.5) *
        np.sin(z_coords * scale + time * 0.3)
    )

    # Second octave
    noise += 0.5 * (
        np.sin(x_coords * scale * 2 - time * 1.5) *
        np.cos(z_coords * scale * 2 + time)
    )

    noise = (noise + 1.5) / 3.0
    return noise > threshold


def generate_clouds(coords, grid_shape, params, time, center, angles=None):
    """
    Volumetric cloud-like patterns with soft billowing.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays (potentially rotated)
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, amplitude, scaling_amount, scaling_speed
        time: Animation time
        center: Tuple of (cx, cy, cz) for rotation center
        angles: Optional tuple of (angle_x, angle_y, angle_z) if rotation already applied

    Returns:
        Boolean mask of cloud voxels
    """
    z_coords, y_coords, x_coords = coords

    # Apply pulsing/scaling effect to pattern frequency
    pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(time * params.scaling_speed)
    freq = 0.15 * params.size * pulse

    # Multiple octaves for cloud-like appearance
    # Octave 1: Large features
    cloud = np.sin(x_coords * freq + time * 0.3) * \
            np.cos(y_coords * freq + time * 0.2) * \
            np.sin(z_coords * freq - time * 0.15)

    # Octave 2: Medium features
    cloud += 0.5 * (
        np.sin(x_coords * freq * 2.3 - time * 0.5) *
        np.cos(y_coords * freq * 1.8 + time * 0.3) *
        np.sin(z_coords * freq * 2.1 + time * 0.25)
    )

    # Octave 3: Fine details
    cloud += 0.25 * (
        np.sin(x_coords * freq * 4.7 + time * 0.8) *
        np.cos(y_coords * freq * 4.2 - time * 0.6) *
        np.sin(z_coords * freq * 4.5 + time * 0.7)
    )

    # Density controls how much cloud coverage
    # Amplitude controls the threshold (more = denser clouds)
    threshold = -0.5 + (1 - params.density) * 1.5 - params.amplitude * 0.5

    return cloud > threshold


def generate_cellular(coords, grid_shape, params, time):
    """
    Cellular/Voronoi-like pattern with animated cells.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, amplitude
        time: Animation time

    Returns:
        Boolean mask of cellular voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    # Number of cell centers based on density (ensure minimum of 3 cells)
    num_cells = max(3, int(5 + params.density * 15))  # 5-20 cells

    # Size controls cell size (ensure minimum scale to prevent empty grid)
    cell_scale = 1.0 / max(0.3, params.size + 0.1)

    mask = np.zeros(grid_shape, dtype=bool)

    # Generate pseudo-random cell centers that move over time
    np.random.seed(42)  # Fixed seed for consistent cells

    for i in range(num_cells):
        # Base position
        cx = np.random.uniform(0, width)
        cy = np.random.uniform(0, height)
        cz = np.random.uniform(0, length)

        # Animate cell centers in orbital patterns
        angle = time * 0.5 + i * np.pi * 2 / num_cells
        orbit_radius = 3 + i % 5

        cx = (cx + np.cos(angle) * orbit_radius) % width
        cy = (cy + np.sin(angle * 0.7) * orbit_radius) % height
        cz = (cz + np.sin(angle * 0.5) * orbit_radius) % length

        # Distance from cell center
        dx = x_coords - cx
        dy = y_coords - cy
        dz = z_coords - cz
        distance = np.sqrt(dx**2 + dy**2 + dz**2)

        # Amplitude controls cell wall thickness
        cell_radius = 8 * cell_scale
        wall_thickness = 1.5 + params.amplitude * 3

        # Create cell walls (hollow spheres)
        mask |= (distance < cell_radius) & (distance > (cell_radius - wall_thickness))

    return mask


def generate_fractals(coords, grid_shape, params, time, center, angles=None):
    """
    Fractal-like recursive patterns with self-similarity.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays (potentially rotated)
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, amplitude, scaling_amount, scaling_speed
        time: Animation time
        center: Tuple of (cx, cy, cz) for rotation center
        angles: Optional tuple of (angle_x, angle_y, angle_z) if rotation already applied

    Returns:
        Boolean mask of fractal voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    # Normalize coordinates to center
    nx = (x_coords - center[0]) / width
    ny = (y_coords - center[1]) / height
    nz = (z_coords - center[2]) / length

    # Apply pulsing/scaling effect to pattern scale
    pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(time * params.scaling_speed)
    scale = params.size * 3 * pulse

    # Create a 3D fractal pattern using recursive sine functions
    # Each iteration adds smaller details
    fractal = np.zeros(grid_shape, dtype=np.float32)

    # Density controls number of iterations (detail level)
    iterations = 2 + int(params.density * 4)  # 2-6 iterations

    amplitude = 1.0
    frequency = 1.0

    for i in range(iterations):
        # Add rotated pattern at each scale
        angle = time * 0.5 + i * np.pi / 3

        fractal += amplitude * (
            np.sin((nx * np.cos(angle) - nz * np.sin(angle)) * frequency * scale + time) *
            np.cos(ny * frequency * scale - time * 0.3) *
            np.sin((nx * np.sin(angle) + nz * np.cos(angle)) * frequency * scale + time * 0.5)
        )

        # Reduce amplitude and increase frequency for next octave
        amplitude *= 0.5
        frequency *= 2.3

    # Amplitude parameter controls threshold
    threshold = -0.5 + (1 - params.amplitude) * 1.0

    return fractal > threshold
