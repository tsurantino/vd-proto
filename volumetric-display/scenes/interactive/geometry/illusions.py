"""
Optical Illusion Geometry Generators
Infinite corridor, waterfall, pulfrich, and moire patterns
"""

import numpy as np


def generate_infinite_corridor(coords, grid_shape, params, time):
    """
    Infinite corridor - scrolling perspective frames along Y axis (vertical).

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density
        time: Animation time

    Returns:
        Boolean mask of corridor voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    # Parameters
    frame_spacing = max(3, int(4 * (1 + params.density)))
    num_frames = int(5 + params.size * 5)

    # Continuous scroll offset (no wrapping at this level)
    scroll_offset = time * 3

    mask = np.zeros(grid_shape, dtype=bool)

    # Collect all frame data first so we can sort by depth
    frames_to_draw = []

    # Generate enough frames to fill the visible area plus wrapping buffer
    for frame in range(num_frames * 2):  # Double to handle wrapping
        # Position along Y axis (height) - scrolling upward
        base_y = (frame * frame_spacing - scroll_offset) % (frame_spacing * num_frames)
        y = int(base_y) % height

        # Skip if this frame is outside visible range
        if y < 0 or y >= height:
            continue

        # Calculate perspective scale based on continuous position (before wrapping)
        # Use the continuous base_y for smooth perspective transitions
        # Map to [0, 1] range across the full loop cycle
        normalized_pos = (base_y % (frame_spacing * num_frames)) / (frame_spacing * num_frames)
        scale = 0.2 + normalized_pos * 0.8 * params.size

        # Frame dimensions in XZ plane
        frame_width = max(1, int(width / 2 * scale))
        depth = max(1, int(length / 2 * scale))

        # Store frame data (scale is our depth key - smaller = farther)
        frames_to_draw.append((scale, y, frame_width, depth))

    # Sort frames by scale (smallest/farthest first, largest/nearest last)
    # This ensures proper depth ordering - distant frames drawn first, near frames on top
    frames_to_draw.sort(key=lambda f: f[0])

    # Now draw frames in back-to-front order
    center_x = width // 2
    center_z = length // 2

    for scale, y, frame_width, depth in frames_to_draw:
        # Draw all four edges of the rectangle
        # Top and bottom edges (parallel to X axis)
        for x in range(-frame_width, frame_width + 1):
            for offset_z in [-depth, depth]:
                wz = center_z + offset_z
                wx = center_x + x
                if 0 <= wx < width and 0 <= wz < length:
                    mask[wz, y, wx] = True

        # Left and right edges (parallel to Z axis)
        for z in range(-depth, depth + 1):
            for offset_x in [-frame_width, frame_width]:
                wx = center_x + offset_x
                wz = center_z + z
                if 0 <= wx < width and 0 <= wz < length:
                    mask[wz, y, wx] = True

    return mask


def generate_waterfall(coords, grid_shape, params, time):
    """
    Waterfall illusion - moving vertical stripes.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with density
        time: Animation time

    Returns:
        Boolean mask of waterfall voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    offset = time * 10
    stripe_spacing = max(2, int(5 - params.density * 3))

    mask = np.zeros(grid_shape, dtype=bool)

    # Create moving stripes pattern along Z axis
    for z in range(length):
        pattern = (z + offset) % (stripe_spacing * 2)
        is_stripe = pattern < stripe_spacing

        if is_stripe:
            # Fill this Z slice
            mask[z, :, :] = True

    # Add horizontal marker lines every 5 units in Y
    # These create the reference frame that makes the illusion work
    for y in range(0, height, 5):
        mask[:, y, :] = True

    return mask


def generate_pulfrich(coords, grid_shape, params, time):
    """
    Pulfrich effect - rotating objects with brightness variation in XY plane.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density
        time: Animation time

    Returns:
        Boolean mask of pulfrich voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    # Density controls orbital radius (how spread out the ring is)
    # 0.0 = tight ring (radius 6), 1.0 = wide ring (radius 18)
    radius = 6 + params.density * 12
    num_objects = 8

    center_x = width / 2
    center_y = height / 2
    center_z = length / 2

    mask = np.zeros(grid_shape, dtype=np.float32)

    for i in range(num_objects):
        obj_angle = time + (i / num_objects) * np.pi * 2

        # Position in XY plane (rotating vertically)
        px = int(center_x + np.cos(obj_angle) * radius)
        py = int(center_y + np.sin(obj_angle) * radius)

        # Brightness varies with position
        brightness = 0.5 + 0.5 * np.sin(obj_angle)

        # Size controls sphere size (0.3-3.0 -> sphere radius 1-7)
        # Using int to ensure at least 1 pixel radius
        obj_size = max(1, int(1 + params.size * 2))

        for dx in range(-obj_size, obj_size + 1):
            for dy in range(-obj_size, obj_size + 1):
                for dz in range(-obj_size, obj_size + 1):
                    if dx*dx + dy*dy + dz*dz <= obj_size * obj_size:
                        wx = px + dx
                        wy = py + dy
                        wz = int(center_z + dz)

                        if 0 <= wx < width and 0 <= wy < height and 0 <= wz < length:
                            mask[wz, wy, wx] = max(mask[wz, wy, wx], brightness)

    return mask > 0.3


def generate_moire(coords, grid_shape, params, time):
    """
    Moire pattern - overlapping rotated grids.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with density
        time: Animation time

    Returns:
        Boolean mask of moire pattern voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    grid_spacing = max(2, int(3 * (1 + params.density)))
    angle = time * 0.1

    mask = np.zeros(grid_shape, dtype=bool)

    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    center_x = width / 2
    center_z = length / 2

    # Draw first grid - vertical lines along X
    for x in range(0, width, grid_spacing):
        mask[:, :, x] = True

    # Draw second grid - rotated in XZ plane
    for z in range(length):
        for x in range(width):
            # Transform to center-origin coords
            cx = x - center_x
            cz = z - center_z

            # Rotate
            rx = cx * cos_angle - cz * sin_angle

            # Check if this point is on a grid line
            if int(abs(rx)) % grid_spacing == 0:
                mask[z, :, x] = True

    return mask
