"""
TouchDesigner Volumetric Display Illusions Generator
Generates complete network with utilities, illusions, and color effects
All parameters controlled via CHOP constants for modularity

Usage:
1. Open a fresh TouchDesigner project
2. Create a Text DAT
3. Paste this script into the Text DAT
4. Right-click the Text DAT and select "Run Script"

Author: Generated for Volumetric Display Prototype
Date: 2025
"""

import td

class VolumetricIllusionsGenerator:
    """Main generator class for volumetric display illusions"""

    def __init__(self):
        self.root = op('/project1')
        self.grid_x = 30
        self.grid_y = 50
        self.grid_z = 30

    def generate_all(self):
        """Generate complete network"""
        print("Starting Volumetric Illusions Network Generation...")

        # Clear existing (optional - be careful!)
        # self.clear_project()

        # Create main containers
        self.create_main_structure()

        # Create utilities
        self.create_utilities()

        # Create voxel grid base
        self.create_voxel_grid()

        # Create illusions
        self.create_illusions()

        # Create color effects (TOPs)
        self.create_color_effects()

        # Create output/render system
        self.create_output_system()

        # Create master control
        self.create_master_control()

        print("Generation Complete!")
        self.print_usage_instructions()

    def clear_project(self):
        """Clear all children of project1 (use with caution!)"""
        for child in self.root.children:
            if child.name not in ['perform', 'local']:
                child.destroy()

    def create_main_structure(self):
        """Create main folder structure"""
        print("Creating main structure...")

        # Main containers
        self.utilities = self.root.create(baseCOMP, 'utilities')
        self.illusions = self.root.create(baseCOMP, 'illusions')
        self.color_effects = self.root.create(baseCOMP, 'color_effects')
        self.output = self.root.create(baseCOMP, 'output')
        self.control = self.root.create(baseCOMP, 'control')

        # Layout
        self.utilities.nodeY = 500
        self.illusions.nodeY = 300
        self.color_effects.nodeY = 100
        self.output.nodeY = -100
        self.control.nodeY = 700

    def create_utilities(self):
        """Create utility components"""
        print("Creating utilities...")

        # Time control
        self.create_time_control()

        # Distance calculator
        self.create_distance_calculator()

        # Angle calculator
        self.create_angle_calculator()

    def create_time_control(self):
        """Create time control CHOP system"""
        container = self.utilities.create(baseCOMP, 'time_control')
        container.nodeX = -400

        # Timer CHOP
        timer = container.create(timerCHOP, 'timer')
        timer.par.initialize = True
        timer.par.play = True
        timer.par.length = 10000
        timer.par.start = 0

        # Speed constant
        speed_const = container.create(constantCHOP, 'speed')
        speed_const.par.name0 = 'speed'
        speed_const.par.value0 = 1.0
        speed_const.nodeX = timer.nodeX
        speed_const.nodeY = timer.nodeY - 100

        # Select and scale the seconds channel
        select = container.create(selectCHOP, 'select_seconds')
        select.par.channames = 'seconds'
        select.inputConnectors[0].connect(timer)
        select.nodeX = timer.nodeX + 150
        select.nodeY = timer.nodeY

        # Expression CHOP to multiply by speed
        expr = container.create(expressionCHOP, 'time_scaled')
        expr.par.expr0.expr = 'me.inputChan(0) * op("../speed")[0]'
        expr.par.outputname0 = 'seconds'
        expr.inputConnectors[0].connect(select)
        expr.nodeX = select.nodeX + 200
        expr.nodeY = select.nodeY

        # Output null
        null = container.create(nullCHOP, 'TIME_OUT')
        null.inputConnectors[0].connect(expr)
        null.nodeX = expr.nodeX + 150
        null.color = (0.5, 1, 0.5)

        # Info DAT
        info = container.create(textDAT, 'info')
        info.text = """TIME CONTROL UTILITY

Usage: chop('../../utilities/time_control/TIME_OUT')[0]
Output: Scaled time value

Parameters:
- speed: Animation speed multiplier (in speed CHOP)
"""
        info.nodeX = null.nodeX + 200

    def create_distance_calculator(self):
        """Create distance from center calculator (TOP-based for voxel grid)"""
        container = self.utilities.create(baseCOMP, 'distance_calc')
        container.nodeX = -200

        # Resolution constant
        res = container.create(constantCHOP, 'resolution')
        res.par.name0 = 'resx'
        res.par.value0 = 512
        res.par.name1 = 'resy'
        res.par.value1 = 512

        # U ramp
        ramp_u = container.create(rampTOP, 'ramp_u')
        ramp_u.par.orient = 'horizontal'
        ramp_u.par.type = 'linear'
        ramp_u.par.outputresolution = 'constant'
        ramp_u.par.resolutionw = 512
        ramp_u.par.resolutionh = 512
        ramp_u.nodeY = 100

        # Center U
        math_u = container.create(mathTOP, 'u_centered')
        math_u.par.srcapreop = 'sub'
        math_u.par.suba = 0.5
        math_u.inputConnectors[0].connect(ramp_u)
        math_u.nodeX = ramp_u.nodeX + 150
        math_u.nodeY = ramp_u.nodeY

        # Square U
        math_u2 = container.create(mathTOP, 'u_squared')
        math_u2.par.combine = 'mult'
        math_u2.par.srcbpreop = 'srcb'
        math_u2.inputConnectors[0].connect(math_u)
        math_u2.inputConnectors[1].connect(math_u)
        math_u2.nodeX = math_u.nodeX + 150
        math_u2.nodeY = math_u.nodeY

        # V ramp
        ramp_v = container.create(rampTOP, 'ramp_v')
        ramp_v.par.orient = 'vertical'
        ramp_v.par.type = 'linear'
        ramp_v.par.outputresolution = 'constant'
        ramp_v.par.resolutionw = 512
        ramp_v.par.resolutionh = 512
        ramp_v.nodeY = -100

        # Center V
        math_v = container.create(mathTOP, 'v_centered')
        math_v.par.srcapreop = 'sub'
        math_v.par.suba = 0.5
        math_v.inputConnectors[0].connect(ramp_v)
        math_v.nodeX = ramp_v.nodeX + 150
        math_v.nodeY = ramp_v.nodeY

        # Square V
        math_v2 = container.create(mathTOP, 'v_squared')
        math_v2.par.combine = 'mult'
        math_v2.par.srcbpreop = 'srcb'
        math_v2.inputConnectors[0].connect(math_v)
        math_v2.inputConnectors[1].connect(math_v)
        math_v2.nodeX = math_v.nodeX + 150
        math_v2.nodeY = math_v.nodeY

        # Composite (add)
        comp = container.create(compositeTOP, 'sum_squares')
        comp.par.operation = 'add'
        comp.inputConnectors[0].connect(math_u2)
        comp.inputConnectors[1].connect(math_v2)
        comp.nodeX = math_u2.nodeX + 200
        comp.nodeY = 0

        # Sqrt
        math_sqrt = container.create(mathTOP, 'distance')
        math_sqrt.par.srcapreop = 'sqrt'
        math_sqrt.inputConnectors[0].connect(comp)
        math_sqrt.nodeX = comp.nodeX + 150

        # Output null
        null = container.create(nullTOP, 'DISTANCE_OUT')
        null.inputConnectors[0].connect(math_sqrt)
        null.nodeX = math_sqrt.nodeX + 150
        null.color = (0.5, 1, 0.5)

    def create_angle_calculator(self):
        """Create angle from center calculator (TOP-based)"""
        container = self.utilities.create(baseCOMP, 'angle_calc')
        container.nodeX = 0

        # U ramp (centered)
        ramp_u = container.create(rampTOP, 'ramp_u')
        ramp_u.par.orient = 'horizontal'
        ramp_u.par.outputresolution = 'constant'
        ramp_u.par.resolutionw = 512
        ramp_u.par.resolutionh = 512
        ramp_u.nodeY = 100

        math_u = container.create(mathTOP, 'u_centered')
        math_u.par.srcapreop = 'sub'
        math_u.par.suba = 0.5
        math_u.inputConnectors[0].connect(ramp_u)
        math_u.nodeX = ramp_u.nodeX + 150
        math_u.nodeY = ramp_u.nodeY

        # V ramp (centered)
        ramp_v = container.create(rampTOP, 'ramp_v')
        ramp_v.par.orient = 'vertical'
        ramp_v.par.outputresolution = 'constant'
        ramp_v.par.resolutionw = 512
        ramp_v.par.resolutionh = 512
        ramp_v.nodeY = -100

        math_v = container.create(mathTOP, 'v_centered')
        math_v.par.srcapreop = 'sub'
        math_v.par.suba = 0.5
        math_v.inputConnectors[0].connect(ramp_v)
        math_v.nodeX = ramp_v.nodeX + 150
        math_v.nodeY = ramp_v.nodeY

        # GLSL for atan2
        glsl = container.create(glslTOP, 'atan2')
        glsl.par.outputresolution = 'constant'
        glsl.par.resolutionw = 512
        glsl.par.resolutionh = 512
        glsl.inputConnectors[0].connect(math_u)
        glsl.inputConnectors[1].connect(math_v)
        glsl.nodeX = math_u.nodeX + 200
        glsl.nodeY = 0

        # Set GLSL shader
        glsl_code = """
uniform sampler2D sTD2DInputs[2];
out vec4 fragColor;
void main()
{
    vec2 uv = gl_FragCoord.xy / uTD2DInfos[0].res.zw;
    float u = texture(sTD2DInputs[0], uv).r;
    float v = texture(sTD2DInputs[1], uv).r;
    float angle = atan(v, u);
    // Normalize to 0-1
    angle = (angle + 3.14159265) / (2.0 * 3.14159265);
    fragColor = vec4(angle, angle, angle, 1.0);
}
"""
        glsl.par.shader = glsl_code

        # Output null
        null = container.create(nullTOP, 'ANGLE_OUT')
        null.inputConnectors[0].connect(glsl)
        null.nodeX = glsl.nodeX + 150
        null.color = (0.5, 1, 0.5)

    def create_voxel_grid(self):
        """Create base voxel grid generator (SOP)"""
        container = self.utilities.create(baseCOMP, 'voxel_grid')
        container.nodeX = 200

        print("Creating voxel grid base...")

        # Grid parameters CHOP
        params = container.create(constantCHOP, 'grid_params')
        params.par.name0 = 'gridx'
        params.par.value0 = self.grid_x
        params.par.name1 = 'gridy'
        params.par.value1 = self.grid_y
        params.par.name2 = 'gridz'
        params.par.value2 = self.grid_z

        # XY Grid SOP
        grid_xy = container.create(gridSOP, 'grid_xy')
        grid_xy.par.rows = self.grid_x
        grid_xy.par.cols = self.grid_z
        grid_xy.par.sizex = self.grid_x
        grid_xy.par.sizey = self.grid_z
        grid_xy.par.orient = 'xy'
        grid_xy.nodeY = 100

        # Line for Z copying
        line_z = container.create(lineSOP, 'line_z')
        line_z.par.orientation = 'z'
        line_z.par.length = self.grid_y
        line_z.par.divisions = self.grid_y - 1
        line_z.nodeY = -100

        # Copy to Z
        copy = container.create(copySOP, 'copy_to_z')
        copy.par.ncy = self.grid_y
        copy.par.ty.expr = 'stamps("../line_z", $CY, "P", 1)'
        copy.inputConnectors[0].connect(grid_xy)
        copy.nodeX = grid_xy.nodeX + 200
        copy.nodeY = 0

        # Transform to center
        xform = container.create(transformSOP, 'center_grid')
        xform.par.tx = -self.grid_x / 2.0
        xform.par.ty = -self.grid_y / 2.0
        xform.par.tz = -self.grid_z / 2.0
        xform.inputConnectors[0].connect(copy)
        xform.nodeX = copy.nodeX + 150

        # Add voxel coordinate attributes
        attrib = container.create(attribCreateSOP, 'voxel_coords')
        attrib.par.name1 = 'voxelX'
        attrib.par.type1 = 'float'
        attrib.par.value1x.expr = 'floor($TX + ' + str(self.grid_x/2) + ')'

        attrib.par.name2 = 'voxelY'
        attrib.par.type2 = 'float'
        attrib.par.value2x.expr = 'floor($TY + ' + str(self.grid_y/2) + ')'

        attrib.par.name3 = 'voxelZ'
        attrib.par.type3 = 'float'
        attrib.par.value3x.expr = 'floor($TZ + ' + str(self.grid_z/2) + ')'

        attrib.par.name4 = 'gridID'
        attrib.par.type4 = 'float'
        attrib.par.value4x.expr = 'v@voxelX + v@voxelY * ' + str(self.grid_x) + ' + v@voxelZ * ' + str(self.grid_x * self.grid_y)

        attrib.inputConnectors[0].connect(xform)
        attrib.nodeX = xform.nodeX + 200

        # Output null
        null = container.create(nullSOP, 'VOXEL_GRID_OUT')
        null.inputConnectors[0].connect(attrib)
        null.nodeX = attrib.nodeX + 150
        null.color = (0.5, 1, 0.5)

    def create_illusions(self):
        """Create all illusion scenes"""
        print("Creating illusions...")

        self.create_rotating_ames()
        self.create_infinite_corridor()
        self.create_kinetic_depth()
        self.create_necker_cube()

    def create_rotating_ames(self):
        """Create Rotating Ames Room illusion"""
        container = self.illusions.create(baseCOMP, 'rotating_ames')
        container.nodeX = -400

        # Parameters CHOP
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0
        params.par.name1 = 'depth'
        params.par.value1 = 1.0
        params.par.name2 = 'speed'
        params.par.value2 = 1.0

        # Base square
        grid = container.create(gridSOP, 'base_square')
        grid.par.rows = 1
        grid.par.cols = 1
        grid.par.sizex = 20
        grid.par.sizey = 20
        grid.nodeY = 100

        # Extrude to walls
        extrude = container.create(polyExtrudeSOP, 'walls')
        extrude.par.dist = 50
        extrude.inputConnectors[0].connect(grid)
        extrude.nodeX = grid.nodeX + 150
        extrude.nodeY = grid.nodeY

        # Trapezoid deformation
        wrangle = container.create(attribWrangleSOP, 'trapezoid_deform')
        wrangle.inputConnectors[0].connect(extrude)
        wrangle.nodeX = extrude.nodeX + 200

        vex_code = """
// Normalize Y position (0 at bottom, 1 at top)
float yNorm = (@P.y + 25) / 50.0;

// Scale factor decreases with height (trapezoid)
float depthParam = chf('depth');
float trapezoidScale = 0.6 + 0.4 * depthParam;
float scaleAtY = 1.0 - yNorm * (1.0 - trapezoidScale);

// Apply scale to X and Z
@P.x *= scaleAtY;
@P.z *= scaleAtY;
"""
        wrangle.par.snippet = vex_code
        wrangle.par.snippet.expr = 'me.par.snippet'

        # Resample to points
        resample = container.create(resampleSOP, 'to_points')
        resample.par.dosegs = True
        resample.par.maxseglength = 1.0
        resample.inputConnectors[0].connect(wrangle)
        resample.nodeX = wrangle.nodeX + 150

        # Keep only edges
        facet = container.create(facetSOP, 'edges_only')
        facet.par.premtedges = True
        facet.inputConnectors[0].connect(resample)
        facet.nodeX = resample.nodeX + 150

        # Rotation
        xform = container.create(transformSOP, 'rotate')
        xform.par.ry.expr = "chop('../../utilities/time_control/TIME_OUT')[0] * chf('../params/speed') * 0.3"
        xform.inputConnectors[0].connect(facet)
        xform.nodeX = facet.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.inputConnectors[0].connect(xform)
        null.nodeX = xform.nodeX + 150
        null.color = (1, 0.5, 0)

    def create_infinite_corridor(self):
        """Create Infinite Corridor illusion"""
        container = self.illusions.create(baseCOMP, 'infinite_corridor')
        container.nodeX = -200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0
        params.par.name1 = 'depth'
        params.par.value1 = 1.0
        params.par.name2 = 'speed'
        params.par.value2 = 1.0
        params.par.name3 = 'spacing'
        params.par.value3 = 1.0
        params.par.name4 = 'numFrames'
        params.par.value4 = 10

        # Using Script SOP for frame generation (simpler than For-Each for this case)
        script = container.create(scriptSOP, 'generate_frames')

        script_code = """
# Get parameters
import math

numFrames = int(parent().par.Numframes)
time = op('../../utilities/time_control/TIME_OUT')[0]
speed = parent().par.Speed
spacing = parent().par.Spacing
size = parent().par.Size
gridX = 30
gridY = 50
gridZ = 30

frameSpacing = max(3, int(4 * spacing))
scrollOffset = (time * speed * 3) % frameSpacing

geo = hou.Geometry()

for frame in range(numFrames):
    baseZ = gridZ - 1 - (frame * frameSpacing) + scrollOffset
    z = int(baseZ)
    wrappedZ = ((z % gridZ) + gridZ) % gridZ

    if wrappedZ < 0 or wrappedZ >= gridZ:
        continue

    normalizedPos = (baseZ / gridZ + 1) % 1
    scale = 0.2 + normalizedPos * 0.8 * size

    if scale <= 0:
        continue

    width = int(gridX / 2 * scale)
    height = int(gridY / 2 * scale)

    # Create rectangle outline
    points = []

    # Bottom edge
    for x in range(-width, width + 1):
        pt = geo.createPoint()
        pt.setPosition((x, -height, wrappedZ - gridZ/2))
        points.append(pt)

    # Right edge
    for y in range(-height + 1, height):
        pt = geo.createPoint()
        pt.setPosition((width, y, wrappedZ - gridZ/2))
        points.append(pt)

    # Top edge
    for x in range(width, -width - 1, -1):
        pt = geo.createPoint()
        pt.setPosition((x, height, wrappedZ - gridZ/2))
        points.append(pt)

    # Left edge
    for y in range(height - 1, -height, -1):
        pt = geo.createPoint()
        pt.setPosition((-width, y, wrappedZ - gridZ/2))
        points.append(pt)

scriptOp.setGeometry(geo)
"""
        script.par.python = script_code

        # Output
        null = container.create(nullSOP, 'OUT')
        null.inputConnectors[0].connect(script)
        null.nodeX = script.nodeX + 200
        null.color = (1, 0.5, 0)

    def create_kinetic_depth(self):
        """Create Kinetic Depth Effect illusion"""
        container = self.illusions.create(baseCOMP, 'kinetic_depth')
        container.nodeX = 0

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0
        params.par.name1 = 'speed'
        params.par.value1 = 1.0
        params.par.name2 = 'numWaves'
        params.par.value2 = 8

        # Script SOP to generate waves
        script = container.create(scriptSOP, 'generate_waves')

        script_code = """
import math

numWaves = int(parent().par.Numwaves)
size = parent().par.Size
speed = parent().par.Speed
time = op('../../utilities/time_control/TIME_OUT')[0]
angle = time * speed * 0.5
radius = 12 * size

geo = hou.Geometry()

for waveID in range(numWaves):
    wavePhase = (float(waveID) / numWaves) * math.pi * 2

    # Create polyline for this wave
    poly = geo.createPolygon()

    numPoints = 100
    for i in range(numPoints):
        t = float(i) / (numPoints - 1)
        theta = t * math.pi * 2

        # Create 2D sinusoidal wave
        sinValue = math.sin(theta * 3 + wavePhase)
        x2d = math.cos(theta) * radius
        y2d = sinValue * 5

        # Rotate in 3D
        x3d = x2d * math.cos(angle)
        z3d = x2d * math.sin(angle)

        pt = geo.createPoint()
        pt.setPosition((x3d, y2d, z3d))
        poly.addVertex(pt)

scriptOp.setGeometry(geo)
"""
        script.par.python = script_code

        # Resample for more points
        resample = container.create(resampleSOP, 'densify')
        resample.par.dosegs = True
        resample.par.maxseglength = 0.5
        resample.inputConnectors[0].connect(script)
        resample.nodeX = script.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.inputConnectors[0].connect(resample)
        null.nodeX = resample.nodeX + 150
        null.color = (1, 0.5, 0)

    def create_necker_cube(self):
        """Create Necker Cube illusion"""
        container = self.illusions.create(baseCOMP, 'necker_cube')
        container.nodeX = 200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0
        params.par.name1 = 'thickness'
        params.par.value1 = 0.5

        # Box SOP
        box = container.create(boxSOP, 'cube')
        box.par.sizex.expr = 'chf("../params/size") * 10'
        box.par.sizey.expr = 'chf("../params/size") * 10'
        box.par.sizez.expr = 'chf("../params/size") * 10'
        box.par.type = 'poly'

        # Wireframe (facet)
        facet = container.create(facetSOP, 'wireframe')
        facet.par.inlineu = True
        facet.par.inlinev = True
        facet.inputConnectors[0].connect(box)
        facet.nodeX = box.nodeX + 150

        # Resample edges to points
        resample = container.create(resampleSOP, 'edge_points')
        resample.par.dosegs = True
        resample.par.maxseglength = 0.5
        resample.inputConnectors[0].connect(facet)
        resample.nodeX = facet.nodeX + 150

        # Set point scale based on thickness
        attrib = container.create(attribCreateSOP, 'set_thickness')
        attrib.par.name1 = 'pscale'
        attrib.par.type1 = 'float'
        attrib.par.value1x.expr = 'chf("../params/thickness") * 0.5'
        attrib.inputConnectors[0].connect(resample)
        attrib.nodeX = resample.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.inputConnectors[0].connect(attrib)
        null.nodeX = attrib.nodeX + 150
        null.color = (1, 0.5, 0)

    def create_color_effects(self):
        """Create TOP-based color effects"""
        print("Creating color effects...")

        self.create_rainbow_sweep()
        self.create_plasma()
        self.create_fire()

    def create_rainbow_sweep(self):
        """Create rainbow sweep color effect"""
        container = self.color_effects.create(baseCOMP, 'rainbow_sweep')
        container.nodeX = -400

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0

        # Ramp U
        ramp_u = container.create(rampTOP, 'ramp_u')
        ramp_u.par.orient = 'horizontal'
        ramp_u.par.outputresolution = 'constant'
        ramp_u.par.resolutionw = 512
        ramp_u.par.resolutionh = 512
        ramp_u.nodeY = 100

        # Ramp V
        ramp_v = container.create(rampTOP, 'ramp_v')
        ramp_v.par.orient = 'vertical'
        ramp_v.par.outputresolution = 'constant'
        ramp_v.par.resolutionw = 512
        ramp_v.par.resolutionh = 512
        ramp_v.nodeY = -100

        # Combine UV
        comp = container.create(compositeTOP, 'combine_uv')
        comp.par.operation = 'add'
        comp.inputConnectors[0].connect(ramp_u)
        comp.inputConnectors[1].connect(ramp_v)
        comp.nodeX = ramp_u.nodeX + 200
        comp.nodeY = 0

        # Add time
        math1 = container.create(mathTOP, 'add_time')
        math1.par.srcapreop = 'add'
        math1.par.adda.expr = "chop('../../utilities/time_control/TIME_OUT')[0] * chf('../params/speed') * 2"
        math1.inputConnectors[0].connect(comp)
        math1.nodeX = comp.nodeX + 150

        # Scale
        math2 = container.create(mathTOP, 'scale')
        math2.par.srcapreop = 'mult'
        math2.par.multa = 0.5
        math2.inputConnectors[0].connect(math1)
        math2.nodeX = math1.nodeX + 150

        # Fract (via GLSL)
        glsl = container.create(glslTOP, 'fract')
        glsl.inputConnectors[0].connect(math2)
        glsl.nodeX = math2.nodeX + 150
        glsl.par.shader = """
uniform sampler2D sTD2DInputs[1];
out vec4 fragColor;
void main() {
    vec2 uv = gl_FragCoord.xy / uTD2DInfos[0].res.zw;
    float val = texture(sTD2DInputs[0], uv).r;
    fragColor = vec4(fract(val));
}
"""

        # Rainbow ramp
        rainbow = container.create(rampTOP, 'rainbow')
        rainbow.par.type = 'horizontal'
        rainbow.par.outputresolution = 'constant'
        rainbow.par.resolutionw = 512
        rainbow.par.resolutionh = 512
        rainbow.nodeX = glsl.nodeX
        rainbow.nodeY = glsl.nodeY - 200

        # Set rainbow colors (manually - TD doesn't expose color ramp well via script)
        # User will need to set this manually or we use default

        # Lookup
        lookup = container.create(lookupTOP, 'apply_rainbow')
        lookup.inputConnectors[0].connect(glsl)
        lookup.inputConnectors[1].connect(rainbow)
        lookup.nodeX = glsl.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 1, 0)

    def create_plasma(self):
        """Create plasma effect"""
        container = self.color_effects.create(baseCOMP, 'plasma')
        container.nodeX = -200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0

        # Get time
        time_expr = "chop('../../utilities/time_control/TIME_OUT')[0]"
        speed_expr = "chf('../params/speed')"

        # Ramp U
        ramp_u = container.create(rampTOP, 'ramp_u')
        ramp_u.par.orient = 'horizontal'
        ramp_u.par.outputresolution = 'constant'
        ramp_u.par.resolutionw = 512
        ramp_u.par.resolutionh = 512

        # Ramp V
        ramp_v = container.create(rampTOP, 'ramp_v')
        ramp_v.par.orient = 'vertical'
        ramp_v.par.outputresolution = 'constant'
        ramp_v.par.resolutionw = 512
        ramp_v.par.resolutionh = 512

        # Create 4 sine waves (simplified - full version would have proper wave setup)
        pattern1 = container.create(patternTOP, 'wave1')
        pattern1.par.type = 'sine'
        pattern1.par.outputresolution = 'constant'
        pattern1.par.resolutionw = 512
        pattern1.par.resolutionh = 512
        pattern1.par.period = 0.1
        pattern1.par.phase.expr = f"{time_expr} * {speed_expr}"
        pattern1.nodeY = 150
        pattern1.nodeX = 200

        pattern2 = container.create(patternTOP, 'wave2')
        pattern2.par.type = 'sine'
        pattern2.par.outputresolution = 'constant'
        pattern2.par.resolutionw = 512
        pattern2.par.resolutionh = 512
        pattern2.par.period = 0.1
        pattern2.par.phase.expr = f"{time_expr} * {speed_expr} * -0.7"
        pattern2.nodeY = 50
        pattern2.nodeX = 200

        # Composite waves
        comp = container.create(compositeTOP, 'combine_waves')
        comp.par.operation = 'add'
        comp.inputConnectors[0].connect(pattern1)
        comp.inputConnectors[1].connect(pattern2)
        comp.nodeX = 400

        # Normalize
        level = container.create(levelTOP, 'normalize')
        level.par.blacklevel1 = -2
        level.par.whitelevel1 = 2
        level.inputConnectors[0].connect(comp)
        level.nodeX = comp.nodeX + 150

        # Apply rainbow
        rainbow = container.create(rampTOP, 'rainbow')
        rainbow.par.type = 'horizontal'
        rainbow.par.outputresolution = 'constant'
        rainbow.par.resolutionw = 512
        rainbow.par.resolutionh = 512
        rainbow.nodeX = level.nodeX
        rainbow.nodeY = level.nodeY - 200

        lookup = container.create(lookupTOP, 'apply_color')
        lookup.inputConnectors[0].connect(level)
        lookup.inputConnectors[1].connect(rainbow)
        lookup.nodeX = level.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 1, 0)

    def create_fire(self):
        """Create fire effect"""
        container = self.color_effects.create(baseCOMP, 'fire')
        container.nodeX = 0

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'speed'
        params.par.value0 = 1.0

        # Height gradient (vertical ramp, inverted)
        height = container.create(rampTOP, 'height_gradient')
        height.par.orient = 'vertical'
        height.par.type = 'linear'
        height.par.outputresolution = 'constant'
        height.par.resolutionw = 512
        height.par.resolutionh = 512
        height.nodeY = 100

        # Noise (turbulence)
        noise = container.create(noiseTOP, 'turbulence')
        noise.par.type = 'turbulence'
        noise.par.amp = 0.3
        noise.par.noisetype = 'perlin'
        noise.par.harmonics = 3
        noise.par.outputresolution = 'constant'
        noise.par.resolutionw = 512
        noise.par.resolutionh = 512
        noise.par.posz.expr = "chop('../../utilities/time_control/TIME_OUT')[0] * chf('../params/speed') * 5"
        noise.nodeY = -100

        # Combine
        comp = container.create(compositeTOP, 'combine')
        comp.par.operation = 'add'
        comp.inputConnectors[0].connect(height)
        comp.inputConnectors[1].connect(noise)
        comp.nodeX = height.nodeX + 250
        comp.nodeY = 0

        # Fire color ramp
        fire_colors = container.create(rampTOP, 'fire_colors')
        fire_colors.par.type = 'horizontal'
        fire_colors.par.outputresolution = 'constant'
        fire_colors.par.resolutionw = 512
        fire_colors.par.resolutionh = 512
        fire_colors.nodeX = comp.nodeX
        fire_colors.nodeY = comp.nodeY - 200
        # Colors: dark red -> red -> orange -> yellow (user will adjust manually)

        # Lookup
        lookup = container.create(lookupTOP, 'apply_fire')
        lookup.inputConnectors[0].connect(comp)
        lookup.inputConnectors[1].connect(fire_colors)
        lookup.nodeX = comp.nodeX + 200

        # Output
        null = container.create(nullTOP, 'OUT')
        null.inputConnectors[0].connect(lookup)
        null.nodeX = lookup.nodeX + 150
        null.color = (1, 1, 0)

    def create_output_system(self):
        """Create output/render system"""
        print("Creating output system...")

        # Illusion selector
        select_chop = self.output.create(constantCHOP, 'illusion_select')
        select_chop.par.name0 = 'index'
        select_chop.par.value0 = 0  # 0=rotating_ames, 1=corridor, etc.

        # Color effect selector
        color_select_chop = self.output.create(constantCHOP, 'color_select')
        color_select_chop.par.name0 = 'index'
        color_select_chop.par.value0 = 0  # 0=rainbow, 1=plasma, 2=fire

        # Switch SOP for illusions
        switch_sop = self.output.create(switchSOP, 'illusion_switch')
        switch_sop.par.index.expr = 'chop("./illusion_select")[0]'
        switch_sop.inputConnectors[0].connect(op('../illusions/rotating_ames/OUT'))
        switch_sop.inputConnectors[1].connect(op('../illusions/infinite_corridor/OUT'))
        switch_sop.inputConnectors[2].connect(op('../illusions/kinetic_depth/OUT'))
        switch_sop.inputConnectors[3].connect(op('../illusions/necker_cube/OUT'))
        switch_sop.nodeX = -200

        # Switch TOP for color effects
        switch_top = self.output.create(switchTOP, 'color_switch')
        switch_top.par.index.expr = 'chop("./color_select")[0]'
        switch_top.inputConnectors[0].connect(op('../color_effects/rainbow_sweep/OUT'))
        switch_top.inputConnectors[1].connect(op('../color_effects/plasma/OUT'))
        switch_top.inputConnectors[2].connect(op('../color_effects/fire/OUT'))
        switch_top.nodeX = -200
        switch_top.nodeY = -200

        # Add UVs to geometry
        attrib_uv = self.output.create(attribCreateSOP, 'add_uvs')
        attrib_uv.par.name1 = 'uv'
        attrib_uv.par.type1 = 'vector'
        attrib_uv.par.size1 = 3
        attrib_uv.par.value1x.expr = '($TX + 15) / 30.0'
        attrib_uv.par.value1y.expr = '($TY + 25) / 50.0'
        attrib_uv.par.value1z.expr = '($TZ + 15) / 30.0'
        attrib_uv.inputConnectors[0].connect(switch_sop)
        attrib_uv.nodeX = switch_sop.nodeX + 200

        # Apply color from TOP to SOP
        color_from_map = self.output.create(attributeFromMapSOP, 'apply_color')
        color_from_map.par.texture = '../color_switch'
        color_from_map.par.class0 = 'point'
        color_from_map.par.attribute0 = 'Cd'
        color_from_map.par.uvattrib = 'uv'
        color_from_map.inputConnectors[0].connect(attrib_uv)
        color_from_map.nodeX = attrib_uv.nodeX + 200

        # Copy small spheres to points (LED representation)
        sphere = self.output.create(sphereSOP, 'led_sphere')
        sphere.par.type = 'poly'
        sphere.par.divsu = 8
        sphere.par.divst = 6
        sphere.par.rad = 0.3
        sphere.nodeX = color_from_map.nodeX - 100
        sphere.nodeY = color_from_map.nodeY - 200

        copy = self.output.create(copySOP, 'instance_leds')
        copy.par.ncy = 1
        copy.inputConnectors[0].connect(sphere)
        copy.inputConnectors[1].connect(color_from_map)
        copy.nodeX = color_from_map.nodeX + 200

        # Final output
        null = self.output.create(nullSOP, 'FINAL_GEOMETRY')
        null.inputConnectors[0].connect(copy)
        null.nodeX = copy.nodeX + 150
        null.color = (0, 1, 0)

    def create_master_control(self):
        """Create master control panel"""
        print("Creating master control...")

        # Info text
        info = self.control.create(textDAT, 'info')
        info.text = """VOLUMETRIC ILLUSIONS - MASTER CONTROL

USAGE:
1. Select illusion: control/illusion_selector CHOP (index 0-3)
   0 = Rotating Ames Room
   1 = Infinite Corridor
   2 = Kinetic Depth Effect
   3 = Necker Cube

2. Select color effect: control/color_selector CHOP (index 0-2)
   0 = Rainbow Sweep
   1 = Plasma
   2 = Fire

3. Adjust parameters in each illusion/effect's params CHOP

4. View output at: output/FINAL_GEOMETRY

PARAMETERS:
- Time speed: utilities/time_control/speed
- Each illusion has params CHOP inside its container
- Each color effect has params CHOP inside its container

STRUCTURE:
/utilities - Time control, distance calc, angle calc, voxel grid
/illusions - All illusion scenes (SOP-based)
/color_effects - All color effects (TOP-based)
/output - Combines illusion + color, renders final
/control - This info and selectors
"""

        # Illusion selector reference
        illusion_sel = self.control.create(constantCHOP, 'illusion_selector')
        illusion_sel.par.name0 = 'index'
        illusion_sel.par.value0 = 0
        illusion_sel.nodeX = -200

        # Color selector reference
        color_sel = self.control.create(constantCHOP, 'color_selector')
        color_sel.par.name0 = 'index'
        color_sel.par.value0 = 0
        color_sel.nodeX = 0

        # Link to output selectors
        op(self.output).op('illusion_select').par.value0.expr = 'op("../control/illusion_selector")[0]'
        op(self.output).op('color_select').par.value0.expr = 'op("../control/color_selector")[0]'

    def print_usage_instructions(self):
        """Print usage instructions to textport"""
        print("""
===============================================
VOLUMETRIC ILLUSIONS NETWORK - GENERATED!
===============================================

STRUCTURE:
/project1/utilities - Time control & calculation utilities
/project1/illusions - All illusion scenes (SOPs)
/project1/color_effects - All color effects (TOPs)
/project1/output - Final rendering system
/project1/control - Master control & info

USAGE:
1. View final output: /project1/output/FINAL_GEOMETRY
2. Change illusion: Edit /project1/control/illusion_selector (index 0-3)
3. Change color: Edit /project1/control/color_selector (index 0-2)
4. Adjust parameters: Each component has a 'params' CHOP inside

PARAMETERS LOCATION:
- Global time speed: /project1/utilities/time_control/speed
- Illusion params: /project1/illusions/[name]/params
- Color params: /project1/color_effects/[name]/params

AVAILABLE ILLUSIONS:
0 - Rotating Ames Room
1 - Infinite Corridor
2 - Kinetic Depth Effect
3 - Necker Cube

AVAILABLE COLOR EFFECTS:
0 - Rainbow Sweep
1 - Plasma
2 - Fire

NOTE: Some color ramps (rainbow, fire) may need manual color adjustment
in the TOP's color palette editor.

===============================================
""")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Execute directly (TouchDesigner Text DAT execution)
generator = VolumetricIllusionsGenerator()
generator.generate_all()
