"""
Interactive Scene with Layered Architecture
Geometry → Color Effects → Global Effects
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any
from artnet import Scene, Raster

# Import geometry generators
from .geometry.shapes import (
    generate_sphere, generate_pulsing_sphere, generate_helix,
    generate_cube, generate_torus, generate_pyramid
)
from .geometry.waves import (
    generate_ripple_wave, generate_plane_wave,
    generate_standing_wave, generate_interference_wave
)

# Import color utilities
from .colors.utils import (
    vectorized_hsv_to_rgb, parse_hex_color, parse_gradient,
    apply_color_to_mask, rainbow_color, hue_shift
)


@dataclass
class SceneParameters:
    """Live parameters controlled by web UI"""
    # Scene/Geometry
    scene_type: str = 'shapeMorph'
    size: float = 1.0
    density: float = 0.5
    objectCount: int = 1
    frequency: float = 1.0
    amplitude: float = 0.5
    animationSpeed: float = 1.0

    # Movement
    rotationX: float = 0.0
    rotationY: float = 0.0
    rotationZ: float = 0.0

    # Color system
    color_type: str = 'single'  # 'single' or 'gradient'
    color_single: str = '#64C8FF'
    color_gradient: str = '#FF0000,#0000FF'
    color_effect: str = 'none'
    color_effect_intensity: float = 1.0
    color_mode: str = 'rainbow'  # 'rainbow' or 'base'
    color_speed: float = 1.0

    # Global effects
    decay: float = 0.0
    strobe: str = 'off'
    pulse: str = 'off'
    invert: bool = False
    scrolling_enabled: bool = False
    scrolling_thickness: int = 0  # Now represents percentage (0-100)
    scrolling_direction: str = 'y'
    scrolling_speed: float = 1.0
    scrolling_loop: bool = False
    scrolling_invert_mask: bool = False

    # Scene-specific params
    scene_params: Dict[str, Any] = field(default_factory=dict)


class InteractiveScene(Scene):
    """
    Main scene class with layered rendering:
    1. Generate geometry (voxel positions/mask)
    2. Apply color effects
    3. Apply global effects
    """

    def __init__(self, **kwargs):
        self.properties = kwargs.get("properties")
        self.params = SceneParameters()

        # Initialize with rainbow scene
        self.params.scene_type = 'rainbow'

        # Coordinate cache
        self.coords_cache = None
        self.grid_shape = None

        # Previous frame for decay
        self.previous_frame = None

        # Color time tracking
        self.color_time = 0

        # Animation time tracking for smooth speed changes
        self.animation_time = 0

        # Mask phase tracking for smooth speed changes
        self.mask_phase = 0
        self.last_frame_time = 0

        print(f"✨ InteractiveScene v2.0 initialized (modular architecture)")

    def update_parameters(self, params_dict: Dict[str, Any]):
        """Update scene parameters from web UI"""
        for key, value in params_dict.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
            else:
                # Scene-specific params
                self.params.scene_params[key] = value

        # Debug logging for scrolling parameters
        if 'scrolling_thickness' in params_dict or 'scrolling_enabled' in params_dict:
            print(f"🔄 SCROLL UPDATE: enabled={self.params.scrolling_enabled}, thickness={self.params.scrolling_thickness}, direction={self.params.scrolling_direction}")
        if 'strobe' in params_dict:
            print(f"⚡ STROBE UPDATE: {self.params.strobe}")
        if 'pulse' in params_dict:
            print(f"💓 PULSE UPDATE: {self.params.pulse}")

    def render(self, raster: Raster, time: float):
        """
        Main render method - layered pipeline:
        1. Generate geometry
        2. Apply colors
        3. Apply global effects
        """
        # Initialize coord cache
        if self.coords_cache is None:
            self._init_coords(raster)

        # Initialize previous frame
        if self.previous_frame is None:
            self.previous_frame = np.zeros_like(raster.data)

        # Update color time
        self.color_time += 1.0 / 60.0 * self.params.color_speed

        # Update animation time and mask phase for smooth speed transitions
        if self.last_frame_time > 0:
            delta_time = time - self.last_frame_time
            self.animation_time += delta_time * self.params.animationSpeed
            self.mask_phase += delta_time * self.params.scrolling_speed
        self.last_frame_time = time

        # Apply decay/trail effect
        if self.params.decay == 0:
            # No trail: start with a clean slate
            raster.data.fill(0)
        else:
            # Create fading trail by starting with decayed previous frame
            # Higher decay = longer trails (slower fade)
            # Decay range: 0 to 3, map to fade factor
            # decay=1.0 -> 58% retention, decay=2.0 -> 76%, decay=3.0 -> 94%
            fade_factor = 0.4 + (self.params.decay * 0.18)
            raster.data[:] = (self.previous_frame * fade_factor).astype(np.uint8)

        # LAYER 1: Generate geometry
        mask = self._generate_geometry(raster, self.animation_time)

        # LAYER 2: Apply colors (draws on top of decayed frame)
        self._apply_colors(raster, mask, self.animation_time)

        # LAYER 3: Apply global effects
        self._apply_global_effects(raster, time)

        # Store frame for decay
        self.previous_frame[:] = raster.data

    def _init_coords(self, raster):
        """Initialize coordinate grids"""
        self.coords_cache = np.indices(
            (raster.length, raster.height, raster.width),
            sparse=True
        )
        self.grid_shape = (raster.length, raster.height, raster.width)

    # ================================================================
    # LAYER 1: GEOMETRY GENERATION
    # ================================================================

    def _generate_geometry(self, raster, time):
        """Generate geometry mask based on scene type"""
        scene_type = self.params.scene_type

        if scene_type == 'shapeMorph':
            return self._geometry_shape_morph(raster, time)
        elif scene_type == 'waveField':
            return self._geometry_wave_field(raster, time)
        elif scene_type == 'particleFlow':
            return self._geometry_particle_flow(raster, time)
        elif scene_type == 'procedural':
            return self._geometry_procedural(raster, time)
        elif scene_type == 'rainbow':
            return self._geometry_rainbow(raster, time)
        else:
            # Default: fill entire volume
            return np.ones((raster.length, raster.height, raster.width), dtype=bool)

    def _geometry_shape_morph(self, raster, time):
        """Shape morph geometry"""
        shape = self.params.scene_params.get('shape', 'sphere')
        size = self.params.size

        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )

        if shape == 'sphere':
            radius = min(center) * size * 0.8
            return generate_pulsing_sphere(
                self.coords_cache, center, radius, time,
                pulse_speed=2, pulse_amount=2
            )

        elif shape == 'helix':
            radius = min(center[0], center[2]) * size * 0.5
            mask = np.zeros(self.grid_shape, dtype=bool)
            for i in range(max(1, self.params.objectCount)):
                helix_mask = generate_helix(
                    self.coords_cache, center, radius,
                    (0, raster.height), time,
                    rotation_speed=self.params.rotationY * 2,
                    num_strands=self.params.objectCount,
                    strand_index=i,
                    thickness=int(3 * size)
                )
                mask |= helix_mask
            return mask

        elif shape == 'cube':
            cube_size = min(center) * size * 0.8
            return generate_cube(self.coords_cache, center, cube_size)

        elif shape == 'torus':
            major_r = min(center[0], center[2]) * size * 0.6
            minor_r = major_r * 0.3
            return generate_torus(self.coords_cache, center, major_r, minor_r)

        elif shape == 'pyramid':
            base_size = min(center[0], center[2]) * size * 0.6
            height = center[1] * size * 1.2
            return generate_pyramid(self.coords_cache, center, base_size, height)

        else:
            # Default sphere
            radius = min(center) * size * 0.8
            return generate_sphere(self.coords_cache, center, radius)

    def _geometry_wave_field(self, raster, time):
        """Wave field geometry"""
        wave_type = self.params.scene_params.get('waveType', 'ripple')

        if wave_type == 'ripple':
            return generate_ripple_wave(
                self.coords_cache, self.grid_shape, time,
                frequency=self.params.frequency,
                amplitude=self.params.amplitude,
                speed=5
            )
        elif wave_type == 'plane':
            return generate_plane_wave(
                self.coords_cache, self.grid_shape, time,
                amplitude=self.params.amplitude,
                speed=3
            )
        elif wave_type == 'standing':
            return generate_standing_wave(
                self.coords_cache, self.grid_shape, time,
                frequency=self.params.frequency,
                amplitude=self.params.amplitude
            )
        elif wave_type == 'interference':
            mask, _ = generate_interference_wave(
                self.coords_cache, self.grid_shape, time,
                frequency=self.params.frequency,
                amplitude=self.params.amplitude
            )
            return mask
        else:
            return generate_ripple_wave(
                self.coords_cache, self.grid_shape, time,
                frequency=self.params.frequency,
                amplitude=self.params.amplitude
            )

    def _geometry_particle_flow(self, raster, time):
        """Particle flow geometry"""
        pattern = self.params.scene_params.get('pattern', 'particles')
        z_coords, y_coords, x_coords = self.coords_cache

        mask = np.zeros(self.grid_shape, dtype=bool)
        num_particles = int(100 * self.params.density)

        for i in range(num_particles):
            seed = i * 12345
            px = ((seed % raster.width) + time * 5 * (1 + i % 3)) % raster.width
            py = ((seed * 7 % raster.height) + time * 3 * (1 + i % 2)) % raster.height
            pz = ((seed * 13 % raster.length) + time * 4 * (1 + i % 4)) % raster.length

            dx = x_coords - px
            dy = y_coords - py
            dz = z_coords - pz
            distance = np.sqrt(dx**2 + dy**2 + dz**2)

            particle_size = 2 * self.params.size
            mask |= distance < particle_size

        return mask

    def _geometry_procedural(self, raster, time):
        """Procedural noise geometry"""
        z_coords, y_coords, x_coords = self.coords_cache

        scale = self.params.size * 0.1
        threshold = self.params.amplitude * 0.5

        noise = (
            np.sin(x_coords * scale + time) *
            np.cos(y_coords * scale - time * 0.5) *
            np.sin(z_coords * scale + time * 0.3)
        )

        noise += 0.5 * (
            np.sin(x_coords * scale * 2 - time * 1.5) *
            np.cos(z_coords * scale * 2 + time)
        )

        noise = (noise + 1.5) / 3.0
        return noise > threshold

    def _geometry_rainbow(self, raster, time):
        """Rainbow fills entire volume"""
        return np.ones(self.grid_shape, dtype=bool)

    # ================================================================
    # LAYER 2: COLOR APPLICATION
    # ================================================================

    def _apply_colors(self, raster, mask, time):
        """Apply colors to geometry mask"""
        if not np.any(mask):
            return

        if self.params.color_mode == 'rainbow':
            self._apply_rainbow_colors(raster, mask, time)
        else:
            self._apply_base_colors(raster, mask, time)

        # Apply color effect
        self._apply_color_effect(raster, mask, time)

    def _apply_rainbow_colors(self, raster, mask, time):
        """Apply rainbow coloring"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Rainbow based on position + time
        hue = (x_coords + y_coords + z_coords) * 4 + self.color_time * 50
        hue = hue.astype(np.int32) % 256

        saturation = np.full_like(hue, 255, dtype=np.uint8)
        value = np.full_like(hue, 255, dtype=np.uint8)

        colors = vectorized_hsv_to_rgb(hue, saturation, value)
        raster.data[mask] = colors[mask]

    def _apply_base_colors(self, raster, mask, time):
        """Apply solid or gradient base colors"""
        if self.params.color_type == 'single':
            color = parse_hex_color(self.params.color_single)
            raster.data[mask] = color
        else:
            # Gradient (simple Y-axis for now)
            gradient_colors = parse_gradient(self.params.color_gradient)
            z_coords, y_coords, x_coords = self.coords_cache

            # Interpolate along Y axis
            t = y_coords[mask] / raster.height
            from .colors.utils import interpolate_colors
            positions = np.linspace(0, 1, len(gradient_colors))
            colors = interpolate_colors(gradient_colors, positions, t)
            raster.data[mask] = colors

    def _apply_color_effect(self, raster, mask, time):
        """Apply color effect to existing colors using comprehensive effects module"""
        effect = self.params.color_effect
        intensity = self.params.color_effect_intensity

        if effect == 'none' or intensity == 0:
            return

        # Import and apply effect from comprehensive effects module
        from .colors.all_effects import apply_color_effect
        apply_color_effect(
            raster.data, mask, self.coords_cache,
            self.color_time, effect, intensity
        )

    # ================================================================
    # LAYER 3: GLOBAL EFFECTS
    # ================================================================

    def _apply_global_effects(self, raster, time):
        """
        Apply global post-processing effects.

        Design:
        1. Strobe/Pulse apply globally to entire scene
        2. Scrolling is an independent masking effect applied after strobe/pulse
        """
        print(f"🎯 EFFECTS: strobe={self.params.strobe}, pulse={self.params.pulse}, scroll_enabled={self.params.scrolling_enabled}, scroll_thickness={self.params.scrolling_thickness}")

        # Step 1: Apply global strobe effect
        if self.params.strobe != 'off':
            print(f"  → Applying GLOBAL STROBE ({self.params.strobe})")
            freq = {'slow': 2, 'medium': 5, 'fast': 10}[self.params.strobe]
            if int(time * freq * 2) % 2 == 1:
                raster.data.fill(0)

        # Step 2: Apply global pulse effect
        if self.params.pulse != 'off':
            print(f"  → Applying GLOBAL PULSE ({self.params.pulse})")
            freq = {'slow': 0.5, 'medium': 1.0, 'fast': 2.0}[self.params.pulse]
            factor = 0.65 + 0.35 * np.sin(time * freq * np.pi * 2)
            raster.data[:] = (raster.data * factor).astype(np.uint8)

        # Step 3: Apply scrolling mask (if enabled)
        if self.params.scrolling_enabled and self.params.scrolling_thickness > 0:
            print(f"  → Applying SCROLLING MASK (dir={self.params.scrolling_direction}, wdt={self.params.scrolling_thickness}%, spd={self.params.scrolling_speed})")
            mask = self._get_scrolling_band_mask(raster, time)
            # Apply mask: normal mode masks out the band, inverted mode keeps only the band
            if self.params.scrolling_invert_mask:
                # Invert mask: keep only the masked area, turn off everything else
                raster.data[~mask] = 0
            else:
                # Normal: mask out the scrolling band itself
                raster.data[mask] = 0

        # Step 4: Invert (always apply after other effects)
        if self.params.invert:
            max_val = np.max(raster.data)
            if max_val > 0:
                # Keep black pixels black, invert everything else
                mask = raster.data > 10
                raster.data[mask] = max_val - raster.data[mask]

    def _get_scrolling_band_mask(self, raster, time):
        """Calculate the mask for the scrolling band"""
        z_coords, y_coords, x_coords = self.coords_cache

        direction = self.params.scrolling_direction

        # Convert percentage (0-100) to actual pixel thickness based on direction
        percentage = self.params.scrolling_thickness / 100.0

        # Calculate appropriate thickness for each direction type
        if direction in ['x', 'y', 'z']:
            max_dim = {
                'x': raster.width,
                'y': raster.height,
                'z': raster.length
            }[direction]
            thickness = percentage * max_dim
        elif direction in ['diagonal-xz', 'diagonal-yz', 'diagonal-xy']:
            if direction == 'diagonal-xz':
                max_dim = np.sqrt(raster.width**2 + raster.length**2)
            elif direction == 'diagonal-yz':
                max_dim = np.sqrt(raster.height**2 + raster.length**2)
            else:  # diagonal-xy
                max_dim = np.sqrt(raster.width**2 + raster.height**2)
            thickness = percentage * max_dim
        elif direction in ['radial', 'spiral', 'rings']:
            center_x = raster.width / 2
            center_y = raster.height / 2
            center_z = raster.length / 2
            max_radius = np.sqrt(center_x**2 + center_y**2 + center_z**2)
            thickness = percentage * max_radius
        else:  # wave, noise, or unknown
            # For wave and noise, use a normalized thickness
            thickness = percentage * 20  # Map to 0-20 range for compatibility


        # Helper function to calculate scroll position with wrap or ping-pong
        def get_scroll_pos(max_dim):
            raw_pos = self.mask_phase * 10
            if self.params.scrolling_loop:
                # Ping-pong: bounce back and forth
                cycle_length = max_dim * 2
                pos_in_cycle = raw_pos % cycle_length
                if pos_in_cycle > max_dim:
                    return cycle_length - pos_in_cycle
                return pos_in_cycle
            else:
                # Wrap around (default)
                return raw_pos % max_dim

        # Simple axis-aligned scrolling
        if direction in ['x', 'y', 'z']:
            max_dim = {
                'x': raster.width,
                'y': raster.height,
                'z': raster.length
            }[direction]

            scroll_pos = get_scroll_pos(max_dim)

            axis_coords = {
                'x': x_coords,
                'y': y_coords,
                'z': z_coords
            }[direction]

            # Force broadcast to full 3D grid
            axis_coords_broadcast = axis_coords + y_coords * 0 + x_coords * 0 + z_coords * 0

            # Calculate distance - use toroidal wrapping for smooth transitions
            # but cap thickness to avoid full coverage at 50%
            if self.params.scrolling_loop:
                # In loop mode, use simple distance (no wrapping)
                dist_from_band = np.abs(axis_coords_broadcast - scroll_pos)
            else:
                # In wrap mode, use toroidal distance but cap the effective thickness
                linear_dist = np.abs(axis_coords_broadcast - scroll_pos)
                dist_from_band = np.minimum(linear_dist, max_dim - linear_dist)
                # Cap thickness to prevent full scene masking before 100%
                # Toroidal distance maxes out at max_dim/2, so cap thickness at 49% to prevent overlap
                thickness = min(thickness, max_dim * 0.49)  # Cap at 49% to prevent wrapping overlap

        # Diagonal scrolling (moving along two axes simultaneously)
        elif direction == 'diagonal-xz':
            max_dim = np.sqrt(raster.width**2 + raster.length**2)
            scroll_pos = get_scroll_pos(max_dim)
            # Distance from diagonal line - force broadcast to full 3D
            diagonal_coord = (x_coords + z_coords + y_coords * 0) / np.sqrt(2)
            if self.params.scrolling_loop:
                dist_from_band = np.abs(diagonal_coord - scroll_pos)
            else:
                linear_dist = np.abs(diagonal_coord - scroll_pos)
                dist_from_band = np.minimum(linear_dist, max_dim - linear_dist)
                thickness = min(thickness, max_dim * 0.49)

        elif direction == 'diagonal-yz':
            max_dim = np.sqrt(raster.height**2 + raster.length**2)
            scroll_pos = get_scroll_pos(max_dim)
            # Force broadcast to full 3D
            diagonal_coord = (y_coords + z_coords + x_coords * 0) / np.sqrt(2)
            if self.params.scrolling_loop:
                dist_from_band = np.abs(diagonal_coord - scroll_pos)
            else:
                linear_dist = np.abs(diagonal_coord - scroll_pos)
                dist_from_band = np.minimum(linear_dist, max_dim - linear_dist)
                thickness = min(thickness, max_dim * 0.49)

        elif direction == 'diagonal-xy':
            max_dim = np.sqrt(raster.width**2 + raster.height**2)
            scroll_pos = get_scroll_pos(max_dim)
            # Force broadcast to full 3D
            diagonal_coord = (x_coords + y_coords + z_coords * 0) / np.sqrt(2)
            if self.params.scrolling_loop:
                dist_from_band = np.abs(diagonal_coord - scroll_pos)
            else:
                linear_dist = np.abs(diagonal_coord - scroll_pos)
                dist_from_band = np.minimum(linear_dist, max_dim - linear_dist)
                thickness = min(thickness, max_dim * 0.49)

        # Radial scrolling (expanding/contracting from center)
        elif direction == 'radial':
            center_x = raster.width / 2
            center_y = raster.height / 2
            center_z = raster.length / 2

            # Distance from center
            radius = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2 + (z_coords - center_z)**2)
            max_radius = np.sqrt(center_x**2 + center_y**2 + center_z**2)

            scroll_pos = get_scroll_pos(max_radius)

            if self.params.scrolling_loop:
                dist_from_band = np.abs(radius - scroll_pos)
            else:
                linear_dist = np.abs(radius - scroll_pos)
                dist_from_band = np.minimum(linear_dist, max_radius - linear_dist)
                thickness = min(thickness, max_radius * 0.49)

            # Return mask for radial mode
            return dist_from_band < thickness

        # Spiral masking (combines radial and angular components)
        elif direction == 'spiral':
            center_x = raster.width / 2
            center_y = raster.height / 2
            center_z = raster.length / 2

            # Calculate cylindrical coordinates (using Y as vertical axis)
            radius_xz = np.sqrt((x_coords - center_x)**2 + (z_coords - center_z)**2)
            angle = np.arctan2(z_coords - center_z, x_coords - center_x)

            # Create an Archimedean spiral: r = a + b*theta
            # Calculate max radius to determine spiral tightness
            max_radius_xz = np.sqrt(center_x**2 + center_z**2)

            # Tightness: how much radius increases per radian
            # Divide by 2π to make one full rotation reach the edge
            # Multiply by 1.5 to get ~1.5 rotations across the grid
            spiral_tightness = (max_radius_xz / (2 * np.pi)) * 1.5

            # The spiral rotates over time
            time_rotation = self.mask_phase * 0.5
            # Normalize angle to [0, 2*pi] and add time rotation
            angle_normalized = (angle + np.pi + time_rotation) % (2 * np.pi)

            # Spiral equation: for a given angle, we expect a certain radius
            # We use angle to determine expected radius, then compare to actual
            spiral_radius_expected = angle_normalized * spiral_tightness

            # Distance from the spiral curve
            dist_from_band = np.abs(radius_xz - spiral_radius_expected)

        # Wave masking (3D sinusoidal wave)
        elif direction == 'wave':
            # Create a continuously flowing 3D wave
            # Use a traveling wave: combine position and time smoothly
            wave_value = (
                np.sin(x_coords * 0.3 + self.mask_phase * 2) +
                np.cos(y_coords * 0.3 + self.mask_phase * 2) +
                np.sin(z_coords * 0.3 + self.mask_phase * 2)
            )
            # Wave value ranges from -3 to 3
            # Use threshold-based masking like noise (thickness is already scaled 0-20)
            # Map thickness (0-20) to threshold (-3 to 3) for gradual masking
            # Higher threshold = more masking (invert comparison for correct behavior)
            threshold = -3.0 + (thickness / 20.0) * 6.0
            return wave_value < threshold

        # Rings masking (concentric spherical shells)
        elif direction == 'rings':
            center_x = raster.width / 2
            center_y = raster.height / 2
            center_z = raster.length / 2

            # Distance from center (same as radial but with multiple rings)
            radius = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2 + (z_coords - center_z)**2)

            # Create pulsing rings by using modulo
            ring_period = 8  # Distance between rings
            ring_coord = (radius + self.mask_phase * 10) % ring_period

            # Scale thickness relative to ring_period (not max_radius)
            # thickness is 0-20 from percentage conversion, map to 0-ring_period
            ring_thickness = (thickness / 20.0) * ring_period

            # Threshold creates the ring band
            dist_from_band = ring_coord
            return dist_from_band < ring_thickness

        # Noise masking (Perlin-like noise pattern)
        elif direction == 'noise':
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

            # Threshold based on mask width (thickness is already scaled 0-20)
            # Map thickness (0-20) to threshold (-1 to 1)
            # Higher threshold = more masking (invert comparison for correct behavior)
            threshold = -1.0 + (thickness / 20.0) * 2.0
            return noise < threshold

        else:
            # Fallback for unknown directions
            return np.ones_like(x_coords, dtype=bool)

        mask = dist_from_band < thickness
        return mask

