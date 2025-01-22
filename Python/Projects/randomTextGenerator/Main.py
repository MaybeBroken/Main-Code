from attr import s
from panda3d.core import *
from panda3d.core import TextNode, loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
import random
from time import sleep
from direct.stdpy.threading import Thread
from clipboard import copy
loadPrcFileData("", "window-title Random Text Generator\nnotify-level-text fatal\n")


def generate_random_string(length, ascii_range: list[2]):
    """
    Generates a random string of a specified length using printable ASCII characters.

    Parameters:
        length (int): The length of the random string to generate.

    Returns:
        str: The generated random string.
    """
    try:
        ascii_chars = [chr(i) for i in range(int(ascii_range[0]), int(ascii_range[1]))]
        return r"".join(random.choice(ascii_chars) for _ in range(int(length)))
    except Exception as e:
        return f"Error: {e}"


class generator(ShowBase):
    def __init__(self):
        super().__init__()
        self.setBackgroundColor(0, 0, 0)
        self.textFrame = OnscreenText(
            "", scale=0.06, align=TextNode.ACenter, pos=(0, 0), fg=(1, 1, 1, 1)
        )
        self.speedSlider = DirectSlider(
            text="Speed",
            text_scale=0.15,
            text_pos=(0, 0.1),
            text_fg=(1, 1, 1, 1),
            range=(10, 100),
            value=50,
            scale=0.4,
            pos=(0, 0, -0.9),
            command=self.setSpeed,
        )
        self.rangeSlider1 = DirectSlider(
            text="Range 1",
            text_scale=0.15,
            text_pos=(0, 0.1),
            text_fg=(1, 1, 1, 1),
            range=(32, 300),
            value=32,
            scale=0.4,
            pos=(0, 0, -0.8),
            command=self.setRange,
        )
        self.rangeSlider2 = DirectSlider(
            text="Range 2",
            text_scale=0.15,
            text_pos=(0, 0.1),
            text_fg=(1, 1, 1, 1),
            range=(32, 300),
            value=127,
            scale=0.4,
            pos=(0, 0, -0.7),
            command=self.setRange,
        )
        self.lengthSlider = DirectSlider(
            text="Length",
            text_scale=0.15,
            text_pos=(0, 0.1),
            text_fg=(1, 1, 1, 1),
            range=(1, 100),
            value=5,
            scale=0.4,
            pos=(0, 0, -0.6),
            command=self.setLength,
        )
        self.speed = 50
        self.range = [32, 127]
        self.length = 5
        self.update_thread = Thread(target=self.update)
        self.update_thread.start()

    def setSpeed(self):
        self.speed = self.speedSlider["value"]

    def setRange(self):
        self.range = [self.rangeSlider1["value"], self.rangeSlider2["value"]]

    def setLength(self):
        self.length = self.lengthSlider["value"]

    def update(self):
        while True:
            sleep(1 / (self.speed + 0.01))
            self.textFrame.setText(generate_random_string(self.length, self.range))
            with open("randomText.txt", "w") as f:
                f.write(self.textFrame.getText())
            copy(self.textFrame.getText())


app = generator()
app.run()
