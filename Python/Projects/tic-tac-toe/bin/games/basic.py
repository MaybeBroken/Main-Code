from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from direct.stdpy.threading import Thread
from direct.gui.DirectGuiBase import DirectGuiWidget
import os
from panda3d.core import AntialiasAttrib, TextNode, PointLight, AmbientLight


class Game:
    def __init__(self, root: ShowBase):
        self.root = root
        self.elements: set[DirectGuiWidget] = set()
        self.onExit = None
        self.x_model = self.root.loader.loadModel(
            "src/models/x.bam",
        )
        self.floor_model = self.root.loader.loadModel(
            "src/models/floor.glb",
        )

        self.SceneLight = PointLight("SceneLight")
        self.SceneLight.setColor((1, 1, 1, 1))
        self.SceneLight.setAttenuation((1, 0, 0))

        self.AmbientLight = AmbientLight("AmbientLight")
        self.AmbientLight.setColor((0.5, 0.5, 0.5, 1))

    def registerExitFunc(self, func):
        """
        Register a function to be called when the game is exited.
        """
        self.onExit = func

    def start(self):
        """
        setup and build the game, using the parent ShowBase instance.
        """
        self.floor_model.reparentTo(self.root.render)
        self.floor_model.setPos(0, 0, 0)

        self.root.camera.setPos(0, -4, 3)
        self.root.camera.lookAt(0, 0, 0)

        self.PointLightNode = self.root.render.attachNewNode(self.SceneLight)
        self.PointLightNode.setPos(0, 0, 5)
        self.root.render.setLight(self.PointLightNode)

        self.AmbientLightNode = self.root.render.attachNewNode(self.AmbientLight)
        self.root.render.setLight(self.AmbientLightNode)


if __name__ == "__main__":
    base = ShowBase()
    # base.setBackgroundColor(0, 0, 0, 1)
    base.disableMouse()
    base.render.set_antialias(AntialiasAttrib.MAuto)
    base.render.setShaderAuto()
    base.mfont = base.loader.loadFont(
        "src/fonts/AquireLight-YzE0o.otf", pixelsPerUnit=250
    )
    game = Game(base)
    game.start()
    base.run()
