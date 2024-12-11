import sys, os
import inspect

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))


def generateDefsDirectory(pyObj, name):
    baseText = [""""""]

    def _inFunc(obj, id, level):
        if not level == 0:
            baseText.append(
                f"""{"    "*(level-1)}class {id}:
{"    "*(level-1)}    ...
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
                        if level == 0:
                            baseText.append(
                                f"""{"    "*level}{item}:{getattr(obj, item).__class__.__name__} = None
"""
                            )
                        else:
                            baseText.append(
                                f"""{"    "*(level-1)}    {item}:{getattr(obj, item).__class__.__name__} = None
"""
                            )
                    elif getattr(obj, item).__class__.__name__ in [
                        "builtin_function_or_method",
                        "method_descriptor",
                    ]:
                        if level == 0:
                            baseText.append(
                                f"""{"    "*level}def {item}{str(getattr(obj, item).__text_signature__).replace("$", "") if not getattr(obj, item).__text_signature__ == None else "()"}: ...
"""
                            )
                        else:
                            baseText.append(
                                f"""{"    "*(level-1)}    def {item}{str(getattr(obj, item).__text_signature__).replace("$", "") if not getattr(obj, item).__text_signature__ == None else "()"}: ...
"""
                            )
                    else:
                        if level == 0:
                            baseText.append(
                                f"""{"    "*level}{item} = None
"""
                            )
                        else:
                            baseText.append(
                                f"""{"    "*(level-1)}    {item} = None
"""
                            )

    _inFunc(pyObj, name, 0)

    baseText = "".join(baseText)
    with open(f"gen{pathSeparator}{name}.py", "wt") as pyFile:
        pyFile.writelines(baseText)


# Make sure to put a custom class into the pyObj input

generateDefsDirectory(pyObj=None, name="none")
