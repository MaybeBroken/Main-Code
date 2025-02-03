# This program is a WebSocket server that connects to and allows users to run commands on the server.
import os

try:
    import asyncio
    import websockets
except ImportError:
    os.system("python3 -m pip install websockets")
    os.system("python3 -m pip install asyncio")
    import asyncio
    import websockets
# Function to handle incoming WebSocket connections
IPADDR_PATH = "ip.txt"


async def handle_connection(websocket):
    print("New connection established.")
    try:
        print(await websocket.recv())
        while True:
            await websocket.send(input(""))
            message = await websocket.recv()
            if str(message) == "1":
                print("Error: Invalid command")
            elif str(message) == "0":
                None
            else:
                print(str(message))
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
    if len(IPADDR) == 0 and os.path.exists(IPADDR_PATH):
        with open(IPADDR_PATH, "r") as f:
            IPADDR = f.read().strip()
    elif len(IPADDR) == 0:
        print("No IP address provided and none found in ip.txt.")
        IPADDR = input("Local IP Address: ")
        main()
        return
    else:
        with open(IPADDR_PATH, "w") as f:
            f.write(IPADDR)
    try:
        asyncio.run(start_websocket_client())
    except Exception as e:
        print(f"Error: {e}")
        wantReconnect = input("Do you want to reconnect? (y/n): ")
        if wantReconnect.lower() == "y":
            main()
        else:
            wantDelete = input("Do you want to delete IP cache? (y/n): ")
            if wantDelete.lower() == "y":
                os.remove(IPADDR_PATH)
                print("IP cache deleted.")
                main()
            else:
                print("Exiting program.")
                exit(0)


if __name__ == "__main__":
    if not os.path.exists(IPADDR_PATH):
        open(IPADDR_PATH, "w").close()
        IPADDR = input(f"Local IP Address: {open(IPADDR_PATH).read().strip()}")
    else:
        IPADDR = open(IPADDR_PATH).read().strip()
        if len(IPADDR) == 0:
            IPADDR = input(f"Local IP Address: {open(IPADDR_PATH).read().strip()}")
    main()
