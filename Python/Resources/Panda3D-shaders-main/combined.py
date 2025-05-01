from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from panda3d.core import Shader

configVars = """
win-size 1280 720
show-frame-rate-meter 1
gl-version 3 3
"""

loadPrcFileData("", configVars)


class MyGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.set_background_color(0, 0, 0, 1)
        # self.wireframeOn()
        self.disable_mouse()
        self.cam.setPos(0, -4, 0)

        my_shader = Shader.load(Shader.SL_GLSL,
                                vertex="shaders/combined-vert.glsl",
                                fragment="shaders/combined-frag.glsl")

        self.plane = self.loader.loadModel("my-models/plane")
        self.plane.reparentTo(self.render)
        self.plane.set_shader_input("resolution", (self.win.getXSize(), self.win.getYSize()))
        self.plane.setShader(my_shader)

        self.accept("aspectRatioChanged", self.win_resize)

    def win_resize(self):
        # print("resize")
        self.plane.set_shader_input("resolution", (self.win.getXSize(), self.win.getYSize()))


game = MyGame()
game.run()
