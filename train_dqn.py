# train_dqn.py
import gymnasium as gym
import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from gym_env import CustomEnv

# Définition du réseau Q-Network
class QNetwork(nn.Module):
    def __init__(self, state_size, action_size, hidden_size=64):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_size, action_size)

    def forward(self, state):
        x = self.fc1(state)
        x = self.relu1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.fc3(x)
        return x

# Fonction pour prétraiter l'état
def preprocess_state(state):
    position_dict = state['position']
    position = np.array([
        position_dict['x'],
        position_dict['y'],
        position_dict['z']
    ], dtype=np.float32)
    sees_enemy = np.array([state['sees_enemy']], dtype=np.float32)
   # print(f"Position: {position}, Shape: {position.shape}, Type: {type(position)}")
   # print(f"Sees Enemy: {sees_enemy}, Shape: {sees_enemy.shape}, Type: {type(sees_enemy)}")
    return np.concatenate([position, sees_enemy])


def train():
    env = CustomEnv()
    # Hyperparamètres
    state_size = 4  # 3 pour la position, 1 pour sees_enemy
    action_size = env.action_space.n
    hidden_size = 64
    batch_size = 64
    gamma = 0.99  # Facteur de discount
    epsilon = 1.0  # Taux d'exploration
    epsilon_min = 0.01
    epsilon_decay = 0.995
    learning_rate = 0.001
    max_episodes = 1000
    max_steps = 100000  # Nombre maximum d'étapes par épisode
    target_update = 10  # Mettre à jour le réseau cible tous les 'target_update' épisodes
    memory = deque(maxlen=10000)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    policy_net = QNetwork(state_size, action_size, hidden_size).to(device)
    target_net = QNetwork(state_size, action_size, hidden_size).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()

    optimizer = optim.Adam(policy_net.parameters(), lr=learning_rate)
    loss_fn = nn.MSELoss()

    for episode in range(max_episodes):
        state = env.reset()
        state = preprocess_state(state)
        state = torch.FloatTensor(state).unsqueeze(0).to(device)

        total_reward = 0
        for t in range(max_steps):
            # Sélection de l'action
            if random.random() < epsilon:
                action = random.randrange(action_size)
            else:
                with torch.no_grad():
                    q_values = policy_net(state)
                    action = torch.argmax(q_values).item()

            # Exécuter l'action
            next_state, reward, done, _ = env.step(action)
            next_state_np = preprocess_state(next_state)
            next_state_tensor = torch.FloatTensor(next_state_np).unsqueeze(0).to(device)

            total_reward += reward

            # Stocker la transition en mémoire
            memory.append((state, action, reward, next_state_tensor, done))

            state = next_state_tensor

            # Expérience Replay
            if len(memory) >= batch_size:
                batch = random.sample(memory, batch_size)
                batch_state, batch_action, batch_reward, batch_next_state, batch_done = zip(*batch)

                batch_state = torch.cat(batch_state)
                batch_action = torch.LongTensor(batch_action).unsqueeze(1).to(device)
                batch_reward = torch.FloatTensor(batch_reward).unsqueeze(1).to(device)
                batch_next_state = torch.cat(batch_next_state)
                batch_done = torch.FloatTensor(batch_done).unsqueeze(1).to(device)

                # Calcul de Q(s_t, a)
                q_values = policy_net(batch_state).gather(1, batch_action)

                # Calcul des valeurs cibles Q
                with torch.no_grad():
                    max_next_q_values = target_net(batch_next_state).max(1)[0].unsqueeze(1)
                    target_q_values = batch_reward + (gamma * max_next_q_values * (1 - batch_done))

                # Calcul de la perte
                loss = loss_fn(q_values, target_q_values)

                # Optimisation du modèle
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            if done:
                break

        # Décroissance de epsilon
        if epsilon > epsilon_min:
            epsilon *= epsilon_decay

        # Mettre à jour le réseau cible
        if episode % target_update == 0:
            target_net.load_state_dict(policy_net.state_dict())

        print(f"===================Épisode {episode}, Récompense Totale: {total_reward}, Epsilon: {epsilon}")

    # Sauvegarder le modèle entraîné
    torch.save(policy_net.state_dict(), "dqn_model.pth")

if __name__ == "__main__":
    train()
