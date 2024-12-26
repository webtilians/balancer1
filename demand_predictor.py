import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
import os

class DemandPredictor:
    def __init__(self, model_path="demand_predictor_model.h5"):
        self.model_path = model_path
        self.input_shape = (304,)  # Ajustado el tamaño
        self.model = self.cargar_o_crear_modelo()
        self.trained = os.path.exists(self.model_path)
        self.mean = None  # Media para normalizar
        self.std = None   # Desviación estándar para normalizar

    def cargar_o_crear_modelo(self):
        """Carga el modelo desde el archivo si existe, de lo contrario crea uno nuevo."""
        if os.path.exists(self.model_path):
            model = keras.models.load_model(self.model_path)
            print("Modelo cargado desde el archivo.")
            # Volver a compilar el modelo después de cargarlo
            model.compile(optimizer='adam', loss=keras.losses.MeanSquaredError())
            self.trained = True
            return model
        else:
            return self.crear_modelo()

    def crear_modelo(self):
        """Crea el modelo de red neuronal."""
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=self.input_shape),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss=keras.losses.MeanSquaredError())
        return model

    def train(self, X, y, epochs=100, validation_split=0.0):  # Cambiar valor por defecto a 0.0
        """Entrena el modelo de red neuronal."""
        X = np.array(X)
        y = np.array(y)

        # Asegurarse de que los datos de entrada sean del tipo correcto
        if not isinstance(X, np.ndarray):
            raise ValueError("X debe ser un array de NumPy")
        if not isinstance(y, np.ndarray):
            raise ValueError("y debe ser un array de NumPy")

        # Normalizar los datos
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0)
        X = (X - self.mean) / self.std

        if validation_split > 0:
            # Dividir los datos en conjuntos de entrenamiento y validación
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split)
        else:
            # Usar todos los datos para entrenamiento
            X_train, y_train = X, y
            X_val, y_val = None, None  # No hay validación

        # Imprimir información sobre las formas de los datos
        print("Forma de X_train:", X_train.shape)
        print("Forma de y_train:", y_train.shape)
        if X_val is not None:
            print("Forma de X_val:", X_val.shape)
            print("Forma de y_val:", y_val.shape)

        # Entrenar el modelo
        try:
            if X_val is not None:
                self.model.fit(X_train, y_train, epochs=epochs, validation_data=(X_val, y_val))
            else:
                self.model.fit(X_train, y_train, epochs=epochs)  # No se pasa validation_data
            self.trained = True
            print("Modelo entrenado.")
        except Exception as e:
            print(f"Error durante el entrenamiento del modelo: {e}")
            return

        # Guardar el modelo entrenado
        try:
            self.model.save(self.model_path)
            print(f"Modelo guardado en {self.model_path}")
        except Exception as e:
            print(f"Error al guardar el modelo: {e}")

    def predict(self, features):
        """Predice la demanda de recursos para una solicitud."""
        if not self.trained:
            print("Advertencia: El modelo no ha sido entrenado. Se devuelve una predicción por defecto.")
            return 1.0

        # Asegurarse de que 'features' es un diccionario
        if not isinstance(features, dict):
            print("Error: 'features' debe ser un diccionario.")
            return 1.0

        # Extraer y convertir características
        longitud = features.get("longitud", 0)  # Valor por defecto 0 si no se encuentra
        tipo = features.get("tipo", "simple")    # Valor por defecto "simple" si no se encuentra

        # Convertir el tipo de solicitud a un vector one-hot
        tipo_vector = [0, 0, 0]
        if tipo == "simple":
            tipo_vector[0] = 1
        elif tipo == "compleja":
            tipo_vector[1] = 1
        elif tipo == "codigo":
            tipo_vector[2] = 1

        # Extraer el vector Word2Vec y asegurarse de que sea un array de NumPy
        # Extraer el vector spaCy y asegurarse de que sea un array de NumPy
        vector_spacy = features.get("vector_spacy", np.zeros(300))
        if isinstance(vector_spacy, list):
            vector_spacy = np.array(vector_spacy)

        # Combinar todas las características en un solo vector
        feature_vector = np.concatenate([
            np.array([longitud]),
            np.array(tipo_vector),
            vector_spacy
        ])

        # Normalizar las características de entrada
        feature_vector = (feature_vector - self.mean) / self.std

        # Asegurarse de que el vector de características sea un array de NumPy y tenga la forma correcta
        if not isinstance(feature_vector, np.ndarray):
            print("Error: feature_vector no es un array de NumPy.")
            return 1.0
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)

        # Verificar la forma del vector de características
        if feature_vector.shape[1] != self.input_shape[0]:
            print(f"Error: La forma del vector de características no coincide con la forma de entrada del modelo. "
                  f"Esperado: {self.input_shape}, Obtenido: {feature_vector.shape}")
            return 1.0

        predicted_demand = self.model.predict(feature_vector)[0][0]
        return predicted_demand