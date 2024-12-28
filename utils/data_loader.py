from api.gestor_usuarios import GestorUsuarios
from api.analizador_solicitudes import AnalizadorSolicitudes
from services.asignador import AsignadorRecursos
from models.demand_predictor import DemandPredictor
import numpy as np
import pandas as pd
import json
from stable_baselines3 import PPO
from entorno_rl import EntornoBalanceo
import os

# --- CONFIGURACIÓN INICIAL ---

# Hiperparámetros del modelo y del entorno
NUM_SERVIDORES_INICIAL = 1
NUM_SERVIDORES_MAX = 5
UMBRAL_ESCALADO_SUPERIOR = 5
UMBRAL_ESCALADO_INFERIOR = 1
INTERVALO_IMPRESION = 10

# --- CARGA DE DATOS DE ENTRENAMIENTO ---

def cargar_datos_entrenamiento(ruta_csv):
    """
    Carga los datos de entrenamiento desde un archivo CSV.

    Args:
        ruta_csv (str): La ruta al archivo CSV.

    Returns:
        tuple: Una tupla que contiene dos arrays de NumPy:
               - X: Las características de entrenamiento.
               - y: Las etiquetas de entrenamiento (demanda).
    """
    try:
        df = pd.read_csv(ruta_csv)
        if df.empty:
            print("El archivo CSV está vacío.")
            return None, None

        # Convertir las características de JSON a diccionarios
        try:
            df['caracteristicas'] = df['caracteristicas'].apply(lambda x: json.loads(x.replace("'", '"')))
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON en la columna 'caracteristicas': {e}")
            return None, None

        # Extraer características y demanda
        X = []
        y = []
        for _, row in df.iterrows():
            caracteristicas = row['caracteristicas']
            if isinstance(caracteristicas, dict) and "longitud" in caracteristicas and "tipo" in caracteristicas and "vector_spacy" in caracteristicas:
                # Convertir el tipo de solicitud a un vector one-hot
                tipo_vector = [0, 0, 0]
                if caracteristicas["tipo"] == "simple":
                    tipo_vector[0] = 1
                elif caracteristicas["tipo"] == "compleja":
                    tipo_vector[1] = 1
                elif caracteristicas["tipo"] == "codigo":
                    tipo_vector[2] = 1

                # Extraer el vector de spaCy
                vector_spacy = caracteristicas["vector_spacy"]

                # Combinar todas las características en un solo vector
                feature_vector = np.concatenate([
                    np.array([caracteristicas["longitud"]]),
                    np.array(tipo_vector),
                    np.array(vector_spacy)
                ])

                X.append(feature_vector)
                y.append(row['demanda_predicha'])
            else:
                print(f"Advertencia: Formato incorrecto en la fila: {row}")

        return np.array(X), np.array(y)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_csv}")
        return None, None
    except Exception as e:
        print(f"Error al cargar los datos de entrenamiento: {e}")
        return None, None