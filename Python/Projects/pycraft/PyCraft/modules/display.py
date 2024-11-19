from posixpath import supports_unicode_filenames
from direct.gui.DirectGui import *
import PyCraft.modules.vars as Wvars
import PyCraft.modules.utils as utils
from direct.filter.CommonFilters import CommonFilters
class bar():
    def buildHotbar(self, main, textureAlias, Sprites:tuple, font, TextNode, aspect2d):
        hotbar = main.loader.loadTexture('PyCraft/src/UI/HUD/hotbar.png')
        hotbar.setMinfilter(textureAlias)
        hotbar.setMagfilter(textureAlias)
        selector = main.loader.loadTexture('PyCraft/src/UI/HUD/hotbar_selection.png')
        selector.setMinfilter(textureAlias)
        selector.setMagfilter(textureAlias)
        self.hotbarUI = DirectFrame(frameColor=(0, 0, 0, 1), pos=(0, 1, -.9), scale=1)
        self.frame = OnscreenImage(hotbar, parent=self.hotbarUI, scale=(0.85, 1, 0.1))
        self.frame.setTransparency(1)
        self.selectorNode = OnscreenImage(selector, parent=self.hotbarUI, scale=(0.11, 1, 0.105), pos=(-0.75, 1, 0))
        self.selectorNode.setTransparency(1)
        self.slotActors = [
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(-0.75, -1, 0)), 0],
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(-0.5625, -1, 0)), 1],
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(-0.375, -1, 0)), 2],
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(-0.1875, -1, 0)), 3],
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(0, -1, 0)), 4],
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(0.1875, -1, 0)), 5],
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(0.374, -1, 0)), 6],
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(0.561, -1, 0)), 7],
            [OnscreenImage(Sprites[0], parent=self.hotbarUI, scale=(0.11/1.7, 1, 0.105/1.7), pos=(0.745, -1, 0)), 8]
        ]
        self.slotText = [
            [TextNode('0'), 0],
            [TextNode('1'), 1],
            [TextNode('2'), 2],
            [TextNode('3'), 3],
            [TextNode('4'), 4],
            [TextNode('5'), 5],
            [TextNode('6'), 6],
            [TextNode('7'), 7],
            [TextNode('8'), 8]
        ]
        textNodePos = -0.74
        for text in self.slotText:
            textNodePath = aspect2d.attachNewNode(text[0])
            textNodePath.setScale(0.07)
            text[0].setFont(font)
            text[0].setAlign(TextNode.ACenter)
            textNodePath.setPos(textNodePos, 1, -0.95)
            textNodePos += 0.186

        
        self.actorSprites=Sprites
        self.updateHotbar(self=self)
    def updateHotbar(self):
        self.updateSelector(self=self)
        self.updateSlots(self=self)
        self.updateText(self=self)
    def updateSelector(self):
        pos = 1.49/(8/(Wvars.selectedSlot+1)) -.935
        self.selectorNode.configure(pos=(pos, 1, 0))
        Wvars.selectedBlock = Wvars.hotbar[Wvars.selectedSlot]
    def updateSlots(self):
        for slot in self.slotActors:
            try:
                slot[0].configure(image=self.actorSprites[utils.item_to_int(Wvars.hotbar[slot[1]])])
            except:
                None
            if Wvars.hotbarCt[slot[1]]==0:
                slot[0].hide()
            else:
                slot[0].show()
    def updateText(self):
        for slot in self.slotText:
            if Wvars.hotbarCt[slot[1]] == 0:
                slot[0].setText('')
            else:
                slot[0].setText(str(Wvars.hotbarCt[slot[1]]))

class Inventory():
    def addItem(self, item, amount):
        added = False
        try:
            slot = Wvars.hotbar.index(item)
            if Wvars.hotbarCt[slot] < 64:
                if item == Wvars.hotbar[slot] or Wvars.hotbarCt[slot] == 0:
                    Wvars.hotbarCt[slot] = Wvars.hotbarCt[slot] + amount
                    Wvars.hotbar[slot] = item
                    added = True
        except:
            None
        if added == False:
            for slot in range(len(Wvars.hotbar)):
                if Wvars.hotbarCt[slot] < 64:
                    if item == Wvars.hotbar[slot] or Wvars.hotbarCt[slot] == 0:
                        Wvars.hotbarCt[slot] = Wvars.hotbarCt[slot] + amount
                        Wvars.hotbar[slot] = item
                        added = True
                        break
        if added == False:
            for row in Wvars.inventory:
                for index in range(len(row)):
                    if Wvars.inventoryCt[row][index] < 64:
                        if item == Wvars.inventory[row][index] or Wvars.inventoryCt[row][index] == 0:
                            Wvars.inventoryCt[row][index] = Wvars.inventoryCt[row][index] + amount
                            Wvars.inventory[row][index] = item
                            added = True
                            break
        return added
    def removeOneItem_hotbar(self):
        if Wvars.hotbarCt[Wvars.selectedSlot] > 0:
            Wvars.hotbarCt[Wvars.selectedSlot] -= 1
            return True
        else:
            return False

