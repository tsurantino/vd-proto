# Hybrid Morph System Specification

## Overview

The Hybrid Morph system is a unified particle-based approach that seamlessly blends geometric shapes and particle flow behaviors. It provides smooth, harmonious transitions between solid shapes, dispersed particle clouds, and everything in between.

## Core Philosophy

Instead of treating "shapes" and "particles" as separate systems, the Hybrid Morph treats everything as particles that can be influenced by:
- **Shape attractors** (geometric equations that define ideal positions)
- **Flow forces** (directional motion, gravity, turbulence)
- **Coherence filters** (probability of particles being visible/active)

This creates a unified system where you can have "turbulent rain that loosely forms a rotating helix" or "a sphere that gradually dissolves into chaotic particles."

---

## Morphology Parameters

### 1. **formCoherence** (0.0 - 1.0)
**Controls the transition between particle cloud and solid shape**

- `0.0` = Pure particle cloud, no shape influence
- `0.3` = Particles vaguely suggest a shape
- `0.6` = Shape is recognizable but loose
- `1.0` = Solid, well-defined shape

**Technical implementation:**
- Acts as a probability filter during rendering
- Lower values = fewer particles drawn (stochastic culling)
- Also affects noise amplitude applied to particle positions

### 2. **particleDensity** (0.0 - 1.0)
**Controls how many particles populate the form**

- `0.0` = Minimal particles (~50-100)
- `0.5` = Moderate density (~300-500)
- `1.0` = Maximum density (~800-1000)

**Interaction with formCoherence:**
- Low coherence + high density = dense particle cloud
- High coherence + low density = sparse wireframe shape
- High coherence + high density = solid filled shape

### 3. **flowIntensity** (0.0 - 1.0)
**Controls strength of directional flow motion**

- `0.0` = Static/stationary particles
- `0.5` = Gentle drifting motion
- `1.0` = Strong directional flow

**Maps to velocity multiplier for flow behaviors**

### 4. **turbulence** (0.0 - 1.0)
**Controls amount of random/chaotic motion**

- `0.0` = Smooth, predictable motion
- `0.5` = Some random variation
- `1.0` = Highly erratic, swirling chaos

**Technical implementation:**
- Applies Perlin noise to particle velocities
- Higher values = higher noise amplitude and frequency

### 5. **attractorStrength** (0.0 - 1.0)
**Controls how strongly particles are pulled toward shape definition**

- `0.0` = Particles ignore shape, move freely
- `0.5` = Gentle pull toward shape surface
- `1.0` = Particles snap/lock to shape surface

**Interaction with formCoherence:**
- formCoherence controls *visibility* (which particles render)
- attractorStrength controls *position* (where particles are pulled)
- Low coherence + high attractor = invisible particles still pulled to shape
- High coherence + low attractor = visible particles floating freely

---

## Shape Definition Parameters

### 6. **baseShape** (enum)
Defines the geometric form that particles are attracted to:

- `sphere` - Perfect sphere
- `helix` - Spiral/helical structure
- `torus` - Donut shape
- `cube` - Box/cube wireframe or filled
- `pyramid` - Pyramid structure
- `plane` - Flat plane(s)

### 7. **shapeThickness** (0.1 - 1.0)
Defines the thickness of the shape surface:

- `0.1` = Thin shell/wireframe
- `0.5` = Moderate thickness
- `1.0` = Thick surface or filled volume

**For shapes:** Affects the distance threshold from the mathematical surface
**For particles:** Affects the scatter radius around attractor points

---

## Flow Behavior Parameters

### 8. **flowDirection** (enum)
Defines the type of motion behavior applied to particles:

- `none` - No flow, only shape attraction
- `fall` - Downward motion (rain-like)
- `rise` - Upward motion (fountain-like)
- `spiral` - Spiraling upward/outward motion
- `explode` - Outward radial expansion from center
- `implode` - Inward radial contraction toward center
- `drift` - Gentle random drifting (low-frequency noise)

### 9. **flowVelocity** (0.0 - 2.0)
Controls the speed of flow behavior:

- `0.0` = No motion
- `1.0` = Normal speed
- `2.0` = Double speed

**Multiplier applied to flow direction velocities**

---

## Global Movement Parameters

All existing movement parameters continue to work and apply to the entire particle system:

