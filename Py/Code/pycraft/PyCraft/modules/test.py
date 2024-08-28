from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

class World(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        scene = self.loader.loadModel('../skybox/menu/skybox.egg')
        scene.reparentTo(self.render)
        scene.setZ(-2)
        scene.setScale(20)

        teapot = self.loader.loadModel('../src/models/dirt/dirt.egg')
        teapot.reparentTo(self.render)

        rig = NodePath('rig')
        buffer = self.win.makeCubeMap('env', 256, rig)
        rig.reparentTo(teapot)

        teapot.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldCubeMap)
        teapot.setTexture(buffer.getTexture())

w = World()
w.run()