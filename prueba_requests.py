import requests
import time
import random
import threading

url = 'http://127.0.0.1:5000/solicitud'

# Lista de usuarios de ejemplo
users = ["user123", "user456", "user789", "user000", "user111", "user222", "user333", "user444"]

# Tipos de solicitud de ejemplo
request_types = ["simple", "compleja", "codigo"]

# Textos de ejemplo
texts = {
    "simple": ["Consulta general", "Duda sobre el servicio", "Información de contacto", "Horario de atención", "Estado de mi pedido", "Precios y planes", "Soporte técnico", "Hacer una reserva"],
    "compleja": ["Análisis de datos y predicciones", "Solicitud compleja de análisis", "Informe detallado", "Estudio de mercado", "Integración con API", "Desarrollo personalizado", "Consulta de seguridad", "Auditoría de datos"],
    "codigo": ["Ejecución de código Python", "Prueba de script", "Solicitud de API", "Integración de código", "Depuración de código", "Optimización de script", "Revisión de código", "Automatización de tareas"]
}

def send_request():
    """Envía una solicitud a la API."""
    while True:
        user_id = random.choice(users)
        request_type = random.choice(request_types)
        text = random.choice(texts[request_type])

        data = {'user_id': user_id, 'texto': text}

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # Lanza una excepción si la respuesta no es 2xx
            print(f"Solicitud enviada: {data}. Respuesta: {response.status_code} - {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")

        time.sleep(random.uniform(0.5, 2))  # Pausa entre 0.5 y 2 segundos

if __name__ == "__main__":
    # Crear y ejecutar varios hilos
    num_threads = 5  # Puedes ajustar el número de hilos
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=send_request)
        threads.append(thread)
        thread.start()

    # Mantener el script principal en ejecución
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulación finalizada.")