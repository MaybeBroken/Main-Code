import io
import os
import sys
from time import sleep
from threading import Thread
import requests
import urllib
import music_tag
from pytubefix import YouTube, Playlist, exceptions
import requests
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
                with open("config.json", "w") as f:
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
    with open("config.json", "w") as f:
        f.write(dumps(config, indent=4))


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
        self.linkInput = DirectEntry(
            scale=0.1,
            text_scale=0.6,
            frameColor=(0.4, 0.4, 0.4, 1),
            pos=(0, 0, 0.7),
            relief=DGG.FLAT,
            text_align=TextNode.ALeft,
            command=self.doLinkInput,
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
        if text != "":
            if self.doneLinkInput:
                ...
            else:
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
                    # command=,
                )
        else:
            print("No link entered")

    def copyLinkFromClipboard(self): ...

    def setOutputFolder(self):
        self.outputFolder = os.path.abspath(
            str(askdirectory(title="Select Output Folder"))
        )
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


YouTubeDownloader().run()
