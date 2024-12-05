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


if __name__ == "__main__":
    from direct.showbase.ShowBase import ShowBase

    base = ShowBase()
    base.setBackgroundColor(0, 0, 0, 1)
    base.accept("q", exit)
    frame.build(base)
    base.run()
