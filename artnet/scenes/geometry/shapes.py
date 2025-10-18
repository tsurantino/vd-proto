"""
Shape Geometry Generators
Sphere, helix, cube, torus, pyramid
"""

import numpy as np


def generate_sphere(coords, center, radius, thickness=1.5):
    """
    Generate a sphere shell.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        radius: Sphere radius
        thickness: Shell thickness

    Returns:
        Boolean mask of sphere voxels
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center

    dx = x_coords - cx
    dy = y_coords - cy
    dz = z_coords - cz
    distance = np.sqrt(dx**2 + dy**2 + dz**2)

    return (distance >= radius - thickness) & (distance <= radius + thickness)


def generate_pulsing_sphere(coords, center, base_radius, time, pulse_speed=2, pulse_amount=2, thickness=1.5):
    """
    Generate a pulsing sphere.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        base_radius: Base sphere radius
        time: Animation time
        pulse_speed: Speed of pulsing
        pulse_amount: Amount of pulse
        thickness: Shell thickness

    Returns:
        Boolean mask of sphere voxels
    """
    radius = base_radius + np.sin(time * pulse_speed) * pulse_amount
    return generate_sphere(coords, center, radius, thickness)


def generate_helix(coords, center, radius, height_range, time, rotation_speed=1, num_strands=1, strand_index=0, thickness=3):
    """
    Generate a helix strand.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        radius: Helix radius
        height_range: Tuple of (min_y, max_y)
        time: Animation time
        rotation_speed: Rotation speed
        num_strands: Total number of strands
        strand_index: Index of this strand
        thickness: Helix thickness

    Returns:
        Boolean mask of helix voxels
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center
    min_y, max_y = height_range

    t_offset = strand_index * 2 * np.pi / max(1, num_strands)
    y_pos = ((time * 10 + strand_index * (max_y - min_y) / max(1, num_strands)) % (max_y - min_y)) + min_y

    angle = time * rotation_speed + t_offset + (y_pos - min_y) * 0.5
    hx = cx + radius * np.cos(angle)
    hz = cz + radius * np.sin(angle)

    dx = x_coords - hx
    dy = y_coords - y_pos
    dz = z_coords - hz
    distance = np.sqrt(dx**2 + dy**2 + dz**2)

    return distance < thickness


def generate_cube(coords, center, size, edge_thickness=2):
    """
    Generate a wireframe cube.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        size: Half-size of cube
        edge_thickness: Edge thickness

    Returns:
        Boolean mask of cube voxels
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center

    mask = np.zeros(z_coords.shape, dtype=bool)

    # Draw edges along each axis
    for axis in range(3):
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                if axis == 0:  # X edges
                    edge_mask = (
                        (np.abs(y_coords - (cy + sy * size)) < edge_thickness) &
                        (np.abs(z_coords - (cz + sx * size)) < edge_thickness)
                    )
                elif axis == 1:  # Y edges
                    edge_mask = (
                        (np.abs(x_coords - (cx + sx * size)) < edge_thickness) &
                        (np.abs(z_coords - (cz + sy * size)) < edge_thickness)
                    )
                else:  # Z edges
                    edge_mask = (
                        (np.abs(x_coords - (cx + sx * size)) < edge_thickness) &
                        (np.abs(y_coords - (cy + sy * size)) < edge_thickness)
                    )
                mask |= edge_mask

    return mask


def generate_torus(coords, center, major_radius, minor_radius, thickness=1.5):
    """
    Generate a torus.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        major_radius: Major radius (from center to tube center)
        minor_radius: Minor radius (tube radius)
        thickness: Shell thickness

    Returns:
        Boolean mask of torus voxels
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center

    dx = x_coords - cx
    dy = y_coords - cy
    dz = z_coords - cz

    # Distance from torus center in XZ plane
    r_xz = np.sqrt(dx**2 + dz**2)

    # Distance from tube center
    tube_distance = np.sqrt((r_xz - major_radius)**2 + dy**2)

    return (tube_distance >= minor_radius - thickness) & (tube_distance <= minor_radius + thickness)


def generate_pyramid(coords, center, base_size, height, edge_thickness=2):
    """
    Generate a wireframe pyramid.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        base_size: Size of square base
        height: Height of pyramid
        edge_thickness: Edge thickness

    Returns:
        Boolean mask of pyramid voxels
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center

    mask = np.zeros(z_coords.shape, dtype=bool)

    # Base square edges
    base_y = cy - height / 2
    for i in range(4):
        angle1 = i * np.pi / 2
        angle2 = ((i + 1) % 4) * np.pi / 2

        x1 = cx + base_size * np.cos(angle1)
        z1 = cz + base_size * np.sin(angle1)
        x2 = cx + base_size * np.cos(angle2)
        z2 = cz + base_size * np.sin(angle2)

        # Simplified edge drawing
        edge_mask = (
            (np.abs(y_coords - base_y) < edge_thickness) &
            (np.abs((x_coords - x1) * (z2 - z1) - (z_coords - z1) * (x2 - x1)) < edge_thickness * 100)
        )
        mask |= edge_mask

    # Edges from corners to apex
    apex_y = cy + height / 2
    for i in range(4):
        angle = i * np.pi / 2
        base_x = cx + base_size * np.cos(angle)
        base_z = cz + base_size * np.sin(angle)

        # Line from base corner to apex
        t = (y_coords - base_y) / (apex_y - base_y + 1e-6)
        line_x = base_x + (cx - base_x) * t
        line_z = base_z + (cz - base_z) * t

        edge_mask = (
            (t >= 0) & (t <= 1) &
            (np.abs(x_coords - line_x) < edge_thickness) &
            (np.abs(z_coords - line_z) < edge_thickness)
        )
        mask |= edge_mask

    return mask
