from direct.filter.CommonFilters import CommonFilters
from direct.gui.DirectGui import *
from src.scripts.guiUtils import fade
import src.scripts.vars as Wvars
from direct.directtools.DirectGrid import DirectGrid
from panda3d.core import deg2Rad
import sys

monitor = None
main = None
guiClass = None
spriteSheet = {}


class ShaderCall:
    def setupShaders(self, mainApp, light, wantShaders):
        if wantShaders == True:
            mainApp.render.setShaderAuto()
            filters = CommonFilters(mainApp.win, mainApp.cam)
            filters.setBloom(
                (0.3, 0.4, 0.3, 0.8),
                mintrigger=0.1,
                maxtrigger=1,
                desat=0.1,
                intensity=1,
                size="medium",
            )
            # filters.setAmbientOcclusion()
            filters.setSrgbEncode()
            filters.setHighDynamicRange()
            # filters.setBlurSharpen(1.5)


class settingsScreen:
    def start(self):
        def updateDifficulty(arg):
            if arg == "Blank":
                self.shipHealthSlider["value"] = 0
                self.shipHitRadiusSlider["value"] = 0
                self.droneHitRadiusSlider["value"] = 0
                self.droneNum.set("0")
                self.droneHealthSlider["value"] = 1

            elif arg == "Easy":
                self.shipHealthSlider["value"] = 20
                self.shipHitRadiusSlider["value"] = 2
                self.droneHitRadiusSlider["value"] = 12
                self.droneNum.set("5")
                self.droneHealthSlider["value"] = 3
            elif arg == "Medium":
                self.shipHealthSlider["value"] = 15
                self.shipHitRadiusSlider["value"] = 6
                self.droneHitRadiusSlider["value"] = 8
                self.droneNum.set("10")
                self.droneHealthSlider["value"] = 8
            elif arg == "Hard":
                self.shipHealthSlider["value"] = 8
                self.shipHitRadiusSlider["value"] = 8
                self.droneHitRadiusSlider["value"] = 5
                self.droneNum.set("25")
                self.droneHealthSlider["value"] = 16
            elif arg == "Impossible ;)":
                self.shipHealthSlider["value"] = 3
                self.shipHitRadiusSlider["value"] = 12
                self.droneHitRadiusSlider["value"] = 3
                self.droneNum.set("50")
                self.droneHealthSlider["value"] = 32

        def updateGuiValues():
            self.shipHealthTitle["text"] = (
                f"Ship Hit Points: {int(self.shipHealthSlider['value'])}"
            )
            self.shipHitRadiusTitle["text"] = (
                f"Ship Hitbox Radius: {int(self.shipHitRadiusSlider['value'])}"
            )
            self.droneHitRadiusTitle["text"] = (
                f"Drone Hitbox Radius: {int(self.droneHitRadiusSlider['value'])}"
            )
            self.droneHealthTitle["text"] = (
                f"Drone Hit Points: {int(self.droneHealthSlider['value'])}"
            )
            Wvars.shipHealth = int(self.shipHealthSlider["value"])
            Wvars.shipHitRadius = int(self.shipHitRadiusSlider["value"])
            Wvars.droneHitRadius = int(self.droneHitRadiusSlider["value"])
            Wvars.droneNum = int(self.droneNum.get())
            Wvars.droneHealth = int(self.droneHealthSlider["value"])

        global spriteSheet
        self.setBackgroundColor(0, 0, 0, 1)
        self.guiFrame = DirectFrame(parent=self.aspect2d)
        spriteSheet["menuBackground"] = self.loader.loadTexture(
            "src/textures/raw/menuBackground.png"
        )
        spriteSheet["startButton"] = self.loader.loadTexture(
            "src/textures/raw/startButton.png"
        )
        spriteSheet["startButton"]
        spriteSheet["exitButton"] = self.loader.loadTexture(
            "src/textures/raw/exitButton.png"
        )
        spriteSheet["voyagerLogo"] = self.loader.loadTexture(
            texturePath="src/textures/raw/Voyager_Logo.png",
        )
        spriteSheet["flightDirector"] = self.loader.loadTexture(
            texturePath="src/textures/raw/flightDirectorTile.png",
        )

        self.startupMenuFrame = DirectFrame(parent=self.guiFrame)
        self.startupMenuFrame.set_transparency(1)

        self.startupMenuBackgroundImage = OnscreenImage(
            parent=self.startupMenuFrame,
            image=spriteSheet["menuBackground"],
            scale=(1 * monitor[0].width / monitor[0].height, 1, 1),
        )

        self.startupMenuBackgroundImage2 = OnscreenImage(
            parent=self.startupMenuFrame,
            image=spriteSheet["voyagerLogo"],
            scale=0.25,
            pos=(0.825 * monitor[0].width / monitor[0].height, 0, -0.725),
        )

        self.startupMenuStartButton = DirectButton(
            parent=self.startupMenuFrame,
            pos=(-0.7 * monitor[0].width / monitor[0].height, 0, 0.6),
            scale=(0.12 * (553 / 194), 1, 0.12),
            relief=None,
            image=spriteSheet["startButton"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=self.load,
        )

        self.startupMenuQuitButton = DirectButton(
            parent=self.startupMenuFrame,
            pos=(-0.7 * monitor[0].width / monitor[0].height, 0, 0.3),
            scale=(0.12 * (553 / 194), 1, 0.12),
            relief=DGG.FLAT,
            image=spriteSheet["exitButton"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=sys.exit,
        )

        self.startupMenuCreditsText = OnscreenText(
            "Programmed by David Sponseller",
            pos=(-0.8 * monitor[0].width / monitor[0].height, -0.95),
            scale=0.04,
            parent=self.startupMenuFrame,
            fg=(0.5, 7, 7, 0.75),
        )

        self.settingsFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.25, 0.75, -0.75, 0.75),
            frameColor=(0, 0, 0, 0.4),
        )
        self.settingsTopBar = DirectFrame(
            parent=self.settingsFrame,
            frameSize=(-0.25, 0.75, 0.65, 0.75),
            frameColor=(0, 0, 0, 0.4),
        )
        self.presetsTitle = OnscreenText(
            text="Presets: ",
            parent=self.settingsTopBar,
            scale=0.04,
            pos=(-0.1, 0.69),
            fg=(1, 1, 1, 1),
        )
        self.presetsMenu = DirectOptionMenu(
            parent=self.settingsTopBar,
            items=["Blank", "Easy", "Medium", "Hard", "Impossible ;)"],
            command=updateDifficulty,
            scale=0.06,
            pos=(0.05, 1, 0.69),
        )

        self.shipHealthTitle = OnscreenText(
            text=f"Ship Hit Points: 1",
            parent=self.settingsFrame,
            scale=0.05,
            pos=(0.05, 0.55),
            fg=(1, 1, 1, 1),
        )
        self.shipHealthSlider = DirectSlider(
            parent=self.settingsFrame,
            range=(1, 32),
            pageSize=1,
            scale=0.15,
            pos=(0.05, 0, 0.485),
            command=updateGuiValues,
        )

        self.shipHitRadiusTitle = OnscreenText(
            text=f"Ship Hitbox Radius: 3",
            parent=self.settingsFrame,
            scale=0.05,
            pos=(0.05, 0.4),
            fg=(1, 1, 1, 1),
        )
        self.shipHitRadiusSlider = DirectSlider(
            parent=self.settingsFrame,
            range=(3, 15),
            pageSize=1,
            scale=0.15,
            pos=(0.05, 0, 0.335),
            command=updateGuiValues,
        )

        self.droneHitRadiusTitle = OnscreenText(
            text=f"Drone Hitbox Radius: 3",
            parent=self.settingsFrame,
            scale=0.05,
            pos=(0.05, 0.25),
            fg=(1, 1, 1, 1),
        )
        self.droneHitRadiusSlider = DirectSlider(
            parent=self.settingsFrame,
            range=(3, 15),
            pageSize=1,
            scale=0.15,
            pos=(0.05, 0, 0.175),
            command=updateGuiValues,
        )

        self.droneNumTitle = OnscreenText(
            text=f"Number of Drones:",
            parent=self.settingsFrame,
            scale=0.05,
            pos=(0.05, 0.05),
            fg=(1, 1, 1, 1),
        )
        self.droneNum = DirectEntry(
            parent=self.settingsFrame,
            scale=0.05,
            pos=(-0.15, 0, -0.05),
            initialText="5",
            cursorKeys=True,
            focusOutCommand=updateGuiValues,
        )

        self.droneHealthTitle = OnscreenText(
            text=f"Drone Hit Points: 1",
            parent=self.settingsFrame,
            scale=0.05,
            pos=(0.05, -0.225),
            fg=(1, 1, 1, 1),
        )
        self.droneHealthSlider = DirectSlider(
            parent=self.settingsFrame,
            range=(1, 32),
            pageSize=1,
            scale=0.15,
            pos=(0.05, 0, -0.3),
            command=updateGuiValues,
        )


