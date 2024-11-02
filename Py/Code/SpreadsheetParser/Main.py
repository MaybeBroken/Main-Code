from os import system

masterSpreadsheet


def parseUrl(raw) -> str:
    url = url.split("edit?")
    url.remove(url[1])
    url.append("export?output=csv")
    return "".join(url)


system(
    f'curl -o MASTER.csv "{parseUrl(input("Master File Url (Must be made public): "))}"'
)

with open("MASTER.csv", "rt") as file:
    data = file.read()
    print(data)
    data = data.split("<A HREF=")[1]
    data = data.split(">here</A>")[0]
    print(data)
    system(f'curl -o file.csv "{data}"')

# https://docs.google.com/spreadsheets/d/1n_A-2qacl6zY1mC3ChP7xNzFDTsz82O-lSrdS93JjX8/edit?gid=0#gid=0
