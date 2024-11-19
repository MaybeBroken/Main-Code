from time import sleep, monotonic
import os
from direct.gui.DirectGui import *  # type: ignore
from direct.showbase.ShowBase import ShowBase
import yaml
from math import *
from random import *
import time as t
import sys
import os
from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper
from direct.stdpy.threading import Thread as Thread
from direct.gui.DirectGui import *
import src.scripts.UTILS as utils
from screeninfo import get_monitors

from panda3d.core import *
from panda3d.core import (
    TransparencyAttrib,
    Texture,
    DirectionalLight,
    AmbientLight,
    loadPrcFile,
    ConfigVariableString,
    AudioSound,
    WindowProperties,
    NodePath,
    TextNode,
    CullFaceAttrib,
    Spotlight,
    PerspectiveLens,
    SphereLight,
    PointLight,
    Point3,
    OccluderNode,
    CollisionTraverser,
    CollisionNode,
    CollisionBox,
    CollisionSphere,
    CollisionRay,
    CollisionHandlerQueue,
    Vec3,
    CollisionHandlerPusher,
)


startTime = monotonic()

monitor = get_monitors()
spriteSheet: dict = {"menuBackground": None}
wantIntro = False

loadPrcFile("src/settings.prc")
ConfigVariableString(
    "win-size", str(monitor[0].width) + " " + str(monitor[0].height)
).setValue(str(monitor[0].width) + " " + str(monitor[0].height))
ConfigVariableString("fullscreen", "true").setValue("true")
ConfigVariableString("notify-level", "fatal").setValue("fatal")
# ConfigVariableString("undecorated", "true").setValue("true")


def getTime() -> int:
    return int(monotonic()) - int(startTime)


def load(stream) -> list:
    returnVal = yaml.load(stream, yaml.CLoader)
    return returnVal


def dump(list):
    return yaml.dump(list, Dumper=yaml.CDumper)


class mainGame(ShowBase):
    def __init__(self):
        # absolute startup values here!
        # end of startup config
        ShowBase.__init__(self)
        self.setBackgroundColor(utils.COLORS_RGB._dict["black"])
        if wantIntro:
            self.intro()
        else:
            self.startup()

    def intro(self):
        movie = self.loader.loadTexture("src/movies/intro.mp4")
        image = OnscreenImage(movie, scale=1, parent=self.aspect2d)
        movie.play()
        movie.setLoopCount(1)
        startTime = t.monotonic()

        def finishLaunch(task):
            if t.monotonic() - startTime > 4:
                image.destroy()
                self.startup()
            else:
                return task.cont

        self.taskMgr.add(finishLaunch)

    def startup(self):
        self.backfaceCullingOn()
        self.disableMouse()
        self.setupInput()
        self.buildGui()
        self.taskMgr.add(self.update)

    def convertAspectRatio(self, value, orientation: str = ("x", "y")):
        if orientation == "x":
            return (monitor[0].width / monitor[0].height) * value
        if orientation == "y":
            return (monitor[0].height / monitor[0].width) * value

    def buildGui(self):
        self.guiFrame = DirectFrame(parent=self.aspect2d)

    def setupInput(self):
        self.accept("q", self.exit)
        self.updateTime = 0

    def exit(self):
        # self.savePrefsFile()
        exit("User Quit")

    def update(self, task):
        ...
        return task.cont


game = mainGame()
game.run()
