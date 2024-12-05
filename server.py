import asyncio
import websockets
import json
from collections import deque

# File d'attente pour les commandes
command_queue = deque()
connected_clients = set()

# Dictionnaire pour stocker les positions et états des agents
agent_states = {}

# Fonction pour gérer les messages du WebSocket
# Ajouter une variable pour suivre si le cube bleu est détruit
blue_destroyed = False

# Modifier la fonction echo pour gérer les messages de collision
async def echo(websocket):
    global blue_destroyed
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
                elif data.get("type") == "agentUpdate":
                    # Mise à jour des informations des agents
                    agent_name = data["agent"]
                    agent_states[agent_name] = {
                        "position": data["position"],
                        "seesEnemy": data.get("seesEnemy", None)
                    }
                elif data.get("type") == "requestState":
                    # Envoyer l'état actuel de l'agent demandé
                    requested_agent = data.get("agent")
                    if requested_agent in agent_states:
                        response = {
                            "type": "agentState",
                            "agent": requested_agent,
                            "state": agent_states[requested_agent],
                            "blue_destroyed": blue_destroyed
                        }
                        await websocket.send(json.dumps(response))
                    else:
                        response = {"type": "error", "message": f"Agent {requested_agent} inconnu"}
                        await websocket.send(json.dumps(response))
                elif data.get("type") == "collision":
                    if data.get("attacker") == "red" and data.get("target") == "blue":
                        blue_destroyed = True
                        print("Le cube bleu a été détruit.")
                elif data.get("type") == "checkCollision":
                    response = {"type": "collisionStatus", "blue_destroyed": blue_destroyed}
                    await websocket.send(json.dumps(response))
                elif data.get("type") == "reset":
                    blue_destroyed = False
                    print("Réinitialisation reçue : blue_destroyed est maintenant False")
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
