import os
from time import sleep
from pytubefix import YouTube, Playlist, exceptions
from threading import Thread
import requests
from cli import Color

outputPath = "./youtubeDownloader/"
threadQueue = []


def downloadSong(link, format):
    yt = YouTube(link, on_progress_callback=print)
    if format == "mp3":
        ys = yt.streams.get_audio_only()
        ys.download(outputPath, mp3=True)
    else:
        ys = yt.streams.get_highest_resolution()
        ys.download(outputPath)


def downloadPlaylist(link, format):
    pl = Playlist(link)
    global outputPath
    outputPath += pl.title + f" - {format}/"
    vId = 0
    for yt in pl.videos:
        songName = "(name)"
        if format == "mp3":
            ys = yt.streams.get_audio_only()
            songName = ys.default_filename.replace("/", "-")
            ys.download(
                outputPath,
                filename=f"{vId} | {songName}",
                mp3=True,
            )
        else:
            songName = ys.default_filename.replace("/", "-")
            ys = yt.streams.get_highest_resolution()
            ys.download(outputPath, filename=f"{vId} | {songName}")

        print(f"Finished download of {songName}")
        vId += 1


def _Wrapper(link, list, format):
    if list:
        downloadPlaylist(link, format)
    if not list:
        downloadSong(link, format)
    print("\n\n\n*********\nFinished\n*********\n")


while True:

    firstchoice = input(
        f"Another project by {Color.GREEN}MaybeBroken{Color.RESET}\nWelcome to the Youtube Downloader Utility!\nDownload or Convert? (D/C)   "
    )
    if firstchoice == "d" or firstchoice == "D":
        format = input("\nWhich format? mp(3/4):  ")
        if format == "3":
            format = "mp3"
        if format == "4":
            format = "mp4"
        secondChoice = input("\nIs this a song or a playlist? (S/P)  ")
        if secondChoice == "p" or secondChoice == "P":
            url = input(f"\nyt Playlist Url:\n-->  ")
            if url == "" or url == None or len(url) < 20:
                url = "https://music.youtube.com/playlist?list=PLt-QnSFN9Gjp2sD8DmeY1B0awsd7tmpP7&si=P8J-srN4y03OWyed"
            print("\n")
            _Wrapper(url, True, format)
        if secondChoice == "s" or secondChoice == "S":
            url = input(f"\nyt song Url:\n-->  ")
            if url == "" or url == None or len(url) < 20:
                url = (
                    "https://music.youtube.com/watch?v=aZti2SC6MFY&si=WtZlNftPk1Im5N1q"
                )
            print("\n")
            _Wrapper(url, False, format)
    if firstchoice == "c" or firstchoice == "C":
        mpQuery = input("\nConvert all to mp3?: (Y/N)  ")
        if mpQuery == "y" or mpQuery == "Y":
            for i in os.listdir(outputPath):
                if i != ".DS_Store":
                    # try:
                    try:
                        os.mkdir(os.path.join(outputPath, i, "converted"))
                    except:
                        None
                    for name in os.listdir(os.path.join(outputPath, i)):
                        dirInput = os.path.abspath(os.path.join(outputPath, i, name))
                        dirOutput = os.path.abspath(
                            os.path.join(
                                outputPath,
                                i,
                                "converted",
                                name.replace(".mp3", ".wav"),
                            )
                        )
                        os.system(f'ffmpeg -i "{dirInput}" "{dirOutput}"')
                # except:
                # print("file conversion error")
