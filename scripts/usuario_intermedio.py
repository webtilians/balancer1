import requests
import time
import random
import csv
import json

url = 'http://127.0.0.1:5000/solicitud'

users = ["user_medio_1", "user_medio_2", "user_medio_3"]  # Usuarios medios
texts = {
    "simple": ["Consultar saldo", "Verificar mi plan", "Solicitar soporte"],
    "compleja": ["Revisar historial de pagos", "Actualizar método de pago", "Informar problema técnico"],
    "codigo": ["Ejecutar validación básica", "Probar funcionalidad de API"]  # Mucho menos frecuente
}

tiempos_respuesta = []

csv_filename = "datos_simulacion_usuario_medio.csv"
csv_headers = [
    "tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud",
    "texto_solicitud", "demanda_predicha", "servidor_asignado",
    "tiempo_asignacion", "tiempo_espera"
]

def send_request():
    while True:
        user_id = random.choice(users)
        request_type = random.choices(["simple", "compleja", "codigo"], weights=[0.6, 0.35, 0.05])[0]  # Ajustar pesos
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
            demanda_predicha = float(demanda_predicha) if demanda_predicha else 0.0

            # Guardar los datos en el CSV
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writerow({
                    "tiempo_inicio": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(inicio)),
                    "tiempo_fin": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fin)),
                    "user_id": user_id,
                    "tipo_solicitud": request_type,
                    "texto_solicitud": text,
                    "demanda_predicha": demanda_predicha,
                    "servidor_asignado": response_data.get("servidor_asignado", -1),
                    "tiempo_asignacion": tiempo_asignacion,
                    "tiempo_espera": tiempo_espera
                })

            print(f"Solicitud enviada por {user_id} ({request_type}): {text}. Respuesta: {response.status_code} - {response_data}. Tiempo de respuesta: {tiempo_respuesta:.4f} segundos")

        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")

        time.sleep(random.uniform(1, 5))  # Mayor intervalo entre solicitudes

def calculate_statistics():
    if tiempos_respuesta:
        promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
        maximo = max(tiempos_respuesta)
        minimo = min(tiempos_respuesta)
        print(f"\nEstadísticas de tiempos de respuesta (Usuario Medio):")
        print(f"  Promedio: {promedio:.4f} segundos")
        print(f"  Máximo: {maximo:.4f} segundos")
        print(f"  Mínimo: {minimo:.4f} segundos")
    else:
        print("No se registraron tiempos de respuesta (Usuario Medio).")

if __name__ == "__main__":
    try:
        send_request()
    except KeyboardInterrupt:
        print("Simulación finalizada.")
        calculate_statistics()
        requests.post('http://127.0.0.1:5000/actualizar_perfiles')
