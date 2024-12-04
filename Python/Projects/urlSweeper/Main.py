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

os.chdir("./html/")

urlList = []
pathList = []


def openLink(link: str, path1: str):
    # if link in urlList:
    #     return "link in url"
    # if os.path.abspath(path1) in pathList:
    #     return "path in pathlist"
    os.chdir(path1)
    print(os.path.abspath(path1))
    if link[-1] == "/":
        os.system(f"curl -o index.html {link}")
    else:
        os.system(f"curl -o {link.split("/")[-1]} {link}")
    pathList.append(os.path.abspath(path1))
    urlList.append(link)
    if link[-1] == "/":
        with open(f"index.html") as index:
            content = index.readlines()
            content = "\n".join(content)
            content = content.split("href=")
            for block in content:
                url: str = block.split('"')[1]
                if not url == "en":
                    link = url
                    path = "src"
                    if url[0] == "/" and url.count(link) == 0:
                        if link.endswith("/"):
                            link = link.rstrip("/")
                            url = link + url
                        else:
                            url = link + url
                    if url.count(link) > 0:
                        path += "".join(url.split(link)[-1])
                    else:
                        if path.count(link) == 0:
                            path = path + link.replace("https://", "/")
                        print(path)
                        print(link)
                        print(url)
                    masterUrl = url
                    if masterUrl.count("?") > 0:
                        masterUrl = masterUrl.split("?")[0]
                    if path.count("?") > 0:
                        path = path.split("?")[0]
                    if path[-1] != "/" and len(path) > 1:
                        path += "/"
                    path = path.replace("//", "/")
                    if path.count("/") >= 2:
                        newPath = ""
                        for folder in path.split("/"):
                            newPath = newPath + "/" + folder
                            if newPath[0] == "/":
                                newPath = newPath.replace("/", "", 1)
                            try:
                                os.mkdir(newPath)
                            except FileExistsError:
                                ...
                        os.chdir(newPath)
                    else:
                        try:
                            os.mkdir(path)
                            os.chdir(path)
                        except FileExistsError:
                            ...
                    print(openLink(masterUrl, os.path.abspath(os.curdir)))


print(openLink(input("url to scan: "), "."))
