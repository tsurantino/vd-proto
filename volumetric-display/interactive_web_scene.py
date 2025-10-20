"""
Interactive Web-Controlled Scene - Wrapper for Modular Scene System
Receives parameters from web UI and renders in real-time
Compatible with sender.py and C++ simulator
"""

# Import the new modular scene system
from scenes.interactive_scene import InteractiveScene as ModularInteractiveScene


# Thin wrapper for backward compatibility with existing server
class InteractiveWebScene(ModularInteractiveScene):
    """
    Wrapper around the new modular InteractiveScene.
    Provides backward compatibility with existing server infrastructure.
    """
    pass


# For direct import compatibility
InteractiveScene = InteractiveWebScene
