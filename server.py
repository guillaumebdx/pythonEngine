import asyncio
import websockets
import json
from collections import deque

# File d'attente pour les commandes
command_queue = deque()
connected_clients = set()

# Fonction pour gérer les messages du WebSocket
async def echo(websocket):
    connected_clients.add(websocket)
    print("Client connecté")
    try:
        async for message in websocket:
            print(f"Message reçu : {message}")
            try:
                data = json.loads(message)
                if data.get("type") == "moveCube":
                    # Ajouter la commande à la file d'attente
                    command_queue.append(data)
                    print(f"Commande ajoutée à la file : {data}")
                elif data.get("type") == "agentData":
                    # Gérer les données des agents
                    agents = data.get("agents", [])
                    print("Données des agents reçues :")
                    for agent in agents:
                        print(f"- Agent: {agent['agent']}")
                        print(f"  Position: {agent['position']}")
                        if agent.get("seesEnemy"):
                            print(f"  Voit l'ennemi à : {agent['seesEnemy']['position']}")
                        else:
                            print("  Ne voit pas d'ennemi.")
                else:
                    response = {"type": "echo", "message": f"Reçu : {message}"}
                    await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                response = {"type": "error", "message": "Message non JSON"}
                await websocket.send(json.dumps(response))
    except websockets.exceptions.ConnectionClosed:
        print("Client déconnecté")
    finally:
        connected_clients.remove(websocket)

# Fonction pour traiter la file d'attente
async def process_queue():
    while True:
        if command_queue:
            command = command_queue.popleft()
            print(f"Commande en cours de traitement : {command}")
            # Diffuser la commande à tous les clients
            await asyncio.gather(*[
                client.send(json.dumps(command)) for client in connected_clients
            ])
        await asyncio.sleep(0.1)

# Fonction principale
async def main():
    print("Serveur WebSocket en cours d'exécution sur ws://localhost:8765")
    async with websockets.serve(echo, "localhost", 8765):
        await process_queue()

if __name__ == "__main__":
    asyncio.run(main())
