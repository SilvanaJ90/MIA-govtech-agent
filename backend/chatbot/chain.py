#!/usr/bin/env python3
from langchain.chains import LLMChain
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field # Definición del Schema

from llm import llm
from memory import prompt, memory
from vector_db import initialize_faiss, documents, embeddings
# NUEVOS IMPORTS:
from prompt_template import CLASSIFIER_TEMPLATE, CLASSIFIER_SCHEMA 

# Inicializar faiss vectordb (usa 'documents' que son los documentos segmentados)
#docsearch = initialize_faiss(documents, embeddings)

# ==============================================================================
# Definición del Schema para la Clasificación de Intención (Obligatorio en LangChain)
# ==============================================================================
class IntentClassification(BaseModel):
    """Estructura de salida requerida para la clasificación de intención."""
    case_type: str = Field(description="Clasificación: 'APPOINTMENT', 'COMPLEX_CASE', o 'SIMPLE_INFO'.")
    procedure_name: str = Field(description="Nombre específico del trámite o tema que el usuario solicita.")

# Inicializar parser
classification_parser = JsonOutputParser(pydantic_object=IntentClassification)

# ==============================================================================
# Cadena de Clasificación de Intención
# ==============================================================================
CLASSIFIER_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content="Analiza la intención de la consulta."),
        ("human", CLASSIFIER_TEMPLATE), # <-- Usa la plantilla importada
    ]
).partial(format_instructions=classification_parser.get_format_instructions())

# La cadena que ejecuta la clasificación
intent_chain = CLASSIFIER_PROMPT | llm | classification_parser


# ==============================================================================
# Cadenas de Respuesta RAG (Tu código existente - sin cambios)
# ==============================================================================
# initialize faiss vectordb
try:
    docsearch = initialize_faiss(documents, embeddings)
    print("INFO: FAISS/Vector DB inicializado correctamente.")
except Exception as e:
    print(f"ERROR: No se pudo inicializar FAISS/Vector DB: {e}")
    # Establecemos docsearch en None para que el script continúe, pero la RAG fallará.
    docsearch = None

# LLM string to generate responses using the custom prompt
chat_llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=False,
    memory=memory
)
# Create the QA Chain with FAISS and use the response from the custom LLM
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=docsearch.as_retriever(),
    chain_type="stuff",
    memory=memory
)


# Function to process the response of the custom LLM
def generate_response_from_llm(question, context, documents):
    """Use the custom LLM to generate a response."""
    # Match the question and the content of the retrieved documents
    combined_input = f"Pregunta: {question}\n\nDocumentos:\n"
    for doc in documents:
        combined_input += f"- {doc.page_content}\n"
    # Execute the LLM chain with the prompt and context
    result = chat_llm_chain.run({
        "human_input": combined_input,
        "chat_history": context,
    })

    return result

def classify_intent(query: str) -> dict:
    """Clasifica la intención del usuario usando el modelo y devuelve un JSON."""
    try:
        # Aquí usamos la nueva cadena de intención
        # Asegúrate de que 'intent_chain' esté definido globalmente justo arriba.
        return intent_chain.invoke({"query": query}) 
    except Exception as e:
        # En caso de error, asume información simple para no bloquear el chat
        print(f"Error en la clasificación de intención: {e}")
        return {"case_type": "SIMPLE_INFO", "procedure_name": "Información general"}