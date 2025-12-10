"""Transform System - Rotation, Copy, Translation, and Scrolling"""

from .rotation import calculate_rotation_angles
from .copy import CopyManager
from .translation import apply_translation, apply_translation_with_indices
from .scrolling import apply_object_scrolling

__all__ = [
    'calculate_rotation_angles',
    'CopyManager',
    'apply_translation',
    'apply_translation_with_indices',
    'apply_object_scrolling',
]
