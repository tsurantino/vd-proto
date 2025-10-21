"""
Quick test script for physics engine.

Run this to verify the physics implementation works correctly.
Usage: python3 volumetric-display/scenes/interactive/physics/test_physics.py
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scenes.interactive.physics import (
    PhysicsEngine, PhysicsState, create_particle_pool,
    gravity, drag, boundary_collision,
    particles_to_voxels
)


def test_physics_engine():
    """Test basic physics engine functionality."""
    print("Testing Physics Engine...")

    # Create engine
    grid_shape = (16, 16, 16)
    bounds_min = np.array([0, 0, 0])
    bounds_max = np.array(grid_shape) - 1

    engine = PhysicsEngine(
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        dt=0.016,
        boundary_mode='bounce'
    )

    # Add forces
    engine.add_force(gravity(g=-9.8, axis=0))
    engine.add_force(drag(coefficient=0.1))

    # Add boundary collision
    engine.add_constraint(boundary_collision(
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        restitution=0.8
    ))

    # Create particle pool
    state = create_particle_pool(max_particles=10, grid_shape=grid_shape)

    # Activate a few particles
    state.position[:5] = np.array([
        [8, 8, 12],  # Center, high up
        [4, 4, 12],
        [12, 12, 12],
        [8, 4, 12],
        [4, 8, 12],
    ])
    state.velocity[:5] = np.array([
        [0, 0, -2],   # Falling
        [1, 0, -2],   # Falling with X velocity
        [-1, 0, -2],
        [0, 1, -2],
        [0, -1, -2],
    ])
    state.active[:5] = True

    print(f"Initial state: {np.sum(state.active)} active particles")
    print(f"Initial positions:\n{state.position[:5]}")

    # Run simulation for 100 steps
    for i in range(100):
        state = engine.step(state, t=i * 0.016)

        # Check if particles are in bounds
        in_bounds = np.all(
            (state.position >= bounds_min) & (state.position <= bounds_max),
            axis=1
        )
        if not np.all(in_bounds[state.active]):
            print(f"ERROR: Particles out of bounds at step {i}")
            return False

    print(f"After 100 steps:")
    print(f"Final positions:\n{state.position[:5]}")
    print(f"Final velocities:\n{state.velocity[:5]}")

    # Test rendering
    mask = particles_to_voxels(state, grid_shape, render_mode='sphere', motion_blur=False)
    print(f"Rendered {np.sum(mask)} voxels")

    print("✓ Physics engine test passed!")
    return True


def test_force_functions():
    """Test force functions."""
    print("\nTesting Force Functions...")

    # Create dummy state
    state = PhysicsState(
        position=np.array([[8, 8, 8]]),
        velocity=np.array([[1, 1, 1]]),
        acceleration=np.array([[0, 0, 0]]),
        mass=np.array([1.0]),
        radius=np.array([1.0]),
        active=np.array([True]),
        age=np.array([0.0]),
        prev_position=np.array([[8, 8, 8]])
    )

    # Test gravity
    grav_force = gravity(g=-9.8, axis=0)
    force = grav_force(state, 0.0)
    assert force.shape == (1, 3), "Gravity force shape mismatch"
    # F = m * g, and mass = 1.0 (note: axis 0 is Z in our coordinate system)
    expected = -9.8 * state.mass[0]
    actual = force[0, 0]
    print(f"  Gravity force: expected={expected}, actual={actual}, force={force[0]}")
    assert np.isclose(actual, expected), f"Gravity force magnitude incorrect: {actual} != {expected}"
    print("✓ Gravity force works")

    # Test drag
    drag_force = drag(coefficient=0.1)
    force = drag_force(state, 0.0)
    assert force.shape == (1, 3), "Drag force shape mismatch"
    assert np.allclose(force[0], [-0.1, -0.1, -0.1]), "Drag force incorrect"
    print("✓ Drag force works")

    print("✓ Force functions test passed!")
    return True


if __name__ == '__main__':
    try:
        success = test_force_functions() and test_physics_engine()
        if success:
            print("\n✅ All physics tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
