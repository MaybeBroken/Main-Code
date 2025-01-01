from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from panda3d.core import Shader

configVars = """
win-size 1280 720
show-frame-rate-meter 1
"""

loadPrcFileData("", configVars)


class MyGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.set_background_color(0, 0, 0, 1)
        # self.wireframeOn()
        self.cam.setPos(0, -4, 0)

        my_shader = Shader.load(Shader.SL_GLSL,
                                vertex="shaders/texturing-vert.glsl",
                                fragment="shaders/texturing-frag.glsl")

        self.plane = self.loader.loadModel("my-models/Ecuador-flag")
        self.plane.reparentTo(self.render)
        self.plane.setShader(my_shader)


game = MyGame()
game.run()
