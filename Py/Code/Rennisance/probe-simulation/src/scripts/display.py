from direct.filter.CommonFilters import CommonFilters
from direct.gui.DirectGui import *
class ShaderCall():
    def setupShaders(self, mainApp, light, wantShaders):
        if wantShaders==True:
            mainApp.render.setShaderAuto()
            filters = CommonFilters(mainApp.win, mainApp.cam)
            filters.setBloom((0.3, 0.4, 0.3, 0.8), mintrigger=0.1, maxtrigger=1, desat=0.1, intensity=1.2, size='medium')
            # filters.setAmbientOcclusion()
            filters.setSrgbEncode()
            filters.setHighDynamicRange()
            filters.setBlurSharpen(1.5)

class GUI():
    def start(self, render, main, TransparencyAttrib):
        self.guiFrame = DirectFrame(parent=render)
        self.render = render
        self.main = main
        self.TransparencyAttrib = TransparencyAttrib
    def setup(self):
        borderFrame = self.main.loader.loadTexture('src/textures/GUI/bar.png')
        self.border = OnscreenImage(image=borderFrame, parent=self.guiFrame, scale=1)
        self.border.setTransparency(self.TransparencyAttrib.MAlpha)
        self.border.hide()
    def show(self):
        self.border.show()
        self.main.crosshairs.show()
    def hide(self):
        self.border.hide()
        self.main.crosshairs.hide()