#!/usr/bin/env python3
"""Test what shape the transformed data actually has"""

import numpy as np
from sender import apply_orientation_transform

def test_transform_shape():
    """Test the actual shape of transformed data"""

    world = np.zeros((40, 40, 40, 3), dtype=np.uint8)

    cube_dims = (20, 20, 20)  # width, height, length

    print("="*60)
    print("TESTING TRANSFORMED DATA SHAPE")
    print("="*60)

    orientations = [
        ["X", "Y", "Z"],      # Identity
        ["-X", "Y", "Z"],     # Flip X
        ["Y", "X", "Z"],      # Swap X and Y
        ["Y", "-Z", "-X"],    # hw_config_4 cube orientation
        ["-Y", "Z", "-X"],    # hw_config_4 mapping orientation
    ]

    for orient in orientations:
        transformed = apply_orientation_transform(world, (0, 0, 0), cube_dims, orient)
        print(f"\nOrientation: {orient}")
        print(f"  Input cube_dims: (width={cube_dims[0]}, height={cube_dims[1]}, length={cube_dims[2]})")
        print(f"  Transformed shape: {transformed.shape}")
        print(f"  Numpy indexing: [length={transformed.shape[0]}, height={transformed.shape[1]}, width={transformed.shape[2]}, RGB={transformed.shape[3]}]")

    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    print("\nThe key question: After applying orientation transformation,")
    print("does the shape change or stay the same?")
    print("\nLooking at the results above, we can see if axis swaps change")
    print("the shape of the output array.")

if __name__ == "__main__":
    test_transform_shape()
