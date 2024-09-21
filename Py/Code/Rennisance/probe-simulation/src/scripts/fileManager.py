from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper
import os

rootDir = os.path.curdir
dataPath = f'{rootDir}/data/'
if not os.path.exists(dataPath):
    os.mkdir(dataPath)
if not os.path.exists(f'{dataPath}/userprefs.txt'):
    with open(f'{dataPath}/userprefs.txt', 'x+') as prefsFile:
        print(f'loaded prefs {prefsFile.readlines()}')

class write:
    def savePrefs(data):
        None