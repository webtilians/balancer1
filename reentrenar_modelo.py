from asignador_recursos import DemandPredictor
from app import cargar_datos_entrenamiento
import numpy as np

# Cargar datos de entrenamiento
X_train, y_train = cargar_datos_entrenamiento("datos_simulacion.csv")

if X_train is not None and y_train is not None:
    # Instanciar el predictor de demanda
    demand_predictor = DemandPredictor()

    # Entrenar el modelo de predicción de demanda
    demand_predictor.train(X_train, y_train, epochs=100)  # Ajusta el número de épocas si es necesario
    print("Modelo de predicción de demanda reentrenado y guardado.")
else:
    print("No se pudieron cargar los datos de entrenamiento.")