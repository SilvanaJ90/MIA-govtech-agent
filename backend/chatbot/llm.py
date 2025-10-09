#!/usr/bin/env python3
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Retrieve the API key from the environment variable
API_KEY = os.getenv('GOOGLE_API_KEY')

# Instantiate the Google Generative AI model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=API_KEY,
    temperature=0,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)
