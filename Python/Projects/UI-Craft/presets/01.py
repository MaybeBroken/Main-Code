from direct.gui.DirectGui import *
from panda3d.core import (
    LVecBase3f,
    LPoint3f,
    LVecBase4f,
    LPoint4f,
)


class frame:
    def build(self):

        self.obj0 = DirectButton(
            parent=self.aspect2d,
            pos=LPoint3f(-0.8575747, 0, 0.84041666),
            scale=LVecBase3f(0.09, 0.09, 0.09),
            color=(0.5, 0.5, 0.5, 1),
            image=self.loader.loadTexture("01/textures/button1.png"),
        )


if __name__ == "__main__":
    from direct.showbase.ShowBase import ShowBase

    base = ShowBase()
    base.setBackgroundColor(0, 0, 0, 1)
    base.accept("q", exit)
    frame.build(base)
    base.run()
