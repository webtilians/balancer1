import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def cargar_datos(ruta_csv):
    """Carga los datos desde un archivo CSV."""
    try:
        df = pd.read_csv(ruta_csv)
        print("Archivo cargado correctamente.")
        return df
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return None

def analizar_outliers(df, columna):
    """Identifica y grafica outliers en una columna específica."""
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1

    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    outliers = df[(df[columna] < limite_inferior) | (df[columna] > limite_superior)]
    print(f"Se encontraron {len(outliers)} outliers en {columna}.")

    # Visualización
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df, x=columna)
    plt.title(f"Outliers en {columna}")
    plt.show()

    return outliers

def analizar_segmentacion(df, columnas_segmento, columna_objetivo):
    """Agrupa datos y calcula métricas por segmento."""
    segmentado = df.groupby(columnas_segmento)[columna_objetivo].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
    print("Estadísticas segmentadas:")
    print(segmentado)
    return segmentado

def graficar_segmentacion(segmentado, columnas_segmento, columna_objetivo):
    """Grafica las métricas segmentadas."""
    for col in columnas_segmento:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=segmentado, x=col, y='mean', ci=None)
        plt.title(f"Media de {columna_objetivo} por {col}")
        plt.show()

def analizar_tendencias(df, columna_tiempo, columna_objetivo):
    """Analiza tendencias temporales."""
    df[columna_tiempo] = pd.to_datetime(df[columna_tiempo])
    df['hora'] = df[columna_tiempo].dt.hour

    tendencias = df.groupby('hora')[columna_objetivo].mean().reset_index()
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=tendencias, x='hora', y=columna_objetivo)
    plt.title(f"Tendencia de {columna_objetivo} por hora del día")
    plt.xlabel("Hora del día")
    plt.ylabel(f"Media de {columna_objetivo}")
    plt.show()

    return tendencias

if __name__ == "__main__":
    ruta_csv = "mix.csv"  # Ajusta la ruta según tu estructura de carpetas
    datos = cargar_datos(ruta_csv)

    if datos is not None:
        # Análisis de outliers
        outliers_latencia = analizar_outliers(datos, 'latencia_calculada')

        # Análisis por nivel de usuario y tipo de solicitud
        if 'nivel_usuario' in datos.columns and 'tipo_solicitud' in datos.columns:
            segmentacion = analizar_segmentacion(datos, ['nivel_usuario', 'tipo_solicitud'], 'latencia_calculada')
            graficar_segmentacion(segmentacion, ['nivel_usuario', 'tipo_solicitud'], 'latencia_calculada')

        # Análisis de tendencias temporales
        if 'tiempo_inicio' in datos.columns:
            tendencias = analizar_tendencias(datos, 'tiempo_inicio', 'latencia_calculada')
