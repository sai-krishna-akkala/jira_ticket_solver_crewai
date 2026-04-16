"""
LLM Configuration — Ollama + llama3.2
"""

import os
from crewai import LLM


def get_llm(temperature=0.7):
    """Return an LLM based on provider env vars.

    Supported providers:
    - ollama (default)
    - groq
    - openai
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower().strip()

    if provider == "groq":
        return LLM(
            model=os.getenv("GROQ_MODEL", "groq/llama-3.1-8b-instant"),
            api_key=os.getenv("GROQ_API_KEY", ""),
            temperature=temperature,
        )

    if provider == "openai":
        return LLM(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=temperature,
        )

    return LLM(
        model=os.getenv("OLLAMA_MODEL", "ollama/llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=temperature,
    )
