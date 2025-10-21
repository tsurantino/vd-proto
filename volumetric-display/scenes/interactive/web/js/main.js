import { sceneConfig } from './config/scenes.js';
import { SocketManager } from './core/socket.js';
import { ParamsManager } from './core/params.js';
import { SessionMemory } from './core/session.js';
import { setupSlider, setupScrollingThickness, updateCopySectionVisibility } from './ui/sliders.js';
import { setupButtonGroup, setupToggleButton, setupEffectButtons } from './ui/buttons.js';
import { setupSubtabs } from './ui/tabs.js';
import { setupColorPresets, setupColorEffectButtons } from './ui/colors.js';
import { setupSceneSelection, initializeScene } from './ui/scenes.js';

// Initialize systems
const socketManager = new SocketManager();
const paramsManager = new ParamsManager();
const sessionMemory = new SessionMemory();

// Setup all sliders
setupSlider('size', 'size', 2, paramsManager, socketManager, sessionMemory);
setupSlider('density', 'density', 2, paramsManager, socketManager, sessionMemory);
setupSlider('animationSpeed', 'animationSpeed', 2, paramsManager, socketManager, sessionMemory);
setupSlider('frequency', 'frequency', 2, paramsManager, socketManager, sessionMemory);
setupSlider('amplitude', 'amplitude', 2, paramsManager, socketManager, sessionMemory);
setupSlider('objectCount', 'objectCount', 0, paramsManager, socketManager, sessionMemory);
setupSlider('scaling_amount', 'scaling_amount', 2, paramsManager, socketManager, sessionMemory);
setupSlider('scaling_speed', 'scaling_speed', 2, paramsManager, socketManager, sessionMemory);
setupSlider('rotationX', 'rotationX', 2, paramsManager, socketManager, sessionMemory);
setupSlider('rotationY', 'rotationY', 2, paramsManager, socketManager, sessionMemory);
setupSlider('rotationZ', 'rotationZ', 2, paramsManager, socketManager, sessionMemory);
setupSlider('rotation_speed', 'rotation_speed', 1, paramsManager, socketManager, sessionMemory);
setupSlider('rotation_offset', 'rotation_offset', 2, paramsManager, socketManager, sessionMemory);
setupSlider('decay', 'decay', 2, paramsManager, socketManager, sessionMemory);
setupSlider('color-speed', 'color_speed', 2, paramsManager, socketManager, sessionMemory);
setupSlider('color-effect-intensity', 'color_effect_intensity', 2, paramsManager, socketManager, sessionMemory);
setupSlider('copy_spacing', 'copy_spacing', 2, paramsManager, socketManager, sessionMemory);
setupSlider('copy_scale_offset', 'copy_scale_offset', 2, paramsManager, socketManager, sessionMemory);
setupSlider('copy_rotation_var', 'copy_rotation_var', 2, paramsManager, socketManager, sessionMemory);
setupSlider('copy_translation_var', 'copy_translation_var', 2, paramsManager, socketManager, sessionMemory);
setupSlider('copy_translation_x', 'copy_translation_x', 2, paramsManager, socketManager, sessionMemory);
setupSlider('copy_translation_y', 'copy_translation_y', 2, paramsManager, socketManager, sessionMemory);
setupSlider('copy_translation_z', 'copy_translation_z', 2, paramsManager, socketManager, sessionMemory);
setupSlider('copy_translation_speed', 'copy_translation_speed', 1, paramsManager, socketManager, sessionMemory);
setupSlider('copy_translation_offset', 'copy_translation_offset', 2, paramsManager, socketManager, sessionMemory);
setupSlider('object_scroll_speed', 'object_scroll_speed', 1, paramsManager, socketManager, sessionMemory);

// Special sliders
setupScrollingThickness(paramsManager, socketManager);

// Mask scrolling speed slider
const maskScrollSpeedSlider = document.getElementById('mask_scrolling_speed');
const maskScrollSpeedDisplay = document.getElementById('mask_scrolling_speed-value');
maskScrollSpeedSlider.addEventListener('input', (e) => {
    const value = parseFloat(e.target.value);
    maskScrollSpeedDisplay.textContent = value.toFixed(1);
    paramsManager.params.scrolling_speed = value;
    socketManager.sendParams(paramsManager.params);
});

// Setup button groups for scene-specific parameters
setupButtonGroup('[data-param="shape"]', 'shape', paramsManager, socketManager);
setupButtonGroup('[data-param="waveType"]', 'waveType', paramsManager, socketManager);
setupButtonGroup('[data-param="pattern"]', 'pattern', paramsManager, socketManager);
setupButtonGroup('[data-param="illusionType"]', 'illusionType', paramsManager, socketManager);
setupButtonGroup('[data-param="proceduralType"]', 'proceduralType', paramsManager, socketManager);
setupButtonGroup('[data-param="gridPattern"]', 'gridPattern', paramsManager, socketManager);
setupButtonGroup('[data-param="copy_arrangement"]', 'copy_arrangement', paramsManager, socketManager);
setupButtonGroup('[data-param="mask_scrolling_direction"]', 'scrolling_direction', paramsManager, socketManager);
setupButtonGroup('[data-param="object_scroll_direction"]', 'object_scroll_direction', paramsManager, socketManager);

// Setup toggle buttons
setupToggleButton('invert', 'invert', paramsManager, socketManager);
setupToggleButton('scrolling_loop', 'scrolling_loop', paramsManager, socketManager);
setupToggleButton('scrolling_invert_mask', 'scrolling_invert_mask', paramsManager, socketManager);

// Setup UI components
setupSubtabs();
setupColorPresets(paramsManager, socketManager);
setupColorEffectButtons(paramsManager, socketManager);
setupEffectButtons(paramsManager, socketManager);

// Setup scene selection
setupSceneSelection(paramsManager, socketManager, sessionMemory, sceneConfig);

// Setup copy section visibility handler
document.getElementById('objectCount').addEventListener('input', updateCopySectionVisibility);
updateCopySectionVisibility();

// Initialize scene on page load
function initialize() {
    initializeScene(paramsManager, sceneConfig);
    console.log('Controller UI loaded');
}

// Call initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// Send initial params on connection
socketManager.socket.on('connect', () => {
    socketManager.sendParams(paramsManager.params);
});
