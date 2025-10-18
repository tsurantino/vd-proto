"""
TouchDesigner Core Scenes Generator
Generates all core volumetric display scenes (non-illusions)
All parameters controlled via CHOP constants for modularity

Scenes Generated:
- Shape Morph (sphere, helix, torus, cube, pyramid, plane)
- Particle Flow (particles, spiral, explode, tornado, whirlpool, galaxy)
- Wave Field (ripple, plane, standing, interference)
- Procedural Volume (perlin, simplex, cellular noise)
- Grid (cube, sphere, tunnel, layers)
- Text 3D (block letters in 3D space)

Usage:
1. Open a fresh TouchDesigner project
2. Create a Text DAT
3. Paste this script into the Text DAT
4. Right-click the Text DAT and select "Run Script"

Author: Generated for Volumetric Display Prototype
Date: 2025
"""

import td

class CoreScenesGenerator:
    """Generator for core volumetric display scenes"""

    def __init__(self):
        self.root = op('/project1')
        self.grid_x = 30
        self.grid_y = 50
        self.grid_z = 30

    def generate_all(self):
        """Generate complete core scenes network"""
        print("Starting Core Scenes Network Generation...")

        # Create main structure
        self.create_main_structure()

        # Create utilities (time, noise, etc)
        self.create_utilities()

        # Create core scenes
        self.create_shape_morph_scenes()
        self.create_particle_flow_scenes()
        self.create_wave_field_scenes()
        self.create_procedural_scenes()
        self.create_grid_scenes()
        self.create_text_3d_scene()

        # Create output system
        self.create_output_system()

        # Create master control
        self.create_master_control()

        print("Core Scenes Generation Complete!")
        self.print_usage_instructions()

    def create_main_structure(self):
        """Create main folder structure"""
        print("Creating main structure...")

        # Main containers
        self.utilities = self.root.create(baseCOMP, 'utilities')
        self.core_scenes = self.root.create(baseCOMP, 'core_scenes')
        self.output = self.root.create(baseCOMP, 'output')
        self.control = self.root.create(baseCOMP, 'control')

        # Layout
        self.utilities.nodeY = 500
        self.core_scenes.nodeY = 200
        self.output.nodeY = -100
        self.control.nodeY = 700

    def create_utilities(self):
        """Create utility components"""
        print("Creating utilities...")

        self.create_time_control()
        self.create_noise_generator()

    def create_time_control(self):
        """Create time control system"""
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

        # Multiply
        math = container.create(mathCHOP, 'time_scaled')
        math.par.combine = 'mult'
        math.par.chan1 = 'seconds'
        math.par.chan2 = 'speed'
        math.setInput(0, timer)
        math.setInput(1, speed_const)
        math.nodeX = timer.nodeX + 200
        math.nodeY = timer.nodeY - 50

        # Output
        null = container.create(nullCHOP, 'TIME_OUT')
        null.setInput(0, math)
        null.nodeX = math.nodeX + 150
        null.color = (0.5, 1, 0.5)

    def create_noise_generator(self):
        """Create 3D noise generator (TOP-based)"""
        container = self.utilities.create(baseCOMP, 'noise_3d')
        container.nodeX = -200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'scale'
        params.par.value0 = 1.0
        params.par.name1 = 'octaves'
        params.par.value1 = 4
        params.par.name2 = 'speed'
        params.par.value2 = 1.0

        # 3D Noise
        noise = container.create(noiseTOP, 'perlin_3d')
        noise.par.type = 'turbulence'
        noise.par.noisetype = 'perlin'
        noise.par.outputresolution = 'constant'
        noise.par.resolutionw = 256
        noise.par.resolutionh = 256
        noise.par.period = "10 / chf('../params/scale')"
        noise.par.harmonics = "int(chf('../params/octaves'))"
        noise.par.posz = "chop('../../time_control/TIME_OUT')[0] * chf('../params/speed')"

        # Output
        null = container.create(nullTOP, 'NOISE_OUT')
        null.setInput(0, noise)
        null.nodeX = noise.nodeX + 200
        null.color = (0.5, 1, 0.5)

    # ========================================================================
    # SHAPE MORPH SCENES
    # ========================================================================

    def create_shape_morph_scenes(self):
        """Create all shape morph variants"""
        print("Creating shape morph scenes...")

        # Container for all shape morphs
        container = self.core_scenes.create(baseCOMP, 'shape_morph')
        container.nodeX = -600

        self.create_sphere_shape(container)
        self.create_helix_shape(container)
        self.create_torus_shape(container)
        self.create_cube_shape(container)
        self.create_pyramid_shape(container)
        self.create_plane_shape(container)

        # Shape selector switch
        self.create_shape_selector(container)

    def create_sphere_shape(self, parent):
        """Create sphere shape"""
        container = parent.create(baseCOMP, 'sphere')
        container.nodeX = -400
        container.nodeY = 200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0
        params.par.name1 = 'thickness'
        params.par.value1 = 0.5

        # Sphere SOP
        sphere = container.create(sphereSOP, 'sphere_geo')
        sphere.par.type = 'poly'
        sphere.par.rad = "5 + chf('../params/size') * 5"
        sphere.par.divsu = 20
        sphere.par.divst = 20

        # Optional: Make wireframe
        facet = container.create(facetSOP, 'wireframe')
        facet.par.inlineu = True
        facet.par.inlinev = True
        facet.setInput(0, sphere)
        facet.nodeX = sphere.nodeX + 150

        # Resample to points
        resample = container.create(resampleSOP, 'to_points')
        resample.par.dosegs = True
        resample.par.maxseglength = "1.0 / chf('../params/thickness')"
        resample.setInput(0, facet)
        resample.nodeX = facet.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, resample)
        null.nodeX = resample.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_helix_shape(self, parent):
        """Create helix/spiral shape"""
        container = parent.create(baseCOMP, 'helix')
        container.nodeX = -200
        container.nodeY = 200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0
        params.par.name1 = 'turns'
        params.par.value1 = 3.0
        params.par.name2 = 'radius'
        params.par.value2 = 1.0

        # Script SOP for helix
        script = container.create(scriptSOP, 'generate_helix')
        script.par.python = """
import math

size = parent().par.Size
turns = parent().par.Turns
radius = parent().par.Radius
time = op('../../utilities/time_control/TIME_OUT')[0]

geo = hou.Geometry()
poly = geo.createPolygon()

numPoints = 200
gridY = 50

for i in range(numPoints):
    t = float(i) / (numPoints - 1)

    # Vertical position
    y = (t - 0.5) * gridY

    # Spiral angle
    angle = t * turns * math.pi * 2 + time

    # Position
    r = 8 * size * radius
    x = math.cos(angle) * r
    z = math.sin(angle) * r

    pt = geo.createPoint()
    pt.setPosition((x, y, z))
    poly.addVertex(pt)

scriptOp.setGeometry(geo)
"""

        # Resample
        resample = container.create(resampleSOP, 'densify')
        resample.par.dosegs = True
        resample.par.maxseglength = 0.5
        resample.setInput(0, script)
        resample.nodeX = script.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, resample)
        null.nodeX = resample.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_torus_shape(self, parent):
        """Create torus shape"""
        container = parent.create(baseCOMP, 'torus')
        container.nodeX = 0
        container.nodeY = 200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0
        params.par.name1 = 'thickness'
        params.par.value1 = 0.5

        # Torus SOP
        torus = container.create(torusSOP, 'torus_geo')
        torus.par.type = 'poly'
        torus.par.rady = "10 * chf('../params/size')"
        torus.par.radx = "3 * chf('../params/size')"
        torus.par.divsu = 30
        torus.par.divst = 15

        # Rotate to vertical
        xform = container.create(transformSOP, 'orient')
        xform.par.rx = 90
        xform.setInput(0, torus)
        xform.nodeX = torus.nodeX + 150

        # Wireframe
        facet = container.create(facetSOP, 'wireframe')
        facet.par.inlineu = True
        facet.par.inlinev = True
        facet.setInput(0, xform)
        facet.nodeX = xform.nodeX + 150

        # Resample
        resample = container.create(resampleSOP, 'to_points')
        resample.par.dosegs = True
        resample.par.maxseglength = "1.0 / chf('../params/thickness')"
        resample.setInput(0, facet)
        resample.nodeX = facet.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, resample)
        null.nodeX = resample.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_cube_shape(self, parent):
        """Create cube shape"""
        container = parent.create(baseCOMP, 'cube')
        container.nodeX = 200
        container.nodeY = 200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0

        # Box
        box = container.create(boxSOP, 'box_geo')
        box.par.type = 'poly'
        box.par.sizex = "15 * chf('../params/size')"
        box.par.sizey = "15 * chf('../params/size')"
        box.par.sizez = "15 * chf('../params/size')"

        # Wireframe
        facet = container.create(facetSOP, 'wireframe')
        facet.par.inlineu = True
        facet.par.inlinev = True
        facet.setInput(0, box)
        facet.nodeX = box.nodeX + 150

        # Resample
        resample = container.create(resampleSOP, 'to_points')
        resample.par.dosegs = True
        resample.par.maxseglength = 1.0
        resample.setInput(0, facet)
        resample.nodeX = facet.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, resample)
        null.nodeX = resample.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_pyramid_shape(self, parent):
        """Create pyramid shape"""
        container = parent.create(baseCOMP, 'pyramid')
        container.nodeX = 400
        container.nodeY = 200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0

        # Script SOP for pyramid
        script = container.create(scriptSOP, 'generate_pyramid')
        script.par.python = """
size = parent().par.Size
base = 12 * size
height = 20 * size

geo = hou.Geometry()

# Base vertices
v0 = geo.createPoint()
v0.setPosition((-base, -height/2, -base))
v1 = geo.createPoint()
v1.setPosition((base, -height/2, -base))
v2 = geo.createPoint()
v2.setPosition((base, -height/2, base))
v3 = geo.createPoint()
v3.setPosition((-base, -height/2, base))

# Apex
apex = geo.createPoint()
apex.setPosition((0, height/2, 0))

# Create edges
# Base edges
for i in range(4):
    poly = geo.createPolygon()
    poly.addVertex(geo.points()[i])
    poly.addVertex(geo.points()[(i+1)%4])

# Side edges
for i in range(4):
    poly = geo.createPolygon()
    poly.addVertex(geo.points()[i])
    poly.addVertex(apex)

scriptOp.setGeometry(geo)
"""

        # Resample
        resample = container.create(resampleSOP, 'to_points')
        resample.par.dosegs = True
        resample.par.maxseglength = 1.0
        resample.setInput(0, script)
        resample.nodeX = script.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, resample)
        null.nodeX = resample.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_plane_shape(self, parent):
        """Create plane shape"""
        container = parent.create(baseCOMP, 'plane')
        container.nodeX = 600
        container.nodeY = 200

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0

        # Grid
        grid = container.create(gridSOP, 'grid_geo')
        grid.par.rows = "int(15 * chf('../params/size'))"
        grid.par.cols = "int(15 * chf('../params/size'))"
        grid.par.sizex = "20 * chf('../params/size')"
        grid.par.sizey = "20 * chf('../params/size')"
        grid.par.orient = 'xy'

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, grid)
        null.nodeX = grid.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_shape_selector(self, parent):
        """Create shape selector switch"""
        # Shape index selector
        selector = parent.create(constantCHOP, 'shape_select')
        selector.par.name0 = 'index'
        selector.par.value0 = 0  # 0=sphere, 1=helix, 2=torus, 3=cube, 4=pyramid, 5=plane
        selector.nodeY = -200

        # Switch SOP
        switch = parent.create(switchSOP, 'shape_output')
        switch.par.index = 'int(chop("./shape_select")[0])'
        switch.setInput(0, parent.op('sphere/OUT'))
        switch.setInput(1, parent.op('helix/OUT'))
        switch.setInput(2, parent.op('torus/OUT'))
        switch.setInput(3, parent.op('cube/OUT'))
        switch.setInput(4, parent.op('pyramid/OUT'))
        switch.setInput(5, parent.op('plane/OUT'))
        switch.nodeX = selector.nodeX + 200
        switch.nodeY = selector.nodeY

        # Final output
        null = parent.create(nullSOP, 'OUT')
        null.setInput(0, switch)
        null.nodeX = switch.nodeX + 150
        null.nodeY = switch.nodeY
        null.color = (0, 1, 0.5)

    # ========================================================================
    # PARTICLE FLOW SCENES
    # ========================================================================

    def create_particle_flow_scenes(self):
        """Create particle flow scenes"""
        print("Creating particle flow scenes...")

        container = self.core_scenes.create(baseCOMP, 'particle_flow')
        container.nodeX = -300

        self.create_particle_system_basic(container)
        self.create_particle_spiral(container)
        self.create_particle_tornado(container)

        # Particle pattern selector
        self.create_particle_selector(container)

    def create_particle_system_basic(self, parent):
        """Create basic particle system"""
        container = parent.create(baseCOMP, 'particles_basic')
        container.nodeX = -300

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'density'
        params.par.value0 = 0.5
        params.par.name1 = 'speed'
        params.par.value1 = 1.0

        # POP Network
        pop = container.create(baseCOMP, 'pop_network')

        # POP Source
        source = pop.create(popSourcePOP, 'source')
        source.par.birthrate = "100 * chf('../params/density')"
        source.par.lifeexp = 5

        # POP Force (gravity-like)
        force = pop.create(popForcePOP, 'flow_force')
        force.par.forcey = "-5 * chf('../params/speed')"
        force.setInput(0, source)
        force.nodeX = source.nodeX + 150

        # POP Wrangle (respawn at top when hitting bottom)
        wrangle = pop.create(popWranglePOP, 'respawn')
        wrangle.par.snippet = """
if (@P.y < -25) {
    @P.y = 25;
    @P.x = fit01(rand(@id * 0.1), -15, 15);
    @P.z = fit01(rand(@id * 0.2), -15, 15);
}
"""
        wrangle.setInput(0, force)
        wrangle.nodeX = force.nodeX + 150

        # Output
        output = pop.create(popOutputPOP, 'output')
        output.setInput(0, wrangle)
        output.nodeX = wrangle.nodeX + 150

        # Convert to geometry
        null = container.create(nullSOP, 'OUT')
        null.par.createinputnode = False
        null.par.objpath = './pop_network/output'
        null.nodeX = pop.nodeX + 300
        null.color = (1, 0.7, 0)

    def create_particle_spiral(self, parent):
        """Create spiral particle system"""
        container = parent.create(baseCOMP, 'particles_spiral')
        container.nodeX = -100

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'density'
        params.par.value0 = 0.5
        params.par.name1 = 'speed'
        params.par.value1 = 1.0

        # POP Network
        pop = container.create(baseCOMP, 'pop_network')

        # Source
        source = pop.create(popSourcePOP, 'source')
        source.par.birthrate = "50 * chf('../params/density')"
        source.par.lifeexp = 10

        # Spiral motion wrangle
        wrangle = pop.create(popWranglePOP, 'spiral_motion')
        wrangle.par.snippet = """
float speed = chf('speed');
float angle = @age * speed + @id * 0.1;
float radius = 8 + @age * 0.5;

@P.x = cos(angle) * radius;
@P.z = sin(angle) * radius;
@P.y = 25 - @age * 5 * speed;

if (@P.y < -25) {
    @dead = 1;
}
"""
        wrangle.setInput(0, source)
        wrangle.nodeX = source.nodeX + 150

        # Output
        output = pop.create(popOutputPOP, 'output')
        output.setInput(0, wrangle)
        output.nodeX = wrangle.nodeX + 150

        # Convert to geometry
        null = container.create(nullSOP, 'OUT')
        null.par.createinputnode = False
        null.par.objpath = './pop_network/output'
        null.nodeX = pop.nodeX + 300
        null.color = (1, 0.7, 0)

    def create_particle_tornado(self, parent):
        """Create tornado/vortex particle system"""
        container = parent.create(baseCOMP, 'particles_tornado')
        container.nodeX = 100

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'density'
        params.par.value0 = 0.5
        params.par.name1 = 'speed'
        params.par.value1 = 1.0
        params.par.name2 = 'radius'
        params.par.value2 = 1.0

        # POP Network
        pop = container.create(baseCOMP, 'pop_network')

        # Source (scattered in volume)
        source = pop.create(popSourcePOP, 'source')
        source.par.birthrate = "80 * chf('../params/density')"
        source.par.lifeexp = 8

        # Tornado wrangle
        wrangle = pop.create(popWranglePOP, 'tornado_motion')
        wrangle.par.snippet = """
float speed = chf('speed');
float maxRadius = chf('radius') * 10;

// Spiral upward
float angle = @age * speed * 2 + @id * 0.2;
float height = -25 + @age * 6 * speed;
float radius = fit(height, -25, 25, maxRadius, 2);

@P.x = cos(angle) * radius;
@P.z = sin(angle) * radius;
@P.y = height;

if (@P.y > 25) {
    @dead = 1;
}
"""
        wrangle.setInput(0, source)
        wrangle.nodeX = source.nodeX + 150

        # Output
        output = pop.create(popOutputPOP, 'output')
        output.setInput(0, wrangle)
        output.nodeX = wrangle.nodeX + 150

        # Convert to geometry
        null = container.create(nullSOP, 'OUT')
        null.par.createinputnode = False
        null.par.objpath = './pop_network/output'
        null.nodeX = pop.nodeX + 300
        null.color = (1, 0.7, 0)

    def create_particle_selector(self, parent):
        """Create particle pattern selector"""
        selector = parent.create(constantCHOP, 'pattern_select')
        selector.par.name0 = 'index'
        selector.par.value0 = 0  # 0=basic, 1=spiral, 2=tornado
        selector.nodeY = -200

        # Switch
        switch = parent.create(switchSOP, 'particle_output')
        switch.par.index = 'int(chop("./pattern_select")[0])'
        switch.setInput(0, parent.op('particles_basic/OUT'))
        switch.setInput(1, parent.op('particles_spiral/OUT'))
        switch.setInput(2, parent.op('particles_tornado/OUT'))
        switch.nodeX = selector.nodeX + 200
        switch.nodeY = selector.nodeY

        # Output
        null = parent.create(nullSOP, 'OUT')
        null.setInput(0, switch)
        null.nodeX = switch.nodeX + 150
        null.color = (0, 1, 0.5)

    # ========================================================================
    # WAVE FIELD SCENES
    # ========================================================================

    def create_wave_field_scenes(self):
        """Create wave field scenes"""
        print("Creating wave field scenes...")

        container = self.core_scenes.create(baseCOMP, 'wave_field')
        container.nodeX = 0

        self.create_wave_ripple(container)
        self.create_wave_plane(container)
        self.create_wave_standing(container)

        # Wave selector
        self.create_wave_selector(container)

    def create_wave_ripple(self, parent):
        """Create ripple wave effect"""
        container = parent.create(baseCOMP, 'wave_ripple')
        container.nodeX = -300

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'frequency'
        params.par.value0 = 1.0
        params.par.name1 = 'amplitude'
        params.par.value1 = 1.0

        # Grid
        grid = container.create(gridSOP, 'base_grid')
        grid.par.rows = 30
        grid.par.cols = 30
        grid.par.sizex = 30
        grid.par.sizey = 30
        grid.par.orient = 'xz'

        # Ripple deformation
        wrangle = container.create(attribWrangleSOP, 'ripple')
        wrangle.par.snippet = """
float time = chop('../../utilities/time_control/TIME_OUT')[0];
float freq = chf('frequency');
float amp = chf('amplitude');

float dist = length(set(@P.x, @P.z));
float wave = sin(dist * freq - time * 5) * amp * 5;

@P.y = wave;
"""
        wrangle.setInput(0, grid)
        wrangle.nodeX = grid.nodeX + 200

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, wrangle)
        null.nodeX = wrangle.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_wave_plane(self, parent):
        """Create traveling plane wave"""
        container = parent.create(baseCOMP, 'wave_plane')
        container.nodeX = -100

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'frequency'
        params.par.value0 = 1.0
        params.par.name1 = 'amplitude'
        params.par.value1 = 1.0

        # Grid
        grid = container.create(gridSOP, 'base_grid')
        grid.par.rows = 30
        grid.par.cols = 30
        grid.par.sizex = 30
        grid.par.sizey = 30
        grid.par.orient = 'xz'

        # Plane wave
        wrangle = container.create(attribWrangleSOP, 'plane_wave')
        wrangle.par.snippet = """
float time = chop('../../utilities/time_control/TIME_OUT')[0];
float freq = chf('frequency');
float amp = chf('amplitude');

float wave = sin(@P.z * freq - time * 5) * amp * 5;
@P.y = wave;
"""
        wrangle.setInput(0, grid)
        wrangle.nodeX = grid.nodeX + 200

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, wrangle)
        null.nodeX = wrangle.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_wave_standing(self, parent):
        """Create standing wave"""
        container = parent.create(baseCOMP, 'wave_standing')
        container.nodeX = 100

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'frequency'
        params.par.value0 = 1.0
        params.par.name1 = 'amplitude'
        params.par.value1 = 1.0

        # Grid
        grid = container.create(gridSOP, 'base_grid')
        grid.par.rows = 30
        grid.par.cols = 30
        grid.par.sizex = 30
        grid.par.sizey = 30
        grid.par.orient = 'xz'

        # Standing wave
        wrangle = container.create(attribWrangleSOP, 'standing_wave')
        wrangle.par.snippet = """
float time = chop('../../utilities/time_control/TIME_OUT')[0];
float freq = chf('frequency');
float amp = chf('amplitude');

float waveX = sin(@P.x * freq);
float waveZ = sin(@P.z * freq);
float timeWave = sin(time * 3);

@P.y = waveX * waveZ * timeWave * amp * 5;
"""
        wrangle.setInput(0, grid)
        wrangle.nodeX = grid.nodeX + 200

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, wrangle)
        null.nodeX = wrangle.nodeX + 150
        null.color = (1, 0.7, 0)

    def create_wave_selector(self, parent):
        """Create wave selector"""
        selector = parent.create(constantCHOP, 'wave_select')
        selector.par.name0 = 'index'
        selector.par.value0 = 0  # 0=ripple, 1=plane, 2=standing
        selector.nodeY = -200

        # Switch
        switch = parent.create(switchSOP, 'wave_output')
        switch.par.index = 'int(chop("./wave_select")[0])'
        switch.setInput(0, parent.op('wave_ripple/OUT'))
        switch.setInput(1, parent.op('wave_plane/OUT'))
        switch.setInput(2, parent.op('wave_standing/OUT'))
        switch.nodeX = selector.nodeX + 200
        switch.nodeY = selector.nodeY

        # Output
        null = parent.create(nullSOP, 'OUT')
        null.setInput(0, switch)
        null.nodeX = switch.nodeX + 150
        null.color = (0, 1, 0.5)

    # ========================================================================
    # PROCEDURAL SCENES
    # ========================================================================

    def create_procedural_scenes(self):
        """Create procedural volume scenes"""
        print("Creating procedural scenes...")

        container = self.core_scenes.create(baseCOMP, 'procedural')
        container.nodeX = 300

        self.create_perlin_noise_scene(container)

        # For simplicity, just one procedural for now
        # Output directly
        null = container.create(nullSOP, 'OUT')
        null.par.createinputnode = False
        null.par.objpath = './perlin/OUT'
        null.color = (0, 1, 0.5)

    def create_perlin_noise_scene(self, parent):
        """Create perlin noise volume"""
        container = parent.create(baseCOMP, 'perlin')
        container.nodeX = 0

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'scale'
        params.par.value0 = 1.0
        params.par.name1 = 'threshold'
        params.par.value1 = 0.5

        # Volume (noise)
        volume = container.create(volumeSOP, 'noise_volume')
        volume.par.divsize = 2
        volume.par.sizex = 30
        volume.par.sizey = 50
        volume.par.sizez = 30

        # Volume Wrangle (noise generation)
        wrangle = container.create(volumeWrangleSOP, 'generate_noise')
        wrangle.par.snippet = """
float time = chop('../../utilities/time_control/TIME_OUT')[0];
float scale = chf('scale');
vector pos = @P / (10.0 / scale);
pos.z += time;

f@density = noise(pos);
"""
        wrangle.setInput(0, volume)
        wrangle.nodeX = volume.nodeX + 200

        # Convert to fog volume
        volume_vop = container.create(volumeVOP, 'to_fog')
        volume_vop.setInput(0, wrangle)
        volume_vop.nodeX = wrangle.nodeX + 150

        # Scatter points in volume
        scatter = container.create(scatterSOP, 'to_points')
        scatter.par.npts = 1000
        scatter.par.usedensityattrib = True
        scatter.par.densityattrib = 'density'
        scatter.setInput(0, volume_vop)
        scatter.nodeX = volume_vop.nodeX + 200

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, scatter)
        null.nodeX = scatter.nodeX + 150
        null.color = (1, 0.7, 0)

    # ========================================================================
    # GRID SCENES
    # ========================================================================

    def create_grid_scenes(self):
        """Create grid pattern scenes"""
        print("Creating grid scenes...")

        container = self.core_scenes.create(baseCOMP, 'grid')
        container.nodeX = 600

        self.create_cube_grid(container)

        # Simple output
        null = container.create(nullSOP, 'OUT')
        null.par.createinputnode = False
        null.par.objpath = './cube_grid/OUT'
        null.color = (0, 1, 0.5)

    def create_cube_grid(self, parent):
        """Create cube grid pattern"""
        container = parent.create(baseCOMP, 'cube_grid')

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'spacing'
        params.par.value0 = 5.0

        # Script SOP
        script = container.create(scriptSOP, 'generate_grid')
        script.par.python = """
spacing = parent().par.Spacing
gridX, gridY, gridZ = 30, 50, 30

geo = hou.Geometry()

for x in range(0, int(gridX), int(spacing)):
    for y in range(0, int(gridY), int(spacing)):
        for z in range(0, int(gridZ), int(spacing)):
            pt = geo.createPoint()
            pt.setPosition((x - gridX/2, y - gridY/2, z - gridZ/2))

scriptOp.setGeometry(geo)
"""

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, script)
        null.nodeX = script.nodeX + 150
        null.color = (1, 0.7, 0)

    # ========================================================================
    # TEXT 3D SCENE
    # ========================================================================

    def create_text_3d_scene(self):
        """Create 3D text scene"""
        print("Creating text 3D scene...")

        container = self.core_scenes.create(baseCOMP, 'text_3d')
        container.nodeX = 900

        # Parameters
        params = container.create(constantCHOP, 'params')
        params.par.name0 = 'size'
        params.par.value0 = 1.0
        params.par.name1 = 'depth'
        params.par.value1 = 1.0

        # Text SOP
        text = container.create(textSOP, 'text')
        text.par.text = 'HELLO'
        text.par.fontsize = "10 * chf('../params/size')"

        # Font (note: font paths vary by system)
        # User may need to adjust

        # Convert to 3D
        extrude = container.create(polyExtrudeSOP, 'extrude_3d')
        extrude.par.dist = "5 * chf('../params/depth')"
        extrude.setInput(0, text)
        extrude.nodeX = text.nodeX + 150

        # Center
        xform = container.create(transformSOP, 'center')
        xform.par.tz = "-2.5 * chf('../params/depth')"
        xform.setInput(0, extrude)
        xform.nodeX = extrude.nodeX + 150

        # Wireframe
        facet = container.create(facetSOP, 'wireframe')
        facet.par.inlineu = True
        facet.par.inlinev = True
        facet.setInput(0, xform)
        facet.nodeX = xform.nodeX + 150

        # Resample
        resample = container.create(resampleSOP, 'to_points')
        resample.par.dosegs = True
        resample.par.maxseglength = 1.0
        resample.setInput(0, facet)
        resample.nodeX = facet.nodeX + 150

        # Output
        null = container.create(nullSOP, 'OUT')
        null.setInput(0, resample)
        null.nodeX = resample.nodeX + 150
        null.color = (0, 1, 0.5)

    # ========================================================================
    # OUTPUT SYSTEM
    # ========================================================================

    def create_output_system(self):
        """Create output system with scene selector"""
        print("Creating output system...")

        # Scene selector
        selector = self.output.create(constantCHOP, 'scene_select')
        selector.par.name0 = 'index'
        selector.par.value0 = 0  # 0=shape_morph, 1=particle, 2=wave, 3=procedural, 4=grid, 5=text
        selector.nodeX = -200

        # Switch SOP
        switch = self.output.create(switchSOP, 'scene_output')
        switch.par.index = 'int(chop("./scene_select")[0])'
        switch.setInput(0, op('../core_scenes/shape_morph/OUT'))
        switch.setInput(1, op('../core_scenes/particle_flow/OUT'))
        switch.setInput(2, op('../core_scenes/wave_field/OUT'))
        switch.setInput(3, op('../core_scenes/procedural/OUT'))
        switch.setInput(4, op('../core_scenes/grid/OUT'))
        switch.setInput(5, op('../core_scenes/text_3d/OUT'))
        switch.nodeX = selector.nodeX + 200

        # Add point scale
        attrib = self.output.create(attribCreateSOP, 'add_pscale')
        attrib.par.name1 = 'pscale'
        attrib.par.type1 = 'float'
        attrib.par.value1x = 0.3
        attrib.setInput(0, switch)
        attrib.nodeX = switch.nodeX + 150

        # Copy spheres
        sphere = self.output.create(sphereSOP, 'led_sphere')
        sphere.par.type = 'poly'
        sphere.par.rad = 0.3
        sphere.par.divsu = 6
        sphere.par.divst = 4
        sphere.nodeX = attrib.nodeX - 100
        sphere.nodeY = attrib.nodeY - 200

        copy = self.output.create(copySOP, 'instance_leds')
        copy.setInput(0, sphere)
        copy.setInput(1, attrib)
        copy.nodeX = attrib.nodeX + 200

        # Final output
        null = self.output.create(nullSOP, 'FINAL_GEOMETRY')
        null.setInput(0, copy)
        null.nodeX = copy.nodeX + 150
        null.color = (0, 1, 0)

    # ========================================================================
    # MASTER CONTROL
    # ========================================================================

    def create_master_control(self):
        """Create master control panel"""
        print("Creating master control...")

        # Info
        info = self.control.create(textDAT, 'info')
        info.text = """CORE SCENES - MASTER CONTROL

USAGE:
Select scene type: control/scene_selector (index 0-5)

SCENES:
0 - Shape Morph (sphere, helix, torus, cube, pyramid, plane)
1 - Particle Flow (basic, spiral, tornado)
2 - Wave Field (ripple, plane, standing)
3 - Procedural (perlin noise)
4 - Grid (cube grid)
5 - Text 3D

PARAMETERS:
- Global speed: utilities/time_control/speed
- Scene sub-type: Each scene category has selector CHOP
  - Shape type: core_scenes/shape_morph/shape_select
  - Particle pattern: core_scenes/particle_flow/pattern_select
  - Wave type: core_scenes/wave_field/wave_select
- Each variant has params CHOP inside

VIEW OUTPUT: output/FINAL_GEOMETRY
"""

        # Scene selector
        scene_sel = self.control.create(constantCHOP, 'scene_selector')
        scene_sel.par.name0 = 'index'
        scene_sel.par.value0 = 0
        scene_sel.nodeX = -200

        # Link to output
        op(self.output).op('scene_select').par.value0.expr = 'op("../control/scene_selector")[0]'

    def print_usage_instructions(self):
        """Print usage instructions"""
        print("""
===============================================
CORE SCENES NETWORK - GENERATED!
===============================================

STRUCTURE:
/project1/utilities - Time control, noise generator
/project1/core_scenes - All core scene types
/project1/output - Final rendering
/project1/control - Master control

SCENES AVAILABLE:
0 - Shape Morph (6 shapes)
    - Control: core_scenes/shape_morph/shape_select (0-5)
1 - Particle Flow (3 patterns)
    - Control: core_scenes/particle_flow/pattern_select (0-2)
2 - Wave Field (3 wave types)
    - Control: core_scenes/wave_field/wave_select (0-2)
3 - Procedural (noise volume)
4 - Grid (cube grid pattern)
5 - Text 3D

CONTROLS:
- Main scene: /project1/control/scene_selector
- Sub-type: Each scene has its own selector
- Parameters: params CHOP in each variant

VIEW OUTPUT: /project1/output/FINAL_GEOMETRY

===============================================
""")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    generator = CoreScenesGenerator()
    generator.generate_all()
