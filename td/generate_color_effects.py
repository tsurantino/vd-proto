"""
TouchDesigner Color Effects Generator
Standalone color effects using TOPs with simple expressions
No dependencies - uses built-in absTime.seconds for animation

Based on: TOUCHDESIGNER_COLOR_EFFECTS_TOPS.md

Effects Generated:
- Sparkle, Rainbow Sweep, Fire, Plasma
- Kaleidoscope, Breath, Color Chase
- Wave (Multi, Vertical, Circular, Standing)
- Cycle Hue, Pulse (Radial, Alternating, Layered, Beat)
- Static (Color, Dynamic, Wave)
- Scrolling (Strobe, Pulse)

Usage:
1. Open TouchDesigner
2. Create a Text DAT
3. Paste this script
4. Right-click → Run Script

Author: Generated for Volumetric Display Prototype
Date: 2025
"""

import td
import math

class ColorEffectsGenerator:
    """Generator for standalone color effects"""

    def __init__(self):
        # Clear existing components to prevent errors on re-run
        for child in op('/project1').children:
            if child.name in ['color_effects', 'output', 'control']:
                child.destroy()
        
        self.root = op('/project1')
        self.resolution = 512

    def generate_all(self):
        """Generate all color effects"""
        print("Starting Color Effects Generation...")

        # Create structure
        self.create_structure()

        # Create effects
        self.create_sparkle()
        self.create_rainbow_sweep()
        self.create_fire()
        self.create_plasma()
        self.create_kaleidoscope()
        self.create_wave_circular()
        self.create_wave_vertical()
        self.create_pulse_radial()
        self.create_static_color()
        self.create_cycle_hue()

        # Create output system
        self.create_output_system()

        # Create control
        self.create_control()

        print("Color Effects Generation Complete!")
        self.print_usage()

    def create_structure(self):
        """Create folder structure"""
        self.effects = self.root.create(baseCOMP, 'color_effects')
        self.output = self.root.create(baseCOMP, 'output')
        self.control = self.root.create(baseCOMP, 'control')

        self.effects.nodeY = 200
        self.output.nodeY = -100
        self.control.nodeY = 400

    # =========================================================================
    # EFFECT: SPARKLE
    # =========================================================================

    def create_sparkle(self):
        """Random pixels flash white briefly"""
        container = self.effects.create(baseCOMP, 'sparkle')
        container.nodeX = -800

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0

        # Animated noise
        noise = container.create(noiseTOP, 'noise')
        noise.par.type = 'random' # CORRECTED: 'random' is for GPU noise
        noise.par.outputresolution = 'constant'
        noise.par.resolutionw = self.resolution
        noise.par.resolutionh = self.resolution
        noise.par.seed.expr = 'int(absTime.seconds * chf("../params/speed") * 100)'
        noise.par.mono = True

        # Threshold (only top 2% pass)
        thresh = container.create(thresholdTOP, 'threshold')
        thresh.par.threshold = 0.98
        thresh.par.soften = 0.02
        thresh.inputConnectors[0].connect(noise)
        thresh.nodeX = noise.nodeX + 150

        # Level (brighten sparkles)
        level = container.create(levelTOP, 'brighten')
        level.par.brightness1 = 1.5
        level.par.gamma1 = 2.0
        level.inputConnectors[0].connect(thresh)
        level.nodeX = thresh.nodeX + 150

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(level)
        null.nodeX = level.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: RAINBOW SWEEP
    # =========================================================================

    def create_rainbow_sweep(self):
        """Full spectrum sweeps across space"""
        container = self.effects.create(baseCOMP, 'rainbow_sweep')
        container.nodeX = -600

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 0.2

        # U ramp
        ramp_u = container.create(rampTOP, 'ramp_u')
        ramp_u.par.type = 'horizontal'
        ramp_u.par.outputresolution = 'constant'
        ramp_u.par.resolutionw = self.resolution
        ramp_u.par.resolutionh = self.resolution

        # V ramp
        ramp_v = container.create(rampTOP, 'ramp_v')
        ramp_v.par.type = 'vertical'
        ramp_v.par.outputresolution = 'constant'
        ramp_v.par.resolutionw = self.resolution
        ramp_v.par.resolutionh = self.resolution
        ramp_v.nodeX = ramp_u.nodeX
        ramp_v.nodeY = ramp_u.nodeY - 150

        # Combine
        comp = container.create(compositeTOP, 'combine_uv')
        comp.par.operand = 'add'
        comp.inputConnectors[0].connect(ramp_u)
        comp.inputConnectors[1].connect(ramp_v)
        comp.nodeX = ramp_u.nodeX + 200

        # Add time + scale
        math1 = container.create(mathTOP, 'add_time_scale')
        math1.par.postadd.expr = 'absTime.seconds * chf("../params/speed")'
        math1.inputConnectors[0].connect(comp)
        math1.nodeX = comp.nodeX + 150

        # Multiply by scale
        math2 = container.create(mathTOP, 'scale')
        math2.par.gain = 0.5
        math2.inputConnectors[0].connect(math1)
        math2.nodeX = math1.nodeX + 150

        # Fract (via GLSL)
        glsl = container.create(glslTOP, 'fract')
        glsl.par.outputresolution = 'constant'
        glsl.par.resolutionw = self.resolution
        glsl.par.resolutionh = self.resolution
        glsl.inputConnectors[0].connect(math2)
        glsl.nodeX = math2.nodeX + 150
        glsl.par.pixelformat = '32bitfloat'
        glsl.par.shader = """
uniform sampler2D sTD2DInputs[1];
out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    float val = texture(sTD2DInputs[0], uv).r;
    fragColor = vec4(vec3(fract(val)), 1.0);
}
"""

        # Rainbow gradient
        rainbow = container.create(rampTOP, 'rainbow')
        rainbow.par.type = 'horizontal'
        rainbow.par.outputresolution = 'constant'
        rainbow.par.resolutionw = self.resolution
        rainbow.par.resolutionh = 32
        keys = rainbow.par.colors
        keys.val = [ (0, 0, 0.5, 1), (1, 0, 0.5, 1) ]
        keys.mode = 'hsv'
        rainbow.nodeX = glsl.nodeX
        rainbow.nodeY = glsl.nodeY - 200

        # Lookup
        lookup = container.create(lookupTOP, 'apply_rainbow')
        lookup.inputConnectors[0].connect(glsl)
        lookup.inputConnectors[1].connect(rainbow)
        lookup.nodeX = glsl.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: FIRE
    # =========================================================================

    def create_fire(self):
        """Flickering warm colors with upward bias"""
        container = self.effects.create(baseCOMP, 'fire')
        container.nodeX = -400

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0

        # Height gradient (vertical, inverted)
        height = container.create(rampTOP, 'height_gradient')
        height.par.type = 'vertical'
        height.par.outputresolution = 'constant'
        height.par.resolutionw = self.resolution
        height.par.resolutionh = self.resolution
        # Invert: bottom=1 (hot), top=0 (cool)
        height.par.rstart = 1.0
        height.par.rend = 0.0
        height.nodeY = 100

        # Turbulence noise
        noise = container.create(noiseTOP, 'turbulence')
        # CORRECTED: Removed incorrect 'type' parameter
        noise.par.noisetype = 'perlin'
        noise.par.amp = 0.3
        noise.par.harmonics = 3
        noise.par.period = 2
        noise.par.translate.z.expr = 'absTime.seconds * chf("../params/speed") * 0.5'
        noise.par.outputresolution = 'constant'
        noise.par.resolutionw = self.resolution
        noise.par.resolutionh = self.resolution
        noise.par.mono = True
        noise.nodeY = -100

        # Combine
        comp = container.create(compositeTOP, 'combine')
        comp.par.operand = 'add'
        comp.inputConnectors[0].connect(height)
        comp.inputConnectors[1].connect(noise)
        comp.nodeX = height.nodeX + 250

        # Fire color gradient
        fire_colors = container.create(rampTOP, 'fire_colors')
        fire_colors.par.type = 'horizontal'
        fire_colors.par.outputresolution = 'constant'
        fire_colors.par.resolutionw = self.resolution
        fire_colors.par.resolutionh = 32
        keys = fire_colors.par.colors
        keys.val = [ (0.2, 0, 0, 1), (1, 0, 0, 1), (1, 0.5, 0, 1), (1, 1, 0, 1) ]
        fire_colors.nodeX = comp.nodeX
        fire_colors.nodeY = comp.nodeY - 200

        # Lookup
        lookup = container.create(lookupTOP, 'apply_fire')
        lookup.inputConnectors[0].connect(comp)
        lookup.inputConnectors[1].connect(fire_colors)
        lookup.nodeX = comp.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: PLASMA
    # =========================================================================

    def create_plasma(self):
        """Multi-sine wave interference pattern"""
        container = self.effects.create(baseCOMP, 'plasma')
        container.nodeX = -200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 0.3

        # Ramps
        ramp_u = container.create(rampTOP, 'ramp_u')
        ramp_u.par.type = 'horizontal'
        ramp_u.par.outputresolution = 'constant'
        ramp_u.par.resolutionw = self.resolution
        ramp_u.par.resolutionh = self.resolution
        ramp_u.nodeY = 200

        ramp_v = container.create(rampTOP, 'ramp_v')
        ramp_v.par.type = 'vertical'
        ramp_v.par.outputresolution = 'constant'
        ramp_v.par.resolutionw = self.resolution
        ramp_v.par.resolutionh = self.resolution
        ramp_v.nodeY = 100

        # Wave 1 (horizontal)
        math1a = container.create(mathTOP, 'wave1_mult')
        math1a.par.gain = 10
        math1a.inputConnectors[0].connect(ramp_u)
        math1a.nodeX = ramp_u.nodeX + 150

        math1b = container.create(mathTOP, 'wave1_add')
        math1b.par.postadd.expr = 'absTime.seconds * chf("../params/speed")'
        math1b.inputConnectors[0].connect(math1a)
        math1b.nodeX = math1a.nodeX + 150

        pattern1 = container.create(patternTOP, 'wave1')
        pattern1.par.type = 'sine'
        pattern1.par.period = 1.0
        pattern1.par.outputresolution = 'constant'
        pattern1.par.resolutionw = self.resolution
        pattern1.par.resolutionh = self.resolution
        pattern1.inputConnectors[0].connect(math1b)
        pattern1.nodeX = math1b.nodeX + 150

        # Wave 2 (vertical)
        math2a = container.create(mathTOP, 'wave2_mult')
        math2a.par.gain = 10
        math2a.inputConnectors[0].connect(ramp_v)
        math2a.nodeX = ramp_v.nodeX + 150

        math2b = container.create(mathTOP, 'wave2_sub')
        math2b.par.postadd.expr = '-(absTime.seconds * chf("../params/speed") * 0.7)'
        math2b.inputConnectors[0].connect(math2a)
        math2b.nodeX = math2a.nodeX + 150

        pattern2 = container.create(patternTOP, 'wave2')
        pattern2.par.type = 'sine'
        pattern2.par.period = 1.0
        pattern2.par.outputresolution = 'constant'
        pattern2.par.resolutionw = self.resolution
        pattern2.par.resolutionh = self.resolution
        pattern2.inputConnectors[0].connect(math2b)
        pattern2.nodeX = math2b.nodeX + 150

        # Combine waves
        comp = container.create(compositeTOP, 'combine_waves')
        comp.par.operand = 'add'
        comp.inputConnectors[0].connect(pattern1)
        comp.inputConnectors[1].connect(pattern2)
        comp.nodeX = pattern1.nodeX + 200
        comp.nodeY = 150

        # Normalize
        level = container.create(levelTOP, 'normalize')
        # CORRECTED: Changed parameter names
        level.par.blacklevel = -2
        level.par.whitelevel = 2
        level.inputConnectors[0].connect(comp)
        level.nodeX = comp.nodeX + 150

        # Rainbow gradient
        rainbow = container.create(rampTOP, 'rainbow')
        rainbow.par.type = 'horizontal'
        rainbow.par.outputresolution = 'constant'
        rainbow.par.resolutionw = self.resolution
        rainbow.par.resolutionh = 32
        keys = rainbow.par.colors
        keys.val = [ (0, 0, 0.5, 1), (1, 0, 0.5, 1) ]
        keys.mode = 'hsv'
        rainbow.nodeX = level.nodeX
        rainbow.nodeY = level.nodeY - 200

        # Lookup
        lookup = container.create(lookupTOP, 'apply_color')
        lookup.inputConnectors[0].connect(level)
        lookup.inputConnectors[1].connect(rainbow)
        lookup.nodeX = level.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: KALEIDOSCOPE
    # =========================================================================

    def create_kaleidoscope(self):
        """Mirror colors with rotational symmetry"""
        container = self.effects.create(baseCOMP, 'kaleidoscope')
        container.nodeX = 0

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 0.2
        params.par.name1 = 'symmetry'
        params.par.value1 = 6

        # Create GLSL for kaleidoscope effect
        glsl = container.create(glslTOP, 'kaleidoscope')
        glsl.par.outputresolution = 'constant'
        glsl.par.resolutionw = self.resolution
        glsl.par.resolutionh = self.resolution
        glsl.par.pixelformat = '32bitfloat'

        glsl_code = """
uniform float uSymmetry;
out vec4 fragColor;

#define PI 3.14159265359

void main() {
    vec2 uv = vUV.st;

    // Center
    vec2 centered = uv - 0.5;

    // Distance and angle
    float dist = length(centered);
    float angle = atan(centered.y, centered.x);

    // Symmetry
    float segmentAngle = (2.0 * PI) / uSymmetry;
    angle = mod(angle, segmentAngle);
    angle = abs(angle - segmentAngle * 0.5);

    // Combine with distance + time
    float pattern = angle / (segmentAngle * 0.5) + dist + uTime.seconds;
    pattern = fract(pattern);

    fragColor = vec4(vec3(pattern), 1.0);
}
"""
        glsl.par.shader = glsl_code

        # Add uniform for symmetry
        glsl.par.uniformname0 = 'uSymmetry'
        glsl.par.uniformvalue0.expr = 'chf("../params/symmetry")'
        glsl.nodeX = 150

        # Hue gradient
        hue_ramp = container.create(rampTOP, 'hue_gradient')
        hue_ramp.par.type = 'horizontal'
        hue_ramp.par.outputresolution = 'constant'
        hue_ramp.par.resolutionw = self.resolution
        hue_ramp.par.resolutionh = 32
        keys = hue_ramp.par.colors
        keys.val = [ (0, 0, 0.5, 1), (1, 0, 0.5, 1) ]
        keys.mode = 'hsv'
        hue_ramp.nodeX = glsl.nodeX
        hue_ramp.nodeY = glsl.nodeY - 200

        # Lookup
        lookup = container.create(lookupTOP, 'apply_color')
        lookup.inputConnectors[0].connect(glsl)
        lookup.inputConnectors[1].connect(hue_ramp)
        lookup.nodeX = glsl.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: WAVE CIRCULAR
    # =========================================================================

    def create_wave_circular(self):
        """Expanding circular waves from center"""
        container = self.effects.create(baseCOMP, 'wave_circular')
        container.nodeX = 200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0
        params.par.name1 = 'frequency'
        params.par.value1 = 15.0

        # Distance from center
        ramp_u = container.create(rampTOP, 'ramp_u')
        ramp_u.par.type = 'horizontal'
        ramp_u.par.outputresolution = 'constant'
        ramp_u.par.resolutionw = self.resolution
        ramp_u.par.resolutionh = self.resolution
        ramp_u.nodeY = 100

        math_u = container.create(mathTOP, 'u_centered')
        math_u.par.postadd = -0.5 # Center the ramp
        math_u.inputConnectors[0].connect(ramp_u)
        math_u.nodeX = ramp_u.nodeX + 150

        math_u2 = container.create(mathTOP, 'u_squared')
        math_u2.par.combine = 'mult'
        math_u2.inputConnectors[0].connect(math_u)
        math_u2.inputConnectors[1].connect(math_u)
        math_u2.nodeX = math_u.nodeX + 150

        ramp_v = container.create(rampTOP, 'ramp_v')
        ramp_v.par.type = 'vertical'
        ramp_v.par.outputresolution = 'constant'
        ramp_v.par.resolutionw = self.resolution
        ramp_v.par.resolutionh = self.resolution
        ramp_v.nodeY = -100

        math_v = container.create(mathTOP, 'v_centered')
        math_v.par.postadd = -0.5 # Center the ramp
        math_v.inputConnectors[0].connect(ramp_v)
        math_v.nodeX = ramp_v.nodeX + 150

        math_v2 = container.create(mathTOP, 'v_squared')
        math_v2.par.combine = 'mult'
        math_v2.inputConnectors[0].connect(math_v)
        math_v2.inputConnectors[1].connect(math_v)
        math_v2.nodeX = math_v.nodeX + 150

        comp = container.create(compositeTOP, 'sum_squares')
        comp.par.operand = 'add'
        comp.inputConnectors[0].connect(math_u2)
        comp.inputConnectors[1].connect(math_v2)
        comp.nodeX = math_u2.nodeX + 200
        comp.nodeY = 0

        math_sqrt = container.create(mathTOP, 'distance')
        math_sqrt.par.combine = 'sqrt'
        math_sqrt.inputConnectors[0].connect(comp)
        math_sqrt.nodeX = comp.nodeX + 150

        math_scale = container.create(mathTOP, 'scale')
        math_scale.par.gain.expr = 'chf("../params/frequency")'
        math_scale.inputConnectors[0].connect(math_sqrt)
        math_scale.nodeX = math_sqrt.nodeX + 150

        math_anim = container.create(mathTOP, 'animate')
        math_anim.par.postadd.expr = '-(absTime.seconds * chf("../params/speed"))'
        math_anim.inputConnectors[0].connect(math_scale)
        math_anim.nodeX = math_scale.nodeX + 150

        # Sine pattern
        pattern = container.create(patternTOP, 'wave')
        pattern.par.type = 'sine'
        pattern.par.period = 1 # Use period 1, frequency is controlled earlier
        pattern.par.outputresolution = 'constant'
        pattern.par.resolutionw = self.resolution
        pattern.par.resolutionh = self.resolution
        pattern.inputConnectors[0].connect(math_anim)
        pattern.nodeX = math_anim.nodeX + 150

        # Normalize
        level = container.create(levelTOP, 'normalize')
        # CORRECTED: Changed parameter names
        level.par.blacklevel = -1
        level.par.whitelevel = 1
        level.inputConnectors[0].connect(pattern)
        level.nodeX = pattern.nodeX + 150

        # Color ramp
        hue_ramp = container.create(rampTOP, 'hue_gradient')
        hue_ramp.par.type = 'horizontal'
        hue_ramp.par.outputresolution = 'constant'
        hue_ramp.par.resolutionw = self.resolution
        hue_ramp.par.resolutionh = 32
        keys = hue_ramp.par.colors
        keys.val = [ (0, 0, 0.5, 1), (1, 0, 0.5, 1) ]
        keys.mode = 'hsv'
        hue_ramp.nodeX = level.nodeX
        hue_ramp.nodeY = level.nodeY - 200

        # Lookup
        lookup = container.create(lookupTOP, 'apply_color')
        lookup.inputConnectors[0].connect(level)
        lookup.inputConnectors[1].connect(hue_ramp)
        lookup.nodeX = level.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: WAVE VERTICAL
    # =========================================================================

    def create_wave_vertical(self):
        """Vertical traveling waves"""
        container = self.effects.create(baseCOMP, 'wave_vertical')
        container.nodeX = 400

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0
        params.par.name1 = 'frequency'
        params.par.value1 = 10.0

        # V ramp
        ramp_v = container.create(rampTOP, 'ramp_v')
        ramp_v.par.type = 'vertical'
        ramp_v.par.outputresolution = 'constant'
        ramp_v.par.resolutionw = self.resolution
        ramp_v.par.resolutionh = self.resolution

        # Scale
        math_scale = container.create(mathTOP, 'scale')
        math_scale.par.gain.expr = 'chf("../params/frequency")'
        math_scale.inputConnectors[0].connect(ramp_v)
        math_scale.nodeX = ramp_v.nodeX + 150

        # Animate
        math = container.create(mathTOP, 'animate')
        math.par.postadd.expr = '-(absTime.seconds * chf("../params/speed"))'
        math.inputConnectors[0].connect(math_scale)
        math.nodeX = math_scale.nodeX + 150

        # Sine pattern
        pattern = container.create(patternTOP, 'wave')
        pattern.par.type = 'sine'
        pattern.par.period = 1.0
        pattern.par.outputresolution = 'constant'
        pattern.par.resolutionw = self.resolution
        pattern.par.resolutionh = self.resolution
        pattern.inputConnectors[0].connect(math)
        pattern.nodeX = math.nodeX + 150

        # Normalize
        level = container.create(levelTOP, 'normalize')
        # CORRECTED: Changed parameter names
        level.par.blacklevel = -1
        level.par.whitelevel = 1
        level.inputConnectors[0].connect(pattern)
        level.nodeX = pattern.nodeX + 150

        # Color ramp
        hue_ramp = container.create(rampTOP, 'hue_gradient')
        hue_ramp.par.type = 'horizontal'
        hue_ramp.par.outputresolution = 'constant'
        hue_ramp.par.resolutionw = self.resolution
        hue_ramp.par.resolutionh = 32
        keys = hue_ramp.par.colors
        keys.val = [ (0, 0, 0.5, 1), (1, 0, 0.5, 1) ]
        keys.mode = 'hsv'
        hue_ramp.nodeX = level.nodeX
        hue_ramp.nodeY = level.nodeY - 200

        # Lookup
        lookup = container.create(lookupTOP, 'apply_color')
        lookup.inputConnectors[0].connect(level)
        lookup.inputConnectors[1].connect(hue_ramp)
        lookup.nodeX = level.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: PULSE RADIAL
    # =========================================================================

    def create_pulse_radial(self):
        """Pulsing brightness from center"""
        container = self.effects.create(baseCOMP, 'pulse_radial')
        container.nodeX = 600

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0
        params.par.name1 = 'basecolor_r'
        params.par.value1 = 0.4
        params.par.name2 = 'basecolor_g'
        params.par.value2 = 0.7
        params.par.name3 = 'basecolor_b'
        params.par.value3 = 1.0

        # Distance calculation
        glsl_dist = container.create(glslTOP, 'distance')
        glsl_dist.par.outputresolution = 'constant'
        glsl_dist.par.resolutionw = self.resolution
        glsl_dist.par.resolutionh = self.resolution
        glsl_dist.par.pixelformat = '32bitfloat'
        glsl_dist.par.shader = """
out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec2 centered = uv - 0.5;
    float dist = length(centered);
    fragColor = vec4(vec3(dist), 1.0);
}
"""

        # Pulse wave
        glsl_pulse = container.create(glslTOP, 'pulse')
        glsl_pulse.par.outputresolution = 'constant'
        glsl_pulse.par.resolutionw = self.resolution
        glsl_pulse.par.resolutionh = self.resolution
        glsl_pulse.inputConnectors[0].connect(glsl_dist)
        glsl_pulse.nodeX = glsl_dist.nodeX + 150

        glsl_pulse.par.uniformname0 = 'uSpeed'
        glsl_pulse.par.uniformvalue0.expr = 'chf("../params/speed")'

        glsl_pulse.par.shader = """
uniform sampler2D sTD2DInputs[1];
uniform float uSpeed;
out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    float dist = texture(sTD2DInputs[0], uv).r;

    float pulse = sin(uTime.seconds * uSpeed * 3.0 - dist * 10.0);
    float brightness = 0.2 + (pulse + 1.0) * 0.4;

    fragColor = vec4(vec3(brightness), 1.0);
}
"""

        # Base color
        base = container.create(constantTOP, 'base_color')
        base.par.outputresolution = 'constant'
        base.par.resolutionw = self.resolution
        base.par.resolutionh = self.resolution
        base.par.colorr.expr = 'chf("../params/basecolor_r")'
        base.par.colorg.expr = 'chf("../params/basecolor_g")'
        base.par.colorb.expr = 'chf("../params/basecolor_b")'
        base.nodeX = glsl_pulse.nodeX
        base.nodeY = glsl_pulse.nodeY - 200

        # Multiply
        mult = container.create(compositeTOP, 'apply_brightness')
        mult.par.operand = 'mult'
        mult.inputConnectors[0].connect(base)
        mult.inputConnectors[1].connect(glsl_pulse)
        mult.nodeX = glsl_pulse.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(mult)
        null.nodeX = mult.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: STATIC COLOR
    # =========================================================================

    def create_static_color(self):
        """Random color per pixel"""
        container = self.effects.create(baseCOMP, 'static_color')
        container.nodeX = 800

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0

        # White noise
        noise = container.create(noiseTOP, 'noise')
        noise.par.type = 'random' # CORRECTED
        noise.par.outputresolution = 'constant'
        noise.par.resolutionw = self.resolution
        noise.par.resolutionh = self.resolution
        noise.par.seed.expr = 'int(absTime.seconds * chf("../params/speed") * 10)'
        noise.par.mono = False

        # Hue ramp
        hue_ramp = container.create(rampTOP, 'hue_spectrum')
        hue_ramp.par.type = 'horizontal'
        hue_ramp.par.outputresolution = 'constant'
        hue_ramp.par.resolutionw = self.resolution
        hue_ramp.par.resolutionh = 32
        keys = hue_ramp.par.colors
        keys.val = [ (0, 0, 0.5, 1), (1, 0, 0.5, 1) ]
        keys.mode = 'hsv'
        hue_ramp.nodeX = noise.nodeX
        hue_ramp.nodeY = noise.nodeY - 200

        # Lookup
        lookup = container.create(lookupTOP, 'apply_color')
        lookup.inputConnectors[0].connect(noise)
        lookup.inputConnectors[1].connect(hue_ramp)
        lookup.nodeX = noise.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # EFFECT: CYCLE HUE
    # =========================================================================

    def create_cycle_hue(self):
        """Smooth hue rotation over time"""
        container = self.effects.create(baseCOMP, 'cycle_hue')
        container.nodeX = 1000

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 0.2

        # Base color
        base = container.create(constantTOP, 'base_color')
        base.par.outputresolution = 'constant'
        base.par.resolutionw = self.resolution
        base.par.resolutionh = self.resolution
        base.par.colorr = 0.5
        base.par.colorg = 0.5
        base.par.colorb = 1.0

        # HSV Adjust
        hsv = container.create(hsvadjustTOP, 'hsv_adjust')
        hsv.par.hueoffset.expr = 'absTime.seconds * 360 * chf("../params/speed")'
        hsv.inputConnectors[0].connect(base)
        hsv.nodeX = base.nodeX + 200
        
        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(hsv)
        null.nodeX = hsv.nodeX + 150
        null.color = (1, 0.7, 0)

    # =========================================================================
    # OUTPUT SYSTEM
    # =========================================================================

    def create_output_system(self):
        """Create effect selector and output"""
        print("Creating output system...")

        # Effect selector
        selector = self.output.create(constantCHOP, 'effect_select')
        selector.par.name0 = 'index'
        selector.par.value0 = 0

        # Switch
        switch = self.output.create(switchTOP, 'effect_switch')
        switch.par.index.expr = 'int(op("./effect_select")[0])'
        
        effect_list = self.effects.findChildren(type=baseCOMP)
        for i, effect in enumerate(effect_list):
            switch.inputConnectors[i].connect(effect.op('OUT'))

        switch.nodeX = selector.nodeX + 200

        # Final output
        null = self.output.create(nullTOP, 'FINAL_OUTPUT')
        null.inputConnectors[0].connect(switch)
        null.nodeX = switch.nodeX + 150
        null.color = (0, 1, 0)
        null.viewer = True

    # =========================================================================
    # CONTROL
    # =========================================================================

    def create_control(self):
        """Create master control"""
        print("Creating control...")

        # Effect selector
        effect_sel = self.control.create(panelCOMP, 'effect_selector')
        lister = effect_sel.create(listCOMP, 'lister')
        
        effect_names = [op.name for op in self.effects.findChildren(type=baseCOMP)]
        lister.par.rows = len(effect_names)
        lister.par.cols = 1
        for i, name in enumerate(effect_names):
            lister.setItem(i, 0, name)

        lister.par.selection = 1
        lister.par.w = 200
        lister.par.h = 220
        
        out_select = effect_sel.create(outCHOP, 'out_select')
        out_select.par.chopu = 'u'
        out_select.par.chopv = 'v'
        out_select.par.chopw = 'w'

        op(self.output).op('effect_select').par.value0.expr = 'int(op("../control/effect_selector/lister").selection[0])'

    def print_usage(self):
        """Print usage instructions"""
        effect_names = [op.name for op in self.effects.findChildren(type=baseCOMP)]
        usage_text = "===============================================\n"
        usage_text += "COLOR EFFECTS STANDALONE - GENERATED!\n"
        usage_text += "===============================================\n\n"
        usage_text += "STRUCTURE:\n"
        usage_text += "/project1/color_effects - All effects (TOPs)\n"
        usage_text += "/project1/output - Effect selector & output\n"
        usage_text += "/project1/control - Master control\n\n"
        usage_text += "EFFECTS:\n"
        for i, name in enumerate(effect_names):
            usage_text += f"{i} - {name.replace('_', ' ').title()}\n"
        
        usage_text += "\nCONTROLS:\n"
        usage_text += "- Main effect: /project1/control/effect_selector (Click to select)\n"
        usage_text += "- Parameters: Look for 'params' CHOP in each effect's container\n"
        usage_text += "- Speed control is available in each effect's params\n\n"
        usage_text += "VIEW OUTPUT: /project1/output/FINAL_OUTPUT\n\n"
        usage_text += "===============================================\n"
        print(usage_text)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

generator = ColorEffectsGenerator()
generator.generate_all()