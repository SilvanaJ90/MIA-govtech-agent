#!/usr/bin/env python3
import re
from langchain_community.document_loaders import PyPDFLoader

# Load the PDF
loader = PyPDFLoader('backend/chatbot/doc/raw_data/documento.pdf')
# Load the document
documents = loader.load()  # Esto devolverá una lista de objetos de documento


def process_text(text):
    # Delete links
    text = re.sub(r'http\S+', '', text)

    # Delete specific words like
    words_to_remove = ['elcorteingles', 'lunamar']
    pattern = r'\b(?:' + '|'.join(map(re.escape, words_to_remove)) + r')\b'
    text = re.sub(pattern, '', text)

    # Remove unwanted special characters
    text = re.sub(r'[^\w\sñáéíóúü]', '', text)

    # Remove unnecessary line breaks
    text = re.sub(r'\n+', ' ', text).strip()

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text


with open('backend/chatbot/doc/processed_data/documento.txt',
          'w', encoding='utf-8') as f:
    for document in documents:
        processed_text = process_text(document.page_content)
        f.write(f"{processed_text}\n\n")
