from flask import Flask
from api.routes import api_routes
from services.asignador import AsignadorRecursos
from models.demand_predictor import DemandPredictor
import numpy as np
import pandas as pd
import time
import json
from stable_baselines3 import PPO
from entorno_rl import EntornoBalanceo
import os
import sys

app = Flask(__name__)

# Registrar las rutas
app.register_blueprint(api_routes)

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- CONFIGURACIÓN INICIAL ---

# Hiperparámetros del modelo y del entorno
NUM_SERVIDORES_INICIAL = 1
NUM_SERVIDORES_MAX = 5
UMBRAL_ESCALADO_SUPERIOR = 5
UMBRAL_ESCALADO_INFERIOR = 1
INTERVALO_IMPRESION = 10

# --- CARGA DE DATOS DE ENTRENAMIENTO ---

def cargar_datos_entrenamiento(archivo_csv):
    datos = pd.read_csv(archivo_csv)
    X = []
    y = []

    for _, row in datos.iterrows():
        try:
            caracteristicas = eval(row['caracteristicas'])  # Asegurarnos de que sea un dict
            tipo_vector = [1, 0] if caracteristicas['tipo'] == 'simple' else [0, 1]  # One-hot encoding
            vector_spacy = caracteristicas['vector_spacy']

            # Incluimos latencia_calculada al feature_vector
            feature_vector = np.concatenate([
                np.array([caracteristicas["longitud"], row['latencia_calculada']]),
                np.array(tipo_vector),
                np.array(vector_spacy)
            ])
            
            X.append(feature_vector)
            y.append(row['demanda_predicha'])
        except Exception as e:
            print(f"Error procesando la fila: {e}")
    
    return np.array(X), np.array(y)


# --- ENTRENAMIENTO DEL MODELO DE PREDICCIÓN DE DEMANDA ---

# Instanciar el predictor de demanda
demand_predictor = DemandPredictor()

# Cargar datos de entrenamiento

X_train, y_train = cargar_datos_entrenamiento("scripts/datos_entrenamiento.csv")

if X_train is not None and y_train is not None:
    # Entrenar el modelo de predicción de demanda
    demand_predictor.train(X_train, y_train, epochs=100)

    # Crear la instancia del asignador de recursos
    asignador_recursos = AsignadorRecursos(NUM_SERVIDORES_INICIAL, demand_predictor)

    # Crear el entorno de RL
    entorno = EntornoBalanceo(asignador_recursos, NUM_SERVIDORES_MAX)

    # Cargar o crear el modelo de RL
    try:
        modelo_cargado = PPO.load("modelo_ppo_balanceo", env=entorno)
        print("Modelo de RL cargado.")
    except FileNotFoundError:
        print("No se encontró un modelo de RL guardado. Creando uno nuevo.")
        modelo_cargado = PPO("MlpPolicy", entorno, verbose=1)

else:
    print("No se pudieron cargar los datos de entrenamiento. Saliendo.")
    exit()
    
if __name__ == "__main__":
    app.run(debug=True)