### Rotation
- `rotationX` (-1.0 to 1.0) - Rotation speed around X axis
- `rotationY` (-1.0 to 1.0) - Rotation speed around Y axis
- `rotationZ` (-1.0 to 1.0) - Rotation speed around Z axis

### Translation
- `translateX` (0.0 to 1.0) - X-axis oscillation speed
- `translateZ` (0.0 to 1.0) - Z-axis oscillation speed
- `translateAmplitude` (0.0 to 1.0) - Translation distance

### Bounce
- `bounceSpeed` (0.0 to 1.0) - Vertical bounce frequency
- `bounceHeight` (0.0 to 1.0) - Bounce amplitude

### Orbit
- `orbitSpeed` (0.0 to 1.0) - Circular orbit speed
- `orbitRadius` (0.0 to 1.0) - Orbit radius

### Pulse
- `pulseSpeed` (0.0 to 1.0) - Size pulsing frequency
- `pulseAmount` (0.0 to 1.0) - Size variation amount

### Advanced Movements
- `spiralSpeed`, `spiralRadius`, `spiralHeight` - Spiral motion
- `wobbleSpeed`, `wobbleAmount` - Tumbling/wobbling
- `figure8Speed`, `figure8Size` - Figure-8 motion
- `ellipseSpeed`, `ellipseRadiusX`, `ellipseRadiusZ` - Elliptical orbit
- `scrollSpeed`, `scrollDirection` - Continuous scrolling
- `objectArrangement`, `objectOffset` - Multi-object layout

### Object Count
- `objectCount` (1-4) - Number of instances to render

---

## Implementation Architecture

### Particle Structure

Each particle has:
```javascript
{
  position: {x, y, z},        // Current position
  velocity: {x, y, z},        // Current velocity
  attractorPoint: {x, y, z},  // Ideal position on shape surface
  noiseOffset: {x, y, z},     // Perlin noise offset for this particle
  age: float,                 // Particle lifetime (for animations)
  id: int                     // Unique particle ID (for deterministic noise)
}
```

### Update Loop (per frame)

```
1. Calculate global transformations (orbit, bounce, rotation, etc.)
2. For each particle:
   a. Update attractorPoint based on shape equation + global transforms
   b. Calculate flow force based on flowDirection and flowVelocity
   c. Calculate turbulence force using Perlin noise
   d. Calculate attraction force toward attractorPoint (scaled by attractorStrength)
   e. Combine forces: velocity = flow + turbulence + attraction
   f. Update position: position += velocity * deltaTime
   g. Apply coherence filter: isVisible = random() < formCoherence
   h. If visible, render particle at position
```

### Force Combination

Forces are additive with weights:

```javascript
const flowForce = calculateFlowForce(flowDirection, flowVelocity);
const turbulenceForce = calculateTurbulence(turbulence, noiseOffset, time);
const attractionForce = (attractorPoint - position) * attractorStrength * 0.1;

velocity = flowForce + turbulenceForce + attractionForce;
position += velocity;
```

### Coherence Filtering

Two approaches can be combined:

1. **Stochastic culling** (render-time):
   ```javascript
   const isVisible = Math.random() < formCoherence;
   if (isVisible) renderParticle(position);
   ```

2. **Noise-based displacement** (physics):
   ```javascript
   const noiseAmount = (1.0 - formCoherence) * 5.0;
   const noise = perlin3D(position + noiseOffset);
   position += noise * noiseAmount;
   ```

---

## Scene Type Implementations

### ShapeMorph Scenes

All existing shapes (sphere, helix, torus, cube, pyramid, plane) become **attractor definitions**:

```javascript
function getSphereAttractor(particleId, time, params) {
  const angle1 = (particleId * 2.4) % (Math.PI * 2);
  const angle2 = (particleId * 1.7) % Math.PI;
  const radius = params.size * 10;

  return {
    x: centerX + Math.cos(angle1) * Math.sin(angle2) * radius,
    y: centerY + Math.cos(angle2) * radius,
    z: centerZ + Math.sin(angle1) * Math.sin(angle2) * radius
  };
}
```

Each particle is assigned an attractor point on the shape surface using its ID for deterministic placement.

### ParticleFlow Scenes

Existing patterns become **flow force definitions**:

