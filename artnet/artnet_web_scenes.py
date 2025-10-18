"""
Scene Adapters for Web UI
Translates web interface scene definitions to Python Scene classes
"""

import math
import numpy as np
from artnet import RGB, Raster, Scene


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB"""
    # Handle case where hex_color might be a dict or other non-string type
    if not isinstance(hex_color, str):
        # Return default cyan if invalid input
        return (100, 200, 255)

    hex_color = hex_color.lstrip("#")
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        # Return default cyan if parsing fails
        return (100, 200, 255)


def get_color_from_state(color_state, time=0.0):
    """Extract RGB color from color state"""
    if color_state.get('mode') == 'single':
        single_color = color_state.get('singleColor', '#64C8FF')
        r, g, b = hex_to_rgb(single_color)
        return RGB(r, g, b)
    elif color_state.get('mode') == 'gradient':
        # For now, use first gradient color
        colors = color_state.get('gradientColors', [])
        if colors:
            r, g, b = hex_to_rgb(colors[0])
            return RGB(r, g, b)
    return RGB(100, 200, 255)  # Default cyan


class WebShapeMorphScene(Scene):
    """Shape morph scene adapter"""

    def __init__(self, params, global_params, color_state):
        self.shape = params.get('shape', 'sphere')
        self.size = global_params.get('size', 1.0)
        self.density = global_params.get('density', 0.5)
        self.rotation_x = global_params.get('rotationX', 0.0)
        self.rotation_y = global_params.get('rotationY', 0.0)
        self.rotation_z = global_params.get('rotationZ', 0.0)
        self.color_state = color_state

    def render(self, raster: Raster, time: float):
        """Render shape"""
        cx = raster.width / 2
        cy = raster.height / 2
        cz = raster.length / 2

        # Get color
        color = get_color_from_state(self.color_state, time)

        # Apply rotation based on time and params
        rot_time = time * 0.5
        rot_x = self.rotation_x * rot_time
        rot_y = self.rotation_y * rot_time
        rot_z = self.rotation_z * rot_time

        if self.shape == 'sphere':
            self._render_sphere(raster, cx, cy, cz, color)
        elif self.shape == 'cube':
            self._render_cube(raster, cx, cy, cz, color)
        elif self.shape == 'helix':
            self._render_helix(raster, cx, cy, cz, color, time)
        elif self.shape == 'torus':
            self._render_torus(raster, cx, cy, cz, color, time)
        elif self.shape == 'pyramid':
            self._render_pyramid(raster, cx, cy, cz, color)
        elif self.shape == 'plane':
            self._render_plane(raster, cx, cy, cz, color)

    def _render_sphere(self, raster, cx, cy, cz, color):
        """Render sphere"""
        radius = min(raster.width, raster.height, raster.length) * 0.35 * self.size

        for x in range(raster.width):
            for y in range(raster.height):
                for z in range(raster.length):
                    dx = x - cx
                    dy = y - cy
                    dz = z - cz
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)

                    if abs(dist - radius) < (1.0 + self.density * 2):
                        raster.set_pix(x, y, z, color)

    def _render_cube(self, raster, cx, cy, cz, color):
        """Render cube"""
        size = min(raster.width, raster.height, raster.length) * 0.3 * self.size
        half = size / 2
        thickness = max(1, int(1 + self.density * 2))

        for x in range(raster.width):
            for y in range(raster.height):
                for z in range(raster.length):
                    dx = abs(x - cx)
                    dy = abs(y - cy)
                    dz = abs(z - cz)

                    # Check if on cube edge
                    if dx <= half and dy <= half and dz <= half:
                        on_edge = (
                            dx >= half - thickness or
                            dy >= half - thickness or
                            dz >= half - thickness
                        )
                        if on_edge:
                            raster.set_pix(x, y, z, color)

    def _render_helix(self, raster, cx, cy, cz, color, time):
        """Render helix"""
        radius = min(raster.width, raster.length) * 0.3 * self.size
        num_points = int(200 * (1 + self.density))

        for i in range(num_points):
            t = i / num_points * 4 * math.pi + time
            x = int(cx + radius * math.cos(t))
            y = int(i / num_points * raster.height)
            z = int(cz + radius * math.sin(t))

            if 0 <= x < raster.width and 0 <= y < raster.height and 0 <= z < raster.length:
                raster.set_pix(x, y, z, color)

    def _render_torus(self, raster, cx, cy, cz, color, time):
        """Render torus"""
        major_radius = min(raster.width, raster.length) * 0.25 * self.size
        minor_radius = major_radius * 0.4
        num_points = int(300 * (1 + self.density))

        for i in range(num_points):
            u = (i / num_points) * 2 * math.pi
            for j in range(0, num_points // 2):
                v = (j / (num_points // 2)) * 2 * math.pi

                x = int(cx + (major_radius + minor_radius * math.cos(v)) * math.cos(u))
                y = int(cy + minor_radius * math.sin(v))
                z = int(cz + (major_radius + minor_radius * math.cos(v)) * math.sin(u))

                if 0 <= x < raster.width and 0 <= y < raster.height and 0 <= z < raster.length:
                    raster.set_pix(x, y, z, color)

    def _render_pyramid(self, raster, cx, cy, cz, color):
        """Render pyramid"""
        base_size = min(raster.width, raster.length) * 0.4 * self.size
        height = raster.height * 0.6 * self.size

        for y in range(int(raster.height)):
            y_ratio = y / raster.height
            current_size = base_size * (1 - y_ratio)

            for x in range(raster.width):
                for z in range(raster.length):
                    dx = abs(x - cx)
                    dz = abs(z - cz)

                    if dx <= current_size and dz <= current_size:
                        edge_dist = min(
                            current_size - dx,
                            current_size - dz
                        )
                        if edge_dist < (1 + self.density * 2):
                            raster.set_pix(x, y, z, color)

    def _render_plane(self, raster, cx, cy, cz, color):
        """Render plane"""
        y_pos = int(cy)
        thickness = max(1, int(1 + self.density * 3))

        for x in range(raster.width):
            for z in range(raster.length):
                for dy in range(-thickness, thickness + 1):
                    y = y_pos + dy
                    if 0 <= y < raster.height:
                        raster.set_pix(x, y, z, color)


class WebParticleFlowScene(Scene):
    """Particle flow scene adapter"""

    def __init__(self, params, global_params, color_state):
        self.pattern = params.get('pattern', 'particles')
        self.density = global_params.get('density', 0.5)
        self.size = global_params.get('size', 1.0)
        self.animation_speed = global_params.get('animationSpeed', 1.0)
        self.color_state = color_state
        self.particles = []
        self._init_particles()

    def _init_particles(self):
        """Initialize particles"""
        num_particles = int(50 * (1 + self.density))
        for i in range(num_particles):
            self.particles.append({
                'phase': i / num_particles * 2 * math.pi,
                'speed': 1.0 + (i % 10) * 0.1
            })

    def render(self, raster: Raster, time: float):
        """Render particles"""
        color = get_color_from_state(self.color_state, time)
        t = time * self.animation_speed

        if self.pattern == 'particles':
            self._render_particles(raster, color, t)
        elif self.pattern == 'spiral':
            self._render_spiral(raster, color, t)
        elif self.pattern == 'tornado':
            self._render_tornado(raster, color, t)
        else:
            self._render_particles(raster, color, t)

    def _render_particles(self, raster, color, t):
        """Render particle cloud"""
        for particle in self.particles:
            phase = particle['phase'] + t * particle['speed']
            x = int(raster.width / 2 + raster.width * 0.3 * math.cos(phase))
            y = int((phase * 5) % raster.height)
            z = int(raster.length / 2 + raster.length * 0.3 * math.sin(phase))

            if 0 <= x < raster.width and 0 <= y < raster.height and 0 <= z < raster.length:
                # Draw particle with size
                particle_size = max(1, int(self.size * 2))
                for dx in range(-particle_size, particle_size + 1):
                    for dy in range(-particle_size, particle_size + 1):
                        for dz in range(-particle_size, particle_size + 1):
                            px, py, pz = x + dx, y + dy, z + dz
                            if 0 <= px < raster.width and 0 <= py < raster.height and 0 <= pz < raster.length:
                                raster.set_pix(px, py, pz, color)

    def _render_spiral(self, raster, color, t):
        """Render spiral pattern"""
        num_points = int(200 * (1 + self.density))
        for i in range(num_points):
            phase = i / num_points * 8 * math.pi + t
            radius = (i / num_points) * min(raster.width, raster.length) * 0.4

            x = int(raster.width / 2 + radius * math.cos(phase))
            y = int(i / num_points * raster.height)
            z = int(raster.length / 2 + radius * math.sin(phase))

            if 0 <= x < raster.width and 0 <= y < raster.height and 0 <= z < raster.length:
                raster.set_pix(x, y, z, color)

    def _render_tornado(self, raster, color, t):
        """Render tornado pattern"""
        for y in range(raster.height):
            y_ratio = y / raster.height
            radius = (raster.width * 0.4) * (1 - y_ratio * 0.7)
            num_points = int(20 * (1 + self.density))

            for i in range(num_points):
                angle = (i / num_points * 2 * math.pi) + t + y * 0.3
                x = int(raster.width / 2 + radius * math.cos(angle))
                z = int(raster.length / 2 + radius * math.sin(angle))

                if 0 <= x < raster.width and 0 <= z < raster.length:
                    raster.set_pix(x, y, z, color)


class WebWaveFieldScene(Scene):
    """Wave field scene adapter"""

    def __init__(self, params, global_params, color_state):
        self.wave_type = params.get('waveType', 'ripple')
        self.frequency = global_params.get('frequency', 1.0)
        self.amplitude = global_params.get('amplitude', 0.5)
        self.color_state = color_state

    def render(self, raster: Raster, time: float):
        """Render wave field"""
        color = get_color_from_state(self.color_state, time)

        if self.wave_type == 'ripple':
            self._render_ripple(raster, color, time)
        elif self.wave_type == 'plane':
            self._render_plane_wave(raster, color, time)
        else:
            self._render_ripple(raster, color, time)

    def _render_ripple(self, raster, color, time):
        """Render ripple waves"""
        cx = raster.width / 2
        cz = raster.length / 2

        for x in range(raster.width):
            for z in range(raster.length):
                dx = x - cx
                dz = z - cz
                dist = math.sqrt(dx * dx + dz * dz)

                wave = math.sin(dist * self.frequency * 0.3 - time * 3)
                y = int(raster.height / 2 + wave * raster.height * 0.3 * self.amplitude)

                if 0 <= y < raster.height:
                    raster.set_pix(x, y, z, color)

    def _render_plane_wave(self, raster, color, time):
        """Render plane wave"""
        for x in range(raster.width):
            for z in range(raster.length):
                wave = math.sin(x * self.frequency * 0.2 - time * 3)
                y = int(raster.height / 2 + wave * raster.height * 0.3 * self.amplitude)

                if 0 <= y < raster.height:
                    raster.set_pix(x, y, z, color)


class WebProceduralScene(Scene):
    """Procedural scene adapter"""

    def __init__(self, params, global_params, color_state):
        self.algorithm = params.get('algorithm', 'perlin')
        self.size = global_params.get('size', 1.0)
        self.amplitude = global_params.get('amplitude', 0.5)
        self.color_state = color_state

    def render(self, raster: Raster, time: float):
        """Render procedural noise"""
        color = get_color_from_state(self.color_state, time)

        # Simple 3D noise-like pattern
        scale = 0.1 / self.size
        threshold = self.amplitude

        for x in range(raster.width):
            for y in range(raster.height):
                for z in range(raster.length):
                    # Simplified perlin-like noise
                    value = (
                        math.sin(x * scale + time) *
                        math.cos(y * scale + time * 0.5) *
                        math.sin(z * scale + time * 0.3)
                    )

                    if value > threshold:
                        raster.set_pix(x, y, z, color)


class WebGridScene(Scene):
    """Grid scene adapter"""

    def __init__(self, params, global_params, color_state):
        self.pattern = params.get('pattern', 'cube')
        self.spacing = global_params.get('spacing', 0.5)
        self.density = global_params.get('density', 0.5)
        self.color_state = color_state

    def render(self, raster: Raster, time: float):
        """Render grid pattern"""
        color = get_color_from_state(self.color_state, time)
        spacing = max(2, int(5 + self.spacing * 10))
        thickness = max(1, int(1 + self.density * 2))

        if self.pattern == 'cube':
            # Grid lines
            for x in range(0, raster.width, spacing):
                for y in range(raster.height):
                    for z in range(raster.length):
                        raster.set_pix(x, y, z, color)

            for y in range(0, raster.height, spacing):
                for x in range(raster.width):
                    for z in range(raster.length):
                        raster.set_pix(x, y, z, color)

            for z in range(0, raster.length, spacing):
                for x in range(raster.width):
                    for y in range(raster.height):
                        raster.set_pix(x, y, z, color)


class WebText3DScene(Scene):
    """Text 3D scene adapter (placeholder)"""

    def __init__(self, params, global_params, color_state):
        self.text = params.get('text', 'HELLO')
        self.style = params.get('style', 'block')
        self.color_state = color_state

    def render(self, raster: Raster, time: float):
        """Render text (simplified)"""
        color = get_color_from_state(self.color_state, time)

        # Simple text rendering - just show a block for now
        cx = raster.width // 2
        cy = raster.height // 2
        cz = raster.length // 2
        size = 5

        for x in range(cx - size, cx + size):
            for y in range(cy - size, cy + size):
                for z in range(cz - size, cz + size):
                    if 0 <= x < raster.width and 0 <= y < raster.height and 0 <= z < raster.length:
                        raster.set_pix(x, y, z, color)


def create_scene_from_state(effect_state, raster, time):
    """Create appropriate scene from effect state"""
    scene_state = effect_state.get('scene', {})
    scene_type = scene_state.get('type', 'shapeMorph')
    scene_params = scene_state.get('params', {})
    global_params = effect_state.get('globalParams', {})
    color_state = effect_state.get('colors', {})

    # Map scene type to scene class
    scene_map = {
        'shapeMorph': WebShapeMorphScene,
        'particleFlow': WebParticleFlowScene,
        'waveField': WebWaveFieldScene,
        'procedural': WebProceduralScene,
        'grid': WebGridScene,
        'text3D': WebText3DScene
    }

    scene_class = scene_map.get(scene_type, WebShapeMorphScene)
    return scene_class(scene_params, global_params, color_state)
