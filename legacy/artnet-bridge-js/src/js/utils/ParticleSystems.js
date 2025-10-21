/**
 * Particle System Managers
 * Handles particle creation and updates for various effects
 */

export class RainParticleSystem {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;
        this.particles = [];
    }

    init(density) {
        this.particles = [];
        const count = Math.floor(200 * density);
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.gridX,
                y: Math.random() * this.gridY,
                z: Math.random() * this.gridZ,
                speed: 0.5 + Math.random() * 0.5
            });
        }
    }

    update(speed, scrollDirection = null, scrollSpeed = 0) {
        // If scrolling is enabled, particles don't move on their own
        // Movement is handled by the scroll transform
        if (scrollSpeed === 0 || !scrollDirection) {
            // Default behavior: rain falls along Y axis (downward)
            this.particles.forEach(p => {
                p.y -= p.speed * speed * 0.3;
                if (p.y < 0) {
                    p.y = this.gridY;
                    p.x = Math.random() * this.gridX;
                    p.z = Math.random() * this.gridZ;
                }
            });
        }
        // When scrolling is active, particles stay at their random positions
        // and the scroll transform creates the motion effect
    }

    getParticles() {
        return this.particles;
    }
}

export class StarfieldParticleSystem {
    constructor(gridX, gridY, gridZ) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.gridZ = gridZ;
        this.particles = [];
    }

    init(density) {
        this.particles = [];
        const count = Math.floor(300 * density);
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.gridX,
                y: Math.random() * this.gridY,
                z: Math.random() * this.gridZ,
                vz: 0.2 + Math.random() * 0.3
            });
        }
    }

    update(speed) {
        this.particles.forEach(p => {
            p.z -= p.vz * speed * 0.5;
            if (p.z < 0) {
                p.z = this.gridZ - 1;
                p.x = Math.random() * this.gridX;
                p.y = Math.random() * this.gridY;
            }
        });
    }

    getParticles() {
        return this.particles;
    }
}
