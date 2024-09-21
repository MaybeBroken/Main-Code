from direct.filter.CommonFilters import CommonFilters
from direct.gui.DirectGui import *
from src.scripts.guiUtils import fade
from direct.directtools.DirectGrid import DirectGrid
from panda3d.core import deg2Rad
monitor = None
main = None
guiClass = None


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


class GUI:
    def start(self, render, _main, TransparencyAttrib, monitor_):
        self.guiFrame = DirectFrame(parent=render)
        self.render = render
        self.main = _main
        self.TransparencyAttrib = TransparencyAttrib
        global monitor, main, guiClass
        monitor = monitor_
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

        self.main.chargingScreen = DirectFrame(parent=self.guiFrame)
        self.main.progress = DirectWaitBar(
            parent=self.main.chargingScreen,
            value=0,
            scale=(0.95, 1, 0.75),
            pos=(0, 0, -0.9),
            barColor=(1, 0, 0, 1),
        )
        self.main.chargingScreen.hide()

    def show(self):
        # self.border.show()
        self.main.crosshair.show()
        self.main.chargingScreen.show()
        self.main.velocityMeter.hide()

    def hide(self):
        # self.border.hide()
        self.main.crosshair.hide()
        self.main.chargingScreen.hide()
        self.main.velocityMeter.show()

    def miniMap(self):
        self.mapFrame = DirectFrame(
                parent=guiClass.guiFrame,
                pos=(0.8, 1, 0.75),
                scale=(0.20, 0.20, 0.20),
            )
        self.mapGeom = main.loader.loadModel("src/models/circle_grid/mesh.bam")
        self.mapGeom.reparentTo(self.mapFrame)
        self.mapGeom.setHpr(90, 90, 90)
        self.mapGeom.setScale(0.025)