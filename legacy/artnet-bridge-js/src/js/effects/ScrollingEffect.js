/**
 * Scrolling Effect
 * Stackable post-processing effect that creates scrolling strobe or pulse bands
 * Can be combined with any color effect
 */
export class ScrollingEffect {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        // Scrolling parameters
        this.enabled = false;
        this.mode = 'strobe'; // 'strobe' or 'pulse'
        this.thickness = 5; // Thickness of the scrolling band (in voxels)
        this.direction = 'y'; // x, y, z, diagonal-xz, diagonal-yz, diagonal-xy, radial
        this.invert = false; // If true, turns pixels OFF instead of ON in the scroll band
        this.speed = 1.0; // Speed multiplier

        // Internal timing
        this.time = 0;
    }

    /**
     * Enable/disable scrolling effect
     */
    setEnabled(enabled) {
        this.enabled = enabled;
    }

    /**
     * Set scrolling mode ('strobe' or 'pulse')
     */
    setMode(mode) {
        this.mode = mode;
    }

    /**
     * Set scrolling effect thickness
     */
    setThickness(thickness) {
        this.thickness = Math.max(1, Math.min(20, thickness));
    }

    /**
     * Set scrolling effect direction
     */
    setDirection(direction) {
        this.direction = direction;
    }

    /**
     * Set scrolling effect invert mode
     */
    setInvert(invert) {
        this.invert = invert;
    }

    /**
     * Set scrolling effect speed multiplier
     */
    setSpeed(speed) {
        this.speed = Math.max(0.1, Math.min(5, speed));
    }

    /**
     * Update time
     */
    update(deltaTime) {
        this.time += deltaTime;
    }

    /**
     * Apply scrolling effect to a single voxel color
     * @param {object} color - {r, g, b} color for the voxel
     * @param {number} x - Grid X coordinate
     * @param {number} y - Grid Y coordinate
     * @param {number} z - Grid Z coordinate
     * @returns {object} - Modified color {r, g, b}
     */
    applyToVoxel(color, x, y, z) {
        if (!this.enabled) {
            return color;
        }

        const maxDim = this.getScrollMaxDimension();
        const scrollPos = (this.time * this.speed * 10) % maxDim;
        const voxelPos = this.calculateScrollPosition(x, y, z);
        const distFromBand = Math.abs(voxelPos - scrollPos);

        if (this.mode === 'strobe') {
            return this.applyStrobeEffectToVoxel(color, distFromBand);
        } else if (this.mode === 'pulse') {
            return this.applyPulseEffectToVoxel(color, distFromBand);
        }

        return color;
    }

    /**
     * Apply strobe effect to a single voxel
     */
    applyStrobeEffectToVoxel(color, distFromBand) {
        if (this.invert) {
            // INVERTED MODE: Turn pixels OFF in the band
            if (distFromBand < this.thickness) {
                // Inside the band - turn off (black)
                return { r: 0, g: 0, b: 0 };
            }
            // Outside the band - keep original color
            return color;
        } else {
            // NORMAL MODE: Turn pixels ON in the band
            if (distFromBand < this.thickness) {
                // Inside the band - full bright (keep existing color at full intensity)
                // Already colored by ColorEffects, just ensure it's visible
                // We could boost brightness here if needed
                if (color.r === 0 && color.g === 0 && color.b === 0) {
                    // If voxel was off, turn it to white
                    return { r: 255, g: 255, b: 255 };
                }
                return color;
            } else {
                // Outside the band - turn off
                return { r: 0, g: 0, b: 0 };
            }
        }
    }

    /**
     * Apply pulse effect to a single voxel
     */
    applyPulseEffectToVoxel(color, distFromBand) {
        if (distFromBand < this.thickness) {
            // Inside the band
            const bandProgress = distFromBand / this.thickness; // 0 at center, 1 at edges

            // Smooth falloff from center
            const falloff = 1 - bandProgress;

            // Pulse oscillation
            const pulse = Math.sin(this.time * this.speed * 5);
            const brightness = 0.5 + (pulse + 1) * 0.25; // 0.5 to 1.0

            // Combine falloff and pulse
            const finalBrightness = brightness * falloff;

            if (this.invert) {
                // INVERTED MODE: Reduce brightness in the band (darken towards black)
                const darkenFactor = 1 - finalBrightness; // Invert the brightness
                return {
                    r: Math.max(0, Math.round(color.r * darkenFactor)),
                    g: Math.max(0, Math.round(color.g * darkenFactor)),
                    b: Math.max(0, Math.round(color.b * darkenFactor))
                };
            } else {
                // NORMAL MODE: Increase brightness in the band
                const brightnessFactor = 1 + finalBrightness;
                return {
                    r: Math.min(255, Math.round(color.r * brightnessFactor)),
                    g: Math.min(255, Math.round(color.g * brightnessFactor)),
                    b: Math.min(255, Math.round(color.b * brightnessFactor))
                };
            }
        }
        // Outside the band - keep original color
        return color;
    }

    /**
     * Calculate scroll position based on direction
     */
    calculateScrollPosition(x, y, z) {
        switch (this.direction) {
            case 'x':
                return x;
            case 'y':
                return y;
            case 'z':
                return z;
            case 'diagonal-xz':
                return (x + z) / 2;
            case 'diagonal-yz':
                return (y + z) / 2;
            case 'diagonal-xy':
                return (x + y) / 2;
            case 'radial': {
                const dx = x - this.gridX / 2;
                const dz = z - this.gridZ / 2;
                return Math.sqrt(dx * dx + dz * dz);
            }
            default:
                return y; // default to Y
        }
    }

    /**
     * Get max dimension for scroll direction
     */
    getScrollMaxDimension() {
        switch (this.direction) {
            case 'x':
                return this.gridX;
            case 'y':
                return this.gridY;
            case 'z':
                return this.gridZ;
            case 'diagonal-xz':
                return (this.gridX + this.gridZ) / 2;
            case 'diagonal-yz':
                return (this.gridY + this.gridZ) / 2;
            case 'diagonal-xy':
                return (this.gridX + this.gridY) / 2;
            case 'radial': {
                const maxX = this.gridX / 2;
                const maxZ = this.gridZ / 2;
                return Math.sqrt(maxX * maxX + maxZ * maxZ);
            }
            default:
                return this.gridY;
        }
    }

    /**
     * Reset effect state
     */
    reset() {
        this.time = 0;
    }
}
