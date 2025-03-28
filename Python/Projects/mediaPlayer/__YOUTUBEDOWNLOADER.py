from pytubefix import YouTube, Playlist, exceptions, Channel, Search
import os
import requests
from threading import Thread as _Thread
import threading as th
import time
import subprocess
import music_tag
from typing import Callable, Any

os.chdir(os.path.dirname(__file__))

result = subprocess.run(
    ["node", "one-shot.js"],
    cwd="./po-token-generator/examples/",
    capture_output=True,
    text=True,
)
exampleOutput = """{
  visitorData: '',
  poToken: ''
}"""


visitorData = ""
poToken = ""
data = result.stdout.splitlines()
for s in data[1:-1]:
    if "visitorData" in s:
        visitorData = s.split(": ")[1].split(",")[0].strip("'")
    elif "poToken" in s:
        poToken = s.split(": ")[1].split(",")[0].strip("'")

os.chdir("youtubeDownloader")
with open("spoofedToken.json", "w") as f:
    f.write(
        '{\n\t"visitorData":"' + visitorData + '",\n\t"poToken":"' + poToken + '"\n}'
    )


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


pathSeparator = "\\"


def checkValidLink(link: str):
    retVal = False
    if link.startswith("http://") or link.startswith("https://"):
        if "youtube.com" in link or "youtu.be" in link:
            if "playlist" in link or "list=" in link:
                retVal = True

    return retVal


def pathSafe(name: str, replace: bool = False):
    for index in [
        ["/", "-"],
        ["|", "-"],
        ["\\", "-"],
        ["*", ""],
        ['"', ""],
        [":", " -"],
        ["?", ""],
        ["<", ""],
        [">", ""],
    ]:
        try:
            name = name.replace(index[0], index[1])
        except:
            ...
    if replace:
        name = f"{"0"*(3-len(name.split(" - ")[0]))}{name.split(' - ')[0]} - {" - ".join(name.split(' - ')[1:])}"
    return name


def get_cover_image(url: str, dest_folder: str, dest_name: str):
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
        get_cover_image(url, dest_folder, dest_name)


def apply_cover_image(url, dest_folder, songName, level=0):
    if level > 5:
        print(
            f"{Color.RED}Failed to download cover image after multiple attempts{Color.RESET}"
        )
        return False
    songName = songName.replace(".m4a", ".png")
    file_path = get_cover_image(url=url, dest_folder=dest_folder, dest_name=songName)
    if file_path is not None:
        songPath = os.path.join(
            dest_folder.split("/")[0], songName.replace(".png", ".m4a")
        ).replace("\\img\\", "\\")
        if os.path.exists(songPath):
            song = music_tag.load_file(songPath)
            with open(file_path, "rb") as imgFile:
                song["artwork"] = imgFile.read()
            song.save()
            print(
                f"| {Color.LIGHT_GREEN}Applied art to {Color.LIGHT_CYAN}{songName}{Color.RESET}"
            )
        else:
            print(f"| {Color.RED}File {songPath} does not exist{Color.RESET}")
    else:
        print(f"| {Color.RED}Failed to download cover image{Color.RESET}")
        return apply_cover_image(url, dest_folder, songName, level + 1)


base_callback_addon = lambda *args, **kwargs: ...
initalize_callback = lambda *args, **kwargs: print("Callback not registered")


def registerCallbackFunction(callback: Callable[[Any], Any]):
    global base_callback_addon
    base_callback_addon = callback


def registerInitalizeCallbackFunction(callback: Callable[[Any], Any]):
    global initalize_callback
    initalize_callback = callback


def base_callback(
    video,
    id,
    title,
    list,
    progress: float = 0,
    status: list = ["Queued", "Downloading", "finished"],
):
    base_callback_addon(
        video=video,
        id=id,
        title=title,
        list=list,
        progress=progress,
        status=status,
    )


