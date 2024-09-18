from yaml import load, dump
from yaml import CLoader as fLoader, CDumper as fDumper
import os

rootDir = os.path.curdir
dataPath = f'{rootDir}/data/'
if not os.path.exists(dataPath):
    os.mkdir(dataPath)

class write:
    def savePrefs(data):
        None