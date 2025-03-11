import os
import pip
import sys
from time import sleep

try:
    import ebooklib.epub as epub
    import ebooklib.utils as utils
    import ebooklib.plugins as plugins
except ImportError:
    pip.main(["install", "ebooklib"])
    import ebooklib.epub as epub
    import ebooklib.utils as utils
    import ebooklib.plugins as plugins
try:
    from panda3d.core import *
    from panda3d.core import (
        TextNode,
    )
    from direct.showbase.ShowBase import ShowBase
    from direct.gui.DirectGui import *
    from direct.stdpy.threading import Thread
except ImportError:
    pip.main(["install", "panda3d"])
    from panda3d.core import *
    from panda3d.core import loadPrcFileData
    from panda3d.core import (
        TextNode,
    )
    from direct.showbase.ShowBase import ShowBase
    from direct.gui.DirectGui import *
    from direct.stdpy.threading import Thread
import warnings
import cleanify

try:
    from bs4 import BeautifulSoup
except ImportError:
    pip.main(["install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
os.chdir(os.path.dirname(__file__))
loadPrcFileData(  # type: ignore
    "",
    f"want-pstats 0\nfullscreen 0\nundecorated 0\nwindow-title eBook Reader\n",
)

if sys.platform == "win32":
    try:
        from tkinter import filedialog
    except ImportError:
        pip.main(["install", "tkinter"])
        from tkinter import filedialog
elif sys.platform == "darwin":
    try:
        from PyQt5.QtWidgets import QApplication, QFileDialog
    except ImportError:
        pip.main(["install", "PyQt5"])
        from PyQt5.QtWidgets import QApplication, QFileDialog


def divideWithRemainder(num, divisor) -> tuple[2]:
    result = 0
    remainder = 0
    while num >= divisor:
        num -= divisor
        result += 1
    remainder = num
    return (
        result,
        remainder,
    )


def word_wrap(text, chars_to_wrap, lines_per_page=10, want_pagination=True):
    """Wraps text to fit within a specified number of characters per line and handles pagination.

    Parameters:
        text (str): The text to wrap.
        chars_to_wrap (int): The maximum number of characters per line.
        lines_per_page (int): The number of lines per page.

    Returns:
        str: The wrapped text with pagination.
    """
    wrapped_text = ""
    lines = text.split("\n")
    for line in lines:
        words = line.split(" ")
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 > chars_to_wrap:
                wrapped_text += current_line.rstrip() + "\n"
                current_line = word + " "
            else:
                current_line += word + " "
        wrapped_text += current_line.rstrip() + "\n"
    if want_pagination:

        # Handle pagination
        lines = wrapped_text.split("\n")
        paginated_text = []
        if len(lines) > lines_per_page:
            for pageIndex in range(divideWithRemainder(len(lines), lines_per_page)[0]):
                paginated_text.append(
                    "\n".join(
                        lines[
                            pageIndex
                            * lines_per_page : (pageIndex + 1)
                            * lines_per_page
                        ]
                    )
                    + "\n\n"
                )
        return paginated_text
    else:
        return wrapped_text


def parse_html_string(html_string):
    """Parses an HTML string and returns a list of text content from the body.

    Args:
        html_string (str): The HTML string to parse.

    Returns:
        list: A list of text content from the body.
    """
    soup = BeautifulSoup(html_string, "html.parser")
    html_string = soup.get_text()
    return html_string


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0.1, 0.1, 0.1, 1)
        self.bookTextNode = OnscreenText()
        self.bookTextNode.setAlign(TextNode.ALeft)
        self.bookTextNode.setScale(0.05)
        self.bookTextNode.setPos(-1, 0.75)
        self.bookTextNode.setFg((1, 1, 1, 1))
        self.progressText = OnscreenText()
        self.progressText.setScale(0.05)
        self.progressText.setPos(0, -0.8)
        self.progressText.setAlign(TextNode.ACenter)
        self.progressText.setFg((1, 1, 1, 1))
        self.pageIndex = 0
        self.runningRepeatArrow = False
        self.accept(
            "arrow_up",
            self.arrow_up,
        )
        self.accept(
            "arrow_down",
            self.arrow_down,
        )
        self.accept(
            "arrow_left",
            self.arrow_up,
        )
        self.accept(
            "arrow_right",
            self.arrow_down,
        )
        self.accept("arrow_left-repeat", self.arrow_up_repeat)
        self.accept("arrow_right-repeat", self.arrow_down_repeat)
        self.accept("arrow_up-repeat", self.arrow_up_repeat)
        self.accept("arrow_down-repeat", self.arrow_down_repeat)
        self.accept("wheel_up", self.arrow_up)
        self.accept("wheel_down", self.arrow_down)
        self.accept(
            "shift-arrow_left-repeat", lambda: [self.arrow_up() for _ in range(3)]
        )
        self.accept(
            "shift-arrow_right-repeat", lambda: [self.arrow_down() for _ in range(3)]
        )
        self.accept(
            "shift-arrow_up-repeat", lambda: [self.arrow_up() for _ in range(3)]
        )
        self.accept(
            "shift-arrow_down-repeat", lambda: [self.arrow_down() for _ in range(3)]
        )
        self.accept("q", exit)
        if sys.platform == "win32":
            self.book = parse_html_string(self.load_book(filedialog.askopenfilename()))
        elif sys.platform == "darwin":
            app = QApplication(sys.argv)
            self.book = parse_html_string(
                self.load_book(QFileDialog.getOpenFileName()[0])
            )
        self.book = cleanify.Purger(
            cleanify.EbookContext(
                rating="G",
                AiRevision=False,
                AiRecursiveRevisionLevel=1,
                AiRevisionModel="GPT-3.5",
            )
        ).cleanify(self.book)
        self.book = word_wrap(self.book, 90, 30)
        self.bookTextNode.setText(self.book[self.pageIndex])
        self.progressText.setText(
            f"Page {self.pageIndex + 1} of {len(self.book)}\nPress q to quit"
        )

    def arrow_up(self):
        sleep(0.01)
        if self.pageIndex - 1 >= 0:
            self.pageIndex -= 1
            self.bookTextNode.setText(self.book[self.pageIndex])
            self.progressText.setText(
                f"Page {self.pageIndex + 1} of {len(self.book)}\nPress q to quit"
            )

    def arrow_down(self):
        if self.pageIndex + 1 < len(self.book):
            self.pageIndex += 1
            self.bookTextNode.setText(self.book[self.pageIndex])
            self.progressText.setText(
                f"Page {self.pageIndex + 1} of {len(self.book)}\nPress q to quit"
            )

    def arrow_up_repeat(self):
        self.arrow_up()
        sleep(0.05)
        return 0

    def arrow_down_repeat(self):
        self.arrow_down()
        sleep(0.05)
        return 0

    def load_book(self, book_path):
        book = epub.read_epub(book_path)
        text = ""
        for item in book.get_items():
            if isinstance(item, epub.EpubHtml):
                text += item.get_body_content().decode("utf-8")
        return text


Main().run()