class HUD():
    def drawInventoryFrames(self, mainApp, textureAlias, GeomSprites:tuple, font, TextNode, aspect2d):
        self.mainApp = mainApp
        self.GeomSprites = GeomSprites
        mainApp.releaseMouse()
        self.InventoryFrame = DirectFrame(frameColor=(0, 0, 0, 1), pos=(0, 1, 0), scale=.65)
        InventoryFrameSource = mainApp.loader.loadTexture('PyCraft/src/UI/HUD/inventory.png')
        InventoryFrameSource.setMinfilter(textureAlias)
        InventoryFrameSource.setMagfilter(textureAlias)
        self.InventoryFrameImg = OnscreenImage(image=InventoryFrameSource, parent=self.InventoryFrame)
        self.InventoryFrameImg.setTransparency(1)
        self._invButtons = [
            [[DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.8245, -1, -0.1)), 0],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.6125, -1, -0.1)), 1],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.4025, -1, -0.1)), 2],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.20125, -1, -0.1)), 3],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0, -1, -0.1)), 4],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.20125, -1, -0.1)), 5],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.4025, -1, -0.1)), 6],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.6125, -1, -0.1)), 7],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.8245, -1, -0.1)), 8]],

            [[DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.8245, -1, -0.325)), 0],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.6125, -1, -0.325)), 1],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.4025, -1, -0.325)), 2],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.20125, -1, -0.325)), 3],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0, -1, -0.325)), 4],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.20125, -1, -0.325)), 5],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.4025, -1, -0.325)), 6],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.6125, -1, -0.325)), 7],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.8245, -1, -0.325)), 8]],

            [[DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.8245, -1, -0.535)), 0],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.6125, -1, -0.535)), 1],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.4025, -1, -0.535)), 2],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(-0.20125, -1, -0.535)), 3],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0, -1, -0.535)), 4],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.20125, -1, -0.535)), 5],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.4025, -1, -0.535)), 6],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.6125, -1, -0.535)), 7],
            [DirectButton(parent=self.InventoryFrame, pressEffect=0, geom=(GeomSprites[0]), relief=None, scale=.09, pos=(0.8245, -1, -0.535)), 8]],
        ]
        bar.hotbarUI.hide()
        for text in bar.slotText:
            text[0].setText('')
        self.setupInventory(self=self)

    def updateInventoryFrame(self, frameNum:list=[0, 0]):
        if Wvars.inventoryCt[frameNum[0]][frameNum[1]] != 0:
            self._invButtons[frameNum[0]][frameNum[1]][0].show()
            self._invButtons[frameNum[0]][frameNum[1]][0].configure(geom=(self.GeomSprites[utils.item_to_int(Wvars.inventory[frameNum[0]][frameNum[1]])]))
        else:
            self._invButtons[frameNum[0]][frameNum[1]][0].hide()
    def setupInventory(self):
        for index1 in range(3):
            for index2 in range(9):
                if Wvars.inventoryCt[index1][index2] != 0:
                    self._invButtons[index1][index2][0].show()
                    self._invButtons[index1][index2][0].configure(geom=(self.GeomSprites[utils.item_to_int(Wvars.inventory[index1][index2])]))
                else:
                    self._invButtons[index1][index2][0].hide()

    def closeInventoryFrames(self):
        self.InventoryFrame.destroy()
        self.mainApp.captureMouse()
        bar.hotbarUI.show()



class ShaderCall():
    def setupShaders(self, mainApp, light):
        mainApp.render.setShaderAuto()
        filters = CommonFilters(mainApp.win, mainApp.cam)
        filters.setBloom((0.3, 0.4, 0.3, 0.8), mintrigger=0.2, maxtrigger=1, desat=0.5, intensity=1, size='medium')
        # filters.setAmbientOcclusion()
        filters.setSrgbEncode()
        filters.setHighDynamicRange()