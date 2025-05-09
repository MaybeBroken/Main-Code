from setuptools import setup

setup(
    name="OP Media Player",
    options={
        "build_apps": {
            "gui_apps": {
                "op_media_player": "build.py",
            },
            "log_filename": "$USER_APPDATA/OPMediaPlayer/output.log",
            "log_append": False,
            "include_patterns": [
                "**/*.png",
                "**/*.jpg",
                "**/*.prc",
                "po-token-generator/**",
            ],
            "plugins": [
                "pandagl",
                "p3openal_audio",
            ],
            "prefer_discrete_gpu": True,
            "platforms": ["win_amd64"],
        }
    },
)
