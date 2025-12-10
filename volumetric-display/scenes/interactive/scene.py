"""
Interactive Scene with Layered Architecture
Geometry → Color Effects → Global Effects

Refactored to use modular scene types, transforms, and effects.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any
from artnet import Scene, Raster

# Import scene registry
from .scenes import SCENE_REGISTRY

# Import color utilities
from .colors.utils import (
    vectorized_hsv_to_rgb, parse_hex_color, parse_gradient,
    interpolate_colors
)

# Import ColorEffects class for advanced color effects
from .colors.effects import ColorEffects

# Import effects system
from .effects import GlobalEffects, MaskingSystem

# Import transforms
from .transforms import apply_translation_with_indices


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

    # Movement / Main Rotation
    rotationX: float = 0.0
    rotationY: float = 0.0
    rotationZ: float = 0.0
    rotation_speed: float = 0.0
    rotation_offset: float = 0.0

    # Copy system
    copy_spacing: float = 1.5
    copy_arrangement: str = 'linear'

    # Copy variation (simplified two-level offset system)
    global_copy_offset: float = 0.0
    copy_scale_offset: float = 0.0
    copy_rotation_var: float = 0.0
    copy_translation_var: float = 0.0

    # Copy rotation override
    use_copy_rotation_override: bool = False
    copy_rotation_x: float = 0.0
    copy_rotation_y: float = 0.0
    copy_rotation_z: float = 0.0
    copy_rotation_speed: float = 0.0
    copy_rotation_offset: float = 0.0

    # Copy translation
    copy_translation_x: float = 0.0
    copy_translation_y: float = 0.0
    copy_translation_z: float = 0.0
    copy_translation_speed: float = 0.0
    copy_translation_offset: float = 0.0

    # Object scrolling system
    object_scroll_speed: float = 0.0
    object_scroll_direction: str = 'y'

    # Color system
    color_type: str = 'single'
    color_single: str = '#64C8FF'
    color_gradient: str = '#FF0000,#0000FF'
    color_effect: str = 'none'
    color_effect_intensity: float = 1.0
    color_mode: str = 'rainbow'
    color_speed: float = 1.0

    # Global effects
    decay: float = 0.0
    strobe: str = 'off'
    pulse: str = 'off'
    invert: bool = False
    scrolling_enabled: bool = False
    scrolling_thickness: int = 0
    scrolling_direction: str = 'y'
    scrolling_speed: float = 1.0
    scrolling_loop: bool = False
    scrolling_invert_mask: bool = False

    # Copy colors (per-copy color variation)
    copy_color_mode: str = 'none'  # 'none', 'hue_shift', 'brightness', 'saturation', 'complementary', 'analogous'

    # Scene-specific params
    scene_params: Dict[str, Any] = field(default_factory=dict)


class InteractiveScene(Scene):
    """
    Main scene orchestrator - delegates to modular scene types.

    Architecture:
    1. SceneRegistry dispatches to specific scene types
    2. Transform system handles rotation, copy, scrolling
    3. Effects system handles global effects and masking
    4. Color system applies colors and color effects
    """

    def __init__(self, **kwargs):
        self.properties = kwargs.get("properties")
        self.scene_config = kwargs.get("scene_config", {})
        self.params = SceneParameters()

        # Initialize with grid scene
        self.params.scene_type = 'grid'

        # Coordinate cache
        self.coords_cache = None
        self.grid_shape = None

        # Active scene instance
        self.active_scene = None

        # ColorEffects instance (initialized when raster is available)
        self.color_effects = None

        # Effects systems (initialized when raster is available)
        self.global_effects = GlobalEffects()
        self.masking_system = None

        # Previous frame for decay
        self.previous_frame = None

        # Copy indices for per-copy coloring (from CopyManager)
        self.copy_indices = None

        # Color time tracking
        self.color_time = 0

        # Animation time tracking for smooth speed changes
        self.animation_time = 0

        # Track previous values to only log changes
        self.prev_color_mode = None
        self.prev_color_effect = None
        self.prev_scene_type = None

        print(f"✨ InteractiveScene v3.0 initialized (modular architecture)")

    def get_web_ui_path(self):
        """Return path to custom web UI for this scene"""
        return "scenes/interactive/web/index.html"

    def update_parameters(self, params_dict: Dict[str, Any]):
        """Update scene parameters from web UI"""
        # Track what actually changed for logging
        scrolling_changed = False
        strobe_changed = False
        pulse_changed = False
        scene_changed = False

        # Check for scene type change
        if 'scene_type' in params_dict:
            new_scene = params_dict['scene_type']
            if new_scene != self.params.scene_type:
                scene_changed = True
                self.prev_scene_type = self.params.scene_type

        # Check for other changes
        if 'scrolling_thickness' in params_dict or 'scrolling_enabled' in params_dict or 'scrolling_direction' in params_dict:
            new_enabled = params_dict.get('scrolling_enabled', self.params.scrolling_enabled)
            new_thickness = params_dict.get('scrolling_thickness', self.params.scrolling_thickness)
            new_direction = params_dict.get('scrolling_direction', self.params.scrolling_direction)

            scrolling_changed = (
                new_enabled != self.params.scrolling_enabled or
                new_thickness != self.params.scrolling_thickness or
                new_direction != self.params.scrolling_direction
            )

        if 'strobe' in params_dict:
            strobe_changed = params_dict['strobe'] != self.params.strobe

        if 'pulse' in params_dict:
            pulse_changed = params_dict['pulse'] != self.params.pulse

        # Update the parameters
        for key, value in params_dict.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
            else:
                # Scene-specific params
                self.params.scene_params[key] = value

        # Recreate active scene if scene type changed
        if scene_changed and self.coords_cache is not None:
            self._create_active_scene()
            print(f"🎬 Scene changed: {self.prev_scene_type} → {self.params.scene_type}")

        # Log changes
        if scrolling_changed:
            print(f"🔄 SCROLL UPDATE: enabled={self.params.scrolling_enabled}, thickness={self.params.scrolling_thickness}, direction={self.params.scrolling_direction}")
        if strobe_changed:
            print(f"⚡ STROBE UPDATE: {self.params.strobe}")
        if pulse_changed:
            print(f"💓 PULSE UPDATE: {self.params.pulse}")

    def render(self, raster: Raster, time: float):
        """
        Main render method - layered pipeline:
        1. Generate geometry (via scene type)
        2. Apply colors
        3. Apply global effects
        """
        # Initialize coord cache and systems
        if self.coords_cache is None:
            self._init_coords(raster)
            self._create_active_scene()

        # Initialize previous frame
        if self.previous_frame is None:
            self.previous_frame = np.zeros_like(raster.data)

        # Update color time
        self.color_time += 1.0 / 60.0 * self.params.color_speed

        # Update animation time
        delta_time = time - self.animation_time if self.animation_time > 0 else 0
        self.animation_time = time

        # Scale time by animation speed for geometry generation
        scaled_time = time * self.params.animationSpeed

        # Update masking system phase
        self.masking_system.update_phase(scaled_time, self.params)

        # Apply decay/trail effect (returns True if decay active)
        decay_active = self.global_effects.apply_decay(raster, self.previous_frame, self.params)

        # LAYER 1: Generate geometry (via active scene)
        mask, copy_indices = self.active_scene.generate_geometry(raster, self.params, scaled_time)

        # Apply translation transform to BOTH geometry and copy indices
        # (keeps them aligned so copy color effects work correctly)
        mask, copy_indices = apply_translation_with_indices(mask, copy_indices, raster, self.params, scaled_time)
        self.copy_indices = copy_indices  # Store for per-copy coloring

        # LAYER 2: Apply colors (draws on top of decayed frame)
        self._apply_colors(raster, mask, scaled_time)

        # LAYER 3: Apply global effects (strobe, pulse, invert)
        self.global_effects.apply_strobe(raster, self.params, scaled_time)
        self.global_effects.apply_pulse(raster, self.params, scaled_time)

        # LAYER 4: Apply scrolling mask
        self.masking_system.apply_mask(raster, self.params)

        # LAYER 5: Apply invert (last)
        self.global_effects.apply_invert(raster, self.params)

        # Store frame for decay
        self.previous_frame[:] = raster.data

    def _init_coords(self, raster):
        """Initialize coordinate grids and systems"""
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

        # Extract gap regions from config for multi-cube gap masking
        gap_regions = self.scene_config.get('gaps', [])

        # Initialize masking system with gap regions
        self.masking_system = MaskingSystem(self.coords_cache, gap_regions=gap_regions)

    def _create_active_scene(self):
        """Create active scene instance based on scene_type"""
        scene_class = SCENE_REGISTRY.get(self.params.scene_type)
        if scene_class:
            self.active_scene = scene_class(self.grid_shape, self.coords_cache)
        else:
            # Fallback to grid scene
            from .scenes.grid import GridScene
            self.active_scene = GridScene(self.grid_shape, self.coords_cache)
            print(f"⚠️  Unknown scene type '{self.params.scene_type}', using grid")

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

        # Apply copy color variation (after base colors, before effects)
        if self.params.copy_color_mode != 'none' and self.copy_indices is not None:
            self._apply_copy_color_variation(raster, mask)

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
            # Gradient (simple Y-axis)
            gradient_colors = parse_gradient(self.params.color_gradient)
            z_coords, y_coords, x_coords = self.coords_cache

            # Broadcast sparse coordinates to full grid before indexing
            y_coords_full = y_coords + z_coords * 0 + x_coords * 0
            masked_y = y_coords_full[mask]

            y_min, y_max = masked_y.min(), masked_y.max()

            # Avoid division by zero
            if y_max > y_min:
                t = (masked_y - y_min) / (y_max - y_min)
            else:
                t = np.zeros_like(masked_y, dtype=np.float32)

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

    def _apply_copy_color_variation(self, raster, mask):
        """Apply per-copy color variation based on copy_color_mode.

        Modifies colors of each copy based on which copy the voxel belongs to.
        Uses HSV manipulation for smooth color transitions.
        """
        mode = self.params.copy_color_mode
        copy_indices = self.copy_indices

        # Get masked colors and copy indices
        masked_colors = raster.data[mask].astype(np.float32)
        masked_indices = copy_indices[mask]

        # Only process voxels that belong to a copy (index >= 0)
        valid_mask = masked_indices >= 0
        if not np.any(valid_mask):
            return

        # Get max copy index for normalization
        max_copy = masked_indices.max()
        if max_copy <= 0:
            return  # Only one copy, no variation needed

        # Convert RGB to HSV for manipulation
        r = masked_colors[valid_mask, 0] / 255.0
        g = masked_colors[valid_mask, 1] / 255.0
        b = masked_colors[valid_mask, 2] / 255.0

        # RGB to HSV conversion
        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        delta = max_c - min_c

        # Hue calculation
        h = np.zeros_like(r)
        s = np.zeros_like(r)
        v = max_c

        # Avoid division by zero
        nonzero_delta = delta > 0
        if np.any(nonzero_delta):
            # Saturation
            nonzero_v = max_c > 0
            s[nonzero_v] = delta[nonzero_v] / max_c[nonzero_v]

            # Hue
            r_max = (max_c == r) & nonzero_delta
            g_max = (max_c == g) & nonzero_delta
            b_max = (max_c == b) & nonzero_delta

            h[r_max] = 60 * (((g[r_max] - b[r_max]) / delta[r_max]) % 6)
            h[g_max] = 60 * (((b[g_max] - r[g_max]) / delta[g_max]) + 2)
            h[b_max] = 60 * (((r[b_max] - g[b_max]) / delta[b_max]) + 4)

        # Get copy indices for valid voxels (0, 1, 2, ...)
        copy_idx = masked_indices[valid_mask].astype(np.float32)

        # Apply color mode
        if mode == 'hue_shift':
            # Shift hue by 40 degrees per copy
            h = (h + copy_idx * 40) % 360
        elif mode == 'brightness':
            # Darken each subsequent copy (copy 0 brightest)
            v = v * (1 - copy_idx * 0.15)
            v = np.clip(v, 0, 1)
        elif mode == 'saturation':
            # Reduce saturation per copy
            s = s * (1 - copy_idx * 0.2)
            s = np.clip(s, 0, 1)
        elif mode == 'complementary':
            # Odd copies get complementary color (+180 degrees)
            odd_copies = (copy_idx.astype(int) % 2) == 1
            h[odd_copies] = (h[odd_copies] + 180) % 360
        elif mode == 'analogous':
            # Spread copies across ±60 degree range centered on base hue
            offset = (copy_idx - max_copy / 2) * 25
            h = (h + offset) % 360

        # Convert HSV back to RGB
        c = v * s
        x = c * (1 - np.abs((h / 60) % 2 - 1))
        m = v - c

        # Initialize RGB arrays
        r_out = np.zeros_like(h)
        g_out = np.zeros_like(h)
        b_out = np.zeros_like(h)

        # Sector assignments
        sector0 = (h >= 0) & (h < 60)
        sector1 = (h >= 60) & (h < 120)
        sector2 = (h >= 120) & (h < 180)
        sector3 = (h >= 180) & (h < 240)
        sector4 = (h >= 240) & (h < 300)
        sector5 = (h >= 300) & (h < 360)

        r_out[sector0] = c[sector0]; g_out[sector0] = x[sector0]; b_out[sector0] = 0
        r_out[sector1] = x[sector1]; g_out[sector1] = c[sector1]; b_out[sector1] = 0
        r_out[sector2] = 0; g_out[sector2] = c[sector2]; b_out[sector2] = x[sector2]
        r_out[sector3] = 0; g_out[sector3] = x[sector3]; b_out[sector3] = c[sector3]
        r_out[sector4] = x[sector4]; g_out[sector4] = 0; b_out[sector4] = c[sector4]
        r_out[sector5] = c[sector5]; g_out[sector5] = 0; b_out[sector5] = x[sector5]

        r_out = ((r_out + m) * 255).astype(np.uint8)
        g_out = ((g_out + m) * 255).astype(np.uint8)
        b_out = ((b_out + m) * 255).astype(np.uint8)

        # Apply modified colors back
        result_colors = masked_colors.copy()
        result_colors[valid_mask, 0] = r_out
        result_colors[valid_mask, 1] = g_out
        result_colors[valid_mask, 2] = b_out

        raster.data[mask] = result_colors.astype(np.uint8)
