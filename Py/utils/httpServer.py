import os
from threading import Thread
from time import sleep
import websockets
import asyncio


Thread(target=os.system, args=["python3 -m http.server"]).start()

serverText = "hi"


async def echo(websocket):
    while True:
        try:
            await websocket.send(serverText)
        except:
            ...


async def main(portNum):
    async with websockets.serve(echo, "localhost", int(portNum)):
        await asyncio.Future()


def startServer(portNum):
    while True:
        try:
            asyncio.run(main(portNum))
        except:
            ...


Thread(target=startServer, args=[8765]).start()


sleep(2)
while True:
    serverText = input("server text: ")