def downloadCallbackFunction(video, id, title, list, status):
    def download_callback(
        chunk: bytes,
        bytes_remaining: int,
    ):
        progress = round((1 - bytes_remaining / 1000000) * 100, 2)
        base_callback(
            video=video,
            id=id,
            title=title,
            list=list,
            progress=progress,
            status=status,
        )

    return download_callback


class CORE:
    downloadingActive = False

    def downloadVideo(self, link):
        self.downloadingActive = True

        def _th():
            try:
                yt = YouTube(
                    link,
                    client="WEB",
                    token_file="spoofedToken.json",
                )
                ys = yt.streams.get_highest_resolution()
                title = pathSafe(f"{len(os.listdir('Videos'))} - {yt.title}", True)
                base_callback(
                    video=yt,
                    id=len(os.listdir("Videos")),
                    title=title,
                    list=[yt],
                    status=["Queued"],
                )
                print(f"Downloading {Color.CYAN}{title}{Color.RESET}")
                ys.on_progress_for_chunks = downloadCallbackFunction(
                    video=yt,
                    id=len(os.listdir("Videos")),
                    title=title,
                    list=[yt],
                    status=["Downloading"],
                )
                ys.download(
                    "Videos",
                    filename=title + ".mp4",
                )
                base_callback(
                    video=yt,
                    id=len(os.listdir("Videos")),
                    title=title,
                    list=[yt],
                    progress=100,
                    status=["Finished"],
                )
                print(f"Downloaded {Color.GREEN}{title}{Color.RESET}")
            except exceptions.VideoUnavailable:
                print(Color.RED + "Video is unavailable" + Color.RESET)
            except exceptions.VideoPrivate:
                print(Color.RED + "Video is private" + Color.RESET)
            except exceptions.VideoRegionBlocked:
                print(Color.RED + "Video is blocked in your region" + Color.RESET)
            except Exception as e:
                print(e)
            self.downloadingActive = False

        thread = _Thread(target=_th)
        thread.start()

    def downloadSong(self, link):
        self.downloadingActive = True

        def _th():
            try:
                yt = YouTube(
                    link,
                    client="WEB",
                    token_file="spoofedToken.json",
                )
                ys = yt.streams.get_audio_only()
                title = pathSafe(f"{len(os.listdir("Songs"))} - {title}", True) + ".m4a"
                ys.on_progress_for_chunks = downloadCallbackFunction(
                    video=yt,
                    id=len(os.listdir("Songs")),
                    title=title,
                    list=[yt],
                    status=["Downloading"],
                )
                ys.download(
                    output_path="Songs",
                    filename=title,
                )
                print(f"Downloaded {Color.GREEN}{title}{Color.RESET}")
                base_callback(
                    video=yt,
                    id=len(os.listdir("Songs")),
                    title=title,
                    list=[yt],
                    progress=100,
                    status=["Finished"],
                )

                apply_cover_image(yt.thumbnail_url, os.path.join("Songs", "img"), title)
                print(f"Downloaded {Color.GREEN}{title}{Color.RESET}")
            except exceptions.VideoUnavailable:
                print(Color.RED + "Video is unavailable" + Color.RESET)
            except exceptions.VideoPrivate:
                print(Color.RED + "Video is private" + Color.RESET)
            except exceptions.VideoRegionBlocked:
                print(Color.RED + "Video is blocked in your region" + Color.RESET)
            except Exception as e:
                print(e)
            self.downloadingActive = False

        thread = _Thread(target=_th)
        thread.start()

    def downloadPlaylist_V(self, link):
        self.downloadingActive = True

        session = requests.Session()
        pl = Playlist(
            url=link,
            client="WEB",
            token_file="spoofedToken.json",
            session=session,
        )
        os.mkdir(path=pathSafe(pl.title))
        initalize_callback(pl)
        vId = 0
        for video in pl.videos:
            time.sleep(0.15)

            def _inThread(vId, video: YouTube):
                try:
                    title = pathSafe(f"{vId} - {video.title}", True)
                    base_callback(
                        video=video,
                        id=vId,
                        title=title,
                        list=pl.videos,
                        status=["Queued"],
                    )
                    ys = video.streams.get_highest_resolution()
                    ys.on_progress_for_chunks = downloadCallbackFunction(
                        video=video,
                        id=vId,
                        title=title,
                        list=pl.videos,
                        status=["Downloading"],
                    )
                    ys.download(
                        output_path=pathSafe(name=pl.title),
                        filename=title + ".mp4",
                    )
                    base_callback(
                        video=video,
                        id=vId,
                        title=title,
                        list=pl.videos,
                        progress=100,
                        status=["Finished"],
                    )
                    print(f"| - Downloaded {Color.CYAN}{title}{Color.RESET}")
                except exceptions.VideoUnavailable:
                    print(Color.RED + "Video is unavailable" + Color.RESET)
                except exceptions.VideoPrivate:
                    print(Color.RED + "Video is private" + Color.RESET)
                except exceptions.VideoRegionBlocked:
                    print(Color.RED + "Video is blocked in your region" + Color.RESET)
                except Exception as e:
                    print(e)

            _Thread(target=_inThread, args=(vId, video)).start()
            vId += 1

        print(
            f"Downloaded {Color.GREEN}{pl.title}{Color.RESET} --  awaiting stragglers"
        )
        self.downloadingActive = False

    def downloadPlaylist_S(self, link):
        if checkValidLink(link) is False:
            print(Color.RED + "Invalid Link" + Color.RESET)
            return
        else:
            print(Color.GREEN + "Valid Link" + Color.RESET)

        self.downloadingActive = True
        pl = Playlist(
            url=link,
            token_file="spoofedToken.json",
            allow_oauth_cache=False,
        )
        print(f"starting download of playlist {pl.title}:")
        initalize_callback(pl)
        print(f"Downloading {Color.CYAN}{pl.title}{Color.RESET}")
        try:
            os.mkdir(path=pathSafe(pl.title))
        except FileExistsError:
            print(
                f"{Color.YELLOW}Folder {pl.title} already exists{Color.RESET}, downloading into {os.path.abspath(os.curdir)}"
            )
        index = 0
        for _video in pl.videos:
            time.sleep(0.05)
            _title = _video.title
            print(f"| - {Color.YELLOW}Downloading{Color.RESET} {_title}")

            def _inThread(title, video: YouTube):
                title = pathSafe(f"{index} - {title}", True)
                base_callback(
                    video=video,
                    id=index,
                    title=title,
                    list=pl.videos,
                    status=["Queued"],
                )
                try:
                    ys = video.streams.get_audio_only()
                    ys.on_progress_for_chunks = downloadCallbackFunction(
                        video=video,
                        id=index,
                        title=title,
                        list=pl.videos,
                        status=["Downloading"],
                    )
                    ys.download(
                        output_path=pathSafe(pl.title),
                        filename=title + ".m4a",
                    )
                    print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
                    apply_cover_image(
                        video.thumbnail_url,
                        pathSafe(pl.title) + os.path.sep + "img",
                        title + ".m4a",
                    )
                    base_callback(
                        video=video,
                        id=index,
                        title=title,
                        list=pl.videos,
                        progress=100,
                        status=["Finished"],
                    )
                except exceptions.VideoUnavailable:
                    print(Color.RED + "Video is unavailable" + Color.RESET)
                except exceptions.VideoPrivate:
                    print(Color.RED + "Video is private" + Color.RESET)
                except exceptions.VideoRegionBlocked:
                    print(Color.RED + "Video is blocked in your region" + Color.RESET)

            _Thread(target=_inThread, args=(_title, _video)).start()
            index += 1
        print(
            f"Downloaded {Color.GREEN}{pl.title}{Color.RESET} --  awaiting stragglers"
        )
        self.downloadingActive = False

    def downloadArtist_V(self, link):
        ch = Channel(
            url=link,
            client="WEB",
            token_file="spoofedToken.json",
        )
        os.mkdir(path=pathSafe(ch.channel_name))
        for _list in ch.home:
            for video in _list.videos:
                time.sleep(0.15)

                def _inThread():
                    try:
                        title = video.title
                        video.streams.get_highest_resolution().download(
                            output_path=pathSafe(name=ch.channel_name),
                            filename=pathSafe(title) + ".mp4",
                        )
                        print(f"| - Downloaded {Color.CYAN}{title}{Color.RESET}")
                    except exceptions.VideoUnavailable:
                        print(Color.RED + "Video is unavailable" + Color.RESET)
                    except exceptions.VideoPrivate:
                        print(Color.RED + "Video is private" + Color.RESET)
                    except exceptions.VideoRegionBlocked:
                        print(
                            Color.RED + "Video is blocked in your region" + Color.RESET
                        )
                    except Exception as e:
                        print(e)

                _Thread(target=_inThread).start()

            print(f"Downloaded {Color.GREEN}{ch.channel_name}{Color.RESET}")

    def downloadArtist_S(self, link):
        ch = Channel(
            url=link,
            client="WEB",
            token_file="spoofedToken.json",
        )
        print(f"starting download of playlist {ch.channel_name}:")
        try:
            os.mkdir(path=pathSafe(ch.channel_name))
        except FileExistsError:
            print(
                f"{Color.YELLOW}Folder {ch.channel_name} already exists{Color.RESET}, downloading into {os.path.abspath(os.curdir)}"
            )
        index = 0
        for _list in ch.home:
            for _video in _list.videos:
                index += 1
                time.sleep(0.05)
                _title = _video.title
                print(f"| - {Color.YELLOW}Downloading{Color.RESET} {_title}")

                def _inThread(title, video):
                    try:
                        video.streams.get_audio_only().download(
                            output_path=pathSafe(ch.channel_name),
                            filename=f"{index} - {pathSafe(name=title)}" + ".m4a",
                        )
                        print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
                    except exceptions.VideoUnavailable:
                        print(Color.RED + "Video is unavailable" + Color.RESET)
                    except exceptions.VideoPrivate:
                        print(Color.RED + "Video is private" + Color.RESET)
                    except exceptions.VideoRegionBlocked:
                        print(
                            Color.RED + "Video is blocked in your region" + Color.RESET
                        )
                    except Exception as e:
                        print(e)

                _Thread(target=_inThread, args=(_title, _video), daemon=True).start()


