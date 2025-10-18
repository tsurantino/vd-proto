"""
All Color Effects
Complete implementation of 50+ color effects from index.html
"""

import numpy as np
from .utils import vectorized_hsv_to_rgb, vectorized_rgb_to_hsv, hue_shift


def apply_color_effect(raster_data, mask, coords, time, effect_name, intensity=1.0, base_colors=None):
    """
    Apply a color effect to the masked voxels.

    Args:
        raster_data: RGB raster array (L, H, W, 3)
        mask: Boolean mask (L, H, W)
        coords: Coordinate cache (z, y, x)
        time: Animation time
        effect_name: Name of effect to apply
        intensity: Effect intensity (0-1)
        base_colors: Optional base colors to modify

    Returns:
        Modified raster_data (in-place modification)
    """
    if not np.any(mask):
        return raster_data

    # Get current colors or use base colors
    if base_colors is not None:
        colors = base_colors
    else:
        colors = raster_data[mask].copy()

    z_coords, y_coords, x_coords = coords

    # Apply the effect
    if effect_name == 'none':
        pass

    # ===== BASE EFFECTS =====
    elif effect_name == 'cycle':
        colors = effect_cycle(colors, time)
    elif effect_name == 'pulse':
        colors = effect_pulse(colors, time)
    elif effect_name == 'wave':
        colors = effect_wave(colors, mask, coords, time)

    # ===== WAVE EFFECTS =====
    elif effect_name == 'waveMulti':
        colors = effect_wave_multi(colors, mask, coords, time)
    elif effect_name == 'waveVertical':
        colors = effect_wave_vertical(colors, mask, coords, time)
    elif effect_name == 'waveCircular':
        colors = effect_wave_circular(colors, mask, coords, time)
    elif effect_name == 'waveStanding':
        colors = effect_wave_standing(colors, mask, coords, time)

    # ===== CYCLE EFFECTS =====
    elif effect_name == 'cycleHue':
        colors = effect_cycle_hue(colors, time)
    elif effect_name == 'cyclePalette':
        colors = effect_cycle_palette(colors, mask, coords, time)
    elif effect_name == 'cycleComplementary':
        colors = effect_cycle_complementary(colors, time)
    elif effect_name == 'cycleTriadic':
        colors = effect_cycle_triadic(colors, time)

    # ===== PULSE EFFECTS =====
    elif effect_name == 'pulseRadial':
        colors = effect_pulse_radial(colors, mask, coords, time)
    elif effect_name == 'pulseAlternating':
        colors = effect_pulse_alternating(colors, mask, coords, time)
    elif effect_name == 'pulseLayered':
        colors = effect_pulse_layered(colors, mask, coords, time)
    elif effect_name == 'pulseBeat':
        colors = effect_pulse_beat(colors, time)

    # ===== STATIC EFFECTS =====
    elif effect_name == 'staticColor':
        colors = effect_static_color(colors, mask, coords, time)
    elif effect_name == 'staticDynamic':
        colors = effect_static_dynamic(colors, mask, coords, time)
    elif effect_name == 'staticWave':
        colors = effect_static_wave(colors, mask, coords, time)

    # ===== COMBO EFFECTS =====
    elif effect_name == 'pulseWave':
        colors = effect_pulse_wave(colors, mask, coords, time)
    elif effect_name == 'cyclePulse':
        colors = effect_cycle_pulse(colors, mask, coords, time)
    elif effect_name == 'waveChase':
        colors = effect_wave_chase(colors, mask, coords, time)
    elif effect_name == 'staticCycle':
        colors = effect_static_cycle(colors, mask, coords, time)
    elif effect_name == 'pulseTrail':
        colors = effect_pulse_trail(colors, mask, coords, time)

    # ===== 3D SPATIAL EFFECTS =====
    elif effect_name == 'diagonalWaves':
        colors = effect_diagonal_waves(colors, mask, coords, time)
    elif effect_name == 'helix':
        colors = effect_helix(colors, mask, coords, time)
    elif effect_name == 'vortex':
        colors = effect_vortex(colors, mask, coords, time)
    elif effect_name == 'tunnel':
        colors = effect_tunnel(colors, mask, coords, time)

    # ===== PROCEDURAL EFFECTS =====
    elif effect_name == 'perlinNoise':
        colors = effect_perlin_noise(colors, mask, coords, time)
    elif effect_name == 'voronoi':
        colors = effect_voronoi(colors, mask, coords, time)
    elif effect_name == 'checkerboard3D':
        colors = effect_checkerboard_3d(colors, mask, coords, time)

    # ===== INTERFERENCE EFFECTS =====
    elif effect_name == 'sineInterferenceXZ':
        colors = effect_sine_interference_xz(colors, mask, coords, time)
    elif effect_name == 'sphericalShellsMoving':
        colors = effect_spherical_shells(colors, mask, coords, time)
    elif effect_name == 'cornerExplosion':
        colors = effect_corner_explosion(colors, mask, coords, time)

    # ===== GEOMETRIC EFFECTS =====
    elif effect_name == 'depthLayers':
        colors = effect_depth_layers(colors, mask, coords, time)
    elif effect_name == 'cubeInCube':
        colors = effect_cube_in_cube(colors, mask, coords, time)
    elif effect_name == 'manhattanDistance':
        colors = effect_manhattan_distance(colors, mask, coords, time)

    # ===== SYMMETRY EFFECTS =====
    elif effect_name == 'xzMirror':
        colors = effect_xz_mirror(colors, mask, coords, time)
    elif effect_name == 'directionalSweep':
        colors = effect_directional_sweep(colors, mask, coords, time)

    # ===== CLASSIC EFFECTS =====
    elif effect_name == 'sparkle':
        colors = effect_sparkle(colors, mask, coords, time)
    elif effect_name == 'rainbowSweep':
        colors = effect_rainbow_sweep(colors, mask, coords, time)
    elif effect_name == 'fire':
        colors = effect_fire(colors, mask, coords, time)
    elif effect_name == 'plasma':
        colors = effect_plasma(colors, mask, coords, time)
    elif effect_name == 'kaleidoscope':
        colors = effect_kaleidoscope(colors, mask, coords, time)
    elif effect_name == 'breath':
        colors = effect_breath(colors, time)
    elif effect_name == 'colorChase':
        colors = effect_color_chase(colors, mask, coords, time)

    # Apply intensity blending
    if intensity < 1.0:
        original = raster_data[mask]
        colors = (original * (1 - intensity) + colors * intensity).astype(np.uint8)

    raster_data[mask] = colors
    return raster_data


