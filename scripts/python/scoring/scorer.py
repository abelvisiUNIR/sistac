"""
scoring/scorer.py — Motor de scoring semántico de candidatos (H2)

Evalúa la compatibilidad entre un CV y una descripción de cargo (JD) usando
el LLM configurado (Anthropic o OpenAI via llm/provider.py).

El scoring se realiza en cuatro dimensiones ponderadas:
  - Competencias técnicas  40%
  - Experiencia relevante  30%
  - Formación académica    20%
  - Soft skills            10%

Score final 0–100. Umbral APTO/NO_APTO: config.SCORE_THRESHOLD (= 70).

Hipótesis: H2 — las configuraciones RAG (C2/C3) alcanzan F1 ≥ 0.85 y
           AUC-ROC ≥ 0.90 frente al Gold Standard de expertos RRHH.

Uso:
    from scoring.scorer import score_candidate

    result = score_candidate(
        cv_text="...",
        jd_text="...",
        context_chunks=["chunk1", "chunk2"],  # None en C1 (sin RAG)
    )
    # result["score"] → int 0-100
    # result["decision"] → "APTO" | "NO_APTO"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# INV-16: rutas via PROJECT_ROOT
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SCORE_THRESHOLD

try:
    from llm.provider import get_chat_completion
except ImportError as exc:
    raise ImportError(
        "No se pudo importar llm.provider. "
        "Verificar que scripts/python/ esté en el PYTHONPATH."
    ) from exc


# ── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres un evaluador experto en selección de talento con 15 años
de experiencia en recursos humanos. Tu tarea es evaluar de forma objetiva y
estructurada la compatibilidad entre un currículum vitae (CV) y una descripción
de cargo (JD). Responde ÚNICAMENTE con JSON válido, sin texto adicional ni
bloques de código."""

_PROMPT_TEMPLATE_RAG = """Evalúa la compatibilidad entre el siguiente CV y la descripción de cargo.

=== DESCRIPCIÓN DEL CARGO ===
{jd_text}

=== FRAGMENTOS RECUPERADOS DEL CV (evidencia disponible) ===
{context}

=== INSTRUCCIONES ===
Evalúa exclusivamente con base en la evidencia presente en los fragmentos.
No inferas información que no esté explícita. Si un criterio no puede evaluarse
por falta de información en los fragmentos, asigna 50 (neutral).

Responde con este JSON exacto:
{{
  "score": <entero 0-100>,
  "dimensions": {{
    "competencias_tecnicas": <entero 0-100>,
    "experiencia": <entero 0-100>,
    "formacion": <entero 0-100>,
    "soft_skills": <entero 0-100>
  }},
  "justification": "<máximo 150 palabras, basada solo en evidencia de los fragmentos>",
  "evidence_gaps": "<aspectos no evaluables por falta de información, o 'ninguno'>"
}}"""

_PROMPT_TEMPLATE_NO_RAG = """Evalúa la compatibilidad entre el siguiente CV y la descripción de cargo.

=== DESCRIPCIÓN DEL CARGO ===
{jd_text}

=== CURRÍCULUM VITAE COMPLETO ===
{cv_text}

=== INSTRUCCIONES ===
Evalúa con base en toda la información del CV. Si un criterio no está explícito,
asigna 50 (neutral). Sé objetivo y basate en evidencia concreta.

Responde con este JSON exacto:
{{
  "score": <entero 0-100>,
  "dimensions": {{
    "competencias_tecnicas": <entero 0-100>,
    "experiencia": <entero 0-100>,
    "formacion": <entero 0-100>,
    "soft_skills": <entero 0-100>
  }},
  "justification": "<máximo 150 palabras, basada en evidencia del CV>",
  "evidence_gaps": "<aspectos no evaluables por falta de información, o 'ninguno'>"
}}"""


# ── Función principal ─────────────────────────────────────────────────────────

