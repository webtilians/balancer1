from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse as jsonify
from pydantic import BaseModel
from typing import Dict
from models.demand_predictor import DemandPredictor
from api.gestor_usuarios import  GestorUsuarios
from api.analizador_solicitudes import AnalizadorSolicitudes
import time
import json
from config import asignador_recursos

# Crear un router para manejar las rutas
router = APIRouter()

@router.post('/solicitud')
async def procesar_solicitud(request: Request):
    try:
        data =await request.json()

        # Validar la entrada
        if not data or 'user_id' not in data or 'texto' not in data:
            return jsonify({'error': 'Datos de solicitud no válidos'}), 400

        user_id = data['user_id']
        texto_solicitud = data['texto']

        # Analizar la solicitud
        analizador=AnalizadorSolicitudes()
        caracteristicas = analizador.analizar(texto_solicitud)

        # Registrar la solicitud en el historial del usuario
        gestorUsuarios=GestorUsuarios()
        gestorUsuarios.registrar_solicitud(user_id, caracteristicas)

        # Obtener el perfil del usuario
        perfil = gestorUsuarios.obtener_perfil(user_id)

        # Registrar el tiempo de inicio
        inicio = time.time()

        # Obtener la predicción de la demanda (si el modelo está disponible)
        # asignador_recursos = AsignadorRecursos(num_servidores_inicial=1, demand_predictor=DemandPredictor)
        if isinstance(caracteristicas, dict):
            demanda_predicha = asignador_recursos.demand_predictor.predict(caracteristicas)
        else:
            raise ValueError("Caracteristicas no es un diccionario válido")


        # Asignar la solicitud a un servidor (sin usar RL, solo encolar)
        servidor_id = asignador_recursos.asignar(user_id, caracteristicas)

        # Registrar el tiempo de finalización
        fin = time.time()

        # Calcular el tiempo de asignación
        tiempo_asignacion = fin - inicio

        # Actualizar el perfil del usuario basado en su historial
        gestorUsuarios=GestorUsuarios()
        gestorUsuarios.actualizar_perfil(user_id)

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
@router.post('/actualizar_perfiles')
def actualizar_perfiles():
    try:
        GestorUsuarios.actualizar_perfiles()
        return jsonify({'mensaje': 'Perfiles de usuario actualizados correctamente'}), 200
    except Exception as e:
        print(f"Error al actualizar perfiles: {e}")
        return jsonify({'error': 'Error interno del servidor al actualizar perfiles'}), 500

@router.get('/num_servidores')
def get_num_servidores():
    global AsignadorRecursos
    num_servidores = len(AsignadorRecursos.servidores)
    return jsonify({'num_servidores': num_servidores})

@router.get('/longitud_cola')
def get_longitud_cola():
    global asignador_recursos
    longitud_cola = asignador_recursos.cola_solicitudes.qsize()
    return jsonify({'longitud_cola': longitud_cola})