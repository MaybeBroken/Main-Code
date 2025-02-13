import os
import sys
from time import sleep
from threading import Thread
import requests
import base64
import urllib

try:
    import music_tag
except:
    os.system("python3 -m pip install music-tag")
    import music_tag
try:
    from pytubefix import YouTube, Playlist, exceptions
except:
    os.system("python3 -m pip install pytubefix")
    from pytubefix import YouTube, Playlist, exceptions

try:
    import requests
except:
    os.system("python3 -m pip install requests")
    import requests

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))


class Color:
    GREEN = "\033[92m"
    LIGHT_GREEN = "\033[1;92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    BOLD = "\033[;1m"
    CYAN = "\033[1;36m"
    LIGHT_CYAN = "\033[1;96m"
    LIGHT_GREY = "\033[1;37m"
    DARK_GREY = "\033[1;90m"
    BLACK = "\033[1;30m"
    WHITE = "\033[1;97m"
    INVERT = "\033[;7m"
    RESET = "\033[0m"


rootPath = os.path.join(".", "youtubeDownloader")
threadQueue = {}


def pathSafe(name: str):
    for index in [["/", "-"], ["|", "-"], ["\\", "-"], ["*", ""], ['"', ""]]:
        try:
            name = name.replace(index[0], index[1])
        except:
            ...
    return name


def get(url: str, dest_folder: str, dest_name: str):
    try:
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        filename = pathSafe(dest_name)
        file_path = os.path.join(dest_folder, filename)
        r = requests.get(url, stream=True)
        open(file_path, "xt")
        if r.ok:
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
        else:
            print(
                "img download failed: status code {}\n{}".format(r.status_code, r.text)
            )
        return file_path
    except FileExistsError:
        return None
    except:
        get(url, dest_folder, dest_name)


def downloadSong(link, format):
    yt = YouTube(link)
    if format == "mp3":
        ys = yt.streams.get_audio_only()
        ys.download(outputPath, mp3=True)
    else:
        ys = yt.streams.get_highest_resolution()
        ys.download(outputPath)
        print("finished")


def downloadPlaylist(link, format):
    try:
        pl = Playlist(link)
        global outputPath
        outputPath = os.path.join(
            rootPath, f"{pathSafe(pl.title)} - {format}{pathSeparator}"
        )
        imgPath = os.path.join(outputPath, f"img{pathSeparator}")
        try:
            os.mkdir(outputPath)
            os.mkdir(imgPath)
        except:
            ...
        vId = 0
        for yt in pl.videos:

            def _th(format, outputPath, imgPath, yt, vId, times):
                try:
                    if format == "mp3":
                        ys = yt.streams.get_audio_only()
                        songName = pathSafe(ys.default_filename)
                        songPath = os.path.join(outputPath, f"{vId} - {songName}")
                        if not os.path.exists(songPath):
                            songPath = ys.download(
                                outputPath,
                                filename=pathSafe(f"{vId} | {songName}"),
                                mp3=False,
                            )
                            print(
                                f"{Color.GREEN}Finished download of {Color.CYAN}{songName}{Color.RESET}"
                            )
                            if (
                                not get(
                                    url=yt.thumbnail_url,
                                    dest_folder=imgPath,
                                    dest_name=f"{vId} - {songName}".replace(
                                        ".m4a", ".png"
                                    ),
                                )
                                == None
                            ):
                                song = music_tag.load_file(songPath)
                                with open(
                                    os.path.join(
                                        imgPath,
                                        f"{vId} - {songName}".replace(".m4a", ".png"),
                                    ),
                                    "rb",
                                ) as imgFile:
                                    song["artwork"] = imgFile.read()
                                song.save()
                                print(
                                    f"{Color.LIGHT_GREEN}Applied art to {Color.LIGHT_CYAN}{songName}{Color.RESET}"
                                )
                        else:
                            print(
                                f"{Color.YELLOW}Found cached version of {Color.BLUE}{songName}{Color.RESET}"
                            )
                    else:
                        ys = yt.streams.filter(progressive=True)[-1]
                        songName = ys.default_filename.replace("\\", "-")
                        songPath = ys.download(
                            outputPath, filename=f"{vId} | {songName}"
                        )
                        print(f"Finished download of {songName}")

                    del threadQueue[vId]
                except:
                    if times < 5:
                        print(
                            f"{Color.YELLOW}failed to download {Color.WHITE}{yt}{Color.YELLOW}, retrying{Color.RESET}"
                        )
                        _th(format, outputPath, imgPath, yt, vId, times=times + 1)
                    else:
                        print(
                            f"{Color.RED}failed to download {Color.WHITE}{yt}{Color.RESET}"
                        )

            t = Thread(
                target=_th,
                args=(
                    format,
                    outputPath,
                    imgPath,
                    yt,
                    vId,
                    0,
                ),
            ).start()

            threadQueue[vId] = t
            sleep(0.05)

            vId += 1
        while len(threadQueue) > 0:
            try:
                for t in threadQueue:
                    if not type(t) == int:
                        t.join()
                        del threadQueue[vId]
            except:
                try:
                    del threadQueue[vId]
                except:
                    ...
    except urllib.error.URLError:
        print(f"{Color.RED} Failed to fetch playlist information{Color.RESET}")


def downloadArtist(link, format):
    link


def _Wrapper(link, list, format):
    if list:
        downloadPlaylist(link, format)
    if not list:
        downloadSong(link, format)
    print("\n\n\n*********\nFinished\n*********\n")


while True:
    firstchoice = input(
        f"Another project by {Color.GREEN}MaybeBroken{Color.RESET}\nWelcome to the Youtube Downloader Utility!\nDownload or Convert? (D\\C)   "
    )
    if firstchoice == "d" or firstchoice == "D":
        format = input("\nWhich format? mp(3/4):  ").lower()
        if format == "3":
            format = "mp3"
        if format == "4":
            format = "mp4"
        secondChoice = input("\nIs this a song, playlist, or artist? (S/P/A)  ")
        if secondChoice == "p" or secondChoice == "P":
            url = input(f"\nyt Playlist Url:\n-->  ")
            if url == "" or url == None or len(url) < 20:
                url = "https://music.youtube.com/playlist?list=PLt-QnSFN9Gjp2sD8DmeY1B0awsd7tmpP7&si=P8J-srN4y03OWyed"
            print("\n")
            _Wrapper(url, True, format)
        if secondChoice == "s" or secondChoice == "S":
            url = input(f"\nyt song Url:\n-->  ")
            if url == "" or url == None or len(url) < 20:
                url = "https://www.youtube.com/watch?v=IICGZ7YOafs"
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
                    path = os.listdir(os.path.join(outputPath, i))
                    path.sort()
                    for name in path:
                        if name.endswith(".mp3"):
                            dirInput = os.path.abspath(
                                os.path.join(outputPath, i, name)
                            )
                            dirOutput = os.path.abspath(
                                os.path.join(
                                    outputPath,
                                    i,
                                    "converted",
                                    name.replace(".m4a.mp3", ".wav"),
                                )
                            )
                            os.system(
                                f'.{pathSeparator}/ffmpeg -y -v panic -i "{dirInput}" "{dirOutput}"'
                            )
                            print(f"Converted {name}")
                # except:
                # print("file conversion error")
