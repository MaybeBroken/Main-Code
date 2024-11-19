from setuptools import setup

setup(
    name='PyCraft',
    options={
        'build_apps': {
            # Build asteroids.exe as a GUI application
            'gui_apps': {
                'PyCraft': 'launch_PyCraft.py',
            },

            # Set up output logging, important for GUI apps!
            'log_filename': '$USER_APPDATA/PyCraft/Logs/output.log',
            'log_append': False,
            'prefer_discrete_gpu':True,

            # Specify which files are included with the distribution
            'include_patterns': [
                '**/*.png',
                '**/*.jpg',
                '**/*.egg',
                '**/*.ttf',
                '**/*.fbx',
                '**/*.mp3',
                '**/*.wav',
                '**/*.prc',
                '**/*.dat',
                '**/*.dat1',
                'userPref.txt'
            ],

            # Include the OpenGL renderer and OpenAL audio plug-in
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
            "icons": {
                # The key needs to match the key used in gui_apps/console_apps.
                # Alternatively, use "*" to set the icon for all apps.
                "PyCraft": ['PyCraft/src/Logo.png'],
            },
            'platforms': ['win_amd64'],
            'include_modules': ['numpy.distutils', 'PyCraft']
        }
    }
)