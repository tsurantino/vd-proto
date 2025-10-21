/**
 * Parameter Automation System
 * LFO engine for animating scene parameters automatically
 */
export class ParameterAutomation {
    constructor() {
        this.automations = new Map(); // parameterId -> automation config
        this.time = 0;
    }

    /**
     * Add or update automation for a parameter
     * @param {string} parameterId - Unique parameter identifier
     * @param {object} config - Automation configuration
     */
    setAutomation(parameterId, config) {
        const automation = {
            waveType: config.waveType || 'sine', // sine, triangle, square, sawtooth, random
            frequency: config.frequency || 1.0,   // Hz
            amplitude: config.amplitude || 0.5,   // 0-1 (percentage of range)
            phase: config.phase || 0,              // 0-1
            min: config.min || 0,                  // parameter minimum
            max: config.max || 1,                  // parameter maximum
            enabled: config.enabled !== false,
            baseValue: config.baseValue || 0.5,   // center point for oscillation
            randomSeed: Math.random() * 1000      // for random wave
        };

        this.automations.set(parameterId, automation);
    }

    /**
     * Remove automation for a parameter
     */
    removeAutomation(parameterId) {
        this.automations.delete(parameterId);
    }

    /**
     * Toggle automation enabled state
     */
    toggleAutomation(parameterId) {
        const automation = this.automations.get(parameterId);
        if (automation) {
            automation.enabled = !automation.enabled;
            return automation.enabled;
        }
        return false;
    }

    /**
     * Check if parameter has active automation
     */
    isAutomated(parameterId) {
        const automation = this.automations.get(parameterId);
        return automation && automation.enabled;
    }

    /**
     * Get automation config for parameter
     */
    getAutomation(parameterId) {
        return this.automations.get(parameterId);
    }

    /**
     * Get all active automations
     */
    getAllAutomations() {
        return Array.from(this.automations.entries())
            .filter(([_, config]) => config.enabled)
            .map(([id, config]) => ({ id, ...config }));
    }

    /**
     * Update time and calculate all automated parameter values
     */
    update(deltaTime) {
        this.time += deltaTime;
    }

    /**
     * Calculate automated value for a parameter
     * @param {string} parameterId - Parameter to calculate
     * @returns {number|null} - Calculated value or null if not automated
     */
    getAutomatedValue(parameterId) {
        const automation = this.automations.get(parameterId);
        if (!automation || !automation.enabled) {
            return null;
        }

        const { waveType, frequency, amplitude, phase, min, max, baseValue } = automation;

        // Calculate phase offset time
        const t = (this.time * frequency + phase) % 1;

        // Calculate wave value (-1 to 1)
        let wave = 0;

        switch (waveType) {
            case 'sine':
                wave = Math.sin(t * Math.PI * 2);
                break;

            case 'triangle':
                wave = Math.abs((t * 4) % 4 - 2) - 1;
                break;

            case 'square':
                wave = t < 0.5 ? -1 : 1;
                break;

            case 'sawtooth':
                wave = (t * 2) - 1;
                break;

            case 'random':
                // Smooth random using sine with changing frequency
                const seed = automation.randomSeed + Math.floor(this.time * frequency);
                wave = Math.sin(seed * 12.9898) * 2 - 1;
                break;

            default:
                wave = 0;
        }

        // Map wave to parameter range
        const range = max - min;
        const center = baseValue !== undefined ? baseValue : (min + max) / 2;
        const offset = wave * (range * amplitude * 0.5);

        // Clamp to parameter range
        return Math.max(min, Math.min(max, center + offset));
    }

    /**
     * Get wave value at current time (for visualization)
     * @param {string} parameterId
     * @returns {number} - Value between -1 and 1
     */
    getWaveValue(parameterId) {
        const automation = this.automations.get(parameterId);
        if (!automation) return 0;

        const { waveType, frequency, phase } = automation;
        const t = (this.time * frequency + phase) % 1;

        switch (waveType) {
            case 'sine':
                return Math.sin(t * Math.PI * 2);
            case 'triangle':
                return Math.abs((t * 4) % 4 - 2) - 1;
            case 'square':
                return t < 0.5 ? -1 : 1;
            case 'sawtooth':
                return (t * 2) - 1;
            case 'random':
                const seed = automation.randomSeed + Math.floor(this.time * frequency);
                return Math.sin(seed * 12.9898) * 2 - 1;
            default:
                return 0;
        }
    }

    /**
     * Clear all automations
     */
    clear() {
        this.automations.clear();
        this.time = 0;
    }

    /**
     * Reset time (useful for synchronization)
     */
    resetTime() {
        this.time = 0;
    }

    /**
     * Export automations to JSON
     */
    export() {
        const data = {};
        this.automations.forEach((config, id) => {
            data[id] = { ...config };
        });
        return data;
    }

    /**
     * Import automations from JSON
     */
    import(data) {
        this.clear();
        Object.entries(data).forEach(([id, config]) => {
            this.setAutomation(id, config);
        });
    }
}
