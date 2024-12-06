from operator import not_
import sys
import os
import shutil

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))

from math import pi, sin, cos
from random import randint
import time as t
import src.scripts.vars as Wvars
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
from direct.gui.OnscreenImage import OnscreenImage
from direct.stdpy.threading import Thread
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
    ).setValue(
        str(int(monitor[0].width / 2) + 80) + " " + str(int(monitor[0].height / 2))
    )
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "false").setValue("false")


xAspect = (int(monitor[0].width / 2) + 80) / int(monitor[0].height / 2)


def toggle(boolVar):
    if boolVar == True:
        boolVar = False
        return False
    elif boolVar == False:
        boolVar = True
        return True
    else:
        # raise TypeError(boolVar)
        ...


def degToRad(degrees):
    return degrees * (pi / 180.0)


class baseElement:
    name: str
    pos: tuple[3] | tuple[2]
    scale: tuple[3] | tuple[2]
    parent: NodePath
    color: tuple[4]
    image: NodePath
    frameSize: tuple[4]
    _type: DirectFrame


class buttonElement(baseElement):
    command: None
    geom: NodePath


class frameElement(baseElement):
    frameColor: tuple[4]


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.intro()

    def intro(self):
        self.setBackgroundColor(0, 0, 0, 1)
        movie = self.loader.loadTexture("src/movies/intro.mp4")
        image = OnscreenImage(movie, scale=1, parent=self.aspect2d)
        movie.play()
        movie.setLoopCount(1)
        startTime = t.monotonic()

        def finishLaunch(task):
            if t.monotonic() - startTime > 0:
                image.destroy()
                self.backfaceCullingOn()
                self.disableMouse()

                # do setup tasks
                # ...
                self.setupWorld()
                self.setupControls()
                # end of setup tasks
                self.taskMgr.add(self.update, "update")
            else:
                return task.cont

        self.taskMgr.add(finishLaunch)

    def update(self, task):
        result = task.cont
        if len(self.elements) > 0 and (self.moving or self.rotating or self.scaling):
            try:

                self.mouse_x = (
                    self.mouseWatcherNode.getMouseX() * xAspect
                ) - self.xOffset
                self.mouse_y = self.mouseWatcherNode.getMouseY() - self.yOffset

                if self.moving and self.selectedObject[0] != None:
                    self.selectedObject[0].setPos(
                        round(self.mouse_x, 2), 0, round(self.mouse_y, 2)
                    )
                elif self.scaling and self.selectedObject[0] != None:
                    if self.x and not self.y and not self.z:
                        self.selectedObject[0].setScale(
                            self.mouse_x,
                            0,
                            self.selectedObject[0].getScale()[2],
                        )
                    elif self.y and not self.x and not self.z:
                        self.selectedObject[0].setScale(
                            self.selectedObject[0].getScale()[0],
                            0,
                            self.mouse_y,
                        )
                    elif self.y and self.x and not self.z:
                        self.selectedObject[0].setScale(
                            self.mouse_x,
                            0,
                            self.mouse_y,
                        )
                    elif self.z and not self.x and not self.y:
                        self.selectedObject[0].setScale(
                            self.mouse_x,
                            0,
                            self.mouse_x,
                        )
                self.xIndicator.setZ(self.selectedObject[0].getZ())
                self.yIndicator.setX(self.selectedObject[0].getX())

                self.elements[self.selectedObject[1]].pos = self.selectedObject[
                    0
                ].getPos()
                self.elements[self.selectedObject[1]].scale = self.selectedObject[
                    0
                ].getScale()

                self.lastmouse_x = self.mouseWatcherNode.getMouseX()
                self.lastmouse_y = self.mouseWatcherNode.getMouseY()
            except AssertionError:
                ...
        return result

    def setupControls(self):
        self.moving = False
        self.rotating = False
        self.scaling = False
        self.x = True
        self.y = True
        self.z = False
        self.mouse_x = True
        self.mouse_y = True
        self.selectedObject = [None, None]
        self.xOffset = 0
        self.yOffset = 0

        self.accept("q", sys.exit)
        self.accept("shift-s", self.saveFile)
        self.accept("s", self.setMode, extraArgs=["scale"])
        self.accept("g", self.setMode, extraArgs=["move"])
        self.accept("r", self.setMode, extraArgs=["rotate"])
        self.accept("enter", self.setMode, extraArgs=["exit"])
        self.accept("mouse1", self.setMode, extraArgs=["exit"])
        self.accept(
            "shift-d",
            self.duplicate,
        )
        self.accept("x", self.setMode, extraArgs=["x"])
        self.accept("y", self.setMode, extraArgs=["y"])
        self.accept("z", self.setMode, extraArgs=["z"])
        self.accept(
            "v",
            self.spawnWindow,
        )

    def spawnWindow(self):
        Thread(
            target=os.system,
            args=["python3 presets/01.py"],
            daemon=True,
        ).start()

    def delete(self):
        if self.selectedObject[0] != None:
            self.selectedObject[0].destroy()
            self.selectedObject = [None, None]
            for element in self.elements.copy():
                if element == self.selectedObject[1]:
                    if len(self.elements) - 2 > 0 and element.endswith("-obj"):
                        self.selectObjFromName(
                            f'obj{int(element.split("obj")[1])-2}-obj'
                        )
                    del self.elements[element]

    def selectObjFromButton(self, button):
        self.selectedObject = [self.elements[button + "-obj"], button]
        if not self.moving and not self.rotating and not self.scaling:
            self.setMode("move")
        elif self.moving or self.scaling or self.rotating:
            self.setMode("exit")

    def selectObjFromName(self, name):
        self.selectedObject = [self.elements[name], name]

    def setMode(self, mode):
        if not self.selectedObject[0] == None:
            if mode == "move":
                self.moving = True
                self.rotating = False
                self.scaling = False
                self.x = False
                self.y = False
                self.z = False
                self.setMode("z")
            elif mode == "scale":
                self.moving = False
                self.rotating = False
                self.scaling = True
                self.x = False
                self.y = False
                self.z = False
                self.setMode("z")
            elif mode == "rotate":
                self.moving = False
                self.rotating = True
                self.scaling = False
            elif mode == "exit":
                self.moving = False
                self.rotating = False
                self.scaling = False
                self.x = False
                self.y = False
                self.z = False
            elif mode == "x":
                if self.moving or self.rotating or self.scaling:
                    self.x = toggle(self.y)
                    self.y = False
                    self.z = False
                else:
                    self.delete()
            elif mode == "y":
                self.x = False
                self.y = toggle(self.y)
                self.z = False
            elif mode == "z":
                self.x = False
                self.y = False
                self.z = True

            if self.x or self.z:
                self.xIndicator.show()
            else:
                self.xIndicator.hide()
            if self.y or self.z:
                self.yIndicator.show()
            else:
                self.yIndicator.hide()
            if (
                mode != "x"
                and mode != "y"
                and mode != "z"
                and mode != "exit"
                and self.selectedObject[0] != None
            ):
                try:
                    self.xOffset = (self.mouseWatcherNode.getMouseX() * xAspect) - (
                        self.selectedObject[0].getScale()[0]
                        if mode == "scale"
                        else self.selectedObject[0].getPos()[0] if mode == "move" else 0
                    )
                    self.yOffset = self.mouseWatcherNode.getMouseY() - (
                        self.selectedObject[0].getScale()[2]
                        if mode == "scale"
                        else self.selectedObject[0].getPos()[2] if mode == "move" else 0
                    )
                except AssertionError:
                    ...

    def doNothing(self):
        return None

    def duplicate(self):
        if self.elements[self.selectedObject[1]]._type == "DirectButton":
            newElement = buttonElement()
            newElement.parent = "self.aspect2d"
            newElement.pos = self.selectedObject[0].getPos()
            newElement.scale = self.selectedObject[0].getScale()
            newElement.color = (1, 1, 1, 1)
            newElement.frameSize = None
            newElement.image = str(self.selectedObject[0].cget("image").getFilename())
            newElement.geom = None
            newElement.name = f"obj{len(self.elements)}"
            newElement._type = "DirectButton"
            newButton = DirectButton(
                parent=self.aspect2d,
                pos=newElement.pos,
                scale=newElement.scale,
                color=newElement.color,
                geom=newElement.geom,
                image=self.loader.loadTexture(newElement.image),
                relief=None,
                frameColor=newElement.color,
                frameSize=newElement.frameSize,
                command=self.selectObjFromButton,
                extraArgs=[newElement.name],
            )
            self.selectedObject = [newButton, newElement.name]
            self.elements[newElement.name] = newElement
            self.elements[newElement.name + "-obj"] = newButton
        elif self.elements[self.selectedObject[1]]._type == "DirectFrame":
            newElement = frameElement()
            newElement.parent = "self.aspect2d"
            newElement.pos = self.selectedObject[0].getPos()
            newElement.scale = self.selectedObject[0].getScale()
            newElement.color = (1, 1, 1, 1)
            newElement.frameSize = self.selectedObject[0].cget("frameSize")
            newElement.frameColor = self.selectedObject[0].cget("frameColor")
            newElement.image = str(self.selectedObject[0].cget("image").getFilename())
            newElement.name = f"obj{len(self.elements)}"
            newElement._type = "DirectFrame"
            newFrame = DirectFrame(
                parent=self.aspect2d,
                pos=newElement.pos,
                scale=newElement.scale,
                color=newElement.color,
                frameColor=newElement.frameColor,
                image=(
                    self.loader.loadTexture(newElement.image)
                    if newElement.image != None
                    else None
                ),
                relief=None,
                frameSize=newElement.frameSize,
            )
            self.selectedObject = [newFrame, newElement.name]
            self.elements[newElement.name] = newElement
            self.elements[newElement.name + "-obj"] = newFrame
        self.setMode("move")

    def addButton(self):
        newElement = buttonElement()
        newElement.parent = "self.aspect2d"
        newElement.pos = (0, 0, 0)
        newElement.scale = 0.09
        newElement.color = (1, 1, 1, 1)
        newElement.frameSize = None
        newElement.image = "src/textures/button1.png"
        newElement.geom = None
        newElement.name = f"obj{len(self.elements)}"
        newElement._type = "DirectButton"

        newButton = DirectButton(
            parent=self.aspect2d,
            pos=newElement.pos,
            scale=newElement.scale,
            color=newElement.color,
            geom=newElement.geom,
            image=self.loader.loadTexture(newElement.image),
            relief=None,
            frameColor=newElement.color,
            frameSize=newElement.frameSize,
            command=self.selectObjFromButton,
            extraArgs=[newElement.name],
        )

        self.selectedObject = [newButton, newElement.name]
        self.elements[newElement.name] = newElement
        self.elements[newElement.name + "-obj"] = newButton

    def addFrame(self):
        newElement = frameElement()
        newElement.parent = "self.aspect2d"
        newElement.pos = (0, 0, 0)
        newElement.scale = 0.09
        newElement.frameColor = (0.5, 0.5, 0.5, 1)
        newElement.color = (1, 1, 1, 1)
        newElement.frameSize = (-0.1, 0.1, -0.1, 0.1)
        newElement.image = "src/textures/frame2.png"
        newElement.name = f"obj{len(self.elements)}"
        newElement._type = "DirectFrame"

        newFrame = DirectFrame(
            parent=self.aspect2d,
            pos=newElement.pos,
            scale=newElement.scale,
            color=newElement.color,
            frameColor=newElement.frameColor,
            image=(
                self.loader.loadTexture(newElement.image)
                if newElement.image != None
                else None
            ),
            relief=None,
            frameSize=newElement.frameSize,
        )

        self.selectedObject = [newFrame, newElement.name]
        self.elements[newElement.name] = newElement
        self.elements[newElement.name + "-obj"] = newFrame

    def setupWorld(self):
        self.elements: dict[baseElement, DirectButton] = {}
        self.appFrame = DirectFrame(
            parent=self.aspect2d,
            frameSize=(-1, 1, -0.8, 1),
            frameColor=(0.1, 0.1, 0.1, 1),
        )
        self.elementBarFrame = DirectFrame(
            parent=self.aspect2d,
            frameSize=(-1, 1, -1, -0.795),
            frameColor=(0.5, 0.5, 0.5, 1),
        )
        self.menuFrame = DirectFrame(
            parent=self.aspect2d,
            frameSize=(-1.75, -1.05, -1, 1),
            frameColor=(0.3, 0.3, 0.3, 1),
        )
        self.elementOptionFrame = DirectFrame(
            parent=self.aspect2d,
            frameSize=(1.05, 1.75, -1, 1),
            frameColor=(0.3, 0.3, 0.3, 1),
        )
        self.xIndicator = OnscreenImage(
            image=self.loader.loadTexture("src/textures/x.png"),
            scale=Vec3(3, 1, 0.0025),
        )
        self.yIndicator = OnscreenImage(
            image=self.loader.loadTexture("src/textures/y.png"),
            scale=Vec3(0.0025, 1, 3),
        )
        self.xIndicator.hide()
        self.yIndicator.hide()
        self.addNewFrame = DirectButton(
            parent=self.elementBarFrame,
            pos=(-0.9, 1, -0.9),
            scale=(0.09, 0.09, 0.09),
            geom=None,
            image=self.loader.loadTexture("src/textures/frame1.png"),
            command=self.addFrame,
            relief=None,
        )
        self.addNewButton = DirectButton(
            parent=self.elementBarFrame,
            pos=(-0.7, 0, -0.9),
            scale=0.09,
            geom=None,
            image=self.loader.loadTexture("src/textures/button1.png"),
            command=self.addButton,
            relief=None,
        )

    def packObject(self, obj: baseElement) -> str:
        shutil.copy(
            obj.image, obj.image.replace("src/textures/", f"presets/01/textures/")
        )
        return f"""
        self.{obj.name} = {obj._type}(
            parent={obj.parent},
            pos={obj.pos},
            scale={obj.scale},
            color={obj.color},
            relief=None,
            geom=None,
            image=self.loader.loadTexture("{obj.image.replace("src/textures/", f"01/textures/")}"),
        )
"""

    def saveFile(self):

        baseText = [
            f"""from direct.gui.DirectGui import *
from panda3d.core import (
    LVecBase3f,
    LPoint3f,
    LVecBase4f,
    LPoint4f,
)


class frame:
    def build(self):
        ...
"""
        ]
        try:
            os.mkdir("presets/01/")
        except:
            ...
        try:
            os.mkdir("presets/01/textures/")
        except:
            ...
        for element in self.elements:
            if element.count("-obj") == 0:
                baseText.append(self.packObject(self.elements[element]))
        baseText.append(
            """

if __name__ == "__main__":
    from direct.showbase.ShowBase import ShowBase

    base = ShowBase()
    base.setBackgroundColor(0, 0, 0, 1)
    base.accept("q", exit)
    frame.build(base)
    base.run()
"""
        )
        baseText = "".join(baseText)
        with open("presets/01.py", "wt") as pyFile:
            pyFile.writelines(baseText)


app = Main()
app.run()
