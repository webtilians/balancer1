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
import pandas as pd
import os
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
    
@router.get("/monitoreo")
async def monitoreo():
    try:
        # Lee el archivo de simulación
        data = pd.read_csv("scripts/datos_simulacion.csv")

        # Calcula estadísticas clave
        latencia_promedio = data['latencia_calculada'].mean()
        latencia_maxima = data['latencia_calculada'].max()
        latencia_minima = data['latencia_calculada'].min()
        demanda_promedio = data['demanda_predicha'].mean()

        return {
            "latencia_promedio": round(latencia_promedio, 2),
            "latencia_maxima": round(latencia_maxima, 2),
            "latencia_minima": round(latencia_minima, 2),
            "demanda_promedio": round(demanda_promedio, 2),
        }
    except Exception as e:
        return {"error": str(e)}
    
# Archivos de datos
data_file_basicos = "scripts/datos_usuario_basico.csv"
data_file_avanzados = "scripts/datos_usuario_avanzado.csv"    
    
@router.get("/metrics")
def get_metrics():
    try:
        response = {}

        # Usuarios Básicos
        if os.path.exists(data_file_basicos):
            data_basicos = pd.read_csv(data_file_basicos)
            total_requests_basicos = len(data_basicos)
            avg_latency_basicos = data_basicos["latencia_calculada"].mean() if "latencia_calculada" in data_basicos else None
            avg_predicted_demand_basicos = data_basicos["demanda_predicha"].mean() if "demanda_predicha" in data_basicos else None
            last_20_basicos = data_basicos.tail(20).to_dict(orient="records")

            response["usuarios_basicos"] = {
                "total_requests": total_requests_basicos,
                "average_latency": avg_latency_basicos,
                "average_predicted_demand": avg_predicted_demand_basicos,
                "last_requests": last_20_basicos,
            }
        else:
            response["usuarios_basicos"] = {"error": "Archivo de usuarios básicos no encontrado."}

        # Usuarios Avanzados
        if os.path.exists(data_file_avanzados):
            data_avanzados = pd.read_csv(data_file_avanzados)
            total_requests_avanzados = len(data_avanzados)
            avg_latency_avanzados = data_avanzados["latencia_calculada"].mean() if "latencia_calculada" in data_avanzados else None
            avg_predicted_demand_avanzados = data_avanzados["demanda_predicha"].mean() if "demanda_predicha" in data_avanzados else None
            last_20_avanzados = data_avanzados.tail(20).to_dict(orient="records")

            response["usuarios_avanzados"] = {
                "total_requests": total_requests_avanzados,
                "average_latency": avg_latency_avanzados,
                "average_predicted_demand": avg_predicted_demand_avanzados,
                "last_requests": last_20_avanzados,
            }
        else:
            response["usuarios_avanzados"] = {"error": "Archivo de usuarios avanzados no encontrado."}

        return jsonify(content=response)
    except Exception as e:
        return jsonify(content={"error": str(e)}, status_code=500)    

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