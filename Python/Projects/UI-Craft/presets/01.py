from direct.gui.DirectGui import *
from panda3d.core import (
    LVecBase3f,
    LPoint3f,
    LVecBase4f,
    LPoint4f,
)


class frame:
    def build(self):
        ...

        self.obj0 = DirectFrame(
            parent=self.aspect2d,
            pos=LPoint3f(0, 0, 0),
            scale=LVecBase3f(0.42196416, 0, 0.42196416),
            color=(1, 1, 1, 1),
            relief=None,
            geom=None,
            image=self.loader.loadTexture("01/textures/frame2.png"),
        )

        self.obj2 = DirectFrame(
            parent=self.aspect2d,
            pos=LPoint3f(-0.12, 0, 0.32),
            scale=LVecBase3f(0.84964305, 0, 0.57294654),
            color=(1, 1, 1, 1),
            relief=None,
            geom=None,
            image=self.loader.loadTexture("01/textures/frame2.png"),
        )

        self.obj4 = DirectButton(
            parent=self.aspect2d,
            pos=LPoint3f(-0.75, 0, 0.67),
            scale=LVecBase3f(0.119360074, 0, 0.119360074),
            color=(1, 1, 1, 1),
            relief=None,
            geom=None,
            image=self.loader.loadTexture("01/textures/button1.png"),
        )

        self.obj6 = DirectButton(
            parent=self.aspect2d,
            pos=LPoint3f(-0.36, 0, 0.67),
            scale=LVecBase3f(0.119360074, 0, 0.119360074),
            color=(1, 1, 1, 1),
            relief=None,
            geom=None,
            image=self.loader.loadTexture("01/textures/button1.png"),
        )

        self.obj8 = DirectButton(
            parent=self.aspect2d,
            pos=LPoint3f(0.08, 0, 0.67),
            scale=LVecBase3f(0.119360074, 0, 0.119360074),
            color=(1, 1, 1, 1),
            relief=None,
            geom=None,
            image=self.loader.loadTexture("01/textures/button1.png"),
        )

        self.obj10 = DirectButton(
            parent=self.aspect2d,
            pos=LPoint3f(-0.77, 0, 0.33),
            scale=LVecBase3f(0.119360074, 0, 0.119360074),
            color=(1, 1, 1, 1),
            relief=None,
            geom=None,
            image=self.loader.loadTexture("01/textures/button1.png"),
        )

        self.obj12 = DirectButton(
            parent=self.aspect2d,
            pos=LPoint3f(-0.35, 0, 0.33),
            scale=LVecBase3f(0.119360074, 0, 0.119360074),
            color=(1, 1, 1, 1),
            relief=None,
            geom=None,
            image=self.loader.loadTexture("01/textures/button1.png"),
        )

        self.obj14 = DirectButton(
            parent=self.aspect2d,
            pos=LPoint3f(0.09, 0, 0.33),
            scale=LVecBase3f(0.119360074, 0, 0.119360074),
            color=(1, 1, 1, 1),
            relief=None,
            geom=None,
            image=self.loader.loadTexture("01/textures/button1.png"),
        )


if __name__ == "__main__":
    from direct.showbase.ShowBase import ShowBase

    base = ShowBase()
    base.setBackgroundColor(0, 0, 0, 1)
    base.accept("q", exit)
    frame.build(base)
    base.run()
