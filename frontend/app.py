#!/usr/bin/env python3
"""
app.py - Main entry point for MIA GovTech Agent (Streamlit frontend)
"""

import streamlit as st
from login import login_page
from admin_dashboard import render_admin_dashboard
from user_dashboard import render_user_dashboard

# ------------------------------
# Streamlit configuration
# ------------------------------
st.set_page_config(
    page_title="MIA — Agente IA para Atención Ciudadana",
    page_icon="🏛️",
    layout="wide",
)

# ------------------------------
# Router logic
# ------------------------------
if "token" not in st.session_state:
    login_page()
else:
    role = st.session_state.get("role", "user")
    if role == "admin":
        render_admin_dashboard()
    else:
        render_user_dashboard()
