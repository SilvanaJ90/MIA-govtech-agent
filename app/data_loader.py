"""
data_loader.py
-------------
Este módulo se encarga de cargar y procesar documentos, específicamente
la documentación de Python en formato PDF. Utiliza LangChain para dividir
el texto en fragmentos manejables (chunks) para el sistema RAG.

Principales funciones:
- load_data(): Carga el PDF, extrae el texto y lo divide en chunks.
"""

# Importaciones necesarias
import pdfplumber
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Construir la ruta al documento de forma robusta
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PDF_PATH = os.path.join(PROJECT_ROOT, "data", "library.pdf")

def load_data():
    """
    Carga el contenido del PDF, lo extrae y lo divide en chunks de texto
    utilizando un divisor de caracteres recursivo de LangChain.

    Returns:
        list[str]: Una lista de cadenas de texto, donde cada cadena es un
                   chunk del documento original. O una lista vacía si
                   ocurre un error.

    Proceso:
    1. Verifica si el archivo PDF existe.
    2. Abre el PDF usando pdfplumber y extrae todo el texto.
    3. Inicializa RecursiveCharacterTextSplitter para dividir el texto
       en chunks de tamaño y solapamiento definidos.
    4. Procesa y divide el texto en chunks.
    5. Devuelve la lista de chunks de texto.
    """
    if not os.path.exists(PDF_PATH):
        print(f"\nERROR: El archivo no se encuentra en la ruta: {PDF_PATH}")
        return []

    try:
        print("\n=== Iniciando carga de datos del PDF ===")
        
        # 1. Extraer todo el texto del PDF
        with pdfplumber.open(PDF_PATH) as pdf:
            full_text = ""
            for page in pdf.pages:
                # Se añade un espacio para asegurar separación entre textos de páginas
                full_text += page.extract_text() + " "
        
        print(f"Total de caracteres extraídos: {len(full_text)}")
        
        # 2. Inicializar el divisor de texto de LangChain
        # chunk_size: el tamaño máximo de cada chunk (en caracteres)
        # chunk_overlap: cuántos caracteres se solapan entre chunks consecutivos
        #                para no perder el contexto en los cortes.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""] # Intenta dividir por párrafos primero
        )
        
        # 3. Dividir el texto en chunks
        chunks = text_splitter.split_text(full_text)
        
        # 4. Mostrar información y devolver los chunks
        print(f"\n=== Documento dividido en {len(chunks)} chunks ===")
        print("Ejemplo del primer chunk:")
        print("-" * 30)
        print(chunks[0])
        print("-" * 30)
            
        return chunks
        
    except Exception as e:
        print(f"\nERROR durante la carga o procesamiento del PDF: {str(e)}")
        return []

# Punto de entrada para ejecución directa del script (para pruebas)
if __name__ == "__main__":
    print("Ejecutando carga de datos directamente...")
    result_chunks = load_data()
    if result_chunks:
        print(f"\nResultado final: {len(result_chunks)} chunks cargados exitosamente.")
