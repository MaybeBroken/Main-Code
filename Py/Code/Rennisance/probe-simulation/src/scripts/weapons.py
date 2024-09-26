_internals = {"materials": {}, "objects": {}, "sceneGraphs": {}, "particles": {}}
from panda3d.core import Material, NodePath, Filename
from direct.stdpy.threading import Thread
from src.scripts.guiUtils import fade
from direct.particles.ParticleEffect import ParticleEffect


def destroyNode(node, particleId):
    _internals["particles"][particleId].disable()
    node.removeNode()


particleId = 0
print("loaded weapons config")


class _firing:
    def addLaser(data, particleId, destroy):
        origin = data["origin"]
        target = data["target"]
        distance = origin.getDistance(target)
        model = _internals["objects"]["cube"]
        modelNode = NodePath("laserNode")
        if origin.getScale() == (3, 3, 3):
            modelNode.setScale(0.3)
        modelNode.reparentTo(origin)
        model.reparentTo(modelNode)
        model.setScale(0.25, (distance) * 1.25, 0.25)
        model.set_y((distance * 2))
        modelNode.lookAt(target)
        model.lookAt(origin)
        model.setMaterial(_internals["materials"]["glowMat"])
        model.setTransparency(True)
        if destroy:
            fade.fadeOutNode(
                modelNode, 60, {"exec": destroyNode, "args": (modelNode, particleId)}
            )
        else:
            fade.fadeOutNode(modelNode, 60)


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

    def fire(
        self: None = _self, origin=None, target=None, normal=(0, 0, 0), destroy=True
    ):
        global particleId
        _firing.addLaser(
            data={"origin": origin, "target": target},
            particleId=particleId,
            destroy=destroy,
        )
        if destroy:
            particleEngine.loadParticleConfig(self, target, normal, particleId)
            particleId += 1
            target.setTransparency(True)
            fade.fadeOutNode(target, 200)


class particleEngine:
    def loadParticleConfig(self, object, normal, particleId):
        _internals["particles"][particleId] = ParticleEffect()
        try:
            _internals["particles"][particleId].loadConfig(
                Filename("src/particles/fireish.ptf")
            )
        except:
            None
        _internals["particles"][particleId].renderParent = object
        _internals["particles"][particleId].start(object)
        _internals["particles"][particleId].setPos(-normal)
