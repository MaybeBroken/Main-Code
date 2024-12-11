import sys, os
import inspect

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))


class classObj: ...


def generateDefsDirectory(pyObj, name) -> classObj:
    baseText = [""""""]

    def _inFunc(obj, id, level):
        baseText.append(
            f"""{"    "*level}class {id}:
{"    "*level}    ...
"""
        )
        for item in dir(obj):
            if not item.count("__") > 0:

                if inspect.isclass(getattr(obj, item)):
                    _inFunc(getattr(obj, item), item, level + 1)
                else:
                    if getattr(obj, item).__class__.__name__ in [
                        "str",
                        "int",
                        "dict",
                        "list",
                    ]:
                        baseText.append(
                            f"""{"    "*level}    {item}:{getattr(obj, item).__class__.__name__} = None
"""
                        )
                    elif getattr(obj, item).__class__.__name__ in [
                        "builtin_function_or_method",
                        "method_descriptor",
                    ]:
                        baseText.append(
                            f"""{"    "*level}    def {item}(): ...
"""
                        )
                    else:
                        baseText.append(
                            f"""{"    "*level}    {item} = None
"""
                        )

    _inFunc(pyObj, name, 0)

    baseText = "".join(baseText)
    with open("GENFRAME.py", "wt") as pyFile:
        pyFile.writelines(baseText)


generateDefsDirectory(None, "sys")
