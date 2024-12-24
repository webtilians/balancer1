from flask import Flask, request, jsonify
from gestor_usuarios import GestorUsuarios
from analizador_solicitudes import AnalizadorSolicitudes
from asignador_recursos import AsignadorRecursos, DemandPredictor, ServidorSimulado
import numpy as np
import pandas as pd
import time
import json
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
import queue
from tensorflow import keras
from sklearn.model_selection import train_test_split
import os

app = Flask(__name__)

# --- CONFIGURACIÓN INICIAL ---
training_data_predefined = [
    ({"longitud": 10, "tipo": "simple"}, 1),
    ({"longitud": 25, "tipo": "compleja"}, 3),
    ({"longitud": 15, "tipo": "codigo"}, 5),
    ({"longitud": 12, "tipo": "simple"}, 1),
    ({"longitud": 30, "tipo": "compleja"}, 4),
    ({"longitud": 20, "tipo": "codigo"}, 6)
]
# Hiperparámetros del modelo y del entorno
NUM_SERVIDORES_INICIAL = 1
NUM_SERVIDORES_MAX = 5
UMBRAL_ESCALADO_SUPERIOR = 5
UMBRAL_ESCALADO_INFERIOR = 1
INTERVALO_IMPRESION = 10

# --- CLASES DEL ENTORNO DE RL (DENTRO DE APP.PY) ---

class EntornoBalanceo(gym.Env):
    def __init__(self, asignador_recursos):
        super(EntornoBalanceo, self).__init__()
        self.asignador_recursos = asignador_recursos
        self.action_space = spaces.Discrete(3)  # 0: No hacer nada, 1: Crear servidor, 2: Eliminar servidor
        self.observation_space = spaces.Box(low=0, high=100, shape=(NUM_SERVIDORES_MAX + 1,), dtype=np.float32)
    
    def reset(self, seed=None):
        super().reset(seed=seed)
        # Reiniciar el entorno a un estado inicial
        for servidor in self.asignador_recursos.servidores:
            servidor.carga = 0
        self.asignador_recursos.cola_solicitudes.queue.clear()

        # Devolver el estado inicial
        return self._get_estado(), {}

    def step(self, accion):
        # Ejecutar la acción en el entorno
        if accion == 1:
            self.asignador_recursos.crear_servidor()
        elif accion == 2:
            self.asignador_recursos.eliminar_servidor()

        # Esperar un tiempo para que la acción tenga efecto y se procesen solicitudes
        time.sleep(1)  # Ajusta el tiempo según sea necesario

        # Calcular la recompensa (esto es solo un ejemplo)
        carga_promedio = sum(s.carga for s in self.asignador_recursos.servidores) / len(self.asignador_recursos.servidores) if len(self.asignador_recursos.servidores) > 0 else 0
        longitud_cola = self.asignador_recursos.cola_solicitudes.qsize()
        recompensa = -carga_promedio - longitud_cola * 0.5  # Penalizar carga alta y cola larga

        # Obtener el nuevo estado
        estado = self._get_estado()

        # Comprobar si el episodio ha terminado (puedes definir un criterio de finalización)
        terminado = False  # En este ejemplo, el episodio nunca termina
        truncado = False
        # Información adicional (opcional)
        info = {}

        return estado, recompensa, terminado, truncado, info

    def _get_estado(self):
        # Obtener el estado actual del sistema
        carga_servidores = [s.carga for s in self.asignador_recursos.servidores]
        longitud_cola = self.asignador_recursos.cola_solicitudes.qsize()

        # Asegurarse de que el estado tenga siempre la misma longitud
        while len(carga_servidores) < NUM_SERVIDORES_MAX:
            carga_servidores.append(0.0)  # Rellenar con ceros si hay menos servidores que el máximo

        estado = np.array(carga_servidores + [longitud_cola], dtype=np.float32)
        return estado

# --- CARGA Y ENTRENAMIENTO DEL MODELO DE RL ---

# Instanciar el predictor de demanda
demand_predictor = DemandPredictor()

