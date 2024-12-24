import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests
import time
import json
import random
# Configuración inicial
app = dash.Dash(__name__)
server = app.server  # Exponer el servidor Flask para Dash
NUM_SERVIDORES_MAX=5
# URL de la API de tu aplicación Flask
api_url = "http://127.0.0.1:5000/solicitud"  # Ajusta si es necesario

# Layout del dashboard
app.layout = html.Div([
    html.H1("Monitor de Balanceo de Carga"),
    dcc.Graph(id='live-graph-carga'),
    dcc.Graph(id='live-graph-cola'),
    dcc.Graph(id='live-graph-respuesta'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Actualizar cada 5 segundos
        n_intervals=0
    )
])

# Función para obtener datos de la API (simulando la obtención de datos del CSV)
def obtener_datos():
    try:
        # Aquí simulamos la obtención de datos. En la práctica, esto podría ser una consulta a una base de datos o la lectura de un archivo.
        # Para propósitos de demostración, crearemos datos aleatorios que simulan la estructura de tu CSV.
        num_filas = 100  # Número de filas de datos simulados
        datos = {
            'tiempo_inicio': pd.date_range(end=pd.Timestamp.now(), periods=num_filas, freq='5S'),
            'tiempo_fin': pd.date_range(end=pd.Timestamp.now(), periods=num_filas, freq='5S'),
            'user_id': [f'user_{random.randint(1, 10)}' for _ in range(num_filas)],
            'tipo_solicitud': [random.choice(['simple', 'compleja', 'codigo']) for _ in range(num_filas)],
            'texto_solicitud': ['Texto de solicitud ' + str(i) for i in range(num_filas)],
            'caracteristicas': [{"longitud": random.randint(10, 150), "tipo": random.choice(['simple', 'compleja', 'codigo'])} for _ in range(num_filas)],
            'demanda_predicha': [round(random.uniform(0.5, 5.0), 2) for _ in range(num_filas)],
            'servidor_asignado': [random.randint(0, 5) for _ in range(num_filas)],
            'tiempo_asignacion': [round(random.uniform(0.01, 0.5), 3) for _ in range(num_filas)],
            'tiempo_espera': [round(random.uniform(0.0, 1.0), 3) for _ in range(num_filas)]
        }
        df = pd.DataFrame(datos)
        return df
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error


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

    # Crear la figura para los tiempos de respuesta
    fig = go.Figure()

    # Añadir traza para los tiempos de respuesta
    fig.add_trace(go.Scatter(x=df['tiempo_inicio'], y=df['tiempo_respuesta'],  # Reemplaza con la métrica correcta
                             mode='lines+markers',
                             name='Tiempo de Respuesta'))

    # Actualizar el layout de la figura
    fig.update_layout(title_text="Tiempos de Respuesta",
                      xaxis_title="Tiempo",
                      yaxis_title="Tiempo de Respuesta (s)")

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)