from math import pi
import os
import random


def getDistance(pointA, pointB):
    if pointA > 0 and pointB < 0 or pointA < 0 and pointB < 0:
        return pointA - pointB
    elif pointA > 0 and pointB > 0 or pointA < 0 and pointB > 0:
        return pointA + pointB


def degToRad(degrees):
    return degrees * (pi / 180.0)


def curl(url, filepath):
    os.system(f"curl -o {filepath} {url}")


def randomText(len): ...


def divideWithRemainder(num, divisor) -> list[2]:
    result = 0
    remainder = 0
    while num >= divisor:
        num -= divisor
        result += 1
    remainder = num
    return [
        result if len(str(result)) > 1 else f"0{result}",
        remainder if len(str(remainder)) > 1 else f"0{remainder}",
    ]


class CLI:
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


class COLORS_RGB:

    _dict = {
        "aliceblue": [
            240,
            248,
            255,
            1,
        ],
        "antiquewhite": [
            250,
            235,
            215,
            1,
        ],
        "aqua": [
            0,
            255,
            255,
            1,
        ],
        "aquamarine": [
            127,
            255,
            212,
            1,
        ],
        "azure": [
            240,
            255,
            255,
            1,
        ],
        "beige": [
            245,
            245,
            220,
            1,
        ],
        "bisque": [
            255,
            228,
            196,
            1,
        ],
        "black": [
            0,
            0,
            0,
            1,
        ],
        "blanchedalmond": [
            255,
            235,
            205,
            1,
        ],
        "blue": [
            0,
            0,
            255,
            1,
        ],
        "blueviolet": [
            138,
            43,
            226,
            1,
        ],
        "brown": [
            165,
            42,
            42,
            1,
        ],
        "burlywood": [
            222,
            184,
            135,
            1,
        ],
        "cadetblue": [
            95,
            158,
            160,
            1,
        ],
        "chartreuse": [
            127,
            255,
            0,
            1,
        ],
        "chocolate": [
            210,
            105,
            30,
            1,
        ],
        "coral": [
            255,
            127,
            80,
            1,
        ],
        "cornflowerblue": [
            100,
            149,
            237,
            1,
        ],
        "cornsilk": [
            255,
            248,
            220,
            1,
        ],
        "crimson": [
            220,
            20,
            60,
            1,
        ],
        "cyan": [
            0,
            255,
            255,
            1,
        ],
        "darkblue": [
            0,
            0,
            139,
            1,
        ],
        "darkcyan": [
            0,
            139,
            139,
            1,
        ],
        "darkgoldenrod": [
            184,
            134,
            11,
            1,
        ],
        "darkgray": [
            169,
            169,
            169,
            1,
        ],
        "darkgreen": [
            0,
            100,
            0,
            1,
        ],
        "darkgrey": [
            169,
            169,
            169,
            1,
        ],
        "darkkhaki": [
            189,
            183,
            107,
            1,
        ],
        "darkmagenta": [
            139,
            0,
            139,
            1,
        ],
        "darkolivegreen": [
            85,
            107,
            47,
            1,
        ],
        "darkorange": [
            255,
            140,
            0,
            1,
        ],
        "darkorchid": [
            153,
            50,
            204,
            1,
        ],
        "darkred": [
            139,
            0,
            0,
            1,
        ],
        "darksalmon": [
            233,
            150,
            122,
            1,
        ],
        "darkseagreen": [
            143,
            188,
            143,
            1,
        ],
        "darkslateblue": [
            72,
            61,
            139,
            1,
        ],
        "darkslategray": [
            47,
            79,
            79,
            1,
        ],
        "darkslategrey": [
            47,
            79,
            79,
            1,
        ],
        "darkturquoise": [
            0,
            206,
            209,
            1,
        ],
        "darkviolet": [
            148,
            0,
            211,
            1,
        ],
        "deeppink": [
            255,
            20,
            147,
            1,
        ],
        "deepskyblue": [
            0,
            191,
            255,
            1,
        ],
        "dimgray": [
            105,
            105,
            105,
            1,
        ],
        "dimgrey": [
            105,
            105,
            105,
            1,
        ],
        "dodgerblue": [
            30,
            144,
            255,
            1,
        ],
        "firebrick": [
            178,
            34,
            34,
            1,
        ],
        "floralwhite": [
            255,
            250,
            240,
            1,
        ],
        "forestgreen": [
            34,
            139,
            34,
            1,
        ],
        "fuchsia": [
            255,
            0,
            255,
            1,
        ],
        "gainsboro": [
            220,
            220,
            220,
            1,
        ],
        "ghostwhite": [
            248,
            248,
            255,
            1,
        ],
        "gold": [
            255,
            215,
            0,
            1,
        ],
        "goldenrod": [
            218,
            165,
            32,
            1,
        ],
        "gray": [
            128,
            128,
            128,
            1,
        ],
        "green": [
            0,
            128,
            0,
            1,
        ],
        "greenyellow": [
            173,
            255,
            47,
            1,
        ],
        "grey": [
            128,
            128,
            128,
            1,
        ],
        "honeydew": [
            240,
            255,
            240,
            1,
        ],
        "hotpink": [
            255,
            105,
            180,
            1,
        ],
        "indianred": [
            205,
            92,
            92,
            1,
        ],
        "indigo": [
            75,
            0,
            130,
            1,
        ],
        "ivory": [
            255,
            255,
            240,
            1,
        ],
        "khaki": [
            240,
            230,
            140,
            1,
        ],
        "lavender": [
            230,
            230,
            250,
            1,
        ],
        "lavenderblush": [
            255,
            240,
            245,
            1,
        ],
        "lawngreen": [
            124,
            252,
            0,
            1,
        ],
        "lemonchiffon": [
            255,
            250,
            205,
            1,
        ],
        "lightblue": [
            173,
            216,
            230,
            1,
        ],
        "lightcoral": [
            240,
            128,
            128,
            1,
        ],
        "lightcyan": [
            224,
            255,
            255,
            1,
        ],
        "lightgoldenrodyellow": [
            250,
            250,
            210,
            1,
        ],
        "lightgray": [
            211,
            211,
            211,
            1,
        ],
        "lightgreen": [
            144,
            238,
            144,
            1,
        ],
        "lightgrey": [
            211,
            211,
            211,
            1,
        ],
        "lightpink": [
            255,
            182,
            193,
            1,
        ],
        "lightsalmon": [
            255,
            160,
            122,
            1,
        ],
        "lightseagreen": [
            32,
            178,
            170,
            1,
        ],
        "lightskyblue": [
            135,
            206,
            250,
            1,
        ],
        "lightslategray": [
            119,
            136,
            153,
            1,
        ],
        "lightslategrey": [
            119,
            136,
            153,
            1,
        ],
        "lightsteelblue": [
            176,
            196,
            222,
            1,
        ],
        "lightyellow": [
            255,
            255,
            224,
            1,
        ],
        "lime": [
            0,
            255,
            0,
            1,
        ],
        "limegreen": [
            50,
            205,
            50,
            1,
        ],
        "linen": [
            250,
            240,
            230,
            1,
        ],
        "magenta": [
            255,
            0,
            255,
            1,
        ],
        "maroon": [
            128,
            0,
            0,
            1,
        ],
        "mediumaquamarine": [
            102,
            205,
            170,
            1,
        ],
        "mediumblue": [
            0,
            0,
            205,
            1,
        ],
        "mediumorchid": [
            186,
            85,
            211,
            1,
        ],
        "mediumpurple": [
            147,
            112,
            219,
            1,
        ],
        "mediumseagreen": [
            60,
            179,
            113,
            1,
        ],
        "mediumslateblue": [
            123,
            104,
            238,
            1,
        ],
        "mediumspringgreen": [
            0,
            250,
            154,
            1,
        ],
        "mediumturquoise": [
            72,
            209,
            204,
            1,
        ],
        "mediumvioletred": [
            199,
            21,
            133,
            1,
        ],
        "midnightblue": [
            25,
            25,
            112,
            1,
        ],
        "mintcream": [
            245,
            255,
            250,
            1,
        ],
        "mistyrose": [
            255,
            228,
            225,
            1,
        ],
        "moccasin": [
            255,
            228,
            181,
            1,
        ],
        "navajowhite": [
            255,
            222,
            173,
            1,
        ],
        "navy": [
            0,
            0,
            128,
            1,
        ],
        "oldlace": [
            253,
            245,
            230,
            1,
        ],
        "olive": [
            128,
            128,
            0,
            1,
        ],
        "olivedrab": [
            107,
            142,
            35,
            1,
        ],
        "orange": [
            255,
            165,
            0,
            1,
        ],
        "orangered": [
            255,
            69,
            0,
            1,
        ],
        "orchid": [
            218,
            112,
            214,
            1,
        ],
        "palegoldenrod": [
            238,
            232,
            170,
            1,
        ],
        "palegreen": [
            152,
            251,
            152,
            1,
        ],
        "paleturquoise": [
            175,
            238,
            238,
            1,
        ],
        "palevioletred": [
            219,
            112,
            147,
            1,
        ],
        "papayawhip": [
            255,
            239,
            213,
            1,
        ],
        "peachpuff": [
            255,
            218,
            185,
            1,
        ],
        "peru": [
            205,
            133,
            63,
            1,
        ],
        "pink": [
            255,
            192,
            203,
            1,
        ],
        "plum": [
            221,
            160,
            221,
            1,
        ],
        "powderblue": [
            176,
            224,
            230,
            1,
        ],
        "purple": [
            128,
            0,
            128,
            1,
        ],
        "rebeccapurple": [
            102,
            51,
            153,
            1,
        ],
        "red": [
            255,
            0,
            0,
            1,
        ],
        "rosybrown": [
            188,
            143,
            143,
            1,
        ],
        "royalblue": [
            65,
            105,
            225,
            1,
        ],
        "saddlebrown": [
            139,
            69,
            19,
            1,
        ],
        "salmon": [
            250,
            128,
            114,
            1,
        ],
        "sandybrown": [
            244,
            164,
            96,
            1,
        ],
        "seagreen": [
            46,
            139,
            87,
            1,
        ],
        "seashell": [
            255,
            245,
            238,
            1,
        ],
        "sienna": [
            160,
            82,
            45,
            1,
        ],
        "silver": [
            192,
            192,
            192,
            1,
        ],
        "skyblue": [
            135,
            206,
            235,
            1,
        ],
        "slateblue": [
            106,
            90,
            205,
            1,
        ],
        "slategray": [
            112,
            128,
            144,
            1,
        ],
        "slategrey": [
            112,
            128,
            144,
            1,
        ],
        "snow": [
            255,
            250,
            250,
            1,
        ],
        "springgreen": [
            0,
            255,
            127,
            1,
        ],
        "steelblue": [
            70,
            130,
            180,
            1,
        ],
        "tan": [
            210,
            180,
            140,
            1,
        ],
        "teal": [
            0,
            128,
            128,
            1,
        ],
        "thistle": [
            216,
            191,
            216,
            1,
        ],
        "tomato": [
            255,
            99,
            71,
            1,
        ],
        "turquoise": [
            64,
            224,
            208,
            1,
        ],
        "violet": [
            238,
            130,
            238,
            1,
        ],
        "wheat": [
            245,
            222,
            179,
            1,
        ],
        "white": [
            255,
            255,
            255,
            1,
        ],
        "whitesmoke": [
            245,
            245,
            245,
            1,
        ],
        "yellow": [
            255,
            255,
            0,
            1,
        ],
        "yellowgreen": [
            154,
            205,
            50,
            1,
        ],
    }

    _list = [
        ["aliceblue", [240, 248, 255]],
        ["antiquewhite", [250, 235, 215]],
        ["aqua", [0, 255, 255]],
        ["aquamarine", [127, 255, 212]],
        ["azure", [240, 255, 255]],
        ["beige", [245, 245, 220]],
        ["bisque", [255, 228, 196]],
        ["black", [0, 0, 0]],
        ["blanchedalmond", [255, 235, 205]],
        ["blue", [0, 0, 255]],
        ["blueviolet", [138, 43, 226]],
        ["brown", [165, 42, 42]],
        ["burlywood", [222, 184, 135]],
        ["cadetblue", [95, 158, 160]],
        ["chartreuse", [127, 255, 0]],
        ["chocolate", [210, 105, 30]],
        ["coral", [255, 127, 80]],
        ["cornflowerblue", [100, 149, 237]],
        ["cornsilk", [255, 248, 220]],
        ["crimson", [220, 20, 60]],
        ["cyan", [0, 255, 255]],
        ["darkblue", [0, 0, 139]],
        ["darkcyan", [0, 139, 139]],
        ["darkgoldenrod", [184, 134, 11]],
        ["darkgray", [169, 169, 169]],
        ["darkgreen", [0, 100, 0]],
        ["darkgrey", [169, 169, 169]],
        ["darkkhaki", [189, 183, 107]],
        ["darkmagenta", [139, 0, 139]],
        ["darkolivegreen", [85, 107, 47]],
        ["darkorange", [255, 140, 0]],
        ["darkorchid", [153, 50, 204]],
        ["darkred", [139, 0, 0]],
        ["darksalmon", [233, 150, 122]],
        ["darkseagreen", [143, 188, 143]],
        ["darkslateblue", [72, 61, 139]],
        ["darkslategray", [47, 79, 79]],
        ["darkslategrey", [47, 79, 79]],
        ["darkturquoise", [0, 206, 209]],
        ["darkviolet", [148, 0, 211]],
        ["deeppink", [255, 20, 147]],
        ["deepskyblue", [0, 191, 255]],
        ["dimgray", [105, 105, 105]],
        ["dimgrey", [105, 105, 105]],
        ["dodgerblue", [30, 144, 255]],
        ["firebrick", [178, 34, 34]],
        ["floralwhite", [255, 250, 240]],
        ["forestgreen", [34, 139, 34]],
        ["fuchsia", [255, 0, 255]],
        ["gainsboro", [220, 220, 220]],
        ["ghostwhite", [248, 248, 255]],
        ["gold", [255, 215, 0]],
        ["goldenrod", [218, 165, 32]],
        ["gray", [128, 128, 128]],
        ["green", [0, 128, 0]],
        ["greenyellow", [173, 255, 47]],
        ["grey", [128, 128, 128]],
        ["honeydew", [240, 255, 240]],
        ["hotpink", [255, 105, 180]],
        ["indianred", [205, 92, 92]],
        ["indigo", [75, 0, 130]],
        ["ivory", [255, 255, 240]],
        ["khaki", [240, 230, 140]],
        ["lavender", [230, 230, 250]],
        ["lavenderblush", [255, 240, 245]],
        ["lawngreen", [124, 252, 0]],
        ["lemonchiffon", [255, 250, 205]],
        ["lightblue", [173, 216, 230]],
        ["lightcoral", [240, 128, 128]],
        ["lightcyan", [224, 255, 255]],
        ["lightgoldenrodyellow", [250, 250, 210]],
        ["lightgray", [211, 211, 211]],
        ["lightgreen", [144, 238, 144]],
        ["lightgrey", [211, 211, 211]],
        ["lightpink", [255, 182, 193]],
        ["lightsalmon", [255, 160, 122]],
        ["lightseagreen", [32, 178, 170]],
        ["lightskyblue", [135, 206, 250]],
        ["lightslategray", [119, 136, 153]],
        ["lightslategrey", [119, 136, 153]],
        ["lightsteelblue", [176, 196, 222]],
        ["lightyellow", [255, 255, 224]],
        ["lime", [0, 255, 0]],
        ["limegreen", [50, 205, 50]],
        ["linen", [250, 240, 230]],
        ["magenta", [255, 0, 255]],
        ["maroon", [128, 0, 0]],
        ["mediumaquamarine", [102, 205, 170]],
        ["mediumblue", [0, 0, 205]],
        ["mediumorchid", [186, 85, 211]],
        ["mediumpurple", [147, 112, 219]],
        ["mediumseagreen", [60, 179, 113]],
        ["mediumslateblue", [123, 104, 238]],
        ["mediumspringgreen", [0, 250, 154]],
        ["mediumturquoise", [72, 209, 204]],
        ["mediumvioletred", [199, 21, 133]],
        ["midnightblue", [25, 25, 112]],
        ["mintcream", [245, 255, 250]],
        ["mistyrose", [255, 228, 225]],
        ["moccasin", [255, 228, 181]],
        ["navajowhite", [255, 222, 173]],
        ["navy", [0, 0, 128]],
        ["oldlace", [253, 245, 230]],
        ["olive", [128, 128, 0]],
        ["olivedrab", [107, 142, 35]],
        ["orange", [255, 165, 0]],
        ["orangered", [255, 69, 0]],
        ["orchid", [218, 112, 214]],
        ["palegoldenrod", [238, 232, 170]],
        ["palegreen", [152, 251, 152]],
        ["paleturquoise", [175, 238, 238]],
        ["palevioletred", [219, 112, 147]],
        ["papayawhip", [255, 239, 213]],
        ["peachpuff", [255, 218, 185]],
        ["peru", [205, 133, 63]],
        ["pink", [255, 192, 203]],
        ["plum", [221, 160, 221]],
        ["powderblue", [176, 224, 230]],
        ["purple", [128, 0, 128]],
        ["rebeccapurple", [102, 51, 153]],
        ["red", [255, 0, 0]],
        ["rosybrown", [188, 143, 143]],
        ["royalblue", [65, 105, 225]],
        ["saddlebrown", [139, 69, 19]],
        ["salmon", [250, 128, 114]],
        ["sandybrown", [244, 164, 96]],
        ["seagreen", [46, 139, 87]],
        ["seashell", [255, 245, 238]],
        ["sienna", [160, 82, 45]],
        ["silver", [192, 192, 192]],
        ["skyblue", [135, 206, 235]],
        ["slateblue", [106, 90, 205]],
        ["slategray", [112, 128, 144]],
        ["slategrey", [112, 128, 144]],
        ["snow", [255, 250, 250]],
        ["springgreen", [0, 255, 127]],
        ["steelblue", [70, 130, 180]],
        ["tan", [210, 180, 140]],
        ["teal", [0, 128, 128]],
        ["thistle", [216, 191, 216]],
        ["tomato", [255, 99, 71]],
        ["turquoise", [64, 224, 208]],
        ["violet", [238, 130, 238]],
        ["wheat", [245, 222, 179]],
        ["white", [255, 255, 255]],
        ["whitesmoke", [245, 245, 245]],
        ["yellow", [255, 255, 0]],
        [
            "yellowgreen",
            [154, 205, 50],
        ],
    ]
