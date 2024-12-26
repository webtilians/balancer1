import random
import pandas as pd
import datetime

# Definir usuarios y sus niveles
usuarios = {
    "user_basico_1": 0,
    "user_basico_2": 0,
    "user_intermedio_1": 1,
    "user_intermedio_2": 1,
    "user_avanzado_1": 2,
    "user_avanzado_2": 2,
}

# Definir tipos de solicitudes y ejemplos de texto
tipos_solicitud = {
    "simple": [
        "Consulta rápida sobre el estado del servidor.",
        "Solicitud de información básica.",
        "Petición de datos de uso recientes."
    ],
    "compleja": [
        "Análisis detallado de rendimiento.",
        "Generación de informes semanales.",
        "Evaluación de métricas avanzadas."
    ],
    "codigo": [
        "Ejecución de script Python para análisis.",
        "Compilación de código fuente.",
        "Despliegue de aplicación en entorno de prueba."
    ]
}

# Definir las cabeceras explícitamente
CABECERAS = [
    "user_id",
    "nivel_usuario",
    "longitud",
    "tipo_simple",
    "tipo_compleja",
    "tipo_codigo",
    "latencia_historica",
    "texto_solicitud",
    "demanda_predicha",
    "tiempo_inicio",
    "tiempo_fin",
    "tiempo_respuesta"
]

def generar_datos_simulados(num_datos=1000):
    """
    Genera un conjunto de datos simulados con las columnas necesarias.

    Args:
        num_datos (int): Número de datos a generar.

    Returns:
        DataFrame con datos simulados.
    """
    datos = []

    for _ in range(num_datos):
        # Información básica del usuario
        user_id = random.choice(list(usuarios.keys()))
        nivel_usuario = usuarios[user_id]
        
        # Información de la solicitud
        tipo = random.choice(list(tipos_solicitud.keys()))
        texto_solicitud = random.choice(tipos_solicitud[tipo])
        longitud = len(texto_solicitud.split())
        latencia_historica = random.uniform(0.1, 1.0)  # Simulación de latencia histórica

        # Codificar tipo de solicitud como one-hot
        tipo_simple = 1 if tipo == "simple" else 0
        tipo_compleja = 1 if tipo == "compleja" else 0
        tipo_codigo = 1 if tipo == "codigo" else 0

        # Generar la demanda objetivo simulada
        demanda = (
            longitud * 0.02 +
            tipo_compleja * 5 +
            tipo_codigo * 10 +
            latencia_historica * 3 +
            nivel_usuario * 2 +
            random.uniform(-3, 3)  # Ruido aleatorio
        )
        demanda = max(0, demanda)  # Asegurarse de que la demanda sea positiva

        # Métricas de tiempo
        tiempo_inicio = datetime.datetime.now()
        tiempo_respuesta = random.uniform(0.1, 2.0)  # Simular tiempos de respuesta entre 0.1 y 2 segundos
        tiempo_fin = tiempo_inicio + datetime.timedelta(seconds=tiempo_respuesta)

        # Crear una fila de datos
        fila = [
            user_id,
            nivel_usuario,
            longitud,
            tipo_simple,
            tipo_compleja,
            tipo_codigo,
            latencia_historica,
            texto_solicitud,
            demanda,
            tiempo_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            tiempo_fin.strftime("%Y-%m-%d %H:%M:%S"),
            tiempo_respuesta
        ]
        datos.append(fila)

    # Crear el DataFrame con las cabeceras
    df = pd.DataFrame(datos, columns=CABECERAS)
    return df

if __name__ == "__main__":
    # Generar datos y guardar en CSV con headers
    datos_simulados = generar_datos_simulados(num_datos=1000)
    datos_simulados.to_csv("datos_simulados.csv", index=False)
    print("Datos simulados guardados en 'datos_simulados.csv' con headers.")
