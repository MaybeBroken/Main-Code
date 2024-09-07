import asyncio
import websockets
import src.scripts.decoder as decoder

portnum = 8765

async def _send_recieve(Keys):
    while True:
        try:
            uri = f"ws://localhost:{portnum}"
            async with websockets.connect(uri) as websocket:
                await websocket.send(decoder.encode(Keys))
                Keys = decoder.decode(await websocket.recv())  # type: ignore
        except:
            None

def runClient(Keys):
    asyncio.run(_send_recieve(Keys))
    print('started client')
