from direct.filter.CommonFilters import CommonFilters
from direct.gui.DirectGui import *

monitor = None


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
