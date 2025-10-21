#!/usr/bin/env python3
"""Test orientation transformations to debug hw_config_4.json issues"""

import numpy as np
from sender import apply_orientation_transform

def create_test_world(width=40, height=40, length=40):
    """Create a test world with gradient patterns to visualize orientation"""
    world = np.zeros((length, height, width, 3), dtype=np.uint8)

    # X gradient (red): increases left to right
    for x in range(width):
        world[:, :, x, 0] = int(255 * x / width)

    # Y gradient (green): increases bottom to top
    for y in range(height):
        world[:, y, :, 1] = int(255 * y / height)

    # Z gradient (blue): increases front to back
    for z in range(length):
        world[z, :, :, 2] = int(255 * z / length)

    return world

def test_orientation(orientation, cube_pos=(0, 0, 0), cube_dims=(20, 20, 20)):
    """Test a specific orientation and print results"""
    print(f"\n{'='*60}")
    print(f"Testing orientation: {orientation}")
    print(f"Cube position: {cube_pos}")
    print(f"Cube dimensions: {cube_dims}")
    print(f"{'='*60}")

    world = create_test_world()

    # Apply transformation
    transformed = apply_orientation_transform(world, cube_pos, cube_dims, orientation)

    print(f"Transformed shape: {transformed.shape}")
    print(f"Expected shape: ({cube_dims[2]}, {cube_dims[1]}, {cube_dims[0]}, 3)")

    # Sample corners to see what happened
    print("\nCorner samples (showing color values):")
    print(f"  (0,0,0): RGB{tuple(transformed[0, 0, 0])}")
    print(f"  (0,0,W-1): RGB{tuple(transformed[0, 0, -1])}")
    print(f"  (0,H-1,0): RGB{tuple(transformed[0, -1, 0])}")
    print(f"  (L-1,0,0): RGB{tuple(transformed[-1, 0, 0])}")

    # Check the center point
    cz, cy, cx = transformed.shape[0]//2, transformed.shape[1]//2, transformed.shape[2]//2
    print(f"  Center ({cz},{cy},{cx}): RGB{tuple(transformed[cz, cy, cx])}")

    return transformed

def analyze_cube_orientation():
    """Analyze the orientations used in hw_config_4.json"""

    print("\n" + "="*60)
    print("ANALYZING hw_config_4.json ORIENTATIONS")
    print("="*60)

    # Test cube-level orientation
    print("\n1. Cube-level orientation (used by localhost mappings):")
    cube_orientation = ["Y", "-Z", "-X"]
    test_orientation(cube_orientation, (0, 0, 0), (20, 20, 20))

    # Test mapping-level orientation
    print("\n2. Mapping-level orientation (used by 2.0.99.x mappings):")
    mapping_orientation = ["-Y", "Z", "-X"]
    test_orientation(mapping_orientation, (0, 0, 0), (20, 20, 20))

    # Explain what each orientation means
    print("\n" + "="*60)
    print("ORIENTATION EXPLANATION")
    print("="*60)
    print("\nOrientation format: [cube_x_source, cube_y_source, cube_z_source]")
    print("Where each entry defines which world axis maps to that cube axis")
    print("\nCube orientation ['Y', '-Z', '-X'] means:")
    print("  - Cube X axis ← World Y axis")
    print("  - Cube Y axis ← World -Z axis (flipped)")
    print("  - Cube Z axis ← World -X axis (flipped)")
    print("\nMapping orientation ['-Y', 'Z', '-X'] means:")
    print("  - Cube X axis ← World -Y axis (flipped)")
    print("  - Cube Y axis ← World Z axis")
    print("  - Cube Z axis ← World -X axis (flipped)")

if __name__ == "__main__":
    analyze_cube_orientation()

    print("\n" + "="*60)
    print("TESTING SIMPLE ORIENTATIONS")
    print("="*60)

    # Test identity (no transformation)
    test_orientation(["X", "Y", "Z"], (0, 0, 0), (20, 20, 20))

    # Test simple flip
    test_orientation(["-X", "Y", "Z"], (0, 0, 0), (20, 20, 20))
