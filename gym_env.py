import gymnasium as gym
from gymnasium import spaces
import numpy as np
import websockets
import asyncio
import json


class CustomEnv(gym.Env):
    def __init__(self):
        super(CustomEnv, self).__init__()

        # Actions possibles : avance, recule, tourne, saute
        self.action_space = spaces.Discrete(5)  # 0: forward, 1: backward, 2: rotate_left, 3: rotate_right, 4: jump

        # Observation : position (x, y, z), vision (booléen si l'ennemi est visible)
        self.observation_space = spaces.Dict({
            "position": spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32),
            "sees_enemy": spaces.Discrete(2)  # 0: ne voit pas, 1: voit
        })

        # Initialisation des états
        self.current_state = {"position": [0.0, 0.0, 0.0], "sees_enemy": 0}
        self.done = False

        # WebSocket
        self.uri = "ws://localhost:8765"

    async def _send_command(self, action):
        command_map = {
            0: "forward",
            1: "backward",
            2: "rotate_left",
            3: "rotate_right",
            4: "jump"
        }
        command = {
            "type": "moveCube",
            "cube": "red",  # Remplace par le cube à contrôler
            "action": command_map[action]
        }
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(json.dumps(command))
            print(f"Action envoyée : {command}")
            response = await websocket.recv()
            print(f"Réponse du serveur : {response}")

    async def _receive_state(self):
        async with websockets.connect(self.uri) as websocket:
            # Demander l'état de l'agent rouge
            await websocket.send(json.dumps({"type": "requestState", "agent": "red"}))
            response = await websocket.recv()
            state = json.loads(response)
            print(f"État reçu : {state}")
            return state["state"]

    def step(self, action):
        asyncio.run(self._send_command(action))
        new_state = asyncio.run(self._receive_state())

        # Met à jour l'état interne
        self.current_state = {
            "position": new_state["position"],
            "sees_enemy": int(bool(new_state["seesEnemy"]))
        }

        # Récompense basique (à ajuster selon l'objectif)
        reward = 1 if self.current_state["sees_enemy"] else 0

        # Condition d'arrêt (exemple)
        self.done = False

        return self.current_state, reward, self.done, {}

    def reset(self):
        # Réinitialiser l'environnement
        self.current_state = {"position": [0.0, 0.0, 0.0], "sees_enemy": 0}
        self.done = False
        return self.current_state

    def render(self, mode="human"):
        # Pas nécessaire ici, mais tu peux visualiser l'état si besoin
        print(f"Position : {self.current_state['position']}, Voit l'ennemi : {self.current_state['sees_enemy']}")

