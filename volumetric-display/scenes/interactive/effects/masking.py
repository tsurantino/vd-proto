"""
Scrolling mask system
Provides various masking patterns: axis-aligned, diagonal, radial, spiral, wave, rings, noise
"""

import numpy as np


class MaskingSystem:
    """
    Manages scrolling mask effects with multiple pattern types.
    Also handles static gap masking for multi-cube configurations.
    """

    def __init__(self, coords_cache, gap_regions=None):
        """
        Initialize masking system.

        Args:
            coords_cache: Cached coordinate arrays (z, y, x)
            gap_regions: List of gap region dicts, e.g. [{"axis": "y", "min": 20, "max": 30}]
        """
        self.coords_cache = coords_cache
        self.gap_regions = gap_regions or []
        self.gap_mask_cache = None  # Static mask, computed once
        self.mask_phase = 0
        self.last_frame_time = 0

    def update_phase(self, time, params):
        """
        Update mask phase for smooth animation.

        Args:
            time: Current time
            params: SceneParameters with scrolling_speed
        """
        if self.last_frame_time > 0:
            delta_time = time - self.last_frame_time
            self.mask_phase += delta_time * params.scrolling_speed
        self.last_frame_time = time

    def _create_gap_mask(self, raster):
        """
        Create boolean mask where True = valid voxel (not in gap).

        Args:
            raster: Raster object with dimensions

        Returns:
            Boolean mask array, or None if no gaps defined
        """
        if not self.gap_regions:
            return None

        z_coords, y_coords, x_coords = self.coords_cache

        # Start with all True (all voxels valid)
        valid_mask = np.ones((raster.length, raster.height, raster.width), dtype=bool)

        for gap in self.gap_regions:
            axis = gap.get('axis', 'y')
            gap_min = gap.get('min', 0)
            gap_max = gap.get('max', 0)

            # Broadcast sparse coordinates to full grid
            if axis == 'x':
                coords = x_coords + y_coords * 0 + z_coords * 0
            elif axis == 'y':
                coords = y_coords + x_coords * 0 + z_coords * 0
            else:  # z
                coords = z_coords + y_coords * 0 + x_coords * 0

            # Mark gap voxels as invalid
            gap_region = (coords >= gap_min) & (coords < gap_max)
            valid_mask = valid_mask & ~gap_region

        return valid_mask

    def apply_mask(self, raster, params):
        """
        Apply gap mask (always) and scrolling mask (if enabled).

        Args:
            raster: Raster object to modify
            params: SceneParameters with scrolling settings
        """
        # Apply gap mask first (always, regardless of scrolling settings)
        if self.gap_regions:
            if self.gap_mask_cache is None:
                self.gap_mask_cache = self._create_gap_mask(raster)
            if self.gap_mask_cache is not None:
                raster.data[~self.gap_mask_cache] = 0

        # Apply scrolling mask if enabled
        if not params.scrolling_enabled or params.scrolling_thickness == 0:
            return

        mask = self.get_mask(raster, params)

        # Apply mask: normal mode masks out the band, inverted mode keeps only the band
        if params.scrolling_invert_mask:
            # Invert mask: keep only the masked area, turn off everything else
            raster.data[~mask] = 0
        else:
            # Normal: mask out the scrolling band itself
            raster.data[mask] = 0

    def get_mask(self, raster, params):
        """
        Calculate the mask for the scrolling band.

        Args:
            raster: Raster object with dimensions
            params: SceneParameters with scrolling settings

        Returns:
            Boolean mask array
        """
        z_coords, y_coords, x_coords = self.coords_cache
        direction = params.scrolling_direction

        # Convert percentage (0-100) to actual pixel thickness based on direction
        percentage = params.scrolling_thickness / 100.0

        # Calculate appropriate thickness for each direction type
        thickness = self._calculate_thickness(raster, direction, percentage)

        # Route to appropriate mask generator based on direction
        if direction in ['x', 'y', 'z']:
            return self._axis_aligned_mask(raster, params, direction, thickness)
        elif direction in ['diagonal-xz', 'diagonal-yz', 'diagonal-xy']:
            return self._diagonal_mask(raster, params, direction, thickness)
        elif direction == 'radial':
            return self._radial_mask(raster, params, thickness)
        elif direction == 'spiral':
            return self._spiral_mask(raster, params, thickness)
        elif direction == 'wave':
            return self._wave_mask(params, thickness)
        elif direction == 'rings':
            return self._rings_mask(raster, params, thickness)
        elif direction == 'noise':
            return self._noise_mask(params, thickness)
        else:
            # Fallback
            return np.ones_like(x_coords, dtype=bool)

    def _calculate_thickness(self, raster, direction, percentage):
        """Calculate pixel thickness based on direction type."""
        if direction in ['x', 'y', 'z']:
            max_dim = {
                'x': raster.width,
                'y': raster.height,
                'z': raster.length
            }[direction]
            return percentage * max_dim
        elif direction in ['diagonal-xz', 'diagonal-yz', 'diagonal-xy']:
            if direction == 'diagonal-xz':
                max_dim = np.sqrt(raster.width**2 + raster.length**2)
            elif direction == 'diagonal-yz':
                max_dim = np.sqrt(raster.height**2 + raster.length**2)
            else:  # diagonal-xy
                max_dim = np.sqrt(raster.width**2 + raster.height**2)
            return percentage * max_dim
        elif direction in ['radial', 'spiral', 'rings']:
            center_x = raster.width / 2
            center_y = raster.height / 2
            center_z = raster.length / 2
            max_radius = np.sqrt(center_x**2 + center_y**2 + center_z**2)
            return percentage * max_radius
        else:  # wave, noise
            # For wave and noise, use a normalized thickness
            return percentage * 20  # Map to 0-20 range for compatibility

    def _get_scroll_pos(self, max_dim, params):
        """Calculate scroll position with wrap or ping-pong."""
        raw_pos = self.mask_phase * 10
        if params.scrolling_loop:
            # Ping-pong: bounce back and forth
            cycle_length = max_dim * 2
            pos_in_cycle = raw_pos % cycle_length
            if pos_in_cycle > max_dim:
                return cycle_length - pos_in_cycle
            return pos_in_cycle
        else:
            # Wrap around (default)
            return raw_pos % max_dim

    def _axis_aligned_mask(self, raster, params, direction, thickness):
        """Simple axis-aligned scrolling."""
        z_coords, y_coords, x_coords = self.coords_cache

        max_dim = {
            'x': raster.width,
            'y': raster.height,
            'z': raster.length
        }[direction]

        scroll_pos = self._get_scroll_pos(max_dim, params)

        axis_coords = {
            'x': x_coords,
            'y': y_coords,
            'z': z_coords
        }[direction]

        # Force broadcast to full 3D grid
        axis_coords_broadcast = axis_coords + y_coords * 0 + x_coords * 0 + z_coords * 0

        # Calculate distance - use toroidal wrapping for smooth transitions
        if params.scrolling_loop:
            # In loop mode, use simple distance (no wrapping)
            dist_from_band = np.abs(axis_coords_broadcast - scroll_pos)
        else:
            # In wrap mode, use toroidal distance but cap the effective thickness
            linear_dist = np.abs(axis_coords_broadcast - scroll_pos)
            dist_from_band = np.minimum(linear_dist, max_dim - linear_dist)
            # Cap thickness to prevent full scene masking before 100%
            thickness = min(thickness, max_dim * 0.49)

        return dist_from_band < thickness

    def _diagonal_mask(self, raster, params, direction, thickness):
        """Diagonal scrolling (moving along two axes simultaneously)."""
        z_coords, y_coords, x_coords = self.coords_cache

        if direction == 'diagonal-xz':
            max_dim = np.sqrt(raster.width**2 + raster.length**2)
            diagonal_coord = (x_coords + z_coords + y_coords * 0) / np.sqrt(2)
        elif direction == 'diagonal-yz':
            max_dim = np.sqrt(raster.height**2 + raster.length**2)
            diagonal_coord = (y_coords + z_coords + x_coords * 0) / np.sqrt(2)
        else:  # diagonal-xy
            max_dim = np.sqrt(raster.width**2 + raster.height**2)
            diagonal_coord = (x_coords + y_coords + z_coords * 0) / np.sqrt(2)

        scroll_pos = self._get_scroll_pos(max_dim, params)

        if params.scrolling_loop:
            dist_from_band = np.abs(diagonal_coord - scroll_pos)
        else:
            linear_dist = np.abs(diagonal_coord - scroll_pos)
            dist_from_band = np.minimum(linear_dist, max_dim - linear_dist)
            thickness = min(thickness, max_dim * 0.49)

        return dist_from_band < thickness

    def _radial_mask(self, raster, params, thickness):
        """Radial scrolling (expanding/contracting from center)."""
        z_coords, y_coords, x_coords = self.coords_cache

        center_x = raster.width / 2
        center_y = raster.height / 2
        center_z = raster.length / 2

        # Distance from center
        radius = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2 + (z_coords - center_z)**2)
        max_radius = np.sqrt(center_x**2 + center_y**2 + center_z**2)

        scroll_pos = self._get_scroll_pos(max_radius, params)

        if params.scrolling_loop:
            dist_from_band = np.abs(radius - scroll_pos)
        else:
            linear_dist = np.abs(radius - scroll_pos)
            dist_from_band = np.minimum(linear_dist, max_radius - linear_dist)
            thickness = min(thickness, max_radius * 0.49)

        return dist_from_band < thickness

    def _spiral_mask(self, raster, params, thickness):
        """Spiral masking (combines radial and angular components)."""
        z_coords, y_coords, x_coords = self.coords_cache

        center_x = raster.width / 2
        center_y = raster.height / 2
        center_z = raster.length / 2

        # Force broadcast sparse coordinates to full 3D arrays
        x_full = x_coords + y_coords * 0 + z_coords * 0
        z_full = z_coords + y_coords * 0 + x_coords * 0

        # Calculate cylindrical coordinates (using Y as vertical axis)
        radius_xz = np.sqrt((x_full - center_x)**2 + (z_full - center_z)**2)
        angle = np.arctan2(z_full - center_z, x_full - center_x)

        # Create an Archimedean spiral: r = a + b*theta
        max_radius_xz = np.sqrt(center_x**2 + center_z**2)

        # Tightness: how much radius increases per radian
        spiral_tightness = (max_radius_xz / (2 * np.pi)) * 1.5

        # The spiral rotates over time
        time_rotation = self.mask_phase * 0.5
        # Normalize angle to [0, 2*pi] and add time rotation
        angle_normalized = (angle + np.pi + time_rotation) % (2 * np.pi)

        # Spiral equation: for a given angle, we expect a certain radius
        spiral_radius_expected = angle_normalized * spiral_tightness

        # Distance from the spiral curve
        dist_from_band = np.abs(radius_xz - spiral_radius_expected)

        return dist_from_band < thickness

    def _wave_mask(self, params, thickness):
        """Wave masking (3D sinusoidal wave)."""
        z_coords, y_coords, x_coords = self.coords_cache

        # Create a continuously flowing 3D wave
        wave_value = (
            np.sin(x_coords * 0.3 + self.mask_phase * 2) +
            np.cos(y_coords * 0.3 + self.mask_phase * 2) +
            np.sin(z_coords * 0.3 + self.mask_phase * 2)
        )
        # Wave value ranges from -3 to 3
        # Map thickness (0-20) to threshold (-3 to 3) for gradual masking
        threshold = -3.0 + (thickness / 20.0) * 6.0
        return wave_value < threshold

    def _rings_mask(self, raster, params, thickness):
        """Rings masking (concentric spherical shells)."""
        z_coords, y_coords, x_coords = self.coords_cache

        center_x = raster.width / 2
        center_y = raster.height / 2
        center_z = raster.length / 2

        # Distance from center (same as radial but with multiple rings)
        radius = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2 + (z_coords - center_z)**2)

        # Create pulsing rings by using modulo
        ring_period = 8  # Distance between rings
        ring_coord = (radius + self.mask_phase * 10) % ring_period

        # Scale thickness relative to ring_period (not max_radius)
        ring_thickness = (thickness / 20.0) * ring_period

        # Threshold creates the ring band
        return ring_coord < ring_thickness

    def _noise_mask(self, params, thickness):
        """Noise masking (Perlin-like noise pattern)."""
        z_coords, y_coords, x_coords = self.coords_cache

        # Create organic, cloud-like masking using multiple octaves of noise
        # Octave 1: large features
        noise1 = np.sin(x_coords * 0.2 + self.mask_phase) * \
                 np.cos(y_coords * 0.2 - self.mask_phase * 0.7) * \
                 np.sin(z_coords * 0.2 + self.mask_phase * 0.5)

        # Octave 2: medium features
        noise2 = np.sin(x_coords * 0.5 + self.mask_phase * 1.5) * \
                 np.cos(y_coords * 0.5 + self.mask_phase * 1.2) * \
                 np.sin(z_coords * 0.5 - self.mask_phase * 0.8)

        # Octave 3: fine features
        noise3 = np.sin(x_coords * 1.0 - self.mask_phase * 2) * \
                 np.cos(y_coords * 1.0 + self.mask_phase * 1.8) * \
                 np.sin(z_coords * 1.0 + self.mask_phase * 1.5)

        # Combine octaves with decreasing weights
        noise = noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2

        # Map thickness (0-20) to threshold (-1 to 1)
        threshold = -1.0 + (thickness / 20.0) * 2.0
        return noise < threshold
