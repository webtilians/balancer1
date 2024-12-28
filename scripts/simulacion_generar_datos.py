import time
import random
import csv
import json
import numpy as np

def simular_solicitud():
    """
    Simula una solicitud de usuario generando datos aleatorios.
    """
    user_id = f"user_simulado_{random.randint(1, 100)}"
    tipo_solicitud = random.choice(["simple", "compleja", "codigo"])
    texto_solicitud = f"Solicitud simulada de tipo {tipo_solicitud}"

    caracteristicas = {
        "longitud": random.randint(10, 150),
        "tipo": tipo_solicitud,
        "vector_spacy": np.random.rand(300).tolist()  # Vector aleatorio de 300 dimensiones
    }

    # Simular la demanda predicha (sin usar el modelo real)
    demanda_predicha = random.uniform(0.5, 5.0)
    if tipo_solicitud == "simple":
        demanda_predicha = random.uniform(0.5, 2.0)
    elif tipo_solicitud == "compleja":
        demanda_predicha = random.uniform(2.0, 4.0)
    elif tipo_solicitud == "codigo":
        demanda_predicha = random.uniform(3.0, 5.0)

    return user_id, tipo_solicitud, texto_solicitud, caracteristicas, demanda_predicha

def generar_datos_simulacion(num_filas, nombre_archivo="datos_simulacion.csv"):
    """
    Genera un archivo CSV con datos de simulación de solicitudes de usuarios.
    """
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud", "texto_solicitud", "caracteristicas", "demanda_predicha", "servidor_asignado", "tiempo_asignacion", "tiempo_espera"])

        for i in range(num_filas):
            tiempo_inicio = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - random.randint(0, 3600)))  # Simular datos de la última hora
            tiempo_fin = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - random.randint(0, 60)))

            user_id, tipo_solicitud, texto_solicitud, caracteristicas, demanda_predicha = simular_solicitud()

            writer.writerow([
                tiempo_inicio,
                tiempo_fin,
                user_id,
                tipo_solicitud,
                texto_solicitud,
                json.dumps(caracteristicas),
                demanda_predicha,
                -1,  # servidor_asignado ficticio
                0.0,  # tiempo_asignacion ficticio
                0.0   # tiempo_espera ficticio
            ])

if __name__ == "__main__":
    generar_datos_simulacion(2000)  # Generar 2000 filas de datos iniciales
    print(f"Archivo 'datos_simulacion.csv' generado con éxito.")