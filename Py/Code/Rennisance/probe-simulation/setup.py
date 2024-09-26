from setuptools import setup

setup(
    name="Probe Destruction 3000",
    options={
        "build_apps": {
            "gui_apps": {
                "Probe Destruction 3000": "launch.py",
            },
            "log_filename": "$USER_APPDATA/Probe Destruction 3000/Logs/output.log",
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
                "**/*.ptf",
            ],
            "plugins": [
                "pandagl",
                "p3openal_audio",
            ],
            "icons": {
                "Probe Destruction 3000": ["icon.jpg"],
            },
            "platforms": [
                "win_amd64",
                # "manylinux2014_x86_64"
            ],
            "include_modules": ["src"],
            "use_optimized_wheels": False,
        }
    },
)
