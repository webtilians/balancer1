import pandas as pd
from glob import glob

# Lista de archivos a combinar
archivos_csv = ["datos_simulacion.csv"]

# Lista para almacenar los DataFrames
dfs = []

for archivo in archivos_csv:
    df = pd.read_csv(archivo)
    # Convertir las columnas de tiempo
    df['tiempo_inicio'] = pd.to_datetime(df['tiempo_inicio'])
    df['tiempo_fin'] = pd.to_datetime(df['tiempo_fin'])
    # Calcular latencia
    df['latencia_calculada'] = (df['tiempo_fin'] - df['tiempo_inicio']).dt.total_seconds()
    dfs.append(df)

# Combinar todos los DataFrames
datos_combinados = pd.concat(dfs, ignore_index=True)

# Guardar el archivo combinado
ruta_combinada = "datos_entrenamiento.csv"
datos_combinados.to_csv(ruta_combinada, index=False)

print(f"Archivo combinado guardado en {ruta_combinada}")
