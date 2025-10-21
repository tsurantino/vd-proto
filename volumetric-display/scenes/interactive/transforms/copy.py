"""
Copy arrangement and variation system
"""

import numpy as np
from ..geometry.utils import rotate_coordinates
from .rotation import calculate_rotation_angles


class CopyManager:
    """
    Manages copy arrangement, variation, and transforms for multi-object scenes.
    """

    def __init__(self, grid_shape):
        """
        Initialize copy manager.

        Args:
            grid_shape: Tuple of (length, height, width)
        """
        self.grid_shape = grid_shape

    def apply_arrangement(self, base_mask, raster, count, spacing, arrangement):
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
            # Arrange copies along X-axis with fixed spacing that wraps
            # This ensures equal spacing even when scrolling wraps objects around

            # Fixed spacing based on grid width divided by number of copies
            # This creates perfectly even distribution around the cylinder
            actual_spacing = int((raster.width * spacing) / count)

            for i in range(count):
                # Each copy is offset by a fixed amount, wrapping with modulo
                offset_x = (i * actual_spacing) % raster.width

                # Use proper translation with wrapping via modulo
                for z in range(raster.length):
                    for y in range(raster.height):
                        for x in range(raster.width):
                            if base_mask[z, y, x]:
                                new_x = (x + offset_x) % raster.width
                                combined_mask[z, y, new_x] = True

        elif arrangement == 'circular':
            # Arrange copies in a ring (XZ plane)
            radius = spacing * min(center_x, center_z) * 0.5

            for i in range(count):
                angle = (i / count) * 2 * np.pi
                offset_x = int(radius * np.cos(angle))
                offset_z = int(radius * np.sin(angle))

                # Translate base_mask to new position
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

    def calculate_positions(self, raster, count, spacing, arrangement, center):
        """
        Calculate offset positions for each copy.

        Args:
            raster: Raster object with grid dimensions
            count: Number of copies
            spacing: Distance multiplier between copies
            arrangement: 'linear', 'circular', 'grid', or 'spiral'
            center: Tuple of (cx, cy, cz)

        Returns:
            List of (offset_x, offset_y, offset_z) tuples
        """
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

    def generate_with_variation(self, raster, time, shape_generator, params, coords, base_center):
        """
        Generate multiple copies with individual scale, rotation, and translation variation.

        Args:
            raster: Raster object with grid dimensions
            time: Current animation time
            shape_generator: Function to generate a single shape (shape, coords, center, size, copy_index)
            params: SceneParameters object
            coords: Base coordinate arrays
            base_center: Tuple of (cx, cy, cz)

        Returns:
            Combined mask with all varied copies
        """
        combined_mask = np.zeros(self.grid_shape, dtype=bool)
        count = params.objectCount
        spacing = params.copy_spacing
        arrangement = params.copy_arrangement

        # Calculate positions for each copy
        positions = self.calculate_positions(raster, count, spacing, arrangement, base_center)

        # Calculate effective variations using two-level offset system
        effective_rotation_var = params.copy_rotation_var if params.copy_rotation_var > 0 else params.global_copy_offset
        effective_translation_var = params.copy_translation_var if params.copy_translation_var > 0 else params.global_copy_offset

        # Generate each copy with its own offset
        for i, (offset_x, offset_y, offset_z) in enumerate(positions):
            # Apply copy rotation with variation
            # When variation > 0, each copy gets a phase offset affecting rotation speed
            rotation_phase = (i * effective_rotation_var) if effective_rotation_var > 0 else 0

            # Apply copy rotation to coordinates
            copy_coords = coords
            # Check if using copy rotation override or main rotation
            use_copy_rot = params.use_copy_rotation_override and (
                params.copy_rotation_x != 0 or
                params.copy_rotation_y != 0 or
                params.copy_rotation_z != 0
            )

            if use_copy_rot:
                # Use copy rotation speed and offset for animation
                copy_rot_angles = calculate_rotation_angles(
                    time,
                    params.copy_rotation_x,
                    params.copy_rotation_y,
                    params.copy_rotation_z,
                    params.copy_rotation_speed,
                    params.copy_rotation_offset
                )

                # Apply rotation variation to create varied rotation per copy
                if effective_rotation_var > 0:
                    phase_shift = rotation_phase * 2 * np.pi
                    copy_rot_angles = (
                        copy_rot_angles[0] + phase_shift,
                        copy_rot_angles[1] + phase_shift,
                        copy_rot_angles[2] + phase_shift
                    )

                copy_coords = rotate_coordinates(coords, base_center, copy_rot_angles)

            # Apply copy translation with variation
            # When variation > 0, each copy gets a wave-like translation offset
            translation_offset_x = 0
            translation_offset_y = 0
            translation_offset_z = 0

            if params.copy_translation_x != 0 or params.copy_translation_y != 0 or params.copy_translation_z != 0:
                # Use copy translation speed for animation
                if params.copy_translation_speed > 0:
                    # Animate with speed and offset
                    wave_time_x = time * params.copy_translation_speed * 1.0
                    wave_time_y = time * params.copy_translation_speed * (1.0 + params.copy_translation_offset * 0.5)
                    wave_time_z = time * params.copy_translation_speed * (1.0 + params.copy_translation_offset * 1.0)

                    # Apply translation variation to create wave pattern across copies
                    if effective_translation_var > 0:
                        wave_phase = rotation_phase * 2 * np.pi
                        wave_time_x += wave_phase
                        wave_time_y += wave_phase
                        wave_time_z += wave_phase

                    translation_offset_x = params.copy_translation_x * 10 * np.sin(wave_time_x)
                    translation_offset_y = params.copy_translation_y * 10 * np.sin(wave_time_y)
                    translation_offset_z = params.copy_translation_z * 10 * np.sin(wave_time_z)
                else:
                    # Static offset
                    translation_offset_x = params.copy_translation_x * 10
                    translation_offset_y = params.copy_translation_y * 10
                    translation_offset_z = params.copy_translation_z * 10

            # Create center position for this copy (base arrangement + translation offsets)
            copy_center = (
                base_center[0] + offset_x + translation_offset_x,
                base_center[1] + offset_y + translation_offset_y,
                base_center[2] + offset_z + translation_offset_z
            )

            # Generate shape with scale and animation offset
            copy_mask = shape_generator(raster, time, copy_coords, copy_center, params.size, i)

            # Merge into combined mask
            combined_mask |= copy_mask

        return combined_mask
