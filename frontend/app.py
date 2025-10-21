# frontend/app.py (Versión Integrada)
"""
Home.py - Streamlit app for MIA (public chatbot).
Incluye sistema de navegación, gestión de citas y derivación de casos.
"""
#!/usr/bin/env python3
import sys
import os
from datetime import datetime, timedelta # Necesitamos timedelta para fechas
import streamlit as st
import logging # Para un mejor manejo de errores/info
from typing import Optional, Dict

# --- Configuración Inicial ---
logging.basicConfig(level=logging.INFO)

# ------------------------------
# 1. ADD BACKEND/CHATBOT TO PATH
# ------------------------------
# (Añadir backend/chatbot al path)
BACKEND_CHATBOT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "backend", "chatbot")
)
if BACKEND_CHATBOT_PATH not in sys.path:
    sys.path.append(BACKEND_CHATBOT_PATH)

# ------------------------------
# 2. CARGA DE .ENV 
# ------------------------------
try:
    from dotenv import load_dotenv
    from os.path import join, dirname, abspath
    current_dir = dirname(abspath(__file__))
    dotenv_path = join(current_dir, '..', '.env') 
    load_dotenv(dotenv_path=dotenv_path) 
except ImportError:
    pass
except Exception as e:
    st.error(f"Error al cargar variables de entorno: {e}")

# ------------------------------
# 3. IMPORTACIÓN DE MÓDULOS DE BACKEND Y NUEVA LÓGICA
# ------------------------------
try:
    from memory import memory
    from chain import classify_intent,generate_response_from_llm, docsearch # <-- Tu cadena existente
    # Importar la nueva lógica de gestión
    from appointment_manager import (
        QueryProcessor, CaseType, Appointment, AppointmentManager, CaseRouter, DepartmentType  # Importar todo
    )
    # Inicialización de QueryProcessor (asumiendo que tiene la lógica de citas)
    query_processor = QueryProcessor() 
    
except Exception as e:
    # Capturar errores durante la inicialización, como el de la ruta de FAISS.
    st.error(f"Error al inicializar módulos del backend. Revisa logs de terminal: {e}")
    st.stop() # Detener para que el usuario solucione el error


st.set_page_config(
    page_title="MIA - Agente de Atención Ciudadana",
    page_icon="🏛️",
    layout="wide",
)

# ------------------------------
# 4. STREAMLIT STATE INICIALIZACIÓN
# ------------------------------
# Inicialización de Sesión (Manejo de estado)
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "text": "¡Hola! Soy MIA, la asistente virtual de tu municipio. ¿En qué trámite o consulta te puedo ayudar hoy?"}
    ]
if 'metrics' not in st.session_state:
    st.session_state.metrics = {'llm_calls': 0, 'derivations': 0, 'appointments': 0}   
if 'current_section' not in st.session_state:
    st.session_state.current_section = "mia_agent" # Se inicia directamente en el chat
# Datos del ciudadano (simulados para el MVP)
if 'citizen_id' not in st.session_state: # Para simular la sesión del usuario
    st.session_state.citizen_id = "C-4235"
if 'citizen_name' not in st.session_state:
    st.session_state.citizen_name = "Ciudadano Invitado"
if 'citizen_email' not in st.session_state:
    st.session_state.citizen_email = "invitado@municipio.gov"
# Estado para manejar citas pendientes de confirmación
if 'pending_appointment' not in st.session_state:
    st.session_state.pending_appointment = None


# ------------------------------
# 5. ESTILOS (Combinando el estilo original con accesibilidad)
# ------------------------------

st.markdown(
    """
    <style>
        /* Estilos del Sidebar: Oscuro (#262730) y texto blanco */
        [data-testid="stSidebar"] {
            background-color: #262730;
            /* ACCESIBILIDAD: Añade un rol ARIA para la navegación principal */
            role: "navigation"; 
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Estilos de botones dentro del Sidebar: Transparentes y texto blanco */
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

        /* Estilos de campos de entrada en el Sidebar (si aplican) */
        [data-testid="stSidebar"] input[type="text"],
        [data-testid="stSidebar"] input[type="password"],
        [data-testid="stSidebar"] textarea {
            background-color: white !important;
            color: black !important;
            border-radius: 6px !important;
        }
        
        /* Estilos de botones PRIMARIOS (fuera del sidebar) para ALTO CONTRASTE */
        .stButton>button { 
            background-color: #007bff; /* Azul primario con buen contraste */
            color: white; 
            border-radius: 8px;
            font-weight: bold;
        }
        
        /* Estilos de las burbujas de chat */
        .st-chat-message {
            border-radius: 8px;
            padding: 8px;
            margin: 6px 0;
        }
        
    </style>
    """, 
    unsafe_allow_html=True
)
    
