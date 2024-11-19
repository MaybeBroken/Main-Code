from os import system, mkdir

try:
    import openpyxl as ex
except:
    system("python3 -m pip install openpyxl")


class CLI:
    GREEN = "\033[92m"
    LIGHT_GREEN = "\033[1;92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    BOLD = "\033[;1m"
    CYAN = "\033[1;36m"
    LIGHT_CYAN = "\033[1;96m"
    LIGHT_GREY = "\033[1;37m"
    DARK_GREY = "\033[1;90m"
    BLACK = "\033[1;30m"
    WHITE = "\033[1;97m"
    INVERT = "\033[;7m"
    RESET = "\033[0m"

    def up(num):
        return f"\033[{num}A"

    def resetline():
        print(f"\033[1A\033[0m")


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
                print(f"{CLI.RESET}retrying time #{CLI.RED}{i}{CLI.RESET}")
            if i == 4:
                exit(f"{CLI.RED}\nPlease enter a valid URL!\n{CLI.RESET}")


inUrl: str = input(f"{CLI.RESET}Master File Url (Must be made public): {CLI.INVERT}")
CLI.resetline()

if len(inUrl) == 0:
    inUrl = "https://docs.google.com/spreadsheets/d/1DtBwzigbbslESYkrX9IWsJf7_1KJOwa-FNEa4OiaDyU/edit?gid=0#gid=0"

masterFile = parseUrl(inUrl, "MASTER.xlsx")

students: list[dict] = []
commands = ["help", "add single student | add", "grade all files | grade"]

# checkRange = input("\nRange to check (LetterNumber:LetterNumber): ").split(":")
# rangeList = []

# rangeStart = checkRange[0]
# rangeEnd = checkRange[1]

# for letter in range(
#     string.ascii_uppercase.index(rangeStart[0]),
#     string.ascii_uppercase.index(rangeEnd[0]),
# ):
#     for number in range(int(rangeStart[1]), int(rangeEnd[1])):
#         rangeList.append(f"{string.ascii_uppercase[letter]}{number}")


try:
    mkdir("studentFiles")
except FileExistsError:
    ...


def grade():
    for student in students:
        dings = []
        errors = []
        sFile = student["file"]
        sName = student["name"]
        for sheet in masterFile:
            for index in sheet:
                for id in index:
                    if id.value != None:
                        if (
                            type(id.value)
                            == type(sFile[sheet.title][id.coordinate].value)
                            and type(id.value) == str
                        ):
                            if (
                                id.value.lower()
                                != sFile[sheet.title][id.coordinate].value.lower()
                                and len(str(id.value)) > 0
                            ):
                                dings.append(
                                    [
                                        id.coordinate,
                                        id.value,
                                        sFile[sheet.title][id.coordinate].value,
                                    ]
                                )
                        elif (
                            len(str(id.value)) > 0
                            and len(str(sFile[sheet.title][id.coordinate].value)) == 0
                        ):
                            dings.append(
                                [
                                    id.coordinate,
                                    id.value,
                                    sFile[sheet.title][id.coordinate].value,
                                ]
                            )
                        elif (
                            str(id.value)
                            != str(sFile[sheet.title][id.coordinate].value)
                            and len(str(id.value)) > 0
                        ):
                            dings.append(
                                [
                                    id.coordinate,
                                    id.value,
                                    sFile[sheet.title][id.coordinate].value,
                                ]
                            )
                        else:
                            errors.append(id)
        if len(errors) > 0:
            print(
                f"{CLI.RESET}\nSystem had {CLI.RED}{len(errors)}{CLI.RESET} errors on Cells: "
            )
            for err in errors:
                print(f"{err}")
        print(
            f"{CLI.RESET}\n{sName} had {CLI.RED}{len(dings)}{CLI.RESET} errors:\n"
        )
        for ding in dings:
            print(
                f"{CLI.RESET}Cell {CLI.BOLD}{ding[0]}{CLI.RESET}, Teacher: {CLI.GREEN}{ding[1]}{CLI.RESET}, Student: {CLI.RED}{ding[2]}{CLI.RESET}"
            )
        print("\n")


while True:
    msg = input(
        f'{CLI.RESET}\nCommand ("{CLI.INVERT}help{CLI.RESET}" for help): {CLI.INVERT}'
    ).lower()
    CLI.resetline()
    if msg == "help":
        print(f"{CLI.RESET}-" * 25)
        for cmd in commands:
            print(f"{CLI.RESET}| {CLI.INVERT}{cmd}{CLI.RESET}")
    if msg == "add single student" or msg == "add":
        sName = input(f"{CLI.RESET}| Student's name: {CLI.INVERT}")
        sFile = input(f"{CLI.RESET}| Student's doc url (must be public): {CLI.INVERT}")
        CLI.resetline()
        sFile = parseUrl(sFile, f"studentFiles/{sName}.xlsx")
        students.append({"name": sName, "file": sFile})
        print(f"{CLI.RESET}\n| Added {CLI.GREEN}{sName}{CLI.RESET} to grading list\n")
    if msg == "grade all files" or msg == "grade":
        CLI.resetline()
        score = grade()
