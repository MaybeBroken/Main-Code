from setuptools import setup

setup(
    name="ProbeSim",
    options={
        "build_apps": {
            "gui_apps": {
                "ProbeSim": "launch.py",
            },
            "log_filename": "$USER_APPDATA/ProbeSim/Logs/output.log",
            "log_append": False,
            "prefer_discrete_gpu": True,
            "include_patterns": [
                "**/*.png",
                "**/*.jpg",
                "**/*.egg",
                "**/*.bam",
                "**/*.glb",
                "**/*.mp3",
                "**/*.wav",
                "**/*.prc",
            ],
            "plugins": [
                "pandagl",
                "p3openal_audio",
            ],
            "icons": {
                "ProbeSim": ["icon.jpg"],
            },
            "platforms": ["win_amd64", "manylinux2014_x86_64"],
            "include_modules": ["src"],
        }
    },
)
