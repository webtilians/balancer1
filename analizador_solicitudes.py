class AnalizadorSolicitudes:
    def analizar(self, texto_solicitud):
        """
        Analiza la solicitud y extrae características básicas.
        """
        longitud = len(texto_solicitud)
        tipo = "simple"  # Valor por defecto

        if "código" in texto_solicitud.lower() or "ejecutar" in texto_solicitud.lower():
            tipo = "codigo"
        elif "análisis" in texto_solicitud.lower() or "predicción" in texto_solicitud.lower():
            tipo = "compleja"

        return {
            "longitud": longitud,
            "tipo": tipo
        }