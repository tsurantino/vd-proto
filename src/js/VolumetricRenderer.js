/**
 * Volumetric Renderer
 * Handles 3D projection and rendering of voxel grid
 */
export class VolumetricRenderer {
    constructor(canvas, gridX, gridY, gridZ) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;

        this.scale = 12;
        this.rotation = { x: -3, y: 7 }; // Looking at corner (0,0,0) from diagonal
        this.defaultRotation = { x: -3, y: 7 }; // Looking at corner (0,0,0) from diagonal
        this.showAxes = false;
        this.autoRotate = false;
        this.rotationRate = { x: 0, y: 0.01, z: 0 }; // Default: rotate around Y at 0.01 rad/frame

        // Color system
        this.colorMode = 'single'; // 'single' or 'gradient'
        this.singleColor = { r: 100, g: 200, b: 255 }; // Default blue
        this.gradientColors = [
            { r: 100, g: 200, b: 255 },
            { r: 100, g: 200, b: 255 }
        ];
        this.colorEffect = 'none'; // 'none', 'cycle', 'pulse', 'wave'
        this.colorEffectSpeed = 1.0;
        this.colorEffectTime = 0;

        this.setupCanvas();
        this.setupMouseControls();
    }

    setupCanvas() {
        this.canvas.width = 900;
        this.canvas.height = 700;
    }

    setupMouseControls() {
        let isDragging = false;
        let lastMouse = { x: 0, y: 0 };

        this.canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            lastMouse = { x: e.clientX, y: e.clientY };
        });

        this.canvas.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const dx = e.clientX - lastMouse.x;
                const dy = e.clientY - lastMouse.y;
                this.rotation.y += dx * 0.01;
                this.rotation.x += dy * 0.01;
                lastMouse = { x: e.clientX, y: e.clientY };
            }
        });

        this.canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });

        this.canvas.addEventListener('mouseleave', () => {
            isDragging = false;
        });
    }

    project3D(x, y, z) {
        // Center and scale
        const cx = (x - this.gridX / 2) * this.scale;
        const cy = (y - this.gridY / 2) * this.scale;
        const cz = (z - this.gridZ / 2) * this.scale;

        // Rotate around X axis
        const rx = cx;
        const ry = cy * Math.cos(this.rotation.x) - cz * Math.sin(this.rotation.x);
        const rz = cy * Math.sin(this.rotation.x) + cz * Math.cos(this.rotation.x);

        // Rotate around Y axis
        const rrx = rx * Math.cos(this.rotation.y) + rz * Math.sin(this.rotation.y);
        const rry = ry;
        const rrz = -rx * Math.sin(this.rotation.y) + rz * Math.cos(this.rotation.y);

        // Perspective projection
        const perspective = 800;
        const scale = perspective / (perspective + rrz);

        return {
            x: this.canvas.width / 2 + rrx * scale,
            y: this.canvas.height / 2 + rry * scale,
            z: rrz,
            scale: scale
        };
    }

    drawAxes() {
        // Fixed axis length and slight offset from corner
        const axisLength = 15; // Fixed length for all axes
        const offset = -2; // Slight offset from corner
        const corner = [offset, offset, offset];

        this.ctx.lineWidth = 2.5;

        // X axis - Red
        const xStart = this.project3D(corner[0], corner[1], corner[2]);
        const xEnd = this.project3D(corner[0] + axisLength, corner[1], corner[2]);
        this.ctx.strokeStyle = 'rgba(255, 100, 100, 0.9)';
        this.ctx.beginPath();
        this.ctx.moveTo(xStart.x, xStart.y);
        this.ctx.lineTo(xEnd.x, xEnd.y);
        this.ctx.stroke();
        this.ctx.fillStyle = 'rgba(255, 100, 100, 0.9)';
        this.ctx.font = 'bold 14px Courier New';
        this.ctx.fillText('X', xEnd.x + 8, xEnd.y + 5);

        // Y axis - Blue (height)
        const yStart = this.project3D(corner[0], corner[1], corner[2]);
        const yEnd = this.project3D(corner[0], corner[1] + axisLength, corner[2]);
        this.ctx.strokeStyle = 'rgba(100, 150, 255, 0.9)';
        this.ctx.beginPath();
        this.ctx.moveTo(yStart.x, yStart.y);
        this.ctx.lineTo(yEnd.x, yEnd.y);
        this.ctx.stroke();
        this.ctx.fillStyle = 'rgba(100, 150, 255, 0.9)';
        this.ctx.fillText('Y', yEnd.x + 8, yEnd.y + 5);

        // Z axis - Green (depth)
        const zStart = this.project3D(corner[0], corner[1], corner[2]);
        const zEnd = this.project3D(corner[0], corner[1], corner[2] + axisLength);
        this.ctx.strokeStyle = 'rgba(100, 255, 100, 0.9)';
        this.ctx.beginPath();
        this.ctx.moveTo(zStart.x, zStart.y);
        this.ctx.lineTo(zEnd.x, zEnd.y);
        this.ctx.stroke();
        this.ctx.fillStyle = 'rgba(100, 255, 100, 0.9)';
        this.ctx.fillText('Z', zEnd.x + 8, zEnd.y + 5);
    }

    drawGrid(gridOpacity) {
        this.ctx.strokeStyle = `rgba(0, 255, 255, ${gridOpacity})`;
        this.ctx.lineWidth = 0.5;

        // Draw cube edges
        const corners = [
            [0, 0, 0], [this.gridX, 0, 0], [this.gridX, this.gridY, 0], [0, this.gridY, 0],
            [0, 0, this.gridZ], [this.gridX, 0, this.gridZ], [this.gridX, this.gridY, this.gridZ], [0, this.gridY, this.gridZ]
        ];

        const edges = [
            [0,1],[1,2],[2,3],[3,0], // bottom
            [4,5],[5,6],[6,7],[7,4], // top
            [0,4],[1,5],[2,6],[3,7]  // sides
        ];

        edges.forEach(([a, b]) => {
            const pa = this.project3D(...corners[a]);
            const pb = this.project3D(...corners[b]);
            this.ctx.beginPath();
            this.ctx.moveTo(pa.x, pa.y);
            this.ctx.lineTo(pb.x, pb.y);
            this.ctx.stroke();
        });

        // Draw grid lines
        if (gridOpacity > 0.1) {
            this.ctx.strokeStyle = `rgba(0, 255, 255, ${gridOpacity * 0.3})`;
            const step = 10;

            for (let i = step; i < this.gridX; i += step) {
                const p1 = this.project3D(i, 0, 0);
                const p2 = this.project3D(i, this.gridY, 0);

                this.ctx.beginPath();
                this.ctx.moveTo(p1.x, p1.y);
                this.ctx.lineTo(p2.x, p2.y);
                this.ctx.stroke();
            }

            for (let j = step; j < this.gridY; j += step) {
                const p1 = this.project3D(0, j, 0);
                const p2 = this.project3D(this.gridX, j, 0);

                this.ctx.beginPath();
                this.ctx.moveTo(p1.x, p1.y);
                this.ctx.lineTo(p2.x, p2.y);
                this.ctx.stroke();
            }
        }
    }

    setRotationRate(x, y, z) {
        this.rotationRate.x = x;
        this.rotationRate.y = y;
        this.rotationRate.z = z;
    }

    toggleAutoRotate() {
        this.autoRotate = !this.autoRotate;
        return this.autoRotate;
    }

    resetView() {
        this.rotation.x = this.defaultRotation.x;
        this.rotation.y = this.defaultRotation.y;
    }

    toggleAxes() {
        this.showAxes = !this.showAxes;
        return this.showAxes;
    }

    setSingleColor(hexColor) {
        this.colorMode = 'single';
        const rgb = this.hexToRgb(hexColor);
        this.singleColor = rgb;
    }

    setGradientColors(hexColors) {
        this.colorMode = 'gradient';
        this.gradientColors = hexColors.map(hex => this.hexToRgb(hex));
    }

    setColorEffect(effect) {
        this.colorEffect = effect;
        this.colorEffectTime = 0;
    }

    setColorEffectSpeed(speed) {
        this.colorEffectSpeed = speed;
    }

    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : { r: 100, g: 200, b: 255 };
    }

    getColorForVoxel(x, y, z, val) {
        let color;

        if (this.colorMode === 'single') {
            color = { ...this.singleColor };
        } else {
            // Gradient based on height (y position)
            const t = y / this.gridY;
            const numColors = this.gradientColors.length;
            const scaledT = t * (numColors - 1);
            const index = Math.floor(scaledT);
            const localT = scaledT - index;

            const c1 = this.gradientColors[Math.min(index, numColors - 1)];
            const c2 = this.gradientColors[Math.min(index + 1, numColors - 1)];

            color = {
                r: c1.r + (c2.r - c1.r) * localT,
                g: c1.g + (c2.g - c1.g) * localT,
                b: c1.b + (c2.b - c1.b) * localT
            };
        }

        // Apply color effects
        if (this.colorEffect === 'cycle') {
            const hueShift = (this.colorEffectTime * 50) % 360;
            color = this.rotateHue(color, hueShift);
        } else if (this.colorEffect === 'pulse') {
            const pulse = (Math.sin(this.colorEffectTime * 2) + 1) / 2;
            const factor = 0.5 + pulse * 0.5;
            color = {
                r: color.r * factor,
                g: color.g * factor,
                b: color.b * factor
            };
        } else if (this.colorEffect === 'wave') {
            const wave = Math.sin(this.colorEffectTime * 2 + y * 0.5);
            const hueShift = wave * 60;
            color = this.rotateHue(color, hueShift);
        }

        return color;
    }

    rotateHue(rgb, degrees) {
        // Convert RGB to HSL
        const r = rgb.r / 255;
        const g = rgb.g / 255;
        const b = rgb.b / 255;

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

        // Rotate hue
        h = (h * 360 + degrees) % 360;
        if (h < 0) h += 360;
        h = h / 360;

        // Convert back to RGB
        const hue2rgb = (p, q, t) => {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1/6) return p + (q - p) * 6 * t;
            if (t < 1/2) return q;
            if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
        };

        let nr, ng, nb;
        if (s === 0) {
            nr = ng = nb = l;
        } else {
            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            nr = hue2rgb(p, q, h + 1/3);
            ng = hue2rgb(p, q, h);
            nb = hue2rgb(p, q, h - 1/3);
        }

        return {
            r: Math.round(nr * 255),
            g: Math.round(ng * 255),
            b: Math.round(nb * 255)
        };
    }

    applyAutoRotation() {
        if (this.autoRotate) {
            this.rotation.x += this.rotationRate.x;
            this.rotation.y += this.rotationRate.y;
            // Z rotation would require modifying the projection
        }
    }

    render(voxels, params) {
        // Apply auto rotation
        this.applyAutoRotation();

        // Update color effect time
        this.colorEffectTime += 0.016 * this.colorEffectSpeed;

        // Clear canvas
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        this.drawGrid(params.gridOpacity);

        // Draw axes if enabled
        if (this.showAxes) {
            this.drawAxes();
        }

        // Collect and sort voxels by depth
        const points = [];
        let activeLEDs = 0;

        for (let x = 0; x < this.gridX; x++) {
            for (let y = 0; y < this.gridY; y++) {
                for (let z = 0; z < this.gridZ; z++) {
                    const val = voxels[x + y * this.gridX + z * this.gridX * this.gridY];
                    if (val > 0) {
                        const p = this.project3D(x, y, z);
                        points.push({ ...p, val, gridX: x, gridY: y, gridZ: z });
                        activeLEDs++;
                    }
                }
            }
        }

        // Sort by depth (back to front)
        points.sort((a, b) => a.z - b.z);

        // Draw LEDs
        points.forEach(p => {
            const size = params.ledSize * p.scale;
            const alpha = params.brightness * p.val;

            // Get color for this voxel
            const color = this.getColorForVoxel(p.gridX, p.gridY, p.gridZ, p.val);

            // Glow effect
            const gradient = this.ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, size * 2);
            gradient.addColorStop(0, `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha})`);
            gradient.addColorStop(0.5, `rgba(${color.r * 0.7}, ${color.g * 0.7}, ${color.b * 0.7}, ${alpha * 0.6})`);
            gradient.addColorStop(1, `rgba(${color.r * 0.5}, ${color.g * 0.5}, ${color.b * 0.5}, 0)`);

            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, size * 2, 0, Math.PI * 2);
            this.ctx.fill();

            // Bright center
            const brightR = Math.min(255, color.r + 55);
            const brightG = Math.min(255, color.g + 30);
            const brightB = Math.min(255, color.b);
            this.ctx.fillStyle = `rgba(${brightR}, ${brightG}, ${brightB}, ${alpha})`;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, size * 0.6, 0, Math.PI * 2);
            this.ctx.fill();
        });

        return activeLEDs;
    }
}
