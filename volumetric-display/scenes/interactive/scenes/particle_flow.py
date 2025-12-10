"""
Particle Flow Scene
Spiral, galaxy, explosion, and flowing particle patterns
"""

import numpy as np
from .base import BaseScene
from ..geometry.particles import (
    generate_spiral, generate_galaxy, generate_explode, generate_flowing_particles
)
from ..transforms import CopyManager, apply_object_scrolling, calculate_rotation_angles
from ..geometry.utils import rotate_coordinates


class ParticleFlowScene(BaseScene):
    """Particle flow scene with various particle patterns."""

    def __init__(self, grid_shape, coords_cache):
        super().__init__(grid_shape, coords_cache)
        self.copy_manager = CopyManager(grid_shape)

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate particle flow geometry."""
        pattern = params.scene_params.get('pattern', 'particles')

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

        if pattern == 'spiral':
            base_mask = generate_spiral(coords, self.grid_shape, params, time)
        elif pattern == 'galaxy':
            base_mask = generate_galaxy(coords, self.grid_shape, params, time)
        elif pattern == 'explode':
            base_mask = generate_explode(coords, self.grid_shape, params, time)
        else:
            # Default: flowing particles
            base_mask = generate_flowing_particles(coords, self.grid_shape, params, time)

        # Apply copy arrangement if count > 1 (for spiral and galaxy)
        if params.objectCount > 1 and pattern in ['spiral', 'galaxy']:
            base_mask, copy_indices = self.copy_manager.apply_arrangement(
                base_mask, raster,
                params.objectCount,
                params.copy_spacing,
                params.copy_arrangement
            )
        else:
            copy_indices = np.where(base_mask, 0, -1).astype(np.int8)

        # Apply object scrolling
        mask = apply_object_scrolling(base_mask, raster, params, time)

        return mask, copy_indices

    @classmethod
    def get_enabled_parameters(cls):
        return [
            'size', 'density', 'amplitude', 'objectCount',
            'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset',
            'copy_spacing', 'object_scroll_speed'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return ['rotation', 'scrolling', 'copy']

    @classmethod
    def get_defaults(cls):
        return {
            'size': 0.8,
            'density': 0.4,
            'amplitude': 0.5,
            'objectCount': 3,
            'rotationX': 0.0,
            'rotationY': 0.0,
            'rotationZ': 0.0,
            'rotation_speed': 0.0,
            'rotation_offset': 0.0,
            'copy_spacing': 1.5,
            'copy_arrangement': 'circular',
            'object_scroll_speed': 0.0,
            'object_scroll_direction': 'y'
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'size': 'Particle/helix radius',
            'density': 'Particle count or spiral tightness',
            'amplitude': 'Thickness or expansion speed',
            'objectCount': 'Number of strands/arms or copies'
        }