if __name__ == "__main__":
    while True:
        try:
            print(
                f"\n{Color.YELLOW}YouTube Downloader{Color.RESET}\n\n{Color.BLUE}1.{Color.RESET} Download Video\n{Color.BLUE}2.{Color.RESET} Download Song\n{Color.BLUE}3.{Color.RESET} Download Playlist (Videos)\n{Color.BLUE}4.{Color.RESET} Download Playlist (Songs)\n{Color.BLUE}5.{Color.RESET} Download Artist (Videos)\n{Color.BLUE}6.{Color.RESET} Download Artist (Songs)\n\n{Color.RED}0.{Color.RESET} Exit"
            )
            option = input(f"\n{Color.GREEN}> {Color.RESET}")
            if option == "1":
                link = input(f"{Color.GREEN}url> {Color.RESET}")
                CORE().downloadVideo(link)
            elif option == "2":
                link = input(f"{Color.GREEN}url> {Color.RESET}")
                CORE().downloadSong(link)
            elif option == "3":
                link = input(f"{Color.GREEN}url> {Color.RESET}")
                CORE().downloadPlaylist_V(link)
            elif option == "4":
                link = input(f"{Color.GREEN}url> {Color.RESET}")
                CORE().downloadPlaylist_S(link)
            elif option == "5":
                link = input(f"{Color.GREEN}url> {Color.RESET}")
                CORE().downloadArtist_V(link)
            elif option == "6":
                link = input(f"{Color.GREEN}url> {Color.RESET}")
                CORE().downloadArtist_S(link)
            elif option == "0":
                exit()
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(Color.RED + f"Something Went Wrong:\n" + Color.RESET + str(e))

        time.sleep(1)

        for thread in th.enumerate():
            if thread is not th.main_thread():
                thread.join()
