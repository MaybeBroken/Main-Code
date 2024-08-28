from time import sleep
from pytubefix import YouTube, Playlist
from threading import Thread
import os

outputPath = "./youtubeDownloader/"

def Download(link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        name = youtubeObject.default_filename.replace(' ', '_')
        youtubeObject.download(outputPath, filename=name)
        print(f"Download of {name} has completed successfully")
    except:
        print(f"\n\nAn error occurred with file {name}!\n\n")


def getPlaylist(link):
    x = Playlist(link)
    print(x.count)
    return x


def _Wrapper(link):
    list = getPlaylist(link)
    global outputPath
    outputPath += list.title.replace(' ', '_') + "/"
    for uri in list:
        Thread(target=Download, daemon=True, args=[uri]).start()
        sleep(0.1)
    print("\n\n\n*********\nFinished\n*********\n")


firstchoice = input("\n\nWelcome to the Downloader Utility!\ndownload or convert? (D/C)   ")
print("\n")
if firstchoice == "d" or firstchoice == "D":
    url = input(f"\nyt Playlist Url:")
    if url == "" or url == None or len(url) < 20:
        url = "https://music.youtube.com/playlist?list=PLt-QnSFN9Gjp2sD8DmeY1B0awsd7tmpP7&si=yqYOMDGHaWBLElwP"
    print("\n")
    _Wrapper(url)
if firstchoice == "c" or firstchoice == "C":
    mpQuery = input("\nConvert all to mp3?: (Y/N)  ")
    if mpQuery == "y" or mpQuery == "Y":
        for i in os.listdir(outputPath):
            if i!='.DS_Store':
                try:
                    os.mkdir(os.path.join(outputPath, i, "converted"))
                    for name in os.listdir(os.path.join(outputPath, i)):
                        print(name)
                        dirInput = os.path.abspath(os.path.join(outputPath, i, name))
                        dirOutput = os.path.abspath(
                            os.path.join(
                                outputPath, i, "converted", name.replace(".mp4", ".mp3")
                            )
                        )
                        os.system(f"Py/utils/ffmpeg -i {dirInput} {dirOutput}")
                except:
                    print("file conversion error")