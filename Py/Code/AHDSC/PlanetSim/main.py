import openpyxl as ex

File = ex.open("./book.xlsx")


class system:
    def __init__(self):
        self.primarySunMass = File["Binary System"]["D4"].value
        self.secondarySunMass = File["Binary System"]["D5"].value
        self.sunOrbitDistance = File["Binary System"]["D6"].value
        self.sunOrbitEccentricity = File["Binary System"]["D7"].value
        self.systemAge = File["System Builder"]["H5"].value

        class planets:
            def __init__(self) -> None:
                planetsMade = 0
                for row in range(6, 102):
                    if File["System Builder"][f"L{row}"].value != "None":
                        print(File["System Builder"][f"L{row}"].value)

                        class planet:
                            def __init__(self) -> None:
                                File["System Builder"][f"H{row}"].value

                        self.__setattr__(str(planetsMade), planet)
                        planetsMade += 1

        self.planets = planets()
        for id in self.planets.__dict__:
            print(f"{id} = {self.planets.__dict__[id]}")


data = system()

for id in data.__dict__:
    print(f"{id} = {data.__dict__[id]}")
