#!/usr/bin/env python3
"""Test if dimension mismatch is causing the shift issue"""

import numpy as np
from sender import apply_orientation_transform

def test_dimension_handling():
    """Test if the orientation transform preserves expected dimensions"""

    print("="*60)
    print("TESTING DIMENSION HANDLING WITH ORIENTATION")
    print("="*60)

    # Create a simple test world
    world = np.zeros((40, 40, 40, 3), dtype=np.uint8)

    # Create a distinctive pattern in a specific region
    # Mark world coordinates (0-19, 0-19, 0-19) with red
    world[0:20, 0:20, 0:20, 0] = 255  # Red in first cube region

    # Mark world coordinates (0-19, 20-39, 0-19) with green
    world[0:20, 20:40, 0:20, 1] = 255  # Green in third cube region

    cube_dims = (20, 20, 20)  # width, height, length

    print("\n1. Testing cube at (0, 0, 0) with orientation ['Y', '-Z', '-X']")
    orientation1 = ["Y", "-Z", "-X"]
    transformed1 = apply_orientation_transform(world, (0, 0, 0), cube_dims, orientation1)
    print(f"   Input world region: world[0:20, 0:20, 0:20] (Z, Y, X order)")
    print(f"   Transformed shape: {transformed1.shape}")
    print(f"   Expected: (20, 20, 20, 3)")
    print(f"   Non-zero pixels: {np.count_nonzero(transformed1)}")

    print("\n2. Testing cube at (0, 0, 0) with orientation ['-Y', 'Z', '-X']")
    orientation2 = ["-Y", "Z", "-X"]
    transformed2 = apply_orientation_transform(world, (0, 0, 0), cube_dims, orientation2)
    print(f"   Input world region: world[0:20, 0:20, 0:20] (Z, Y, X order)")
    print(f"   Transformed shape: {transformed2.shape}")
    print(f"   Expected: (20, 20, 20, 3)")
    print(f"   Non-zero pixels: {np.count_nonzero(transformed2)}")

    print("\n3. Testing cube at (0, 20, 0) with orientation ['Y', '-Z', '-X']")
    transformed3 = apply_orientation_transform(world, (0, 20, 0), cube_dims, orientation1)
    print(f"   Input world region: world[0:20, 20:40, 0:20] (Z, Y, X order)")
    print(f"   Transformed shape: {transformed3.shape}")
    print(f"   Expected: (20, 20, 20, 3)")
    print(f"   Non-zero pixels: {np.count_nonzero(transformed3)}")
    print(f"   Should be GREEN since world[0:20, 20:40, 0:20] is green")

    print("\n" + "="*60)
    print("KEY INSIGHT:")
    print("="*60)
    print("The orientation ['Y', '-Z', '-X'] means:")
    print("  - Cube's X axis gets data from World's Y axis")
    print("  - Cube's Y axis gets data from World's -Z axis")
    print("  - Cube's Z axis gets data from World's -X axis")
    print("")
    print("PROBLEM: When cube_dims = (width=20, height=20, length=20),")
    print("the transformation assumes these are CUBE dimensions.")
    print("But after orientation, the WORLD slice dimensions might differ!")
    print("")
    print("For orientation ['Y', '-Z', '-X']:")
    print("  - To get 20 pixels in cube X, we need 20 pixels from world Y")
    print("  - To get 20 pixels in cube Y, we need 20 pixels from world Z")
    print("  - To get 20 pixels in cube Z, we need 20 pixels from world X")
    print("")
    print("So the world slice should be: world[0:20, 0:20, 0:20]")
    print("Which extracts (length=20, height=20, width=20) from world")
    print("This matches cube_dims=(20,20,20) so it should work!")

def check_send_dmx_bytes_dimensions():
    """Check what dimensions are being passed to send_dmx_bytes"""
    print("\n" + "="*60)
    print("CHECKING send_dmx_bytes DIMENSION USAGE")
    print("="*60)
    print("\nIn interactive_scene_server.py, the code does:")
    print("  controller.send_dmx_bytes(")
    print("      width=cube_raster.width,")
    print("      height=cube_raster.height,")
    print("      length=cube_raster.length,")
    print("      ...)")
    print("")
    print("But it's sending transformed_data.tobytes()!")
    print("")
    print("PROBLEM FOUND:")
    print("The transformed data has shape that matches the orientation,")
    print("but we're still passing the ORIGINAL cube_raster dimensions!")
    print("")
    print("For orientation ['-Y', 'Z', '-X'], the axes are swapped:")
    print("  Original: (width, height, length) = (20, 20, 20)")
    print("  After ['Y', '-Z', '-X']: axes reordered, shape still (20,20,20,3)")
    print("  But the MEANING of each dimension changed!")
    print("")
    print("The send_dmx_bytes function needs to know the TRANSFORMED dimensions,")
    print("not the original cube raster dimensions!")

if __name__ == "__main__":
    test_dimension_handling()
    check_send_dmx_bytes_dimensions()
