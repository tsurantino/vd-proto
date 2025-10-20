"""
Geometry utilities for transformations
"""

import numpy as np


def rotate_coordinates(coords, center, angles):
    """
    Apply 3D rotation to sparse coordinate arrays around a center point.

    Args:
        coords: Tuple of (z, y, x) sparse coordinate arrays
        center: Tuple of (cx, cy, cz) center point
        angles: Tuple of (angle_x, angle_y, angle_z) in radians

    Returns:
        Tuple of rotated (z, y, x) coordinate arrays
    """
    z_coords, y_coords, x_coords = coords
    cx, cy, cz = center
    angle_x, angle_y, angle_z = angles

    # If no rotation, return original coords
    if angle_x == 0 and angle_y == 0 and angle_z == 0:
        return coords

    # Translate to origin
    x = x_coords - cx
    y = y_coords - cy
    z = z_coords - cz

    # Rotation around X axis (pitch)
    if angle_x != 0:
        cos_x = np.cos(angle_x)
        sin_x = np.sin(angle_x)
        y_new = y * cos_x - z * sin_x
        z_new = y * sin_x + z * cos_x
        y = y_new
        z = z_new

    # Rotation around Y axis (yaw)
    if angle_y != 0:
        cos_y = np.cos(angle_y)
        sin_y = np.sin(angle_y)
        x_new = x * cos_y + z * sin_y
        z_new = -x * sin_y + z * cos_y
        x = x_new
        z = z_new

    # Rotation around Z axis (roll)
    if angle_z != 0:
        cos_z = np.cos(angle_z)
        sin_z = np.sin(angle_z)
        x_new = x * cos_z - y * sin_z
        y_new = x * sin_z + y * cos_z
        x = x_new
        y = y_new

    # Translate back
    x_rotated = x + cx
    y_rotated = y + cy
    z_rotated = z + cz

    return (z_rotated, y_rotated, x_rotated)
