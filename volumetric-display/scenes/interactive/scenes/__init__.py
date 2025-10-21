"""Scene types - Modular scene implementations"""

from .base import BaseScene
from .shape_morph import ShapeMorphScene
from .wave_field import WaveFieldScene
from .particle_flow import ParticleFlowScene
from .procedural import ProceduralScene
from .grid import GridScene
from .illusions import IllusionsScene

# Scene registry for factory pattern
SCENE_REGISTRY = {
    'shapeMorph': ShapeMorphScene,
    'waveField': WaveFieldScene,
    'particleFlow': ParticleFlowScene,
    'procedural': ProceduralScene,
    'grid': GridScene,
    'illusions': IllusionsScene,
}

__all__ = [
    'BaseScene',
    'ShapeMorphScene',
    'WaveFieldScene',
    'ParticleFlowScene',
    'ProceduralScene',
    'GridScene',
    'IllusionsScene',
    'SCENE_REGISTRY',
]
