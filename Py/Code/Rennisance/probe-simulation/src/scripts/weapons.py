_colliders = []
_triggers = []
_internals = {"materials":{}, "objects":{}, "sceneGraphs":{}}
from panda3d.core import Material, NodePath
from math import sin, cos
class _firing:
    def addLaser(data):
        origin = data["origin"]
        target = data["target"]
        render3d = _internals["sceneGraphs"]["render3d"]
        distance = origin.getDistance(target)
        model = _internals["objects"]["cube"]
        modelNode = NodePath('laserNode')
        modelNode.instanceTo(origin)
        model.instanceTo(modelNode)
        modelNode.lookAt(target)
        model.setScale(0.25, distance, 0.25)
        model.set_y((distance*2) -5)

        laser = [None]
        _triggers.append(laser)


class lasers:
    _self = None

    def __init__(self, internalArgs:list=None):
        for type in internalArgs:
            for arg in type:
                _internals[type[0]][arg[0]] = arg[1]
        _self = self
        glowMat = Material()
        glowMat.setShininess(-5.0)
        glowMat.setAmbient((1, 0, 0, 1))
        glowMat.setEmission((5, 0, 0, 1))
        _internals["materials"]["glowMat"] = glowMat

    def fire(self: None = _self, origin=None, target=None):
        _firing.addLaser(data={"origin":origin, "target":target})
        target.setMaterial(_internals["materials"]["glowMat"])