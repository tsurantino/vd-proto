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
    'procedural': 'Procedural'
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
    }
    console.log('Scene controls created');
}

function createShapeMorphControls(params) {
    // Shape select
    createSelectControl('shape', 'Shape', params.shape, [
        { value: 'sphere', label: 'Sphere' },
        { value: 'helix', label: 'Helix' },
        { value: 'torus', label: 'Torus' },
        { value: 'cube', label: 'Cube' },
        { value: 'pyramid', label: 'Pyramid' },
        { value: 'plane', label: 'Plane' }
    ]);

    // Animation type
    createSelectControl('animation', 'Animation', params.animation, [
        { value: 'pulse', label: 'Pulse' },
        { value: 'rotate', label: 'Rotate' },
        { value: 'breathe', label: 'Breathe' },
        { value: 'morph', label: 'Morph' }
    ]);

    // Numeric controls
    createSliderControl('size', 'Size', params.size, 0.5, 3, 0.1);
    createSliderControl('thickness', 'Thickness', params.thickness, 0.1, 1, 0.1);
    createSliderControl('speed', 'Speed', params.speed, 0.1, 10, 0.1);
    createSliderControl('objectCount', 'Object Count', params.objectCount, 1, 4, 1);
}

function createParticleFlowControls(params) {
    // Pattern select
    createSelectControl('pattern', 'Pattern', params.pattern, [
        { value: 'rain', label: 'Rain' },
        { value: 'stars', label: 'Stars' },
        { value: 'fountain', label: 'Fountain' },
        { value: 'spiral', label: 'Spiral' },
        { value: 'explode', label: 'Explode' }
    ]);

    // Numeric controls
    createSliderControl('density', 'Density', params.density, 0.05, 1, 0.05);
    createSliderControl('velocity', 'Velocity', params.velocity, 0.5, 3, 0.1);
    createSliderControl('speed', 'Speed', params.speed, 0.1, 10, 0.1);
    createSliderControl('turbulence', 'Turbulence', params.turbulence, 0, 1, 0.05);
    createSliderControl('trailLength', 'Trail Length', params.trailLength, 0, 5, 1);
}

function createWaveFieldControls(params) {
    // Wave type select
    createSelectControl('waveType', 'Wave Type', params.waveType, [
        { value: 'ripple', label: 'Ripple' },
        { value: 'plane', label: 'Plane' },
        { value: 'standing', label: 'Standing' },
        { value: 'interference', label: 'Interference' }
    ]);

    // Direction select
    createSelectControl('direction', 'Direction', params.direction, [
        { value: 'radial', label: 'Radial' },
        { value: 'x', label: 'X' },
        { value: 'y', label: 'Y' },
        { value: 'z', label: 'Z' },
        { value: 'diagonal', label: 'Diagonal' }
    ]);

    // Numeric controls
    createSliderControl('frequency', 'Frequency', params.frequency, 0.1, 2, 0.1);
    createSliderControl('amplitude', 'Amplitude', params.amplitude, 0.5, 3, 0.1);
    createSliderControl('speed', 'Speed', params.speed, 0.1, 10, 0.1);
}

function createProceduralControls(params) {
    // Algorithm select
    createSelectControl('algorithm', 'Algorithm', params.algorithm, [
        { value: 'perlin', label: 'Perlin' }
        // Future: simplex, cellular, voronoi, fractal
    ]);

    // Animation type select
    createSelectControl('animationType', 'Animation', params.animationType, [
        { value: 'scroll', label: 'Scroll' },
        { value: 'evolve', label: 'Evolve' },
        { value: 'morph', label: 'Morph' },
        { value: 'none', label: 'Static' }
    ]);

    // Numeric controls
    createSliderControl('scale', 'Scale', params.scale, 0.05, 0.5, 0.01);
    createSliderControl('threshold', 'Threshold', params.threshold, 0, 0.8, 0.05);
    createSliderControl('octaves', 'Octaves', params.octaves, 1, 5, 1);
    createSliderControl('speed', 'Speed', params.speed, 0.1, 10, 0.1);

    // Inversion checkbox
    createCheckboxControl('inversion', 'Invert', params.inversion);
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
        display.setSceneParameter(paramName, e.target.value);
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

// Initialize scene controls
console.log('Initializing scene controls for:', display.getCurrentSceneType());
updateSceneControls(display.getCurrentSceneType());
console.log('Scene controls initialized');

// ============================================================================
// GLOBAL EFFECTS CONTROLS
// ============================================================================

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
        display.setGlobalParameter(param, val);
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
// START DISPLAY
// ============================================================================

console.log('Starting volumetric display...');
display.start();
console.log('Application initialization complete!');

// Log initial performance baseline
setTimeout(() => {
    console.log('Performance baseline established');
}, 2000);
