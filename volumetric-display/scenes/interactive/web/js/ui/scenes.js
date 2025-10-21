import { updateTabStates, switchToValidTab } from './tabs.js';

// Physics type parameter mappings with smart defaults
const PHYSICS_PARAMS = {
    fountain: {
        enabled: ['particle_size_variation', 'restitution', 'air_resistance', 'spread_angle', 'motion_blur', 'boundary_mode', 'trail_length'],
        disabled: ['enable_particle_collisions', 'turbulence', 'energy_boost'],
        defaults: {
            particle_size_variation: 0.0,
            restitution: 0.8,
            air_resistance: 0.05,
            spread_angle: 15.0,
            motion_blur: false,
            enable_particle_collisions: false,
            turbulence: 0.3,
            boundary_mode: 'despawn',
            energy_boost: 0.0,
            trail_length: 0.0
        }
    },
    bouncing: {
        enabled: ['particle_size_variation', 'restitution', 'air_resistance', 'motion_blur', 'enable_particle_collisions', 'energy_boost', 'trail_length'],
        disabled: ['spread_angle', 'turbulence', 'boundary_mode'],  // Always bounces
        defaults: {
            particle_size_variation: 0.0,
            restitution: 0.95,
            air_resistance: 0.02,
            spread_angle: 15.0,
            motion_blur: false,
            enable_particle_collisions: false,
            turbulence: 0.3,
            boundary_mode: 'bounce',  // Always bounces
            energy_boost: 0.0,
            trail_length: 0.0
        }
    },
    orbital: {
        enabled: ['particle_size_variation', 'air_resistance', 'motion_blur', 'boundary_mode', 'energy_boost', 'trail_length'],
        disabled: ['restitution', 'spread_angle', 'turbulence', 'enable_particle_collisions'],
        defaults: {
            particle_size_variation: 0.0,
            restitution: 0.8,
            air_resistance: 0.0,
            spread_angle: 15.0,
            motion_blur: true,
            enable_particle_collisions: false,
            turbulence: 0.3,
            boundary_mode: 'despawn',
            energy_boost: 0.3,  // Default to some kick for variation
            trail_length: 0.0
        }
    },
    rain: {
        enabled: ['particle_size_variation', 'turbulence', 'motion_blur', 'boundary_mode', 'trail_length'],
        disabled: ['restitution', 'air_resistance', 'spread_angle', 'enable_particle_collisions', 'energy_boost'],
        defaults: {
            particle_size_variation: 0.0,
            restitution: 0.8,
            air_resistance: 0.05,
            spread_angle: 15.0,
            motion_blur: false,
            enable_particle_collisions: false,
            turbulence: 0.3,
            boundary_mode: 'despawn',
            energy_boost: 0.0,
            trail_length: 0.0
        }
    }
};

