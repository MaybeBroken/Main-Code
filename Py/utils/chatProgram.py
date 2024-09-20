import asyncio
import websockets
import time as t
import ipaddress
from threading import Thread

startTime = t.monotonic()

def currentTime(dp):
    return t.monotonic() - startTime


portNum = 8765
ip = "localhost"


async def _echo(websocket):
    print(f"\nuser: {await websocket.recv()}\n")


async def _buildServe():
    async with websockets.serve(_echo, "localhost", int(portNum)):
        print(f"*********\n:SERVER (notice): listening on port {portNum}\n*********")
        await asyncio.Future()


def startServer():
    asyncio.run(_buildServe())


async def _send_recieve(Keys):
    async with websockets.connect(ip) as websocket:
        await websocket.send(Keys)


def runClient(data):
    asyncio.run(_send_recieve(data))


class wrapper:
    global ip
    ip = input("connect to ip: ")
    # runClient()
    # startServer()
    Thread(target=startServer, daemon=True).start()
    while 1 == 1:
        t.sleep(2)
        data = input()
        runClient(data)
