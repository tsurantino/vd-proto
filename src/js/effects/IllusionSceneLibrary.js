/**
 * Illusion Scene Library
 * Collection of optical illusion scenes for volumetric display
 */
export class IllusionSceneLibrary {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        this.scenes = this.createScenes();
    }

    createScenes() {
        return {
            'rotatingAmes': {
                name: 'Rotating Ames Room',
                defaultParams: {
                    // Global params used: size, animationSpeed, depth
                },
                fn: (voxels, time, params) => this.renderRotatingAmes(voxels, time, params)
            },
            'infiniteCorridor': {
                name: 'Infinite Corridor',
                defaultParams: {
                    // Global params used: size, depth, spacing
                },
                fn: (voxels, time, params) => this.renderInfiniteCorridor(voxels, time, params)
            },
            'kineticDepth': {
                name: 'Kinetic Depth Effect',
                defaultParams: {
                    // Global params used: animationSpeed, size
                },
                fn: (voxels, time, params) => this.renderKineticDepth(voxels, time, params)
            },
            'waterfallIllusion': {
                name: 'Motion Aftereffect',
                defaultParams: {
                    // Global params used: animationSpeed, density
                },
                fn: (voxels, time, params) => this.renderWaterfallIllusion(voxels, time, params)
            },
            'penroseTriangle': {
                name: 'Penrose Triangle',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.renderPenroseTriangle(voxels, time, params)
            },
            'neckerCube': {
                name: 'Necker Cube',
                defaultParams: {
                    // Global params used: size, thickness
                },
                fn: (voxels, time, params) => this.renderNeckerCube(voxels, time, params)
            },
            'fraserSpiral': {
                name: 'Fraser Spiral',
                defaultParams: {
                    // Global params used: size, frequency, animationSpeed
                },
                fn: (voxels, time, params) => this.renderFraserSpiral(voxels, time, params)
            },
            'cafeWall': {
                name: 'Café Wall Illusion',
                defaultParams: {
                    // Global params used: size, spacing
                },
                fn: (voxels, time, params) => this.renderCafeWall(voxels, time, params)
            },
            'pulfrich': {
                name: 'Pulfrich Effect',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.renderPulfrich(voxels, time, params)
            },
            'rotatingSnakes': {
                name: 'Rotating Snakes',
                defaultParams: {
                    // Global params used: size, animationSpeed
                },
                fn: (voxels, time, params) => this.renderRotatingSnakes(voxels, time, params)
            },
            'breathingSquare': {
                name: 'Breathing Square',
                defaultParams: {
                    // Global params used: size, frequency
                },
                fn: (voxels, time, params) => this.renderBreathingSquare(voxels, time, params)
            },
            'moirePattern': {
                name: 'Moiré Pattern',
                defaultParams: {
                    // Global params used: spacing, animationSpeed
                },
                fn: (voxels, time, params) => this.renderMoirePattern(voxels, time, params)
            }
        };
    }

    // ============================================================================
    // ROTATING AMES ROOM
    // ============================================================================
    renderRotatingAmes(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;
        const depth = params.depth || 1.0;

        const angle = time * speed * 0.3;
        const trapezoidScale = 0.6 + 0.4 * depth;

        // Create rotating trapezoid that appears rectangular
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

    // ============================================================================
    // INFINITE CORRIDOR (DROSTE EFFECT)
    // ============================================================================
    renderInfiniteCorridor(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const depth = params.depth || 1.0;
        const speed = params.animationSpeed || 1.0;
        const spacing = params.spacing || 1.0;

        // Calculate spacing between frames
        const frameSpacing = Math.max(3, Math.floor(4 * spacing));
        const numFrames = Math.floor(5 + depth * 5);

        // Continuous scrolling animation from back to front
        const scrollOffset = (time * speed * 3) % frameSpacing;

        for (let frame = 0; frame < numFrames; frame++) {
            // Position frames from back (high Z) to front (low Z)
            const baseZ = this.gridZ - 1 - (frame * frameSpacing) + scrollOffset;
            const z = Math.floor(baseZ);

            // Wrap around when reaching the front
            const wrappedZ = ((z % this.gridZ) + this.gridZ) % this.gridZ;

            if (wrappedZ < 0 || wrappedZ >= this.gridZ) continue;

            // Calculate scale - frames get bigger as they come toward the front
            // Normalize frame position for smooth scaling
            const normalizedPos = (baseZ / this.gridZ + 1) % 1;
            const scale = 0.2 + normalizedPos * 0.8 * size;

            if (scale <= 0) continue;

            const width = Math.floor(this.gridX / 2 * scale);
            const height = Math.floor(this.gridY / 2 * scale);

            // Draw rectangle frame
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

    // ============================================================================
    // KINETIC DEPTH EFFECT
    // ============================================================================
    renderKineticDepth(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;
        const angle = time * speed * 0.5;

        // Rotating 2D sine wave pattern that appears 3D when in motion
        const numWaves = 8;
        const radius = 12 * size;

        for (let i = 0; i < numWaves; i++) {
            const wavePhase = (i / numWaves) * Math.PI * 2;

            for (let t = 0; t <= 1; t += 0.02) {
                const theta = t * Math.PI * 2;
                const sinValue = Math.sin(theta * 3 + wavePhase);

                // Project rotating pattern
                const x2d = Math.cos(theta) * radius;
                const y2d = sinValue * 5;

                // Rotate in 3D space
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

    // ============================================================================
    // WATERFALL ILLUSION (MOTION AFTEREFFECT)
    // ============================================================================
    renderWaterfallIllusion(voxels, time, params) {
        voxels.fill(0);

        const speed = params.animationSpeed || 1.0;
        const density = params.density || 0.5;
        const offset = time * speed * 10;

        // Moving vertical stripes
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

        // Add stationary reference grid
        for (let y = 0; y < this.gridY; y += 5) {
            for (let x = 0; x < this.gridX; x++) {
                for (let z = 0; z < this.gridZ; z++) {
                    voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 0.3;
                }
            }
        }
    }

    // ============================================================================
    // PENROSE TRIANGLE
    // ============================================================================
    renderPenroseTriangle(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;
        const angle = time * speed * 0.3;

        const scale = 8 * size;
        const thickness = 2;

        // Three bars that create impossible triangle
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

                // Rotate
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

    // ============================================================================
    // NECKER CUBE
    // ============================================================================
    renderNeckerCube(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const thickness = Math.max(1, Math.floor((params.thickness || 0.5) * 2));

        const cubeSize = 10 * size;
        const offset = 2;

        // Draw wireframe cube with ambiguous depth
        const corners = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ];

        const edges = [
            [0, 1], [1, 2], [2, 3], [3, 0], // Back face
            [4, 5], [5, 6], [6, 7], [7, 4], // Front face
            [0, 4], [1, 5], [2, 6], [3, 7]  // Connecting edges
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

    // ============================================================================
    // FRASER SPIRAL
    // ============================================================================
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

                // Alternate diagonal pattern to create spiral illusion
                const brightness = seg % 2 === 0 ? 1 : 0.3;

                for (let t = 0; t <= 1; t += 0.1) {
                    const a = angle + (nextAngle - angle) * t;
                    const x = Math.floor(this.gridX / 2 + Math.cos(a) * radius);
                    const z = Math.floor(this.gridZ / 2 + Math.sin(a) * radius);

                    // Add diagonal segments
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

    // ============================================================================
    // CAFÉ WALL ILLUSION
    // ============================================================================
    renderCafeWall(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const spacing = params.spacing || 1.0;

        const tileSize = Math.max(2, Math.floor(3 * size));
        const offset = Math.floor(tileSize * 0.5);

        // Optimized: render per-layer instead of per-voxel
        for (let y = 0; y < this.gridY; y += tileSize) {
            const rowOffset = Math.floor(y / tileSize) % 2 === 0 ? 0 : offset;

            for (let x = 0; x < this.gridX; x += tileSize) {
                const adjustedX = x + rowOffset;
                const tileColor = (Math.floor(adjustedX / tileSize) % 2) === 0 ? 1 : 0;

                // Render entire tile at once
                for (let dx = 0; dx < tileSize; dx++) {
                    for (let dy = 0; dy < tileSize; dy++) {
                        const wx = (adjustedX + dx) % this.gridX;
                        const wy = y + dy;

                        if (wy < this.gridY) {
                            const baseIdx = wx + wy * this.gridX;
                            // Fill all Z layers at once
                            for (let z = 0; z < this.gridZ; z++) {
                                voxels[baseIdx + z * this.gridX * this.gridY] = tileColor;
                            }
                        }
                    }
                }
            }

            // Add mortar line (gray line between rows)
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

    // ============================================================================
    // PULFRICH EFFECT
    // ============================================================================
    renderPulfrich(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;

        const angle = time * speed;
        const radius = 12 * size;
        const numObjects = 8;

        // Objects moving in circle appear to move in 3D ellipse with brightness variation
        for (let i = 0; i < numObjects; i++) {
            const objAngle = angle + (i / numObjects) * Math.PI * 2;
            const x = Math.floor(this.gridX / 2 + Math.cos(objAngle) * radius);
            const z = Math.floor(this.gridZ / 2 + Math.sin(objAngle) * radius);

            // Brightness varies with position to enhance 3D effect
            const brightness = 0.5 + 0.5 * Math.sin(objAngle);

            // Draw sphere
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

    // ============================================================================
    // ROTATING SNAKES
    // ============================================================================
    renderRotatingSnakes(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const speed = params.animationSpeed || 1.0;

        const numRings = Math.floor(4 * size);
        const rotation = time * speed * 0.1;
        const halfX = this.gridX / 2;
        const halfZ = this.gridZ / 2;

        // Brightness lookup
        const patternBrightness = [1, 0.7, 0.3, 0.7];

        for (let ring = 0; ring < numRings; ring++) {
            const radius = 5 + ring * 5;
            const numSegments = 16;
            const ringRotation = rotation + ring * 0.5;
            const angleStep = (Math.PI * 2) / numSegments;

            for (let seg = 0; seg < numSegments; seg++) {
                const angle = seg * angleStep + ringRotation;

                // Create alternating pattern
                const pattern = Math.floor(seg / 4) % 4;
                const brightness = patternBrightness[pattern];

                // Reduced sampling for performance
                for (let t = 0; t <= 1; t += 0.5) {
                    const a = angle + t * angleStep;
                    const x = Math.floor(halfX + Math.cos(a) * radius);
                    const z = Math.floor(halfZ + Math.sin(a) * radius);

                    if (x >= 0 && x < this.gridX && z >= 0 && z < this.gridZ) {
                        const baseIdx = x + z * this.gridX * this.gridY;
                        // Fill columns more efficiently
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

    // ============================================================================
    // BREATHING SQUARE
    // ============================================================================
    renderBreathingSquare(voxels, time, params) {
        voxels.fill(0);

        const size = params.size || 1.0;
        const frequency = params.frequency || 1.0;

        const checkSize = Math.max(2, Math.floor(4 * size));
        const pulse = Math.sin(time * frequency * 2) * 0.2 + 1;

        // Optimized: only render a subset of the volume
        const step = 2; // Skip every other voxel for performance
        for (let x = 0; x < this.gridX; x += step) {
            for (let y = 0; y < this.gridY; y += step) {
                for (let z = 0; z < this.gridZ; z += step) {
                    const checkX = Math.floor((x + time * 2) / checkSize);
                    const checkY = Math.floor(y / checkSize);
                    const checkZ = Math.floor(z / checkSize);

                    const isLight = (checkX + checkY + checkZ) % 2 === 0;

                    // Distance from center for pulsing
                    const dx = x - this.gridX / 2;
                    const dy = y - this.gridY / 2;
                    const dz = z - this.gridZ / 2;
                    const distSq = dx * dx + dy * dy + dz * dz; // Avoid sqrt
                    const distNorm = distSq / ((this.gridX / 2) * (this.gridX / 2));

                    const brightness = isLight ? pulse : (1 - distNorm * 0.1);
                    const value = brightness * (isLight ? 1 : 0.3);

                    // Fill block of voxels for better visibility
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

    // ============================================================================
    // MOIRÉ PATTERN
    // ============================================================================
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

        // First grid (stationary) - optimized
        for (let x = 0; x < this.gridX; x += gridSpacing) {
            const baseIndex = x;
            for (let y = 0; y < this.gridY; y++) {
                const yOffset = y * this.gridX;
                for (let z = 0; z < this.gridZ; z++) {
                    voxels[baseIndex + yOffset + z * this.gridX * this.gridY] = 0.5;
                }
            }
        }

        // Second grid (rotating) - creates interference pattern - optimized
        for (let x = 0; x < this.gridX; x++) {
            const cx = x - halfX;
            for (let z = 0; z < this.gridZ; z++) {
                const cz = z - halfZ;

                // Rotate coordinates
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
    // UTILITY METHODS
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
        // Placeholder for any particle systems we might add
    }
}
