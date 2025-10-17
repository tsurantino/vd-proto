/**
 * Main Application Entry Point
 * Initializes the volumetric display and UI controls for scene-based system
 */
import { VolumetricDisplay } from './VolumetricDisplay.js';

// ============================================================================
// DEBUG LOGGING SYSTEM
// ============================================================================
const DebugLogger = {
    logs: [],
    maxLogs: 100,
    container: null,

    init() {
        this.container = document.getElementById('debug-logs');
        this.setupDebugPanel();
        this.interceptConsole();
        this.log('Debug system initialized', 'success');
    },

    setupDebugPanel() {
        const debugHeader = document.getElementById('debug-header');
        const debugContent = document.getElementById('debug-content');
        const debugToggle = document.getElementById('debug-toggle');
        const debugClear = document.getElementById('debug-clear');

        debugHeader.addEventListener('click', () => {
            debugHeader.classList.toggle('collapsed');
            debugContent.classList.toggle('collapsed');
            debugToggle.textContent = debugContent.classList.contains('collapsed') ? '▶' : '▼';
        });

        debugClear.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent toggling when clicking clear
            this.clear();
        });
    },

    interceptConsole() {
        const originalLog = console.log;
        const originalWarn = console.warn;
        const originalError = console.error;

        console.log = (...args) => {
            originalLog.apply(console, args);
            this.log(args.join(' '), 'info');
        };

        console.warn = (...args) => {
            originalWarn.apply(console, args);
            this.log(args.join(' '), 'warn');
        };

        console.error = (...args) => {
            originalError.apply(console, args);
            this.log(args.join(' '), 'error');
        };

        // Capture errors
        window.addEventListener('error', (e) => {
            this.log(`ERROR: ${e.message} at ${e.filename}:${e.lineno}:${e.colno}`, 'error');
        });

        window.addEventListener('unhandledrejection', (e) => {
            this.log(`UNHANDLED PROMISE REJECTION: ${e.reason}`, 'error');
        });
    },

    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = {
            timestamp,
            message,
            type
        };

        this.logs.push(logEntry);
        if (this.logs.length > this.maxLogs) {
            this.logs.shift();
        }

        this.render();
    },

    render() {
        if (!this.container) return;

        this.container.innerHTML = this.logs.map(log =>
            `<div class="log-${log.type}">[${log.timestamp}] ${log.message}</div>`
        ).join('');

        this.container.scrollTop = this.container.scrollHeight;
    },

    clear() {
        this.logs = [];
        this.render();
        this.log('Debug log cleared', 'info');
    }
};

// Initialize debug system first
DebugLogger.init();

// Initialize the display (gridX, gridY, gridZ) = (40, 20, 40)
console.log('Initializing Volumetric Display...');
const display = new VolumetricDisplay('canvas', 40, 20, 40);
console.log('Display initialized successfully');

// Get grid info and display
const gridInfo = display.getGridInfo();
document.getElementById('grid-resolution').textContent = `${gridInfo.x}×${gridInfo.y}×${gridInfo.z}`;

// Set up callbacks
let lastFPS = 0;
display.setFPSCallback((fps) => {
    document.getElementById('fps').textContent = `FPS: ${fps}`;

    // Log significant FPS drops
    if (lastFPS > 0 && fps < 30 && lastFPS >= 30) {
        console.warn(`FPS dropped to ${fps} (was ${lastFPS})`);
    } else if (lastFPS > 0 && fps < 15 && lastFPS >= 15) {
        console.error(`Critical FPS drop: ${fps} (was ${lastFPS})`);
    }
    lastFPS = fps;
});

let currentActiveLEDs = 0;
display.setActiveLEDsCallback((count) => {
    currentActiveLEDs = count;
    document.getElementById('active-leds').textContent = count.toLocaleString();
});

// Update camera view display
function updateCameraView() {
    const rx = display.renderer.rotation.x.toFixed(1);
    const ry = display.renderer.rotation.y.toFixed(1);
    document.getElementById('camera-view').textContent = `(${rx}, ${ry})`;
}

setInterval(updateCameraView, 100);

// ============================================================================
// COLOR CONTROLS (unchanged from original)
// ============================================================================

const colorPresetBtns = document.querySelectorAll('.color-preset-btn');
colorPresetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        colorPresetBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const type = btn.dataset.type;
        if (type === 'single') {
            const color = btn.dataset.color;
            display.renderer.setSingleColor(color);
        } else if (type === 'gradient') {
            const colors = btn.dataset.gradient.split(',');
            display.renderer.setGradientColors(colors);
        }
    });
});

document.getElementById('apply-single-color').addEventListener('click', () => {
    const color = document.getElementById('custom-single-color').value;
    display.renderer.setSingleColor(color);
    colorPresetBtns.forEach(b => b.classList.remove('active'));
});

document.getElementById('apply-gradient').addEventListener('click', () => {
    const startColor = document.getElementById('custom-gradient-start').value;
    const endColor = document.getElementById('custom-gradient-end').value;
    display.renderer.setGradientColors([startColor, endColor]);
    colorPresetBtns.forEach(b => b.classList.remove('active'));
});

const colorEffectBtns = document.querySelectorAll('.color-effect-btn');
colorEffectBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        colorEffectBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const effect = btn.dataset.effect;
        display.renderer.setColorEffect(effect);
    });
});

const colorEffectSpeedSlider = document.getElementById('color-effect-speed');
const colorEffectSpeedValue = document.getElementById('color-effect-speed-value');

colorEffectSpeedSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    display.renderer.setColorEffectSpeed(val);
    colorEffectSpeedValue.textContent = val.toFixed(1);
});

// ============================================================================
// GLOBAL SCENE PARAMETERS
// ============================================================================

const globalParamsContainer = document.getElementById('global-params-container');

