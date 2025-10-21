/**
 * Global Parameter Mapper
 * Maps unified global parameters to scene-specific parameters
 */

export class GlobalParameterMapper {
    /**
     * Maps global parameters to scene-specific parameter format
     * @param {string} sceneType - The scene type
     * @param {object} globalParams - Global parameters
     * @param {object} sceneParams - Scene-specific parameters
     * @returns {object} Merged parameters with global values mapped appropriately
     */
    static mapToScene(sceneType, globalParams, sceneParams) {
        const mapped = { ...sceneParams };

        // Pass through all movement parameters to all scenes (now universal)
        mapped.rotationX = globalParams.rotationX || 0;
        mapped.rotationY = globalParams.rotationY || 0;
        mapped.rotationZ = globalParams.rotationZ || 0;
        mapped.translateX = globalParams.translateX || 0;
        mapped.translateY = globalParams.translateY || 0;
        mapped.translateZ = globalParams.translateZ || 0;
        mapped.translateAmplitude = globalParams.translateAmplitude || 0;
        mapped.bounceSpeed = globalParams.bounceSpeed || 0;
        mapped.bounceHeight = globalParams.bounceHeight || 0;
        mapped.orbitSpeed = globalParams.orbitSpeed || 0;
        mapped.orbitRadius = globalParams.orbitRadius || 0;
        mapped.pulseSpeed = globalParams.pulseSpeed || 0;
        mapped.pulseAmount = globalParams.pulseAmount || 0;

        // Advanced movement types
        mapped.spiralSpeed = globalParams.spiralSpeed || 0;
        mapped.spiralRadius = globalParams.spiralRadius || 0;
        mapped.spiralHeight = globalParams.spiralHeight || 0;
        mapped.wobbleSpeed = globalParams.wobbleSpeed || 0;
        mapped.wobbleAmount = globalParams.wobbleAmount || 0;
        mapped.figure8Speed = globalParams.figure8Speed || 0;
        mapped.figure8Size = globalParams.figure8Size || 0;
        mapped.ellipseSpeed = globalParams.ellipseSpeed || 0;
        mapped.ellipseRadiusX = globalParams.ellipseRadiusX || 0;
        mapped.ellipseRadiusZ = globalParams.ellipseRadiusZ || 0;
        mapped.scrollSpeed = globalParams.scrollSpeed || 0;
        mapped.scrollDirection = globalParams.scrollDirection || 'x';
        mapped.objectArrangement = globalParams.objectArrangement || 'circular';
        mapped.objectOffset = globalParams.objectOffset || 0;

        // Map Size/Scale parameter
        if (globalParams.size !== undefined) {
            switch (sceneType) {
                case 'shapeMorph':
                case 'text3D':
                    mapped.size = globalParams.size;
                    break;
                case 'particleFlow':
                    // Map size (0.1-3.0) to particleSize (1-5)
                    // 0.1-0.6 -> 1, 0.6-1.2 -> 2, 1.2-1.8 -> 3, 1.8-2.4 -> 4, 2.4-3.0 -> 5
                    mapped.particleSize = Math.max(1, Math.min(5, Math.round(globalParams.size * 1.67)));
                    break;
                case 'procedural':
                    // Scale is inverse of size for noise
                    mapped.scale = 0.05 + (1 - globalParams.size / 3) * 0.45;
                    break;
                case 'plasma':
                    // Similar inverse mapping
                    mapped.scale = 0.1 + (1 - globalParams.size / 3) * 0.4;
                    break;
            }
        }

        // Map Density/Thickness parameter
        if (globalParams.density !== undefined) {
            switch (sceneType) {
                case 'particleFlow':
                case 'vortex':
                    mapped.density = globalParams.density;
                    break;
                case 'shapeMorph':
                    // Thickness for shapes (0.1 to 1.0)
                    mapped.thickness = 0.1 + globalParams.density * 0.9;
                    break;
                case 'grid':
                    // Thickness for grid (0.2 to 2.0)
                    mapped.thickness = 0.2 + globalParams.density * 1.8;
                    break;
            }
        }

        // Map Object Count parameter (universal)
        if (globalParams.objectCount !== undefined) {
            mapped.objectCount = globalParams.objectCount;
        }

        // Map Animation Speed parameter
        if (globalParams.animationSpeed !== undefined) {
            switch (sceneType) {
                case 'particleFlow':
                    mapped.velocity = 0.5 + globalParams.animationSpeed * 2.5;
                    break;
                case 'vortex':
                    mapped.twist = 0.1 + globalParams.animationSpeed * 2.9;
                    break;
            }
        }

        // Map Animation Type parameter
        if (globalParams.animationType !== undefined) {
            switch (sceneType) {
                case 'shapeMorph':
                    // Map to shape morph animations
                    const shapeAnimMap = {
                        'none': 'pulse', // Default to pulse if none
                        'pulse': 'pulse',
                        'rotate': 'rotate',
                        'breathe': 'breathe',
                        'morph': 'morph',
                        'evolve': 'breathe',
                        'scroll': 'rotate'
                    };
                    mapped.animation = shapeAnimMap[globalParams.animationType] || 'pulse';
                    break;
                case 'procedural':
                    // Map to procedural animations
                    const procAnimMap = {
                        'none': 'none',
                        'pulse': 'evolve',
                        'rotate': 'scroll',
                        'breathe': 'evolve',
                        'morph': 'morph',
                        'evolve': 'evolve',
                        'scroll': 'scroll'
                    };
                    mapped.animationType = procAnimMap[globalParams.animationType] || 'scroll';
                    break;
            }
        }

        // Map Frequency parameter
        if (globalParams.frequency !== undefined) {
            switch (sceneType) {
                case 'waveField':
                    mapped.frequency = globalParams.frequency;
                    break;
                case 'plasma':
                    // Map to complexity
                    mapped.complexity = 0.5 + globalParams.frequency * 0.75;
                    break;
            }
        }

        // Map Amplitude/Intensity parameter
        if (globalParams.amplitude !== undefined) {
            switch (sceneType) {
                case 'waveField':
                    // Special handling for plasma wave type
                    if (sceneParams.waveType === 'plasma') {
                        // For plasma, amplitude controls threshold (inverse relationship)
                        // Higher amplitude = lower threshold = more visible voxels
                        // Map amplitude (0.0-1.0) to threshold (0.8-0.3)
                        mapped.amplitude = 0.8 - globalParams.amplitude * 0.5;
                    } else {
                        // For other wave types, amplitude controls wave height
                        mapped.amplitude = 0.5 + globalParams.amplitude * 2.5;
                    }
                    break;
                case 'procedural':
                case 'plasma':
                    // Map to threshold (inverse)
                    mapped.threshold = 0.8 - globalParams.amplitude * 0.5;
                    break;
                case 'vortex':
                    mapped.radius = 0.5 + globalParams.amplitude * 1.5;
                    break;
                case 'particleFlow':
                    // For vortex patterns in particleFlow, map amplitude to radius
                    mapped.radius = 0.5 + globalParams.amplitude * 1.5;
                    break;
            }
        }

        // Map Detail Level parameter
        if (globalParams.detailLevel !== undefined) {
            switch (sceneType) {
                case 'procedural':
                    mapped.octaves = Math.floor(globalParams.detailLevel);
                    break;
                case 'plasma':
                    mapped.layers = Math.floor(globalParams.detailLevel);
                    break;
            }
        }

        // Map Spacing/Offset parameter
        if (globalParams.spacing !== undefined) {
            switch (sceneType) {
                case 'grid':
                    // Map to spacing (2-10 range)
                    mapped.spacing = 2 + globalParams.spacing * 8;
                    mapped.offset = globalParams.spacing;
                    break;
            }
        }

        // Map Direction parameter
        if (globalParams.direction !== undefined) {
            switch (sceneType) {
                case 'waveField':
                    mapped.direction = globalParams.direction;
                    break;
            }
        }

        // Map Depth/Height parameter
        if (globalParams.depth !== undefined) {
            switch (sceneType) {
                case 'text3D':
                    mapped.depth = 0.2 + globalParams.depth * 0.8;
                    break;
                case 'vortex':
                    mapped.height = 0.3 + globalParams.depth * 1.2;
                    break;
                case 'particleFlow':
                    // For vortex patterns in particleFlow, map depth to height
                    mapped.height = 0.3 + globalParams.depth * 1.2;
                    break;
            }
        }

        // Map Inversion parameter
        if (globalParams.inversion !== undefined) {
            switch (sceneType) {
                case 'procedural':
                    mapped.inversion = globalParams.inversion;
                    break;
            }
        }

        return mapped;
    }

