"""
Procedural Scene
Noise, clouds, cellular, and fractal patterns
"""

import numpy as np
from .base import BaseScene
from ..geometry.procedural import (
    generate_noise, generate_clouds, generate_cellular, generate_fractals
)
from ..transforms import apply_object_scrolling, calculate_rotation_angles
from ..geometry.utils import rotate_coordinates


class ProceduralScene(BaseScene):
    """Procedural noise scene with various pattern types."""

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate procedural geometry."""
        pattern = params.scene_params.get('proceduralType', 'noise')

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

        if pattern == 'noise':
            mask = generate_noise(coords, self.grid_shape, params, time, center, angles)
        elif pattern == 'clouds':
            mask = generate_clouds(coords, self.grid_shape, params, time, center, angles)
        elif pattern == 'cellular':
            mask = generate_cellular(coords, self.grid_shape, params, time)
        elif pattern == 'fractals':
            mask = generate_fractals(coords, self.grid_shape, params, time, center, angles)
        else:
            mask = generate_noise(coords, self.grid_shape, params, time, center, angles)

        # Apply object scrolling
        mask = apply_object_scrolling(mask, raster, params, time)

        return mask, None  # No copy indices for procedural

    @classmethod
    def get_enabled_parameters(cls):
        return [
            'size', 'density', 'amplitude', 'scaling_amount', 'scaling_speed',
            'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset',
            'object_scroll_speed'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return ['scale', 'rotation', 'scrolling']

    @classmethod
    def get_defaults(cls):
        return {
            'size': 1.5,
            'density': 0.5,
            'amplitude': 0.5,
            'scaling_amount': 1.0,
            'scaling_speed': 1.0,
            'rotationX': 0.0,
            'rotationY': 0.0,
            'rotationZ': 0.0,
            'rotation_speed': 0.0,
            'rotation_offset': 0.0,
            'object_scroll_speed': 0.0,
            'object_scroll_direction': 'y',
            'objectCount': 1
        }

    @classmethod
    def get_tooltips(cls):
        return {
            'size': 'Pattern scale/frequency',
            'density': 'Coverage or iteration count',
            'amplitude': 'Threshold or wall thickness'
        }
