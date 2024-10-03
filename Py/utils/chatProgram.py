import asyncio
import websockets
import time as t
from threading import Thread
import subprocess as sp
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
startTime = t.monotonic()


def currentTime(dp):
    return t.monotonic() - startTime


portNum = 8765
ip = "localhost"


async def _echo(websocket):
    print(f"\n{websocket.remote_address}: {await websocket.recv()}\n")


async def _buildServe():
    async with websockets.serve(_echo, "localhost", int(portNum)):
        print(f"*********\n:SERVER (notice): listening on port {portNum}\n*********")
        await asyncio.Future()

def runNgrok():
    sp.run(['./ngrok', 'http', f'{portNum}'], capture_output=False)


def startServer():
    asyncio.run(_buildServe())


async def _send_recieve(Keys):
    async with websockets.connect(ip) as websocket:
        await websocket.send(Keys)


def runClient(data):
    asyncio.run(_send_recieve(data))


class wrapper:
    global ip
    Thread(target=startServer, daemon=True).start()
    Thread(target=runNgrok, daemon=True).start()
    ip = input("connect to ip: ")
    while 1 == 1:
        t.sleep(2)
        data = input()
        runClient(data)

# ip: 204.225.31.201