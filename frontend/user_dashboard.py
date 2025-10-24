#!/usr/bin/env python3
# user_dashboard.py
import os
from datetime import datetime, timedelta
from typing import Dict
import streamlit as st
# -----------------------------
# MOCK: Query Processor mínimo para probar la app (DEV only)
# -----------------------------
from typing import Dict, Any
import random
from datetime import date, timedelta

class MockAppointmentManager:
    def __init__(self):
        # Disponibilidad simple: fechas próximas con 3 slots cada una
        today = date.today()
        self.availability = {}
        for i in range(1, 6):  # próximos 5 días
            d = str(today + timedelta(days=i))
            self.availability[d] = {"09:00": 3, "10:00": 2, "11:00": 1}

    def get_available_slots(self, date_str: str) -> Dict[str, int]:
        return self.availability.get(date_str, {})

    def schedule_appointment(self, citizen_id: str, citizen_name: str, citizen_email: str,
                             procedure: str, date: str, time: str, notes: str):
        slots = self.get_available_slots(date)
        if not slots or time not in slots or slots[time] <= 0:
            return False, "La hora no está disponible", None
        # reservar 1 slot
        self.availability[date][time] -= 1
        appointment = {
            "id": f"APP-{random.randint(1000,9999)}",
            "citizen_id": citizen_id,
            "citizen_name": citizen_name,
            "citizen_email": citizen_email,
            "procedure": procedure,
            "date": date,
            "time": time,
            "notes": notes
        }
        message = f"Cita agendada: {appointment['date']} {appointment['time']} (ID: {appointment['id']})"
        return True, message, appointment

class MockQueryProcessor:
    def __init__(self):
        self.appointment_manager = MockAppointmentManager()

    def process_query(self, query: str, docsearch=None, citizen_id=None, citizen_name=None, citizen_email=None) -> Dict[str, Any]:
        q = (query or "").lower().strip()

        # 1) Si pregunta por "cita" o "turno" -> ofrecer appointment
        if any(term in q for term in ["cita", "turno", "agendar", "agendar cita", "solicitar turno"]):
            # sugerimos un procedimiento y datos de ejemplo
            appointment_data = {
                "procedure": "Solicitud de licencia de construcción",
                "available_dates": list(self.appointment_manager.availability.keys())
            }
            return {
                "primary_response": "Puedo ayudarte a agendar una cita. ¿Deseas que te muestre fechas disponibles?",
                "actions": ["offer_appointment"],
                "appointment_data": appointment_data
            }

        # 2) Si contiene palabras de reclamo/problema -> crear caso complejo
        if any(term in q for term in ["reclamo", "problema", "queja", "incidente", "no me atendieron"]):
            case_id = f"CASE-{random.randint(10000,99999)}"
            case = {
                "id": case_id,
                "citizen_id": citizen_id or "unknown",
                "citizen_name": citizen_name or "Ciudadano",
                "citizen_email": citizen_email or "sin-email",
                "department": "Atención al Ciudadano",
                "priority": "medium",
                "summary": q[:200]
            }
            return {
                "primary_response": (
                    "He identificado que tu caso necesita derivación a un funcionario. "
                    "Estoy generando el caso y te doy el número de referencia."
                ),
                "actions": ["create_complex_case"],
                "case": case
            }

        # 3) Respuesta informativa básica (simulación RAG/LLM)
        # Podemos simular búsqueda en documentos: si pregunta por "horarios" devolvemos algo útil
        if "horario" in q or "horarios" in q:
            return {
                "primary_response": "El horario de atención es de lunes a viernes de 8:00 a 17:00. ¿Quieres que agende una cita?"
            }

        # 4) Respuesta por defecto
        return {
            "primary_response": "Claro — puedo ayudarte con ese tema. ¿Puedes darme más detalles o decir si quieres agendar una cita?"
        }

# Instancia de prueba (reemplaza query_processor = None con esto)
query_processor = MockQueryProcessor()
docsearch = None


# -----------------------------
# Placeholders / conectar con tu RAG/LLM
# -----------------------------
# TODO: Conectar query_processor real (RAG, LLM, appointment_manager, etc.)
query_processor = None
docsearch = None

# Asegurar estado mínimo local (por si se llama directamente)
if "metrics" not in st.session_state:
    st.session_state.metrics = {'llm_calls': 0, 'derivations': 0, 'appointments': 0}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "text": "¡Hola! Soy MIA. ¿En qué te puedo ayudar hoy?"}]
if "current_section" not in st.session_state:
    st.session_state.current_section = "mia_agent"

def save_case_to_db(case_data: Dict):
    """Guardar caso en DB (placeholder)."""
    # TODO: Implementar persistencia real (SQLite/Postgres)
    print("Guardar caso:", case_data)

def save_appointment_to_db(appointment: Dict):
    """Guardar cita en DB (placeholder)."""
    # TODO: Implementar persistencia real
    print("Guardar appointment:", appointment)

