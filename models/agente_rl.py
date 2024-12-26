import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from services.asignador import AsignadorRecursos
from demand_predictor import DemandPredictor
from entorno_rl import EntornoBalanceo
from app import cargar_datos_entrenamiento

# Definir constantes
NUM_SERVIDORES_INICIAL = 1
NUM_SERVIDORES_MAX = 5
UMBRAL_ESCALADO_SUPERIOR = 5
UMBRAL_ESCALADO_INFERIOR = 1
INTERVALO_IMPRESION = 10

# Inicializar el DemandPredictor y entrenarlo si es necesario
demand_predictor = DemandPredictor()

# Cargar datos de entrenamiento
X_train, y_train = cargar_datos_entrenamiento("datos_simulacion.csv")

if X_train is not None and y_train is not None:
    # Entrenar el modelo de predicción de demanda
    demand_predictor.train(X_train, y_train, epochs=100)

# Crear una instancia de AsignadorRecursos
asignador_recursos = AsignadorRecursos(NUM_SERVIDORES_INICIAL, demand_predictor)

# Crear el entorno de RL
entorno = EntornoBalanceo(asignador_recursos, NUM_SERVIDORES_MAX)

# Crear el agente PPO
modelo = PPO("MlpPolicy", entorno, verbose=1)

# Entrenar el agente
modelo.learn(total_timesteps=10000)  # Ajusta el número de pasos de entrenamiento

# Guardar el modelo entrenado (opcional)
modelo.save("modelo_ppo_balanceo")

print("Entrenamiento completado. Modelo guardado.")