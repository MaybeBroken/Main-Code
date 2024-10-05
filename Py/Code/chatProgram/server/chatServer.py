import asyncio
import websockets
import json as js
import time as t

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
        parseMessage(msg)
        await websocket.send(encoder.encode(o=chatRooms))


async def _buildServe():
    async with websockets.serve(_echo, "localhost", int(portNum)):
        print(f"*********\n:SERVER (notice): listening on port {portNum}\n*********")
        await asyncio.Future()


asyncio.run(_buildServe())
