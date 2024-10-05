import asyncio
import websockets
import time as t
from threading import Thread
import json as js


startTime = t.monotonic()


def currentTime(dp):
    return t.monotonic() - startTime


serverContents = []
portNum = 8765
ip = "wss://maybebroken.loca.lt"


async def _send_recieve(data):
    async with websockets.connect(ip) as websocket:
        encoder = js.encoder.JSONEncoder()
        if data == "!!#update":
            await websocket.send("!!#update")
            serverContents = js.decoder.JSONDecoder().decode(s=await websocket.recv())
        else:
            await websocket.send(
                encoder.encode(o={"usr": usrName, "text": data, "roomName": roomName})
            )


def runClient(data):
    asyncio.run(_send_recieve(data))


_ip = input("connect to external ip (leave blank for normal usage): ")
if len(_ip) > 5:
    ip = _ip
else:
    print(f"using default ip {ip}")
usrName = input("what is your username: ")

roomName = input(f'what room to join?\n{runClient("!!#update")}\n--> ')


def mainLoop():
    while 1 == 1:
        data = input()
        try:
            runClient(data)
        except:
            print(
                f"failed to send message!\nplease ensure the server is runing by checking this link:\n{ip}"
            )


def update():
    while True:
        try:
            runClient("!!#update")
        except:
            ...
        t.sleep(1)


Thread(target=update).start()
mainLoop()
