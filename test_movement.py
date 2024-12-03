import asyncio
import websockets
import json

async def send_move_command():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Commande pour déplacer le cube rouge vers l'avant
        command = json.dumps({
            "type": "moveCube",
            "cube": "blue",  # Cube rouge
            "action": "forward"  # Action : avancer
        })
        await websocket.send(command)
        response = await websocket.recv()
        print(f"Réponse : {response}")

asyncio.run(send_move_command())
