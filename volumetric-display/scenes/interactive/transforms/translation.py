"""
Translation system for animated object movement
"""

import numpy as np


def apply_translation(mask, raster, params, time):
    """
    Apply animated translation by shifting the mask based on direction, speed, and offset.

    Args:
        mask: Boolean array to translate
        raster: Raster object with grid dimensions
        params: SceneParameters object with copy_translation_x/y/z, copy_translation_speed, copy_translation_offset
        time: Current animation time

    Returns:
        Translated mask
    """
    # Check if any translation is active
    has_static_translation = (params.copy_translation_x != 0 or
                             params.copy_translation_y != 0 or
                             params.copy_translation_z != 0)
    has_animated_translation = params.copy_translation_speed != 0

    if not has_static_translation and not has_animated_translation:
        return mask

    # Calculate animated offset if speed is set
    animated_offset = 0
    if has_animated_translation:
        # Apply speed and time, with phase offset
        animated_offset = time * params.copy_translation_speed + params.copy_translation_offset

    # Calculate total offset for each axis
    # Static translation + animated translation component
    offset_x = params.copy_translation_x * raster.width
    offset_y = params.copy_translation_y * raster.height
    offset_z = params.copy_translation_z * raster.length

    # Add animated offset to all axes proportionally to their static values
    if has_animated_translation:
        total_static = abs(params.copy_translation_x) + abs(params.copy_translation_y) + abs(params.copy_translation_z)
        if total_static > 0:
            # Distribute animated movement across axes based on static proportions
            if params.copy_translation_x != 0:
                offset_x += animated_offset * (params.copy_translation_x / total_static) * raster.width
            if params.copy_translation_y != 0:
                offset_y += animated_offset * (params.copy_translation_y / total_static) * raster.height
            if params.copy_translation_z != 0:
                offset_z += animated_offset * (params.copy_translation_z / total_static) * raster.length
        else:
            # If no static translation, animate in Y direction by default
            offset_y = animated_offset * raster.height

    # Convert to integer offsets
    offset_x_int = int(offset_x) % raster.width if offset_x != 0 else 0
    offset_y_int = int(offset_y) % raster.height if offset_y != 0 else 0
    offset_z_int = int(offset_z) % raster.length if offset_z != 0 else 0

    # Apply translation using numpy roll for wrapping
    translated_mask = mask
    if offset_z_int != 0:
        translated_mask = np.roll(translated_mask, offset_z_int, axis=0)
    if offset_y_int != 0:
        translated_mask = np.roll(translated_mask, offset_y_int, axis=1)
    if offset_x_int != 0:
        translated_mask = np.roll(translated_mask, offset_x_int, axis=2)

    return translated_mask


def apply_translation_with_indices(mask, copy_indices, raster, params, time):
    """
    Apply animated translation to both mask and copy_indices arrays.

    This ensures that copy_indices stays aligned with the mask after translation,
    which is required for copy color effects to work correctly.

    Args:
        mask: Boolean array to translate
        copy_indices: Int8 array of copy indices to translate alongside mask
        raster: Raster object with grid dimensions
        params: SceneParameters object with copy_translation_x/y/z, copy_translation_speed, copy_translation_offset
        time: Current animation time

    Returns:
        Tuple of (translated_mask, translated_copy_indices)
    """
    # Check if any translation is active
    has_static_translation = (params.copy_translation_x != 0 or
                             params.copy_translation_y != 0 or
                             params.copy_translation_z != 0)
    has_animated_translation = params.copy_translation_speed != 0

    if not has_static_translation and not has_animated_translation:
        return mask, copy_indices

    # Calculate animated offset if speed is set
    animated_offset = 0
    if has_animated_translation:
        # Apply speed and time, with phase offset
        animated_offset = time * params.copy_translation_speed + params.copy_translation_offset

    # Calculate total offset for each axis
    # Static translation + animated translation component
    offset_x = params.copy_translation_x * raster.width
    offset_y = params.copy_translation_y * raster.height
    offset_z = params.copy_translation_z * raster.length

    # Add animated offset to all axes proportionally to their static values
    if has_animated_translation:
        total_static = abs(params.copy_translation_x) + abs(params.copy_translation_y) + abs(params.copy_translation_z)
        if total_static > 0:
            # Distribute animated movement across axes based on static proportions
            if params.copy_translation_x != 0:
                offset_x += animated_offset * (params.copy_translation_x / total_static) * raster.width
            if params.copy_translation_y != 0:
                offset_y += animated_offset * (params.copy_translation_y / total_static) * raster.height
            if params.copy_translation_z != 0:
                offset_z += animated_offset * (params.copy_translation_z / total_static) * raster.length
        else:
            # If no static translation, animate in Y direction by default
            offset_y = animated_offset * raster.height

    # Convert to integer offsets
    offset_x_int = int(offset_x) % raster.width if offset_x != 0 else 0
    offset_y_int = int(offset_y) % raster.height if offset_y != 0 else 0
    offset_z_int = int(offset_z) % raster.length if offset_z != 0 else 0

    # Apply translation using numpy roll for wrapping (to both arrays)
    translated_mask = mask
    translated_indices = copy_indices
    if offset_z_int != 0:
        translated_mask = np.roll(translated_mask, offset_z_int, axis=0)
        translated_indices = np.roll(translated_indices, offset_z_int, axis=0)
    if offset_y_int != 0:
        translated_mask = np.roll(translated_mask, offset_y_int, axis=1)
        translated_indices = np.roll(translated_indices, offset_y_int, axis=1)
    if offset_x_int != 0:
        translated_mask = np.roll(translated_mask, offset_x_int, axis=2)
        translated_indices = np.roll(translated_indices, offset_x_int, axis=2)

    return translated_mask, translated_indices
