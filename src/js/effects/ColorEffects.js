/**
 * Advanced Color Effects Library
 * Post-processing color effects that avoid duplication with GlobalEffects
 *
 * NOTE: GlobalEffects (GlobalEffects.js) handles:
 * - Pulse (brightness oscillation)
 * - Strobe (on/off flashing)
 * These effects operate on the voxel buffer AFTER scene generation.
 *
 * ColorEffects handles per-voxel color manipulation during rendering.
 */
export class ColorEffects {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        this.time = 0;
        this.activeEffect = 'none'; // none, sparkle, rainbowSweep, fire, plasma, kaleidoscope, breath, colorChase,
                                     // waveMulti, waveVertical, waveCircular, waveStanding,
                                     // cycleHue, cyclePalette, cycleComplementary, cycleTriadic,
                                     // pulseRadial, pulseAlternating, pulseLayered, pulseBeat,
                                     // staticColor, staticDynamic, staticWave,
                                     // pulseWave, cyclePulse, waveChase, staticCycle, pulseTrail,
                                     // diagonalWaves, helix, vortex, tunnel,
                                     // perlinNoise, voronoi, checkerboard3D,
                                     // sineInterferenceXZ, sphericalShellsMoving, cornerExplosion,
                                     // depthLayers, cubeInCube, manhattanDistance,
                                     // xzMirror, directionalSweep
        this.intensity = 1.0; // 0-1
        this.speed = 1.0; // Speed multiplier for time-based effects

        // Color mode: 'rainbow' uses generated colors, 'base' modulates the base color
        this.colorMode = 'rainbow'; // rainbow or base

        // Effect-specific state
        this.sparkleMap = new Map(); // Track sparkle state per voxel
        this.sparkleFrequency = 0.01; // Chance per frame per voxel
        this.sparkleDuration = 0.3; // Seconds

        // Color palettes for cyclePalette effect
        this.colorPalettes = [
            [{r: 255, g: 0, b: 0}, {r: 255, g: 255, b: 0}, {r: 255, g: 0, b: 0}], // Red-Yellow
            [{r: 0, g: 255, b: 0}, {r: 0, g: 255, b: 255}, {r: 0, g: 255, b: 0}], // Green-Cyan
            [{r: 0, g: 0, b: 255}, {r: 255, g: 0, b: 255}, {r: 0, g: 0, b: 255}], // Blue-Magenta
            [{r: 255, g: 100, b: 0}, {r: 255, g: 0, b: 100}, {r: 255, g: 100, b: 0}], // Orange-Pink
            [{r: 100, g: 0, b: 255}, {r: 255, g: 0, b: 200}, {r: 100, g: 0, b: 255}] // Purple-Pink
        ];

        // Voronoi effect parameters
        this.voronoiSeeds = [];
        this.voronoiCellCount = 5;
        this.initVoronoiSeeds();

