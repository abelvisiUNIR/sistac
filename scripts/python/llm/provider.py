"""
Módulo: llm/provider.py
Propósito: Abstracción de proveedor LLM — Anthropic (Mario) u OpenAI (David)
Hipótesis: H2, H3 (scorer y evaluación)

Configurar en .env:
    LLM_PROVIDER=anthropic   # usa Claude Haiku/Sonnet
    LLM_PROVIDER=openai      # usa GPT-4o / text-embedding-3-small

No importar anthropic ni openai directamente en módulos de negocio.
Usar siempre: from llm.provider import get_chat_completion, get_embedding
"""
from __future__ import annotations

import os
import time
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic").lower()

# Modelos por defecto (sobreescribibles desde .env)
_ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
_OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
_OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 2.0  # segundos


def _retry(func, *args, **kwargs):
    """Retry con backoff exponencial para llamadas LLM."""
    for attempt in range(_MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            if attempt == _MAX_RETRIES - 1:
                raise
            delay = _RETRY_BASE_DELAY ** attempt
            print(f"[llm.provider] Intento {attempt + 1} falló: {exc}. Reintentando en {delay}s…")
            time.sleep(delay)


# ---------------------------------------------------------------------------
# Chat completion
# ---------------------------------------------------------------------------

def _anthropic_chat(prompt: str, system: Optional[str] = None, max_tokens: int = 1024) -> str:
    import anthropic  # import local — no contamina otros módulos

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": prompt}]
    kwargs = {
        "model": _ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text


def _openai_chat(prompt: str, system: Optional[str] = None, max_tokens: int = 1024) -> str:
    from openai import OpenAI  # import local

    client = OpenAI()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=_OPENAI_CHAT_MODEL,
        messages=messages,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def get_chat_completion(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 1024,
) -> str:
    """
    Genera una respuesta de chat con el proveedor configurado.

    Args:
        prompt:     Mensaje del usuario.
        system:     Instrucción de sistema (opcional).
        max_tokens: Límite de tokens en la respuesta.

    Returns:
        Texto de la respuesta del modelo.
    """
    if LLM_PROVIDER == "anthropic":
        return _retry(_anthropic_chat, prompt, system, max_tokens)
    elif LLM_PROVIDER == "openai":
        return _retry(_openai_chat, prompt, system, max_tokens)
    else:
        raise ValueError(f"LLM_PROVIDER desconocido: '{LLM_PROVIDER}'. Usar 'anthropic' u 'openai'.")


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

def _anthropic_embed(text: str) -> list[float]:
    """
    Anthropic no tiene API de embeddings propia.
    Usar sentence-transformers como fallback neutral.
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return model.encode(text).tolist()


def _openai_embed(text: str) -> list[float]:
    from openai import OpenAI

    client = OpenAI()
    response = client.embeddings.create(
        model=_OPENAI_EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


def get_embedding(text: str) -> list[float]:
    """
    Genera un embedding de texto con el proveedor configurado.

    Args:
        text: Texto a embeber.

    Returns:
        Lista de floats (vector de embedding).
    """
    if LLM_PROVIDER == "anthropic":
        return _retry(_anthropic_embed, text)
    elif LLM_PROVIDER == "openai":
        return _retry(_openai_embed, text)
    else:
        raise ValueError(f"LLM_PROVIDER desconocido: '{LLM_PROVIDER}'.")


# ---------------------------------------------------------------------------
# Demo / smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Proveedor activo: {LLM_PROVIDER}")
    reply = get_chat_completion(
        prompt="Responde solo 'OK' si me escuchas.",
        system="Eres un asistente de prueba.",
        max_tokens=10,
    )
    print(f"Respuesta: {reply}")
