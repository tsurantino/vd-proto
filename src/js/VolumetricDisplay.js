/**
 * Volumetric Display Controller
 * Main application controller that orchestrates the display simulation
 */
import { VolumetricRenderer } from './VolumetricRenderer.js';
import { SceneLibrary } from './effects/SceneLibrary.js';
import { ScrollingEffect } from './effects/ScrollingEffect.js';
import { GlobalEffects } from './effects/GlobalEffects.js';
import { ParameterAutomation } from './automation/ParameterAutomation.js';
import { GlobalParameterMapper } from './utils/GlobalParameterMapper.js';

export class VolumetricDisplay {
    constructor(canvasId, gridX = 40, gridY = 20, gridZ = 40) {
        // Grid dimensions
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        // Initialize voxel grid
        this.voxels = new Array(gridX * gridY * gridZ).fill(0);

        // Initialize renderer
        const canvas = document.getElementById(canvasId);
        this.renderer = new VolumetricRenderer(canvas, gridX, gridY, gridZ);

        // Initialize scene library and effects
        this.sceneLibrary = new SceneLibrary(gridX, gridY, gridZ);
        this.scrollingEffect = new ScrollingEffect(gridX, gridY, gridZ);
        this.globalEffects = new GlobalEffects(gridX, gridY, gridZ);

        // Initialize parameter automation
        this.parameterAutomation = new ParameterAutomation();

        // State
        this.currentSceneType = 'shapeMorph';
        this.time = 0;

        // Scene parameters (start with defaults from first scene)
        this.sceneParams = { ...this.sceneLibrary.getScene(this.currentSceneType).defaultParams };

        // Display parameters
        this.displayParams = {
            ledSize: 1.0,
            brightness: 0.8,
            gridOpacity: 0.2,
            speed: 1.0 // Global speed multiplier
        };

        // Global scene parameters (shared across all scenes)
        this.globalSceneParams = GlobalParameterMapper.getDefaults();

        // Transition state
        this.isTransitioning = false;
        this.transitionProgress = 0;
        this.transitionDuration = 0.5; // seconds
        this.oldVoxels = new Array(gridX * gridY * gridZ).fill(0);

        // FPS tracking
        this.lastTime = performance.now();
        this.frameCount = 0;
        this.fps = 0;
        this.fpsCallback = null;
        this.activeLEDsCallback = null;

        // Animation loop
        this.isRunning = false;
    }

    setScene(sceneType) {
        const scene = this.getSceneFromLibrary(sceneType);
        if (scene) {
            if (sceneType !== this.currentSceneType) {
                // Start transition
                this.oldVoxels = [...this.voxels];
                this.isTransitioning = true;
                this.transitionProgress = 0;
                this.currentSceneType = sceneType;
                this.time = 0;

                // Reset to default parameters for new scene
                this.sceneParams = { ...scene.defaultParams };
            }
        }
    }

    getSceneFromLibrary(sceneType) {
        return this.sceneLibrary.getScene(sceneType);
    }

    setSceneParameter(name, value) {
        this.sceneParams[name] = value;

        // Update particle systems if density changed (via global params)
        const mappedParams = GlobalParameterMapper.mapToScene(
            this.currentSceneType,
            this.globalSceneParams,
            this.sceneParams
        );
        if (mappedParams.density !== undefined) {
            this.sceneLibrary.updateDensity(mappedParams.density);
        }
    }

    setGlobalSceneParameter(name, value) {
        this.globalSceneParams[name] = value;

        // Update particle systems if density changed
        if (name === 'density') {
            this.sceneLibrary.updateDensity(value);
        }
    }

    setDisplayParameter(name, value) {
        this.displayParams[name] = value;
    }

    getSceneParameter(name) {
        return this.sceneParams[name];
    }

    getGlobalSceneParameter(name) {
        return this.globalSceneParams[name];
    }

    getDisplayParameter(name) {
        return this.displayParams[name];
    }

    getGlobalSceneParams() {
        return { ...this.globalSceneParams };
    }

    getActiveGlobalParameters() {
        return GlobalParameterMapper.getActiveParameters(this.currentSceneType);
    }

    // Global effect controls
    setDecay(value) {
        this.globalEffects.setDecay(value);
    }

    setStrobe(mode) {
        this.globalEffects.setStrobe(mode);
    }

    setPulse(mode) {
        this.globalEffects.setPulse(mode);
    }

    setInvert(enabled) {
        this.globalEffects.setInvert(enabled);
    }

    // Scrolling effect controls
    setScrollingEnabled(enabled) {
        this.scrollingEffect.setEnabled(enabled);
    }

    setScrollingMode(mode) {
        this.scrollingEffect.setMode(mode);
    }

    setScrollingThickness(thickness) {
        this.scrollingEffect.setThickness(thickness);
    }

    setScrollingDirection(direction) {
        this.scrollingEffect.setDirection(direction);
    }

