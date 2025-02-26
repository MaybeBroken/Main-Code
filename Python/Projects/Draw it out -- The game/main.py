from panda3d.core import *
from panda3d.core import (
    loadPrcFileData,
    AmbientLight,
    DirectionalLight,
    Texture,
    # Shader,
    Vec4,
    TransparencyAttrib,
    CardMaker,
    NodePath,
    GraphicsOutput,
    TextureStage,
    PerspectiveLens,
    MovieTexture,
)
from direct.showbase.ShowBase import ShowBase
from math import sin, cos, pi
from screeninfo import get_monitors
import os
import sys
from time import sleep
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *


def getDistance(pointA, pointB):
    return abs(pointA - pointB)


if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"
os.chdir(os.path.dirname(os.path.abspath(__file__)))

monitor = get_monitors()

loadPrcFileData(
    "",
    f"""want-pstats 0
win-size {monitor[0].width} {monitor[0].height}
fullscreen 0
undecorated 0
show-frame-rate-meter 1
frame-rate-meter-scale 0.035
frame-rate-meter-update-interval 0.1
clock-mode normal
sync-video 0
clock-frame-rate 0
window-title Master Project - 2025
""",
)


class Main(ShowBase):
    def __init__(self):
        super().__init__()
        self.setBackgroundColor(0, 0, 0, 1)
        x_resolution = 20
        y_resolution = 20
        self.posGrid = []
        self.buildGrid(x_resolution, y_resolution)
        self.lastShownNodes = []
        self.lastMousePos = ()
        self.taskMgr.add(self.getMousePosTask, "mouseTask")

    def buildGrid(self, x_resolution, y_resolution):
        self.gameGrid: dict[dict[OnscreenImage]] = {}
        xGrid = range(x_resolution)
        for x in xGrid:
            self.gameGrid[x] = {}

        yGrid = range(y_resolution)
        for x in self.gameGrid:
            for y in yGrid:
                self.gameGrid[x][y] = OnscreenImage(
                    parent=self.aspect2d,
                    image="textures/frame.png",
                    pos=(
                        2 * ((1 / ((x_resolution + 1) / (x + 1))) - 0.5),
                        1,
                        2 * ((1 / ((y_resolution + 1) / (y + 1))) - 0.5),
                    ),
                    scale=(
                        (1 / x_resolution) * 0.9,
                        0,
                        (1 / y_resolution) * 0.9,
                    ),
                )
                self.gameGrid[x][y].hide()
                self.posGrid.append(
                    [
                        round(((1 / ((x_resolution + 1) / (x + 1))) - 0.5), 2),
                        round(((1 / ((y_resolution + 1) / (y + 1))) - 0.5), 2),
                        x,
                        y,
                    ]
                )

    def getMousePosTask(self, task):
        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = -md.getY()
        mouseX = 1.5 * (round((1 / monitor[0].width) * mouseX, 2) - 0.5)
        mouseY = 1 * (round((1 / monitor[0].height) * mouseY, 2) + 0.5)
        if self.lastMousePos != (mouseX, mouseY):
            if len(self.lastShownNodes) != 0:
                for node in self.lastShownNodes:
                    node.hide()
                self.lastShownNodes = []
            for x, y, index_x, index_y in self.posGrid:
                if getDistance(x, mouseX) < 0.2 and getDistance(y, mouseY) < 0.2:
                    self.gameGrid[index_x][index_y].show()
                    self.lastShownNodes.append(self.gameGrid[index_x][index_y])
            self.lastMousePos = (mouseX, mouseY)

        return task.cont


Main = Main()
Main.run()
