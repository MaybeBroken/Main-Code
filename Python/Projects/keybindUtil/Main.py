import sys
import os
import keyboard
import asyncio
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
)

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
    loadPrcFile,
    ConfigVariableString,
)
from direct.stdpy.threading import Thread
from direct.gui.DirectGui import *
from PIL import Image, ImageOps

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


def correctAspectRatio(aspectRatio):
    return aspectRatio * monitor[0].width / monitor[0].height


def convertSvgToPng(svgPath, pngPath, dpi=800, color=(50, 50, 50)):
    if not os.path.exists(pngPath):
        drawing = svg2rlg(svgPath)
        renderPM.drawToFile(
            drawing,
            pngPath,
            fmt="PNG",
            dpi=dpi,
            # bg=int("0x{:02x}{:02x}{:02x}".format(color[0], color[1], color[2],), 16),
        )
        img = Image.open(pngPath)
        inverted_image = ImageOps.invert(img.convert("RGB"))
        inverted_image.save(pngPath)
    return pngPath


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.backfaceCullingOn()
        self.disableMouse()

        # do setup tasksD
        # ...
        self.setupWorld()
        self.setupControls()
        # end of setup tasks
        self.taskMgr.add(self.update, "update")

    def update(self, task):
        return task.cont

    def setupControls(self):
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.keyMap = {}
        self.accept("q", sys.exit)

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def doNothing(self):
        return None

    def setupWorld(self):
        self.guiFrame = DirectFrame(
            parent=self.aspect2d,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-2, 2, -1, 1),
            pos=(0, 0, 0),
        )
        self.keyBindsListFrame = DirectFrame(
            parent=self.guiFrame,
            frameColor=(0, 0, 0, 1),
            frameSize=(-0.5, 0.5, -1, 1),
            pos=(correctAspectRatio(-0.75), 0, 0),
        )
        self.keyBindsListBorder = DirectFrame(
            parent=self.guiFrame,
            frameColor=(0, 0, 0, 1),
            frameSize=(-0.5, 0.5, -0.2, 0),
            pos=(correctAspectRatio(-0.75), 0, -0.8),
        )
        self.editorWindow = DirectFrame(
            parent=self.guiFrame,
            frameColor=(0.4, 0.4, 0.4, 1),
            frameSize=(-1.1, 2, -1, 1),
            pos=(0.25, 0, 0),
        )
        self.keyBindsList = []
        self.newKeyBindButton = DirectButton(
            parent=self.guiFrame,
            scale=0.1,
            geom=None,
            relief=None,
            image=self.loader.loadTexture(
                convertSvgToPng(
                    "src/textures/ui-cons/file-plus-03.svg",
                    "src/textures/file-plus-03.png",
                )
            ),
            pos=(correctAspectRatio(-0.75), 0, -0.9),
            command=self.newKeyBind,
            extraArgs=[" blank ", self.doNothing],
        )

    def deleteKeyBind(self, keyBind):
        self.keyBindsList.remove(keyBind)
        self.updateKeyBindList()

    def newKeyBind(self, key, func):
        self.keyBindsList.append([key, func])
        self.updateKeyBindList()

    def updateKeyBindList(self):
        for childNode in self.keyBindsListFrame.getChildren():
            try:
                childNode.destroy()
            except:
                childNode.removeNode()
        for i in range(len(self.keyBindsList)):
            DirectLabel(
                parent=self.keyBindsListFrame,
                text=self.keyBindsList[i][0],
                text_scale=0.08,
                text_fg=(1, 1, 1, 1),
                frameColor=(0, 0, 0, 0),
                pos=(-0.3, 0, 0.9 - i * 0.2),
            )
            DirectButton(
                parent=self.keyBindsListFrame,
                scale=0.03,
                frameColor=(1.0, 1.0, 1.0, 0.0),
                geom=None,
                relief=None,
                image=self.loader.loadTexture(
                    convertSvgToPng(
                        "src/textures/ui-cons/delete.svg",
                        "src/textures/delete.png",
                    )
                ),
                pos=(0.4, 0, (0.9 - i * 0.2) - 0.05),
                command=self.deleteKeyBind,
                extraArgs=[self.keyBindsList[i]],
            )
            DirectButton(
                parent=self.keyBindsListFrame,
                scale=0.03,
                frameColor=(1.0, 1.0, 1.0, 0.0),
                geom=None,
                relief=None,
                image=self.loader.loadTexture(
                    convertSvgToPng(
                        "src/textures/ui-cons/edit-05.svg",
                        "src/textures/edit-05.png",
                    )
                ),
                pos=(0.4, 0, (0.975 - i * 0.2) - 0.05),
                command=self.openEditorPage,
                extraArgs=[self.keyBindsList[i]],
            )

    def openEditorPage(self, page):
        for childNode in self.editorWindow.getChildren():
            try:
                childNode.destroy()
            except:
                childNode.removeNode()
        


app = Main()
app.run()