# ===================================================================
# BASE EFFECTS
# ===================================================================

def effect_cycle(colors, time):
    """Cycle through hue"""
    shift = int(time * 50) % 256
    return hue_shift(colors, shift)


def effect_pulse(colors, time):
    """Brightness pulsing"""
    factor = 0.5 + 0.5 * np.sin(time * 3)
    return (colors.astype(np.float32) * factor).astype(np.uint8)


def effect_wave(colors, mask, coords, time):
    """Wave color shift based on Y position"""
    z_coords, y_coords, x_coords = coords
    wave = np.sin(y_coords[mask] * 0.2 + time * 2) * 128
    shift = wave.astype(np.int32)
    return hue_shift(colors, shift)


# ===================================================================
# WAVE EFFECTS
# ===================================================================

def effect_wave_multi(colors, mask, coords, time):
    """Multiple wave patterns"""
    z_coords, y_coords, x_coords = coords
    wave_y = np.sin(y_coords[mask] * 0.3 + time * 2)
    wave_x = np.sin(x_coords[mask] * 0.3 + time * 1.5)
    combined = (wave_y + wave_x) * 64
    return hue_shift(colors, combined.astype(np.int32))


def effect_wave_vertical(colors, mask, coords, time):
    """Vertical wave sweep"""
    z_coords, y_coords, x_coords = coords
    wave = np.sin(y_coords[mask] * 0.5 + time * 4) * 128
    return hue_shift(colors, wave.astype(np.int32))


