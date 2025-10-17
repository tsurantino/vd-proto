/**
 * Effect Library
 * Collection of volumetric display effects
 */
import { PerlinNoise } from '../utils/PerlinNoise.js';
import { RainParticleSystem, StarfieldParticleSystem } from '../utils/ParticleSystems.js';

export class EffectLibrary {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        // Initialize utilities
        this.perlin = new PerlinNoise();
        this.rainSystem = new RainParticleSystem(gridX, gridY, gridZ);
        this.starSystem = new StarfieldParticleSystem(gridX, gridY, gridZ);

        // Initialize particle systems with default density
        this.rainSystem.init(0.1);
        this.starSystem.init(0.1);

        this.effects = this.createEffects();
    }

    updateDensity(density) {
        this.rainSystem.init(density);
        this.starSystem.init(density);
    }

    createEffects() {
        return [
            {
                name: 'Rotating Plane Slice',
                fn: (voxels, time, params) => {
                    const angle = time * params.speed * 0.5;
                    const normal = {
                        x: Math.cos(angle),
                        y: Math.sin(angle),
                        z: 0.3
                    };
                    const thickness = 2 + params.density * 3;

                    for (let x = 0; x < this.gridX; x++) {
                        for (let y = 0; y < this.gridY; y++) {
                            for (let z = 0; z < this.gridZ; z++) {
                                const cx = x - this.gridX / 2;
                                const cy = y - this.gridY / 2;
                                const cz = z - this.gridZ / 2;
                                const dist = Math.abs(cx * normal.x + cy * normal.y + cz * normal.z);
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = dist < thickness ? 1 : 0;
                            }
                        }
                    }
                }
            },
            {
                name: 'Pulsing Sphere',
                fn: (voxels, time, params) => {
                    const pulse = (Math.sin(time * params.speed) + 1) / 2;
                    const radius = 5 + pulse * (8 + params.density * 5);
                    const thickness = 1 + params.density * 2;

                    for (let x = 0; x < this.gridX; x++) {
                        for (let y = 0; y < this.gridY; y++) {
                            for (let z = 0; z < this.gridZ; z++) {
                                const dx = x - this.gridX / 2;
                                const dy = (y - this.gridY / 2) * 2; // Y is half the size, so scale it
                                const dz = z - this.gridZ / 2;
                                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] =
                                    Math.abs(dist - radius) < thickness ? 1 : 0;
                            }
                        }
                    }
                }
            },
            {
                name: 'Rain/Waterfall',
                fn: (voxels, time, params) => {
                    voxels.fill(0);
                    this.rainSystem.update(params.speed);

                    this.rainSystem.getParticles().forEach(p => {
                        const x = Math.floor(p.x);
                        const y = Math.floor(p.y);
                        const z = Math.floor(p.z);
                        if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                            voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                        }
                    });
                }
            },
            {
                name: 'Wave Ripple',
                fn: (voxels, time, params) => {
                    for (let x = 0; x < this.gridX; x++) {
                        for (let z = 0; z < this.gridZ; z++) {
                            const dx = x - this.gridX / 2;
                            const dz = z - this.gridZ / 2;
                            const dist = Math.sqrt(dx * dx + dz * dz);
                            const wave = Math.sin(dist * 0.3 - time * params.speed * 2) * (2 + params.density * 3);
                            const yPos = this.gridY / 2 + wave;

                            for (let y = 0; y < this.gridY; y++) {
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] =
                                    Math.abs(y - yPos) < 1.5 ? 1 : 0;
                            }
                        }
                    }
                }
            },
            {
                name: 'Helix Spiral',
                fn: (voxels, time, params) => {
                    voxels.fill(0);
                    const numStrands = Math.ceil(2 + params.density * 2);
                    const radius = 12 + params.density * 5;
                    const thickness = 2;

                    for (let strand = 0; strand < numStrands; strand++) {
                        const offset = (strand / numStrands) * Math.PI * 2;
                        // Spiral along Y axis (vertical)
                        for (let y = 0; y < this.gridY; y++) {
                            const angle = y * 0.8 + time * params.speed * 0.5 + offset;
                            const x = Math.floor(this.gridX / 2 + Math.cos(angle) * radius);
                            const z = Math.floor(this.gridZ / 2 + Math.sin(angle) * radius);

                            for (let dx = -thickness; dx <= thickness; dx++) {
                                for (let dz = -thickness; dz <= thickness; dz++) {
                                    const nx = x + dx;
                                    const nz = z + dz;
                                    if (nx >= 0 && nx < this.gridX && nz >= 0 && nz < this.gridZ) {
                                        voxels[nx + y * this.gridX + nz * this.gridX * this.gridY] = 1;
                                    }
                                }
                            }
                        }
                    }
                }
            },
            {
                name: 'Corner-to-Corner Sweep',
                fn: (voxels, time, params) => {
                    const progress = (Math.sin(time * params.speed * 0.5) + 1) / 2;
                    const sweepPos = progress * (this.gridX + this.gridY + this.gridZ);
                    const thickness = 3 + params.density * 4;

                    for (let x = 0; x < this.gridX; x++) {
                        for (let y = 0; y < this.gridY; y++) {
                            for (let z = 0; z < this.gridZ; z++) {
                                const sum = x + y + z;
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] =
                                    Math.abs(sum - sweepPos) < thickness ? 1 : 0;
                            }
                        }
                    }
                }
            },
            {
                name: 'Tunnel Zoom',
                fn: (voxels, time, params) => {
                    const offset = time * params.speed * 5;
                    const spacing = 3 + (1 - params.density) * 3;

                    for (let x = 0; x < this.gridX; x++) {
                        for (let y = 0; y < this.gridY; y++) {
                            const dx = x - this.gridX / 2;
                            const dy = y - this.gridY / 2;
                            const dist = Math.sqrt(dx * dx + dy * dy);

                            for (let z = 0; z < this.gridZ; z++) {
                                // Create expanding rings based on distance and depth
                                const pattern = (dist + z * 2 - offset) % spacing;
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] =
                                    pattern < 1.5 ? 1 : 0;
                            }
                        }
                    }
                }
            },
            {
                name: 'Starfield Depth',
                fn: (voxels, time, params) => {
                    voxels.fill(0);
                    this.starSystem.update(params.speed);

                    this.starSystem.getParticles().forEach(p => {
                        const x = Math.floor(p.x);
                        const y = Math.floor(p.y);
                        const z = Math.floor(p.z);
                        if (x >= 0 && x < this.gridX && y >= 0 && y < this.gridY && z >= 0 && z < this.gridZ) {
                            voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                        }
                    });
                }
            },
            {
                name: 'Perlin Noise Clouds',
                fn: (voxels, time, params) => {
                    const scale = 0.15 / params.density;
                    const threshold = 0.3 - params.density * 0.2;

                    for (let x = 0; x < this.gridX; x++) {
                        for (let y = 0; y < this.gridY; y++) {
                            for (let z = 0; z < this.gridZ; z++) {
                                const noise = this.perlin.noise(
                                    x * scale,
                                    y * scale,
                                    z * scale + time * params.speed * 0.1
                                );
                                voxels[x + y * this.gridX + z * this.gridX * this.gridY] = noise > threshold ? 1 : 0;
                            }
                        }
                    }
                }
            },
            {
                name: 'Layer Sequence',
                fn: (voxels, time, params) => {
                    voxels.fill(0);
                    const activeLayer = Math.floor((time * params.speed * 0.5) % this.gridZ);
                    const pattern = Math.floor((time * params.speed * 0.3) % 4);

                    for (let z = 0; z < this.gridZ; z++) {
                        const layerDist = Math.min(
                            Math.abs(z - activeLayer),
                            Math.abs(z - activeLayer + this.gridZ),
                            Math.abs(z - activeLayer - this.gridZ)
                        );

                        if (layerDist <= 2) {
                            for (let x = 0; x < this.gridX; x++) {
                                for (let y = 0; y < this.gridY; y++) {
                                    let lit = false;

                                    if (pattern === 0) { // Grid
                                        lit = (x % 4 === 0 || y % 4 === 0);
                                    } else if (pattern === 1) { // Checkerboard
                                        lit = ((x + y) % 2 === 0);
                                    } else if (pattern === 2) { // Rings
                                        const dx = x - this.gridX / 2;
                                        const dy = y - this.gridY / 2;
                                        const dist = Math.sqrt(dx * dx + dy * dy);
                                        lit = Math.floor(dist) % 3 === 0;
                                    } else { // Diagonal
                                        lit = (x + y) % 5 === 0;
                                    }

                                    if (lit && layerDist === 0) {
                                        voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 1;
                                    } else if (layerDist > 0 && Math.random() > 0.7) {
                                        voxels[x + y * this.gridX + z * this.gridX * this.gridY] = 0.3;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ];
    }

    getEffect(index) {
        return this.effects[index];
    }

    getEffectNames() {
        return this.effects.map(e => e.name);
    }

    getEffectCount() {
        return this.effects.length;
    }
}
