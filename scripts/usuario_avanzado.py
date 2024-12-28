import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import time
import random
import csv
import json
from api.analizador_solicitudes import AnalizadorSolicitudes
import numpy as np
# Configuración
url = 'http://127.0.0.1:5000/solicitud'
users = ["user_simulado_1", "user_simulado_2", "user_simulado_3"]
texts = {
    "compleja": ["Análisis avanzado de datos", "Informe de rendimiento personalizado", "Predicciones de mercado", "Optimización de modelo de ML"],
    "codigo": ["Ejecución de código Python complejo", "Automatización de tareas con scripts", "Integración de API avanzada", "Depuración de código"]
}

csv_filename = "datos_simulacion.csv"
csv_headers = [
    "tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud",
    "texto_solicitud", "caracteristicas", "demanda_predicha",
    "servidor_asignado", "tiempo_asignacion", "tiempo_espera"
]

# Instanciar el analizador de solicitudes
analizador = AnalizadorSolicitudes()

# Crear archivo CSV si no existe
def crear_csv():
    try:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()
    except Exception as e:
        print(f"Error al crear el archivo CSV: {e}")

# Enviar solicitudes simuladas
def send_request():
    while True:
        try:
            user_id = random.choice(users)
            request_type = random.choices(["compleja", "codigo"], weights=[0.6, 0.4])[0]
            text = random.choice(texts[request_type])

            # Analizar características
            caracteristicas = analizador.analizar(text)


            # Si caracteristicas contiene un array de NumPy, conviértelo a lista
            if isinstance(caracteristicas.get("vector_spacy"), np.ndarray):
                caracteristicas["vector_spacy"] = caracteristicas["vector_spacy"].tolist()
            print(caracteristicas)
            if isinstance(caracteristicas.get("vector_tfidf"), np.ndarray):
                caracteristicas["vector_tfidf"] = caracteristicas["vector_tfidf"].tolist()
            # print("Datos enviados:", json.dumps(data, indent=2))
            # Datos iniciales
            data = {
                'user_id': user_id,
                'texto': text,
                'request_type': request_type,
                'caracteristicas': caracteristicas
            }

            # Enviar la solicitud
            inicio = time.time()
            response = requests.post(url, json=data)
            response.raise_for_status()
            fin = time.time()

            # Procesar la respuesta
            response_data = response.json()

            # Obtener datos relevantes de la respuesta
            tiempo_asignacion = response_data.get('tiempo_asignacion', 0)
            demanda_predicha = float(response_data.get('demanda_predicha', 0))
            servidor_asignado = response_data.get('servidor_asignado', -1)
            caracteristicas_respuesta = response_data.get("caracteristicas", {})

            # Calcular el tiempo de espera
            tiempo_espera = fin - inicio

            # Guardar los datos en el CSV
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writerow({
                    "tiempo_inicio": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(inicio)),
                    "tiempo_fin": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fin)),
                    "user_id": user_id,
                    "tipo_solicitud": request_type,
                    "texto_solicitud": text,
                    "caracteristicas": json.dumps(caracteristicas_respuesta),
                    "demanda_predicha": demanda_predicha,
                    "servidor_asignado": servidor_asignado,
                    "tiempo_asignacion": tiempo_asignacion,
                    "tiempo_espera": tiempo_espera
                })

            print(f"Solicitud enviada por {user_id} ({request_type}): {text}. Respuesta: {response.status_code} - {response_data}. Tiempo de respuesta: {tiempo_espera:.4f} segundos")

        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")

        time.sleep(random.uniform(0.5, 1.5))

# Calcular estadísticas
def calculate_statistics():
    try:
        tiempos_respuesta = []
        with open(csv_filename, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tiempos_respuesta.append(float(row['tiempo_espera']))

        if tiempos_respuesta:
            promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
            maximo = max(tiempos_respuesta)
            minimo = min(tiempos_respuesta)

            print("\nEstadísticas de tiempos de respuesta:")
            print(f"  Promedio: {promedio:.4f} segundos")
            print(f"  Máximo: {maximo:.4f} segundos")
            print(f"  Mínimo: {minimo:.4f} segundos")
        else:
            print("No se registraron tiempos de respuesta.")

    except Exception as e:
        print(f"Error al calcular estadísticas: {e}")

if __name__ == "__main__":
    try:
        crear_csv()
        send_request()
    except KeyboardInterrupt:
        print("Simulación finalizada.")
        calculate_statistics()
