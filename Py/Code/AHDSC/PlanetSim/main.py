import openpyxl as ex
import formulas

File = ex.open("./book.xlsx")


def __calculateFormulaInternal(formula, inputs):
    func = formulas.Parser().ast(formula)[1].compile()
    return func(inputs)


def __getFormulaInputs(formula):
    return formulas.Parser().ast(formula)[1].compile().inputs


def calculateFormula(formula, sheet):
    if type(formula) == str:
        inputs = list(__getFormulaInputs(formula))
        calcInputs = []
        inputs.sort()

        for cell in inputs:
            if not type(sheet[cell].value) == str:
                calcInputs.append(sheet[cell].value)
            else:
                print(sheet[cell].value)
                calcInputs.append(calculateFormula(sheet[cell].value, sheet)[0])

        return __calculateFormulaInternal(formula, inputs=calcInputs)[0]
    else:
        return formula


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
                                self.massJm = calculateFormula(
                                    File["System Builder"][f"M{row}"].value,
                                    File["System Builder"],
                                )
                                self.radius = calculateFormula(
                                    File["System Builder"][f"P{row}"].value,
                                    File["System Builder"],
                                )

                        self._list.append(planet())
                for id in self._list:
                    print(id.__dict__)

        self.planets = planets()


data = system()
