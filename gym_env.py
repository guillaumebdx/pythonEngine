# gym_env.py
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import websocket
import json
import time

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
        self.current_state = {"position": {"x": 0.0, "y": 0.0, "z": 0.0}, "sees_enemy": 0}
        self.done = False

        # WebSocket
        self.uri = "ws://localhost:8765"
        self.ws = websocket.create_connection(self.uri)

        # Gestion du temps
        self.start_time = None
        self.last_time = None  # Ajout de last_time
        self.max_episode_duration = 20  # secondes

        # Variables pour les récompenses
        self.total_reward = 0
        self.sees_enemy_duration = 0
        self.blue_destroyed = False

    def _send_command(self, action):
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
        self.ws.send(json.dumps(command))
        # Pas besoin d'attendre une réponse pour cette commande

    def _receive_state(self):
        # Demander l'état de l'agent rouge
        request = {"type": "requestState", "agent": "red"}
        self.ws.send(json.dumps(request))
        while True:
            response = self.ws.recv()
            data = json.loads(response)
            if data.get("type") == "agentState" and data.get("agent") == "red":
                return data["state"]
            else:
                # Si le message n'est pas celui attendu, ignorer et continuer
                continue

    def _check_collision(self):
        # Vérifier si le cube bleu a été détruit
        request = {"type": "checkCollision"}
        self.ws.send(json.dumps(request))
        while True:
            response = self.ws.recv()
            data = json.loads(response)
            if data.get("type") == "collisionStatus":
                return data.get("blue_destroyed", False)
            else:
                # Si le message n'est pas celui attendu, ignorer et continuer
                continue

    def step(self, action):
        self._send_command(action)
        new_state = self._receive_state()

        # Mise à jour de l'état interne
        self.current_state = {
            "position": new_state["position"],
            "sees_enemy": int(bool(new_state.get("seesEnemy", False)))
        }

        # Gestion du temps
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Calcul du temps écoulé depuis la dernière étape
        delta_time = current_time - self.last_time if self.last_time else 0

        # Calcul de la récompense
        reward = 0

        # +1 point par seconde si le cube rouge voit le cube bleu
        if self.current_state["sees_enemy"]:
            reward += delta_time * 2.0  # 2.0 point par seconde

        # Vérifier si le cube bleu a été détruit
        blue_destroyed = self._check_collision()
        if blue_destroyed and not self.blue_destroyed:
            reward += 30  # +30 points pour l'élimination de l'ennemi
            self.blue_destroyed = True
            self.done = True  # Fin de l'épisode si l'ennemi est détruit

        # Si l'épisode atteint sa durée maximale
        if elapsed_time >= self.max_episode_duration:
            self.done = True
            if not self.blue_destroyed:
                reward -= 5  # Pénalité pour l'échec de l'élimination
            self.ws.send(json.dumps({"type": "request_reset"}))
        self.total_reward += reward

        # Mettre à jour le temps de la dernière étape
        self.last_time = current_time

        return self.current_state, reward, self.done, {}

    def reset(self):
        # Attendre que le cube bleu ait été réinitialisé
        while True:
            blue_destroyed = self._check_collision()
            if not blue_destroyed:
                break
            time.sleep(0.1)  # Attendre 100 ms avant de vérifier à nouveau

        # Réinitialiser l'environnement
        self.current_state = {"position": {"x": 0.0, "y": 0.0, "z": 0.0}, "sees_enemy": 0}
        self.done = False
        self.start_time = time.time()
        self.last_time = self.start_time  # Initialiser last_time ici
        self.total_reward = 0
        self.sees_enemy_duration = 0
        self.blue_destroyed = False
        return self.current_state

    def render(self, mode="human"):
        # Optionnel : visualisation de l'état actuel
        print(f"Position : {self.current_state['position']}, Voit l'ennemi : {self.current_state['sees_enemy']}")

    def close(self):
        # Fermer la connexion WebSocket
        self.ws.close()
