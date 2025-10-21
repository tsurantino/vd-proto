import { updateTabStates, switchToValidTab } from './tabs.js';

// Update scene-specific controls visibility
export function updateSceneParams(sceneType) {
    document.getElementById('shape-control').style.display =
        sceneType === 'shapeMorph' ? 'block' : 'none';
    document.getElementById('waveType-control').style.display =
        sceneType === 'waveField' ? 'block' : 'none';
    document.getElementById('pattern-control').style.display =
        sceneType === 'particleFlow' ? 'block' : 'none';
    document.getElementById('illusionType-control').style.display =
        sceneType === 'illusions' ? 'block' : 'none';
    document.getElementById('proceduralType-control').style.display =
        sceneType === 'procedural' ? 'block' : 'none';
    document.getElementById('gridPattern-control').style.display =
        sceneType === 'grid' ? 'block' : 'none';
}

// Save current scene parameters to session memory
export function saveCurrentSceneParams(paramsManager, sessionMemory, sceneConfig) {
    const sceneType = paramsManager.params.scene_type;
    const config = sceneConfig[sceneType];
    if (!config) return;

    sessionMemory.memory[sceneType] = {};
    config.enabled.forEach(paramName => {
        sessionMemory.memory[sceneType][paramName] = paramsManager.params[paramName];
    });
}

// Load scene parameters (from session memory or defaults)
export function loadSceneParams(sceneType, paramsManager, sessionMemory, sceneConfig) {
    const config = sceneConfig[sceneType];
    if (!config) return;

    // Check if we have user-modified values for this scene
    const savedParams = sessionMemory.load(sceneType);

    config.enabled.forEach(paramName => {
        let value;

        if (savedParams && savedParams[paramName] !== undefined) {
            // Use saved user value
            value = savedParams[paramName];
        } else {
            // Use smart default
            value = config.defaults[paramName];
        }

        // Update params object
        paramsManager.params[paramName] = value;

        // Update slider UI
        const slider = document.getElementById(paramName);
        const valueDisplay = document.getElementById(`${paramName}-value`);
        if (slider) {
            slider.value = value;
            if (valueDisplay) {
                // Determine decimal places based on slider step
                const step = parseFloat(slider.step);
                const decimals = step >= 1 ? 0 : (step === 0.1 ? 1 : 2);
                valueDisplay.textContent = value.toFixed(decimals);
            }
        }
    });
}

// Update slider state (enabled/disabled) based on scene and tab states
export function updateSliderStates(sceneType, sceneConfig) {
    const config = sceneConfig[sceneType];
    if (!config) return;

    const allParams = ['size', 'density', 'frequency', 'amplitude', 'objectCount',
                     'scaling_amount', 'scaling_speed', 'rotationX', 'rotationY', 'rotationZ',
                     'rotation_speed', 'rotation_offset',
                     'copy_spacing', 'copy_scale_offset',
                     'copy_rotation_var', 'copy_translation_var',
                     'copy_translation_x', 'copy_translation_y', 'copy_translation_z',
                     'copy_translation_speed', 'copy_translation_offset',
                     'object_scroll_speed'];

    allParams.forEach(paramName => {
        const slider = document.getElementById(paramName);
        const container = slider?.closest('.control-group');
        if (!slider || !container) return;

        const isEnabled = config.enabled.includes(paramName);

        if (isEnabled) {
            // Enable slider
            slider.disabled = false;
            container.classList.remove('slider-disabled');
            container.removeAttribute('title');
        } else {
            // Disable slider with tooltip
            slider.disabled = true;
            container.classList.add('slider-disabled');
            container.setAttribute('title', `Not used in ${sceneType}`);
        }
    });

    // Update tab states
    updateTabStates(sceneType, sceneConfig);
}

// Setup scene selection buttons
export function setupSceneSelection(paramsManager, socketManager, sessionMemory, sceneConfig) {
    document.querySelectorAll('button[data-scene]').forEach(btn => {
        btn.addEventListener('click', () => {
            // Save current scene parameters before switching
            saveCurrentSceneParams(paramsManager, sessionMemory, sceneConfig);

            // Update UI
            document.querySelectorAll('button[data-scene]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Switch scene type
            paramsManager.params.scene_type = btn.dataset.scene;

            // Update scene-specific controls visibility
            updateSceneParams(paramsManager.params.scene_type);

            // Load parameters for new scene (from memory or defaults)
            loadSceneParams(paramsManager.params.scene_type, paramsManager, sessionMemory, sceneConfig);

            // Update slider enabled/disabled states
            updateSliderStates(paramsManager.params.scene_type, sceneConfig);

            // Check if current active tab is still valid for new scene, otherwise switch
            switchToValidTab(paramsManager.params.scene_type, sceneConfig);

            // Send updated parameters to server
            socketManager.sendParams(paramsManager.params);
        });
    });
}

// Initialize scene on page load
export function initializeScene(paramsManager, sceneConfig) {
    // Load default scene parameters
    loadSceneParams(paramsManager.params.scene_type, paramsManager, {}, sceneConfig);
    // Update slider states for default scene
    updateSliderStates(paramsManager.params.scene_type, sceneConfig);
    console.log('✅ Scene parameter system initialized');
    console.log('📊 Scene config:', sceneConfig);
}
