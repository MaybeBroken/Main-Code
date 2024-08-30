from time import sleep, monotonic
import Vars as Vars
import os
from direct.gui.DirectGui import *  # type: ignore
from direct.showbase.ShowBase import ShowBase
from direct.stdpy.threading import Thread
import encoder
import yaml

os.chdir(os.path.abspath("./Py/games/rpg"))

startTime = monotonic()



def getTime() -> int:
    return int(monotonic()) - int(startTime)


def decodeFile(stream) -> list:
    returnVal = yaml.load(stream, yaml.CLoader)
    return returnVal


def encodeFile(list):
    return yaml.dump(list, Dumper=yaml.CDumper)


def fadeInNode(node, time):
    def _func():
        for step in range(time):
            node.set_alpha(1/(time-step))
            sleep(0.1)
    Thread(target=_func, daemon=True).start()


class mainGame(ShowBase):
    def __init__(self):
        # absolute startup values here!

        # end of startup config
        ShowBase.__init__(self)
        self.startup()

    def startup(self):
        self.loadPrefsFile()
        self.buildGui()
        self.setupInput()

    def savePrefsFile(self):
        with open("story.txt", "wt") as storyTextStream:
            storyTextStream.writelines(encodeFile(Vars.gameVars))

    def loadPrefsFile(self):
        with open("story.txt", "rt") as storyTextStream:
            Vars.gameVars = decodeFile(storyTextStream)

    def buildGui(self):
        self.frameBackdrop = DirectFrame(
            frameColor=(0, 0, 0, 1),
            frameSize=(-1, 1, -1, 1),
            parent=self.render2d,
        )
        fadeInNode(self.frameBackdrop, 1000)


    def setupInput(self):
        self.accept('q', self.exit)

    def exit(self):
        self.savePrefsFile()
        exit("\n\n:sys: User Quit\n\n")


game = mainGame()
game.run()
