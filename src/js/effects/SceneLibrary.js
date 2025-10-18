/**
 * Scene Library
 * Main orchestrator for all volumetric display scenes
 */
import { CoreScenes } from './scenes/CoreScenes.js';
import { IllusionScenes } from './scenes/IllusionScenes.js';

export class SceneLibrary {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        // Initialize scene modules
        this.coreScenes = new CoreScenes(gridX, gridY, gridZ);
        this.illusionScenes = new IllusionScenes(gridX, gridY, gridZ);

        this.scenes = this.createScenes();
    }

    createScenes() {
        return {
            'shapeMorph': {
                name: 'Shape Morph',
                category: 'core',
                defaultParams: {
                    shape: 'sphere', // 'sphere', 'helix', 'torus', 'cube', 'pyramid', 'plane'
                    // Global params used: size, thickness, objectCount, animation
                },
                fn: (voxels, time, params) => this.coreScenes.renderShapeMorph(voxels, time, params)
            },
            'particleFlow': {
                name: 'Particle Flow',
                category: 'core',
                defaultParams: {
                    pattern: 'particles', // 'particles', 'spiral', 'explode', 'tornado', 'whirlpool', 'galaxy'
                    particleSize: 1, // Size of each particle (1-5) - mapped from global size parameter
                    // Global params used: size (particleSize), density, velocity (animationSpeed), amplitude (radius), depth (height), objectOffset, movement params
                    // For directional flow (rain, fountain, stars), use movement presets with scrollSpeed/scrollDirection
                    // Vortex patterns (tornado, whirlpool, galaxy) also use: amplitude->radius, depth->height, animationSpeed->velocity/twist
                },
                fn: (voxels, time, params) => this.coreScenes.renderParticleFlow(voxels, time, params)
            },
            'waveField': {
                name: 'Wave Field',
                category: 'core',
                defaultParams: {
                    waveType: 'ripple', // 'ripple', 'plane', 'standing', 'interference'
                    // Global params used: frequency, amplitude, direction
                },
                fn: (voxels, time, params) => this.coreScenes.renderWaveField(voxels, time, params)
            },
            'procedural': {
                name: 'Procedural Volume',
                category: 'core',
                defaultParams: {
                    algorithm: 'perlin', // 'perlin', 'simplex', 'cellular', 'voronoi', 'fractal'
                    // Global params used: scale (size), threshold (amplitude), octaves (detailLevel), animationType, inversion
                },
                fn: (voxels, time, params) => this.coreScenes.renderProcedural(voxels, time, params)
            },
            'grid': {
                name: 'Grid',
                category: 'core',
                defaultParams: {
                    pattern: 'cube', // 'cube', 'sphere', 'tunnel', 'layers'
                    // Global params used: spacing, thickness (density), offset (spacing)
                },
                fn: (voxels, time, params) => this.coreScenes.renderGrid(voxels, time, params)
            },
            'text3D': {
                name: 'Text 3D',
                category: 'core',
                defaultParams: {
                    text: 'HELLO',
                    style: 'block' // 'block', 'outline', 'filled'
                    // Global params used: size, depth
                },
                fn: (voxels, time, params) => this.coreScenes.renderText3D(voxels, time, params)
            },
            // Illusion scenes
            'rotatingAmes': {
                name: 'Rotating Ames Room',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, animationSpeed, depth
                },
                fn: (voxels, time, params) => this.illusionScenes.renderRotatingAmes(voxels, time, params)
            },
            'infiniteCorridor': {
                name: 'Infinite Corridor',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, depth, spacing
                },
                fn: (voxels, time, params) => this.illusionScenes.renderInfiniteCorridor(voxels, time, params)
            },
            'kineticDepth': {
                name: 'Kinetic Depth Effect',
                category: 'illusion',
                defaultParams: {
                    // Global params used: animationSpeed, size
                },
                fn: (voxels, time, params) => this.illusionScenes.renderKineticDepth(voxels, time, params)
            },
            'waterfallIllusion': {
                name: 'Motion Aftereffect',
                category: 'illusion',
                defaultParams: {
                    // Global params used: animationSpeed, density
                },
                fn: (voxels, time, params) => this.illusionScenes.renderWaterfallIllusion(voxels, time, params)
            },
            'penroseTriangle': {
                name: 'Penrose Triangle',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.illusionScenes.renderPenroseTriangle(voxels, time, params)
            },
            'neckerCube': {
                name: 'Necker Cube',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, thickness
                },
                fn: (voxels, time, params) => this.illusionScenes.renderNeckerCube(voxels, time, params)
            },
            'fraserSpiral': {
                name: 'Fraser Spiral',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, frequency, animationSpeed
                },
                fn: (voxels, time, params) => this.illusionScenes.renderFraserSpiral(voxels, time, params)
            },
            'cafeWall': {
                name: 'Café Wall Illusion',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, spacing
                },
                fn: (voxels, time, params) => this.illusionScenes.renderCafeWall(voxels, time, params)
            },
            'pulfrich': {
                name: 'Pulfrich Effect',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.illusionScenes.renderPulfrich(voxels, time, params)
            },
            'rotatingSnakes': {
                name: 'Rotating Snakes',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.illusionScenes.renderRotatingSnakes(voxels, time, params)
            },
            'breathingSquare': {
                name: 'Breathing Square',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, frequency
                },
                fn: (voxels, time, params) => this.illusionScenes.renderBreathingSquare(voxels, time, params)
            },
            'moirePattern': {
                name: 'Moiré Pattern',
                category: 'illusion',
                defaultParams: {
                    // Global params used: spacing, animationSpeed
                },
                fn: (voxels, time, params) => this.illusionScenes.renderMoirePattern(voxels, time, params)
            }
        };
    }

    // ============================================================================
    // PUBLIC API
    // ============================================================================
    getScene(sceneType) {
        return this.scenes[sceneType];
    }

    getSceneNames() {
        return Object.keys(this.scenes).map(key => this.scenes[key].name);
    }

    getSceneTypes() {
        return Object.keys(this.scenes);
    }

    updateDensity(density) {
        this.coreScenes.updateDensity(density);
    }
}