- `rain` → flowDirection: fall, high flowIntensity
- `stars` → flowDirection: fall (Z-axis), moderate flowIntensity
- `fountain` → flowDirection: rise, moderate flowIntensity, with gravity
- `spiral` → flowDirection: spiral, combined with helical attractor
- `explode` → flowDirection: explode, radial outward forces

### Vortex Scenes

Implemented as **helical attractor + rotational flow**:

```javascript
// Tornado: vertical helix with upward flow and radial turbulence
attractorStrength: 0.4
flowDirection: rise
turbulence: 0.6
baseShape: helix (stretched vertically)

// Whirlpool: horizontal spiral with downward center pull
attractorStrength: 0.5
flowDirection: fall (toward center)
turbulence: 0.4
baseShape: spiral (XZ plane)

// Galaxy: dual helical arms with orbital motion
objectCount: 2
attractorStrength: 0.3
flowDirection: spiral
turbulence: 0.5
```

### WaveField Scenes

Implemented as **dynamic plane attractor + wave displacement**:

```javascript
function getWaveAttractor(particleId, time, params) {
  const x = (particleId % gridX);
  const z = Math.floor(particleId / gridX);
  const dist = Math.sqrt((x - centerX)² + (z - centerZ)²);
  const wave = Math.sin(dist * frequency - time) * amplitude;

  return {
    x: x,
    y: centerY + wave,
    z: z
  };
}

// Parameters:
formCoherence: 0.7-0.9 (solid wave surface)
attractorStrength: 0.8 (particles follow wave closely)
turbulence: 0.1-0.3 (slight surface noise)
```

### Plasma Scenes

Implemented as **volumetric noise field threshold**:

```javascript
function getPlasmaVisibility(position, time, params) {
  let value = 0;
  value += Math.sin((position.x * scale + time) * complexity);
  value += Math.sin((position.y * scale + time * 0.8) * complexity);
  value += Math.sin((position.z * scale + time * 0.6) * complexity);
  value += Math.sin(Math.sqrt(position.x² + position.y²) * scale + time);

  const normalized = (value + 4) / 8;
  return normalized > threshold;
}

// Particles distributed in 3D grid
// Visibility determined by plasma function instead of coherence
formCoherence: replaced by plasma threshold
turbulence: 0.2-0.4 (shimmering effect)
flowDirection: drift (slow evolution)
```

---

## Parameter Interaction Examples

### Example 1: Solid Sphere → Particle Cloud

```javascript
// Start
formCoherence: 1.0
attractorStrength: 1.0
turbulence: 0.0
baseShape: sphere
flowDirection: none

// Transition over time
formCoherence: 1.0 → 0.2
attractorStrength: 1.0 → 0.1
turbulence: 0.0 → 0.7

// Result: Sphere gradually dissolves into chaotic particles
```

### Example 2: Falling Rain → Flowing Helix

```javascript
// Start
formCoherence: 0.1
attractorStrength: 0.0
turbulence: 0.2
baseShape: plane
flowDirection: fall
flowVelocity: 1.5

// Transition
formCoherence: 0.1 → 0.6
attractorStrength: 0.0 → 0.5
baseShape: plane → helix
flowDirection: fall → spiral

// Result: Rain particles gradually organize into spiraling helix
```

### Example 3: Dense Chaotic Cloud → Sparse Wireframe Torus

```javascript
// Start
formCoherence: 0.4
particleDensity: 0.9
attractorStrength: 0.2
turbulence: 0.6
baseShape: sphere

// Transition
formCoherence: 0.4 → 0.9
particleDensity: 0.9 → 0.3
attractorStrength: 0.2 → 0.9
turbulence: 0.6 → 0.1
baseShape: sphere → torus

// Result: Dense chaotic sphere transforms into clean torus outline
```

### Example 4: Turbulent Vortex with Loose Shape

```javascript
formCoherence: 0.5        // Medium visibility
particleDensity: 0.7       // Fairly dense
attractorStrength: 0.4     // Moderate pull to shape
turbulence: 0.7            // High chaos
baseShape: helix           // Spiral attractor
flowDirection: spiral      // Spiraling upward
flowVelocity: 1.2          // Fast motion
spiralSpeed: 0.6           // Add rotation
wobbleAmount: 0.3          // Add wobble

// Result: Dense swirling particle tornado that loosely follows helical path
```

---

## Performance Considerations

### Particle Count Management

