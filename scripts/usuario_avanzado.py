import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import time
import random
import csv
import json
from api.analizador_solicitudes import AnalizadorSolicitudes

# Configuración
url = 'http://127.0.0.1:8000/solicitud'
users = ["user_simulado_1", "user_simulado_2", "user_simulado_3"]
texts = {
    "compleja": ["Análisis avanzado de datos", "Informe de rendimiento personalizado", "Predicciones de mercado", "Optimización de modelo de ML"],
    "codigo": ["Ejecución de código Python complejo", "Automatización de tareas con scripts", "Integración de API avanzada", "Depuración de código"]
}

csv_filename = "datos_simulacion.csv"
csv_headers = [
    "tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud",
    "texto_solicitud", "caracteristicas", "demanda_predicha",
    "servidor_asignado", "tiempo_asignacion", "tiempo_espera", "latencia_calculada"
]

# Instanciar el analizador de solicitudes
analizador = AnalizadorSolicitudes()

tiempos_respuesta = []

# Crear archivo CSV si no existe
def crear_csv():
    try:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()
    except Exception as e:
        print(f"Error al crear el archivo CSV: {e}")

# Enviar solicitudes simuladas
def send_request(csv_writer):
    while True:
        user_id = random.choice(users)
        request_type = random.choices(["compleja", "codigo"], weights=[0.6, 0.4])[0]
        text = random.choice(texts[request_type])

        caracteristicas = analizador.analizar(text)

        data = {'user_id': user_id, 'texto': text, 'request_type': request_type, 'caracteristicas': caracteristicas}
        try:
            inicio = time.time()
            response = requests.post(url, json=data)
            response.raise_for_status()
            fin = time.time()
            
            tiempo_respuesta = fin - inicio
            tiempos_respuesta.append(tiempo_respuesta)

            response_data = response.json()

            tiempo_asignacion = response_data[0].get('tiempo_asignacion', 0)
            demanda_predicha = float(response_data[0].get('demanda_predicha', 0))
            servidor_asignado = response_data[0].get('servidor_asignado', -1)

            latencia_calculada = fin - inicio  # Cálculo directo de la latencia

            csv_writer.writerow({
                "tiempo_inicio": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(inicio)),
                "tiempo_fin": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fin)),
                "user_id": user_id,
                "tipo_solicitud": request_type,
                "texto_solicitud": text,
                "caracteristicas": json.dumps(caracteristicas),
                "demanda_predicha": demanda_predicha,
                "servidor_asignado": servidor_asignado,
                "tiempo_asignacion": tiempo_asignacion,
                "tiempo_espera": 0,
                "latencia_calculada": latencia_calculada
            })

            print(f"Solicitud enviada por {user_id} ({request_type}): {text}. Respuesta: {response.status_code} - {response_data}. Latencia: {latencia_calculada:.4f} segundos")

        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
            if isinstance(e, requests.exceptions.ConnectionError):
                print("Error de conexión: Asegúrate de que el servidor Flask esté corriendo.")
            elif isinstance(e, requests.exceptions.Timeout):
                print("Tiempo de espera agotado al enviar la solicitud.")
            elif isinstance(e, requests.exceptions.HTTPError):
                print(f"Error HTTP: {e.response.status_code} - {e.response.text}")
            else:
                print(f"Error desconocido al enviar la solicitud: {e}")

        time.sleep(random.uniform(0.5, 1.5))

# Calcular estadísticas
def calculate_statistics():
    try:
        tiempos_respuesta = []
        with open(csv_filename, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['latencia_calculada']:
                    tiempos_respuesta.append(float(row['latencia_calculada']))

        if tiempos_respuesta:
            promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
            maximo = max(tiempos_respuesta)
            minimo = min(tiempos_respuesta)

            print("\nEstadísticas de latencias:")
            print(f"  Promedio: {promedio:.4f} segundos")
            print(f"  Máximo: {maximo:.4f} segundos")
            print(f"  Mínimo: {minimo:.4f} segundos")
        else:
            print("No se registraron latencias calculadas.")

    except Exception as e:
        print(f"Error al calcular estadísticas: {e}")

if __name__ == "__main__":
    try:
        with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            if csvfile.tell() == 0:
                writer.writeheader()
            send_request(writer)
    except KeyboardInterrupt:
        print("Simulación finalizada.")
        calculate_statistics()
        requests.post('http://127.0.0.1:8000/actualizar_perfiles')
