import os

try:
    import music_tag
except:
    os.system("python3 -m pip install music_tag")
    import music_tag
try:
    from pytubefix import YouTube, Playlist, exceptions
except:
    os.system("python3 -m pip install pytubefix")
    from pytubefix import YouTube, Playlist, exceptions
from time import sleep
from threading import Thread
import requests


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


outputPath = "./youtubeDownloader/"
threadQueue = {}


def get(url: str, dest_folder: str, dest_name: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    filename = dest_name
    file_path = os.path.join(dest_folder, filename)
    r = requests.get(url, stream=True)
    if r.ok:
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("img download failed: status code {}\n{}".format(r.status_code, r.text))
    return file_path


def downloadSong(link, format):
    yt = YouTube(link)
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
    imgPath = outputPath + "img/"
    vId = 0
    for yt in pl.videos:

        def _th(format, outputPath, imgPath, yt, vId):
            try:
                if format == "mp3":
                    ys = yt.streams.get_audio_only()
                    songName = ys.default_filename.replace("/", "-")
                    if not os.path.exists(outputPath + f"/{vId} | {songName}"):
                        songPath = ys.download(
                            outputPath,
                            filename=f"{vId} | {songName}",
                            mp3=False,
                        )
                        get(
                            yt.thumbnail_url,
                            imgPath,
                            "".join(f"{vId} | {songName}".split(".")[0] + ".png"),
                        )
                        song = music_tag.load_file(songPath)
                        with open(
                            imgPath
                            + "".join(f"{vId} | {songName}".split(".")[0] + ".png"),
                            "rb",
                        ) as imgFile:
                            song["artwork"] = imgFile.read()
                        song.save()
                        print(f"Finished download of {songName}")
                    else:
                        print(f"Found cached version of {songName}")
                else:
                    songName = ys.default_filename.replace("/", "-")
                    ys = yt.streams.get_highest_resolution()
                    songPath = ys.download(outputPath, filename=f"{vId} | {songName}")
                    print(f"Finished download of {songName}")
            except:
                ...
            finally:
                del threadQueue[vId]

        t = Thread(
            target=_th,
            args=(
                format,
                outputPath,
                imgPath,
                yt,
                vId,
            ),
        ).start()

        threadQueue[vId] = t
        sleep(0.1)

        vId += 1
    while len(threadQueue) > 0:
        try:
            for t in threadQueue:
                t.join()
        except:
            ...


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
        format = input("\nWhich format? mp(3/4):  ").lower()
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
                                f'./ffmpeg -y -v panic -i "{dirInput}" "{dirOutput}"'
                            )
                            print(f"Converted {name}")
                # except:
                # print("file conversion error")