def effect_wave_circular(colors, mask, coords, time):
    """Circular wave from center"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    # Get grid dimensions from sparse coords
    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cz, cy, cx = grid_shape[0] / 2, grid_shape[1] / 2, grid_shape[2] / 2

    distance = np.sqrt((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
    wave = np.sin(distance * 0.3 + time * 3) * 128
    return hue_shift(colors, wave.astype(np.int32))


def effect_wave_standing(colors, mask, coords, time):
    """Standing wave pattern"""
    z_coords, y_coords, x_coords = coords
    wave = np.sin(x_coords[mask] * 0.4) * np.sin(time * 3) * 128
    return hue_shift(colors, wave.astype(np.int32))


# ===================================================================
# CYCLE EFFECTS
# ===================================================================

def effect_cycle_hue(colors, time):
    """Smooth hue cycling"""
    shift = int(time * 30) % 256
    return hue_shift(colors, shift)


def effect_cycle_palette(colors, mask, coords, time):
    """Cycle through color palette"""
    z_coords, y_coords, x_coords = coords
    phase = (y_coords[mask] / 20.0 + time * 0.5) % 1.0
    hue = (phase * 256).astype(np.int32)
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_cycle_complementary(colors, time):
    """Cycle between complementary colors"""
    h, s, v = vectorized_rgb_to_hsv(colors)
    shift = 128 if (int(time * 2) % 2) else 0
    h = (h.astype(np.int32) + shift) % 256
    return vectorized_hsv_to_rgb(h, s, v)


def effect_cycle_triadic(colors, time):
    """Cycle through triadic colors"""
    h, s, v = vectorized_rgb_to_hsv(colors)
    shift = int((time % 3) * 85)  # 0, 85, 170
    h = (h.astype(np.int32) + shift) % 256
    return vectorized_hsv_to_rgb(h, s, v)


# ===================================================================
# PULSE EFFECTS
# ===================================================================

def effect_pulse_radial(colors, mask, coords, time):
    """Radial pulse from center"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cz, cy, cx = grid_shape[0] / 2, grid_shape[1] / 2, grid_shape[2] / 2

    distance = np.sqrt((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
    pulse = 0.5 + 0.5 * np.sin(distance * 0.5 - time * 5)
    return (colors.astype(np.float32) * pulse[..., np.newaxis]).astype(np.uint8)


def effect_pulse_alternating(colors, mask, coords, time):
    """Alternating brightness pulses"""
    z_coords, y_coords, x_coords = coords
    pattern = ((x_coords[mask] + y_coords[mask] + z_coords[mask]) % 2).astype(np.float32)
    pulse = 0.5 + 0.5 * np.sin(time * 4 + pattern * np.pi)
    return (colors.astype(np.float32) * pulse[..., np.newaxis]).astype(np.uint8)


def effect_pulse_layered(colors, mask, coords, time):
    """Layered pulses by height"""
    z_coords, y_coords, x_coords = coords
    layer = y_coords[mask] / 20.0
    pulse = 0.5 + 0.5 * np.sin(time * 3 + layer * 2 * np.pi)
    return (colors.astype(np.float32) * pulse[..., np.newaxis]).astype(np.uint8)


def effect_pulse_beat(colors, time):
    """Beat-style pulsing"""
    beat = np.abs(np.sin(time * 2))
    return (colors.astype(np.float32) * beat).astype(np.uint8)


# ===================================================================
# STATIC EFFECTS
# ===================================================================

def effect_static_color(colors, mask, coords, time):
    """Random static noise in color"""
    noise = np.random.random(colors.shape) * 0.3
    return np.clip(colors.astype(np.float32) * (1 + noise), 0, 255).astype(np.uint8)


def effect_static_dynamic(colors, mask, coords, time):
    """Dynamic animated static"""
    z_coords, y_coords, x_coords = coords
    noise = np.sin(x_coords[mask] * 123 + time * 10) * np.cos(y_coords[mask] * 456 + time * 7)
    noise = (noise + 1) * 0.15 + 0.7  # 0.7 to 1.0
    return (colors.astype(np.float32) * noise[..., np.newaxis]).astype(np.uint8)


def effect_static_wave(colors, mask, coords, time):
    """Static with wave modulation"""
    z_coords, y_coords, x_coords = coords
    wave = 0.8 + 0.2 * np.sin(y_coords[mask] * 0.3 + time * 2)
    noise = np.random.random(np.sum(mask)) * 0.2 + 0.9
    combined = wave * noise
    return (colors.astype(np.float32) * combined[..., np.newaxis]).astype(np.uint8)


# ===================================================================
# COMBO EFFECTS
# ===================================================================

def effect_pulse_wave(colors, mask, coords, time):
    """Combined pulse and wave"""
    z_coords, y_coords, x_coords = coords
    pulse = 0.6 + 0.4 * np.sin(time * 3)
    wave = np.sin(y_coords[mask] * 0.3 + time * 2) * 64
    colors_shifted = hue_shift(colors, wave.astype(np.int32))
    return (colors_shifted.astype(np.float32) * pulse).astype(np.uint8)


def effect_cycle_pulse(colors, mask, coords, time):
    """Cycling hue with pulsing brightness"""
    shift = int(time * 40) % 256
    colors_shifted = hue_shift(colors, shift)
    pulse = 0.5 + 0.5 * np.sin(time * 4)
    return (colors_shifted.astype(np.float32) * pulse).astype(np.uint8)


def effect_wave_chase(colors, mask, coords, time):
    """Chasing wave pattern"""
    z_coords, y_coords, x_coords = coords
    chase = (y_coords[mask] + time * 10) % 20
    brightness = 1.0 - (chase / 20.0) * 0.5
    return (colors.astype(np.float32) * brightness[..., np.newaxis]).astype(np.uint8)


def effect_static_cycle(colors, mask, coords, time):
    """Static with color cycling"""
    shift = int(time * 30) % 256
    colors_shifted = hue_shift(colors, shift)
    noise = np.random.random(colors.shape) * 0.2 + 0.9
    return (colors_shifted.astype(np.float32) * noise).astype(np.uint8)


def effect_pulse_trail(colors, mask, coords, time):
    """Pulsing trailing effect"""
    z_coords, y_coords, x_coords = coords
    trail = np.sin(y_coords[mask] * 0.2 - time * 5)
    brightness = np.clip((trail + 1) * 0.5, 0.2, 1.0)
    return (colors.astype(np.float32) * brightness[..., np.newaxis]).astype(np.uint8)


# ===================================================================
# 3D SPATIAL EFFECTS
# ===================================================================

def effect_diagonal_waves(colors, mask, coords, time):
    """Diagonal wave patterns"""
    z_coords, y_coords, x_coords = coords
    diagonal = x_coords[mask] + y_coords[mask] + z_coords[mask]
    wave = np.sin(diagonal * 0.2 + time * 3) * 128
    return hue_shift(colors, wave.astype(np.int32))


def effect_helix(colors, mask, coords, time):
    """Helix color pattern"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cx, cz = grid_shape[2] / 2, grid_shape[0] / 2

    angle = np.arctan2(z - cz, x - cx) + y * 0.3 + time * 2
    hue = ((angle + np.pi) / (2 * np.pi) * 256).astype(np.int32) % 256
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_vortex(colors, mask, coords, time):
    """Vortex/spiral effect"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cx, cy, cz = grid_shape[2] / 2, grid_shape[1] / 2, grid_shape[0] / 2

    dx, dz = x - cx, z - cz
    distance = np.sqrt(dx**2 + dz**2)
    angle = np.arctan2(dz, dx)

    spiral = angle + distance * 0.3 - time * 3
    hue = ((spiral + np.pi) / (2 * np.pi) * 256).astype(np.int32) % 256
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_tunnel(colors, mask, coords, time):
    """Tunnel effect"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cx, cy, cz = grid_shape[2] / 2, grid_shape[1] / 2, grid_shape[0] / 2

    distance = np.sqrt((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
    tunnel = distance * 0.5 - time * 5
    hue = (tunnel * 20).astype(np.int32) % 256
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


# ===================================================================
# PROCEDURAL EFFECTS
# ===================================================================

def effect_perlin_noise(colors, mask, coords, time):
    """Perlin-like noise (simplified)"""
    z_coords, y_coords, x_coords = coords
    noise = (
        np.sin(x_coords[mask] * 0.3 + time) *
        np.cos(y_coords[mask] * 0.3 + time * 0.7) *
        np.sin(z_coords[mask] * 0.3 + time * 0.5)
    )
    hue_offset = (noise * 128).astype(np.int32)
    return hue_shift(colors, hue_offset)


def effect_voronoi(colors, mask, coords, time):
    """Voronoi cell pattern"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    # Simplified Voronoi with fixed seed points
    seed_points = np.array([[10, 10, 10], [30, 10, 10], [10, 10, 30], [30, 10, 30]])

    min_dist = np.full(len(x), np.inf)
    cell_id = np.zeros(len(x), dtype=np.int32)

    for i, seed in enumerate(seed_points):
        dist = np.sqrt((x - seed[2])**2 + (y - seed[1])**2 + (z - seed[0])**2)
        mask_closer = dist < min_dist
        min_dist[mask_closer] = dist[mask_closer]
        cell_id[mask_closer] = i

    hue = ((cell_id * 64 + time * 20) % 256).astype(np.int32)
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_checkerboard_3d(colors, mask, coords, time):
    """3D checkerboard pattern"""
    z_coords, y_coords, x_coords = coords
    checker = ((x_coords[mask] // 5) + (y_coords[mask] // 5) + (z_coords[mask] // 5)) % 2
    shift = (checker.astype(np.int32) * 128 + int(time * 30)) % 256
    return hue_shift(colors, shift)


# ===================================================================
# INTERFERENCE EFFECTS
# ===================================================================

def effect_sine_interference_xz(colors, mask, coords, time):
    """Sine wave interference in XZ plane"""
    z_coords, y_coords, x_coords = coords
    wave_x = np.sin(x_coords[mask] * 0.4 + time * 2)
    wave_z = np.sin(z_coords[mask] * 0.4 - time * 2)
    interference = ((wave_x + wave_z) * 64).astype(np.int32)
    return hue_shift(colors, interference)


def effect_spherical_shells(colors, mask, coords, time):
    """Moving spherical shells (bubbles)"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cx, cy, cz = grid_shape[2] / 2, grid_shape[1] / 2, grid_shape[0] / 2

    distance = np.sqrt((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
    shells = np.sin(distance * 0.5 - time * 3) * 128
    return hue_shift(colors, shells.astype(np.int32))


def effect_corner_explosion(colors, mask, coords, time):
    """Explosion from corners"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    # Distance from corner
    corner_dist = np.sqrt(x**2 + y**2 + z**2)
    explosion = np.sin(corner_dist * 0.3 - time * 4) * 128
    return hue_shift(colors, explosion.astype(np.int32))


# ===================================================================
# GEOMETRIC EFFECTS
# ===================================================================

def effect_depth_layers(colors, mask, coords, time):
    """Color by depth layers"""
    z_coords, y_coords, x_coords = coords
    layer = (z_coords[mask] + time * 5) % 40
    hue = (layer / 40 * 256).astype(np.int32)
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_cube_in_cube(colors, mask, coords, time):
    """Concentric cube pattern"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cx, cy, cz = grid_shape[2] / 2, grid_shape[1] / 2, grid_shape[0] / 2

    cube_dist = np.maximum(np.abs(x - cx), np.maximum(np.abs(y - cy), np.abs(z - cz)))
    hue = ((cube_dist * 20 + time * 30) % 256).astype(np.int32)
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_manhattan_distance(colors, mask, coords, time):
    """Color by Manhattan distance"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cx, cy, cz = grid_shape[2] / 2, grid_shape[1] / 2, grid_shape[0] / 2

    manhattan = np.abs(x - cx) + np.abs(y - cy) + np.abs(z - cz)
    hue = ((manhattan * 10 + time * 20) % 256).astype(np.int32)
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


# ===================================================================
# SYMMETRY EFFECTS
# ===================================================================

def effect_xz_mirror(colors, mask, coords, time):
    """XZ plane mirroring effect"""
    z_coords, y_coords, x_coords = coords
    mirrored_y = np.abs(y_coords[mask] - 10)  # Mirror around center
    hue = ((mirrored_y * 25 + time * 30) % 256).astype(np.int32)
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_directional_sweep(colors, mask, coords, time):
    """Directional color sweep"""
    z_coords, y_coords, x_coords = coords
    sweep = (x_coords[mask] + y_coords[mask] + z_coords[mask] + time * 10) % 60
    hue = (sweep / 60 * 256).astype(np.int32)
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


# ===================================================================
# CLASSIC EFFECTS
# ===================================================================

def effect_sparkle(colors, mask, coords, time):
    """Random sparkle"""
    sparkle_mask = np.random.random(np.sum(mask)) < 0.1
    colors_copy = colors.copy()
    colors_copy[sparkle_mask] = [255, 255, 255]
    return colors_copy


def effect_rainbow_sweep(colors, mask, coords, time):
    """Sweeping rainbow"""
    z_coords, y_coords, x_coords = coords
    rainbow = (x_coords[mask] + y_coords[mask] + time * 20) % 256
    sat = np.full_like(rainbow, 255, dtype=np.uint8)
    val = np.full_like(rainbow, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(rainbow.astype(np.int32), sat, val)


def effect_fire(colors, mask, coords, time):
    """Fire effect"""
    z_coords, y_coords, x_coords = coords
    heat = y_coords[mask] / 20.0
    flicker = 0.9 + 0.1 * np.sin(time * 10 + x_coords[mask] * 0.5)
    hue = ((1 - heat * flicker) * 60).astype(np.int32)  # Red to yellow
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = (heat * flicker * 255).astype(np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_plasma(colors, mask, coords, time):
    """Plasma effect"""
    z_coords, y_coords, x_coords = coords
    plasma = (
        np.sin(x_coords[mask] * 0.2 + time) +
        np.sin(y_coords[mask] * 0.3 + time * 1.3) +
        np.sin((x_coords[mask] + y_coords[mask]) * 0.15 + time * 0.7)
    )
    hue = ((plasma + 3) / 6 * 256).astype(np.int32) % 256
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_kaleidoscope(colors, mask, coords, time):
    """Kaleidoscope pattern"""
    z_coords, y_coords, x_coords = coords
    z, y, x = z_coords[mask], y_coords[mask], x_coords[mask]

    grid_shape = (z_coords.shape[0], y_coords.shape[1], x_coords.shape[2])
    cx, cy, cz = grid_shape[2] / 2, grid_shape[1] / 2, grid_shape[0] / 2

    angle = np.arctan2(y - cy, x - cx)
    mirrored_angle = np.abs(angle % (np.pi / 3))  # 6-fold symmetry
    distance = np.sqrt((x - cx)**2 + (y - cy)**2)

    pattern = np.sin(mirrored_angle * 3 + distance * 0.3 + time * 2)
    hue = ((pattern + 1) * 128).astype(np.int32) % 256
    sat = np.full_like(hue, 255, dtype=np.uint8)
    val = np.full_like(hue, 255, dtype=np.uint8)
    return vectorized_hsv_to_rgb(hue, sat, val)


def effect_breath(colors, time):
    """Breathing effect"""
    breath = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(time * 1.5))
    return (colors.astype(np.float32) * breath).astype(np.uint8)


def effect_color_chase(colors, mask, coords, time):
    """Chasing colors"""
    z_coords, y_coords, x_coords = coords
    chase_pos = (time * 15) % 60
    distance_from_chase = np.abs((x_coords[mask] + y_coords[mask] + z_coords[mask]) % 60 - chase_pos)
    brightness = np.clip(1.0 - distance_from_chase / 10, 0.2, 1.0)

    hue_offset = (time * 50).astype(np.int32) % 256
    colors_shifted = hue_shift(colors, hue_offset)
    return (colors_shifted.astype(np.float32) * brightness[..., np.newaxis]).astype(np.uint8)
