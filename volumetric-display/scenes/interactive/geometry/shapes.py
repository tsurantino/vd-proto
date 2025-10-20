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
    Generate a helix strand spiraling along Z-axis.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        radius: Helix radius (in XY plane)
        height_range: Tuple of (min_z, max_z) - extent along Z-axis
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
    min_z, max_z = height_range

    # Strand offset for multiple helixes
    strand_offset = strand_index * 2 * np.pi / max(1, num_strands)

    # For each Z coordinate, calculate the helix angle and position
    # helix_angle varies with Z position (z * 0.3 creates the spiral)
    # Add strand_offset to separate multiple strands
    helix_angle = z_coords * 0.3 + strand_offset

    # Calculate helix centerline position at each Z
    helix_x = cx + radius * np.cos(helix_angle)
    helix_y = cy + radius * np.sin(helix_angle)

    # Distance from each voxel to the helix centerline
    dx = x_coords - helix_x
    dy = y_coords - helix_y
    distance = np.sqrt(dx**2 + dy**2)

    # Voxels within thickness distance from helix centerline
    return distance < thickness


def generate_cube(coords, center, size, edge_thickness=2):
    """
    Generate a wireframe cube with 12 edges.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        size: Half-size of cube (distance from center to face)
        edge_thickness: Edge line thickness

    Returns:
        Boolean mask of cube voxels
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center

    # Calculate absolute distances from center
    dx = np.abs(x_coords - cx)
    dy = np.abs(y_coords - cy)
    dz = np.abs(z_coords - cz)

    # A voxel is on a cube edge if:
    # - It's close to a cube face in 2 dimensions
    # - AND within the cube bounds in the 3rd dimension

    # Edges parallel to X-axis (4 edges)
    x_edges = (dy >= size - edge_thickness) & (dy <= size + edge_thickness) & \
              (dz >= size - edge_thickness) & (dz <= size + edge_thickness) & \
              (dx <= size)

    # Edges parallel to Y-axis (4 edges)
    y_edges = (dx >= size - edge_thickness) & (dx <= size + edge_thickness) & \
              (dz >= size - edge_thickness) & (dz <= size + edge_thickness) & \
              (dy <= size)

    # Edges parallel to Z-axis (4 edges)
    z_edges = (dx >= size - edge_thickness) & (dx <= size + edge_thickness) & \
              (dy >= size - edge_thickness) & (dy <= size + edge_thickness) & \
              (dz <= size)

    mask = x_edges | y_edges | z_edges

    return mask


def generate_cross_grid(coords, center, size, line_thickness=2):
    """
    Generate a 3D cross pattern (axes through center).

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        size: Half-size of bounding volume
        line_thickness: Thickness of cross lines

    Returns:
        Boolean mask of cross pattern voxels
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center

    # Calculate distances from center axes
    dx = np.abs(x_coords - cx)
    dy = np.abs(y_coords - cy)
    dz = np.abs(z_coords - cz)

    # Create cross pattern: lines along each axis
    # X-axis line (dy and dz near center)
    x_line = (dy < line_thickness) & (dz < line_thickness)

    # Y-axis line (dx and dz near center)
    y_line = (dx < line_thickness) & (dz < line_thickness)

    # Z-axis line (dx and dy near center)
    z_line = (dx < line_thickness) & (dy < line_thickness)

    return x_line | y_line | z_line


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
    Generate a pyramid cone shell oriented along Z-axis.
    Base sits on XY plane, apex extends along Z.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        center: Tuple of (cx, cy, cz)
        base_size: Radius of circular base
        height: Height of pyramid (length along Z-axis)
        edge_thickness: Wall thickness

    Returns:
        Boolean mask of pyramid voxels
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center

    # Base of pyramid starts at one end of Z, apex at the other
    base_z = cz - height / 2

    # Calculate relative Z position from base
    dz = z_coords - base_z

    # Height ratio: 0 at base, 1 at apex
    height_ratio = dz / height

    # Current radius at this height (linear taper from base to apex)
    # At base (ratio=0): radius = base_size
    # At apex (ratio=1): radius = 0
    current_radius = base_size * (1 - height_ratio)

    # Distance from center axis (XY plane)
    dx = x_coords - cx
    dy = y_coords - cy
    dist_from_axis = np.sqrt(dx**2 + dy**2)

    # Voxel is part of cone if:
    # 1. Z is between base and apex
    # 2. Distance from axis is close to the current radius at this Z position
    mask = (
        (dz >= 0) & (dz < height) &
        (np.abs(dist_from_axis - current_radius) < edge_thickness)
    )

    return mask
