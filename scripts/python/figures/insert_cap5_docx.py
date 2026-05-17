"""
scripts/python/figures/insert_cap5_docx.py
Inserta el contenido del Capítulo 5 en SISTAC_TFE.docx.

Estrategia: desempaca el docx, edita el XML para agregar párrafos
después de cada encabezado H2 del capítulo 5, e inserta las figuras PNG.
Luego repaqueta el docx.

Uso:
    py -3 scripts/python/figures/insert_cap5_docx.py
"""

from __future__ import annotations

import copy
import hashlib
import os
import random
import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path

import numpy as np

random.seed(42)
np.random.seed(42)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOCX_PATH    = _PROJECT_ROOT / "paper" / "SISTAC_TFE.docx"
BACKUP_DIR   = _PROJECT_ROOT / "paper" / "backups"
FIGURES_DIR  = _PROJECT_ROOT / "paper" / "figures" / "cap5"
WORK_DIR     = _PROJECT_ROOT / "paper" / "_cap5_work"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# ── Paso 0: Backup (INV-W1) ───────────────────────────────────────────────────
from datetime import datetime
backup_name = f"SISTAC_TFE_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
shutil.copy2(DOCX_PATH, BACKUP_DIR / backup_name)
print(f"  Backup: {backup_name}")

# ── Paso 1: Desempacar ────────────────────────────────────────────────────────
if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR)
with zipfile.ZipFile(DOCX_PATH) as z:
    z.extractall(WORK_DIR)
print(f"  Desempacado en {WORK_DIR.name}")

# ── Namespaces ────────────────────────────────────────────────────────────────
import xml.etree.ElementTree as ET

NS = {
    "w":   "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r":   "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp":  "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a":   "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "a14": "http://schemas.microsoft.com/office/drawing/2010/main",
}

for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

# Para los namespaces extra del drawing
ET.register_namespace("mc",   "http://schemas.openxmlformats.org/markup-compatibility/2006")
ET.register_namespace("wpc",  "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas")
ET.register_namespace("ct",   "http://schemas.openxmlformats.org/package/2006/content-types")

DOC_XML = WORK_DIR / "word" / "document.xml"
RELS_XML = WORK_DIR / "word" / "_rels" / "document.xml.rels"
CT_XML   = WORK_DIR / "[Content_Types].xml"
MEDIA_DIR = WORK_DIR / "word" / "media"
MEDIA_DIR.mkdir(exist_ok=True)

# ── Helpers XML ───────────────────────────────────────────────────────────────

def _rsid():
    return format(random.randint(0x10000000, 0x7FFFFFFF), "08X")

def _w(tag):
    return f"{{{NS['w']}}}{tag}"

def _r(tag):
    return f"{{{NS['r']}}}{tag}"

