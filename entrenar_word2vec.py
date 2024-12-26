from gensim.models import Word2Vec
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
nltk.data.path.append('C:\\Users\\ENRIQUE\\balancer1\\nltk_data\\tokenizers')

# Descargar los recursos de NLTK si no están ya descargados
nltk.download('punkt')
nltk.download('stopwords')

def _preprocess(text):
    # Convertir a minúsculas, tokenizar y eliminar stopwords
    stop_words = set(stopwords.words('spanish'))
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t not in stop_words and t.isalnum()]
    return tokens

def entrenar_modelo_word2vec(csv_path, model_path="word2vec.model"):
    """
    Entrena un modelo Word2Vec con los textos del csv y lo guarda en un archivo.
    """
    try:
        # Cargar datos desde el CSV
        df = pd.read_csv(csv_path)

        # Asegurarse de que la columna 'texto_solicitud' existe
        if 'texto_solicitud' not in df.columns:
            raise ValueError("El CSV debe contener una columna 'texto_solicitud'")

        # Preprocesar los textos y tokenizar
        corpus = [_preprocess(texto) for texto in df['texto_solicitud']]

        # Entrenar el modelo Word2Vec
        model = Word2Vec(sentences=corpus, vector_size=100, window=5, min_count=1, workers=4)

        # Guardar el modelo
        model.save(model_path)
        print(f"Modelo Word2Vec entrenado y guardado en {model_path}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {csv_path}")
    except Exception as e:
        print(f"Error al entrenar el modelo Word2Vec: {e}")

if __name__ == "__main__":
    csv_path = "datos_simulacion_inicial.csv"  # Ruta a tu archivo CSV
    entrenar_modelo_word2vec(csv_path)