gameVars = {
    "player": {
        "name": str,
        "walking": int,
        "casting": int,
        "active": int,
        "talking": int,
        "fighting": int,
        "alive": int,
        "age": int,
        "hp": int,
    },
    "TextFile": {
        "titles": {"Story 1": (0, 200), "Story 2": (200, 400), "Story 3": (400, 600)},
        "choices": {
            0: {
                "text": {"line0s"},
                "opts": {
                    0: {
                        "text": "None",
                        "command": {"name": "editPlayerConfig", "extraArgs": []},
                    }
                },
            }
        },
    },
}
winMode = "win"
resolution = [1920, 1080]
