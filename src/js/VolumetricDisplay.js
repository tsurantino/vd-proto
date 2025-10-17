/**
 * Volumetric Display Controller
 * Main application controller that orchestrates the display simulation
 */
import { VolumetricRenderer } from './VolumetricRenderer.js';
import { EffectLibrary } from './effects/EffectLibrary.js';

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

        // Initialize effect library
        this.effectLibrary = new EffectLibrary(gridX, gridY, gridZ);

        // State
        this.currentEffectIndex = 0;
        this.time = 0;
        this.params = {
            speed: 1.0,
            density: 0.1,
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

    setEffect(index) {
        if (index >= 0 && index < this.effectLibrary.getEffectCount()) {
            if (index !== this.currentEffectIndex) {
                // Start transition
                this.oldVoxels = [...this.voxels];
                this.isTransitioning = true;
                this.transitionProgress = 0;
                this.currentEffectIndex = index;
                this.time = 0;
            }
        }
    }

    setParameter(name, value) {
        if (this.params.hasOwnProperty(name)) {
            this.params[name] = value;

            // Update particle systems if density changed
            if (name === 'density') {
                this.effectLibrary.updateDensity(value);
            }
        }
    }

    getParameter(name) {
        return this.params[name];
    }

    setFPSCallback(callback) {
        this.fpsCallback = callback;
    }

    setActiveLEDsCallback(callback) {
        this.activeLEDsCallback = callback;
    }

    update() {
        // Get current effect
        const effect = this.effectLibrary.getEffect(this.currentEffectIndex);

        // Run effect to update voxel grid
        effect.fn(this.voxels, this.time, this.params);

        // Handle transition
        if (this.isTransitioning) {
            this.transitionProgress += 0.016 / this.transitionDuration;

            if (this.transitionProgress >= 1) {
                this.isTransitioning = false;
                this.transitionProgress = 1;
            }
        }

        // Increment time
        this.time += 0.016;
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
        const activeLEDs = this.renderer.render(renderVoxels, this.params);

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

    getEffectNames() {
        return this.effectLibrary.getEffectNames();
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
