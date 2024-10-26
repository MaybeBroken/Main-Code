class Color:
    GREEN = "\033[92m"
    LIGHT_GREEN = "\033[1;92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    BOLD = "\033[;1m"
    CYAN = "\033[1;36m"
    LIGHT_CYAN = "\033[1;96m"
    LIGHT_GREY = "\033[1;37m"
    DARK_GREY = "\033[1;90m"
    BLACK = "\033[1;30m"
    WHITE = "\033[1;97m"
    INVERT = "\033[;7m"
    RESET = "\033[0m"
    ALL = [
        GREEN,
        LIGHT_GREEN,
        RED,
        YELLOW,
        BLUE,
        MAGENTA,
        BOLD,
        CYAN,
        LIGHT_CYAN,
        LIGHT_GREY,
        DARK_GREY,
        BLACK,
        WHITE,
        INVERT,
        RESET,
    ]

    def printAllColors(self):
        print(
            f"{self.GREEN}green{self.RESET}\n{self.LIGHT_GREEN}light green{self.RESET}\n{self.RED}red{self.RESET}\n{self.YELLOW}yellow{self.RESET}\n{self.BLUE}blue{self.RESET}\n{self.MAGENTA}magenta{self.RESET}\n{self.BOLD}bold{self.RESET}\n{self.CYAN}cyan{self.RESET}\n{self.LIGHT_CYAN}light cyan{self.RESET}\n{self.LIGHT_GREY}light grey{self.RESET}\n{self.DARK_GREY}dark grey{self.RESET}\n{self.BLACK}black{self.RESET}\n{self.WHITE}white{self.RESET}\n{self.INVERT}inverted{self.RESET}\n"
        )


class Control:
    def left(num):
        return f"\033[{num}D"

    def right(num):
        return f"\033[{num}C"

    def up(num):
        return f"\033[{num}A"

    def down(num):
        return f"\033[{num}B"

    def changeLineUp(line, len):
        return f"\033[{line}A\033[{len}D"

    def changeLineLeft(len):
        return f"\033[{1}A\033[{len}D"

    def changeLineRight(len):
        return f"\033[{1}A\033[{len}C"