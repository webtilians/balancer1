class GestorUsuarios:
    def __init__(self):
        self.perfiles = {}  # {user_id: perfil}
        self.historial = {}  # {user_id: [lista de solicitudes]}

    def obtener_perfil(self, user_id):
        """
        Obtiene el perfil de un usuario. Si no existe, lo crea con un perfil básico.
        """
        if user_id not in self.perfiles:
            self.perfiles[user_id] = "basico"
            self.historial[user_id] = []
        return self.perfiles[user_id]

    def registrar_solicitud(self, user_id, solicitud):
        """
        Registra una solicitud en el historial del usuario.
        """
        if user_id not in self.historial:
            self.historial[user_id] = []
        self.historial[user_id].append(solicitud)

    def actualizar_perfil(self, user_id):
        """
        Actualiza el perfil del usuario en función de su historial de solicitudes.
        """
        if user_id not in self.historial:
            return

        historial = self.historial[user_id]
        num_solicitudes = len(historial)
        num_complejas = sum(1 for s in historial if s["tipo"] == "compleja")
        num_codigo = sum(1 for s in historial if s["tipo"] == "codigo")

        if num_solicitudes >= 15 and num_codigo >= 5:
            self.perfiles[user_id] = "avanzado"
        elif num_solicitudes >= 10 and num_complejas >= 3:
            self.perfiles[user_id] = "intermedio"
        else:
            self.perfiles[user_id] = "basico"
    
    def actualizar_perfiles(self):
      """
      Actualiza los perfiles de todos los usuarios registrados.
      """
      for user_id in self.historial.keys():
          self.actualizar_perfil(user_id)