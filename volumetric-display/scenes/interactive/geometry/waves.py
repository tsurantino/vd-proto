"""
Wave Geometry Generators
Ripple, plane, standing, interference patterns
"""

import numpy as np


def generate_ripple_wave(coords, grid_shape, time, frequency=1.0, amplitude=0.5, speed=5, thickness=2):
    """
    Generate radial ripple wave from center.
    Ripples in XY plane, wave extends along Z axis (vertical).

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

    cx, cy = width / 2, height / 2

    # Broadcast to full grid
    zz, yy, xx = np.meshgrid(np.arange(length), np.arange(height), np.arange(width), indexing='ij')

    # Calculate distance in XY plane
    dx = xx - cx
    dy = yy - cy
    distance = np.sqrt(dx**2 + dy**2)

    # Wave modulates along Z axis
    wave = amplitude * length * 0.5 * np.sin(distance * frequency * 0.5 - time * speed)
    z_target = length / 2 + wave

    # Create mask for wave surface
    mask = np.abs(zz - z_target) < thickness

    return mask


def generate_plane_wave(coords, grid_shape, time, amplitude=0.4, speed=3, direction='x', frequency=1.0):
    """
    Generate directional sweeping plane wave.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        time: Animation time
        amplitude: Wave amplitude (controls thickness)
        speed: Wave speed
        direction: Direction of wave ('x', 'y', 'z', 'diagonal', 'radial')
        frequency: Wave frequency

    Returns:
        Boolean mask of plane voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    # Create full meshgrid for calculations
    zz, yy, xx = np.meshgrid(np.arange(length), np.arange(height), np.arange(width), indexing='ij')

    # Direction functions
    if direction == 'x':
        pos = xx
    elif direction == 'y':
        pos = yy
    elif direction == 'z':
        pos = zz
    elif direction == 'diagonal':
        pos = xx + zz
    elif direction == 'radial':
        cx, cz = width / 2, length / 2
        dx = xx - cx
        dz = zz - cz
        pos = np.sqrt(dx**2 + dz**2)
    else:
        pos = xx

    # Sweeping position based on time
    progress = (np.sin(time * 0.5) + 1) / 2
    sweep_pos = progress * (width + height + length)

    # Thickness based on amplitude
    thickness = 3 + amplitude * 4

    # Create mask where position is within thickness of sweep
    mask = np.abs(pos - sweep_pos * frequency) < thickness

    return mask


def generate_standing_wave(coords, grid_shape, time, frequency=1.0, amplitude=0.5):
    """
    Generate standing wave pattern filling Z columns (vertical).

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        time: Animation time
        frequency: Wave frequency
        amplitude: Wave amplitude (0-1)

    Returns:
        Boolean mask of standing wave voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    # Calculate standing wave pattern in XY plane
    freq = 0.3 * frequency
    time_sin = np.sin(time)
    threshold = 0.5

    # Create a full grid for the XY pattern
    mask = np.zeros(grid_shape, dtype=bool)

    # Calculate pattern for each XY position
    for y in range(height):
        for x in range(width):
            wave_x = np.sin(x * freq)
            wave_y = np.sin(y * freq)
            wave = wave_x * wave_y * time_sin
            value = (wave + 1) * 0.5 * amplitude

            # If this XY position is active, fill entire Z column (vertical)
            if value > threshold:
                mask[:, y, x] = True

    return mask


def generate_interference_wave(coords, grid_shape, time, frequency=1.0, amplitude=0.5, speed=5):
    """
    Generate two-source interference pattern.
    Creates ripples from two sources in XY plane that interfere, wave extends along Z (vertical).

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
    length, height, width = grid_shape

    # Two wave sources at (30%, 30%) and (70%, 70%) in XY plane
    source1_x = width * 0.3
    source1_y = height * 0.3
    source2_x = width * 0.7
    source2_y = height * 0.7

    # Create full meshgrid
    zz, yy, xx = np.meshgrid(np.arange(length), np.arange(height), np.arange(width), indexing='ij')

    # Calculate distance from each point to each source in XY plane
    dx1 = xx - source1_x
    dy1 = yy - source1_y
    dist1 = np.sqrt(dx1**2 + dy1**2)

    dx2 = xx - source2_x
    dy2 = yy - source2_y
    dist2 = np.sqrt(dx2**2 + dy2**2)

    # Wave parameters
    freq = 0.3 * frequency
    time_phase = time * 2
    wave_amplitude = 2 + amplitude * 3
    threshold = 1.5

    # Calculate waves from each source
    wave1 = np.sin(dist1 * freq - time_phase)
    wave2 = np.sin(dist2 * freq - time_phase)
    total_wave = (wave1 + wave2) / 2

    # Calculate Z position for wave surface (vertical modulation)
    z_pos = length / 2 + total_wave * wave_amplitude

    # Create mask for wave surface
    mask = np.abs(zz - z_pos) < threshold

    # Create intensity field for color mapping
    intensity = (total_wave + 1) / 2

    return mask, intensity
