import json
from random import randint, shuffle
import shutil
import time as t
import sys
import os
import PIL
import PIL.Image
import src.scripts.vars as Wvars
from screeninfo import get_monitors
from direct.showbase.ShowBase import ShowBase
from clipboard import copy
from direct.interval.LerpInterval import *
from __YOUTUBEDOWNLOADER import (
    CORE,
    UPDATE,
    YouTube,
    Playlist,
    registerCallbackFunction,
    registerInitalizeCallbackFunction,
    registerFinalizeCallbackFunction,
    checkValidLink,
)
from panda3d.core import (
    FilterProperties,
    loadPrcFile,
    ConfigVariableString,
    AudioSound,
    TextNode,
    LineSegs,
    NodePath,
    TransparencyAttrib,
    Point3,
    AudioManager,
)
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from direct.gui.OnscreenImage import OnscreenImage
from direct.stdpy.threading import Thread
from direct.gui.DirectGui import *
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from pydub import AudioSegment
import numpy as np
import scipy.fftpack as fft

try:
    CORE = CORE()
except:
    print("YT Downloader failed to load")
import clipboard

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"
os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))

IMAGESCALE: int = None


def convertSvgToPng(svgPath, pngPath, dpi=800, bgColor="#212121"):
    if os.path.exists(svgPath):
        drawing = svg2rlg(svgPath)
        # Change the color of the objects in the SVG
        for obj in drawing.contents:
            if isinstance(obj, Drawing):
                for sub_obj in obj.contents:
                    sub_obj.fillColor = HexColor(bgColor)

        renderPM.drawToFile(
            drawing,
            pngPath,
            fmt="PNG",
            dpi=dpi,
            bg=HexColor(bgColor),
        )
    else:
        print(f"Error: {svgPath} does not exist.")
    return pngPath


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
        str(int(monitor[0].width / 5) * 4) + " " + str(int(monitor[0].height / 5) * 4),
    ).setValue(
        str(int(monitor[0].width / 5) * 4) + " " + str(int(monitor[0].height / 5) * 4)
    )
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "false").setValue("false")
    ConfigVariableString("win-origin", "100 100").setValue("100 100")


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
        self.downloaderFrameVisible = False
        self.internalClipboard = None
        self.favoritesToggle = False
        self.favoritesList = []
        self.rootListPath = os.path.join(".", f"youtubeDownloader{pathSeparator}")
        self.setupWorld()
        self.buildGui()
        self.setupControls()
        Thread(target=self.checkForUpdatedLists).start()
        self.activeSongElement = None
        self.downloaderSongs: list[YouTube, NodePath] = []
        registerCallbackFunction(self.downloadCallback())
        registerInitalizeCallbackFunction(self.initalizeCallback())
        registerFinalizeCallbackFunction(self.finalizeCallback())
        global appGuiFrame
        appGuiFrame = self.aspect2d

    def downloadCallback(self):

        def _callback(
            video: YouTube,
            id: int,
            chunk: None,
            title: str,
            list: list[YouTube],
            progress: float = 0,
            status: list = ["Queued", "Downloading", "finished"],
        ):

            print(
                f"Video: {title}, ID: {id} of {len(list)}, Progress: {progress}%, Status: {status}"
            )

        return _callback

    def initalizeCallback(self):

        def _callback(playlist: Playlist):
            title = playlist.title
            notify(f"Playlist: {title} has been initialized")

        return _callback

    def finalizeCallback(self):
        def _callback(playlist: Playlist):
            title = playlist.title
            notify(f"Playlist: {title} has been downloaded")
            os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))
            self.refreshPlaylists()

        return _callback

    def makeDownloaderPanel(self, songId):
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
        nameText = OnscreenText(
            text=song["name"][:55] + "..." if len(song["name"]) > 55 else song["name"],
            parent=frame,
            scale=(0.05 / self.getAspectRatio(self.win), 0.05, 0.05),
            fg=self.hexToRgb("#f6f6f6"),
            pos=(-0.3, 0, 0),
            align=TextNode.ALeft,
        )
        nameText.setBin("background", 1001)
        frameHighlight = DirectFrame(
            parent=frame,
            frameSize=(-0.45, 0.85, -0.005, 0),
            frameColor=self.hexToRgb("#1e1e1e"),
            pos=(0, 0, -0.065),
        )

        self.scaledItemList.append(nameText)
        self.scaledItemList.append(frameHighlight)
        self.scaledItemList.append(frame)
        return frame

    def startSongDownloader(self, mode, url):
        if url is None:
            url = self.pasteFromClipboard()
        if url is None:
            return
        if mode == "s":
            CORE.downloadSong(url)
        elif mode == "ps":
            CORE.downloadPlaylist_S(url)
        elif mode == "v":
            CORE.downloadVideo(url)
        elif mode == "pv":
            CORE.downloadPlaylist_V(url)
        elif mode == "u":
            UPDATE().updatePlaylist(url)

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
            self.progressControlBar.setValue(
                (
                    self.songList[self.songIndex]["object"].get_time()
                    / self.songList[self.songIndex]["object"].length()
                )
                * 100
            )
            self.songName.setText(self.songList[self.songIndex]["name"])
        except:
            ...
        return task.cont

    def update(self, task):
        try:
            if not self.paused:
                if (
                    self.songList[self.songIndex]["object"].status() == 1
                    and self.songList[self.songIndex]["played"] == 1
                ):
                    self.songList[self.songIndex]["played"] = 0
                    self.nextSong()
        except:
            ...
        self.scrollBar.setValue(self.songListFrameOffset.getZ())
        self.updateAudioWaveform()
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

    def updateAudioWaveform(self):
        if (
            self.activeSongElement is not None
            and self.songList[self.songIndex]["object"].status() != 1
        ):
            current_time = self.songList[self.songIndex]["object"].get_time()
            start_sample = int(current_time * self.activeSongElement.frame_rate)
            end_sample = start_sample + int(self.activeSongElement.frame_rate // 50)
            audio_data = np.array(
                self.activeSongElement.get_array_of_samples()[start_sample:end_sample]
            )
            if len(audio_data) > 0:
                audio_data = np.pad(
                    audio_data, (0, (1024) - len(audio_data)), "constant"
                )
                fft_data = np.abs(fft.fft(audio_data))
                fft_data = fft_data[0 : (len(fft_data) // 10)]
                self.audioWaveform.setData(fft_data)

    def setupControls(self):
        self.lastBackTime = t.time()
        self.paused = True
        self.currentTime = 0
        self.accept("space", self.togglePlay)
        self.accept("arrow_left", self.prevSong)
        self.accept("arrow_up", self.prevSong)
        self.accept("arrow_left-repeat", self.prevSong)
        self.accept("arrow_up-repeat", self.prevSong)
        self.accept("arrow_right", self.nextSong)
        self.accept("arrow_down", self.nextSong)
        self.accept("arrow_right-repeat", self.nextSong)
        self.accept("arrow_down-repeat", self.nextSong)
        self.accept("c", self.copySong)
        self.accept("q", sys.exit)
        self.accept("window-event", self.winEvent)
        self.accept(
            "wheel_up",
            lambda: (
                self.songListFrameOffset.setZ(
                    self.songListFrameOffset.getZ() - 0.07
                    if self.songListFrameOffset.getZ() - 0.07 > 0
                    else 0
                ),
            ),
        )
        self.accept(
            "wheel_down",
            lambda: self.songListFrameOffset.setZ(
                self.songListFrameOffset.getZ() + 0.07
                if self.songListFrameOffset.getZ() + 0.07
                < ((len(self.songList) - 1) / 10) * 1.5
                else ((len(self.songList) - 1) / 10) * 1.5
            ),
        )

    def pasteFromClipboard(self):
        initial_text = clipboard.paste()
        if initial_text is not None and checkValidLink(initial_text):
            self.internalClipboard = initial_text
            return initial_text
        else:
            notify("Invalid URL")

    def checkForUpdatedLists(self):
        self.lastDir = []
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
                    self.lastDir.append(item)
        while True:
            t.sleep(0.2)
            currentDir = []
            for item in os.listdir(
                os.path.join(".", f"youtubeDownloader{pathSeparator}")
            ):
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
                        currentDir.append(item)
            if len(currentDir) != len(self.lastDir):
                self.refreshPlaylists()
            self.lastDir = currentDir

    def refreshPlaylists(self):
        for elem in self.playlists:
            for li in elem:
                if li in self.scaledItemList:
                    self.scaledItemList.remove(li)
                li.removeNode()
        self.playlists.clear()
        self.listStartY = 0.7
        self.playlists = []
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
                        pos=(-0.95, 0, self.listStartY),
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
                        pos=(0, 0, self.listStartY - 0.0275),
                    )
                    icon = OnscreenImage(
                        image="src/textures/playlist.png",
                        parent=self.optionBar,
                        scale=(0.025 / self.getAspectRatio(self.win), 0.025, 0.025),
                        pos=(-0.975, 0, self.listStartY + 0.0025),
                    )
                    self.listStartY -= 0.075
                    self.playlists.append([button, divider, icon])
                else:
                    print(
                        f"Error: {os.path.abspath(os.path.join(".", f"youtubeDownloader{pathSeparator}", item),)} does not contain songs."
                    )

    class audioWaveformVis:
        def __init__(self, main: "Main.audioWaveformVis", parent):
            self.parent = parent
            self.main = main
            self.graph = NodePath("waveformGraph")
            self.graph.reparentTo(parent)
            self.graph.setPos(0, 0, -0.78)
            self.line_segs = LineSegs()
            self.line_segs.setThickness(1)
            self.line_segs.setColor(1, 1, 1, 1)
            self.graph.attachNewNode(self.line_segs.create())
            self.floating_lines = [0] * 1024

        def setData(self, data):
            if len(data) > 0:
                current_max = float(np.max(data))
                num_points = len(data)
                self.line_segs.reset()
                for i, value in enumerate(data):
                    value = float(np.max(value))
                    x1 = -0.95 + (1.9 * (i / num_points))
                    x2 = -0.95 + (1.9 * ((i + 1) / num_points))
                    y = 0
                    z = (value / current_max) * 0.5 if current_max > 0 else 0
                    z *= 0.5
                    if z > self.floating_lines[i]:
                        self.floating_lines[i] = z
                    else:
                        self.floating_lines[i] -= 0.005
                    self.line_segs.moveTo(x1, y, 0)
                    self.line_segs.drawTo(x1, y, z)
                    self.line_segs.drawTo(x2, y, z)
                    self.line_segs.drawTo(x2, y, 0)
                    self.line_segs.drawTo(x1, y, 0)
                    self.line_segs.moveTo(x1, y, self.floating_lines[i])
                    self.line_segs.drawTo(x2, y, self.floating_lines[i])

                self.graph.node().removeAllChildren()
                self.graph.attachNewNode(self.line_segs.create())

    def openDownloaderPanel(self):
        if not self.downloaderFrameVisible:
            self.downloaderPanel = DirectFrame(
                self.aspect2d,
                frameColor=(0.8, 0.8, 0.8, 0.7),
                frameSize=(-0.3, 0.3, 0.4, -0.4),
                pos=(-1.2, 0, 0.45),
            )
            infoText = OnscreenText(
                text="Copy the link to the clipboard, then click which type below you would like to download",
                parent=self.downloaderPanel,
                scale=0.04,
                wordwrap=15,
                pos=(0, 0.35),
            )
            downloadSongButton = DirectButton(
                parent=self.downloaderPanel,
                text="Download Song",
                scale=0.05,
                pos=(-0.1, 0, 0.2),
                command=self.startSongDownloader,
                extraArgs=["s", None],
            )
            downloadPlaylistButton = DirectButton(
                parent=self.downloaderPanel,
                text="Download Playlist (s)",
                scale=0.05,
                pos=(-0.1, 0, 0.1),
                command=self.startSongDownloader,
                extraArgs=["ps", None],
            )
            downloadVideoButton = DirectButton(
                parent=self.downloaderPanel,
                text="Download Video",
                scale=0.05,
                pos=(-0.1, 0, 0),
                command=self.startSongDownloader,
                extraArgs=["v", None],
            )
            downloadPlaylistVideoButton = DirectButton(
                parent=self.downloaderPanel,
                text="Download Playlist (v)",
                scale=0.05,
                pos=(-0.1, 0, -0.1),
                command=self.startSongDownloader,
                extraArgs=["pv", None],
            )
            self.downloaderFrameVisible = True
        else:
            self.downloaderPanel.removeNode()
            self.downloaderFrameVisible = False

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

        self.downloaderButton = DirectButton(
            parent=self.topBar,
            text="Download from Youtube",
            pos=(-0.7, 0, 0.8775),
            scale=0.07,
            command=self.openDownloaderPanel,
        )
        self.scaledItemList.append(self.downloaderButton)

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
        self.progressControlBar = DirectScrollBar(
            parent=self.controlBar,
            range=[0, 100],
            value=0,
            thumb_relief=DGG.FLAT,
            thumb_clickSound=None,
            thumb_geom=None,
            thumb_scale=0.9,
            command=self.setSongTime,
            orientation=DGG.HORIZONTAL,
            pos=(0, 0, -0.79),
            frameSize=(-1.02, 1.02, -0.01, 0.01),
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pageSize=1,
        )
        self.progressControlBar.setBin("background", 3103)
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

        self.toggleSongShuffleButton = DirectButton(
            parent=self.controlBar,
            image=self.loader.loadTexture("src/textures/shuffle.png"),
            scale=(0.03 / self.getAspectRatio(self.win), 0.03, 0.03),
            pos=(0.65, 0, -0.9),
            command=self.toggleShuffle,
            relief=DGG.FLAT,
            frameColor=(0, 0, 0, 0),
        )
        self.audioWaveform = self.audioWaveformVis(self, self.controlBar)

        self.scaledItemList.append(self.pausePlayButton)
        self.scaledItemList.append(self.arrowLeftButton)
        self.scaledItemList.append(self.arrowRightButton)
        self.scaledItemList.append(self.progressText)
        self.scaledItemList.append(self.songName)

        self.listStartY = 0.7
        self.playlists = []
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
                    backgroundFrame = DirectFrame(
                        parent=self.optionBar,
                        frameSize=(-1, -0.5, 0.075, -0.075),
                        frameColor=(0.3, 0.3, 0.3, 1),
                        pos=(0, 0, self.listStartY),
                    )
                    button = DirectButton(
                        parent=self.optionBar,
                        text=item[:28] + "..." if len(item) > 28 else item,
                        scale=(0.05 / self.getAspectRatio(self.win), 0.05, 0.05),
                        pos=(-0.95, 0, self.listStartY+0.015),
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
                        pos=(0, 0, self.listStartY),
                    )
                    icon = OnscreenImage(
                        image="src/textures/playlist.png",
                        parent=self.optionBar,
                        scale=(0.025 / self.getAspectRatio(self.win), 0.025, 0.025),
                        pos=(-0.975, 0, self.listStartY + 0.0025),
                    )
                    self.scaledItemList.append(icon)
                    self.listStartY -= 0.01
                    self.playlists.append([button, divider, icon])

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
        self.winEvent(None)

    def checkFolderForSongs(self, path, formatList):
        for file in os.listdir(path):
            if file.endswith(tuple(formatList)):
                return True
        return False

    def setSongTime(self):
        try:
            if self.progressControlBar.guiItem.isButtonDown():
                if int(self.progressControlBar.getValue()) != self.lastSongTime:
                    new_time = (
                        self.progressControlBar.getValue() / 100
                    ) * self.songList[self.songIndex]["object"].length()
                    self.songList[self.songIndex]["object"].stop()
                    self.songList[self.songIndex]["object"].set_time(new_time)
                    self.songList[self.songIndex]["object"].play()
                    self.progressBar["value"] = self.progressControlBar.getValue()
                    self.progressBar.setValue()
        except Exception as e:
            print(e)
        self.lastSongTime = int(self.progressControlBar.getValue())

    def copySong(self):
        copy(self.songList[self.songIndex]["path"])

    def shuffleSongs(self):
        self.baseSongList = self.songList.copy()
        shuffle(self.songList)
        self.songIndex = 0
        for item in self.songList:
            item["object"].stop()
            item["nodePath"].setColorScale((1, 1, 1, 1))
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["object"].set_time(0)
        self.songList[self.songIndex]["played"] = 1
        self.songList[self.songIndex]["nodePath"].setColorScale((0.65, 1, 0.7, 1))
        self.activeSongElement: AudioSegment = AudioSegment.from_file(
            self.songList[self.songIndex]["path"],
            format=self.songList[self.songIndex]["path"].split(".")[-1],
        )
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )

    def sortSongs(self):
        self.songList = self.baseSongList.copy()
        self.songIndex = 0
        for item in self.songList:
            item["object"].stop()
            item["nodePath"].setColorScale((1, 1, 1, 1))
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["object"].set_time(0)
        self.songList[self.songIndex]["played"] = 1
        self.songList[self.songIndex]["nodePath"].setColorScale((0.65, 1, 0.7, 1))
        self.activeSongElement: AudioSegment = AudioSegment.from_file(
            self.songList[self.songIndex]["path"],
            format=self.songList[self.songIndex]["path"].split(".")[-1],
        )
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )

    def nextSong(self):
        self.songList[self.songIndex]["object"].stop()
        self.songList[self.songIndex]["nodePath"].setColorScale((1, 1, 1, 1))
        if self.songIndex + 1 < len(self.songList):
            self.songIndex += 1
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["object"].set_time(0)
        self.songList[self.songIndex]["played"] = 1
        self.songList[self.songIndex]["nodePath"].setColorScale((0.65, 1, 0.7, 1))
        self.activeSongElement: AudioSegment = AudioSegment.from_file(
            self.songList[self.songIndex]["path"],
            format=self.songList[self.songIndex]["path"].split(".")[-1],
        )
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        self.paused = False

    def prevSong(self):
        self.songList[self.songIndex]["object"].stop()
        self.songList[self.songIndex]["nodePath"].setColorScale((1, 1, 1, 1))
        if self.songIndex - 1 >= 0 and t.time() - self.lastBackTime < 3.5:
            self.songIndex -= 1
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["object"].set_time(0)
        self.songList[self.songIndex]["played"] = 1
        self.songList[self.songIndex]["nodePath"].setColorScale((0.65, 1, 0.7, 1))
        self.activeSongElement: AudioSegment = AudioSegment.from_file(
            self.songList[self.songIndex]["path"],
            format=self.songList[self.songIndex]["path"].split(".")[-1],
        )
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        self.paused = False
        self.lastBackTime = t.time()

    def goToSong(self, songId):
        if self.shuffleSongsToggle:
            self.sortSongs()
            self.shuffleSongsToggle = False
            self.toggleSongShuffleButton.setColor((1, 1, 1, 1))
        self.songList[self.songIndex]["object"].stop()
        self.songList[self.songIndex]["nodePath"].setColorScale((1, 1, 1, 1))
        if songId < len(self.songList) and songId >= 0:
            self.songIndex = songId
        self.songList[self.songIndex]["object"].play()
        self.songList[self.songIndex]["object"].set_time(0)
        self.songList[self.songIndex]["played"] = 1
        self.songList[self.songIndex]["nodePath"].setColorScale((0.65, 1, 0.7, 1))
        self.activeSongElement: AudioSegment = AudioSegment.from_file(
            self.songList[self.songIndex]["path"],
            format=self.songList[self.songIndex]["path"].split(".")[-1],
        )
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        self.paused = False

    def setBackgroundImage(self, imageName, blur, background):
        try:
            self.backgroundImage.setImage(imageName)
        except Exception as e:
            self.backgroundImage.setImage("src/textures/404.png")

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
                        (0.75 / self.getAspectRatio(self.win)) * IMAGESCALE,
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
                        (0.25 / self.getAspectRatio(self.win)) * IMAGESCALE,
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

    def toggleShuffle(self):
        if self.shuffleSongsToggle:
            self.sortSongs()
            self.shuffleSongsToggle = False
            self.toggleSongShuffleButton.setColor((1, 1, 1, 1))
        else:
            self.shuffleSongs()
            self.shuffleSongsToggle = True
            self.toggleSongShuffleButton.setColor((0.65, 1, 0.7, 1))
        LerpHprInterval(
            self.toggleSongShuffleButton,
            0.25,
            (0, self.toggleSongShuffleButton.getP() + 180, 0),
            blendType="easeInOut",
        ).start()

    def setupWorld(self):

        # Vars

        self.songList = []
        self.songIndex = 0
        self.backgroundToggle = True
        self.shuffleSongsToggle = False
        self.lastSongTime = 0

    def winEvent(self, window):
        try:
            if window.isClosed():
                sys.exit()
        except:
            None
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
            pos=(-0.45, 0, 0),
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
        try:
            image = OnscreenImage(
                parent=frame,
                image=self.loader.loadTexture(song["imagePath"]),
                scale=(0.05 / self.getAspectRatio(self.win) * IMAGESCALE, 1, 0.05),
                pos=(-0.36, 0, 0),
            )
        except:
            image = OnscreenImage(
                parent=frame,
                image=self.loader.loadTexture("src/textures/404.png"),
                scale=(0.05 / self.getAspectRatio(self.win) * (1280 / 720), 1, 0.05),
                pos=(-0.36, 0, 0),
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
        for obj in self.songList:
            if obj["object"].length() < 1:
                self.songList.remove(obj)
        for songId in range(len(self.songList)):
            global IMAGESCALE
            try:
                refImage = PIL.Image.open(self.songList[songId]["imagePath"])
                IMAGESCALE = refImage.width / refImage.height
            except:
                IMAGESCALE = 1280 / 720
            songPanel = self.makeSongPanel(songId)
            self.songListFrameOffset.setZ(((songId) / 10) * 1.5 - 0.9)
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
        if IMAGESCALE is None:
            IMAGESCALE = 1280 / 720
        self.backgroundImage = OnscreenImage(
            parent=self.render2d,
            image=self.loader.loadTexture("src/textures/404.png"),
            scale=((0.25 / self.getAspectRatio(self.win)) * IMAGESCALE, 1, 0.25),
            pos=(0.65, 0, -0.5),
        )
        self.backgroundImage.setBin("foreground", 5000)
        self.setBackgroundImage(
            self.songList[self.songIndex]["imagePath"],
            self.backgroundToggle,
            self.backgroundToggle,
        )
        self.songList[self.songIndex]["nodePath"].setColorScale((0.65, 1, 0.7, 1))
        if not self.doneInitialSetup:
            self.taskMgr.add(self.update, "update")
            self.taskMgr.add(self.syncProgress, "syncProgress")
            Thread(target=self.cullSongPanels).start()
            self.doneInitialSetup = True
        self.activeSongElement: AudioSegment = AudioSegment.from_file(
            self.songList[self.songIndex]["path"],
            format=self.songList[self.songIndex]["path"].split(".")[-1],
        )
        self.togglePlay()

    def registerFolder(self, path):
        os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))
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
                    audio_path = f"{path}{song}"
                    self.songList.append(
                        {
                            "path": audio_path,
                            "object": self.loader.loadMusic(audio_path),
                            "name": str(song).replace(".m4a", ""),
                            "nodePath": None,
                            "played": 0,
                            "imagePath": f"{path}img{pathSeparator}{imagePath}",
                        }
                    )
                else:
                    ...
        Thread(target=self.registerSongs).start()


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
    try:
        global appGuiFrame

        def fade(none):
            timeToFade = 5
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
    except Exception as e:
        print(f"Error: {e}")


app = Main()
app.run()
