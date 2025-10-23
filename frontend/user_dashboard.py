import streamlit as st
import requests
import os

API_BASE = "http://127.0.0.1:5000"

def render_user_dashboard():
    st.title("💬 Chat con MIA — Atención Ciudadana")
    st.caption("Consulta sobre trámites, licencias o servicios municipales")

    # Sidebar
    with st.sidebar:
        st.image("img/mia.png", width=120)
        st.subheader("Opciones del Ciudadano")
        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

        st.markdown("---")
        st.subheader("📄 Documentos Oficiales")

        doc_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "docs", "Politica_Etica_Transparencia_Privacidad_Chatbot_MSI.pdf")
        )

        if os.path.exists(doc_path):
            with open(doc_path, "rb") as f:
                st.download_button(
                    label="📘 Política de Ética, Transparencia y Privacidad",
                    data=f,
                    file_name="Politica_Etica_Transparencia_Privacidad_Chatbot_MSI.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Documento no encontrado en la carpeta /docs")

    # Chat Section
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown("### 🤖 Inicia tu conversación")
    user_input = st.chat_input("Escribe tu pregunta aquí...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "text": user_input})

        with st.spinner("MIA está respondiendo..."):
            try:
                headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
                res = requests.post(
                    f"{API_BASE}/chat",
                    json={"message": user_input},
                    headers=headers
                )
                if res.status_code == 200:
                    answer = res.json().get("response", "No hay respuesta disponible.")
                else:
                    answer = "Error en la comunicación con la API."
            except Exception as e:
                answer = f"Error al conectar con la API: {e}"

        st.session_state.chat_history.append({"role": "assistant", "text": answer})

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    st.markdown("---")
    st.caption("© 2025 MIA — Agente IA de Atención Ciudadana")
