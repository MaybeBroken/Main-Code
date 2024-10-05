import asyncio
from threading import Thread
import websockets
import json as js
import time as t
from os import system

portNum = 8765

exampleMsg = {"usr": "MaybeBroken", "text": "test"}


chatRooms = [
    {
        "roomName": "testRoom",
        "messages": [],
    }
]


def parseMessage(msg: str):
    parseMsg: dict = js.decoder.JSONDecoder().decode(s=msg)
    for chatRoom in chatRooms:
        if chatRoom["roomName"] == parseMsg["roomName"]:
            chatRoom["messages"].append(
                {
                    "time": int(t.time()),
                    "usr": parseMsg["usr"],
                    "text": parseMsg["text"],
                }
            )


async def _echo(websocket):
    msg = await websocket.recv()
    encoder = js.encoder.JSONEncoder()
    if msg == "!!#update":
        await websocket.send(encoder.encode(o=chatRooms))
    else:
        usrIp = websocket.remote_address[0]
        print(f'{usrIp}: {msg}')
        parseMessage(msg)
        await websocket.send(encoder.encode(o=chatRooms))


async def _buildServe():
    async with websockets.serve(_echo, "localhost", int(portNum)):
        print(f"*********\n:SERVER (notice): listening on port {portNum}\n*********")
        await asyncio.Future()


def startLocaltunnel():
    system(command=f"lt -p {portNum} -s maybebroken")


Thread(target=startLocaltunnel).start()
asyncio.run(_buildServe())
