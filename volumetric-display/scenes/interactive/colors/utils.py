"""
Color Utilities
Fast color conversion and manipulation functions
"""

import numpy as np
import re


def vectorized_hsv_to_rgb(h, s, v):
    """
    Fast, NumPy-based conversion from HSV to RGB.

    Args:
        h: Hue array (0-255)
        s: Saturation array (0-255)
        v: Value array (0-255)

    Returns:
        RGB array of shape (..., 3) with dtype=uint8
    """
    h_norm = h / 255.0
    s_norm = s / 255.0
    v_norm = v / 255.0

    i = np.floor(h_norm * 6).astype(np.int32)
    f = h_norm * 6 - i
    p = v_norm * (1 - s_norm)
    q = v_norm * (1 - f * s_norm)
    t = v_norm * (1 - (1 - f) * s_norm)

    i = i % 6

    # Create an empty array for the RGB output
    rgb = np.zeros(h.shape + (3,), dtype=np.float32)

    # Use boolean array indexing for each of the 6 HSV cases
    mask = i == 0
    rgb[mask] = np.stack([v_norm[mask], t[mask], p[mask]], axis=-1)
    mask = i == 1
    rgb[mask] = np.stack([q[mask], v_norm[mask], p[mask]], axis=-1)
    mask = i == 2
    rgb[mask] = np.stack([p[mask], v_norm[mask], t[mask]], axis=-1)
    mask = i == 3
    rgb[mask] = np.stack([p[mask], q[mask], v_norm[mask]], axis=-1)
    mask = i == 4
    rgb[mask] = np.stack([t[mask], p[mask], v_norm[mask]], axis=-1)
    mask = i == 5
    rgb[mask] = np.stack([v_norm[mask], p[mask], q[mask]], axis=-1)

    return (rgb * 255).astype(np.uint8)


def vectorized_rgb_to_hsv(rgb):
    """
    Fast, NumPy-based conversion from RGB to HSV.

    Args:
        rgb: RGB array of shape (..., 3) with values 0-255

    Returns:
        Tuple of (h, s, v) arrays with values 0-255
    """
    rgb = rgb.astype(np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]

    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    v = maxc

    deltac = maxc - minc
    s = np.where(maxc != 0, deltac / maxc, 0)

    # Calculate hue
    h = np.zeros_like(maxc)

    # Red is max
    mask = (maxc == r) & (deltac != 0)
    h[mask] = ((g[mask] - b[mask]) / deltac[mask]) % 6

    # Green is max
    mask = (maxc == g) & (deltac != 0)
    h[mask] = ((b[mask] - r[mask]) / deltac[mask]) + 2

    # Blue is max
    mask = (maxc == b) & (deltac != 0)
    h[mask] = ((r[mask] - g[mask]) / deltac[mask]) + 4

    h = (h / 6.0 * 255).astype(np.uint8)
    s = (s * 255).astype(np.uint8)
    v = (v * 255).astype(np.uint8)

    return h, s, v


def parse_hex_color(hex_color):
    """
    Parse hex color string to RGB tuple.

    Args:
        hex_color: String like '#FF0000' or '#F00'

    Returns:
        Tuple of (r, g, b) values 0-255
    """
    hex_color = hex_color.lstrip('#')

    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return np.array([r, g, b], dtype=np.uint8)


def parse_gradient(gradient_str):
    """
    Parse gradient string to list of RGB colors.

    Args:
        gradient_str: String like '#FF0000,#00FF00,#0000FF'

    Returns:
        List of RGB arrays
    """
    colors = gradient_str.split(',')
    return [parse_hex_color(c.strip()) for c in colors]