# ------------------------------
# 6. FUNCIÓN CENTRAL DE RESPUESTA (Modificación)
# ------------------------------
def ask_question(prompt: str) -> str:
    """Procesa la pregunta, maneja acciones (citas/casos) y devuelve la respuesta final."""
    if not query_processor:
        return "El sistema no está inicializado. Contacte a soporte."
    
    st.session_state.metrics['llm_calls'] += 1 # Métricas
    
    response_data = query_processor.process_query(
        query=prompt,
        docsearch=docsearch, # Se pasa la base de datos vectorial para contexto
        #chat_chain=generate_response_from_llm # Se pasa la función de la cadena
        citizen_id=st.session_state.citizen_id, 
        citizen_name=st.session_state.citizen_name, 
        citizen_email=st.session_state.citizen_email,
    )
    
    
    # 2. Manejar acciones (Turnos y Derivación)
    if 'actions' in response_data:
        if 'offer_appointment' in response_data['actions']:
            st.session_state.pending_appointment = response_data['appointment_data']
            st.session_state.current_section = "appointment_form"
            st.rerun() # Detiene el chat y va al formulario
            
        elif 'create_complex_case' in response_data['actions']:
            case_data = response_data['case']
            st.session_state.metrics['derivations'] += 1 # Métricas
            
            # Devuelve una respuesta formal al usuario sobre la derivación
            return (
                f"🚨 **¡Caso Complejo Derivado!** 🚨\n\n"
                f"He identificado que tu consulta requiere la intervención de un funcionario. "
                f"Hemos creado el **Caso N° {case_data['id']}** (Prioridad: {case_data['priority'].upper()}) "
                f"y ha sido asignado a **{case_data['department']}**. "
                f"Un agente se comunicará contigo pronto al correo {st.session_state.citizen_email}."
            )
            
    # 3. Si no hay acción especial, devuelve la respuesta de información simple
    return response_data['primary_response']

   



# ------------------------------
# 7. RENDERIZADO DE GESTIÓN DE CITAS (Nueva Función)
# ------------------------------
def render_appointment_form(pending_appointment: Dict):
    st.subheader("🗓️ Formulario de Cita para Trámite")
    st.info(f"Trámite: {pending_appointment.get('procedure', 'No especificado')}")
    
    # ... (Aquí va la lógica completa del formulario de citas de new_app.py) ...
    # Nota: Simplificaremos el renderizado por concisión, pero aquí iría la implementación
    # de las fechas disponibles de tu 'appointment_manager.py'.
    
    col1, col2 = st.columns(2)
    today = datetime.now().date()
    
    # Obtener fechas disponibles (simulación, ya que no puedo acceder al módulo completo)
    available_dates_str = list(query_processor.appointment_manager.availability.keys())
    
    with col1:
        # Usar la primera fecha disponible como valor inicial, o hoy + 1 día
        default_date = today + timedelta(days=1)
        selected_date = st.date_input(
            "Selecciona una fecha",
            default_date,
            min_value=today + timedelta(days=1)
        )
    
    with col2:
        # Obtener horas disponibles para la fecha seleccionada
        try:
            available_times = list(query_processor.appointment_manager.get_available_slots(str(selected_date)).keys())
        except KeyError:
            available_times = ["No hay horas"]
            
        selected_time = st.selectbox(
            "Selecciona una hora",
            available_times
        )

    procedure = st.text_input("Trámite Confirmado:", pending_appointment.get('procedure', 'Trámite no especificado'))
    notes = st.text_area("Notas adicionales (opcional)")
    
    if st.button("✅ Confirmar Cita", type="primary"):
        if selected_time == "No hay horas":
            st.error("Por favor, selecciona una fecha y hora válidas.")
            return

        success, message, appointment = query_processor.appointment_manager.schedule_appointment(
            citizen_id=st.session_state.citizen_id,
            citizen_name=st.session_state.citizen_name,
            citizen_email=st.session_state.citizen_email,
            procedure=procedure,
            date=str(selected_date),
            time=selected_time,
            notes=notes
        )
        
        if success:
            st.success(f"¡Cita confirmada! {message}. Regresando al chat.")
            st.session_state.pending_appointment = None
            st.session_state.metrics['appointments'] += 1 # Métricas
            st.session_state.current_section = "mia_agent"
            st.rerun()
        else:
            st.error(f"Error al confirmar cita: {message}")


