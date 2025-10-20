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
    generate_cube, generate_torus, generate_pyramid, generate_cross_grid
)
from .geometry.waves import (
    generate_ripple_wave, generate_plane_wave,
    generate_standing_wave, generate_interference_wave
)
from .geometry.utils import rotate_coordinates

# Import color utilities
from .colors.utils import (
    vectorized_hsv_to_rgb, parse_hex_color, parse_gradient,
    apply_color_to_mask, rainbow_color, hue_shift
)

# Import ColorEffects class for advanced color effects
from .colors.effects import ColorEffects


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
    scaling_amount: float = 2.0
    scaling_speed: float = 2.0

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

        # Initialize with grid scene
        self.params.scene_type = 'grid'

        # Coordinate cache
        self.coords_cache = None
        self.grid_shape = None

        # ColorEffects instance (initialized when raster is available)
        self.color_effects = None

        # Previous frame for decay
        self.previous_frame = None

        # Color time tracking
        self.color_time = 0

        # Animation time tracking for smooth speed changes
        self.animation_time = 0

        # Mask phase tracking for smooth speed changes
        self.mask_phase = 0
        self.last_frame_time = 0

        # Track previous values to only log changes
        self.prev_color_mode = None
        self.prev_color_effect = None

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
        """Initialize coordinate grids and ColorEffects"""
        self.coords_cache = np.indices(
            (raster.length, raster.height, raster.width),
            sparse=True
        )
        self.grid_shape = (raster.length, raster.height, raster.width)

        # Initialize ColorEffects with grid dimensions
        self.color_effects = ColorEffects(
            gridX=raster.width,
            gridY=raster.height,
            gridZ=raster.length
        )

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
        elif scene_type == 'grid':
            return self._geometry_grid(raster, time)
        elif scene_type == 'illusions':
            return self._geometry_illusions(raster, time)
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

        # Apply rotation to coordinates
        # Controller sends values -1 to 1, convert to radians (-π to π)
        angles = (
            self.params.rotationX * np.pi,
            self.params.rotationY * np.pi,
            self.params.rotationZ * np.pi
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)

        if shape == 'sphere':
            radius = min(center) * size * 0.8
            return generate_pulsing_sphere(
                coords, center, radius, time,
                pulse_speed=self.params.scaling_speed,
                pulse_amount=self.params.scaling_amount
            )

        elif shape == 'cube':
            base_size = min(center) * size * 0.8
            # Apply pulsing/scaling effect
            pulse = 1.0 + (self.params.scaling_amount * 0.1) * np.sin(time * self.params.scaling_speed)
            cube_size = base_size * pulse
            # Use density to control edge thickness (0.1-1.0 -> 0.5-2.5 pixels)
            # Smaller range prevents edges from overlapping
            edge_thickness = 0.5 + self.params.density * 2.0
            return generate_cube(coords, center, cube_size, edge_thickness)

        elif shape == 'torus':
            base_major_r = min(center[0], center[2]) * size * 0.6
            # Apply pulsing/scaling effect
            pulse = 1.0 + (self.params.scaling_amount * 0.1) * np.sin(time * self.params.scaling_speed)
            major_r = base_major_r * pulse
            minor_r = major_r * 0.3
            return generate_torus(coords, center, major_r, minor_r)

        elif shape == 'pyramid':
            # Base sits on XY plane, extends along Z axis
            base_base_size = min(center[0], center[1]) * size * 0.6
            # Height along Z axis (length dimension)
            base_height = raster.length * size * 0.9
            # Apply pulsing/scaling effect
            pulse = 1.0 + (self.params.scaling_amount * 0.1) * np.sin(time * self.params.scaling_speed)
            base_size = base_base_size * pulse
            height = base_height * pulse
            return generate_pyramid(coords, center, base_size, height)

        else:
            # Default sphere
            radius = min(center) * size * 0.8
            return generate_sphere(coords, center, radius)

    def _geometry_wave_field(self, raster, time):
        """Wave field geometry"""
        wave_type = self.params.scene_params.get('waveType', 'ripple')

        # Apply rotation to coordinates
        # Controller sends values -1 to 1, convert to radians (-π to π)
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )
        angles = (
            self.params.rotationX * np.pi,
            self.params.rotationY * np.pi,
            self.params.rotationZ * np.pi
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)

        # Apply pulsing/scaling effect to amplitude
        pulse = 1.0 + (self.params.scaling_amount * 0.1) * np.sin(time * self.params.scaling_speed)
        modulated_amplitude = self.params.amplitude * pulse

        if wave_type == 'ripple':
            return generate_ripple_wave(
                coords, self.grid_shape, time,
                frequency=self.params.frequency,
                amplitude=modulated_amplitude,
                speed=5
            )
        elif wave_type == 'plane':
            return generate_plane_wave(
                coords, self.grid_shape, time,
                amplitude=modulated_amplitude,
                speed=3,
                direction='x',  # Default direction
                frequency=self.params.frequency
            )
        elif wave_type == 'standing':
            return generate_standing_wave(
                coords, self.grid_shape, time,
                frequency=self.params.frequency,
                amplitude=modulated_amplitude
            )
        elif wave_type == 'interference':
            mask, _ = generate_interference_wave(
                coords, self.grid_shape, time,
                frequency=self.params.frequency,
                amplitude=modulated_amplitude
            )
            return mask
        else:
            return generate_ripple_wave(
                coords, self.grid_shape, time,
                frequency=self.params.frequency,
                amplitude=modulated_amplitude
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
        # Apply rotation to coordinates
        # Controller sends values -1 to 1, convert to radians (-π to π)
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )
        angles = (
            self.params.rotationX * np.pi,
            self.params.rotationY * np.pi,
            self.params.rotationZ * np.pi
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)
        z_coords, y_coords, x_coords = coords

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

    def _geometry_grid(self, raster, time):
        """Grid - can be full volume or cross pattern"""
        pattern = self.params.scene_params.get('gridPattern', 'full')

        if pattern == 'cross':
            # Cross pattern with density-controlled line thickness
            center = (
                raster.width / 2,
                raster.height / 2,
                raster.length / 2
            )
            size = min(center)
            # Use density to control cross line thickness (1-10 pixels)
            line_thickness = 1 + self.params.density * 9
            return generate_cross_grid(self.coords_cache, center, size, line_thickness)
        else:
            # Full grid (default)
            return np.ones(self.grid_shape, dtype=bool)

    def _geometry_illusions(self, raster, time):
        """Optical illusion effects"""
        illusion_type = self.params.scene_params.get('illusionType', 'infiniteCorridor')

        if illusion_type == 'infiniteCorridor':
            return self._illusion_infinite_corridor(raster, time)
        elif illusion_type == 'waterfallIllusion':
            return self._illusion_waterfall(raster, time)
        elif illusion_type == 'pulfrich':
            return self._illusion_pulfrich(raster, time)
        elif illusion_type == 'moirePattern':
            return self._illusion_moire(raster, time)
        else:
            return self._illusion_infinite_corridor(raster, time)

    def _illusion_infinite_corridor(self, raster, time):
        """Infinite corridor - scrolling perspective frames along Y axis (vertical)"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Parameters
        frame_spacing = max(3, int(4 * (1 + self.params.density)))
        num_frames = int(5 + self.params.size * 5)
        scroll_offset = (time * 3) % (frame_spacing * num_frames)

        mask = np.zeros(self.grid_shape, dtype=bool)

        for frame in range(num_frames):
            # Position along Y axis (height) - scrolling upward
            base_y = (frame * frame_spacing - scroll_offset)
            y = int(base_y) % raster.height

            # Calculate perspective scale based on Y position
            # Bottom (y near 0) = small (far away)
            # Top (y near height) = large (close)
            normalized_pos = y / raster.height
            scale = 0.2 + normalized_pos * 0.8 * self.params.size

            # Frame dimensions in XZ plane
            width = max(1, int(raster.width / 2 * scale))
            depth = max(1, int(raster.length / 2 * scale))

            # Draw rectangular frame at this Y position
            center_x = raster.width // 2
            center_z = raster.length // 2

            # Draw all four edges of the rectangle
            # Top and bottom edges (parallel to X axis)
            for x in range(-width, width + 1):
                for offset_z in [-depth, depth]:
                    wz = center_z + offset_z
                    wx = center_x + x
                    if 0 <= wx < raster.width and 0 <= wz < raster.length:
                        mask[wz, y, wx] = True

            # Left and right edges (parallel to Z axis)
            for z in range(-depth, depth + 1):
                for offset_x in [-width, width]:
                    wx = center_x + offset_x
                    wz = center_z + z
                    if 0 <= wx < raster.width and 0 <= wz < raster.length:
                        mask[wz, y, wx] = True

        return mask

    def _illusion_waterfall(self, raster, time):
        """Waterfall illusion - moving vertical stripes"""
        z_coords, y_coords, x_coords = self.coords_cache

        offset = time * 10
        stripe_spacing = max(2, int(5 - self.params.density * 3))

        mask = np.zeros(self.grid_shape, dtype=bool)

        # Create moving stripes pattern along Z axis
        for z in range(raster.length):
            pattern = (z + offset) % (stripe_spacing * 2)
            is_stripe = pattern < stripe_spacing

            if is_stripe:
                # Fill this Z slice
                mask[z, :, :] = True

        # Add horizontal marker lines every 5 units in Y
        # These create the reference frame that makes the illusion work
        for y in range(0, raster.height, 5):
            mask[:, y, :] = True

        return mask

    def _illusion_pulfrich(self, raster, time):
        """Pulfrich effect - rotating objects with brightness variation in XY plane"""
        z_coords, y_coords, x_coords = self.coords_cache

        radius = 12 * self.params.size
        num_objects = 8

        center_x = raster.width / 2
        center_y = raster.height / 2
        center_z = raster.length / 2

        mask = np.zeros(self.grid_shape, dtype=np.float32)

        for i in range(num_objects):
            obj_angle = time + (i / num_objects) * np.pi * 2

            # Position in XY plane (rotating vertically)
            px = int(center_x + np.cos(obj_angle) * radius)
            py = int(center_y + np.sin(obj_angle) * radius)

            # Brightness varies with position
            brightness = 0.5 + 0.5 * np.sin(obj_angle)

            # Draw sphere at this position
            obj_size = 2
            for dx in range(-obj_size, obj_size + 1):
                for dy in range(-obj_size, obj_size + 1):
                    for dz in range(-obj_size, obj_size + 1):
                        if dx*dx + dy*dy + dz*dz <= obj_size * obj_size:
                            wx = px + dx
                            wy = py + dy
                            wz = int(center_z + dz)

                            if 0 <= wx < raster.width and 0 <= wy < raster.height and 0 <= wz < raster.length:
                                mask[wz, wy, wx] = max(mask[wz, wy, wx], brightness)

        return mask > 0.3

    def _illusion_moire(self, raster, time):
        """Moire pattern - overlapping rotated grids"""
        grid_spacing = max(2, int(3 * (1 + self.params.density)))
        angle = time * 0.1

        mask = np.zeros(self.grid_shape, dtype=bool)

        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)

        center_x = raster.width / 2
        center_z = raster.length / 2

        # Draw first grid - vertical lines along X
        for x in range(0, raster.width, grid_spacing):
            mask[:, :, x] = True

        # Draw second grid - rotated in XZ plane
        for z in range(raster.length):
            for x in range(raster.width):
                # Transform to center-origin coords
                cx = x - center_x
                cz = z - center_z

                # Rotate
                rx = cx * cos_angle - cz * sin_angle

                # Check if this point is on a grid line
                if int(abs(rx)) % grid_spacing == 0:
                    mask[z, :, x] = True

        return mask

    # ================================================================
    # LAYER 2: COLOR APPLICATION
    # ================================================================

    def _apply_colors(self, raster, mask, time):
        """Apply colors to geometry mask"""
        if not np.any(mask):
            return

        # Only log when color mode changes
        if self.params.color_mode != self.prev_color_mode:
            if self.params.color_mode == 'rainbow':
                print(f"🌈 COLOR MODE: rainbow")
            else:
                print(f"🎨 COLOR MODE: base (type={self.params.color_type})")
            self.prev_color_mode = self.params.color_mode

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

            # Broadcast sparse coordinates to full grid before indexing
            # This converts (1, H, 1) to (L, H, W) by adding zeros
            y_coords_full = y_coords + z_coords * 0 + x_coords * 0

            # Now index with the boolean mask
            masked_y = y_coords_full[mask]

            y_min, y_max = masked_y.min(), masked_y.max()

            # Avoid division by zero if all pixels are at same Y
            if y_max > y_min:
                t = (masked_y - y_min) / (y_max - y_min)
            else:
                t = np.zeros_like(masked_y, dtype=np.float32)

            from .colors.utils import interpolate_colors
            positions = np.linspace(0, 1, len(gradient_colors))
            colors = interpolate_colors(gradient_colors, positions, t)
            raster.data[mask] = colors

    def _apply_color_effect(self, raster, mask, time):
        """Apply color effect to existing colors using ColorEffects class"""
        effect = self.params.color_effect
        intensity = self.params.color_effect_intensity

        if effect == 'none' or intensity == 0:
            if self.prev_color_effect is not None and self.prev_color_effect != 'none':
                print(f"🎨 COLOR EFFECT: disabled")
                self.prev_color_effect = 'none'
            return

        # Only log when effect changes
        if effect != self.prev_color_effect:
            print(f"🎨 COLOR EFFECT: {effect} (intensity={intensity}, speed={self.params.color_speed})")
            self.prev_color_effect = effect

        # Use ColorEffects class (20 core effects)
        self.color_effects.set_effect(effect)
        self.color_effects.set_intensity(intensity)
        self.color_effects.set_speed(self.params.color_speed)
        self.color_effects.set_color_mode(self.params.color_mode)
        self.color_effects.apply_to_raster(
            raster.data, mask, self.coords_cache, self.color_time
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
        # Step 1: Apply global strobe effect
        if self.params.strobe != 'off':
            freq = {'slow': 2, 'medium': 5, 'fast': 10}[self.params.strobe]
            if int(time * freq * 2) % 2 == 1:
                raster.data.fill(0)

        # Step 2: Apply global pulse effect
        if self.params.pulse != 'off':
            freq = {'slow': 0.5, 'medium': 1.0, 'fast': 2.0}[self.params.pulse]
            factor = 0.65 + 0.35 * np.sin(time * freq * np.pi * 2)
            raster.data[:] = (raster.data * factor).astype(np.uint8)

        # Step 3: Apply scrolling mask (if enabled)
        if self.params.scrolling_enabled and self.params.scrolling_thickness > 0:
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

