// Parameter state management
export class ParamsManager {
    constructor() {
        this.params = {
            scene_type: 'shapeMorph',
            size: 1.0,
            density: 0.5,
            animationSpeed: 1.0,
            frequency: 1.0,
            amplitude: 0.5,
            objectCount: 1,
            scaling_amount: 2.0,
            scaling_speed: 2.0,
            rotationX: 0.0,
            rotationY: 0.0,
            rotationZ: 0.0,
            rotation_speed: 0.0,
            rotation_offset: 0.0,
            // Copy system
            copy_spacing: 1.5,
            copy_arrangement: 'linear',
            copy_scale_offset: 0.0,
            copy_rotation_var: 0.0,
            copy_translation_var: 0.0,
            copy_translation_x: 0.0,
            copy_translation_y: 0.0,
            copy_translation_z: 0.0,
            copy_translation_speed: 0.0,
            copy_translation_offset: 0.0,
            // Object scrolling system
            object_scroll_speed: 0.0,
            object_scroll_direction: 'y',
            // Color system
            color_type: 'single',
            color_single: '#FF0000',
            color_gradient: '#FF0000,#FF00FF,#0000FF',
            color_effect: 'none',
            color_effect_intensity: 1.0,
            color_mode: 'rainbow',
            color_speed: 1.0,
            // Global effects
            decay: 0.0,
            strobe: 'off',
            pulse: 'off',
            invert: false,
            // Mask scrolling (separate from object scrolling)
            scrolling_enabled: false,
            scrolling_direction: 'y',
            scrolling_speed: 1.0,
            scrolling_thickness: 0,
            scrolling_loop: false,
            scrolling_invert_mask: false,
            // Scene-specific params
            scene_params: {
                shape: 'sphere',
                waveType: 'ripple',
                pattern: 'particles',
                illusionType: 'infiniteCorridor',
                proceduralType: 'noise',
                gridPattern: 'full',
                physicsType: 'fountain',
                // Physics-specific params
                particle_size_variation: 0.0,
                restitution: 0.8,
                air_resistance: 0.05,
                spread_angle: 15.0,
                enable_particle_collisions: false,
                motion_blur: false,
                turbulence: 0.3,
                boundary_mode: 'despawn',
                energy_boost: 0.0,
                trail_length: 0.0
            }
        };
    }

    update(key, value) {
        if (this.params.hasOwnProperty(key)) {
            this.params[key] = value;
        } else {
            this.params.scene_params[key] = value;
        }
    }

    get(key) {
        return this.params[key] ?? this.params.scene_params[key];
    }
}
