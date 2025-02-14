from pytubefix import YouTube, Playlist, exceptions, Channel, Search
import os
import requests
from threading import Thread as _Thread
import threading as th
import time
import subprocess
import music_tag

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

data = result.stdout.splitlines()
for s in data:
    if "visitorData" in s:
        visitorData = s.split(": ")[1].split(",")[0].strip("'")
    if "poToken" in s:
        poToken = s.split(": ")[1].split(",")[0].strip("'")

with open("spoofedToken.json", "w") as f:
    f.write(
        '{\n\t"visitorData":"' + visitorData + '",\n\t"poToken":"' + poToken + '"\n}'
    )
os.chdir("youtubeDownloader")


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


def apply_cover_image(url, dest_folder, songName):
    songName = songName.replace(".m4a", ".png")
    if (
        not get_cover_image(
            url=url,
            dest_folder=dest_folder,
            dest_name=songName,
        )
        == None
    ):
        songPath = os.path.join(dest_folder, songName)
        song = music_tag.load_file(songPath)
        with open(
            songPath.replace(".png", ".m4a"),
            "rb",
        ) as imgFile:
            song["artwork"] = imgFile.read()
        song.save()
        print(
            f"{Color.LIGHT_GREEN}Applied art to {Color.LIGHT_CYAN}{songName}{Color.RESET}"
        )


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
                title = yt.title
                print(f"Downloading {Color.CYAN}{title}{Color.RESET}")
                ys.download(
                    "Videos",
                    filename=pathSafe(f"{len(os.listdir("Videos"))} - {title}", True)
                    + ".mp4",
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
                ys.download(
                    output_path="Songs",
                    filename=title,
                )
                print(f"Downloaded {Color.GREEN}{title}{Color.RESET}")
                apply_cover_image(
                    yt.thumbnail_url, "Songs" + os.path.sep + "img", title
                )
            except exceptions.VideoUnavailable:
                print(Color.RED + "Video is unavailable" + Color.RESET)
            except exceptions.VideoPrivate:
                print(Color.RED + "Video is private" + Color.RESET)
            except exceptions.VideoRegionBlocked:
                print(Color.RED + "Video is blocked in your region" + Color.RESET)
            except Exception as e:
                print(e)
            print(f"Downloaded {Color.GREEN}{title}{Color.RESET}")
            self.downloadingActive = False

        thread = _Thread(target=_th)
        thread.start()

    def downloadPlaylist_V(self, link):
        self.downloadingActive = True

        pl = Playlist(
            url=link,
            client="WEB",
            token_file="spoofedToken.json",
        )
        os.mkdir(path=pathSafe(pl.title))
        vId = 0
        for video in pl.videos:
            time.sleep(0.15)

            def _inThread(vId):
                try:
                    title = video.title
                    video.streams.get_highest_resolution().download(
                        output_path=pathSafe(name=pl.title),
                        filename=pathSafe(f"{vId} - {title}", True) + ".mp4",
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

            _Thread(target=_inThread, args=(vId,)).start()
            vId += 1

        print(
            f"Downloaded {Color.GREEN}{pl.title}{Color.RESET} --  awaiting stragglers"
        )
        self.downloadingActive = False

    def downloadPlaylist_S(self, link):
        self.downloadingActive = True
        pl = Playlist(
            url=link,
            client="WEB",
            token_file="spoofedToken.json",
        )
        print(f"starting download of playlist {pl.title}:")
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
                title = pathSafe(f"{index} - {title}", True) + ".m4a"
                try:
                    video.streams.get_audio_only().download(
                        output_path=pathSafe(pl.title),
                        filename=title,
                    )
                    print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
                    apply_cover_image(
                        video.thumbnail_url,
                        pathSafe(pl.title) + os.path.sep + "img",
                        title,
                    )
                except exceptions.VideoUnavailable:
                    print(Color.RED + "Video is unavailable" + Color.RESET)
                except exceptions.VideoPrivate:
                    print(Color.RED + "Video is private" + Color.RESET)
                except exceptions.VideoRegionBlocked:
                    print(Color.RED + "Video is blocked in your region" + Color.RESET)
                except Exception as e:
                    print(e)

            _Thread(target=_inThread, args=(_title, _video), daemon=True).start()
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
