import asyncio
import websockets
import decoder

Keys = []

portnum = 8765


async def send_recieve(data):
    uri = f"ws://localhost:{portnum}"
    async with websockets.connect(uri) as websocket:
        await websocket.send(decoder.encode(data))
        data = decoder.decode(await websocket.recv())  # type: ignore
        global Keys
        Keys = data
    return data


def runClient():
    asyncio.run(send_recieve(Keys))
