/**
 * 3D Color Mapping System
 * Advanced gradient mapping in 3D space
 */
export class ColorMapper3D {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        // Gradient configuration
        this.enabled = false;
        this.gradientType = 'linear-y'; // linear-x, linear-y, linear-z, radial, spherical, cylindrical
        this.colorStops = [
            { position: 0, color: { r: 100, g: 200, b: 255 } },
            { position: 1, color: { r: 255, g: 100, b: 200 } }
        ];

        // Origin point (normalized 0-1)
        this.origin = { x: 0.5, y: 0.5, z: 0.5 };

        // Falloff curve
        this.falloff = 'linear'; // linear, quadratic, cubic, smoothstep

        // Invert gradient
        this.invert = false;

        // Cache for optimization
        this.cache = {
            enabled: false,
            maxDistance: 0,
            originGrid: { x: 0, y: 0, z: 0 }
        };

        this.updateCache();
    }

    /**
     * Enable/disable 3D gradient mapping
     */
    setEnabled(enabled) {
        this.enabled = enabled;
    }

    /**
     * Set gradient type
     */
    setGradientType(type) {
        this.gradientType = type;
        this.updateCache();
    }

    /**
     * Set color stops (array of {position: 0-1, color: {r,g,b}})
     */
    setColorStops(stops) {
        // Sort by position
        this.colorStops = stops.sort((a, b) => a.position - b.position);
    }

    /**
     * Set origin point (normalized 0-1 coordinates)
     */
    setOrigin(x, y, z) {
        this.origin = { x, y, z };
        this.updateCache();
    }

    /**
     * Set falloff curve type
     */
    setFalloff(falloff) {
        this.falloff = falloff;
    }

    /**
     * Set invert state
     */
    setInvert(invert) {
        this.invert = invert;
    }

    /**
     * Update cached values for optimization
     */
    updateCache() {
        // Convert origin to grid coordinates
        this.cache.originGrid = {
            x: this.origin.x * this.gridX,
            y: this.origin.y * this.gridY,
            z: this.origin.z * this.gridZ
        };

        // Calculate maximum possible distance for normalization
        const dx = Math.max(this.cache.originGrid.x, this.gridX - this.cache.originGrid.x);
        const dy = Math.max(this.cache.originGrid.y, this.gridY - this.cache.originGrid.y);
        const dz = Math.max(this.cache.originGrid.z, this.gridZ - this.cache.originGrid.z);

        if (this.gradientType === 'radial' || this.gradientType === 'spherical') {
            this.cache.maxDistance = Math.sqrt(dx * dx + dy * dy + dz * dz);
        } else if (this.gradientType === 'cylindrical') {
            this.cache.maxDistance = Math.sqrt(dx * dx + dz * dz);
        }

        this.cache.enabled = true;
    }

    /**
     * Get color for voxel at grid position
     * @param {number} x - Grid X coordinate
     * @param {number} y - Grid Y coordinate
     * @param {number} z - Grid Z coordinate
     * @returns {{r: number, g: number, b: number}}
     */
    getColorForVoxel(x, y, z) {
        if (!this.enabled) {
            return null; // Use default coloring
        }

        // Calculate mapping value (0-1)
        let t = this.calculateMappingValue(x, y, z);

        // Apply invert
        if (this.invert) {
            t = 1 - t;
        }

        // Apply falloff curve
        t = this.applyFalloff(t);

        // Interpolate color from stops
        return this.interpolateColorStops(t);
    }

    /**
     * Calculate mapping value based on gradient type
     * @returns {number} - Value between 0 and 1
     */
    calculateMappingValue(x, y, z) {
        const { originGrid, maxDistance } = this.cache;

        switch (this.gradientType) {
            case 'linear-x':
                return x / this.gridX;

            case 'linear-y':
                return y / this.gridY;

            case 'linear-z':
                return z / this.gridZ;

            case 'radial':
            case 'spherical': {
                const dx = x - originGrid.x;
                const dy = y - originGrid.y;
                const dz = z - originGrid.z;
                const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
                return Math.min(1, distance / maxDistance);
            }

            case 'cylindrical': {
                const dx = x - originGrid.x;
                const dz = z - originGrid.z;
                const distance = Math.sqrt(dx * dx + dz * dz);
                return Math.min(1, distance / maxDistance);
            }

            default:
                return y / this.gridY; // fallback to linear-y
        }
    }

    /**
     * Apply falloff curve to mapping value
     */
    applyFalloff(t) {
        switch (this.falloff) {
            case 'linear':
                return t;

            case 'quadratic':
                return t * t;

            case 'cubic':
                return t * t * t;

            case 'smoothstep':
                return t * t * (3 - 2 * t);

            default:
                return t;
        }
    }

    /**
     * Interpolate color from color stops
     */
    interpolateColorStops(t) {
        // Clamp t to 0-1
        t = Math.max(0, Math.min(1, t));

        // Find surrounding color stops
        let lowerStop = this.colorStops[0];
        let upperStop = this.colorStops[this.colorStops.length - 1];

        for (let i = 0; i < this.colorStops.length - 1; i++) {
            if (t >= this.colorStops[i].position && t <= this.colorStops[i + 1].position) {
                lowerStop = this.colorStops[i];
                upperStop = this.colorStops[i + 1];
                break;
            }
        }

        // Calculate local t between stops
        const range = upperStop.position - lowerStop.position;
        const localT = range > 0 ? (t - lowerStop.position) / range : 0;

        // Interpolate RGB
        return {
            r: lowerStop.color.r + (upperStop.color.r - lowerStop.color.r) * localT,
            g: lowerStop.color.g + (upperStop.color.g - lowerStop.color.g) * localT,
            b: lowerStop.color.b + (upperStop.color.b - lowerStop.color.b) * localT
        };
    }

    /**
     * Export configuration to JSON
     */
    export() {
        return {
            enabled: this.enabled,
            gradientType: this.gradientType,
            colorStops: this.colorStops,
            origin: this.origin,
            falloff: this.falloff,
            invert: this.invert
        };
    }

    /**
     * Import configuration from JSON
     */
    import(data) {
        this.enabled = data.enabled || false;
        this.gradientType = data.gradientType || 'linear-y';
        this.colorStops = data.colorStops || this.colorStops;
        this.origin = data.origin || { x: 0.5, y: 0.5, z: 0.5 };
        this.falloff = data.falloff || 'linear';
        this.invert = data.invert || false;
        this.updateCache();
    }
}