    /**
     * Get default global parameters
     */
    static getDefaults() {
        return {
            size: 1.0,              // 0.1 - 3.0
            density: 0.5,           // 0.0 - 1.0
            objectCount: 1,         // 1 - 4
            animationSpeed: 1.0,    // 0.1 - 3.0
            animationType: 'pulse', // none/pulse/rotate/breathe/morph/evolve/scroll (legacy, kept for procedural)
            frequency: 1.0,         // 0.1 - 2.0
            amplitude: 0.5,         // 0.0 - 1.0
            detailLevel: 1,         // 1 - 5
            spacing: 0.3,           // 0.0 - 1.0
            direction: 'radial',    // x/y/z/radial/diagonal/random
            depth: 0.5,             // 0.0 - 1.0
            inversion: false,       // boolean

            // Independent movement controls (stackable)
            rotationX: 0,           // -1.0 to 1.0 (rotation speed around X axis)
            rotationY: 0,           // -1.0 to 1.0 (rotation speed around Y axis)
            rotationZ: 0,           // -1.0 to 1.0 (rotation speed around Z axis)
            translateX: 0,          // 0.0 to 1.0 (translation oscillation speed)
            translateY: 0,          // 0.0 to 1.0 (translation oscillation speed)
            translateZ: 0,          // 0.0 to 1.0 (translation oscillation speed)
            translateAmplitude: 0,  // 0.0 to 1.0 (how far to translate)
            bounceSpeed: 0,         // 0.0 to 1.0 (vertical bounce speed)
            bounceHeight: 0,        // 0.0 to 1.0 (how high to bounce)
            orbitSpeed: 0,          // 0.0 to 1.0 (circular orbit speed)
            orbitRadius: 0,         // 0.0 to 1.0 (orbit radius)
            pulseSpeed: 0,          // 0.0 to 1.0 (size pulsing speed)
            pulseAmount: 0,         // 0.0 to 1.0 (how much to pulse)

            // Advanced movement controls
            spiralSpeed: 0,         // 0.0 to 1.0 (spiral motion speed)
            spiralRadius: 0,        // 0.0 to 1.0 (spiral radius)
            spiralHeight: 0,        // 0.0 to 1.0 (spiral vertical range)
            wobbleSpeed: 0,         // 0.0 to 1.0 (wobble/tumble speed)
            wobbleAmount: 0,        // 0.0 to 1.0 (wobble intensity)
            figure8Speed: 0,        // 0.0 to 1.0 (figure-8 motion speed)
            figure8Size: 0,         // 0.0 to 1.0 (figure-8 size)
            ellipseSpeed: 0,        // 0.0 to 1.0 (elliptical orbit speed)
            ellipseRadiusX: 0,      // 0.0 to 1.0 (ellipse X radius)
            ellipseRadiusZ: 0,      // 0.0 to 1.0 (ellipse Z radius)
            scrollSpeed: 0,         // 0.0 to 2.0 (continuous scroll speed)
            scrollDirection: 'x',   // x/y/z/diagonal
            objectArrangement: 'circular',  // circular/linear (how multiple objects are arranged)
            objectOffset: 0         // 0.0 to 1.0 (time offset between objects for staggered movement)
        };
    }

