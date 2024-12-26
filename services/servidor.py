import time
import random
import numpy as np

# Definir constantes
FACTOR_LONGITUD = 0.1
FACTOR_COMPLEJA = 0.2
FACTOR_CODIGO = 0.3
FACTOR_DEMANDA = 0.4

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