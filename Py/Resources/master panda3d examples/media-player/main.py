#!/usr/bin/env python

from panda3d.core import *
# Tell Panda3D to use OpenAL, not FMOD
loadPrcFileData("", "audio-library-name p3openal_audio")

from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase


class MediaPlayer():
    def __init__(self, media_file):
        self.tex = MovieTexture("name")
        success = self.tex.read(media_file)
        assert success, "Failed to load video!"
        cm = CardMaker("fullscreenCard")
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)
        card = NodePath(cm.generate())
        card.reparentTo(self.render2d)
        card.setTexture(self.tex)

    def stop(self):
        self.tex.stop()

    def play(self):
        self.tex.play()

player = MediaPlayer("PandaSneezes.ogv")
player.run()
