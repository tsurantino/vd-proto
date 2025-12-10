"""
Shape Morph Scene
Morphing geometric shapes: sphere, cube, torus, pyramid
"""

import numpy as np
from .base import BaseScene
from ..geometry.shapes import generate_pulsing_sphere, generate_cube, generate_torus, generate_pyramid
from ..transforms import CopyManager, apply_object_scrolling_with_indices, calculate_rotation_angles
from ..geometry.utils import rotate_coordinates


class ShapeMorphScene(BaseScene):
    """Shape morphing scene with pulsing geometric shapes."""

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)
        self.copy_manager = CopyManager(grid_shape)

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate shape morph geometry."""
        shape = params.scene_params.get('shape', 'sphere')

        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )

        # Apply rotation to coordinates with speed and offset
        angles = calculate_rotation_angles(
            time,
            params.rotationX,
            params.rotationY,
            params.rotationZ,
            params.rotation_speed,
            params.rotation_offset
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)

        # Check if we need to generate copies with variation
        has_variation = (params.global_copy_offset > 0 or
                        params.copy_scale_offset > 0 or
                        params.copy_rotation_var > 0 or
                        params.copy_translation_var > 0)

        if params.objectCount > 1 and has_variation:
            # Generate with individual variation per copy
            mask, copy_indices = self.copy_manager.generate_with_variation(
                raster, time, self._generate_single_shape_wrapper(shape, params), params, coords, center
            )
        else:
            # Generate base shape
            base_mask = self._generate_single_shape(raster, time, shape, coords, center, params.size, 0, params)

            # Apply copy arrangement if count > 1 (simple translation without offsets)
            if params.objectCount > 1:
                mask, copy_indices = self.copy_manager.apply_arrangement(
                    base_mask, raster,
                    params.objectCount,
                    params.copy_spacing,
                    params.copy_arrangement
                )
            else:
                mask = base_mask
                copy_indices = np.where(mask, 0, -1).astype(np.int8)

        # Apply object scrolling (to both mask and copy_indices)
        mask, copy_indices = apply_object_scrolling_with_indices(mask, copy_indices, raster, params, time)

        return mask, copy_indices

    def _generate_single_shape_wrapper(self, shape, params):
        """Wrapper to match CopyManager signature."""
        def wrapper(raster, time, coords, center, size, copy_index):
            return self._generate_single_shape(raster, time, shape, coords, center, size, copy_index, params)
        return wrapper

    def _generate_single_shape(self, raster, time, shape, coords, center, size, copy_index, params):
        """Generate a single shape with optional per-copy animation/scale offset."""
        # Calculate effective offset using two-level system
        effective_scale_offset = params.copy_scale_offset if params.copy_scale_offset > 0 else params.global_copy_offset

        # Apply animation offset for scaling animation
        offset_time = time + (copy_index * effective_scale_offset * 2 * np.pi / params.scaling_speed if params.scaling_speed > 0 else 0)

        # Apply scale offset (each copy gets progressively larger/smaller)
        scale_multiplier = 1.0 + (copy_index * effective_scale_offset * 0.2)
        effective_size = size * scale_multiplier

        if shape == 'sphere':
            radius = min(center) * effective_size * 0.8
            return generate_pulsing_sphere(
                coords, center, radius, offset_time,
                pulse_speed=params.scaling_speed,
                pulse_amount=params.scaling_amount
            )

        elif shape == 'cube':
            base_size = min(center) * effective_size * 0.8
            pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(offset_time * params.scaling_speed)
            cube_size = base_size * pulse
            edge_thickness = 1.0 + params.density * 2.0
            return generate_cube(coords, center, cube_size, edge_thickness)

        elif shape == 'torus':
            base_major_r = min(center[0], center[2]) * effective_size * 0.6
            pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(offset_time * params.scaling_speed)
            major_r = base_major_r * pulse
            minor_r = major_r * 0.3
            return generate_torus(coords, center, major_r, minor_r)

        elif shape == 'pyramid':
            base_base_size = min(center[0], center[1]) * effective_size * 0.6
            base_height = raster.length * effective_size * 0.9
            pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(offset_time * params.scaling_speed)
            base_size = base_base_size * pulse
            height = base_height * pulse
            return generate_pyramid(coords, center, base_size, height)

        else:
            # Default sphere
            from ..geometry.shapes import generate_sphere
            radius = min(center) * effective_size * 0.8
            return generate_sphere(coords, center, radius)

    @classmethod
    def get_enabled_parameters(cls):
        return [
            'size', 'density', 'scaling_amount', 'scaling_speed',
            'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset',
            'objectCount', 'copy_spacing', 'copy_scale_offset', 'copy_rotation_var', 'copy_translation_var',
            'copy_translation_x', 'copy_translation_y', 'copy_translation_z',
            'copy_translation_speed', 'copy_translation_offset',
            'object_scroll_speed'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return ['scale', 'rotation', 'translation', 'scrolling', 'copy']

    @classmethod
    def get_defaults(cls):
        return {
            'size': 1.2,
            'density': 0.6,
            'scaling_amount': 1.5,
            'scaling_speed': 2.0,
            'rotationX': 0.0,
            'rotationY': 0.0,
            'rotationZ': 0.0,
            'rotation_speed': 0.0,
            'rotation_offset': 0.0,
            'objectCount': 1,
            'copy_spacing': 1.5,
            'copy_arrangement': 'linear',
            'copy_scale_offset': 0.0,
            'copy_rotation_var': 0.0,
            'copy_translation_var': 0.0,
            'use_copy_rotation_override': False,
            'copy_rotation_x': 0.0,
            'copy_rotation_y': 0.0,
            'copy_rotation_z': 0.0,
            'copy_rotation_speed': 0.0,
            'copy_rotation_offset': 0.0,
            'copy_translation_x': 0.0,
            'copy_translation_y': 0.0,
            'copy_translation_z': 0.0,
            'copy_translation_speed': 0.0,
            'copy_translation_offset': 0.0,
            'object_scroll_speed': 0.0,
            'object_scroll_direction': 'y'
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'size': 'Controls shape size',
            'density': 'Controls cube edge thickness',
            'scaling_amount': 'Pulsing magnitude',
            'scaling_speed': 'Pulsing frequency'
        }
