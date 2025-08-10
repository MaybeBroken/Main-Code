from webbrowser import open_new
from panda3d.core import *
from panda3d.core import (
    TextNode,
)
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from typing import Callable


class Screen:
    def __init__(self, root: ShowBase):
        self.root = root
        self.elements = set()
        self.onExit: Callable[[], None] = None

    def registerExitFunc(self, func: Callable[[], None]):
        """
        Register a function to be called when the screen is exited.
        """
        self.onExit = func

    def build(self):
        """
        Build the UI screen.
        """
        self.win = DirectDialog(
            frameSize=(-2, 2, -1, 1),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=(0, 0, 0, 0.8),
        )
        self.elements.add(self.win)
        self.exitButton = DirectButton(
            text="Back",
            scale=0.1,
            pos=(-1, 0, 0.85),
            geom=None,
            relief=None,
            command=self.exitScreen,
            parent=self.win,
            text_fg=(1, 1, 1, 1),
            text_font=self.root.mfont,
            text_align=TextNode.ACenter,
        )
        self.elements.add(self.exitButton)
        self.rootTitle = OnscreenText(
            style=2,
            text="Credits",
            pos=(0, 0.7),
            scale=0.18,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=self.win,
            font=self.root.mfont,
        )
        self.elements.add(self.rootTitle)
        self.name = OnscreenText(
            text="Programmed by David Sponseller\nAlso known as MaybeBroken",
            pos=(0, 0.45),
            scale=0.1,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=self.win,
            font=self.root.mfont,
        )
        self.elements.add(self.name)
        self.panda3dCredits = OnscreenText(
            text="2D and 3D graphics provided by Panda3D",
            pos=(0, 0.2),
            scale=0.1,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=self.win,
            font=self.root.mfont,
        )
        self.elements.add(self.panda3dCredits)
        self.panda3dLink = DirectButton(
            text="More about Panda3D here",
            scale=0.05,
            pos=(0, 0, 0.125),
            command=lambda: open_new("https://www.panda3d.org/"),
            parent=self.win,
            text_font=self.root.mfont,
        )
        self.elements.add(self.panda3dLink)

    def exitScreen(self):
        """
        Exit the screen and call the registered exit function if it exists.
        """
        for element in self.elements:
            if hasattr(element, "destroy"):
                element.destroy()
            else:
                element.removeNode()
        self.elements.clear()
        if self.onExit:
            self.onExit()


if __name__ == "__main__":
    from direct.showbase.ShowBase import ShowBase

    base = ShowBase()
    base.setBackgroundColor(0, 0, 0, 1)
    base.mfont = base.loader.loadFont(
        "../../src/fonts/AquireLight-YzE0o.otf", pixelsPerUnit=250
    )
    base.accept("q", base.userExit)
    screen = Screen(base)
    screen.registerExitFunc(base.userExit)
    screen.build()
    base.run()
