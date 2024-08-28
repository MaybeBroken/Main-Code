from math import pi, sin, cos, sqrt
from random import randint
import time as t
import sys
import os
from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper
import src.scripts.vars as Wvars
import src.scripts.display as disp
import src.scripts.fileManager as fMgr
from screeninfo import get_monitors
from direct.showbase.ShowBase import ShowBase
from direct.distributed import *
from panda3d.core import *
from panda3d.core import (
    TransparencyAttrib,
    Texture,
    DirectionalLight,
    AmbientLight,
    loadPrcFile,
    ConfigVariableString,
    AudioSound,
    AntialiasAttrib,
    GeomVertexReader,
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
    OrthographicLens,
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
from direct.motiontrail.MotionTrail import MotionTrail

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
        ShowBase.__init__(self)
        self.backfaceCullingOn()
        self.disableMouse()

        # do setup tasks
        # ...

        self.setupControls()
        disp.GUI.start(self=disp.GUI, render=self.render2d, main=self, TransparencyAttrib=TransparencyAttrib)
        self.loadModels()
        self.setupLights()
        self.setupCamera()
        self.setupSkybox()
        self.setupScene()

        # end of setup tasks
        self.update_time = 0
        self.taskMgr.add(self.update, "update")

    def update(self, task):
        result = task.cont
        playerMoveSpeed = Wvars.speed / 100
        drag = 0.001

        # update velocities
        if self.update_time > 4:
            self.update_time = 0
            self.vel_text = (
                "Thrust: "
                + str(
                    round(
                        number=(
                            ((round(abs(self.x_movement) * 1000)) ^ 2)
                            + ((round(abs(self.y_movement) * 1000)) ^ 2)
                            + ((round(abs(self.z_movement) * 1000)) ^ 2) / 1000
                        )
                        - 4,
                        ndigits=2,
                    )
                )
                + " km/s"
            )
            self.velocityMeter.configure(text=self.vel_text)
        else:
            self.update_time += 1

        # do system updates
        dt = globalClock.getDt()  # type: ignore
        self.camera.setHpr(0, 0, 0)
        self.camera.setPos(0, -50, 40)
        self.camera.lookAt(self.ship)
        self.skybox.setPos(self.camNodePath.getPos())
        self.skybox2.setPos(self.camNodePath.getPos())
        # self.trail.geom_node_path.setPos(self.ship.getPos())

        # calculate thrust
        if Wvars.movementEnabled ==True:
            if self.keyMap["left"]:
                self.ship.setH(self.ship.getH() + Wvars.turnspeed / 100)
            if self.keyMap["right"]:
                self.ship.setH(self.ship.getH() - Wvars.turnspeed / 100)
            if self.keyMap["up"]:
                self.ship.setP(self.ship.getP() + Wvars.turnspeed / 100)
            if self.keyMap["down"]:
                self.ship.setP(self.ship.getP() - Wvars.turnspeed / 100)
            if self.keyMap["forward"]:
                self.x_movement -= dt * playerMoveSpeed * sin(degToRad(self.ship.getH()))
                self.y_movement += dt * playerMoveSpeed * cos(degToRad(self.ship.getH()))
                self.z_movement += (
                    dt * playerMoveSpeed * cos(degToRad(self.ship.getP() - 90))
                )
            if self.keyMap["backward"]:
                self.x_movement += dt * playerMoveSpeed * sin(degToRad(self.ship.getH()))
                self.y_movement -= dt * playerMoveSpeed * cos(degToRad(self.ship.getH()))
                self.z_movement -= (
                    dt * playerMoveSpeed * cos(degToRad(self.ship.getP() - 90))
                )

        # calculate momentum/drag
        if self.keyMap["forward"] == False and self.keyMap["backward"] == False or Wvars.movementEnabled == False:
            if self.x_movement > 0:
                self.x_movement -= drag
            if self.x_movement < 0:
                self.x_movement += drag
            if self.y_movement > 0:
                self.y_movement -= drag
            if self.y_movement < 0:
                self.y_movement += drag
            if self.z_movement > 0:
                self.z_movement -= drag
            if self.z_movement < 0:
                self.z_movement += drag
            zero_factor = 0.05
            if self.x_movement < zero_factor and self.x_movement > -zero_factor:
                self.x_movement = 0
            if self.y_movement < zero_factor and self.y_movement > -zero_factor:
                self.y_movement = 0
            if self.z_movement < zero_factor and self.z_movement > -zero_factor:
                self.z_movement = 0
        if self.x_movement > 2:
            self.x_movement -= drag
        if self.x_movement < -2:
            self.x_movement += drag
        if self.y_movement > 2:
            self.y_movement -= drag
        if self.y_movement < -2:
            self.y_movement += drag
        if self.z_movement > 2:
            self.z_movement -= drag
        if self.z_movement < -2:
            self.z_movement += drag

        # apply movement changes

        self.ship.setPos(
            self.ship.getX() + self.x_movement,
            self.ship.getY() + self.y_movement,
            self.ship.getZ() + self.z_movement,
        )
        self.camNodePath.setPos(self.ship.getPos())
        Wvars.camX = self.camNodePath.getX()
        Wvars.camY = self.camNodePath.getY()
        Wvars.camZ = self.camNodePath.getZ()

        # move cursor to stay within screen bounds
        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = md.getY()
        if Wvars.cursorLock == True:
            # if int(monitor[0].width / 2) - mouseX >= int(monitor[0].width / 4):
            #     self.win.movePointer(0, x=int(monitor[0].width / 2), y=int(mouseY))
            #     self.lastMouseX = int(monitor[0].width / 2)
            # elif int(monitor[0].width / 2) - mouseX <= -int(monitor[0].width / 4):
            #     self.win.movePointer(0, x=int(monitor[0].width / 2), y=int(mouseY))
            #     self.lastMouseX = int(monitor[0].width / 2)
            # elif int(monitor[0].height / 2) - mouseY >= int(monitor[0].height / 4):
            #     self.win.movePointer(0, x=int(mouseX), y=int(monitor[0].height / 2))
            #     self.lastMouseY = int(monitor[0].height / 2)
            # elif int(monitor[0].height / 2) - mouseY <= -int(monitor[0].height / 4):
            #     self.win.movePointer(0, x=int(mouseX), y=int(monitor[0].height / 2))
            #     self.lastMouseY = int(monitor[0].height / 2)s
            # else:
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
        return result

    def setupControls(self):
        self.lastMouseX = self.win.getPointer(0).getX()
        self.lastMouseY = self.win.getPointer(0).getX()
        self.x_movement = 0
        self.y_movement = 0
        self.z_movement = 0
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
        self.accept("t", self.toggleTargetingGui)
        self.accept("r", self.doNothing)
        self.accept("q", sys.exit)
        self.accept("f", self.fullStop)

    def toggleTargetingGui(self):
        if Wvars.aiming == False:
            Wvars.aiming = True
            Wvars.cursorLock = False
            Wvars.movementEnabled = False
            disp.GUI.show(disp.GUI)
        elif Wvars.aiming == True:
            Wvars.aiming = False
            Wvars.cursorLock = True
            Wvars.movementEnabled = True
            disp.GUI.hide(disp.GUI)

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def doNothing(self):
        return None

    def fullStop(self):
        self.x_movement = 0
        self.y_movement = 0
        self.z_movement = 0

    def loadModels(self):
        self.sun = self.loader.loadModel("src/models/sun/sun.egg")
        self.ship = self.loader.loadModel("src/models/simple_ship/model.egg")
        self.skybox = self.loader.loadModel("src/models/skybox/stars.egg")
        self.skybox2 = self.loader.loadModel("src/models/skybox/stars.egg")
        self.voyager = self.loader.loadModel("src/models/voyager/voyager.bam")
        self.starNode = NodePath("starNode")
        self.starNode.reparentTo(self.render)
        disp.GUI.setup(disp.GUI)

    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((1, 1, 1, 1))
        self.ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNP)

    def setupCamera(self):
        self.camNodePath = NodePath("Camera_ship")
        self.camNodePath.reparentTo(self.render)

        self.ship.reparentTo(self.render)

        self.camera.reparentTo(self.camNodePath)
        self.camera.setPos(0, -50, 40)
        self.camLens.setFov(Wvars.camFOV)
        self.camera.lookAt(self.ship)

        self.crosshairs = OnscreenImage(
            image="src/textures/crosshairs.png",
            pos=(0, 0, 0),
            scale=0.03,
        )
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)
        self.crosshairs.show()

        self.cTrav = CollisionTraverser()

        fromObject = self.ship.attachNewNode(CollisionNode("shipColNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 3))
        fromObject.node().set_from_collide_mask(1)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, self.ship)
        self.cTrav.addCollider(fromObject, pusher)

        fromObject = self.camera.attachNewNode(CollisionNode("cameraColNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 1.5))
        fromObject.node().set_from_collide_mask(1)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, self.camera, self.drive.node())
        self.cTrav.addCollider(fromObject, pusher)

        disp.ShaderCall.setupShaders(
            self=disp.ShaderCall,
            mainApp=self,
            light=self.ambientLightNP,
            wantShaders=True,
        )

        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)

        self.velocityMeter = OnscreenText(text="", pos=(-1, -0.95), fg=(1, 1, 1, 1))

    def setupSkybox(self):
        self.skybox.setScale(50)
        self.skybox.setBin("background", 1)
        self.skybox.setDepthWrite(0)
        # self.skybox.setLightOff()
        self.skybox.setAntialias(AntialiasAttrib.MNone)
        self.skybox.reparentTo(self.render)

        self.skybox2.setScale(50)
        self.skybox2.setP(180)
        self.skybox2.setBin("background", 1)
        self.skybox2.setDepthWrite(0)
        # self.skybox2.setLightOff()
        self.skybox2.setAntialias(AntialiasAttrib.MNone)
        self.skybox2.reparentTo(self.render)

    def setupScene(self):
        # setup sun
        nodeScale = 500
        sunNode = NodePath("sun")
        sunNode.setPos(10000, 0, 1000)
        sunNode.setScale(nodeScale)
        self.sun.setTexture(
            self.loader.loadTexture(
                texturePath="src/textures/sun variants/" + str(randint(0, 3)) + ".png"
            )
        )
        self.sun.instanceTo(sunNode)
        sunNode.reparentTo(self.starNode)
        blockSolid = CollisionSphere(0, 0, 0, 1)
        blockNode = CollisionNode("block-collision-node")
        blockNode.addSolid(blockSolid)

        collider = sunNode.attachNewNode(blockNode)
        collider.setPythonTag("owner", sunNode)

        fromObject = sunNode.attachNewNode(CollisionNode("colNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 3.375))
        fromObject.node().set_from_collide_mask(0)
        fromObject.node().setPythonTag("owner", sunNode)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, sunNode)
        self.cTrav.addCollider(fromObject, pusher)

        self.voyager.reparentTo(self.render)
        self.voyager.setScale(180)
        self.voyager.setPos(-3000, 1500, 100)


app = Main()
