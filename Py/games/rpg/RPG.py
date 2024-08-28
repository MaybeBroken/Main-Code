import time
import Vars as Vars
import sys
from direct.gui.DirectGui import * # type: ignore
from direct.showbase.ShowBase import ShowBase
from tkinter.constants import * # type: ignore
import threading as th
import encoder

startTime = time.monotonic()

def getTime() -> int:
    return int(time.monotonic()) - int(startTime)

def decodelist(list_to_decode:list):
    for index1 in range(len(list_to_decode)):
        for index2 in range(len(list_to_decode[index1])):
            list_to_decode[index1][index2] = encoder.decode(list_to_decode[index1][index2], Vars.textFile.indexing)

def decodebuttons(list_to_decode:list):
    for index1 in range(len(list_to_decode)):
        list_to_decode[index1][0] = encoder.decode(list_to_decode[index1][0], Vars.textFile.indexing)
        list_to_decode[index1][1] = encoder.decode(list_to_decode[index1][1], Vars.textFile.indexing)

class mainGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.click = self.loader.loadSfx('Click1.wav') # type: ignore
        decodelist(Vars.TextFile)
        decodebuttons(Vars.TextChoices)
        self.startup()
    
    def startup(self):
        self.graphics()
        self.taskMgr.add(self.timeThread, 'timeMGR')
        self.taskMgr.add(self.updateValues, 'timeMGR')
    
    def graphics(self):
        self.frameBackdrop = DirectFrame(
            frameColor = (.5, .5, .5, 1),
            frameSize = (-1, 1, -1, 1),
            parent = self.render2d
            )
        
        self.frame = DirectFrame(frameColor = (1, 1, 1, 0))

        self.hp = DirectFrame(parent=self.frame, pos = (-0.75, 0, 0.75), scale = (0.1, 0, 0.1))
        self.time = DirectFrame(parent=self.frame, pos = (0.75, 0, 0.75), scale = (0.1, 0, 0.1))

        self.label0 = DirectLabel(parent=self.frame, pos = (0, 0, 0.5), scale = 0.08, text_scale = 0.75, text_pos = (0, 0))
        self.label1 = DirectLabel(parent=self.frame, pos = (0, 0, 0.3), scale = 0.08)
        self.label2 = DirectLabel(parent=self.frame, pos = (0, 0, 0.1), scale = 0.08)
        self.label3 = DirectLabel(parent=self.frame, pos = (0, 0, -0.1), scale = 0.08)
        self.label4 = DirectLabel(parent=self.frame, pos = (0, 0, -0.3), scale = 0.08)
        self.label5 = DirectLabel(parent=self.frame, pos = (0, 0, -0.5), scale = 0.08)

        self.button1 = DirectButton(
            parent=self.frame,
            text = " ",
            command = self.doTkButtonLeft,
            pos = (-0.85, 0, -0.85),
            scale = 0.07,
            frameSize = (-4, 4, -1, 1),
            clickSound = self.click,
            text_scale = 0.75,
            text_pos = (0, -0.2)
        )

        self.button2 = DirectButton(
            parent=self.frame,
            text = " ",
            command = self.doTkButtonRight,
            pos = (0.85, 0, -0.85),
            scale = 0.07,
            frameSize = (-4, 4, -1, 1),
            clickSound = self.click,
            text_scale = 0.75,
            text_pos = (0, -0.2)
        )

        self.label0.configure(text=Vars.TextFile[Vars.current_choice][0])
        self.label1.configure(text=Vars.TextFile[Vars.current_choice][1])
        self.label2.configure(text=Vars.TextFile[Vars.current_choice][2])
        self.label3.configure(text=Vars.TextFile[Vars.current_choice][3])
        self.label4.configure(text=Vars.TextFile[Vars.current_choice][4])
        self.label5.configure(text=Vars.TextFile[Vars.current_choice][5])
        
        self.button1.configure(text=Vars.TextChoices[Vars.current_choice][0])
        self.button2.configure(text=Vars.TextChoices[Vars.current_choice][1])

    def doTkButtonLeft(self):
        Vars.current_choice = Vars.TextChoices[Vars.current_choice][2]

        self.label0.configure(text=Vars.TextFile[Vars.current_choice][0])
        self.label1.configure(text=Vars.TextFile[Vars.current_choice][1])
        self.label2.configure(text=Vars.TextFile[Vars.current_choice][2])
        self.label3.configure(text=Vars.TextFile[Vars.current_choice][3])
        self.label4.configure(text=Vars.TextFile[Vars.current_choice][4])
        self.label5.configure(text=Vars.TextFile[Vars.current_choice][5])
        
        self.button1.configure(text=Vars.TextChoices[Vars.current_choice][0])
        self.button2.configure(text=Vars.TextChoices[Vars.current_choice][1])
        Vars.audioIsPlaying = 1

    def doTkButtonRight(self):
        Vars.current_choice = Vars.TextChoices[Vars.current_choice][3]
        
        self.label0.configure(text=Vars.TextFile[Vars.current_choice][0])
        self.label1.configure(text=Vars.TextFile[Vars.current_choice][1])
        self.label2.configure(text=Vars.TextFile[Vars.current_choice][2])
        self.label3.configure(text=Vars.TextFile[Vars.current_choice][3])
        self.label4.configure(text=Vars.TextFile[Vars.current_choice][4])
        self.label5.configure(text=Vars.TextFile[Vars.current_choice][5])
        
        self.button1.configure(text=Vars.TextChoices[Vars.current_choice][0])
        self.button2.configure(text=Vars.TextChoices[Vars.current_choice][1])
        Vars.audioIsPlaying = 1
    
    def timeThread(self, task):
        timeNow = getTime()
        self.time.configure(text=str(timeNow) +'s')
        return task.cont

    def updateValues(self, task):
            if Vars.PlayerHealth[0] == 100:
                Vars.PlayerHealth[1] = 'Full'
            if Vars.PlayerHealth[0] < 100:
                Vars.PlayerHealth[1] = 'High'
            if Vars.PlayerHealth[0] <= 85:
                Vars.PlayerHealth[1] = 'Ok'
            if Vars.PlayerHealth[0] <= 60:
                Vars.PlayerHealth[1] = 'Medium'
            if Vars.PlayerHealth[0] <= 35:
                Vars.PlayerHealth[1] = 'Low'
            if Vars.PlayerHealth[0] <= 15:
                Vars.PlayerHealth[1] = 'Almost Dead'
            if Vars.PlayerHealth[0] <= 0:
                exit()
            self.hp.configure(text=str(Vars.PlayerHealth[1]) +', ' +str(Vars.PlayerHealth[0]))
            return task.cont
    
    def charcterRandomizer(self, species: str | None, randomness: int | None) -> list:
        bio = []
        if species == 'human':
            self
        return bio

if sys.platform == 'win32':
    game = mainGame()
    game.run()
else: print('You must be on windows to run this program!')
