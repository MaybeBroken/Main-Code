import opensimplex as noise


class terrainGen:
    def makeNoiseMap(self, x, y, z, seed):
        noise.seed(seed=seed)
        return int(round(noise.noise4(x=x, y=y, z=0, w=z) * 10))
