import dash
from dash import dcc, html, Input, Output, callback
from dash import dash_table
import requests
import pandas as pd
import plotly.express as px

# Inicializa la app de Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dashboard de Métricas"

# Layout del dashboard
app.layout = html.Div([
    html.H1("Dashboard de Métricas", style={"textAlign": "center"}),

    dcc.Tabs([
        dcc.Tab(label="Métricas Generales", children=[
            html.Div(id="metrics-container", children="Cargando métricas..."),

            dash_table.DataTable(
                id="recent-requests-table",
                columns=[
                    {"name": "Tiempo Inicio", "id": "tiempo_inicio"},
                    {"name": "Tiempo Fin", "id": "tiempo_fin"},
                    {"name": "Usuario", "id": "user_id"},
                    {"name": "Tipo de Solicitud", "id": "tipo_solicitud"},
                    {"name": "Demanda Predicha", "id": "demanda_predicha"},
                    {"name": "Latencia Calculada", "id": "latencia_calculada"},
                ],
                style_table={"overflowX": "auto"},
                page_size=10,
            ),
        ]),

        dcc.Tab(label="Usuarios Básicos", children=[
            dcc.Graph(id="basic-users-latency-graph"),
            dcc.Graph(id="basic-users-demand-graph"),
        ]),

        dcc.Tab(label="Usuarios Avanzados", children=[
            dcc.Graph(id="advanced-users-latency-graph"),
            dcc.Graph(id="advanced-users-demand-graph"),
        ]),
    ]),

    dcc.Interval(
        id="interval-component",
        interval=10 * 1000,  # Actualización cada 10 segundos
        n_intervals=0
    ),
])

# Callback para actualizar métricas generales y tabla
@app.callback(
    [
        Output("metrics-container", "children"),
        Output("recent-requests-table", "data"),
    ],
    [Input("interval-component", "n_intervals")]
)
def update_metrics(n_intervals):
    try:
        response = requests.get("http://127.0.0.1:8000/metrics")
        if response.status_code != 200:
            return "Error al obtener métricas.", []

        metrics = response.json().get("content", {})

        # Métricas Generales
        usuarios_basicos = metrics.get("usuarios_basicos", {})
        usuarios_avanzados = metrics.get("usuarios_avanzados", {})

        total_requests_basicos = usuarios_basicos.get("total_requests", "N/A")
        avg_latency_basicos = usuarios_basicos.get("average_latency", "N/A")
        avg_predicted_demand_basicos = usuarios_basicos.get("average_predicted_demand", "N/A")

        total_requests_avanzados = usuarios_avanzados.get("total_requests", "N/A")
        avg_latency_avanzados = usuarios_avanzados.get("average_latency", "N/A")
        avg_predicted_demand_avanzados = usuarios_avanzados.get("average_predicted_demand", "N/A")

        metrics_summary = html.Div([
            html.P(f"Total de Solicitudes (Básicos): {total_requests_basicos}"),
            html.P(f"Latencia Promedio (Básicos): {avg_latency_basicos} ms"),
            html.P(f"Demanda Predicha Promedio (Básicos): {avg_predicted_demand_basicos}"),
            html.Br(),
            html.P(f"Total de Solicitudes (Avanzados): {total_requests_avanzados}"),
            html.P(f"Latencia Promedio (Avanzados): {avg_latency_avanzados} ms"),
            html.P(f"Demanda Predicha Promedio (Avanzados): {avg_predicted_demand_avanzados}"),
        ])

        # Tabla de últimas solicitudes
        last_requests = usuarios_basicos.get("last_requests", []) + usuarios_avanzados.get("last_requests", [])

        return metrics_summary, last_requests
    except Exception as e:
        return f"Error al procesar las métricas: {str(e)}", []

# Callback para actualizar gráficos de usuarios básicos
@app.callback(
    [
        Output("basic-users-latency-graph", "figure"),
        Output("basic-users-demand-graph", "figure"),
    ],
    [Input("interval-component", "n_intervals")]
)
def update_basic_users_graphs(n_intervals):
    try:
        response = requests.get("http://127.0.0.1:8000/metrics")
        if response.status_code != 200:
            raise Exception("Error al obtener métricas de usuarios básicos.")

        metrics = response.json().get("content", {})
        usuarios_basicos = metrics.get("usuarios_basicos", {})
        last_requests = usuarios_basicos.get("last_requests", [])

        df = pd.DataFrame(last_requests)

        if not df.empty:
            latency_fig = px.histogram(df, x="latencia_calculada", title="Latencia de Usuarios Básicos")
            demand_fig = px.histogram(df, x="demanda_predicha", title="Demanda Predicha de Usuarios Básicos")
        else:
            latency_fig = px.histogram(title="Latencia de Usuarios Básicos (Sin datos)")
            demand_fig = px.histogram(title="Demanda Predicha de Usuarios Básicos (Sin datos)")

        return latency_fig, demand_fig
    except Exception as e:
        return px.histogram(title=f"Error: {str(e)}"), px.histogram(title=f"Error: {str(e)}")

# Callback para actualizar gráficos de usuarios avanzados
@app.callback(
    [
        Output("advanced-users-latency-graph", "figure"),
        Output("advanced-users-demand-graph", "figure"),
    ],
    [Input("interval-component", "n_intervals")]
)
def update_advanced_users_graphs(n_intervals):
    try:
        response = requests.get("http://127.0.0.1:8000/metrics")
        if response.status_code != 200:
            raise Exception("Error al obtener métricas de usuarios avanzados.")

        metrics = response.json().get("content", {})
        usuarios_avanzados = metrics.get("usuarios_avanzados", {})
        last_requests = usuarios_avanzados.get("last_requests", [])

        df = pd.DataFrame(last_requests)

        if not df.empty:
            latency_fig = px.histogram(df, x="latencia_calculada", title="Latencia de Usuarios Avanzados")
            demand_fig = px.histogram(df, x="demanda_predicha", title="Demanda Predicha de Usuarios Avanzados")
        else:
            latency_fig = px.histogram(title="Latencia de Usuarios Avanzados (Sin datos)")
            demand_fig = px.histogram(title="Demanda Predicha de Usuarios Avanzados (Sin datos)")

        return latency_fig, demand_fig
    except Exception as e:
        return px.histogram(title=f"Error: {str(e)}"), px.histogram(title=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run_server(debug=True)
