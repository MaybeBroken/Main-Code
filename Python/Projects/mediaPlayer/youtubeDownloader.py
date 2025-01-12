subProgram = r"""from pytubefix import YouTube, Playlist, exceptions, Channel, Search
import os
import requests
from threading import Thread as _Thread
import time

class Color:
    GREEN = "\033[92m"
    LIGHT_GREEN = "\033[1;92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    BOLD = "\033[;1m"
    CYAN = "\033[1;36m"
    LIGHT_CYAN = "\033[1;96m"
    LIGHT_GREY = "\033[1;37m"
    DARK_GREY = "\033[1;90m"
    BLACK = "\033[1;30m"
    WHITE = "\033[1;97m"
    INVERT = "\033[;7m"
    RESET = "\033[0m"


pathSeparator = "\\"


def pathSafe(name: str):
    for index in [["/", "-"], ["|", "-"], ["\\", "-"], ["*", ""], ['"', ""]]:
        try:
            name = name.replace(index[0], index[1])
        except:
            ...
    return name


def get_cover_image(url: str, dest_folder: str, dest_name: str):
    try:
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        filename = pathSafe(dest_name)
        file_path = os.path.join(dest_folder, filename)
        r = requests.get(url, stream=True)
        open(file_path, "xt")
        if r.ok:
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
        else:
            print(
                "img download failed: status code {}\n{}".format(r.status_code, r.text)
            )
        return file_path
    except FileExistsError:
        return None
    except:
        get_cover_image(url, dest_folder, dest_name)


class CORE:
    def downloadVideo(self, link):
        def _th():
            try:
                yt = YouTube(link)
                ys = yt.streams.get_highest_resolution()
                title = yt.title
                ys.download(
                    self.outputFolder + pathSeparator + "Videos" + pathSeparator,
                    filename=pathSafe(title) + ".mp4",
                )
            except exceptions.VideoUnavailable:
                print(Color.RED + "Video is unavailable" + Color.RESET)
            except exceptions.VideoPrivate:
                print(Color.RED + "Video is private" + Color.RESET)
            except exceptions.VideoRegionBlocked:
                print(Color.RED + "Video is blocked in your region" + Color.RESET)
            print(f"Downloaded {Color.GREEN}{title}{Color.RESET}")

        thread = _Thread(target=_th)
        thread.start()

    def downloadSong(self, link):
        def _th():
            try:
                yt = YouTube(link)
                ys = yt.streams.get_audio_only()
                title = yt.title
                ys.download(
                    output_path=self.outputFolder
                    + pathSeparator
                    + "Songs"
                    + pathSeparator,
                    filename=pathSafe(title) + ".m4a",
                )
            except exceptions.VideoUnavailable:
                print(Color.RED + "Video is unavailable" + Color.RESET)
            except exceptions.VideoPrivate:
                print(Color.RED + "Video is private" + Color.RESET)
            except exceptions.VideoRegionBlocked:
                print(Color.RED + "Video is blocked in your region" + Color.RESET)
            print(f"Downloaded {Color.GREEN}{title}{Color.RESET}")

        thread = _Thread(target=_th)
        thread.start()

    def downloadPlaylist_V(self, link):
        def _th():
            pl = Playlist(url=link)
            os.mkdir(path=pathSafe(pl.title))
            for video in pl.videos:
                time.sleep(0.15)

                def _inThread():
                    try:
                        title = video.title
                        video.streams.get_highest_resolution().download(
                            output_path=pathSafe(name=pl.title),
                            filename=pathSafe(title) + ".mp4",
                        )
                        print(f"| - Downloaded {Color.CYAN}{title}{Color.RESET}")
                    except exceptions.VideoUnavailable:
                        print(Color.RED + "Video is unavailable" + Color.RESET)
                    except exceptions.VideoPrivate:
                        print(Color.RED + "Video is private" + Color.RESET)
                    except exceptions.VideoRegionBlocked:
                        print(
                            Color.RED + "Video is blocked in your region" + Color.RESET
                        )

                _Thread(target=_inThread).start()

            print(f"Downloaded {Color.GREEN}{pl.title}{Color.RESET}")

        thread = _Thread(target=_th)
        thread.start()

    def downloadPlaylist_S(self, link):
        def _th():
            pl = Playlist(url=link)
            print(f"starting download of playlist {pl.title}:")
            os.mkdir(path=pathSafe(pl.title))
            for video in pl.videos:
                time.sleep(0.15)

                def _inThread():
                    try:
                        video.streams.get_audio_only().download(
                            output_path=pathSafe(name=pl.title),
                            filename=pathSafe(video.title) + ".m4a",
                            mp3=True,
                        )
                        print(f"| - Downloaded {video.title}")
                    except exceptions.VideoUnavailable:
                        print(Color.RED + "Video is unavailable" + Color.RESET)
                    except exceptions.VideoPrivate:
                        print(Color.RED + "Video is private" + Color.RESET)
                    except exceptions.VideoRegionBlocked:
                        print(
                            Color.RED + "Video is blocked in your region" + Color.RESET
                        )

                _Thread(target=_inThread).start()

        thread = _Thread(target=_th)
        thread.start()

    def downloadArtist_V(self, link):
        def _th():
            ch = Channel(url=link)
            os.mkdir(path=pathSafe(ch.title))
            for video in ch.videos:
                try:
                    video.streams.get_highest_resolution().download(
                        output_path=pathSafe(name=ch.title)
                    )
                except exceptions.VideoUnavailable:
                    print(Color.RED + "Video is unavailable" + Color.RESET)
                except exceptions.VideoPrivate:
                    print(Color.RED + "Video is private" + Color.RESET)
                except exceptions.VideoRegionBlocked:
                    print(Color.RED + "Video is blocked in your region" + Color.RESET)

        thread = _Thread(target=_th)
        thread.start()
"""
CORE = None
import io
import os
import sys
from panda3d.core import *
from panda3d.core import (
    TextNode,
    NodePath,
    loadPrcFileData,
)
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from json import loads, dumps
from tkinter.filedialog import askdirectory
from clipboard import copy, paste
import shutil

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))


