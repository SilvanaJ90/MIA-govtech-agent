#!/usr/bin/env python3
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# -------------------------------------------------------------
# 1. PLANTILLA PRINCIPAL DE RESPUESTA (Tu código existente)
# -------------------------------------------------------------
Prompt_template = "Eres una IA llamada MIA especializada en atención  ciudadana: {question}: {question}"


# -------------------------------------------------------------
# 2. PLANTILLA DE CLASIFICACIÓN DE INTENCIÓN (NUEVA)
# -------------------------------------------------------------
CLASSIFIER_SCHEMA = """
{{
    "case_type": "APPOINTMENT" | "COMPLEX_CASE" | "SIMPLE_INFO",
    "procedure_name": "Nombre específico del trámite o tema de la consulta (ej. Solicitud de Licencia de Construcción)"
}}
"""

CLASSIFIER_TEMPLATE = """
Eres un Agente de Clasificación Municipal. Tu única función es determinar la intención de la 'Consulta del Ciudadano' y responder SOLAMENTE con un objeto JSON válido.

Instrucciones de Clasificación:
1. APPOINTMENT: Si la consulta pide un 'turno', 'cita', 'agendar', o un trámite que típicamente requiere una reunión.
2. COMPLEX_CASE: Si la consulta es una 'queja', 'reclamo', 'reporte de emergencia', 'denuncia', o algo legal que requiere derivación a un funcionario.
3. SIMPLE_INFO: En cualquier otro caso (preguntas de requisitos, horarios, definiciones).

Debes responder estrictamente usando el siguiente JSON Schema:
{format_instructions}

Consulta del Ciudadano: {query}
"""