import matplotlib.pyplot as plt
from math import *

def _func(x):
    returnVal = 2**x
    return returnVal


xArr = []
yArr = []


def _build():
    for val in range(100):
        xArr.append(val)
        yArr.append(_func(val))

_build()
plt.plot(xArr, yArr)
plt.show()