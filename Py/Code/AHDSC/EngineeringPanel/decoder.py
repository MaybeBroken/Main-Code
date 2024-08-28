def decode(packed_list):
    strippedText = str(packed_list)
    strippedText = strippedText.splitlines()
    for var in strippedText:
        var2 = var.split(":")
        strippedText[strippedText.index(var)] = var2  # type: ignore
    return strippedText


def encode(list: list):
    returnval = ""
    for sect in list:  # type: ignore
        returnval += str(sect[0]) + ":" + str(sect[1]) + "\n"
    return returnval
