from gym_env import CustomEnv

# Créer l'environnement
env = CustomEnv()

# Réinitialiser l'environnement
state = env.reset()
print(f"État initial : {state}")

# Exécuter quelques étapes pour tester
for i in range(5):
    print(f"\n--- Étape {i+1} ---")
    action = i % 5  # Alterner entre les actions 0 à 4
    state, reward, done, _ = env.step(action)
    print(f"Action : {action}")
    print(f"Nouvel état : {state}")
    print(f"Récompense : {reward}")
    print(f"Terminé : {done}")
