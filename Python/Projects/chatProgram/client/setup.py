from setuptools import setup

setup(
    name="chatt",
    options={
        "build_apps": {
            # Build asteroids.exe as a GUI application
            "gui_apps": {
                "chatt": "chatProgram.py",
            },
            # Set up output logging, important for GUI apps!
            "log_filename": "$USER_APPDATA/chatt/Logs/output.log",
            "log_append": False,
            # "prefer_discrete_gpu": True,
            # Specify which files are included with the distribution
            # "include_patterns": [
            #     "**/*.png",
            #     "**/*.jpg",
            #     "**/*.egg",
            #     "**/*.ttf",
            #     "**/*.fbx",
            #     "**/*.mp3",
            #     "**/*.wav",
            #     "**/*.prc",
            #     "**/*.dat",
            #     "**/*.dat1",
            #     "userPref.txt",
            # ],
            # Include the OpenGL renderer and OpenAL audio plug-in
            "plugins": [
                "pandagl",
                "p3openal_audio",
            ],
            #"platforms": ["win_amd64", "darwin"],
        }
    },
)
