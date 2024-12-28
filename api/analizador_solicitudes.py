from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import spacy

class AnalizadorSolicitudes:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)  # Limitar el vocabulario a 100 palabras
        self.corpus = []  # Lista para almacenar las solicitudes de entrenamiento
        # Cargar modelo de spaCy (asegúrate de instalarlo previamente con: python -m spacy download es_core_news_md)
        self.nlp = spacy.load("es_core_news_md")
    def ajustar_vectorizador(self, textos):
        """
        Ajusta el vectorizador TF-IDF con un corpus de textos.
        """
        self.corpus = textos
        self.vectorizer.fit(textos)

    def analizar(self, texto_solicitud):
        # Extraer características básicas
        longitud = len(texto_solicitud)
        tipo = "simple"  # Valor por defecto
        # Procesar el texto con spaCy
        doc = self.nlp(texto_solicitud)
        # Generar el vector embedding del texto
        vector_spacy = doc.vector
        # Calcular longitud del texto
        longitud = len(texto_solicitud)

        if "código" in texto_solicitud.lower() or "ejecutar" in texto_solicitud.lower():
            tipo = "codigo"
        elif "análisis" in texto_solicitud.lower() or "predicción" in texto_solicitud.lower():
            tipo = "compleja"

        

        # Combinar todas las características
        caracteristicas = {
            "longitud": longitud,
            "tipo": tipo,
            "vector_spacy": vector_spacy.tolist()
        }

        return caracteristicas