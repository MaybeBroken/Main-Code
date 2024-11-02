from os import system, mkdir
import string

try:
    import openpyxl as ex
except:
    system("python3 -m pip install openpyxl")


def parseUrl(url, path):
    def _in(url):
        url = url.split("edit?")
        url.remove(url[1])
        url.append("export?output=xlsx")
        url = "".join(url)
        system(f'curl -o {path} "{url}"')
        try:
            with open(path, "rt") as file:
                data = file.read()
                data = data.split("<A HREF=")[1]
                data = data.split(">here</A>")[0]
                system(f'curl -o {path} "{data}"')
        except:
            ...
        return ex.open(path)

    try:
        return _in(url)
    except:
        for i in range(5):
            try:
                return _in(url)
            except:
                print(f"retrying time #{i}")


inUrl: str = input("Master File Url (Must be made public): ")

if len(inUrl) == 0:
    inUrl = "https://docs.google.com/spreadsheets/d/1DtBwzigbbslESYkrX9IWsJf7_1KJOwa-FNEa4OiaDyU/edit?gid=0#gid=0"

masterFile = parseUrl(inUrl, "MASTER.xlsx")

students: list[dict] = []
commands = ["Help", "Add single student", "Grade all files"]

checkRange = input("\nRange to check (LetterNumber:LetterNumber): ").split(":")
rangeList = []

rangeStart = checkRange[0]
rangeEnd = checkRange[1]

for letter in range(
    string.ascii_uppercase.index(rangeStart[0]),
    string.ascii_uppercase.index(rangeEnd[0]),
):
    for number in range(int(rangeStart[1]), int(rangeEnd[1])):
        rangeList.append(f"{string.ascii_uppercase[letter]}{number}")


try:
    mkdir("studentFiles")
except FileExistsError:
    ...


def grade():
    for student in students:
        dings = []
        errors = []
        sFile = student["file"]
        for sheet in masterFile:
            for id in rangeList:
                try:
                    if (
                        type(masterFile[sheet.title][id].value)
                        == type(sFile[sheet.title][id].value)
                        and type(masterFile[sheet.title][id].value) == float
                    ):
                        if (
                            masterFile[sheet.title][id].value
                            != sFile[sheet.title][id].value
                        ):
                            dings.append(
                                [
                                    id,
                                    masterFile[sheet.title][id].value,
                                    sFile[sheet.title][id].value,
                                ]
                            )
                    elif (
                        type(masterFile[sheet.title][id].value)
                        == type(sFile[sheet.title][id].value)
                        and type(masterFile[sheet.title][id].value) == str
                    ):
                        if (
                            masterFile[sheet.title][id].value.lower()
                            != sFile[sheet.title][id].value.lower()
                        ):
                            dings.append(
                                [
                                    id,
                                    masterFile[sheet.title][id].value,
                                    sFile[sheet.title][id].value,
                                ]
                            )
                    else:
                        errors.append(id)
                except:
                    errors.append(id)

        print(f"\nSystem had {len(errors)} errors on Cells: ")
        for err in errors:
            print(f"{err}")
        print(f"\n{student["name"]} had {len(dings)} errors:\n")
        for ding in dings:
            print(f"Cell {ding[0]}, Teacher: {ding[1]}, Student: {ding[2]}")
        print("\n")


while True:
    try:
        msg = input('Command ("help" for help): ').lower()
        if msg == "help" or msg == "Help" or msg == "HELP":
            print("-" * 25)
            for cmd in commands:
                print(f"| {cmd}")
        if (
            msg == "add single student"
            or msg == "Add single student"
            or msg == "Add Single Student"
        ):
            sName = input("| Student's name: ")
            sFile = input("| Student's doc url (must be public): ")
            sFile = parseUrl(sFile, f"studentFiles/{sName}.xlsx")
            students.append({"name": sName, "file": sFile})
            print(f"\n| Added {sName} to grading list\n")
        if (
            msg == "grade all files"
            or msg == "Grade all files"
            or msg == "Grade all Files"
        ):
            score = grade()
    except:
        print("System err, please try again!")
