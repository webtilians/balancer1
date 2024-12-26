import queue
import time
import random
import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
import os
import tensorflow as tf

# Constantes
FACTOR_LONGITUD = 0.01
FACTOR_COMPLEJA = 0.5
FACTOR_CODIGO = 1.0
FACTOR_DEMANDA = 0.2
TIEMPO_ARRANQUE = 0.5
UMBRAL_ESCALADO_SUPERIOR = 5
UMBRAL_ESCALADO_INFERIOR = 1
INTERVALO_IMPRESION = 10

class DemandPredictor:
    def __init__(self, model_path="demand_predictor_model.h5"):
        self.model_path = model_path
        self.input_shape = (104,)  # Ajustado el tamaño
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

    def train(self, X, y, epochs=100, validation_split=0.2):
        """Entrena el modelo de red neuronal."""
        X = np.array(X)
        y = np.array(y)

        # Asegurarse de que los datos de entrada sean del tipo correcto
        if not isinstance(X, np.ndarray):
            raise ValueError("X debe ser un array de NumPy")
        if not isinstance(y, np.ndarray):
            raise ValueError("y debe ser un array de NumPy")

        # Dividir los datos en conjuntos de entrenamiento y validación
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split)

        # Imprimir información sobre las formas de los datos
        print("Forma de X_train:", X_train.shape)
        print("Forma de y_train:", y_train.shape)
        print("Forma de X_val:", X_val.shape)
        print("Forma de y_val:", y_val.shape)

        # Normalizar los datos
        self.mean = X_train.mean(axis=0)
        self.std = X_train.std(axis=0)
        X_train = (X_train - self.mean) / self.std
        X_val = (X_val - self.mean) / self.std

        # Entrenar el modelo
        try:
            self.model.fit(X_train, y_train, epochs=epochs, validation_data=(X_val, y_val))
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
        vector_w2v = features.get("vector_w2v", np.zeros(100))  # Asumiendo que Word2Vec tiene 100 dimensiones
        if isinstance(vector_w2v, list):
            vector_w2v = np.array(vector_w2v)

        # Combinar todas las características en un solo vector
        feature_vector = np.concatenate([
            np.array([longitud]),
            np.array(tipo_vector),
            vector_w2v
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

class ServidorSimulado:
    def __init__(self, id):
        self.id = id
        self.carga = 0
        self.arrancando = True  # Atributo para simular el arranque
        self.tiempo_arranque = 0.5
        self.tiempos_procesamiento = []  # Lista para registrar los tiempos de procesamiento
        print(f"Servidor {self.id}: Iniciando...")
        time.sleep(self.tiempo_arranque)
        self.arrancando = False
        print(f"Servidor {self.id}: Listo para procesar solicitudes.")

    def procesar_solicitud(self, longitud, tipo, demanda_predicha, timestamp_llegada):
        """Simula el procesamiento de una solicitud."""
        if self.arrancando:
            print(f"Servidor {self.id}: No se puede procesar la solicitud, el servidor está arrancando.")
            return

        # Calcular el tiempo de espera en la cola
        tiempo_espera = time.time() - timestamp_llegada

        print(f"Servidor {self.id}: Procesando solicitud. Longitud: {longitud}, Tipo: {tipo}, Demanda Predicha: {demanda_predicha}. Tiempo de espera en cola: {tiempo_espera:.4f}")
        # Cálculo del tiempo de procesamiento (incluyendo tipo de solicitud y demanda predicha)
        tiempo_procesamiento = (longitud * FACTOR_LONGITUD +
                               (1 if tipo == "compleja" else 0) * FACTOR_COMPLEJA +
                               (1 if tipo == "codigo" else 0) * FACTOR_CODIGO +
                               demanda_predicha * FACTOR_DEMANDA +
                               random.uniform(-0.1, 0.1))  # Añadir un factor aleatorio

        # Asegurarse de que el tiempo de procesamiento no sea negativo
        tiempo_procesamiento = max(0, tiempo_procesamiento)

        # Convertir tiempo_procesamiento a float estándar
        tiempo_procesamiento = float(tiempo_procesamiento)

        self.carga += tiempo_procesamiento

        # --- DEBUG ---
        print(f"DEBUG - Servidor {self.id}: Iniciando procesamiento. Carga actual: {self.carga:.2f}")

        time.sleep(tiempo_procesamiento)  # Simular tiempo de procesamiento

        self.carga -= tiempo_procesamiento

        # --- DEBUG ---
        print(f"DEBUG - Servidor {self.id}: Terminando procesamiento. Carga actual: {self.carga:.2f}")

        # Calcular y registrar métricas de latencia
        tiempo_respuesta = time.time() - timestamp_llegada

        # Registrar el tiempo de procesamiento real
        tiempo_procesamiento_real = time.time() - timestamp_llegada - tiempo_espera
        self.tiempos_procesamiento.append(tiempo_procesamiento_real)

        print(f"Servidor {self.id}: Solicitud completada. Tiempo de respuesta: {tiempo_respuesta:.4f} segundos. Carga actual: {self.carga:.2f}")

    def calcular_tasa_servicio(self):
        """
        Calcula la tasa de servicio promedio del servidor en solicitudes por segundo.
        """
        if len(self.tiempos_procesamiento) == 0:
            return 0

        tasa_servicio = 1 / np.mean(self.tiempos_procesamiento)
        return tasa_servicio

class AsignadorRecursos:
    def __init__(self, num_servidores_inicial, demand_predictor):
        self.num_servidores_max = 5
        self.servidores = [ServidorSimulado(i) for i in range(num_servidores_inicial)]
        self.demand_predictor = demand_predictor
        self.umbral_escalado_superior = 5
        self.umbral_escalado_inferior = 1
        self.cola_solicitudes = queue.Queue()
        self.intervalo_impresion = 10
        self.ultimo_tiempo_impresion = time.time()
        self.tiempos_llegada = []
        self.tiempos_respuesta_recientes = []
        self.servidor_creado_anteriormente = False
        self.servidor_eliminado_anteriormente = False

    def asignar(self, user_id, caracteristicas):
        """Asigna una solicitud a la cola."""
        predicted_demand = self.demand_predictor.predict(caracteristicas)
        timestamp_llegada = time.time()
        self.cola_solicitudes.put((user_id, caracteristicas, predicted_demand, timestamp_llegada))
        self.tiempos_llegada.append(timestamp_llegada)
        print(f"Solicitud de usuario {user_id} encolada. Demanda predicha: {predicted_demand:.2f}")
        self.procesar_solicitudes()
        self.comprobar_escalado()
        return "encolada"
    
    def procesar_solicitudes(self):
        servidor_elegido = min(self.servidores, key=lambda s: s.carga)
        while not self.cola_solicitudes.empty() and not servidor_elegido.arrancando:
            user_id, caracteristicas, predicted_demand, timestamp_llegada = self.cola_solicitudes.get()
            longitud = caracteristicas['longitud']
            tipo = caracteristicas['tipo']

            print(f"Asignando solicitud de usuario {user_id} al servidor {servidor_elegido.id} con demanda predicha de: {predicted_demand}")

            try:
                tiempo_inicio_asignacion = time.time()
                tiempo_respuesta = servidor_elegido.procesar_solicitud(longitud, tipo, predicted_demand, timestamp_llegada)
                tiempo_fin_asignacion = time.time()

                if tiempo_respuesta is not None:
                    self.tiempos_respuesta_recientes.append(tiempo_respuesta)
                    if len(self.tiempos_respuesta_recientes) > 10:
                        self.tiempos_respuesta_recientes.pop(0)

                tiempo_asignacion = tiempo_fin_asignacion - tiempo_inicio_asignacion
                print(f"Tiempo de asignación para usuario {user_id}: {tiempo_asignacion:.4f} segundos")

            except Exception as e:
                print(f"Error al procesar la solicitud del usuario {user_id}: {e}")

            finally:
                self.cola_solicitudes.task_done()

    def crear_servidor(self):
        """Añade un nuevo servidor a la lista de servidores."""
        if len(self.servidores) < self.num_servidores_max:
            nuevo_servidor_id = len(self.servidores)
            self.servidores.append(ServidorSimulado(nuevo_servidor_id))
            print(f"Nuevo servidor creado con ID {nuevo_servidor_id}. Total de servidores: {len(self.servidores)}")
            self.servidor_creado_anteriormente = True  # Establecer el flag de creación de servidor
        else:
            print(f"No se pueden crear más servidores. Se ha alcanzado el límite máximo de {self.num_servidores_max} servidores.")

    def eliminar_servidor(self):
        """Elimina un servidor de la lista de servidores, si hay más de uno."""
        if len(self.servidores) > 1:
            servidor_a_eliminar = self.servidores.pop()
            print(f"Servidor {servidor_a_eliminar.id} eliminado. Total de servidores: {len(self.servidores)}")
            self.servidor_eliminado_anteriormente = True  # Establecer el flag de eliminación de servidor
        else:
            print("No se pueden eliminar más servidores. Se ha alcanzado el mínimo de 1 servidor.")
            
    def obtener_tiempos_respuesta_recientes(self, n):
        """
        Devuelve los últimos 'n' tiempos de respuesta registrados.
        """
        return self.tiempos_respuesta_recientes[-n:]

    def comprobar_escalado(self):
        """
        Comprueba si la carga total de los servidores supera o cae por debajo de los umbrales definidos.
        Escala el número de servidores en consecuencia.
        """
        carga_total = sum(s.carga for s in self.servidores if not s.arrancando)
        num_servidores_activos = sum(1 for s in self.servidores if not s.arrancando)
        print(f"Carga total del sistema: {carga_total:.2f}, servidores activos: {num_servidores_activos}")

        if carga_total > self.umbral_escalado_superior and len(self.servidores) < self.num_servidores_max:
            self.crear_servidor()
        elif carga_total < self.umbral_escalado_inferior and len(self.servidores) > 1:
            self.eliminar_servidor()
        self.imprimir_estado()

    def imprimir_estado(self):
        """Imprime el estado actual de los servidores y la cola de solicitudes."""
        ahora = time.time()
        if ahora - self.ultimo_tiempo_impresion > self.intervalo_impresion:
            print("\n--- Estado del Sistema ---")
            for servidor in self.servidores:
                print(f"Servidor {servidor.id}: Carga actual = {servidor.carga:.2f}, Arrancando = {servidor.arrancando}")
            print(f"Longitud de la cola de solicitudes: {self.cola_solicitudes.qsize()}")
            print("--------------------------\n")
            self.ultimo_tiempo_impresion = ahora

    
            
    def calcular_tasa_llegadas(self):
        """
        Calcula la tasa de llegadas promedio (lambda) en solicitudes por segundo.
        """
        if len(self.tiempos_llegada) < 2:
            return 0  # No hay suficientes datos para calcular la tasa

        # Calcular las diferencias de tiempo entre llegadas consecutivas
        diferencias_tiempo = np.diff(self.tiempos_llegada)

        # Calcular la tasa de llegadas promedio (lambda)
        tasa_llegadas = 1 / np.mean(diferencias_tiempo)
        return tasa_llegadas