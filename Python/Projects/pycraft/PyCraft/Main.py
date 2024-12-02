from math import pi, sin, cos
from random import randint
import numpy as np
import time as t
import sys
import os
from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper

import PyCraft.modules.worldGen as gen
import PyCraft.modules.FileMgr as Fmgr
import PyCraft.modules.vars as Worldvars
import PyCraft.modules.FileParser as Parser
import PyCraft.modules.display as Ui
import PyCraft.modules.utils as utils

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
import direct.stdpy.threading as thread
import direct.stdpy.file as panda_fMgr
from direct.gui.DirectGui import *
import direct.particles.Particles as part

userPrefFile = panda_fMgr.open("userPref.txt", "rt")
data = load(userPrefFile, Loader=fLoader)
userPrefFile.close()
Worldvars.difficulty = data[0]
Worldvars.font = data[1]
Worldvars.winMode = data[2]
Worldvars.resolution = data[3]
Worldvars.reachDistance = data[4]
Worldvars.renderDist = data[5]
Worldvars.audioVolume = data[6]

loadPrcFile("PyCraft/settings.prc")
monitor = get_monitors()
if Worldvars.winMode == "full-win":
    ConfigVariableString(
        "win-size", str(monitor[0].width) + " " + str(monitor[0].height)
    ).setValue(str(monitor[0].width) + " " + str(monitor[0].height))
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "true").setValue("true")

elif Worldvars.winMode == "full":
    ConfigVariableString(
        "win-size", str(Worldvars.resolution[0]) + " " + str(Worldvars.resolution[1])
    ).setValue(str(Worldvars.resolution[0]) + " " + str(Worldvars.resolution[1]))
    ConfigVariableString("fullscreen", "true").setValue("true")
    ConfigVariableString("undecorated", "true").setValue("true")

elif Worldvars.winMode == "full-1":
    ConfigVariableString(
        "win-size", str(monitor[0].width) + " " + str(monitor[0].height)
    ).setValue(str(monitor[0].width) + " " + str(monitor[0].height))
    ConfigVariableString("fullscreen", "true").setValue("true")
    ConfigVariableString("undecorated", "true").setValue("true")

elif Worldvars.winMode == "win":
    ConfigVariableString(
        "win-size",
        str(int(monitor[0].width / 2)) + " " + str(int(monitor[0].height / 2)),
    ).setValue(str(int(monitor[0].width / 2)) + " " + str(int(monitor[0].height / 2)))
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "false").setValue("false")
# Runtime


def degToRad(degrees):
    return degrees * (pi / 180.0)


