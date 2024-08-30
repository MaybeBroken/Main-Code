from time import sleep, monotonic
import Vars as Vars
import os
from direct.gui.DirectGui import *  # type: ignore
from direct.showbase.ShowBase import ShowBase

import encoder
import yaml
from math import *
from random import *
import time as t
import sys
import os
from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper
from direct.stdpy.threading import Thread as ThreadC
from direct.gui.DirectGui import *

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
)
from panda3d.core import (
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
)
from panda3d.core import (
    CollisionTraverser,
    CollisionNode,
    CollisionBox,
    CollisionSphere,
    CollisionRay,
    CollisionHandlerQueue,
    Vec3,
    CollisionHandlerPusher,
)


try:
    os.chdir(os.path.abspath("./Py/games/rpg"))
except:
    None

startTime = monotonic()

monitor = get_monitors()
spriteSheet: dict = {"menuBackground": None}


loadPrcFile("src/settings.prc")
if Vars.winMode == "full-win":
    ConfigVariableString(
        "win-size", str(monitor[0].width) + " " + str(monitor[0].height)
    ).setValue(str(monitor[0].width) + " " + str(monitor[0].height))
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "true").setValue("true")

if Vars.winMode == "full":
    ConfigVariableString(
        "win-size", str(Vars.resolution[0]) + " " + str(Vars.resolution[1])
    ).setValue(str(Vars.resolution[0]) + " " + str(Vars.resolution[1]))
    ConfigVariableString("fullscreen", "true").setValue("true")
    ConfigVariableString("undecorated", "true").setValue("true")

if Vars.winMode == "win":
    ConfigVariableString(
        "win-size",
        str(int(monitor[0].width / 2)) + " " + str(int(monitor[0].height / 2)),
    ).setValue(str(int(monitor[0].width / 2)) + " " + str(int(monitor[0].height / 2)))
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "false").setValue("false")


def getTime() -> int:
    return int(monotonic()) - int(startTime)


def decodeFile(stream) -> list:
    returnVal = yaml.load(stream, yaml.CLoader)
    return returnVal


def encodeFile(list):
    return yaml.dump(list, Dumper=yaml.CDumper)


class mainGame(ShowBase):
    def __init__(self):
        # absolute startup values here!
        # end of startup config
        ShowBase.__init__(self)
        self.setBackgroundColor(0, 0, 0, 1, self.win)
        self.startup()

    def startup(self):
        self.loadPrefsFile()
        self.buildGui()
        self.setupInput()

    def savePrefsFile(self):
        with open("story.txt", "wt") as storyTextStream:
            storyTextStream.writelines(encodeFile(Vars.gameVars))

    def loadPrefsFile(self):
        with open("story.txt", "rt") as storyTextStream:
            Vars.gameVars = decodeFile(storyTextStream)

    def buildGui(self):
        self.frameBackdrop = DirectFrame(
            frameColor=(0, 0, 0, 1),
            frameSize=(-1, 1, -1, 1),
            parent=self.render2d,
        )
        self.maybebrokenText = OnscreenText(
            "Developed by Maybebroken", pos=(-0.9, -0.95), scale=0.05, fg=(1, 1, 1, 1)
        )
        ThreadC(
            target=self.fadeInGuiElement_ThreadedOnly,
            args=[
                self.maybebrokenText,
                80,
                None,
                None,
                None,
            ],
            daemon=True,
        ).start()

    def setupInput(self):
        self.accept("q", self.exit)

    def exit(self):
        self.savePrefsFile()
        exit("\n\n:sys: User Quit\n\n")

    def fadeOutGuiElement_ThreadedOnly(
        self, element, timeToFade, execBeforeOrAfter, target, args=()
    ):
        if execBeforeOrAfter == "Before":
            target(*args)

        for i in range(timeToFade):
            val = 1 - (1 / timeToFade) * (i + 1)
            try:
                element.setAlphaScale(val)
            except:
                None
            sleep(0.01)
        element.hide()
        if execBeforeOrAfter == "After":
            target(*args)

    def fadeInGuiElement_ThreadedOnly(
        self, element, timeToFade, execBeforeOrAfter, target, args=()
    ):
        if execBeforeOrAfter == "Before":
            target(*args)

        element.show()
        for i in range(timeToFade):
            val = abs(0 - (1 / timeToFade) * (i + 1))
            element.setAlphaScale(val)
            sleep(0.01)
        if execBeforeOrAfter == "After":
            target(*args)


game = mainGame()
game.run()
