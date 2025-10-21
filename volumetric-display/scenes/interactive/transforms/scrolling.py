"""
Object scrolling system
"""

import numpy as np


def apply_object_scrolling(mask, raster, params, time):
    """
    Apply object scrolling by translating the entire mask based on direction and speed.

    Args:
        mask: Boolean array to scroll
        raster: Raster object with grid dimensions
        params: SceneParameters object with object_scroll_speed, object_scroll_direction
        time: Current animation time

    Returns:
        Scrolled mask
    """
    if params.object_scroll_speed == 0:
        return mask

    # Calculate scroll offset based on time and speed
    scroll_distance = time * params.object_scroll_speed * 5  # Scale for visible movement
    direction = params.object_scroll_direction

    # Determine offset for each axis based on direction
    offset_x = 0
    offset_y = 0
    offset_z = 0

    if direction == 'x':
        offset_x = int(scroll_distance) % raster.width
    elif direction == 'y':
        offset_y = int(scroll_distance) % raster.height
    elif direction == 'z':
        offset_z = int(scroll_distance) % raster.length
    elif direction == 'diagonal-xz':
        offset_x = int(scroll_distance * 0.707) % raster.width  # 1/sqrt(2)
        offset_z = int(scroll_distance * 0.707) % raster.length
    elif direction == 'diagonal-yz':
        offset_y = int(scroll_distance * 0.707) % raster.height
        offset_z = int(scroll_distance * 0.707) % raster.length
    elif direction == 'diagonal-xy':
        offset_x = int(scroll_distance * 0.707) % raster.width
        offset_y = int(scroll_distance * 0.707) % raster.height

    # Apply scrolling using numpy roll for wrapping
    scrolled_mask = mask
    if offset_z != 0:
        scrolled_mask = np.roll(scrolled_mask, offset_z, axis=0)
    if offset_y != 0:
        scrolled_mask = np.roll(scrolled_mask, offset_y, axis=1)
    if offset_x != 0:
        scrolled_mask = np.roll(scrolled_mask, offset_x, axis=2)

    return scrolled_mask
