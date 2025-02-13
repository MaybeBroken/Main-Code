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

from panda3d.core import (
    Texture,
    loadPrcFile,
    ConfigVariableString,
    AudioSound,
    WindowProperties,
    NodePath,
    TextNode,
    Point3,
    Point4,
    Vec3,
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
    SEPARATOR = " /  "


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0, 0, 0, 1)
        self.backfaceCullingOn()
        self.disableMouse()
        self.viewMode = 0
        self.favoritesToggle = False
        self.favoritesList = []
        self.rootListPath = os.path.join(".", f"youtubeDownloader{pathSeparator}")
        self.setupWorld()
        self.setupControls()
        self.buildGui()

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
            self.progressBar["value"] = (
                self.songList[self.songIndex]["object"].get_time()
                / self.songList[self.songIndex]["object"].length()
            ) * 100
            self.progressBar.setValue()
            self.songName.setText(self.songList[self.songIndex]["name"])

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
        self.accept("arrow_left", self.prevSong)
        self.accept("arrow_up", self.prevSong)
        self.accept("arrow_right", self.nextSong)
        self.accept("arrow_down", self.nextSong)
        self.accept("c", self.copySong)
        self.accept("q", sys.exit)
        self.accept("window-event", self.onWindowResize)
        self.paused = True
        self.currentTime = 0

    def buildGui(self):
        self.guiFrame = DirectFrame(
            parent=self.aspect2d, scale=(1 * self.getAspectRatio(self.win), 1, 1)
        )
        self.songListFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.5, 0.9, -0.8, 0.8),
            frameColor=(0.4, 0.4, 0.4, 1),
        )
        self.songListFrame.setBin("background", 1000)
        self.optionBar = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, -0.5, -0.8, 0.8),
            frameColor=(0.2, 0.2, 0.2, 1),
        )
        self.optionBar.setBin("background", 2000)
        self.topBar = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, 1, 0.8, 1),
            frameColor=(0.1, 0.1, 0.1, 1),
        )
        self.topBar.setBin("background", 3000)
        self.controlBar = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, 1, -1, -0.8),
            frameColor=self.hexToRgb("#212121"),
        )
        self.controlBar.setBin("background", 3000)
        self.progressText = OnscreenText(
            text="time / length",
            parent=self.controlBar,
            scale=(0.04 / self.getAspectRatio(self.win), 0.04, 0.04),
            pos=(-0.7, -0.9),
            fg=self.hexToRgb("#919191"),
            align=TextNode.ALeft,
        )
        self.progressText.setBin("background", 3100)
        self.progressBar = DirectWaitBar(
            parent=self.controlBar,
            scale=(1, 1, 0.05),
            frameColor=self.hexToRgb("#212121"),
            pos=(0, 0, -0.8),
            relief=DGG.FLAT,
            barColor=self.hexToRgb("#B2071d"),
        )
        self.progressBar["range"] = 100
        self.progressBar.setRange()
        self.progressBar.setBin("background", 3101)
        self.songName = OnscreenText(
            text="Name of the Song Here",
            parent=self.topBar,
            scale=(0.05 / self.getAspectRatio(self.win), 0.05, 0.05),
            pos=(0.1, -0.9),
            fg=self.hexToRgb("#f6f6f6"),
            align=TextNode.ALeft,
        )
        self.songName.setBin("background", 3102)
        startY = 0.7
        self.scaledItemList = []
        for item in os.listdir(os.path.join(".", f"youtubeDownloader{pathSeparator}")):
            if os.path.isdir(
                os.path.join(".", f"youtubeDownloader{pathSeparator}", item)
            ):
                button = DirectButton(
                    parent=self.optionBar,
                    text=item[:28] + "..." if len(item) > 28 else item,
                    scale=(0.05 / self.getAspectRatio(self.win), 0.05, 0.05),
                    pos=(-0.95, 0, startY),
                    command=self.registerFolder,
                    extraArgs=[item],
                    text_align=TextNode.ALeft,
                    relief=DGG.FLAT,
                    geom=None,
                )
                self.scaledItemList.append(button)
                startY -= 0.075

    def copySong(self):
        copy(self.songList[self.songIndex]["path"])

    def changePlaylist(self, path):
        self.paused = True
        for song in self.songList:
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
                item["object"].stop()
                item["nodePath"].hide()
            self.songList[self.songIndex]["object"].stop()
            self.songIndex += 1
            self.songList[self.songIndex]["object"].play()
            self.songList[self.songIndex]["played"] = 1

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
                item["object"].stop()
            self.songList[self.songIndex]["object"].stop()
            self.songIndex += 1
            self.songList[self.songIndex]["object"].play()
            self.songList[self.songIndex]["played"] = 1

        t.sleep(0.1)
        self.prevSong()

    def nextSong(self):
        if len(self.songList) > 0 and not self.paused:
            if self.viewMode == 0:
                self.songList[self.songIndex]["object"].stop()
                if self.songIndex + 1 < len(self.songList):
                    self.songIndex += 1
                else:
                    self.songIndex = 0
                self.songList[self.songIndex]["object"].play()
                self.songList[self.songIndex]["played"] = 1

            self.setBackgroundImage(
                self.songList[self.songIndex]["imagePath"],
                self.backgroundToggle,
                self.backgroundToggle,
            )

    def prevSong(self):
        if len(self.songList) > 0 and not self.paused:
            if self.viewMode == 0:
                self.songList[self.songIndex]["object"].stop()
                self.songIndex -= 1
                self.songList[self.songIndex]["object"].play()
                self.songList[self.songIndex]["played"] = 1
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
        self.accept("q", sys.exit)
        self.accept("window-event", self.onWindowResize)

    def onWindowResize(self, window):
        for item in self.scaledItemList:
            item.setScale(
                item.getScale()[2] / self.getAspectRatio(self.win),
                item.getScale()[1],
                item.getScale()[2],
            )

    def makeSongPanel(self, songId):
        song = self.songList[songId]
        return DirectButton(
            parent=self.songListFrame,
            text=song["name"],
            scale=(0.05 / self.getAspectRatio(self.win), 0.05, 0.05),
            pos=(0, 0, 0),
            text_align=TextNode.ALeft,
        )

    def hexToRgb(self, hex: str) -> tuple:
        hex = hex.lstrip("#")
        return tuple(int(hex[i : i + 2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)

    def registerSongs(self):
        for songId in range(len(self.songList)):
            if self.songList[songId]["nodePath"] is not None:
                self.songList[songId]["nodePath"].destroy()
        for songId in range(len(self.songList)):
            songPanel = self.makeSongPanel(songId)
            self.songList[songId]["nodePath"] = songPanel
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
        self.togglePlay()


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
