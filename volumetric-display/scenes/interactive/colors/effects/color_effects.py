"""
ColorEffects - Refactored and Optimized
20 core effects with full-spectrum rainbow support and intelligent base color modulation
"""

import numpy as np
from .color_utils import hsl_to_rgb, rgb_to_hsl


class ColorEffects:
    """
    Advanced Color Effects Library

    Features:
    - Rainbow mode: Full-spectrum vibrant colors (ignores base color)
    - Base mode: Intelligent modulation of base color properties
    - 20 carefully curated effects (removed 30+ redundant ones)
    - Smooth animations with proper time/speed integration
    """

    def __init__(self, gridX, gridY, gridZ):
        self.gridX = gridX
        self.gridY = gridY
        self.gridZ = gridZ

        # State
        self.active_effect = 'none'
        self.intensity = 1.0
        self.speed = 1.0
        self.color_mode = 'rainbow'  # 'rainbow' or 'base'

        # Sparkle state - use 3D array for efficient vectorized operations
        # Values: NaN = not sparkling, float = start time of sparkle
        self.sparkle_map = np.full((gridZ, gridY, gridX), np.nan, dtype=np.float32)
        self.sparkle_frequency = 0.01
        self.sparkle_duration = 0.3

        # Voronoi state
        self.voronoi_seeds = []
        self.voronoi_cell_count = 5
        self._init_voronoi_seeds()

        # Perlin noise
        self.perlin_perm = self._generate_perlin_permutation()

    def set_effect(self, effect):
        """Set active effect"""
        if effect != self.active_effect:
            self.active_effect = effect
            if effect == 'sparkle':
                self.sparkle_map.fill(np.nan)

    def set_intensity(self, intensity):
        """Set effect intensity (0-1)"""
        self.intensity = np.clip(intensity, 0, 1)

    def set_speed(self, speed):
        """Set effect speed multiplier"""
        self.speed = np.clip(speed, 0.1, 5.0)

    def set_color_mode(self, mode):
        """Set color mode: 'rainbow' or 'base'"""
        self.color_mode = mode

    def apply_to_raster(self, raster_data, mask, coords, time):
        """
        Apply effect to raster data

        Args:
            raster_data: (L, H, W, 3) RGB array
            mask: (L, H, W) boolean mask
            coords: (z, y, x) coordinate cache (sparse)
            time: current animation time (from scene)
        """
        if not np.any(mask):
            return

        # Update sparkles if needed (time-based cleanup)
        if self.active_effect == 'sparkle':
            self._update_sparkles(time)

        # Update Voronoi if needed
        if self.active_effect == 'voronoi':
            # Calculate delta from last frame (approximate)
            delta_time = 1.0 / 60.0  # Assume 60 FPS
            self._update_voronoi_seeds(delta_time)

        # Get masked voxels
        base_colors = raster_data[mask].copy()

        # Apply effect (pass time directly)
        effect_colors = self._apply_effect(base_colors, mask, coords, time)

        # Blend based on intensity
        if self.intensity < 1.0:
            effect_colors = (base_colors * (1 - self.intensity) +
                           effect_colors * self.intensity).astype(np.uint8)

        raster_data[mask] = effect_colors

    def _apply_effect(self, base_colors, mask, coords, time):
        """Apply the selected effect"""
        effect = self.active_effect

        # Extract coordinates from sparse cache
        z_coords, y_coords, x_coords = coords

        # Get actual coordinate values at masked positions
        z_grid, y_grid, x_grid = np.meshgrid(
            z_coords[:, 0, 0],
            y_coords[0, :, 0],
            x_coords[0, 0, :],
            indexing='ij'
        )
        z = z_grid[mask]
        y = y_grid[mask]
        x = x_grid[mask]

        # Route to effect handler (only 20 effects)
        if effect == 'none':
            return base_colors

        # Wave/Flow effects (5)
        elif effect == 'waveCircular':
            return self._effect_wave_circular(base_colors, x, y, z, time)
        elif effect == 'waveVertical':
            return self._effect_wave_vertical(base_colors, x, y, z, time)
        elif effect == 'sineInterferenceXZ':
            return self._effect_sine_interference_xz(base_colors, x, y, z, time)
        elif effect == 'rainbowSweep':
            return self._effect_rainbow_sweep(base_colors, x, y, z, time)
        elif effect == 'directionalSweep':
            return self._effect_directional_sweep(base_colors, x, y, z, time)

        # Geometric effects (5)
        elif effect == 'helix':
            return self._effect_helix(base_colors, x, y, z, time)
        elif effect == 'vortex':
            return self._effect_vortex(base_colors, x, y, z, time)
        elif effect == 'tunnel':
            return self._effect_tunnel(base_colors, x, y, z, time)
        elif effect == 'sphericalShellsMoving':
            return self._effect_spherical_shells(base_colors, x, y, z, time)
        elif effect == 'cubeInCube':
            return self._effect_cube_in_cube(base_colors, x, y, z, time)

        # Procedural effects (3)
        elif effect == 'perlinNoise':
            return self._effect_perlin_noise(base_colors, x, y, z, time)
        elif effect == 'voronoi':
            return self._effect_voronoi(base_colors, x, y, z, time)
        elif effect == 'plasma':
            return self._effect_plasma(base_colors, x, y, z, time)

        # Combination effects (4)
        elif effect == 'pulseWave':
            return self._effect_pulse_wave(base_colors, x, y, z, time)
        elif effect == 'waveChase':
            return self._effect_wave_chase(base_colors, x, y, z, time)
        elif effect == 'cyclePulse':
            return self._effect_cycle_pulse(base_colors, x, y, z, time)
        elif effect == 'kaleidoscope':
            return self._effect_kaleidoscope(base_colors, x, y, z, time)

        # Classic effects (3)
        elif effect == 'sparkle':
            return self._effect_sparkle(base_colors, x, y, z, time)
        elif effect == 'fire':
            return self._effect_fire(base_colors, x, y, z, time)
        elif effect == 'breath':
            return self._effect_breath(base_colors, time)

        return base_colors

    # ============================================================
    # CORE HELPER: COLOR MODE APPLICATION
    # ============================================================

    def _apply_color_mode(self, base_colors, rainbow_colors, pattern_value):
        """
        Apply color mode logic (KEY FIX for vibrant effects)

        Args:
            base_colors: Original voxel colors (N, 3) RGB
            rainbow_colors: Generated rainbow colors (N, 3) RGB
            pattern_value: Pattern intensity 0-1 for base mode modulation

        Returns:
            Final colors respecting color_mode setting
        """
        if self.color_mode == 'rainbow':
            # Rainbow mode: Return generated colors directly (full spectrum)
            return rainbow_colors
        else:
            # Base mode: Modulate base color lightness based on pattern
            h, s, l = rgb_to_hsl(base_colors[:, 0], base_colors[:, 1], base_colors[:, 2])

            # Vary lightness based on pattern (0.2 to 0.8 range)
            new_lightness = 0.2 + pattern_value * 0.6

            return hsl_to_rgb(h, s, new_lightness)

    # ============================================================
    # WAVE/FLOW EFFECTS (5)
    # ============================================================

    def _effect_wave_circular(self, colors, x, y, z, time):
        """Expanding circular waves from center - VIBRANT"""
        dx = x - self.gridX / 2
        dz = z - self.gridZ / 2
        dist = np.sqrt(dx**2 + dz**2)

        wave = np.sin(dist * 0.5 - time * self.speed * 3)
        pattern_value = (wave + 1) / 2  # 0-1

        # Generate full-spectrum hue (0-360°)
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_wave_vertical(self, colors, x, y, z, time):
        """Vertical color bands moving up/down"""
        wave = np.sin(y * 0.3 - time * self.speed * 2)
        pattern_value = (wave + 1) / 2  # 0-1

        # Full spectrum hue
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_sine_interference_xz(self, colors, x, y, z, time):
        """Complex wave interference patterns"""
        wave1 = np.sin(x * 0.3 - time * self.speed * 2)
        wave2 = np.sin(z * 0.3 - time * self.speed * 2.5)
        wave3 = np.sin((x + z) * 0.2 - time * self.speed * 1.8)
        wave4 = np.sin((x - z) * 0.2 + time * self.speed * 2.2)

        interference = (wave1 + wave2 + wave3 + wave4) / 4
        pattern_value = (interference + 1) / 2  # 0-1

        # Full spectrum
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_rainbow_sweep(self, colors, x, y, z, time):
        """Sweeping rainbow across entire space"""
        # Create a wave that sweeps through space
        wave = (x + y + z + time * self.speed * 20) * 0.01
        pattern_value = wave % 1.0  # 0-1

        # Full spectrum sweep
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_directional_sweep(self, colors, x, y, z, time):
        """Rotating directional wave sweep"""
        # Rotating direction vector
        angle = time * self.speed * 0.3
        dir_x = np.cos(angle)
        dir_y = np.sin(angle * 0.7)
        dir_z = np.sin(angle * 0.5)

        # Normalize
        length = np.sqrt(dir_x**2 + dir_y**2 + dir_z**2)
        nx, ny, nz = dir_x / length, dir_y / length, dir_z / length

        # Distance along direction
        dist = x * nx + y * ny + z * nz
        wave = np.sin(dist * 0.2 - time * self.speed * 2)
        pattern_value = (wave + 1) / 2  # 0-1

        # Full spectrum
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    # ============================================================
    # GEOMETRIC EFFECTS (5)
    # ============================================================

    def _effect_helix(self, colors, x, y, z, time):
        """Twisting spiral around vertical axis"""
        cx = x - self.gridX / 2
        cz = z - self.gridZ / 2

        radius = np.sqrt(cx**2 + cz**2)
        angle = np.arctan2(cz, cx)

        # Create helix rotation
        helix_angle = angle + y * 0.3 + time * self.speed
        pattern_value = ((helix_angle / (np.pi * 2)) % 1.0 + 1) % 1.0  # 0-1

        # Full spectrum hue
        hue = pattern_value

        # Saturation varies with radius for depth
        saturation = np.clip(0.7 + np.sin(radius * 0.2) * 0.3, 0, 1)
        rainbow_color = hsl_to_rgb(hue, saturation, np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_vortex(self, colors, x, y, z, time):
        """Swirling tornado vortex"""
        cx = x - self.gridX / 2
        cy = y - self.gridY / 2
        cz = z - self.gridZ / 2

        radius = np.sqrt(cx**2 + cz**2)
        angle = np.arctan2(cz, cx)

        # Vortex rotation speed increases towards center
        angular_speed = np.where(radius > 0, 10 / (radius + 1), 10)
        vortex_angle = angle + angular_speed * time * self.speed

        # Combine rotation with height for spiral pattern
        pattern_value = ((vortex_angle / (np.pi * 2)) % 1.0 + cy / self.gridY * 0.3) % 1.0

        # Full spectrum
        hue = pattern_value

        # Brightness varies with radius (brighter at center)
        lightness = np.clip(0.3 + 0.5 / (1 + radius * 0.1), 0, 1)
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), lightness)

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_tunnel(self, colors, x, y, z, time):
        """Perspective tunnel with animated color bands"""
        cx = x - self.gridX / 2
        cy = y - self.gridY / 2

        # Rectangular tunnel distance
        dist_x = np.abs(cx) / (self.gridX / 2)
        dist_y = np.abs(cy) / (self.gridY / 2)
        tunnel_dist = np.maximum(dist_x, dist_y)

        # Depth component
        depth = z / self.gridZ

        # Create traveling bands
        bands = (depth + tunnel_dist + time * self.speed * 0.3) * 10
        pattern_value = bands % 1.0

        # Full spectrum
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_spherical_shells(self, colors, x, y, z, time):
        """Expanding/contracting spherical bubble shells"""
        # Moving center point
        center_x = self.gridX / 2 + np.sin(time * self.speed * 0.5) * self.gridX * 0.3
        center_y = self.gridY / 2 + np.cos(time * self.speed * 0.7) * self.gridY * 0.3
        center_z = self.gridZ / 2 + np.sin(time * self.speed * 0.3) * self.gridZ * 0.3

        dx = x - center_x
        dy = y - center_y
        dz = z - center_z
        dist = np.sqrt(dx**2 + dy**2 + dz**2)

        # Concentric shells
        shell = (dist + time * self.speed * 5) % 10
        pattern_value = shell / 10  # 0-1

        # Full spectrum
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_cube_in_cube(self, colors, x, y, z, time):
        """Concentric cubic shells"""
        cx = np.abs(x - self.gridX / 2) / (self.gridX / 2)
        cy = np.abs(y - self.gridY / 2) / (self.gridY / 2)
        cz = np.abs(z - self.gridZ / 2) / (self.gridZ / 2)

        # Distance to nearest cube face
        cube_dist = np.maximum(cx, np.maximum(cy, cz))

        # Create shells
        shell = (cube_dist * 10 + time * self.speed * 2) % 10
        pattern_value = shell / 10  # 0-1

        # Full spectrum
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    # ============================================================
    # PROCEDURAL EFFECTS (3)
    # ============================================================

    def _effect_perlin_noise(self, colors, x, y, z, time):
        """Organic cloud-like flowing patterns"""
        scale = 0.1
        noise = self._perlin_noise_3d(
            x * scale,
            y * scale,
            (z + time * self.speed * 5) * scale
        )

        # Map noise (-1 to 1) to pattern value (0-1)
        pattern_value = (noise + 1) / 2

        # Full spectrum hue
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 0.8), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_voronoi(self, colors, x, y, z, time):
        """Cellular/organic voronoi regions"""
        min_dist = np.full(len(x), np.inf)
        nearest_hue = np.zeros(len(x))

        for seed in self.voronoi_seeds:
            dx = x - seed['x']
            dy = y - seed['y']
            dz = z - seed['z']
            dist = np.sqrt(dx**2 + dy**2 + dz**2)

            mask = dist < min_dist
            min_dist[mask] = dist[mask]
            nearest_hue[mask] = seed['hue']

        pattern_value = nearest_hue  # Already 0-1

        # Full spectrum
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_plasma(self, colors, x, y, z, time):
        """Multi-sine wave interference plasma"""
        nx = x / self.gridX
        ny = y / self.gridY
        nz = z / self.gridZ

        # Multiple sine waves
        v1 = np.sin(nx * 10 + time * self.speed)
        v2 = np.sin(ny * 10 - time * self.speed * 0.7)
        v3 = np.sin((nx + ny + nz) * 8 + time * self.speed * 0.5)
        v4 = np.sin(np.sqrt((nx - 0.5)**2 + (nz - 0.5)**2) * 20 + time * self.speed)

        plasma = (v1 + v2 + v3 + v4) / 4
        pattern_value = (plasma + 1) / 2  # 0-1

        # Full spectrum (map to 0-360°)
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    # ============================================================
    # COMBINATION EFFECTS (4)
    # ============================================================

    def _effect_pulse_wave(self, colors, x, y, z, time):
        """Pulsing circular waves"""
        dx = x - self.gridX / 2
        dz = z - self.gridZ / 2
        dist = np.sqrt(dx**2 + dz**2)

        # Wave component
        wave = np.sin(dist * 0.3 - time * self.speed * 2)

        # Pulse component
        pulse = np.sin(time * self.speed * 5)

        # Combine
        combined = wave * (0.5 + pulse * 0.5)
        pattern_value = (combined + 1) / 2  # 0-1

        # Full spectrum
        hue = pattern_value
        rainbow_color = hsl_to_rgb(hue, np.full(len(hue), 1.0), np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_wave_chase(self, colors, x, y, z, time):
        """Multiple colored waves chasing each other"""
        dx = x - self.gridX / 2
        dz = z - self.gridZ / 2
        dist = np.sqrt(dx**2 + dz**2)

        # Three waves with different speeds and phases
        wave1 = np.sin(dist * 0.3 - time * self.speed * 2)
        wave2 = np.sin(dist * 0.3 - time * self.speed * 2.3 + np.pi / 3)
        wave3 = np.sin(dist * 0.3 - time * self.speed * 2.6 + 2 * np.pi / 3)

        # Map each wave to RGB channels for chasing effect
        r = ((wave1 + 1) / 2) * 255
        g = ((wave2 + 1) / 2) * 255
        b = ((wave3 + 1) / 2) * 255

        rainbow_color = np.stack([r, g, b], axis=1).astype(np.uint8)

        # Pattern value for base mode
        pattern_value = (wave1 + wave2 + wave3 + 3) / 6  # Average normalized

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_cycle_pulse(self, colors, x, y, z, time):
        """Color cycling with pulsing brightness"""
        # Hue cycles over time
        hue = (time * self.speed * 0.2) % 1.0
        hue_array = np.full(len(x), hue)

        # Brightness pulses
        pulse = np.sin(time * self.speed * 3)
        lightness = 0.3 + ((pulse + 1) / 2) * 0.5  # 0.3 to 0.8

        rainbow_color = hsl_to_rgb(
            hue_array,
            np.full(len(x), 1.0),
            np.full(len(x), lightness)
        )

        pattern_value = (pulse + 1) / 2

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    def _effect_kaleidoscope(self, colors, x, y, z, time):
        """Mirror symmetry with rotating colors"""
        # Mirror coordinates from center
        cx = np.abs(x - self.gridX / 2)
        cy = np.abs(y - self.gridY / 2)
        cz = np.abs(z - self.gridZ / 2)

        # Create radial pattern
        angle = np.arctan2(cy, cx) + time * self.speed * 0.5
        radius = np.sqrt(cx**2 + cz**2)

        # 6-fold symmetry
        segments = 6
        segment_angle = (angle * segments) % (np.pi * 2)

        # Map to hue with radius influence
        pattern_value = (segment_angle / (np.pi * 2) + radius * 0.01) % 1.0

        # Full spectrum
        hue = pattern_value

        # Enhanced saturation for kaleidoscope effect
        saturation = np.full(len(hue), 0.9)

        rainbow_color = hsl_to_rgb(hue, saturation, np.full(len(hue), 0.5))

        return self._apply_color_mode(colors, rainbow_color, pattern_value)

    # ============================================================
    # CLASSIC EFFECTS (3)
    # ============================================================

    def _effect_sparkle(self, colors, x, y, z, time):
        """Random white sparkles - always overrides color"""
        result = colors.copy()

        # Convert coordinates to integers for indexing
        xi = x.astype(int)
        yi = y.astype(int)
        zi = z.astype(int)

        # Get sparkle start times
        sparkle_times = self.sparkle_map[zi, yi, xi]

        # Check which voxels are currently sparkling
        is_sparkling = ~np.isnan(sparkle_times)

        if np.any(is_sparkling):
            # Calculate brightness for sparkling voxels
            elapsed = time - sparkle_times[is_sparkling]
            t = elapsed / self.sparkle_duration

            # Fade in (0-0.3) and fade out (0.3-1.0)
            brightness = np.where(t < 0.3, t / 0.3, (1 - t) / 0.7)
            brightness = np.clip(brightness, 0, 1)

            # Set to white with calculated brightness
            result[is_sparkling] = (255 * brightness[:, np.newaxis]).astype(np.uint8)

        # Randomly start new sparkles
        random_vals = np.random.rand(len(x))
        should_sparkle = random_vals < self.sparkle_frequency

        # Only start sparkles on voxels that aren't already sparkling
        new_sparkles = should_sparkle & ~is_sparkling

        if np.any(new_sparkles):
            self.sparkle_map[zi[new_sparkles], yi[new_sparkles], xi[new_sparkles]] = time

        return result

    def _effect_fire(self, colors, x, y, z, time):
        """Flickering fire with red/orange/yellow colors"""
        # More intense at bottom, cooler at top
        height_factor = 1 - (y / self.gridY)

        # Flicker using multiple noise functions
        flicker = (np.sin(time * self.speed * 5 + x * 0.3 + z * 0.3) * 0.3 +
                  np.sin(time * self.speed * 8 + x * 0.5) * 0.2)

        intensity = (height_factor * 0.7 + 0.3) + flicker
        intensity = np.clip(intensity, 0, 1)

        # Temperature determines color: hot (yellow) to cool (red)
        temp = height_factor + np.sin(time * self.speed * 3 + y * 0.1) * 0.3

        # Fire colors
        r = np.full(len(x), 255)
        g = np.where(temp > 0.7, 255, np.where(temp > 0.3, 150, 50))
        b = np.where(temp > 0.7, 100, np.where(temp > 0.3, 50, 0))

        fire_color = np.stack([r * intensity, g * intensity, b * intensity], axis=1).astype(np.uint8)

        # Fire always generates its own colors (ignore color mode)
        return fire_color

    def _effect_breath(self, colors, time):
        """Slow breathing saturation modulation"""
        # Convert to HSL
        h, s, l = rgb_to_hsl(colors[:, 0], colors[:, 1], colors[:, 2])

        # Oscillate saturation slowly
        breath_cycle = (np.sin(time * self.speed * 1.5) + 1) / 2  # 0-1
        new_saturation = 0.3 + breath_cycle * 0.7  # 0.3-1.0

        return hsl_to_rgb(h, np.full(len(h), new_saturation), l)

    # ============================================================
    # PERLIN NOISE HELPERS
    # ============================================================

    def _perlin_fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _perlin_lerp(self, t, a, b):
        return a + t * (b - a)

    def _perlin_grad(self, hash_val, x, y, z):
        h = hash_val & 15
        u = np.where(h < 8, x, y)
        v = np.where(h < 4, y, np.where((h == 12) | (h == 14), x, z))
        return np.where((h & 1) == 0, u, -u) + np.where((h & 2) == 0, v, -v)

    def _perlin_noise_3d(self, x, y, z):
        """3D Perlin noise - vectorized implementation"""
        X = np.floor(x).astype(int) & 255
        Y = np.floor(y).astype(int) & 255
        Z = np.floor(z).astype(int) & 255

        x = x - np.floor(x)
        y = y - np.floor(y)
        z = z - np.floor(z)

        u = self._perlin_fade(x)
        v = self._perlin_fade(y)
        w = self._perlin_fade(z)

        p = self.perlin_perm
        A = (p[X] + Y) & 255
        AA = (p[A] + Z) & 255
        AB = (p[(A + 1) & 255] + Z) & 255
        B = (p[(X + 1) & 255] + Y) & 255
        BA = (p[B] + Z) & 255
        BB = (p[(B + 1) & 255] + Z) & 255

        return self._perlin_lerp(w,
            self._perlin_lerp(v,
                self._perlin_lerp(u, self._perlin_grad(p[AA], x, y, z),
                                    self._perlin_grad(p[BA], x - 1, y, z)),
                self._perlin_lerp(u, self._perlin_grad(p[AB], x, y - 1, z),
                                    self._perlin_grad(p[BB], x - 1, y - 1, z))),
            self._perlin_lerp(v,
                self._perlin_lerp(u, self._perlin_grad(p[(AA + 1) & 255], x, y, z - 1),
                                    self._perlin_grad(p[(BA + 1) & 255], x - 1, y, z - 1)),
                self._perlin_lerp(u, self._perlin_grad(p[(AB + 1) & 255], x, y - 1, z - 1),
                                    self._perlin_grad(p[(BB + 1) & 255], x - 1, y - 1, z - 1))))

    # ============================================================
    # STATE MANAGEMENT HELPERS
    # ============================================================

    def _update_sparkles(self, time):
        """Remove expired sparkles - vectorized"""
        is_sparkling = ~np.isnan(self.sparkle_map)

        if np.any(is_sparkling):
            elapsed = time - self.sparkle_map[is_sparkling]
            expired = elapsed > self.sparkle_duration

            if np.any(expired):
                expired_mask = np.zeros_like(self.sparkle_map, dtype=bool)
                expired_mask[is_sparkling] = expired
                self.sparkle_map[expired_mask] = np.nan

    def _init_voronoi_seeds(self):
        """Initialize Voronoi seed points"""
        self.voronoi_seeds = []
        for i in range(self.voronoi_cell_count):
            self.voronoi_seeds.append({
                'x': np.random.rand() * self.gridX,
                'y': np.random.rand() * self.gridY,
                'z': np.random.rand() * self.gridZ,
                'hue': np.random.rand(),
                'vx': (np.random.rand() - 0.5) * 2,
                'vy': (np.random.rand() - 0.5) * 2,
                'vz': (np.random.rand() - 0.5) * 2
            })

    def _update_voronoi_seeds(self, delta_time):
        """Update Voronoi seed positions"""
        for seed in self.voronoi_seeds:
            seed['x'] += seed['vx'] * delta_time * self.speed
            seed['y'] += seed['vy'] * delta_time * self.speed
            seed['z'] += seed['vz'] * delta_time * self.speed

            # Bounce off walls
            if seed['x'] < 0 or seed['x'] > self.gridX:
                seed['vx'] *= -1
            if seed['y'] < 0 or seed['y'] > self.gridY:
                seed['vy'] *= -1
            if seed['z'] < 0 or seed['z'] > self.gridZ:
                seed['vz'] *= -1

            seed['x'] = np.clip(seed['x'], 0, self.gridX)
            seed['y'] = np.clip(seed['y'], 0, self.gridY)
            seed['z'] = np.clip(seed['z'], 0, self.gridZ)

    def _generate_perlin_permutation(self):
        """Generate Perlin noise permutation table"""
        p = list(range(256))
        np.random.shuffle(p)
        return np.array(p + p, dtype=np.int32)
