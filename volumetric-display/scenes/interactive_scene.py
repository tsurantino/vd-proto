"""
Interactive Scene - Web-Controllable Volumetric Scene

This is a wrapper for easy importing. The actual implementation
is in the scenes/interactive/ module.

Usage:
    python sender.py --scene scenes/interactive_scene.py --web-server --web-port 5001
"""

from scenes.interactive import InteractiveScene

# For backward compatibility
__all__ = ['InteractiveScene']
