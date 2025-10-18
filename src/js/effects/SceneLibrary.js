/**
 * Scene Library
 * Four scene types with configurable parameters
 */
import { PerlinNoise } from '../utils/PerlinNoise.js';
import { RainParticleSystem, StarfieldParticleSystem } from '../utils/ParticleSystems.js';

export class SceneLibrary {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        // Initialize utilities
        this.perlin = new PerlinNoise();
        this.rainSystem = new RainParticleSystem(gridX, gridY, gridZ);
        this.starSystem = new StarfieldParticleSystem(gridX, gridY, gridZ);

        // Initialize particle systems
        this.rainSystem.init(0.1);
        this.starSystem.init(0.1);

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
                fn: (voxels, time, params) => this.renderShapeMorph(voxels, time, params)
            },
            'particleFlow': {
                name: 'Particle Flow',
                category: 'core',
                defaultParams: {
                    pattern: 'rain', // 'rain', 'stars', 'fountain', 'spiral', 'explode'
                    particleSize: 1, // Size of each particle (1-5) - mapped from global size parameter
                    // Global params used: size (particleSize), density, velocity (animationSpeed), movement params
                },
                fn: (voxels, time, params) => this.renderParticleFlow(voxels, time, params)
            },
            'waveField': {
                name: 'Wave Field',
                category: 'core',
                defaultParams: {
                    waveType: 'ripple', // 'ripple', 'plane', 'standing', 'interference'
                    // Global params used: frequency, amplitude, direction
                },
                fn: (voxels, time, params) => this.renderWaveField(voxels, time, params)
            },
            'procedural': {
                name: 'Procedural Volume',
                category: 'core',
                defaultParams: {
                    algorithm: 'perlin', // 'perlin', 'simplex', 'cellular', 'voronoi', 'fractal'
                    // Global params used: scale (size), threshold (amplitude), octaves (detailLevel), animationType, inversion
                },
                fn: (voxels, time, params) => this.renderProcedural(voxels, time, params)
            },
            'vortex': {
                name: 'Vortex',
                category: 'core',
                defaultParams: {
                    type: 'tornado', // 'tornado', 'whirlpool', 'galaxy' (double removed - use objectCount=2)
                    // Global params used: density, twist (animationSpeed), radius (amplitude), height (depth), objectCount
                },
                fn: (voxels, time, params) => this.renderVortex(voxels, time, params)
            },
            'grid': {
                name: 'Grid',
                category: 'core',
                defaultParams: {
                    pattern: 'cube', // 'cube', 'sphere', 'tunnel', 'layers'
                    // Global params used: spacing, thickness (density), offset (spacing)
                },
                fn: (voxels, time, params) => this.renderGrid(voxels, time, params)
            },
            'text3D': {
                name: 'Text 3D',
                category: 'core',
                defaultParams: {
                    text: 'HELLO',
                    style: 'block' // 'block', 'outline', 'filled'
                    // Global params used: size, depth
                },
                fn: (voxels, time, params) => this.renderText3D(voxels, time, params)
            },
            // Illusion scenes
            'rotatingAmes': {
                name: 'Rotating Ames Room',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, animationSpeed, depth
                },
                fn: (voxels, time, params) => this.renderRotatingAmes(voxels, time, params)
            },
            'infiniteCorridor': {
                name: 'Infinite Corridor',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, depth, spacing
                },
                fn: (voxels, time, params) => this.renderInfiniteCorridor(voxels, time, params)
            },
            'kineticDepth': {
                name: 'Kinetic Depth Effect',
                category: 'illusion',
                defaultParams: {
                    // Global params used: animationSpeed, size
                },
                fn: (voxels, time, params) => this.renderKineticDepth(voxels, time, params)
            },
            'waterfallIllusion': {
                name: 'Motion Aftereffect',
                category: 'illusion',
                defaultParams: {
                    // Global params used: animationSpeed, density
                },
                fn: (voxels, time, params) => this.renderWaterfallIllusion(voxels, time, params)
            },
            'penroseTriangle': {
                name: 'Penrose Triangle',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.renderPenroseTriangle(voxels, time, params)
            },
            'neckerCube': {
                name: 'Necker Cube',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, thickness
                },
                fn: (voxels, time, params) => this.renderNeckerCube(voxels, time, params)
            },
            'fraserSpiral': {
                name: 'Fraser Spiral',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, frequency, animationSpeed
                },
                fn: (voxels, time, params) => this.renderFraserSpiral(voxels, time, params)
            },
            'cafeWall': {
                name: 'Café Wall Illusion',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, spacing
                },
                fn: (voxels, time, params) => this.renderCafeWall(voxels, time, params)
            },
            'pulfrich': {
                name: 'Pulfrich Effect',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.renderPulfrich(voxels, time, params)
            },
            'rotatingSnakes': {
                name: 'Rotating Snakes',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.renderRotatingSnakes(voxels, time, params)
            },
            'breathingSquare': {
                name: 'Breathing Square',
                category: 'illusion',
                defaultParams: {
                    // Global params used: size, frequency
                },
                fn: (voxels, time, params) => this.renderBreathingSquare(voxels, time, params)
            },
            'moirePattern': {
                name: 'Moiré Pattern',
                category: 'illusion',
                defaultParams: {
                    // Global params used: spacing, animationSpeed
                },
                fn: (voxels, time, params) => this.renderMoirePattern(voxels, time, params)
            }
        };
    }

    // ============================================================================
    // SHAPE MORPH
    // ============================================================================
    renderShapeMorph(voxels, time, params) {
        voxels.fill(0);

        const shapes = {
            'sphere': () => this.drawSphere(voxels, time, params),
            'helix': () => this.drawHelix(voxels, time, params),
            'plane': () => this.drawPlane(voxels, time, params),
            'torus': () => this.drawTorus(voxels, time, params),
            'cube': () => this.drawCube(voxels, time, params),
            'pyramid': () => this.drawPyramid(voxels, time, params)
        };

        const drawFn = shapes[params.shape] || shapes['sphere'];
        drawFn();
    }

    drawSphere(voxels, time, params) {
        // Start with center position
        const baseCenterX = this.gridX / 2;
        const baseCenterY = this.gridY / 2;
        const baseCenterZ = this.gridZ / 2;
        const numSpheres = Math.max(1, params.objectCount);

        // Base radius
        const baseRadiusBase = 5 + params.size * 5;

        // Helper function to calculate movements with time offset
        const calculateMovements = (objIdx) => {
            // Apply time offset for staggered movement
            const timeOffset = objIdx * (params.objectOffset || 0) * 2; // 0 to 2 second offset per object
            const offsetTime = time + timeOffset;

            let centerX = baseCenterX;
            let centerY = baseCenterY;
            let centerZ = baseCenterZ;
            let radius = baseRadiusBase;

            // Apply STACKABLE transformations with offset time

            // 1. Pulse (size modulation)
            if (params.pulseSpeed > 0 && params.pulseAmount > 0) {
                const pulse = (Math.sin(offsetTime * params.pulseSpeed * 3) + 1) / 2;
                const pulseRange = params.pulseAmount * 0.5; // 0 to 0.5
                radius = radius * (1 - pulseRange + pulse * pulseRange * 2);
            }

            // 2. Translation (figure-8 or linear oscillation)
            if (params.translateX > 0 && params.translateAmplitude > 0) {
                centerX += Math.sin(offsetTime * params.translateX * 2) * (this.gridX * params.translateAmplitude * 0.3);
            }
            if (params.translateY > 0 && params.translateAmplitude > 0) {
                centerY += Math.sin(offsetTime * params.translateY * 2) * (this.gridY * params.translateAmplitude * 0.3);
            }
            if (params.translateZ > 0 && params.translateAmplitude > 0) {
                centerZ += Math.cos(offsetTime * params.translateZ * 2) * (this.gridZ * params.translateAmplitude * 0.3);
            }

            // 3. Orbit (circular motion)
            if (params.orbitSpeed > 0 && params.orbitRadius > 0) {
                const angle = offsetTime * params.orbitSpeed * 2;
                const orbitR = this.gridX * params.orbitRadius * 0.3;
                centerX += Math.cos(angle) * orbitR;
                centerZ += Math.sin(angle) * orbitR;
            }

            // 4. Bounce (vertical oscillation)
            if (params.bounceSpeed > 0 && params.bounceHeight > 0) {
                centerY += Math.abs(Math.sin(offsetTime * params.bounceSpeed * 3)) * (this.gridY * params.bounceHeight * 0.4);
            }

            // 5. Spiral movement (circular motion combined with vertical oscillation)
            if (params.spiralSpeed > 0 && params.spiralRadius > 0) {
                const spiralAngle = offsetTime * params.spiralSpeed * 2;
                const spiralR = this.gridX * params.spiralRadius * 0.3;
                centerX += Math.cos(spiralAngle) * spiralR;
                centerZ += Math.sin(spiralAngle) * spiralR;
                if (params.spiralHeight > 0) {
                    centerY += Math.sin(spiralAngle) * (this.gridY * params.spiralHeight * 0.3);
                }
            }

            // 6. Figure-8 movement (lemniscate pattern)
            if (params.figure8Speed > 0 && params.figure8Size > 0) {
                const fig8Angle = offsetTime * params.figure8Speed * 2;
                const fig8Scale = this.gridX * params.figure8Size * 0.3;
                // Lemniscate of Gerono: x = a*cos(t), y = a*sin(t)*cos(t)
                centerX += Math.cos(fig8Angle) * fig8Scale;
                centerZ += Math.sin(fig8Angle) * Math.cos(fig8Angle) * fig8Scale;
            }

            // 7. Elliptical orbit (orbit with different X and Z radii)
            if (params.ellipseSpeed > 0 && (params.ellipseRadiusX > 0 || params.ellipseRadiusZ > 0)) {
                const ellipseAngle = offsetTime * params.ellipseSpeed * 2;
                const ellipseRX = this.gridX * params.ellipseRadiusX * 0.3;
                const ellipseRZ = this.gridZ * params.ellipseRadiusZ * 0.3;
                centerX += Math.cos(ellipseAngle) * ellipseRX;
                centerZ += Math.sin(ellipseAngle) * ellipseRZ;
            }

            // 8. Continuous scroll - let individual objects wrap, not the center
            let scrollOffsetX = 0;
            let scrollOffsetY = 0;
            let scrollOffsetZ = 0;

            if (params.scrollSpeed > 0) {
                const scrollAmount = offsetTime * params.scrollSpeed * 2;
                switch (params.scrollDirection) {
                    case 'x':
                        scrollOffsetX = scrollAmount;
                        break;
                    case 'y':
                        scrollOffsetY = scrollAmount;
                        break;
                    case 'z':
                        scrollOffsetZ = scrollAmount;
                        break;
                    case 'diagonal':
                        scrollOffsetX = scrollAmount;
                        scrollOffsetZ = scrollAmount;
                        break;
                }
            }

            // 9. Rotation angles (will be applied to each voxel)
            let rotX = offsetTime * (params.rotationX || 0) * 0.5;
            let rotY = offsetTime * (params.rotationY || 0) * 0.5;
            let rotZ = offsetTime * (params.rotationZ || 0) * 0.5;

            // 10. Wobble (organic rotation using multiple sine waves)
            if (params.wobbleSpeed > 0 && params.wobbleAmount > 0) {
                const wobbleAmount = params.wobbleAmount * 0.3;
                rotX += Math.sin(offsetTime * params.wobbleSpeed * 2.3) * wobbleAmount;
                rotY += Math.sin(offsetTime * params.wobbleSpeed * 1.7) * wobbleAmount;
                rotZ += Math.sin(offsetTime * params.wobbleSpeed * 2.9) * wobbleAmount;
            }

            return {
                centerX, centerY, centerZ, radius,
                scrollOffsetX, scrollOffsetY, scrollOffsetZ,
                rotX, rotY, rotZ
            };
        };

        const thickness = 1 + params.thickness * 3;

        // For linear arrangement with scrolling, render multiple copies to create seamless loop
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed > 0) ? 2 : 1;

        // Draw multiple objects distributed around center (not nested)
        for (let copyIdx = 0; copyIdx < renderCopies; copyIdx++) {
            for (let objIdx = 0; objIdx < numSpheres; objIdx++) {
                // Calculate movements for this object with offset
                const movements = calculateMovements(objIdx);
                const { centerX, centerY, centerZ, radius, scrollOffsetX, scrollOffsetY, scrollOffsetZ, rotX, rotY, rotZ } = movements;

                // Position objects based on arrangement mode
                let objCenterX = centerX;
                let objCenterY = centerY;
                let objCenterZ = centerZ;

                if (numSpheres > 1) {
                    if (params.objectArrangement === 'linear') {
                        // Linear/trailing arrangement - objects appear behind in scroll direction
                        const spacing = radius * 3;
                        const offset = objIdx * spacing;
                        switch (params.scrollDirection) {
                            case 'x':
                                objCenterX = centerX - offset;
                                break;
                            case 'y':
                                objCenterY = centerY - offset;
                                break;
                            case 'z':
                                objCenterZ = centerZ - offset;
                                break;
                            case 'diagonal':
                            default:
                                objCenterX = centerX - offset;
                                objCenterZ = centerZ - offset;
                                break;
                        }
                    } else {
                        // Circular arrangement (default)
                        const angleOffset = (objIdx / numSpheres) * Math.PI * 2;
                        const distributionRadius = radius * 1.5;
                        objCenterX = centerX + Math.cos(angleOffset) * distributionRadius;
                        objCenterZ = centerZ + Math.sin(angleOffset) * distributionRadius;
                    }
                }

                // Apply scroll offset
                objCenterX += scrollOffsetX;
                objCenterY += scrollOffsetY;
                objCenterZ += scrollOffsetZ;

                // For seamless looping, add offset for duplicate copy
                if (params.objectArrangement === 'linear' && renderCopies > 1 && copyIdx > 0) {
                    const totalWrapDistance = (radius * 3) * numSpheres;

                    // Offset the duplicate set by the wrap distance
                    switch (params.scrollDirection) {
                        case 'x':
                            objCenterX -= totalWrapDistance;
                            break;
                        case 'y':
                            objCenterY -= totalWrapDistance;
                            break;
                        case 'z':
                            objCenterZ -= totalWrapDistance;
                            break;
                        case 'diagonal':
                            objCenterX -= totalWrapDistance;
                            objCenterZ -= totalWrapDistance;
                            break;
                    }
                }

                // Modulo wrap to keep values in reasonable range
                if (params.objectArrangement === 'linear' && numSpheres > 1) {
                    const totalWrapDistance = (radius * 3) * numSpheres;
                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        objCenterX = centerX + ((objCenterX - centerX) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'y') {
                        objCenterY = centerY + ((objCenterY - centerY) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        objCenterZ = centerZ + ((objCenterZ - centerZ) % totalWrapDistance);
                    }
                }

            // Draw each sphere
            for (let x = 0; x < this.gridX; x++) {
                for (let y = 0; y < this.gridY; y++) {
                    for (let z = 0; z < this.gridZ; z++) {
                        // Get position relative to object center
                        let dx = x - objCenterX;
                        let dy = (y - objCenterY) * 2; // Y is half size
                        let dz = z - objCenterZ;

                        // Apply 3D rotations around the LOCAL object center
                        // Rotation around X axis
                        if (rotX !== 0) {
                            const tempY = dy;
                            const tempZ = dz;
                            dy = tempY * Math.cos(rotX) - tempZ * Math.sin(rotX);
                            dz = tempY * Math.sin(rotX) + tempZ * Math.cos(rotX);
                        }
                        // Rotation around Y axis
                        if (rotY !== 0) {
                            const tempX = dx;
                            const tempZ = dz;
                            dx = tempX * Math.cos(rotY) + tempZ * Math.sin(rotY);
                            dz = -tempX * Math.sin(rotY) + tempZ * Math.cos(rotY);
                        }
                        // Rotation around Z axis
                        if (rotZ !== 0) {
                            const tempX = dx;
                            const tempY = dy;
                            dx = tempX * Math.cos(rotZ) - tempY * Math.sin(rotZ);
                            dy = tempX * Math.sin(rotZ) + tempY * Math.cos(rotZ);
                        }

                        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

                        if (Math.abs(dist - radius) < thickness) {
                            voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                        }
                    }
                }
            }
            }
        }
    }

    drawHelix(voxels, time, params) {
        const numHelixes = Math.max(1, params.objectCount);
        let radius = 8 + params.size * 5;
        const thickness = 0.5 + params.thickness * 2.5;  // Range: 0.5 (when thickness=0.1) to 3.0 (when thickness=1.0)

        // Center position with movement
        let centerX = this.gridX / 2;
        let centerY = this.gridY / 2;
        let centerZ = this.gridZ / 2;

        // Apply STACKABLE transformations
        // 1. Pulse (radius modulation)
        if (params.pulseSpeed > 0 && params.pulseAmount > 0) {
            const pulse = (Math.sin(time * params.pulseSpeed * 3) + 1) / 2;
            const pulseRange = params.pulseAmount * 0.5;
            radius = radius * (1 - pulseRange + pulse * pulseRange * 2);
        }

        // 2. Translation
        if (params.translateX > 0 && params.translateAmplitude > 0) {
            centerX += Math.sin(time * params.translateX * 2) * (this.gridX * params.translateAmplitude * 0.3);
        }
        if (params.translateY > 0 && params.translateAmplitude > 0) {
            centerY += Math.sin(time * params.translateY * 2) * (this.gridY * params.translateAmplitude * 0.3);
        }
        if (params.translateZ > 0 && params.translateAmplitude > 0) {
            centerZ += Math.cos(time * params.translateZ * 2) * (this.gridZ * params.translateAmplitude * 0.3);
        }

        // 3. Orbit
        if (params.orbitSpeed > 0 && params.orbitRadius > 0) {
            const angle = time * params.orbitSpeed * 2;
            const orbitR = this.gridX * params.orbitRadius * 0.3;
            centerX += Math.cos(angle) * orbitR;
            centerZ += Math.sin(angle) * orbitR;
        }

        // 4. Bounce
        if (params.bounceSpeed > 0 && params.bounceHeight > 0) {
            centerY += Math.abs(Math.sin(time * params.bounceSpeed * 3)) * (this.gridY * params.bounceHeight * 0.4);
        }

        // 5. Spiral
        if (params.spiralSpeed > 0 && params.spiralRadius > 0) {
            const spiralAngle = time * params.spiralSpeed * 2;
            const spiralR = this.gridX * params.spiralRadius * 0.3;
            centerX += Math.cos(spiralAngle) * spiralR;
            centerZ += Math.sin(spiralAngle) * spiralR;
            if (params.spiralHeight > 0) {
                centerY += Math.sin(spiralAngle) * (this.gridY * params.spiralHeight * 0.3);
            }
        }

        // 6. Figure-8
        if (params.figure8Speed > 0 && params.figure8Size > 0) {
            const fig8Angle = time * params.figure8Speed * 2;
            const fig8Scale = this.gridX * params.figure8Size * 0.3;
            centerX += Math.cos(fig8Angle) * fig8Scale;
            centerZ += Math.sin(fig8Angle) * Math.cos(fig8Angle) * fig8Scale;
        }

        // 7. Elliptical orbit
        if (params.ellipseSpeed > 0 && (params.ellipseRadiusX > 0 || params.ellipseRadiusZ > 0)) {
            const ellipseAngle = time * params.ellipseSpeed * 2;
            const ellipseRX = this.gridX * params.ellipseRadiusX * 0.3;
            const ellipseRZ = this.gridZ * params.ellipseRadiusZ * 0.3;
            centerX += Math.cos(ellipseAngle) * ellipseRX;
            centerZ += Math.sin(ellipseAngle) * ellipseRZ;
        }

        // 8. Continuous scroll - let individual objects wrap, not the center
        let scrollOffsetX = 0;
        let scrollOffsetY = 0;
        let scrollOffsetZ = 0;

        if (params.scrollSpeed > 0) {
            const scrollAmount = time * params.scrollSpeed * 2;
            switch (params.scrollDirection) {
                case 'x':
                    scrollOffsetX = scrollAmount;
                    break;
                case 'y':
                    scrollOffsetY = scrollAmount;
                    break;
                case 'z':
                    scrollOffsetZ = scrollAmount;
                    break;
                case 'diagonal':
                    scrollOffsetX = scrollAmount;
                    scrollOffsetZ = scrollAmount;
                    break;
            }
        }

        // 9. Rotation angles
        let rotX = time * (params.rotationX || 0) * 0.5;
        let rotY = time * (params.rotationY || 0) * 0.5;
        let rotZ = time * (params.rotationZ || 0) * 0.5;

        // 10. Wobble
        if (params.wobbleSpeed > 0 && params.wobbleAmount > 0) {
            const wobbleAmount = params.wobbleAmount * 0.3;
            rotX += Math.sin(time * params.wobbleSpeed * 2.3) * wobbleAmount;
            rotY += Math.sin(time * params.wobbleSpeed * 1.7) * wobbleAmount;
            rotZ += Math.sin(time * params.wobbleSpeed * 2.9) * wobbleAmount;
        }

        // For linear arrangement with scrolling, render multiple copies to create seamless loop
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed > 0) ? 2 : 1;

        // Draw multiple helixes distributed around center
        for (let copyIdx = 0; copyIdx < renderCopies; copyIdx++) {
            for (let helixIdx = 0; helixIdx < numHelixes; helixIdx++) {
                let helixCenterX = centerX;
                let helixCenterZ = centerZ;

                if (numHelixes > 1) {
                    if (params.objectArrangement === 'linear') {
                        // Linear/trailing arrangement
                        const spacing = radius * 3;
                        const offset = helixIdx * spacing;
                        switch (params.scrollDirection) {
                            case 'x':
                                helixCenterX = centerX - offset;
                                break;
                            case 'z':
                                helixCenterZ = centerZ - offset;
                                break;
                            case 'diagonal':
                            default:
                                helixCenterX = centerX - offset;
                                helixCenterZ = centerZ - offset;
                                break;
                        }
                    } else {
                        // Circular arrangement (default)
                        const angleOffset = (helixIdx / numHelixes) * Math.PI * 2;
                        const distributionRadius = radius * 1.5;
                        helixCenterX = centerX + Math.cos(angleOffset) * distributionRadius;
                        helixCenterZ = centerZ + Math.sin(angleOffset) * distributionRadius;
                    }
                }

                // Apply scroll offset
                helixCenterX += scrollOffsetX;
                helixCenterZ += scrollOffsetZ;

                // For seamless looping, add offset for duplicate copy
                if (params.objectArrangement === 'linear' && renderCopies > 1 && copyIdx > 0) {
                    const totalWrapDistance = (radius * 3) * numHelixes;

                    // Offset the duplicate set by the wrap distance
                    switch (params.scrollDirection) {
                        case 'x':
                            helixCenterX -= totalWrapDistance;
                            break;
                        case 'z':
                            helixCenterZ -= totalWrapDistance;
                            break;
                        case 'diagonal':
                            helixCenterX -= totalWrapDistance;
                            helixCenterZ -= totalWrapDistance;
                            break;
                    }
                }

                // Modulo wrap to keep values in reasonable range
                if (params.objectArrangement === 'linear' && numHelixes > 1) {
                    const totalWrapDistance = (radius * 3) * numHelixes;
                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        helixCenterX = centerX + ((helixCenterX - centerX) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        helixCenterZ = centerZ + ((helixCenterZ - centerZ) % totalWrapDistance);
                    }
                }

            const strandOffset = (helixIdx / numHelixes) * Math.PI * 2;

            for (let y = 0; y < this.gridY; y++) {
                const helixAngle = y * 0.3 + strandOffset;

                // Calculate helix point
                let hx = Math.cos(helixAngle) * radius;
                let hy = y - centerY;
                let hz = Math.sin(helixAngle) * radius;

                // Apply rotations to the helix point (relative to helix center)
                if (rotX !== 0) {
                    const tempY = hy;
                    const tempZ = hz;
                    hy = tempY * Math.cos(rotX) - tempZ * Math.sin(rotX);
                    hz = tempY * Math.sin(rotX) + tempZ * Math.cos(rotX);
                }
                if (rotY !== 0) {
                    const tempX = hx;
                    const tempZ = hz;
                    hx = tempX * Math.cos(rotY) + tempZ * Math.sin(rotY);
                    hz = -tempX * Math.sin(rotY) + tempZ * Math.cos(rotY);
                }
                if (rotZ !== 0) {
                    const tempX = hx;
                    const tempY = hy;
                    hx = tempX * Math.cos(rotZ) - tempY * Math.sin(rotZ);
                    hy = tempX * Math.sin(rotZ) + tempY * Math.cos(rotZ);
                }

                // Transform back to grid coordinates
                const x = helixCenterX + hx;
                const finalY = centerY + hy;
                const z = helixCenterZ + hz;

                // Draw thickness using distance-based approach for continuous values
                const thicknessRadius = thickness;
                const searchRange = Math.ceil(thicknessRadius);

                for (let dx = -searchRange; dx <= searchRange; dx++) {
                    for (let dz = -searchRange; dz <= searchRange; dz++) {
                        // Use distance check for smooth thickness
                        const dist = Math.sqrt(dx * dx + dz * dz);
                        if (dist <= thicknessRadius) {
                            const nx = Math.floor(x + dx);
                            const nz = Math.floor(z + dz);
                            const ny = Math.floor(finalY);
                            if (nx >= 0 && nx < this.gridX && ny >= 0 && ny < this.gridY && nz >= 0 && nz < this.gridZ) {
                                voxels[nx + ny * this.gridX + nz * this.gridX * this.gridY] = 1;
                            }
                        }
                    }
                }
            }
            }
        }
    }

    drawPlane(voxels, time, params) {
        const numPlanes = Math.max(1, params.objectCount);
        const thickness = 2 + params.thickness * 3;

        // Center position with movement
        let centerX = this.gridX / 2;
        let centerY = this.gridY / 2;
        let centerZ = this.gridZ / 2;

        // Apply STACKABLE transformations
        // 1. Translation
        if (params.translateX > 0 && params.translateAmplitude > 0) {
            centerX += Math.sin(time * params.translateX * 2) * (this.gridX * params.translateAmplitude * 0.3);
        }
        if (params.translateZ > 0 && params.translateAmplitude > 0) {
            centerZ += Math.cos(time * params.translateZ * 2) * (this.gridZ * params.translateAmplitude * 0.3);
        }

        // 2. Orbit
        if (params.orbitSpeed > 0 && params.orbitRadius > 0) {
            const angle = time * params.orbitSpeed * 2;
            const orbitR = this.gridX * params.orbitRadius * 0.3;
            centerX += Math.cos(angle) * orbitR;
            centerZ += Math.sin(angle) * orbitR;
        }

        // 3. Bounce
        if (params.bounceSpeed > 0 && params.bounceHeight > 0) {
            centerY += Math.abs(Math.sin(time * params.bounceSpeed * 3)) * (this.gridY * params.bounceHeight * 0.4);
        }

        // 4. Spiral
        if (params.spiralSpeed > 0 && params.spiralRadius > 0) {
            const spiralAngle = time * params.spiralSpeed * 2;
            const spiralR = this.gridX * params.spiralRadius * 0.3;
            centerX += Math.cos(spiralAngle) * spiralR;
            centerZ += Math.sin(spiralAngle) * spiralR;
            if (params.spiralHeight > 0) {
                centerY += Math.sin(spiralAngle) * (this.gridY * params.spiralHeight * 0.3);
            }
        }

        // 5. Figure-8
        if (params.figure8Speed > 0 && params.figure8Size > 0) {
            const fig8Angle = time * params.figure8Speed * 2;
            const fig8Scale = this.gridX * params.figure8Size * 0.3;
            centerX += Math.cos(fig8Angle) * fig8Scale;
            centerZ += Math.sin(fig8Angle) * Math.cos(fig8Angle) * fig8Scale;
        }

        // 6. Elliptical orbit
        if (params.ellipseSpeed > 0 && (params.ellipseRadiusX > 0 || params.ellipseRadiusZ > 0)) {
            const ellipseAngle = time * params.ellipseSpeed * 2;
            const ellipseRX = this.gridX * params.ellipseRadiusX * 0.3;
            const ellipseRZ = this.gridZ * params.ellipseRadiusZ * 0.3;
            centerX += Math.cos(ellipseAngle) * ellipseRX;
            centerZ += Math.sin(ellipseAngle) * ellipseRZ;
        }

        // 7. Continuous scroll - use offset variables
        let scrollOffsetX = 0;
        let scrollOffsetY = 0;
        let scrollOffsetZ = 0;

        if (params.scrollSpeed > 0) {
            const scrollAmount = time * params.scrollSpeed * 2;
            switch (params.scrollDirection) {
                case 'x':
                    scrollOffsetX = scrollAmount;
                    break;
                case 'y':
                    scrollOffsetY = scrollAmount;
                    break;
                case 'z':
                    scrollOffsetZ = scrollAmount;
                    break;
                case 'diagonal':
                    scrollOffsetX = scrollAmount;
                    scrollOffsetZ = scrollAmount;
                    break;
            }
        }

        // 8. Rotation angles for plane normal
        let rotX = time * (params.rotationX || 0) * 0.5;
        let rotY = time * (params.rotationY || 0) * 0.5;
        let rotZ = time * (params.rotationZ || 0) * 0.5;

        // 9. Wobble
        if (params.wobbleSpeed > 0 && params.wobbleAmount > 0) {
            const wobbleAmount = params.wobbleAmount * 0.3;
            rotX += Math.sin(time * params.wobbleSpeed * 2.3) * wobbleAmount;
            rotY += Math.sin(time * params.wobbleSpeed * 1.7) * wobbleAmount;
            rotZ += Math.sin(time * params.wobbleSpeed * 2.9) * wobbleAmount;
        }

        // Calculate plane normal with rotations
        let normalX = 1;
        let normalY = 0;
        let normalZ = 0;

        // Apply rotations to normal vector
        if (rotX !== 0) {
            const tempY = normalY;
            const tempZ = normalZ;
            normalY = tempY * Math.cos(rotX) - tempZ * Math.sin(rotX);
            normalZ = tempY * Math.sin(rotX) + tempZ * Math.cos(rotX);
        }
        if (rotY !== 0) {
            const tempX = normalX;
            const tempZ = normalZ;
            normalX = tempX * Math.cos(rotY) + tempZ * Math.sin(rotY);
            normalZ = -tempX * Math.sin(rotY) + tempZ * Math.cos(rotY);
        }
        if (rotZ !== 0) {
            const tempX = normalX;
            const tempY = normalY;
            normalX = tempX * Math.cos(rotZ) - tempY * Math.sin(rotZ);
            normalY = tempX * Math.sin(rotZ) + tempY * Math.cos(rotZ);
        }

        // For linear arrangement with scrolling, render multiple copies to create seamless loop
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed > 0) ? 2 : 1;
        const maxDimension = Math.max(this.gridX, this.gridY, this.gridZ);
        const spacing = maxDimension / (numPlanes + 1);

        // Draw multiple parallel planes
        for (let copyIdx = 0; copyIdx < renderCopies; copyIdx++) {
            for (let planeIdx = 0; planeIdx < numPlanes; planeIdx++) {
                let planeCenterX = centerX;
                let planeCenterY = centerY;
                let planeCenterZ = centerZ;

                if (numPlanes > 1) {
                    if (params.objectArrangement === 'linear') {
                        // Linear/trailing arrangement
                        const offset = planeIdx * spacing;
                        switch (params.scrollDirection) {
                            case 'x':
                                planeCenterX = centerX - offset;
                                break;
                            case 'y':
                                planeCenterY = centerY - offset;
                                break;
                            case 'z':
                                planeCenterZ = centerZ - offset;
                                break;
                            case 'diagonal':
                            default:
                                planeCenterX = centerX - offset;
                                planeCenterZ = centerZ - offset;
                                break;
                        }
                    }
                }

                // Apply scroll offset
                planeCenterX += scrollOffsetX;
                planeCenterY += scrollOffsetY;
                planeCenterZ += scrollOffsetZ;

                // For seamless looping, add offset for duplicate copy
                if (params.objectArrangement === 'linear' && renderCopies > 1 && copyIdx > 0) {
                    const totalWrapDistance = spacing * numPlanes;
                    switch (params.scrollDirection) {
                        case 'x':
                            planeCenterX -= totalWrapDistance;
                            break;
                        case 'y':
                            planeCenterY -= totalWrapDistance;
                            break;
                        case 'z':
                            planeCenterZ -= totalWrapDistance;
                            break;
                        case 'diagonal':
                            planeCenterX -= totalWrapDistance;
                            planeCenterZ -= totalWrapDistance;
                            break;
                    }
                }

                // Modulo wrap to keep values in reasonable range
                if (params.objectArrangement === 'linear' && numPlanes > 1) {
                    const totalWrapDistance = spacing * numPlanes;
                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        planeCenterX = centerX + ((planeCenterX - centerX) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'y') {
                        planeCenterY = centerY + ((planeCenterY - centerY) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        planeCenterZ = centerZ + ((planeCenterZ - centerZ) % totalWrapDistance);
                    }
                }

                const planeOffset = (params.objectArrangement === 'linear') ? 0 : (planeIdx - (numPlanes - 1) / 2) * spacing;

                for (let x = 0; x < this.gridX; x++) {
                    for (let y = 0; y < this.gridY; y++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            const cx = x - planeCenterX;
                            const cy = y - planeCenterY;
                            const cz = z - planeCenterZ;
                            const dist = Math.abs(cx * normalX + cy * normalY + cz * normalZ - planeOffset);

                            if (dist < thickness) {
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                            }
                        }
                    }
                }
            }
        }
    }

    drawTorus(voxels, time, params) {
        const numToruses = Math.max(1, params.objectCount);
        let baseMajorRadius = 15 + params.size * 5;
        let baseMinorRadius = 3 + params.thickness * 3;

        // Center position with movement
        let centerX = this.gridX / 2;
        let centerY = this.gridY / 2;
        let centerZ = this.gridZ / 2;

        // Apply STACKABLE transformations
        // 1. Pulse (radius modulation)
        if (params.pulseSpeed > 0 && params.pulseAmount > 0) {
            const pulse = (Math.sin(time * params.pulseSpeed * 3) + 1) / 2;
            const pulseRange = params.pulseAmount * 0.5;
            baseMajorRadius = baseMajorRadius * (1 - pulseRange + pulse * pulseRange * 2);
            baseMinorRadius = baseMinorRadius * (1 - pulseRange + pulse * pulseRange * 2);
        }

        // 2. Translation
        if (params.translateX > 0 && params.translateAmplitude > 0) {
            centerX += Math.sin(time * params.translateX * 2) * (this.gridX * params.translateAmplitude * 0.3);
        }
        if (params.translateY > 0 && params.translateAmplitude > 0) {
            centerY += Math.sin(time * params.translateY * 2) * (this.gridY * params.translateAmplitude * 0.3);
        }
        if (params.translateZ > 0 && params.translateAmplitude > 0) {
            centerZ += Math.cos(time * params.translateZ * 2) * (this.gridZ * params.translateAmplitude * 0.3);
        }

        // 3. Orbit
        if (params.orbitSpeed > 0 && params.orbitRadius > 0) {
            const angle = time * params.orbitSpeed * 2;
            const orbitR = this.gridX * params.orbitRadius * 0.3;
            centerX += Math.cos(angle) * orbitR;
            centerZ += Math.sin(angle) * orbitR;
        }

        // 4. Bounce
        if (params.bounceSpeed > 0 && params.bounceHeight > 0) {
            centerY += Math.abs(Math.sin(time * params.bounceSpeed * 3)) * (this.gridY * params.bounceHeight * 0.4);
        }

        // 5. Spiral
        if (params.spiralSpeed > 0 && params.spiralRadius > 0) {
            const spiralAngle = time * params.spiralSpeed * 2;
            const spiralR = this.gridX * params.spiralRadius * 0.3;
            centerX += Math.cos(spiralAngle) * spiralR;
            centerZ += Math.sin(spiralAngle) * spiralR;
            if (params.spiralHeight > 0) {
                centerY += Math.sin(spiralAngle) * (this.gridY * params.spiralHeight * 0.3);
            }
        }

        // 6. Figure-8
        if (params.figure8Speed > 0 && params.figure8Size > 0) {
            const fig8Angle = time * params.figure8Speed * 2;
            const fig8Scale = this.gridX * params.figure8Size * 0.3;
            centerX += Math.cos(fig8Angle) * fig8Scale;
            centerZ += Math.sin(fig8Angle) * Math.cos(fig8Angle) * fig8Scale;
        }

        // 7. Elliptical orbit
        if (params.ellipseSpeed > 0 && (params.ellipseRadiusX > 0 || params.ellipseRadiusZ > 0)) {
            const ellipseAngle = time * params.ellipseSpeed * 2;
            const ellipseRX = this.gridX * params.ellipseRadiusX * 0.3;
            const ellipseRZ = this.gridZ * params.ellipseRadiusZ * 0.3;
            centerX += Math.cos(ellipseAngle) * ellipseRX;
            centerZ += Math.sin(ellipseAngle) * ellipseRZ;
        }

        // 8. Continuous scroll - use offset variables
        let scrollOffsetX = 0;
        let scrollOffsetY = 0;
        let scrollOffsetZ = 0;

        if (params.scrollSpeed > 0) {
            const scrollAmount = time * params.scrollSpeed * 2;
            switch (params.scrollDirection) {
                case 'x':
                    scrollOffsetX = scrollAmount;
                    break;
                case 'y':
                    scrollOffsetY = scrollAmount;
                    break;
                case 'z':
                    scrollOffsetZ = scrollAmount;
                    break;
                case 'diagonal':
                    scrollOffsetX = scrollAmount;
                    scrollOffsetZ = scrollAmount;
                    break;
            }
        }

        // 9. Rotation angles
        let rotX = time * (params.rotationX || 0) * 0.5;
        let rotY = time * (params.rotationY || 0) * 0.5;
        let rotZ = time * (params.rotationZ || 0) * 0.5;

        // 10. Wobble
        if (params.wobbleSpeed > 0 && params.wobbleAmount > 0) {
            const wobbleAmount = params.wobbleAmount * 0.3;
            rotX += Math.sin(time * params.wobbleSpeed * 2.3) * wobbleAmount;
            rotY += Math.sin(time * params.wobbleSpeed * 1.7) * wobbleAmount;
            rotZ += Math.sin(time * params.wobbleSpeed * 2.9) * wobbleAmount;
        }

        // For linear arrangement with scrolling, render multiple copies to create seamless loop
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed > 0) ? 2 : 1;

        // Draw multiple toruses distributed around center
        for (let copyIdx = 0; copyIdx < renderCopies; copyIdx++) {
            for (let torusIdx = 0; torusIdx < numToruses; torusIdx++) {
                let torusCenterX = centerX;
                let torusCenterY = centerY;
                let torusCenterZ = centerZ;

                if (numToruses > 1) {
                    if (params.objectArrangement === 'linear') {
                        // Linear/trailing arrangement
                        const spacing = baseMajorRadius * 3;
                        const offset = torusIdx * spacing;
                        switch (params.scrollDirection) {
                            case 'x':
                                torusCenterX = centerX - offset;
                                break;
                            case 'y':
                                torusCenterY = centerY - offset;
                                break;
                            case 'z':
                                torusCenterZ = centerZ - offset;
                                break;
                            case 'diagonal':
                            default:
                                torusCenterX = centerX - offset;
                                torusCenterZ = centerZ - offset;
                                break;
                        }
                    } else {
                        // Circular arrangement (default)
                        const angleOffset = (torusIdx / numToruses) * Math.PI * 2;
                        const distributionRadius = baseMajorRadius * 0.8;
                        torusCenterX = centerX + Math.cos(angleOffset) * distributionRadius;
                        torusCenterZ = centerZ + Math.sin(angleOffset) * distributionRadius;
                    }
                }

                // Apply scroll offset
                torusCenterX += scrollOffsetX;
                torusCenterY += scrollOffsetY;
                torusCenterZ += scrollOffsetZ;

                // For seamless looping, add offset for duplicate copy
                if (params.objectArrangement === 'linear' && renderCopies > 1 && copyIdx > 0) {
                    const totalWrapDistance = (baseMajorRadius * 3) * numToruses;
                    switch (params.scrollDirection) {
                        case 'x':
                            torusCenterX -= totalWrapDistance;
                            break;
                        case 'y':
                            torusCenterY -= totalWrapDistance;
                            break;
                        case 'z':
                            torusCenterZ -= totalWrapDistance;
                            break;
                        case 'diagonal':
                            torusCenterX -= totalWrapDistance;
                            torusCenterZ -= totalWrapDistance;
                            break;
                    }
                }

                // Modulo wrap to keep values in reasonable range
                if (params.objectArrangement === 'linear' && numToruses > 1) {
                    const totalWrapDistance = (baseMajorRadius * 3) * numToruses;
                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        torusCenterX = centerX + ((torusCenterX - centerX) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'y') {
                        torusCenterY = centerY + ((torusCenterY - centerY) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        torusCenterZ = centerZ + ((torusCenterZ - centerZ) % totalWrapDistance);
                    }
                }

                for (let x = 0; x < this.gridX; x++) {
                    for (let y = 0; y < this.gridY; y++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            // Get position relative to torus center
                            let dx = x - torusCenterX;
                            let dy = (y - torusCenterY) * 2;
                            let dz = z - torusCenterZ;

                            // Apply 3D rotations around the LOCAL torus center
                            if (rotX !== 0) {
                                const tempY = dy;
                                const tempZ = dz;
                                dy = tempY * Math.cos(rotX) - tempZ * Math.sin(rotX);
                                dz = tempY * Math.sin(rotX) + tempZ * Math.cos(rotX);
                            }
                            if (rotY !== 0) {
                                const tempX = dx;
                                const tempZ = dz;
                                dx = tempX * Math.cos(rotY) + tempZ * Math.sin(rotY);
                                dz = -tempX * Math.sin(rotY) + tempZ * Math.cos(rotY);
                            }
                            if (rotZ !== 0) {
                                const tempX = dx;
                                const tempY = dy;
                                dx = tempX * Math.cos(rotZ) - tempY * Math.sin(rotZ);
                                dy = tempX * Math.sin(rotZ) + tempY * Math.cos(rotZ);
                            }

                            // Torus equation
                            const distFromAxis = Math.sqrt(dx * dx + dz * dz);
                            const torusDistance = Math.sqrt(
                                Math.pow(distFromAxis - baseMajorRadius, 2) + dy * dy
                            );

                            if (torusDistance < baseMinorRadius) {
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                            }
                        }
                    }
                }
            }
        }
    }

    drawCube(voxels, time, params) {
        const numCubes = Math.max(1, params.objectCount);
        let baseSize = 10 + params.size * 10;
        let baseThickness = params.thickness * baseSize * 0.9;

        // Center position with movement
        let centerX = this.gridX / 2;
        let centerY = this.gridY / 2;
        let centerZ = this.gridZ / 2;

        // Apply STACKABLE transformations
        // 1. Pulse (size modulation)
        if (params.pulseSpeed > 0 && params.pulseAmount > 0) {
            const pulse = (Math.sin(time * params.pulseSpeed * 3) + 1) / 2;
            const pulseRange = params.pulseAmount * 0.5;
            baseSize = baseSize * (1 - pulseRange + pulse * pulseRange * 2);
        }

        // 2. Translation
        if (params.translateX > 0 && params.translateAmplitude > 0) {
            centerX += Math.sin(time * params.translateX * 2) * (this.gridX * params.translateAmplitude * 0.3);
        }
        if (params.translateY > 0 && params.translateAmplitude > 0) {
            centerY += Math.sin(time * params.translateY * 2) * (this.gridY * params.translateAmplitude * 0.3);
        }
        if (params.translateZ > 0 && params.translateAmplitude > 0) {
            centerZ += Math.cos(time * params.translateZ * 2) * (this.gridZ * params.translateAmplitude * 0.3);
        }

        // 3. Orbit
        if (params.orbitSpeed > 0 && params.orbitRadius > 0) {
            const angle = time * params.orbitSpeed * 2;
            const orbitR = this.gridX * params.orbitRadius * 0.3;
            centerX += Math.cos(angle) * orbitR;
            centerZ += Math.sin(angle) * orbitR;
        }

        // 4. Bounce
        if (params.bounceSpeed > 0 && params.bounceHeight > 0) {
            centerY += Math.abs(Math.sin(time * params.bounceSpeed * 3)) * (this.gridY * params.bounceHeight * 0.4);
        }

        // 5. Spiral
        if (params.spiralSpeed > 0 && params.spiralRadius > 0) {
            const spiralAngle = time * params.spiralSpeed * 2;
            const spiralR = this.gridX * params.spiralRadius * 0.3;
            centerX += Math.cos(spiralAngle) * spiralR;
            centerZ += Math.sin(spiralAngle) * spiralR;
            if (params.spiralHeight > 0) {
                centerY += Math.sin(spiralAngle) * (this.gridY * params.spiralHeight * 0.3);
            }
        }

        // 6. Figure-8
        if (params.figure8Speed > 0 && params.figure8Size > 0) {
            const fig8Angle = time * params.figure8Speed * 2;
            const fig8Scale = this.gridX * params.figure8Size * 0.3;
            centerX += Math.cos(fig8Angle) * fig8Scale;
            centerZ += Math.sin(fig8Angle) * Math.cos(fig8Angle) * fig8Scale;
        }

        // 7. Elliptical orbit
        if (params.ellipseSpeed > 0 && (params.ellipseRadiusX > 0 || params.ellipseRadiusZ > 0)) {
            const ellipseAngle = time * params.ellipseSpeed * 2;
            const ellipseRX = this.gridX * params.ellipseRadiusX * 0.3;
            const ellipseRZ = this.gridZ * params.ellipseRadiusZ * 0.3;
            centerX += Math.cos(ellipseAngle) * ellipseRX;
            centerZ += Math.sin(ellipseAngle) * ellipseRZ;
        }

        // 8. Continuous scroll - use offset variables
        let scrollOffsetX = 0;
        let scrollOffsetY = 0;
        let scrollOffsetZ = 0;

        if (params.scrollSpeed > 0) {
            const scrollAmount = time * params.scrollSpeed * 2;
            switch (params.scrollDirection) {
                case 'x':
                    scrollOffsetX = scrollAmount;
                    break;
                case 'y':
                    scrollOffsetY = scrollAmount;
                    break;
                case 'z':
                    scrollOffsetZ = scrollAmount;
                    break;
                case 'diagonal':
                    scrollOffsetX = scrollAmount;
                    scrollOffsetZ = scrollAmount;
                    break;
            }
        }

        // 9. Rotation angles
        let rotX = time * (params.rotationX || 0) * 0.5;
        let rotY = time * (params.rotationY || 0) * 0.5;
        let rotZ = time * (params.rotationZ || 0) * 0.5;

        // 10. Wobble
        if (params.wobbleSpeed > 0 && params.wobbleAmount > 0) {
            const wobbleAmount = params.wobbleAmount * 0.3;
            rotX += Math.sin(time * params.wobbleSpeed * 2.3) * wobbleAmount;
            rotY += Math.sin(time * params.wobbleSpeed * 1.7) * wobbleAmount;
            rotZ += Math.sin(time * params.wobbleSpeed * 2.9) * wobbleAmount;
        }

        // For linear arrangement with scrolling, render multiple copies to create seamless loop
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed > 0) ? 2 : 1;

        // Draw multiple cubes distributed around center
        for (let copyIdx = 0; copyIdx < renderCopies; copyIdx++) {
            for (let cubeIdx = 0; cubeIdx < numCubes; cubeIdx++) {
                let cubeCenterX = centerX;
                let cubeCenterY = centerY;
                let cubeCenterZ = centerZ;

                if (numCubes > 1) {
                    if (params.objectArrangement === 'linear') {
                        // Linear/trailing arrangement
                        const spacing = baseSize * 3;
                        const offset = cubeIdx * spacing;
                        switch (params.scrollDirection) {
                            case 'x':
                                cubeCenterX = centerX - offset;
                                break;
                            case 'y':
                                cubeCenterY = centerY - offset;
                                break;
                            case 'z':
                                cubeCenterZ = centerZ - offset;
                                break;
                            case 'diagonal':
                            default:
                                cubeCenterX = centerX - offset;
                                cubeCenterZ = centerZ - offset;
                                break;
                        }
                    } else {
                        // Circular arrangement (default)
                        const angleOffset = (cubeIdx / numCubes) * Math.PI * 2;
                        const distributionRadius = baseSize * 1.2;
                        cubeCenterX = centerX + Math.cos(angleOffset) * distributionRadius;
                        cubeCenterZ = centerZ + Math.sin(angleOffset) * distributionRadius;
                    }
                }

                // Apply scroll offset
                cubeCenterX += scrollOffsetX;
                cubeCenterY += scrollOffsetY;
                cubeCenterZ += scrollOffsetZ;

                // For seamless looping, add offset for duplicate copy
                if (params.objectArrangement === 'linear' && renderCopies > 1 && copyIdx > 0) {
                    const totalWrapDistance = (baseSize * 3) * numCubes;
                    switch (params.scrollDirection) {
                        case 'x':
                            cubeCenterX -= totalWrapDistance;
                            break;
                        case 'y':
                            cubeCenterY -= totalWrapDistance;
                            break;
                        case 'z':
                            cubeCenterZ -= totalWrapDistance;
                            break;
                        case 'diagonal':
                            cubeCenterX -= totalWrapDistance;
                            cubeCenterZ -= totalWrapDistance;
                            break;
                    }
                }

                // Modulo wrap to keep values in reasonable range
                if (params.objectArrangement === 'linear' && numCubes > 1) {
                    const totalWrapDistance = (baseSize * 3) * numCubes;
                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        cubeCenterX = centerX + ((cubeCenterX - centerX) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'y') {
                        cubeCenterY = centerY + ((cubeCenterY - centerY) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        cubeCenterZ = centerZ + ((cubeCenterZ - centerZ) % totalWrapDistance);
                    }
                }

                for (let x = 0; x < this.gridX; x++) {
                    for (let y = 0; y < this.gridY; y++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            // Get position relative to cube center
                            let dx = x - cubeCenterX;
                            let dy = (y - cubeCenterY) * 2;
                            let dz = z - cubeCenterZ;

                            // Apply 3D rotations around the LOCAL cube center
                            if (rotX !== 0) {
                                const tempY = dy;
                                const tempZ = dz;
                                dy = tempY * Math.cos(rotX) - tempZ * Math.sin(rotX);
                                dz = tempY * Math.sin(rotX) + tempZ * Math.cos(rotX);
                            }
                            if (rotY !== 0) {
                                const tempX = dx;
                                const tempZ = dz;
                                dx = tempX * Math.cos(rotY) + tempZ * Math.sin(rotY);
                                dz = -tempX * Math.sin(rotY) + tempZ * Math.cos(rotY);
                            }
                            if (rotZ !== 0) {
                                const tempX = dx;
                                const tempY = dy;
                                dx = tempX * Math.cos(rotZ) - tempY * Math.sin(rotZ);
                                dy = tempX * Math.sin(rotZ) + tempY * Math.cos(rotZ);
                            }

                            // Check if inside cube but outside inner cube (hollow)
                            const isOutside = Math.abs(dx) <= baseSize && Math.abs(dy) <= baseSize && Math.abs(dz) <= baseSize;
                            const isInside = Math.abs(dx) <= baseSize - baseThickness &&
                                           Math.abs(dy) <= baseSize - baseThickness &&
                                           Math.abs(dz) <= baseSize - baseThickness;

                            if (isOutside && !isInside) {
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                            }
                        }
                    }
                }
            }
        }
    }

    drawPyramid(voxels, time, params) {
        const numPyramids = Math.max(1, params.objectCount);
        let baseBaseSize = 12 + params.size * 8;
        const height = this.gridY * 0.8;
        let baseThickness = 1 + params.thickness * 2;

        // Center position with movement
        let centerX = this.gridX / 2;
        let centerY = this.gridY / 2;
        let centerZ = this.gridZ / 2;

        // Apply STACKABLE transformations
        // 1. Pulse
        if (params.pulseSpeed > 0 && params.pulseAmount > 0) {
            const pulse = (Math.sin(time * params.pulseSpeed * 3) + 1) / 2;
            const pulseRange = params.pulseAmount * 0.5;
            baseBaseSize = baseBaseSize * (1 - pulseRange + pulse * pulseRange * 2);
        }

        // 2. Translation
        if (params.translateX > 0 && params.translateAmplitude > 0) {
            centerX += Math.sin(time * params.translateX * 2) * (this.gridX * params.translateAmplitude * 0.3);
        }
        if (params.translateY > 0 && params.translateAmplitude > 0) {
            centerY += Math.sin(time * params.translateY * 2) * (this.gridY * params.translateAmplitude * 0.3);
        }
        if (params.translateZ > 0 && params.translateAmplitude > 0) {
            centerZ += Math.cos(time * params.translateZ * 2) * (this.gridZ * params.translateAmplitude * 0.3);
        }

        // 3. Orbit
        if (params.orbitSpeed > 0 && params.orbitRadius > 0) {
            const angle = time * params.orbitSpeed * 2;
            const orbitR = this.gridX * params.orbitRadius * 0.3;
            centerX += Math.cos(angle) * orbitR;
            centerZ += Math.sin(angle) * orbitR;
        }

        // 4. Bounce
        if (params.bounceSpeed > 0 && params.bounceHeight > 0) {
            centerY += Math.abs(Math.sin(time * params.bounceSpeed * 3)) * (this.gridY * params.bounceHeight * 0.4);
        }

        // 5. Spiral
        if (params.spiralSpeed > 0 && params.spiralRadius > 0) {
            const spiralAngle = time * params.spiralSpeed * 2;
            const spiralR = this.gridX * params.spiralRadius * 0.3;
            centerX += Math.cos(spiralAngle) * spiralR;
            centerZ += Math.sin(spiralAngle) * spiralR;
            if (params.spiralHeight > 0) {
                centerY += Math.sin(spiralAngle) * (this.gridY * params.spiralHeight * 0.3);
            }
        }

        // 6. Figure-8
        if (params.figure8Speed > 0 && params.figure8Size > 0) {
            const fig8Angle = time * params.figure8Speed * 2;
            const fig8Scale = this.gridX * params.figure8Size * 0.3;
            centerX += Math.cos(fig8Angle) * fig8Scale;
            centerZ += Math.sin(fig8Angle) * Math.cos(fig8Angle) * fig8Scale;
        }

        // 7. Elliptical orbit
        if (params.ellipseSpeed > 0 && (params.ellipseRadiusX > 0 || params.ellipseRadiusZ > 0)) {
            const ellipseAngle = time * params.ellipseSpeed * 2;
            const ellipseRX = this.gridX * params.ellipseRadiusX * 0.3;
            const ellipseRZ = this.gridZ * params.ellipseRadiusZ * 0.3;
            centerX += Math.cos(ellipseAngle) * ellipseRX;
            centerZ += Math.sin(ellipseAngle) * ellipseRZ;
        }

        // 8. Continuous scroll - use offset variables
        let scrollOffsetX = 0;
        let scrollOffsetY = 0;
        let scrollOffsetZ = 0;

        if (params.scrollSpeed > 0) {
            const scrollAmount = time * params.scrollSpeed * 2;
            switch (params.scrollDirection) {
                case 'x':
                    scrollOffsetX = scrollAmount;
                    break;
                case 'y':
                    scrollOffsetY = scrollAmount;
                    break;
                case 'z':
                    scrollOffsetZ = scrollAmount;
                    break;
                case 'diagonal':
                    scrollOffsetX = scrollAmount;
                    scrollOffsetZ = scrollAmount;
                    break;
            }
        }

        // 9. Rotation angles
        let rotX = time * (params.rotationX || 0) * 0.5;
        let rotY = time * (params.rotationY || 0) * 0.5;
        let rotZ = time * (params.rotationZ || 0) * 0.5;

        // 10. Wobble
        if (params.wobbleSpeed > 0 && params.wobbleAmount > 0) {
            const wobbleAmount = params.wobbleAmount * 0.3;
            rotX += Math.sin(time * params.wobbleSpeed * 2.3) * wobbleAmount;
            rotY += Math.sin(time * params.wobbleSpeed * 1.7) * wobbleAmount;
            rotZ += Math.sin(time * params.wobbleSpeed * 2.9) * wobbleAmount;
        }

        // For linear arrangement with scrolling, render multiple copies to create seamless loop
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed > 0) ? 2 : 1;

        // Draw multiple pyramids distributed around center
        for (let copyIdx = 0; copyIdx < renderCopies; copyIdx++) {
            for (let pyrIdx = 0; pyrIdx < numPyramids; pyrIdx++) {
                let pyrCenterX = centerX;
                let pyrCenterY = centerY;
                let pyrCenterZ = centerZ;

                if (numPyramids > 1) {
                    if (params.objectArrangement === 'linear') {
                        // Linear/trailing arrangement
                        const spacing = baseBaseSize * 3;
                        const offset = pyrIdx * spacing;
                        switch (params.scrollDirection) {
                            case 'x':
                                pyrCenterX = centerX - offset;
                                break;
                            case 'y':
                                pyrCenterY = centerY - offset;
                                break;
                            case 'z':
                                pyrCenterZ = centerZ - offset;
                                break;
                            case 'diagonal':
                            default:
                                pyrCenterX = centerX - offset;
                                pyrCenterZ = centerZ - offset;
                                break;
                        }
                    } else {
                        // Circular arrangement (default)
                        const angleOffset = (pyrIdx / numPyramids) * Math.PI * 2;
                        const distributionRadius = baseBaseSize * 1.2;
                        pyrCenterX = centerX + Math.cos(angleOffset) * distributionRadius;
                        pyrCenterZ = centerZ + Math.sin(angleOffset) * distributionRadius;
                    }
                }

                // Apply scroll offset
                pyrCenterX += scrollOffsetX;
                pyrCenterY += scrollOffsetY;
                pyrCenterZ += scrollOffsetZ;

                // For seamless looping, add offset for duplicate copy
                if (params.objectArrangement === 'linear' && renderCopies > 1 && copyIdx > 0) {
                    const totalWrapDistance = (baseBaseSize * 3) * numPyramids;
                    switch (params.scrollDirection) {
                        case 'x':
                            pyrCenterX -= totalWrapDistance;
                            break;
                        case 'y':
                            pyrCenterY -= totalWrapDistance;
                            break;
                        case 'z':
                            pyrCenterZ -= totalWrapDistance;
                            break;
                        case 'diagonal':
                            pyrCenterX -= totalWrapDistance;
                            pyrCenterZ -= totalWrapDistance;
                            break;
                    }
                }

                // Modulo wrap to keep values in reasonable range
                if (params.objectArrangement === 'linear' && numPyramids > 1) {
                    const totalWrapDistance = (baseBaseSize * 3) * numPyramids;
                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        pyrCenterX = centerX + ((pyrCenterX - centerX) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'y') {
                        pyrCenterY = centerY + ((pyrCenterY - centerY) % totalWrapDistance);
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        pyrCenterZ = centerZ + ((pyrCenterZ - centerZ) % totalWrapDistance);
                    }
                }

                for (let x = 0; x < this.gridX; x++) {
                    for (let y = 0; y < this.gridY; y++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            // Get position relative to pyramid base center
                            let dx = x - pyrCenterX;
                            let dy = y - (pyrCenterY - height / 2);
                            let dz = z - pyrCenterZ;

                            // Apply 3D rotations
                            if (rotX !== 0) {
                                const tempY = dy;
                                const tempZ = dz;
                                dy = tempY * Math.cos(rotX) - tempZ * Math.sin(rotX);
                                dz = tempY * Math.sin(rotX) + tempZ * Math.cos(rotX);
                            }
                            if (rotY !== 0) {
                                const tempX = dx;
                                const tempZ = dz;
                                dx = tempX * Math.cos(rotY) + tempZ * Math.sin(rotY);
                                dz = -tempX * Math.sin(rotY) + tempZ * Math.cos(rotY);
                            }
                            if (rotZ !== 0) {
                                const tempX = dx;
                                const tempY = dy;
                                dx = tempX * Math.cos(rotZ) - tempY * Math.sin(rotZ);
                                dy = tempX * Math.sin(rotZ) + tempY * Math.cos(rotZ);
                            }

                            // Height ratio
                            const heightRatio = dy / height;
                            const currentSize = baseBaseSize * (1 - heightRatio);
                            const dist = Math.sqrt(dx * dx + dz * dz);

                            if (dy >= 0 && dy < height && Math.abs(dist - currentSize) < baseThickness) {
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================================================
    // PARTICLE FLOW
    // ============================================================================
    renderParticleFlow(voxels, time, params) {
        voxels.fill(0);

        // Calculate movement offsets that will be applied to all particles
        const movement = this.calculateParticleMovement(time, params);

        // Pass movement to pattern renderers
        const patterns = {
            'rain': () => this.flowRain(voxels, params, movement),
            'stars': () => this.flowStars(voxels, params, movement),
            'fountain': () => this.flowFountain(voxels, params, movement),
            'spiral': () => this.flowSpiral(voxels, time, params, movement),
            'explode': () => this.flowExplode(voxels, time, params, movement)
        };

        const flowFn = patterns[params.pattern] || patterns['rain'];
        flowFn();
    }

    /**
     * Calculate movement transformations for particle flow
     */
    calculateParticleMovement(time, params) {
        const centerX = this.gridX / 2;
        const centerY = this.gridY / 2;
        const centerZ = this.gridZ / 2;

        let offsetX = 0;
        let offsetY = 0;
        let offsetZ = 0;

        // 1. Translation (side-to-side oscillation)
        if (params.translateX > 0 && params.translateAmplitude > 0) {
            offsetX += Math.sin(time * params.translateX * 2) * params.translateAmplitude * 10;
        }
        if (params.translateZ > 0 && params.translateAmplitude > 0) {
            offsetZ += Math.sin(time * params.translateZ * 2) * params.translateAmplitude * 10;
        }

        // 2. Bounce (vertical oscillation)
        if (params.bounceSpeed > 0 && params.bounceHeight > 0) {
            offsetY += Math.abs(Math.sin(time * params.bounceSpeed * 3)) * params.bounceHeight * 8;
        }

        // 3. Orbit (circular motion in XZ plane)
        if (params.orbitSpeed > 0 && params.orbitRadius > 0) {
            const angle = time * params.orbitSpeed * 2;
            const radius = params.orbitRadius * 10;
            offsetX += Math.cos(angle) * radius;
            offsetZ += Math.sin(angle) * radius;
        }

        // 4. Spiral (3D spiral motion)
        if (params.spiralSpeed > 0 && (params.spiralRadius > 0 || params.spiralHeight > 0)) {
            const angle = time * params.spiralSpeed * 2;
            const radius = params.spiralRadius * 8;
            offsetX += Math.cos(angle) * radius;
            offsetZ += Math.sin(angle) * radius;
            offsetY += (Math.sin(time * params.spiralSpeed * 1.5) * params.spiralHeight * 5);
        }

        // 5. Figure-8 motion
        if (params.figure8Speed > 0 && params.figure8Size > 0) {
            const t = time * params.figure8Speed * 2;
            const size = params.figure8Size * 8;
            offsetX += Math.sin(t) * size;
            offsetZ += Math.sin(t * 2) * size * 0.5;
        }

        // 6. Elliptical orbit
        if (params.ellipseSpeed > 0 && (params.ellipseRadiusX > 0 || params.ellipseRadiusZ > 0)) {
            const angle = time * params.ellipseSpeed * 2;
            offsetX += Math.cos(angle) * params.ellipseRadiusX * 10;
            offsetZ += Math.sin(angle) * params.ellipseRadiusZ * 10;
        }

        // 7. Wobble (random-ish motion)
        if (params.wobbleSpeed > 0 && params.wobbleAmount > 0) {
            const wobbleAmount = params.wobbleAmount * 5;
            offsetX += Math.sin(time * params.wobbleSpeed * 2.3) * wobbleAmount;
            offsetY += Math.sin(time * params.wobbleSpeed * 1.7) * wobbleAmount;
            offsetZ += Math.sin(time * params.wobbleSpeed * 2.9) * wobbleAmount;
        }

        // 8. Continuous scroll
        if (params.scrollSpeed > 0) {
            const scrollAmount = (time * params.scrollSpeed * 15) % (this.gridX + this.gridZ);
            switch (params.scrollDirection) {
                case 'x':
                    offsetX += scrollAmount;
                    break;
                case 'y':
                    offsetY += scrollAmount % this.gridY;
                    break;
                case 'z':
                    offsetZ += scrollAmount;
                    break;
                case 'diagonal':
                    offsetX += scrollAmount * 0.7;
                    offsetZ += scrollAmount * 0.7;
                    break;
            }
        }

        return { offsetX, offsetY, offsetZ };
    }

    /**
     * Helper function to draw a particle with size
     */
    drawParticle(voxels, centerX, centerY, centerZ, size) {
        const radius = Math.max(0, size - 1);

        if (size === 1) {
            // Single voxel (fast path)
            const x = Math.floor(centerX);
            const y = Math.floor(centerY);
            const z = Math.floor(centerZ);
            if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
            }
        } else {
            // Multi-voxel particle (draw a small sphere)
            const cx = Math.floor(centerX);
            const cy = Math.floor(centerY);
            const cz = Math.floor(centerZ);

            for (let dx = -radius; dx <= radius; dx++) {
                for (let dy = -radius; dy <= radius; dy++) {
                    for (let dz = -radius; dz <= radius; dz++) {
                        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
                        if (dist <= radius) {
                            const x = cx + dx;
                            const y = cy + dy;
                            const z = cz + dz;
                            if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                            }
                        }
                    }
                }
            }
        }
    }

    flowRain(voxels, params, movement) {
        this.rainSystem.update(params.velocity);

        this.rainSystem.getParticles().forEach(p => {
            this.drawParticle(voxels,
                p.x + movement.offsetX,
                p.y + movement.offsetY,
                p.z + movement.offsetZ,
                params.particleSize);
        });
    }

    flowStars(voxels, params, movement) {
        this.starSystem.update(params.velocity);

        this.starSystem.getParticles().forEach(p => {
            this.drawParticle(voxels,
                p.x + movement.offsetX,
                p.y + movement.offsetY,
                p.z + movement.offsetZ,
                params.particleSize);
        });
    }

    flowFountain(voxels, params, movement) {
        // Similar to rain but particles move upward
        // For now, reuse rain system but could create dedicated fountain system
        this.rainSystem.update(params.velocity);

        this.rainSystem.getParticles().forEach(p => {
            // Flip Y coordinate for upward motion
            const x = p.x + movement.offsetX;
            const y = this.gridY - 1 - p.y + movement.offsetY;
            const z = p.z + movement.offsetZ;
            this.drawParticle(voxels, x, y, z, params.particleSize);
        });
    }

    flowSpiral(voxels, time, params, movement) {
        // Generate spiral particle motion
        const particleCount = Math.floor(params.density * 500);

        for (let i = 0; i < particleCount; i++) {
            const t = (time * params.velocity + i * 0.1) % (Math.PI * 4);
            const radius = (t / (Math.PI * 4)) * this.gridX / 2;
            const angle = t * 3;

            const x = this.gridX / 2 + Math.cos(angle) * radius + movement.offsetX;
            const z = this.gridZ / 2 + Math.sin(angle) * radius + movement.offsetZ;
            const y = (t / (Math.PI * 4)) * this.gridY + movement.offsetY;

            this.drawParticle(voxels, x, y, z, params.particleSize);
        }
    }

    flowExplode(voxels, time, params, movement) {
        // Particles explode outward from center
        const particleCount = Math.floor(params.density * 300);

        for (let i = 0; i < particleCount; i++) {
            const angle1 = (i * 2.4) % (Math.PI * 2);
            const angle2 = (i * 1.7) % Math.PI;
            const expansion = ((time * params.velocity) % 3) * 10;

            const x = this.gridX / 2 + Math.cos(angle1) * Math.sin(angle2) * expansion + movement.offsetX;
            const y = this.gridY / 2 + Math.cos(angle2) * expansion + movement.offsetY;
            const z = this.gridZ / 2 + Math.sin(angle1) * Math.sin(angle2) * expansion + movement.offsetZ;

            this.drawParticle(voxels, x, y, z, params.particleSize);
        }
    }

    // ============================================================================
    // WAVE FIELD
    // ============================================================================
    renderWaveField(voxels, time, params) {
        const waveTypes = {
            'ripple': () => this.waveRipple(voxels, time, params),
            'plane': () => this.wavePlane(voxels, time, params),
            'standing': () => this.waveStanding(voxels, time, params),
            'interference': () => this.waveInterference(voxels, time, params),
            'plasma': () => this.wavePlasma(voxels, time, params)
        };

        const waveFn = waveTypes[params.waveType] || waveTypes['ripple'];
        waveFn();
    }

    waveRipple(voxels, time, params) {
        const centerX = this.gridX / 2;
        const centerZ = this.gridZ / 2;
        const halfY = this.gridY / 2;
        const waveAmplitude = 2 + params.amplitude * 3;
        const timePhase = time * 2;
        const freq = 0.3 * params.frequency;
        const threshold = 1.5;
        const gridStride = this.gridX * this.gridY;

        for (let x = 0; x < this.gridX; x++) {
            const dx = x - centerX;
            const dx2 = dx * dx; // Cache squared value

            for (let z = 0; z < this.gridZ; z++) {
                const dz = z - centerZ;
                const dist = Math.sqrt(dx2 + dz * dz);
                const wave = Math.sin(dist * freq - timePhase) * waveAmplitude;
                const yPos = halfY + wave;

                const yMin = Math.max(0, Math.floor(yPos - threshold));
                const yMax = Math.min(this.gridY - 1, Math.ceil(yPos + threshold));

                // Only iterate over the range where voxels will be active
                for (let y = yMin; y <= yMax; y++) {
                    voxels[x + y * this.gridX + z * gridStride] =
                        Math.abs(y - yPos) < threshold ? 1 : 0;
                }
            }
        }
    }

    wavePlane(voxels, time, params) {
        // Directional wave based on direction parameter
        const directions = {
            'x': (x, y, z) => x,
            'y': (x, y, z) => y,
            'z': (x, y, z) => z,
            'diagonal': (x, y, z) => x + z,
            'radial': (x, y, z) => Math.sqrt(
                Math.pow(x - this.gridX/2, 2) + Math.pow(z - this.gridZ/2, 2)
            )
        };

        const dirFn = directions[params.direction] || directions['x'];

        const progress = (Math.sin(time * 0.5) + 1) / 2;
        const sweepPos = progress * (this.gridX + this.gridY + this.gridZ);
        const thickness = 3 + params.amplitude * 4;

        for (let x = 0; x < this.gridX; x++) {
            for (let y = 0; y < this.gridY; y++) {
                for (let z = 0; z < this.gridZ; z++) {
                    const pos = dirFn(x, y, z);
                    voxels[x + y * this.gridX + z * this.gridX * this.gridY] =
                        Math.abs(pos - sweepPos * params.frequency) < thickness ? 1 : 0;
                }
            }
        }
    }

    waveStanding(voxels, time, params) {
        // Standing wave pattern - pre-calculate sine values
        const freq = 0.3 * params.frequency;
        const timeSin = Math.sin(time);
        const threshold = 0.5;
        const gridStride = this.gridX * this.gridY;

        // Pre-calculate sine values for x and z
        const sinX = new Array(this.gridX);
        const sinZ = new Array(this.gridZ);

        for (let x = 0; x < this.gridX; x++) {
            sinX[x] = Math.sin(x * freq);
        }
        for (let z = 0; z < this.gridZ; z++) {
            sinZ[z] = Math.sin(z * freq);
        }

        // Calculate wave pattern
        for (let x = 0; x < this.gridX; x++) {
            const sX = sinX[x];

            for (let z = 0; z < this.gridZ; z++) {
                const wave = sX * sinZ[z] * timeSin;
                const value = (wave + 1) * 0.5 * params.amplitude;
                const isActive = value > threshold ? 1 : 0;

                // Set same value for entire Y column
                for (let y = 0; y < this.gridY; y++) {
                    voxels[x + y * this.gridX + z * gridStride] = isActive;
                }
            }
        }
    }

    waveInterference(voxels, time, params) {
        // Multiple wave sources creating interference pattern
        const sources = [
            { x: this.gridX * 0.3, z: this.gridZ * 0.3 },
            { x: this.gridX * 0.7, z: this.gridZ * 0.7 }
        ];

        const halfY = this.gridY / 2;
        const waveAmplitude = 2 + params.amplitude * 3;
        const timePhase = time * 2;
        const freq = 0.3 * params.frequency;
        const threshold = 1.5;
        const gridStride = this.gridX * this.gridY;
        const sourceCount = sources.length;

        for (let x = 0; x < this.gridX; x++) {
            for (let z = 0; z < this.gridZ; z++) {
                let totalWave = 0;

                // Unroll source loop for performance (only 2 sources)
                const dx1 = x - sources[0].x;
                const dz1 = z - sources[0].z;
                const dist1 = Math.sqrt(dx1 * dx1 + dz1 * dz1);
                totalWave += Math.sin(dist1 * freq - timePhase);

                const dx2 = x - sources[1].x;
                const dz2 = z - sources[1].z;
                const dist2 = Math.sqrt(dx2 * dx2 + dz2 * dz2);
                totalWave += Math.sin(dist2 * freq - timePhase);

                const wave = (totalWave / sourceCount) * waveAmplitude;
                const yPos = halfY + wave;

                const yMin = Math.max(0, Math.floor(yPos - threshold));
                const yMax = Math.min(this.gridY - 1, Math.ceil(yPos + threshold));

                // Only iterate over active range
                for (let y = yMin; y <= yMax; y++) {
                    voxels[x + y * this.gridX + z * gridStride] =
                        Math.abs(y - yPos) < threshold ? 1 : 0;
                }
            }
        }
    }

    wavePlasma(voxels, time, params) {
        // Plasma wave - volumetric sine wave interference pattern
        // Uses waveField parameters: frequency (complexity), amplitude (threshold)
        const scale = 0.1; // Fixed scale for plasma effect
        const threshold = params.amplitude; // Map amplitude to threshold
        const complexity = params.frequency; // Map frequency to complexity
        const layers = 2; // Fixed layer count

        let idx = 0;
        for (let z = 0; z < this.gridZ; z++) {
            for (let y = 0; y < this.gridY; y++) {
                for (let x = 0; x < this.gridX; x++) {
                    let value = 0;

                    // Multiple sine waves for plasma effect
                    value += Math.sin((x * scale + time) * complexity);
                    value += Math.sin((y * scale + time * 0.8) * complexity);
                    value += Math.sin((z * scale + time * 0.6) * complexity);
                    value += Math.sin(Math.sqrt(x * x + y * y) * scale * complexity + time);

                    if (layers > 1) {
                        value += Math.sin((x + y) * scale * 0.5 + time * 1.2) * 0.5;
                    }
                    if (layers > 2) {
                        value += Math.sin((y + z) * scale * 0.5 + time * 0.9) * 0.5;
                    }

                    // Normalize and threshold
                    value = (value + 4) / 8;
                    voxels[idx++] = value > threshold ? 1 : 0;
                }
            }
        }
    }

    // ============================================================================
    // PROCEDURAL VOLUME
    // ============================================================================
    renderProcedural(voxels, time, params) {
        const scale = params.scale;
        const threshold = params.threshold;
        const gridStride = this.gridX * this.gridY;
        let timeOffset = 0;

        if (params.animationType === 'scroll') {
            timeOffset = time * 0.1;
        } else if (params.animationType === 'evolve') {
            timeOffset = time * 0.05;
        }

        const octaves = params.octaves;
        const useOctaves = octaves > 1;
        const normalizeFactor = useOctaves ? (2 - Math.pow(0.5, octaves)) : 1;

        let idx = 0;
        for (let z = 0; z < this.gridZ; z++) {
            const zScaled = z * scale + timeOffset;

            for (let y = 0; y < this.gridY; y++) {
                const yScaled = y * scale;

                for (let x = 0; x < this.gridX; x++) {
                    const xScaled = x * scale;
                    let noise = this.perlin.noise(xScaled, yScaled, zScaled);

                    // Apply octaves for fractal detail
                    if (useOctaves) {
                        let amplitude = 0.5;
                        let frequency = 2;
                        for (let o = 1; o < octaves; o++) {
                            noise += this.perlin.noise(
                                xScaled * frequency,
                                yScaled * frequency,
                                zScaled * frequency
                            ) * amplitude;
                            amplitude *= 0.5;
                            frequency *= 2;
                        }
                        noise = noise / normalizeFactor;
                    }

                    const isActive = params.inversion ? (noise < threshold) : (noise > threshold);
                    voxels[idx++] = isActive ? 1 : 0;
                }
            }
        }
    }

    // ============================================================================
    // VORTEX
    // ============================================================================
    renderVortex(voxels, time, params) {
        voxels.fill(0);

        const types = {
            'tornado': () => this.vortexTornado(voxels, time, params),
            'whirlpool': () => this.vortexWhirlpool(voxels, time, params),
            'galaxy': () => this.vortexGalaxy(voxels, time, params)
        };

        const vortexFn = types[params.type] || types['tornado'];

        // Support multiple vortices using objectCount
        const numVortices = Math.max(1, params.objectCount || 1);

        if (numVortices === 1) {
            vortexFn();
        } else {
            // Multiple vortices side by side
            this.vortexMultiple(voxels, time, params, numVortices, vortexFn);
        }
    }

    vortexTornado(voxels, time, params) {
        const particleCount = Math.floor(params.density * 1000);
        const baseRadius = 5 + params.radius * 10;
        const maxHeight = this.gridY * params.height;

        for (let i = 0; i < particleCount; i++) {
            const t = (time + i * 0.1) % 10;
            const heightProgress = t / 10;
            const y = Math.floor(heightProgress * maxHeight);

            const radiusAtHeight = baseRadius * (1 - heightProgress * 0.7);
            const angle = t * params.twist * Math.PI * 2 + i * 0.5;

            const x = Math.floor(this.gridX / 2 + Math.cos(angle) * radiusAtHeight);
            const z = Math.floor(this.gridZ / 2 + Math.sin(angle) * radiusAtHeight);

            if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
            }
        }
    }

    vortexWhirlpool(voxels, time, params) {
        const particleCount = Math.floor(params.density * 800);
        const baseRadius = 8 + params.radius * 10;
        const maxHeight = this.gridY * params.height;
        const centerY = this.gridY / 2;
        const verticalRange = maxHeight * 0.5;

        for (let i = 0; i < particleCount; i++) {
            const angle = i * 0.3 + time * params.twist;
            const radiusProgress = (i / particleCount);
            const radius = baseRadius * (1 - radiusProgress);

            const x = Math.floor(this.gridX / 2 + Math.cos(angle) * radius);
            const z = Math.floor(this.gridZ / 2 + Math.sin(angle) * radius);
            // Height varies with spiral motion, respecting height parameter
            const y = Math.floor(centerY + Math.sin(radiusProgress * Math.PI * 4) * verticalRange);

            if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
            }
        }
    }

    vortexGalaxy(voxels, time, params) {
        const armCount = 3;
        const particleCount = Math.floor(params.density * 600);
        const maxHeight = this.gridY * params.height;
        const centerY = this.gridY / 2;
        const verticalRange = maxHeight * 0.3; // Galaxy is flatter than whirlpool

        for (let arm = 0; arm < armCount; arm++) {
            const armOffset = (arm / armCount) * Math.PI * 2;

            for (let i = 0; i < particleCount / armCount; i++) {
                const t = i / (particleCount / armCount);
                const radius = t * (8 + params.radius * 8);
                const angle = armOffset + t * params.twist * Math.PI * 4 + time * 0.5;

                const x = Math.floor(this.gridX / 2 + Math.cos(angle) * radius);
                const z = Math.floor(this.gridZ / 2 + Math.sin(angle) * radius);
                // Galaxy undulates slightly, respecting height parameter
                const y = Math.floor(centerY + Math.sin(t * Math.PI * 2) * verticalRange);

                if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                    voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                }
            }
        }
    }

    vortexMultiple(voxels, time, params, numVortices, renderFn) {
        // Render multiple vortices side by side with alternating rotation
        const totalWidth = this.gridX;
        const spacing = totalWidth / (numVortices + 1);

        for (let vortexIdx = 0; vortexIdx < numVortices; vortexIdx++) {
            // Calculate offset for this vortex
            const offsetX = (vortexIdx + 1) * spacing - this.gridX / 2;

            // Alternate rotation direction for even/odd vortices
            const rotationDir = (vortexIdx % 2 === 0) ? 1 : -1;

            // Create modified params with offset and rotation
            const modifiedParams = {
                ...params,
                vortexOffset: offsetX,
                rotationDirection: rotationDir,
                vortexIndex: vortexIdx
            };

            // Save original voxels
            const tempVoxels = [...voxels];

            // Render single vortex with offset
            this.renderSingleVortexWithOffset(voxels, time, modifiedParams);
        }
    }

    renderSingleVortexWithOffset(voxels, time, params) {
        // This is a helper that renders individual vortex types with offset
        const offsetX = params.vortexOffset || 0;
        const rotationDir = params.rotationDirection || 1;

        if (params.type === 'tornado') {
            this.vortexTornadoWithOffset(voxels, time, params, offsetX, rotationDir);
        } else if (params.type === 'whirlpool') {
            this.vortexWhirlpoolWithOffset(voxels, time, params, offsetX, rotationDir);
        } else if (params.type === 'galaxy') {
            this.vortexGalaxyWithOffset(voxels, time, params, offsetX, rotationDir);
        }
    }

    vortexTornadoWithOffset(voxels, time, params, offsetX = 0, rotationDir = 1) {
        const particleCount = Math.floor(params.density * 1000);
        const baseRadius = 5 + params.radius * 10;
        const maxHeight = this.gridY * params.height;

        for (let i = 0; i < particleCount; i++) {
            const t = (time + i * 0.1) % 10;
            const heightProgress = t / 10;
            const y = Math.floor(heightProgress * maxHeight);

            const radiusAtHeight = baseRadius * (1 - heightProgress * 0.7);
            const angle = rotationDir * (t * params.twist * Math.PI * 2 + i * 0.5);

            const x = Math.floor(this.gridX / 2 + offsetX + Math.cos(angle) * radiusAtHeight);
            const z = Math.floor(this.gridZ / 2 + Math.sin(angle) * radiusAtHeight);

            if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
            }
        }
    }

    vortexWhirlpoolWithOffset(voxels, time, params, offsetX = 0, rotationDir = 1) {
        const particleCount = Math.floor(params.density * 800);
        const baseRadius = 8 + params.radius * 10;
        const maxHeight = this.gridY * params.height;
        const centerY = this.gridY / 2;
        const verticalRange = maxHeight * 0.5;

        for (let i = 0; i < particleCount; i++) {
            const angle = rotationDir * (i * 0.3 + time * params.twist);
            const radiusProgress = (i / particleCount);
            const radius = baseRadius * (1 - radiusProgress);

            const x = Math.floor(this.gridX / 2 + offsetX + Math.cos(angle) * radius);
            const z = Math.floor(this.gridZ / 2 + Math.sin(angle) * radius);
            const y = Math.floor(centerY + Math.sin(radiusProgress * Math.PI * 4) * verticalRange);

            if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
            }
        }
    }

    vortexGalaxyWithOffset(voxels, time, params, offsetX = 0, rotationDir = 1) {
        const armCount = 3;
        const particleCount = Math.floor(params.density * 600);
        const maxHeight = this.gridY * params.height;
        const centerY = this.gridY / 2;
        const verticalRange = maxHeight * 0.3;

        for (let arm = 0; arm < armCount; arm++) {
            const armOffset = (arm / armCount) * Math.PI * 2;

            for (let i = 0; i < particleCount / armCount; i++) {
                const t = i / (particleCount / armCount);
                const radius = t * (8 + params.radius * 8);
                const angle = armOffset + rotationDir * (t * params.twist * Math.PI * 4 + time * 0.5);

                const x = Math.floor(this.gridX / 2 + offsetX + Math.cos(angle) * radius);
                const z = Math.floor(this.gridZ / 2 + Math.sin(angle) * radius);
                const y = Math.floor(centerY + Math.sin(t * Math.PI * 2) * verticalRange);

                if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                    voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                }
            }
        }
    }

    // ============================================================================
    // GRID
    // ============================================================================
    renderGrid(voxels, time, params) {
        voxels.fill(0);

        const patterns = {
            'cube': () => this.gridCube(voxels, time, params),
            'sphere': () => this.gridSphere(voxels, time, params),
            'tunnel': () => this.gridTunnel(voxels, time, params),
            'layers': () => this.gridLayers(voxels, time, params)
        };

        const gridFn = patterns[params.pattern] || patterns['cube'];
        gridFn();
    }

    gridCube(voxels, time, params) {
        const spacing = Math.max(2, Math.floor(params.spacing));
        const thickness = Math.max(1, Math.floor(params.thickness * 2));
        const offset = Math.floor(time * params.offset) % spacing;

        for (let x = offset; x < this.gridX; x += spacing) {
            for (let y = 0; y < this.gridY; y += spacing) {
                for (let z = 0; z < this.gridZ; z += spacing) {
                    // Draw small cubes at grid intersections
                    for (let dx = 0; dx < thickness; dx++) {
                        for (let dy = 0; dy < thickness; dy++) {
                            for (let dz = 0; dz < thickness; dz++) {
                                const nx = x + dx;
                                const ny = y + dy;
                                const nz = z + dz;
                                if (nx < this.gridX && ny < this.gridY && nz < this.gridZ) {
                                    voxels[nx + ny * this.gridX + nz * this.gridX * this.gridY] = 1;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    gridSphere(voxels, time, params) {
        const centerX = this.gridX / 2;
        const centerY = this.gridY / 2;
        const centerZ = this.gridZ / 2;
        const spacing = Math.max(2, Math.floor(params.spacing));
        const thickness = Math.max(1, Math.floor(params.thickness * 2));

        for (let r = spacing; r < Math.min(this.gridX, this.gridZ) / 2; r += spacing) {
            const numPoints = Math.floor(r * 6);
            for (let i = 0; i < numPoints; i++) {
                const theta = (i / numPoints) * Math.PI * 2;
                const phi = Math.acos(1 - 2 * (i / numPoints));

                const x = Math.floor(centerX + r * Math.sin(phi) * Math.cos(theta));
                const y = Math.floor(centerY + r * Math.cos(phi) * 0.5);
                const z = Math.floor(centerZ + r * Math.sin(phi) * Math.sin(theta));

                if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                    voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                }
            }
        }
    }

    gridTunnel(voxels, time, params) {
        const centerX = this.gridX / 2;
        const centerZ = this.gridZ / 2;
        const spacing = Math.max(2, Math.floor(params.spacing));

        for (let y = 0; y < this.gridY; y++) {
            const radius = 8 + Math.sin(y * 0.3 + time) * 3;
            const numPoints = Math.floor(radius * 6);

            for (let i = 0; i < numPoints; i++) {
                if (i % spacing === 0) {
                    const angle = (i / numPoints) * Math.PI * 2;
                    const x = Math.floor(centerX + Math.cos(angle) * radius);
                    const z = Math.floor(centerZ + Math.sin(angle) * radius);

                    if (x >= 0 && x < this.gridX && z >= 0 && z < this.gridZ) {
                        voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                    }
                }
            }
        }
    }

    gridLayers(voxels, time, params) {
        const spacing = Math.max(2, Math.floor(params.spacing));
        const offset = Math.floor(time * params.offset) % spacing;

        for (let y = offset; y < this.gridY; y += spacing) {
            for (let x = 0; x < this.gridX; x++) {
                for (let z = 0; z < this.gridZ; z++) {
                    voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                }
            }
        }
    }

    // ============================================================================
    // TEXT 3D
    // ============================================================================
    renderText3D(voxels, time, params) {
        voxels.fill(0);

        // Simple block letter patterns (5x5 grid)
        const letters = {
            'H': [[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1]],
            'E': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,1,1,1,1]],
            'L': [[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'O': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            ' ': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        };

        const text = params.text.toUpperCase();
        const scale = Math.max(1, Math.floor(params.size * 2));
        const depth = Math.max(1, Math.floor(params.depth * 5));

        let xOffset = 5;

        for (let charIdx = 0; charIdx < text.length; charIdx++) {
            const char = text[charIdx];
            const pattern = letters[char] || letters['H'];

            for (let py = 0; py < 5; py++) {
                for (let px = 0; px < 5; px++) {
                    if (pattern[py][px]) {
                        for (let sx = 0; sx < scale; sx++) {
                            for (let sy = 0; sy < scale; sy++) {
                                for (let d = 0; d < depth; d++) {
                                    const x = xOffset + px * scale + sx;
                                    const y = 5 + py * scale + sy;
                                    const z = this.gridZ / 2 - depth / 2 + d;

                                    if (x < this.gridX && y < this.gridY && z >= 0 && z < this.gridZ) {
                                        voxels[x + y * this.gridX + Math.floor(z) * this.gridX * this.gridY] = 1;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            xOffset += 6 * scale;
        }
    }

    // ============================================================================
    // ILLUSION SCENES
    // ============================================================================

    // ROTATING AMES ROOM
    renderRotatingAmes(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;
        const depth = params.depth || 1.0;

        const angle = time * speed * 0.3;
        const trapezoidScale = 0.6 + 0.4 * depth;

        for (let y = 0; y < this.gridY; y++) {
            const yNorm = y / this.gridY;
            const scaleAtY = 1.0 - yNorm * (1.0 - trapezoidScale);

            for (let i = 0; i < 4; i++) {
                const edgeAngle = angle + (i * Math.PI / 2);
                const nextAngle = angle + ((i + 1) * Math.PI / 2);

                for (let t = 0; t <= 1; t += 0.1) {
                    const lerpAngle = edgeAngle + (nextAngle - edgeAngle) * t;
                    const radius = 10 * size * scaleAtY;

                    const x = Math.floor(this.gridX / 2 + Math.cos(lerpAngle) * radius);
                    const z = Math.floor(this.gridZ / 2 + Math.sin(lerpAngle) * radius);

                    if (x >= 0 && x < this.gridX && z >= 0 && z < this.gridZ) {
                        voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                    }
                }
            }
        }
    }

    // INFINITE CORRIDOR
    renderInfiniteCorridor(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const depth = params.depth || 1.0;
        const speed = params.animationSpeed || 1.0;
        const spacing = params.spacing || 1.0;

        const frameSpacing = Math.max(3, Math.floor(4 * spacing));
        const numFrames = Math.floor(5 + depth * 5);
        const scrollOffset = (time * speed * 3) % frameSpacing;

        for (let frame = 0; frame < numFrames; frame++) {
            const baseZ = this.gridZ - 1 - (frame * frameSpacing) + scrollOffset;
            const z = Math.floor(baseZ);
            const wrappedZ = ((z % this.gridZ) + this.gridZ) % this.gridZ;

            if (wrappedZ < 0 || wrappedZ >= this.gridZ) continue;

            const normalizedPos = (baseZ / this.gridZ + 1) % 1;
            const scale = 0.2 + normalizedPos * 0.8 * size;

            if (scale <= 0) continue;

            const width = Math.floor(this.gridX / 2 * scale);
            const height = Math.floor(this.gridY / 2 * scale);

            for (let x = -width; x <= width; x++) {
                for (let y = -height; y <= height; y++) {
                    const isEdge = Math.abs(x) === width || Math.abs(y) === height;
                    if (isEdge) {
                        const wx = Math.floor(this.gridX / 2 + x);
                        const wy = Math.floor(this.gridY / 2 + y);

                        if (wx >= 0 && wx < this.gridX && wy >= 0 && wy < this.gridY) {
                            voxels[wx + wy * this.gridX + wrappedZ * this.gridX * this.gridY] = 1;
                        }
                    }
                }
            }
        }
    }

    // KINETIC DEPTH EFFECT
    renderKineticDepth(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;
        const angle = time * speed * 0.5;

        const numWaves = 8;
        const radius = 12 * size;

        for (let i = 0; i < numWaves; i++) {
            const wavePhase = (i / numWaves) * Math.PI * 2;

            for (let t = 0; t <= 1; t += 0.02) {
                const theta = t * Math.PI * 2;
                const sinValue = Math.sin(theta * 3 + wavePhase);

                const x2d = Math.cos(theta) * radius;
                const y2d = sinValue * 5;

                const x3d = x2d * Math.cos(angle);
                const z3d = x2d * Math.sin(angle);

                const x = Math.floor(this.gridX / 2 + x3d);
                const y = Math.floor(this.gridY / 2 + y2d);
                const z = Math.floor(this.gridZ / 2 + z3d);

                if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                    voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                }
            }
        }
    }

    // WATERFALL ILLUSION
    renderWaterfallIllusion(voxels, time, params) {
        voxels.fill(0);

        const speed = params.animationSpeed || 1.0;
        const density = params.density || 0.5;
        const offset = time * speed * 10;

        const stripeSpacing = Math.max(2, Math.floor(5 - density * 3));

        for (let x = 0; x < this.gridX; x++) {
            for (let z = 0; z < this.gridZ; z++) {
                const pattern = (z + offset) % (stripeSpacing * 2);
                const isStripe = pattern < stripeSpacing;

                if (isStripe) {
                    for (let y = 0; y < this.gridY; y++) {
                        voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                    }
                }
            }
        }

        for (let y = 0; y < this.gridY; y += 5) {
            for (let x = 0; x < this.gridX; x++) {
                for (let z = 0; z < this.gridZ; z++) {
                    voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 0.3;
                }
            }
        }
    }

    // PENROSE TRIANGLE
    renderPenroseTriangle(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;
        const angle = time * speed * 0.3;

        const scale = 8 * size;
        const thickness = 2;

        const bars = [
            { start: [0, 0, 0], end: [1, 0, 0], offset: [0, 0, 0.5] },
            { start: [1, 0, 0], end: [0.5, 1, 0], offset: [0, 0, 0] },
            { start: [0.5, 1, 0], end: [0, 0, 0], offset: [0.5, 0, 0] }
        ];

        bars.forEach(bar => {
            for (let t = 0; t <= 1; t += 0.05) {
                const x = (bar.start[0] + (bar.end[0] - bar.start[0]) * t - 0.5) * scale;
                const y = (bar.start[1] + (bar.end[1] - bar.start[1]) * t - 0.5) * scale;
                const z = (bar.start[2] + (bar.end[2] - bar.start[2]) * t + bar.offset[2] * t) * scale;

                const xRot = x * Math.cos(angle) - z * Math.sin(angle);
                const zRot = x * Math.sin(angle) + z * Math.cos(angle);

                for (let dx = -thickness; dx <= thickness; dx++) {
                    for (let dy = -thickness; dy <= thickness; dy++) {
                        const wx = Math.floor(this.gridX / 2 + xRot + dx);
                        const wy = Math.floor(this.gridY / 2 + y + dy);
                        const wz = Math.floor(this.gridZ / 2 + zRot);

                        if (wx >= 0 && wx < this.gridX && wy >= 0 && wy < this.gridY && wz >= 0 && wz < this.gridZ) {
                            voxels[wx + wy * this.gridX + wz * this.gridX * this.gridY] = 1;
                        }
                    }
                }
            }
        });
    }

    // NECKER CUBE
    renderNeckerCube(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const thickness = Math.max(1, Math.floor((params.thickness || 0.5) * 2));

        const cubeSize = 10 * size;

        const corners = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ];

        const edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7]
        ];

        edges.forEach(edge => {
            const start = corners[edge[0]];
            const end = corners[edge[1]];

            for (let t = 0; t <= 1; t += 0.05) {
                const x = Math.floor(this.gridX / 2 + (start[0] + (end[0] - start[0]) * t) * cubeSize);
                const y = Math.floor(this.gridY / 2 + (start[1] + (end[1] - start[1]) * t) * cubeSize);
                const z = Math.floor(this.gridZ / 2 + (start[2] + (end[2] - start[2]) * t) * cubeSize);

                for (let dx = -thickness; dx <= thickness; dx++) {
                    for (let dy = -thickness; dy <= thickness; dy++) {
                        for (let dz = -thickness; dz <= thickness; dz++) {
                            const wx = x + dx;
                            const wy = y + dy;
                            const wz = z + dz;

                            if (wx >= 0 && wx < this.gridX && wy >= 0 && wy < this.gridY && wz >= 0 && wz < this.gridZ) {
                                voxels[wx + wy * this.gridX + wz * this.gridX * this.gridY] = 1;
                            }
                        }
                    }
                }
            }
        });
    }

    // FRASER SPIRAL
    renderFraserSpiral(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const frequency = params.frequency || 1.0;
        const speed = params.animationSpeed || 1.0;

        const numCircles = Math.floor(8 * size);
        const rotation = time * speed * 0.2;

        for (let circle = 1; circle <= numCircles; circle++) {
            const radius = (circle / numCircles) * (this.gridX / 2 - 2);
            const numSegments = Math.floor(circle * 8 * frequency);

            for (let seg = 0; seg < numSegments; seg++) {
                const angle = (seg / numSegments) * Math.PI * 2 + rotation;
                const nextAngle = ((seg + 1) / numSegments) * Math.PI * 2 + rotation;

                const brightness = seg % 2 === 0 ? 1 : 0.3;

                for (let t = 0; t <= 1; t += 0.1) {
                    const a = angle + (nextAngle - angle) * t;
                    const x = Math.floor(this.gridX / 2 + Math.cos(a) * radius);
                    const z = Math.floor(this.gridZ / 2 + Math.sin(a) * radius);

                    for (let y = 0; y < this.gridY; y++) {
                        const yOffset = Math.floor((Math.sin(a * 4) * 3 + y / 2) % this.gridY);

                        if (x >= 0 && x < this.gridX && z >= 0 && z < this.gridZ) {
                            voxels[x + yOffset * this.gridX + z * this.gridX * this.gridY] = brightness;
                        }
                    }
                }
            }
        }
    }

    // CAFÉ WALL ILLUSION
    renderCafeWall(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const spacing = params.spacing || 1.0;

        const tileSize = Math.max(2, Math.floor(3 * size));
        const offset = Math.floor(tileSize * 0.5);

        for (let y = 0; y < this.gridY; y += tileSize) {
            const rowOffset = Math.floor(y / tileSize) % 2 === 0 ? 0 : offset;

            for (let x = 0; x < this.gridX; x += tileSize) {
                const adjustedX = x + rowOffset;
                const tileColor = (Math.floor(adjustedX / tileSize) % 2) === 0 ? 1 : 0;

                for (let dx = 0; dx < tileSize; dx++) {
                    for (let dy = 0; dy < tileSize; dy++) {
                        const wx = (adjustedX + dx) % this.gridX;
                        const wy = y + dy;

                        if (wy < this.gridY) {
                            const baseIdx = wx + wy * this.gridX;
                            for (let z = 0; z < this.gridZ; z++) {
                                voxels[baseIdx + z * this.gridX * this.gridY] = tileColor;
                            }
                        }
                    }
                }
            }

            if (y > 0) {
                const baseIdx = y * this.gridX;
                for (let x = 0; x < this.gridX; x++) {
                    for (let z = 0; z < this.gridZ; z++) {
                        voxels[baseIdx + x + z * this.gridX * this.gridY] = 0.5;
                    }
                }
            }
        }
    }

    // PULFRICH EFFECT
    renderPulfrich(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;

        const angle = time * speed;
        const radius = 12 * size;
        const numObjects = 8;

        for (let i = 0; i < numObjects; i++) {
            const objAngle = angle + (i / numObjects) * Math.PI * 2;
            const x = Math.floor(this.gridX / 2 + Math.cos(objAngle) * radius);
            const z = Math.floor(this.gridZ / 2 + Math.sin(objAngle) * radius);

            const brightness = 0.5 + 0.5 * Math.sin(objAngle);

            const objSize = 2;
            for (let dx = -objSize; dx <= objSize; dx++) {
                for (let dy = -objSize; dy <= objSize; dy++) {
                    for (let dz = -objSize; dz <= objSize; dz++) {
                        if (dx * dx + dy * dy + dz * dz <= objSize * objSize) {
                            const wx = x + dx;
                            const wy = this.gridY / 2 + dy;
                            const wz = z + dz;

                            if (wx >= 0 && wx < this.gridX && wy >= 0 && wy < this.gridY && wz >= 0 && wz < this.gridZ) {
                                voxels[wx + wy * this.gridX + wz * this.gridX * this.gridY] = brightness;
                            }
                        }
                    }
                }
            }
        }
    }

    // ROTATING SNAKES
    renderRotatingSnakes(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;

        const numRings = Math.floor(4 * size);
        const rotation = time * speed * 0.1;
        const halfX = this.gridX / 2;
        const halfZ = this.gridZ / 2;

        const patternBrightness = [1, 0.7, 0.3, 0.7];

        for (let ring = 0; ring < numRings; ring++) {
            const radius = 5 + ring * 5;
            const numSegments = 16;
            const ringRotation = rotation + ring * 0.5;
            const angleStep = (Math.PI * 2) / numSegments;

            for (let seg = 0; seg < numSegments; seg++) {
                const angle = seg * angleStep + ringRotation;

                const pattern = Math.floor(seg / 4) % 4;
                const brightness = patternBrightness[pattern];

                for (let t = 0; t <= 1; t += 0.5) {
                    const a = angle + t * angleStep;
                    const x = Math.floor(halfX + Math.cos(a) * radius);
                    const z = Math.floor(halfZ + Math.sin(a) * radius);

                    if (x >= 0 && x < this.gridX && z >= 0 && z < this.gridZ) {
                        const baseIdx = x + z * this.gridX * this.gridY;
                        for (let y = 0; y < this.gridY; y++) {
                            const yPattern = (y + seg) % 4;
                            const yBrightness = yPattern < 2 ? brightness : brightness * 0.5;
                            voxels[baseIdx + y * this.gridX] = yBrightness;
                        }
                    }
                }
            }
        }
    }

    // BREATHING SQUARE
    renderBreathingSquare(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const frequency = params.frequency || 1.0;

        const checkSize = Math.max(2, Math.floor(4 * size));
        const pulse = Math.sin(time * frequency * 2) * 0.2 + 1;

        const step = 2;
        for (let x = 0; x < this.gridX; x += step) {
            for (let y = 0; y < this.gridY; y += step) {
                for (let z = 0; z < this.gridZ; z += step) {
                    const checkX = Math.floor((x + time * 2) / checkSize);
                    const checkY = Math.floor(y / checkSize);
                    const checkZ = Math.floor(z / checkSize);

                    const isLight = (checkX + checkY + checkZ) % 2 === 0;

                    const dx = x - this.gridX / 2;
                    const dy = y - this.gridY / 2;
                    const dz = z - this.gridZ / 2;
                    const distSq = dx * dx + dy * dy + dz * dz;
                    const distNorm = distSq / ((this.gridX / 2) * (this.gridX / 2));

                    const brightness = isLight ? pulse : (1 - distNorm * 0.1);
                    const value = brightness * (isLight ? 1 : 0.3);

                    for (let dx = 0; dx < step && x + dx < this.gridX; dx++) {
                        for (let dy = 0; dy < step && y + dy < this.gridY; dy++) {
                            for (let dz = 0; dz < step && z + dz < this.gridZ; dz++) {
                                voxels[(x + dx) + (y + dy) * this.gridX + (z + dz) * this.gridX * this.gridY] = value;
                            }
                        }
                    }
                }
            }
        }
    }

    // MOIRÉ PATTERN
    renderMoirePattern(voxels, time, params) {
        voxels.fill(0);

        const spacing = params.spacing || 1.0;
        const speed = params.animationSpeed || 1.0;

        const gridSpacing = Math.max(2, Math.floor(3 * spacing));
        const angle = time * speed * 0.1;
        const cosAngle = Math.cos(angle);
        const sinAngle = Math.sin(angle);
        const halfX = this.gridX / 2;
        const halfZ = this.gridZ / 2;

        for (let x = 0; x < this.gridX; x += gridSpacing) {
            const baseIndex = x;
            for (let y = 0; y < this.gridY; y++) {
                const yOffset = y * this.gridX;
                for (let z = 0; z < this.gridZ; z++) {
                    voxels[baseIndex + yOffset + z * this.gridX * this.gridY] = 0.5;
                }
            }
        }

        for (let x = 0; x < this.gridX; x++) {
            const cx = x - halfX;
            for (let z = 0; z < this.gridZ; z++) {
                const cz = z - halfZ;

                const rx = cx * cosAngle - cz * sinAngle;
                const rotatedX = rx + halfX;

                if (Math.floor(rotatedX) % gridSpacing === 0) {
                    const baseIndex = x;
                    const zOffset = z * this.gridX * this.gridY;
                    for (let y = 0; y < this.gridY; y++) {
                        const idx = baseIndex + y * this.gridX + zOffset;
                        voxels[idx] = Math.min(1, voxels[idx] + 0.5);
                    }
                }
            }
        }
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
        this.rainSystem.init(density);
        this.starSystem.init(density);
    }
}
