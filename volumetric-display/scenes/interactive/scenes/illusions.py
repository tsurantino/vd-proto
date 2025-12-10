"""
Illusions Scene
Optical illusion effects: infinite corridor, waterfall, pulfrich, moire
"""

import numpy as np
from .base import BaseScene
from ..geometry.illusions import (
    generate_infinite_corridor, generate_waterfall,
    generate_pulfrich, generate_moire
)
from ..transforms import CopyManager, calculate_rotation_angles
from ..geometry.utils import rotate_coordinates


class IllusionsScene(BaseScene):
    """Optical illusion scene with various illusion patterns."""

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)
        self.copy_manager = CopyManager(grid_shape)

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate illusion geometry."""
        illusion_type = params.scene_params.get('illusionType', 'infiniteCorridor')

        # Apply rotation to coordinates if any rotation is non-zero
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )

        has_rotation = (params.rotationX != 0 or
                       params.rotationY != 0 or
                       params.rotationZ != 0)

        if has_rotation:
            angles = calculate_rotation_angles(
                time,
                params.rotationX,
                params.rotationY,
                params.rotationZ,
                params.rotation_speed,
                params.rotation_offset
            )
            coords = rotate_coordinates(self.coords_cache, center, angles)
        else:
            coords = self.coords_cache

        if illusion_type == 'infiniteCorridor':
            base_mask = generate_infinite_corridor(coords, self.grid_shape, params, time)
        elif illusion_type == 'waterfallIllusion':
            base_mask = generate_waterfall(coords, self.grid_shape, params, time)
        elif illusion_type == 'pulfrich':
            base_mask = generate_pulfrich(coords, self.grid_shape, params, time)
        elif illusion_type == 'moirePattern':
            base_mask = generate_moire(coords, self.grid_shape, params, time)
        else:
            base_mask = generate_infinite_corridor(coords, self.grid_shape, params, time)

        # Apply copy arrangement if count > 1
        if params.objectCount > 1:
            base_mask, copy_indices = self.copy_manager.apply_arrangement(
                base_mask, raster,
                params.objectCount,
                params.copy_spacing,
                params.copy_arrangement
            )
        else:
            copy_indices = np.where(base_mask, 0, -1).astype(np.int8)

        return base_mask, copy_indices

    @classmethod
    def get_enabled_parameters(cls):
        return [
            'size', 'density',
            'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset',
            'objectCount', 'copy_spacing'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return ['rotation', 'copy']

    @classmethod
    def get_defaults(cls):
        return {
            'size': 1.0,
            'density': 0.0,
            'rotationX': 0.0,
            'rotationY': 0.0,
            'rotationZ': 0.0,
            'rotation_speed': 0.0,
            'rotation_offset': 0.0,
            'objectCount': 1,
            'copy_spacing': 1.5,
            'copy_arrangement': 'linear'
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'size': 'Frame count or object size',
            'density': 'Frame/stripe spacing'
        }
