import streamlit as st
from datetime import datetime

def render_user_dashboard():
    st.title("🤖 MIA — Atención Ciudadana")
    st.markdown("Bienvenido/a al asistente virtual. Realiza tus consultas o trámites aquí.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Mostrar historial
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    prompt = st.chat_input("Escribe tu pregunta...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Simular respuesta (aquí luego conectas al backend/chatbot)
        response = "Gracias por tu consulta. MIA está procesando tu solicitud..."
        st.session_state.chat_history.append({"role": "assistant", "text": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    st.sidebar.markdown("---")
    st.sidebar.caption(f"🕒 Sesión activa: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")