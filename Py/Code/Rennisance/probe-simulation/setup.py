from setuptools import setup

setup(
    name='ProbeSim',
    options={
        'build_apps': {
            # Build asteroids.exe as a GUI application
            'gui_apps': {
                'ProbeSim': 'launch.py',
            },

            # Set up output logging, important for GUI apps!
            'log_filename': '$USER_APPDATA/ProbeSim/Logs/output.log',
            'log_append': False,
            'prefer_discrete_gpu':True,

            # Specify which files are included with the distribution
            'include_patterns': [
                '**/*.png',
                '**/*.jpg',
                '**/*.egg',
                '**/*.glb',
                '**/*.mp3',
                '**/*.wav',
                '**/*.prc'
            ],

            # Include the OpenGL renderer and OpenAL audio plug-in
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
            "icons": {
                # The key needs to match the key used in gui_apps/console_apps.
                # Alternatively, use "*" to set the icon for all apps.
                "ProbeSim": ['icon.jpg'],
            },
            'platforms': ['win_amd64'],
            'include_modules': ['src']
        }
    }
)