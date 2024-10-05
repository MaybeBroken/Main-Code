import asyncio
import websockets
import time as t
from threading import Thread
import json as js

startTime = t.monotonic()


def currentTime(dp):
    return t.monotonic() - startTime


portNum = 8765
ip = "wss://maybebroken.loca.lt"


async def _send_recieve(data):
    async with websockets.connect(ip) as websocket:
        if data == "!!#update":
            await websocket.send("!!#update")
            print(await websocket.recv())
        else:
            await websocket.send(
                js.encoder.JSONEncoder.encode(o={"usr": usrName, "text": data})
            )


def runClient(data):
    asyncio.run(_send_recieve(data))


_ip = input("connect to external ip (leave blank for normal usage): ")
if len(_ip) > 5:
    ip = _ip
else:
    print(f"using default ip {ip}")
usrName = input("what is your username: ")


def mainLoop():
    while 1 == 1:
        data = input()
        runClient(data)


def update():
    runClient("!!#update")


Thread(target=update).start()
mainLoop()
