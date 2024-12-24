import requests
import time
import random
import csv
import json

url = 'http://127.0.0.1:5000/solicitud'

users = ["user_basico_1", "user_basico_2", "user_basico_3"]
texts = ["Consulta general", "Duda sobre el servicio", "Información de contacto"]

tiempos_respuesta = []

csv_filename = "datos_simulacion.csv"
csv_headers = [
    "tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud",
    "texto_solicitud", "caracteristicas", "demanda_predicha",
    "servidor_asignado", "tiempo_asignacion", "tiempo_espera"
]

# Escribir encabezados en el archivo CSV
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
    writer.writeheader()

def send_request():
    while True:
        user_id = random.choice(users)
        text = random.choice(texts)
        # Incluir el timestamp en la solicitud
        data = {'user_id': user_id, 'texto': text, 'request_type': 'simple', 'timestamp': time.time()}
        try:
            inicio = time.time()
            response = requests.post(url, json=data)
            response.raise_for_status()
            fin = time.time()
            tiempo_respuesta = fin - inicio
            tiempos_respuesta.append(tiempo_respuesta)

            response_data = response.json()

            # Obtener el tiempo de asignación y la demanda predicha
            tiempo_asignacion = response_data.get('tiempo_asignacion', 0)
            demanda_predicha = response_data.get('demanda_predicha', 0)
            servidor_asignado = response_data.get('servidor_asignado', -1)
            timestamp_llegada = response_data.get('timestamp_llegada', 0)

            # Calcular el tiempo de espera
            tiempo_espera = fin - timestamp_llegada

            # Guardar los datos en el CSV
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writerow({
                    "tiempo_inicio": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(inicio)),
                    "tiempo_fin": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fin)),
                    "user_id": user_id,
                    "tipo_solicitud": 'simple',
                    "texto_solicitud": text,
                    "caracteristicas": json.dumps(response_data.get("caracteristicas", {})),
                    "demanda_predicha": demanda_predicha,
                    "servidor_asignado": servidor_asignado,
                    "tiempo_asignacion": tiempo_asignacion,
                    "tiempo_espera": tiempo_espera
                })

            print(f"Solicitud enviada por {user_id}: {text}. Respuesta: {response.status_code} - {response_data}. Tiempo de respuesta: {tiempo_respuesta:.4f} segundos. Tiempo de espera: {tiempo_espera:.4f} segundos")

        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")

        time.sleep(random.uniform(2, 5))

def calculate_statistics():
    if tiempos_respuesta:
        promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
        maximo = max(tiempos_respuesta)
        minimo = min(tiempos_respuesta)
        print(f"\nEstadísticas de tiempos de respuesta (Usuario Básico):")
        print(f"  Promedio: {promedio:.4f} segundos")
        print(f"  Máximo: {maximo:.4f} segundos")
        print(f"  Mínimo: {minimo:.4f} segundos")
    else:
        print("No se registraron tiempos de respuesta (Usuario Básico).")

if __name__ == "__main__":
    try:
        send_request()
    except KeyboardInterrupt:
        print("Simulación finalizada.")
        calculate_statistics()
        requests.post('http://127.0.0.1:5000/actualizar_perfiles')