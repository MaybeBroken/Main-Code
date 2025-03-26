from gevent import config
import websockets as ws
import asyncio
import json
import socket
import time
import os
import logging

logging.basicConfig(level=logging.INFO)

GAME = {
    "players": {
        "player1": {"x": 0, "y": 0},
        "player2": {"x": 0, "y": 0},
    },
    "ball": {"x": 0, "y": 0},
    "score": {"player1": 0, "player2": 0},
    "game_state": "waiting",
    "game_time": 0,
}


def get_local_ip():
    """
    Returns the local IP address of the machine.
    """
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


async def launch_server():
    """
    Launches the WebSocket server.
    """
    async with ws.serve(handle_client, get_local_ip(), 8765) as server:
        print(f"Server started at ws://{get_local_ip()}:8765")
        await asyncio.Future()


async def handle_client(websocket):
    """
    Handles incoming client connections.
    """
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message from {websocket.remote_address}: {data}")
            response = process_message(data)
            await websocket.send(json.dumps(response))
    except ws.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Exception in handle_client: {e}", exc_info=True)


def process_message(data):
    """
    Processes incoming messages from clients.
    """
    print(f"Processing message: {data}")
    if "message" in data:
        message = data["message"]
        if message == "ping":
            return {"message": "pong received at time: " + str(time.time())}
        elif message == "pong":
            return {"message": "ping received at time: " + str(time.time())}
        else:
            return {"echo": message}
    elif "init" in data:
        player_id = data["player_id"]
        GAME["players"][player_id] = {"x": 0, "y": 0}
        GAME["score"][player_id] = 0
        GAME["game_time"] = time.time()
        return GAME
    elif "config" in data:
        config = data["config"]
        GAME["config"] = config
        return GAME
    elif "action" in data:
        action = data["action"]
        if action == "update_player":
            player_id = data["player_id"]
            x = data["x"]
            y = data["y"]
            GAME["players"][player_id]["x"] = x
            GAME["players"][player_id]["y"] = y
        elif action == "update_ball":
            x = data["x"]
            y = data["y"]
            GAME["ball"]["x"] = x
            GAME["ball"]["y"] = y
        elif action == "update_score":
            player_id = data["player_id"]
            score = data["score"]
            GAME["score"][player_id] += score
        elif action == "start_game":
            GAME["game_state"] = "playing"
        elif action == "stop_game":
            GAME["game_state"] = "stopped"
        else:
            return {"error": "Invalid action"}
        return GAME
    elif "query" in data:
        query = data["query"]
        if query == "game_state":
            return {
                "game_state": GAME["game_state"],
                "players": GAME["players"],
                "ball": GAME["ball"],
                "score": GAME["score"],
                "game_time": GAME["game_time"],
            }
        else:
            return {"error": "Invalid message format"}
    elif "update" in data:
        return {"update": True}
    else:
        return {"error": "Invalid message format"}


async def main():
    while True:
        try:
            await launch_server()
        except Exception as e:
            print(f"Server error: {e}")
            logging.error(f"Exception in main: {e}", exc_info=True)
            await asyncio.sleep(5)  # Wait before restarting the server


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Server error: {e}")
        logging.error(f"Exception in __main__: {e}", exc_info=True)
