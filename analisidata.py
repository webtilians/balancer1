import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos desde el archivo CSV
def cargar_datos(ruta_csv):
    try:
        datos = pd.read_csv(ruta_csv)
        print("Datos cargados correctamente.")
        return datos
    except FileNotFoundError:
        print(f"Error: El archivo {ruta_csv} no fue encontrado.")
        return None
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return None

# Generar estadísticas descriptivas
def estadisticas_descriptivas(datos):
    print("--- Estadísticas Descriptivas ---")
    print(datos.describe())

# Graficar la demanda predicha vs latencia calculada
def graficar_demanda_vs_latencia(datos):
    try:
        plt.figure(figsize=(10, 6))
        plt.scatter(datos['demanda_predicha'], datos['latencia_calculada'], alpha=0.7)
        plt.title("Demanda Predicha vs Latencia Calculada")
        plt.xlabel("Demanda Predicha")
        plt.ylabel("Latencia Calculada")
        plt.grid()
        plt.show()
    except KeyError as e:
        print(f"Error: La columna necesaria no está en los datos ({e}).")

# Detección de valores atípicos en la latencia

def detectar_valores_atipicos(datos):
    try:
        q1 = datos['latencia_calculada'].quantile(0.25)
        q3 = datos['latencia_calculada'].quantile(0.75)
        iqr = q3 - q1
        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr

        atipicos = datos[(datos['latencia_calculada'] < limite_inferior) | (datos['latencia_calculada'] > limite_superior)]
        print("--- Valores Atípicos en Latencia Calculada ---")
        print(atipicos)

        return atipicos
    except KeyError as e:
        print(f"Error: La columna necesaria no está en los datos ({e}).")
        return None

# Función principal
if __name__ == "__main__":
    ruta_csv = "scripts/datos_simulacion.csv"

    # Cargar los datos
    datos = cargar_datos(ruta_csv)

    if datos is not None:
        # Generar estadísticas descriptivas
        estadisticas_descriptivas(datos)

        # Graficar la demanda predicha vs latencia calculada
        graficar_demanda_vs_latencia(datos)

        # Detectar valores atípicos en la latencia calculada
        detectar_valores_atipicos(datos)
