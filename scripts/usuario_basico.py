import requests
import time
import random
import csv
import json

url = 'http://127.0.0.1:5000/solicitud'

# Lista de usuarios básicos y mensajes predefinidos
users = ["user_basico_1", "user_basico_2", "user_basico_3"]
texts = ["Consulta general", "Duda sobre el servicio", "Información de contacto"]

# Archivo CSV para registrar las simulaciones
csv_filename = "datos_usuario_basico.csv"
csv_headers = [
    "tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud",
    "texto_solicitud", "respuesta_servidor", "tiempo_respuesta"
]

# Inicializar el archivo CSV con encabezados
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
    writer.writeheader()

def send_request():
    while True:
        user_id = random.choice(users)
        text = random.choice(texts)
        
        # Estructura mínima del JSON
        data = {
            'user_id': user_id,
            'texto': text,
            'request_type': 'basic',
            'timestamp': time.time()
        }
        
        try:
            inicio = time.time()
            response = requests.post(url, json=data)
            response.raise_for_status()  # Lanza excepción si el código HTTP no es 200
            fin = time.time()
            
            tiempo_respuesta = fin - inicio
            response_data = response.json()  # Convertir la respuesta a JSON
            
            # Guardar resultados en el archivo CSV
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writerow({
                    "tiempo_inicio": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(inicio)),
                    "tiempo_fin": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fin)),
                    "user_id": user_id,
                    "tipo_solicitud": 'basic',
                    "texto_solicitud": text,
                    "respuesta_servidor": json.dumps(response_data),
                    "tiempo_respuesta": tiempo_respuesta
                })
            
            print(f"[{user_id}] Solicitud enviada: {text}. Respuesta: {response.status_code}. Tiempo: {tiempo_respuesta:.4f}s")
        
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
        
        # Pausa entre solicitudes
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    try:
        send_request()
    except KeyboardInterrupt:
        print("Simulación terminada. Revisa el archivo CSV para los detalles.")
