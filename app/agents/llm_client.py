import os
from langchain_groq import ChatGroq

def get_llm(model: str = "llama-3.1-8b-instant", temperature: float = 0.0):
    """
    Returns a Groq LLM client.
    Make sure GROQ_API_KEY is set in environment.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment.")

    return ChatGroq(
        groq_api_key=api_key,
        model=model,
        temperature=temperature,
    )
