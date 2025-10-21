"""
Base Scene Interface

All scene types inherit from this class and implement generate_geometry()
"""

from abc import ABC, abstractmethod


class BaseScene(ABC):
    """
    Base class for all scene types.

    Each scene is responsible for:
    1. Defining its enabled parameters
    2. Providing default parameter values
    3. Generating geometry based on those parameters
    """

    def __init__(self, grid_shape, coords_cache):
        """
        Initialize base scene.

        Args:
            grid_shape: Tuple of (length, height, width)
            coords_cache: Cached coordinate arrays (z, y, x)
        """
        self.grid_shape = grid_shape
        self.coords_cache = coords_cache

    @abstractmethod
    def generate_geometry(self, raster, params, time, rotated_coords=None):
        """
        Generate geometry mask for this scene type.

        Args:
            raster: Raster object with grid dimensions
            params: SceneParameters object with all parameters
            time: Current animation time
            rotated_coords: Optional pre-rotated coordinates (z, y, x)

        Returns:
            Boolean mask array
        """
        pass

    @classmethod
    @abstractmethod
    def get_enabled_parameters(cls):
        """
        Get list of parameter names this scene uses.

        Returns:
            List of parameter name strings
        """
        pass

    @classmethod
    @abstractmethod
    def get_enabled_tabs(cls):
        """
        Get list of tab names this scene enables.

        Returns:
            List of tab name strings: 'scale', 'rotation', 'translation', 'scrolling', 'copy'
        """
        pass

    @classmethod
    @abstractmethod
    def get_defaults(cls):
        """
        Get default parameter values for this scene.

        Returns:
            Dictionary of parameter_name: default_value
        """
        pass

    @classmethod
    @abstractmethod
    def get_tooltips(cls):
        """
        Get tooltip descriptions for this scene's parameters.

        Returns:
            Dictionary of parameter_name: tooltip_string
        """
        pass

    def supports_copy(self):
        """
        Whether this scene supports copy system.

        Returns:
            Boolean
        """
        return 'objectCount' in self.get_enabled_parameters()

    def supports_rotation(self):
        """
        Whether this scene supports rotation.

        Returns:
            Boolean
        """
        return 'rotationX' in self.get_enabled_parameters()
