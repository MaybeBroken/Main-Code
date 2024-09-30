from math import *
from random import *
import time as t
import sys
import os
from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper

import src.scripts.server as server
import src.scripts.vars as Wvars
import src.scripts.display as disp
import src.scripts.fileManager as fMgr
import src.scripts.physics as physics
from screeninfo import get_monitors

from direct.showbase.ShowBase import ShowBase

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

import direct.stdpy.threading as thread
import direct.stdpy.file as panda_fMgr
from direct.gui.DirectGui import *
import direct.particles.Particles as part


# just a bit of setup going on, nothing much to see;)


monitor = get_monitors()
spriteSheet: dict = {"menuBackground": None}


loadPrcFile("src/settings.prc")
if Wvars.winMode == "full-win":
    ConfigVariableString(
        "win-size", str(monitor[0].width) + " " + str(monitor[0].height)
    ).setValue(str(monitor[0].width) + " " + str(monitor[0].height))
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "true").setValue("true")

if Wvars.winMode == "full":
    ConfigVariableString(
        "win-size", str(Wvars.resolution[0]) + " " + str(Wvars.resolution[1])
    ).setValue(str(Wvars.resolution[0]) + " " + str(Wvars.resolution[1]))
    ConfigVariableString("fullscreen", "true").setValue("true")
    ConfigVariableString("undecorated", "true").setValue("true")

if Wvars.winMode == "win":
    ConfigVariableString(
        "win-size",
        str(int(monitor[0].width / 2)) + " " + str(int(monitor[0].height / 2)),
    ).setValue(str(int(monitor[0].width / 2)) + " " + str(int(monitor[0].height / 2)))
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "false").setValue("false")


def degToRad(degrees):
    return degrees * (pi / 180.0)


