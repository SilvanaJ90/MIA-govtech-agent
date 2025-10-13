#!/usr/bin/env python3
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

from prompt_template import Prompt_template


prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=Prompt_template
        ),  # The persistent system prompt
        MessagesPlaceholder(
            variable_name="chat_history"
        ),  # Where the memory will be stored.
        HumanMessagePromptTemplate.from_template(
            "{human_input}"
        ),  # Where the human input will be injected
    ]
)


# Memory for conversation history
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
    )