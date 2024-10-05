alphabet = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' '.', ',', '!', '?', '-', '+', '*', '/', ':', ')', '(', ';', '"', "'", '[', ']']

def encode(string_to_be_encoded: str, key: int) -> str:
    newalphabet = []
    returnval = []
    key = int(key)
    for i in range(len(alphabet)):
        if i+key <= (len(alphabet) - 1):
            newalphabet.append(alphabet[i+key])
        elif i+key > (len(alphabet)-1):
            pos = abs(len(alphabet) - (i+key))
            newalphabet.append(alphabet[pos])
        else: print("Error 0"); break
    for i in range(len(string_to_be_encoded)):
        index = alphabet.index(string_to_be_encoded[i])
        returnval.append(newalphabet[index])
    returnval = ''.join(returnval)
    return returnval

def decode(string_to_be_decoded, key):
    newalphabet = []
    returnval = []
    key = int(key)
    for i in range(len(alphabet)):
        if i-key <= (len(alphabet) - 1):
            newalphabet.append(alphabet[i-key])
        if i-key > len(alphabet):
            pos = abs(len(alphabet) - (i-key))
            newalphabet.append(alphabet[pos])
    for i in range(len(string_to_be_decoded)):
        index = alphabet.index(string_to_be_decoded[i])
        returnval.append(newalphabet[index])
    returnval = ''.join(returnval)
    return returnval

def __wrapper():
    while 1==1:
        try:
            answer = input("Encode or Decode? ")
            if answer == 'encode':
                print("  ")
                print(encode(input("string: "), int(input("Key: "))))
                print("  ")
            elif answer == 'decode':
                print("  ")
                print(decode(input("string: "), input("Key: ")))
                print("  ")
            else: print("Please put in either 'encode' or 'decode', no other values accepted")
        except:
            print("  ")
            print("Runtime error in file //encoder.py>__init__>return>returnVal()")
            print("Failed to parse either string or key, please make sure string is longer than 2 charecters, and key is an integer between 1 and 32")
            print("  ")

__wrapper()