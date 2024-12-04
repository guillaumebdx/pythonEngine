import asyncio
import websockets
import json
import time

async def send_move_command():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Commandes à envoyer
        commands = [
            {"type": "moveCube", "cube": "red", "action": "jump"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "blue", "action": "rotate_right"},
            {"type": "moveCube", "cube": "blue", "action": "rotate_right"},
            {"type": "moveCube", "cube": "blue", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            {"type": "moveCube", "cube": "red", "action": "forward"},
            # {"type": "moveCube", "cube": "red", "action": "forward"},
            # {"type": "moveCube", "cube": "red", "action": "rotate_left"},
            # {"type": "moveCube", "cube": "red", "action": "forward"},
            # {"type": "moveCube", "cube": "red", "action": "rotate_right"},
            # {"type": "moveCube", "cube": "red", "action": "backward"},

        ]

        for command in commands:
            await websocket.send(json.dumps(command))
            print(f"Commande envoyée : {command}")
            response = await websocket.recv()
            print(f"Réponse : {response}")
            time.sleep(0.05)

asyncio.run(send_move_command())
