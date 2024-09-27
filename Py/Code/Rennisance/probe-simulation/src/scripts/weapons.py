_internals = {"materials": {}, "objects": {}, "sceneGraphs": {}}
from panda3d.core import Material, NodePath, Filename
from direct.stdpy.threading import Thread
from src.scripts.guiUtils import fade
from direct.particles.ParticleEffect import ParticleEffect


def destroyNode(node, particleId):
    node.removeNode()


class _firing:
    def addLaser(data, destroy):
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
            # fade.fadeOutNode(
            #     modelNode, 60, {"exec": destroyNode, "args": (modelNode, particleId)}
            # )
            Thread(
                target=fade.fadeOutGuiElement_ThreadedOnly,
                args=(
                    modelNode,
                    20,
                    "after",
                    destroyNode,
                    (modelNode),
                ),
            ).start()
        else:
            # fade.fadeOutNode(modelNode, 60)
            Thread(
                target=fade.fadeOutGuiElement_ThreadedOnly,
                args=(
                    modelNode,
                    20,
                ),
            ).start()


class lasers:
    _self = None

    def __init__(self, internalArgs: list = None):
        for type in internalArgs:
            for arg in type:
                _internals[type[0]][arg[0]] = arg[1]
        _self = self
        glowMat = Material()
        glowMat.setAmbient((5, 0, 0, 1))
        glowMat.setEmission((10, 0, 0, 1))
        _internals["materials"]["glowMat"] = glowMat

    def fire(
        self: None = _self, origin=None, target=None, normal=(0, 0, 0), destroy=True
    ):
        _firing.addLaser(
            data={"origin": origin, "target": target},
            destroy=destroy,
        )
        if destroy:
            target.setTransparency(True)
            Thread(
                target=fade.fadeOutGuiElement_ThreadedOnly,
                args=(
                    target,
                    100,
                ),
            ).start()