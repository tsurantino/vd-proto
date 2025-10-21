"""Scene types - Modular scene implementations"""

from .base import BaseScene
from .shape_morph import ShapeMorphScene
from .wave_field import WaveFieldScene
from .particle_flow import ParticleFlowScene
from .procedural import ProceduralScene
from .grid import GridScene
from .illusions import IllusionsScene

# Unified physics scene
from .physics import PhysicsScene

# Scene registry for factory pattern
SCENE_REGISTRY = {
    'shapeMorph': ShapeMorphScene,
    'waveField': WaveFieldScene,
    'particleFlow': ParticleFlowScene,
    'procedural': ProceduralScene,
    'grid': GridScene,
    'illusions': IllusionsScene,
    'physics': PhysicsScene,
}

__all__ = [
    'BaseScene',
    'ShapeMorphScene',
    'WaveFieldScene',
    'ParticleFlowScene',
    'ProceduralScene',
    'GridScene',
    'IllusionsScene',
    'PhysicsScene',
    'SCENE_REGISTRY',
]
