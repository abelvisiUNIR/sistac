def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    """
    Divide un texto en fragmentos con solapamiento.
    chunk_size y overlap se miden en caracteres para esta primera versión.
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


if __name__ == "__main__":
    texto_prueba = """
    Candidato con experiencia en SAP BPC, presupuestación financiera,
    planificación corporativa, análisis de datos y reportes ejecutivos.
    Ha participado en proyectos de implementación de modelos financieros,
    integración con SAP BW y automatización de procesos de planificación.
    También posee conocimientos en Python, machine learning y visualización de datos.
    """

    resultado = chunk_text(texto_prueba, chunk_size=120, overlap=30)

    for i, chunk in enumerate(resultado, start=1):
        print(f"Chunk {i}:")
        print(chunk)
        print("-" * 40)