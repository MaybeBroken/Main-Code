import asyncio
import decoder
import websockets
import functools


def updateValues(var):
    for key in var.jsKeys:
        var.serverKeys.append(key)
    for key in var.clientKeys:
        var.serverKeys.append(key)


async def echo(websocket, var, serverType):
    clientKey = await websocket.recv()
    newKey = decoder.decode(clientKey)
    if serverType == "py":
        var.boardKeys = newKey
    if serverType == "js":
        var.jsKeys = newKey
    updateValues(var=var)
    await websocket.send(decoder.encode(var.serverKeys))


async def main(portNum, var, serverType):
    bound_handler = functools.partial(echo, var=var, serverType=serverType)
    async with websockets.serve(bound_handler, "localhost", int(portNum)):
        await asyncio.Future()


def startServer(portNum, var, serverType):
    asyncio.run(main(portNum, var, serverType))
