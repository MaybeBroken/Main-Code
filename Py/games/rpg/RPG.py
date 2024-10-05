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
        self.intro()
        # self.startup()

    def intro(self):
        self.setBackgroundColor(0, 0, 0, 1)
        movie = self.loader.loadTexture("src/movies/intro.mp4")
        image = OnscreenImage(movie, scale=1, parent=self.aspect2d)
        movie.play()
        movie.setLoopCount(1)
        startTime = t.monotonic()

        def finishLaunch(task):
            if t.monotonic() - startTime > 3.76:
                image.destroy()
                self.startup()
            else:
                return task.cont

        self.taskMgr.add(finishLaunch)

    def startup(self):
        self.backfaceCullingOn()
        self.disableMouse()
        self.savePrefsFile()
        self.buildGui()
        self.setupInput()

    def savePrefsFile(self):
        with open("story.txt", "wt") as storyTextStream:
            storyTextStream.writelines(encodeFile(Vars.gameVars))

    def loadPrefsFile(self):
        with open("story.txt", "rt") as storyTextStream:
            Vars.gameVars = decodeFile(storyTextStream)

    def convertAspectRatio(self, value, x_or_y):
        if x_or_y == "x":
            return (monitor[0].width / monitor[0].height) * value
        if x_or_y == "y":
            return (monitor[0].height / monitor[0].width) * value

    def buildGui(self):
        self.GUIFRAME = DirectFrame(parent=self.aspect2d)
        self.frameBackdrop = DirectFrame(
            frameColor=(0, 0, 0, 1),
            frameSize=(-1, 1, -1, 1),
            parent=self.render2d,
        )
        self.maybebrokenText = OnscreenText(
            "Chapter 1",
            pos=(self.convertAspectRatio(-0.85, "x"), 0.75),
            scale=0.08,
            fg=(1, 1, 1, 1),
            parent=self.GUIFRAME,
        )
        self.startButton = DirectButton(
            parent=self.GUIFRAME,
            pos=(self.convertAspectRatio(-0.875, "x"), 1, 0.45),
            scale=0.1,
            text="Start",
            command=ThreadC(
                target=self.fadeOutGuiElement_ThreadedOnly,
                args=[
                    self,
                    self.GUIFRAME,
                    25,
                    "After",
                    self.launch,
                    [self],
                ],
                daemon=True,
            ).start,
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
        )
        self.quitButton = DirectButton(
            parent=self.GUIFRAME,
            pos=(self.convertAspectRatio(-0.875, "x"), 1, 0.25),
            scale=0.1,
            text="Quit",
            command=self.exit,
            relief=DGG.FLAT,
            text_fg=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
        )
        ThreadC(
            target=self.fadeInGuiElement_ThreadedOnly,
            args=[
                self.GUIFRAME,
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

    def launch(self):
        None


game = mainGame()
game.run()
