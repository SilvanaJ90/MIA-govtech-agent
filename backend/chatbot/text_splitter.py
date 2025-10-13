#!/usr/bin/env python3
from langchain.text_splitter import CharacterTextSplitter


def text_splitter(
        documents,
        separator=" ",
        chunk_size=1000,
        chunk_overlap=200,
        is_separator_regex=False):
    """
        Extracts text from a list of document objects and splits
        it into chunks using the CharacterTextSplitter.

        Parameters:
        - documents (list): List of document objects,
            each with a `page_content` attribute.
        - separator (str): The separator to use for
            splitting the text. Default value is a space.
        - chunk_size (int): Size of each text chunk.
        - chunk_overlap (int): Amount of overlap between chunks.
        - is_separator_regex (bool): Whether the separator
            is a regular expression.

        Returns:
        - texts (list): List of split text chunks.
    """
    # Check if the documents have the 'page_content' attribute
    if not all(hasattr(doc, 'page_content') for doc in documents):
        raise AttributeError("The provided object does not have the 'page_content' attribute.")

    # Extract the full text from each document
    full_text = "\n\n".join([doc.page_content for doc in documents])

    # Create a text_splitter object with the provided parameters
    text_splitter = CharacterTextSplitter(
        separator=separator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=is_separator_regex,
    )

    # Split the text into chunks
    texts = text_splitter.split_text(full_text)

    return texts

