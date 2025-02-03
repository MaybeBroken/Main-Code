# This program is a WebSocket server that connects to and allows users to run commands on the server.

import asyncio
import websockets
import os

# Function to handle incoming WebSocket connections


async def handle_connection(websocket):
    print("New connection established.")
    try:
        print(await websocket.recv())
        while True:
            await websocket.send(input("Enter command: "))
            message = await websocket.recv()
            print(f"Received command: {message}")
    except websockets.ConnectionClosed:
        print("Connection closed.")
    except Exception as e:
        print(f"Error: {e}")


# Function to start the WebSocket client
async def start_websocket_client():
    async with websockets.connect(f"ws://{IPADDR}") as websocket:
        await handle_connection(websocket)


# Main function
def main():
    global IPADDR
    if len(IPADDR) == 0 and os.path.exists("ip.txt"):
        with open("ip.txt", "r") as f:
            IPADDR = f.read().strip()
    elif len(IPADDR) == 0:
        print("No IP address provided and none found in ip.txt.")
        IPADDR = input("Local IP Address: ")
        main()
        return
    else:
        with open("ip.txt", "w") as f:
            f.write(IPADDR)
    asyncio.run(start_websocket_client())


if __name__ == "__main__":
    if not os.path.exists("ip.txt"):
        open("ip.txt", "w").close()
    IPADDR = input(f"Local IP Address: {open('ip.txt').read().strip()}")
    main()
