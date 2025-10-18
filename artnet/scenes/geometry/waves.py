"""
Wave Geometry Generators
Ripple, plane, standing, interference patterns
"""

import numpy as np


def generate_ripple_wave(coords, grid_shape, time, frequency=1.0, amplitude=0.5, speed=5, thickness=2):
    """
    Generate radial ripple wave from center.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        time: Animation time
        frequency: Wave frequency
        amplitude: Wave amplitude (0-1)
        speed: Wave propagation speed
        thickness: Wave surface thickness

    Returns:
        Boolean mask of wave voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    cx, cz = width / 2, length / 2

    # Create dense coordinates for calculation
    z = z_coords.squeeze() if hasattr(z_coords, 'squeeze') else z_coords
    y = y_coords.squeeze() if hasattr(y_coords, 'squeeze') else y_coords
    x = x_coords.squeeze() if hasattr(x_coords, 'squeeze') else x_coords

    # Broadcast to full grid
    zz, yy, xx = np.meshgrid(np.arange(length), np.arange(height), np.arange(width), indexing='ij')

    dx = xx - cx
    dz = zz - cz
    distance = np.sqrt(dx**2 + dz**2)

    wave = amplitude * height * 0.5 * np.sin(distance * frequency * 0.5 - time * speed)
    y_target = height / 2 + wave

    # Create mask for wave surface
    mask = np.abs(yy - y_target) < thickness

    return mask


def generate_plane_wave(coords, grid_shape, time, amplitude=0.4, speed=3, thickness=2):
    """
    Generate flat plane moving up and down.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        time: Animation time
        amplitude: Movement amplitude (0-1)
        speed: Movement speed
        thickness: Plane thickness

    Returns:
        Boolean mask of plane voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    y_target = height / 2 + amplitude * height * 0.4 * np.sin(time * speed)

    mask = np.zeros(z_coords.shape, dtype=bool)
    for y in range(height):
        if abs(y - y_target) < thickness:
            mask[:, y, :] = True

    return mask


def generate_standing_wave(coords, grid_shape, time, frequency=1.0, amplitude=0.5, thickness=2):
    """
    Generate standing wave pattern.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        time: Animation time
        frequency: Wave frequency
        amplitude: Wave amplitude (0-1)
        thickness: Wave surface thickness

    Returns:
        Boolean mask of standing wave voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    wave_x = np.sin(x_coords * frequency * 0.3)
    wave_z = np.sin(z_coords * frequency * 0.3)
    wave_t = np.sin(time * 3)

    y_offset = amplitude * height * 0.3 * wave_x * wave_z * wave_t
    y_target = height / 2 + y_offset

    mask = np.zeros(z_coords.shape, dtype=bool)
    for y in range(height):
        y_mask = np.abs(y - y_target) < thickness
        mask[:, y, :] |= y_mask[:, 0, :]

    return mask


def generate_interference_wave(coords, grid_shape, time, frequency=1.0, amplitude=0.5, speed=5):
    """
    Generate two-source interference pattern.
    Returns mask and intensity values for color mapping.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        time: Animation time
        frequency: Wave frequency
        amplitude: Wave amplitude (0-1)
        speed: Wave speed

    Returns:
        Tuple of (mask, intensity) where intensity is 0-1
    """
    z_coords, y_coords, x_coords = coords

    wave1 = np.sin(x_coords * frequency + time * speed)
    wave2 = np.sin(z_coords * frequency - time * speed)
    combined = (wave1 + wave2) / 2

    # Create intensity field
    intensity = (combined * amplitude + 1) / 2  # Normalize to 0-1

    # Threshold for mask
    mask = intensity > 0.3

    return mask, intensity