        // Perlin noise implementation (simplified)
        this.perlinPerm = this.generatePerlinPermutation();
    }

    /**
     * Set active effect
     */
    setEffect(effect) {
        this.activeEffect = effect;
        if (effect === 'sparkle') {
            this.sparkleMap.clear();
        }
    }

    /**
     * Set effect intensity (0-1)
     */
    setIntensity(intensity) {
        this.intensity = Math.max(0, Math.min(1, intensity));
    }

    /**
     * Set effect speed multiplier
     */
    setSpeed(speed) {
        this.speed = Math.max(0.1, Math.min(5, speed));
    }

    /**
     * Set color mode ('rainbow' or 'base')
     */
    setColorMode(mode) {
        this.colorMode = mode;
    }


    /**
     * Update time
     */
    update(deltaTime) {
        this.time += deltaTime;

        // Update sparkle map
        if (this.activeEffect === 'sparkle') {
            this.updateSparkles(deltaTime);
        }

        // Update Voronoi seeds
        if (this.activeEffect === 'voronoi') {
            this.updateVoronoiSeeds(deltaTime);
        }
    }

    /**
     * Apply effect to a color
     * @param {object} baseColor - {r, g, b}
     * @param {number} x - Grid X coordinate
     * @param {number} y - Grid Y coordinate
     * @param {number} z - Grid Z coordinate
     * @param {number} val - Voxel brightness value
     * @returns {object} - Modified {r, g, b}
     */
    applyEffect(baseColor, x, y, z, val) {
        if (this.activeEffect === 'none' || this.intensity === 0) {
            return baseColor;
        }

        let effectColor = { ...baseColor };

        switch (this.activeEffect) {
            case 'sparkle':
                effectColor = this.applySparkle(effectColor, x, y, z);
                break;

            case 'rainbowSweep':
                effectColor = this.applyRainbowSweep(effectColor, x, y, z);
                break;

            case 'fire':
                effectColor = this.applyFire(effectColor, x, y, z);
                break;

            case 'plasma':
                effectColor = this.applyPlasma(effectColor, x, y, z);
                break;

            case 'kaleidoscope':
                effectColor = this.applyKaleidoscope(effectColor, x, y, z);
                break;

            case 'breath':
                effectColor = this.applyBreath(effectColor, x, y, z);
                break;

            case 'colorChase':
                effectColor = this.applyColorChase(effectColor, x, y, z);
                break;

            // Wave-based effects
            case 'waveMulti':
                effectColor = this.applyWaveMulti(effectColor, x, y, z);
                break;

            case 'waveVertical':
                effectColor = this.applyWaveVertical(effectColor, x, y, z);
                break;

            case 'waveCircular':
                effectColor = this.applyWaveCircular(effectColor, x, y, z);
                break;

            case 'waveStanding':
                effectColor = this.applyWaveStanding(effectColor, x, y, z);
                break;

            // Cycle-based effects
            case 'cycleHue':
                effectColor = this.applyCycleHue(effectColor, x, y, z);
                break;

            case 'cyclePalette':
                effectColor = this.applyCyclePalette(effectColor, x, y, z);
                break;

            case 'cycleComplementary':
                effectColor = this.applyCycleComplementary(effectColor, x, y, z);
                break;

            case 'cycleTriadic':
                effectColor = this.applyCycleTriadic(effectColor, x, y, z);
                break;

            // Pulse-based effects
            case 'pulseRadial':
                effectColor = this.applyPulseRadial(effectColor, x, y, z);
                break;

            case 'pulseAlternating':
                effectColor = this.applyPulseAlternating(effectColor, x, y, z);
                break;

            case 'pulseLayered':
                effectColor = this.applyPulseLayered(effectColor, x, y, z);
                break;

            case 'pulseBeat':
                effectColor = this.applyPulseBeat(effectColor, x, y, z);
                break;

            // Static/noise effects
            case 'staticColor':
                effectColor = this.applyStaticColor(effectColor, x, y, z);
                break;

            case 'staticDynamic':
                effectColor = this.applyStaticDynamic(effectColor, x, y, z);
                break;

            case 'staticWave':
                effectColor = this.applyStaticWave(effectColor, x, y, z);
                break;

            // Combination effects
            case 'pulseWave':
                effectColor = this.applyPulseWave(effectColor, x, y, z);
                break;

            case 'cyclePulse':
                effectColor = this.applyCyclePulse(effectColor, x, y, z);
                break;

            case 'waveChase':
                effectColor = this.applyWaveChase(effectColor, x, y, z);
                break;

            case 'staticCycle':
                effectColor = this.applyStaticCycle(effectColor, x, y, z);
                break;

            case 'pulseTrail':
                effectColor = this.applyPulseTrail(effectColor, x, y, z);
                break;

            // New 3D Spatial effects
            case 'diagonalWaves':
                effectColor = this.applyDiagonalWaves(effectColor, x, y, z);
                break;

            case 'helix':
                effectColor = this.applyHelix(effectColor, x, y, z);
                break;

            case 'vortex':
                effectColor = this.applyVortex(effectColor, x, y, z);
                break;

            case 'tunnel':
                effectColor = this.applyTunnel(effectColor, x, y, z);
                break;

            // New Procedural effects
            case 'perlinNoise':
                effectColor = this.applyPerlinNoise(effectColor, x, y, z);
                break;

            case 'voronoi':
                effectColor = this.applyVoronoi(effectColor, x, y, z);
                break;

            case 'checkerboard3D':
                effectColor = this.applyCheckerboard3D(effectColor, x, y, z);
                break;

            // New Interference effects
            case 'sineInterferenceXZ':
                effectColor = this.applySineInterferenceXZ(effectColor, x, y, z);
                break;

            case 'sphericalShellsMoving':
                effectColor = this.applySphericalShellsMoving(effectColor, x, y, z);
                break;

            case 'cornerExplosion':
                effectColor = this.applyCornerExplosion(effectColor, x, y, z);
                break;

            // New Geometric effects
            case 'depthLayers':
                effectColor = this.applyDepthLayers(effectColor, x, y, z);
                break;

            case 'cubeInCube':
                effectColor = this.applyCubeInCube(effectColor, x, y, z);
                break;

            case 'manhattanDistance':
                effectColor = this.applyManhattanDistance(effectColor, x, y, z);
                break;

            // New Symmetry effects
            case 'xzMirror':
                effectColor = this.applyXZMirror(effectColor, x, y, z);
                break;

            case 'directionalSweep':
                effectColor = this.applyDirectionalSweep(effectColor, x, y, z);
                break;
        }

        // Blend with base color based on intensity
        return {
            r: baseColor.r * (1 - this.intensity) + effectColor.r * this.intensity,
            g: baseColor.g * (1 - this.intensity) + effectColor.g * this.intensity,
            b: baseColor.b * (1 - this.intensity) + effectColor.b * this.intensity
        };
    }

    /**
     * SPARKLE: Random voxels briefly flash bright white
     */
    updateSparkles(deltaTime) {
        // Remove expired sparkles
        const now = this.time;
        for (const [key, startTime] of this.sparkleMap.entries()) {
            if (now - startTime > this.sparkleDuration) {
                this.sparkleMap.delete(key);
            }
        }
    }

    applySparkle(color, x, y, z) {
        const key = `${x},${y},${z}`;

        // Check if this voxel is sparkling
        if (this.sparkleMap.has(key)) {
            const startTime = this.sparkleMap.get(key);
            const elapsed = this.time - startTime;
            const t = elapsed / this.sparkleDuration;

            // Fade in/out (peak at 0.3, fade out by 1.0)
            const brightness = t < 0.3 ? t / 0.3 : (1 - t) / 0.7;

            return {
                r: 255,
                g: 255,
                b: 255,
                brightness // Extra property for brightness multiplier
            };
        }

        // Random chance to start sparkling
        if (Math.random() < this.sparkleFrequency) {
            this.sparkleMap.set(key, this.time);
        }

        return color;
    }

    /**
     * RAINBOW SWEEP: Full spectrum sweep across space
     */
    applyRainbowSweep(color, x, y, z) {
        // Create a wave that sweeps through space
        const wave = (x + y + z + this.time * 10) * 0.1;
        const hue = (wave * 60) % 360;

        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    /**
     * FIRE: Flickering warm colors with upward bias
     */
    applyFire(color, x, y, z) {
        // More intense at bottom, cooler at top
        const heightFactor = 1 - (y / this.gridY);

        // Flicker using multiple noise functions
        const flicker = Math.sin(this.time * 5 + x * 0.3 + z * 0.3) * 0.3 +
                       Math.sin(this.time * 8 + x * 0.5) * 0.2;

        const intensity = (heightFactor * 0.7 + 0.3) + flicker;

        // Fire colors: yellow-orange-red
        const temp = heightFactor + Math.sin(this.time * 3 + y * 0.1) * 0.3;

        if (temp > 0.7) {
            // Yellow (hot)
            return {
                r: 255 * intensity,
                g: 255 * intensity,
                b: 100 * intensity
            };
        } else if (temp > 0.3) {
            // Orange
            return {
                r: 255 * intensity,
                g: 150 * intensity,
                b: 50 * intensity
            };
        } else {
            // Red (cooler)
            return {
                r: 255 * intensity,
                g: 50 * intensity,
                b: 0
            };
        }
    }

    /**
     * PLASMA: Multi-sine wave interference pattern
     */
    applyPlasma(color, x, y, z) {
        const nx = x / this.gridX;
        const ny = y / this.gridY;
        const nz = z / this.gridZ;

        // Multiple sine waves
        const v1 = Math.sin(nx * 10 + this.time);
        const v2 = Math.sin(ny * 10 - this.time * 0.7);
        const v3 = Math.sin((nx + ny + nz) * 8 + this.time * 0.5);
        const v4 = Math.sin(Math.sqrt((nx - 0.5) ** 2 + (nz - 0.5) ** 2) * 20 + this.time);

        const plasma = (v1 + v2 + v3 + v4) / 4;

        // Map to color spectrum
        const hue = (plasma + 1) * 180; // 0-360
        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    /**
     * KALEIDOSCOPE: Mirror colors across axes with symmetry
     */
    applyKaleidoscope(color, x, y, z) {
        // Mirror coordinates from center
        const cx = Math.abs(x - this.gridX / 2);
        const cy = Math.abs(y - this.gridY / 2);
        const cz = Math.abs(z - this.gridZ / 2);

        // Create radial pattern
        const angle = Math.atan2(cy, cx) + this.time * 0.5;
        const radius = Math.sqrt(cx * cx + cz * cz);

        // Kaleidoscope segments (6-fold symmetry)
        const segments = 6;
        const segmentAngle = (angle * segments) % (Math.PI * 2);

        const hue = (segmentAngle / (Math.PI * 2) * 360 + radius * 10) % 360;

        return this.hslToRgb(hue / 360, 0.9, 0.5);
    }

    /**
     * BREATH: Slow saturation oscillation (NOT brightness)
     */
    applyBreath(color, x, y, z) {
        // Convert to HSL
        const hsl = this.rgbToHsl(color.r, color.g, color.b);

        // Oscillate saturation slowly
        const breathCycle = (Math.sin(this.time * 0.5) + 1) / 2; // 0-1
        const newSaturation = 0.3 + breathCycle * 0.7; // 0.3-1.0

        return this.hslToRgb(hsl.h, newSaturation, hsl.l);
    }

    /**
     * COLOR CHASE: Moving pattern/wave of color across grid
     */
    applyColorChase(color, x, y, z) {
        // Create a wave moving through the grid
        const wave1 = Math.sin((x * 0.3 + this.time * 3)) * 0.5 + 0.5;
        const wave2 = Math.sin((z * 0.3 + this.time * 3 + Math.PI)) * 0.5 + 0.5;

        // Combine waves
        const combined = (wave1 + wave2) / 2;

        // Map to hue
        const hue = combined * 360;

        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    // ========================================
    // WAVE-BASED EFFECTS
    // ========================================

    /**
     * WAVE MULTI: Multiple wave sources with interference
     */
    applyWaveMulti(color, x, y, z) {
        const sources = [
            {x: this.gridX / 4, z: this.gridZ / 4},
            {x: 3 * this.gridX / 4, z: this.gridZ / 4},
            {x: this.gridX / 2, z: 3 * this.gridZ / 4}
        ];

        let totalWave = 0;
        sources.forEach(source => {
            const dx = x - source.x;
            const dz = z - source.z;
            const dist = Math.sqrt(dx * dx + dz * dz);
            totalWave += Math.sin(dist * 0.3 - this.time * this.speed * 2);
        });

        const waveValue = (totalWave / sources.length + 1) / 2; // Normalize to 0-1
        const hue = waveValue * 360;

        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    /**
     * WAVE VERTICAL: Vertical waves moving up/down through Y axis
     */
    applyWaveVertical(color, x, y, z) {
        const wave = Math.sin(y * 0.3 - this.time * this.speed * 2);
        const hue = (wave + 1) * 180; // 0-360

        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    /**
     * WAVE CIRCULAR: Expanding circular waves from center
     */
    applyWaveCircular(color, x, y, z) {
        const dx = x - this.gridX / 2;
        const dz = z - this.gridZ / 2;
        const dist = Math.sqrt(dx * dx + dz * dz);
        const wave = Math.sin(dist * 0.5 - this.time * this.speed * 3);

        const hue = (wave + 1) * 180; // 0-360

        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    /**
     * WAVE STANDING: Standing wave patterns (oscillates but doesn't travel)
     */
    applyWaveStanding(color, x, y, z) {
        const waveX = Math.sin(x * 0.3);
        const waveZ = Math.sin(z * 0.3);
        const timeFactor = Math.sin(this.time * this.speed * 2);
        const combined = (waveX * waveZ * timeFactor + 1) / 2;

        const hue = combined * 360;

        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    // ========================================
    // CYCLE-BASED EFFECTS
    // ========================================

    /**
     * CYCLE HUE: Smooth hue rotation through entire spectrum
     */
    applyCycleHue(color, x, y, z) {
        const hsl = this.rgbToHsl(color.r, color.g, color.b);
        const hue = (hsl.h + this.time * this.speed * 0.2) % 1.0;

        return this.hslToRgb(hue, hsl.s, hsl.l);
    }

    /**
     * CYCLE PALETTE: Cycle through predefined color palettes
     */
    applyCyclePalette(color, x, y, z) {
        const paletteIndex = Math.floor(this.time * this.speed * 0.3) % this.colorPalettes.length;
        const palette = this.colorPalettes[paletteIndex];

        // Interpolate within the palette based on position
        const nx = x / this.gridX;
        const ny = y / this.gridY;
        const nz = z / this.gridZ;
        const t = (nx + ny + nz) / 3;

        const scaledT = t * (palette.length - 1);
        const index = Math.floor(scaledT);
        const frac = scaledT - index;

        const c1 = palette[Math.min(index, palette.length - 1)];
        const c2 = palette[Math.min(index + 1, palette.length - 1)];

        return {
            r: c1.r + (c2.r - c1.r) * frac,
            g: c1.g + (c2.g - c1.g) * frac,
            b: c1.b + (c2.b - c1.b) * frac
        };
    }

    /**
     * CYCLE COMPLEMENTARY: Cycle between complementary colors
     */
    applyCycleComplementary(color, x, y, z) {
        const baseHue = (this.time * this.speed * 0.1) % 1.0;
        const compHue = (baseHue + 0.5) % 1.0;

        // Alternate between base and complementary based on position
        const dx = x - this.gridX / 2;
        const dz = z - this.gridZ / 2;
        const dist = Math.sqrt(dx * dx + dz * dz);
        const useComp = Math.floor(dist / 5) % 2 === 0;

        const hue = useComp ? compHue : baseHue;

        return this.hslToRgb(hue, 1.0, 0.5);
    }

    /**
     * CYCLE TRIADIC: Cycle through triadic color harmony
     */
    applyCycleTriadic(color, x, y, z) {
        const baseHue = (this.time * this.speed * 0.1) % 1.0;
        const hue2 = (baseHue + 1/3) % 1.0;
        const hue3 = (baseHue + 2/3) % 1.0;

        // Choose hue based on 3D position
        const sum = (x + y + z);
        const section = Math.floor(sum / 10) % 3;

        let hue;
        if (section === 0) hue = baseHue;
        else if (section === 1) hue = hue2;
        else hue = hue3;

        return this.hslToRgb(hue, 1.0, 0.5);
    }

    // ========================================
    // PULSE-BASED EFFECTS
    // ========================================

    /**
     * PULSE RADIAL: Pulse emanating from center
     */
    applyPulseRadial(color, x, y, z) {
        const dx = x - this.gridX / 2;
        const dy = y - this.gridY / 2;
        const dz = z - this.gridZ / 2;
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        const pulse = Math.sin(this.time * this.speed * 3 - dist * 0.2);
        const brightness = (pulse + 1) / 2;

        const hsl = this.rgbToHsl(color.r, color.g, color.b);
        return this.hslToRgb(hsl.h, hsl.s, brightness * 0.8 + 0.2);
    }

    /**
     * PULSE ALTERNATING: Different areas pulse out of phase
     */
    applyPulseAlternating(color, x, y, z) {
        const dx = x - this.gridX / 2;
        const dz = z - this.gridZ / 2;
        const angle = Math.atan2(dz, dx);
        const sector = Math.floor((angle + Math.PI) / (Math.PI / 4)); // 8 sectors
        const phase = sector * Math.PI / 4;

        const pulse = Math.sin(this.time * this.speed * 2 + phase);
        const brightness = (pulse + 1) / 2;

        const hsl = this.rgbToHsl(color.r, color.g, color.b);
        return this.hslToRgb(hsl.h, hsl.s, brightness * 0.8 + 0.2);
    }

    /**
     * PULSE LAYERED: Each Y layer pulses with delay
     */
    applyPulseLayered(color, x, y, z) {
        const pulse = Math.sin(this.time * this.speed * 2 + y * 0.5);
        const brightness = (pulse + 1) / 2;

        const hsl = this.rgbToHsl(color.r, color.g, color.b);
        return this.hslToRgb(hsl.h, hsl.s, brightness * 0.8 + 0.2);
    }

    /**
     * PULSE BEAT: Double-pulse heartbeat effect
     */
    applyPulseBeat(color, x, y, z) {
        const t = (this.time * this.speed) % 2;
        let pulse;

        if (t < 0.3) {
            // First beat
            pulse = Math.sin(t * 10);
        } else if (t < 0.7) {
            // Second beat
            pulse = Math.sin((t - 0.3) * 8);
        } else {
            // Rest
            pulse = 0;
        }

        const brightness = (pulse + 1) / 2;

        const hsl = this.rgbToHsl(color.r, color.g, color.b);
        return this.hslToRgb(hsl.h, hsl.s, brightness * 0.8 + 0.2);
    }

    // ========================================
    // STATIC/NOISE EFFECTS
    // ========================================

    /**
     * STATIC COLOR: Random color per voxel
     */
    applyStaticColor(color, x, y, z) {
        // Use position-based pseudo-random + time for animated static
        const seed = x * 374761393 + y * 668265263 + z * 1274126177 + Math.floor(this.time * this.speed * 10);
        const random = ((seed ^ (seed >> 16)) * 0x85ebca6b) & 0xFFFFFFFF;
        const hue = (random / 0xFFFFFFFF);

        return this.hslToRgb(hue, 1.0, 0.5);
    }

    /**
     * STATIC DYNAMIC: Static that changes intensity
     */
    applyStaticDynamic(color, x, y, z) {
        // Position-based pseudo-random
        const seed = x * 374761393 + y * 668265263 + z * 1274126177;
        const random = ((seed ^ (seed >> 16)) * 0x85ebca6b) & 0xFFFFFFFF;
        const noise = random / 0xFFFFFFFF;

        // Pulsing brightness
        const pulse = Math.sin(this.time * this.speed * 3);
        const brightness = noise * ((pulse + 1) / 2);

        const hsl = this.rgbToHsl(color.r, color.g, color.b);
        return this.hslToRgb(hsl.h, hsl.s, brightness * 0.8 + 0.2);
    }

    /**
     * STATIC WAVE: Static pattern that travels like a wave
     */
    applyStaticWave(color, x, y, z) {
        // Moving noise pattern
        const offset = this.time * this.speed * 3;
        const nx = (x + offset) * 0.2;
        const ny = y * 0.2;
        const nz = z * 0.2;

        // Simple noise using sin waves
        const noise1 = Math.sin(nx) * Math.cos(nz);
        const noise2 = Math.sin(ny + nx) * Math.cos(nz + ny);
        const combined = (noise1 + noise2 + 2) / 4; // Normalize to 0-1

        const hue = combined * 360;

        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    // ========================================
    // COMBINATION EFFECTS
    // ========================================

    /**
     * PULSE WAVE: Pulsing waves
     */
    applyPulseWave(color, x, y, z) {
        const dx = x - this.gridX / 2;
        const dz = z - this.gridZ / 2;
        const dist = Math.sqrt(dx * dx + dz * dz);

        // Wave component
        const wave = Math.sin(dist * 0.3 - this.time * this.speed * 2);

        // Pulse component
        const pulse = Math.sin(this.time * this.speed * 5);

        const combined = wave * (0.5 + pulse * 0.5);
        const hue = (combined + 1) * 180;

        return this.hslToRgb(hue / 360, 1.0, 0.5);
    }

    /**
     * CYCLE PULSE: Color cycling with pulse intensity
     */
    applyCyclePulse(color, x, y, z) {
        // Hue rotates
        const hue = (this.time * this.speed * 0.2) % 1.0;

        // Brightness pulses
        const pulse = Math.sin(this.time * this.speed * 3);
        const brightness = 0.3 + ((pulse + 1) / 2) * 0.5; // 0.3 to 0.8

        return this.hslToRgb(hue, 1.0, brightness);
    }

    /**
     * WAVE CHASE: Multiple colored waves chasing each other
     */
    applyWaveChase(color, x, y, z) {
        const dx = x - this.gridX / 2;
        const dz = z - this.gridZ / 2;
        const dist = Math.sqrt(dx * dx + dz * dz);

        // Three waves with different speeds
        const wave1 = Math.sin(dist * 0.3 - this.time * this.speed * 2);
        const wave2 = Math.sin(dist * 0.3 - this.time * this.speed * 2.3 + Math.PI / 3);
        const wave3 = Math.sin(dist * 0.3 - this.time * this.speed * 2.6 + 2 * Math.PI / 3);

        // Map to RGB
        const r = ((wave1 + 1) / 2) * 255;
        const g = ((wave2 + 1) / 2) * 255;
        const b = ((wave3 + 1) / 2) * 255;

        return { r, g, b };
    }

    /**
     * STATIC CYCLE: Static that changes color over time
     */
    applyStaticCycle(color, x, y, z) {
        // Position-based pseudo-random for static pattern
        const seed = x * 374761393 + y * 668265263 + z * 1274126177;
        const random = ((seed ^ (seed >> 16)) * 0x85ebca6b) & 0xFFFFFFFF;
        const noise = random / 0xFFFFFFFF;

        // Cycling hue
        const baseHue = (this.time * this.speed * 0.2) % 1.0;
        const hue = (baseHue + noise * 0.3) % 1.0;

        return this.hslToRgb(hue, 1.0, 0.5);
    }

    /**
     * PULSE TRAIL: Pulsing effect with trailing fade
     */
    applyPulseTrail(color, x, y, z) {
        const dx = x - this.gridX / 2;
        const dy = y - this.gridY / 2;
        const dz = z - this.gridZ / 2;
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        // Pulse with spatial falloff
        const pulse = Math.sin(this.time * this.speed * 3 - dist * 0.3);

        // Create trailing effect
        const trail = Math.max(0, pulse);
        const brightness = trail * 0.8 + 0.2;

        const hsl = this.rgbToHsl(color.r, color.g, color.b);
        return this.hslToRgb(hsl.h, hsl.s, brightness);
    }

    /**
     * Convert HSL to RGB
     */
    hslToRgb(h, s, l) {
        let r, g, b;

        if (s === 0) {
            r = g = b = l;
        } else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1/6) return p + (q - p) * 6 * t;
                if (t < 1/2) return q;
                if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
            };

            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1/3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1/3);
        }

        return {
            r: Math.round(r * 255),
            g: Math.round(g * 255),
            b: Math.round(b * 255)
        };
    }

    /**
     * Convert RGB to HSL
     */
    rgbToHsl(r, g, b) {
        r /= 255;
        g /= 255;
        b /= 255;

        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0;
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

            switch (max) {
                case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
                case g: h = ((b - r) / d + 2) / 6; break;
                case b: h = ((r - g) / d + 4) / 6; break;
            }
        }

        return { h, s, l };
    }

    /**
     * Helper: Apply color mode to effect
     * If colorMode is 'base', modulate the baseColor with the pattern value (0-1)
     * If colorMode is 'rainbow', return the rainbow color directly
     *
     * @param {object} baseColor - Original color {r, g, b}
     * @param {object} rainbowColor - Generated rainbow color {r, g, b}
     * @param {number} patternValue - Pattern value 0-1 for base color modulation
     * @returns {object} - Final color {r, g, b}
     */
    applyColorMode(baseColor, rainbowColor, patternValue) {
        if (this.colorMode === 'base') {
            // Modulate base color brightness/saturation based on pattern
            const hsl = this.rgbToHsl(baseColor.r, baseColor.g, baseColor.b);
            // Vary lightness based on pattern
            const newLightness = 0.2 + patternValue * 0.6; // Range 0.2 to 0.8
            return this.hslToRgb(hsl.h, hsl.s, newLightness);
        } else {
            // Return rainbow color
            return rainbowColor;
        }
    }

    // ========================================
    // NEW 3D SPATIAL EFFECTS
    // ========================================

    /**
     * DIAGONAL WAVES: Corner-to-corner wave travel along XYZ diagonals
     */
    applyDiagonalWaves(color, x, y, z) {
        // Three different diagonal directions
        const diag1 = (x + y + z) / Math.sqrt(3); // Main diagonal
        const diag2 = (x - y + z) / Math.sqrt(3); // Cross diagonal 1
        const diag3 = (x + y - z) / Math.sqrt(3); // Cross diagonal 2

        // Create traveling waves along each diagonal
        const wave1 = Math.sin(diag1 * 0.2 - this.time * this.speed * 2);
        const wave2 = Math.sin(diag2 * 0.2 - this.time * this.speed * 2.3);
        const wave3 = Math.sin(diag3 * 0.2 - this.time * this.speed * 2.7);

        // Combine waves and map to hue
        const combined = (wave1 + wave2 + wave3) / 3;
        const patternValue = (combined + 1) / 2; // 0-1
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * HELIX: Twisting spiral around axis with color rotation
     */
    applyHelix(color, x, y, z) {
        const cx = x - this.gridX / 2;
        const cz = z - this.gridZ / 2;

        // Distance from center axis
        const radius = Math.sqrt(cx * cx + cz * cz);

        // Angle around the axis
        const angle = Math.atan2(cz, cx);

        // Create helix by combining Y position with rotation
        const helixAngle = angle + y * 0.3 + this.time * this.speed;

        // Color based on helix angle and radius
        const patternValue = ((helixAngle / (Math.PI * 2)) % 1.0 + 1) % 1.0;
        const hue = patternValue * 360;
        const saturation = 0.7 + Math.sin(radius * 0.2) * 0.3;

        const rainbowColor = this.hslToRgb(hue / 360, saturation, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * VORTEX: Swirling inward/outward with angular velocity
     */
    applyVortex(color, x, y, z) {
        const cx = x - this.gridX / 2;
        const cy = y - this.gridY / 2;
        const cz = z - this.gridZ / 2;

        // Distance from center
        const radius = Math.sqrt(cx * cx + cz * cz);

        // Angle around vertical axis
        const angle = Math.atan2(cz, cx);

        // Angular velocity increases towards center (tornado effect)
        const angularSpeed = radius > 0 ? 10 / (radius + 1) : 10;
        const vortexAngle = angle + angularSpeed * this.time * this.speed;

        // Color spiral
        const patternValue = ((vortexAngle / (Math.PI * 2)) % 1.0 + cy / this.gridY) % 1.0;

        // Brightness falls off with distance
        const brightness = 0.3 + 0.5 / (1 + radius * 0.1);

        const rainbowColor = this.hslToRgb(patternValue, 1.0, brightness);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * TUNNEL: Rectangular tunnel receding with color bands
     */
    applyTunnel(color, x, y, z) {
        const cx = x - this.gridX / 2;
        const cy = y - this.gridY / 2;

        // Distance to nearest edge (rectangular tunnel)
        const distX = Math.abs(cx);
        const distY = Math.abs(cy);
        const tunnelDist = Math.max(distX / (this.gridX / 2), distY / (this.gridY / 2));

        // Perspective depth
        const depth = z / this.gridZ;

        // Create bands along tunnel depth
        const bands = (depth + tunnelDist + this.time * this.speed * 0.3) * 10;
        const patternValue = bands % 1.0;
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    // ========================================
    // NEW PROCEDURAL EFFECTS
    // ========================================

    /**
     * Generate permutation table for Perlin noise
     */
    generatePerlinPermutation() {
        const p = [];
        for (let i = 0; i < 256; i++) p[i] = i;
        // Shuffle
        for (let i = 255; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [p[i], p[j]] = [p[j], p[i]];
        }
        return [...p, ...p]; // Duplicate for wrapping
    }

    /**
     * Perlin noise helper functions
     */
    perlinFade(t) {
        return t * t * t * (t * (t * 6 - 15) + 10);
    }

    perlinLerp(t, a, b) {
        return a + t * (b - a);
    }

    perlinGrad(hash, x, y, z) {
        const h = hash & 15;
        const u = h < 8 ? x : y;
        const v = h < 4 ? y : h === 12 || h === 14 ? x : z;
        return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
    }

    /**
     * 3D Perlin noise
     */
    perlinNoise3D(x, y, z) {
        const X = Math.floor(x) & 255;
        const Y = Math.floor(y) & 255;
        const Z = Math.floor(z) & 255;

        x -= Math.floor(x);
        y -= Math.floor(y);
        z -= Math.floor(z);

        const u = this.perlinFade(x);
        const v = this.perlinFade(y);
        const w = this.perlinFade(z);

        const p = this.perlinPerm;
        const A = p[X] + Y;
        const AA = p[A] + Z;
        const AB = p[A + 1] + Z;
        const B = p[X + 1] + Y;
        const BA = p[B] + Z;
        const BB = p[B + 1] + Z;

        return this.perlinLerp(w,
            this.perlinLerp(v,
                this.perlinLerp(u, this.perlinGrad(p[AA], x, y, z),
                                this.perlinGrad(p[BA], x - 1, y, z)),
                this.perlinLerp(u, this.perlinGrad(p[AB], x, y - 1, z),
                                this.perlinGrad(p[BB], x - 1, y - 1, z))),
            this.perlinLerp(v,
                this.perlinLerp(u, this.perlinGrad(p[AA + 1], x, y, z - 1),
                                this.perlinGrad(p[BA + 1], x - 1, y, z - 1)),
                this.perlinLerp(u, this.perlinGrad(p[AB + 1], x, y - 1, z - 1),
                                this.perlinGrad(p[BB + 1], x - 1, y - 1, z - 1))));
    }

    /**
     * PERLIN NOISE: Organic cloud-like color patterns
     */
    applyPerlinNoise(color, x, y, z) {
        const scale = 0.1;
        const noise = this.perlinNoise3D(
            x * scale,
            y * scale,
            (z + this.time * this.speed * 5) * scale
        );

        // Map noise (-1 to 1) to 0-1
        const patternValue = (noise + 1) / 2;
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 0.8, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * Initialize Voronoi seed points
     */
    initVoronoiSeeds() {
        this.voronoiSeeds = [];
        for (let i = 0; i < this.voronoiCellCount; i++) {
            this.voronoiSeeds.push({
                x: Math.random() * this.gridX,
                y: Math.random() * this.gridY,
                z: Math.random() * this.gridZ,
                hue: Math.random() * 360,
                // Velocity for animation
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2,
                vz: (Math.random() - 0.5) * 2
            });
        }
    }

    /**
     * Update Voronoi seeds (called during update)
     */
    updateVoronoiSeeds(deltaTime) {
        this.voronoiSeeds.forEach(seed => {
            // Move seed
            seed.x += seed.vx * deltaTime * this.speed;
            seed.y += seed.vy * deltaTime * this.speed;
            seed.z += seed.vz * deltaTime * this.speed;

            // Wrap around boundaries
            if (seed.x < 0 || seed.x > this.gridX) seed.vx *= -1;
            if (seed.y < 0 || seed.y > this.gridY) seed.vy *= -1;
            if (seed.z < 0 || seed.z > this.gridZ) seed.vz *= -1;

            seed.x = Math.max(0, Math.min(this.gridX, seed.x));
            seed.y = Math.max(0, Math.min(this.gridY, seed.y));
            seed.z = Math.max(0, Math.min(this.gridZ, seed.z));
        });
    }

    /**
     * VORONOI: Cellular structures with moving seed points
     */
    applyVoronoi(color, x, y, z) {
        let minDist = Infinity;
        let nearestSeed = null;

        // Find nearest seed
        this.voronoiSeeds.forEach(seed => {
            const dx = x - seed.x;
            const dy = y - seed.y;
            const dz = z - seed.z;
            const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

            if (dist < minDist) {
                minDist = dist;
                nearestSeed = seed;
            }
        });

        if (nearestSeed) {
            // Pattern value based on seed's hue
            const patternValue = nearestSeed.hue / 360;
            const rainbowColor = this.hslToRgb(patternValue, 1.0, 0.5);
            return this.applyColorMode(color, rainbowColor, patternValue);
        }

        return color;
    }

    /**
     * CHECKERBOARD 3D: 3D alternating pattern with animation
     */
    applyCheckerboard3D(color, x, y, z) {
        const gridSize = 4 + Math.floor(Math.sin(this.time * this.speed * 0.5) * 2); // Animate grid size 2-6

        const cellX = Math.floor(x / gridSize);
        const cellY = Math.floor(y / gridSize);
        const cellZ = Math.floor(z / gridSize);

        // 3D checkerboard pattern
        const isEven = (cellX + cellY + cellZ) % 2 === 0;

        // Rotate hue over time
        const baseHue = (this.time * this.speed * 30) % 360;
        const hue = isEven ? baseHue : (baseHue + 180) % 360;
        const patternValue = isEven ? 0.25 : 0.75;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    // ========================================
    // NEW INTERFERENCE EFFECTS
    // ========================================

    /**
     * SINE INTERFERENCE XZ: Horizontal wave interference patterns
     */
    applySineInterferenceXZ(color, x, y, z) {
        // Multiple wave sources in XZ plane
        const wave1 = Math.sin(x * 0.3 - this.time * this.speed * 2);
        const wave2 = Math.sin(z * 0.3 - this.time * this.speed * 2.5);
        const wave3 = Math.sin((x + z) * 0.2 - this.time * this.speed * 1.8);
        const wave4 = Math.sin((x - z) * 0.2 + this.time * this.speed * 2.2);

        // Interference pattern
        const interference = (wave1 + wave2 + wave3 + wave4) / 4;
        const patternValue = (interference + 1) / 2;
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * SPHERICAL SHELLS MOVING: Dynamic bubble effects with moving center
     */
    applySphericalShellsMoving(color, x, y, z) {
        // Center point moves over time
        const centerX = this.gridX / 2 + Math.sin(this.time * this.speed * 0.5) * this.gridX * 0.3;
        const centerY = this.gridY / 2 + Math.cos(this.time * this.speed * 0.7) * this.gridY * 0.3;
        const centerZ = this.gridZ / 2 + Math.sin(this.time * this.speed * 0.3) * this.gridZ * 0.3;

        const dx = x - centerX;
        const dy = y - centerY;
        const dz = z - centerZ;
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        // Concentric shells
        const shell = (dist + this.time * this.speed * 5) % 10;
        const patternValue = shell / 10;
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * CORNER EXPLOSION: Colors radiate from all 8 corners simultaneously
     */
    applyCornerExplosion(color, x, y, z) {
        const corners = [
            [0, 0, 0],
            [this.gridX, 0, 0],
            [0, this.gridY, 0],
            [0, 0, this.gridZ],
            [this.gridX, this.gridY, 0],
            [this.gridX, 0, this.gridZ],
            [0, this.gridY, this.gridZ],
            [this.gridX, this.gridY, this.gridZ]
        ];

        let minDist = Infinity;
        let cornerIndex = 0;

        // Find nearest corner
        corners.forEach((corner, i) => {
            const dx = x - corner[0];
            const dy = y - corner[1];
            const dz = z - corner[2];
            const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

            if (dist < minDist) {
                minDist = dist;
                cornerIndex = i;
            }
        });

        // Each corner gets a different base hue
        const baseHue = (cornerIndex / corners.length) * 360;

        // Pulse from corners
        const pulse = Math.sin(minDist * 0.2 - this.time * this.speed * 3);
        const patternValue = ((baseHue / 360) + (pulse + 1) / 2 * 0.2) % 1.0;
        const hue = (baseHue + pulse * 60) % 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    // ========================================
    // NEW GEOMETRIC EFFECTS
    // ========================================

    /**
     * DEPTH LAYERS: Front-to-back color bands (Z-axis layers)
     */
    applyDepthLayers(color, x, y, z) {
        // Create color layers based on Z depth
        const layers = 5;
        const layerSize = this.gridZ / layers;
        const currentLayer = Math.floor((z + this.time * this.speed * 2) % this.gridZ / layerSize);

        const patternValue = currentLayer / layers;
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * CUBE IN CUBE: Nested cubic shells
     */
    applyCubeInCube(color, x, y, z) {
        const cx = Math.abs(x - this.gridX / 2);
        const cy = Math.abs(y - this.gridY / 2);
        const cz = Math.abs(z - this.gridZ / 2);

        // Distance to nearest face of cube
        const maxDist = Math.max(cx / (this.gridX / 2), cy / (this.gridY / 2), cz / (this.gridZ / 2));

        // Create concentric cubes
        const shell = (maxDist * 10 + this.time * this.speed * 2) % 10;
        const patternValue = shell / 10;
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * MANHATTAN DISTANCE: Taxicab metric for blocky gradients
     */
    applyManhattanDistance(color, x, y, z) {
        const cx = Math.abs(x - this.gridX / 2);
        const cy = Math.abs(y - this.gridY / 2);
        const cz = Math.abs(z - this.gridZ / 2);

        // Manhattan distance instead of Euclidean
        const manhattanDist = cx + cy + cz;
        const maxDist = this.gridX / 2 + this.gridY / 2 + this.gridZ / 2;

        // Normalize and map to hue
        const patternValue = (manhattanDist / maxDist + this.time * this.speed * 0.1) % 1.0;
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    // ========================================
    // NEW SYMMETRY EFFECTS
    // ========================================

    /**
     * XZ MIRROR: Horizontal plane symmetry (flip colors across middle)
     */
    applyXZMirror(color, x, y, z) {
        // Mirror Y coordinate across middle
        const mirrorY = y < this.gridY / 2 ? y : this.gridY - y;

        // Create gradient based on mirrored position
        const patternValue = mirrorY / (this.gridY / 2);
        const hue = (patternValue * 360 + this.time * this.speed * 30) % 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * DIRECTIONAL SWEEP: Planar wave along arbitrary vector with rotation
     */
    applyDirectionalSweep(color, x, y, z) {
        // Rotating direction vector
        const angle = this.time * this.speed * 0.3;
        const dirX = Math.cos(angle);
        const dirY = Math.sin(angle * 0.7);
        const dirZ = Math.sin(angle * 0.5);

        // Normalize direction
        const len = Math.sqrt(dirX * dirX + dirY * dirY + dirZ * dirZ);
        const nx = dirX / len;
        const ny = dirY / len;
        const nz = dirZ / len;

        // Dot product gives distance along direction vector
        const dist = x * nx + y * ny + z * nz;

        // Create sweeping wave
        const wave = Math.sin(dist * 0.2 - this.time * this.speed * 2);
        const patternValue = (wave + 1) / 2;
        const hue = patternValue * 360;

        const rainbowColor = this.hslToRgb(hue / 360, 1.0, 0.5);
        return this.applyColorMode(color, rainbowColor, patternValue);
    }

    /**
     * Reset effect state
     */
    reset() {
        this.time = 0;
        this.sparkleMap.clear();
        this.initVoronoiSeeds();
    }
}
