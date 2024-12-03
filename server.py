import asyncio
import websockets
import json

# Stocker les connexions actives
connected_clients = set()

async def echo(websocket):
    # Ajouter le client à la liste des connexions actives
    connected_clients.add(websocket)
    print("Client connecté")
    try:
        async for message in websocket:
            print(f"Message reçu : {message}")

            # Traiter les messages en JSON
            try:
                data = json.loads(message)

                if data.get("type") == "moveCube":
                    # Exemple de commande de mouvement
                    print("Commande moveCube reçue")
                    response = {
                        "type": "move",
                        "cube": data.get("cube", "red"),
                        "action": data.get("action", "forward")
                    }
                    # Diffuser à tous les clients connectés
                    await asyncio.gather(*[
                        client.send(json.dumps(response))
                        for client in connected_clients
                        if client != websocket  # Optionnel : éviter d'envoyer au client émetteur
                    ])
                else:
                    response = {
                        "type": "echo",
                        "message": f"Reçu : {message}"
                    }
                    await websocket.send(json.dumps(response))

            except json.JSONDecodeError:
                print("Message non JSON reçu")
                response = {
                    "type": "error",
                    "message": "Message non JSON"
                }
                await websocket.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        print("Client déconnecté")
    finally:
        # Supprimer le client de la liste des connexions actives
        connected_clients.remove(websocket)

# Fonction principale
async def main():
    print("Serveur WebSocket en cours d'exécution sur ws://localhost:8765")
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Garde le serveur actif

if __name__ == "__main__":
    asyncio.run(main())