function createGlobalParameterControls() {
    console.log('Creating global parameter controls');

    // Size/Scale
    createGlobalSliderControl('size', 'Size / Scale', display.getGlobalSceneParameter('size'), 0.1, 3, 0.1);

    // Density/Thickness
    createGlobalSliderControl('density', 'Density / Thickness', display.getGlobalSceneParameter('density'), 0, 1, 0.05);

    // Object Count
    createGlobalSliderControl('objectCount', 'Object Count', display.getGlobalSceneParameter('objectCount'), 1, 4, 1);

    // Object Arrangement
    createGlobalSelectControl('objectArrangement', 'Object Arrangement', display.getGlobalSceneParameter('objectArrangement'), [
        { value: 'circular', label: 'Circular' },
        { value: 'linear', label: 'Linear/Trailing' }
    ]);

    // Object Offset (time stagger between objects)
    createGlobalSliderControl('objectOffset', 'Object Time Offset', display.getGlobalSceneParameter('objectOffset'), 0, 1, 0.05);

    // Animation Speed
    createGlobalSliderControl('animationSpeed', 'Animation Speed', display.getGlobalSceneParameter('animationSpeed'), 0.1, 3, 0.1);

    // Movement Controls Section Header
    const movementHeader = document.createElement('div');
    movementHeader.className = 'subsection-title';
    movementHeader.textContent = 'Movement Controls';
    movementHeader.style.marginTop = '15px';
    globalParamsContainer.appendChild(movementHeader);

    // Rotation Controls
    createGlobalSliderControl('rotationX', 'Rotation X', display.getGlobalSceneParameter('rotationX'), -1, 1, 0.1);
    createGlobalSliderControl('rotationY', 'Rotation Y', display.getGlobalSceneParameter('rotationY'), -1, 1, 0.1);
    createGlobalSliderControl('rotationZ', 'Rotation Z', display.getGlobalSceneParameter('rotationZ'), -1, 1, 0.1);

    // Translation Controls
    createGlobalSliderControl('translateX', 'Translate X Speed', display.getGlobalSceneParameter('translateX'), 0, 1, 0.05);
    createGlobalSliderControl('translateZ', 'Translate Z Speed', display.getGlobalSceneParameter('translateZ'), 0, 1, 0.05);
    createGlobalSliderControl('translateAmplitude', 'Translate Distance', display.getGlobalSceneParameter('translateAmplitude'), 0, 1, 0.05);

    // Bounce Controls
    createGlobalSliderControl('bounceSpeed', 'Bounce Speed', display.getGlobalSceneParameter('bounceSpeed'), 0, 1, 0.05);
    createGlobalSliderControl('bounceHeight', 'Bounce Height', display.getGlobalSceneParameter('bounceHeight'), 0, 1, 0.05);

    // Orbit Controls
    createGlobalSliderControl('orbitSpeed', 'Orbit Speed', display.getGlobalSceneParameter('orbitSpeed'), 0, 1, 0.05);
    createGlobalSliderControl('orbitRadius', 'Orbit Radius', display.getGlobalSceneParameter('orbitRadius'), 0, 1, 0.05);

    // Pulse Controls
    createGlobalSliderControl('pulseSpeed', 'Pulse Speed', display.getGlobalSceneParameter('pulseSpeed'), 0, 1, 0.05);
    createGlobalSliderControl('pulseAmount', 'Pulse Amount', display.getGlobalSceneParameter('pulseAmount'), 0, 1, 0.05);

    // Advanced Movement Section Header
    const advMovementHeader = document.createElement('div');
    advMovementHeader.className = 'subsection-title';
    advMovementHeader.textContent = 'Advanced Movement';
    advMovementHeader.style.marginTop = '15px';
    globalParamsContainer.appendChild(advMovementHeader);

    // Spiral Controls
    createGlobalSliderControl('spiralSpeed', 'Spiral Speed', display.getGlobalSceneParameter('spiralSpeed'), 0, 1, 0.05);
    createGlobalSliderControl('spiralRadius', 'Spiral Radius', display.getGlobalSceneParameter('spiralRadius'), 0, 1, 0.05);
    createGlobalSliderControl('spiralHeight', 'Spiral Height', display.getGlobalSceneParameter('spiralHeight'), 0, 1, 0.05);

    // Wobble Controls
    createGlobalSliderControl('wobbleSpeed', 'Wobble Speed', display.getGlobalSceneParameter('wobbleSpeed'), 0, 1, 0.05);
    createGlobalSliderControl('wobbleAmount', 'Wobble Amount', display.getGlobalSceneParameter('wobbleAmount'), 0, 1, 0.05);

    // Figure-8 Controls
    createGlobalSliderControl('figure8Speed', 'Figure-8 Speed', display.getGlobalSceneParameter('figure8Speed'), 0, 1, 0.05);
    createGlobalSliderControl('figure8Size', 'Figure-8 Size', display.getGlobalSceneParameter('figure8Size'), 0, 1, 0.05);

    // Elliptical Orbit Controls
    createGlobalSliderControl('ellipseSpeed', 'Ellipse Speed', display.getGlobalSceneParameter('ellipseSpeed'), 0, 1, 0.05);
    createGlobalSliderControl('ellipseRadiusX', 'Ellipse Radius X', display.getGlobalSceneParameter('ellipseRadiusX'), 0, 1, 0.05);
    createGlobalSliderControl('ellipseRadiusZ', 'Ellipse Radius Z', display.getGlobalSceneParameter('ellipseRadiusZ'), 0, 1, 0.05);

    // Scroll Controls
    createGlobalSliderControl('scrollSpeed', 'Scroll Speed', display.getGlobalSceneParameter('scrollSpeed'), 0, 5, 0.1);
    createGlobalSelectControl('scrollDirection', 'Scroll Direction', display.getGlobalSceneParameter('scrollDirection'), [
        { value: 'x', label: 'X' },
        { value: 'y', label: 'Y' },
        { value: 'z', label: 'Z' },
        { value: 'diagonal', label: 'Diagonal' }
    ]);

    // Legacy Animation Type (for procedural/plasma scenes only)
    createGlobalSelectControl('animationType', 'Legacy Animation', display.getGlobalSceneParameter('animationType'), [
        { value: 'none', label: 'None' },
        { value: 'evolve', label: 'Evolve' },
        { value: 'scroll', label: 'Scroll' }
    ]);

    // Wave/Procedural Section Header
    const waveHeader = document.createElement('div');
    waveHeader.className = 'subsection-title';
    waveHeader.textContent = 'Wave & Procedural';
    waveHeader.style.marginTop = '15px';
    globalParamsContainer.appendChild(waveHeader);

    // Frequency
    createGlobalSliderControl('frequency', 'Frequency', display.getGlobalSceneParameter('frequency'), 0.1, 2, 0.1);

    // Amplitude/Intensity
    createGlobalSliderControl('amplitude', 'Amplitude / Intensity', display.getGlobalSceneParameter('amplitude'), 0, 1, 0.05);

    // Detail Level
    createGlobalSliderControl('detailLevel', 'Detail Level', display.getGlobalSceneParameter('detailLevel'), 1, 5, 1);

    // Spacing/Offset
    createGlobalSliderControl('spacing', 'Spacing / Offset', display.getGlobalSceneParameter('spacing'), 0, 1, 0.05);

    // Direction
    createGlobalSelectControl('direction', 'Direction', display.getGlobalSceneParameter('direction'), [
        { value: 'radial', label: 'Radial' },
        { value: 'x', label: 'X' },
        { value: 'y', label: 'Y' },
        { value: 'z', label: 'Z' },
        { value: 'diagonal', label: 'Diagonal' },
        { value: 'random', label: 'Random' }
    ]);

    // Depth/Height
    createGlobalSliderControl('depth', 'Depth / Height', display.getGlobalSceneParameter('depth'), 0, 1, 0.05);

    // Inversion
    createGlobalCheckboxControl('inversion', 'Invert', display.getGlobalSceneParameter('inversion'));

    console.log('Global parameter controls created');
    updateActiveGlobalIndicators();
}

