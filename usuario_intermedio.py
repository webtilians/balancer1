import requests
import time
import random
import csv
import json

url = 'http://127.0.0.1:5000/solicitud'

users = ["user_intermedio_1", "user_intermedio_2", "user_intermedio_3"]  # Usuarios intermedios
texts = {
    "simple": ["Consulta sobre mi plan", "Duda sobre la factura", "Cambiar mi suscripción"],
    "compleja": ["Análisis de datos de mi cuenta", "Informe de uso del último mes", "Solicitud de integración con API"],
    "codigo": ["Ejecución de script simple", "Prueba de API"]  # Ocasionalmente ejecutan código
}

tiempos_respuesta = []

csv_filename = "datos_simulacion.csv"
csv_headers = [
    "tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud",
    "texto_solicitud", "caracteristicas", "demanda_predicha",
    "servidor_asignado", "tiempo_asignacion", "tiempo_espera"
]

def send_request():
    while True:
        user_id = random.choice(users)
        request_type = random.choices(["simple", "compleja", "codigo"], weights=[0.4, 0.4, 0.2])[0]
        text = random.choice(texts[request_type])
        data = {'user_id': user_id, 'texto': text, 'request_type': request_type}
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
            timestamp_llegada = response_data.get('timestamp_llegada', 0)
            
            # Calcular el tiempo de espera
            tiempo_espera = fin - timestamp_llegada

            # Asegurar que la demanda predicha sea un float
            if demanda_predicha is None:
                print(f"Advertencia: 'demanda_predicha' es None. Usando 0.0 por defecto.")
                demanda_predicha = 0.0
            else:
                demanda_predicha = float(demanda_predicha)

            # Guardar los datos en el CSV
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writerow({
                    "tiempo_inicio": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(inicio)),
                    "tiempo_fin": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fin)),
                    "user_id": user_id,
                    "tipo_solicitud": request_type,
                    "texto_solicitud": text,
                    "caracteristicas": json.dumps(response_data.get("caracteristicas", {})),
                    "demanda_predicha": demanda_predicha,
                    "servidor_asignado": response_data.get("servidor_asignado", -1),
                    "tiempo_asignacion": tiempo_asignacion,
                    "tiempo_espera": tiempo_espera  # Podrías calcular esto si es necesario
                })

            print(f"Solicitud enviada por {user_id} ({request_type}): {text}. Respuesta: {response.status_code} - {response_data}. Tiempo de respuesta: {tiempo_respuesta:.4f} segundos")

        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")

        time.sleep(random.uniform(1, 3))

def calculate_statistics():
    if tiempos_respuesta:
        promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
        maximo = max(tiempos_respuesta)
        minimo = min(tiempos_respuesta)
        print(f"\nEstadísticas de tiempos de respuesta (Usuario Intermedio):")
        print(f"  Promedio: {promedio:.4f} segundos")
        print(f"  Máximo: {maximo:.4f} segundos")
        print(f"  Mínimo: {minimo:.4f} segundos")
    else:
        print("No se registraron tiempos de respuesta (Usuario Intermedio).")

if __name__ == "__main__":
    try:
        send_request()
    except KeyboardInterrupt:
        print("Simulación finalizada.")
        calculate_statistics()
        requests.post('http://127.0.0.1:5000/actualizar_perfiles')