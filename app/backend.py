from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from vector_store import load_vector_store
from langchain.prompts import PromptTemplate
import yaml
from new_prompts import SYSTEM_TEMPLATE

# Cargar configuración desde config.yaml
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

def handle_query(query, messages):
    # 1. CONFIGURACIÓN DEL LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,
        openai_api_key=config["openai_api_key"]
    )
    
    # 2. RETRIEVAL: Obtener el vector store para búsqueda
    vector_store = load_vector_store()
    
    # 3. AUGMENTATION: Configurar el prompt que combinará el contexto recuperado
    prompt = PromptTemplate(
        template=SYSTEM_TEMPLATE,
        input_variables=["context", "chat_history", "question"]
    )
    
    # 4. GENERATION: Crear la cadena que combina recuperación y generación
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        # RETRIEVAL: Configura la búsqueda de documentos relevantes
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        # AUGMENTATION: Usa el prompt para combinar contexto y pregunta
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        verbose=True
    )
    
    # Formatear el historial correctamente en pares (humano, ia)
    formatted_history = []
    # Ignorar el mensaje de bienvenida y la última pregunta del usuario
    chat_history_messages = messages[1:-1]
    
    for i in range(0, len(chat_history_messages), 2):
        if i + 1 < len(chat_history_messages):
            user_msg = chat_history_messages[i]
            bot_msg = chat_history_messages[i+1]
            if user_msg['role'] == 'user' and bot_msg['role'] == 'bot':
                formatted_history.append((user_msg['content'], bot_msg['content']))

    try:
        # Usar el callback para obtener las estadísticas
        with get_openai_callback() as cb:
            result = chain.invoke({
                "question": query,
                "chat_history": formatted_history
            })
            
            # Devolver un diccionario con la respuesta y las estadísticas
            return {
                "answer": result["answer"],
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost_usd": cb.total_cost
            }

    except Exception as e:
        # En caso de error, devolver un diccionario con valores por defecto
        return {
            "answer": "¡Hola! Soy Nutrilac - Bot. Disculpa, tuve un problema técnico. ¿Podrías reformular tu pregunta?",
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_cost_usd": 0
        }