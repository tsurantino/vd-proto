/**
 * Global Effects
 * Post-processing effects that apply to all scenes
 */
export class GlobalEffects {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        // Frame buffer for decay effect
        this.previousFrame = new Array(gridX * gridY * gridZ).fill(0);

        // Effect parameters
        this.decay = 0; // 0 = sharp, 1 = maximum trails
        this.strobe = 'off'; // 'off', 'slow', 'medium', 'fast'
        this.pulse = 'off'; // 'off', 'slow', 'medium', 'fast'
        this.invert = false;

        // Internal timing
        this.time = 0;
    }

    setDecay(value) {
        this.decay = Math.max(0, Math.min(1, value));
    }

    setStrobe(mode) {
        this.strobe = mode; // 'off', 'slow', 'medium', 'fast'
    }

    setPulse(mode) {
        this.pulse = mode; // 'off', 'slow', 'medium', 'fast'
    }

    setInvert(enabled) {
        this.invert = enabled;
    }

    update(deltaTime) {
        this.time += deltaTime;
    }

    apply(voxels) {
        const len = voxels.length;

        // Pre-calculate effect values
        const hasDecay = this.decay > 0;
        const hasPulse = this.pulse !== 'off';
        const hasStrobe = this.strobe !== 'off';
        const strobeActive = hasStrobe ? this.getStrobeState() : true;
        const pulseFactor = hasPulse ? this.getPulseFactor() : 1.0;

        // Early exit for strobe off state
        if (hasStrobe && !strobeActive) {
            voxels.fill(0);
            if (hasDecay) this.previousFrame.fill(0);
            return voxels;
        }

        // Combine all effects in a single pass when possible
        if (hasDecay || hasPulse) {
            const currentWeight = hasDecay ? (1 - this.decay * 0.7) : 1.0;
            const previousWeight = hasDecay ? (this.decay * 0.7) : 0.0;

            for (let i = 0; i < len; i++) {
                let value = voxels[i];

                // Apply decay
                if (hasDecay) {
                    value = value * currentWeight + this.previousFrame[i] * previousWeight;
                }

                // Apply pulse
                if (hasPulse) {
                    value *= pulseFactor;
                }

                voxels[i] = value;

                // Store for next frame
                if (hasDecay) {
                    this.previousFrame[i] = value;
                }
            }
        }

        // Apply invert (requires separate passes)
        if (this.invert) {
            // Find max in single pass
            let max = 0.1;
            for (let i = 0; i < len; i++) {
                if (voxels[i] > max) max = voxels[i];
            }

            // Invert
            for (let i = 0; i < len; i++) {
                voxels[i] = voxels[i] > 0.1 ? 0 : max;
            }
        }

        return voxels;
    }

    getStrobeState() {
        const frequencies = {
            'slow': 2, // 2 Hz
            'medium': 5, // 5 Hz
            'fast': 10 // 10 Hz
        };

        const freq = frequencies[this.strobe] || 0;
        if (freq === 0) return true;

        // Square wave: on/off at frequency
        const cycle = Math.floor(this.time * freq * 2);
        return cycle % 2 === 0;
    }

    getPulseFactor() {
        const frequencies = {
            'slow': 0.5, // 0.5 Hz
            'medium': 1.0, // 1 Hz
            'fast': 2.0 // 2 Hz
        };

        const freq = frequencies[this.pulse] || 0;
        if (freq === 0) return 1.0;

        // Sine wave: smooth brightness oscillation
        // Range: 0.3 to 1.0
        return 0.65 + 0.35 * Math.sin(this.time * freq * Math.PI * 2);
    }

    reset() {
        this.previousFrame.fill(0);
        this.time = 0;
    }
}
