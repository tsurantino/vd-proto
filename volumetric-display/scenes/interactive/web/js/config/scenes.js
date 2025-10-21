// Scene parameter configuration - defines which parameters each scene uses and their defaults
export const sceneConfig = {
    shapeMorph: {
        enabled: ['size', 'density', 'scaling_amount', 'scaling_speed', 'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset', 'objectCount', 'copy_spacing', 'copy_scale_offset', 'copy_rotation_var', 'copy_translation_var', 'copy_translation_x', 'copy_translation_y', 'copy_translation_z', 'copy_translation_speed', 'copy_translation_offset', 'object_scroll_speed'],
        enabledTabs: ['scale', 'rotation', 'translation', 'scrolling', 'copy'],
        defaults: {
            size: 1.2,
            density: 0.6,
            scaling_amount: 1.5,
            scaling_speed: 2.0,
            rotationX: 0.0,
            rotationY: 0.0,
            rotationZ: 0.0,
            rotation_speed: 0.0,
            rotation_offset: 0.0,
            objectCount: 1,
            copy_spacing: 1.5,
            copy_arrangement: 'linear',
            copy_scale_offset: 0.0,
            copy_rotation_var: 0.0,
            copy_translation_var: 0.0,
            use_copy_rotation_override: false,
            copy_rotation_x: 0.0,
            copy_rotation_y: 0.0,
            copy_rotation_z: 0.0,
            copy_rotation_speed: 0.0,
            copy_rotation_offset: 0.0,
            copy_translation_x: 0.0,
            copy_translation_y: 0.0,
            copy_translation_z: 0.0,
            copy_translation_speed: 0.0,
            copy_translation_offset: 0.0,
            object_scroll_speed: 0.0,
            object_scroll_direction: 'y'
        },
        tooltips: {
            size: 'Controls shape size',
            density: 'Controls cube edge thickness',
            scaling_amount: 'Pulsing magnitude',
            scaling_speed: 'Pulsing frequency'
        }
    },
    waveField: {
        enabled: ['size', 'frequency', 'amplitude', 'scaling_amount', 'scaling_speed', 'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset', 'object_scroll_speed'],
        enabledTabs: ['scale', 'rotation', 'scrolling'],
        defaults: {
            size: 1.0,
            frequency: 2.0,
            amplitude: 0.6,
            scaling_amount: 1.0,
            scaling_speed: 2.0,
            rotationX: 0.0,
            rotationY: 0.0,
            rotationZ: 0.0,
            rotation_speed: 0.0,
            rotation_offset: 0.0,
            object_scroll_speed: 0.0,
            object_scroll_direction: 'y',
            objectCount: 1
        },
        tooltips: {
            frequency: 'Wave frequency',
            amplitude: 'Wave height',
            scaling_amount: 'Modulates amplitude',
            scaling_speed: 'Pulse frequency'
        }
    },
    particleFlow: {
        enabled: ['size', 'density', 'amplitude', 'objectCount', 'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset', 'copy_spacing', 'object_scroll_speed'],
        enabledTabs: ['rotation', 'scrolling', 'copy'],
        defaults: {
            size: 0.8,
            density: 0.4,
            amplitude: 0.5,
            objectCount: 3,
            rotationX: 0.0,
            rotationY: 0.0,
            rotationZ: 0.0,
            rotation_speed: 0.0,
            rotation_offset: 0.0,
            copy_spacing: 1.5,
            copy_arrangement: 'circular',
            object_scroll_speed: 0.0,
            object_scroll_direction: 'y'
        },
        tooltips: {
            size: 'Particle/helix radius',
            density: 'Particle count or spiral tightness',
            amplitude: 'Thickness or expansion speed',
            objectCount: 'Number of strands/arms or copies'
        }
    },
    procedural: {
        enabled: ['size', 'density', 'amplitude', 'scaling_amount', 'scaling_speed', 'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset', 'object_scroll_speed'],
        enabledTabs: ['scale', 'rotation', 'scrolling'],
        defaults: {
            size: 1.5,
            density: 0.5,
            amplitude: 0.5,
            scaling_amount: 1.0,
            scaling_speed: 1.0,
            rotationX: 0.0,
            rotationY: 0.0,
            rotationZ: 0.0,
            rotation_speed: 0.0,
            rotation_offset: 0.0,
            object_scroll_speed: 0.0,
            object_scroll_direction: 'y',
            objectCount: 1
        },
        tooltips: {
            size: 'Pattern scale/frequency',
            density: 'Coverage or iteration count',
            amplitude: 'Threshold or wall thickness'
        }
    },
    grid: {
        enabled: ['size', 'density', 'scaling_amount', 'scaling_speed', 'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset', 'objectCount', 'copy_spacing', 'object_scroll_speed'],
        enabledTabs: ['scale', 'rotation', 'scrolling', 'copy'],
        defaults: {
            size: 1.5,
            density: 0.3,
            scaling_amount: 1.0,
            scaling_speed: 1.0,
            rotationX: 0.0,
            rotationY: 0.0,
            rotationZ: 0.0,
            rotation_speed: 0.0,
            rotation_offset: 0.0,
            objectCount: 1,
            copy_spacing: 1.5,
            copy_arrangement: 'grid',
            object_scroll_speed: 0.0,
            object_scroll_direction: 'y'
        },
        tooltips: {
            size: 'Dot/box size',
            density: 'Spacing or line thickness'
        }
    },
    illusions: {
        enabled: ['size', 'density', 'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset', 'objectCount', 'copy_spacing'],
        enabledTabs: ['rotation', 'copy'],
        defaults: {
            size: 1.0,
            density: 0.0,
            rotationX: 0.0,
            rotationY: 0.0,
            rotationZ: 0.0,
            rotation_speed: 0.0,
            rotation_offset: 0.0,
            objectCount: 1,
            copy_spacing: 1.5,
            copy_arrangement: 'linear'
        },
        tooltips: {
            size: 'Frame count or object size',
            density: 'Frame/stripe spacing'
        }
    },
    // Unified Physics scene
    physics: {
        enabled: ['size', 'density', 'frequency', 'amplitude', 'particle_size_variation', 'restitution', 'air_resistance', 'spread_angle', 'enable_particle_collisions', 'motion_blur', 'turbulence', 'boundary_mode', 'scaling_amount', 'scaling_speed', 'rotationX', 'rotationY', 'rotationZ', 'rotation_speed', 'rotation_offset', 'copy_translation_x', 'copy_translation_y', 'copy_translation_z', 'copy_translation_speed', 'copy_translation_offset', 'object_scroll_speed'],
        enabledTabs: ['scaling', 'rotation', 'translation', 'scrolling', 'particles'],
        defaults: {
            size: 1.5,
            density: 0.3,
            frequency: 2.0,
            amplitude: 0.5,
            particle_size_variation: 0.0,
            restitution: 0.8,
            air_resistance: 0.05,
            spread_angle: 15.0,
            enable_particle_collisions: false,
            motion_blur: false,
            turbulence: 0.3,
            boundary_mode: 'despawn',
            scaling_amount: 1.0,
            scaling_speed: 0.0,
            rotationX: 0.0,
            rotationY: 0.0,
            rotationZ: 0.0,
            rotation_speed: 0.0,
            rotation_offset: 0.0,
            copy_translation_x: 0.0,
            copy_translation_y: 0.0,
            copy_translation_z: 0.0,
            copy_translation_speed: 0.0,
            copy_translation_offset: 0.0,
            object_scroll_speed: 0.0
        },
        tooltips: {
            size: 'Particle size (radius in voxels)',
            density: 'Emission rate (fountain/rain) or particle count (bouncing/orbital)',
            frequency: 'Velocity (fountain), attractor strength (orbital), wind speed (rain)',
            amplitude: 'Gravity strength (fountain/bouncing/rain) or num attractors (orbital)',
            restitution: 'Bounciness (0=no bounce, 1=perfect bounce)',
            air_resistance: 'Air drag (0=none, 1=heavy)',
            spread_angle: 'Fountain cone angle (degrees)',
            enable_particle_collisions: 'Ball-to-ball collisions (bouncing only, expensive)',
            motion_blur: 'Velocity-based particle trails',
            turbulence: 'Wind turbulence/gusts (rain only)'
        }
    }
};
