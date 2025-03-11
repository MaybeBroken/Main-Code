import base64
import string

alphabet = [chr(i) for i in range(0, 54599)]


def encode(string_to_be_encoded: str, key: int) -> str:
    newalphabet = []
    returnval = []
    key = int(key)
    for i in range(len(alphabet)):
        if i + key <= (len(alphabet) - 1):
            newalphabet.append(alphabet[i + key])
        elif i + key > (len(alphabet) - 1):
            pos = abs(len(alphabet) - (i + key))
            newalphabet.append(alphabet[pos])
        else:
            print("Error 0")
            break
    for i in range(len(string_to_be_encoded)):
        index = alphabet.index(string_to_be_encoded[i])
        returnval.append(newalphabet[index])
    returnval = r"".join(returnval)
    return returnval


def decode(string_to_be_decoded, key):
    newalphabet = []
    returnval = []
    key = int(key)
    for i in range(len(alphabet)):
        if i - key <= (len(alphabet) - 1):
            newalphabet.append(alphabet[i - key])
        if i - key > len(alphabet):
            pos = abs(len(alphabet) - (i - key))
            newalphabet.append(alphabet[pos])
    for i in range(len(string_to_be_decoded)):
        index = alphabet.index(string_to_be_decoded[i])
        returnval.append(newalphabet[index])
    returnval = r"".join(returnval)
    return returnval


def to_binary(string):
    return r"".join(format(ord(char), "08b") for char in string)


def from_binary(binary):
    return r"".join(chr(int(binary[i : i + 8], 2)) for i in range(0, len(binary), 8))


def to_hex(string):
    return r"".join(format(ord(char), "02x") for char in string)


def from_hex(hex):
    return r"".join(chr(int(hex[i : i + 2], 16)) for i in range(0, len(hex), 2))


def to_base64(string):
    return base64.b64encode(string.encode()).decode()


def from_base64(string):
    return base64.b64decode(string).decode()


def to_base85(string):
    return base64.a85encode(string.encode()).decode()


def from_base85(base85):
    return base64.a85decode(base85).decode()


def to_base32(string):
    return base64.b32encode(string.encode()).decode()


def from_base32(base32):
    return base64.b32decode(base32).decode()


def to_base16(string):
    return base64.b16encode(string.encode()).decode()


def from_base16(base16):
    return base64.b16decode(base16).decode()


def to_base58(string):
    return base64.b58encode(string.encode()).decode()


def from_base58(base58):
    return base64.b58decode(base58).decode()


def to_trinary(string):
    return r"".join(format(ord(char), "03o") for char in string)


def from_trinary(trinary):
    return r"".join(chr(int(trinary[i : i + 3], 8)) for i in range(0, len(trinary), 3))


def to_quaternary(string):
    return r"".join(format(ord(char), "04o") for char in string)


def from_quaternary(quaternary):
    return r"".join(
        chr(int(quaternary[i : i + 4], 8)) for i in range(0, len(quaternary), 4)
    )


def to_quinary(string):
    return r"".join(format(ord(char), "05o") for char in string)


def from_quinary(quinary):
    return r"".join(chr(int(quinary[i : i + 5], 8)) for i in range(0, len(quinary), 5))


def to_senary(string):
    return r"".join(format(ord(char), "06o") for char in string)


def from_senary(senary):
    return r"".join(chr(int(senary[i : i + 6], 8)) for i in range(0, len(senary), 6))


def to_septenary(string):
    return r"".join(format(ord(char), "07o") for char in string)


def from_septenary(septenary):
    return r"".join(
        chr(int(septenary[i : i + 7], 8)) for i in range(0, len(septenary), 7)
    )


def to_octal(string):
    return r"".join(format(ord(char), "08o") for char in string)


def from_octal(octal):
    return r"".join(chr(int(octal[i : i + 8], 8)) for i in range(0, len(octal), 8))


def to_nonary(string):
    return r"".join(format(ord(char), "09o") for char in string)


def from_nonary(nonary):
    return r"".join(chr(int(nonary[i : i + 9], 8)) for i in range(0, len(nonary), 9))


def caps(string):
    return string.upper()


def lower(string):
    return string.lower()


def reverse(string):
    return string[::-1]


class Ciphers:
    class Encoders:
        def level_1(string, key_1):
            return f"{key_1}&{encode(string, key_1)}"

        def level_2(string, key_1):
            return f"{key_1}&{reverse(encode(string, key_1))}"

        def level_3(string, key_1):
            return f"{key_1}&{to_hex(reverse(encode(string, key_1)))}"

        def level_4(string, key_1):
            return f"{key_1}&{to_base64(to_hex(reverse(encode(string, key_1))))}"

    class Decoders:
        def level_1(encoded_string):
            key_1, encoded = encoded_string.split("&")
            return decode(encoded, int(key_1))

        def level_2(encoded_string):
            key_1, encoded = encoded_string.split("&")
            return decode(reverse(encoded), int(key_1))

        def level_3(encoded_string):
            key_1, encoded = encoded_string.split("&")
            return decode(reverse(from_hex(encoded)), int(key_1))

        def level_4(encoded_string):
            key_1, encoded = encoded_string.split("&")
            return decode(reverse(from_hex(from_base64(encoded))), int(key_1))
