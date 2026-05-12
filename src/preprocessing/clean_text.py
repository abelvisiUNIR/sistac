import re

def clean_text(text: str) -> str:
    """
    Limpia texto basico para el preprocesamiento NLP
    """
    if not isinstance(text, str):
        return ""
    #parsear a minuscula
    text = text.lower()

    # Eliminar caracteres raros
    text = re.sub(r"[^a-záéíóúñ0-9\s]", "", text)

    # Eliminar espacios nultiples
    text = re.sub(r"\s+", " ", text)

    return text.strip()

if __name__ == "__main__":
    prueba = "3 años en DATA!!! con Python, SQL..."

    limpio =  clean_text(prueba)

    print("Original:", prueba)
    print("limpio", limpio)