    /**
     * Get which global parameters affect a given scene
     * @param {string} sceneType
     * @returns {array} List of global parameter names that affect this scene
     */
    static getActiveParameters(sceneType) {
        const movementParams = [
            'rotationX', 'rotationY', 'rotationZ',
            'translateX', 'translateY', 'translateZ', 'translateAmplitude',
            'bounceSpeed', 'bounceHeight',
            'orbitSpeed', 'orbitRadius',
            'pulseSpeed', 'pulseAmount',
            'spiralSpeed', 'spiralRadius', 'spiralHeight',
            'wobbleSpeed', 'wobbleAmount',
            'figure8Speed', 'figure8Size',
            'ellipseSpeed', 'ellipseRadiusX', 'ellipseRadiusZ',
            'scrollSpeed', 'scrollDirection', 'objectArrangement', 'objectOffset'
        ];

        const paramMap = {
            'shapeMorph': ['size', 'density', 'objectCount', ...movementParams],
            'particleFlow': ['size', 'density', 'animationSpeed', 'amplitude', 'depth', ...movementParams],
            'waveField': ['frequency', 'amplitude', 'direction', ...movementParams],
            'procedural': ['size', 'amplitude', 'detailLevel', 'animationType', 'inversion', ...movementParams],
            'vortex': ['density', 'animationSpeed', 'amplitude', 'depth', 'objectCount', ...movementParams],
            'grid': ['density', 'spacing', ...movementParams],
            'text3D': ['size', 'depth', ...movementParams]
        };

        return paramMap[sceneType] || [];
    }

