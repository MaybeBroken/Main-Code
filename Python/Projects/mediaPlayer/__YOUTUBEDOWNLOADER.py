import sys
import subprocess


def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        __import__(package)
        print(f"Installed {package} successfully.")


def update_package(package):
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", package]
        )
        print(f"Updated {package} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update {package}: {e}")


try:
    from pytubefix import YouTube, Playlist, exceptions, Channel, Search
except ImportError:
    install_and_import("pytubefix")
    from pytubefix import YouTube, Playlist, exceptions, Channel, Search

update_package("pytubefix")


try:
    import requests
except ImportError:
    install_and_import("requests")
    import requests

import os
from threading import Thread as _Thread
import threading as th
import time

try:
    import music_tag
except ImportError:
    install_and_import("music-tag")
    import music_tag

try:
    from typing import Callable, Any, overload
except ImportError:
    install_and_import("typing")
    from typing import Callable, Any, overload

try:
    import json
except ImportError:
    install_and_import("json")
    import json

os.chdir(os.path.dirname(__file__))

semaphore = th.Semaphore(20)

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

if not os.path.exists("youtubeDownloader"):
    os.mkdir("youtubeDownloader")
os.chdir("youtubeDownloader")
with open("spoofedToken.json", "w") as f:
    f.write(
        '{\n\t"visitorData":"' + visitorData + '",\n\t"poToken":"' + poToken + '"\n}'
    )

if __name__ == "__main__":

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

else:

    class Color:
        GREEN = ""
        LIGHT_GREEN = ""
        RED = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        BOLD = ""
        CYAN = ""
        LIGHT_CYAN = ""
        LIGHT_GREY = ""
        DARK_GREY = ""
        BLACK = ""
        WHITE = ""
        INVERT = ""
        RESET = ""


pathSeparator = "\\"


def checkValidLink(link: str):
    retVal = False
    if link.startswith("http://") or link.startswith("https://"):
        if "youtube.com" in link or "youtu.be" in link:
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
        parts = name.split(" - ")
        while (
            len(parts) > 1
            and parts[0].isdigit()
            and parts[1].isdigit()
            and len(parts[0]) == 3
            and len(parts[1]) == 3
        ):
            parts = parts[0] + parts[2:]
            name = " - ".join(parts)
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
        return "EXISTS"
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
    if file_path is not None and file_path != "EXISTS":
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
    elif file_path == "EXISTS":
        print(f"| {Color.YELLOW}Cover image already exists{Color.RESET}")
        return "EXISTS"
    else:
        print(f"| {Color.RED}Failed to download cover image{Color.RESET}")
        return apply_cover_image(url, dest_folder, songName, level + 1)


base_callback_addon = lambda *args, **kwargs: ...
initalize_callback = lambda *args, **kwargs: print("INIT Callback not registered")
finalize_callback = lambda *args, **kwargs: print("POST Callback not registered")


def registerCallbackFunction(callback: Callable[[Any], Any]):
    global base_callback_addon
    base_callback_addon = callback


def registerInitalizeCallbackFunction(callback: Callable[[Any], Any]):
    global initalize_callback
    initalize_callback = callback


def registerFinalizeCallbackFunction(callback: Callable[[Any], Any]):
    global finalize_callback
    finalize_callback = callback


def base_callback(
    video,
    id,
    title,
    list,
    chunk: bytes = b"",
    progress: float = 0,
    status: list = ["Queued", "Downloading", "finished"],
):
    base_callback_addon(
        video=video,
        id=id,
        title=title,
        list=list,
        chunk=chunk,
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
            chunk=chunk,
            progress=progress,
            status=status,
        )

    return download_callback


