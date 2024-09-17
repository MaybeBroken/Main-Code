from math import pi, sin, cos, sqrt
from random import randint
import time as t
import sys
from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper
import websockets as ws
import src.scripts.vars as Wvars
import src.scripts.physics as physics
import src.scripts.display as disp
import src.scripts.fileManager as fMgr
import src.scripts.client as cli
import src.scripts.weapons as weapons

from screeninfo import get_monitors
from direct.showbase.ShowBase import ShowBase
from panda3d.ai import *
from panda3d.ai import AIWorld, AICharacter, Flock

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
    Vec4,
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

        disp.GUI.start(
            self=disp.GUI,
            render=self.render2d,
            main=self,
            TransparencyAttrib=TransparencyAttrib,
            monitor_=monitor,
        )
        physics.physicsMgr.enable(
            self=physics.physicsMgr,
            minimum_motion_check=0.001,
            drag=0.001,
            gravity=(0, 0, 0),
        )

        self.loadModels()
        self.setupLights()
        self.setupCamera()
        self.setupSkybox()
        self.setupScene()
        self.setupAiWorld()
        weapons.lasers.__init__(
            self=self,
            internalArgs=[
                [
                    "objects",
                    ["cube", self.loader.loadModel("src/models/cube/cube.egg")],
                ],
                ["sceneGraphs", ["render3d", self.render]],
            ],
        )

        thread.Thread(target=cli.runClient, daemon=True, args=[Wvars.dataKeys]).start()

        # end of setup tasks
        self.update_time = 0
        self.taskMgr.add(self.update, "update")
        self.taskMgr.add(self.sync, "syncServer+Client")

    def sync(self, task):
        Wvars.dataKeys = {
            "shipPos": {
                "x": self.ship.getX(),
                "y": self.ship.getY(),
                "z": self.ship.getZ(),
            }
        }
        return task.cont

    def updateAiWorld(self):
        self.AIworld.update()
        try:
            for aiChar in range(len(self.aiChars)):
                ai = self.aiChars[aiChar]["ai"]
                node = self.aiChars[aiChar]["mesh"]
                AIbehaviors = ai.getAiBehaviors()
                # if self.ship.getDistance(node) < 50:
                #     AIbehaviors.flee(self.ship)
                # if self.ship.getDistance(node) > 100:
                #     AIbehaviors.pursue(self.ship)
        except:
            None

    def update(self, task):
        result = task.cont
        playerMoveSpeed = Wvars.speed / 100
        self.updateAiWorld()

        # update velocities
        if self.update_time > 4:
            self.update_time = 0
            self.velocity = physics.physicsMgr.getObjectVelocity(
                physics.physicsMgr, self.ship, "ship"
            )
            self.vel_text = (
                "Thrust: "
                + str(
                    round(
                        number=(
                            ((round(abs(self.velocity[0]) * 1000)) ^ 2)
                            + ((round(abs(self.velocity[1]) * 1000)) ^ 2)
                            + ((round(abs(self.velocity[2]) * 1000)) ^ 2) / 1000
                        )
                        - 4,
                        ndigits=2,
                    )
                )
                + " km/s"
            )
            self.velocityMeter.configure(text=self.vel_text)
            self.posMeter.configure(text="pos XYZ: " + str(self.ship.getPos()))
        else:
            self.update_time += 1

        # do system updates
        dt = globalClock.getDt()  # type: ignore
        self.camera.setHpr(0, 0, 0)
        self.camera.setPos(0, -50, 40)
        self.camera.lookAt(self.ship)
        self.skybox.setPos(self.camNodePath.getPos())
        self.skybox2.setPos(self.camNodePath.getPos())

        self.SceneLightNode_sm.lookAt(self.ship)

        # calculate thrust
        if Wvars.movementEnabled == True:
            if self.keyMap["left"]:
                self.ship.setH(self.ship.getH() + Wvars.turnspeed / 100)
            if self.keyMap["right"]:
                self.ship.setH(self.ship.getH() - Wvars.turnspeed / 100)
            if self.keyMap["up"]:
                self.ship.setP(self.ship.getP() + Wvars.turnspeed / 100)
            if self.keyMap["down"]:
                self.ship.setP(self.ship.getP() - Wvars.turnspeed / 100)
            if self.keyMap["forward"]:
                self.x_movement -= (
                    dt * playerMoveSpeed * sin(degToRad(self.ship.getH()))
                )
                self.y_movement += (
                    dt * playerMoveSpeed * cos(degToRad(self.ship.getH()))
                )
                self.z_movement += (
                    dt * playerMoveSpeed * cos(degToRad(self.ship.getP() - 90))
                )
            if self.keyMap["backward"]:
                self.x_movement += (
                    dt * playerMoveSpeed * sin(degToRad(self.ship.getH()))
                )
                self.y_movement -= (
                    dt * playerMoveSpeed * cos(degToRad(self.ship.getH()))
                )
                self.z_movement -= (
                    dt * playerMoveSpeed * cos(degToRad(self.ship.getP() - 90))
                )

        physics.physicsMgr.addVectorForce(
            physics.physicsMgr,
            self.ship,
            "ship",
            [self.x_movement, self.y_movement, self.z_movement],
        )
        self.x_movement = 0
        self.y_movement = 0
        self.z_movement = 0
        physics.physicsMgr.updateWorldPositions(physics.physicsMgr)
        if len(physics.physicsMgr.returnCollisions(physics.physicsMgr)) > 0:
            physics.physicsMgr.returnCollisions(physics.physicsMgr)
            physics.physicsMgr.clearCollisions(physics.physicsMgr)

        self.camNodePath.setPos(self.ship.getPos())
        Wvars.camX = self.camNodePath.getX()
        Wvars.camY = self.camNodePath.getY()
        Wvars.camZ = self.camNodePath.getZ()

        # move cursor to stay within screen bounds
        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = md.getY()
        if Wvars.cursorLock == True:

            def moveCam():
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

            if sys.platform == "darwin":
                moveCam()
            elif int(monitor[0].width / 2) - mouseX >= int(monitor[0].width / 4):
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
                moveCam()

        if Wvars.aiming == True:
            md = self.win.getPointer(0)
            self.lastMouseX = md.getX()
            self.lastMouseY = md.getY()

            self.crosshair.setPos(
                (2 / monitor[0].width) * md.getX() - 1,
                0,
                -((2 / monitor[0].height) * md.getY() - 1),
            )
            if self.progress["value"] < 100:
                self.progress["value"] += 1
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
        self.accept("mouse1", self.MouseClicked)
        self.accept("mouse1-up", self.doNothing)
        self.accept("mouse3", self.toggleTargetingGui)
        self.accept("mouse3-up", self.toggleTargetingGui)
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
            self.hideCursor(True)
            Wvars.movementEnabled = False
            self.progress["value"] = 0
            disp.GUI.show(disp.GUI)
        elif Wvars.aiming == True:
            Wvars.aiming = False
            Wvars.cursorLock = True
            self.hideCursor(True)
            Wvars.movementEnabled = True
            disp.GUI.hide(disp.GUI)
            self.progress["value"] = 0

    def chargeLaser(self):
        self.laserPower = 0

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def doNothing(self):
        return None

    def fullStop(self):
        self.x_movement = 0
        self.y_movement = 0
        self.z_movement = 0
        physics.physicsMgr.clearVectorForce(physics.physicsMgr, self.ship, "ship")

    def loadModels(self):
        self.sun = self.loader.loadModel("src/models/sun/sun.egg")
        self.skybox = self.loader.loadModel("src/models/skybox/stars.egg")
        self.ship = self.loader.loadModel("src/models/simple_ship/model.egg")
        self.skybox2 = self.loader.loadModel("src/models/skybox/stars.egg")
        self.voyager = self.loader.loadModel("src/models/cube/cube.egg")
        self.laser_base_geom = self.loader.loadModel(
            "src/models/simple_ship/redRect.bam"
        )
        self.drone = self.loader.loadModel("src/models/cube/cube.egg")
        self.starNode = NodePath("starNode")
        self.starNode.reparentTo(self.render)
        disp.GUI.setup(disp.GUI)

    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((0.1, 0.1, 0.1, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)

        slight = Spotlight("slight")
        slight.setColor((1, 1, 1, 1))
        lens = OrthographicLens()
        lens.setFov(80)
        slight.setLens(lens)

        self.SceneLightNode_sm = self.render.attachNewNode(slight)

        self.SceneLightNode_sm.setPos(10000, 0, 1000)
        self.SceneLightNode_sm.lookAt(self.ship)

        self.render.setLight(self.SceneLightNode_sm)

    def setupCamera(self):
        self.camNodePath = NodePath("Camera_ship")
        self.camNodePath.reparentTo(self.render)

        self.ship.reparentTo(self.render)

        physics.physicsMgr.registerObject(
            physics.physicsMgr, self.ship, [0, 0, 0], "ship"
        )

        self.camera.reparentTo(self.camNodePath)
        self.camera.setPos(0, -50, 40)
        self.camLens.setFov(Wvars.camFOV)
        self.camera.lookAt(self.ship)

        self.cTrav = CollisionTraverser()

        fromObject = self.ship.attachNewNode(CollisionNode("shipColNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 3))
        fromObject.node().set_from_collide_mask(1)
        fromObject.node().set_from_collide_mask(0)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, self.ship)
        self.cTrav.addCollider(fromObject, pusher)

        fromObject = self.camera.attachNewNode(CollisionNode("cameraColNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 1.5))
        fromObject.node().set_from_collide_mask(1)
        fromObject.node().set_from_collide_mask(0)
        pusher.addCollider(fromObject, self.camera, self.drive.node())
        self.cTrav.addCollider(fromObject, pusher)

        self.ray = CollisionRay()
        self.ray.setFromLens(self.camNode, (0, 0))
        self.rayNode = CollisionNode("line-of-sight")
        self.rayNode.addSolid(self.ray)
        self.rayNode.set_into_collide_mask(0)
        self.rayNode.set_into_collide_mask(1)
        self.rayNodePath = self.ship.attachNewNode(self.rayNode)
        self.rayQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(self.rayNodePath, self.rayQueue)

        targetNode = NodePath("targetingNode")
        targetNode.reparentTo(self.ship)
        targetNode.set_y(45)

        size = 3

        fromObject = self.ship.attachNewNode(CollisionNode("colNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, size))
        fromObject.node().set_from_collide_mask(0)
        fromObject.node().setPythonTag("owner", targetNode)
        fromObject.set_y(10000)

        sNodeSolid = CollisionNode("block-collision-node")
        collider = self.ship.attachNewNode(sNodeSolid)
        collider.setPythonTag("owner", targetNode)

        self.cTrav.addCollider(fromObject, self.rayQueue)

        disp.ShaderCall.setupShaders(
            self=disp.ShaderCall,
            mainApp=self,
            light=self.SceneLightNode_sm,
            wantShaders=True,
        )

        self.hideCursor(True)
        self.velocityMeter = OnscreenText(
            text="",
            scale=(0.1 * (monitor[0].height / monitor[0].width), 0.1, 0.1),
            pos=(-0.5, -0.95),
            fg=(1, 1, 1, 1),
            parent=self.render2d,
        )
        self.posMeter = OnscreenText(
            text="",
            scale=(0.1 * (monitor[0].height / monitor[0].width), 0.1, 0.1),
            pos=(-0.5, -0.8),
            fg=(1, 1, 1, 1),
            parent=self.render2d,
        )

    def hideCursor(self, boolVar):
        properties = WindowProperties()
        properties.setCursorHidden(boolVar)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)

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

    def setupAiWorld(self):
        self.AIworld = AIWorld(self.render)
        self.AiFlock = Flock(1, 270, 10, 2, 4, 1)
        self.AIworld.addFlock(self.AiFlock)
        self.AIworld.flockOn(1)

        self.aiChars = {}
        for num in range(3):
            dNode = self.loader.loadModel("src/models/cube/cube.egg")
            dNode.instanceTo(self.droneMasterNode)
            dNode.setPos(randint(-100, 100), randint(-100, 100), randint(-100, 100))
            dNode.setScale(3)
            AIchar = AICharacter("seeker", dNode, 1, 15, 1)
            self.AIworld.addAiChar(AIchar)
            self.AiFlock.addAiChar(AIchar)
            AIbehaviors = AIchar.getAiBehaviors()
            # AIbehaviors.pursue(self.ship)
            AIbehaviors.flock(0.5)

            size = 3

            fromObject = dNode.attachNewNode(CollisionNode("colNode"))
            fromObject.node().addSolid(CollisionSphere(0, 0, 0, size))
            fromObject.node().set_from_collide_mask(0)
            fromObject.node().setPythonTag("owner", num)
            fromObject.node().setPythonTag("collision", fromObject)
            pusher = CollisionHandlerPusher()
            pusher.addCollider(fromObject, dNode)
            self.cTrav.addCollider(fromObject, pusher)

            self.aiChars[num] = {"mesh": dNode, "ai": AIchar}

    def setupScene(self):
        # setup sun
        nodeScale = 5000
        sunNode = NodePath("sun")
        sunNode.reparentTo(self.starNode)
        self.starNode.setPos(100000, 0, 10000)
        self.starNode.setScale(nodeScale)
        self.sun.setTexture(
            self.loader.loadTexture(
                texturePath="src/textures/sun variants/" + str(randint(0, 3)) + ".png"
            )
        )
        self.sun.instanceTo(sunNode)
        droneNode = CollisionSphere(0, 0, 0, 1)
        droneNodeSolid = CollisionNode("block-collision-node")
        droneNodeSolid.addSolid(droneNode)

        collider = sunNode.attachNewNode(droneNodeSolid)
        collider.setPythonTag("owner", sunNode)

        fromObject = sunNode.attachNewNode(CollisionNode("colNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 3.375))
        fromObject.node().set_from_collide_mask(0)
        fromObject.node().setPythonTag("owner", sunNode)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, sunNode)
        self.cTrav.addCollider(fromObject, pusher)

        self.voyager.reparentTo(self.render)
        self.voyager.setScale(280)
        self.voyager.setPos(-3000, 1500, 100)
        self.camera.lookAt(self.voyager)

        worldDistance = 1000

        physics.physicsMgr.registerColliderPlane(
            self=physics.physicsMgr,
            object="1",
            pos=-worldDistance,
            name="Collider1",
            orientation="+x",
            collisionAction="stop",
        )

        physics.physicsMgr.registerColliderPlane(
            self=physics.physicsMgr,
            object="2",
            pos=worldDistance,
            name="Collider2",
            orientation="-x",
            collisionAction="stop",
        )

        physics.physicsMgr.registerColliderPlane(
            self=physics.physicsMgr,
            object="3",
            pos=-worldDistance,
            name="Collider3",
            orientation="+y",
            collisionAction="stop",
        )

        physics.physicsMgr.registerColliderPlane(
            self=physics.physicsMgr,
            object="4",
            pos=worldDistance,
            name="Collider4",
            orientation="-y",
            collisionAction="stop",
        )

        physics.physicsMgr.registerColliderPlane(
            self=physics.physicsMgr,
            object="5",
            pos=-worldDistance,
            name="Collider5",
            orientation="+z",
            collisionAction="stop",
        )

        physics.physicsMgr.registerColliderPlane(
            self=physics.physicsMgr,
            object="6",
            pos=worldDistance,
            name="Collider6",
            orientation="-z",
            collisionAction="stop",
        )

        self.droneMasterNode = NodePath("drone-MN")
        self.droneMasterNode.reparentTo(self.render)

        self.shipTrailNode = NodePath("shipTrailNode")
        self.shipTrailNode.reparentTo(self.ship)
        self.shipTrailNode.set_y(-10)

        shipTrail = MotionTrail("shipTrail", self.shipTrailNode)

        flame_colors = (
            Vec4(0, 0.0, 1.0, 1),
            Vec4(0, 0.2, 1.0, 1),
            Vec4(0, 0.7, 1.0, 1),
            Vec4(0.0, 0.0, 0.2, 1),
            Vec4(0, 0.7, 0.5, 1),
            Vec4(0, 0, 1.0, 1),
            Vec4(0.3, 0.7, 0.0, 1),
            Vec4(0.1, 0.1, 0.2, 1),
        )
        for x in [-6, 6]:
            center = self.render.attach_new_node("center")
            around = center.attach_new_node("around")
            around.set_z(1.5)
            center.set_x(x)
            res = 8
            for i in range(res + 1):
                center.set_r((360 / res) * i)
                vertex_pos = around.get_pos(self.render)
                shipTrail.add_vertex(vertex_pos)

                start_color = flame_colors[i % len(flame_colors)] * 1.7
                end_color = Vec4(1, 1, 0, 1)
                shipTrail.set_vertex_color(i, start_color, end_color)
        shipTrail.update_vertices()

        shipTrail.register_motion_trail()
        shipTrail.geom_node_path.reparentTo(self.render)
        self.enableParticles()

    def MouseClicked(self):
        mpos = self.mouseWatcherNode.getMouse()
        # self.cTrav.showCollisions(self.render)
        # self.ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())
        self.cTrav.traverse(self.render)
        destroy = False
        if self.rayQueue.getNumEntries() > 1:
            self.rayQueue.sortEntries()
            try:
                rayHit = self.rayQueue.getEntry(1)
                hitNodePath = rayHit.getIntoNodePath()
                normal = rayHit.getSurfaceNormal(hitNodePath)
            except:
                None
            try:
                hitObject = self.aiChars[hitNodePath.getPythonTag("owner")]["mesh"]
                colNode = hitNodePath.getPythonTag("collision")
                self.cTrav.removeCollider(colNode)
                del self.aiChars[hitNodePath.getPythonTag("owner")]
                destroy = True
                print(f"destroyed node {colNode} at path {hitNodePath}")
            except:
                hitObject = hitNodePath.getPythonTag("owner")
                destroy = False
            if type(hitObject) == int:
                return
            else:
                weapons.lasers.fire(origin=self.ship, target=hitObject, normal=normal, destroy=destroy)


app = Main()
