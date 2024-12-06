import os
import sys
from threading import Thread

# Thread(
#     target=system, args=["websocat -v -E -t ws-l:127.0.0.1:1234 broadcast:mirror:"]
# ).start()
# print("make sure visualize.html is open in your browser")
# system(
#     f"bbot -t {input("enter url to start scan: ")} -om websocket -c dns.search_distance=10 scope.report_distance=10 modules.websocket.url=ws://127.0.0.1:8765"
# )

# websocat -v -E -t ws-l:127.0.0.1:1234 broadcast:mirror:
# american-heritage.instructure.com amazon.com youtube.com google.com cloudflare.com dns.google.com 8.8.8.8 gmail.com tesla.com
# bbot -t american-heritage.instructure.com -om websocket -c dns.search_distance=100 scope.report_distance=100 modules.websocket.url=ws://127.0.0.1:1234

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"

os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))
os.chdir("./html/src/")
rootPath = os.path.abspath(os.curdir)


def openLink(link: str, path1: str, depth: int):
    # if link in urlList:
    #     return "link in url"
    # if os.path.abspath(path1) in pathList:
    #     return "path in pathlist"
    os.chdir(rootPath)
    try:
        os.chdir(path1)
    except FileNotFoundError:
        if path1.count("/") > 1:
            newPath = ""
            for folder in path1.split("/"):
                newPath = newPath + "/" + folder
                if newPath[0] == "/":
                    newPath = newPath.replace("/", "", 1)
                try:
                    os.mkdir(newPath)
                except FileExistsError:
                    ...
                except OSError:
                    return
        else:
            try:
                os.mkdir(url)
            except FileExistsError:
                ...
            except OSError:
                return
    try:
        if link[-1] == "/" or link.endswith((".org", ".com", ".net")):
            os.system(f"curl -s -o index.html {link}")
        else:
            os.system(f"curl -s -o {link.split("/")[-1]} {link}")
        print(f"downloaded host {link}") if len(link) < 150 else ...
    except:
        print(f"failed to download host {link}") if len(link) < 150 else ...
        return

    if link[-1] == "/":
        try:
            with open(f"index.html") as index:
                try:
                    content = index.readlines()
                    content = "\n".join(content)
                    content = content.split('"https://')
                    num = 0
                    links: list[str] = {}
                    for chunk in content:
                        if num == 0:
                            num = 1
                        else:
                            chunk = chunk.split('"')
                            if chunk[0] != link.removeprefix("https://").removeprefix(
                                "http://"
                            ):
                                url = chunk[0]
                                if url.count("?") > 0:
                                    url = url.split("?")[0]
                                if url.count("/{w}x{h}") > 0:
                                    url = url.split("/{w}x{h}")[0]
                                if (
                                    not url.endswith((".org", ".com", ".net"))
                                    and url[-1] != "/"
                                ):
                                    url = url + "/"
                                links[url] = chunk[0]
                    os.chdir(rootPath)
                    for url in links:
                        if url.count("/") > 1:
                            newPath = ""
                            for folder in url.split("/"):
                                newPath = newPath + "/" + folder
                                if newPath[0] == "/":
                                    newPath = newPath.replace("/", "", 1)
                                try:
                                    os.mkdir(newPath)
                                except FileExistsError:
                                    ...
                                except OSError:
                                    return
                        else:
                            try:
                                os.mkdir(url)
                            except FileExistsError:
                                ...
                            except OSError:
                                return
                        if depth <= 0:
                            # Thread(
                            #     target=openLink,
                            #     args=[f"https://{url}", url, depth + 1],
                            # ).start()
                            openLink(f"https://{url}", url, depth + 1)
                except UnicodeDecodeError:
                    ...
        except FileNotFoundError:
            ...


openLink(input("url to scan: "), ".", -int(input("depth to scan: ")))

# https://8.8.8.8/
