#!/usr/bin/env python3
import streamlit as st
import os
from datetime import datetime
from user_dashboard import render_user_dashboard
from admin_dashboard import render_admin_dashboard

# -----------------------------
# Configuración general
# -----------------------------
st.set_page_config(page_title="MIA - Atención Ciudadana", page_icon="🏛️", layout="wide")

# -----------------------------
# Simulación de usuarios (puedes conectar luego a DB)
# -----------------------------
USERS = {
    "admin@mia.gov": {"password": "admin123", "role": "admin"},
    "user@mia.gov": {"password": "user123", "role": "user"},
}

# -----------------------------
# Estado de sesión
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "email" not in st.session_state:
    st.session_state.email = None

# -----------------------------
# Función de login
# -----------------------------
def login(email, password):
    user = USERS.get(email)
    if user and user["password"] == password:
        st.session_state.authenticated = True
        st.session_state.role = user["role"]
        st.session_state.email = email
        st.success(f"Inicio de sesión exitoso como {user['role'].capitalize()}")
        st.rerun()
    else:
        st.error("Credenciales incorrectas. Intenta nuevamente.")

# -----------------------------
# Función de logout
# -----------------------------
def logout():
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.email = None
    st.rerun()

# -----------------------------
# Interfaz de inicio de sesión
# -----------------------------
if not st.session_state.authenticated:
    st.title("🏛️ MIA — Agente IA para Atención Ciudadana")
    st.markdown("Inicia sesión para acceder al sistema.")

    email = st.text_input("Correo electrónico", placeholder="ejemplo@mia.gov")
    password = st.text_input("Contraseña", type="password", placeholder="********")

    if st.button("Iniciar sesión"):
        login(email, password)

    st.caption("Sistema GovTech — Acceso seguro para ciudadanos y administradores.")
else:
    st.sidebar.success(f"Sesión iniciada como: {st.session_state.email}")
    st.sidebar.button("Cerrar sesión", on_click=logout)

    if st.session_state.role == "user":
        render_user_dashboard()
    elif st.session_state.role == "admin":
        render_admin_dashboard()
