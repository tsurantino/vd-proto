"""
Grid Scene
Full volume, dots, cross, and wireframe patterns
"""

import numpy as np
from .base import BaseScene
from ..geometry.grids import generate_full, generate_dots, generate_cross, generate_wireframe
from ..transforms import CopyManager, apply_object_scrolling_with_indices, calculate_rotation_angles
from ..geometry.utils import rotate_coordinates


class GridScene(BaseScene):
    """Grid scene with various grid patterns."""

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)
        self.copy_manager = CopyManager(grid_shape)

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate grid geometry."""
        pattern = params.scene_params.get('gridPattern', 'full')

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

        if pattern == 'full':
            base_mask = generate_full(self.grid_shape)
        elif pattern == 'dots':
            base_mask = generate_dots(coords, self.grid_shape, params, time)
        elif pattern == 'cross':
            base_mask = generate_cross(coords, self.grid_shape, params, time, center)
        elif pattern == 'wireframe':
            base_mask = generate_wireframe(coords, self.grid_shape, params, time)
        else:
            base_mask = generate_full(self.grid_shape)

        # Apply copy arrangement if count > 1 (for wireframe and cross only)
        if params.objectCount > 1 and pattern in ['wireframe', 'cross']:
            base_mask, copy_indices = self.copy_manager.apply_arrangement(
                base_mask, raster,
                params.objectCount,
                params.copy_spacing,
                params.copy_arrangement
            )
        else:
            copy_indices = np.where(base_mask, 0, -1).astype(np.int8)

        # Apply object scrolling (to both mask and copy_indices)
        mask, copy_indices = apply_object_scrolling_with_indices(base_mask, copy_indices, raster, params, time)

        return mask, copy_indices

    @classmethod
    def get_enabled_parameters(cls):
        return [
            'size', 'density', 'scaling_amount', 'scaling_speed',
            'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset',
            'objectCount', 'copy_spacing', 'object_scroll_speed'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return ['scale', 'rotation', 'scrolling', 'copy']

    @classmethod
    def get_defaults(cls):
        return {
            'size': 1.5,
            'density': 0.3,
            'scaling_amount': 1.0,
            'scaling_speed': 1.0,
            'rotationX': 0.0,
            'rotationY': 0.0,
            'rotationZ': 0.0,
            'rotation_speed': 0.0,
            'rotation_offset': 0.0,
            'objectCount': 1,
            'copy_spacing': 1.5,
            'copy_arrangement': 'grid',
            'object_scroll_speed': 0.0,
            'object_scroll_direction': 'y'
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'size': 'Dot/box size',
            'density': 'Spacing or line thickness'
        }
