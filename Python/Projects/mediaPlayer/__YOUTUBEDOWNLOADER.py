from pytubefix import YouTube, Playlist, exceptions, Channel, Search
import os
import requests
from threading import Thread as _Thread
import threading as th
import time
import subprocess

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


def pathSafe(name: str):
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


class CORE:
    def downloadVideo(self, link):
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
                    self.outputFolder + pathSeparator + "Videos" + pathSeparator,
                    filename=pathSafe(title) + ".mp4",
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

        thread = _Thread(target=_th)
        thread.start()

    def downloadSong(self, link):
        def _th():
            try:
                yt = YouTube(
                    link,
                    client="WEB",
                    token_file="spoofedToken.json",
                )
                ys = yt.streams.get_audio_only()
                title = yt.title
                ys.download(
                    output_path=self.outputFolder
                    + pathSeparator
                    + "Songs"
                    + pathSeparator,
                    filename=pathSafe(title) + ".m4a",
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

        thread = _Thread(target=_th)
        thread.start()

    def downloadPlaylist_V(self, link):
        def _th():
            pl = Playlist(
                url=link,
                client="WEB",
                token_file="spoofedToken.json",
            )
            os.mkdir(path=pathSafe(pl.title))
            for video in pl.videos:
                time.sleep(0.15)

                def _inThread():
                    try:
                        title = video.title
                        video.streams.get_highest_resolution().download(
                            output_path=pathSafe(name=pl.title),
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

            print(f"Downloaded {Color.GREEN}{pl.title}{Color.RESET}")

        thread = _Thread(target=_th)
        thread.start()

    def downloadPlaylist_S(self, link):
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
            index += 1
            time.sleep(0.05)
            _title = _video.title
            print(f"| - {Color.YELLOW}Downloading{Color.RESET} {_title}")

            def _inThread(title, video):
                try:
                    video.streams.get_audio_only().download(
                        output_path=pathSafe(pl.title),
                        filename=f"{index} - {pathSafe(name=title)}" + ".m4a",
                    )
                    print(f"| - {Color.GREEN}Downloaded{Color.RESET} {title}")
                except exceptions.VideoUnavailable:
                    print(Color.RED + "Video is unavailable" + Color.RESET)
                except exceptions.VideoPrivate:
                    print(Color.RED + "Video is private" + Color.RESET)
                except exceptions.VideoRegionBlocked:
                    print(Color.RED + "Video is blocked in your region" + Color.RESET)
                except Exception as e:
                    print(e)

            _Thread(target=_inThread, args=(_title, _video), daemon=True).start()

    def downloadArtist_V(self, link):
        def _th():
            ch = Channel(
                url=link,
                client="WEB",
                token_file="spoofedToken.json",
            )
            os.mkdir(path=pathSafe(ch.title))
            for video in ch.videos:
                try:
                    video.streams.get_highest_resolution().download(
                        output_path=pathSafe(name=ch.title)
                    )
                except exceptions.VideoUnavailable:
                    print(Color.RED + "Video is unavailable" + Color.RESET)
                except exceptions.VideoPrivate:
                    print(Color.RED + "Video is private" + Color.RESET)
                except exceptions.VideoRegionBlocked:
                    print(Color.RED + "Video is blocked in your region" + Color.RESET)
                except Exception as e:
                    print(e)

        thread = _Thread(target=_th)
        thread.start()


while True:
    try:
        print(
            f"{Color.YELLOW}YouTube Downloader{Color.RESET}\n\n{Color.BLUE}1.{Color.RESET} Download Video\n{Color.BLUE}2.{Color.RESET} Download Song\n{Color.BLUE}3.{Color.RESET} Download Playlist (Videos)\n{Color.BLUE}4.{Color.RESET} Download Playlist (Songs)\n{Color.BLUE}5.{Color.RESET} Download Artist (Videos)\n{Color.BLUE}6.{Color.RESET} Download Artist (Songs)\n\n{Color.RED}0.{Color.RESET} Exit"
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

    for thread in th.enumerate():
        if thread is not th.main_thread():
            thread.join()