# Cargar datos de entrenamiento desde el CSV
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

        # Asegurarse de que las columnas necesarias existen
        if 'caracteristicas' not in df.columns or 'demanda_predicha' not in df.columns:
            raise ValueError("El archivo CSV debe contener las columnas 'caracteristicas' y 'demanda_predicha'")

        # Limpieza de datos: convertir la cadena JSON en la columna 'caracteristicas' a un diccionario
        def limpiar_caracteristicas(x):
            try:
                # Asegurarse de que el valor sea una cadena antes de procesarlo
                if isinstance(x, str):
                    # Eliminar espacios en blanco y saltos de línea adicionales
                    x = x.strip().replace('\n', '')
                    # Reemplazar comillas simples por dobles para que sea un JSON válido
                    x = x.replace("'", '"')
                    # Convertir la cadena JSON a un diccionario
                    return json.loads(x)
                else:
                    print(f"Advertencia: 'caracteristicas' no es una cadena: {x}")
                    return {}  # Devolver un diccionario vacío en caso de error
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}. Valor: {x}")
                return {}  # Devolver un diccionario vacío en caso de error

        # Aplicar la función de limpieza a la columna 'caracteristicas'
        df['caracteristicas'] = df['caracteristicas'].apply(limpiar_caracteristicas)

        # Extraer características y demanda
        X = []
        y = []
        for _, row in df.iterrows():
            caracteristicas = row['caracteristicas']
            # Asegurarse de que las características se extraen correctamente
            if not isinstance(caracteristicas, dict) or "longitud" not in caracteristicas or "tipo" not in caracteristicas:
                print(f"Advertencia: Formato incorrecto en la fila: {row}")
                continue

            feature_vector = [
                caracteristicas["longitud"],
                1 if caracteristicas["tipo"] == "simple" else 0,
                1 if caracteristicas["tipo"] == "compleja" else 0,
                1 if caracteristicas["tipo"] == "codigo" else 0
            ]
            X.append(feature_vector)
            y.append(row['demanda_predicha'])

        return np.array(X), np.array(y)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_csv}")
        return None, None
    except Exception as e:
        print(f"Error al cargar los datos de entrenamiento: {e}")
        return None, None

# # Cargar datos de entrenamiento
# X_train, y_train = cargar_datos_entrenamiento("datos_simulacion.csv")

# if X_train is not None and y_train is not None:
#     # Entrenar el modelo de predicción de demanda
#     demand_predictor.train(X_train, y_train, epochs=100)

#     # Crear la instancia del asignador de recursos
#     asignador_recursos = AsignadorRecursos(NUM_SERVIDORES_INICIAL, demand_predictor)

#     # Crear el entorno de RL
#     entorno = EntornoBalanceo(asignador_recursos)

#     # Cargar o crear el modelo de RL
#     try:
#         modelo_cargado = PPO.load("modelo_ppo_balanceo", env=entorno)
#         print("Modelo de RL cargado.")
#     except FileNotFoundError:
#         print("No se encontró un modelo de RL guardado. Creando uno nuevo.")
#         modelo_cargado = PPO("MlpPolicy", entorno, verbose=1)

# else:
#     print("No se pudieron cargar los datos de entrenamiento. Saliendo.")
#     exit()

# Cargar datos de entrenamiento
X_train, y_train = None, None  # Inicializar como None
if os.path.exists("datos_simulacion.csv"):
    X_train, y_train = cargar_datos_entrenamiento("datos_simulacion.csv")

if X_train is not None and y_train is not None:
    # Entrenar el modelo de predicción de demanda
    demand_predictor.train(X_train, y_train, epochs=100)
else:
    print("No se encontraron datos de entrenamiento en el CSV. Se usará un conjunto de datos predefinido.")
    X_train = np.array([list(d[0].values()) for d in training_data_predefined])
    y_train = np.array([d[1] for d in training_data_predefined])
    demand_predictor.train(X_train, y_train, epochs=100)
    
# Crear la instancia del asignador de recursos
asignador_recursos = AsignadorRecursos(NUM_SERVIDORES_INICIAL, demand_predictor)

# Crear el entorno de RL
entorno = EntornoBalanceo(asignador_recursos)

# Cargar o crear el modelo de RL
try:
    modelo_cargado = PPO.load("modelo_ppo_balanceo", env=entorno)
    print("Modelo de RL cargado.")
