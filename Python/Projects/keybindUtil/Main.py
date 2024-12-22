import sys
import os
import keyboard
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))

from math import e, pi, sin, cos
from random import randint
import time as t
import src.scripts.vars as Wvars
from screeninfo import get_monitors
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.core import (
    loadPrcFile,
    ConfigVariableString,
    TextNode,
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

        # do setup tasks
        # ...
        self.setupWorld()
        # end of setup tasks
        self.taskMgr.add(self.update, "update")

    def update(self, task):
        return task.cont

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
        self.keyBindsDict = {}
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
            extraArgs=[
                "blank",
                {
                    "func": self.doNothing,
                    "funcObj": None,
                    "args": [],
                    "hotkey": "",
                    "commandType": None,
                    "nameObj": None,
                    "hotkeyObj": None,
                    "commandTypeObj": None,
                },
            ],
        )

    def deleteKeyBind(self, key):
        if key in self.keyBindsDict:
            del self.keyBindsDict[key]
        self.updateKeyBindList()
        for childNode in self.editorWindow.getChildren():
            try:
                childNode.destroy()
            except:
                childNode.removeNode()

    def newKeyBind(self, key, func):
        unique_key = key
        counter = 1
        while unique_key in self.keyBindsDict:
            unique_key = f"{key} {counter}"
            counter += 1
        self.keyBindsDict[unique_key] = func
        self.updateKeyBindList()
        self.openEditorPage(unique_key)

    def updateKeyBindList(self):
        for childNode in self.keyBindsListFrame.getChildren():
            try:
                childNode.destroy()
            except:
                childNode.removeNode()
        for i, (key, dict) in enumerate(self.keyBindsDict.items()):
            DirectLabel(
                parent=self.keyBindsListFrame,
                text=key,
                text_scale=0.08,
                text_fg=(1, 1, 1, 1),
                frameColor=(0, 0, 0, 0),
                pos=(0.2, 0, 0.9 - i * 0.2),
                text_align=TextNode.ARight,
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
                extraArgs=[key],
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
                extraArgs=[key],
            )

    def changeKeyBindName(self, key):
        if key in self.keyBindsDict:
            newName = self.keyBindsDict[key]["nameObj"].get()
            self.keyBindsDict[newName] = self.keyBindsDict.pop(key)
            self.updateKeyBindList()
            self.openEditorPage(newName)

    def changeHotkey(self, key):
        self.keyBindsDict[key]["hotkey"] = keyboard.read_hotkey()
        self.keyBindsDict[key]["hotkeyObj"]["text"] = self.keyBindsDict[key]["hotkey"]
        self.openEditorPage(key)

    def openEditorPage(self, key):
        for childNode in self.editorWindow.getChildren():
            try:
                childNode.destroy()
            except:
                childNode.removeNode()
        self.keyBindsDict[key]["nameObj"] = DirectEntry(
            parent=self.editorWindow,
            scale=0.075,
            pos=(-1, 0, 0.9),
            initialText=key,
            focusOutCommand=self.changeKeyBindName,
            focusOutExtraArgs=[key],
        )
        self.keyBindCommandWindow = DirectFrame(
            parent=self.editorWindow,
            frameColor=(0.2, 0.2, 0.2, 1),
            frameSize=(-0.5, 1.4, -0.6, 0.8),
            pos=(0, 0, -0.2),
        )
        self.keyBindsDict[key]["hotkeyObj"] = DirectButton(
            parent=self.editorWindow,
            scale=0.15,
            text=(
                self.keyBindsDict[key]["hotkey"]
                if "hotkey" in self.keyBindsDict[key]
                else "None"
            ),
            pos=(-0.5, 0, 0.7),
            command=self.changeHotkey,
            extraArgs=[key],
        )
        self.keyBindsDict[key]["commandTypeObj"] = DirectOptionMenu(
            parent=self.editorWindow,
            scale=0.075,
            items=["Command", "Script", "Trigger"],
            initialitem=0,
            pos=(-1, 0, 0.5),
            command=self.changeKeybindCommandType,
            extraArgs=[key],
        )
        self.bindButton = DirectButton(
            parent=self.editorWindow,
            scale=0.1,
            text="Bind",
            pos=(-0.8, 0, -0.9),
            command=self.bind,
            extraArgs=[key],
        )
        self.refreshKeybindCommandWindow(key)

    def bind(self, key):
        if self.keyBindsDict[key]["commandType"] == "Script":
            self.keyBindsDict[key]["func"] = lambda: Thread(
                target=os.system,
                args=["python3 " + self.keyBindsDict[key]["args"]],
            ).start()
        keyboard.add_hotkey(
            self.keyBindsDict[key]["hotkey"],
            self.keyBindsDict[key]["func"],
        )

    def setArgs(self, key):
        self.keyBindsDict[key]["args"] = (
            self.keyBindsDict[key]["funcObj"].get().replace("\\n", "\n")
        )

    def changeKeybindCommandType(self, index, key):
        self.keyBindsDict[key]["commandType"] = index
        self.openEditorPage(key)

    def refreshKeybindCommandWindow(self, key):
        for childNode in self.keyBindCommandWindow.getChildren():
            try:
                childNode.destroy()
            except:
                childNode.removeNode()
        if self.keyBindsDict[key]["commandType"] == "Command":
            self.keyBindsDict[key]["funcObj"] = DirectOptionMenu(
                parent=self.keyBindCommandWindow,
                scale=0.075,
                items=["preset1", "preset2", "preset3"],
                initialitem=0,
                pos=(-0.4, 0, 0.5),
            )
        elif self.keyBindsDict[key]["commandType"] == "Script":
            self.keyBindsDict[key]["funcObj"] = DirectEntry(
                parent=self.keyBindCommandWindow,
                scale=0.075,
                pos=(-0.25, 0, 0.5),
                numLines=8,
                width=20,
                focusOutCommand=self.setArgs,
                focusOutExtraArgs=[key],
                focus=True,
                overflow=True,
            )


app = Main()
app.run()
