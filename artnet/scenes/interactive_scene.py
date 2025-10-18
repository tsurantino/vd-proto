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
    scrolling_mode: str = 'strobe'
    scrolling_thickness: int = 5
    scrolling_direction: str = 'y'
    scrolling_speed: float = 1.0
    scrolling_invert: bool = False

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

        print(f"✨ InteractiveScene v2.0 initialized (modular architecture)")

    def update_parameters(self, params_dict: Dict[str, Any]):
        """Update scene parameters from web UI"""
        for key, value in params_dict.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
            else:
                # Scene-specific params
                self.params.scene_params[key] = value

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

        # Clear or apply decay
        if self.params.decay == 0:
            raster.data.fill(0)
        else:
            current_weight = 1 - self.params.decay * 0.7
            previous_weight = self.params.decay * 0.7
            raster.data[:] = (
                raster.data * current_weight +
                self.previous_frame * previous_weight
            ).astype(np.uint8)

        # LAYER 1: Generate geometry
        mask = self._generate_geometry(raster, time * self.params.animationSpeed)

        # LAYER 2: Apply colors
        self._apply_colors(raster, mask, time * self.params.animationSpeed)

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
        """Apply global post-processing effects"""
        # Strobe
        if self.params.strobe != 'off':
            freq = {'slow': 2, 'medium': 5, 'fast': 10}[self.params.strobe]
            if int(time * freq * 2) % 2 == 1:
                raster.data.fill(0)
                return

        # Pulse
        if self.params.pulse != 'off':
            freq = {'slow': 0.5, 'medium': 1.0, 'fast': 2.0}[self.params.pulse]
            factor = 0.65 + 0.35 * np.sin(time * freq * np.pi * 2)
            raster.data[:] = (raster.data * factor).astype(np.uint8)

        # Invert
        if self.params.invert:
            max_val = np.max(raster.data)
            if max_val > 0:
                raster.data[:] = np.where(raster.data > 10, 0, max_val)

        # Scrolling
        if self.params.scrolling_enabled:
            self._apply_scrolling_effect(raster, time)

    def _apply_scrolling_effect(self, raster, time):
        """Apply scrolling effect"""
        z_coords, y_coords, x_coords = self.coords_cache

        max_dim = {
            'x': raster.width,
            'y': raster.height,
            'z': raster.length
        }[self.params.scrolling_direction]

        scroll_pos = (time * self.params.scrolling_speed * 10) % max_dim

        axis_coords = {
            'x': x_coords,
            'y': y_coords,
            'z': z_coords
        }[self.params.scrolling_direction]

        dist_from_band = np.abs(axis_coords - scroll_pos)

        if self.params.scrolling_mode == 'strobe':
            mask = dist_from_band < self.params.scrolling_thickness
            if self.params.scrolling_invert:
                raster.data[mask] = 0
            else:
                raster.data[~mask] = 0

        elif self.params.scrolling_mode == 'pulse':
            mask = dist_from_band < self.params.scrolling_thickness
            if np.any(mask):
                factor = 1 - dist_from_band[mask] / self.params.scrolling_thickness
                raster.data[mask] = (raster.data[mask] * factor[..., np.newaxis]).astype(np.uint8)
