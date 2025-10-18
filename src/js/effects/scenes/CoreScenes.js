/**
 * Core Scenes
 * Core scene rendering methods extracted from SceneLibrary
 */
import { PerlinNoise } from '../../utils/PerlinNoise.js';
import { RainParticleSystem, StarfieldParticleSystem } from '../../utils/ParticleSystems.js';

export class CoreScenes {
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
    }

    renderShapeMorph(voxels, time, params) {
        if (params.shouldClear !== false) voxels.fill(0);

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

            if (params.scrollSpeed !== 0) {
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
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed !== 0) ? 2 : 1;

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

                // Wrap object center to keep it within reasonable bounds for continuous scrolling
                // This prevents the center from drifting infinitely far from the grid
                if (params.scrollSpeed !== 0) {
                    // Define wrap boundaries (with margin for smooth transitions)
                    const wrapMargin = radius * 2;
                    const minX = -wrapMargin;
                    const maxX = this.gridX + wrapMargin;
                    const minY = -wrapMargin;
                    const maxY = this.gridY + wrapMargin;
                    const minZ = -wrapMargin;
                    const maxZ = this.gridZ + wrapMargin;

                    const rangeX = maxX - minX;
                    const rangeY = maxY - minY;
                    const rangeZ = maxZ - minZ;

                    // Wrap each axis using proper modulo that handles any offset
                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        // Normalize to range [0, rangeX), then shift to [minX, maxX)
                        objCenterX = minX + ((objCenterX - minX) % rangeX + rangeX) % rangeX;
                    }
                    if (params.scrollDirection === 'y') {
                        objCenterY = minY + ((objCenterY - minY) % rangeY + rangeY) % rangeY;
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        objCenterZ = minZ + ((objCenterZ - minZ) % rangeZ + rangeZ) % rangeZ;
                    }
                }

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

                // NO modulo wrap - let objects scroll continuously
                // Wrapping is handled at the voxel level below

            // Draw each sphere with wrapping support
            for (let x = 0; x < this.gridX; x++) {
                for (let y = 0; y < this.gridY; y++) {
                    for (let z = 0; z < this.gridZ; z++) {
                        // Get position relative to object center
                        // Apply wrapping to handle objects outside grid bounds
                        let dx = x - objCenterX;
                        let dy = (y - objCenterY) * 2; // Y is half size
                        let dz = z - objCenterZ;

                        // Wrap dx, dy, dz to handle scrolling objects
                        // This creates seamless edge-to-edge wrapping
                        if (Math.abs(dx) > this.gridX / 2) {
                            dx = dx > 0 ? dx - this.gridX : dx + this.gridX;
                        }
                        if (Math.abs(dy) > this.gridY) {
                            dy = dy > 0 ? dy - this.gridY * 2 : dy + this.gridY * 2;
                        }
                        if (Math.abs(dz) > this.gridZ / 2) {
                            dz = dz > 0 ? dz - this.gridZ : dz + this.gridZ;
                        }

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

        if (params.scrollSpeed !== 0) {
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
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed !== 0) ? 2 : 1;

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

                // Wrap object center to keep it within reasonable bounds for continuous scrolling
                if (params.scrollSpeed !== 0) {
                    const wrapMargin = radius * 2;
                    const minX = -wrapMargin;
                    const maxX = this.gridX + wrapMargin;
                    const minZ = -wrapMargin;
                    const maxZ = this.gridZ + wrapMargin;

                    const rangeX = maxX - minX;
                    const rangeZ = maxZ - minZ;

                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        helixCenterX = minX + ((helixCenterX - minX) % rangeX + rangeX) % rangeX;
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        helixCenterZ = minZ + ((helixCenterZ - minZ) % rangeZ + rangeZ) % rangeZ;
                    }
                }

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

                // NO modulo wrap - let objects scroll continuously
                // Wrapping is handled at the voxel level below

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
                            let nx = Math.floor(x + dx);
                            let nz = Math.floor(z + dz);
                            const ny = Math.floor(finalY);

                            // Wrap coordinates for seamless scrolling
                            nx = ((nx % this.gridX) + this.gridX) % this.gridX;
                            nz = ((nz % this.gridZ) + this.gridZ) % this.gridZ;

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

        if (params.scrollSpeed !== 0) {
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
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed !== 0) ? 2 : 1;
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

                // Wrap object center to keep it within reasonable bounds for continuous scrolling
                if (params.scrollSpeed !== 0) {
                    const wrapMargin = spacing;
                    const minX = -wrapMargin;
                    const maxX = this.gridX + wrapMargin;
                    const minY = -wrapMargin;
                    const maxY = this.gridY + wrapMargin;
                    const minZ = -wrapMargin;
                    const maxZ = this.gridZ + wrapMargin;

                    const rangeX = maxX - minX;
                    const rangeY = maxY - minY;
                    const rangeZ = maxZ - minZ;

                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        planeCenterX = minX + ((planeCenterX - minX) % rangeX + rangeX) % rangeX;
                    }
                    if (params.scrollDirection === 'y') {
                        planeCenterY = minY + ((planeCenterY - minY) % rangeY + rangeY) % rangeY;
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        planeCenterZ = minZ + ((planeCenterZ - minZ) % rangeZ + rangeZ) % rangeZ;
                    }
                }

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

                // NO modulo wrap - let objects scroll continuously
                // Wrapping is handled at the voxel level below

                const planeOffset = (params.objectArrangement === 'linear') ? 0 : (planeIdx - (numPlanes - 1) / 2) * spacing;

                for (let x = 0; x < this.gridX; x++) {
                    for (let y = 0; y < this.gridY; y++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            let cx = x - planeCenterX;
                            let cy = y - planeCenterY;
                            let cz = z - planeCenterZ;

                            // Wrap offsets for seamless scrolling
                            if (Math.abs(cx) > this.gridX / 2) {
                                cx = cx > 0 ? cx - this.gridX : cx + this.gridX;
                            }
                            if (Math.abs(cy) > this.gridY / 2) {
                                cy = cy > 0 ? cy - this.gridY : cy + this.gridY;
                            }
                            if (Math.abs(cz) > this.gridZ / 2) {
                                cz = cz > 0 ? cz - this.gridZ : cz + this.gridZ;
                            }

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

        if (params.scrollSpeed !== 0) {
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
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed !== 0) ? 2 : 1;

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

                // Wrap object center to keep it within reasonable bounds for continuous scrolling
                if (params.scrollSpeed !== 0) {
                    const wrapMargin = baseMajorRadius * 2;
                    const minX = -wrapMargin;
                    const maxX = this.gridX + wrapMargin;
                    const minY = -wrapMargin;
                    const maxY = this.gridY + wrapMargin;
                    const minZ = -wrapMargin;
                    const maxZ = this.gridZ + wrapMargin;

                    const rangeX = maxX - minX;
                    const rangeY = maxY - minY;
                    const rangeZ = maxZ - minZ;

                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        torusCenterX = minX + ((torusCenterX - minX) % rangeX + rangeX) % rangeX;
                    }
                    if (params.scrollDirection === 'y') {
                        torusCenterY = minY + ((torusCenterY - minY) % rangeY + rangeY) % rangeY;
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        torusCenterZ = minZ + ((torusCenterZ - minZ) % rangeZ + rangeZ) % rangeZ;
                    }
                }

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

                // NO modulo wrap - let objects scroll continuously
                // Wrapping is handled at the voxel level below

                for (let x = 0; x < this.gridX; x++) {
                    for (let y = 0; y < this.gridY; y++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            // Get position relative to torus center with wrapping
                            let dx = x - torusCenterX;
                            let dy = (y - torusCenterY) * 2;
                            let dz = z - torusCenterZ;

                            // Wrap offsets for seamless scrolling
                            if (Math.abs(dx) > this.gridX / 2) {
                                dx = dx > 0 ? dx - this.gridX : dx + this.gridX;
                            }
                            if (Math.abs(dy) > this.gridY) {
                                dy = dy > 0 ? dy - this.gridY * 2 : dy + this.gridY * 2;
                            }
                            if (Math.abs(dz) > this.gridZ / 2) {
                                dz = dz > 0 ? dz - this.gridZ : dz + this.gridZ;
                            }

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

        if (params.scrollSpeed !== 0) {
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
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed !== 0) ? 2 : 1;

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

                // Wrap object center to keep it within reasonable bounds for continuous scrolling
                if (params.scrollSpeed !== 0) {
                    const wrapMargin = baseSize * 2;
                    const minX = -wrapMargin;
                    const maxX = this.gridX + wrapMargin;
                    const minY = -wrapMargin;
                    const maxY = this.gridY + wrapMargin;
                    const minZ = -wrapMargin;
                    const maxZ = this.gridZ + wrapMargin;

                    const rangeX = maxX - minX;
                    const rangeY = maxY - minY;
                    const rangeZ = maxZ - minZ;

                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        cubeCenterX = minX + ((cubeCenterX - minX) % rangeX + rangeX) % rangeX;
                    }
                    if (params.scrollDirection === 'y') {
                        cubeCenterY = minY + ((cubeCenterY - minY) % rangeY + rangeY) % rangeY;
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        cubeCenterZ = minZ + ((cubeCenterZ - minZ) % rangeZ + rangeZ) % rangeZ;
                    }
                }

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

                // NO modulo wrap - let objects scroll continuously
                // Wrapping is handled at the voxel level below

                for (let x = 0; x < this.gridX; x++) {
                    for (let y = 0; y < this.gridY; y++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            // Get position relative to cube center with wrapping
                            let dx = x - cubeCenterX;
                            let dy = (y - cubeCenterY) * 2;
                            let dz = z - cubeCenterZ;

                            // Wrap offsets for seamless scrolling
                            if (Math.abs(dx) > this.gridX / 2) {
                                dx = dx > 0 ? dx - this.gridX : dx + this.gridX;
                            }
                            if (Math.abs(dy) > this.gridY) {
                                dy = dy > 0 ? dy - this.gridY * 2 : dy + this.gridY * 2;
                            }
                            if (Math.abs(dz) > this.gridZ / 2) {
                                dz = dz > 0 ? dz - this.gridZ : dz + this.gridZ;
                            }

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

        if (params.scrollSpeed !== 0) {
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
        const renderCopies = (params.objectArrangement === 'linear' && params.scrollSpeed !== 0) ? 2 : 1;

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

                // Wrap object center to keep it within reasonable bounds for continuous scrolling
                if (params.scrollSpeed !== 0) {
                    const wrapMargin = baseBaseSize * 2;
                    const minX = -wrapMargin;
                    const maxX = this.gridX + wrapMargin;
                    const minY = -wrapMargin;
                    const maxY = this.gridY + wrapMargin;
                    const minZ = -wrapMargin;
                    const maxZ = this.gridZ + wrapMargin;

                    const rangeX = maxX - minX;
                    const rangeY = maxY - minY;
                    const rangeZ = maxZ - minZ;

                    if (params.scrollDirection === 'x' || params.scrollDirection === 'diagonal') {
                        pyrCenterX = minX + ((pyrCenterX - minX) % rangeX + rangeX) % rangeX;
                    }
                    if (params.scrollDirection === 'y') {
                        pyrCenterY = minY + ((pyrCenterY - minY) % rangeY + rangeY) % rangeY;
                    }
                    if (params.scrollDirection === 'z' || params.scrollDirection === 'diagonal') {
                        pyrCenterZ = minZ + ((pyrCenterZ - minZ) % rangeZ + rangeZ) % rangeZ;
                    }
                }

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

                // NO modulo wrap - let objects scroll continuously
                // Wrapping is handled at the voxel level below

                for (let x = 0; x < this.gridX; x++) {
                    for (let y = 0; y < this.gridY; y++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            // Get position relative to pyramid base center with wrapping
                            let dx = x - pyrCenterX;
                            let dy = y - (pyrCenterY - height / 2);
                            let dz = z - pyrCenterZ;

                            // Wrap offsets for seamless scrolling
                            if (Math.abs(dx) > this.gridX / 2) {
                                dx = dx > 0 ? dx - this.gridX : dx + this.gridX;
                            }
                            if (Math.abs(dy) > this.gridY / 2) {
                                dy = dy > 0 ? dy - this.gridY : dy + this.gridY;
                            }
                            if (Math.abs(dz) > this.gridZ / 2) {
                                dz = dz > 0 ? dz - this.gridZ : dz + this.gridZ;
                            }

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
        if (params.shouldClear !== false) voxels.fill(0);

        // Pass movement to pattern renderers
        const patterns = {
            'particles': () => this.flowParticles(voxels, params, time),
            'spiral': () => this.flowSpiral(voxels, time, params),
            'explode': () => this.flowExplode(voxels, time, params),
            // Vortex patterns merged into particle flow
            'tornado': () => this.flowTornado(voxels, time, params),
            'whirlpool': () => this.flowWhirlpool(voxels, time, params),
            'galaxy': () => this.flowGalaxy(voxels, time, params)
        };

        const flowFn = patterns[params.pattern] || patterns['particles'];
        flowFn();
    }

    /**
     * Calculate movement transformations for particle flow
     * @param {number} time - Current animation time
     * @param {object} params - Parameters including movement controls
     * @param {number} particleIndex - Index of the particle (for staggered movement)
     * @param {number} totalParticles - Total number of particles (for normalization)
     * @returns {object} Movement offsets {offsetX, offsetY, offsetZ}
     */
    calculateParticleMovement(time, params, particleIndex = 0, totalParticles = 1) {
        // Apply individual time offset based on objectOffset parameter
        // This creates a wave/stagger effect where each particle's movement is delayed
        const timeOffset = params.objectOffset > 0 ?
            (particleIndex / Math.max(1, totalParticles)) * params.objectOffset * 10 : 0;
        const effectiveTime = time - timeOffset;

        let offsetX = 0;
        let offsetY = 0;
        let offsetZ = 0;

        // 1. Translation (side-to-side oscillation)
        if (params.translateX > 0 && params.translateAmplitude > 0) {
            offsetX += Math.sin(effectiveTime * params.translateX * 2) * params.translateAmplitude * 10;
        }
        if (params.translateZ > 0 && params.translateAmplitude > 0) {
            offsetZ += Math.sin(effectiveTime * params.translateZ * 2) * params.translateAmplitude * 10;
        }

        // 2. Bounce (vertical oscillation)
        if (params.bounceSpeed > 0 && params.bounceHeight > 0) {
            offsetY += Math.abs(Math.sin(effectiveTime * params.bounceSpeed * 3)) * params.bounceHeight * 8;
        }

        // 3. Orbit (circular motion in XZ plane)
        if (params.orbitSpeed > 0 && params.orbitRadius > 0) {
            const angle = effectiveTime * params.orbitSpeed * 2;
            const radius = params.orbitRadius * 10;
            offsetX += Math.cos(angle) * radius;
            offsetZ += Math.sin(angle) * radius;
        }

        // 4. Spiral (3D spiral motion)
        if (params.spiralSpeed > 0 && (params.spiralRadius > 0 || params.spiralHeight > 0)) {
            const angle = effectiveTime * params.spiralSpeed * 2;
            const radius = params.spiralRadius * 8;
            offsetX += Math.cos(angle) * radius;
            offsetZ += Math.sin(angle) * radius;
            offsetY += (Math.sin(effectiveTime * params.spiralSpeed * 1.5) * params.spiralHeight * 5);
        }

        // 5. Figure-8 motion
        if (params.figure8Speed > 0 && params.figure8Size > 0) {
            const t = effectiveTime * params.figure8Speed * 2;
            const size = params.figure8Size * 8;
            offsetX += Math.sin(t) * size;
            offsetZ += Math.sin(t * 2) * size * 0.5;
        }

        // 6. Elliptical orbit
        if (params.ellipseSpeed > 0 && (params.ellipseRadiusX > 0 || params.ellipseRadiusZ > 0)) {
            const angle = effectiveTime * params.ellipseSpeed * 2;
            offsetX += Math.cos(angle) * params.ellipseRadiusX * 10;
            offsetZ += Math.sin(angle) * params.ellipseRadiusZ * 10;
        }

        // 7. Wobble (random-ish motion)
        if (params.wobbleSpeed > 0 && params.wobbleAmount > 0) {
            const wobbleAmount = params.wobbleAmount * 5;
            offsetX += Math.sin(effectiveTime * params.wobbleSpeed * 2.3) * wobbleAmount;
            offsetY += Math.sin(effectiveTime * params.wobbleSpeed * 1.7) * wobbleAmount;
            offsetZ += Math.sin(effectiveTime * params.wobbleSpeed * 2.9) * wobbleAmount;
        }

        // 8. Continuous scroll (no modulo - wrapping handled in drawParticle)
        if (params.scrollSpeed !== 0) {
            const scrollAmount = effectiveTime * params.scrollSpeed * 15;
            switch (params.scrollDirection) {
                case 'x':
                    offsetX += scrollAmount;
                    break;
                case 'y':
                    offsetY += scrollAmount;
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
     * Wraps coordinates to create seamless scrolling
     */
    drawParticle(voxels, centerX, centerY, centerZ, size) {
        const radius = Math.max(0, size - 1);

        if (size === 1) {
            // Single voxel (fast path) with wrapping
            let x = Math.floor(centerX) % this.gridX;
            let y = Math.floor(centerY) % this.gridY;
            let z = Math.floor(centerZ) % this.gridZ;

            // Handle negative wrapping
            if (x < 0) x += this.gridX;
            if (y < 0) y += this.gridY;
            if (z < 0) z += this.gridZ;

            if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
            }
        } else {
            // Multi-voxel particle (draw a small sphere) with wrapping
            const cx = Math.floor(centerX);
            const cy = Math.floor(centerY);
            const cz = Math.floor(centerZ);

            for (let dx = -radius; dx <= radius; dx++) {
                for (let dy = -radius; dy <= radius; dy++) {
                    for (let dz = -radius; dz <= radius; dz++) {
                        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
                        if (dist <= radius) {
                            let x = (cx + dx) % this.gridX;
                            let y = (cy + dy) % this.gridY;
                            let z = (cz + dz) % this.gridZ;

                            // Handle negative wrapping
                            if (x < 0) x += this.gridX;
                            if (y < 0) y += this.gridY;
                            if (z < 0) z += this.gridZ;

                            if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                            }
                        }
                    }
                }
            }
        }
    }

    flowParticles(voxels, params, time) {
        // Unified particle system - direction controlled by scrollSpeed/scrollDirection in movement params
        // Use rain system as default particle generator
        this.rainSystem.update(params.velocity, params.scrollDirection, params.scrollSpeed);
        const particles = this.rainSystem.getParticles();
        const totalParticles = particles.length;

        particles.forEach((p, i) => {
            const movement = this.calculateParticleMovement(time, params, i, totalParticles);
            this.drawParticle(voxels,
                p.x + movement.offsetX,
                p.y + movement.offsetY,
                p.z + movement.offsetZ,
                params.particleSize);
        });
    }

    flowSpiral(voxels, time, params) {
        // Generate spiral particle motion
        const particleCount = Math.floor(params.density * 500);

        for (let i = 0; i < particleCount; i++) {
            const movement = this.calculateParticleMovement(time, params, i, particleCount);
            const t = (time * params.velocity + i * 0.1) % (Math.PI * 4);
            const radius = (t / (Math.PI * 4)) * this.gridX / 2;
            const angle = t * 3;

            const x = this.gridX / 2 + Math.cos(angle) * radius + movement.offsetX;
            const z = this.gridZ / 2 + Math.sin(angle) * radius + movement.offsetZ;
            const y = (t / (Math.PI * 4)) * this.gridY + movement.offsetY;

            this.drawParticle(voxels, x, y, z, params.particleSize);
        }
    }

    flowExplode(voxels, time, params) {
        // Particles explode outward from center
        const particleCount = Math.floor(params.density * 300);

        for (let i = 0; i < particleCount; i++) {
            const movement = this.calculateParticleMovement(time, params, i, particleCount);
            const angle1 = (i * 2.4) % (Math.PI * 2);
            const angle2 = (i * 1.7) % Math.PI;
            const expansion = ((time * params.velocity) % 3) * 10;

            const x = this.gridX / 2 + Math.cos(angle1) * Math.sin(angle2) * expansion + movement.offsetX;
            const y = this.gridY / 2 + Math.cos(angle2) * expansion + movement.offsetY;
            const z = this.gridZ / 2 + Math.sin(angle1) * Math.sin(angle2) * expansion + movement.offsetZ;

            this.drawParticle(voxels, x, y, z, params.particleSize);
        }
    }

    // Vortex patterns merged into particle flow with movement effects
    flowTornado(voxels, time, params) {
        const particleCount = Math.floor(params.density * 1000);
        // Use velocity parameter for animation speed (mapped from animationSpeed)
        const twist = params.velocity || 1.0;
        // Use amplitude for radius control (defaults to reasonable value)
        const baseRadius = 5 + (params.radius || 1.0) * 10;
        // Use depth for height control (defaults to reasonable value)
        const maxHeight = this.gridY * (params.height || 0.8);

        for (let i = 0; i < particleCount; i++) {
            // Calculate per-particle movement with time offset
            const movement = this.calculateParticleMovement(time, params, i, particleCount);

            const t = (time + i * 0.1) % 10;
            const heightProgress = t / 10;
            const y = Math.floor(heightProgress * maxHeight);

            const radiusAtHeight = baseRadius * (1 - heightProgress * 0.7);
            const angle = t * twist * Math.PI * 2 + i * 0.5;

            const x = this.gridX / 2 + Math.cos(angle) * radiusAtHeight + movement.offsetX;
            const z = this.gridZ / 2 + Math.sin(angle) * radiusAtHeight + movement.offsetZ;

            this.drawParticle(voxels, x, y + movement.offsetY, z, params.particleSize);
        }
    }

    flowWhirlpool(voxels, time, params) {
        const particleCount = Math.floor(params.density * 800);
        const twist = params.velocity || 1.0;
        const baseRadius = 8 + (params.radius || 1.0) * 10;
        const maxHeight = this.gridY * (params.height || 0.8);
        const centerY = this.gridY / 2;
        const verticalRange = maxHeight * 0.5;

        for (let i = 0; i < particleCount; i++) {
            // Calculate per-particle movement with time offset
            const movement = this.calculateParticleMovement(time, params, i, particleCount);

            const angle = i * 0.3 + time * twist;
            const radiusProgress = (i / particleCount);
            const radius = baseRadius * (1 - radiusProgress);

            const x = this.gridX / 2 + Math.cos(angle) * radius + movement.offsetX;
            const z = this.gridZ / 2 + Math.sin(angle) * radius + movement.offsetZ;
            // Height varies with spiral motion
            const y = centerY + Math.sin(radiusProgress * Math.PI * 4) * verticalRange;

            this.drawParticle(voxels, x, y + movement.offsetY, z, params.particleSize);
        }
    }

    flowGalaxy(voxels, time, params) {
        const armCount = 3;
        const particleCount = Math.floor(params.density * 600);
        const twist = params.velocity || 1.0;
        const maxHeight = this.gridY * (params.height || 0.8);
        const centerY = this.gridY / 2;
        const verticalRange = maxHeight * 0.3; // Galaxy is flatter than whirlpool

        for (let arm = 0; arm < armCount; arm++) {
            const armOffset = (arm / armCount) * Math.PI * 2;
            const particlesPerArm = Math.floor(particleCount / armCount);

            for (let i = 0; i < particlesPerArm; i++) {
                // Calculate global particle index for time offset
                const globalIdx = arm * particlesPerArm + i;
                const movement = this.calculateParticleMovement(time, params, globalIdx, particleCount);

                const t = i / particlesPerArm;
                const radius = t * (8 + (params.radius || 1.0) * 8);
                const angle = armOffset + t * twist * Math.PI * 4 + time * 0.5;

                const x = this.gridX / 2 + Math.cos(angle) * radius + movement.offsetX;
                const z = this.gridZ / 2 + Math.sin(angle) * radius + movement.offsetZ;
                // Galaxy undulates slightly
                const y = centerY + Math.sin(t * Math.PI * 2) * verticalRange;

                this.drawParticle(voxels, x, y + movement.offsetY, z, params.particleSize);
            }
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
        if (params.shouldClear !== false) voxels.fill(0);

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
        if (params.shouldClear !== false) voxels.fill(0);

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
        if (params.shouldClear !== false) voxels.fill(0);

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

    updateDensity(density) {
        this.rainSystem.init(density);
        this.starSystem.init(density);
    }
}