except FileNotFoundError:
    print("No se encontró un modelo de RL guardado. Creando uno nuevo.")
    modelo_cargado = PPO("MlpPolicy", entorno, verbose=1)

# --- CONFIGURACIÓN DE LA APLICACIÓN FLASK ---

# Instanciar los componentes
gestor_usuarios = GestorUsuarios()
analizador_solicitudes = AnalizadorSolicitudes()

# --- RUTAS DE LA API ---

@app.route('/solicitud', methods=['POST'])
def procesar_solicitud():
    global modelo_cargado
    """
    Recibe una solicitud de usuario, la analiza, asigna un perfil y la enruta a un servidor.
    """
    try:
        data = request.get_json()

        # Validar la entrada
        if not data or 'user_id' not in data or 'texto' not in data:
            return jsonify({'error': 'Datos de solicitud no válidos'}), 400

        user_id = data['user_id']
        texto_solicitud = data['texto']

        # Analizar la solicitud
        caracteristicas = analizador_solicitudes.analizar(texto_solicitud)

        # Registrar la solicitud en el historial del usuario
        gestor_usuarios.registrar_solicitud(user_id, caracteristicas)

        # Obtener el perfil del usuario
        perfil = gestor_usuarios.obtener_perfil(user_id)

        # Registrar el tiempo de inicio
        inicio = time.time()
        
        # Obtener el timestamp de llegada o usar el tiempo actual si no se proporciona
        timestamp_llegada = data.get('timestamp', time.time())

        # Obtener el estado actual del sistema para el agente de RL
        estado = entorno._get_estado()

        # Obtener la acción del modelo de RL
        accion, _ = modelo_cargado.predict(estado)

        # Ejecutar la acción en el entorno (escalado)
        nuevo_estado, recompensa, terminado, truncado, info = entorno.step(accion)

        # Asignar la solicitud a un servidor (usando la lógica de AsignadorRecursos)
        servidor_id = asignador_recursos.asignar(user_id, caracteristicas)

        # Registrar el tiempo de finalización
        fin = time.time()

        # Calcular el tiempo de asignación
        tiempo_asignacion = fin - inicio

        # Obtener la predicción de la demanda
        demanda_predicha = demand_predictor.predict(caracteristicas)

        # Actualizar el perfil del usuario basado en su historial
        gestor_usuarios.actualizar_perfil(user_id)

        # Registrar el tiempo de inicio
        inicio = time.time()

        # Obtener la predicción de la demanda
        demanda_predicha = demand_predictor.predict(caracteristicas)

        # Asignar la solicitud a un servidor
        servidor_id = asignador_recursos.asignar(user_id, caracteristicas)

        # Registrar el tiempo de finalización
        fin = time.time()

        # Calcular el tiempo de asignación
        tiempo_asignacion = fin - inicio

        # Actualizar el perfil del usuario basado en su historial
        gestor_usuarios.actualizar_perfil(user_id)

        caracteristicas_para_respuesta = {
            'longitud': caracteristicas['longitud'],
            'tipo': caracteristicas['tipo'],
            'demanda_predicha': float(demanda_predicha)  # Convertir a float
        }

        return jsonify({
            'mensaje': 'Solicitud procesada correctamente',
            'user_id': user_id,
            'perfil': perfil,
            'servidor_asignado': servidor_id,
            'caracteristicas': caracteristicas_para_respuesta,
            'tiempo_asignacion': tiempo_asignacion,
            'demanda_predicha': float(demanda_predicha),
            'timestamp_llegada': timestamp_llegada# Convertir a float
        }), 200

    except Exception as e:
        print(f"Error al procesar la solicitud: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Nueva ruta para actualizar todos los perfiles
@app.route('/actualizar_perfiles', methods=['POST'])
def actualizar_perfiles():
    try:
        gestor_usuarios.actualizar_perfiles()
        return jsonify({'mensaje': 'Perfiles de usuario actualizados correctamente'}), 200
    except Exception as e:
        print(f"Error al actualizar perfiles: {e}")
        return jsonify({'error': 'Error interno del servidor al actualizar perfiles'}), 500

if __name__ == '__main__':
    app.run(debug=True)