def diff(pl: Playlist, mtd: dict):
    pl_title = pl.title
    mtd_title = mtd["title"]
    if pl_title == pathSafe(mtd_title):
        pl_vids = []
        th_queue: list[_Thread] = []
        for _obj in pl.videos:

            def inFunc(obj: YouTube):
                print(f"Checking {obj.title}")
                pl_vids.append(
                    {
                        "title": obj.title,
                        "url": obj.watch_url,
                        "thumbnail_url": obj.thumbnail_url,
                        "channel_id": obj.channel_id,
                        "channel_url": obj.channel_url,
                        "publish_date": str(obj.publish_date),
                    }
                )

            th_queue.append(_Thread(target=inFunc, args=(_obj,)))
        for thread in th_queue:
            thread.start()
        for thread in th_queue:
            thread.join()
        if pl_vids == mtd["objects"]:
            return False
        else:
            old = pl_vids
            new = mtd["objects"]
            removed = []
            added = []
            for obj in old:
                if obj not in new:
                    removed.append(obj)
            for obj in new:
                if obj not in old:
                    added.append(obj)

            return [added, removed]


def writeJson(
    title,
    pl: Playlist,
    objects: list[YouTube],
    path: str,
    o_type: str = "s|v",
):
    content = {
        "title": title,
        "playlist": {
            "title": pl.title,
            "url": pl.playlist_url,
            "length": pl.length,
            "views": pl.views,
            "thumbnail_url": pl.thumbnail_url,
        },
        "objects": [],
        "type": o_type,
    }
    th_queue: list[_Thread] = []
    for _obj in objects:

        def inFunc(obj: YouTube):
            print(f"Writing {obj.title} to json")
            content["objects"].append(
                {
                    "title": obj.title,
                    "url": obj.watch_url,
                    "thumbnail_url": obj.thumbnail_url,
                    "channel_id": obj.channel_id,
                    "channel_url": obj.channel_url,
                    "publish_date": str(obj.publish_date),
                }
            )

        th_queue.append(_Thread(target=inFunc, args=(_obj,)))
    for thread in th_queue:
        thread.start()
    for thread in th_queue:
        thread.join()
    with open(path, "w") as json_file:
        json.dump(content, json_file, indent=4)
    print(f"Playlist {title} written to {path}")


def renameSongs(folder):
    fileSet = set()
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".m4a"):
                fileSet.add(file)
    fileSet = sorted(fileSet)
    for index, file in enumerate(fileSet):
        newName = pathSafe(f"{index} - {' - '.join(file.split(' - ')[1:])}", True)
        oldPath = os.path.join(folder, file)
        newPath = os.path.join(folder, newName)
        if not os.path.exists(newPath):
            os.rename(oldPath, newPath)
            print(f"Renamed {file} to {newName}")
        else:
            print(f"File {newName} already exists, skipping rename")


def deleteByName(folder, name):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if name in file:
                os.remove(os.path.join(root, file))
                print(f"Deleted {file}")


