mass_first = int(input("\nmass of first object in Kg:  "))
mass_second = int(input("\nmass of second object in Kg:  "))
radius = int(input("\nRadius between objects in Meters:  "))
g = 6.67e-11
result = (g*mass_first*mass_second)/(radius**2)
print(f"\n\nRESULT IN NM^2/KG^2:\n{result}")