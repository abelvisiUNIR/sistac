"""
Módulo: llm
Propósito: Abstracción de proveedor LLM para SISTAC (Anthropic / OpenAI)
Uso: from sistac.llm.provider import get_chat_completion, get_embedding
"""
from sistac.llm.provider import get_chat_completion, get_embedding, LLM_PROVIDER

__all__ = ["get_chat_completion", "get_embedding", "LLM_PROVIDER"]
