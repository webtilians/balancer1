from flask import Flask, request, jsonify
from api.gestor_usuarios import GestorUsuarios
from api.analizador_solicitudes import AnalizadorSolicitudes
import numpy as np
import time
import json

# Acceder a las variables y funciones de app.py
from app import modelo_cargado, entorno, demand_predictor, asignador_recursos

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA APLICACIÓN FLASK ---

# Instanciar los componentes (ya deberían estar creados en app.py)
gestor_usuarios = GestorUsuarios()
analizador_solicitudes = AnalizadorSolicitudes()

# --- RUTAS DE LA API ---

@app.route('/solicitud', methods=['POST'])
def procesar_solicitud():
    global modelo_cargado
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

        # Obtener el estado actual del sistema para el agente de RL
        estado = entorno._get_estado()

        # Obtener la acción del modelo de RL
        accion, _states = modelo_cargado.predict(estado, deterministic=True)

        # Ejecutar la acción en el entorno (escalado)
        nuevo_estado, recompensa, terminado, truncado, info = entorno.step(int(accion))

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

        caracteristicas_para_respuesta = {
            'longitud': caracteristicas['longitud'],
            'tipo': caracteristicas['tipo'],
            'vector_spacy': caracteristicas['vector_spacy']
        }

        return jsonify({
            'mensaje': 'Solicitud procesada correctamente',
            'user_id': user_id,
            'perfil': perfil,
            'servidor_asignado': servidor_id,
            'caracteristicas': caracteristicas_para_respuesta,
            'tiempo_asignacion': tiempo_asignacion,
            'demanda_predicha': float(demanda_predicha),
            'accion_rl': int(accion),
            'recompensa_rl': recompensa
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

@app.route('/num_servidores')
def get_num_servidores():
    global asignador_recursos
    num_servidores = len(asignador_recursos.servidores)
    return jsonify({'num_servidores': num_servidores})

@app.route('/longitud_cola')
def get_longitud_cola():
    global asignador_recursos
    longitud_cola = asignador_recursos.cola_solicitudes.qsize()
    return jsonify({'longitud_cola': longitud_cola})

if __name__ == '__main__':
    app.run(debug=True)