def score_candidate(
    cv_text: str,
    jd_text: str,
    context_chunks: list[str] | None = None,
    max_tokens: int = 512,
) -> dict:
    """
    Puntúa la compatibilidad entre un CV y una JD usando el LLM configurado.

    Args:
        cv_text:        Texto completo del CV (usado en C1 sin RAG).
        jd_text:        Descripción del cargo.
        context_chunks: Fragmentos recuperados por RAG (C2/C3).
                        Si es None, se usa el cv_text completo (C1).
        max_tokens:     Límite de tokens en la respuesta del LLM.

    Returns:
        Diccionario con:
            score        (int 0-100): compatibilidad global ponderada
            dimensions   (dict): score por dimensión (competencias, experiencia,
                                 formacion, soft_skills)
            justification (str): justificación basada en evidencia
            evidence_gaps (str): aspectos no evaluables
            decision     (str): "APTO" | "NO_APTO" según SCORE_THRESHOLD
            mode         (str): "rag" | "no_rag" (para trazabilidad)

    Raises:
        ValueError: si el LLM no devuelve JSON válido tras 2 intentos.
    """
    if context_chunks:
        context_str = "\n\n".join(
            f"[Fragmento {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        )
        prompt = _PROMPT_TEMPLATE_RAG.format(
            jd_text=jd_text.strip(),
            context=context_str,
        )
        mode = "rag"
    else:
        prompt = _PROMPT_TEMPLATE_NO_RAG.format(
            jd_text=jd_text.strip(),
            cv_text=cv_text.strip(),
        )
        mode = "no_rag"

    # Llamada al LLM (con retry incorporado en llm/provider.py)
    raw = get_chat_completion(
        prompt=prompt,
        system=SYSTEM_PROMPT,
        max_tokens=max_tokens,
    )

    result = _parse_llm_response(raw, cv_text=cv_text, jd_text=jd_text, mode=mode)
    return result


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_llm_response(
    raw: str,
    cv_text: str,
    jd_text: str,
    mode: str,
) -> dict:
    """
    Parsea la respuesta JSON del LLM y calcula el score ponderado final.

    Ponderaciones de dimensiones:
        competencias_tecnicas  40%
        experiencia            30%
        formacion              20%
        soft_skills            10%

    Si el JSON es inválido, intenta limpiar bloques de código y reintenta.
    Si falla dos veces, retorna un resultado de error para no interrumpir
    el experimento.
    """
    # Limpiar posibles bloques de código markdown
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: buscar el primer bloque JSON en el texto
        import re
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return _error_result(raw, mode)
        else:
            return _error_result(raw, mode)

    # Calcular score ponderado si las dimensiones están presentes
    dims = data.get("dimensions", {})
    weights = {
        "competencias_tecnicas": 0.40,
        "experiencia":           0.30,
        "formacion":             0.20,
        "soft_skills":           0.10,
    }

    if dims and all(k in dims for k in weights):
        weighted_score = sum(
            dims[k] * w for k, w in weights.items()
        )
        # El score ponderado tiene prioridad sobre el score declarado por el LLM
        score = round(weighted_score)
    else:
        score = int(data.get("score", 0))

    decision = "APTO" if score >= SCORE_THRESHOLD else "NO_APTO"

    return {
        "score":         score,
        "dimensions":    dims,
        "justification": data.get("justification", ""),
        "evidence_gaps": data.get("evidence_gaps", ""),
        "decision":      decision,
        "mode":          mode,
        "raw_llm_score": data.get("score"),  # score declarado por el LLM (para auditoría)
    }


def _error_result(raw: str, mode: str) -> dict:
    """Resultado de error cuando el LLM no devuelve JSON válido."""
    return {
        "score":         None,
        "dimensions":    {},
        "justification": f"[ERROR] LLM no retornó JSON válido: {raw}",
        "evidence_gaps": "N/A",
        "decision":      "ERROR",
        "mode":          mode,
        "raw_llm_score": None,
    }


# ── Demo / smoke test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os

    cv_ejemplo = """
    María González — Analista de Datos
    Universidad de la República (2018) — Lic. en Sistemas
    Experiencia: 3 años en análisis de datos con Python, SQL y Power BI.
    Habilidades: pandas, scikit-learn, visualización, comunicación efectiva.
    """

    jd_ejemplo = """
    Cargo: Analista de Datos Senior
    Requisitos: Python (avanzado), SQL, 2+ años de experiencia en análisis de datos.
    Responsabilidades: dashboards, reportes ejecutivos, automatización de procesos.
    """

    print(f"SCORE_THRESHOLD activo: {SCORE_THRESHOLD}")
    print("\n--- Modo C1 (sin RAG) ---")
    resultado = score_candidate(cv_text=cv_ejemplo, jd_text=jd_ejemplo)
    print(f"Score: {resultado['score']} | Decisión: {resultado['decision']}")
    print(f"Justificación: {resultado['justification'][:100]}...")

    print("\n--- Modo C2 (con RAG) ---")
    chunks_ejemplo = [
        "María González tiene 3 años de experiencia en análisis de datos con Python y SQL.",
        "Estudió Licenciatura en Sistemas en la Universidad de la República (2018).",
    ]
    resultado_rag = score_candidate(
        cv_text=cv_ejemplo,
        jd_text=jd_ejemplo,
        context_chunks=chunks_ejemplo,
    )
    print(f"Score: {resultado_rag['score']} | Decisión: {resultado_rag['decision']}")
    print(f"Dimensiones: {resultado_rag['dimensions']}")
