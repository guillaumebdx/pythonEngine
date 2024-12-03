import asyncio
import websockets

# Fonction pour gérer les messages du WebSocket
async def echo(websocket):
    print("Client connecté")
    try:
        async for message in websocket:
            print(f"Message reçu : {message}")
            if message == "ping":
                await websocket.send("pong")
            else:
                await websocket.send(f"Reçu : {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client déconnecté")

# Fonction principale pour lancer le serveur
async def main():
    print("Serveur WebSocket en cours d'exécution sur ws://localhost:8765")
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Garde le serveur actif

if __name__ == "__main__":
    asyncio.run(main())
