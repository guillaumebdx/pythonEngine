from custom_env import CubeChaseEnv  # Remplace par ton module
import random

# Classe factice pour simuler le WebSocket (à remplacer par ton vrai WebSocket plus tard)
class FakeWebSocket:
    def send(self, message):
        print(f"Message envoyé au moteur JS : {message}")

    def recv(self):
        # Exemple d'état retourné par le moteur JS
        return {
            "cube_red": {"pos": [random.uniform(-5, 5), random.uniform(-5, 5)], "orientation": random.uniform(0, 3.14)},
            "cube_blue": {"pos": [random.uniform(-5, 5), random.uniform(-5, 5)], "orientation": random.uniform(0, 3.14)},
        }

# Créer l'environnement avec un faux WebSocket
env = CubeChaseEnv(FakeWebSocket())
obs = env.reset()

# Simulation de quelques étapes avec des actions aléatoires
for step in range(10):  # On fait 10 étapes
    red_action = env.action_space.sample()  # Action aléatoire pour le chat
    blue_action = env.action_space.sample()  # Action aléatoire pour la souris

    obs, rewards, done, _ = env.step([red_action, blue_action])

    print(f"Étape {step + 1}:")
    print(f"  Actions : Chat={red_action}, Souris={blue_action}")
    print(f"  Observations : {obs}")
    print(f"  Récompenses : {rewards}")

    if done:
        print("Fin de l'épisode : collision détectée.")
        break

