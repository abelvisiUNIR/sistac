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
_GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")

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


def _google_chat(prompt: str, system: Optional[str] = None, max_tokens: int = 1024) -> str:
    from google import genai
    from google.genai import types

    # Si hay credenciales de cuenta de servicio de GCP, usar Vertex AI
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        project = os.getenv("GCP_PROJECT_ID", "bps-process-gen")
        location = os.getenv("GCP_LOCATION", "us-central1")
        if location == "global":
            location = "us-central1"
        client = genai.Client(vertexai=True, project=project, location=location)
    else:
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY no está configurada.\n"
                "Agregala al archivo .env:\n"
                "  GOOGLE_API_KEY=AIza..."
            )
        client = genai.Client(api_key=api_key)
    
    config = types.GenerateContentConfig(
        max_output_tokens=max(max_tokens or 1024, 4096),
        temperature=0.0
    )
    if system:
        config.system_instruction = system

    response = client.models.generate_content(
        model=_GOOGLE_MODEL,
        contents=prompt,
        config=config
    )
    if response.text:
        return response.text.strip()
    if response.candidates and response.candidates[0].content.parts:
        t = response.candidates[0].content.parts[0].text
        if t:
            return t.strip()
    return ""


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
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    if provider == "anthropic":
        return _retry(_anthropic_chat, prompt, system, max_tokens)
    elif provider == "openai":
        return _retry(_openai_chat, prompt, system, max_tokens)
    elif provider == "google":
        return _retry(_google_chat, prompt, system, max_tokens)
    else:
        raise ValueError(f"LLM_PROVIDER desconocido: '{provider}'. Usar 'anthropic', 'openai' o 'google'.")


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

# Singleton del modelo sentence-transformers — se carga una sola vez por proceso
_ST_MODEL = None

def _anthropic_embed(text: str) -> list[float]:
    """
    Anthropic/Google no tienen API de embeddings compatible por defecto o se usa local.
    Usar sentence-transformers: paraphrase-multilingual-mpnet-base-v2 → 768 dims.
    Debe coincidir con EMBEDDING_DIMENSIONS = 768 en rag/create_index.py.

    El modelo se carga una sola vez (singleton) para no recargar pesos en cada chunk.
    """
    global _ST_MODEL
    if _ST_MODEL is None:
        from sentence_transformers import SentenceTransformer
        import os

        # Autenticar con HF si hay token en .env (evita warning de unauthenticated)
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            try:
                from huggingface_hub import login
                login(token=hf_token, add_to_git_credential=False)
            except Exception:
                pass  # si falla el login, continuar igual (modelo ya cacheado)

        print("  Cargando modelo de embeddings (una sola vez)...")
        _ST_MODEL = SentenceTransformer(
            "paraphrase-multilingual-mpnet-base-v2",
            token=hf_token or None,
        )
    return _ST_MODEL.encode(text).tolist()


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
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    if provider in {"anthropic", "google"}:
        return _retry(_anthropic_embed, text)
    elif provider == "openai":
        return _retry(_openai_embed, text)
    else:
        raise ValueError(f"LLM_PROVIDER desconocido: '{provider}'.")


# ---------------------------------------------------------------------------
# Demo / smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    print(f"Proveedor activo: {provider}")
    reply = get_chat_completion(
        prompt="Responde solo 'OK' si me escuchas.",
        system="Eres un asistente de prueba.",
        max_tokens=100,
    )
    print(f"Respuesta: {reply}")

