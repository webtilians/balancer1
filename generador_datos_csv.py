import csv
import random
import time
import json

def generar_datos_csv(num_filas, nombre_archivo="datos_simulacion.csv"):
    """
    Genera un archivo CSV con datos de simulación.

    Args:
        num_filas (int): El número de filas de datos a generar.
        nombre_archivo (str): El nombre del archivo CSV de salida.
    """

    usuarios = ["user_basico_" + str(i) for i in range(1, 6)] + \
              ["user_intermedio_" + str(i) for i in range(1, 6)] + \
              ["user_avanzado_" + str(i) for i in range(1, 6)]

    tipos_solicitud = ["simple", "compleja", "codigo"]

    textos = {
        "simple": ["Consulta general", "Duda sobre el servicio", "Información de contacto"],
        "compleja": ["Análisis de datos", "Informe de uso", "Solicitud de integración"],
        "codigo": ["Ejecución de script", "Prueba de API", "Depuración de código"]
    }

    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud", "texto_solicitud", "caracteristicas", "demanda_predicha", "servidor_asignado", "tiempo_asignacion", "tiempo_espera"])

        for i in range(num_filas):
            tiempo_inicio = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - random.randint(0, 3600)))  # Simular datos de la última hora
            tiempo_fin = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - random.randint(0, 60)))
            user_id = random.choice(usuarios)
            tipo_solicitud = random.choice(tipos_solicitud)
            texto_solicitud = random.choice(textos[tipo_solicitud])

            caracteristicas = {
                "longitud": random.randint(10, 150),
                "tipo": tipo_solicitud
            }

            demanda_predicha = random.uniform(0.5, 5.0)  # Simular demanda predicha
            if tipo_solicitud == "simple":
                demanda_predicha = random.uniform(0.5, 2.0)
            elif tipo_solicitud == "compleja":
                demanda_predicha = random.uniform(2.0, 4.0)
            elif tipo_solicitud == "codigo":
                demanda_predicha = random.uniform(3.0, 5.0)

            servidor_asignado = random.randint(0, 5)  # Simular asignación a un servidor
            tiempo_asignacion = random.uniform(0.01, 0.1)  # Simular tiempo de asignación
            tiempo_espera = random.uniform(0.0, 0.5)  # Simular tiempo de espera en la cola

            writer.writerow([
                tiempo_inicio,
                tiempo_fin,
                user_id,
                tipo_solicitud,
                texto_solicitud,
                json.dumps(caracteristicas),
                demanda_predicha,
                servidor_asignado,
                tiempo_asignacion,
                tiempo_espera
            ])

if __name__ == "__main__":
    generar_datos_csv(1000)
    print(f"Archivo '{'datos_fake'}' generado con éxito.")