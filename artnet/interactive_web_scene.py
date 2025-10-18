"""
Interactive Web-Controlled Scene
Receives parameters from web UI and renders in real-time
Compatible with sender.py and C++ simulator
"""

import numpy as np
import math
from artnet import Scene, Raster, RGB, HSV
from dataclasses import dataclass, field
from typing import Dict, Any


def vectorized_hsv_to_rgb(h, s, v):
    """
    A fast, NumPy-based conversion from HSV to RGB.
    Inputs H, S, V are NumPy arrays of shape (L, H, W).
    Output is a NumPy array of shape (L, H, W, 3) with dtype=uint8.
    """
    h_norm = h / 255.0
    s_norm = s / 255.0
    v_norm = v / 255.0

    i = np.floor(h_norm * 6)
    f = h_norm * 6 - i
    p = v_norm * (1 - s_norm)
    q = v_norm * (1 - f * s_norm)
    t = v_norm * (1 - (1 - f) * s_norm)

    i = i.astype(np.int32) % 6

    # Create an empty array for the RGB output
    rgb = np.zeros(h.shape + (3,), dtype=np.float32)

    # Use boolean array indexing for each of the 6 HSV cases
    mask = i == 0
    rgb[mask] = np.stack([v_norm[mask], t[mask], p[mask]], axis=-1)
    mask = i == 1
    rgb[mask] = np.stack([q[mask], v_norm[mask], p[mask]], axis=-1)
    mask = i == 2
    rgb[mask] = np.stack([p[mask], v_norm[mask], t[mask]], axis=-1)
    mask = i == 3
    rgb[mask] = np.stack([p[mask], q[mask], v_norm[mask]], axis=-1)
    mask = i == 4
    rgb[mask] = np.stack([t[mask], p[mask], v_norm[mask]], axis=-1)
    mask = i == 5
    rgb[mask] = np.stack([v_norm[mask], p[mask], q[mask]], axis=-1)

    return (rgb * 255).astype(np.uint8)


@dataclass
class SceneParameters:
    """Live parameters controlled by web UI"""
    # Scene selection
    scene_type: str = 'shapeMorph'

    # Global parameters (from your web UI)
    size: float = 1.0
    density: float = 0.5
    objectCount: int = 1
    frequency: float = 1.0
    amplitude: float = 0.5
    animationSpeed: float = 1.0

    # Movement parameters
    rotationX: float = 0.0
    rotationY: float = 0.0
    rotationZ: float = 0.0
    translateX: float = 0.0
    translateY: float = 0.0
    translateZ: float = 0.0

    # Scene-specific params (dict for flexibility)
    scene_params: Dict[str, Any] = field(default_factory=dict)

    # Global effects
    decay: float = 0.0
    strobe: str = 'off'
    pulse: str = 'off'
    invert: bool = False

    # Scrolling effect
    scrolling_enabled: bool = False
    scrolling_mode: str = 'strobe'
    scrolling_thickness: int = 5
    scrolling_direction: str = 'y'
    scrolling_speed: float = 1.0
    scrolling_invert: bool = False


