import asyncio
from threading import Thread
import websockets
import json as js
import time as t
from os import system

portNum = 8765

exampleMsg = {"time": 0, "usr": "MaybeBroken", "text": "test"}

devMode = True
anyAuth = True
chatRooms = [{"roomName": "hangout", "messages": []}]

accounts = {
    "MaybeBroken": "123456",
    "EthanG": "123456",
    "Creeper": "123456",
    "nobody-(!)": "",
}


def parseMessage(msg: str):
    parseMsg: dict = js.decoder.JSONDecoder().decode(s=msg)
    for chatRoom in chatRooms:
        if chatRoom["roomName"] == parseMsg["roomName"]:
            chatRoom["messages"].append(
                {
                    "time": f"{t.localtime()[1]}/{t.localtime()[2]}/{t.localtime()[0]} at {t.localtime()[3]}:{t.localtime()[4]}:{t.localtime()[5]}",
                    "usr": parseMsg["usr"],
                    "text": parseMsg["text"],
                }
            )


async def _echo(websocket):
    try:
        msg = await websocket.recv()
        encoder = js.encoder.JSONEncoder()
        if msg == "!!#update":
            await websocket.send(encoder.encode(o=chatRooms))
        elif msg[0] == "+" and msg[1] == "@":
            if anyAuth:
                await websocket.send("!!#authDisabled")
            else:
                try:
                    msg = msg.splitlines()
                    try:
                        i = accounts[msg[1]]
                        if accounts[msg[1]] == msg[2]:
                            print(f":auth: user {msg[1]} joined the lobby")
                            await websocket.send("!!#authSuccess")
                        else:
                            await websocket.send("!!#wrongPassword")
                    except:
                        await websocket.send("!!#wrongUsrname")
                except:
                    print(f"STUPID SERVER BROKE:\nmsg-->{msg}\naccounts-->{accounts}")
                    await websocket.send("!!#internalErr")
        else:
            parseMessage(msg)
            await websocket.send(encoder.encode(o=chatRooms))
    except:
        ...


async def _buildServe():
    async with websockets.serve(_echo, "localhost", int(portNum)):
        print(f"*********\n:SERVER (notice): listening on port {portNum}\n*********")
        await asyncio.Future()


def startLocaltunnel():
    system(command=f"lt -p {portNum} -s maybebroken")
    ...


def saveServer():
    while True:
        with open("./backup.dat", "wt") as backup:
            backup.write(js.encoder.JSONEncoder().encode(o=chatRooms))
        t.sleep(3)


if not devMode:
    Thread(target=startLocaltunnel).start()
with open("./backup.dat", "rt") as backup:
    chatRooms = js.decoder.JSONDecoder().decode(s=backup.read())
Thread(target=saveServer).start()
asyncio.run(_buildServe())
