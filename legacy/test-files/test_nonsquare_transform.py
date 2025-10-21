#!/usr/bin/env python3
"""Test transformation with non-square dimensions to see if transpose is working"""

import numpy as np
from sender import apply_orientation_transform

def test_nonsquare_transform():
    """Test with non-square cube to see dimension changes"""

    # Create a non-square world
    world = np.zeros((60, 50, 40, 3), dtype=np.uint8)  # (length=60, height=50, width=40)

    print("="*70)
    print("TESTING NON-SQUARE TRANSFORMATIONS")
    print("="*70)
    print(f"\nWorld shape: {world.shape} (length=60, height=50, width=40, RGB)")

    # Test cube with non-square dimensions
    cube_dims = (10, 20, 30)  # width=10, height=20, length=30

    orientations = [
        (["X", "Y", "Z"], "Identity - no transformation"),
        (["Y", "X", "Z"], "Swap X and Y"),
        (["Y", "Z", "X"], "Rotate axes: X←Y, Y←Z, Z←X"),
        (["Z", "Y", "X"], "Swap X and Z"),
        (["Y", "-Z", "-X"], "hw_config_4 cube orientation"),
    ]

    for orient, desc in orientations:
        transformed = apply_orientation_transform(world, (0, 0, 0), cube_dims, orient)
        print(f"\n{desc}")
        print(f"  Orientation: {orient}")
        print(f"  cube_dims: (W={cube_dims[0]}, H={cube_dims[1]}, L={cube_dims[2]})")
        print(f"  Transformed: {transformed.shape} (L, H, W, RGB)")

        # What we EXPECT based on the orientation:
        # orientation = [cube_x_source, cube_y_source, cube_z_source]
        # If cube_x gets data from axis A, cube_y from B, cube_z from C
        # Then the output should have:
        #   - width dimension = size of source for cube_x
        #   - height dimension = size of source for cube_y
        #   - length dimension = size of source for cube_z

    print("\n" + "="*70)
    print("KEY INSIGHT:")
    print("="*70)
    print("If orientation [\"Y\", \"X\", \"Z\"] swaps X and Y, we expect:")
    print("  Input:  (W=10, H=20, L=30) → Numpy (L=30, H=20, W=10)")
    print("  Output after swap should be: (L=30, H=10, W=20)")
    print("  Because cube_x now comes from world_y (size 20)")
    print("  and cube_y now comes from world_x (size 10)")

if __name__ == "__main__":
    test_nonsquare_transform()
