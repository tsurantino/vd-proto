"""
Wave Field Scene
Ripple, plane, standing, and interference wave patterns
"""

import numpy as np
from .base import BaseScene
from ..geometry.waves import (
    generate_ripple_wave, generate_plane_wave,
    generate_standing_wave, generate_interference_wave
)
from ..transforms import apply_object_scrolling, calculate_rotation_angles
from ..geometry.utils import rotate_coordinates


class WaveFieldScene(BaseScene):
    """Wave field scene with various wave patterns."""

    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """Generate wave field geometry."""
        wave_type = params.scene_params.get('waveType', 'ripple')

        # Apply rotation to coordinates with speed and offset
        center = (
            raster.width / 2,
            raster.height / 2,
            raster.length / 2
        )
        angles = calculate_rotation_angles(
            time,
            params.rotationX,
            params.rotationY,
            params.rotationZ,
            params.rotation_speed,
            params.rotation_offset
        )
        coords = rotate_coordinates(self.coords_cache, center, angles)

        # Apply pulsing/scaling effect to amplitude
        pulse = 1.0 + (params.scaling_amount * 0.1) * np.sin(time * params.scaling_speed)
        modulated_amplitude = params.amplitude * pulse

        if wave_type == 'ripple':
            mask = generate_ripple_wave(
                coords, self.grid_shape, time,
                frequency=params.frequency,
                amplitude=modulated_amplitude,
                speed=5
            )
        elif wave_type == 'plane':
            mask = generate_plane_wave(
                coords, self.grid_shape, time,
                amplitude=modulated_amplitude,
                speed=3,
                direction='x',
                frequency=params.frequency
            )
        elif wave_type == 'standing':
            mask = generate_standing_wave(
                coords, self.grid_shape, time,
                frequency=params.frequency,
                amplitude=modulated_amplitude
            )
        elif wave_type == 'interference':
            mask, _ = generate_interference_wave(
                coords, self.grid_shape, time,
                frequency=params.frequency,
                amplitude=modulated_amplitude
            )
        else:
            mask = generate_ripple_wave(
                coords, self.grid_shape, time,
                frequency=params.frequency,
                amplitude=modulated_amplitude
            )

        # Apply object scrolling
        mask = apply_object_scrolling(mask, raster, params, time)

        return mask

    @classmethod
    def get_enabled_parameters(cls):
        return [
            'size', 'frequency', 'amplitude', 'scaling_amount', 'scaling_speed',
            'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset',
            'object_scroll_speed'
        ]

    @classmethod
    def get_enabled_tabs(cls):
        return ['scale', 'rotation', 'scrolling']

    @classmethod
    def get_defaults(cls):
        return {
            'size': 1.0,
            'frequency': 2.0,
            'amplitude': 0.6,
            'scaling_amount': 1.0,
            'scaling_speed': 2.0,
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
            'frequency': 'Wave frequency',
            'amplitude': 'Wave height',
            'scaling_amount': 'Modulates amplitude',
            'scaling_speed': 'Pulse frequency'
        }
