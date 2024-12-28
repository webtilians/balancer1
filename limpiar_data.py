import pandas as pd
import json

# Cargar el archivo CSV
ruta_csv = "data/datos_simulacion.csv"
df = pd.read_csv(ruta_csv)

# Verificar las últimas filas
print(df.tail())

# Verificar si hay valores nulos
print("Valores nulos por columna:")
print(df.isnull().sum())

# Validar el formato de la columna 'caracteristicas'
def validar_caracteristicas(caracteristica):
    try:
        # Intentar cargar el JSON
        json.loads(caracteristica.replace("'", '"'))
        return True
    except Exception as e:
        print(f"Error en la fila con caracteristica: {caracteristica}, Error: {e}")
        return False

df['caracteristicas_validas'] = df['caracteristicas'].apply(validar_caracteristicas)

# Mostrar filas con características inválidas
invalidas = df[~df['caracteristicas_validas']]
print(f"Filas inválidas: {len(invalidas)}")
print(invalidas)