class Color:
    GREEN = "\033[92m"
    LIGHT_GREEN = "\033[1;92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    BOLD = "\033[;1m"
    CYAN = "\033[1;36m"
    LIGHT_CYAN = "\033[1;96m"
    LIGHT_GREY = "\033[1;37m"
    DARK_GREY = "\033[1;90m"
    BLACK = "\033[1;30m"
    WHITE = "\033[1;97m"
    INVERT = "\033[;7m"
    RESET = "\033[0m"


rootPath = os.path.join(".", "youtubeDownloader")
threadQueue = {}


def load():
    default_config = {
        "config_prc": "window-title YouTube Downloader\nwin-size 720 720\nundecorated true\n",
        "output_folder": "\\No Folder Selected",
    }
    settingUp = True
    while settingUp:
        try:
            open("config.json", "r")
        except FileNotFoundError:
            with open("config.json", "w") as f:
                f.write(dumps(default_config, indent=4))
                pass
        with open("config.json", "r") as f:
            try:
                config = loads(f.read())
            except ValueError:
                with open("config.json", "wb") as f:
                    f.write(dumps(default_config, indent=4))
                pass
            except io.UnsupportedOperation:
                print(
                    "config.json is corrupted, please delete it and restart the program"
                )
                settingUp = False
                pass

            loadPrcFileData(
                "",
                config["config_prc"],
            )
            settingUp = False
    return config


def save(config):
    os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))
    with open("config.json", "w") as f:
        f.write(dumps(config, indent=4))
    print("Saved config")
    os.remove("CORE.py")


