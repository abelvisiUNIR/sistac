"""
chunking.py — Estrategias de chunking para el pipeline RAG de SISTAC

Dos funciones:
  chunk_text()        — chunking por caracteres (piloto David, mantener por compatibilidad)
  chunk_text_tokens() — chunking por tokens con RecursiveCharacterTextSplitter (canónico)

La función canónica es chunk_text_tokens(), que respeta config.CHUNK_SIZE (512 tokens)
y usa separadores semánticos para preservar la coherencia del texto CV.
"""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    """
    Divide un texto en fragmentos con solapamiento medido en caracteres.

    Conservada por compatibilidad con el piloto C2 de David
    (index_pilot_corpus.py, evaluate_pilot_c2.py).
    Para nuevos desarrollos usar chunk_text_tokens().

    Args:
        text:       Texto a dividir.
        chunk_size: Tamaño del fragmento en caracteres (default: 600).
        overlap:    Solapamiento entre fragmentos en caracteres (default: 100).

    Returns:
        Lista de strings con los fragmentos.
    """
    if not text:
        return []

    text = " ".join(text.split())

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

        if start < 0:
            start = 0

        if start >= len(text):
            break

    return chunks


def chunk_text_tokens(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    separators: list[str] | None = None,
) -> list[str]:
    """
    Divide un texto en fragmentos usando RecursiveCharacterTextSplitter de LangChain.

    Función canónica para el pipeline RAG oficial (C1/C2/C3).
    chunk_size y chunk_overlap se expresan en tokens (aproximados por caracteres
    con factor ~4 chars/token para texto en español). LangChain usa len() por
    defecto, que cuenta caracteres; para texto de CV en español la aproximación
    es suficientemente precisa para CHUNK_SIZE=512.

    Separadores en orden de preferencia: párrafo → salto de línea → espacio.
    Esto preserva secciones del CV (Experiencia, Educación, Habilidades) como
    unidades semánticas antes de recurrir a cortes arbitrarios.

    Args:
        text:           Texto a dividir.
        chunk_size:     Tamaño del fragmento (default: 512, de config.CHUNK_SIZE).
        chunk_overlap:  Solapamiento entre fragmentos (default: 64, de config.CHUNK_OVERLAP).
        separators:     Separadores semánticos (default: párrafo, newline, espacio).

    Returns:
        Lista de strings con los fragmentos.
    """
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError as exc:
        raise ImportError(
            "langchain-text-splitters no está instalado.\n"
            "Instalar con: pip install langchain-text-splitters>=0.3.0"
        ) from exc

    if not text:
        return []

    if separators is None:
        separators = ["\n\n", "\n", " ", ""]

    # Aproximar tokens a caracteres (factor ~4 caracteres por token en español)
    # 512 tokens ≈ 2048 caracteres. Esto reduce 4x el número de chunks generados.
    chunk_size_chars = chunk_size * 4
    chunk_overlap_chars = chunk_overlap * 4

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_chars,
        chunk_overlap=chunk_overlap_chars,
        separators=separators,
        length_function=len,
    )

    chunks = splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]


if __name__ == "__main__":
    texto_prueba = """
    EXPERIENCIA PROFESIONAL

    Analista de Datos Senior — Empresa XYZ (2021–2024)
    Responsable del desarrollo de dashboards en Power BI y automatización de reportes
    financieros con Python. Implementó pipelines ETL que redujeron el tiempo de
    procesamiento en un 40%.

    EDUCACIÓN

    Licenciatura en Sistemas de Información — Universidad ORT Uruguay (2018)
    Diplomado en Inteligencia Artificial — UNIR (2023–2024)

    HABILIDADES TÉCNICAS
    Python, SQL, Power BI, Machine Learning, scikit-learn, pandas, numpy.
    """

    print("=== chunk_text() — por caracteres (piloto) ===")
    r1 = chunk_text(texto_prueba, chunk_size=200, overlap=40)
    for i, c in enumerate(r1, 1):
        print(f"  [{i}] {c[:80]}...")

    print("\n=== chunk_text_tokens() — por tokens (canónico) ===")
    r2 = chunk_text_tokens(texto_prueba, chunk_size=200, chunk_overlap=40)
    for i, c in enumerate(r2, 1):
        print(f"  [{i}] {c[:80]}...")
