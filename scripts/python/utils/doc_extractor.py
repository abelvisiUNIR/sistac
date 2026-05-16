"""
utils/doc_extractor.py — Extracción de texto desde PDF, DOCX e imágenes

Estrategia por formato:
  .pdf   → pdfplumber primero (gratis, texto nativo)
           Si el texto es escaso (PDF escaneado) → Gemini 2.5 Flash (PDF nativo)
  .docx  → python-docx (gratis, sin API)
  .png / .jpg / .jpeg / .webp → Gemini 2.5 Flash Vision
  .txt   → lectura directa UTF-8

¿Por qué Gemini 2.5 Flash para documentos?
  - Acepta PDF completo de forma nativa (sin convertir a imágenes)
  - Ventana de contexto: 1M tokens (CVs largos, sin problema)
  - Costo: ~$0.00035/imagen vs ~$0.0025 Claude Haiku (7x más barato)
  - OCR de calidad equivalente

Uso:
    from utils.doc_extractor import extract_text
    texto = extract_text(Path("cv_maria.pdf"))
    texto = extract_text(raw_bytes, filename="cv_scan.jpg")
"""

from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

# INV-16: rutas via PROJECT_ROOT
_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg", ".webp"}
IMAGE_EXTENSIONS     = {".png", ".jpg", ".jpeg", ".webp"}

_GEMINI_MODEL = os.getenv("GEMINI_DOC_MODEL", "gemini-2.5-flash-preview-05-20")

_EXTRACT_PROMPT = (
    "Extraé todo el texto de este documento de forma fiel y completa. "
    "Preservá la estructura: si es un CV mantené nombre, contacto, experiencia, "
    "educación y habilidades; si es una descripción de cargo mantené título, "
    "responsabilidades y requisitos. "
    "Devolvé únicamente el texto extraído, sin comentarios ni explicaciones."
)


# ── Función principal ─────────────────────────────────────────────────────────

def extract_text(source: Path | bytes, filename: str = "") -> str:
    """
    Extrae texto legible de un documento o imagen.

    Args:
        source:   Path al archivo, o bytes del contenido (uploads web).
        filename: Nombre del archivo (requerido si source es bytes).

    Returns:
        Texto extraído como string.

    Raises:
        ValueError:  si el formato no está soportado.
        RuntimeError: si la extracción falla.
    """
    if isinstance(source, Path):
        filename = source.name
        data = source.read_bytes()
    else:
        data = source

    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Formato '{ext}' no soportado.\n"
            f"Formatos aceptados: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if ext == ".txt":
        return _extract_txt(data)
    elif ext == ".docx":
        return _extract_docx(data)
    elif ext == ".doc":
        raise ValueError(
            "Formato .doc no soportado. "
            "Convertí a .docx en Word: Archivo → Guardar como → .docx"
        )
    elif ext == ".pdf":
        return _extract_pdf(data, filename)
    elif ext in IMAGE_EXTENSIONS:
        return _extract_image_gemini(data, ext)
    else:
        raise ValueError(f"Formato '{ext}' no implementado.")


# ── Extractores gratuitos (sin API) ──────────────────────────────────────────

def _extract_txt(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def _extract_docx(data: bytes) -> str:
    try:
        from docx import Document
        import io
    except ImportError:
        raise RuntimeError("python-docx no instalado. pip install python-docx")

    doc = Document(io.BytesIO(data))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]

    # Tablas (CVs con formato tabular)
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                parts.append("  ".join(cells))

    text = "\n".join(parts)
    if len(text.strip()) < 20:
        raise RuntimeError(
            "El DOCX parece vacío o solo contiene imágenes. "
            "Probá exportarlo como PDF."
        )
    return text


def _extract_pdf(data: bytes, filename: str = "doc.pdf") -> str:
    """
    PDF: pdfplumber para texto nativo (gratis).
    Si el resultado tiene menos de 100 chars → PDF escaneado → Gemini.
    """
    try:
        import pdfplumber, io
    except ImportError:
        raise RuntimeError("pdfplumber no instalado. pip install pdfplumber")

    pages = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages.append(t)

    text = "\n".join(pages).strip()

    if len(text) >= 100:
        return text          # PDF con texto nativo — listo, sin API

    # PDF escaneado: mandarlo a Gemini completo (acepta PDF nativo)
    print(f"  [doc_extractor] PDF escaneado ({len(text)} chars extraídos) → Gemini 2.5 Flash")
    return _extract_pdf_gemini(data)


# ── Extractores con Gemini 2.5 Flash ─────────────────────────────────────────

def _get_gemini_client():
    """Inicializa el cliente Gemini. Lanza RuntimeError si falta la key."""
    try:
        from google import genai
    except ImportError:
        raise RuntimeError(
            "google-genai no instalado.\n"
            "pip install google-genai"
        )

    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY no configurada.\n"
            "Obtené una key gratis en: https://aistudio.google.com → Get API Key\n"
            "Luego agregala al archivo .env:\n"
            "  GOOGLE_API_KEY=AIza..."
        )

    return genai.Client(api_key=api_key)


def _extract_pdf_gemini(data: bytes) -> str:
    """
    Envía el PDF completo a Gemini 2.5 Flash.
    Gemini acepta PDF de forma nativa — sin convertir a imágenes.
    Ventana 1M tokens: soporta CVs largos sin truncar.
    """
    from google.genai import types

    client = _get_gemini_client()

    response = client.models.generate_content(
        model=_GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=data, mime_type="application/pdf"),
            types.Part.from_text(_EXTRACT_PROMPT),
        ],
    )
    return response.text.strip()


def _extract_image_gemini(data: bytes, ext: str) -> str:
    """
    Envía una imagen (JPG, PNG, WEBP) a Gemini 2.5 Flash Vision.
    Sin Tesseract OCR — todo via API.
    """
    from google.genai import types

    mime_map = {
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/png")

    client = _get_gemini_client()

    response = client.models.generate_content(
        model=_GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=data, mime_type=mime_type),
            types.Part.from_text(_EXTRACT_PROMPT),
        ],
    )
    return response.text.strip()


# ── Utilidad: detectar tipo MIME ──────────────────────────────────────────────

def detect_media_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return {
        ".pdf":  "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt":  "text/plain",
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext, "application/octet-stream")


# ── Demo CLI ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Extraer texto de un documento")
    parser.add_argument("archivo", help="PDF, DOCX, JPG, PNG o TXT")
    args = parser.parse_args()

    path = Path(args.archivo)
    if not path.exists():
        print(f"Archivo no encontrado: {path}")
        sys.exit(1)

    print(f"Extrayendo: {path.name} ({path.stat().st_size // 1024} KB)")
    texto = extract_text(path)
    print(f"Caracteres extraídos: {len(texto)}")
    print("-" * 60)
    print(texto[:1500])
    if len(texto) > 1500:
        print(f"\n... ({len(texto) - 1500} chars más)")
