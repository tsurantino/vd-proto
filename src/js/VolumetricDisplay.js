/**
 * Volumetric Display Controller
 * Main application controller that orchestrates the display simulation
 */
import { VolumetricRenderer } from './VolumetricRenderer.js';
import { SceneLibrary } from './effects/SceneLibrary.js';
import { GlobalEffects } from './effects/GlobalEffects.js';

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

        // Initialize scene library and global effects
        this.sceneLibrary = new SceneLibrary(gridX, gridY, gridZ);
        this.globalEffects = new GlobalEffects(gridX, gridY, gridZ);

        // State
        this.currentSceneType = 'shapeMorph';
        this.time = 0;

        // Scene parameters (start with defaults from first scene)
        this.sceneParams = { ...this.sceneLibrary.getScene(this.currentSceneType).defaultParams };

        // Global parameters
        this.globalParams = {
            ledSize: 1.0,
            brightness: 0.8,
            gridOpacity: 0.2
        };

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
        if (this.sceneLibrary.getScene(sceneType)) {
            if (sceneType !== this.currentSceneType) {
                // Start transition
                this.oldVoxels = [...this.voxels];
                this.isTransitioning = true;
                this.transitionProgress = 0;
                this.currentSceneType = sceneType;
                this.time = 0;

                // Reset to default parameters for new scene
                this.sceneParams = { ...this.sceneLibrary.getScene(sceneType).defaultParams };
            }
        }
    }

    setSceneParameter(name, value) {
        this.sceneParams[name] = value;

        // Update particle systems if density changed
        if (name === 'density') {
            this.sceneLibrary.updateDensity(value);
        }
    }

    setGlobalParameter(name, value) {
        this.globalParams[name] = value;
    }

    getSceneParameter(name) {
        return this.sceneParams[name];
    }

    getGlobalParameter(name) {
        return this.globalParams[name];
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

    setFPSCallback(callback) {
        this.fpsCallback = callback;
    }

    setActiveLEDsCallback(callback) {
        this.activeLEDsCallback = callback;
    }

    update() {
        const deltaTime = 0.016;

        // Get current scene
        const scene = this.sceneLibrary.getScene(this.currentSceneType);

        // Run scene to update voxel grid
        scene.fn(this.voxels, this.time, this.sceneParams);

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

        // Render the voxel grid
        const activeLEDs = this.renderer.render(renderVoxels, this.globalParams);

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

    getCurrentSceneType() {
        return this.currentSceneType;
    }

    getCurrentSceneParams() {
        return { ...this.sceneParams };
    }

    getSceneDefaultParams(sceneType) {
        const scene = this.sceneLibrary.getScene(sceneType);
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