// Update physics-type-specific parameter visibility and reset to defaults
export function updatePhysicsParams(physicsType, paramsManager, socketManager) {
    const config = PHYSICS_PARAMS[physicsType];
    if (!config) return;

    const allPhysicsParams = ['particle_size_variation', 'restitution', 'air_resistance', 'spread_angle', 'turbulence',
                              'enable_particle_collisions', 'motion_blur', 'boundary_mode', 'energy_boost', 'trail_length'];

    allPhysicsParams.forEach(paramName => {
        // Get default value for this physics type
        const defaultValue = config.defaults[paramName];

        // Special handling for boundary_mode (single toggle button)
        if (paramName === 'boundary_mode') {
            const boundaryToggle = document.getElementById('boundary_bounce_toggle');
            const isEnabled = config.enabled.includes(paramName);

            if (boundaryToggle) {
                // Reset to default value
                const shouldBeActive = defaultValue === 'bounce';
                if (shouldBeActive) {
                    boundaryToggle.classList.add('active');
                } else {
                    boundaryToggle.classList.remove('active');
                }

                // Update params
                if (paramsManager) {
                    paramsManager.update('boundary_mode', defaultValue);
                }

                // Enable/disable based on physics type
                boundaryToggle.disabled = !isEnabled;
                boundaryToggle.style.opacity = isEnabled ? '1' : '0.4';

                // Special handling for bouncing scene - show it's always on
                if (physicsType === 'bouncing') {
                    boundaryToggle.classList.add('active');
                    boundaryToggle.setAttribute('title', 'Always enabled for bouncing');
                } else if (!isEnabled) {
                    boundaryToggle.setAttribute('title', `Not used in ${physicsType} mode`);
                } else {
                    boundaryToggle.removeAttribute('title');
                }
            }
            return;
        }

        let element = document.getElementById(paramName);
        if (!element) return;

        const isEnabled = config.enabled.includes(paramName);
        const isToggleButton = element.classList.contains('toggle-btn');

        if (isToggleButton) {
            // Reset toggle to default value
            if (defaultValue === true) {
                element.classList.add('active');
            } else {
                element.classList.remove('active');
            }

            // Update params
            if (paramsManager) {
                paramsManager.update(paramName, defaultValue);
            }

            // For toggle buttons, disable the button itself
            element.disabled = !isEnabled;
            element.style.opacity = isEnabled ? '1' : '0.4';
            if (isEnabled) {
                element.removeAttribute('title');
            } else {
                element.setAttribute('title', `Not used in ${physicsType} mode`);
            }
        } else {
            // For sliders, reset value and update UI
            const valueDisplay = document.getElementById(`${paramName}-value`);

            if (element && defaultValue !== undefined) {
                element.value = defaultValue;

                if (valueDisplay) {
                    const step = parseFloat(element.step);
                    const decimals = step >= 1 ? 0 : (step === 0.1 ? 1 : 2);
                    valueDisplay.textContent = defaultValue.toFixed(decimals);
                }

                // Update params
                if (paramsManager) {
                    paramsManager.update(paramName, defaultValue);
                }
            }

            const container = element.closest('.control-group');
            if (!container) return;

            if (isEnabled) {
                // Enable control
                element.disabled = false;
                container.classList.remove('slider-disabled');
                container.removeAttribute('title');
                container.style.opacity = '1';
            } else {
                // Disable control with visual feedback
                element.disabled = true;
                container.classList.add('slider-disabled');
                container.setAttribute('title', `Not used in ${physicsType} mode`);
                container.style.opacity = '0.4';
            }
        }
    });

    // Send updated params to server
    if (socketManager) {
        socketManager.sendParams(paramsManager.params);
    }
}

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
    document.getElementById('physicsType-control').style.display =
        sceneType === 'physics' ? 'block' : 'none';
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

        // Skip if value is still undefined (no default exists)
        if (value === undefined) {
            return;
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

            // If switching to physics scene, update physics param visibility
            if (paramsManager.params.scene_type === 'physics') {
                const physicsType = paramsManager.params.scene_params.physicsType || 'fountain';
                updatePhysicsParams(physicsType, paramsManager, socketManager);
            } else {
                // Send updated parameters to server for non-physics scenes
                socketManager.sendParams(paramsManager.params);
            }
        });
    });
}

// Initialize scene on page load
export function initializeScene(paramsManager, sessionMemory, sceneConfig) {
    // Load default scene parameters
    loadSceneParams(paramsManager.params.scene_type, paramsManager, sessionMemory, sceneConfig);

    // Update slider states for default scene (this also calls updateTabStates)
    updateSliderStates(paramsManager.params.scene_type, sceneConfig);

    // If starting with physics scene, update physics param visibility (but don't reset on initial load)
    if (paramsManager.params.scene_type === 'physics') {
        const physicsType = paramsManager.params.scene_params.physicsType || 'fountain';
        // Don't pass paramsManager/socketManager on init to avoid resetting user's saved values
        updatePhysicsParams(physicsType, null, null);
    }

    console.log('✅ Scene parameter system initialized');
    console.log('📊 Scene config:', sceneConfig);
    console.log('🎬 Default scene:', paramsManager.params.scene_type);
}
