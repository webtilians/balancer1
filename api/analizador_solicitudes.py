import spacy
import numpy as np

class AnalizadorSolicitudes:
    def __init__(self):
        # Cargar el modelo de spaCy para español
        self.nlp = spacy.load("es_core_news_md")

    def analizar(self, texto_solicitud):
        # Extraer características básicas
        longitud = len(texto_solicitud)
        tipo = "simple"  # Valor por defecto

        if "código" in texto_solicitud.lower() or "ejecutar" in texto_solicitud.lower():
            tipo = "codigo"
        elif "análisis" in texto_solicitud.lower() or "predicción" in texto_solicitud.lower():
            tipo = "compleja"

        # Procesar el texto con spaCy
        doc = self.nlp(texto_solicitud)

        # Extraer el vector de embedding para la solicitud (promedio de los vectores de los tokens)
        vector_spacy = doc.vector.tolist()

        # Combinar todas las características
        caracteristicas = {
            "longitud": longitud,
            "tipo": tipo,
            "vector_spacy": vector_spacy
        }

        return caracteristicas