function createGlobalSliderControl(paramName, label, currentValue, min, max, step) {
    const group = document.createElement('div');
    group.className = 'control-group global-param';
    group.dataset.param = paramName;

    const labelEl = document.createElement('label');
    labelEl.innerHTML = `${label} <span class="value-display" id="global-param-${paramName}-value">${currentValue.toFixed(step >= 1 ? 0 : 2)}</span>`;
    group.appendChild(labelEl);

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.id = `global-param-${paramName}`;
    slider.min = min;
    slider.max = max;
    slider.step = step;
    slider.value = currentValue;

    slider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        display.setGlobalSceneParameter(paramName, val);
        document.getElementById(`global-param-${paramName}-value`).textContent = val.toFixed(step >= 1 ? 0 : 2);
    });

    group.appendChild(slider);
    globalParamsContainer.appendChild(group);
}

function createGlobalSelectControl(paramName, label, currentValue, options) {
    const group = document.createElement('div');
    group.className = 'control-group global-param';
    group.dataset.param = paramName;

    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    group.appendChild(labelEl);

    const select = document.createElement('select');
    select.className = 'param-select';
    select.id = `global-param-${paramName}`;

    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.value;
        option.textContent = opt.label;
        option.selected = opt.value === currentValue;
        select.appendChild(option);
    });

    select.addEventListener('change', (e) => {
        display.setGlobalSceneParameter(paramName, e.target.value);
    });

    group.appendChild(select);
    globalParamsContainer.appendChild(group);
}

function createGlobalCheckboxControl(paramName, label, currentValue) {
    const group = document.createElement('div');
    group.className = 'control-group global-param';
    group.dataset.param = paramName;

    const labelEl = document.createElement('label');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `global-param-${paramName}`;
    checkbox.checked = currentValue;

    checkbox.addEventListener('change', (e) => {
        display.setGlobalSceneParameter(paramName, e.target.checked);
    });

    labelEl.appendChild(checkbox);
    labelEl.appendChild(document.createTextNode(` ${label}`));
    group.appendChild(labelEl);
    globalParamsContainer.appendChild(group);
}

