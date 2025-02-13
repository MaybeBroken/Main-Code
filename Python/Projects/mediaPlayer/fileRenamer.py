import os
import sys
from time import sleep

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))

os.chdir(f".{pathSeparator}youtubeDownloader{pathSeparator}")
while True:
    for dir in os.listdir("."):
        print(dir)
    folder = input("Enter the folder name: ")
    os.chdir(f".{pathSeparator}{folder}{pathSeparator}")

    for file in os.listdir():
        if len(file.split(" - ")[0]) < 3:
            newFileName = f"..{pathSeparator}{folder}{pathSeparator}{"0"*(3-len(file.split(" - ")[0]))}{file.split(' - ')[0]}{file.replace(file.split(' - ')[0], "")}"
            print(f"Renaming {file} to {newFileName}")
            os.rename(
                file,
                newFileName,
            )
            print(f"Renamed {file} to {newFileName}")
        sleep(0.1)
