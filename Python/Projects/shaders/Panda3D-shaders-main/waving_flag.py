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
        self.cam.setPos(0, -8, 0)

        my_shader = Shader.load(Shader.SL_GLSL,
                                vertex="shaders/waving-vert.glsl",
                                fragment="shaders/waving-frag.glsl")

        self.plane = self.loader.loadModel("my-models/Ecuador-flag")
        self.plane.reparentTo(self.render)
        self.plane.setShader(my_shader)

        self.taskMgr.add(self.update, "update")

    def update(self, task):
        ft = globalClock.getFrameTime()
        self.plane.set_shader_input("time", ft)
        return task.cont


game = MyGame()
game.run()