# This class controls most of the flight director management


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.backfaceCullingOn()
        self.disableMouse()
        physics.physicsMgr.enable(physics.physicsMgr, gravity=(0, 0, 0))

        # do setup tasks
        # ...

        self.setupControls()
        self.loadInitialTextures()
        thread.Thread(
            target=server.startServer, daemon=True, args=[8765, Wvars.serverKeys]
        ).start()
        Wvars.cursorLock = False

        GUI.start(self=GUI, main=self)
        # end of setup tasks

        self.taskMgr.add(self.update, "update")

    def update(self, task):
        result = task.cont

        # do all systems updates

        dt = globalClock.getDt()  # type: ignore
        physics.physicsMgr.updateWorldPositions(physics.physicsMgr)

        # move cursor to stay within screen bounds
        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = md.getY()
        if Wvars.cursorLock == True:
            if int(monitor[0].width / 2) - mouseX >= int(monitor[0].width / 4):
                self.win.movePointer(0, x=int(monitor[0].width / 2), y=int(mouseY))
                self.lastMouseX = int(monitor[0].width / 2)
            elif int(monitor[0].width / 2) - mouseX <= -int(monitor[0].width / 4):
                self.win.movePointer(0, x=int(monitor[0].width / 2), y=int(mouseY))
                self.lastMouseX = int(monitor[0].width / 2)
            elif int(monitor[0].height / 2) - mouseY >= int(monitor[0].height / 4):
                self.win.movePointer(0, x=int(mouseX), y=int(monitor[0].height / 2))
                self.lastMouseY = int(monitor[0].height / 2)
            elif int(monitor[0].height / 2) - mouseY <= -int(monitor[0].height / 4):
                self.win.movePointer(0, x=int(mouseX), y=int(monitor[0].height / 2))
                self.lastMouseY = int(monitor[0].height / 2)

            else:
                # move camera based on mouse position
                mouseChangeX = mouseX - self.lastMouseX
                mouseChangeY = mouseY - self.lastMouseY

                self.cameraSwingFactor = Wvars.swingSpeed / 10

                currentH = self.camNodePath.getH()
                currentP = self.camNodePath.getP()
                currentR = self.camNodePath.getR()

                Wvars.camH = currentH
                Wvars.camP = currentP
                Wvars.camR = currentR

                self.camNodePath.setHpr(
                    currentH - mouseChangeX * dt * self.cameraSwingFactor,
                    currentP - mouseChangeY * dt * self.cameraSwingFactor,
                    0,
                )

                self.lastMouseX = mouseX
                self.lastMouseY = mouseY

        if Wvars.aiming == True:
            md = self.win.getPointer(0)
            self.lastMouseX = md.getX()
            self.lastMouseY = md.getY()

            self.crosshair.setPos(
                (2 / monitor[0].width) * md.getX() - 1,
                0,
                -((2 / monitor[0].height) * md.getY() - 1),
            )
        return result

    def setupControls(self):
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "primary": False,
            "secondary": False,
        }

        self.accept("escape", self.doNothing)
        self.accept("mouse1", self.doNothing)
        self.accept("mouse1-up", self.doNothing)
        self.accept("mouse3", self.doNothing)
        self.accept("q", sys.exit)
        self.accept("w", self.updateKeyMap, ["forward", True])
        self.accept("w-up", self.updateKeyMap, ["forward", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("s", self.updateKeyMap, ["backward", True])
        self.accept("s-up", self.updateKeyMap, ["backward", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("space", self.updateKeyMap, ["up", True])
        self.accept("space-up", self.updateKeyMap, ["up", False])
        self.accept("lshift", self.updateKeyMap, ["down", True])
        self.accept("lshift-up", self.updateKeyMap, ["down", False])
        self.accept("wheel_up", self.wireframeOn)
        self.accept("wheel_down", self.wireframeOff)

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def doNothing(self):
        return None

    def loadInitialTextures(self):
        global spriteSheet
        spriteSheet["menuBackground"] = self.loader.loadTexture(
            "src/textures/raw/menuBackground.png"
        )
        spriteSheet["startButton"] = self.loader.loadTexture(
            "src/textures/raw/startButton.png"
        )
        spriteSheet["startButton"]
        spriteSheet["exitButton"] = self.loader.loadTexture(
            "src/textures/raw/exitButton.png"
        )
        spriteSheet["voyagerLogo"] = self.loader.loadTexture(
            texturePath="src/textures/raw/Voyager_Logo.png",
        )
        spriteSheet["flightDirector"] = self.loader.loadTexture(
            texturePath="src/textures/raw/flightDirectorTile.png",
        )

    def loadAllTextures(self):
        spriteSheet["play_blue"] = self.loader.load_texture(
            "src/textures/raw/icon_play_blue.png"
        )
        spriteSheet["X_blue"] = self.loader.load_texture(
            "src/textures/raw/icon_X_blue.png"
        )

    def load(self):
        self.loadAllTextures()


# this class controls most of the things on the screen


class GUI(Main):
    def start(self, main):
        self.guiFrame = DirectFrame(parent=main.aspect2d)
        self.main = main
        GUI.setupIntroMenu(self=self)

    def setupIntroMenu(self):
        self.startupMenuFrame = DirectFrame(parent=self.guiFrame)
        self.startupMenuFrame.set_transparency(1)

        self.startupMenuBackgroundImage = OnscreenImage(
            parent=self.startupMenuFrame,
            image=spriteSheet["menuBackground"],
            scale=(1 * monitor[0].width / monitor[0].height, 1, 1),
        )

        self.startupMenuBackgroundImage2 = OnscreenImage(
            parent=self.startupMenuFrame,
            image=spriteSheet["voyagerLogo"],
            scale=0.25,
            pos=(0.825 * monitor[0].width / monitor[0].height, 0, -0.725),
        )

        self.startupMenuBackgroundImage3 = OnscreenImage(
            parent=self.startupMenuFrame,
            image=spriteSheet["flightDirector"],
            scale=(0.05 * (569 / 127), 1, 0.05),
            pos=(-0.86 * monitor[0].width / monitor[0].height, 0, 0.95),
        )

        startupMenuStartButton = DirectButton(
            parent=self.startupMenuFrame,
            pos=(-0.7 * monitor[0].width / monitor[0].height, 0, 0.6),
            scale=(0.12 * (553 / 194), 1, 0.12),
            relief=None,
            image=spriteSheet["startButton"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=thread.Thread(
                target=self.fadeOutGuiElement_ThreadedOnly,
                args=[
                    self,
                    self.startupMenuFrame,
                    25,
                    "Before",
                    self.setupLoaderFromMenu,
                    [self],
                ],
                daemon=True,
            ).start,
        )

        startupMenuQuitButton = DirectButton(
            parent=self.startupMenuFrame,
            pos=(-0.7 * monitor[0].width / monitor[0].height, 0, 0.3),
            scale=(0.12 * (553 / 194), 1, 0.12),
            relief=DGG.FLAT,
            image=spriteSheet["exitButton"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=sys.exit,
        )

        startupMenuCreditsText = OnscreenText(
            "Programmed by David Sponseller",
            pos=(-0.8 * monitor[0].width / monitor[0].height, -0.95),
            scale=0.04,
            parent=self.startupMenuFrame,
            fg=(0.5, 7, 7, 0.75),
        )

    def setupLoaderFromMenu(self):
        self.startupLoaderFrame = DirectFrame(
            parent=self.guiFrame,
        )
        self.startupLoaderFrame.set_transparency(1)

        self.setBackgroundColor(self=self, r=0, g=0, b=0, a=1, win=self.main.win)

        self.startupLoaderVoyagerLogo = OnscreenImage(
            parent=self.startupLoaderFrame,
            image=spriteSheet["voyagerLogo"],
            scale=0.5,
            pos=(0, 0, 0.25),
        )

        startupLoaderLoadingText = OnscreenText(
            "Loading...",
            pos=(0 * monitor[0].width / monitor[0].height, -0.5),
            scale=0.05,
            parent=self.startupLoaderFrame,
            fg=(0.6, 1, 1, 1),
        )
        thread.Thread(
            target=self.fadeInGuiElement_ThreadedOnly,
            args=[
                self,
                self.startupLoaderFrame,
                50,
                None,
                None,
                None,
            ],
            daemon=True,
        ).start()
        self.setupMainframe()


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
            t.sleep(0.01)
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
            t.sleep(0.01)
        if execBeforeOrAfter == "After":
            target(*args)

    def showGuiFrame(self):
        self.guiFrame.show()

    def hideGuiFrame(self):
        self.guiFrame.hide()
    

    def setupMainframe(self): ...


app = Main()
