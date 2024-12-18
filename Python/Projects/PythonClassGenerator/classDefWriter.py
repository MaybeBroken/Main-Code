import sys, os
import inspect
import Cocoa as c

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))


def generateDefsDirectory(pyObj, name):
    baseText = [""""""]

    def _inFunc(obj, id, level):
        funcList = []
        _baseText = []
        if not level == 0:
            baseText.append(
                f"""{"    "*(level-1)}class {id}:
{"    "*(level-1)}    def __init__(self):
{"    "*(level)}    ...
"""
            )
        for item in dir(obj):
            try:
                if not item.count("__") > 0:

                    if inspect.isclass(getattr(obj, item)):
                        funcList.append([getattr(obj, item), item, level + 1])
                    else:
                        if getattr(obj, item).__class__.__name__ in [
                            "str",
                            "int",
                            "dict",
                            "list",
                        ]:
                            if level == 0:
                                _baseText.append(
                                    f"""{"    "*level}{item}:{getattr(obj, item).__class__.__name__} = None
    """
                                )
                            else:
                                _baseText.append(
                                    f"""{"    "*(level)}    self.{item}:{getattr(obj, item).__class__.__name__} = None
    """
                                )
                        elif getattr(obj, item).__class__.__name__ in [
                            "builtin_function_or_method",
                            "method_descriptor",
                        ]:
                            if level == 0:
                                _baseText.append(
                                    f"""{"    "*level}def {item}{str(getattr(obj, item).__text_signature__).replace("$", "") if not getattr(obj, item).__text_signature__ == None else "()"}: ...
    """
                                )
                            else:
                                _baseText.append(
                                    f"""{"    "*(level-1)}    def {item}{str(getattr(obj, item).__text_signature__).replace("$", "") if not getattr(obj, item).__text_signature__ == None else "()"}: ...
    """
                                )
                        else:
                            if level == 0:
                                _baseText.append(
                                    f"""{"    "*level}{item} = None
    """
                                )
                            else:
                                _baseText.append(
                                    f"""{"    "*(level)}    self.{item} = None
    """
                                )
            except:
                ...
        returnText = []
        for obj in _baseText:
            if obj.count("def ") > 0:
                returnText.reverse()
                returnText.append(obj)
                returnText.reverse()
            else:
                returnText.append(obj)
        returnText.reverse()
        baseText.append("".join(returnText))
        for item in funcList:
            _inFunc(item[0], item[1], item[2])

    _inFunc(pyObj, name, 0)

    baseText = "".join(baseText)
    with open(f"gen{pathSeparator}{name}.py", "wt") as pyFile:
        pyFile.writelines(baseText)


# Make sure to put a custom class into the pyObj input

generateDefsDirectory(pyObj=c, name="Cocoa")