function updateActiveGlobalIndicators() {
    // Get which global params affect the current scene
    const activeParams = display.getActiveGlobalParameters();

    // Update visual indicators
    document.querySelectorAll('.global-param').forEach(el => {
        const paramName = el.dataset.param;
        if (activeParams.includes(paramName)) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}

// Initialize global parameter controls
createGlobalParameterControls();

// ============================================================================
// SCENE CONTROLS
// ============================================================================

// Generate scene type buttons
const sceneTypeContainer = document.getElementById('scene-type-container');
console.log('Scene type container:', sceneTypeContainer);

const sceneTypes = display.getSceneTypes();
console.log('Available scene types:', sceneTypes);

const sceneNames = {
    'shapeMorph': 'Shape Morph',
    'particleFlow': 'Particle Flow',
    'waveField': 'Wave Field',
    'procedural': 'Procedural',
    'vortex': 'Vortex',
    'grid': 'Grid',
    'text3D': 'Text 3D',
    'plasma': 'Plasma'
};

if (!sceneTypeContainer) {
    console.error('Scene type container not found!');
} else {
    sceneTypes.forEach((sceneType, index) => {
        const btn = document.createElement('button');
        btn.className = 'scene-type-btn' + (index === 0 ? ' active' : '');
        btn.dataset.sceneType = sceneType;
        btn.textContent = sceneNames[sceneType] || sceneType;

        btn.addEventListener('click', () => {
            console.log('Scene type clicked:', sceneType);
            document.querySelectorAll('.scene-type-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            display.setScene(sceneType);
            updateSceneControls(sceneType);
            updateActiveGlobalIndicators();
        });

        sceneTypeContainer.appendChild(btn);
        console.log('Added scene button:', sceneType);
    });
    console.log('Scene buttons created successfully');
}

// Scene parameter control generators
const sceneParamsContainer = document.getElementById('scene-params-container');

function updateSceneControls(sceneType) {
    console.log('updateSceneControls called for:', sceneType);
    sceneParamsContainer.innerHTML = '';
    const params = display.getCurrentSceneParams();
    console.log('Current scene params:', params);

    // Generate controls based on scene type
    if (sceneType === 'shapeMorph') {
        console.log('Creating Shape Morph controls');
        createShapeMorphControls(params);
    } else if (sceneType === 'particleFlow') {
        console.log('Creating Particle Flow controls');
        createParticleFlowControls(params);
    } else if (sceneType === 'waveField') {
        console.log('Creating Wave Field controls');
        createWaveFieldControls(params);
    } else if (sceneType === 'procedural') {
        console.log('Creating Procedural controls');
        createProceduralControls(params);
    } else if (sceneType === 'vortex') {
        console.log('Creating Vortex controls');
        createVortexControls(params);
    } else if (sceneType === 'grid') {
        console.log('Creating Grid controls');
        createGridControls(params);
    } else if (sceneType === 'text3D') {
        console.log('Creating Text 3D controls');
        createText3DControls(params);
    } else if (sceneType === 'plasma') {
        console.log('Creating Plasma controls');
        createPlasmaControls(params);
    }
    console.log('Scene controls created');
}

function createShapeMorphControls(params) {
    // Shape select (scene-specific)
    createSelectControl('shape', 'Shape', params.shape || 'sphere', [
        { value: 'sphere', label: 'Sphere' },
        { value: 'helix', label: 'Helix' },
        { value: 'torus', label: 'Torus' },
        { value: 'cube', label: 'Cube' },
        { value: 'pyramid', label: 'Pyramid' },
        { value: 'plane', label: 'Plane' }
    ]);

    // Note: size, thickness, objectCount, animation moved to global parameters
}

function createParticleFlowControls(params) {
    // Pattern select (scene-specific)
    createSelectControl('pattern', 'Pattern', params.pattern || 'rain', [
        { value: 'rain', label: 'Rain' },
        { value: 'stars', label: 'Stars' },
        { value: 'fountain', label: 'Fountain' },
        { value: 'spiral', label: 'Spiral' },
        { value: 'explode', label: 'Explode' }
    ]);

    // Note: particle size controlled by global "Size / Scale" parameter
    // Note: density, velocity (animationSpeed), and movement all moved to global parameters
}

function createWaveFieldControls(params) {
    // Wave type select (scene-specific)
    createSelectControl('waveType', 'Wave Type', params.waveType || 'ripple', [
        { value: 'ripple', label: 'Ripple' },
        { value: 'plane', label: 'Plane' },
        { value: 'standing', label: 'Standing' },
        { value: 'interference', label: 'Interference' }
    ]);

    // Note: frequency, amplitude, direction moved to global parameters
}

function createProceduralControls(params) {
    // Algorithm select (scene-specific)
    createSelectControl('algorithm', 'Algorithm', params.algorithm || 'perlin', [
        { value: 'perlin', label: 'Perlin' }
        // Future: simplex, cellular, voronoi, fractal
    ]);

    // Note: scale (size), threshold (amplitude), octaves (detailLevel), animationType, inversion moved to global parameters
}

function createVortexControls(params) {
    // Type select (scene-specific)
    createSelectControl('type', 'Type', params.type || 'tornado', [
        { value: 'tornado', label: 'Tornado' },
        { value: 'whirlpool', label: 'Whirlpool' },
        { value: 'galaxy', label: 'Galaxy' }
        // Note: 'double' removed - use objectCount=2 in global params instead
    ]);

    // Note: radius (amplitude), twist (animationSpeed), density, height (depth), objectCount moved to global parameters
}

function createGridControls(params) {
    // Pattern select (scene-specific)
    createSelectControl('pattern', 'Pattern', params.pattern || 'cube', [
        { value: 'cube', label: 'Cube' },
        { value: 'sphere', label: 'Sphere' },
        { value: 'tunnel', label: 'Tunnel' },
        { value: 'layers', label: 'Layers' }
    ]);

    // Note: spacing, thickness (density), offset moved to global parameters
}

function createText3DControls(params) {
    // Style select (scene-specific)
    createSelectControl('style', 'Style', params.style || 'block', [
        { value: 'block', label: 'Block' },
        { value: 'outline', label: 'Outline' }
    ]);

    // Text input (scene-specific)
    createTextControl('text', 'Text', params.text || 'HELLO');

    // Note: size, depth moved to global parameters
}

function createPlasmaControls(params) {
    // No scene-specific controls - everything uses global parameters
    // Note: scale (size), complexity (frequency), threshold (amplitude), layers (detailLevel) moved to global parameters

    const notice = document.createElement('div');
    notice.className = 'scene-notice';
    notice.textContent = 'All parameters controlled by global settings';
    notice.style.padding = '10px';
    notice.style.fontStyle = 'italic';
    notice.style.color = '#888';
    sceneParamsContainer.appendChild(notice);
}

// Helper functions to create controls
function createSelectControl(paramName, label, currentValue, options) {
    const group = document.createElement('div');
    group.className = 'control-group';

    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    group.appendChild(labelEl);

    const select = document.createElement('select');
    select.className = 'param-select';
    select.id = `scene-param-${paramName}`;

    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.value;
        option.textContent = opt.label;
        option.selected = opt.value === currentValue;
        select.appendChild(option);
    });

    select.addEventListener('change', (e) => {
        console.log(`Setting ${paramName} to ${e.target.value}`);
        display.setSceneParameter(paramName, e.target.value);
        console.log('Current scene params after change:', display.getCurrentSceneParams());
    });

    group.appendChild(select);
    sceneParamsContainer.appendChild(group);
}

function createSliderControl(paramName, label, currentValue, min, max, step) {
    const group = document.createElement('div');
    group.className = 'control-group';

    const labelEl = document.createElement('label');
    labelEl.innerHTML = `${label} <span class="value-display" id="scene-param-${paramName}-value">${currentValue.toFixed(step >= 1 ? 0 : 2)}</span>`;
    group.appendChild(labelEl);

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.id = `scene-param-${paramName}`;
    slider.min = min;
    slider.max = max;
    slider.step = step;
    slider.value = currentValue;

    slider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        display.setSceneParameter(paramName, val);
        document.getElementById(`scene-param-${paramName}-value`).textContent = val.toFixed(step >= 1 ? 0 : 2);
    });

    group.appendChild(slider);
    sceneParamsContainer.appendChild(group);
}

