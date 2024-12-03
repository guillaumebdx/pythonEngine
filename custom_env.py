import gymnasium as gym
from gymnasium import spaces
import numpy as np

class CubeChaseEnv(gym.Env):
    def __init__(self, websocket):
        super(CubeChaseEnv, self).__init__()

        # WebSocket pour la communication avec le jeu JS
        self.websocket = websocket

        # Observation : distance, angle, orientation
        self.observation_space = spaces.Box(low=-10, high=10, shape=(6,), dtype=np.float32)

        # Actions : avancer, reculer, tourner gauche/droite, sauter
        self.action_space = spaces.Discrete(5)

        # État des cubes (sera mis à jour par le JS)
        self.cube_red = None
        self.cube_blue = None

    def reset(self):
        # Envoyer un signal de réinitialisation au jeu JS
        self.websocket.send("reset")

        # Recevoir l'état initial
        state = self._receive_state()
        return self._get_obs(state)

    def _receive_state(self):
        # Réception de l’état depuis le jeu (à implémenter côté WebSocket)
        state = self.websocket.recv()
        self.cube_red, self.cube_blue = state["cube_red"], state["cube_blue"]
        return state

    def _get_obs(self, state):
        # Convertir les positions en tableaux NumPy
        red_pos = np.array(self.cube_red["pos"])
        blue_pos = np.array(self.cube_blue["pos"])

        # Observation pour le chat (cube rouge)
        red_to_blue = blue_pos - red_pos
        red_distance = np.linalg.norm(red_to_blue)
        red_angle = np.arctan2(red_to_blue[1], red_to_blue[0]) - self.cube_red["orientation"]
        red_obs = [
            red_distance if red_distance < 5.0 else 0,
            red_angle if red_distance < 5.0 else 0,
            self.cube_red["orientation"],
            self.cube_red["pos"][0],
            self.cube_red["pos"][1],
        ]

        # Observation pour la souris (cube bleu)
        blue_to_red = red_pos - blue_pos
        blue_distance = np.linalg.norm(blue_to_red)
        blue_angle = np.arctan2(blue_to_red[1], blue_to_red[0]) - self.cube_blue["orientation"]
        blue_obs = [
            blue_distance if blue_distance < 5.0 else 0,
            blue_angle if blue_distance < 5.0 else 0,
            self.cube_blue["orientation"],
            self.cube_blue["pos"][0],
            self.cube_blue["pos"][1],
        ]

        return np.array(red_obs), np.array(blue_obs)

    def step(self, actions):
        red_action, blue_action = actions

        # Envoyer les actions au moteur JS
        self.websocket.send({
            "red_action": red_action,
            "blue_action": blue_action
        })

        # Recevoir l'état mis à jour
        state = self._receive_state()

        # Convertir les positions en tableaux NumPy
        red_pos = np.array(self.cube_red["pos"])
        blue_pos = np.array(self.cube_blue["pos"])

        # Calcul des récompenses
        distance = np.linalg.norm(red_pos - blue_pos)
        red_reward = -distance
        blue_reward = distance

        done = distance < 0.5  # Fin de partie si collision
        if done:
            red_reward += 100
            blue_reward -= 100

        return self._get_obs(state), [red_reward, blue_reward], done, {}

    def render(self):
        print(f"Chat : {self.cube_red}, Souris : {self.cube_blue}")
