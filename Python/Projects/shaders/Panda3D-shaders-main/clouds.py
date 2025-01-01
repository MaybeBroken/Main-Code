from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from panda3d.core import Shader

configVars = """
win-size 1920 1080
show-frame-rate-meter 0
"""

loadPrcFileData("", configVars)


class MyGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.set_background_color(0, 0, 0, 1)
        # self.wireframeOn()
        self.disable_mouse()
        self.accept("q", exit)
        self.cam.setPos(0, -2, 0)

        my_shader = Shader.load(Shader.SL_GLSL,
                                vertex="shaders/clouds-vert.glsl",
                                fragment="shaders/clouds-frag.glsl")

        self.plane = self.loader.loadModel("my-models/plane")
        self.plane.reparentTo(self.render)
        self.plane.setShader(my_shader)

        self.plane.set_shader_input("iResolution", (self.win.getXSize(), self.win.getYSize()))
        self.plane.set_shader_input("iMouse", (self.win.getXSize() / 2, self.win.getYSize() / 2))

        self.accept("aspectRatioChanged", self.win_resize)

        self.taskMgr.add(self.update, "update")

    def update(self, task):
        ft = globalClock.getFrameTime()
        self.plane.set_shader_input("iTime", ft)
        return task.cont

    def win_resize(self):
        self.plane.set_shader_input("iResolution", (self.win.getXSize(), self.win.getYSize()))
        self.plane.set_shader_input("iMouse", (self.win.getXSize() / 2, self.win.getYSize() / 2))


game = MyGame()
game.run()
