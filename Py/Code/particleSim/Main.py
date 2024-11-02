from math import pi, sin, cos
from random import randint
import numpy as np
import time as t
import sys
import os
from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper
import src.scripts.vars as Wvars
from src.scripts.physics import physicsMgr
import src.scripts.display as disp
import src.scripts.fileManager as fMgr
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
from direct.gui.OnscreenImage import OnscreenImage
import direct.stdpy.threading as thread
import direct.stdpy.file as panda_fMgr
from direct.gui.DirectGui import *
import direct.particles.Particles as part

monitor = get_monitors()
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


class Main(ShowBase):
    def __init__(self):
        base = ShowBase.__init__(self)
        self.backfaceCullingOn()
        self.disableMouse()

        # do setup tasks
        # ...
        physicsMgr.enable(physicsMgr)
        self.setupControls()
        self.loadModels()
        self.buildWindow()

        # end of setup tasks

        self.taskMgr.add(self.update, "update")

    def update(self, task):
        result = task.cont
        playerMoveSpeed = Wvars.speed / 10

        x_movement = 0
        y_movement = 0
        z_movement = 0

        dt = globalClock.getDt()  # type: ignore
        if Wvars.gameType == "3D":
            if self.keyMap["forward"]:
                x_movement -= dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
                y_movement += dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
            if self.keyMap["backward"]:
                x_movement += dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
                y_movement -= dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
            if self.keyMap["left"]:
                x_movement -= dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
                y_movement -= dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
            if self.keyMap["right"]:
                x_movement += dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
                y_movement += dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
            if self.keyMap["up"]:
                z_movement += dt * playerMoveSpeed
            if self.keyMap["down"]:
                z_movement -= dt * playerMoveSpeed
            self.camera.setPos(
                self.camera.getX() + x_movement,
                self.camera.getY() + y_movement,
                self.camera.getZ() + z_movement,
            )
            Wvars.camX = self.camera.getX()
            Wvars.camY = self.camera.getY()
            Wvars.camZ = self.camera.getZ()

        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = md.getY()
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
            mouseChangeX = mouseX - self.lastMouseX
            mouseChangeY = mouseY - self.lastMouseY
            self.cameraSwingFactor = Wvars.swingSpeed / 10
            if Wvars.gameType == "3D":
                currentH = self.camera.getH()
                currentP = self.camera.getP()
                currentR = self.camera.getR()
                Wvars.camH = currentH
                Wvars.camP = currentP
                Wvars.camR = currentR
                self.camera.setHpr(
                    currentH - mouseChangeX * dt * self.cameraSwingFactor,
                    min(
                        90,
                        max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor),
                    ),
                    0,
                )
            elif Wvars.gameType == "2D":
                physicsMgr.addVectorForce(
                    physicsMgr,
                    "pointer",
                    [mouseChangeX / 50000, 0, -mouseChangeY / 50000],
                )
                for node in self.actors:
                    if self.pointer.getDistance(node[0]) < 20:
                        physicsMgr.addVectorForce(
                            physicsMgr,
                            str(node[1]),
                            [
                                mouseChangeX
                                / (self.pointer.getDistance(node[0]) * 5000),
                                0,
                                -mouseChangeY
                                / (self.pointer.getDistance(node[0]) * 5000),
                            ],
                        )

            self.lastMouseX = mouseX
            self.lastMouseY = mouseY
        # if Wvars.inInventory == True:
        #     md = self.win.getPointer(0)
        #     self.lastMouseX = md.getX()
        #     self.lastMouseY = md.getY()
        return result

    def setupControls(self):
        md = self.win.getPointer(0)
        self.lastMouseX = md.getX()
        self.lastMouseY = md.getY()
        properties = WindowProperties()
        properties.setCursorHidden(Wvars.hideCursor)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)
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

        self.accept("q", sys.exit)
        self.accept("mouse1", self.doNothing)
        self.accept("mouse1-up", self.doNothing)
        self.accept("mouse3", self.doNothing)
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

    def buildWindow(self):
        self.setBackgroundColor(0, 0, 0, 0, self.win)
        # self.background = DirectFrame(parent=self.render2d, frameSize=(-1, 1, -1, 1), frameColor = (0, 0, 0, 1))
        self.winFrame = DirectFrame(parent=self.render2d)

        self.actors = []
        for index1 in range(-9, 10):
            for index2 in range(-9, 10):
                self.actors.append(
                    {
                        "node":OnscreenGeom(
                            geom=self.pointerGeom,
                            scale=0.025,
                            pos=(index1 / 10, 0.01, index2 / 10),
                            parent=self.winFrame,
                            color=(1, 3 / (index2 + 10), 3 / (index1 + 10), 1),
                        ),
                        "name":f"{index1} {index2}"
                    }
                )
        for node in self.actors:
            physicsMgr.registerObject(
                physicsMgr,
                object=node[0],
                velocity=[0, 0, 0],
                name=str(node[1]),
                rotation=[0, 0, 0],
            )
        self.pointer = OnscreenGeom(
            geom=self.pointerGeom,
            scale=0.05,
            pos=(0, 0, 0),
            parent=self.winFrame,
            color=(1, 0, 0, 1),
        )
        physicsMgr.registerObject(
            physicsMgr,
            self.pointer,
            velocity=[0, 0, 0],
            name="pointer",
            rotation=[0, 0, 0],
        )
        physicsMgr.registerColliderPlane(
            physicsMgr,
            pos=-1,
            name="collider",
            orientation="+y",
            collisionAction="rebound",
        )
        physicsMgr.registerColliderPlane(
            physicsMgr,
            pos=-1,
            name="collider",
            orientation="+X",
            collisionAction="rebound",
        )
        physicsMgr.registerColliderPlane(
            physicsMgr,
            pos=1,
            name="collider",
            orientation="-y",
            collisionAction="rebound",
        )
        physicsMgr.registerColliderPlane(
            physicsMgr,
            pos=1,
            name="collider",
            orientation="-x",
            collisionAction="rebound",
        )

    def loadModels(self):
        self.pointerGeom = self.loader.loadModel("src/models/pointer/pointer.egg")


Main().run()
