/**
 * Main Application Entry Point
 * Initializes the volumetric display and UI controls
 */
import { VolumetricDisplay } from './VolumetricDisplay.js';

// Initialize the display (gridX, gridY, gridZ) = (40, 20, 40)
const display = new VolumetricDisplay('canvas', 40, 20, 40);

// Get grid info and display
const gridInfo = display.getGridInfo();
document.getElementById('grid-resolution').textContent = `Resolution: ${gridInfo.x}×${gridInfo.y}×${gridInfo.z}`;
document.getElementById('total-leds').textContent = `Total LEDs: ${gridInfo.total.toLocaleString()}`;

// Set up callbacks
display.setFPSCallback((fps) => {
    document.getElementById('fps').textContent = `FPS: ${fps}`;
});

display.setActiveLEDsCallback((count) => {
    document.getElementById('active-leds').textContent = `Active LEDs: ${count}`;
});

// Update camera view display
function updateCameraView() {
    const rx = display.renderer.rotation.x.toFixed(1);
    const ry = display.renderer.rotation.y.toFixed(1);
    document.getElementById('camera-view').textContent = `Camera: (${rx}, ${ry}, 0.0)`;
}

setInterval(updateCameraView, 100);

// Set up LED color preset buttons
const colorPresetBtns = document.querySelectorAll('.color-preset-btn');
colorPresetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all color preset buttons
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

// Set up custom single color
document.getElementById('apply-single-color').addEventListener('click', () => {
    const color = document.getElementById('custom-single-color').value;
    display.renderer.setSingleColor(color);

    // Remove active class from preset buttons
    colorPresetBtns.forEach(b => b.classList.remove('active'));
});

// Set up custom gradient
document.getElementById('apply-gradient').addEventListener('click', () => {
    const startColor = document.getElementById('custom-gradient-start').value;
    const endColor = document.getElementById('custom-gradient-end').value;
    display.renderer.setGradientColors([startColor, endColor]);

    // Remove active class from preset buttons
    colorPresetBtns.forEach(b => b.classList.remove('active'));
});

// Set up color effect buttons
const colorEffectBtns = document.querySelectorAll('.color-effect-btn');
colorEffectBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all color effect buttons
        colorEffectBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const effect = btn.dataset.effect;
        display.renderer.setColorEffect(effect);
    });
});

// Set up color effect speed control
const colorEffectSpeedSlider = document.getElementById('color-effect-speed');
const colorEffectSpeedValue = document.getElementById('color-effect-speed-value');

colorEffectSpeedSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    display.renderer.setColorEffectSpeed(val);
    colorEffectSpeedValue.textContent = val.toFixed(1);
});

// Generate effect buttons
const effectsContainer = document.getElementById('effects-container');
const effectNames = display.getEffectNames();

effectNames.forEach((name, index) => {
    const btn = document.createElement('button');
    btn.className = 'effect-btn' + (index === 0 ? ' active' : '');
    btn.dataset.effect = index;
    btn.textContent = name;

    btn.addEventListener('click', () => {
        document.querySelectorAll('.effect-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        display.setEffect(index);
    });

    effectsContainer.appendChild(btn);
});

// Set up parameter controls
function setupControl(id, param, formatter = (v) => v) {
    const slider = document.getElementById(id);
    const valueDisplay = document.getElementById(`${id}-value`);

    slider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        display.setParameter(param, val);
        valueDisplay.textContent = formatter(val);
    });
}

setupControl('speed', 'speed', v => v.toFixed(1));
setupControl('density', 'density', v => v.toFixed(2));
setupControl('led-size', 'ledSize', v => v.toFixed(1));
setupControl('brightness', 'brightness', v => v.toFixed(2));
setupControl('grid-opacity', 'gridOpacity', v => v.toFixed(2));

// Set up view control buttons
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

// Set up rotation rate controls (now text inputs)
function setupRotationControl(id, axis) {
    const input = document.getElementById(id);

    input.addEventListener('change', (e) => {
        const val = parseFloat(e.target.value) || 0;
        // Clamp value
        const clamped = Math.max(-20, Math.min(20, val));
        input.value = clamped;

        // Convert to rotation rate (divide by 1000 for smooth rotation)
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

// Set up reset view point controls
document.getElementById('reset-x').addEventListener('change', (e) => {
    const val = parseFloat(e.target.value) || 0;
    display.renderer.defaultRotation.x = val;
});

document.getElementById('reset-y').addEventListener('change', (e) => {
    const val = parseFloat(e.target.value) || 0;
    display.renderer.defaultRotation.y = val;
});

// Set up collapsible sections
const ledColorsHeader = document.getElementById('led-colors-header');
const ledColorsContent = document.getElementById('led-colors-content');

ledColorsHeader.addEventListener('click', () => {
    ledColorsHeader.classList.toggle('active');
    ledColorsContent.classList.toggle('active');
});

const effectsHeader = document.getElementById('effects-header');
const effectsContent = document.getElementById('effects-content');

effectsHeader.addEventListener('click', () => {
    effectsHeader.classList.toggle('active');
    effectsContent.classList.toggle('active');
});

const controlsHeader = document.getElementById('controls-header');
const controlsContent = document.getElementById('controls-content');

controlsHeader.addEventListener('click', () => {
    controlsHeader.classList.toggle('active');
    controlsContent.classList.toggle('active');
});

const paramsHeader = document.getElementById('params-header');
const paramsContent = document.getElementById('params-content');

paramsHeader.addEventListener('click', () => {
    paramsHeader.classList.toggle('active');
    paramsContent.classList.toggle('active');
});

const displayHeader = document.getElementById('display-header');
const displayContent = document.getElementById('display-content');

displayHeader.addEventListener('click', () => {
    displayHeader.classList.toggle('active');
    displayContent.classList.toggle('active');
});

// Start the display
display.start();
