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
from direct.interval.LerpInterval import *
from __YOUTUBEDOWNLOADER import CORE

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
    TransparencyAttrib,
    Point3,
    Point4,
    Vec3,
)
from direct.gui.OnscreenImage import OnscreenImage
from direct.stdpy.threading import Thread
from direct.gui.DirectGui import *


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
        self.doneInitialSetup = False
        self.setBackgroundColor(self.hexToRgb("#262626"))
        self.backfaceCullingOn()
        self.disableMouse()
        self.viewMode = 0
        self.favoritesToggle = False
        self.favoritesList = []
        self.rootListPath = os.path.join(".", f"youtubeDownloader{pathSeparator}")
        self.setupWorld()
        self.buildGui()
        self.setupControls()

    def syncProgress(self, task):
        try:
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
        except:
            ...
        return task.cont

    def update(self, task):
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
        self.scrollBar.setValue(self.songListFrameOffset.getZ())
        return task.cont

    def cullSongPanels(self):
        while True:
            t.sleep(0.1)
            for song in self.songList:
                if song["nodePath"]:
                    pos = song["nodePath"].getPos(self.render2d)
                    if pos.getZ() < -1.2 or pos.getZ() > 1.2:
                        song["nodePath"].hide()
                    else:
                        song["nodePath"].show()

    def setupControls(self):
        self.lastBackTime = t.time()
        self.paused = True
        self.currentTime = 0
        self.accept("space", self.togglePlay)
        self.accept("arrow_left", self.prevSong)
        self.accept("arrow_up", self.prevSong)
        self.accept("arrow_right", self.nextSong)
        self.accept("arrow_down", self.nextSong)
        self.accept("c", self.copySong)
        self.accept("q", sys.exit)
        self.accept("window-event", self.winEvent)
        self.accept(
            "wheel_up",
            lambda: (
                self.songListFrameOffset.setZ(self.songListFrameOffset.getZ() - 0.07),
            ),
        )
        self.accept(
            "wheel_down",
            lambda: self.songListFrameOffset.setZ(
                self.songListFrameOffset.getZ() + 0.07
            ),
        )

    def buildGui(self):
        self.scaledItemList = []
        self.guiFrame = DirectFrame(
            parent=self.aspect2d, scale=(1 * self.getAspectRatio(self.win), 1, 1)
        )
        self.songListFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.498, 0.99, -0.99, 0.79),
            frameColor=self.hexToRgb("#030303"),
        )
        self.songListFrame.setBin("background", 1000)
        self.songListFrameOffset = NodePath("songListFrameOffset")
        self.songListFrameOffset.reparentTo(self.songListFrame)
        self.optionBar = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, -0.5, -1, 0.79),
            frameColor=self.hexToRgb("#030303"),
        )
        self.optionBar.setBin("background", 2000)
        self.topBar = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, 1, 0.79, 1),
            frameColor=self.hexToRgb("#030303"),
        )
        self.topBar.setBin("background", 3000)
        self.topBarHighlight = DirectFrame(
            parent=self.topBar,
            frameSize=(-1, 1, 0.79, 0.8),
            frameColor=self.hexToRgb("#1e1e1e"),
        )
        self.topBarHighlight.setBin("background", 3001)
        self.controlBar = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, 1, -1, -0.79),
            frameColor=self.hexToRgb("#212121"),
        )
        self.controlBarClickButton = DirectButton(
            parent=self.controlBar,
            frameSize=(-1, 1, -1, -0.79),
            frameColor=(0, 0, 0, 0),
            command=self.setBackgroundBin,
        )
        self.controlBar.setBin("background", 3000)
        self.controlBar.setPos(0, 0, -0.2)
        self.blackoutOverlay = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, 1, -1, 1),
            frameColor=(0, 0, 0, 0),
        )
        self.blackoutOverlay.setBin("background", 2999)
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
            pos=(0, 0, -0.79),
            relief=DGG.FLAT,
            barColor=self.hexToRgb("#B2071d"),
            frameColor=(0, 0, 0, 0),
        )
        self.progressBar["range"] = 100
        self.progressBar.setRange()
        self.progressBar.setBin("background", 3101)
        self.songName = OnscreenText(
            text="Name of the Song Here",
            parent=self.controlBar,
            scale=(0.04 / self.getAspectRatio(self.win), 0.04, 0.04),
            pos=(-0.4, -0.9),
            fg=self.hexToRgb("#f6f6f6"),
            align=TextNode.ALeft,
        )
        self.songName.setBin("background", 3102)
        self.pausePlayButton = DirectButton(
            parent=self.controlBar,
            image=self.loader.loadTexture("src/textures/play.png"),
            scale=(0.04 / self.getAspectRatio(self.win), 0.04, 0.04),
            pos=(-0.85, 0, -0.9),
            command=self.togglePlay,
            relief=DGG.FLAT,
            frameColor=(0, 0, 0, 0),
        )
        self.pausePlayButton.setTransparency(TransparencyAttrib.MAlpha)
        self.arrowLeftButton = DirectButton(
            parent=self.controlBar,
            image=self.loader.loadTexture("src/textures/arrow.png"),
            scale=(0.03 / self.getAspectRatio(self.win), 0.03, 0.03),
            pos=(-0.95, 0, -0.9),
            hpr=(0, 0, 180),
            command=self.prevSong,
            relief=DGG.FLAT,
            frameColor=(0, 0, 0, 0),
        )
        self.arrowLeftButton.setTransparency(TransparencyAttrib.MAlpha)

        self.arrowRightButton = DirectButton(
            parent=self.controlBar,
            image=self.loader.loadTexture("src/textures/arrow.png"),
            scale=(0.03 / self.getAspectRatio(self.win), 0.03, 0.03),
            pos=(-0.75, 0, -0.9),
            command=self.nextSong,
            relief=DGG.FLAT,
            frameColor=(0, 0, 0, 0),
        )
        self.arrowRightButton.setTransparency(TransparencyAttrib.MAlpha)

        self.scaledItemList.append(self.pausePlayButton)
        self.scaledItemList.append(self.arrowLeftButton)
        self.scaledItemList.append(self.arrowRightButton)
        self.scaledItemList.append(self.progressText)
        self.scaledItemList.append(self.songName)

        startY = 0.7
        for item in os.listdir(os.path.join(".", f"youtubeDownloader{pathSeparator}")):
            if os.path.isdir(
                os.path.join(".", f"youtubeDownloader{pathSeparator}", item)
            ):
                if self.checkFolderForSongs(
                    os.path.join(".", f"youtubeDownloader{pathSeparator}", item),
                    (
                        ".m4a",
                        ".mp3",
                        ".wav",
                        ".ogg",
                        ".flac",
                        ".wma",
                        ".aac",
                    ),
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
                        text_fg=self.hexToRgb("#ffffff"),
                        frameColor=(0, 0, 0, 0),
                    )
                    self.scaledItemList.append(button)
                    divider = DirectFrame(
                        parent=self.optionBar,
                        frameSize=(
                            -0.95,
                            ((len(item) if len(item) < 28 else 31) * 0.012) - 0.9,
                            0,
                            0.004,
                        ),
                        frameColor=self.hexToRgb("#8f8f8f"),
                        pos=(0, 0, startY - 0.0275),
                    )
                    startY -= 0.075

        self.scrollBar = DirectScrollBar(
            parent=self.topBar,
            range=[0, ((len(self.songList) - 1) / 10) * 1.5],
            value=0,
            thumb_relief=DGG.FLAT,
            thumb_clickSound=None,
            command=lambda: self.songListFrameOffset.setZ(self.scrollBar["value"]),
            orientation=DGG.VERTICAL,
            pos=(0.765, 0, 0),
            frameSize=(0.1, 0.12, -0.82, 0.82),
            frameColor=(0.6, 0.6, 0.6, 0.5),
            relief=DGG.FLAT,
            pageSize=1,
        )
        self.scrollBar.setBin("background", 1900)
        self.scrollBar.hide()

    def checkFolderForSongs(self, path, formatList):
        for file in os.listdir(path):
            if file.endswith(tuple(formatList)):
                return True
        return False

    def copySong(self):
        copy(self.songList[self.songIndex]["path"])

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
        self.songList[self.songIndex]["object"].stop()
        if self.songIndex + 1 < len(self.songList):
            self.songIndex += 1
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["played"] = 1

        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        self.paused = False

    def prevSong(self):
        self.songList[self.songIndex]["object"].stop()
        if self.songIndex - 1 >= 0 and t.time() - self.lastBackTime > 1:
            self.songIndex -= 1
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["played"] = 1
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        self.paused = False
        self.lastBackTime = t.time()

    def goToSong(self, songId):
        self.songList[self.songIndex]["object"].stop()
        if songId < len(self.songList) and songId >= 0:
            self.songIndex = songId
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["played"] = 1
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        self.paused = False

    def setBackgroundImage(self, imageName, blur, background):
        def _th1(imageName, blur, background):
            try:
                if blur and not os.path.exists(
                    imageName.replace(".png", " - blur.png")
                ):
                    image = Image.open(imageName)
                    image = image.filter(ImageFilter.GaussianBlur(4))
                    newImageName = imageName.replace(".png", " - blur.png")
                    image.save(newImageName)
                else:
                    newImageName = imageName
                self.backgroundImage.setImage(newImageName)
            except Exception as e:
                self.backgroundImage.setImage("src/textures/404.png")

        Thread(target=_th1, args=(imageName, blur, background)).start()

    def setBackgroundBin(self):
        if self.viewMode == 0:
            if self.backgroundToggle:
                self.backgroundToggle = False
                LerpPosInterval(
                    self.backgroundImage,
                    0.25,
                    Point3(0, 0, 0),
                ).start()
                LerpScaleInterval(
                    self.backgroundImage,
                    0.25,
                    Point3(
                        (0.75 / self.getAspectRatio(self.win)) * (1280 / 720),
                        1,
                        0.75,
                    ),
                ).start()
                LerpColorInterval(
                    self.blackoutOverlay,
                    0.25,
                    (0, 0, 0, 1),
                ).start()
            else:
                self.backgroundToggle = True
                LerpPosInterval(
                    self.backgroundImage,
                    0.25,
                    Point3(0.65, 0, -0.5),
                ).start()
                LerpScaleInterval(
                    self.backgroundImage,
                    0.25,
                    Point3(
                        (0.25 / self.getAspectRatio(self.win)) * (1280 / 720),
                        1,
                        0.25,
                    ),
                ).start()
                LerpColorInterval(
                    self.blackoutOverlay,
                    0.25,
                    (0, 0, 0, 0),
                ).start()

    def togglePlay(self):
        if len(self.songList) > 0:
            self.pausePlayButton["image"] = self.loader.loadTexture(
                "src/textures/play.png"
                if self.songList[self.songIndex]["object"].status() == 2
                else "src/textures/pause.png"
            )
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

    def winEvent(self, window):
        if window.isClosed():
            sys.exit()
        for item in self.scaledItemList:
            try:
                item.setScale(
                    item.getScale()[2] / self.getAspectRatio(self.win),
                    item.getScale()[1],
                    item.getScale()[2],
                )
            except:
                try:
                    item.setScale(
                        item.getScale()[1] / self.getAspectRatio(self.win),
                        item.getScale()[1],
                    )
                except:
                    pass

    def makeSongPanel(self, songId):
        song = self.songList[songId]
        y = 0.7 + ((-songId) / 10) * 1.5
        frame = DirectFrame(
            parent=self.songListFrameOffset,
            frameSize=(-0.45, 0.85, -0.06, 0.06),
            frameColor=self.hexToRgb("#030303"),
            pos=(0, 0, y),
        )
        frame.setBin("background", 1000)
        frame.setTag("songId", str(songId))
        song["name"] = song["name"].split(" - ")[1:]
        song["name"] = " - ".join(song["name"])
        song["name"] = song["name"].replace(".m4a", "")
        nameText = OnscreenText(
            text=song["name"][:55] + "..." if len(song["name"]) > 55 else song["name"],
            parent=frame,
            scale=(0.05 / self.getAspectRatio(self.win), 0.05, 0.05),
            fg=self.hexToRgb("#f6f6f6"),
            pos=(-0.3, 0, 0),
            align=TextNode.ALeft,
        )
        nameText.setBin("background", 1001)
        lengthText = OnscreenText(
            text=str(divide(int(song["object"].length()), 60)[0])
            + ":"
            + str(divide(int(song["object"].length()), 60)[1]),
            parent=frame,
            scale=(0.05 / self.getAspectRatio(self.win), 0.05, 0.05),
            fg=self.hexToRgb("#f6f6f6"),
            pos=(0.7, 0, 0),
            align=TextNode.ARight,
        )
        lengthText.setBin("background", 1001)
        playButton = DirectButton(
            image=self.loader.loadTexture("src/textures/play.png"),
            parent=frame,
            scale=(0.03 / self.getAspectRatio(self.win), 0.03, 0.03),
            pos=(-0.4, 0, 0),
            command=self.goToSong,
            extraArgs=[songId],
            relief=DGG.FLAT,
            frameColor=(0, 0, 0, 0),
        )
        playButton.setTransparency(TransparencyAttrib.MAlpha)
        playButton.setBin("background", 1001)
        frameHighlight = DirectFrame(
            parent=frame,
            frameSize=(-0.45, 0.85, -0.005, 0),
            frameColor=self.hexToRgb("#1e1e1e"),
            pos=(0, 0, -0.065),
        )

        self.scaledItemList.append(playButton)
        self.scaledItemList.append(nameText)
        self.scaledItemList.append(lengthText)
        return frame

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

        self.scrollBar["range"] = [0, ((len(self.songList) - 1) / 10) * 1.5]
        self.scrollBar.setRange()
        self.scrollBar.setValue(0)
        self.scrollBar.show()
        LerpPosInterval(
            self.controlBar,
            0.5,
            Point3(0, 0, 0),
            Point3(0, 0, -0.2),
            blendType="easeInOut",
        ).start()
        self.backgroundImage = OnscreenImage(
            parent=self.render2d,
            image=self.loader.loadTexture("src/textures/404.png"),
            scale=((0.25 / self.getAspectRatio(self.win)) * (1280 / 720), 1, 0.25),
            pos=(0.65, 0, -0.5),
        )
        self.backgroundImage.setBin("foreground", 5000)
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        if not self.doneInitialSetup:
            self.taskMgr.add(self.update, "update")
            self.taskMgr.add(self.syncProgress, "syncProgress")
            Thread(target=self.cullSongPanels).start()
            self.doneInitialSetup = True

    def registerFolder(self, path):
        self.paused = True
        del self.songList[:]
        self.songIndex = 0
        if self.songListFrameOffset is not None:
            self.songListFrameOffset.setZ(0)
        for node in self.songListFrameOffset.getChildren():
            node.removeNode()
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
            _newDir: list = [None for _ in range(len(_dir))]
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
