from flask import Blueprint, request, jsonify

from . import analizador_solicitudes, gestor_usuarios
from .. import asignador_recursos
import time
import json

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/solicitud', methods=['POST'])
def procesar_solicitud():
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

        # Obtener la predicción de la demanda (si el modelo está disponible)
        try:
            demanda_predicha = asignador_recursos.demand_predictor.predict(caracteristicas)
        except Exception as e:
            print(f"Error al predecir la demanda: {e}")
            demanda_predicha = 0.0  # Valor por defecto en caso de error

        # Asignar la solicitud a un servidor (sin usar RL, solo encolar)
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
            'vector_spacy': caracteristicas['vector_spacy']
        }

        return jsonify({
            'mensaje': 'Solicitud procesada correctamente',
            'user_id': user_id,
            'perfil': perfil,
            'servidor_asignado': servidor_id,
            'caracteristicas': caracteristicas_para_respuesta,
            'tiempo_asignacion': tiempo_asignacion,
            'demanda_predicha': float(demanda_predicha)
        }), 200

    except Exception as e:
        print(f"Error al procesar la solicitud: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Nueva ruta para actualizar todos los perfiles
@api_routes.route('/actualizar_perfiles', methods=['POST'])
def actualizar_perfiles():
    try:
        gestor_usuarios.actualizar_perfiles()
        return jsonify({'mensaje': 'Perfiles de usuario actualizados correctamente'}), 200
    except Exception as e:
        print(f"Error al actualizar perfiles: {e}")
        return jsonify({'error': 'Error interno del servidor al actualizar perfiles'}), 500

@api_routes.route('/num_servidores')
def get_num_servidores():
    global asignador_recursos
    num_servidores = len(asignador_recursos.servidores)
    return jsonify({'num_servidores': num_servidores})

@api_routes.route('/longitud_cola')
def get_longitud_cola():
    global asignador_recursos
    longitud_cola = asignador_recursos.cola_solicitudes.qsize()
    return jsonify({'longitud_cola': longitud_cola})