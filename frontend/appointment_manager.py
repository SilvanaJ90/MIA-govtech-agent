# appointment_manager.py
"""
Sistema de gestión de citas y derivación de casos complejos
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from dataclasses import dataclass, asdict
from chain import classify_intent, generate_response_from_llm
from memory import memory # Necesario para cargar el historial de chat
from typing import Dict, List, Optional, Tuple # Ya deberías tener este

class CaseType(Enum):
    """Tipos de casos que el sistema puede manejar"""
    SIMPLE_INFO = "simple_info"  # Solo información (no requiere cita)
    APPOINTMENT = "appointment"  # Requiere cita
    COMPLEX_CASE = "complex_case"  # Requiere derivación a oficial/departamento
    FOLLOW_UP = "follow_up"  # Seguimiento de caso

class DepartmentType(Enum):
    """Departamentos disponibles"""
    DOCUMENTATION = "Departamento de Documentos"
    VITAL_RECORDS = "Registro Civil"
    PERMITS = "Departamento de Permisos"
    LEGAL = "Asesoría Legal"
    COMPLAINTS = "Departamento de Quejas"
    SPECIAL_CASES = "Casos Especiales"

@dataclass
class Appointment:
    """Modelo para citas"""
    id: str
    citizen_id: str
    citizen_name: str
    citizen_email: str
    procedure: str
    date: str  # Format: "YYYY-MM-DD"
    time: str  # Format: "HH:MM"
    status: str  # "scheduled", "completed", "cancelled"
    created_at: str
    notes: str = ""

@dataclass
class ComplexCase:
    """Modelo para casos complejos"""
    id: str
    citizen_id: str
    citizen_name: str
    citizen_email: str
    description: str
    department: DepartmentType
    priority: str  # "low", "medium", "high"
    status: str  # "pending", "assigned", "in_progress", "resolved"
    created_at: str
    assigned_to: Optional[str] = None
    notes: str = ""

class AppointmentManager:
    """Gestiona citas y disponibilidad"""
    
    def __init__(self):
        self.appointments: List[Appointment] = []
        self.availability = self._init_availability()
    
    def _init_availability(self) -> Dict:
        """Inicializa disponibilidad de citas (próximas 30 días)"""
        availability = {}
        today = datetime.now()
        
        for i in range(1, 31):
            date = today + timedelta(days=i)
            # Saltar fines de semana
            if date.weekday() < 5:  # 0-4 son lunes a viernes
                date_str = date.strftime("%Y-%m-%d")
                availability[date_str] = {
                    "09:00": True, "09:30": True, "10:00": True, "10:30": True,
                    "11:00": True, "11:30": True, "14:00": True, "14:30": True,
                    "15:00": True, "15:30": True, "16:00": True, "16:30": True
                }
        
        return availability
    
    def get_available_slots(self, date: str) -> Dict[str, bool]:
        """Obtiene slots disponibles para una fecha"""
        return self.availability.get(date, {})
    
    def schedule_appointment(
        self, 
        citizen_id: str, 
        citizen_name: str, 
        citizen_email: str,
        procedure: str, 
        date: str, 
        time: str,
        notes: str = ""
    ) -> Tuple[bool, str, Optional[Appointment]]:
        """
        Programa una cita
        Returns: (success, message, appointment_object)
        """
        # Validar disponibilidad
        if date not in self.availability:
            return False, f"La fecha {date} no está disponible", None
        
        if not self.availability[date].get(time, False):
            return False, f"El horario {time} no está disponible para {date}", None
        
        # Crear cita
        appointment_id = f"APT_{citizen_id}_{datetime.now().timestamp()}"
        appointment = Appointment(
            id=appointment_id,
            citizen_id=citizen_id,
            citizen_name=citizen_name,
            citizen_email=citizen_email,
            procedure=procedure,
            date=date,
            time=time,
            status="scheduled",
            created_at=datetime.now().isoformat(),
            notes=notes
        )
        
        # Marcar como no disponible
        self.availability[date][time] = False
        self.appointments.append(appointment)
        
        message = f"✓ Cita programada para {date} a las {time}. ID: {appointment_id}"
        return True, message, appointment
    
    def cancel_appointment(self, appointment_id: str) -> Tuple[bool, str]:
        """Cancela una cita"""
        for apt in self.appointments:
            if apt.id == appointment_id:
                # Liberar slot
                self.availability[apt.date][apt.time] = True
                apt.status = "cancelled"
                return True, f"Cita {appointment_id} cancelada exitosamente"
        
        return False, f"No se encontró la cita {appointment_id}"

class CaseRouter:
    """Clasifica casos y los deriva al departamento correspondiente"""
    
    def __init__(self):
        self.complex_cases: List[ComplexCase] = []
        self.case_keywords = self._init_keywords()
    
    def _init_keywords(self) -> Dict[str, List[str]]:
        """Palabras clave para clasificar casos"""
        return {
            "appointment": [
                "cita", "agendar", "horario", "disponibilidad", 
                "cuando", "reservar", "programar"
            ],
            "documentation": [
                "certificado", "documento", "DNI", "pasaporte", 
                "cédula", "expediente", "registro"
            ],
            "vital_records": [
                "nacimiento", "matrimonio", "defunción", "divorcio",
                "registro civil", "partida", "acta"
            ],
            "permits": [
                "licencia", "permiso", "autorización", "trámite especial",
                "comercial", "construcción"
            ],
            "legal": [
                "demanda", "ley", "derecho", "conflicto", "recurso",
                "apelación", "procedimiento legal"
            ],
            "complaints": [
                "queja", "reclamo", "problema", "mal servicio",
                "denuncia", "irregularidad"
            ]
        }
    
    def classify_case(self, query: str, conversation_context: List[Dict]) -> CaseType:
        """
        Clasifica el tipo de caso basado en la consulta y contexto
        """
        query_lower = query.lower()
        
        # Lógica de clasificación
        if any(keyword in query_lower for keyword in self.case_keywords["appointment"]):
            return CaseType.APPOINTMENT
        
        elif any(keyword in query_lower for keyword in self.case_keywords["legal"]):
            return CaseType.COMPLEX_CASE
        
        elif any(keyword in query_lower for keyword in self.case_keywords["complaints"]):
            return CaseType.COMPLEX_CASE
        
        elif len(conversation_context) > 10:  # Conversación larga = caso complejo
            return CaseType.COMPLEX_CASE
        
        else:
            return CaseType.SIMPLE_INFO
    
    def route_to_department(self, query: str) -> Optional[DepartmentType]:
        """
        Determina a qué departamento derivar basado en la consulta
        """
        query_lower = query.lower()
        
        dept_mapping = {
            DepartmentType.DOCUMENTATION: self.case_keywords["documentation"],
            DepartmentType.VITAL_RECORDS: self.case_keywords["vital_records"],
            DepartmentType.PERMITS: self.case_keywords["permits"],
            DepartmentType.LEGAL: self.case_keywords["legal"],
            DepartmentType.COMPLAINTS: self.case_keywords["complaints"],
        }
        
        for department, keywords in dept_mapping.items():
            if any(keyword in query_lower for keyword in keywords):
                return department
        
        return DepartmentType.SPECIAL_CASES
    
    def create_complex_case(
        self,
        citizen_id: str,
        citizen_name: str,
        citizen_email: str,
        description: str,
        priority: str = "medium"
    ) -> Tuple[bool, str, Optional[ComplexCase]]:
        """
        Crea un caso complejo y lo deriva al departamento apropiado
        """
        department = self.route_to_department(description)
        
        case_id = f"CASE_{citizen_id}_{datetime.now().timestamp()}"
        complex_case = ComplexCase(
            id=case_id,
            citizen_id=citizen_id,
            citizen_name=citizen_name,
            citizen_email=citizen_email,
            description=description,
            department=department,
            priority=priority,
            status="pending",
            created_at=datetime.now().isoformat()
        )
        
        self.complex_cases.append(complex_case)
        
        message = (
            f"✓ Caso derivado al {department.value}\n"
            f"ID de caso: {case_id}\n"
            f"Prioridad: {priority}\n"
            f"Estado: Pendiente de revisión"
        )
        
        return True, message, complex_case
    
    def get_case_status(self, case_id: str) -> Optional[ComplexCase]:
        """Obtiene el estado de un caso complejo"""
        for case in self.complex_cases:
            if case.id == case_id:
                return case
        return None
    
    def update_case_status(self, case_id: str, new_status: str) -> Tuple[bool, str]:
        """Actualiza el estado de un caso"""
        for case in self.complex_cases:
            if case.id == case_id:
                case.status = new_status
                return True, f"Caso {case_id} actualizado a {new_status}"
        return False, f"Caso {case_id} no encontrado"

class QueryProcessor:
    """Procesa consultas y determina la acción correspondiente"""
    
    def __init__(self):
        self.appointment_manager = AppointmentManager()
        self.case_router = CaseRouter()
    
    def process_query(
        self,
        query: str,
        docsearch,
        citizen_id: str,
        citizen_name: str,
        citizen_email: str,
    ) -> Dict:
        """
        Procesa la consulta del usuario y determina si necesita:
        1. Solo información (RAG response)
        2. Cita (appointment)
        3. Derivación (complex case)
        """
        
        
        #case_type = self.case_router.classify_case(query, conversation_context)
        intent_result = classify_intent(query)
        case_type_str = intent_result.get("case_type", "SIMPLE_INFO").upper()
        
        # Mapea el string a tu Enum
        try:
            case_type = CaseType(case_type_str.lower())
        except ValueError:
            case_type = CaseType.SIMPLE_INFO # Default

        # Obtener el nombre del procedimiento sugerido por el LLM
        procedure_name = intent_result.get("procedure_name", "Trámite no especificado")
        response_data = {
            "case_type": case_type.value,
            "primary_response": "",
            "actions": [],
            "appointment": None,
            "case": None,
            "procedure": procedure_name
        }
        
        # Si es solo información, devolver respuesta RAG
        if case_type == CaseType.SIMPLE_INFO:
            response_data["actions"].append("provide_information")
            # --- NUEVA LÓGICA DE EJECUCIÓN RAG ---
            # 1. Recuperar documentos
            documents_retrieved = docsearch.as_retriever().get_relevant_documents(query)
        
            # 2. Cargar contexto (memoria global)
            context = memory.load_memory_variables({})['chat_history']
        
            # 3. Ejecutar la función RAG
            response_data['primary_response'] = generate_response_from_llm(
                query, 
                context, 
                documents_retrieved
            )
            return response_data    
            # ------------------------------------
        elif case_type == CaseType.APPOINTMENT:
            response_data["actions"].append("offer_appointment")
        
            # Generamos la estructura de datos para el formulario de Streamlit
            response_data["appointment_data"] = {
                "procedure": procedure_name,
                "suggested_date": str(datetime.now().date() + timedelta(days=1)) 
            }
        
            # Retornamos inmediatamente para que new_app.py redirija al formulario
            return response_data
        # ... (Tu lógica para ofrecer cita) ...
    
        elif case_type == CaseType.COMPLEX_CASE:
            response_data["actions"].append("create_complex_case")
            priority = self._determine_priority(query)
        
            # Creamos el caso usando tu CaseRouter existente
            success, message, case = self.case_router.create_complex_case(
                citizen_id=citizen_id,
                citizen_name=citizen_name,
                citizen_email=citizen_email,
                description=query,
                priority=priority
            )
        
            response_data["case"] = asdict(case) if case else None
            response_data["case_message"] = message
        
            # Generamos una respuesta para notificar al usuario
            response_data['primary_response'] = (
                f"🚨 **¡Caso Complejo Derivado!** 🚨\n\n"
                f"He identificado que tu consulta requiere la intervención de un funcionario. "
                f"Hemos creado el **Caso N° {case.id}** y ha sido asignado al **{case.department.value}**."
            )
        
            return response_data
            
        return response_data
        
        
    def _determine_priority(self, query: str) -> str:
        """Determina la prioridad basada en palabras clave"""
        query_lower = query.lower()
        
        # Palabras clave para CASOS ALTAMENTE CRÍTICOS (Riesgo, Emergencia)
        high_priority_keywords = [
            "urgente", "emergencia", "grave", "crítico", "inmediato", 
            "violación", "peligro", "inaceptable"
        ]
        
        # Palabras clave para DEMORAS SIGNIFICATIVAS O TEMAS IMPORTANTES
        medium_priority_keywords = [
            "demora", "retraso", "seis meses", "tres meses", "meses", 
            "mucho tiempo", "importante", "pronto", "necesito respuesta"
        ]
        
        # 1. Prioridad Alta (Si encuentra cualquier palabra de la lista High)
        if any(keyword in query_lower for keyword in high_priority_keywords):
            return "HIGH"
        
        # 2. Prioridad Media (Si encuentra palabras de Demora/Importancia)
        elif any(keyword in query_lower for keyword in medium_priority_keywords):
            return "MEDIUM"
        
        # 3. Prioridad Baja (Por defecto, o consultas menos críticas)
        else:
            return "LOW"