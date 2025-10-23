import streamlit as st
import os
from datetime import datetime

def render_admin_dashboard():
    st.title("📊 Panel de Administración — MIA")
    st.markdown("Bienvenido, administrador. Aquí puedes consultar métricas y documentos oficiales.")

    # Métricas básicas
    c1, c2, c3 = st.columns(3)
    c1.metric("Consultas totales", "8,462", "+12%")
    c2.metric("Resolución automática", "78%")
    c3.metric("Casos derivados", "412")

    st.markdown("### 🗂️ Documentos oficiales")

    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "Politica_Etica_Transparencia_Privacidad_Chatbot_MSI.pdf"))
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()
            st.download_button(
                label="📘 Descargar Política, Ética y Privacidad",
                data=pdf_data,
                file_name="Politica_Etica_Transparencia_Privacidad_Chatbot_MSI.pdf",
                mime="application/pdf",
            )
    else:
        st.warning("⚠️ Documento PDF no encontrado en carpeta docs.")

    st.markdown("### 🧠 Estado del Chatbot")
    st.info("LLM: Activo ✅ — VectorDB: 132 documentos cargados — Última actualización: 20/10/2025")

    st.sidebar.markdown("---")
    st.sidebar.caption(f"👤 Admin conectado — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
