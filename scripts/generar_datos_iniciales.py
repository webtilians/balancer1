import random
import time
import csv
import json
import numpy as np

def generar_datos_iniciales(num_filas, nombre_archivo="datos_simulacion_inicial.csv"):
    """
    Genera un archivo CSV con datos de simulación iniciales, incluyendo vectores aleatorios.
    """
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["tiempo_inicio", "tiempo_fin", "user_id", "tipo_solicitud", "texto_solicitud", "caracteristicas", "demanda_predicha", "servidor_asignado", "tiempo_asignacion", "tiempo_espera"])

        for i in range(num_filas):
            tiempo_inicio = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - random.randint(0, 3600)))
            tiempo_fin = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - random.randint(0, 60)))

            user_id = f"user_inicial_{random.randint(1, 100)}"
            tipo_solicitud = random.choice(["simple", "compleja", "codigo"])
            texto_solicitud = f"Solicitud inicial de tipo {tipo_solicitud} - {i}"

            # Generar un vector ficticio para 'vector_w2v'
            vector_w2v = np.random.rand(100).tolist()  # Vector aleatorio de 100 dimensiones

            caracteristicas = {
                "longitud": random.randint(10, 150),
                "tipo": tipo_solicitud,
                "vector_w2v": vector_w2v
            }

            demanda_predicha = random.uniform(0.5, 5.0)
            if tipo_solicitud == "simple":
                demanda_predicha = random.uniform(0.5, 2.0)
            elif tipo_solicitud == "compleja":
                demanda_predicha = random.uniform(2.0, 4.0)
            elif tipo_solicitud == "codigo":
                demanda_predicha = random.uniform(3.0, 5.0)

            servidor_asignado = -1  # Valor ficticio
            tiempo_asignacion = 0.0  # Valor ficticio
            tiempo_espera = 0.0  # Valor ficticio

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
    generar_datos_iniciales(1500)  # Generar 1500 filas de datos iniciales
    print(f"Archivo 'datos_simulacion_inicial.csv' generado con éxito.")