function createCheckboxControl(paramName, label, currentValue) {
    const group = document.createElement('div');
    group.className = 'control-group';

    const labelEl = document.createElement('label');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `scene-param-${paramName}`;
    checkbox.checked = currentValue;

    checkbox.addEventListener('change', (e) => {
        display.setSceneParameter(paramName, e.target.checked);
    });

    labelEl.appendChild(checkbox);
    labelEl.appendChild(document.createTextNode(` ${label}`));
    group.appendChild(labelEl);
    sceneParamsContainer.appendChild(group);
}

function createTextControl(paramName, label, currentValue) {
    const group = document.createElement('div');
    group.className = 'control-group';

    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    group.appendChild(labelEl);

    const input = document.createElement('input');
    input.type = 'text';
    input.id = `scene-param-${paramName}`;
    input.value = currentValue;
    input.maxLength = 10;
    input.style.width = '100%';
    input.style.padding = '6px';
    input.style.fontSize = '14px';
    input.style.marginTop = '5px';

    input.addEventListener('input', (e) => {
        const val = e.target.value.toUpperCase();
        display.setSceneParameter(paramName, val);
    });

    group.appendChild(input);
    sceneParamsContainer.appendChild(group);
}

// Initialize scene controls
console.log('Initializing scene controls for:', display.getCurrentSceneType());
updateSceneControls(display.getCurrentSceneType());
console.log('Scene controls initialized');

// ============================================================================
// ILLUSION SCENE CONTROLS
// ============================================================================

// Generate illusion scene buttons
const illusionSceneTypeContainer = document.getElementById('illusion-scene-type-container');
console.log('Illusion scene type container:', illusionSceneTypeContainer);

const illusionSceneTypes = display.getIllusionSceneTypes();
console.log('Available illusion scene types:', illusionSceneTypes);

const illusionSceneNames = {
    'rotatingAmes': 'Ames Room',
    'infiniteCorridor': 'Infinite Corridor',
    'kineticDepth': 'Kinetic Depth',
    'waterfallIllusion': 'Waterfall',
    'penroseTriangle': 'Penrose Tri',
    'neckerCube': 'Necker Cube',
    'fraserSpiral': 'Fraser Spiral',
    'cafeWall': 'Café Wall',
    'pulfrich': 'Pulfrich',
    'rotatingSnakes': 'Rotating Snakes',
    'breathingSquare': 'Breathing Square',
    'moirePattern': 'Moiré Pattern'
};

if (!illusionSceneTypeContainer) {
    console.error('Illusion scene type container not found!');
} else {
    illusionSceneTypes.forEach((sceneType) => {
        const btn = document.createElement('button');
        btn.className = 'scene-type-btn';
        btn.dataset.sceneType = sceneType;
        btn.textContent = illusionSceneNames[sceneType] || sceneType;

        btn.addEventListener('click', () => {
            console.log('Illusion scene type clicked:', sceneType);
            // Deactivate both regular and illusion scene buttons
            document.querySelectorAll('.scene-type-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            display.setScene(sceneType);
            updateSceneControls(sceneType);
            updateActiveGlobalIndicators();
        });

        illusionSceneTypeContainer.appendChild(btn);
        console.log('Added illusion scene button:', sceneType);
    });
    console.log('Illusion scene buttons created successfully');
}

// ============================================================================
// GLOBAL EFFECTS CONTROLS
// ============================================================================

// Animation speed control (display speed, not scene speed)
const animationSpeedSlider = document.getElementById('animation-speed');
const animationSpeedValue = document.getElementById('animation-speed-value');

animationSpeedSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    display.setDisplayParameter('speed', val);
    animationSpeedValue.textContent = val.toFixed(1);
});

// Decay control
const decaySlider = document.getElementById('decay');
const decayValue = document.getElementById('decay-value');

decaySlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    display.setDecay(val);
    decayValue.textContent = val.toFixed(2);
});

// Strobe controls
const strobeBtns = document.querySelectorAll('[id^="strobe-"]');
strobeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        strobeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.dataset.mode;
        display.setStrobe(mode);
    });
});

// Pulse controls
const pulseBtns = document.querySelectorAll('[id^="pulse-"]');
pulseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        pulseBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.dataset.mode;
        display.setPulse(mode);
    });
});

// Invert checkbox
const invertCheckbox = document.getElementById('invert-checkbox');
invertCheckbox.addEventListener('change', (e) => {
    display.setInvert(e.target.checked);
});

// ============================================================================
// DISPLAY PARAMETER CONTROLS
// ============================================================================

function setupGlobalControl(id, param, formatter = (v) => v) {
    const slider = document.getElementById(id);
    const valueDisplay = document.getElementById(`${id}-value`);

    slider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        display.setDisplayParameter(param, val);
        valueDisplay.textContent = formatter(val);
    });
}

setupGlobalControl('led-size', 'ledSize', v => v.toFixed(1));
setupGlobalControl('brightness', 'brightness', v => v.toFixed(2));
setupGlobalControl('grid-opacity', 'gridOpacity', v => v.toFixed(2));

