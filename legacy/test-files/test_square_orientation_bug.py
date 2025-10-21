#!/usr/bin/env python3
"""
Test to demonstrate the square cube orientation bug.

With square cubes (20x20x20), the transformed data has the same shape,
but the axes have been reordered. This causes the data to be interpreted
incorrectly when sent to the ArtNet controllers.
"""
import numpy as np
from sender import apply_orientation_transform

def test_square_cube_orientation():
    """Demonstrate the bug with square cubes"""

    # Create a test world with a distinctive pattern
    world = np.zeros((40, 40, 40, 3), dtype=np.uint8)

    # Draw a RED vertical line at x=10, y=10, from z=0 to z=20
    world[0:20, 10, 10, 0] = 255  # Red channel

    print("="*70)
    print("Test: Square Cube Orientation Bug")
    print("="*70)
    print("\nOriginal world pattern:")
    print("  RED vertical line at (x=10, y=10, z=0-20)")
    print()

    # Test 1: No orientation (identity)
    cube_pos = (0, 0, 0)
    cube_dims = (20, 20, 20)
    orientation = ["X", "Y", "Z"]

    transformed = apply_orientation_transform(world, cube_pos, cube_dims, orientation)

    print("Test 1: Orientation ['X', 'Y', 'Z'] (identity)")
    print(f"  Transformed shape: {transformed.shape}")
    print(f"  Expected red line at x=10, y=10, z=0-20")
    print(f"  Red pixel count: {np.sum(transformed[:, :, :, 0] > 0)}")
    print(f"  First red pixel location (z, y, x): ", end="")
    red_pixels = np.argwhere(transformed[:, :, :, 0] > 0)
    if len(red_pixels) > 0:
        print(red_pixels[0])
    else:
        print("None found!")
    print()

    # Test 2: Swap Y and Z axes
    orientation = ["X", "Z", "Y"]
    transformed = apply_orientation_transform(world, cube_pos, cube_dims, orientation)

    print("Test 2: Orientation ['X', 'Z', 'Y'] (swap Y and Z)")
    print(f"  Transformed shape: {transformed.shape}")
    print(f"  Shape is SAME (20, 20, 20, 3) because cube is square!")
    print(f"  But data axes have been swapped")
    print(f"  Red pixel count: {np.sum(transformed[:, :, :, 0] > 0)}")
    print(f"  First red pixel location (z, y, x): ", end="")
    red_pixels = np.argwhere(transformed[:, :, :, 0] > 0)
    if len(red_pixels) > 0:
        print(red_pixels[0])
    else:
        print("None found!")
    print()

    # Test 3: Complex orientation like in hw_config_4.json
    orientation = ["-Y", "Z", "-X"]
    transformed = apply_orientation_transform(world, cube_pos, cube_dims, orientation)

    print("Test 3: Orientation ['-Y', 'Z', '-X'] (like in hw_config_4.json)")
    print(f"  Transformed shape: {transformed.shape}")
    print(f"  Shape is SAME (20, 20, 20, 3) because cube is square!")
    print(f"  Red pixel count: {np.sum(transformed[:, :, :, 0] > 0)}")
    print(f"  First red pixel location (z, y, x): ", end="")
    red_pixels = np.argwhere(transformed[:, :, :, 0] > 0)
    if len(red_pixels) > 0:
        print(red_pixels[0])
    else:
        print("None found!")
    print()

    print("="*70)
    print("CONCLUSION:")
    print("="*70)
    print("The shape stays (20, 20, 20, 3) for all orientations,")
    print("but the semantic meaning of each axis has changed!")
    print()
    print("When we pass this to send_dmx_bytes with:")
    print("  width=20, height=20, length=20")
    print()
    print("The Rust code doesn't know the axes were reordered,")
    print("so it treats the data as if it were in standard orientation.")
    print()
    print("This causes the visual output to be rotated/flipped incorrectly!")
    print("="*70)

if __name__ == "__main__":
    test_square_cube_orientation()
