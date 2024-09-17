_colliders = []
_triggers = []
_internals = {"materials": {}, "objects": {}, "sceneGraphs": {}, "particles": {}}
from panda3d.core import Material, NodePath, Filename
from direct.stdpy.threading import Thread
from src.scripts.guiUtils import fade
from direct.particles.ParticleEffect import ParticleEffect
from math import sin, cos


def destroyNode(node):
    node.destroy()


class _firing:
    def addLaser(data):
        origin = data["origin"]
        target = data["target"]
        render3d = _internals["sceneGraphs"]["render3d"]
        distance = origin.getDistance(target)
        model = _internals["objects"]["cube"]
        modelNode = NodePath("laserNode")
        modelNode.reparentTo(origin)
        model.reparentTo(modelNode)
        model.setScale(0.25, distance, 0.25)
        model.set_y((distance * 2) - 5)
        modelNode.lookAt(target)
        model.lookAt(origin)
        model.setMaterial(_internals["materials"]["glowMat"])
        model.setTransparency(True)
        Thread(
            target=fade.fadeOutGuiElement_ThreadedOnly,
            args=[modelNode, 25, "after", destroyNode, (modelNode)],
            daemon=True,
        ).start()


class lasers:
    _self = None

    def __init__(self, internalArgs: list = None):
        for type in internalArgs:
            for arg in type:
                _internals[type[0]][arg[0]] = arg[1]
        _self = self
        glowMat = Material()
        glowMat.setShininess(-5.0)
        glowMat.setAmbient((1, 0, 0, 1))
        glowMat.setEmission((5, 0, 0, 1))
        _internals["materials"]["glowMat"] = glowMat

    def fire(self: None = _self, origin=None, target=None, normal=None, destroy=True):
        _firing.addLaser(data={"origin": origin, "target": target})
        # target.setMaterial(_internals["materials"]["glowMat"])
        if destroy:
            particleEngine.loadParticleConfig(self, target, normal)
            target.setTransparency(True)
            Thread(
                target=fade.fadeOutGuiElement_ThreadedOnly,
                args=[target, 100, None, None, None],
                daemon=True,
            ).start()


class particleEngine:
    def loadParticleConfig(self, object, normal):
        _internals["particles"][object] = ParticleEffect()
        _internals["particles"][object].loadConfig(
            Filename("Py/Code/Rennisance/probe-simulation/src/particles/fireish.ptf")
        )
        _internals["particles"][object].start(object)
        _internals["particles"][object].setPos(-normal)
