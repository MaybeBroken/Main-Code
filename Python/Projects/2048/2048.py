from math import hypot, sqrt
import random
import time

from direct.gui.DirectGui import *  # type: ignore
from direct.showbase.ShowBase import ShowBase
import direct.dist.pfreeze as dist
from panda3d.core import loadPrcFile, ConfigVariableString, NodePath, loadPrcFileData
from panda3d.physics import *  # type: ignore
import panda3d.physics as physics
import threading as th
import vars as Vars
import os
from screeninfo import get_monitors

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def load_subclass():
    global prcfile
    global backdropColor
    global textColor
    global gameGridColor
    global start_time
    prcfile = loadPrcFile("config.prc")
    winh = get_monitors()[0].height
    winv = get_monitors()[0].width
    ConfigVariableString("win-size", "").setValue(str(winh) + " " + str(winv))
    backdropColor = Vars.black
    textColor = Vars.green
    gameGridColor = Vars.grey
    start_time = int(time.monotonic())


class mainGame(ShowBase):

    def __init__(self):
        load_subclass()
        start_time = int(time.monotonic())
        ShowBase.__init__(self)
        with open("xnaFramework.dll", "+rt") as xna:
            Vars.highScore = int(xna.read())
            xna.close()
        self.setupControls()
        self.gameWindow()
        self.updateScreen()
        th.Thread(None, self.updateScore, "Update Score", daemon=True).start()

    def savescore(self):
        with open("xnaFramework.dll", "+wt") as xna:
            xna.write(str(Vars.highScore))
            xna.close()

    def quitApp(self):
        self.savescore()
        ShowBase.destroy(self)
        exit()

    def relaunchgui(self):
        self.savescore()
        Vars.gameGrid = gameGrid = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        ShowBase.destroy(self)
        self.__init__()

    def gameWindow(self):
        self.loadTextures()
        self.setupmodels()

        self.frameBackdrop = DirectFrame(
            frameColor=backdropColor, frameSize=(-1, 1, -1, 1), parent=self.render2d
        )

        self.frame = DirectFrame()

        self.highscore = OnscreenText(
            parent=self.frame,
            pos=(-0.9, 0.9, 0.9),
            text="High score: 0",
            scale=0.08,
            fg=textColor,
        )
        self.currentscore = OnscreenText(
            parent=self.frame,
            pos=(0.9, 0.9, 0.9),
            text="Current Score: 0",
            scale=0.08,
            fg=textColor,
        )

        icon1 = DirectFrame(
            parent=self.render2d,
            frameSize=(-1, -0.5, -1, -0.5),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(-0.75, 0, -0.75),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon2 = DirectFrame(
            parent=self.render2d,
            frameSize=(-0.5, 0, -1, -0.5),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(-0.25, 0, -0.75),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon3 = DirectFrame(
            parent=self.render2d,
            frameSize=(0, 0.5, -1, -0.5),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(0.25, 0, -0.75),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon4 = DirectFrame(
            parent=self.render2d,
            frameSize=(0.5, 1, -1, -0.5),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(0.75, 0, -0.75),
            image_scale=(0.25, 0.25, 0.25),
        )

        icon5 = DirectFrame(
            parent=self.render2d,
            frameSize=(-1, -0.5, -0.5, 0),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(-0.75, 0, -0.25),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon6 = DirectFrame(
            parent=self.render2d,
            frameSize=(-0.5, 0, -0.5, 0),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(-0.25, 0, -0.25),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon7 = DirectFrame(
            parent=self.render2d,
            frameSize=(0, 0.5, -0.5, 0),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(0.25, 0, -0.25),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon8 = DirectFrame(
            parent=self.render2d,
            frameSize=(0.5, 1, -0.5, 0),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(0.75, 0, -0.25),
            image_scale=(0.25, 0.25, 0.25),
        )

        icon9 = DirectFrame(
            parent=self.render2d,
            frameSize=(-1, -0.5, 0, 0.5),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(-0.75, 0, 0.25),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon10 = DirectFrame(
            parent=self.render2d,
            frameSize=(-0.5, 0, 0, 0.5),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(-0.25, 0, 0.25),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon11 = DirectFrame(
            parent=self.render2d,
            frameSize=(0, 0.5, 0, 0.5),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(0.25, 0, 0.25),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon12 = DirectFrame(
            parent=self.render2d,
            frameSize=(0.5, 1, 0, 0.5),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(0.75, 0, 0.25),
            image_scale=(0.25, 0.25, 0.25),
        )

        icon13 = DirectFrame(
            parent=self.render2d,
            frameSize=(-1, -0.5, 0.5, 1),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(-0.75, 0, 0.75),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon14 = DirectFrame(
            parent=self.render2d,
            frameSize=(-0.5, 0, 0.5, 1),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(-0.25, 0, 0.75),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon15 = DirectFrame(
            parent=self.render2d,
            frameSize=(0, 0.5, 0.5, 1),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(0.25, 0, 0.75),
            image_scale=(0.25, 0.25, 0.25),
        )
        icon16 = DirectFrame(
            parent=self.render2d,
            frameSize=(0.5, 1, 0.5, 1),
            frameColor=gameGridColor,
            image=self.frametexture,
            image_pos=(0.75, 0, 0.75),
            image_scale=(0.25, 0.25, 0.25),
        )

        textframe1 = OnscreenText("-", pos=(-1.36, -0.8), scale=0.25)
        textframe2 = OnscreenText("-", pos=(-0.45, -0.8), scale=0.25)
        textframe3 = OnscreenText("-", pos=(0.45, -0.8), scale=0.25)
        textframe4 = OnscreenText("-", pos=(1.36, -0.8), scale=0.25)

        textframe5 = OnscreenText("-", pos=(-1.36, -0.25), scale=0.25)
        textframe6 = OnscreenText("-", pos=(-0.45, -0.25), scale=0.25)
        textframe7 = OnscreenText("-", pos=(0.45, -0.25), scale=0.25)
        textframe8 = OnscreenText("-", pos=(1.36, -0.25), scale=0.25)

        textframe9 = OnscreenText("-", pos=(-1.36, 0.25), scale=0.25)
        textframe10 = OnscreenText("-", pos=(-0.45, 0.25), scale=0.25)
        textframe11 = OnscreenText("-", pos=(0.45, 0.25), scale=0.25)
        textframe12 = OnscreenText("-", pos=(1.36, 0.25), scale=0.25)

        textframe13 = OnscreenText("-", pos=(-1.36, 0.72), scale=0.25)
        textframe14 = OnscreenText("-", pos=(-0.45, 0.72), scale=0.25)
        textframe15 = OnscreenText("-", pos=(0.45, 0.72), scale=0.25)
        textframe16 = OnscreenText("-", pos=(1.36, 0.72), scale=0.25)

        self.screenGrid = [
            [textframe13, textframe14, textframe15, textframe16],
            [textframe9, textframe10, textframe11, textframe12],
            [textframe5, textframe6, textframe7, textframe8],
            [textframe1, textframe2, textframe3, textframe4],
        ]

        self.backGrid = [
            [icon13, icon14, icon15, icon16],
            [icon9, icon10, icon11, icon12],
            [icon5, icon6, icon7, icon8],
            [icon1, icon2, icon3, icon4],
        ]

        th.Thread(
            None, self.updatecrosshair, "Update pointer crosshair", daemon=True
        ).start()

    def calc_score(self):
        Vars.score = 0
        temp = 0
        for index1 in range(len(Vars.gameGrid)):
            for index2 in range(len(Vars.gameGrid[index1])):
                temp = int(Vars.gameGrid[index1][index2])
                if temp == 2:
                    temp = 1
                elif temp == 4:
                    temp = 4
                elif temp == 8:
                    temp = 10
                elif temp == 16:
                    temp = 20
                elif temp == 32:
                    temp = 50
                elif temp == 64:
                    temp = 100
                elif temp == 128:
                    temp = 500
                elif temp == 256:
                    temp = 1000
                elif temp == 512:
                    temp = 5000
                elif temp == 1024:
                    temp = 10000
                elif temp == 2048:
                    temp = 50000
                Vars.score = Vars.score + temp
        self.savescore()

    def updateScore(self):
        while 1 == 1:
            if Vars.score > Vars.highScore:
                Vars.highScore = Vars.score
            try:
                self.currentscore.configure(text="Current Score: " + str(Vars.score))
            except:
                print("failed to update score")
            try:
                self.highscore.configure(text="High Score: " + str(Vars.highScore))
            except:
                print("failed to update high score")
            time.sleep(0.1)

    def setupControls(self):
        self.accept("w", self.updateValues, [True])
        self.accept("s", self.updateValues, [False, True])
        self.accept("a", self.updateValues, [False, False, True])
        self.accept("d", self.updateValues, [False, False, False, True])
        self.accept("arrow_up", self.updateValues, [True])
        self.accept("arrow_down", self.updateValues, [False, True])
        self.accept("arrow_left", self.updateValues, [False, False, True])
        self.accept("arrow_right", self.updateValues, [False, False, False, True])
        self.accept("r", self.relaunchgui)
        self.accept("q", self.quitApp)

    def updateValues(
        self,
        up: bool = False,
        down: bool = False,
        left: bool = False,
        right: bool = False,
    ):
        if up == True:
            print("Up")
            self.mathUp()
        if down == True:
            print("Down")
            self.mathDown()
        if left == True:
            print("Left")
            self.mathLeft()
        if right == True:
            print("Right")
            self.mathRight()

    def mathRight(self):
        for i in range(2):
            for row in range(len(Vars.gameGrid)):

                # first sequence to move all numbers over

                if Vars.gameGrid[row][2] != 0 and Vars.gameGrid[row][3] == 0:
                    Vars.gameGrid[row][3] = Vars.gameGrid[row][2]
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][1]
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0]
                    Vars.gameGrid[row][0] = 0
                if Vars.gameGrid[row][1] != 0 and Vars.gameGrid[row][2] == 0:
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][1]
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0]
                    Vars.gameGrid[row][0] = 0
                if Vars.gameGrid[row][0] != 0 and Vars.gameGrid[row][1] == 0:
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0]
                    Vars.gameGrid[row][0] = 0

                # second sequence to add all correct numbers

                if (
                    Vars.gameGrid[row][2] == Vars.gameGrid[row][3]
                    and Vars.gameGrid[row][3] != 0
                ):
                    Vars.gameGrid[row][3] = Vars.gameGrid[row][2] * 2
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][1]
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0]
                    Vars.gameGrid[row][0] = 0
                elif (
                    Vars.gameGrid[row][1] == Vars.gameGrid[row][2]
                    and Vars.gameGrid[row][2] != 0
                ):
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][1] * 2
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0]
                    Vars.gameGrid[row][0] = 0
                elif (
                    Vars.gameGrid[row][0] == Vars.gameGrid[row][1]
                    and Vars.gameGrid[row][1] != 0
                ):
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0] * 2
                    Vars.gameGrid[row][0] = 0

                # third sequence to move the final producs over

                if Vars.gameGrid[row][2] != 0 and Vars.gameGrid[row][3] == 0:
                    Vars.gameGrid[row][3] = Vars.gameGrid[row][2]
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][1]
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0]
                    Vars.gameGrid[row][0] = 0
                if Vars.gameGrid[row][1] != 0 and Vars.gameGrid[row][2] == 0:
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][1]
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0]
                    Vars.gameGrid[row][0] = 0
                if Vars.gameGrid[row][0] != 0 and Vars.gameGrid[row][1] == 0:
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][0]
                    Vars.gameGrid[row][0] = 0
        self.updateScreen()

    def mathLeft(self):
        for i in range(2):
            for row in range(len(Vars.gameGrid)):

                # first sequence to move all numbers over

                if Vars.gameGrid[row][1] != 0 and Vars.gameGrid[row][0] == 0:
                    Vars.gameGrid[row][0] = Vars.gameGrid[row][1]
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][2]
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3]
                    Vars.gameGrid[row][3] = 0
                if Vars.gameGrid[row][2] != 0 and Vars.gameGrid[row][1] == 0:
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][2]
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3]
                    Vars.gameGrid[row][3] = 0
                if Vars.gameGrid[row][3] != 0 and Vars.gameGrid[row][2] == 0:
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3]
                    Vars.gameGrid[row][3] = 0

                # second sequence to add all correct numbers

                if (
                    Vars.gameGrid[row][1] == Vars.gameGrid[row][0]
                    and Vars.gameGrid[row][1] != 0
                ):
                    Vars.gameGrid[row][0] = Vars.gameGrid[row][1] * 2
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][2]
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3]
                    Vars.gameGrid[row][3] = 0
                elif (
                    Vars.gameGrid[row][2] == Vars.gameGrid[row][1]
                    and Vars.gameGrid[row][2] != 0
                ):
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][2] * 2
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3]
                    Vars.gameGrid[row][3] = 0
                elif (
                    Vars.gameGrid[row][3] == Vars.gameGrid[row][2]
                    and Vars.gameGrid[row][3] != 0
                ):
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3] * 2
                    Vars.gameGrid[row][3] = 0

                # third sequence to move the final producs over

                if Vars.gameGrid[row][1] != 0 and Vars.gameGrid[row][0] == 0:
                    Vars.gameGrid[row][0] = Vars.gameGrid[row][1]
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][2]
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3]
                    Vars.gameGrid[row][3] = 0
                if Vars.gameGrid[row][2] != 0 and Vars.gameGrid[row][1] == 0:
                    Vars.gameGrid[row][1] = Vars.gameGrid[row][2]
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3]
                    Vars.gameGrid[row][3] = 0
                if Vars.gameGrid[row][3] != 0 and Vars.gameGrid[row][2] == 0:
                    Vars.gameGrid[row][2] = Vars.gameGrid[row][3]
                    Vars.gameGrid[row][3] = 0
        self.updateScreen()

    def mathUp(self):
        for i in range(2):
            for row in range(len(Vars.gameGrid)):

                # first sequence to move all numbers over

                if Vars.gameGrid[1][row] != 0 and Vars.gameGrid[0][row] == 0:
                    Vars.gameGrid[0][row] = Vars.gameGrid[1][row]
                    Vars.gameGrid[1][row] = Vars.gameGrid[2][row]
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row]
                    Vars.gameGrid[3][row] = 0
                if Vars.gameGrid[2][row] != 0 and Vars.gameGrid[1][row] == 0:
                    Vars.gameGrid[1][row] = Vars.gameGrid[2][row]
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row]
                    Vars.gameGrid[3][row] = 0
                if Vars.gameGrid[3][row] != 0 and Vars.gameGrid[2][row] == 0:
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row]
                    Vars.gameGrid[3][row] = 0

                # second sequence to add all correct numbers

                if (
                    Vars.gameGrid[1][row] == Vars.gameGrid[0][row]
                    and Vars.gameGrid[1][row] != 0
                ):
                    Vars.gameGrid[0][row] = Vars.gameGrid[1][row] * 2
                    Vars.gameGrid[1][row] = Vars.gameGrid[2][row]
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row]
                    Vars.gameGrid[3][row] = 0
                elif (
                    Vars.gameGrid[2][row] == Vars.gameGrid[1][row]
                    and Vars.gameGrid[2][row] != 0
                ):
                    Vars.gameGrid[1][row] = Vars.gameGrid[2][row] * 2
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row]
                    Vars.gameGrid[3][row] = 0
                elif (
                    Vars.gameGrid[3][row] == Vars.gameGrid[2][row]
                    and Vars.gameGrid[3][row] != 0
                ):
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row] * 2
                    Vars.gameGrid[3][row] = 0

                # third sequence to move the final producs over

                if Vars.gameGrid[1][row] != 0 and Vars.gameGrid[0][row] == 0:
                    Vars.gameGrid[0][row] = Vars.gameGrid[1][row]
                    Vars.gameGrid[1][row] = Vars.gameGrid[2][row]
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row]
                    Vars.gameGrid[3][row] = 0
                if Vars.gameGrid[2][row] != 0 and Vars.gameGrid[1][row] == 0:
                    Vars.gameGrid[1][row] = Vars.gameGrid[2][row]
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row]
                    Vars.gameGrid[3][row] = 0
                if Vars.gameGrid[3][row] != 0 and Vars.gameGrid[2][row] == 0:
                    Vars.gameGrid[2][row] = Vars.gameGrid[3][row]
                    Vars.gameGrid[3][row] = 0
        self.updateScreen()

    def mathDown(self):
        for i in range(2):
            for row in range(len(Vars.gameGrid)):
                # first sequence to move all numbers over
                if Vars.gameGrid[2][row] != 0 and Vars.gameGrid[3][row] == 0:
                    Vars.gameGrid[3][row] = Vars.gameGrid[2][row]
                    Vars.gameGrid[2][row] = Vars.gameGrid[1][row]
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row]
                    Vars.gameGrid[0][row] = 0
                if Vars.gameGrid[1][row] != 0 and Vars.gameGrid[2][row] == 0:
                    Vars.gameGrid[2][row] = Vars.gameGrid[1][row]
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row]
                    Vars.gameGrid[0][row] = 0
                if Vars.gameGrid[0][row] != 0 and Vars.gameGrid[1][row] == 0:
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row]
                    Vars.gameGrid[0][row] = 0

                # second sequence to add all correct numbers

                if (
                    Vars.gameGrid[2][row] == Vars.gameGrid[3][row]
                    and Vars.gameGrid[3][row] != 0
                ):
                    Vars.gameGrid[3][row] = Vars.gameGrid[2][row] * 2
                    Vars.gameGrid[2][row] = Vars.gameGrid[1][row]
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row]
                    Vars.gameGrid[0][row] = 0
                elif (
                    Vars.gameGrid[1][row] == Vars.gameGrid[2][row]
                    and Vars.gameGrid[2][row] != 0
                ):
                    Vars.gameGrid[2][row] = Vars.gameGrid[1][row] * 2
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row]
                    Vars.gameGrid[0][row] = 0
                elif (
                    Vars.gameGrid[0][row] == Vars.gameGrid[1][row]
                    and Vars.gameGrid[1][row] != 0
                ):
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row] * 2
                    Vars.gameGrid[0][row] = 0

                # third sequence to move the final producs over

                if Vars.gameGrid[2][row] != 0 and Vars.gameGrid[3][row] == 0:
                    Vars.gameGrid[3][row] = Vars.gameGrid[2][row]
                    Vars.gameGrid[2][row] = Vars.gameGrid[1][row]
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row]
                    Vars.gameGrid[0][row] = 0
                if Vars.gameGrid[1][row] != 0 and Vars.gameGrid[2][row] == 0:
                    Vars.gameGrid[2][row] = Vars.gameGrid[1][row]
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row]
                    Vars.gameGrid[0][row] = 0
                if Vars.gameGrid[0][row] != 0 and Vars.gameGrid[1][row] == 0:
                    Vars.gameGrid[1][row] = Vars.gameGrid[0][row]
                    Vars.gameGrid[0][row] = 0
        self.updateScreen()

    def randomscatter(self):
        randomActive = True
        while randomActive == True:
            randomindex1 = random.randint(0, len(Vars.gameGrid))
            randomindex2 = random.randint(0, len(Vars.gameGrid[0]))
            for index1 in range(len(Vars.gameGrid)):
                for index2 in range(len(Vars.gameGrid[index1])):
                    if Vars.gameGrid[index1][index2] * 1 == 0:
                        if index1 == randomindex1 and index2 == randomindex2:
                            Vars.gameGrid[index1][index2] = 2
                            print(
                                "placed number in slot "
                                + str(index1)
                                + ", "
                                + str(index2)
                                + ":  randomly selected numbers were "
                                + str(randomindex1)
                                + ", "
                                + str(randomindex1)
                            )
                            randomActive = False
                            break

    def updateScreen(self):
        self.randomscatter()
        for i in range(len(Vars.gameGrid)):
            print(
                "["
                + str(int(time.monotonic() - start_time))
                + "] --> "
                + str(Vars.gameGrid[i])
            )

        # change display values to hide zeros

        for index1 in range(4):
            for index2 in range(4):
                panel = self.screenGrid[index1][index2]
                background = self.backGrid[index1][index2]
                result = Vars.gameGrid[index1][index2]
                image = None
                if result == 0:
                    result = " "
                    image = self.frametexture
                if result == 2:
                    image = self.frametexture_white
                if result == 4:
                    image = self.frametexture_white
                if result == 8:
                    image = self.frametexture_grey
                if result == 16:
                    image = self.frametexture_grey
                if result == 32:
                    image = self.frametexture_grey
                if result == 64:
                    image = self.frametexture_orange
                if result == 128:
                    image = self.frametexture_orange
                if result == 256:
                    image = self.frametexture_yellow
                if result == 512:
                    image = self.frametexture_yellow
                if result == 1024:
                    image = self.frametexture_blue
                if result == 2048:
                    image = self.frametexture_blue
                if result == 4096:
                    image = self.frametexture_blue
                result = str(result)
                panel.configure(text=result)
                background.configure(image=image)
        self.calc_score()

    def setupmodels(self):

        self.crosshairimagenode = OnscreenImage(self.crosshair)
        self.crosshairimagenode.configure(pos=(0, 0, 1))
        self.crosshairimagenode.configure(scale=0.1)
        self.crosshairimagenode.setTransparency(1)

        self.cross_ring_imagenode = OnscreenImage(self.cross_ring)
        self.cross_ring_imagenode.configure(pos=(0, 0, 1))
        self.cross_ring_imagenode.configure(scale=0.1)
        self.cross_ring_imagenode.setTransparency(1)

        # physicsNode = NodePath("PhysicsNode")
        # physicsNode.reparentTo(self.render)
        # cursor_parent = ActorNode("cursor") # type: ignore
        # self.physicsMgr.attachPhysicalNode(cursor_parent) # type: ignore
        # cursor_parent.getPhysicsObject().setMass(50)

    def loadTextures(self):
        self.frametexture = self.loader.load_texture("src/frameBackground_transparent.png")  # type: ignore
        self.frametexture_blue = self.loader.load_texture("src/frameBackground_blue.png")  # type: ignore
        self.frametexture_grey = self.loader.load_texture("src/frameBackground_grey.png")  # type: ignore
        self.frametexture_orange = self.loader.load_texture("src/frameBackground_orange.png")  # type: ignore
        self.frametexture_white = self.loader.load_texture("src/frameBackground_white.png")  # type: ignore
        self.frametexture_yellow = self.loader.load_texture("src/frameBackground_yellow.png")  # type: ignore

        self.crosshair = self.loader.load_texture("src/crosshair_focus.png")  # type: ignore
        self.cross_ring = self.loader.load_texture("src/crosshair_ring.png")  # type: ignore

    def updatecrosshair(self):

        winh = get_monitors()[0].height
        winv = get_monitors()[0].width
        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = md.getY()
        self.cursor_pos = [mouseX, mouseY]
        current_cursor_x = self.cross_ring_imagenode.getPos()[0]
        current_cursor_y = self.cross_ring_imagenode.getPos()[1]
        true_cursor_pos_x = ((3.5 / winh) * self.cursor_pos[0]) - 1.75
        true_cursor_pos_y = ((2 / winv) * self.cursor_pos[1]) - 1

        while True:
            # get values
            md = self.win.getPointer(0)
            mouseX = md.getX()
            mouseY = md.getY()
            self.cursor_pos = [mouseX, mouseY]
            current_cursor_x = self.cross_ring_imagenode.getPos()[0]
            current_cursor_y = self.cross_ring_imagenode.getPos()[1]
            true_cursor_pos_x = ((3.5 / winh) * self.cursor_pos[0]) - 1.75
            true_cursor_pos_y = ((2 / winv) * self.cursor_pos[1]) - 1

            # momentum calculations

            image_pos_x = round(true_cursor_pos_x, 3)
            image_pos_y = round(true_cursor_pos_y, 3)
            self.crosshairimagenode.setPos(image_pos_x, image_pos_y, -image_pos_y)
            self.cross_ring_imagenode.setPos(image_pos_x, image_pos_y, -image_pos_y)
            self.cross_ring_imagenode.setR(self.cross_ring_imagenode.getR() + 0.3)

            time.sleep(0.01)


game = mainGame()
game.run()
