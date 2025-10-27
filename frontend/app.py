# frontend/app.py (Versión Integrada)
"""
Home.py - Streamlit app for MIA (public chatbot).
Incluye sistema de navegación, gestión de citas y derivación de casos.
"""
#!/usr/bin/env python3
import sys
import os
from datetime import date, datetime, timedelta # Necesitamos timedelta para fechas
import streamlit as st
import logging # Para un mejor manejo de errores/info
from typing import Optional, Dict
import sqlite3
import pandas as pd

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

DOCS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))

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
    from chain import docsearch 
    # Importar la nueva lógica de gestión
    from appointment_manager import QueryProcessor
    # Inicialización de QueryProcessor (asumiendo que tiene la lógica de citas)
    query_processor = QueryProcessor() 
    
except Exception as e:
    # Capturar errores durante la inicialización, como el de la ruta de FAISS.
    st.error(f"Error al inicializar módulos del backend. Revisa logs de terminal: {e}")
    st.stop() # Detener para que el usuario solucione el error

import sqlite3

# ------------------------------
# AUTENTICACIÓN BÁSICA (SQLite)
# ------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "mia_users.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()


def init_user_db():
    """Crea la tabla de usuarios si no existe."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS citizens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            dni TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def init_data_tables():
    """Crea tablas de citas y casos complejos si no existen."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabla de citas
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            citizen_email TEXT,
            procedure TEXT,
            date TEXT,
            time TEXT,
            status TEXT,
            notes TEXT,
            created_at TEXT
        )
    """)
    # Tabla de casos complejos
    c.execute("""
        CREATE TABLE IF NOT EXISTS complex_cases (
            id TEXT PRIMARY KEY,
            citizen_email TEXT,
            description TEXT,
            department TEXT,
            priority TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    
def init_metrics_table():
    """Crea tabla para métricas de uso si no existe."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            total_queries INTEGER DEFAULT 0,
            appointments INTEGER DEFAULT 0,
            complex_cases INTEGER DEFAULT 0,
            tokens_used INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    
def ensure_admin_exists():
    """Verifica si existe al menos un administrador. Si no, permite crearlo desde Streamlit."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM citizens WHERE is_admin = 1")
    has_admin = c.fetchone()[0] > 0
    conn.close()

    if not has_admin:
        st.title("🧑‍💼 Configuración inicial del administrador")
        st.info("No se ha encontrado ningún usuario administrador. Crea uno para continuar.")

        with st.form("create_admin_form"):
            name = st.text_input("Nombre completo del administrador")
            email = st.text_input("Correo institucional")
            password = st.text_input("Contraseña", type="password")
            dni = st.text_input("DNI o documento de identidad")
            submitted = st.form_submit_button("Crear administrador")

            if submitted:
                if not (name and email and password and dni):
                    st.error("Por favor, completa todos los campos.")
                    return
                try:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO citizens (name, email, dni, password, is_admin) VALUES (?, ?, ?, ?, 1)",
                        (name, email, dni, password)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Administrador '{name}' creado correctamente.")
                    st.info("Ahora puedes iniciar sesión con tus credenciales.")
                    st.stop()
                except Exception as e:
                    st.error(f"Error al crear el administrador: {e}")
                    st.stop()



# Llama las inicializaciones al inicio de la app
init_user_db()
init_data_tables()
init_metrics_table()
ensure_admin_exists()

def save_appointment_to_db(appointment):
    """Guarda una cita confirmada en la base SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO appointments 
        (id, citizen_email, procedure, date, time, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        appointment.id,
        appointment.citizen_email,
        appointment.procedure,
        appointment.date,
        appointment.time,
        appointment.status,
        appointment.notes,
        appointment.created_at
    ))
    conn.commit()
    conn.close()
    update_metrics("appointments")


def save_case_to_db(case):
    """Guarda un caso complejo derivado en la base SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Convertir enums y otros tipos no serializables
    department = case.get("department")
    if not isinstance(department, str):
        department = str(department.name) if hasattr(department, "name") else str(department)

    priority = case.get("priority")
    if not isinstance(priority, str):
        priority = str(priority.name) if hasattr(priority, "name") else str(priority)

    c.execute("""
        INSERT OR REPLACE INTO complex_cases
        (id, citizen_email, description, department, priority, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        case.get("id"),
        case.get("citizen_email"),
        case.get("description"),
        department,
        priority,
        case.get("status"),
        case.get("created_at"),
    ))
    conn.commit()
    conn.close()
    update_metrics("complex_cases")


def register_user(name, email, dni, password):
    """Registra un nuevo usuario."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO citizens (name, email, dni, password) VALUES (?, ?, ?, ?)",
                  (name, email, dni, password))
        conn.commit()
        return True, "Usuario registrado correctamente."
    except sqlite3.IntegrityError:
        return False, "El correo ya está registrado."
    finally:
        conn.close()

