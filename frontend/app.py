#!/usr/bin/env python3
"""
Home.py - Streamlit app for MIA (public chatbot).
Uses real backend logic (memory, chain, docsearch) for responses.
"""

import sys
import os
from datetime import datetime
import streamlit as st

# ------------------------------
# Add backend/chatbot to path
# ------------------------------
BACKEND_CHATBOT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "backend", "chatbot")
)
if BACKEND_CHATBOT_PATH not in sys.path:
    sys.path.append(BACKEND_CHATBOT_PATH)

DOCS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))

# ------------------------------
# Import backend modules
# ------------------------------
try:
    from memory import memory
    from chain import generate_response_from_llm, docsearch
except Exception as e:
    st.error(f"Error al importar módulos del backend: {e}")
    memory = None
    generate_response_from_llm = None
    docsearch = None

# ------------------------------
# Streamlit configuration
# ------------------------------
st.set_page_config(
    page_title="MIA Agent Atención Ciudadana",
    page_icon="🏛️",
    layout="wide",
)

# ------------------------------
# Styles (dark sidebar, clean buttons)
# ------------------------------
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #262730;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        [data-testid="stSidebar"] .stButton button,
        [data-testid="stSidebar"] .stDownloadButton button {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: white !important;
            text-align: left !important;
            padding-left: 0.25rem !important;
        }
        [data-testid="stSidebar"] .stButton button:hover,
        [data-testid="stSidebar"] .stDownloadButton button:hover {
            color: #cccccc !important;
            background-color: transparent !important;
        }
        [data-testid="stSidebar"] input[type="text"],
        [data-testid="stSidebar"] input[type="password"],
        [data-testid="stSidebar"] textarea {
            background-color: white !important;
            color: black !important;
            border-radius: 6px !important;
        }
        .st-chat-message {
            border-radius: 8px;
            padding: 8px;
            margin: 6px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------
# Real LLM question handler
# ------------------------------
def ask_question(question: str) -> str:
    """Genera la respuesta real usando el LLM, docsearch y memory."""
    if not question or not question.strip():
        return "Por favor, proporciona una pregunta."

    try:
        docs = docsearch.similarity_search(question) if docsearch else []
    except Exception as e:
        return f"Error al buscar documentos: {e}"

    if not docs:
        return "No se encontraron documentos relevantes."

    try:
        context = memory.load_memory_variables({}).get("chat_history", []) if memory else []
    except Exception:
        context = []

    try:
        response = generate_response_from_llm(question, context, docs) if generate_response_from_llm else "Error: LLM no disponible."
    except Exception as e:
        return f"Error al generar la respuesta: {e}"

    try:
        if memory:
            memory.save_context({"human_input": question}, {"AI_response": response})
    except Exception:
        pass  # No romper si falla el guardado

    return response

# ------------------------------
# Session state initialization
# ------------------------------
if "current_section" not in st.session_state:
    st.session_state.current_section = "inicio"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    try:
        st.image("frontend/assets/img/mia.png", width=120)
    except Exception:
        pass

    st.title("MIA — Menú")
    st.markdown("Seleccione una sección:")

    if st.button("🏠 Inicio"):
        st.session_state.current_section = "inicio"
    if st.button("💬 Chat con MIA"):
        st.session_state.current_section = "mia"

    st.markdown("---")
    st.subheader("📄 Documentos")

    # Ruta del documento PDF real
    pdf_path = os.path.join(DOCS_PATH, "Politica_Etica_Transparencia_Privacidad_Chatbot_MSI.pdf")

    # Verificar existencia del PDF y mostrar botón de descarga
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()
            st.download_button(
                label="📘 Política, Ética, Transparencia y Privacidad — MIA",
                data=pdf_data,
                file_name="Politica_Etica_Transparencia_Privacidad_Chatbot_MSI.pdf",
                mime="application/pdf",
            )
    else:
        st.warning("⚠️ No se encontró el documento PDF en la carpeta docs.")

    st.markdown("---")
    st.caption("MIA — Agente IA público. Disponible 24/7.")

# ------------------------------
# Render Inicio
# ------------------------------
def render_inicio():
    st.write("# Bienvenido a MIA Agente IA para Atención Ciudadana ✨")
    st.markdown(
        """
        MIA Agent es una plataforma de atención ciudadana que responde preguntas, gestiona turnos y facilita trámites de manera automatizada.
        """
    )

    st.markdown("### 📈 Métricas públicas (ejemplo)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Consultas hoy", "1,248", "+5%")
    c2.metric("Resolución automática", "74%")
    c3.metric("Casos derivados", "312")

    st.markdown("---")
    st.info("Selecciona **Chat con MIA** en la barra lateral para iniciar una conversación.")

# ------------------------------
# Render Chatbot MIA (real)
# ------------------------------
def render_mia_agent():
    st.header("Chat con MIA")
    st.markdown(
        "Pregunta lo que necesites sobre trámites, licencias o información municipal. "
        "MIA responderá automáticamente o derivará tu caso cuando sea necesario."
    )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg.get("role", "user")):
            st.markdown(msg.get("text", ""))

    prompt = st.chat_input("Escribe tu pregunta aquí...")
    if not prompt:
        return

    user_msg = {"role": "user", "text": prompt}
    st.session_state.chat_history.append(user_msg)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("MIA está pensando..."):
        response = ask_question(prompt)

    assistant_msg = {"role": "assistant", "text": response}
    st.session_state.chat_history.append(assistant_msg)
    with st.chat_message("assistant"):
        st.markdown(response)

# ------------------------------
# Dispatcher
# ------------------------------
if st.session_state.current_section == "inicio":
    render_inicio()
elif st.session_state.current_section == "mia":
    render_mia_agent()
else:
    render_inicio()

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.caption("© 2025 MIA — Agente IA para Atención Ciudadana | GovTech Demo")