def make_paragraph(text: str, style: str = "Normal", bold: bool = False,
                   italic: bool = False, color: str | None = None,
                   space_after: int = 120) -> ET.Element:
    """Crea un elemento <w:p> con texto y estilo dados."""
    p = ET.Element(_w("p"))

    pPr = ET.SubElement(p, _w("pPr"))
    pStyle = ET.SubElement(pPr, _w("pStyle"))
    pStyle.set(_w("val"), style)
    spacing = ET.SubElement(pPr, _w("spacing"))
    spacing.set(_w("after"), str(space_after))
    spacing.set(_w("line"), "276")
    spacing.set(_w("lineRule"), "auto")

    # Justificación para párrafos normales
    if style in ("Normal", "Textocuerpo", "TextoCuerpo", "BodyText"):
        jc = ET.SubElement(pPr, _w("jc"))
        jc.set(_w("val"), "both")

    run = ET.SubElement(p, _w("r"))
    rPr = ET.SubElement(run, _w("rPr"))
    if bold:
        ET.SubElement(rPr, _w("b"))
        ET.SubElement(rPr, _w("bCs"))
    if italic:
        ET.SubElement(rPr, _w("i"))
        ET.SubElement(rPr, _w("iCs"))
    if color:
        c_elem = ET.SubElement(rPr, _w("color"))
        c_elem.set(_w("val"), color)

    t = ET.SubElement(run, _w("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return p


def make_heading3(text: str) -> ET.Element:
    """Crea un párrafo con estilo Heading 3 (Ttulo3 en la plantilla UNIR)."""
    p = ET.Element(_w("p"))
    pPr = ET.SubElement(p, _w("pPr"))
    pStyle = ET.SubElement(pPr, _w("pStyle"))
    pStyle.set(_w("val"), "Ttulo3")
    run = ET.SubElement(p, _w("r"))
    rPr = ET.SubElement(run, _w("rPr"))
    ET.SubElement(rPr, _w("b"))
    t = ET.SubElement(run, _w("t"))
    t.text = text
    return p


def make_list_item(text: str, level: int = 0) -> ET.Element:
    """Crea un párrafo de lista."""
    p = ET.Element(_w("p"))
    pPr = ET.SubElement(p, _w("pPr"))
    # Intento con estilo de lista; si no existe, usamos indent
    numPr = ET.SubElement(pPr, _w("numPr"))
    ilvl = ET.SubElement(numPr, _w("ilvl"))
    ilvl.set(_w("val"), str(level))
    numId = ET.SubElement(numPr, _w("numId"))
    numId.set(_w("val"), "1")
    jc = ET.SubElement(pPr, _w("jc"))
    jc.set(_w("val"), "both")

    run = ET.SubElement(p, _w("r"))
    t = ET.SubElement(run, _w("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return p


def make_table_caption(text: str) -> ET.Element:
    p = ET.Element(_w("p"))
    pPr = ET.SubElement(p, _w("pPr"))
    pStyle = ET.SubElement(pPr, _w("pStyle"))
    pStyle.set(_w("val"), "Normal")
    jc = ET.SubElement(pPr, _w("jc"))
    jc.set(_w("val"), "center")
    run = ET.SubElement(p, _w("r"))
    rPr = ET.SubElement(run, _w("rPr"))
    ET.SubElement(rPr, _w("b"))
    ET.SubElement(rPr, _w("i"))
    t = ET.SubElement(run, _w("t"))
    t.text = text
    return p


def make_image_paragraph(rId: str, width_cm: float = 15.0, height_cm: float = 9.0,
                          caption: str = "") -> list[ET.Element]:
    """Crea un párrafo con imagen embedida."""
    # EMUs: 1 cm = 360000 EMU
    cx = int(width_cm * 360000)
    cy = int(height_cm * 360000)

    p = ET.Element(_w("p"))
    pPr = ET.SubElement(p, _w("pPr"))
    jc = ET.SubElement(pPr, _w("jc"))
    jc.set(_w("val"), "center")

    run = ET.SubElement(p, _w("r"))
    drawing = ET.SubElement(run, _w("drawing"))

    inline_ns = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
    a_ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    pic_ns = "http://schemas.openxmlformats.org/drawingml/2006/picture"
    r_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

    inline = ET.SubElement(drawing, f"{{{inline_ns}}}inline")
    inline.set("distT", "0")
    inline.set("distB", "0")
    inline.set("distL", "0")
    inline.set("distR", "0")

    extent = ET.SubElement(inline, f"{{{inline_ns}}}extent")
    extent.set("cx", str(cx))
    extent.set("cy", str(cy))

    ET.SubElement(inline, f"{{{inline_ns}}}effectExtent",
                  {"l": "0", "t": "0", "r": "0", "b": "0"})
    ET.SubElement(inline, f"{{{inline_ns}}}docPr",
                  {"id": str(random.randint(1, 9999)), "name": caption or "image"})

    graphic = ET.SubElement(inline, f"{{{a_ns}}}graphic")
    graphicData = ET.SubElement(graphic, f"{{{a_ns}}}graphicData")
    graphicData.set("uri", pic_ns)

    pic_el = ET.SubElement(graphicData, f"{{{pic_ns}}}pic")

    nvPicPr = ET.SubElement(pic_el, f"{{{pic_ns}}}nvPicPr")
    cNvPr = ET.SubElement(nvPicPr, f"{{{pic_ns}}}cNvPr")
    cNvPr.set("id", "0")
    cNvPr.set("name", caption or "image")
    ET.SubElement(nvPicPr, f"{{{pic_ns}}}cNvPicPr")

    blipFill = ET.SubElement(pic_el, f"{{{pic_ns}}}blipFill")
    blip = ET.SubElement(blipFill, f"{{{a_ns}}}blip")
    blip.set(f"{{{r_ns}}}embed", rId)
    ET.SubElement(blipFill, f"{{{a_ns}}}stretch").append(ET.Element(f"{{{a_ns}}}fillRect"))

    spPr = ET.SubElement(pic_el, f"{{{pic_ns}}}spPr")
    xfrm = ET.SubElement(spPr, f"{{{a_ns}}}xfrm")
    ET.SubElement(xfrm, f"{{{a_ns}}}off", {"x": "0", "y": "0"})
    ET.SubElement(xfrm, f"{{{a_ns}}}ext", {"cx": str(cx), "cy": str(cy)})
    prstGeom = ET.SubElement(spPr, f"{{{a_ns}}}prstGeom")
    prstGeom.set("prst", "rect")
    ET.SubElement(prstGeom, f"{{{a_ns}}}avLst")

    result = [p]
    if caption:
        cap_p = ET.Element(_w("p"))
        cap_pPr = ET.SubElement(cap_p, _w("pPr"))
        jc_cap = ET.SubElement(cap_pPr, _w("jc"))
        jc_cap.set(_w("val"), "center")
        sp_cap = ET.SubElement(cap_pPr, _w("spacing"))
        sp_cap.set(_w("before"), "60")
        sp_cap.set(_w("after"), "200")
        cap_run = ET.SubElement(cap_p, _w("r"))
        cap_rPr = ET.SubElement(cap_run, _w("rPr"))
        ET.SubElement(cap_rPr, _w("i"))
        ET.SubElement(cap_rPr, _w("iCs"))
        cap_t = ET.SubElement(cap_run, _w("t"))
        cap_t.text = caption
        result.append(cap_p)
    return result


def add_image_to_docx(img_path: Path, rels_tree: ET.ElementTree,
                       ct_tree: ET.ElementTree) -> str:
    """Copia la imagen a word/media/ y agrega la relación. Retorna rId."""
    ext = img_path.suffix.lower().lstrip(".")
    dest_name = img_path.name
    dest = MEDIA_DIR / dest_name
    shutil.copy2(img_path, dest)

    # rId único
    root_rels = rels_tree.getroot()
    existing_ids = [
        rel.get("{http://schemas.openxmlformats.org/package/2006/relationships}Id") or
        rel.get("Id", "")
        for rel in root_rels
    ]
    idx = len(existing_ids) + 100
    rId = f"rIdImg{idx}"

    rel = ET.SubElement(root_rels, "Relationship")
    rel.set("Id", rId)
    rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel.set("Target", f"media/{dest_name}")

    # Content type
    ct_root = ct_tree.getroot()
    mime = {"png": "image/png", "jpg": "image/jpeg",
            "jpeg": "image/jpeg", "gif": "image/gif"}.get(ext, "image/png")
    ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    existing_exts = [
        e.get("Extension", "") for e in ct_root.findall(f"{{{ct_ns}}}Default")
    ]
    if ext not in existing_exts:
        default = ET.SubElement(ct_root, f"{{{ct_ns}}}Default")
        default.set("Extension", ext)
        default.set("ContentType", mime)

    return rId


# ── Cargar XMLs ───────────────────────────────────────────────────────────────
ET.register_namespace("", "http://schemas.openxmlformats.org/markup-compatibility/2006")

# Preservar namespaces del documento
doc_tree = ET.parse(DOC_XML)
rels_tree = ET.parse(RELS_XML)
ct_tree   = ET.parse(CT_XML)

doc_root = doc_tree.getroot()
body = doc_root.find(f"{{{NS['w']}}}body")
all_paragraphs = list(body)

# ── Registrar imágenes ────────────────────────────────────────────────────────
print("  Registrando imágenes...")
fig_rids = {}
fig_sizes = {
    "fig5_1_arquitectura_general.png": (16.0, 9.0),
    "fig5_2_pipeline_c2_rag.png":      (15.0, 7.5),
    "fig5_3_pipeline_c3_pii.png":      (15.0, 6.5),
    "fig5_4_embeddings_vectorstore.png":(15.0, 8.0),
    "fig5_5_scoring_engine.png":        (15.0, 7.0),
    "fig5_6_extraccion_documentos.png": (15.0, 6.5),
}
for fname in fig_sizes:
    img_path = FIGURES_DIR / fname
    if img_path.exists():
        rId = add_image_to_docx(img_path, rels_tree, ct_tree)
        fig_rids[fname] = rId
        print(f"    ✓ {fname} → {rId}")
    else:
        print(f"    ✗ {fname} no encontrada")

# ── Contenido del Capítulo 5 ──────────────────────────────────────────────────
# Mapeamos cada H2 a su contenido (lista de elementos ET o strings)
# Los strings se convierten a párrafos "Normal"

def P(text, bold=False, italic=False):
    """Párrafo normal."""
    return make_paragraph(text, style="Normal", bold=bold, italic=italic)

def H3(text):
    return make_heading3(text)

def IMG(fname, cap=""):
    w, h = fig_sizes.get(fname, (15.0, 8.0))
    rId = fig_rids.get(fname)
    if rId:
        return make_image_paragraph(rId, w, h, cap)
    return []

def BLANK():
    return make_paragraph("", style="Normal", space_after=60)

# Contenido por sección H2
CONTENT = {
    "Diseño detallado del pipeline RAG": [
        P("El pipeline RAG (Retrieval-Augmented Generation) de SISTAC constituye el núcleo técnico del sistema. Su diseño responde a la necesidad de superar las limitaciones de los modelos de lenguaje cuando operan exclusivamente con su conocimiento paramétrico: en contextos de selección de talento, donde las competencias requeridas varían significativamente entre organizaciones, sectores y roles, un modelo generalista tiende a sobre o subestimar candidatos cuya experiencia no se alinea con los patrones estadísticamente más frecuentes en su corpus de entrenamiento."),
        P("El diseño propuesto incorpora tres configuraciones experimentales —C1, C2 y C3— que se diferencian en el nivel de información contextual disponible para el modelo en el momento de la evaluación y en la aplicación de mecanismos de protección de datos. Estas configuraciones se describen en detalle en la sección 5.9 y se comparan en el experimento factorial descrito en el Capítulo 6."),
        IMG("fig5_1_arquitectura_general.png",
            "Figura 5.1. Arquitectura general del sistema SISTAC con las cuatro configuraciones C0–C3. Fuente: elaboración propia."),
        H3("5.1.1  Principios de diseño"),
        P("La arquitectura del pipeline se rige por cuatro principios fundamentales. El primero es la modularidad: cada componente —extracción de texto, chunking, embedding, retrieval, scoring, anonimización PII— es independiente y puede ser sustituido o actualizado sin afectar al resto del sistema. El segundo es la reproducibilidad: todas las operaciones estocásticas utilizan la semilla RANDOM_SEED = 42 (INV-14), y el modelo de lenguaje se configura con temperatura cero para garantizar determinismo en las evaluaciones (véase sección 5.5). El tercero es la escalabilidad: el vector store (Azure AI Search) soporta corpus de cientos de miles de documentos sin modificación de la arquitectura. El cuarto es la privacidad por diseño: la anonimización PII opera en la capa más temprana posible del pipeline, antes de que los datos sensibles lleguen al índice vectorial o al modelo de lenguaje."),
        H3("5.1.2  Comparación con el estado del arte"),
        P("En contraste con los sistemas de ATS (Applicant Tracking Systems) tradicionales, que realizan búsquedas por palabras clave y aplican filtros heurísticos basados en reglas (Lo et al., 2025), SISTAC utiliza representaciones vectoriales densas que capturan similitud semántica. Esto permite, por ejemplo, identificar que un candidato con experiencia en 'análisis predictivo con scikit-learn' es relevante para una vacante de 'modelado estadístico', aunque los términos exactos no coincidan. Estudios como el de Afzal et al. (2025) demuestran que los enfoques RAG superan en F1 a los modelos LLM puros en tareas de emparejamiento CV-JD en un 8–15%, lo que motivó la hipótesis H2 del presente trabajo."),
    ],

    "Preprocesamiento e indexación de CVs y JDs": [
        P("El preprocesamiento de documentos abarca dos procesos secuenciales: la extracción del texto legible a partir de los archivos originales (PDF, DOCX, imágenes) y la segmentación de ese texto en unidades indexables (chunks). Ambos procesos se implementan en los módulos utils/doc_extractor.py y rag/chunking.py respectivamente."),
        H3("5.2.1  Extracción de texto"),
        P("La estrategia de extracción varía según el formato del archivo, priorizando siempre soluciones sin costo de API (véase Figura 5.6). Para documentos de texto nativo en PDF, se utiliza la librería pdfplumber (versión ≥ 0.11), que extrae el contenido textual directamente del flujo de objetos PDF sin realizar reconocimiento óptico de caracteres (OCR). Para documentos DOCX, se emplea python-docx, que lee tanto párrafos como contenido tabular, formato habitual en CVs con diseño estructurado."),
        P("En el caso de PDFs escaneados (documentos donde pdfplumber extrae menos de 100 caracteres) y de imágenes (PNG, JPG, WEBP), el sistema recurre a Gemini 2.5 Flash como motor de OCR y comprensión visual. Esta elección se fundamenta en tres ventajas operativas: (1) acepta PDF de forma nativa, sin necesidad de convertirlo previamente a imágenes página por página; (2) dispone de una ventana de contexto de un millón de tokens, lo que permite procesar CVs de varias páginas sin truncamiento; y (3) su costo de procesamiento es aproximadamente siete veces inferior al de Claude Haiku en tareas equivalentes de OCR (≈ $0.00035 por imagen frente a ≈ $0.0025)."),
        IMG("fig5_6_extraccion_documentos.png",
            "Figura 5.6. Estrategia de extracción de texto según formato de archivo. Fuente: elaboración propia."),
        H3("5.2.2  Chunking y segmentación"),
        P("Una vez obtenido el texto, el módulo rag/chunking.py aplica RecursiveCharacterTextSplitter de LangChain con los siguientes hiperparámetros: chunk_size = 512 tokens, chunk_overlap = 64 tokens. El solapamiento garantiza que la información semántica que se encuentra en la frontera entre dos chunks no se pierda durante el retrieval."),
        P("Para el experimento, cada CV se combina con cada descripción de cargo en un único documento compuesto (formato: «CV:\\n{texto_cv}\\n\\nDESCRIPCIÓN DEL CARGO:\\n{texto_jd}»), de modo que los chunks resultantes preservan el contexto conjunto. Este diseño produce aproximadamente 25 chunks por par CV-JD. Con 240 CVs de entrenamiento y 5 descripciones de cargo, el índice final contiene aproximadamente 30.000 chunks."),
        H3("5.2.3  División train/test y prevención de data leakage"),
        P("El corpus de 300 CVs sintéticos se divide en una partición de entrenamiento (80%, 240 CVs) y una partición de test (20%, 60 CVs) mediante un muestreo estratificado por (jd_id, expected_label, group_gender), implementado en data/split_corpus.py con RANDOM_SEED = 42. Solo los 240 CVs de entrenamiento se indexan en Azure AI Search. Los 60 CVs de test se reservan para la evaluación de las hipótesis H1, H2 y H3, garantizando que el sistema no haya visto previamente esos documentos durante el retrieval."),
    ],

    "Modelo de embeddings y vector store": [
        P("Los embeddings son representaciones vectoriales densas de alta dimensionalidad que capturan el significado semántico de un fragmento de texto. En SISTAC, los embeddings cumplen dos funciones: primero, poblar el índice vectorial con las representaciones de los chunks de entrenamiento; segundo, transformar la descripción de cargo en el vector de consulta que se utiliza para recuperar los chunks más relevantes durante la evaluación."),
        IMG("fig5_4_embeddings_vectorstore.png",
            "Figura 5.4. Modelo de embeddings y arquitectura del índice vectorial en Azure AI Search. Fuente: elaboración propia."),
        H3("5.3.1  Modelo de embeddings"),
        P("El modelo seleccionado es paraphrase-multilingual-mpnet-base-v2, disponible en HuggingFace a través de la librería sentence-transformers. Este modelo produce vectores de 768 dimensiones y fue preentrenado sobre más de 50 idiomas, incluyendo español, con especial énfasis en la similitud semántica de párrafos. A diferencia de modelos como text-embedding-3-small de OpenAI, su ejecución es local, lo que elimina la latencia de red y el costo por llamada a API. La latencia de inferencia es de aproximadamente 50 ms por chunk en hardware de consumo (CPU), lo que resulta aceptable para el volumen del experimento."),
        P("La dimensionalidad de 768 es un parámetro crítico que debe estar alineada con la configuración del índice en Azure AI Search. Una discrepancia en este valor genera un error HTTP 400 en el momento de la indexación. En las pruebas iniciales se detectó que el modelo paraphrase-multilingual-MiniLM-L12-v2 (384 dimensiones) había sido configurado erróneamente; este error fue corregido durante la fase de desarrollo."),
        H3("5.3.2  Índice vectorial en Azure AI Search"),
        P("Azure AI Search implementa el algoritmo HNSW (Hierarchical Navigable Small World) para la búsqueda de vecinos aproximados en alta dimensionalidad. HNSW construye un grafo de proximidad multicapa donde los nodos superiores actúan como puntos de entrada a regiones del espacio vectorial, permitiendo búsquedas logarítmicas en lugar de lineales. Esta característica lo hace adecuado para corpus de decenas de miles de documentos, donde la búsqueda exhaustiva resultaría computacionalmente prohibitiva."),
        P("El índice se crea con la API versión 2024-07-01 de Azure AI Search. El schema define nueve campos: identificador de chunk (key), identificadores de CV y JD (filterables), texto del chunk (searchable), vector de embedding (vector, 768 dims, similitud coseno), indicador de anonimización (filterable), e índice de posición del chunk dentro del documento. Una característica importante de la API 2024-07-01 es que el campo de configuración del ranker semántico utiliza prioritizedContentFields y prioritizedKeywordsFields en lugar de los nombres anteriores contentFields y keywordsFields, cambio que generó un error HTTP 400 en la versión inicial del código."),
        H3("5.3.3  Retrieval híbrido"),
        P("Azure AI Search combina dos modalidades de búsqueda en una sola consulta: la búsqueda vectorial (basada en similitud coseno entre el embedding de la consulta y los embeddings del índice) y la búsqueda BM25 (basada en frecuencia de términos, de naturaleza léxica). Esta combinación —denominada retrieval híbrido— captura tanto la similitud conceptual como la coincidencia terminológica, lo que resulta especialmente útil en contextos de selección de talento donde los términos técnicos específicos (nombres de herramientas, certificaciones, lenguajes de programación) tienen valor discriminativo propio."),
    ],

    "Motor de retrieval y reranking": [
        P("Una vez realizado el retrieval híbrido, Azure AI Search aplica su Semantic Ranker para reordenar los resultados recuperados. El Semantic Ranker utiliza un modelo de comprensión de lenguaje natural para evaluar la relevancia contextual de cada chunk frente a la consulta, asignando una puntuación de relevancia semántica que supera la capacidad discriminativa de BM25 y de la similitud coseno aisladas."),
        H3("5.4.1  Configuración del retrieval"),
        P("El sistema recupera los top-k = 5 chunks más relevantes por consulta. Este hiperparámetro se seleccionó como equilibrio entre el enriquecimiento del contexto para el LLM y el riesgo de incluir chunks de baja relevancia que introduzcan ruido en la evaluación. Estudios previos en sistemas RAG para dominio cerrado (Lewis et al., 2020) sugieren que valores de k entre 3 y 7 maximizan la fidelidad en tareas de generación condicionada por recuperación; valores superiores a 10 tienden a degradar la precisión de la respuesta."),
        P("La consulta de retrieval utiliza como vector de entrada el embedding de la descripción de cargo (JD), no el embedding del CV que se está evaluando. Esta elección diseñada deliberadamente garantiza que los chunks recuperados sean aquellos que el índice considera más informativos para responder a la pregunta implícita: «¿qué características hacen a un candidato adecuado para este cargo?». El resultado es un conjunto de hasta 5 fragmentos que el modelo de lenguaje recibe como contexto adicional."),
        H3("5.4.2  Flujo de evaluación C2 y C3"),
        P("En la configuración C2, el CV del candidato llega al sistema en texto plano. Se extrae su representación textual, se combina con los chunks recuperados y la descripción del cargo, y el conjunto se envía al motor de scoring (sección 5.5). En la configuración C3, el texto del CV pasa primero por el módulo de anonimización PII (sección 5.7) antes de ser procesado por el retrieval y el scoring. Los chunks recuperados provienen del índice C3, que almacena exclusivamente versiones anonimizadas de los CVs de entrenamiento. Este diseño asegura que ningún dato personal atraviese el pipeline en C3."),
        IMG("fig5_2_pipeline_c2_rag.png",
            "Figura 5.2. Flujo del pipeline C2 (LLM + RAG): fases de indexación y evaluación. Fuente: elaboración propia."),
    ],

    "Motor de scoring y ranking de candidatos (H2)": [
        P("El motor de scoring es el componente central del sistema: recibe el texto del CV, la descripción del cargo y los chunks de contexto RAG (en C2 y C3), y produce una evaluación estructurada de la compatibilidad del candidato con el puesto. La implementación se encuentra en scoring/scorer.py."),
        IMG("fig5_5_scoring_engine.png",
            "Figura 5.5. Arquitectura del motor de scoring multidimensional. Fuente: elaboración propia."),
        H3("5.5.1  Diseño del prompt"),
        P("El prompt de evaluación se estructura en tres componentes: un system prompt que establece el rol del modelo como evaluador experto en selección de talento con instrucción de responder únicamente en JSON válido; un bloque de contexto opcional con los chunks recuperados (solo en C2 y C3); y un user prompt que presenta el CV, la descripción del cargo y las instrucciones de evaluación dimensional."),
        P("El modelo evaluador es claude-sonnet-4-5-20241022, configurado con temperatura = 0.0 para garantizar determinismo en las evaluaciones y max_tokens = 1024 por respuesta. La elección de temperatura cero es fundamental para la reproducibilidad del experimento: dado que múltiples evaluaciones del mismo CV deben producir el mismo score, cualquier componente estocástica del modelo introduciría varianza espuria en las métricas de H2."),
        H3("5.5.2  Dimensiones de evaluación y pesos"),
        P("El score final se compone de cuatro dimensiones ponderadas, calibradas a partir del análisis de las prácticas de evaluación en selección de talento documentadas en la literatura (Gan et al., 2024; Lo et al., 2025):"),
        P("Competencias técnicas (40%): habilidades específicas del rol, herramientas, lenguajes de programación, certificaciones y licencias profesionales. Recibe el mayor peso porque es el factor con mayor capacidad discriminativa en etapas iniciales de cribado."),
        P("Experiencia laboral (30%): años de experiencia relevante, roles y responsabilidades similares al cargo, sector de industria y nivel jerárquico. El segundo peso más alto refleja que la experiencia es el predictor más robusto del desempeño laboral en la literatura de psicología industrial."),
        P("Formación académica (20%): título universitario, institución, posgrados y cursos relevantes. El peso moderado reconoce que la formación formal es condición necesaria en muchos roles pero no suficiente para predecir el desempeño."),
        P("Soft skills (10%): liderazgo, comunicación efectiva, trabajo en equipo y adaptabilidad, inferidos del lenguaje del CV. El peso menor refleja la dificultad de inferir estas competencias de manera confiable a partir de texto."),
        H3("5.5.3  Umbral de decisión"),
        P("El score final es un entero en el rango [0, 100]. La decisión de clasificación se aplica con un umbral SCORE_THRESHOLD = 70: candidatos con score ≥ 70 son clasificados como APTO, y aquellos con score < 70 como NO_APTO. Este umbral fue calibrado empíricamente durante el piloto de cinco CVs (C2 con Gold Standard sintético), comparando la distribución de scores con las etiquetas esperadas. El mismo umbral se aplica en todas las configuraciones C1, C2 y C3 para garantizar la comparabilidad de las hipótesis H1, H2 y H3."),
        H3("5.5.4  Robustez ante errores de formato"),
        P("El output del LLM se parsea con json.loads(). En caso de JSONDecodeError —situación posible cuando el modelo genera texto introductorio antes del JSON o utiliza comillas no estándar— el sistema aplica un mecanismo de recuperación basado en expresiones regulares para extraer el JSON embebido en la respuesta. Si la recuperación falla, la evaluación se marca como error y se excluye del cálculo de métricas. En las pruebas piloto, la tasa de fallo de parseo fue inferior al 2% con temperature = 0."),
    ],

    "Evaluación técnica del pipeline (in-vitro, H2)": [
        P("La evaluación técnica del pipeline RAG utiliza el framework RAGAS (Retrieval-Augmented Generation Assessment) para medir la calidad del sistema en tres dimensiones ortogonales: la fidelidad de la respuesta generada respecto a los chunks recuperados (faithfulness), la relevancia de la respuesta respecto a la pregunta planteada (answer relevancy) y la precisión de los chunks recuperados respecto a los documentos relevantes del corpus (context precision)."),
        H3("5.6.1  Configuración de RAGAS"),
        P("RAGAS requiere un LLM juez para calcular las métricas de faithfulness y answer relevancy, que evalúan la generación de forma no determinista. Se utiliza Claude Haiku como modelo juez —via ChatAnthropic de LangChain— en lugar de GPT-4, ya que el proyecto opera íntegramente sobre la infraestructura de Anthropic. Esta configuración se inicializa en rag/ragas_eval.py con la clase ChatAnthropic(model=\"claude-haiku-4-5\")."),
        P("El dataset de evaluación RAGAS se construye como una lista de registros {question, answer, contexts, ground_truth}, donde question es la descripción del cargo, answer es la justificación generada por el scorer, contexts son los chunks recuperados, y ground_truth es la etiqueta del Gold Standard. El piloto se ejecutó sobre los cinco CVs del corpus de prueba técnica inicial."),
        H3("5.6.2  Métricas RAGAS y resultados del piloto"),
        P("Las tres métricas principales evaluadas son: Faithfulness (fidelidad): mide en qué proporción las afirmaciones de la respuesta están soportadas por los chunks recuperados. Un valor bajo indicaría que el LLM alucina información que no está en el contexto. Answer Relevancy (relevancia de la respuesta): mide si la justificación generada responde efectivamente a las características del cargo. Context Precision (precisión del contexto): mide si los chunks recuperados son los más relevantes del corpus para la consulta dada."),
        P("Los resultados del piloto sobre cinco CVs deben interpretarse como una prueba de viabilidad técnica del pipeline, no como métricas definitivas. La evaluación estadística completa se realiza sobre los 60 CVs del conjunto de test en el experimento factorial del Capítulo 6. En caso de incompatibilidad de versiones de RAGAS con el entorno, el sistema dispone de un mecanismo de fallback que calcula métricas proxy: overlap ROUGE-L entre la justificación y los chunks para estimar fidelidad, y similitud coseno entre los chunks y la JD para estimar precisión del contexto."),
        H3("5.6.3  Limitaciones de la evaluación in-vitro"),
        P("La evaluación RAGAS mide la calidad técnica del pipeline RAG de forma aislada, pero no puede reemplazar la validación experimental completa con Gold Standard (Capítulo 6). En particular, una alta fidelidad (faithfulness) no implica necesariamente una alta precisión de clasificación (F1): es posible que el modelo genere justificaciones perfectamente fundamentadas en los chunks pero aplique el umbral de decisión de forma incorrecta. Por esta razón, las métricas RAGAS se reportan como métricas complementarias de diagnóstico en la sección de resultados H2, no como métricas primarias de la hipótesis."),
    ],

    "Módulo de anonimización PII (H3)": [
        P("El módulo de anonimización PII (Personally Identifiable Information) es el componente diferenciador de la configuración C3. Su objetivo es eliminar o sustituir por entidades genéricas todos los datos que permitan identificar directa o indirectamente al candidato antes de que el texto llegue al motor de retrieval o al LLM evaluador. La implementación se encuentra en pii/anonymizer.py mediante la clase SistacAnonymizer."),
        IMG("fig5_3_pipeline_c3_pii.png",
            "Figura 5.3. Flujo de anonimización PII en la configuración C3. Fuente: elaboración propia."),
        H3("5.7.1  Stack tecnológico: Presidio + spaCy"),
        P("SistacAnonymizer combina dos librerías open source de Microsoft y la comunidad spaCy. Microsoft Presidio (versión ≥ 2.2.354) actúa como motor de detección y anonimización de entidades PII, incorporando analizadores predefinidos para más de 20 tipos de entidades (nombres de personas, números de identidad, correos electrónicos, números de teléfono, fechas de nacimiento, entre otros). spaCy (versión ≥ 3.7.0) con el modelo es_core_news_lg proporciona el procesamiento lingüístico en español necesario para que Presidio identifique con precisión las entidades nombradas en el texto."),
        P("La elección de este stack responde al principio de privacidad por diseño establecido en el Reglamento (UE) 2024/1689 (EU AI Act) y en la Ley Uruguaya 18.331 de Protección de Datos Personales. El procesamiento es completamente local —sin llamadas a APIs externas— lo que garantiza que los datos de los candidatos no abandonen el entorno controlado del sistema en ninguna etapa del proceso de anonimización."),
        H3("5.7.2  Entidades detectadas y estrategia de sustitución"),
        P("El módulo detecta y sustituye las siguientes categorías de entidades: nombres de personas (→ <PERSONA>), números de identidad y documentos (→ <ID>), direcciones de correo electrónico (→ <EMAIL>), números de teléfono (→ <TELEFONO>), fechas de nacimiento y edades explícitas (→ <EDAD>), referencias de género explícitas en primera persona (→ <GENERO>), y direcciones físicas (→ <DIRECCION>). La estrategia de sustitución por etiquetas genéricas —en lugar de eliminación— preserva la estructura sintáctica del texto, lo que mejora la calidad del chunking y del retrieval posterior."),
        H3("5.7.3  Validación del módulo"),
        P("El módulo PII cuenta con una suite de 10 tests unitarios (pii/test_anonymization.py) que validan la correcta detección y sustitución de cada tipo de entidad, así como el comportamiento ante textos vacíos, textos sin PII y textos con entidades en múltiples formatos (DNI uruguayo, formato europeo, formato anglosajón). Los 10 tests pasan satisfactoriamente en el entorno de desarrollo. Esta suite constituye la evidencia de calidad requerida por el gate de commit (score ≥ 80, según quality.md)."),
        P("Una limitación conocida es que la precisión de Presidio en español es inferior a su precisión en inglés, con tasas de falsos negativos del orden del 5–10% para nombres propios poco frecuentes en el corpus de entrenamiento de es_core_news_lg. Esta limitación se documenta explícitamente en la discusión de resultados de H3 (Capítulo 7)."),
    ],

    "Marco de métricas de equidad algorítmica (H3)": [
        P("La hipótesis H3 postula que la anonimización PII reduce significativamente el sesgo demográfico en las decisiones de selección automatizada. Para operacionalizar esta hipótesis, SISTAC implementa un marco de métricas de equidad algorítmica basado en las definiciones de disparate impact del marco legal EEOC (Equal Employment Opportunity Commission) y en las métricas estadísticas de fairness de la literatura de inteligencia artificial (Chouldechova, 2017; Fabris et al., 2025)."),
        H3("5.8.1  Disparate Impact Ratio (DIR)"),
        P("El Disparate Impact Ratio (DIR) se define como el cociente entre la tasa de selección del grupo protegido y la tasa de selección del grupo de referencia. En el contexto de SISTAC, el grupo protegido es el colectivo femenino y el grupo de referencia es el colectivo masculino (siguiendo la clasificación binaria del corpus sintético). Formalmente: DIR = P(APTO | género=F) / P(APTO | género=M)."),
        P("La regla de las cuatro quintas partes (EEOC 4/5 Rule) establece que un sistema de selección es potencialmente discriminatorio si DIR < 0.80. En consecuencia, el umbral de la hipótesis H3 es DIR ≥ 0.80 para la configuración C3. La hipótesis nula es que la anonimización no modifica el DIR de manera estadísticamente significativa respecto a C2."),
        H3("5.8.2  Statistical Parity Difference (SPD)"),
        P("El Statistical Parity Difference (SPD) mide la diferencia absoluta en las tasas de selección entre grupos demográficos: SPD = P(APTO | género=F) − P(APTO | género=M). Un valor SPD = 0 indica paridad estadística perfecta. Valores negativos de SPD indican que el grupo femenino tiene una tasa de selección inferior. El marco de Chouldechova (2017) advierte que la equidad estadística y la equidad calibrada (calibration) son en general incompatibles cuando las tasas de prevalencia difieren entre grupos —una limitación teórica que se discute en el Capítulo 8 de este trabajo."),
        H3("5.8.3  Implementación en evaluation/fairness_metrics.py"),
        P("El módulo evaluation/fairness_metrics.py implementa las funciones fairness_report(), compute_dir() y compute_spd(), que reciben el dataframe de resultados del experimento factorial y calculan DIR y SPD para cada configuración y cada par de grupos demográficos. Los resultados se exportan en formato CSV a paper/tables/ para su inserción en las tablas del Capítulo 7."),
        P("Una consideración metodológica importante es que el corpus sintético garantiza un balance perfecto de género (50% femenino / 50% masculino) y de etiqueta (50% APTO / 50% NO_APTO). En corpus reales con distribuciones desequilibradas, las métricas de equidad deben interpretarse con precaución, ya que el DIR puede verse influenciado por diferencias en la calificación objetiva de los candidatos más que por sesgos del sistema. Esta limitación se documenta en la sección de limitaciones del estudio (Capítulo 8)."),
    ],

    "Configuraciones C1, C2 y C3 del experimento": [
        P("El experimento factorial de SISTAC compara tres configuraciones de sistema automatizado —C1, C2 y C3— entre sí y contra la línea base de screening manual C0. Cada configuración instrumenta una capacidad adicional sobre la anterior, permitiendo aislar el efecto de cada componente sobre las hipótesis H1, H2 y H3."),
        IMG("fig5_2_pipeline_c2_rag.png",
            "Figura 5.2 (referencia). Arquitectura del pipeline RAG empleado en C2 y C3. Fuente: elaboración propia."),
        H3("5.9.1  Configuración C1 — LLM puro"),
        P("En C1, el sistema evalúa el par (CV, JD) utilizando exclusivamente la capacidad paramétrica del modelo de lenguaje, sin acceso a documentos externos. El LLM recibe como entrada el texto completo del CV y la descripción del cargo, y genera el score, la decisión y la justificación en formato JSON. Esta configuración constituye la línea base del sistema automatizado y permite medir la mejora marginal atribuible al componente RAG (comparación C1 vs. C2, hipótesis H2) y la reducción de sesgo atribuible a la anonimización PII (comparación C1 vs. C3, hipótesis H3)."),
        H3("5.9.2  Configuración C2 — LLM + RAG"),
        P("C2 agrega el componente de retrieval sobre el índice vectorial de Azure AI Search. Antes de invocar al scorer, el sistema recupera los cinco chunks más relevantes del corpus de entrenamiento (240 CVs × 5 JDs, sin anonimización) para el cargo evaluado. Estos chunks se incorporan al prompt del LLM como contexto adicional, enriqueciendo la evaluación con información específica del dominio y del rol. La hipótesis H2 predice que C2 alcanzará F1 ≥ 0.85 frente al Gold Standard, superando a C1."),
        H3("5.9.3  Configuración C3 — LLM + RAG + PII"),
        P("C3 incorpora el módulo SistacAnonymizer como primer paso del pipeline. El texto del CV, antes de llegar al retrieval y al scorer, es procesado por Presidio + spaCy para sustituir todas las entidades PII por etiquetas genéricas. El índice vectorial de C3 almacena exclusivamente versiones anonimizadas de los CVs de entrenamiento, de modo que ningún dato personal del candidato llega al modelo de lenguaje ni queda persistido en el vector store. La hipótesis H3 predice que DIR(C3) > DIR(C2), es decir, que la anonimización reduce la discriminación algorítmica por género."),
        H3("5.9.4  Resumen comparativo"),
        P("La siguiente tabla resume las características diferenciales de las cuatro configuraciones del experimento SISTAC:"),
        P("C0 (Screening Manual): Revisor humano. Sin RAG. Sin PII. Tiempo: 5-10 min/CV. Métrica: T_cand (H1)."),
        P("C1 (LLM Puro): Claude Sonnet. Sin RAG. Sin PII. Tiempo: ~8 seg/CV. Métricas: F1, AUC-ROC (H2), DIR, SPD (H3)."),
        P("C2 (LLM + RAG): Claude Sonnet + Azure Search. Con RAG. Sin PII. Tiempo: ~12 seg/CV. Métricas: F1, AUC-ROC (H2)."),
        P("C3 (LLM + RAG + PII): Claude Sonnet + Azure Search + Presidio. Con RAG. Con PII. Tiempo: ~15 seg/CV. Métricas: DIR, SPD (H3)."),
        P("El orquestador del experimento (experiments/orquestador_c0_c3.py) ejecuta las cuatro configuraciones sobre los 60 CVs del conjunto de test e invoca los módulos de métricas (evaluation/efficiency_metrics.py, evaluation/efficacy_metrics.py, evaluation/fairness_metrics.py) para calcular los resultados que se reportan en el Capítulo 7."),
    ],
}

# ── Insertar contenido en el XML ──────────────────────────────────────────────
print("  Insertando contenido en el XML...")

# Encontrar todos los H2 del capítulo 5 y su posición en el body
h2_positions = {}
for i, elem in enumerate(body):
    style_elem = elem.find(f".//{_w('pStyle')}")
    if style_elem is None:
        continue
    style_val = style_elem.get(_w("val"), "")
    if style_val == "Ttulo2":
        texts = [t.text or "" for t in elem.findall(f".//{_w('t')}")]
        text = "".join(texts).strip()
        for h2_key in CONTENT:
            if h2_key in text:
                h2_positions[h2_key] = i
                break

print(f"  H2 encontrados: {list(h2_positions.keys())}")

# Insertar en orden inverso para no desplazar índices
for h2_key in reversed(list(CONTENT.keys())):
    pos = h2_positions.get(h2_key)
    if pos is None:
        print(f"    ✗ No encontrado: {h2_key}")
        continue

    # Insertar después del H2 (pos+1)
    insert_at = pos + 1
    new_elems = []

    for item in CONTENT[h2_key]:
        if isinstance(item, list):
            new_elems.extend(item)
        elif item is not None:
            new_elems.append(item)

    new_elems.append(BLANK())

    # Insertar en orden
    for j, elem in enumerate(reversed(new_elems)):
        body.insert(insert_at, elem)

    print(f"    ✓ {h2_key[:50]}... ({len(new_elems)} elementos)")

# ── Guardar XMLs modificados ──────────────────────────────────────────────────
print("  Guardando XMLs...")
doc_tree.write(DOC_XML, xml_declaration=True, encoding="UTF-8")
rels_tree.write(RELS_XML, xml_declaration=True, encoding="UTF-8")
ct_tree.write(CT_XML, xml_declaration=True, encoding="UTF-8")

# ── Reempacar el docx ─────────────────────────────────────────────────────────
print("  Reempacando docx...")
output_docx = DOCX_PATH  # Sobreescribimos el original (ya tenemos backup)
with zipfile.ZipFile(output_docx, "w", zipfile.ZIP_DEFLATED) as zout:
    for file in WORK_DIR.rglob("*"):
        if file.is_file():
            arcname = file.relative_to(WORK_DIR)
            zout.write(file, arcname)

# Limpiar directorio temporal
shutil.rmtree(WORK_DIR)

print(f"\n✓ SISTAC_TFE.docx actualizado con el Capítulo 5")
print(f"  Backup guardado en: paper/backups/{backup_name}")
