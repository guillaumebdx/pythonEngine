# gym_env.py
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import websockets
import asyncio
import json
import time  # Importer la bibliothèque time pour gérer le temps


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

        # Gestion du temps
        self.start_time = None
        self.max_episode_duration = 20  # secondes

        # Variables pour les récompenses
        self.total_reward = 0
        self.sees_enemy_duration = 0
        self.blue_destroyed = False

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
            "cube": "red",  # Contrôle du cube rouge
            "action": command_map[action]
        }
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(json.dumps(command))
            response = await websocket.recv()
            # Traitement de la réponse si nécessaire

    async def _receive_state(self):
        async with websockets.connect(self.uri) as websocket:
            # Demander l'état de l'agent rouge
            await websocket.send(json.dumps({"type": "requestState", "agent": "red"}))
            response = await websocket.recv()
            state = json.loads(response)
            return state["state"]

    async def _check_collision(self):
        async with websockets.connect(self.uri) as websocket:
            # Vérifier si le cube bleu a été détruit
            await websocket.send(json.dumps({"type": "checkCollision"}))
            response = await websocket.recv()
            data = json.loads(response)
            return data.get("blue_destroyed", False)

    def step(self, action):
        asyncio.run(self._send_command(action))
        new_state = asyncio.run(self._receive_state())

        # Mise à jour de l'état interne
        self.current_state = {
            "position": new_state["position"],
            "sees_enemy": int(bool(new_state["seesEnemy"]))
        }

        # Gestion du temps
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Calcul de la récompense
        reward = 0

        # +1 point par seconde si le cube rouge voit le cube bleu
        if self.current_state["sees_enemy"]:
            reward += 1
            self.sees_enemy_duration += 1  # Compte le nombre de pas où l'ennemi est vu

        # Vérifier si le cube bleu a été détruit
        blue_destroyed = asyncio.run(self._check_collision())
        if blue_destroyed and not self.blue_destroyed:
            reward += 20  # +20 points pour l'élimination de l'ennemi
            self.blue_destroyed = True
            self.done = True  # Fin de l'épisode si l'ennemi est détruit

        # Si l'épisode atteint sa durée maximale
        if elapsed_time >= self.max_episode_duration:
            self.done = True
            if not self.blue_destroyed:
                reward -= 20  # Pénalité pour l'échec de l'élimination

        self.total_reward += reward

        return self.current_state, reward, self.done, {}

    def reset(self):
        # Réinitialiser l'environnement
        self.current_state = {"position": {"x": 0.0, "y": 0.0, "z": 0.0}, "sees_enemy": 0}
        self.done = False
        self.start_time = time.time()
        self.total_reward = 0
        self.sees_enemy_duration = 0
        self.blue_destroyed = False
        return self.current_state

    def render(self, mode="human"):
        # Optionnel : visualisation de l'état actuel
        print(f"Position : {self.current_state['position']}, Voit l'ennemi : {self.current_state['sees_enemy']}")
