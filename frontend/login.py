import streamlit as st
from utils.api_client import api_login, api_register

def login_page():
    st.title("🔐 Iniciar Sesión - MIA")
    option = st.radio("Selecciona una opción", ["Iniciar Sesión", "Registrarse"])

    email = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")

    if option == "Registrarse":
        first_name = st.text_input("Nombre")
        last_name = st.text_input("Apellido")

    if st.button(option):
        if option == "Iniciar Sesión":
            data, code = api_login(email, password)
            if code == 200:
                st.session_state["token"] = data["token"]
                st.session_state["role"] = data["role"]
                st.session_state["email"] = data["email"]
                st.success("Sesión iniciada correctamente ✅")
                st.rerun()
            else:
                st.error(data.get("error", "Error al iniciar sesión"))
        else:
            data, code = api_register(email, password, first_name, last_name)
            if code == 201:
                st.success("Registro exitoso ✅ — ahora puedes iniciar sesión.")
            else:
                st.error(data.get("error", "Error al registrar usuario"))