class Main(ShowBase):
    def __init__(self):
        # initialize panda3d

        ShowBase.__init__(self)

        self.selectedBlockType = "grass"
        # what to load on startup
        self.font = self.loader.loadFont("PyCraft/src/" + Worldvars.font + ".ttf")
        self.intro()

    def intro(self):
        self.setBackgroundColor(0, 0, 0, 1)
        movie = self.loader.loadTexture("PyCraft/src/movies/intro.mp4")
        image = OnscreenImage(movie, scale=1, parent=self.aspect2d)
        movie.play()
        movie.setLoopCount(1)
        startTime = t.monotonic()

        def finishLaunch(task):
            if t.monotonic() - startTime > 3.1:
                image.destroy()
                self.loadModels()
                self.setupLights()
                self.backfaceCullingOn()
                self.disableMouse()
                self.menu()
                Fmgr.mgr.start()
                self.startAudio()
                self.taskMgr.add(self.update, "update")
            else:
                return task.cont

        self.taskMgr.add(finishLaunch)

    def selectorUp(self):
        if Worldvars.inMenu != True:
            Worldvars.selectedSlot += 1
            if Worldvars.selectedSlot > 8:
                Worldvars.selectedSlot = 0

    def selectorDown(self):
        if Worldvars.inMenu != True:
            Worldvars.selectedSlot -= 1
            if Worldvars.selectedSlot < 0:
                Worldvars.selectedSlot = 8

    def startAudio(self):
        print("Starting Audio Manager")
        self.songARR = []
        self.setupAudioPaths()
        self.AudioPath = self.songARR[randint(0, len(self.songARR) - 1)]
        self.playOnce()
        self.task_mgr.add(self.playSongs, "AudioMGR")
        self.music.setVolume(Worldvars.audioVolume / 100)

    def setupAudioPaths(self):
        for root, dirs, files in os.walk("PyCraft/src/audio"):
            for name in files:
                if name.endswith((".wav", ".mp3", ".ogg")):
                    self.songARR.append(
                        self.loader.loadSfx("PyCraft/src/audio/" + name)
                    )

    def playSongs(self, task):
        if self.music.status() == AudioSound.READY:
            self.AudioPath = self.songARR[randint(0, len(self.songARR) - 1)]
            self.music = self.AudioPath
            self.music.play()
        return task.cont

    def playOnce(self):
        self.music = self.AudioPath
        self.music.play()

    def makeWorld(self):
        Worldvars.seed = randint(0, 99999999)
        name = self.worldname.get(plain=True)
        Fmgr.mgr.makeNewWorld(name=name)
        self.loadNewWorld(name=Fmgr.mgr.folderPath + name + ".dat\n")

    def newWorld(self):

        self.killWorldOptionsScreen()

        worldlist = Fmgr.mgr.returnWorldList()
        i = 0
        for blank in worldlist:
            i = i + 1

        self.newWorldScreen = DirectFrame(frameColor=(1, 1, 1, 0))

        self.worldname = DirectEntry(
            pos=(-0.38, 0, 0.2),
            parent=self.newWorldScreen,
            scale=0.1,
            text_font=self.font,
            text_scale=0.75,
            initialText="New World " + str(i),
        )

        loadButton = DirectButton(
            text="Create New World",
            command=self.makeWorld,
            pos=(0.5, 0, -0.75),
            parent=self.newWorldScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        backButton = DirectButton(
            text="Back",
            command=self.killNewWorldScreen,
            pos=(-0.5, 0, -0.75),
            parent=self.newWorldScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

    def killNewWorldScreen(self):
        self.newWorldScreen.destroy()
        self.worldOptionsScreen()

    def openWorld(self):
        self.killWorldOptionsScreen()

        worldlist = Fmgr.mgr.returnWorldList()
        remVal = worldlist[0]
        worldlist.remove(remVal)

        self.openWorldScreen = DirectFrame(frameColor=(1, 1, 1, 0))

        num_worlds = 0
        for blank in worldlist:
            num_worlds = num_worlds + 1

        self.worldListDisplay = DirectOptionMenu(
            parent=self.openWorldScreen,
            items=worldlist,
            scale=(0.1, 0.2, 0.2),
            pos=(-0.75, 0, 0.5),
            text_font=self.font,
            text_scale=(0.6, 0.3, 0.3),
            text_pos=(1, 0, 0.5),
            rolloverSound=self.clickSound,
        )

        loadButton = DirectButton(
            text="Open World",
            command=self.loadWorldMGR,
            pos=(0.5, 0, 0),
            parent=self.openWorldScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        delButton = DirectButton(
            text="Delete World",
            command=self.delWorldMGR,
            pos=(-0.5, 0, 0),
            parent=self.openWorldScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        back = DirectButton(
            text="Back",
            command=self.returnToWorldScreenFromLoad,
            pos=(0, 0, -0.5),
            parent=self.openWorldScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        for listMgr in range(num_worlds):
            event = "B" + str(listMgr + 1) + "CLICK"

    def saveSettingChanges(self):
        self.settingsScreen.destroy()
        userPrefFile = panda_fMgr.open("userPref.txt", "wt")
        saveData = [
            Worldvars.difficulty,
            Worldvars.font,
            Worldvars.winMode,
            Worldvars.resolution,
            Worldvars.reachDistance,
            Worldvars.renderDist,
            Worldvars.audioVolume,
        ]
        output = dump(saveData, Dumper=fDumper)
        userPrefFile.writelines(output)
        userPrefFile.close()
        self.settings()

    def saveGSettingChanges(self):
        userPrefFile = panda_fMgr.open("userPref.txt", "wt")
        saveData = [
            Worldvars.difficulty,
            Worldvars.font,
            Worldvars.winMode,
            Worldvars.resolution,
            Worldvars.reachDistance,
            Worldvars.renderDist,
            Worldvars.audioVolume,
        ]
        output = dump(saveData, Dumper=fDumper)
        userPrefFile.writelines(output)
        userPrefFile.close()
        restartGame(self=self)

    def GSettingBack(self):
        self.GraphicsSettingsScreen.destroy()
        # Worldvars.inMenu = False
        self.settings()

    def changeWindowMode(self):
        if Worldvars.winMode == "full-win":
            Worldvars.winMode = "full"
            self.changeWinMode.configure(text="Mode: " + Worldvars.winMode)
        elif Worldvars.winMode == "full":
            Worldvars.winMode = "win"
            self.changeWinMode.configure(text="Mode: " + Worldvars.winMode)
        elif Worldvars.winMode == "win":
            Worldvars.winMode = "full-win"
            self.changeWinMode.configure(text="Mode: " + Worldvars.winMode)

    def changeWindowResolution(self):
        None

    def changeRenderDist(self):
        Worldvars.renderDist = int(self.renderDistance.cget("value"))
        self.renderDistance.configure(
            text="Render Distance: " + str(int(Worldvars.renderDist))
        )

    def changeAudioVolume(self):
        Worldvars.audioVolume = int(self.audioVolume.cget("value"))
        self.audioVolume.configure(
            text="Master Volume: " + str(int(Worldvars.audioVolume))
        )
        self.music.setVolume(Worldvars.audioVolume / 100)

    def settings(self):
        self.killWorldOptionsScreen()
        Worldvars.inMenu = True
        self.settingsScreen = DirectFrame(frameColor=(1, 1, 1, 0))

        self.difficultyOption = DirectButton(
            text="Difficulty: " + Worldvars.difficulty,
            command=self.cycleDifficultyScreen,
            pos=(-0.5, 0, 0.75),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        self.fontOption = DirectButton(
            text="Font: " + Worldvars.font,
            command=self.cycleFont,
            pos=(-0.5, 0, 0.5),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
            textMayChange=1,
        )

        self.renderDistance = DirectSlider(
            text="Render Distance: " + str(Worldvars.renderDist),
            range=(15, 100),
            value=Worldvars.renderDist,
            pos=(0.5, 0, 0.45),
            parent=self.settingsScreen,
            scale=0.4,
            text_font=self.font,
            text_scale=0.2,
            text_pos=(0, 0.15),
            text_fg=(1, 1, 1, 1),
            pageSize=1,
            command=self.changeRenderDist,
        )

        self.audioVolume = DirectSlider(
            text="Master Volume: " + str(Worldvars.audioVolume),
            range=(15, 100),
            value=Worldvars.audioVolume,
            pos=(0.5, 0, 0.2),
            parent=self.settingsScreen,
            scale=0.4,
            text_font=self.font,
            text_scale=0.2,
            text_pos=(0, 0.15),
            text_fg=(1, 1, 1, 1),
            pageSize=1,
            command=self.changeAudioVolume,
        )

        if Worldvars.font == "LiberationMono":
            self.fontOption.configure(text_scale=0.65)
            self.difficultyOption.configure(text_scale=0.65)

        GraphicsOptions = DirectButton(
            text="Graphics Options:",
            command=self.GraphicsOptionsMGR,
            pos=(0.5, 0, 0.75),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        saveChanges = DirectButton(
            text="Save Changes",
            command=self.saveSettingChanges,
            pos=(0.5, 0, -0.75),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        back = DirectButton(
            text="Back",
            command=self.returnToWorldScreen,
            pos=(-0.5, 0, -0.75),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

    def settings2(self):
        Worldvars.inMenu = True
        self.killEscape()
        self.releaseMouse()
        self.settingsScreen = DirectFrame(frameColor=(1, 1, 1, 0))

        self.difficultyOption = DirectButton(
            text="Difficulty: " + Worldvars.difficulty,
            command=self.cycleDifficultyScreen,
            pos=(-0.5, 0, 0.75),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        self.fontOption = DirectButton(
            text="Font: " + Worldvars.font,
            command=self.cycleFont,
            pos=(-0.5, 0, 0.5),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
            textMayChange=1,
        )

        self.renderDistance = DirectSlider(
            text="Render Distance: " + str(Worldvars.renderDist),
            range=(15, 100),
            value=Worldvars.renderDist,
            pos=(0.5, 0, 0.45),
            parent=self.settingsScreen,
            scale=0.4,
            text_font=self.font,
            text_scale=0.2,
            text_pos=(0, 0.15),
            text_fg=(1, 1, 1, 1),
            pageSize=1,
            command=self.changeRenderDist,
        )

        self.audioVolume = DirectSlider(
            text="Master Volume: " + str(Worldvars.audioVolume),
            range=(15, 100),
            value=Worldvars.audioVolume,
            pos=(0.5, 0, 0.2),
            parent=self.settingsScreen,
            scale=0.4,
            text_font=self.font,
            text_scale=0.2,
            text_pos=(0, 0.15),
            text_fg=(1, 1, 1, 1),
            pageSize=1,
            command=self.changeAudioVolume,
        )

        if Worldvars.font == "LiberationMono":
            self.fontOption.configure(text_scale=0.65)
            self.difficultyOption.configure(text_scale=0.65)

        GraphicsOptions = DirectButton(
            text="Graphics Options:",
            command=self.GraphicsOptionsMGR2,
            pos=(0.5, 0, 0.75),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        saveChanges = DirectButton(
            text="Save Changes",
            command=self.saveSettingChanges,
            pos=(0.5, 0, -0.75),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        back = DirectButton(
            text="Back",
            command=self.returnToWorldScreen2,
            pos=(-0.5, 0, -0.75),
            parent=self.settingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

    def returnToWorldScreen(self):
        self.settingsScreen.destroy()
        self.worldOptionsScreen()

    def returnToWorldScreen2(self):
        self.settingsScreen.destroy()
        self.escape()

    def GraphicsOptionsMGR(self):
        self.settingsScreen.destroy()
        self.GraphicsSettingsScreen = DirectFrame(frameColor=(1, 1, 1, 0))
        self.changeWinMode = DirectButton(
            text="Mode: " + Worldvars.winMode,
            command=self.changeWindowMode,
            pos=(-0.5, 0, 0.75),
            parent=self.GraphicsSettingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        self.changeRes = DirectButton(
            text="Resolution: " + str(Worldvars.resolution),
            command=self.changeWindowResolution,
            pos=(-0.5, 0, 0.5),
            parent=self.GraphicsSettingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
            textMayChange=1,
        )

        saveGChanges = DirectButton(
            text="Save Changes",
            command=self.saveGSettingChanges,
            pos=(0.5, 0, -0.75),
            parent=self.GraphicsSettingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        Gback = DirectButton(
            text="Back",
            command=self.GSettingBack,
            pos=(-0.5, 0, -0.75),
            parent=self.GraphicsSettingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

    def GraphicsOptionsMGR2(self):
        Worldvars.inMenu = True
        self.settingsScreen.destroy()

        self.GraphicsSettingsScreen = DirectFrame(frameColor=(1, 1, 1, 0))

        self.changeWinMode = DirectButton(
            text="Mode: " + Worldvars.winMode,
            command=self.changeWindowMode,
            pos=(-0.5, 0, 0.75),
            parent=self.GraphicsSettingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        self.changeRes = DirectButton(
            text="Resolution: " + str(Worldvars.resolution),
            command=self.changeWindowResolution,
            pos=(-0.5, 0, 0.5),
            parent=self.GraphicsSettingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
            textMayChange=1,
        )

        saveGChanges = DirectButton(
            text="Save Changes",
            command=self.saveGSettingChanges,
            pos=(0.5, 0, -0.75),
            parent=self.GraphicsSettingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        Gback = DirectButton(
            text="Back",
            command=self.GSettingBack,
            pos=(-0.5, 0, -0.75),
            parent=self.GraphicsSettingsScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

    def cycleDifficultyScreen(self):
        self.releaseMouse()
        if Worldvars.difficulty == "Normal":
            Worldvars.difficulty = "Hard"
        elif Worldvars.difficulty == "Hard":
            Worldvars.difficulty = "Peaceful"
        elif Worldvars.difficulty == "Peaceful":
            Worldvars.difficulty = "Easy"
        elif Worldvars.difficulty == "Easy":
            Worldvars.difficulty = "Normal"

        self.difficultyOption.configure(text="Difficulty: " + Worldvars.difficulty)

    def cycleFont(self):
        self.releaseMouse()
        if Worldvars.font == "Minecraft":
            Worldvars.font = "Sans"
        elif Worldvars.font == "Sans":
            Worldvars.font = "LiberationMono"
        elif Worldvars.font == "LiberationMono":
            Worldvars.font = "Minecraft"

        self.fontOption.configure(text="Font: " + Worldvars.font)
        self.font = self.loader.load_font("PyCraft/src/" + Worldvars.font + ".ttf")
        self.settingsScreen.destroy()

        self.settings()

    def killWorldOptionsScreen(self):

        self.worldOptions.destroy()

    def loadWorldMGR(self):
        self.worldnameFile = self.worldListDisplay.get()
        self.openWorldScreen.destroy()

        self.loadWorld(name=self.worldnameFile)

    def returnToWorldScreenFromLoad(self):
        self.openWorldScreen.destroy()

        self.worldOptionsScreen()

    def delWorldMGR(self):
        self.worldnameFile = self.worldListDisplay.get()
        Fmgr.mgr.deleteWorld(name=self.worldnameFile)
        self.openWorldScreen.destroy()

        self.worldOptionsScreen()

    def loadWorld(self, name):
        worldARR = Fmgr.mgr.readWorldFile(name)
        self.launch()
        worldBlockArr = Parser.get.decodeFile(self=Fmgr.mgr, fileARR=worldARR)
        i = 0
        for blank in worldBlockArr:
            self.createNewBlock(
                x=(worldBlockArr[i][0]),
                y=(worldBlockArr[i][1]),
                z=(worldBlockArr[i][2]),
                type=worldBlockArr[i][3],
            )
            i = i + 1
        self.camera.setPos(Worldvars.camX, Worldvars.camY, Worldvars.camZ)
        self.camera.setHpr(Worldvars.camH, Worldvars.camP, Worldvars.camR)

    def loadNewWorld(self, name):
        self.worldnameFile = Fmgr.mgr.folderPath + self.worldname.get() + ".dat\n"
        self.newWorldScreen.destroy()
        self.launch()
        self.generateTerrain()

    def saveWorld(self):
        Worldvars.saving = True
        array = Parser.saveWorld.worldToText(
            Parser.saveWorld, worldARR=Worldvars.allBlocks
        )
        Fmgr.openWorldFile.saveWorld(
            Fmgr.openWorldFile, worldARR=array, name=self.worldnameFile
        )
        Worldvars.saving = False

    def worldOptionsScreen(self):
        Fmgr.mgr.start()
        worldlist = Fmgr.mgr.returnWorldList()

        self.killMenu()

        self.worldOptions = DirectFrame(frameColor=(1, 1, 1, 0))

        btn = DirectButton(
            text="New world",
            command=self.newWorld,
            pos=(0.5, 0, 0.25),
            parent=self.worldOptions,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        btn = DirectButton(
            text="Open World",
            command=self.openWorld,
            pos=(-0.5, 0, 0.25),
            parent=self.worldOptions,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        btn = DirectButton(
            text="Settings",
            command=self.settings,
            pos=(0.5, 0, -0.5),
            parent=self.worldOptions,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )

        backButton = DirectButton(
            text="Back",
            command=self.optionsToMenu,
            pos=(-0.5, 0, -0.5),
            parent=self.worldOptions,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )
        btn.setTransparency(True)

    def optionsToMenu(self):
        self.killWorldOptionsScreen()
        self.menu()

    def killMenu(self):
        self.titleMenu.destroy()

    def launch(self):
        Worldvars.inMenu = False
        self.blockRenderNode = self.render.attachNewNode("blockRenderNode")
        self.itemRenderNode = self.render.attachNewNode("itemRenderNode")
        self.setupSkybox()
        self.captureMouse()
        self.setupCamera()
        self.setupControls()
        Ui.bar.buildHotbar(
            self=Ui.bar,
            main=self,
            textureAlias=Texture.FTNearest,
            Sprites=self.sprites,
            font=self.font,
            TextNode=TextNode,
            aspect2d=self.aspect2d,
        )
        thread.Thread(
            target=self.renderBlocks, name="renderBlocks", daemon=True
        ).start()
        self.taskMgr.add(self.selectBlockOverlay, "blockSelectorOverlay")
        self.menuBackground.hide()
        self.render.prepareScene(self.win.getGsg())

    def killGameEndScreen(self):
        Worldvars.hp = 10
        self.gameOverScreen.destroy()
        self.menu()

    def menu(self):
        self.mouseHidden = False
        Worldvars.inMenu = True
        self.titleMenu = DirectFrame(frameColor=(1, 1, 1, 0))
        title = DirectLabel(
            text="Minecraft",
            scale=0.125,
            pos=(0, 0, 0.75),
            parent=self.titleMenu,
            relief=None,
            text_font=self.font,
            text_fg=(1, 1, 1, 1),
        )
        title2 = DirectLabel(
            text="recreated in python by",
            scale=0.07,
            pos=(0, 0, 0.6),
            parent=self.titleMenu,
            relief=None,
            text_font=self.font,
            text_fg=(1, 1, 1, 1),
        )
        title3 = DirectLabel(
            text="MaybeBroken",
            scale=0.1,
            pos=(0, 0, 0.45),
            parent=self.titleMenu,
            relief=None,
            text_font=self.font,
            text_fg=(1, 1, 1, 1),
        )

        btn = DirectButton(
            text="Start Game",
            command=self.worldOptionsScreen,
            pos=(0, 0, 0.2),
            parent=self.titleMenu,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )
        btn.setTransparency(True)

        btn = DirectButton(
            text="Quit",
            command=exit,
            pos=(0, 0, -0.2),
            parent=self.titleMenu,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )
        btn.setTransparency(True)

    def death(self):
        self.releaseMouse()
        t.sleep(1)
        self.gameOverScreen = DirectDialog(
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameTexture="PyCraft/src/Dirt.jpg",
        )
        label = DirectLabel(
            text="Game Over!",
            parent=self.gameOverScreen,
            scale=0.1,
            pos=(0, 0, 0.2),
            text_font=self.font,
        )
        self.finalScoreLabel = DirectLabel(
            text="You Died",
            parent=self.gameOverScreen,
            scale=0.15,
            pos=(0, 0, 0),
            text_font=self.font,
        )

        btn = DirectButton(
            text="Main Menu",
            command=restartGame,
            extraArgs=[self],
            pos=(-0.3, 0, -0.2),
            parent=self.gameOverScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )
        btn.setTransparency(True)

        btn = DirectButton(
            text="Quit",
            command=self.quit,
            pos=(0.3, 0, -0.2),
            parent=self.gameOverScreen,
            scale=0.12,
            text_font=self.font,
            clickSound=self.clickSound,
            frameTexture=self.buttonImages,
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            text_scale=0.65,
            relief=DGG.FLAT,
            text_pos=(0, -0.2),
        )
        btn.setTransparency(True)
        self.gameOverScreen.show()
        self.releaseMouse()

    def killEscape(self):
        self.escapeScreen.destroy()
        Worldvars.inMenu = False
        self.captureMouse()

    def killEscapeMenu(self):
        self.escapeScreen.destroy()
        exit("Code Not Finished:/")

    def escape(self):
        if Worldvars.hp > 0 and not Worldvars.inMenu:
            self.releaseMouse()
            Worldvars.inMenu = True
            self.escapeScreen = DirectFrame(frameSize=(0, 0, 0, 0))

            label = DirectLabel(
                text="Game Paused:",
                parent=self.escapeScreen,
                scale=0.1,
                pos=(0, 0, 0.5),
                text_font=self.font,
            )

            btn = DirectButton(
                text="Resume",
                command=self.killEscape,
                pos=(0, 0, 0.3),
                parent=self.escapeScreen,
                scale=0.12,
                text_font=self.font,
                clickSound=self.clickSound,
                frameTexture=self.buttonImages,
                frameSize=(-3.5, 3.5, -0.5, 0.5),
                text_scale=0.65,
                relief=DGG.FLAT,
                text_pos=(0, -0.2),
            )
            btn.setTransparency(True)

            btn = DirectButton(
                text="Settings",
                command=self.settings2,
                pos=(0, 0, 0.1),
                parent=self.escapeScreen,
                scale=0.12,
                text_font=self.font,
                clickSound=self.clickSound,
                frameTexture=self.buttonImages,
                frameSize=(-3.5, 3.5, -0.5, 0.5),
                text_scale=0.65,
                relief=DGG.FLAT,
                text_pos=(0, -0.2),
            )

            btn.setTransparency(True)

            btn = DirectButton(
                text="Main Menu",
                command=self.killEscapeMenu,
                extraArgs=[self],
                pos=(0, 0, -0.1),
                parent=self.escapeScreen,
                scale=0.12,
                text_font=self.font,
                clickSound=self.clickSound,
                frameTexture=self.buttonImages,
                frameSize=(-3.5, 3.5, -0.5, 0.5),
                text_scale=0.65,
                relief=DGG.FLAT,
                text_pos=(0, -0.2),
            )
            btn.setTransparency(True)

            btn = DirectButton(
                text="Quit",
                command=self.quit,
                pos=(0, 0, -0.5),
                parent=self.escapeScreen,
                scale=0.12,
                text_font=self.font,
                clickSound=self.clickSound,
                frameTexture=self.buttonImages,
                frameSize=(-3.5, 3.5, -0.5, 0.5),
                text_scale=0.65,
                relief=DGG.FLAT,
                text_pos=(0, -0.2),
            )

            btn = DirectButton(
                text="Save World",
                command=self.saveWorld,
                pos=(0, 0, -0.3),
                parent=self.escapeScreen,
                scale=0.12,
                text_font=self.font,
                clickSound=self.clickSound,
                frameTexture=self.buttonImages,
                frameSize=(-3.5, 3.5, -0.5, 0.5),
                text_scale=0.65,
                relief=DGG.FLAT,
                text_pos=(0, -0.2),
            )
            btn.setTransparency(True)
            self.escapeScreen.show()

    def update(self, task):
        result = task.cont
        self.moveLightToCam()
        if Worldvars.inMenu == True:
            if Worldvars.inInventory == False:
                self.menuBackground.setH(self.menuBackground.getH() + 0.03)
        elif Worldvars.inInventory == False and not Worldvars.inMenu:
            thread.Thread(target=self.updateItemsWorld, name="updateItemsWorld").start()

            playerMoveSpeed = Worldvars.speed / 10

            x_movement = 0
            y_movement = 0
            z_movement = 0

            dt = globalClock.getDt()  # type: ignore
            Ui.bar.updateHotbar(Ui.bar)
            self.selectedBlockType = Worldvars.selectedBlock
            self.skybox.setX(self.camera.getX())
            self.skybox.setY(self.camera.getY())
            self.skybox.setZ(self.camera.getZ() - 10)

            if Worldvars.hp <= 0:
                self.releaseMouse()
                self.death()
                result = None
            else:

                if self.keyMap["forward"]:
                    x_movement -= (
                        dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
                    )
                    y_movement += (
                        dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
                    )
                if self.keyMap["backward"]:
                    x_movement += (
                        dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
                    )
                    y_movement -= (
                        dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
                    )
                if self.keyMap["left"]:
                    x_movement -= (
                        dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
                    )
                    y_movement -= (
                        dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
                    )
                if self.keyMap["right"]:
                    x_movement += (
                        dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
                    )
                    y_movement += (
                        dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
                    )
                if self.keyMap["up"]:
                    z_movement += dt * playerMoveSpeed
                if self.keyMap["down"]:
                    z_movement -= dt * playerMoveSpeed

                self.camera.setPos(
                    self.camera.getX() + x_movement,
                    self.camera.getY() + y_movement,
                    self.camera.getZ() + z_movement,
                )
                Worldvars.camX = self.camera.getX()
                Worldvars.camY = self.camera.getY()
                Worldvars.camZ = self.camera.getZ()

                md = self.win.getPointer(0)
                mouseX = md.getX()
                mouseY = md.getY()
                if self.mouseHidden:

                    if int(monitor[0].width / 2) - mouseX >= int(monitor[0].width / 4):
                        self.win.movePointer(
                            0, x=int(monitor[0].width / 2), y=int(mouseY)
                        )
                        self.lastMouseX = int(monitor[0].width / 2)
                    elif int(monitor[0].width / 2) - mouseX <= -int(
                        monitor[0].width / 4
                    ):
                        self.win.movePointer(
                            0, x=int(monitor[0].width / 2), y=int(mouseY)
                        )
                        self.lastMouseX = int(monitor[0].width / 2)
                    elif int(monitor[0].height / 2) - mouseY >= int(
                        monitor[0].height / 4
                    ):
                        self.win.movePointer(
                            0, x=int(mouseX), y=int(monitor[0].height / 2)
                        )
                        self.lastMouseY = int(monitor[0].height / 2)
                    elif int(monitor[0].height / 2) - mouseY <= -int(
                        monitor[0].height / 4
                    ):
                        self.win.movePointer(
                            0, x=int(mouseX), y=int(monitor[0].height / 2)
                        )
                        self.lastMouseY = int(monitor[0].height / 2)

                    elif self.cameraSwingActivated:

                        mouseChangeX = mouseX - self.lastMouseX
                        mouseChangeY = mouseY - self.lastMouseY

                        self.cameraSwingFactor = Worldvars.swingSpeed / 10

                        currentH = self.camera.getH()
                        currentP = self.camera.getP()
                        currentR = self.camera.getR()

                        Worldvars.camH = currentH
                        Worldvars.camP = currentP
                        Worldvars.camR = currentR

                        self.camera.setHpr(
                            currentH - mouseChangeX * dt * self.cameraSwingFactor,
                            min(
                                90,
                                max(
                                    -90,
                                    currentP
                                    - mouseChangeY * dt * self.cameraSwingFactor,
                                ),
                            ),
                            0,
                        )

                        self.lastMouseX = mouseX
                        self.lastMouseY = mouseY
        if Worldvars.inInventory == True:
            md = self.win.getPointer(0)
            self.lastMouseX = md.getX()
            self.lastMouseY = md.getY()

        return result

    def doEscape(self):
        if Worldvars.inMenu != True and self.mouseHidden:
            self.escape()

    def setupControls(self):
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

        self.accept("escape", self.doEscape)
        self.accept("mouse1", self.handleLeftClick, ["primary", True])
        self.accept("mouse1-up", self.handleLeftClick, ["primary", False])
        self.accept("mouse3", self.placeBlock)

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

        self.accept("e", self.toggleInventory)
        self.accept("t", self.moveLightToCam)

        self.accept("wheel_up", self.selectorUp)
        self.accept("wheel_down", self.selectorDown)

        self.accept("o", self.wireframeOn)
        self.accept("o-up", self.wireframeOff)

    def handleLeftClick(self, key, value):
        if Worldvars.inInventory == False and self.mouseHidden:
            self.updateKeyMap(key=key, value=value)
            if self.keyMap["primary"]:
                self.captureMouse()
                self.removeBlock()
                Worldvars.hp = Worldvars.hp - 1

    def toggleInventory(self):
        if (
            Worldvars.inInventory == False
            and Worldvars.inMenu != True
            and self.mouseHidden
        ):
            self.openInventory()
        elif Worldvars.inInventory == True:
            self.closeInventory()

    def openInventory(self):
        Ui.HUD.drawInventoryFrames(
            self=Ui.HUD,
            mainApp=self,
            textureAlias=Texture.FTNearest,
            GeomSprites=self.GeomSprites,
            font=self.font,
            TextNode=TextNode,
            aspect2d=self.aspect2d,
        )
        Worldvars.inInventory = True

    def closeInventory(self):
        Ui.HUD.closeInventoryFrames(self=Ui.HUD)
        Worldvars.inInventory = False

    def removeBlock(self):
        try:
            if self.rayQueue.getNumEntries() > 1 and Worldvars.inMenu != True:
                self.rayQueue.sortEntries()
                rayHit = self.rayQueue.getEntry(1)

                hitNodePath = rayHit.getIntoNodePath()
                hitObject = hitNodePath.getPythonTag("owner")
                distanceFromPlayer = hitObject.getDistance(self.camera)

                if distanceFromPlayer <= Worldvars.reachDistance:

                    hitObjectName = str(hitObject)
                    hitObjectName = hitObjectName.replace("render/blockRenderNode/", "")
                    hitObjectName = list(hitObjectName)
                    hitObjectName.remove("[")
                    hitObjectName.remove("]")
                    hitObjectName.remove(",")
                    hitObjectName.remove(",")
                    hitObjectName.remove(",")
                    hitObjectName.remove("'")
                    hitObjectName.remove("'")
                    hitObjectName = "".join(hitObjectName)
                    hitObjectName = list(hitObjectName.split(" "))
                    hitObjectName[0] = int(hitObjectName[0])
                    hitObjectName[1] = int(hitObjectName[1])
                    hitObjectName[2] = int(hitObjectName[2])
                    thread.Thread(
                        target=self.removeBlockAnimation,
                        args=[hitObject, hitObjectName, hitNodePath],
                        daemon=True,
                    ).start()
        except:
            None

    def removeBlockAnimation(self, hitObject, hitObjectName, hitNodePath):
        for i in range(
            round(
                Worldvars.kinds_of_blocks[utils.item_to_int(hitObjectName[3])][1] * 1000
            )
        ):
            if self.keyMap["primary"]:
                t.sleep(0.001)
            else:
                t.sleep(0.1)
                break
        if self.keyMap["primary"]:
            if list(hitObjectName) in Worldvars.allBlocks:
                Worldvars.allBlocks.remove(hitObjectName)
            self.createNewdroppedItem(
                hitObjectName[0], hitObjectName[1], hitObjectName[2], hitObjectName[3]
            )
            hitNodePath.clearPythonTag("owner")
            hitObject.removeNode()

    def placeBlock(self):
        try:
            if self.rayQueue.getNumEntries() > 1 and Worldvars.inMenu != True:
                self.rayQueue.sortEntries()
                rayHit = self.rayQueue.getEntry(1)
                hitNodePath = rayHit.getIntoNodePath()
                normal = rayHit.getSurfaceNormal(hitNodePath)
                hitObject = hitNodePath.getPythonTag("owner")
                distanceFromPlayer = hitObject.getDistance(self.camera)
                if Ui.Inventory.removeOneItem_hotbar(Ui.Inventory) == True:
                    if distanceFromPlayer <= Worldvars.reachDistance:
                        hitBlockPos = hitObject.getPos()
                        newBlockPos = hitBlockPos + normal * 2
                        self.createNewBlock(
                            int(newBlockPos.x),
                            int(newBlockPos.y),
                            int(newBlockPos.z),
                            self.selectedBlockType,
                        )
        except:
            None

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def captureMouse(self):
        if Worldvars.inMenu != True:
            self.cameraSwingActivated = True
            md = self.win.getPointer(0)
            self.lastMouseX = md.getX()
            self.lastMouseY = md.getY()
            properties = WindowProperties()
            properties.setCursorHidden(True)
            properties.setMouseMode(WindowProperties.M_relative)
            self.win.requestProperties(properties)
            self.mouseHidden = True

    def releaseMouse(self):
        self.mouseHidden = False
        self.cameraSwingActivated = False
        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(properties)

    def setupCamera(self):
        self.camera.setPos(Worldvars.camX, Worldvars.camY, Worldvars.camZ)
        self.camLens.setFov(Worldvars.camFOV)
        self.camera.setHpr(Worldvars.camH, Worldvars.camP, Worldvars.camR)

        self.crosshairs = OnscreenImage(
            image="PyCraft/src/crosshairs.png",
            pos=(0, 0, 0),
            scale=0.04,
        )
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)

        self.backface_culling_on()

        self.cTrav = CollisionTraverser()
        self.ray = CollisionRay()
        self.ray.setFromLens(self.camNode, (0, 0))
        self.rayNode = CollisionNode("line-of-sight")
        self.rayNode.addSolid(self.ray)
        self.rayNode.set_into_collide_mask(0)
        self.rayNode.set_into_collide_mask(1)
        self.rayNodePath = self.camera.attachNewNode(self.rayNode)
        self.rayQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(self.rayNodePath, self.rayQueue)

        fromObject = self.camera.attachNewNode(CollisionNode("colNode"))
        fromObject.node().addSolid(CollisionBox((-1, -1, -1), (1, 1, 1)))
        fromObject.node().set_from_collide_mask(1)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, self.camera, self.drive.node())
        self.cTrav.addCollider(fromObject, pusher)

        Ui.ShaderCall.setupShaders(
            self=Ui.ShaderCall, mainApp=self, light=self.SceneLightNode
        )

        self.selectorNode = self.render.attachNewNode("Block Selector")
        self.selector.instanceTo(self.selectorNode)
        self.selector.setLightOff()
        self.selectorNode.setScale(0.01)
        self.selectorNode.setPos(0, 0, 0)

    def moveLightToCam(self):
        if Worldvars.inMenu != True:
            self.SceneLightNode.setPos(self.camera.getPos())
            self.SceneLightNode.setHpr(self.camera.getHpr())

    def setupSkybox(self):
        self.skybox = self.loader.loadModel("PyCraft/skybox/skybox/skybox.egg")
        self.skybox.setScale(0.5)
        self.skybox.setBin("background", 1)
        self.skybox.setDepthWrite(0)
        self.skybox.setLightOff()
        self.skybox.reparentTo(self.render)

    def generateTerrain(self):
        camPosX = int(self.camera.getX())
        camPosY = int(self.camera.getY())
        for index1 in range(
            round(camPosX - (Worldvars.renderDist / 2)),
            round(camPosX + (Worldvars.renderDist / 2)),
        ):
            for index2 in range(
                round(camPosY - (Worldvars.renderDist / 2)),
                round(camPosY + (Worldvars.renderDist / 2)),
            ):
                for index3 in range(Worldvars.worldz):
                    index3 = gen.terrainGen.makeNoiseMap(
                        gen.terrainGen,
                        index1 / Worldvars.dens,
                        index2 / Worldvars.dens,
                        index3 / Worldvars.dens,
                        Worldvars.seed,
                    )
                    if index1 == camPosX and index2 == camPosY:
                        self.camera.setPos(camPosX, camPosY, index3 * 2 + 1)
                    if any(
                        item
                        == [index1, index2, index3, (I[0] for I in Worldvars.allItems)]
                        for item in Worldvars.allBlocks
                    ):
                        None
                    else:
                        self.createNewBlock(index1 * 2, index2 * 2, index3 * 2, "stone")

    def createNewBlock(self, x, y, z, type):
        BlockNode = self.render.attachNewNode(str([x, y, z, type]))
        BlockNode.reparentTo(self.blockRenderNode)
        BlockNode.setPos(x, y, z)
        node = utils.item_to_nodePath(item=type, MainApp=self)
        if node == self.glowBlock or node == self.glassBlock:
            node.setDepthOffset(-1)
        node.instanceTo(BlockNode)

        blockSolid = CollisionBox((-1, -1, -1), (1, 1, 1))
        blockNode = CollisionNode("block-collision-node")
        blockNode.addSolid(blockSolid)

        collider = BlockNode.attachNewNode(blockNode)
        collider.setPythonTag("owner", BlockNode)

        fromObject = BlockNode.attachNewNode(CollisionNode("colNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 1))
        fromObject.node().set_from_collide_mask(0)
        fromObject.node().setPythonTag("owner", BlockNode)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, BlockNode)
        self.cTrav.addCollider(fromObject, pusher)

        BlockNode.clearColor()

        blockList = [x, y, z, type]
        Worldvars.allBlocks.append(blockList)

    def createNewdroppedItem(self, x, y, z, type):
        itemNode = self.render.attachNewNode(str([x, y, z, type]))
        itemNode.reparentTo(self.itemRenderNode)
        itemNode.setPos(x, y, z - 0.5)
        itemNode.setScale(0.25)
        node = utils.item_to_nodePath(item=type, MainApp=self)
        node.instanceTo(itemNode)

        blockSolid = CollisionBox((-1, -1, -1), (1, 1, 1))
        blockNode = CollisionNode("item-collision-node")
        blockNode.addSolid(blockSolid)

        collider = itemNode.attachNewNode(blockNode)
        collider.setPythonTag("owner", itemNode)

        fromObject = itemNode.attachNewNode(CollisionNode("colNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 1))
        fromObject.node().set_from_collide_mask(0)
        fromObject.node().setPythonTag("owner", itemNode)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, itemNode)
        self.cTrav.addCollider(fromObject, pusher)

        itemNode.clearColor()

        blockList = [x, y, z, type]
        Worldvars.allItems.append(blockList)

    def loadModels(self):
        for root, dirs, files in os.walk("PyCraft/src/models/"):
            for name in files:
                if name.endswith((".egg")):
                    file_name = os.path.basename(name)
                    file_no_extension = os.path.splitext(file_name)[0]
                    self.__setattr__(
                        file_no_extension + "Block",
                        self.loader.loadModel(
                            "PyCraft/src/models/" + file_no_extension + "/" + name
                        ),
                    )
        self.menuBackground = self.loader.loadModel("PyCraft/skybox/menu/skybox.egg")
        self.selector = self.loader.loadModel("PyCraft/src/selector.fbx")

        self.menuBackground.setScale(500)
        self.menuBackground.setBin("background", 1)
        self.menuBackground.setDepthWrite(0)
        self.menuBackground.setLightOff()
        self.menuBackground.reparentTo(self.render)
        self.camLens.setFov(Worldvars.camFOV)

        self.buttonImages = (
            self.loader.loadTexture("PyCraft/src/UI/HUD/button.png"),
            self.loader.loadTexture("PyCraft/src/UI/UIButtonPressed.png"),
            self.loader.loadTexture("PyCraft/src/UI/HUD/button_highlighted.png"),
            self.loader.loadTexture("PyCraft/src/UI/UIButtonDisabled.png"),
        )
        self.sprites = (
            self.loader.loadTexture("PyCraft/src/models/dirt/t_up.png"),
            self.loader.loadTexture("PyCraft/src/textures/grass_block.png"),
            self.loader.loadTexture("PyCraft/src/models/sand/t_up.png"),
            self.loader.loadTexture("PyCraft/src/models/stone/t_up.png"),
            self.loader.loadTexture("PyCraft/src/models/ancient_debris/t_north.png"),
            self.loader.loadTexture("PyCraft/src/models/glass/t_all.png"),
            self.loader.loadTexture("PyCraft/src/models/glow/t_all.png"),
        )
        self.GeomSprites = (
            self.dirtBlock,
            self.grassBlock,
            self.sandBlock,
            self.stoneBlock,
            self.ancient_debrisBlock,
            self.glassBlock,
            self.glowBlock,
        )
        for tex in self.buttonImages:
            tex.setMinfilter(Texture.FTNearest)
            tex.setMagfilter(Texture.FTNearest)
        for tex in self.sprites:
            tex.setMinfilter(Texture.FTNearest)
            tex.setMagfilter(Texture.FTNearest)

        self.clickSound = self.loader.loadSfx("PyCraft/src/UI/Sounds/Click1.wav")

        print("Loading models/textures complete")

    def setupLights(self):

        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((0.1, 0.1, 0.1, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)

        spotLight = PointLight("pLight")
        spotLight.setColor((1, 1, 1, 0.5))
        spotLight.setShadowCaster(True)
        spotLight.setColorTemperature(4500)

        self.SceneLightNode = self.render.attachNewNode(spotLight)
        self.SceneLightNode.setPos(self.camera.getPos())
        self.SceneLightNode.setHpr(self.camera.getHpr())
        self.render.setLight(self.SceneLightNode)

        print("Lighting complete")

    def quit(self):
        self.saveWorld()
        sys.exit()

    def renderBlocks(self):
        while True:
            # t.sleep(1)
            for node in self.blockRenderNode.getChildren():
                # get all nodes within render distance
                if node.getDistance(self.camera) <= Worldvars.renderDist:
                    node.show()
                else:
                    # hide nodes out of render distance
                    node.hide()
            # camPosX = int(self.camera.getX())
            # camPosY = int(self.camera.getY())
            # for index1 in range(
            #     round(camPosX - (Worldvars.renderDist / 2)),
            #     round(camPosX + (Worldvars.renderDist / 2)),
            # ):
            #     for index2 in range(
            #         round(camPosY - (Worldvars.renderDist / 2)),
            #         round(camPosY + (Worldvars.renderDist / 2)),
            #     ):
            #         index3 = gen.terrainGen.makeNoiseMap(
            #             gen.terrainGen,
            #             index1 / Worldvars.dens,
            #             index2 / Worldvars.dens,
            #             Worldvars.dens,
            #             Worldvars.seed,
            #         )
            #         for blockType in utils.items:
            #             if [
            #                 index1,
            #                 index2,
            #                 index3,
            #                 blockType,
            #             ] in Worldvars.allBlocks:
            #                 self.createNewBlock(
            #                     index1 * 2, index2 * 2, index3 * 2, "stone"
            #                 )

    def selectBlockOverlay(self, task):
        t.sleep(0.01)
        try:
            if self.rayQueue.getNumEntries() > 1:
                self.rayQueue.sortEntries()
                rayHit = self.rayQueue.getEntry(1)
                hitNodePath = rayHit.getIntoNodePath()
                hitObject = hitNodePath.getPythonTag("owner")
                distanceFromPlayer = hitObject.getDistance(self.camera)
                if distanceFromPlayer <= Worldvars.reachDistance:
                    self.selectorNode.setPos(hitObject.getPos())
                    self.selectorNode.setScale(hitObject.getScale() / 100)
                    self.selectorNode.setHpr(hitObject.getHpr())
                    self.selectorNode.show()
                else:
                    self.selectorNode.hide()
            else:
                self.selectorNode.hide()
        except:
            None
        return task.cont

    def updateItemsWorld(self):
        try:
            for node in self.itemRenderNode.getChildren():
                node.setH(node.getH() + 1)
                if node.getDistance(self.camera) <= 4:
                    hitObjectName = str(node)
                    hitObjectName = hitObjectName.replace("render/itemRenderNode/", "")
                    hitObjectName = list(hitObjectName)
                    hitObjectName.remove("[")
                    hitObjectName.remove("]")
                    hitObjectName.remove(",")
                    hitObjectName.remove(",")
                    hitObjectName.remove(",")
                    hitObjectName.remove("'")
                    hitObjectName.remove("'")
                    hitObjectName = "".join(hitObjectName)
                    hitObjectName = list(hitObjectName.split(" "))
                    hitObjectName[0] = int(hitObjectName[0])
                    hitObjectName[1] = int(hitObjectName[1])
                    hitObjectName[2] = int(hitObjectName[2])
                    if (
                        Ui.Inventory.addItem(
                            self=Ui.Inventory, item=hitObjectName[3], amount=1
                        )
                        == True
                    ):
                        node.removeNode()
        except:
            None


def restartGame(self):
    try:
        self.saveWorld()
    except:
        None
    self.finalizeExit = False
    Worldvars.relaunching == True
    ShowBase.destroy(self)


print("Minecraft in python...?")

game = Main()