// ============================================================================
// VIEW CONTROLS
// ============================================================================

const toggleRotateBtn = document.getElementById('toggle-rotate');
toggleRotateBtn.addEventListener('click', () => {
    const isRotating = display.renderer.toggleAutoRotate();
    toggleRotateBtn.classList.toggle('active', isRotating);
});

const toggleAxesBtn = document.getElementById('toggle-axes');
toggleAxesBtn.addEventListener('click', () => {
    const showingAxes = display.renderer.toggleAxes();
    toggleAxesBtn.classList.toggle('active', showingAxes);
});

document.getElementById('reset-view').addEventListener('click', () => {
    display.renderer.resetView();
});

// Rotation rate controls
function setupRotationControl(id, axis) {
    const input = document.getElementById(id);

    input.addEventListener('change', (e) => {
        const val = parseFloat(e.target.value) || 0;
        const clamped = Math.max(-20, Math.min(20, val));
        input.value = clamped;

        const rate = clamped / 1000;

        const currentRates = display.renderer.rotationRate;
        if (axis === 'x') {
            display.renderer.setRotationRate(rate, currentRates.y, currentRates.z);
        } else if (axis === 'y') {
            display.renderer.setRotationRate(currentRates.x, rate, currentRates.z);
        } else if (axis === 'z') {
            display.renderer.setRotationRate(currentRates.x, currentRates.y, rate);
        }
    });
}

setupRotationControl('rot-x', 'x');
setupRotationControl('rot-y', 'y');
setupRotationControl('rot-z', 'z');

// Reset view point controls
document.getElementById('reset-x').addEventListener('change', (e) => {
    const val = parseFloat(e.target.value) || 0;
    display.renderer.defaultRotation.x = val;
});

document.getElementById('reset-y').addEventListener('change', (e) => {
    const val = parseFloat(e.target.value) || 0;
    display.renderer.defaultRotation.y = val;
});

// ============================================================================
// COLLAPSIBLE SECTIONS
// ============================================================================

console.log('Setting up collapsible sections...');

const collapsibleSections = [
    { header: 'led-colors-header', content: 'led-colors-content' },
    { header: 'scenes-header', content: 'scenes-content' },
    { header: 'illusion-scenes-header', content: 'illusion-scenes-content' },
    { header: 'controls-header', content: 'controls-content' }
];

collapsibleSections.forEach(({ header, content }) => {
    const headerEl = document.getElementById(header);
    const contentEl = document.getElementById(content);

    console.log(`Setting up ${header}:`, headerEl ? 'found' : 'NOT FOUND');
    console.log(`Setting up ${content}:`, contentEl ? 'found' : 'NOT FOUND');

    if (headerEl && contentEl) {
        headerEl.addEventListener('click', () => {
            console.log(`Toggling ${header}`);
            headerEl.classList.toggle('active');
            contentEl.classList.toggle('active');
        });
    } else {
        console.error(`Missing element for ${header} or ${content}`);
    }
});

console.log('Collapsible sections setup complete');

// ============================================================================
// DISPLAY PARAMETERS COLLAPSIBLE
// ============================================================================

const displayParamsHeader = document.getElementById('display-params-header');
const displayParamsContent = document.getElementById('display-params-content');

if (displayParamsHeader && displayParamsContent) {
    displayParamsHeader.addEventListener('click', () => {
        console.log('Toggling display parameters');
        displayParamsHeader.classList.toggle('collapsed');
        displayParamsContent.classList.toggle('collapsed');
    });
    console.log('Display parameters collapsible setup complete');
} else {
    console.error('Display parameters elements not found');
}

// ============================================================================
// PERFORMANCE MONITORING
// ============================================================================

let frameTimeSum = 0;
let frameCount = 0;
let lastFrameTime = performance.now();

function updateDebugStats() {
    // Update scene info
    const sceneEl = document.getElementById('debug-scene');
    if (sceneEl) {
        sceneEl.textContent = display.getCurrentSceneType();
    }

    // Update active LEDs count
    const activeLEDsEl = document.getElementById('debug-active-leds');
    if (activeLEDsEl) {
        activeLEDsEl.textContent = currentActiveLEDs.toLocaleString();
    }

    // Update global effects status
    const fxEl = document.getElementById('debug-fx');
    if (fxEl) {
        const effects = [];
        if (display.globalEffects.decay > 0) effects.push(`Decay:${display.globalEffects.decay.toFixed(2)}`);
        if (display.globalEffects.strobe !== 'off') effects.push(`Strobe:${display.globalEffects.strobe}`);
        if (display.globalEffects.pulse !== 'off') effects.push(`Pulse:${display.globalEffects.pulse}`);
        if (display.globalEffects.invert) effects.push('Invert');
        fxEl.textContent = effects.length > 0 ? effects.join(', ') : 'None';
    }

    // Update frame time
    const now = performance.now();
    const frameTime = now - lastFrameTime;
    lastFrameTime = now;

    frameTimeSum += frameTime;
    frameCount++;

    if (frameCount >= 30) {
        const avgFrameTime = frameTimeSum / frameCount;
        const frameTimeEl = document.getElementById('debug-frame-time');
        if (frameTimeEl) {
            frameTimeEl.textContent = `${avgFrameTime.toFixed(2)}ms (${(1000/avgFrameTime).toFixed(1)} FPS)`;
        }
        frameTimeSum = 0;
        frameCount = 0;
    }
}

// Update debug stats every frame
setInterval(updateDebugStats, 100);

// ============================================================================
// PARAMETER AUTOMATION CONTROLS
// ============================================================================

let currentAutomationParam = null;

// Modal controls
const automationModal = document.getElementById('automation-modal');
const automationModalClose = document.getElementById('automation-modal-close');
const automationCancel = document.getElementById('automation-cancel');
const automationApply = document.getElementById('automation-apply');
const automationRemove = document.getElementById('automation-remove');
const automationClearAll = document.getElementById('automation-clear-all');

