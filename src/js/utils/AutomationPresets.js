/**
 * Automation Presets
 * Pre-configured parameter automation patterns for common effects
 */

export class AutomationPresets {
    static presets = {
        'gentle-wave': {
            name: 'Gentle Wave',
            description: 'Slow, smooth sine wave oscillation',
            config: {
                waveType: 'sine',
                frequency: 0.5,
                amplitude: 0.3,
                phase: 0
            }
        },
        'fast-pulse': {
            name: 'Fast Pulse',
            description: 'Quick pulsing movement',
            config: {
                waveType: 'sine',
                frequency: 2.0,
                amplitude: 0.5,
                phase: 0
            }
        },
        'triangle-sweep': {
            name: 'Triangle Sweep',
            description: 'Linear back-and-forth motion',
            config: {
                waveType: 'triangle',
                frequency: 1.0,
                amplitude: 0.5,
                phase: 0
            }
        },
        'sharp-pulse': {
            name: 'Sharp Pulse',
            description: 'Quick attacks with square wave',
            config: {
                waveType: 'square',
                frequency: 1.5,
                amplitude: 0.6,
                phase: 0
            }
        },
        'sawtooth-ramp': {
            name: 'Sawtooth Ramp',
            description: 'Gradual rise with sudden drop',
            config: {
                waveType: 'sawtooth',
                frequency: 1.0,
                amplitude: 0.5,
                phase: 0
            }
        },
        'slow-breathe': {
            name: 'Slow Breathe',
            description: 'Very slow, deep breathing effect',
            config: {
                waveType: 'sine',
                frequency: 0.3,
                amplitude: 0.7,
                phase: 0
            }
        },
        'random-jitter': {
            name: 'Random Jitter',
            description: 'Chaotic random variation',
            config: {
                waveType: 'random',
                frequency: 3.0,
                amplitude: 0.4,
                phase: 0
            }
        },
        'subtle-drift': {
            name: 'Subtle Drift',
            description: 'Barely noticeable slow drift',
            config: {
                waveType: 'sine',
                frequency: 0.2,
                amplitude: 0.15,
                phase: 0
            }
        },
        'extreme-chaos': {
            name: 'Extreme Chaos',
            description: 'Wild random fluctuations',
            config: {
                waveType: 'random',
                frequency: 5.0,
                amplitude: 0.8,
                phase: 0
            }
        },
        'pendulum': {
            name: 'Pendulum',
            description: 'Regular pendulum swing',
            config: {
                waveType: 'sine',
                frequency: 1.0,
                amplitude: 0.5,
                phase: 0
            }
        }
    };

    /**
     * Get all preset names and descriptions
     * @returns {array} Array of [key, preset] entries
     */
    static getAll() {
        return Object.entries(this.presets);
    }

    /**
     * Get a specific preset by key
     * @param {string} key - Preset key
     * @returns {object|null} Preset object or null if not found
     */
    static get(key) {
        return this.presets[key] || null;
    }

    /**
     * Apply a preset to a parameter
     * @param {object} parameterAutomation - ParameterAutomation instance
     * @param {string} paramId - Parameter ID to automate
     * @param {string} presetKey - Preset key
     * @param {number} min - Parameter minimum value
     * @param {number} max - Parameter maximum value
     * @param {number} baseValue - Parameter base/center value
     */
    static apply(parameterAutomation, paramId, presetKey, min, max, baseValue) {
        const preset = this.get(presetKey);
        if (!preset) {
            console.error(`Preset "${presetKey}" not found`);
            return false;
        }

        const config = {
            ...preset.config,
            min,
            max,
            baseValue,
            enabled: true
        };

        parameterAutomation.setAutomation(paramId, config);
        return true;
    }
}
