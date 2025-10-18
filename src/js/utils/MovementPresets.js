/**
 * Movement Presets
 * Predefined movement parameter combinations for quick configuration
 */

export class MovementPresets {
    static presets = {
        'reset': {
            name: 'Reset All',
            description: 'Clear all movement effects',
            params: {
                rotationX: 0,
                rotationY: 0,
                rotationZ: 0,
                translateX: 0,
                translateY: 0,
                translateZ: 0,
                translateAmplitude: 0,
                bounceSpeed: 0,
                bounceHeight: 0,
                orbitSpeed: 0,
                orbitRadius: 0,
                pulseSpeed: 0,
                pulseAmount: 0,
                spiralSpeed: 0,
                spiralRadius: 0,
                spiralHeight: 0,
                wobbleSpeed: 0,
                wobbleAmount: 0,
                figure8Speed: 0,
                figure8Size: 0,
                ellipseSpeed: 0,
                ellipseRadiusX: 0,
                ellipseRadiusZ: 0,
                scrollSpeed: 0,
                scrollDirection: 'x'
            }
        },
        'gentleFloat': {
            name: 'Gentle Float',
            description: 'Slow bounce and drift motion',
            params: {
                bounceSpeed: 0.2,
                bounceHeight: 0.3,
                translateX: 0.1,
                translateZ: 0.15,
                translateAmplitude: 0.2,
                rotationY: 0.1
            }
        },
        'orbitalDance': {
            name: 'Orbital Dance',
            description: 'Circular orbit with pulsing size',
            params: {
                orbitSpeed: 0.4,
                orbitRadius: 0.5,
                pulseSpeed: 0.3,
                pulseAmount: 0.2,
                rotationY: 0.3
            }
        },
        'tumbling': {
            name: 'Tumbling',
            description: 'Chaotic rotation and wobble',
            params: {
                wobbleSpeed: 0.6,
                wobbleAmount: 0.7,
                rotationX: 0.4,
                rotationY: 0.5,
                rotationZ: 0.3
            }
        },
        'figure8Glide': {
            name: 'Figure-8 Glide',
            description: 'Smooth figure-8 path with bounce',
            params: {
                figure8Speed: 0.5,
                figure8Size: 0.6,
                bounceSpeed: 0.2,
                bounceHeight: 0.2,
                rotationY: 0.2
            }
        },
        'spiralAscent': {
            name: 'Spiral Ascent',
            description: 'Upward spiral motion',
            params: {
                spiralSpeed: 0.4,
                spiralRadius: 0.5,
                spiralHeight: 0.8,
                rotationY: 0.3
            }
        },
        'spinningTop': {
            name: 'Spinning Top',
            description: 'Fast rotation with wobble',
            params: {
                rotationY: 0.8,
                wobbleSpeed: 0.3,
                wobbleAmount: 0.2,
                bounceSpeed: 0.1,
                bounceHeight: 0.1
            }
        },
        'ellipticalOrbit': {
            name: 'Elliptical Orbit',
            description: 'Oval-shaped orbital path',
            params: {
                ellipseSpeed: 0.5,
                ellipseRadiusX: 0.7,
                ellipseRadiusZ: 0.4,
                rotationY: 0.2
            }
        },
        'breathingPulse': {
            name: 'Breathing Pulse',
            description: 'Gentle size oscillation',
            params: {
                pulseSpeed: 0.3,
                pulseAmount: 0.5,
                rotationY: 0.1
            }
        },
        'scrollingBanner': {
            name: 'Scrolling Banner',
            description: 'Continuous horizontal scroll',
            params: {
                scrollSpeed: 1.5,
                scrollDirection: 'x'
            }
        },
        'scrollRight': {
            name: 'Scroll Right',
            description: 'Continuous scroll to the right (positive X)',
            params: {
                scrollSpeed: 1.0,
                scrollDirection: 'x'
            }
        },
        'scrollUp': {
            name: 'Scroll Up',
            description: 'Continuous upward scroll (fountain effect)',
            params: {
                scrollSpeed: 1.0,
                scrollDirection: 'y'
            }
        },
        'scrollForward': {
            name: 'Scroll Forward',
            description: 'Continuous scroll forward (positive Z)',
            params: {
                scrollSpeed: 1.0,
                scrollDirection: 'z'
            }
        },
        'scrollDiagonal': {
            name: 'Scroll Diagonal',
            description: 'Continuous diagonal scroll (X and Z)',
            params: {
                scrollSpeed: 1.0,
                scrollDirection: 'diagonal'
            }
        },
        'rain': {
            name: 'Rain (Scroll Down)',
            description: 'Downward falling motion like rain',
            params: {
                scrollSpeed: -1.0,
                scrollDirection: 'y'
            }
        },
        'starfield': {
            name: 'Starfield (Scroll Back)',
            description: 'Stars coming toward viewer',
            params: {
                scrollSpeed: -1.0,
                scrollDirection: 'z'
            }
        }
    };

    /**
     * Get a specific preset by name
     * @param {string} name - Preset name
     * @returns {object} Preset configuration
     */
    static getPreset(name) {
        return this.presets[name];
    }

    /**
     * Get all presets as array of [name, preset] pairs
     * @returns {array} Array of preset entries
     */
    static getAll() {
        return Object.entries(this.presets);
    }

    /**
     * Get all preset names
     * @returns {array} Array of preset names
     */
    static getNames() {
        return Object.keys(this.presets);
    }

    /**
     * Apply a preset to a display instance
     * @param {VolumetricDisplay} display - Display instance
     * @param {string} presetName - Preset to apply
     * @returns {boolean} Success status
     */
    static apply(display, presetName) {
        const preset = this.getPreset(presetName);
        if (!preset) {
            console.error(`Preset "${presetName}" not found`);
            return false;
        }

        // Reset all movement parameters first if it's not the reset preset
        if (presetName !== 'reset') {
            const resetPreset = this.getPreset('reset');
            Object.entries(resetPreset.params).forEach(([param, value]) => {
                display.setGlobalSceneParameter(param, value);
            });
        }

        // Apply the preset parameters
        Object.entries(preset.params).forEach(([param, value]) => {
            display.setGlobalSceneParameter(param, value);
        });

        console.log(`Applied movement preset: ${preset.name}`);
        return true;
    }
}
