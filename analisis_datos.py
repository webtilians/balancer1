import pandas as pd
import matplotlib.pyplot as plt
import json

def analizar_datos(ruta_csv):
    """
    Analiza los datos de la simulación guardados en un archivo CSV.

    Args:
        ruta_csv (str): La ruta al archivo CSV.
    """
    try:
        df = pd.read_csv(ruta_csv)

        # Convertir las columnas de tiempo a datetime
        df['tiempo_inicio'] = pd.to_datetime(df['tiempo_inicio'])
        df['tiempo_fin'] = pd.to_datetime(df['tiempo_fin'])

        # Calcular el tiempo de respuesta en segundos
        df['tiempo_respuesta'] = (df['tiempo_fin'] - df['tiempo_inicio']).dt.total_seconds()

        # Convertir las características de JSON a columnas separadas
        caracteristicas_df = pd.json_normalize(df['caracteristicas'].apply(lambda x: json.loads(x.replace("'", '"'))))
        df = pd.concat([df, caracteristicas_df], axis=1)

        # Eliminar la columna 'caracteristicas' original
        df.drop('caracteristicas', axis=1, inplace=True)

        # 1. Análisis de la Demanda Predicha
        print("=" * 30)
        print("ANÁLISIS DE LA DEMANDA PREDICTA")
        print("=" * 30)

        # Estadísticas descriptivas para 'demanda_predicha'
        print(df['demanda_predicha'].describe())

        # Histograma de la demanda predicha
        plt.figure(figsize=(8, 6))
        plt.hist(df['demanda_predicha'], bins=20, edgecolor='k')
        plt.xlabel('Demanda Predicha')
        plt.ylabel('Frecuencia')
        plt.title('Distribución de la Demanda Predicha')
        plt.show()

        # Análisis de la demanda predicha por tipo de solicitud
        print("\nDemanda predicha por tipo de solicitud:")
        print(df.groupby('tipo_solicitud')['demanda_predicha'].mean())

        # 2. Análisis del Tiempo de Respuesta
        print("\n" + "=" * 30)
        print("ANÁLISIS DEL TIEMPO DE RESPUESTA")
        print("=" * 30)

        # Estadísticas descriptivas para 'tiempo_respuesta'
        print(df['tiempo_respuesta'].describe())

        # Histograma del tiempo de respuesta
        plt.figure(figsize=(8, 6))
        plt.hist(df['tiempo_respuesta'], bins=20, edgecolor='k')
        plt.xlabel('Tiempo de Respuesta (s)')
        plt.ylabel('Frecuencia')
        plt.title('Distribución del Tiempo de Respuesta')
        plt.show()

        # Gráfico de dispersión de la demanda predicha vs. tiempo de respuesta
        plt.figure(figsize=(8, 6))
        plt.scatter(df['demanda_predicha'], df['tiempo_respuesta'])
        plt.xlabel('Demanda Predicha')
        plt.ylabel('Tiempo de Respuesta (s)')
        plt.title('Relación entre Demanda Predicha y Tiempo de Respuesta')
        plt.show()

        # Análisis del tiempo de respuesta por tipo de solicitud
        print("\nTiempos de respuesta por tipo de solicitud:")
        print(df.groupby('tipo_solicitud')['tiempo_respuesta'].mean())

        # 3. Análisis del Tiempo de Asignación
        print("\n" + "=" * 30)
        print("ANÁLISIS DEL TIEMPO DE ASIGNACIÓN")
        print("=" * 30)

        # Estadísticas descriptivas para 'tiempo_asignacion'
        print(df['tiempo_asignacion'].describe())

        # Histograma del tiempo de asignación
        plt.figure(figsize=(8, 6))
        plt.hist(df['tiempo_asignacion'], bins=20, edgecolor='k')
        plt.xlabel('Tiempo de Asignación (s)')
        plt.ylabel('Frecuencia')
        plt.title('Distribución del Tiempo de Asignación')
        plt.show()

        # Gráfico de línea del tiempo de asignación a lo largo del tiempo
        plt.figure(figsize=(12, 6))
        plt.plot(df['tiempo_inicio'], df['tiempo_asignacion'])
        plt.xlabel('Tiempo')
        plt.ylabel('Tiempo de Asignación (s)')
        plt.title('Tiempo de Asignación a lo Largo del Tiempo')
        plt.show()

        # Análisis del tiempo de asignación por tipo de solicitud
        print("\nTiempo de asignación por tipo de solicitud:")
        print(df.groupby('tipo_solicitud')['tiempo_asignacion'].mean())

        # 4. Análisis por Servidor
        print("\n" + "=" * 30)
        print("ANÁLISIS POR SERVIDOR")
        print("=" * 30)

        # Tiempo promedio de respuesta por servidor
        print("\nTiempo promedio de respuesta por servidor:")
        print(df.groupby('servidor_asignado')['tiempo_respuesta'].mean())

        # Demanda predicha promedio por servidor
        print("\nDemanda predicha promedio por servidor:")
        print(df.groupby('servidor_asignado')['demanda_predicha'].mean())

        # 5. Análisis por Perfil de Usuario
        print("\n" + "=" * 30)
        print("ANÁLISIS POR PERFIL DE USUARIO")
        print("=" * 30)

        # Tiempo promedio de respuesta por perfil de usuario
        print("\nTiempo promedio de respuesta por perfil de usuario:")
        print(df.groupby('perfil')['tiempo_respuesta'].mean())

        # Demanda predicha promedio por perfil de usuario
        print("\nDemanda predicha promedio por perfil de usuario:")
        print(df.groupby('perfil')['demanda_predicha'].mean())

        # 6. Análisis Temporal
        print("\n" + "=" * 30)
        print("ANÁLISIS TEMPORAL")
        print("=" * 30)

        # Gráfico de la demanda predicha a lo largo del tiempo
        plt.figure(figsize=(12, 6))
        plt.plot(df['tiempo_inicio'], df['demanda_predicha'])
        plt.xlabel('Tiempo')
        plt.ylabel('Demanda Predicha')
        plt.title('Demanda Predicha a lo Largo del Tiempo')
        plt.show()

        # Gráfico del tiempo de respuesta a lo largo del tiempo
        plt.figure(figsize=(12, 6))
        plt.plot(df['tiempo_inicio'], df['tiempo_respuesta'])
        plt.xlabel('Tiempo')
        plt.ylabel('Tiempo de Respuesta (s)')
        plt.title('Tiempo de Respuesta a lo Largo del Tiempo')
        plt.show()

        # 7. Análisis de Correlación
        print("\n" + "=" * 30)
        print("ANÁLISIS DE CORRELACIÓN")
        print("=" * 30)

        # Matriz de correlación
        corr_matrix = df.corr(numeric_only=True)
        print("\nMatriz de correlación:")
        print(corr_matrix)

        # Mapa de calor de la matriz de correlación
        plt.figure(figsize=(10, 8))
        plt.matshow(corr_matrix, fignum=1)
        plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=90)
        plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
        plt.gca().xaxis.tick_bottom()
        plt.colorbar()
        plt.title('Mapa de Calor de la Matriz de Correlación')
        plt.show()

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_csv}")
    except Exception as e:
        print(f"Error al analizar los datos: {e}")

if __name__ == "__main__":
    analizar_datos("datos_simulacion.csv")