    setScrollingInvert(invert) {
        this.scrollingEffect.setInvert(invert);
    }

    setScrollingSpeed(speed) {
        this.scrollingEffect.setSpeed(speed);
    }

    setFPSCallback(callback) {
        this.fpsCallback = callback;
    }

    setActiveLEDsCallback(callback) {
        this.activeLEDsCallback = callback;
    }

    update() {
        const deltaTime = 0.016 * this.displayParams.speed;

        // Update parameter automation
        this.parameterAutomation.update(deltaTime);

        // Apply automated values to scene parameters
        const automatedSceneParams = { ...this.sceneParams };
        for (const [paramName, _] of Object.entries(this.sceneParams)) {
            const automatedValue = this.parameterAutomation.getAutomatedValue(paramName);
            if (automatedValue !== null) {
                automatedSceneParams[paramName] = automatedValue;
            }
        }

        // Apply automated values to global scene parameters
        const automatedGlobalParams = { ...this.globalSceneParams };
        for (const [paramName, _] of Object.entries(this.globalSceneParams)) {
            const automatedValue = this.parameterAutomation.getAutomatedValue(paramName);
            if (automatedValue !== null) {
                automatedGlobalParams[paramName] = automatedValue;
            }
        }

        // Map global parameters to scene-specific format
        const mappedParams = GlobalParameterMapper.mapToScene(
            this.currentSceneType,
            automatedGlobalParams,
            automatedSceneParams
        );

        // Add decay state to params so scenes can skip clearing when decay is active
        mappedParams.shouldClear = this.globalEffects.decay === 0;

        // Get current scene from appropriate library
        const scene = this.getSceneFromLibrary(this.currentSceneType);

        // Run scene to update voxel grid (use mapped params)
        if (scene) {
            scene.fn(this.voxels, this.time, mappedParams);
        }

        // Apply global effects (only if any are active)
        if (this.globalEffects.decay > 0 ||
            this.globalEffects.strobe !== 'off' ||
            this.globalEffects.pulse !== 'off' ||
            this.globalEffects.invert) {
            const processedVoxels = this.globalEffects.apply(this.voxels);
            this.voxels = processedVoxels;
        }

        // Handle transition
        if (this.isTransitioning) {
            this.transitionProgress += deltaTime / this.transitionDuration;

            if (this.transitionProgress >= 1) {
                this.isTransitioning = false;
                this.transitionProgress = 1;
            }
        }

        // Update time
        this.time += deltaTime;
        this.scrollingEffect.update(deltaTime);
        this.globalEffects.update(deltaTime);
    }

    render() {
        // Prepare voxels for rendering (blend during transition)
        let renderVoxels = this.voxels;

        if (this.isTransitioning) {
            // Create blended voxel array
            const blendedVoxels = new Array(this.voxels.length);
            const t = this.easeInOutCubic(this.transitionProgress);

            for (let i = 0; i < this.voxels.length; i++) {
                // Crossfade between old and new effect
                blendedVoxels[i] = this.oldVoxels[i] * (1 - t) + this.voxels[i] * t;
            }
            renderVoxels = blendedVoxels;
        }

        // Render the voxel grid (pass scrolling effect for application in renderer)
        const activeLEDs = this.renderer.render(renderVoxels, this.displayParams, this.scrollingEffect);

        // Update stats
        if (this.activeLEDsCallback) {
            this.activeLEDsCallback(activeLEDs);
        }

        // Update FPS
        this.frameCount++;
        const now = performance.now();
        if (now - this.lastTime >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastTime = now;
            if (this.fpsCallback) {
                this.fpsCallback(this.fps);
            }
        }
    }

    easeInOutCubic(t) {
        return t < 0.5
            ? 4 * t * t * t
            : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    loop() {
        if (!this.isRunning) return;

        this.update();
        this.render();

        requestAnimationFrame(() => this.loop());
    }

    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.loop();
        }
    }

    stop() {
        this.isRunning = false;
    }

    getSceneNames() {
        return this.sceneLibrary.getSceneNames();
    }

    getSceneTypes() {
        return this.sceneLibrary.getSceneTypes();
    }

    getScenesByCategory(category) {
        const allScenes = this.sceneLibrary.scenes;
        return Object.entries(allScenes)
            .filter(([_, scene]) => scene.category === category)
            .map(([key, scene]) => ({ key, ...scene }));
    }

    getCurrentSceneType() {
        return this.currentSceneType;
    }

    getCurrentSceneParams() {
        return { ...this.sceneParams };
    }

    getSceneDefaultParams(sceneType) {
        const scene = this.getSceneFromLibrary(sceneType);
        return scene ? { ...scene.defaultParams } : {};
    }

    getGridInfo() {
        return {
            x: this.gridX,
            y: this.gridY,
            z: this.gridZ,
            total: this.gridX * this.gridY * this.gridZ
        };
    }
}
