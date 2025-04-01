import os
import sys
from threading import Thread, Semaphore
from time import sleep
from typing import List

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

threadDict = {}
semaphore = Semaphore(10)  # Limit to 10 active threads
os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))
os.chdir(f".{pathSeparator}youtubeDownloader{pathSeparator}")
print(os.system("dir"))
folder = input("Enter the folder name: ")
if os.path.exists(folder):
    converterFormat = input("Enter the format to convert all songs to: ")
    try:
        os.mkdir(f"{folder} - {converterFormat}")
    except FileExistsError:
        pass
    os.chdir(f"{folder} - {converterFormat}")
    for _file in os.listdir(f"..{pathSeparator}{folder}"):

        def _internal(file):
            with semaphore:  # Acquire semaphore
                os.system(
                    f'ffmpeg -i "..{pathSeparator}{folder}{pathSeparator}{file}" -b:a 128k "{file.replace(file.split(".")[-1], f"{converterFormat}")}" -y'
                )

        if not os.path.exists(
            _file.replace(_file.split(".")[-1], f"{converterFormat}")
        ):
            threadDict[_file] = Thread(target=_internal, args=(_file,)).start()
        sleep(0.1)
else:
    print("Folder does not exist.")
