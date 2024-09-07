import json
def decode(packed_list):
    returnval = json.loads(packed_list)
    print(returnval)
    return returnval


def encode(list: list):
    strippedText = json.dumps(list)
    print(strippedText)
    return strippedText
