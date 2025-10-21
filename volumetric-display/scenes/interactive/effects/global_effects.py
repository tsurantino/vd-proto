"""
Global post-processing effects
Strobe, pulse, decay, and invert effects
"""

import numpy as np


class GlobalEffects:
    """
    Manages global post-processing effects applied to the entire scene.
    """

    @staticmethod
    def apply_strobe(raster, params, time):
        """
        Apply strobe effect (on/off flashing).

        Args:
            raster: Raster object to modify
            params: SceneParameters object with strobe setting
            time: Current animation time
        """
        if params.strobe == 'off':
            return

        freq = {'slow': 2, 'medium': 5, 'fast': 10}[params.strobe]
        if int(time * freq * 2) % 2 == 1:
            raster.data.fill(0)

    @staticmethod
    def apply_pulse(raster, params, time):
        """
        Apply pulse effect (breathing brightness).

        Args:
            raster: Raster object to modify
            params: SceneParameters object with pulse setting
            time: Current animation time
        """
        if params.pulse == 'off':
            return

        freq = {'slow': 0.5, 'medium': 1.0, 'fast': 2.0}[params.pulse]
        factor = 0.65 + 0.35 * np.sin(time * freq * np.pi * 2)
        raster.data[:] = (raster.data * factor).astype(np.uint8)

    @staticmethod
    def apply_decay(raster, previous_frame, params):
        """
        Apply decay/trail effect.

        Args:
            raster: Raster object to modify
            previous_frame: Previous frame data
            params: SceneParameters object with decay setting

        Returns:
            Boolean indicating if decay is active
        """
        if params.decay == 0:
            # No trail: start with a clean slate
            raster.data.fill(0)
            return False
        else:
            # Create fading trail by starting with decayed previous frame
            # Higher decay = longer trails (slower fade)
            # Decay range: 0 to 3, map to fade factor
            # decay=1.0 -> 58% retention, decay=2.0 -> 76%, decay=3.0 -> 94%
            fade_factor = 0.4 + (params.decay * 0.18)
            raster.data[:] = (previous_frame * fade_factor).astype(np.uint8)
            return True

    @staticmethod
    def apply_invert(raster, params):
        """
        Apply color inversion.

        Args:
            raster: Raster object to modify
            params: SceneParameters object with invert setting
        """
        if not params.invert:
            return

        max_val = np.max(raster.data)
        if max_val > 0:
            # Keep black pixels black, invert everything else
            mask = raster.data > 10
            raster.data[mask] = max_val - raster.data[mask]

    @staticmethod
    def apply_all(raster, previous_frame, params, time):
        """
        Apply all global effects in the correct order.

        Order:
        1. Decay (affects initial frame state)
        2. Strobe (global on/off)
        3. Pulse (global brightness modulation)
        4. Invert (final color transformation)

        Args:
            raster: Raster object to modify
            previous_frame: Previous frame data
            params: SceneParameters object
            time: Current animation time

        Returns:
            Boolean indicating if decay was applied
        """
        # Step 1: Apply decay (affects initial frame state)
        decay_active = GlobalEffects.apply_decay(raster, previous_frame, params)

        # Step 2: Apply strobe (global on/off)
        GlobalEffects.apply_strobe(raster, params, time)

        # Step 3: Apply pulse (global brightness modulation)
        GlobalEffects.apply_pulse(raster, params, time)

        # Step 4: Invert (final color transformation)
        GlobalEffects.apply_invert(raster, params)

        return decay_active
