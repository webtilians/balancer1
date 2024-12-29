import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests
import time
import json
import random
import numpy as np

# Configuración inicial
app = dash.Dash(__name__)
server = app.server  # Exponer el servidor Flask para Dash

NUM_SERVIDORES_MAX = 5  # Definir NUM_SERVIDORES_MAX antes de usarlo

# URL de la API de tu aplicación Flask
api_url = "http://127.0.0.1:8000"  # Ajusta si es necesario

# Layout del dashboard
app.layout = html.Div([
    html.H1("Monitor de Balanceo de Carga"),
    dcc.Graph(id='live-graph-carga'),
    dcc.Graph(id='live-graph-cola'),
    dcc.Graph(id='live-graph-respuesta'),
    html.Div(id='live-num-servidores', style={'font-size': '24px', 'margin-top': '20px'}),
    html.Div(id='live-saturacion', style={'font-size': '24px', 'margin-top': '20px'}),
    dcc.Interval(
        id='interval-component',
        interval=2*1000,  # Actualizar cada 5 segundos
        n_intervals=0
    )
])

# Función para obtener datos de la API (simulando la obtención de datos del CSV)
def obtener_datos():
    try:
        df = pd.read_csv("datos_simulacion.csv")
        # Eliminar filas con valores NaN o infinitos
        df = df.replace([np.inf, -np.inf], np.nan).dropna()

        # Convertir las características de JSON a diccionarios si es necesario
        if 'caracteristicas' in df.columns:
            df['caracteristicas'] = df['caracteristicas'].apply(lambda x: json.loads(x.replace("'", '"')) if isinstance(x, str) else x)

        # Asegurarse de que 'tiempo_inicio' es de tipo datetime
        if 'tiempo_inicio' in df.columns:
            df['tiempo_inicio'] = pd.to_datetime(df['tiempo_inicio'])
        else:
            # Si no existe, crea una columna con la marca de tiempo actual
            df['tiempo_inicio'] = pd.Timestamp.now()

        # Asegurarse de que 'tiempo_respuesta' existe y es numérico
        if 'tiempo_respuesta' not in df.columns:
            df['tiempo_respuesta'] = 0.0  # O algún valor por defecto
        else:
            df['tiempo_respuesta'] = pd.to_numeric(df['tiempo_respuesta'], errors='coerce').fillna(0.0)

        # Aquí puedes agregar más columnas o cálculos si es necesario

        return df
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

# Función para obtener el número de servidores activos
def obtener_numero_servidores():
    try:
        response = requests.get(f"{api_url}/num_servidores")
        response.raise_for_status()
        return response.json()['num_servidores']
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el número de servidores: {e}")
        return 0

# Callback para actualizar la gráfica de carga de los servidores
@app.callback(Output('live-graph-carga', 'figure'),
              [Input('interval-component', 'n_intervals')])
def actualizar_grafica_carga(n):
    df = obtener_datos()

    # Crear la figura para la carga de los servidores
    fig = go.Figure()

    # Añadir trazas para cada servidor
    for i in range(NUM_SERVIDORES_MAX):
        fig.add_trace(go.Scatter(x=df['tiempo_inicio'], y=df['demanda_predicha'],  # Reemplaza con la métrica correcta
                                 mode='lines+markers',
                                 name=f'Servidor {i}'))

    # Actualizar el layout de la figura
    fig.update_layout(title_text="Carga de los Servidores",
                      xaxis_title="Tiempo",
                      yaxis_title="Carga")

    return fig

# Callback para actualizar la gráfica de longitud de la cola
@app.callback(Output('live-graph-cola', 'figure'),
              [Input('interval-component', 'n_intervals')])
def actualizar_grafica_cola(n):
    df = obtener_datos()

    # Crear la figura para la longitud de la cola
    fig = go.Figure()

    # Añadir traza para la longitud de la cola
    fig.add_trace(go.Scatter(x=df['tiempo_inicio'], y=df['tiempo_espera'],  # Reemplaza con la métrica correcta
                             mode='lines+markers',
                             name='Longitud de la Cola'))

    # Actualizar el layout de la figura
    fig.update_layout(title_text="Longitud de la Cola de Solicitudes",
                      xaxis_title="Tiempo",
                      yaxis_title="Longitud de la Cola")

    return fig

# Callback para actualizar la gráfica de tiempos de respuesta
@app.callback(Output('live-graph-respuesta', 'figure'),
              [Input('interval-component', 'n_intervals')])
def actualizar_grafica_respuesta(n):
    df = obtener_datos()

    # Convertir tiempos de respuesta a milisegundos
    df['tiempo_respuesta_ms'] = df['tiempo_respuesta'] * 1000

    # Crear la figura
    fig = go.Figure()

    # Añadir traza (en ms)
    fig.add_trace(go.Scatter(
        x=df['tiempo_inicio'],
        y=df['tiempo_respuesta_ms'],
        mode='lines+markers',
        name='Tiempo de Respuesta (ms)'
    ))

    # Configuración del layout
    fig.update_layout(
        title_text="Tiempos de Respuesta",
        xaxis_title="Tiempo",
        yaxis_title="Tiempo de Respuesta (ms)"
    )

    return fig


# Callback para actualizar el número de servidores activos
@app.callback(Output('live-num-servidores', 'children'),
              [Input('interval-component', 'n_intervals')])
def actualizar_numero_servidores(n):
    num_servidores = obtener_numero_servidores()
    return f"Número de Servidores Activos: {num_servidores}"

def obtener_carga_promedio():
    """Obtiene la carga promedio del sistema."""
    df = obtener_datos()
    if not df.empty:
        # Suponiendo que 'demanda_predicha' puede ser representativo de la carga
        return df['demanda_predicha'].mean()
    return 0

def obtener_longitud_cola():
    """Obtiene la longitud de la cola de solicitudes."""
    try:
        response = requests.get(f"{api_url}/longitud_cola")  # Usar la ruta correcta
        response.raise_for_status()
        return response.json()['longitud_cola']
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la longitud de la cola: {e}")
        return 0

def calcular_color_saturacion(carga_promedio, longitud_cola):
    """
    Calcula el color del indicador de saturación basado en la carga promedio y la longitud de la cola.
    """
    # Escala de colores: verde -> amarillo -> naranja -> rojo
    if carga_promedio < 50 and longitud_cola < 5:
        return 'green'
    elif carga_promedio < 75 and longitud_cola < 10:
        return 'yellow'
    elif carga_promedio < 90 and longitud_cola < 20:
        return 'orange'
    else:
        return 'red'
    
# Añadir un callback para actualizar el indicador de saturación
@app.callback(Output('live-saturacion', 'style'),
              [Input('interval-component', 'n_intervals')])
def actualizar_indicador_saturacion(n):
    carga_promedio = obtener_carga_promedio()
    longitud_cola = obtener_longitud_cola()
    color = calcular_color_saturacion(carga_promedio, longitud_cola)
    return {'background-color': color, 'padding': '10px', 'border-radius': '5px'}

if __name__ == '__main__':
    app.run_server(debug=True)