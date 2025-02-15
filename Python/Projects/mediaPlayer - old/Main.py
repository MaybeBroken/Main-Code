import json
from math import pi, sin, cos
from random import randint, shuffle
import shutil
import time as t
import sys
import os
import src.scripts.vars as Wvars
from screeninfo import get_monitors
from direct.showbase.ShowBase import ShowBase
from clipboard import copy
from PIL import Image, ImageFilter
from direct.interval.LerpInterval import LerpPosInterval, LerpColorInterval

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))

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
    Point4,
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
from direct.filter.CommonFilters import CommonFilters

monitor = get_monitors()
loadPrcFile(f"src{pathSeparator}settings.prc")
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


def divide(num, divisor) -> list[2]:
    result = 0
    remainder = 0
    while num >= divisor:
        num -= divisor
        result += 1
    remainder = num
    return [
        result if len(str(result)) > 1 else f"0{result}",
        remainder if len(str(remainder)) > 1 else f"0{remainder}",
    ]


class CHARS:
    SEPARATOR = "  -->  "


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0, 0, 0, 1)
        self.backfaceCullingOn()
        self.disableMouse()
        # do setup tasks
        # ...
        self.viewMode = 0
        self.favoritesToggle = False
        self.favoritesList = []
        self.rootListPath = os.path.join(".", f"youtubeDownloader{pathSeparator}")
        self.setupWorld()

    def syncProgress(self):
        while True:
            t.sleep(0.1)
            progressText = (
                str(
                    divide(
                        int(self.songList[self.songIndex]["object"].get_time()),
                        60,
                    )[0]
                )
                + ":"
                + str(
                    divide(
                        int(self.songList[self.songIndex]["object"].get_time()),
                        60,
                    )[1]
                )
                + CHARS.SEPARATOR
                + str(
                    divide(
                        int(self.songList[self.songIndex]["object"].length()),
                        60,
                    )[0]
                )
                + ":"
                + str(
                    divide(
                        int(self.songList[self.songIndex]["object"].length()),
                        60,
                    )[1]
                )
            )
            self.progressText.setText(progressText)

    def update(self):
        while True:
            t.sleep(0.5)
            try:
                if not self.paused:
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
            except:
                ...

    def setupControls(self):
        self.accept("space", self.togglePlay)
        self.accept("o", self.setBackgroundBin)
        self.accept("arrow_left", self.prevSong)
        self.accept("arrow_right", self.nextSong)
        self.accept("c", self.copySong)
        self.accept("s", self.shuffleSongs)
        self.accept("shift-s", self.sortSongs)
        self.accept("f", self.toggleSongFavorite)
        self.accept(
            "shift-f",
            self.changePlaylist,
            extraArgs=[
                self.songList[self.songIndex]["path"]
                .replace(
                    self.songList[self.songIndex]["path"].split(pathSeparator)[-2],
                    "favorites",
                )
                .replace(
                    pathSeparator
                    + self.songList[self.songIndex]["path"].split(pathSeparator)[-1],
                    "",
                ),
            ],
        )
        self.paused = False
        self.currentTime = 0

    def copySong(self):
        copy(self.songList[self.songIndex]["path"])

    def changePlaylist(self, path):
        self.progressText.destroy()
        self.paused = True
        for song in self.songList:
            song["nodePath"].hide()
            song["nodePath"].destroy()
            song["object"].stop()
            self.songList.remove(song)
        self.paused = False
        self.registerFolder(path)
        self.songList[self.songIndex]["object"].play()

    def toggleSongFavorite(self):
        favoritesList: list = []
        favoritesNum = 0
        with open(self.rootListPath + "index", "tr") as listFile:
            try:
                favoritesList = json.JSONDecoder().decode(listFile.readline())
            except:
                favoritesList = []
        favoritesNum = len(favoritesList)
        if not self.songList[self.songIndex]["path"] in favoritesList:
            favoritesList.append(self.songList[self.songIndex]["path"])
            # try:
            #     os.mkdir(
            #         self.songList[self.songIndex]["path"]
            #         .replace(
            #             self.songList[self.songIndex]["path"].split(pathSeparator)[-2],
            #             f"{self.songList[self.songIndex]["path"].split(pathSeparator)[-2]}{pathSeparator}favorites",
            #         )
            #         .replace(
            #             self.songList[self.songIndex]["path"].split(pathSeparator)[-1],
            #             "",
            #         ),
            #     )
            #     os.mkdir(
            #         self.songList[self.songIndex]["imagePath"]
            #         .replace(
            #             self.songList[self.songIndex]["imagePath"].split(pathSeparator)[
            #                 -3
            #             ],
            #             f"{self.songList[self.songIndex]["imagePath"].split(pathSeparator)[-3]}{pathSeparator}favorites",
            #         )
            #         .replace(
            #             self.songList[self.songIndex]["imagePath"].split(pathSeparator)[
            #                 -1
            #             ],
            #             "",
            #         ),
            #     )
            # except:
            #     ...
            print(self.songList[self.songIndex]["path"])
            shutil.copy(
                self.songList[self.songIndex]["path"],
                self.songList[self.songIndex]["path"]
                .replace(
                    self.songList[self.songIndex]["path"].split(pathSeparator)[-3],
                    f"{self.songList[self.songIndex]["path"].split(pathSeparator)[-3]}{pathSeparator}favorites",
                )
                .replace(
                    self.songList[self.songIndex]["path"]
                    .replace(
                        self.songList[self.songIndex]["path"].split(pathSeparator)[-3],
                        f"{self.songList[self.songIndex]["path"].split(pathSeparator)[-3]}{pathSeparator}favorites",
                    )
                    .split(pathSeparator)[-1],
                    f"{favoritesNum} - {self.songList[self.songIndex]["path"].split(pathSeparator)[-1].split(" - ", 1)[1]}",
                ),
            )
            shutil.copy(
                self.songList[self.songIndex]["imagePath"],
                self.songList[self.songIndex]["imagePath"]
                .replace(
                    self.songList[self.songIndex]["imagePath"].split(pathSeparator)[-3],
                    f"{self.songList[self.songIndex]["imagePath"].split(pathSeparator)[-3]}{pathSeparator}favorites",
                )
                .replace(
                    self.songList[self.songIndex]["imagePath"].split(pathSeparator)[-1],
                    f"{favoritesNum} - {self.songList[self.songIndex]["imagePath"].split(pathSeparator)[-1].split(" - ", 1)[1]}",
                ),
            )
            with open(self.rootListPath + "index", "tw") as listFile:
                listFile.write(json.JSONEncoder().encode(favoritesList))

    def shuffleSongs(self):
        shuffle(self.songList)
        self.songIndex = 0
        if self.viewMode == 0:
            for item in self.songList:
                item["nodePath"].setPos(0, self.songIndex, -0.5)
                item["nodePath"].setScale(0.8)
                item["object"].stop()
                item["nodePath"]["frameColor"] = (0, 0, 0.6, 1)
                item["nodePath"].hide()
            if self.songIndex - 1 >= 0:
                self.songList[self.songIndex - 1]["nodePath"].setPos(10)
                self.songList[self.songIndex - 1]["nodePath"].hide()
            self.songList[self.songIndex]["nodePath"].show()
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
            self.songList[self.songIndex + 1]["nodePath"].show()

        t.sleep(0.1)
        self.prevSong()

    def sortSongs(self):
        _songList = self.songList.copy()
        for id in self.songList:
            try:
                newId = str(id["name"]).split("-")
                _songList[int(newId[0])] = id
            except:
                ...
        self.songList = _songList
        self.songIndex = 0

        if self.viewMode == 0:
            for item in self.songList:
                item["nodePath"].setPos(0, self.songIndex, -0.5)
                item["nodePath"].setScale(0.8)
                item["object"].stop()
                item["nodePath"]["frameColor"] = (0, 0, 0.6, 1)
                item["nodePath"].hide()
            if self.songIndex - 1 >= 0:
                self.songList[self.songIndex - 1]["nodePath"].setPos(10)
                self.songList[self.songIndex - 1]["nodePath"].hide()
            self.songList[self.songIndex]["nodePath"].show()
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
            self.songList[self.songIndex + 1]["nodePath"].show()

        t.sleep(0.1)
        self.prevSong()

    def nextSong(self):
        if len(self.songList) > 0 and not self.paused:
            if self.viewMode == 0:
                if self.songIndex - 1 >= 0:
                    LerpPosInterval(
                        self.songList[self.songIndex - 1]["nodePath"],
                        0.75,
                        Point3(0, self.songIndex, 2),
                        other=self.songPanel,
                        blendType="easeInOut",
                    ).start()

                self.songList[self.songIndex]["nodePath"].show()
                LerpPosInterval(
                    self.songList[self.songIndex]["nodePath"],
                    0.25,
                    Point3(0, self.songIndex, 0.5),
                    other=self.songPanel,
                    blendType="easeInOut",
                ).start()
                self.songList[self.songIndex]["nodePath"].setScale(0.8)
                self.songList[self.songIndex]["object"].stop()
                self.songList[self.songIndex]["nodePath"]["frameColor"] = (0, 0, 0.6, 1)
                if self.songIndex + 1 < len(self.songList):
                    self.songIndex += 1
                else:
                    self.songIndex = 0
                self.songList[self.songIndex]["nodePath"].show()
                LerpPosInterval(
                    self.songList[self.songIndex]["nodePath"],
                    0.25,
                    Point3(0, self.songIndex, 0),
                    other=self.songPanel,
                    blendType="easeInOut",
                ).start()
                self.songList[self.songIndex]["nodePath"].setScale(1)
                self.songList[self.songIndex]["object"].play()
                self.songList[self.songIndex]["played"] = 1
                self.songList[self.songIndex]["nodePath"]["frameColor"] = (
                    0,
                    0.6,
                    0.3,
                    1,
                )
                if self.songIndex + 1 < len(self.songList):
                    self.songList[self.songIndex + 1]["nodePath"].show()

            self.setBackgroundImage(
                self.songList[self.songIndex]["imagePath"],
                self.backgroundToggle,
                self.backgroundToggle,
            )

    def prevSong(self):
        if len(self.songList) > 0 and not self.paused:
            if self.viewMode == 0:
                if self.songIndex - 2 >= 0:
                    self.songList[self.songIndex - 2]["nodePath"].setPos(0, 0, 0.5)
                    self.songList[self.songIndex - 2]["nodePath"].show()
                LerpPosInterval(
                    self.songList[self.songIndex]["nodePath"],
                    0.25,
                    Point3(0, self.songIndex, -0.5),
                    other=self.songPanel,
                    blendType="easeInOut",
                ).start()
                self.songList[self.songIndex]["nodePath"].setScale(0.8)
                self.songList[self.songIndex]["object"].stop()
                self.songList[self.songIndex]["nodePath"]["frameColor"] = (0, 0, 0.6, 1)
                if self.songIndex + 1 < len(self.songList):
                    self.songList[self.songIndex + 1]["nodePath"].hide()
                self.songIndex -= 1
                self.songList[self.songIndex]["nodePath"].show()
                LerpPosInterval(
                    self.songList[self.songIndex]["nodePath"],
                    0.25,
                    Point3(0, self.songIndex, 0),
                    other=self.songPanel,
                    blendType="easeInOut",
                ).start()
                self.songList[self.songIndex]["nodePath"].setScale(1)
                self.songList[self.songIndex]["object"].play()
                self.songList[self.songIndex]["played"] = 1
                self.songList[self.songIndex]["nodePath"]["frameColor"] = (
                    0,
                    0.6,
                    0.3,
                    1,
                )
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )

    def setBackgroundImage(self, imageName, blur, background):
        def _th1(self, imageName, blur, background):
            try:
                if blur:
                    image = Image.open(imageName)
                    image = image.filter(ImageFilter.GaussianBlur(4))
                    newImageName = imageName.replace(".png", " - blur.png")
                    image.save(newImageName)
                else:
                    newImageName = imageName
                self.backgroundImage.destroy()
                self.backgroundImage = OnscreenImage(
                    parent=self.guiFrame,
                    image=self.loader.loadTexture(newImageName),
                    scale=(1.5 * (640 / 480), 1, 1.5),
                    pos=(0, 0, 0),
                )
                if background:
                    self.backgroundImage.setBin("background", 0)
                else:
                    # self.backgroundImage.setBin("foreground", 1000)
                    ...
            except:
                try:
                    self.backgroundImage.hide()
                except:
                    ...

        def _th2(self, imageName, blur, background): ...

        _th1(self, imageName, blur, background)
        # if self.viewMode == 0:
        #     Thread(target=_th1, args=(self, imageName, blur, background)).start()
        # elif self.viewMode == 1:
        #     Thread(target=_th2, args=(self, imageName, blur, background)).start()

    def setBackgroundBin(self):
        if self.viewMode == 0:
            if self.backgroundToggle:
                self.backgroundToggle = False
                self.setBackgroundImage(
                    self.songList[self.songIndex]["imagePath"],
                    self.backgroundToggle,
                    self.backgroundToggle,
                )
            else:
                self.backgroundToggle = True
                self.setBackgroundImage(
                    self.songList[self.songIndex]["imagePath"],
                    self.backgroundToggle,
                    self.backgroundToggle,
                )

    def togglePlay(self):
        if len(self.songList) > 0:
            if self.songList[self.songIndex]["object"].status() == 2:
                self.currentTime = self.songList[self.songIndex]["object"].getTime()
                self.songList[self.songIndex]["object"].stop()
                self.paused = True
            elif self.songList[self.songIndex]["object"].status() == 1:
                self.songList[self.songIndex]["object"].set_time(self.currentTime)
                self.songList[self.songIndex]["object"].play()
                self.paused = False

    def setupWorld(self):

        # Vars

        self.songList = []
        self.songIndex = 0
        self.backgroundToggle = True

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
        self.pathObject = DirectOptionMenu(
            parent=self.guiFrame,
            items=os.listdir(os.path.join(".", f"youtubeDownloader{pathSeparator}")),
            scale=0.1,
            pos=(-0.5, 0, 0),
            text_pos=(1, 0, 0.5),
            command=self.registerFolder,
        )
        self.accept("q", sys.exit)

    def registerSongs(self):
        self.songPanel = DirectFrame(parent=self.guiFrame, pos=(0, 0, 0))
        self.progressText = OnscreenText(
            text="",
            parent=self.guiFrame,
            scale=0.1,
            pos=(0, -0.3),
            fg=(1, 1, 1, 1),
        )
        # self.progressBar = DirectWaitBar(
        #     parent=self.guiFrame,
        #     scale=0.15,
        #     pos=(0.25, 0, 0.485),
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
                wordwrap=30,
            )
            self.songList[songId]["nodePath"] = songPanel
            songPanel.hide()
        self.songList.reverse()
        self.songList[0]["nodePath"].setPos(0, 0, 0)
        self.songList[0]["nodePath"].setScale(1)
        self.songList[self.songIndex]["nodePath"].show()
        try:
            self.songList[self.songIndex + 1]["nodePath"].show()
        except:
            ...
        try:
            self.backgroundImage = OnscreenImage(
                parent=self.guiFrame,
                image=self.loader.loadTexture(
                    self.songList[self.songIndex]["imagePath"]
                ),
                scale=(1.5 * (640 / 480), 1, 1.5),
                pos=(0, 0, 0),
            )
            self.backgroundImage.setBin("background", 0)
        except:
            ...
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        self.pathObject.removeNode()
        self.setupControls()
        Thread(target=self.update, daemon=True).start()
        Thread(target=self.syncProgress, daemon=True).start()

    def registerFolder(self, path):
        path = os.path.join(".", "youtubeDownloader", f"{path}{pathSeparator}")
        try:
            path = path.replace(
                "./youtubeDownloader/./youtubeDownloader/", "./youtubeDownloader/"
            )
        except:
            ...
        if os.path.isdir(path):
            self.rootListPath = path
            _dir: list = os.listdir(path)
            _newDir = _dir.copy()
            for id in _dir:
                try:
                    id = str(id).split(" - ")
                    _newDir[int(id[0])] = " - ".join(id)
                except:
                    ...
            for song in _newDir:
                if str(song).endswith((".m4a", ".mp3")):
                    imagePath = song.replace("m4a", "png")
                    self.songList.append(
                        {
                            "path": f"{path}{song}",
                            "object": self.loader.loadMusic(f"{path}{song}"),
                            "name": str(song).replace(".m4a", ""),
                            "nodePath": None,
                            "played": 0,
                            "imagePath": f"{path}img{pathSeparator}{imagePath}",
                        }
                    )
                else:
                    ...
        self.registerSongs()


