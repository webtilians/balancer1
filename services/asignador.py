import queue
import time
import random
import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
import os
import tensorflow as tf
from demand_predictor import DemandPredictor
from services.servidor import ServidorSimulado

# Constantes
FACTOR_LONGITUD = 0.01
FACTOR_COMPLEJA = 0.5
FACTOR_CODIGO = 1.0
FACTOR_DEMANDA = 0.2
TIEMPO_ARRANQUE = 0.5
UMBRAL_ESCALADO_SUPERIOR = 5
UMBRAL_ESCALADO_INFERIOR = 1
INTERVALO_IMPRESION = 10

class AsignadorRecursos:
    def __init__(self, num_servidores_inicial, demand_predictor):
        self.num_servidores_max = 5
        self.servidores = [ServidorSimulado(i) for i in range(num_servidores_inicial)]
        self.demand_predictor = demand_predictor
        self.umbral_escalado_superior = UMBRAL_ESCALADO_SUPERIOR
        self.umbral_escalado_inferior = UMBRAL_ESCALADO_INFERIOR
        self.cola_solicitudes = queue.Queue()
        self.intervalo_impresion = INTERVALO_IMPRESION
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

    def obtener_tiempos_respuesta_recientes(self, n):
        """
        Devuelve los últimos 'n' tiempos de respuesta registrados.
        """
        return self.tiempos_respuesta_recientes[-n:]