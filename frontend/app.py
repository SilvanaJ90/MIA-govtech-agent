#!/usr/bin/env python3
# app.py
import uuid
import streamlit as st
import requests

from user_dashboard import render_user_dashboard
from admin_dashboard import render_admin_dashboard

# -----------------------------
# Configuración general
# -----------------------------
st.set_page_config(page_title="MIA - Atención Ciudadana", page_icon="🏛️", layout="wide")
API_URL = "http://127.0.0.1:5000/api/auth"  # AJUSTA si tu API está en otra ruta

# -----------------------------
# Estado de sesión inicial / defaults (inicializamos aquí)
# -----------------------------
defaults = {
    "authenticated": False,
    "role": None,
    "email": None,
    # flags para el entorno MIA
    "logged_in": False,
    "citizen_id": None,
    "citizen_name": None,
    "citizen_email": None,
    # dashboard / mia
    "metrics": {'llm_calls': 0, 'derivations': 0, 'appointments': 0},
    "chat_history": [{"role": "assistant", "text": "¡Hola! Soy MIA. ¿En qué te puedo ayudar hoy?"}],
    "current_section": "inicio",
    "pending_appointment": None,
    "show_confirmation": False,
    "last_confirmation": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------
# Helpers de auth (API)
# -----------------------------
def api_login(email: str, password: str):
    try:
        r = requests.post(f"{API_URL}/login", json={"email": email, "password": password}, timeout=8)
    except requests.exceptions.RequestException as e:
        return False, f"No se pudo conectar con el servidor: {e}"
    try:
        data = r.json()
    except Exception:
        return False, f"Respuesta inválida del servidor: {r.text}"
    if r.status_code == 200 and data.get("status") == "success":
        return True, data.get("user")
    return False, data.get("message", f"Error {r.status_code}")

def api_register(first_name: str, last_name: str, email: str, password: str):
    payload = {"email": email, "password": password, "first_name": first_name, "last_name": last_name}
    try:
        r = requests.post(f"{API_URL}/register", json=payload, timeout=8)
    except requests.exceptions.RequestException as e:
        return False, f"No se pudo conectar con el servidor: {e}"
    try:
        data = r.json()
    except Exception:
        return False, f"Respuesta inválida del servidor: {r.text}"
    if r.status_code in (200, 201) and data.get("status") == "success":
        return True, data.get("user") or "Usuario registrado"
    return False, data.get("message", f"Error {r.status_code}")

# -----------------------------
# Interfaz de autenticación (simple)
# -----------------------------
def render_auth_forms():
    st.title("🏛️ MIA — Iniciar sesión")
    st.markdown("Ingresa tus credenciales o crea una cuenta.")

    tab_login, tab_register = st.tabs(["🔐 Iniciar sesión", "📝 Registrarse"])

    with tab_login:
        with st.form(key="login_form"):
            email = st.text_input("Correo electrónico", key="auth_email")
            password = st.text_input("Contraseña", type="password", key="auth_password")
            submitted = st.form_submit_button("Entrar")
        if submitted:
            ok, payload = api_login(email.strip(), password.strip())
            if ok:
                user = payload
                st.session_state.authenticated = True
                st.session_state.role = user.get("type", "user")
                st.session_state.email = user.get("email")
                # si es user, activar entorno MIA
                if st.session_state.role == "user":
                    st.session_state.logged_in = True
                    st.session_state.citizen_id = user.get("id", str(uuid.uuid4()))
                    st.session_state.citizen_name = f"{user.get('first_name','')} {user.get('last_name','')}".strip() or user.get("email")
                    st.session_state.citizen_email = user.get("email")
                    st.success(f"¡Bienvenido/a, {st.session_state.citizen_name}!")
                    st.rerun()
                else:
                    st.success("Inicio de sesión correcto. Redirigiendo...")
                    st.rerun()
            else:
                st.error(payload)

    with tab_register:
        with st.form(key="register_form"):
            first_name = st.text_input("Nombre", key="reg_first_name")
            last_name = st.text_input("Apellido", key="reg_last_name")
            email_reg = st.text_input("Correo electrónico", key="reg_email")
            password_reg = st.text_input("Contraseña", type="password", key="reg_password")
            submit_reg = st.form_submit_button("Registrarme")
        if submit_reg:
            missing = [n for n, v in [("Nombre", first_name), ("Apellido", last_name), ("Correo electrónico", email_reg), ("Contraseña", password_reg)] if not v or not v.strip()]
            if missing:
                st.error(f"Faltan campos: {', '.join(missing)}")
            else:
                ok, created = api_register(first_name.strip(), last_name.strip(), email_reg.strip(), password_reg.strip())
                if ok:
                    st.success("Usuario registrado correctamente.")
                    # si la API devolvió el user y es user, iniciar sesión automático
                    if isinstance(created, dict) and created.get("type") == "user":
                        st.session_state.authenticated = True
                        st.session_state.role = created.get("type", "user")
                        st.session_state.email = created.get("email")
                        st.session_state.logged_in = True
                        st.session_state.citizen_id = created.get("id", str(uuid.uuid4()))
                        st.session_state.citizen_name = f"{created.get('first_name','')} {created.get('last_name','')}".strip() or created.get("email")
                        st.session_state.citizen_email = created.get("email")
                        st.success(f"¡Bienvenido/a, {st.session_state.citizen_name}!")
                        st.rerun()
                    else:
                        st.info("Ahora puedes iniciar sesión con tu correo y contraseña.")

# -----------------------------
# Dispatcher principal
# -----------------------------
# Si admin autenticado -> panel admin
if st.session_state.get("authenticated", False) and st.session_state.get("role") == "admin":
    render_admin_dashboard()
else:
    # si usuario ciudadano logueado -> render user dashboard (chat, citas, etc.)
    if st.session_state.get("logged_in", False):
        render_user_dashboard()   # función completa definida en user_dashboard.py
    else:
        render_auth_forms()
