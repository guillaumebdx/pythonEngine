from stable_baselines3 import DQN
import gymnasium as gym

# Crée un environnement Gymnasium
env = gym.make("CartPole-v1")

# Initialise le modèle DQN
model = DQN("MlpPolicy", env, verbose=1)

# Entraîne le modèle pendant 1000 itérations
model.learn(total_timesteps=1000)

print("Test DQN terminé avec succès !")