// Modal inputs
const automationWaveType = document.getElementById('automation-wave-type');
const automationFrequency = document.getElementById('automation-frequency');
const automationAmplitude = document.getElementById('automation-amplitude');
const automationPhase = document.getElementById('automation-phase');
const automationFrequencyValue = document.getElementById('automation-frequency-value');
const automationAmplitudeValue = document.getElementById('automation-amplitude-value');
const automationPhaseValue = document.getElementById('automation-phase-value');

// Update value displays
automationFrequency.addEventListener('input', (e) => {
    automationFrequencyValue.textContent = parseFloat(e.target.value).toFixed(1);
});

automationAmplitude.addEventListener('input', (e) => {
    automationAmplitudeValue.textContent = parseFloat(e.target.value).toFixed(2);
});

automationPhase.addEventListener('input', (e) => {
    automationPhaseValue.textContent = parseFloat(e.target.value).toFixed(2);
});

// Close modal
automationModalClose.addEventListener('click', () => {
    automationModal.style.display = 'none';
});

automationCancel.addEventListener('click', () => {
    automationModal.style.display = 'none';
});

// Apply automation
automationApply.addEventListener('click', () => {
    if (!currentAutomationParam) return;

    const config = {
        waveType: automationWaveType.value,
        frequency: parseFloat(automationFrequency.value),
        amplitude: parseFloat(automationAmplitude.value),
        phase: parseFloat(automationPhase.value),
        min: parseFloat(currentAutomationParam.slider.min),
        max: parseFloat(currentAutomationParam.slider.max),
        baseValue: parseFloat(currentAutomationParam.slider.value),
        enabled: true
    };

    display.parameterAutomation.setAutomation(currentAutomationParam.id, config);
    currentAutomationParam.slider.classList.add('automated');
    automationModal.style.display = 'none';
    updateActiveAutomationsList();
    console.log(`Automation applied to ${currentAutomationParam.id}`);
});

// Remove automation
automationRemove.addEventListener('click', () => {
    if (!currentAutomationParam) return;

    display.parameterAutomation.removeAutomation(currentAutomationParam.id);
    currentAutomationParam.slider.classList.remove('automated');
    automationModal.style.display = 'none';
    updateActiveAutomationsList();
    console.log(`Automation removed from ${currentAutomationParam.id}`);
});

// Clear all automations
automationClearAll.addEventListener('click', () => {
    display.parameterAutomation.clear();
    document.querySelectorAll('input[type="range"].automated').forEach(slider => {
        slider.classList.remove('automated');
    });
    updateActiveAutomationsList();
    console.log('All automations cleared');
});

// Add right-click handlers to all range sliders
function setupAutomationForSliders() {
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        slider.addEventListener('contextmenu', (e) => {
            e.preventDefault();

            // Get parameter info
            const paramId = slider.id;
            const paramName = paramId.replace('scene-param-', '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

            currentAutomationParam = {
                id: paramId,
                name: paramName,
                slider: slider
            };

            // Check if already automated
            const existing = display.parameterAutomation.getAutomation(paramId);
            if (existing) {
                automationWaveType.value = existing.waveType;
                automationFrequency.value = existing.frequency;
                automationAmplitude.value = existing.amplitude;
                automationPhase.value = existing.phase;
                automationFrequencyValue.textContent = existing.frequency.toFixed(1);
                automationAmplitudeValue.textContent = existing.amplitude.toFixed(2);
                automationPhaseValue.textContent = existing.phase.toFixed(2);
            } else {
                // Defaults
                automationWaveType.value = 'sine';
                automationFrequency.value = 1.0;
                automationAmplitude.value = 0.5;
                automationPhase.value = 0;
                automationFrequencyValue.textContent = '1.0';
                automationAmplitudeValue.textContent = '0.50';
                automationPhaseValue.textContent = '0.00';
            }

            document.getElementById('automation-param-name').textContent = `Parameter: ${paramName}`;
            automationModal.style.display = 'flex';
        });
    });
}

