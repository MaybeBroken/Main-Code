import math as mt

from matplotlib import pyplot as plt

class sinWave:
    def _1d(inputVal, val=1) -> float:
        out = val/mt.sin(inputVal)
        return out

plt.plot(data=sinWave._1d(3))
plt.show()