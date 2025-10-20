"""Utility functions for handling dimension transformations with orientations"""


def get_transformed_dimensions_from_shape(transformed_shape):
    """
    Extract width, height, length from a transformed numpy array shape.

    Args:
        transformed_shape: Tuple from numpy array shape, e.g., (30, 20, 10, 3)
                          Format: (length, height, width, channels)

    Returns:
        Tuple of (width, height, length) suitable for send_dmx_bytes

    Example:
        transformed_data.shape = (30, 20, 10, 3)
        width, height, length = get_transformed_dimensions_from_shape(transformed_data.shape)
        # Returns: (10, 20, 30)
    """
    if len(transformed_shape) != 4:
        raise ValueError(f"Expected 4D array shape (L,H,W,C), got {transformed_shape}")

    # Numpy shape is (length, height, width, channels)
    length = transformed_shape[0]
    height = transformed_shape[1]
    width = transformed_shape[2]

    return (width, height, length)
