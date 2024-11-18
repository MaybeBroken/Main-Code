import json
import os
from threading import Thread
from time import sleep
import websockets
import asyncio
import socket

serverData = {}
messageQueue: list[dict[str, None]] = []
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
portNum = 8001
send = lambda head, body: messageQueue.append({"head": head, "body": body})


async def echo(websocket):
    while True:
        for message in messageQueue:
            try:
                global serverData
                await websocket.send(json.JSONEncoder().encode(message))
                messageQueue.remove(message)
                serverData = json.JSONDecoder().decode(await websocket.recv())
            except:
                ...
        if len(messageQueue) == 0:
            send("", "")
        sleep(0.01)


async def main(portNum):
    async with websockets.serve(echo, IPAddr, int(portNum)):
        await asyncio.Future()


def startServer(portNum):
    while True:
        asyncio.run(main(portNum))


Thread(target=os.system, args=["python3 -m http.server 80"]).start()
Thread(target=startServer, args=[portNum]).start()
print(f"server running on http://localhost")

while True:
    sleep(0.1)
    print(serverData)