class GUI:
    def start(self, render, _main, TransparencyAttrib):
        self.guiFrame = DirectFrame(parent=render)
        self.render = render
        self.main = _main
        self.TransparencyAttrib = TransparencyAttrib
        global main, guiClass
        main = _main
        guiClass = self

    def setup(self):
        borderFrame = self.main.loader.loadTexture("src/textures/GUI/bar.png")
        self.border = OnscreenImage(
            image=borderFrame,
            parent=self.guiFrame,
            scale=(1.75 * (monitor[0].height / monitor[0].width), 1, 0.15),
            pos=(0, 0, -0.9),
        )
        self.border.setTransparency(self.TransparencyAttrib.MAlpha)
        self.border.hide()
        self.main.crosshair = OnscreenImage(
            image="src/textures/crosshairs.png",
            pos=(0, 0, 0),
            scale=(0.03 * (monitor[0].height / monitor[0].width), 0.03, 0.03),
            parent=self.guiFrame,
        )
        self.main.crosshair.setTransparency(self.TransparencyAttrib.MAlpha)
        self.main.crosshair.hide()

        self.main.HpIndicator = DirectWaitBar(
            parent=self.guiFrame,
            value=0,
            scale=(0.25, 1, 0.5),
            pos=(0, 0, -0.9),
            barColor=(1, 0, 0, 1),
        )
        self.main.displayOverlay = DirectFrame(parent=self.guiFrame)

    def miniMap(self):
        self.mapFrame = DirectFrame(
            parent=guiClass.guiFrame,
            pos=(0.9, 1, 0.9),
            scale=(0.3),
        )
        self.mapGeom = main.loader.loadModel("src/models/circle_grid/mesh.bam")
        self.mapGeom.reparentTo(self.mapFrame)
        self.mapGeom.setHpr(0, 90, 0)
        self.mapGeom.setScale(
            0.025 / (monitor[0].width / monitor[0].height),
            0.025 / (monitor[0].width / monitor[0].height),
            0.025,
        )
