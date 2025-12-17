# Ollama LLM client

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": os.getenv("OLLAMA_MODEL"),
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]
