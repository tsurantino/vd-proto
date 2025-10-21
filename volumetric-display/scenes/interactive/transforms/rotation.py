"""
Rotation calculation utilities
"""

import numpy as np


def calculate_rotation_angles(time, rot_x, rot_y, rot_z, speed, offset):
    """
    Calculate rotation angles with optional animation speed and offset.

    Args:
        time: Current animation time
        rot_x, rot_y, rot_z: Base rotation amounts (-1 to 1)
        speed: Animation speed (0-5)
        offset: Phase offset between axes (0-1) - creates off-axis rotation

    Returns:
        Tuple of (angle_x, angle_y, angle_z) in radians
    """
    if speed > 0:
        # Animate rotation with speed and offset
        # Offset creates phase difference between axes for interesting spinning effects
        angle_x = (rot_x * np.pi) + (time * speed * 1.0)
        angle_y = (rot_y * np.pi) + (time * speed * (1.0 + offset * 0.5))
        angle_z = (rot_z * np.pi) + (time * speed * (1.0 + offset * 1.0))
    else:
        # Static rotation (no animation)
        angle_x = rot_x * np.pi
        angle_y = rot_y * np.pi
        angle_z = rot_z * np.pi

    return (angle_x, angle_y, angle_z)