class InteractiveWebScene(Scene):
    """
    Main scene class that renders based on web UI parameters.
    Compatible with sender.py - just pass as --scene argument.
    """

    def __init__(self, **kwargs):
        self.properties = kwargs.get("properties")
        self.params = SceneParameters()

        # Start with rainbow scene (simpler, working)
        self.params.scene_type = 'rainbow'

        # Pre-allocate coordinate grids for performance
        self.coords_cache = None

        # Previous frame for decay effect
        self.previous_frame = None

        # Scene renderers
        self.scene_renderers = {
            'shapeMorph': self.render_shape_morph,
            'particleFlow': self.render_particle_flow,
            'waveField': self.render_wave_field,
            'procedural': self.render_procedural,
            'rainbow': self.render_rainbow,
        }

        # State for particle-based scenes
        self.particles = []

        print(f"✨ InteractiveWebScene initialized (starting with rainbow scene)")

    def update_parameters(self, params_dict: Dict[str, Any]):
        """Update scene parameters from web UI (called by server)"""
        for key, value in params_dict.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
            else:
                # Scene-specific params
                self.params.scene_params[key] = value

    def render(self, raster: Raster, time: float):
        """
        Main render method called by sender.py @ 60 FPS
        This is the ONLY method sender.py cares about.
        """
        # Initialize coordinate cache if needed
        if self.coords_cache is None:
            self._init_coords(raster)

        # Initialize previous frame for decay
        if self.previous_frame is None:
            self.previous_frame = np.zeros_like(raster.data)

        # Clear or apply decay
        if self.params.decay == 0:
            raster.data.fill(0)
        else:
            # Decay effect: blend with previous frame
            current_weight = 1 - self.params.decay * 0.7
            previous_weight = self.params.decay * 0.7
            raster.data[:] = (
                raster.data * current_weight +
                self.previous_frame * previous_weight
            ).astype(np.uint8)

        # Render the current scene
        scene_renderer = self.scene_renderers.get(
            self.params.scene_type,
            self.render_wave_field
        )
        scene_renderer(raster, time * self.params.animationSpeed)

        # Apply global effects
        self._apply_global_effects(raster, time)

        # Store frame for next decay
        self.previous_frame[:] = raster.data

    def _init_coords(self, raster):
        """Initialize coordinate grids for vectorized rendering"""
        self.coords_cache = np.indices(
            (raster.length, raster.height, raster.width),
            sparse=True
        )

    # ================================================================
    # SCENE RENDERERS (Port from your JavaScript CoreScenes)
    # ================================================================

    def render_shape_morph(self, raster: Raster, time: float):
        """Shape morph scene - sphere, helix, torus, etc."""
        z_coords, y_coords, x_coords = self.coords_cache

        # Get shape from scene params
        shape = self.params.scene_params.get('shape', 'sphere')
        size = self.params.size

        # Center coordinates
        cx, cy, cz = raster.width / 2, raster.height / 2, raster.length / 2

        if shape == 'sphere':
            # Distance from center
            dx = x_coords - cx
            dy = y_coords - cy
            dz = z_coords - cz
            distance = np.sqrt(dx**2 + dy**2 + dz**2)

            # Pulsing radius
            radius = min(cx, cy, cz) * size * 0.8
            pulse = radius + np.sin(time * 2) * 2

            # Create sphere shell
            mask = (distance >= pulse - 1.5) & (distance <= pulse + 1.5)

            # Apply color (rainbow based on angle)
            hue = ((np.arctan2(dy, dx) + np.pi) * 128 / np.pi + time * 50).astype(np.int32) % 256
            # Use vectorized function for better performance
            hue_masked = hue[mask]
            if hue_masked.size > 0:
                colors = self._hsv_to_rgb_vectorized(hue_masked, 255, 255)
                raster.data[mask] = colors

        elif shape == 'helix':
            # Rotating helix pattern
            angle_speed = self.params.rotationY * 2
            helix_radius = min(cx, cz) * size * 0.5

            for i in range(max(1, self.params.objectCount)):
                t_offset = i * 2 * np.pi / max(1, self.params.objectCount)
                y_pos = ((time * 10 + i * raster.height / max(1, self.params.objectCount)) % raster.height)

                # Helix path
                angle = time * angle_speed + t_offset + y_pos * 0.5
                hx = cx + helix_radius * np.cos(angle)
                hz = cz + helix_radius * np.sin(angle)

                # Draw sphere at helix position
                dx = x_coords - hx
                dy = y_coords - y_pos
                dz = z_coords - hz
                distance = np.sqrt(dx**2 + dy**2 + dz**2)

                thickness = 3 * size
                mask = distance < thickness

                # Color based on height
                hue = int((i * 255 / max(1, self.params.objectCount) + time * 30) % 256)
                raster.data[mask] = [255, 100, 200]

        elif shape == 'cube':
            # Rotating wireframe cube
            cube_size = min(cx, cy, cz) * size * 0.8

            # Draw edges
            edge_thickness = 2
            for axis in range(3):
                for sign in [-1, 1]:
                    if axis == 0:  # X edges
                        mask = (
                            (np.abs(x_coords - (cx + sign * cube_size)) < edge_thickness) &
                            (np.abs(y_coords - cy) < cube_size) &
                            (np.abs(z_coords - cz) < cube_size)
                        )
                    elif axis == 1:  # Y edges
                        mask = (
                            (np.abs(y_coords - (cy + sign * cube_size)) < edge_thickness) &
                            (np.abs(x_coords - cx) < cube_size) &
                            (np.abs(z_coords - cz) < cube_size)
                        )
                    else:  # Z edges
                        mask = (
                            (np.abs(z_coords - (cz + sign * cube_size)) < edge_thickness) &
                            (np.abs(x_coords - cx) < cube_size) &
                            (np.abs(y_coords - cy) < cube_size)
                        )

                    raster.data[mask] = [100, 200, 255]

    def render_wave_field(self, raster: Raster, time: float):
        """Wave field scene - ripple, plane, interference"""
        z_coords, y_coords, x_coords = self.coords_cache

        wave_type = self.params.scene_params.get('waveType', 'ripple')
        freq = self.params.frequency
        amp = self.params.amplitude

        if wave_type == 'ripple':
            # Radial ripple from center
            cx, cz = raster.width / 2, raster.length / 2
            dx = x_coords - cx
            dz = z_coords - cz
            distance = np.sqrt(dx**2 + dz**2)

            wave = amp * raster.height * 0.5 * np.sin(distance * freq * 0.5 - time * 5)
            y_target = raster.height / 2 + wave

            # Draw wave as plane
            thickness = 2
            for y in range(raster.height):
                mask = np.abs(y - y_target) < thickness
                brightness = 255 * (1 - abs(y - raster.height / 2) / raster.height)
                raster.data[:, y, :][mask[:, 0, :]] = np.array([
                    int(brightness),
                    int(brightness * 0.5),
                    255
                ], dtype=np.uint8)

        elif wave_type == 'interference':
            # Two-source interference pattern
            wave1 = np.sin(x_coords * freq + time * 5)
            wave2 = np.sin(z_coords * freq - time * 5)
            combined = (wave1 + wave2) * amp * 128 + 128

            r = combined.astype(np.uint8)
            g = (128 - combined * 0.5).astype(np.uint8)
            b = (255 - combined).astype(np.uint8)

            raster.data[:] = np.stack([r, g, b], axis=-1)

        elif wave_type == 'plane':
            # Flat plane moving up and down
            y_target = raster.height / 2 + amp * raster.height * 0.4 * np.sin(time * 3)
            thickness = 2

            for y in range(raster.height):
                if abs(y - y_target) < thickness:
                    raster.data[:, y, :] = [100, 200, 255]

    def render_procedural(self, raster: Raster, time: float):
        """Procedural volume - 3D noise"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Simple 3D noise approximation
        scale = self.params.size * 0.1
        threshold = self.params.amplitude * 0.5

        # Multi-octave noise simulation
        noise = (
            np.sin(x_coords * scale + time) *
            np.cos(y_coords * scale - time * 0.5) *
            np.sin(z_coords * scale + time * 0.3)
        )

        # Add second octave
        noise += 0.5 * (
            np.sin(x_coords * scale * 2 - time * 1.5) *
            np.cos(z_coords * scale * 2 + time)
        )

        # Normalize
        noise = (noise + 1.5) / 3.0  # Range approximately 0-1

        # Threshold
        mask = noise > threshold

        # Color based on noise value
        if np.any(mask):
            noise_vals = noise[mask]
            brightness = ((noise_vals - threshold) / (1 - threshold) * 255).astype(np.uint8)
            brightness = np.clip(brightness, 0, 255)

            colors = np.stack([
                brightness,
                (brightness * 0.5).astype(np.uint8),
                (255 - brightness).astype(np.uint8)
            ], axis=-1)

            raster.data[mask] = colors

    def render_particle_flow(self, raster: Raster, time: float):
        """Particle flow scene - simple particle system"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Simplified particle flow - scrolling dots
        pattern = self.params.scene_params.get('pattern', 'particles')

        if pattern == 'particles':
            # Random particles flowing
            num_particles = int(100 * self.params.density)

            for i in range(num_particles):
                # Deterministic particle positions based on time and index
                seed = i * 12345
                px = ((seed % raster.width) + time * 5 * (1 + i % 3)) % raster.width
                py = ((seed * 7 % raster.height) + time * 3 * (1 + i % 2)) % raster.height
                pz = ((seed * 13 % raster.length) + time * 4 * (1 + i % 4)) % raster.length

                # Draw particle
                dx = x_coords - px
                dy = y_coords - py
                dz = z_coords - pz
                distance = np.sqrt(dx**2 + dy**2 + dz**2)

                particle_size = 2 * self.params.size
                mask = distance < particle_size

                # Color based on particle index
                hue = int((i * 255 / num_particles + time * 20) % 256)
                raster.data[mask] = self._hsv_to_rgb_simple(hue, 255, 255)

    def render_rainbow(self, raster: Raster, time: float):
        """Rainbow pattern (like rainbow_scene.py)"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Calculate hue for all voxels at once
        hue = (x_coords + y_coords + z_coords) * 4 + time * 50
        hue = hue.astype(np.int32) % 256

        # Create full arrays for saturation and value
        saturation = np.full_like(hue, 255, dtype=np.uint8)
        value = np.full_like(hue, 255, dtype=np.uint8)

        # Use the same vectorized HSV to RGB as rainbow_scene.py
        raster.data[:] = vectorized_hsv_to_rgb(hue, saturation, value)

    # ================================================================
    # GLOBAL EFFECTS
    # ================================================================

    def _apply_global_effects(self, raster: Raster, time: float):
        """Apply strobe, pulse, invert, scrolling effects"""
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

        # Scrolling effect
        if self.params.scrolling_enabled:
            self._apply_scrolling_effect(raster, time)

    def _apply_scrolling_effect(self, raster: Raster, time: float):
        """Apply scrolling strobe/pulse effect"""
        z_coords, y_coords, x_coords = self.coords_cache

        # Calculate scroll position
        max_dim = {
            'x': raster.width,
            'y': raster.height,
            'z': raster.length
        }[self.params.scrolling_direction]

        scroll_pos = (time * self.params.scrolling_speed * 10) % max_dim

        # Get voxel positions along scroll axis
        axis_coords = {
            'x': x_coords,
            'y': y_coords,
            'z': z_coords
        }[self.params.scrolling_direction]

        # Distance from scroll band
        dist_from_band = np.abs(axis_coords - scroll_pos)

        if self.params.scrolling_mode == 'strobe':
            # Turn pixels on/off in band
            mask = dist_from_band < self.params.scrolling_thickness
            if self.params.scrolling_invert:
                raster.data[mask] = 0  # Turn off in band
            else:
                raster.data[~mask] = 0  # Turn off outside band

        elif self.params.scrolling_mode == 'pulse':
            # Pulse brightness in band
            mask = dist_from_band < self.params.scrolling_thickness
            if np.any(mask):
                factor = 1 - dist_from_band[mask] / self.params.scrolling_thickness
                raster.data[mask] = (raster.data[mask] * factor[..., np.newaxis]).astype(np.uint8)

    # ================================================================
    # UTILITIES
    # ================================================================

    def _hsv_to_rgb_simple(self, h, s, v):
        """Simple HSV to RGB for single value or small arrays"""
        # Ensure inputs are numpy arrays
        h = np.atleast_1d(h)
        is_scalar = h.shape == (1,)

        h_norm = h / 255.0
        s_norm = s / 255.0
        v_norm = v / 255.0

        c = v_norm * s_norm
        x = c * (1 - np.abs((h_norm * 6) % 2 - 1))
        m = v_norm - c

        h_sector = (h_norm * 6).astype(int) % 6

        rgb = np.zeros((len(h), 3), dtype=np.uint8)

        for i, sector in enumerate(h_sector):
            if sector == 0:
                rgb[i] = [(c[i] + m) * 255, (x[i] + m) * 255, m * 255]
            elif sector == 1:
                rgb[i] = [(x[i] + m) * 255, (c[i] + m) * 255, m * 255]
            elif sector == 2:
                rgb[i] = [m * 255, (c[i] + m) * 255, (x[i] + m) * 255]
            elif sector == 3:
                rgb[i] = [m * 255, (x[i] + m) * 255, (c[i] + m) * 255]
            elif sector == 4:
                rgb[i] = [(x[i] + m) * 255, m * 255, (c[i] + m) * 255]
            else:
                rgb[i] = [(c[i] + m) * 255, m * 255, (x[i] + m) * 255]

        return rgb[0] if is_scalar else rgb

    def _hsv_to_rgb_vectorized(self, h, s, v):
        """Fast NumPy HSV to RGB conversion for full arrays"""
        h_norm = h / 255.0
        s_norm = s / 255.0 if np.isscalar(s) else s / 255.0
        v_norm = v / 255.0 if np.isscalar(v) else v / 255.0

        i = np.floor(h_norm * 6).astype(np.int32) % 6
        f = h_norm * 6 - i
        p = v_norm * (1 - s_norm)
        q = v_norm * (1 - f * s_norm)
        t = v_norm * (1 - (1 - f) * s_norm)

        rgb = np.zeros(h.shape + (3,), dtype=np.float32)

        mask = i == 0
        rgb[mask] = np.stack([v_norm[mask], t[mask], p[mask]], axis=-1)
        mask = i == 1
        rgb[mask] = np.stack([q[mask], v_norm[mask], p[mask]], axis=-1)
        mask = i == 2
        rgb[mask] = np.stack([p[mask], v_norm[mask], t[mask]], axis=-1)
        mask = i == 3
        rgb[mask] = np.stack([p[mask], q[mask], v_norm[mask]], axis=-1)
        mask = i == 4
        rgb[mask] = np.stack([t[mask], p[mask], v_norm[mask]], axis=-1)
        mask = i == 5
        rgb[mask] = np.stack([v_norm[mask], p[mask], q[mask]], axis=-1)

        return (rgb * 255).astype(np.uint8)