# ------------------------------
# 7. RENDERIZADO DEL CHAT (Modificación)
# ------------------------------
def render_mia_agent():
    st.header("Chat con MIA 🏛️")
    st.markdown("Pregunta lo que necesites. MIA gestionará trámites, turnos y derivaciones.")
    
    # ... (Lógica de chat existente) ...
    # Renderiza todo el historial de chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    prompt = st.chat_input("Escribe tu pregunta aquí...")
    if not prompt:
        return

    # Mantiene el historial de chat (user)
    user_msg = {"role": "user", "text": prompt}
    st.session_state.chat_history.append(user_msg)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llama a la función central (ask_question) que maneja el flujo de trabajo
    with st.spinner("MIA está pensando y analizando la intención..."):
        response = ask_question(prompt)
        
    # Mantiene el historial de chat (assistant) si no ha redirigido a un formulario
    if st.session_state.current_section == "mia_agent":
        assistant_msg = {"role": "assistant", "text": response}
        st.session_state.chat_history.append(assistant_msg)
        with st.chat_message("assistant"):
            st.markdown(response)

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    try:
        # Intenta cargar una imagen simulada (reemplazar con tu ruta real si existe)
        st.image("img/mia.png", width=120) 
    except Exception:
        # Si la imagen no carga, usa un placeholder
        st.header("🏛️ MIA")

    st.title("MIA — Menú")
    st.markdown("Seleccione una sección:")

    # Botones de navegación
    if st.button("🏠 Inicio"):
        st.session_state.current_section = "inicio"
    if st.button("💬 Chat con MIA"):
        st.session_state.current_section = "mia_agent"

    # Botón de formulario de cita (visible solo si está en modo chat y hay una cita pendiente)
    if st.session_state.pending_appointment and st.session_state.current_section == "mia":
        if st.button("➡️ Agendar Cita (Pendiente)", type="secondary"):
            st.session_state.current_section = "appointment_form"
            st.rerun()


    st.markdown("---")
    st.subheader("📄 Documentos")

    manual_ethics = (
        "Manual de Ética — MIA\n\nTransparencia, privacidad y uso responsable de IA."
    )
    manual_privacy = (
        "Política de Privacidad — MIA\n\nTratamiento de datos y protección ciudadana."
    )

    # Botones de descarga
    st.download_button(
        label="📘 Manual de Ética",
        data=manual_ethics.encode("utf-8"),
        file_name=f"manual_etica_mia_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
    )

    st.download_button(
        label="🔒 Política de Privacidad",
        data=manual_privacy.encode("utf-8"),
        file_name=f"politica_privacidad_mia_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
    )

    st.markdown("---")
# ------------------------------
# 8. Renderizado de Métricas y Flujo Principal
# ------------------------------

def render_metrics():
    st.sidebar.subheader("📊 Métricas de Uso")
    col1, col2, col3 = st.sidebar.columns(3)
    
    col1.metric("Llamadas LLM", st.session_state.metrics['llm_calls'])
    col2.metric("Turnos", st.session_state.metrics['appointments'])
    col3.metric("Derivaciones", st.session_state.metrics['derivations'])
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Reiniciar Conversación", help="Borra el historial de chat y métricas"):
        st.session_state.chat_history = [
            {"role": "assistant", "text": "¡Hola! He reiniciado mi memoria. ¿En qué te puedo ayudar?"}
        ]
        st.session_state.metrics = {'llm_calls': 0, 'derivations': 0, 'appointments': 0}
        st.session_state.current_section = "mia_agent"
        st.session_state.pending_appointment = None
        st.rerun()

# ------------------------------
# 9. DISPATCHER (Flujo de la App)
# ------------------------------
render_metrics()

if st.session_state.current_section == "mia_agent":
    render_mia_agent()
elif st.session_state.current_section == "appointment_form":
    render_appointment_form(st.session_state.pending_appointment)
# Añade otros else/elif si quieres más secciones (como un formulario de derivación)

