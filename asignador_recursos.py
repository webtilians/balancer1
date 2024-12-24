import queue
import time
import random
import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
import os
import tensorflow as tf

class DemandPredictor:
    def __init__(self, model_path="demand_predictor_model.h5"):
        self.model_path = model_path
        self.input_shape = (4,)  # Definir input_shape como atributo de la clase
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

        feature_vector = np.array([
            features["longitud"],
            1 if features["tipo"] == "simple" else 0,
            1 if features["tipo"] == "compleja" else 0,
            1 if features["tipo"] == "codigo" else 0
        ])

        # Normalizar las características de entrada
        feature_vector = (feature_vector - self.mean) / self.std

        predicted_demand = self.model.predict(np.array([feature_vector]))[0][0]
        return predicted_demand

class ServidorSimulado:
    def __init__(self, id):
        self.id = id
        self.carga = 0
        self.arrancando = True  # Atributo para simular el arranque
        self.tiempo_arranque = 0.5
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
        tiempo_procesamiento = (longitud * 0.01 +
                               (1 if tipo == "compleja" else 0) * 0.5 +
                               (1 if tipo == "codigo" else 0) * 1 +
                               demanda_predicha * 0.2 +
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
        print(f"Servidor {self.id}: Solicitud completada. Tiempo de respuesta: {tiempo_respuesta:.4f} segundos. Carga actual: {self.carga:.2f}")

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
        """
        Procesa solicitudes de la cola, asignándolas a servidores libres.
        """
        servidor_elegido = min(self.servidores, key=lambda s: s.carga)
        # Solo asignar la solicitud si el servidor no está arrancando y hay solicitudes en la cola
        if not servidor_elegido.arrancando and not self.cola_solicitudes.empty():
            user_id, caracteristicas, predicted_demand, timestamp_llegada = self.cola_solicitudes.get()

            # Extraer 'longitud' y 'tipo' de 'caracteristicas'
            longitud = caracteristicas['longitud']
            tipo = caracteristicas['tipo']

            # Calcular el tiempo de espera en la cola
            tiempo_espera = time.time() - timestamp_llegada

            # --- DEBUG ---
            print(f"DEBUG - Intentando asignar solicitud de usuario {user_id} al servidor {servidor_elegido.id}")

            # Comprobación adicional de 'arrancando' dentro de procesar_solicitud
            if servidor_elegido.arrancando:
                print(f"ERROR - Servidor {servidor_elegido.id} está arrancando, pero fue seleccionado para asignación.")
                self.cola_solicitudes.put((user_id, caracteristicas, predicted_demand, timestamp_llegada))  # Devolver la solicitud a la cola
                self.cola_solicitudes.task_done()
                return

            print(f"Asignando solicitud de usuario {user_id} al servidor {servidor_elegido.id} con demanda predicha de: {predicted_demand}, tiempo de espera en cola: {tiempo_espera:.4f}")

            try:
                # Registrar el tiempo de inicio de la asignación
                tiempo_inicio_asignacion = time.time()

                # Asignar la solicitud al servidor
                servidor_elegido.procesar_solicitud(longitud, tipo, predicted_demand, timestamp_llegada)

                # Registrar el tiempo de finalización de la asignación
                tiempo_fin_asignacion = time.time()

                # Calcular y registrar el tiempo de asignación
                tiempo_asignacion = tiempo_fin_asignacion - tiempo_inicio_asignacion
                print(f"Tiempo de asignación para usuario {user_id}: {tiempo_asignacion:.4f} segundos")

            except Exception as e:
                print(f"Error al procesar la solicitud del usuario {user_id}: {e}")
                # Considera la posibilidad de volver a encolar la solicitud o manejar el error de otra manera

            finally:
                self.cola_solicitudes.task_done()

            # --- DEBUG ---
            print(f"DEBUG - Servidor elegido: {servidor_elegido.id}, Carga del servidor: {servidor_elegido.carga:.2f}")
            print(f"DEBUG - Tamaño de la cola después de asignar: {self.cola_solicitudes.qsize()}")

    def crear_servidor(self):
        """Añade un nuevo servidor a la lista de servidores."""
        if len(self.servidores) < self.num_servidores_max:
            nuevo_servidor_id = len(self.servidores)
            self.servidores.append(ServidorSimulado(nuevo_servidor_id))
            print(f"Nuevo servidor creado con ID {nuevo_servidor_id}. Total de servidores: {len(self.servidores)}")
        else:
            print(f"No se pueden crear más servidores. Se ha alcanzado el límite máximo de {self.num_servidores_max} servidores.")

    def eliminar_servidor(self):
        """Elimina un servidor de la lista de servidores, si hay más de uno."""
        if len(self.servidores) > 1:
            servidor_a_eliminar = self.servidores.pop()
            print(f"Servidor {servidor_a_eliminar.id} eliminado. Total de servidores: {len(self.servidores)}")
        else:
            print("No se pueden eliminar más servidores. Se ha alcanzado el mínimo de 1 servidor.")

    def comprobar_escalado(self):
        """Comprueba la carga total y escala el número de servidores si es necesario."""
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