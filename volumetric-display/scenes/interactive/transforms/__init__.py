"""Transform System - Rotation, Copy, and Scrolling"""

from .rotation import calculate_rotation_angles
from .copy import CopyManager
from .scrolling import apply_object_scrolling

__all__ = [
    'calculate_rotation_angles',
    'CopyManager',
    'apply_object_scrolling',
]
