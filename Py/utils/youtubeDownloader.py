from time import sleep
from pytubefix import YouTube, Playlist
from threading import Thread
import os

outputPath = "./youtubeDownloader/"
threadQueue = []


def Download(link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        name = youtubeObject.default_filename.replace(" ", "_")
        name = youtubeObject.default_filename.replace("(", "")
        name = youtubeObject.default_filename.replace(")", "")
        name = youtubeObject.default_filename.replace("[", "")
        name = youtubeObject.default_filename.replace("]", "")
        youtubeObject.download(outputPath, filename=name)
        print(f"Download of {name} has completed successfully")
    except:
        print(f"\n\nAn error occurred with file {name}!\n\n")


def getPlaylist(link):
    x = Playlist(link)
    return x


def _Wrapper(link):
    list = getPlaylist(link)
    global outputPath
    outputPath += list.title.replace(" ", "_") + "/"
    for uri in list:
        thread = Thread(target=Download, daemon=True, args=[uri])
        thread.start()
        threadQueue.append(thread)
        sleep(0.1)
    for id in threadQueue:
        if id.is_alive():
            id.join()
    print("\n\n\n*********\nFinished\n*********\n")


def _Song(link):
    global outputPath
    outputPath += "_songs/"
    Download(link)
    print("\n\n\n*********\nFinished\n*********\n")


firstchoice = input(
    "\n\nWelcome to the Downloader Utility!\ndownload or convert? (D/C)   "
)

print("\n")
if firstchoice == "d" or firstchoice == "D":
    secondChoice = input("\nIs this a song or a playlist? (S/P)   ")
    if secondChoice == "p" or secondChoice == "P":
        url = input(f"\nyt Playlist Url:\n-->  ")
        if url == "" or url == None or len(url) < 20:
            url = "https://music.youtube.com/playlist?list=PLt-QnSFN9Gjp2sD8DmeY1B0awsd7tmpP7&si=yqYOMDGHaWBLElwP"
        print("\n")
        _Wrapper(url)
    if secondChoice == "s" or secondChoice == "S":
        url = input(f"\nyt song Url:\n-->  ")
        if url == "" or url == None or len(url) < 20:
            url = "https://music.youtube.com/watch?v=aZti2SC6MFY&si=WtZlNftPk1Im5N1q"
        print("\n")
        _Song(url)
if firstchoice == "c" or firstchoice == "C":
    mpQuery = input("\nConvert all to mp3?: (Y/N)  ")
    if mpQuery == "y" or mpQuery == "Y":
        for i in os.listdir(outputPath):
            if i != ".DS_Store":
                try:
                    try:
                        os.mkdir(os.path.join(outputPath, i, "converted"))
                    except:
                        None
                    for name in os.listdir(os.path.join(outputPath, i)):
                        print(name)
                        dirInput = os.path.abspath(os.path.join(outputPath, i, name))
                        dirOutput = os.path.abspath(
                            os.path.join(
                                outputPath, i, "converted", name.replace(".mp4", ".mp3")
                            )
                        )
                        thread = Thread(
                            target=os.system,
                            args=[f"Py/utils/ffmpeg -v 0 -i {dirInput} {dirOutput}"],
                            daemon=True,
                        )
                        thread.start()
                        threadQueue.append(thread)
                except:
                    print("file conversion error")
        while len(threadQueue) > 0:
            None
