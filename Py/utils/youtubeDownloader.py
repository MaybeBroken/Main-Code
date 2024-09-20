import os

os.system("python3 -m pip install pytubefix")
os.system("python3 -m pip install requests")
os.system("python3 -m pip install mutagen")
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from time import sleep
from pytubefix import YouTube, Playlist
from threading import Thread
import requests


outputPath = "./youtubeDownloader/"
threadQueue = []


def Download(link, format):
    youtubeObject = YouTube(link)
    thumbUrl = youtubeObject.thumbnail_url
    if format == "mp4":
        None
        dataObject = youtubeObject.streams.get_highest_resolution()
    elif format == "mp3":
        dataObject = youtubeObject.streams.filter(only_audio=True)
        dataObject = dataObject.get_audio_only()
    try:
        name = dataObject.default_filename
    except:
        try:
            name = dataObject.audio_track_name
        except:
            try:
                _stream = youtubeObject.streams.get_highest_resolution()
                name = _stream.default_filename
            except:
                print(f"failed fetch at link {link} with format {format}")
                return
    for var in [" ", "(", ")", "[", "]"]:
        name = name.replace(var, "_")
    if format == "mp3":
        mp3Check = True
        name = name.replace(".mp4", "")
    else:
        mp3Check = False
    try:
        dataObject.download(
            outputPath, filename=name if name != None else "name lost", mp3=mp3Check
        )
        print(f"Download of {name} has completed successfully")
    except:
        print(
            f"failed download at link {link} with format {format}, resorting to fallback mp4"
        )
        Download(link, "mp4")
        return
    if format == "mp3":
        response = requests.get(thumbUrl)
        with open(outputPath + name + ".jpg", "wb") as file:
            file.write(response.content)

        os.system(
            f'ffmpeg -v 1 -i "{outputPath+name+"."+format}" "{outputPath+"_"+name+"."+format}"'
        )

        audio = MP3(outputPath + "_" + name + "." + format, ID3=ID3)
        audio.tags.add(
            APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=open(outputPath + name + ".jpg", "rb").read(),
            )
        )


def getPlaylist(link):
    x = Playlist(link)
    return x


def _Wrapper(link, format):
    list = getPlaylist(link)
    global outputPath
    outputPath += list.title.replace(" ", "_") + f"_{format}/"
    for uri in list:
        thread = Thread(target=Download, daemon=True, args=[uri, format])
        thread.start()
        threadQueue.append(thread)
        sleep(0.1)
    for id in threadQueue:
        if id.is_alive():
            id.join()
    print("\n\n\n*********\nFinished\n*********\n")


def _Song(link, format):
    global outputPath
    outputPath += "_songs/"
    Download(link, format)
    print("\n\n\n*********\nFinished\n*********\n")


firstchoice = input(
    "\nAnother project by MaybeBroken\nWelcome to the Youtube Downloader Utility!\ndownload or convert? (D/C)   "
)
if firstchoice == "d" or firstchoice == "D":
    format = input("\nwhich format? mp(3/4):  ")
    if format == "3":
        format = "mp3"
    if format == "4":
        format = "mp4"
    secondChoice = input("\nIs this a song or a playlist? (S/P)  ")
    if secondChoice == "p" or secondChoice == "P":
        url = input(f"\nyt Playlist Url:\n-->  ")
        if url == "" or url == None or len(url) < 20:
            url = "https://music.youtube.com/playlist?list=PLt-QnSFN9Gjp2sD8DmeY1B0awsd7tmpP7&si=yqYOMDGHaWBLElwP"
        print("\n")
        _Wrapper(url, format)
    if secondChoice == "s" or secondChoice == "S":
        url = input(f"\nyt song Url:\n-->  ")
        if url == "" or url == None or len(url) < 20:
            url = "https://music.youtube.com/watch?v=aZti2SC6MFY&si=WtZlNftPk1Im5N1q"
        print("\n")
        _Song(url, format)
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
                        dirInput = os.path.abspath(os.path.join(outputPath, i, name))
                        dirOutput = os.path.abspath(
                            os.path.join(
                                outputPath, i, "converted", name.replace(".mp4", ".mp3")
                            )
                        )
                        os.system(f'ffmpeg -v 1 -i "{dirInput}" "{dirOutput}"')
                except:
                    print("file conversion error")