# ------------------------------
# Lógica central de respuesta
# ------------------------------
def ask_question(prompt: str) -> str:
    if query_processor is None:
        return "El sistema no está inicializado. Contacte a soporte."

    st.session_state.metrics['llm_calls'] += 1

    # contrato de ejemplo; ajusta a tu query_processor
    response_data = query_processor.process_query(
        query=prompt,
        docsearch=docsearch,
        citizen_id=st.session_state.get("citizen_id"),
        citizen_name=st.session_state.get("citizen_name"),
        citizen_email=st.session_state.get("citizen_email"),
    )

    if 'actions' in response_data:
        if 'offer_appointment' in response_data['actions']:
            st.session_state.pending_appointment = response_data['appointment_data']
            st.session_state.current_section = "appointment_form"
            st.rerun()

        if 'create_complex_case' in response_data['actions']:
            case_data = response_data.get('case')
            st.session_state.metrics['derivations'] += 1
            if not case_data:
                return "Lo siento, hubo un error al generar el caso."
            save_case_to_db(case_data)
            return (
                f"🚨 Caso derivado. ID: {case_data.get('id','N/A')}. "
                f"Se ha notificado al departamento {case_data.get('department','-')}."
            )

    return response_data.get('primary_response', "No tengo una respuesta ahora mismo.")

# ------------------------------
# Renderizado: formulario de cita
# ------------------------------
def render_appointment_form(pending_appointment: Dict):
    st.subheader("🗓️ Formulario de Cita para Trámite")
    st.info(f"Trámite: {pending_appointment.get('procedure', 'No especificado')}")
    col1, col2 = st.columns(2)
    today = datetime.now().date()

    try:
        avail = query_processor.appointment_manager.availability
    except Exception:
        avail = {}

    with col1:
        default_date = today + timedelta(days=1)
        selected_date = st.date_input("Selecciona una fecha", default_date, min_value=today + timedelta(days=1))
    with col2:
        try:
            times = list(query_processor.appointment_manager.get_available_slots(str(selected_date)).keys())
        except Exception:
            times = ["No hay horas"]
        selected_time = st.selectbox("Selecciona una hora", times)

    procedure = st.text_input("Trámite confirmado:", pending_appointment.get('procedure','Trámite no especificado'))
    notes = st.text_area("Notas adicionales (opcional)")

    if st.button("✅ Confirmar Cita"):
        if selected_time == "No hay horas":
            st.error("Por favor, selecciona una fecha y hora válidas.")
            return
        success, message, appointment = query_processor.appointment_manager.schedule_appointment(
            citizen_id=st.session_state.get("citizen_id"),
            citizen_name=st.session_state.get("citizen_name"),
            citizen_email=st.session_state.get("citizen_email"),
            procedure=procedure,
            date=str(selected_date),
            time=selected_time,
            notes=notes
        )
        if success:
            save_appointment_to_db(appointment)
            st.session_state.last_confirmation = f"✅ ¡Cita confirmada!\n\n{message}"
            st.session_state.show_confirmation = True
            st.session_state.pending_appointment = None
            st.session_state.metrics['appointments'] += 1
            st.session_state.current_section = "mia_agent"
            st.rerun()
        else:
            st.error(f"Error al confirmar cita: {message}")

# ------------------------------
# Renderizado: chat MIA
# ------------------------------
def render_mia_agent():
    st.header("Chat con MIA 🏛️")
    st.markdown("Pregunta lo que necesites. MIA gestionará trámites, turnos y derivaciones.")

    if st.session_state.get("show_confirmation"):
        st.success(st.session_state.get("last_confirmation"))
        st.balloons()
        st.session_state.show_confirmation = False

    for msg in st.session_state.get("chat_history", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    prompt = st.chat_input("Escribe tu pregunta aquí...")
    if not prompt:
        return

    st.session_state.chat_history.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("MIA está analizando la intención..."):
        answer = ask_question(prompt)

    if st.session_state.get("current_section", "mia_agent") == "mia_agent":
        st.session_state.chat_history.append({"role": "assistant", "text": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

# ------------------------------
# Sidebar y métricas del usuario
# ------------------------------
def render_sidebar_and_metrics():
    with st.sidebar:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "assets", "img", "mia.png")
            st.image(image_path, width=120)
        except Exception:
            st.header("🏛️ MIA")

        st.title("MIA — Menú")
        if st.button("🏠 Inicio"):
            st.session_state.current_section = "inicio"
            st.rerun()
        if st.button("💬 Chat con MIA"):
            st.session_state.current_section = "mia_agent"
            st.rerun()

        st.markdown("---")
        st.subheader("📊 Métricas")
        c1, c2, c3 = st.columns(3)
        c1.metric("LLM calls", st.session_state.metrics.get('llm_calls',0))
        c2.metric("Turnos", st.session_state.metrics.get('appointments',0))
        c3.metric("Derivaciones", st.session_state.metrics.get('derivations',0))

        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            # limpiar sesión MIA
            keys = ["logged_in","citizen_id","citizen_name","citizen_email","authenticated","email","role"]
            for k in keys:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state.current_section = "inicio"
            st.rerun()

# ------------------------------
# Función que exportamos al main
# ------------------------------
def render_user_dashboard():
    """Punto de entrada para la UI del usuario (chat, citas, etc.)."""
    render_sidebar_and_metrics()

    section = st.session_state.get("current_section", "mia_agent")
    if section == "mia_agent":
        render_mia_agent()
    elif section == "appointment_form":
        pending = st.session_state.get("pending_appointment")
        if pending:
            render_appointment_form(pending)
        else:
            st.warning("No hay cita pendiente. Volviendo al chat.")
            st.session_state.current_section = "mia_agent"
            st.rerun()
    else:
        st.header("🏛️ Bienvenido")
        st.markdown("Selecciona una opción en el menú lateral para comenzar.")
