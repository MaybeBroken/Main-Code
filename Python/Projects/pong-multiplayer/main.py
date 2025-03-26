import websockets
import asyncio
import json
import socket
import os
import time
from threading import Thread

messageQueue = []
responseQueue = []
startTime = time.time()


def get_time(startTime=startTime):
    """
    Returns the current time since the start of the program.
    """
    return time.time() - startTime


def get_local_ip():
    """
    Returns the local IP address of the machine.
    """
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


async def connect_to_server():
    """
    Connects to the WebSocket server.
    """
    uri = f"ws://{get_local_ip()}:8765"
    print(f"Connecting to server at {uri}")
    async with websockets.connect(uri) as websocket:
        print(f"Connected to server at {uri}")
        while True:
            if len(messageQueue) == 0:
                await websocket.send(json.dumps({"update": time.time()}))
            for id in range(len(messageQueue)):
                request_data = messageQueue.pop(0)
                await websocket.send(json.dumps(request_data))
                response = await websocket.recv()
                data = json.loads(response)
                (
                    responseQueue.append([data, time.time()])
                    if data != {"update": True}
                    else None
                )
            messageQueue.clear()


async def main():
    """
    Main function to run the WebSocket client.
    """
    await connect_to_server()


def asyncio_main():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Client stopped")


def start_client():
    """
    Starts the WebSocket client in a separate thread.
    """
    client_thread = Thread(target=asyncio_main)
    client_thread.start()
    return client_thread


def send_message(message):
    """
    Sends a message to the server.
    """
    messageQueue.append(message)


def get_response():
    """
    Gets the response from the server.
    """
    for _ in range(5):
        if responseQueue:
            break
        time.sleep(0.2)
    else:
        return {"error": "No response from server"}
    return responseQueue.pop(0)


def purge_queue():
    """
    Purges the response queue.
    """
    newQueue = responseQueue.copy()
    responseQueue.clear()
    for item in newQueue:
        if item[1] > time.time() - 5:
            responseQueue.append(item)
    return responseQueue


if __name__ == "__main__":
    start_client()
    print("Client started")
    while True:
        try:
            send_message({"message": input("Enter message: ")})
            response = get_response()
            print(f"Response from server: {response}")
            purge_queue()
        except KeyboardInterrupt:
            print("Client stopped")
