from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import yaml
import os
# import logging # Logging import will be removed as we are switching to print

# Determine the absolute path to the directory containing the current script (vector_store.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go one level up to the project root directory
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# Construct the absolute path to config.yaml
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")
# Construct the absolute path for the Chroma vector store persistence
VECTOR_STORE_DIR = os.path.join(PROJECT_ROOT, "vector_store")

# Load configuration from YAML file
# This section reads the 'config.yaml' file to get necessary configurations,
# like the OpenAI API key. It's crucial for the application to connect to OpenAI services.
#with open(CONFIG_PATH, "r") as file:
    #config = yaml.safe_load(file)
try:
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)
        if not config or "openai_api_key" not in config:
            raise ValueError("Falta 'openai_api_key' en config.yaml")
except Exception as e:
    print(f"ERROR al cargar configuración desde {CONFIG_PATH}: {e}")
    exit(1)

# logger = logging.getLogger(__name__) # Logger initialization will be removed

def initialize_vector_store(data, store_name="nutricion_store"):
    """
    Crea un almacén vectorial desde datos iniciales.
    Ahora `data` es una lista de textos (chunks).
    """
    print("\n=== Inicializando Vector Store ===")
    
    if not data:
        print("ERROR: No hay datos para inicializar el vector store")
        return None
    
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=config["openai_api_key"])
        vector_store_path = os.path.join(VECTOR_STORE_DIR, store_name)
        os.makedirs(vector_store_path, exist_ok=True)

        # El 'data' que llega ahora es una lista de textos (chunks),
        # por lo que se puede usar directamente.
        texts = data
        
        print(f"\n=== {len(texts)} chunks de texto listos para ser indexados ===")
        
        # Ensure the persist directory exists
        #os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

        vector_store = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            #persist_directory=VECTOR_STORE_DIR
            persist_directory=vector_store_path
        )

        print("\nVector Store creado y persistido correctamente en:", vector_store_path)
        return vector_store
        
    except Exception as e:
        print(f"\nERROR al crear vector store: {str(e)}")
        return None

def load_vector_store(store_name="nutricion_store"):
    """
    Carga el almacén vectorial para búsqueda semántica
    """
    try:
        vector_store_path = os.path.join(VECTOR_STORE_DIR, store_name)
        # Check if the vector store directory exists
        if not os.path.exists(vector_store_path) or not os.listdir(vector_store_path):
            # Using print instead of logger.warning
            print(f"ADVERTENCIA: El directorio de Vector Store ({store_name}) no existe o está vacío. Es posible que necesite inicialización.")
            return None

        embeddings = OpenAIEmbeddings(openai_api_key=config["openai_api_key"])
        vector_store = Chroma(
            #persist_directory=VECTOR_STORE_DIR,
            #vector_store_path = os.path.join(VECTOR_STORE_DIR, store_name)
            persist_directory=vector_store_path,
            embedding_function=embeddings
        )
        # Using print instead of logger.info
        print(f"INFO: Vector store cargado exitosamente desde: {vector_store_path}")
        return vector_store
    except Exception as e:
        # Using print instead of logger.error
        print(f"ERROR: Error al cargar vector store desde {vector_store_path}: {str(e)}")
        return None
    #return vector_store
    #except Exception as e: