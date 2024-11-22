import os
import sys

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))


import PyCraft.Main as Main
import PyCraft.modules.vars

PyCraft.modules.vars.hp = 300000
PyCraft.modules.vars.worldz = 1
PyCraft.modules.vars.seed = int(Main.randint(0, 999999))
running = True
while running == True:
    try:
        Main.game.run()
    except:
        if PyCraft.modules.vars.relaunching == True:
            PyCraft.modules.vars.relaunching == False
        else:
            running = False
