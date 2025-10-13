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

Prompt_template = "Eres una IA llamada MIA especializada en atención  ciudadana: {question}: {question}"
