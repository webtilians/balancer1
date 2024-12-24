import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time

class EntornoBalanceo(gym.Env):
    def __init__(self, asignador_recursos):
        super(EntornoBalanceo, self).__init__()
        self.asignador_recursos = asignador_recursos
        self.action_space = spaces.Discrete(3)  # 0: No hacer nada, 1: Crear servidor, 2: Eliminar servidor
        self.observation_space = spaces.Box(low=0, high=100, shape=(self.asignador_recursos.num_servidores_max + 1,), dtype=np.float32)

    def reset(self, seed=None):
        super().reset(seed=seed)
        # Reiniciar el entorno a un estado inicial
        for servidor in self.asignador_recursos.servidores:
            servidor.carga = 0
        self.asignador_recursos.cola_solicitudes.queue.clear()

        # Devolver el estado inicial
        return self._get_estado(), {}

    def step(self, accion):
        # Ejecutar la acción en el entorno
        if accion == 1:
            self.asignador_recursos.crear_servidor()
        elif accion == 2:
            self.asignador_recursos.eliminar_servidor()

        # Esperar un tiempo para que la acción tenga efecto y se procesen solicitudes
        time.sleep(1)  # Ajusta el tiempo según sea necesario

        # Calcular la recompensa (esto es solo un ejemplo)
        carga_promedio = sum(s.carga for s in self.asignador_recursos.servidores) / len(self.asignador_recursos.servidores) if len(self.asignador_recursos.servidores) > 0 else 0
        longitud_cola = self.asignador_recursos.cola_solicitudes.qsize()
        recompensa = -carga_promedio - longitud_cola * 0.5  # Penalizar carga alta y cola larga

        # Obtener el nuevo estado
        estado = self._get_estado()

        # Comprobar si el episodio ha terminado (puedes definir un criterio de finalización)
        terminado = False  # En este ejemplo, el episodio nunca termina
        truncado = False
        # Información adicional (opcional)
        info = {}

        return estado, recompensa, terminado, truncado, info

    def _get_estado(self):
        # Obtener el estado actual del sistema
        carga_servidores = [s.carga for s in self.asignador_recursos.servidores]
        longitud_cola = self.asignador_recursos.cola_solicitudes.qsize()

        # Asegurarse de que el estado tenga siempre la misma longitud
        while len(carga_servidores) < self.asignador_recursos.num_servidores_max:
            carga_servidores.append(0.0)  # Rellenar con ceros si hay menos servidores que el máximo

        estado = np.array(carga_servidores + [longitud_cola], dtype=np.float32)
        return estado