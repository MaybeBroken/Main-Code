import openpyxl as ex
import formulas as fm

File = ex.open("./book.xlsx")


class system:
    def __init__(self):
        self.primarySunMass = File["Binary System"]["D4"].value
        self.secondarySunMass = File["Binary System"]["D5"].value
        self.sunOrbitDistance = File["Binary System"]["D6"].value
        self.sunOrbitEccentricity = File["Binary System"]["D7"].value
        self.systemAge = File["System Builder"]["H5"].value

        class planets:
            def __init__(self):
                self._list = []
                for row in range(6, 102):
                    if not File["System Builder"][f"L{row}"].value == None:

                        class planet:
                            def __init__(self) -> None:
                                self.mass = File["System Builder"][f"L{row}"].value

                        self._list.append(planet())

        self.planets = planets()


data = system()

for planet in data.planets._list:
    print(planet.mass)
