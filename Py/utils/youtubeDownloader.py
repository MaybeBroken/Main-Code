from time import sleep
from pytubefix import YouTube, Playlist
from threading import Thread
import ffmpeg
outputPath = "./youtubeDownloader/"

def Download(link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        name = youtubeObject.default_filename
        youtubeObject.download(outputPath)
        print(f"Download of {name} has completed successfully")
        #ffmpeg.input(outputPath+'/'+name)
    except:
        print(f"\n\nAn error occurred with file {name}!\n\n")


def getPlaylist(link):
    x = Playlist(link)
    print(x.count)
    return x


def _Wrapper(link):
    list = getPlaylist(link)
    global outputPath
    outputPath += list.title+'/'
    for uri in list:
        Thread(target=Download, daemon=True, args=[uri]).start()
        sleep(0.2)
    print('\n\n\n*********\nFinished\n*********\n')

url = input(f"\nyt Playlist Url: \n")
mpQuery = input('\nConvert all to mp3?: (Y/N)  ')
print('\n')
if url == '' or url == None or len(url)<20:
    url = 'https://music.youtube.com/playlist?list=PLt-QnSFN9Gjp2sD8DmeY1B0awsd7tmpP7&si=yqYOMDGHaWBLElwP'
_Wrapper(url)
