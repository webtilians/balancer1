import requests
import time
import random
import threading
import csv
import json

url = 'http://127.0.0.1:8000/solicitud'

# Tipos de solicitud de ejemplo
request_types = ["simple", "compleja", "codigo"]

# Textos de ejemplo (más variados)
texts = {
    "simple": [
        "Consulta general", "Duda sobre el servicio", "Información de contacto",
        "Horario de atención", "Estado de mi pedido", "Precios y planes",
        "Soporte técnico", "Hacer una reserva", "Cancelar mi suscripción",
        "Actualizar mi perfil", "Cambiar contraseña", "Añadir método de pago",
        "Eliminar método de pago", "Consultar saldo", "Ver historial de transacciones",
        "Descargar factura", "Solicitar ayuda", "Preguntas frecuentes",
        "Reportar un problema", "Dar feedback"
    ],
    "compleja": [
        "Análisis de datos y predicciones", "Solicitud compleja de análisis",
        "Informe detallado", "Estudio de mercado", "Integración con API",
        "Desarrollo personalizado", "Consulta de seguridad", "Auditoría de datos",
        "Optimización de rendimiento", "Análisis de logs", "Prueba de carga",
        "Simulación de escenarios", "Generar reporte de usuarios", "Exportar datos",
        "Importar datos", "Configurar webhook", "Obtener estadísticas de uso",
        "Análisis de sentimiento", "Resumen de texto"
    ],
    "codigo": [
        "Ejecución de código Python", "Prueba de script", "Solicitud de API",
        "Integración de código", "Depuración de código", "Optimización de script",
        "Revisión de código", "Automatización de tareas", "Ejecutar pruebas unitarias",
        "Desplegar aplicación", "Reiniciar servidor", "Crear usuario",
        "Eliminar usuario", "Actualizar permisos", "Ejecutar script de migración",
        "Configurar entorno de desarrollo", "Instalar dependencias", "Compilar código"
    ]
}

csv_filename = "datos_simulacion.csv"
csv_headers = [
    "tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud",
    "texto_solicitud", "caracteristicas", "demanda_predicha",
    "servidor_asignado", "tiempo_asignacion", "tiempo_espera"
]

def send_request(user_id):
    """Envía una solicitud a la API."""
    while True:
        request_type = random.choice(request_types)
        text = random.choice(texts[request_type])

        # Generar características aleatorias para la solicitud
        caracteristicas = {
            'longitud': random.randint(10, 150),  # Longitud variable
            'tipo': request_type
        }

        data = {'user_id': user_id, 'texto': text, 'request_type': request_type}

        try:
            inicio = time.time()
            response = requests.post(url, json=data)
            response.raise_for_status()
            fin = time.time()
            tiempo_respuesta = fin - inicio

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
                    "tiempo_espera": tiempo_espera
                })

            print(f"Solicitud enviada por {user_id}: {text}. Respuesta: {response.status_code} - {response_data}. Tiempo de respuesta: {tiempo_respuesta:.4f} segundos")

        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")

        time.sleep(random.uniform(0.7, 1.5))  # Pausa más corta para generar más carga

if __name__ == "__main__":
    num_threads = 5

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=send_request, args=(f"generador_{i}",))
        threads.append(thread)
        thread.start()

    # Mantener el script principal en ejecución
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulación finalizada.")
        requests.post('http://127.0.0.1:5000/actualizar_perfiles')