class UPDATE:
    def updatePlaylist(self, metadata: dict):
        if metadata["type"] == "s":
            print(f"Updating {Color.CYAN}{metadata['title']}{Color.RESET}")
            pl = Playlist(
                url=metadata["playlist"]["url"],
                token_file="spoofedToken.json",
                allow_oauth_cache=False,
            )
            _diff = diff(pl, metadata)
            if _diff is False or (len(_diff[0]) == 0 and len(_diff[1]) == 0):
                print(f"{Color.GREEN}No changes detected{Color.RESET}")
                return
            else:
                print(f"{Color.YELLOW}Changes detected{Color.RESET}")
                print(f"Removed: {Color.RED}{len(_diff[0])}{Color.RESET}")
                print(f"Added: {Color.GREEN}{len(_diff[1])}{Color.RESET}")
                index = 0
                for obj in _diff[0]:
                    deleteByName(pathSafe(pl.title), obj["title"])
                    print(f"| - {Color.RED}Removed{Color.RESET} {obj['title']}")
                for obj in _diff[1]:
                    _video = YouTube(
                        url=obj["url"],
                        token_file="spoofedToken.json",
                        allow_oauth_cache=False,
                    )
                    time.sleep(0.05)
                    _title = _video.title
                    print(f"| - {Color.YELLOW}Downloading{Color.RESET} {_title}")

                    def _inThread(title, video: YouTube):
                        title = pathSafe(f"{index} - {title}", True) + ".m4a"
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
                                filename=title,
                            )
                            print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
                            apply_cover_image(
                                video.thumbnail_url,
                                pathSafe(pl.title) + os.path.sep + "img",
                                title,
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
                            print(
                                Color.RED
                                + "Video is blocked in your region"
                                + Color.RESET
                            )

                    _Thread(target=_inThread, args=(_title, _video)).start()
                    index += 1
                    print(
                        f"Downloaded {Color.GREEN}{pl.title}{Color.RESET} --  awaiting stragglers"
                    )
                    finalize_callback(pl)
                    self.downloadingActive = False
                renameSongs(pathSafe(pl.title))
                writeJson(
                    title=pl.title,
                    pl=pl,
                    objects=pl.videos,
                    path=os.path.join(pathSafe(pl.title), "metadata.json"),
                    o_type="s",
                )


class CORE:
    downloadingActive = False

    def downloadVideo(self, link):
        os.chdir("youtubeDownloader")
        if checkValidLink(link) is False:
            print(Color.RED + "Invalid Link" + Color.RESET)
            return
        else:
            print(Color.GREEN + "Valid Link" + Color.RESET)

        self.downloadingActive = True
        try:
            yt = YouTube(
                link,
                client="WEB_EMBED",
                token_file="spoofedToken.json",
            )
            initalize_callback(yt)
            title = pathSafe(f"0 - {yt.title}", True) + ".mp4"
            print(f"| - {Color.YELLOW}Downloading{Color.RESET} {title}")
            base_callback(
                video=yt,
                id=0,
                title=title,
                list=[yt],
                status=["Queued"],
            )
            ys = yt.streams.get_highest_resolution()
            ys.on_progress_for_chunks = downloadCallbackFunction(
                video=yt,
                id=0,
                title=title,
                list=[yt],
                status=["Downloading"],
            )
            ys.download(
                output_path="Videos",
                filename=title,
            )
            print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
            base_callback(
                video=yt,
                id=0,
                title=title,
                list=[yt],
                progress=100,
                status=["Finished"],
            )
        except exceptions.VideoUnavailable:
            print(Color.RED + "Video is unavailable" + Color.RESET)
        except exceptions.VideoPrivate:
            print(Color.RED + "Video is private" + Color.RESET)
        except exceptions.VideoRegionBlocked:
            print(Color.RED + "Video is blocked in your region" + Color.RESET)
        except Exception as e:
            print(f"Error downloading video: {e}")
        self.downloadingActive = False
        finalize_callback(link)

    def downloadSong(self, link):
        os.chdir("youtubeDownloader")
        if checkValidLink(link) is False:
            print(Color.RED + "Invalid Link" + Color.RESET)
            return
        else:
            print(Color.GREEN + "Valid Link" + Color.RESET)

        self.downloadingActive = True
        try:
            yt = YouTube(
                link,
                client="WEB_EMBED",
                token_file="spoofedToken.json",
            )
            initalize_callback(yt)
            title = pathSafe(f"0 - {yt.title}", True) + ".m4a"
            print(f"| - {Color.YELLOW}Downloading{Color.RESET} {title}")
            base_callback(
                video=yt,
                id=0,
                title=title,
                list=[yt],
                status=["Queued"],
            )
            ys = yt.streams.get_audio_only()
            ys.on_progress_for_chunks = downloadCallbackFunction(
                video=yt,
                id=0,
                title=title,
                list=[yt],
                status=["Downloading"],
            )
            ys.download(
                output_path="Songs",
                filename=title,
            )
            print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
            apply_cover_image(yt.thumbnail_url, os.path.join("Songs", "img"), title)
            base_callback(
                video=yt,
                id=0,
                title=title,
                list=[yt],
                progress=100,
                status=["Finished"],
            )
        except exceptions.VideoUnavailable:
            print(Color.RED + "Video is unavailable" + Color.RESET)
        except exceptions.VideoPrivate:
            print(Color.RED + "Video is private" + Color.RESET)
        except exceptions.VideoRegionBlocked:
            print(Color.RED + "Video is blocked in your region" + Color.RESET)
        except Exception as e:
            print(f"Error downloading song: {e}")
        self.downloadingActive = False
        finalize_callback(link)

    def downloadPlaylist_V(self, link):
        os.chdir("youtubeDownloader")
        if checkValidLink(link) is False:
            print(Color.RED + "Invalid Link" + Color.RESET)
            return
        else:
            print(Color.GREEN + "Valid Link" + Color.RESET)

        self.downloadingActive = True
        pl = Playlist(
            url=link,
            client="WEB_EMBED",
            token_file="spoofedToken.json",
            allow_oauth_cache=False,
        )
        initalize_callback(pl)
        print(f"starting download of playlist {pl.title}:")
        print(f"Downloading {Color.CYAN}{pl.title}{Color.RESET}")
        try:
            os.mkdir(path=pathSafe(pl.title))
        except FileExistsError:
            print(
                f"{Color.YELLOW}Folder {pl.title} already exists{Color.RESET}, downloading into {os.path.abspath(os.curdir)}"
            )
        index = 0
        sucessfulVideos = []
        threadQueue: list[_Thread] = []
        for _video in pl.videos:
            time.sleep(0.1)

            def _inThread(video: YouTube, index: int):
                print(f"Starting download for video {index}")
                title = pathSafe(f"{index} - {video.title}", True) + ".mp4"
                print(f"| - {Color.YELLOW}Downloading{Color.RESET} {title}")
                base_callback(
                    video=video,
                    id=index,
                    title=title,
                    list=pl.videos,
                    status=["Queued"],
                )
                try:
                    ys = video.streams.get_highest_resolution()
                    ys.on_progress_for_chunks = downloadCallbackFunction(
                        video=video,
                        id=index,
                        title=title,
                        list=pl.videos,
                        status=["Downloading"],
                    )
                    ys.download(
                        output_path=pathSafe(pl.title),
                        filename=title,
                    )
                    print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
                    base_callback(
                        video=video,
                        id=index,
                        title=title,
                        list=pl.videos,
                        progress=100,
                        status=["Finished"],
                    )
                    sucessfulVideos.append(video)
                except exceptions.VideoUnavailable:
                    print(Color.RED + "Video is unavailable" + Color.RESET)
                except exceptions.VideoPrivate:
                    print(Color.RED + "Video is private" + Color.RESET)
                except exceptions.VideoRegionBlocked:
                    print(Color.RED + "Video is blocked in your region" + Color.RESET)
                except Exception as e:
                    print(f"Error downloading video: {e}")

            threadQueue.append(_Thread(target=_inThread, args=(_video, index)))
            index += 1
        for thread in threadQueue:
            thread.start()
        for thread in threadQueue:
            thread.join()
        print(f"Downloaded {Color.GREEN}{pl.title}{Color.RESET}")
        if len(sucessfulVideos) > 0:
            writeJson(
                title=pl.title,
                pl=pl,
                objects=sucessfulVideos,
                path=os.path.join(pathSafe(pl.title), "metadata.json"),
                o_type="v",
            )
        finalize_callback(pl)
        self.downloadingActive = False

    def downloadPlaylist_S(self, link):
        os.chdir("youtubeDownloader")
        if checkValidLink(link) is False:
            print(Color.RED + "Invalid Link" + Color.RESET)
            return
        else:
            print(Color.GREEN + "Valid Link" + Color.RESET)

        self.downloadingActive = True
        pl = Playlist(
            url=link,
            client="WEB_EMBED",
            token_file="spoofedToken.json",
            allow_oauth_cache=False,
        )
        initalize_callback(pl)
        print(f"starting download of playlist {pl.title}:")
        print(f"Downloading {Color.CYAN}{pl.title}{Color.RESET}")
        try:
            os.mkdir(path=pathSafe(pl.title))
        except FileExistsError:
            print(
                f"{Color.YELLOW}Folder {pl.title} already exists{Color.RESET}, downloading into {os.path.abspath(os.curdir)}"
            )
        index = 0
        sucessfulVideos = []
        threadQueue: list[_Thread] = []
        for _video in pl.videos:

            def _inThread(video: YouTube, index: int):
                print(f"Starting download for video {index}")
                title = video.title
                print(f"| - {Color.YELLOW}Downloading{Color.RESET} {title}")
                title = pathSafe(f"{index} - {video.title}", True) + ".m4a"
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
                        filename=title,
                    )
                    print(f"| - {Color.GREEN}Finished downloading{Color.RESET} {title}")
                    apply_cover_image(
                        video.thumbnail_url,
                        pathSafe(pl.title) + os.path.sep + "img",
                        title,
                    )
                    base_callback(
                        video=video,
                        id=index,
                        title=title,
                        list=pl.videos,
                        progress=100,
                        status=["Finished"],
                    )
                    sucessfulVideos.append(video)
                except exceptions.VideoUnavailable:
                    print(Color.RED + f"Video {video} is unavailable" + Color.RESET)
                except exceptions.VideoPrivate:
                    print(Color.RED + f"Video {video} is private" + Color.RESET)
                except exceptions.VideoRegionBlocked:
                    print(
                        Color.RED
                        + f"Video {video} is blocked in your region"
                        + Color.RESET
                    )
                except Exception as e:
                    print(f"Error downloading video: {e}")

            threadQueue.append(_Thread(target=_inThread, args=(_video, index)))
            index += 1
        for thread in threadQueue:
            time.sleep(0.5)
            thread.start()
        for thread in threadQueue:
            thread.join()
        print(f"Downloaded {Color.GREEN}{pl.title}{Color.RESET}")
        if len(sucessfulVideos) > 0:
            writeJson(
                title=pl.title,
                pl=pl,
                objects=sucessfulVideos,
                path=os.path.join(pathSafe(pl.title), "metadata.json"),
                o_type="s",
            )
        finalize_callback(pl)
        self.downloadingActive = False

    def downloadArtist_V(self, link):
        if checkValidLink(link) is False:
            print(Color.RED + "Invalid Link" + Color.RESET)
            return
        else:
            print(Color.GREEN + "Valid Link" + Color.RESET)

        self.downloadingActive = True
        ch = Channel(
            url=link,
            client="WEB_EMBED",
            token_file="spoofedToken.json",
        )
        print(f"starting download of artist {ch.channel_name}:")
        try:
            os.mkdir(path=pathSafe(ch.channel_name))
        except FileExistsError:
            print(
                f"{Color.YELLOW}Folder {ch.channel_name} already exists{Color.RESET}, downloading into {os.path.abspath(os.curdir)}"
            )
        index = 0
        for _list in ch.home:
            for _video in _list.videos:
                time.sleep(0.05)
                _title = _video.title
                print(f"| - {Color.YELLOW}Downloading{Color.RESET} {_title}")

                def _inThread(title, video: YouTube):
                    title = pathSafe(f"{index} - {title}", True) + ".mp4"
                    base_callback(
                        video=video,
                        id=index,
                        title=title,
                        list=_list.videos,
                        status=["Queued"],
                    )
                    try:
                        ys = video.streams.get_highest_resolution()
                        ys.on_progress_for_chunks = downloadCallbackFunction(
                            video=video,
                            id=index,
                            title=title,
                            list=_list.videos,
                            status=["Downloading"],
                        )
                        ys.download(
                            output_path=pathSafe(ch.channel_name),
                            filename=title,
                        )
                        print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
                        base_callback(
                            video=video,
                            id=index,
                            title=title,
                            list=_list.videos,
                            progress=100,
                            status=["Finished"],
                        )
                    except exceptions.VideoUnavailable:
                        print(Color.RED + "Video is unavailable" + Color.RESET)
                    except exceptions.VideoPrivate:
                        print(Color.RED + "Video is private" + Color.RESET)
                    except exceptions.VideoRegionBlocked:
                        print(
                            Color.RED + "Video is blocked in your region" + Color.RESET
                        )

                _Thread(target=_inThread, args=(_title, _video)).start()
                index += 1
        print(
            f"Downloaded {Color.GREEN}{ch.channel_name}{Color.RESET} --  awaiting stragglers"
        )
        self.downloadingActive = False

    def downloadArtist_S(self, link):
        os.chdir("youtubeDownloader")
        if checkValidLink(link) is False:
            print(Color.RED + "Invalid Link" + Color.RESET)
            return
        else:
            print(Color.GREEN + "Valid Link" + Color.RESET)

        self.downloadingActive = True
        ch = Channel(
            url=link,
            client="WEB_EMBED",
            token_file="spoofedToken.json",
        )
        print(f"starting download of artist {ch.channel_name}:")
        try:
            os.mkdir(path=pathSafe(ch.channel_name))
        except FileExistsError:
            print(
                f"{Color.YELLOW}Folder {ch.channel_name} already exists{Color.RESET}, downloading into {os.path.abspath(os.curdir)}"
            )
        _index = 0
        for _list in ch.home:
            for _video in _list.videos:
                time.sleep(0.05)

                def _inThread(video: YouTube, index: int):
                    title = video.title
                    print(f"| - {Color.YELLOW}Downloading{Color.RESET} {title}")
                    title = pathSafe(f"{index} - {title}", True) + ".m4a"
                    base_callback(
                        video=video,
                        id=index,
                        title=title,
                        list=_list.videos,
                        status=["Queued"],
                    )
                    try:
                        ys = video.streams.get_audio_only()
                        ys.on_progress_for_chunks = downloadCallbackFunction(
                            video=video,
                            id=index,
                            title=title,
                            list=_list.videos,
                            status=["Downloading"],
                        )
                        ys.download(
                            output_path=pathSafe(ch.channel_name),
                            filename=title,
                        )
                        print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
                        base_callback(
                            video=video,
                            id=index,
                            title=title,
                            list=_list.videos,
                            progress=100,
                            status=["Finished"],
                        )
                    except exceptions.VideoUnavailable:
                        print(Color.RED + "Video is unavailable" + Color.RESET)
                    except exceptions.VideoPrivate:
                        print(Color.RED + "Video is private" + Color.RESET)
                    except exceptions.VideoRegionBlocked:
                        print(
                            Color.RED + "Video is blocked in your region" + Color.RESET
                        )

                _Thread(target=_inThread, args=(_video, _index)).start()
                _index += 1
        print(
            f"Downloaded {Color.GREEN}{ch.channel_name}{Color.RESET} --  awaiting stragglers"
        )
        self.downloadingActive = False


