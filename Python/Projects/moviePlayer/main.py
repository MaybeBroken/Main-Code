import sys
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase

if sys.platform == "win32":
    from tkinter import filedialog
elif sys.platform == "darwin":
    from PyQt5.QtWidgets import QApplication, QFileDialog


class MediaPlayer(ShowBase):
    def __init__(self, media_file):
        ShowBase.__init__(self)
        self.tex = MovieTexture("name")
        success = self.tex.read(media_file)
        assert success, "Failed to load video!"
        cm = CardMaker("fullscreenCard")
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)
        card = self.render2d.attachNewNode(cm.generate())
        card.setTexture(self.tex)
        self.tex.play()


def get_media_file():
    if sys.platform == "win32":
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.ogv *.mp4 *.avi *.mov *.mkv")],
        )
    elif sys.platform == "darwin":
        app = QApplication(sys.argv)
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None, "Select Video File", "", "Video Files (*.ogv *.mp4 *.avi *.mov *.mkv)"
        )
        app.quit()
    return file_path


if __name__ == "__main__":
    media_file = get_media_file()
    if media_file:
        player = MediaPlayer(media_file)
        player.run()
    else:
        print("No file selected.")
