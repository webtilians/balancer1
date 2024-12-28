# config.py
from models.demand_predictor import DemandPredictor
from services.asignador import AsignadorRecursos

# Crear instancias compartidas
demand_predictor = DemandPredictor()
asignador_recursos = AsignadorRecursos(num_servidores_inicial=1, demand_predictor=demand_predictor)