- Base particle count determined by `particleDensity`
- `formCoherence` doesn't change particle count, only visibility
- Recommended max: 1000 particles for 60fps
- Consider particle pooling/recycling for flow effects

### Optimization Strategies

1. **Spatial hashing**: Group particles by grid cell for faster updates
2. **Level of detail**: Reduce particle count when shape is far from camera
3. **Coherence optimization**: Skip physics for invisible particles at low coherence
4. **Force caching**: Cache global transformation matrices per frame
5. **SIMD/GPU**: Consider GPU compute shaders for particle updates

### Memory Footprint

Per particle (assuming 32-bit floats):
- Position: 12 bytes
- Velocity: 12 bytes
- Attractor: 12 bytes
- Noise offset: 12 bytes
- Age: 4 bytes
- ID: 4 bytes
- **Total: 56 bytes per particle**

For 1000 particles: ~56KB (negligible)

---

## Integration with Existing System

### GlobalParameterMapper Updates

Add new mappings:

```javascript
// New hybrid-specific parameters
if (globalParams.formCoherence !== undefined) {
  mapped.formCoherence = globalParams.formCoherence;
}
if (globalParams.particleDensity !== undefined) {
  mapped.particleDensity = globalParams.particleDensity;
}
if (globalParams.flowIntensity !== undefined) {
  mapped.flowIntensity = globalParams.flowIntensity;
}
if (globalParams.turbulence !== undefined) {
  mapped.turbulence = globalParams.turbulence;
}
if (globalParams.attractorStrength !== undefined) {
  mapped.attractorStrength = globalParams.attractorStrength;
}
if (globalParams.flowDirection !== undefined) {
  mapped.flowDirection = globalParams.flowDirection;
}
if (globalParams.flowVelocity !== undefined) {
  mapped.flowVelocity = globalParams.flowVelocity;
}

// Backwards compatibility: map old parameters to hybrid equivalents
if (sceneType === 'shapeMorph') {
  mapped.formCoherence = 1.0; // Solid shapes
  mapped.attractorStrength = 1.0;
  mapped.turbulence = 0.0;
  mapped.flowDirection = 'none';
}
if (sceneType === 'particleFlow') {
  mapped.formCoherence = 0.2; // Loose particles
  mapped.attractorStrength = 0.0;
  mapped.turbulence = 0.3;
  // flowDirection mapped from pattern parameter
}
```

### Scene Library Integration

New scene type:

```javascript
'hybridMorph': {
  name: 'Hybrid Morph',
  defaultParams: {
    baseShape: 'sphere',
    formCoherence: 0.8,
    particleDensity: 0.6,
    attractorStrength: 0.7,
    turbulence: 0.2,
    flowDirection: 'none',
    flowVelocity: 1.0,
    shapeThickness: 0.5
  },
  fn: (voxels, time, params) => this.renderHybridMorph(voxels, time, params)
}
```

---

## Future Enhancements

### Advanced Features

1. **Particle lifecycle**: Birth/death animations, fade in/out
2. **Inter-particle forces**: Flocking, collision avoidance
3. **Multiple attractors**: Blend between multiple shapes
4. **Texture mapping**: Color/intensity based on position on shape
5. **Trails**: Motion blur/particle trails for flow visualization
6. **Force fields**: User-defined vector fields for custom flows
7. **Physics integration**: Gravity, wind, drag forces
8. **Particle types**: Different sizes/behaviors within same system

### Parameter Presets

Pre-configured combinations for common effects:

- **"Dissolve"**: High coherence → low coherence transition
- **"Crystallize"**: Low coherence → high coherence transition
- **"Swarm"**: High turbulence + low attractor + medium coherence
- **"Solid"**: Max coherence + max attractor + min turbulence
- **"Ghost"**: Medium coherence + low density + high turbulence
- **"Wireframe"**: High coherence + low density + max attractor

---

## Conclusion

The Hybrid Morph system provides a powerful, unified approach to volumetric rendering that seamlessly blends geometric precision with organic particle behaviors. By treating all visual elements as particles influenced by attractors and forces, it enables smooth transitions and rich combinations that would be impossible with separate shape/particle systems.

The parameter space is designed for intuitive, harmonious interactions where each parameter has a clear, predictable effect that composes well with others. This creates an expressive tool for real-time volumetric art and visualization.