// Update active automations list
function updateActiveAutomationsList() {
    const listContainer = document.getElementById('active-automations-list');
    const automations = display.parameterAutomation.getAllAutomations();

    if (automations.length === 0) {
        listContainer.innerHTML = '<div class="automation-item-empty">No active automations</div>';
        return;
    }

    listContainer.innerHTML = automations.map(auto => {
        const paramName = auto.id.replace('scene-param-', '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        return `
            <div class="automation-item">
                <span class="automation-param-name">${paramName}</span>
                <span class="automation-wave-type">${auto.waveType}</span>
                <span class="automation-frequency">${auto.frequency.toFixed(1)}Hz</span>
                <button class="automation-toggle" data-id="${auto.id}">${auto.enabled ? '⏸' : '▶'}</button>
            </div>
        `;
    }).join('');

    // Add toggle handlers
    listContainer.querySelectorAll('.automation-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const paramId = btn.dataset.id;
            const enabled = display.parameterAutomation.toggleAutomation(paramId);
            btn.textContent = enabled ? '⏸' : '▶';
        });
    });
}

// Initialize automation UI
setupAutomationForSliders();
updateActiveAutomationsList();

// Collapsible automation section
const automationHeader = document.getElementById('automation-header');
const automationContent = document.getElementById('automation-content');

if (automationHeader && automationContent) {
    automationHeader.addEventListener('click', () => {
        automationHeader.classList.toggle('active');
        automationContent.classList.toggle('active');
    });
}

// ============================================================================
// 3D GRADIENT MAPPING CONTROLS
// ============================================================================

const gradient3dEnable = document.getElementById('gradient-3d-enable');
const gradient3dControls = document.getElementById('gradient-3d-controls');
const gradient3dType = document.getElementById('gradient-3d-type');
const gradient3dOriginX = document.getElementById('gradient-3d-origin-x');
const gradient3dOriginY = document.getElementById('gradient-3d-origin-y');
const gradient3dOriginZ = document.getElementById('gradient-3d-origin-z');
const gradient3dFalloff = document.getElementById('gradient-3d-falloff');
const gradient3dInvert = document.getElementById('gradient-3d-invert');

// Toggle 3D gradient mapping
gradient3dEnable.addEventListener('change', (e) => {
    const enabled = e.target.checked;
    display.renderer.colorMapper3D.setEnabled(enabled);
    gradient3dControls.style.display = enabled ? 'block' : 'none';
    console.log(`3D Gradient Mapping: ${enabled ? 'ON' : 'OFF'}`);
});

// Gradient type
gradient3dType.addEventListener('change', (e) => {
    display.renderer.colorMapper3D.setGradientType(e.target.value);
    console.log(`3D Gradient Type: ${e.target.value}`);
});

// Origin controls
gradient3dOriginX.addEventListener('input', (e) => {
    const x = parseFloat(e.target.value);
    const y = parseFloat(gradient3dOriginY.value);
    const z = parseFloat(gradient3dOriginZ.value);
    display.renderer.colorMapper3D.setOrigin(x, y, z);
    document.getElementById('gradient-3d-origin-x-value').textContent = x.toFixed(2);
});

gradient3dOriginY.addEventListener('input', (e) => {
    const x = parseFloat(gradient3dOriginX.value);
    const y = parseFloat(e.target.value);
    const z = parseFloat(gradient3dOriginZ.value);
    display.renderer.colorMapper3D.setOrigin(x, y, z);
    document.getElementById('gradient-3d-origin-y-value').textContent = y.toFixed(2);
});

gradient3dOriginZ.addEventListener('input', (e) => {
    const x = parseFloat(gradient3dOriginX.value);
    const y = parseFloat(gradient3dOriginY.value);
    const z = parseFloat(e.target.value);
    display.renderer.colorMapper3D.setOrigin(x, y, z);
    document.getElementById('gradient-3d-origin-z-value').textContent = z.toFixed(2);
});

// Falloff
gradient3dFalloff.addEventListener('change', (e) => {
    display.renderer.colorMapper3D.setFalloff(e.target.value);
    console.log(`3D Gradient Falloff: ${e.target.value}`);
});

// Invert
gradient3dInvert.addEventListener('change', (e) => {
    display.renderer.colorMapper3D.setInvert(e.target.checked);
});

// Initialize 3D gradient with current gradient colors
function sync3DGradientColors() {
    const stops = display.renderer.gradientColors.map((color, index) => ({
        position: index / (display.renderer.gradientColors.length - 1),
        color: color
    }));
    display.renderer.colorMapper3D.setColorStops(stops);
}

// Sync on gradient change
const applyGradientBtn = document.getElementById('apply-gradient');
const originalApplyGradient = applyGradientBtn.onclick;
applyGradientBtn.addEventListener('click', () => {
    setTimeout(sync3DGradientColors, 10); // Sync after gradient is applied
});

// Sync preset gradients too
document.querySelectorAll('.color-preset-btn[data-type="gradient"]').forEach(btn => {
    btn.addEventListener('click', () => {
        setTimeout(sync3DGradientColors, 10);
    });
});

sync3DGradientColors(); // Initial sync

// ============================================================================
// ADVANCED COLOR EFFECTS CONTROLS
// ============================================================================

const advancedEffectBtns = document.querySelectorAll('.advanced-effect-btn');
const advancedEffectIntensity = document.getElementById('advanced-effect-intensity');
const advancedEffectIntensityValue = document.getElementById('advanced-effect-intensity-value');

advancedEffectBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        advancedEffectBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const effect = btn.dataset.effect;
        display.renderer.colorEffects.setEffect(effect);
        console.log(`Advanced Color Effect: ${effect}`);
    });
});

advancedEffectIntensity.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    display.renderer.colorEffects.setIntensity(val);
    advancedEffectIntensityValue.textContent = val.toFixed(2);
});

// Advanced effect speed control
const advancedEffectSpeed = document.getElementById('advanced-effect-speed');
const advancedEffectSpeedValue = document.getElementById('advanced-effect-speed-value');

if (advancedEffectSpeed) {
    advancedEffectSpeed.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        display.renderer.colorEffects.setSpeed(val);
        advancedEffectSpeedValue.textContent = val.toFixed(1);
    });
}

// Color mode toggle
const colorModeButtons = document.querySelectorAll('[id^="color-mode-"]');
colorModeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        colorModeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.dataset.mode;
        display.renderer.colorEffects.setColorMode(mode);
        console.log(`Color Mode: ${mode}`);
    });
});

// Scrolling effect parameters
const scrollThickness = document.getElementById('scroll-thickness');
const scrollThicknessValue = document.getElementById('scroll-thickness-value');
const scrollDirection = document.getElementById('scroll-direction');

if (scrollThickness) {
    scrollThickness.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        display.renderer.colorEffects.setScrollThickness(val);
        scrollThicknessValue.textContent = val.toFixed(0);
    });
}

if (scrollDirection) {
    scrollDirection.addEventListener('change', (e) => {
        display.renderer.colorEffects.setScrollDirection(e.target.value);
        console.log(`Scroll Direction: ${e.target.value}`);
    });
}

const scrollInvert = document.getElementById('scroll-invert');
if (scrollInvert) {
    scrollInvert.addEventListener('change', (e) => {
        display.renderer.colorEffects.setScrollInvert(e.target.checked);
        console.log(`Scroll Invert: ${e.target.checked ? 'ON (pixels turn OFF)' : 'OFF (pixels turn ON)'}`);
    });
}

// ============================================================================
// START DISPLAY
// ============================================================================

console.log('Starting volumetric display...');
display.start();
console.log('Application initialization complete!');

// Log initial performance baseline
setTimeout(() => {
    console.log('Performance baseline established');
}, 2000);
