"""
Color Utilities - HSL/RGB Conversion matching JavaScript implementation
"""

import numpy as np


def hsl_to_rgb_single(h, s, l):
    """
    Convert single HSL color to RGB (matching JavaScript algorithm exactly)
    h: 0-1, s: 0-1, l: 0-1
    Returns: (r, g, b) in 0-255 range
    """
    if s == 0:
        r = g = b = l
    else:
        def hue2rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue2rgb(p, q, h + 1/3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1/3)

    return (
        np.round(r * 255).astype(np.uint8),
        np.round(g * 255).astype(np.uint8),
        np.round(b * 255).astype(np.uint8)
    )


def hsl_to_rgb(h, s, l):
    """
    Vectorized HSL to RGB conversion
    h, s, l: arrays of values (0-1 range)
    Returns: (N, 3) RGB array
    """
    # Handle scalar inputs
    if np.isscalar(h):
        return np.array(hsl_to_rgb_single(h, s, l))

    # Vectorized implementation
    # Store scalar status before conversion
    s_is_scalar = np.isscalar(s)
    l_is_scalar = np.isscalar(l)

    h = np.asarray(h)
    s = np.asarray(s)
    l = np.asarray(l)

    shape = h.shape
    h = h.flatten()
    s = np.full_like(h, s.item()) if s_is_scalar else s.flatten()
    l = np.full_like(h, l.item()) if l_is_scalar else l.flatten()

    # Create output arrays
    r = np.zeros_like(h)
    g = np.zeros_like(h)
    b = np.zeros_like(h)

    # Achromatic case (s == 0)
    achromatic = s == 0
    r[achromatic] = l[achromatic]
    g[achromatic] = l[achromatic]
    b[achromatic] = l[achromatic]

    # Chromatic case
    chromatic = ~achromatic
    if np.any(chromatic):
        h_c = h[chromatic]
        s_c = s[chromatic]
        l_c = l[chromatic]

        q = np.where(l_c < 0.5, l_c * (1 + s_c), l_c + s_c - l_c * s_c)
        p = 2 * l_c - q

        # Helper function for vectorized hue2rgb
        def hue2rgb_vec(p, q, t):
            t = t % 1.0  # Wrap to [0, 1]
            result = np.zeros_like(t)

            mask1 = t < 1/6
            result[mask1] = p[mask1] + (q[mask1] - p[mask1]) * 6 * t[mask1]

            mask2 = (t >= 1/6) & (t < 1/2)
            result[mask2] = q[mask2]

            mask3 = (t >= 1/2) & (t < 2/3)
            result[mask3] = p[mask3] + (q[mask3] - p[mask3]) * (2/3 - t[mask3]) * 6

            mask4 = t >= 2/3
            result[mask4] = p[mask4]

            return result

        r[chromatic] = hue2rgb_vec(p, q, h_c + 1/3)
        g[chromatic] = hue2rgb_vec(p, q, h_c)
        b[chromatic] = hue2rgb_vec(p, q, h_c - 1/3)

    # Convert to 0-255 range and combine
    rgb = np.stack([r, g, b], axis=-1) * 255
    rgb = np.round(rgb).astype(np.uint8)

    return rgb.reshape(shape + (3,)) if len(shape) > 0 else rgb.squeeze()


def rgb_to_hsl(r, g, b):
    """
    Convert RGB to HSL (matching JavaScript algorithm)
    r, g, b: 0-255 or arrays
    Returns: (h, s, l) in 0-1 range
    """
    # Normalize to 0-1
    r = np.asarray(r) / 255.0
    g = np.asarray(g) / 255.0
    b = np.asarray(b) / 255.0

    max_val = np.maximum(np.maximum(r, g), b)
    min_val = np.minimum(np.minimum(r, g), b)

    l = (max_val + min_val) / 2

    # Initialize h and s
    h = np.zeros_like(l)
    s = np.zeros_like(l)

    # Chromatic case
    chroma = max_val - min_val
    chromatic = chroma != 0

    if np.any(chromatic):
        # Calculate saturation
        s_denom = np.where(l <= 0.5, max_val + min_val, 2 - max_val - min_val)
        s[chromatic] = chroma[chromatic] / s_denom[chromatic]

        # Calculate hue
        r_c = r[chromatic]
        g_c = g[chromatic]
        b_c = b[chromatic]
        max_c = max_val[chromatic]
        chroma_c = chroma[chromatic]

        h_val = np.zeros_like(r_c)

        # Red is max
        mask_r = (r_c == max_c)
        h_val[mask_r] = ((g_c[mask_r] - b_c[mask_r]) / chroma_c[mask_r] + (6 if np.any(g_c[mask_r] < b_c[mask_r]) else 0)) / 6

        # Green is max
        mask_g = (g_c == max_c)
        h_val[mask_g] = ((b_c[mask_g] - r_c[mask_g]) / chroma_c[mask_g] + 2) / 6

        # Blue is max
        mask_b = (b_c == max_c)
        h_val[mask_b] = ((r_c[mask_b] - g_c[mask_b]) / chroma_c[mask_b] + 4) / 6

        h[chromatic] = h_val % 1.0

    return h, s, l


def apply_color_dict_to_array(color_dict, count):
    """
    Convert color dict {r, g, b} to numpy array
    """
    return np.array([[color_dict['r'], color_dict['g'], color_dict['b']]] * count, dtype=np.uint8)