    /**
     * Get mapping description for a parameter in a specific scene
     * @param {string} paramName - Global parameter name
     * @param {string} sceneType - Scene type
     * @returns {string|null} Description of how this parameter maps to the scene
     */
    static getMappingDescription(paramName, sceneType) {
        const mappings = {
            'size': {
                'shapeMorph': 'Maps to shape size',
                'text3D': 'Maps to text size',
                'particleFlow': 'Maps to particle size (1-5)',
                'procedural': 'Maps to noise scale (inverse)',
                'waveField': 'Maps to plasma scale (inverse)'
            },
            'density': {
                'particleFlow': 'Maps to particle density',
                'vortex': 'Maps to vortex density',
                'shapeMorph': 'Maps to shape thickness',
                'grid': 'Maps to grid line thickness'
            },
            'animationSpeed': {
                'particleFlow': 'Maps to particle velocity',
                'vortex': 'Maps to vortex twist speed'
            },
            'frequency': {
                'waveField': 'Maps to wave frequency',
                'plasma': 'Maps to plasma complexity'
            },
            'amplitude': {
                'waveField': 'Maps to wave amplitude',
                'procedural': 'Maps to noise threshold (inverse)',
                'vortex': 'Maps to vortex radius',
                'particleFlow': 'Maps to vortex radius (for tornado/whirlpool/galaxy patterns)'
            },
            'detailLevel': {
                'procedural': 'Maps to noise octaves',
                'plasma': 'Maps to plasma layers'
            },
            'spacing': {
                'grid': 'Maps to grid spacing & offset'
            },
            'direction': {
                'waveField': 'Maps to wave direction'
            },
            'depth': {
                'text3D': 'Maps to text depth/extrusion',
                'vortex': 'Maps to vortex height',
                'particleFlow': 'Maps to vortex height (for tornado/whirlpool/galaxy patterns)'
            },
            'inversion': {
                'procedural': 'Maps to noise inversion'
            },
            'objectCount': {
                'shapeMorph': 'Number of shapes to render',
                'vortex': 'Number of vortices to render'
            }
        };

        // Movement parameters are universal
        const movementParams = [
            'rotationX', 'rotationY', 'rotationZ',
            'translateX', 'translateY', 'translateZ', 'translateAmplitude',
            'bounceSpeed', 'bounceHeight',
            'orbitSpeed', 'orbitRadius',
            'pulseSpeed', 'pulseAmount',
            'spiralSpeed', 'spiralRadius', 'spiralHeight',
            'wobbleSpeed', 'wobbleAmount',
            'figure8Speed', 'figure8Size',
            'ellipseSpeed', 'ellipseRadiusX', 'ellipseRadiusZ',
            'scrollSpeed', 'scrollDirection', 'objectArrangement', 'objectOffset'
        ];

        if (movementParams.includes(paramName)) {
            return 'Applied to all scenes for movement effects';
        }

        if (mappings[paramName] && mappings[paramName][sceneType]) {
            return mappings[paramName][sceneType];
        }

        return null;
    }
}
