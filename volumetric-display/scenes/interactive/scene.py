"""
Interactive Scene with Layered Architecture
Geometry → Color Effects → Global Effects
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any
from artnet import Scene, Raster

# Import geometry generators (relative imports within package)
from .geometry.shapes import (
    generate_sphere, generate_pulsing_sphere, generate_helix,
    generate_cube, generate_torus, generate_pyramid, generate_cross_grid
)
from .geometry.waves import (
    generate_ripple_wave, generate_plane_wave,
    generate_standing_wave, generate_interference_wave
)
from .geometry.utils import rotate_coordinates

# Import color utilities (relative imports within package)
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

    # Movement / Main Rotation
    rotationX: float = 0.0
    rotationY: float = 0.0
    rotationZ: float = 0.0
    rotation_speed: float = 0.0  # Animation speed for rotation
    rotation_offset: float = 0.0  # Offset between X/Y/Z axes (0-1)

    # Copy system
    copy_spacing: float = 1.5
    copy_arrangement: str = 'linear'  # 'linear', 'circular', 'grid', 'spiral'
    copy_scale_offset: float = 0.0  # Scale variation between copies (0-1)
    copy_anim_offset: float = 0.0  # Animation phase offset between copies (0-1)

    # Copy rotation (applied to entire copy set)
    copy_rotation_x: float = 0.0  # -1 to 1 (amount of rotation)
    copy_rotation_y: float = 0.0
    copy_rotation_z: float = 0.0
    copy_rotation_speed: float = 0.0  # Animation speed for copy rotation
    copy_rotation_offset: float = 0.0  # Offset between X/Y/Z axes (0-1)

    # Copy translation (applied to entire copy set)
    copy_translation_x: float = 0.0  # -1 to 1 (amount of translation)
    copy_translation_y: float = 0.0
    copy_translation_z: float = 0.0
    copy_translation_speed: float = 0.0  # Animation speed for copy translation
    copy_translation_offset: float = 0.0  # Offset between X/Y/Z axes (0-1)

    # Object scrolling system
    object_scroll_speed: float = 0.0
    object_scroll_direction: str = 'y'  # 'y', 'x', 'z', 'diagonal-xz', 'diagonal-yz', 'diagonal-xy'

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

    Web UI Support (duck typing):
    - Implements update_parameters(params_dict) for real-time control
    - Implements get_web_ui_path() to specify custom UI location
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

    def get_web_ui_path(self):
        """Return path to custom web UI for this scene"""
        return "scenes/interactive/web/index.html"

    def update_parameters(self, params_dict: Dict[str, Any]):
        """Update scene parameters from web UI"""
        # Track what actually changed for logging
        scrolling_changed = False
        strobe_changed = False
        pulse_changed = False

        # Check for changes before updating
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

        # Now update the parameters
        for key, value in params_dict.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
            else:
                # Scene-specific params
                self.params.scene_params[key] = value

        # Only log when values actually changed
        if scrolling_changed:
            print(f"🔄 SCROLL UPDATE: enabled={self.params.scrolling_enabled}, thickness={self.params.scrolling_thickness}, direction={self.params.scrolling_direction}")
        if strobe_changed:
            print(f"⚡ STROBE UPDATE: {self.params.strobe}")
        if pulse_changed:
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

    def _apply_object_scrolling(self, mask, raster, time):
        """
        Apply object scrolling by translating the entire mask based on direction and speed.

        Args:
            mask: Boolean array to scroll
            raster: Raster object with grid dimensions
            time: Current animation time

        Returns:
            Scrolled mask
        """
        if self.params.object_scroll_speed == 0:
            return mask

        # Calculate scroll offset based on time and speed
        scroll_distance = time * self.params.object_scroll_speed * 5  # Scale for visible movement
        direction = self.params.object_scroll_direction

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

    def _apply_copy_arrangement(self, base_mask, raster, count, spacing, arrangement):
        """
        Create multiple copies of base_mask arranged in a pattern.

        Args:
            base_mask: Boolean array to copy
            raster: Raster object with grid dimensions
            count: Number of copies (including original)
            spacing: Distance multiplier between copies
            arrangement: 'linear', 'circular', 'grid', or 'spiral'

        Returns:
            Combined mask with all copies
        """
        if count <= 1:
            return base_mask

        combined_mask = np.zeros(self.grid_shape, dtype=bool)

        center_x = raster.width / 2
        center_y = raster.height / 2
        center_z = raster.length / 2

        if arrangement == 'linear':
            # Arrange copies along X-axis
            total_width = (count - 1) * spacing * (raster.width * 0.3)
            start_offset = -total_width / 2

            for i in range(count):
                offset_x = int(start_offset + i * spacing * (raster.width * 0.3))

                # Skip if offset is completely out of bounds
                if offset_x >= raster.width or offset_x <= -raster.width:
                    continue

                # Shift mask by offset with bounds checking
                if offset_x >= 0:
                    # Positive offset - shift right
                    src_end = raster.width - offset_x
                    if src_end > 0:
                        combined_mask[:, :, offset_x:offset_x+src_end] |= base_mask[:, :, :src_end]
                else:
                    # Negative offset - shift left
                    src_start = -offset_x
                    dest_end = raster.width + offset_x
                    if dest_end > 0:
                        combined_mask[:, :, :dest_end] |= base_mask[:, :, src_start:]

        elif arrangement == 'circular':
            # Arrange copies in a ring (XZ plane)
            radius = spacing * min(center_x, center_z) * 0.5

            for i in range(count):
                angle = (i / count) * 2 * np.pi
                offset_x = int(radius * np.cos(angle))
                offset_z = int(radius * np.sin(angle))

                # Translate base_mask to new position
                z_coords, y_coords, x_coords = self.coords_cache
                translated_x = x_coords - center_x - offset_x
                translated_z = z_coords - center_z - offset_z

                # Create a shifted version by checking which voxels from base_mask map to new positions
                for z in range(raster.length):
                    for y in range(raster.height):
                        for x in range(raster.width):
                            if base_mask[z, y, x]:
                                new_x = x + offset_x
                                new_z = z + offset_z
                                if 0 <= new_x < raster.width and 0 <= new_z < raster.length:
                                    combined_mask[new_z, y, new_x] = True

        elif arrangement == 'grid':
            # Arrange copies in 2D grid (XZ plane)
            grid_size = int(np.ceil(np.sqrt(count)))
            cell_size_x = (raster.width * spacing) / grid_size
            cell_size_z = (raster.length * spacing) / grid_size
            start_x = center_x - (grid_size * cell_size_x) / 2
            start_z = center_z - (grid_size * cell_size_z) / 2

            copy_idx = 0
            for row in range(grid_size):
                for col in range(grid_size):
                    if copy_idx >= count:
                        break
                    offset_x = int(start_x + col * cell_size_x - center_x)
                    offset_z = int(start_z + row * cell_size_z - center_z)

                    # Translate base_mask
                    for z in range(raster.length):
                        for y in range(raster.height):
                            for x in range(raster.width):
                                if base_mask[z, y, x]:
                                    new_x = x + offset_x
                                    new_z = z + offset_z
                                    if 0 <= new_x < raster.width and 0 <= new_z < raster.length:
                                        combined_mask[new_z, y, new_x] = True
                    copy_idx += 1

        elif arrangement == 'spiral':
            # Arrange copies along a spiral path (XZ plane)
            spiral_radius_step = spacing * min(center_x, center_z) * 0.2
            angle_step = (2 * np.pi) / max(count / 2, 1)

            for i in range(count):
                angle = i * angle_step
                radius = i * spiral_radius_step
                offset_x = int(radius * np.cos(angle))
                offset_z = int(radius * np.sin(angle))

                # Translate base_mask
                for z in range(raster.length):
                    for y in range(raster.height):
                        for x in range(raster.width):
                            if base_mask[z, y, x]:
                                new_x = x + offset_x
                                new_z = z + offset_z
                                if 0 <= new_x < raster.width and 0 <= new_z < raster.length:
                                    combined_mask[new_z, y, new_x] = True

        return combined_mask

    # ================================================================
    # LAYER 1: GEOMETRY GENERATION
    # ================================================================

    def _generate_geometry(self, raster, time):
        """Generate geometry mask based on scene type"""
        scene_type = self.params.scene_type

        # Generate base geometry
        if scene_type == 'shapeMorph':
            mask = self._geometry_shape_morph(raster, time)
        elif scene_type == 'waveField':
            mask = self._geometry_wave_field(raster, time)
        elif scene_type == 'particleFlow':
            mask = self._geometry_particle_flow(raster, time)
        elif scene_type == 'procedural':
            mask = self._geometry_procedural(raster, time)
        elif scene_type == 'grid':
            mask = self._geometry_grid(raster, time)
        elif scene_type == 'illusions':
            mask = self._geometry_illusions(raster, time)
        else:
            # Default: fill entire volume
            mask = np.ones((raster.length, raster.height, raster.width), dtype=bool)

        # Apply object scrolling to the entire geometry
        mask = self._apply_object_scrolling(mask, raster, time)

        return mask

    def _calculate_rotation_angles(self, time, rot_x, rot_y, rot_z, speed, offset):
        """
        Calculate rotation angles with optional animation speed and offset.

        Args:
            time: Current animation time
            rot_x, rot_y, rot_z: Base rotation amounts (-1 to 1)
            speed: Animation speed (0-5)
            offset: Phase offset between axes (0-1) - creates off-axis rotation

        Returns:
            Tuple of (angle_x, angle_y, angle_z) in radians
        """
        if speed > 0:
            # Animate rotation with speed and offset
            # Offset creates phase difference between axes for interesting spinning effects
            angle_x = (rot_x * np.pi) + (time * speed * 1.0)
            angle_y = (rot_y * np.pi) + (time * speed * (1.0 + offset * 0.5))
            angle_z = (rot_z * np.pi) + (time * speed * (1.0 + offset * 1.0))
        else:
            # Static rotation (no animation)
            angle_x = rot_x * np.pi
            angle_y = rot_y * np.pi
            angle_z = rot_z * np.pi

        return (angle_x, angle_y, angle_z)

    def _geometry_shape_morph(self, raster, time):
        """Shape morph geometry"""
        shape = self.params.scene_params.get('shape', 'sphere')

        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )

        # Apply rotation to coordinates with speed and offset
        angles = self._calculate_rotation_angles(
            time,
            self.params.rotationX,
            self.params.rotationY,
            self.params.rotationZ,
            self.params.rotation_speed,
            self.params.rotation_offset
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)

        # If we have copies with offsets, generate each copy individually
        if self.params.objectCount > 1 and (self.params.copy_scale_offset > 0 or self.params.copy_anim_offset > 0):
            return self._generate_shape_copies_with_offsets(raster, time, shape, coords, center)

        # Otherwise, generate base shape and copy it
        base_mask = self._generate_single_shape(raster, time, shape, coords, center, self.params.size, 0)

        # Apply copy arrangement if count > 1 (simple translation without offsets)
        if self.params.objectCount > 1:
            return self._apply_copy_arrangement(
                base_mask, raster,
                self.params.objectCount,
                self.params.copy_spacing,
                self.params.copy_arrangement
            )

        return base_mask

    def _generate_single_shape(self, raster, time, shape, coords, center, size, copy_index):
        """Generate a single shape with optional per-copy animation/scale offset"""
        # Apply animation offset
        offset_time = time + (copy_index * self.params.copy_anim_offset * 2 * np.pi / self.params.scaling_speed if self.params.scaling_speed > 0 else 0)

        # Apply scale offset (each copy gets progressively larger/smaller)
        scale_multiplier = 1.0 + (copy_index * self.params.copy_scale_offset * 0.2)
        effective_size = size * scale_multiplier

        if shape == 'sphere':
            radius = min(center) * effective_size * 0.8
            return generate_pulsing_sphere(
                coords, center, radius, offset_time,
                pulse_speed=self.params.scaling_speed,
                pulse_amount=self.params.scaling_amount
            )

        elif shape == 'cube':
            base_size = min(center) * effective_size * 0.8
            pulse = 1.0 + (self.params.scaling_amount * 0.1) * np.sin(offset_time * self.params.scaling_speed)
            cube_size = base_size * pulse
            edge_thickness = 1.0 + self.params.density * 2.0
            return generate_cube(coords, center, cube_size, edge_thickness)

        elif shape == 'torus':
            base_major_r = min(center[0], center[2]) * effective_size * 0.6
            pulse = 1.0 + (self.params.scaling_amount * 0.1) * np.sin(offset_time * self.params.scaling_speed)
            major_r = base_major_r * pulse
            minor_r = major_r * 0.3
            return generate_torus(coords, center, major_r, minor_r)

        elif shape == 'pyramid':
            base_base_size = min(center[0], center[1]) * effective_size * 0.6
            base_height = raster.length * effective_size * 0.9
            pulse = 1.0 + (self.params.scaling_amount * 0.1) * np.sin(offset_time * self.params.scaling_speed)
            base_size = base_base_size * pulse
            height = base_height * pulse
            return generate_pyramid(coords, center, base_size, height)

        else:
            # Default sphere
            radius = min(center) * effective_size * 0.8
            return generate_sphere(coords, center, radius)

    def _generate_shape_copies_with_offsets(self, raster, time, shape, coords, base_center):
        """Generate multiple copies with individual scale and animation offsets"""
        combined_mask = np.zeros(self.grid_shape, dtype=bool)
        count = self.params.objectCount
        spacing = self.params.copy_spacing
        arrangement = self.params.copy_arrangement

        # Calculate positions for each copy
        positions = self._calculate_copy_positions(raster, count, spacing, arrangement, base_center)

        # Generate each copy with its own offset
        for i, (offset_x, offset_y, offset_z) in enumerate(positions):
            # Apply copy rotation with animation offset
            # When anim_offset > 0, each copy gets a phase offset affecting rotation speed
            rotation_phase = (i * self.params.copy_anim_offset) if self.params.copy_anim_offset > 0 else 0

            # Apply copy rotation to coordinates
            copy_coords = coords
            if self.params.copy_rotation_x != 0 or self.params.copy_rotation_y != 0 or self.params.copy_rotation_z != 0:
                # Use copy rotation speed and offset for animation
                copy_rot_angles = self._calculate_rotation_angles(
                    time,
                    self.params.copy_rotation_x,
                    self.params.copy_rotation_y,
                    self.params.copy_rotation_z,
                    self.params.copy_rotation_speed,
                    self.params.copy_rotation_offset
                )

                # Apply anim_offset phase to create varied rotation per copy
                if self.params.copy_anim_offset > 0:
                    phase_shift = rotation_phase * 2 * np.pi
                    copy_rot_angles = (
                        copy_rot_angles[0] + phase_shift,
                        copy_rot_angles[1] + phase_shift,
                        copy_rot_angles[2] + phase_shift
                    )

                copy_coords = rotate_coordinates(coords, base_center, copy_rot_angles)

            # Apply copy translation with animation offset
            # When anim_offset > 0, each copy gets a wave-like translation offset
            translation_offset_x = 0
            translation_offset_y = 0
            translation_offset_z = 0

            if self.params.copy_translation_x != 0 or self.params.copy_translation_y != 0 or self.params.copy_translation_z != 0:
                # Use copy translation speed for animation
                if self.params.copy_translation_speed > 0:
                    # Animate with speed and offset
                    wave_time_x = time * self.params.copy_translation_speed * 1.0
                    wave_time_y = time * self.params.copy_translation_speed * (1.0 + self.params.copy_translation_offset * 0.5)
                    wave_time_z = time * self.params.copy_translation_speed * (1.0 + self.params.copy_translation_offset * 1.0)

                    # Apply anim_offset phase to create wave pattern across copies
                    if self.params.copy_anim_offset > 0:
                        wave_phase = rotation_phase * 2 * np.pi
                        wave_time_x += wave_phase
                        wave_time_y += wave_phase
                        wave_time_z += wave_phase

                    translation_offset_x = self.params.copy_translation_x * 10 * np.sin(wave_time_x)
                    translation_offset_y = self.params.copy_translation_y * 10 * np.sin(wave_time_y)
                    translation_offset_z = self.params.copy_translation_z * 10 * np.sin(wave_time_z)
                else:
                    # Static offset
                    translation_offset_x = self.params.copy_translation_x * 10
                    translation_offset_y = self.params.copy_translation_y * 10
                    translation_offset_z = self.params.copy_translation_z * 10

            # Create center position for this copy (base arrangement + translation offsets)
            copy_center = (
                base_center[0] + offset_x + translation_offset_x,
                base_center[1] + offset_y + translation_offset_y,
                base_center[2] + offset_z + translation_offset_z
            )

            # Generate shape with scale and animation offset
            copy_mask = self._generate_single_shape(raster, time, shape, copy_coords, copy_center, self.params.size, i)

            # Merge into combined mask
            combined_mask |= copy_mask

        return combined_mask

    def _calculate_copy_positions(self, raster, count, spacing, arrangement, center):
        """Calculate offset positions for each copy"""
        positions = []
        center_x, center_y, center_z = center

        if arrangement == 'linear':
            total_width = (count - 1) * spacing * (raster.width * 0.3)
            start_offset = -total_width / 2
            for i in range(count):
                offset_x = start_offset + i * spacing * (raster.width * 0.3)
                positions.append((offset_x, 0, 0))

        elif arrangement == 'circular':
            radius = spacing * min(center_x, center_z) * 0.5
            for i in range(count):
                angle = (i / count) * 2 * np.pi
                offset_x = radius * np.cos(angle)
                offset_z = radius * np.sin(angle)
                positions.append((offset_x, 0, offset_z))

        elif arrangement == 'grid':
            grid_size = int(np.ceil(np.sqrt(count)))
            cell_size_x = (raster.width * spacing) / grid_size
            cell_size_z = (raster.length * spacing) / grid_size
            start_x = -(grid_size * cell_size_x) / 2
            start_z = -(grid_size * cell_size_z) / 2

            copy_idx = 0
            for row in range(grid_size):
                for col in range(grid_size):
                    if copy_idx >= count:
                        break
                    offset_x = start_x + col * cell_size_x
                    offset_z = start_z + row * cell_size_z
                    positions.append((offset_x, 0, offset_z))
                    copy_idx += 1

        elif arrangement == 'spiral':
            spiral_radius_step = spacing * min(center_x, center_z) * 0.2
            angle_step = (2 * np.pi) / max(count / 2, 1)
            for i in range(count):
                angle = i * angle_step
                radius = i * spiral_radius_step
                offset_x = radius * np.cos(angle)
                offset_z = radius * np.sin(angle)
                positions.append((offset_x, 0, offset_z))

        return positions

    def _geometry_wave_field(self, raster, time):
        """Wave field geometry"""
        wave_type = self.params.scene_params.get('waveType', 'ripple')

        # Apply rotation to coordinates with speed and offset
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )
        angles = self._calculate_rotation_angles(
            time,
            self.params.rotationX,
            self.params.rotationY,
            self.params.rotationZ,
            self.params.rotation_speed,
            self.params.rotation_offset
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
        """Particle flow geometry with optional rotation"""
        pattern = self.params.scene_params.get('pattern', 'particles')

        # Apply rotation to coordinates if any rotation is non-zero
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )

        # Check if rotation is enabled
        has_rotation = (self.params.rotationX != 0 or
                       self.params.rotationY != 0 or
                       self.params.rotationZ != 0)

        if has_rotation:
            angles = self._calculate_rotation_angles(
                time,
                self.params.rotationX,
                self.params.rotationY,
                self.params.rotationZ,
                self.params.rotation_speed,
                self.params.rotation_offset
            )
            coords = rotate_coordinates(self.coords_cache, center, angles)
            z_coords, y_coords, x_coords = coords
        else:
            z_coords, y_coords, x_coords = self.coords_cache

        if pattern == 'spiral':
            base_mask = self._particle_spiral(raster, time, coords=(z_coords, y_coords, x_coords))
        elif pattern == 'galaxy':
            base_mask = self._particle_galaxy(raster, time, coords=(z_coords, y_coords, x_coords))
        elif pattern == 'explode':
            base_mask = self._particle_explode(raster, time, coords=(z_coords, y_coords, x_coords))
        else:
            # Default: flowing particles
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

            base_mask = mask

        # Apply copy arrangement if count > 1
        if self.params.objectCount > 1 and pattern in ['spiral', 'galaxy']:
            return self._apply_copy_arrangement(
                base_mask, raster,
                self.params.objectCount,
                self.params.copy_spacing,
                self.params.copy_arrangement
            )

        return base_mask

    def _particle_spiral(self, raster, time, coords=None):
        """Spiral/helix pattern with adjustable parameters - travels along Z axis"""
        if coords is None:
            z_coords, y_coords, x_coords = self.coords_cache
        else:
            z_coords, y_coords, x_coords = coords

        center_x = raster.width / 2
        center_y = raster.height / 2
        center_z = raster.length / 2

        # Size controls the overall radius of the helix
        radius = min(center_x, center_y) * self.params.size * 0.6

        # Density controls tightness of helix (rotations per unit length)
        # Higher density = more rotations = tighter spiral
        turns_per_length = 2 + self.params.density * 8  # 2-10 turns

        # Amplitude controls thickness of the helix tube
        tube_thickness = 1.5 + self.params.amplitude * 4  # 1.5-5.5 pixels

        # Number of separate helix strands (controlled by objectCount)
        num_strands = max(1, self.params.objectCount)

        mask = np.zeros(self.grid_shape, dtype=bool)

        for strand in range(num_strands):
            # Each strand has a phase offset
            phase_offset = (strand / num_strands) * 2 * np.pi

            # Create helix path along Z axis (depth/length)
            # For each Z position, calculate the expected X,Y based on helix equation
            z_normalized = (z_coords - center_z) / raster.length  # -0.5 to 0.5

            # Helix angle based on length position and animation
            angle = z_normalized * turns_per_length * 2 * np.pi + time * 2 + phase_offset

            # Expected helix positions (spiraling in XY plane as we move along Z)
            helix_x = center_x + radius * np.cos(angle)
            helix_y = center_y + radius * np.sin(angle)

            # Distance from helix path
            dx = x_coords - helix_x
            dy = y_coords - helix_y
            distance = np.sqrt(dx**2 + dy**2)

            # Particles along the helix path
            mask |= distance < tube_thickness

        return mask

    def _particle_galaxy(self, raster, time, coords=None):
        """Galaxy-style spiral arms with enhanced customization - travels along Z axis"""
        if coords is None:
            z_coords, y_coords, x_coords = self.coords_cache
        else:
            z_coords, y_coords, x_coords = coords

        center_x = raster.width / 2
        center_y = raster.height / 2
        center_z = raster.length / 2

        # Galaxy is in the XY plane (front-facing), extending along Z axis
        # Calculate cylindrical coordinates
        dx = x_coords - center_x
        dy = y_coords - center_y
        dz = z_coords - center_z

        radius_xy = np.sqrt(dx**2 + dy**2)
        angle = np.arctan2(dy, dx)

        # Size controls overall galaxy diameter (0.1-2.0 scale)
        galaxy_radius = min(center_x, center_y) * self.params.size * 0.9

        # Amplitude controls both disc thickness AND arm prominence
        # Lower amplitude = thin disc with subtle arms
        # Higher amplitude = thick disc with prominent arms
        base_disc_thickness = 1.5 + self.params.amplitude * 8  # 1.5-9.5 voxels

        # Density controls spiral tightness AND number of particles
        # Lower density = loose, open spiral
        # Higher density = tight, compressed spiral
        spiral_tightness = 1.0 + self.params.density * 4  # 1-5

        mask = np.zeros(self.grid_shape, dtype=bool)

        # Number of spiral arms (controlled by objectCount parameter)
        num_arms = max(2, min(6, self.params.objectCount))

        for arm in range(num_arms):
            arm_phase = (arm / num_arms) * 2 * np.pi

            # Logarithmic spiral: θ = a * ln(r)
            # Expected angle at this radius for this arm
            # Add time rotation for spinning galaxy
            expected_angle = spiral_tightness * np.log(radius_xy + 1) + arm_phase - time * 0.3

            # Angular distance from spiral arm (wrapping around)
            angle_diff = ((angle - expected_angle + np.pi) % (2 * np.pi)) - np.pi

            # Convert angular difference to linear distance at this radius
            arm_distance = np.abs(angle_diff * radius_xy)

            # Arm width varies with radius - thicker at center, thinner at edges
            # Also controlled by amplitude for more dramatic arms
            radius_factor = np.clip(radius_xy / (galaxy_radius + 0.1), 0, 1)
            arm_width = (2 + self.params.amplitude * 6) * (1.2 - radius_factor)

            # Distance from disc plane (Z axis) - variable thickness
            # Disc is thicker at center (bulge) and thinner at edges
            disc_thickness_at_radius = base_disc_thickness * (1.5 - radius_factor)
            disc_distance = np.abs(dz)

            # Add density variation along arms (more particles toward center)
            # This creates a more organic, cloud-like appearance
            density_factor = 1.0 - 0.3 * radius_factor

            # Combine conditions: near spiral arm AND near disc plane AND within galaxy radius
            in_arm = arm_distance < arm_width * density_factor
            in_disc = disc_distance < disc_thickness_at_radius
            in_galaxy = radius_xy < galaxy_radius

            mask |= (in_arm & in_disc & in_galaxy)

            # Add "dust lanes" - darker regions between arms
            # Create secondary, fainter structures
            if self.params.frequency > 2.0:  # Only add detail at higher frequency settings
                # Offset dust lane angle slightly
                dust_angle = expected_angle + np.pi / num_arms
                dust_angle_diff = ((angle - dust_angle + np.pi) % (2 * np.pi)) - np.pi
                dust_distance = np.abs(dust_angle_diff * radius_xy)

                # Narrower than main arms
                in_dust = dust_distance < arm_width * 0.4 * density_factor
                mask |= (in_dust & in_disc & in_galaxy)

        # Add central bulge (spheroidal)
        # Size controlled by size parameter
        bulge_radius = galaxy_radius * (0.15 + self.params.size * 0.1)
        # Bulge is slightly elongated along Z
        bulge_z_factor = 0.7  # Flatter bulge
        bulge_distance = np.sqrt(dx**2 + dy**2 + (dz * bulge_z_factor)**2)
        mask |= bulge_distance < bulge_radius

        # Add outer halo particles for visual interest (if amplitude is high)
        if self.params.amplitude > 0.5:
            halo_radius = galaxy_radius * 1.2
            halo_thickness = base_disc_thickness * 0.3

            # Sparse halo particles
            halo_condition = (
                (radius_xy > galaxy_radius * 0.9) &
                (radius_xy < halo_radius) &
                (disc_distance < halo_thickness) &
                # Make halo sparse using modulo pattern
                ((x_coords.astype(int) + y_coords.astype(int) + z_coords.astype(int)) % 3 == 0)
            )
            mask |= halo_condition

        return mask

    def _particle_explode(self, raster, time, coords=None):
        """Particles exploding from a random center point"""
        if coords is None:
            z_coords, y_coords, x_coords = self.coords_cache
        else:
            z_coords, y_coords, x_coords = coords

        # Use time to create explosion cycles
        # Each explosion lasts a few seconds, then resets
        explosion_cycle = 3.0  # seconds per explosion
        cycle_time = time % explosion_cycle

        # Generate a consistent random position for this cycle
        # Use floor division to get the cycle number
        cycle_num = int(time / explosion_cycle)

        # Pseudo-random center position based on cycle number
        np.random.seed(cycle_num * 42)
        center_x = np.random.randint(raster.width // 4, 3 * raster.width // 4)
        center_y = np.random.randint(raster.height // 4, 3 * raster.height // 4)
        center_z = np.random.randint(raster.length // 4, 3 * raster.length // 4)

        # Size controls the initial explosion size
        initial_radius = 2 + self.params.size * 3

        # Expansion over time - amplitude controls speed (5-15 units/sec for visible but not instant)
        # Reduced range to prevent particles from disappearing too quickly
        expansion_speed = 5 + self.params.amplitude * 10
        current_radius = initial_radius + expansion_speed * cycle_time

        # Shell thickness (ring of particles expanding)
        shell_thickness = 2 + self.params.size * 3

        # Calculate distance from explosion center
        dx = x_coords - center_x
        dy = y_coords - center_y
        dz = z_coords - center_z
        distance = np.sqrt(dx**2 + dy**2 + dz**2)

        # Density controls number of particles
        num_particles = int(50 + self.params.density * 200)

        # Create particle spray using polar coordinates
        mask = np.zeros(self.grid_shape, dtype=bool)

        np.random.seed(cycle_num * 42 + 1)  # Same seed for consistent directions

        for i in range(num_particles):
            # Random direction for each particle (spherical coordinates)
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, np.pi)

            # Particle position along its trajectory
            px = center_x + current_radius * np.sin(phi) * np.cos(theta)
            py = center_y + current_radius * np.sin(phi) * np.sin(theta)
            pz = center_z + current_radius * np.cos(phi)

            # Particle size (small)
            particle_size = 0.8 + self.params.size * 0.5

            # Distance to this particle
            pdx = x_coords - px
            pdy = y_coords - py
            pdz = z_coords - pz
            pdist = np.sqrt(pdx**2 + pdy**2 + pdz**2)

            mask |= pdist < particle_size

        return mask

    def _geometry_procedural(self, raster, time):
        """Procedural noise geometry with multiple pattern types"""
        pattern = self.params.scene_params.get('proceduralType', 'noise')

        if pattern == 'noise':
            return self._procedural_noise(raster, time)
        elif pattern == 'clouds':
            return self._procedural_clouds(raster, time)
        elif pattern == 'cellular':
            return self._procedural_cellular(raster, time)
        elif pattern == 'fractals':
            return self._procedural_fractals(raster, time)
        else:
            return self._procedural_noise(raster, time)

    def _procedural_noise(self, raster, time):
        """Multi-octave sine-based noise pattern"""
        # Apply rotation to coordinates with speed and offset
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )
        angles = self._calculate_rotation_angles(
            time,
            self.params.rotationX,
            self.params.rotationY,
            self.params.rotationZ,
            self.params.rotation_speed,
            self.params.rotation_offset
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)
        z_coords, y_coords, x_coords = coords

        scale = self.params.size * 0.1
        threshold = self.params.amplitude * 0.5

        # Base noise
        noise = (
            np.sin(x_coords * scale + time) *
            np.cos(y_coords * scale - time * 0.5) *
            np.sin(z_coords * scale + time * 0.3)
        )

        # Second octave
        noise += 0.5 * (
            np.sin(x_coords * scale * 2 - time * 1.5) *
            np.cos(z_coords * scale * 2 + time)
        )

        noise = (noise + 1.5) / 3.0
        return noise > threshold

    def _procedural_clouds(self, raster, time):
        """Volumetric cloud-like patterns with soft billowing"""
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )
        angles = self._calculate_rotation_angles(
            time,
            self.params.rotationX,
            self.params.rotationY,
            self.params.rotationZ,
            self.params.rotation_speed,
            self.params.rotation_offset
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)
        z_coords, y_coords, x_coords = coords

        # Frequency controlled by size
        freq = 0.15 * self.params.size

        # Multiple octaves for cloud-like appearance
        # Octave 1: Large features
        cloud = np.sin(x_coords * freq + time * 0.3) * \
                np.cos(y_coords * freq + time * 0.2) * \
                np.sin(z_coords * freq - time * 0.15)

        # Octave 2: Medium features
        cloud += 0.5 * (
            np.sin(x_coords * freq * 2.3 - time * 0.5) *
            np.cos(y_coords * freq * 1.8 + time * 0.3) *
            np.sin(z_coords * freq * 2.1 + time * 0.25)
        )

        # Octave 3: Fine details
        cloud += 0.25 * (
            np.sin(x_coords * freq * 4.7 + time * 0.8) *
            np.cos(y_coords * freq * 4.2 - time * 0.6) *
            np.sin(z_coords * freq * 4.5 + time * 0.7)
        )

        # Density controls how much cloud coverage
        # Amplitude controls the threshold (more = denser clouds)
        threshold = -0.5 + (1 - self.params.density) * 1.5 - self.params.amplitude * 0.5

        return cloud > threshold

    def _procedural_cellular(self, raster, time):
        """Cellular/Voronoi-like pattern with animated cells"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Number of cell centers based on density (ensure minimum of 3 cells)
        num_cells = max(3, int(5 + self.params.density * 15))  # 5-20 cells

        # Size controls cell size (ensure minimum scale to prevent empty grid)
        cell_scale = 1.0 / max(0.3, self.params.size + 0.1)

        mask = np.zeros(self.grid_shape, dtype=bool)

        # Generate pseudo-random cell centers that move over time
        np.random.seed(42)  # Fixed seed for consistent cells

        for i in range(num_cells):
            # Base position
            cx = np.random.uniform(0, raster.width)
            cy = np.random.uniform(0, raster.height)
            cz = np.random.uniform(0, raster.length)

            # Animate cell centers in orbital patterns
            angle = time * 0.5 + i * np.pi * 2 / num_cells
            orbit_radius = 3 + i % 5

            cx = (cx + np.cos(angle) * orbit_radius) % raster.width
            cy = (cy + np.sin(angle * 0.7) * orbit_radius) % raster.height
            cz = (cz + np.sin(angle * 0.5) * orbit_radius) % raster.length

            # Distance from cell center
            dx = x_coords - cx
            dy = y_coords - cy
            dz = z_coords - cz
            distance = np.sqrt(dx**2 + dy**2 + dz**2)

            # Amplitude controls cell wall thickness
            cell_radius = 8 * cell_scale
            wall_thickness = 1.5 + self.params.amplitude * 3

            # Create cell walls (hollow spheres)
            mask |= (distance < cell_radius) & (distance > (cell_radius - wall_thickness))

        return mask

    def _procedural_fractals(self, raster, time):
        """Fractal-like recursive patterns with self-similarity"""
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )
        angles = self._calculate_rotation_angles(
            time,
            self.params.rotationX,
            self.params.rotationY,
            self.params.rotationZ,
            self.params.rotation_speed,
            self.params.rotation_offset
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)
        z_coords, y_coords, x_coords = coords

        # Normalize coordinates to center
        nx = (x_coords - center[0]) / raster.width
        ny = (y_coords - center[1]) / raster.height
        nz = (z_coords - center[2]) / raster.length

        # Size controls the scale of the fractal
        scale = self.params.size * 3

        # Create a 3D fractal pattern using recursive sine functions
        # Each iteration adds smaller details
        fractal = np.zeros(self.grid_shape, dtype=np.float32)

        # Density controls number of iterations (detail level)
        iterations = 2 + int(self.params.density * 4)  # 2-6 iterations

        amplitude = 1.0
        frequency = 1.0

        for i in range(iterations):
            # Add rotated pattern at each scale
            angle = time * 0.5 + i * np.pi / 3

            fractal += amplitude * (
                np.sin((nx * np.cos(angle) - nz * np.sin(angle)) * frequency * scale + time) *
                np.cos(ny * frequency * scale - time * 0.3) *
                np.sin((nx * np.sin(angle) + nz * np.cos(angle)) * frequency * scale + time * 0.5)
            )

            # Reduce amplitude and increase frequency for next octave
            amplitude *= 0.5
            frequency *= 2.3

        # Amplitude parameter controls threshold
        threshold = -0.5 + (1 - self.params.amplitude) * 1.0

        return fractal > threshold

    def _geometry_grid(self, raster, time):
        """Grid - multiple pattern types with optional copy"""
        pattern = self.params.scene_params.get('gridPattern', 'full')

        if pattern == 'full':
            base_mask = self._grid_full(raster, time)
        elif pattern == 'dots':
            base_mask = self._grid_dots(raster, time)
        elif pattern == 'cross':
            base_mask = self._grid_cross(raster, time)
        elif pattern == 'wireframe':
            base_mask = self._grid_wireframe(raster, time)
        else:
            base_mask = self._grid_full(raster, time)

        # Apply copy arrangement if count > 1 (for wireframe only, since others fill volume)
        if self.params.objectCount > 1 and pattern in ['wireframe', 'cross']:
            return self._apply_copy_arrangement(
                base_mask, raster,
                self.params.objectCount,
                self.params.copy_spacing,
                self.params.copy_arrangement
            )

        return base_mask

    def _grid_full(self, raster, time):
        """Full volume - all voxels lit"""
        return np.ones(self.grid_shape, dtype=bool)

    def _grid_dots(self, raster, time):
        """Grid of dots/points at intersections - optimized vectorized version"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Density controls dot spacing
        spacing = max(2, int(8 - self.params.density * 6))  # 2-8 voxels apart

        # Size controls dot size
        dot_radius = 0.5 + self.params.size * 2  # 0.5-2.5 voxels

        # Use modulo to create repeating pattern instead of loops
        # This is much faster than iterating through each dot position

        # For each axis, find the distance to the nearest grid line
        x_dist_to_grid = np.minimum(x_coords % spacing, spacing - (x_coords % spacing))
        y_dist_to_grid = np.minimum(y_coords % spacing, spacing - (y_coords % spacing))
        z_dist_to_grid = np.minimum(z_coords % spacing, spacing - (z_coords % spacing))

        # Distance from nearest grid intersection point (3D)
        distance = np.sqrt(x_dist_to_grid**2 + y_dist_to_grid**2 + z_dist_to_grid**2)

        # Create mask where distance is less than dot radius
        mask = distance < dot_radius

        return mask

    def _grid_cross(self, raster, time):
        """Cross pattern through center with adjustable thickness"""
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )
        size = min(center)
        # Use density to control cross line thickness (1-10 pixels)
        line_thickness = 1 + self.params.density * 9
        return generate_cross_grid(self.coords_cache, center, size, line_thickness)

    def _grid_wireframe(self, raster, time):
        """Wireframe cube/box edges only"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Size controls the box size (0.3 to 0.95 of volume)
        size_factor = 0.3 + self.params.size * 0.65

        # Density controls edge thickness
        thickness = max(1, int(1 + self.params.density * 3))

        # Calculate box boundaries
        x_min = int(raster.width * (1 - size_factor) / 2)
        x_max = int(raster.width * (1 + size_factor) / 2)
        y_min = int(raster.height * (1 - size_factor) / 2)
        y_max = int(raster.height * (1 + size_factor) / 2)
        z_min = int(raster.length * (1 - size_factor) / 2)
        z_max = int(raster.length * (1 + size_factor) / 2)

        mask = np.zeros(self.grid_shape, dtype=bool)

        # Draw 12 edges of the cube
        # Bottom face (4 edges)
        mask[z_min:z_min+thickness, y_min:y_min+thickness, x_min:x_max] = True  # Bottom-front edge
        mask[z_min:z_min+thickness, y_max-thickness:y_max, x_min:x_max] = True  # Bottom-back edge
        mask[z_min:z_min+thickness, y_min:y_max, x_min:x_min+thickness] = True  # Bottom-left edge
        mask[z_min:z_min+thickness, y_min:y_max, x_max-thickness:x_max] = True  # Bottom-right edge

        # Top face (4 edges)
        mask[z_max-thickness:z_max, y_min:y_min+thickness, x_min:x_max] = True  # Top-front edge
        mask[z_max-thickness:z_max, y_max-thickness:y_max, x_min:x_max] = True  # Top-back edge
        mask[z_max-thickness:z_max, y_min:y_max, x_min:x_min+thickness] = True  # Top-left edge
        mask[z_max-thickness:z_max, y_min:y_max, x_max-thickness:x_max] = True  # Top-right edge

        # Vertical edges (4 edges)
        mask[z_min:z_max, y_min:y_min+thickness, x_min:x_min+thickness] = True  # Front-left edge
        mask[z_min:z_max, y_min:y_min+thickness, x_max-thickness:x_max] = True  # Front-right edge
        mask[z_min:z_max, y_max-thickness:y_max, x_min:x_min+thickness] = True  # Back-left edge
        mask[z_min:z_max, y_max-thickness:y_max, x_max-thickness:x_max] = True  # Back-right edge

        # Animate rotation
        if self.params.animationSpeed > 0:
            # Use existing rotation parameters
            center_point = (raster.width / 2, raster.height / 2, raster.length / 2)
            angles = (
                self.params.rotationX * np.pi + time * self.params.animationSpeed * 0.5,
                self.params.rotationY * np.pi + time * self.params.animationSpeed * 0.3,
                self.params.rotationZ * np.pi + time * self.params.animationSpeed * 0.4
            )
            # Note: This creates a static rotated box. For true rotation, we'd need to
            # transform the wireframe geometry, which is complex. This version works well as-is.

        return mask

    def _geometry_illusions(self, raster, time):
        """Optical illusion effects with optional rotation"""
        illusion_type = self.params.scene_params.get('illusionType', 'infiniteCorridor')

        # Apply rotation to coordinates if any rotation is non-zero
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )

        has_rotation = (self.params.rotationX != 0 or
                       self.params.rotationY != 0 or
                       self.params.rotationZ != 0)

        if has_rotation:
            angles = self._calculate_rotation_angles(
                time,
                self.params.rotationX,
                self.params.rotationY,
                self.params.rotationZ,
                self.params.rotation_speed,
                self.params.rotation_offset
            )
            coords = rotate_coordinates(self.coords_cache, center, angles)
        else:
            coords = self.coords_cache

        if illusion_type == 'infiniteCorridor':
            base_mask = self._illusion_infinite_corridor(raster, time, coords)
        elif illusion_type == 'waterfallIllusion':
            base_mask = self._illusion_waterfall(raster, time, coords)
        elif illusion_type == 'pulfrich':
            base_mask = self._illusion_pulfrich(raster, time, coords)
        elif illusion_type == 'moirePattern':
            base_mask = self._illusion_moire(raster, time, coords)
        else:
            base_mask = self._illusion_infinite_corridor(raster, time, coords)

        # Apply copy arrangement if count > 1
        if self.params.objectCount > 1:
            return self._apply_copy_arrangement(
                base_mask, raster,
                self.params.objectCount,
                self.params.copy_spacing,
                self.params.copy_arrangement
            )

        return base_mask

    def _illusion_infinite_corridor(self, raster, time, coords=None):
        """Infinite corridor - scrolling perspective frames along Y axis (vertical)"""
        if coords is None:
            z_coords, y_coords, x_coords = self.coords_cache
        else:
            z_coords, y_coords, x_coords = coords

        # Parameters
        frame_spacing = max(3, int(4 * (1 + self.params.density)))
        num_frames = int(5 + self.params.size * 5)

        # Continuous scroll offset (no wrapping at this level)
        scroll_offset = time * 3

        mask = np.zeros(self.grid_shape, dtype=bool)

        # Collect all frame data first so we can sort by depth
        frames_to_draw = []

        # Generate enough frames to fill the visible area plus wrapping buffer
        for frame in range(num_frames * 2):  # Double to handle wrapping
            # Position along Y axis (height) - scrolling upward
            base_y = (frame * frame_spacing - scroll_offset) % (frame_spacing * num_frames)
            y = int(base_y) % raster.height

            # Skip if this frame is outside visible range
            if y < 0 or y >= raster.height:
                continue

            # Calculate perspective scale based on continuous position (before wrapping)
            # Use the continuous base_y for smooth perspective transitions
            # Map to [0, 1] range across the full loop cycle
            normalized_pos = (base_y % (frame_spacing * num_frames)) / (frame_spacing * num_frames)
            scale = 0.2 + normalized_pos * 0.8 * self.params.size

            # Frame dimensions in XZ plane
            width = max(1, int(raster.width / 2 * scale))
            depth = max(1, int(raster.length / 2 * scale))

            # Store frame data (scale is our depth key - smaller = farther)
            frames_to_draw.append((scale, y, width, depth))

        # Sort frames by scale (smallest/farthest first, largest/nearest last)
        # This ensures proper depth ordering - distant frames drawn first, near frames on top
        frames_to_draw.sort(key=lambda f: f[0])

        # Now draw frames in back-to-front order
        center_x = raster.width // 2
        center_z = raster.length // 2

        for scale, y, width, depth in frames_to_draw:
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

    def _illusion_waterfall(self, raster, time, coords=None):
        """Waterfall illusion - moving vertical stripes"""
        if coords is None:
            z_coords, y_coords, x_coords = self.coords_cache
        else:
            z_coords, y_coords, x_coords = coords

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

    def _illusion_pulfrich(self, raster, time, coords=None):
        """Pulfrich effect - rotating objects with brightness variation in XY plane"""
        if coords is None:
            z_coords, y_coords, x_coords = self.coords_cache
        else:
            z_coords, y_coords, x_coords = coords

        # Density controls orbital radius (how spread out the ring is)
        # 0.0 = tight ring (radius 6), 1.0 = wide ring (radius 18)
        radius = 6 + self.params.density * 12
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

            # Size controls sphere size (0.3-3.0 -> sphere radius 1-7)
            # Using int to ensure at least 1 pixel radius
            obj_size = max(1, int(1 + self.params.size * 2))

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

    def _illusion_moire(self, raster, time, coords=None):
        """Moire pattern - overlapping rotated grids"""
        if coords is None:
            z_coords, y_coords, x_coords = self.coords_cache
        else:
            z_coords, y_coords, x_coords = coords

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

            # Return mask for spiral mode
            return dist_from_band < thickness

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