if __name__ == "__main__":
    while True:
        try:
            print(
                f"\n{Color.YELLOW}YouTube Downloader{Color.RESET}\n\n{Color.BLUE}\
1.{Color.RESET} Download Video\n{Color.BLUE}\
2.{Color.RESET} Download Song\n{Color.BLUE}\
3.{Color.RESET} Download Playlist (Videos)\n{Color.BLUE}\
4.{Color.RESET} Download Playlist (Songs)\n{Color.BLUE}\
5.{Color.RESET} Download Artist (Videos)\n{Color.BLUE}\
6.{Color.RESET} Download Artist (Songs)\n{Color.BLUE}\
7.{Color.RESET} Update Playlist\n\n{Color.RED}\
0.{Color.RESET} Exit"
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
            elif option == "7":
                print(
                    "\n".join(
                        os.listdir(
                            os.path.join(os.path.dirname(__file__), "youtubeDownloader")
                        )
                    )
                )
                path = input(f"{Color.GREEN}path> {Color.RESET}")
                playlist_data = json.load(
                    open(
                        os.path.join(
                            os.path.dirname(__file__),
                            "youtubeDownloader",
                            path,
                            "metadata.json",
                        ),
                        "r",
                    )
                )
                UPDATE().updatePlaylist(playlist_data)
            elif option == "0":
                exit()
        except KeyboardInterrupt:
            exit()
        # except Exception as e:
        #     print(Color.RED + f"Something Went Wrong:\n" + Color.RESET + str(e))

        time.sleep(1)

        for thread in th.enumerate():
            if thread is not th.main_thread():
                print(
                    f"{Color.YELLOW}Thread {thread.name} still running{Color.RESET}, waiting for it to finish..."
                )
                thread.join()
else:
    GLOBAL_NOTIFY = []

    def print(msg: str, *args: Any, **kwargs: Any) -> None:
        msg = msg.encode("ascii", "ignore").decode("ascii")
        filtered_msg = "".join(
            c
            for c in str(msg)
            if c.isalnum()
            or c.isspace()
            or c
            in [
                "-",
                "_",
                ":",
                ".",
                ",",
                "(",
                ")",
                "!",
                "?",
                "'",
                '"',
                "=",
                "+",
                "&",
                "%",
                "$",
                "#",
                "@",
                "^",
                "*",
                ">",
                "<",
                "/",
                "\\",
                "|",
                "{",
                "}",
                "[",
                "]",
            ]
        )
        GLOBAL_NOTIFY.append(filtered_msg)