def authenticate_user(email, password):
    """Valida credenciales."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, email, dni FROM citizens WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "name": user[1], "email": user[2], "dni": user[3]}
    return None

def update_metrics(field, increment=1):
    """Actualiza las métricas diarias en la base."""
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Crear registro del día si no existe
    c.execute("SELECT * FROM metrics WHERE date = ?", (today,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO metrics (date) VALUES (?)", (today,))
    # Actualizar campo correspondiente
    c.execute(f"UPDATE metrics SET {field} = {field} + ? WHERE date = ?", (increment, today))
    conn.commit()
    conn.close()



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
    
    update_metrics("total_queries")
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
            case_data = response_data.get('case', None)
            st.session_state.metrics['derivations'] += 1

            # 🧩 Validación preventiva
            if not case_data:
                st.warning("No se pudo generar el caso correctamente.")
                return "Lo siento, hubo un error al registrar tu caso. Intenta nuevamente."

            # Guardar el caso en la base de datos SQLite
            save_case_to_db(case_data)

            # Mensaje de confirmación visual y textual
            st.success(f"🚨 ¡Caso Complejo Derivado! 🚨\n\nID: {case_data['id']}")
            st.toast(f"Caso {case_data['id']} derivado al {case_data['department']}.", icon="⚖️")

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
            # Guardar la cita en la base de datos SQLite
            save_appointment_to_db(appointment)

            # Mensaje de confirmación al usuario
            st.session_state.last_confirmation = f"✅ ¡Cita confirmada!\n\n{message}"
            st.session_state.show_confirmation = True

            # Actualizar estado de sesión
            st.session_state.pending_appointment = None
            st.session_state.metrics['appointments'] += 1
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
    
    # Mostrar confirmación de cita si existe
    if st.session_state.get("show_confirmation", False):
        st.success(st.session_state.last_confirmation)
        st.balloons()
        st.session_state.show_confirmation = False  # Evita que se repita

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
if not st.session_state.get("is_admin"):
    with st.sidebar:
        try:
            # Ruta absoluta al archivo de imagen dentro de frontend/assets/img
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "assets", "img", "mia.png")
            st.image(image_path, width=120)
        except Exception:
            # Si la imagen no carga, usa un placeholder
            st.header("🏛️ MIA")

        st.title("MIA — Menú Ciudadano")
        st.markdown("Seleccione una sección:")

        # Botones de navegación
        if st.button("🏠 Inicio"):
            st.session_state.current_section = "inicio"
        if st.button("💬 Chat con MIA"):
            st.session_state.current_section = "mia_agent"

        # Botón de formulario de cita (solo si hay cita pendiente)
        if (
            st.session_state.pending_appointment
            and st.session_state.current_section == "mia_agent"
        ):
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

        # ------------------------------
        # BOTÓN DE CIERRE DE SESIÓN (CIUDADANO)
        # ------------------------------
        if (
            st.session_state.get("logged_in")
            and not st.session_state.get("is_admin")
            and st.session_state.get("current_section") == "mia_agent"
        ):
            st.markdown("---")
            st.caption("Sesión activa: Ciudadano")
            if st.button("🚪 Cerrar sesión"):
                for key in ["logged_in", "citizen_id", "citizen_name", "citizen_email", "is_admin"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_section = "inicio"
                st.rerun()

# ------------------------------
# 8. Renderizado de Métricas y Flujo Principal
# ------------------------------

def render_metrics():
    st.sidebar.subheader("📊 Métricas de Uso")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT SUM(total_queries), SUM(appointments), SUM(complex_cases) FROM metrics")
    data = c.fetchone() or (0, 0, 0)
    conn.close()
    
    
    col1, col2, col3 = st.sidebar.columns(3)

    col1.metric("Consultas", data[0])
    col2.metric("Citas", data[1])
    col3.metric("Casos derivados", data[2])
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Reiniciar Conversación", help="Borra el historial de conversación actual"):
        st.session_state.chat_history = [
            {"role": "assistant", "text": "¡Hola! He reiniciado mi memoria. ¿En qué te puedo ayudar?"}
        ]
        st.session_state.metrics = {'llm_calls': 0, 'derivations': 0, 'appointments': 0}
        st.session_state.current_section = "mia_agent"
        st.session_state.pending_appointment = None
        st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar sesión"):
        for key in ["logged_in", "citizen_id", "citizen_name", "citizen_email"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.current_section = "inicio"
        st.rerun()

def render_login():
    st.title("🏛️ MIA — Iniciar sesión")
    st.markdown("Por favor, ingresa tus credenciales para continuar.")

    tab_login, tab_register = st.tabs(["🔐 Iniciar sesión", "📝 Registrarse"])

    with tab_login:
        email = st.text_input("Correo electrónico", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_password")
        if st.button("Entrar", type="primary", key="login_button"):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, name, email, is_admin FROM citizens WHERE email=? AND password=?", (email, password))
            user = c.fetchone()
            conn.close()

            if user:
                st.session_state.logged_in = True
                st.session_state.citizen_id = user[0]
                st.session_state.citizen_name = user[1]
                st.session_state.citizen_email = user[2]
                st.session_state.is_admin = bool(user[3])
                st.session_state.current_section = "admin" if st.session_state.is_admin else "mia_agent"
                st.success(f"¡Bienvenido/a, {user[1]}!")
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Intenta nuevamente.")

    with tab_register:
        name = st.text_input("Nombre completo", key="register_name")
        reg_email = st.text_input("Correo de registro", key="register_email")
        dni = st.text_input("DNI", key="register_dni")
        reg_pass = st.text_input("Contraseña", type="password", key="register_password")
        if st.button("Crear cuenta", type="primary", key="register_button"):
            success, msg = register_user(name, reg_email, dni, reg_pass)
            if success:
                st.success(msg)
            else:
                st.error(msg)
                
def render_admin_panel():
    """Panel administrativo para visualizar métricas y datos del sistema."""
    st.title("🧑‍💼 Panel Administrativo - MIA")
    st.markdown("Bienvenido, **administrador**. Desde aquí puedes visualizar la actividad general del asistente y las gestiones ciudadanas realizadas.")

    st.markdown("---")

    # ------------------------------
    # MÉTRICAS DIARIAS
    # ------------------------------
    st.subheader("📈 Actividad diaria")

    conn = sqlite3.connect(DB_PATH)
    df_metrics = pd.read_sql_query("SELECT * FROM metrics ORDER BY date DESC", conn)
    df_appointments = pd.read_sql_query("SELECT * FROM appointments ORDER BY created_at DESC", conn)
    df_cases = pd.read_sql_query("SELECT * FROM complex_cases ORDER BY created_at DESC", conn)
    conn.close()

    if not df_metrics.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Consultas", int(df_metrics["total_queries"].sum()))
        col2.metric("Citas", int(df_metrics["appointments"].sum()))
        col3.metric("Casos derivados", int(df_metrics["complex_cases"].sum()))
        st.line_chart(df_metrics.set_index("date")[["total_queries", "appointments", "complex_cases"]])
    else:
        st.info("Aún no hay métricas registradas en el sistema.")

    st.markdown("---")

    # ------------------------------
    # TABLA DE CITAS
    # ------------------------------
    st.subheader("🗓️ Citas registradas")
    if not df_appointments.empty:
        df_appointments_view = df_appointments[["id", "citizen_email", "procedure", "date", "time", "status"]]
        df_appointments_view.rename(columns={
            "citizen_email": "Ciudadano",
            "procedure": "Trámite",
            "date": "Fecha",
            "time": "Hora",
            "status": "Estado"
        }, inplace=True)
        st.dataframe(df_appointments_view, use_container_width=True)
    else:
        st.info("No hay citas registradas aún.")

    st.markdown("---")

    # ------------------------------
    # TABLA DE CASOS COMPLEJOS
    # ------------------------------
    st.subheader("⚖️ Casos derivados")
    if not df_cases.empty:
        df_cases_view = df_cases[["id", "citizen_email", "description", "department", "priority", "status", "created_at"]]
        df_cases_view.rename(columns={
            "citizen_email": "Ciudadano",
            "description": "Descripción",
            "department": "Departamento",
            "priority": "Prioridad",
            "status": "Estado",
            "created_at": "Fecha creación"
        }, inplace=True)
        st.dataframe(df_cases_view, use_container_width=True)
    else:
        st.info("No hay casos derivados aún.")

    st.markdown("---")

    # ------------------------------
    # BOTÓN DE CIERRE DE SESIÓN
    # ------------------------------
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar sesión de administrador"):
        for key in ["logged_in", "citizen_id", "citizen_name", "citizen_email", "is_admin"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.current_section = "inicio"
        st.rerun()


# ------------------------------
# 9. DISPATCHER (Flujo de la App)
# ------------------------------



# Mostrar login primero si no está autenticado
if not st.session_state.get("logged_in", False):
    render_login()
else:
    section = st.session_state.current_section
    
    if st.session_state.get("is_admin"):
        render_admin_panel()
        
    else:
        if section == "mia_agent":
            render_mia_agent()
        elif section == "appointment_form":
            render_appointment_form(st.session_state.pending_appointment)
        elif section == "inicio":
            st.header("🏛️ Bienvenido a MIA")
            st.markdown("Selecciona una opción en el menú lateral para comenzar.")
        
        else:
            st.warning("Sección no reconocida. Volviendo al chat principal.")
            st.session_state.current_section = "mia_agent"
            st.rerun()