def fadeOutGuiElement(
    element,
    timeToFade=100,
    daemon=True,
    execBeforeOrAfter: None = None,
    target: None = None,
    args=(),
):
    def _internalThread():
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

    return Thread(target=_internalThread, daemon=daemon).start()


def fadeInGuiElement(
    element,
    timeToFade=100,
    daemon=True,
    execBeforeOrAfter: None = None,
    target: None = None,
    args=(),
):
    def _internalThread():
        if execBeforeOrAfter == "Before":
            target(*args)

        element.show()
        for i in range(timeToFade):
            val = abs(0 - (1 / timeToFade) * (i + 1))
            element.setAlphaScale(val)
            t.sleep(0.01)
        if execBeforeOrAfter == "After":
            target(*args)

    return Thread(target=_internalThread, daemon=daemon).start()


def notify(message: str, pos=(0.8, 0, -0.5), scale=0.75):
    global appGuiFrame

    def fade(none):
        timeToFade = 20
        newMessage.setTransparency(True)

        def _internalThread():
            for i in range(timeToFade):
                val = 1 - (1 / timeToFade) * (i + 1)
                newMessage.setAlphaScale(val)
                t.sleep(0.01)
            newMessage.destroy()
            # newMessage.cleanup()

        Thread(target=_internalThread).start()

    newMessage = OkDialog(
        parent=appGuiFrame,
        text=message,
        pos=pos,
        scale=scale,
        frameColor=(0.5, 0.5, 0.5, 0.25),
        text_fg=(1, 1, 1, 1),
        command=fade,
        pad=[0.02, 0.02, 0.02, 0.02],
    )
    return newMessage


app = Main()
app.run()