class YouTubeDownloader(ShowBase):
    def __init__(self):
        self.jsonConfig = load()
        ShowBase.__init__(self)
        self.setBackgroundColor(0, 0, 0)
        self.disableMouse()
        self.accept("escape", sys.exit)
        self.accept("q", sys.exit)
        self.setupVars()
        self.startUi()

    def setupVars(self):
        self.outputFolder = self.jsonConfig["output_folder"]
        if not self.outputFolder == "\\No Folder Selected":
            try:
                os.chdir(self.outputFolder + pathSeparator)
            except FileNotFoundError:
                self.outputFolder = "\\No Folder Selected"
                self.jsonConfig["output_folder"] = self.outputFolder
                print("output folder not found, resetting to default")
        print(f"changed folder to {self.outputFolder}")
        with open("..\\CORE.py", "w") as f:
            f.write(subProgram)
        global CORE
        CORE = __import__("CORE", fromlist=["CORE"]).CORE

    def startUi(self):
        self.guiFrame = DirectFrame(
            frameSize=(-1, 1, -1, 1), frameColor=(0.2, 0.2, 0.2, 1)
        )
        self.titleText = DirectLabel(
            text="goofy ahh youtube downloader dont ask for help",
            scale=0.1,
            text_scale=0.6,
            frameColor=(0.2, 0.2, 0.2, 1),
            pos=(0, 0, 0.9),
            relief=DGG.FLAT,
            text_align=TextNode.ACenter,
        )
        self.setOutputFolderButton = DirectButton(
            text="Change Output Folder",
            scale=0.1,
            text_scale=0.6,
            frameColor=(0.8, 0.8, 0.8, 1),
            pos=(-0.65, 0, 0.8),
            relief=DGG.RIDGE,
            command=self.setOutputFolder,
        )
        self.outputFolderLabel = DirectLabel(
            text="Output Folder: " + self.outputFolder.split(pathSeparator)[-1],
            scale=0.1,
            text_scale=0.6,
            frameColor=(0.6, 0.6, 0.6, 1),
            pos=(-0.3, 0, 0.8),
            relief=DGG.FLAT,
            text_align=TextNode.ALeft,
        )
        self.exitButton = DirectButton(
            text="X",
            scale=0.2,
            text_scale=0.6,
            frameColor=(0.2, 0.2, 0.2, 1),
            pos=(0.9, 0, 0.85),
            relief=DGG.FLAT,
            command=self.userExit,
        )
        self.copyLinkFromClipboardButton = DirectButton(
            text="Copy Link From Clipboard",
            scale=0.1,
            text_scale=0.6,
            frameColor=(0.8, 0.8, 0.8, 1),
            pos=(0, 0, 0.6),
            relief=DGG.RIDGE,
            command=self.copyLinkFromClipboard,
        )
        self.exitFunc = self.close

    doneLinkInput = False

    def close(self):
        save(self.jsonConfig)
        print("Exiting...")

    def doLinkInput(self, text):
        # check to see if the link is a valid youtube url
        if "youtube.com" in text and "https://" in text:
            if self.doneLinkInput:
                self.linkTypeButton.removeNode()
                self.downloadButton.removeNode()
                self.linkTypeButton = DirectOptionMenu(
                    scale=0.1,
                    text_scale=0.6,
                    frameColor=(0.8, 0.8, 0.8, 1),
                    pos=(0, 0, 0.5),
                    relief=DGG.RIDGE,
                    items=["", "Video", "Song", "Playlist", "Artist"],
                )
                self.downloadButton = DirectButton(
                    text="Download",
                    scale=0.1,
                    text_scale=0.6,
                    frameColor=(0.8, 0.8, 0.8, 1),
                    pos=(0, 0, 0.4),
                    relief=DGG.RIDGE,
                    command=self.download,
                )
            else:
                self.linkTypeButton = DirectOptionMenu(
                    scale=0.1,
                    text_scale=0.6,
                    frameColor=(0.8, 0.8, 0.8, 1),
                    pos=(0, 0, 0.5),
                    relief=DGG.RIDGE,
                    items=[
                        "",
                        "Video",
                        "Song",
                        "Playlist - Videos",
                        "Playlist - Songs",
                        "Artist - Videos",
                        "Artist - Songs",
                    ],
                )
                self.downloadButton = DirectButton(
                    text="Download",
                    scale=0.1,
                    text_scale=0.6,
                    frameColor=(0.8, 0.8, 0.8, 1),
                    pos=(0, 0, 0.4),
                    relief=DGG.RIDGE,
                    command=self.download,
                )
        else:
            print("Invalid URL: " + Color.CYAN + text + Color.RESET)

    def copyLinkFromClipboard(self):
        link = paste()
        self.link = link
        self.doLinkInput(link)

    def setOutputFolder(self):
        self.outputFolder = os.path.abspath(
            str(askdirectory(title="Select Output Folder"))
        )
        os.chdir(self.outputFolder + pathSeparator)
        self.jsonConfig["output_folder"] = self.outputFolder
        self.outputFolderLabel.removeNode()
        self.outputFolderLabel = DirectLabel(
            text="Output Folder: " + self.outputFolder.split(pathSeparator)[-1],
            scale=0.1,
            text_scale=0.6,
            frameColor=(0.6, 0.6, 0.6, 1),
            pos=(-0.3, 0, 0.8),
            relief=DGG.FLAT,
            text_align=TextNode.ALeft,
        )

    def download(self):
        link = self.link
        linkType = self.linkTypeButton.get()
        if linkType == "Video":
            CORE.downloadVideo(self, link)
        elif linkType == "Song":
            CORE.downloadSong(self, link)
        elif linkType == "Playlist - Videos":
            CORE.downloadPlaylist_V(self, link)
        elif linkType == "Playlist - Songs":
            CORE.downloadPlaylist_S(self, link)
        elif linkType == "Artist - Videos":
            CORE.downloadArtist_V(self, link)
        elif linkType == "Artist - Songs":
            CORE.downloadArtist_S(self, link)
        else:
            ...
        self.downloadButton.removeNode()
        self.linkTypeButton.removeNode()
        self.doneLinkInput = False


YouTubeDownloader().run()