def interpolate_colors(colors, positions, t):
    """
    Interpolate between multiple colors.

    Args:
        colors: List of RGB arrays
        positions: Positions of each color (0-1)
        t: Position to sample (0-1) or array of positions

    Returns:
        RGB color(s) at position t
    """
    t = np.asarray(t)
    is_scalar = t.ndim == 0
    if is_scalar:
        t = t[np.newaxis]

    colors = np.array(colors, dtype=np.float32)
    positions = np.array(positions, dtype=np.float32)

    # Find which segment each t is in
    result = np.zeros(t.shape + (3,), dtype=np.uint8)

    for i in range(len(positions) - 1):
        mask = (t >= positions[i]) & (t < positions[i+1])
        if np.any(mask):
            # Interpolate between colors[i] and colors[i+1]
            local_t = (t[mask] - positions[i]) / (positions[i+1] - positions[i])
            local_t = local_t[..., np.newaxis]
            result[mask] = (
                colors[i] * (1 - local_t) + colors[i+1] * local_t
            ).astype(np.uint8)

    # Handle t >= last position
    mask = t >= positions[-1]
    result[mask] = colors[-1].astype(np.uint8)

    # Handle t < first position
    mask = t < positions[0]
    result[mask] = colors[0].astype(np.uint8)

    if is_scalar:
        return result[0]
    return result


def create_gradient(colors, num_steps):
    """
    Create a gradient with num_steps colors.

    Args:
        colors: List of RGB arrays
        num_steps: Number of color steps in gradient

    Returns:
        Array of RGB colors, shape (num_steps, 3)
    """
    positions = np.linspace(0, 1, len(colors))
    t_values = np.linspace(0, 1, num_steps)
    return interpolate_colors(colors, positions, t_values)


def apply_color_to_mask(raster_data, mask, color):
    """
    Apply a single color to voxels matching mask.

    Args:
        raster_data: RGB raster array (L, H, W, 3)
        mask: Boolean mask (L, H, W)
        color: RGB color as array [r, g, b]
    """
    raster_data[mask] = color


def apply_gradient_to_mask(raster_data, mask, coords, gradient_colors, gradient_direction='y'):
    """
    Apply a gradient to voxels matching mask.

    Args:
        raster_data: RGB raster array (L, H, W, 3)
        mask: Boolean mask (L, H, W)
        coords: Coordinate cache (z, y, x)
        gradient_colors: List of RGB colors
        gradient_direction: 'x', 'y', 'z', or array of positions
    """
    if not np.any(mask):
        return

    z_coords, y_coords, x_coords = coords

    # Get coordinate along gradient direction
    if gradient_direction == 'x':
        pos = x_coords[mask] / x_coords.max()
    elif gradient_direction == 'y':
        pos = y_coords[mask] / y_coords.max()
    elif gradient_direction == 'z':
        pos = z_coords[mask] / z_coords.max()
    else:
        # Custom position array
        pos = gradient_direction[mask]

    # Create gradient color positions
    color_positions = np.linspace(0, 1, len(gradient_colors))

    # Interpolate colors
    colors = interpolate_colors(gradient_colors, color_positions, pos)
    raster_data[mask] = colors


def hue_shift(rgb, shift_amount):
    """
    Shift hue of RGB colors.

    Args:
        rgb: RGB array (..., 3)
        shift_amount: Amount to shift hue (0-255)

    Returns:
        RGB array with shifted hue
    """
    h, s, v = vectorized_rgb_to_hsv(rgb)
    h = (h.astype(np.int32) + shift_amount) % 256
    return vectorized_hsv_to_rgb(h, s, v)


def adjust_brightness(rgb, factor):
    """
    Adjust brightness of RGB colors.

    Args:
        rgb: RGB array (..., 3)
        factor: Brightness multiplier (0-2)

    Returns:
        RGB array with adjusted brightness
    """
    return np.clip(rgb.astype(np.float32) * factor, 0, 255).astype(np.uint8)


def rainbow_color(position, saturation=255, value=255):
    """
    Generate rainbow color at position.

    Args:
        position: Position in rainbow (0-255 or array)
        saturation: Color saturation (0-255)
        value: Color value/brightness (0-255)

    Returns:
        RGB color(s)
    """
    position = np.asarray(position)
    hue = position % 256

    s = np.full_like(hue, saturation, dtype=np.uint8)
    v = np.full_like(hue, value, dtype=np.uint8)

    return vectorized_hsv_to_rgb(hue, s, v)
