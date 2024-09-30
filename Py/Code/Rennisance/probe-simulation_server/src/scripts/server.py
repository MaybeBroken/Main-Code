import asyncio
import os
import src.scripts.decoder as decoder
import websockets
import functools
import time as t
startTime = t.monotonic()
def currentTime(dp):
    return t.monotonic()-startTime
async def _echo(websocket, var):
    clientKey = await websocket.recv()
    newKey = decoder.decode(clientKey)
    print(f'SERVER -> {currentTime()}: {websocket.remoteAddress} sent data: [\n{newKey}\n]')
    var=newKey
    await websocket.send(decoder.encode(var))


async def _buildServe(portNum, var):
    bound_handler = functools.partial(_echo, var=var)
    async with websockets.serve(bound_handler, "localhost", int(portNum)):
        print(f'*********\n:SERVER(notice): listening on port {portNum}\n*********')
        startLocalTunnel(portNum)
        await asyncio.Future()

def startLocalTunnel(portNum):
    os.system(f'lt -p {portNum} -s SpacePlace3000')

def startServer(portNum, var):
    asyncio.run(_buildServe(portNum, var))