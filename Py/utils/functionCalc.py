import matplotlib.pyplot as plt
from math import *
import sounddevice as sd

chords = 200
def _func(x, chords):
    returnVal = sin(x)
    for i in range(chords):
        returnVal += sin(x / (i+1))
    return returnVal


xArr = []
yArr = []


def _build():
    for val in range(500):
        xArr.append(val)
        yArr.append(_func(val, chords=chords))

_build()
plt.plot(xArr, yArr)
plt.show()