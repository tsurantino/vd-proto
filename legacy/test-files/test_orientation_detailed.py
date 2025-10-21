#!/usr/bin/env python3
"""
Detailed test to understand the exact transformation being applied.
"""
import numpy as np
from sender import apply_orientation_transform

def test_specific_pixel_mapping():
    """Test where specific pixels end up after transformation"""

    # Create a simple test world - 40x40x40
    world = np.zeros((40, 40, 40, 3), dtype=np.uint8)

    # Mark specific corner pixels in RED
    # Bottom-left-front corner (0, 0, 0)
    world[0, 0, 0] = [255, 0, 0]  # RED at (x=0, y=0, z=0)

    # Top-right-back corner (19, 19, 19) in first cube
    world[19, 19, 19] = [0, 255, 0]  # GREEN at (x=19, y=19, z=19)

    # Mark a position in the middle-bottom
    world[0, 10, 10] = [0, 0, 255]  # BLUE at (x=10, y=10, z=0)

    print("="*70)
    print("Pixel Mapping Test")
    print("="*70)
    print("\nOriginal world markings:")
    print("  RED   at world (x=0,  y=0,  z=0)  - bottom-left-front corner")
    print("  GREEN at world (x=19, y=19, z=19) - top-right-back corner (of first cube)")
    print("  BLUE  at world (x=10, y=10, z=0)  - middle position, bottom layer")
    print()

    cube_pos = (0, 0, 0)
    cube_dims = (20, 20, 20)

    # Test 1: Identity orientation
    print("Test 1: Identity orientation ['X', 'Y', 'Z']")
    print("  Cube X ← World X, Cube Y ← World Y, Cube Z ← World Z")
    orientation = ["X", "Y", "Z"]
    transformed = apply_orientation_transform(world, cube_pos, cube_dims, orientation)

    # Find where each color ended up (in numpy [Z, Y, X] coordinates)
    red_loc = np.argwhere(transformed[:, :, :, 0] == 255)
    green_loc = np.argwhere(transformed[:, :, :, 1] == 255)
    blue_loc = np.argwhere(transformed[:, :, :, 2] == 255)

    if len(red_loc) > 0:
        z, y, x = red_loc[0]
        print(f"  RED found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
    if len(green_loc) > 0:
        z, y, x = green_loc[0]
        print(f"  GREEN found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
    if len(blue_loc) > 0:
        z, y, x = blue_loc[0]
        print(f"  BLUE found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
    print()

    # Test 2: Cube-level orientation from hw_config_4.json
    print("Test 2: Cube orientation ['Y', '-Z', '-X']")
    print("  Cube X ← World Y, Cube Y ← World -Z, Cube Z ← World -X")
    orientation = ["Y", "-Z", "-X"]
    transformed = apply_orientation_transform(world, cube_pos, cube_dims, orientation)

    red_loc = np.argwhere(transformed[:, :, :, 0] == 255)
    green_loc = np.argwhere(transformed[:, :, :, 1] == 255)
    blue_loc = np.argwhere(transformed[:, :, :, 2] == 255)

    if len(red_loc) > 0:
        z, y, x = red_loc[0]
        print(f"  RED found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
    if len(green_loc) > 0:
        z, y, x = green_loc[0]
        print(f"  GREEN found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
    if len(blue_loc) > 0:
        z, y, x = blue_loc[0]
        print(f"  BLUE found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
    print()

    # Test 3: Mapping-level orientation from hw_config_4.json
    print("Test 3: Mapping orientation ['-Y', 'Z', '-X']")
    print("  Cube X ← World -Y, Cube Y ← World Z, Cube Z ← World -X")
    orientation = ["-Y", "Z", "-X"]
    transformed = apply_orientation_transform(world, cube_pos, cube_dims, orientation)

    print(f"  Transformed shape: {transformed.shape}")

    red_loc = np.argwhere(transformed[:, :, :, 0] == 255)
    green_loc = np.argwhere(transformed[:, :, :, 1] == 255)
    blue_loc = np.argwhere(transformed[:, :, :, 2] == 255)

    if len(red_loc) > 0:
        z, y, x = red_loc[0]
        print(f"  RED found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
        print(f"    Expected: World (x=0, y=0, z=0) → Cube X=World(-Y)=-0=0, Y=World(Z)=0, Z=World(-X)=-0=0")
    if len(green_loc) > 0:
        z, y, x = green_loc[0]
        print(f"  GREEN found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
        print(f"    Expected: World (x=19, y=19, z=19) → Cube X=World(-Y)=-(19)→0, Y=World(Z)=19, Z=World(-X)=-(19)→0")
    if len(blue_loc) > 0:
        z, y, x = blue_loc[0]
        print(f"  BLUE found at numpy[z={z}, y={y}, x={x}] = cube(x={x}, y={y}, z={z})")
        print(f"    Expected: World (x=10, y=10, z=0) → Cube X=World(-Y)=-(10)→9, Y=World(Z)=0, Z=World(-X)=-(10)→9")
    print()

    print("="*70)

if __name__ == "__main__":
    test_specific_pixel_mapping()
