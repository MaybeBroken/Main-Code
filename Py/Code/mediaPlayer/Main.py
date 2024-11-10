from math import pi, sin, cos
from random import randint
import time as t
import sys
import os
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
from direct.stdpy.threading import Thread
import direct.stdpy.file as panda_fMgr
from direct.gui.DirectGui import *
import direct.particles.Particles as part
from direct.filter.CommonFilters import CommonFilters

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


wantIntro = False


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        if wantIntro:
            self.intro()
        else:
            self.setBackgroundColor(0, 0, 0, 1)
            self.backfaceCullingOn()
            self.disableMouse()

            # do setup tasks
            # ...
            self.setupWorld()
            self.setupControls()
            Thread(target=self.update, daemon=True).start()

    def intro(self):
        self.setBackgroundColor(0, 0, 0, 1)
        movie = self.loader.loadTexture("src/movies/intro.mp4")
        image = OnscreenImage(movie, scale=1, parent=self.aspect2d)
        movie.play()
        movie.setLoopCount(1)
        startTime = t.monotonic()

        def finishLaunch(task):
            if t.monotonic() - startTime > 4:
                image.destroy()
                self.backfaceCullingOn()
                self.disableMouse()

                # do setup tasks
                # ...
                self.setupWorld()
                self.setupControls()
                # end of setup tasks
            else:
                return task.cont

        self.taskMgr.add(finishLaunch)

    def update(self):
        while True:
            t.sleep(0.25)
            try:
                if (
                    self.songList[self.songIndex]["object"].status() == 1
                    and self.songList[self.songIndex]["played"] == 0
                ):
                    self.songList[self.songIndex]["played"] = 1
                    self.songList[self.songIndex]["nodePath"]["frameColor"] = (
                        0,
                        0.6,
                        0.3,
                        1,
                    )
                    self.songList[self.songIndex]["object"].play()
                elif (
                    self.songList[self.songIndex]["object"].status() == 1
                    and self.songList[self.songIndex]["played"] == 1
                ):

                    self.songList[self.songIndex]["played"] = 0
                    self.nextSong()
                self.progressText.setText(
                    str(int(self.songList[self.songIndex]["object"].get_time()))
                    + " / "
                    + str(int(self.songList[self.songIndex]["object"].length()))
                )
            except:
                None

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
        self.accept("wheel_up", self.doNothing)
        self.accept("wheel_down", self.doNothing)
        self.accept("q", sys.exit)
        # self.accept("arrow_up", self.updateValues, [True])
        # self.accept("arrow_down", self.updateValues, [False, True])
        self.accept("arrow_left", self.prevSong)
        self.accept("arrow_right", self.nextSong)

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def doNothing(self):
        return None

    def nextSong(self):
        if self.songIndex - 1 >= 0:
            self.songList[self.songIndex - 1]["nodePath"].setPos(10)
        self.songList[self.songIndex]["nodePath"].setPos(0, self.songIndex, 0.5)
        self.songList[self.songIndex]["nodePath"].setScale(0.8)
        self.songList[self.songIndex]["object"].stop()
        self.songList[self.songIndex]["nodePath"]["frameColor"] = (0, 0, 0.6, 1)
        self.songIndex += 1
        self.songList[self.songIndex]["nodePath"].show()
        self.songList[self.songIndex]["nodePath"].setPos(0, self.songIndex, 0)
        self.songList[self.songIndex]["nodePath"].setScale(1)
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["played"] = 1
        self.songList[self.songIndex]["nodePath"]["frameColor"] = (0, 0.6, 0.3, 1)

    def prevSong(self):
        if self.songIndex - 2 >= 0:
            self.songList[self.songIndex - 2]["nodePath"].setPos(0, 0, 0.5)
        self.songList[self.songIndex]["nodePath"].setPos(0, self.songIndex, -0.5)
        self.songList[self.songIndex]["nodePath"].setScale(0.8)
        self.songList[self.songIndex]["object"].stop()
        self.songList[self.songIndex]["nodePath"]["frameColor"] = (0, 0, 0.6, 1)
        self.songIndex -= 1
        self.songList[self.songIndex]["nodePath"].show()
        self.songList[self.songIndex]["nodePath"].setPos(0, self.songIndex, 0)
        self.songList[self.songIndex]["nodePath"].setScale(1)
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["played"] = 1
        self.songList[self.songIndex]["nodePath"]["frameColor"] = (0, 0.6, 0.3, 1)

    def setupWorld(self):

        # Vars

        self.songList = []
        self.songIndex = 0

        # Shaders

        filters = CommonFilters(self.win, self.cam)
        filters.setBloom(
            blend=(0.3, 0.4, 0.3, 0.8),
            mintrigger=0.1,
            maxtrigger=1,
            desat=0.1,
            intensity=1,
            size="medium",
        )
        # filters.setAmbientOcclusion()
        filters.setSrgbEncode()
        filters.setHighDynamicRange()
        filters.setBlurSharpen(0.5)

        # GUI

        self.guiFrame = DirectFrame(parent=self.aspect2d)
        self.pathObject = DirectEntry(
            parent=self.guiFrame,
            scale=0.1,
            pos=(-0.5, 0, 0.85),
            initialText="./utils/youtubeDownloader/good songs - mp3/",
            cursorKeys=True,
            overflow=1,
            # focus=True,
            focusOutCommand=self.registerFolder,
        )

    def registerSongs(self):
        self.songPanel = DirectFrame(parent=self.guiFrame, pos=(0, 0, 0))
        self.progressText = OnscreenText(
            text="",
            parent=self.guiFrame,
            scale=0.1,
            pos=(0.85, 0.9),
            fg=(1, 1, 1, 1),
        )
        # self.progressBar = DirectSlider(
        #     parent=self.settingsFrame,
        #     range=(1, 32),
        #     pageSize=1,
        #     scale=0.15,
        #     pos=(0.25, 0, 0.485),
        #     command=updateGuiValues,
        # )
        self.songList.reverse()
        for songId in range(len(self.songList)):

            def _playSong(song, panel, button):
                if song.status() == 2:
                    song.stop()
                    panel["frameColor"] = (0, 0, 0.6, 1)
                    button["text"] = "play"
                else:
                    song.play()
                    panel["frameColor"] = (0, 0.6, 0.3, 1)
                    button["text"] = "stop"

            songPanel = DirectFrame(
                parent=self.songPanel,
                frameSize=(-2, 2, -0.2, 0.2),
                pos=(0, 0, -0.5),
                scale=0.8,
                frameColor=(0, 0, 0.6, 1),
            )

            # playButton = DirectButton(
            #     parent=songPanel,
            #     text="play",
            #     command=_playSong,
            #     extraArgs=(self.songList[songId]["object"], songPanel),
            #     scale=0.2,
            #     pos=(0, 0, -0.1),
            # )
            # playButton["extraArgs"] = (
            #     self.songList[songId]["object"],
            #     songPanel,
            #     playButton,
            # )

            songName = OnscreenText(
                text=self.songList[songId]["name"],
                parent=songPanel,
                scale=0.1,
                pos=(0, 0),
            )
            self.songList[songId]["nodePath"] = songPanel
            # songPanel.hide()
        self.songList.reverse()
        self.songList[0]["nodePath"].setPos(0, 0, 0)
        self.songList[0]["nodePath"].setScale(1)

    def registerFolder(self):
        oldLength = len(self.songList)
        path = self.pathObject.get(plain=True)
        if os.path.isdir(path):
            _dir: list = os.listdir(path)
            _newDir = _dir.copy()
            for id in _dir:
                try:
                    id = str(id).split("|")
                    _newDir[int(id[0])] = "|".join(id)
                except:
                    ...
            for song in _newDir:
                if str(song).endswith((".m4a", ".mp3")):
                    self.songList.append(
                        {
                            "path": f"{path}{song}",
                            "object": self.loader.loadMusic(f"{path}{song}"),
                            "name": str(song).replace(".m4a", ""),
                            "nodePath": None,
                            "played": 0,
                        }
                    )
                else:
                    print(song)
        if len(self.songList) != oldLength:
            self.registerSongs()

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


app = Main()
app.run()
