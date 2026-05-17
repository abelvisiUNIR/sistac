"""
scripts/python/figures/insert_cap5_docx.py  (v2 — XML correcto)
Inserta el contenido del Capítulo 5 en SISTAC_TFE.docx.

Correcciones respecto a v1:
  - Párrafos Normal sin declarar pStyle (herencia) + lang=es-UY correcto
  - Imágenes con fromstring() para preservar namespaces inline
  - Captions con estilo Piedefoto-tabla (el de la plantilla UNIR)
  - Sin make_list_item: los bullets son párrafos normales con guión
  - Ttulo3 con estructura exacta del documento real

Uso:
    py -3 -X utf8 scripts/python/figures/insert_cap5_docx.py
"""

from __future__ import annotations

import random
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import xml.etree.ElementTree as ET

random.seed(42)
np.random.seed(42)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOCX_PATH   = _PROJECT_ROOT / "paper" / "SISTAC_TFE.docx"
BACKUP_DIR  = _PROJECT_ROOT / "paper" / "backups"
FIGURES_DIR = _PROJECT_ROOT / "paper" / "figures" / "cap5"
WORK_DIR    = _PROJECT_ROOT / "paper" / "_cap5_work"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# ── Backup (INV-W1) ───────────────────────────────────────────────────────────
backup_name = f"SISTAC_TFE_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
shutil.copy2(DOCX_PATH, BACKUP_DIR / backup_name)
print(f"  Backup: {backup_name}")

# ── Desempacar ────────────────────────────────────────────────────────────────
if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR)
with zipfile.ZipFile(DOCX_PATH) as z:
    z.extractall(WORK_DIR)
print(f"  Desempacado en {WORK_DIR.name}")

# ── Namespaces ────────────────────────────────────────────────────────────────
W_NS  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS  = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"

def _w(tag):  return f"{{{W_NS}}}{tag}"
def _r(tag):  return f"{{{R_NS}}}{tag}"

# Registrar namespaces para que ET los use con prefijos correctos
ET.register_namespace("w",   W_NS)
ET.register_namespace("r",   R_NS)
ET.register_namespace("w14", "http://schemas.microsoft.com/office/word/2010/wordml")
ET.register_namespace("wp",  "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing")
ET.register_namespace("a",   "http://schemas.openxmlformats.org/drawingml/2006/main")
ET.register_namespace("pic", "http://schemas.openxmlformats.org/drawingml/2006/picture")
ET.register_namespace("mc",  "http://schemas.openxmlformats.org/markup-compatibility/2006")
ET.register_namespace("ct",  "http://schemas.openxmlformats.org/package/2006/content-types")

DOC_XML  = WORK_DIR / "word" / "document.xml"
RELS_XML = WORK_DIR / "word" / "_rels" / "document.xml.rels"
CT_XML   = WORK_DIR / "[Content_Types].xml"
MEDIA    = WORK_DIR / "word" / "media"
MEDIA.mkdir(exist_ok=True)

# ── Constructores de párrafos (XML correcto según plantilla UNIR) ─────────────

def P(text: str) -> ET.Element:
    """
    Párrafo de cuerpo de texto.
    Sin declarar pStyle (hereda Normal de la plantilla).
    Incluye lang=es-UY y bCs como los párrafos reales del documento.
    """
    p = ET.Element(_w("p"))
    pPr = ET.SubElement(p, _w("pPr"))
    pPr_rPr = ET.SubElement(pPr, _w("rPr"))
    ET.SubElement(pPr_rPr, _w("bCs"))
    lang_ppr = ET.SubElement(pPr_rPr, _w("lang"))
    lang_ppr.set(_w("val"), "es-UY")

    run = ET.SubElement(p, _w("r"))
    rPr = ET.SubElement(run, _w("rPr"))
    ET.SubElement(rPr, _w("bCs"))
    lang_run = ET.SubElement(rPr, _w("lang"))
    lang_run.set(_w("val"), "es-UY")

    t = ET.SubElement(run, _w("t"))
    t.set(f"{{{XML_NS}}}space", "preserve")
    t.text = text
    return p


def H3(text: str) -> ET.Element:
    """Encabezado nivel 3 (Ttulo3 de la plantilla UNIR)."""
    p = ET.Element(_w("p"))
    pPr = ET.SubElement(p, _w("pPr"))
    pStyle = ET.SubElement(pPr, _w("pStyle"))
    pStyle.set(_w("val"), "Ttulo3")
    pPr_rPr = ET.SubElement(pPr, _w("rPr"))
    lang_ppr = ET.SubElement(pPr_rPr, _w("lang"))
    lang_ppr.set(_w("val"), "es-UY")

    run = ET.SubElement(p, _w("r"))
    rPr = ET.SubElement(run, _w("rPr"))
    lang_run = ET.SubElement(rPr, _w("lang"))
    lang_run.set(_w("val"), "es-UY")

    t = ET.SubElement(run, _w("t"))
    t.text = text
    return p


def CAPTION(text: str) -> ET.Element:
    """
    Pie de foto/tabla usando el estilo Piedefoto-tabla de la plantilla UNIR.
    Para: 'Figura X. Descripción. Fuente: elaboración propia.'
    """
    p = ET.Element(_w("p"))
    pPr = ET.SubElement(p, _w("pPr"))
    pStyle = ET.SubElement(pPr, _w("pStyle"))
    pStyle.set(_w("val"), "Piedefoto-tabla")
    pPr_rPr = ET.SubElement(pPr, _w("rPr"))
    lang_ppr = ET.SubElement(pPr_rPr, _w("lang"))
    lang_ppr.set(_w("val"), "es-UY")

    run = ET.SubElement(p, _w("r"))
    rPr = ET.SubElement(run, _w("rPr"))
    lang_run = ET.SubElement(rPr, _w("lang"))
    lang_run.set(_w("val"), "es-UY")

    t = ET.SubElement(run, _w("t"))
    t.set(f"{{{XML_NS}}}space", "preserve")
    t.text = text
    return p


def BLANK() -> ET.Element:
    """Párrafo vacío para espaciado."""
    p = ET.Element(_w("p"))
    pPr = ET.SubElement(p, _w("pPr"))
    pPr_rPr = ET.SubElement(pPr, _w("rPr"))
    lang_ppr = ET.SubElement(pPr_rPr, _w("lang"))
    lang_ppr.set(_w("val"), "es-UY")
    return p


def IMG(rId: str, cx: int, cy: int, caption_text: str,
        img_id: int | None = None) -> list[ET.Element]:
    """
    Párrafo con imagen embedida + párrafo de caption.
    Usa fromstring() con XML raw para preservar namespaces inline.
    Estructura copiada del documento real.
    """
    if rId is None:
        return []

    if img_id is None:
        img_id = random.randint(5200, 9999)

    # XML raw con namespaces inline — igual que el documento original
    img_xml = f'''<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
        xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
        xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
        xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <w:pPr>
        <w:spacing w:line="276" w:lineRule="auto"/>
        <w:jc w:val="center"/>
        <w:rPr><w:lang w:val="es-UY"/></w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr><w:noProof/><w:lang w:val="es-UY"/></w:rPr>
        <w:drawing>
          <wp:inline distT="0" distB="0" distL="0" distR="0">
            <wp:extent cx="{cx}" cy="{cy}"/>
            <wp:effectExtent l="0" t="0" r="0" b="0"/>
            <wp:docPr id="{img_id}" name="Figura_{img_id}"/>
            <wp:cNvGraphicFramePr>
              <a:graphicFrameLocks noChangeAspect="1"/>
            </wp:cNvGraphicFramePr>
            <a:graphic>
              <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                <pic:pic>
                  <pic:nvPicPr>
                    <pic:cNvPr id="{img_id}" name="Figura_{img_id}"/>
                    <pic:cNvPicPr>
                      <a:picLocks noChangeAspect="1"/>
                    </pic:cNvPicPr>
                  </pic:nvPicPr>
                  <pic:blipFill>
                    <a:blip r:embed="{rId}"/>
                    <a:stretch><a:fillRect/></a:stretch>
                  </pic:blipFill>
                  <pic:spPr bwMode="auto">
                    <a:xfrm>
                      <a:off x="0" y="0"/>
                      <a:ext cx="{cx}" cy="{cy}"/>
                    </a:xfrm>
                    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                    <a:noFill/>
                    <a:ln><a:noFill/></a:ln>
                  </pic:spPr>
                </pic:pic>
              </a:graphicData>
            </a:graphic>
          </wp:inline>
        </w:drawing>
      </w:r>
    </w:p>'''

    img_elem = ET.fromstring(img_xml)
    cap_elem = CAPTION(caption_text)
    return [img_elem, cap_elem]


# ── Registrar imágenes en rels y content types ────────────────────────────────

def add_image(img_path: Path, rels_root: ET.Element,
              ct_root: ET.Element, rId: str) -> None:
    """Copia la imagen a word/media/ y registra la relación y content type."""
    shutil.copy2(img_path, MEDIA / img_path.name)

    rel = ET.SubElement(rels_root, "Relationship")
    rel.set("Id", rId)
    rel.set("Type",
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel.set("Target", f"media/{img_path.name}")

    ext = img_path.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg",
            "jpeg": "image/jpeg"}.get(ext, "image/png")
    ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    existing = [e.get("Extension", "")
                for e in ct_root.findall(f"{{{ct_ns}}}Default")]
    if ext not in existing:
        d = ET.SubElement(ct_root, f"{{{ct_ns}}}Default")
        d.set("Extension", ext)
        d.set("ContentType", mime)


# ── Cargar XMLs ───────────────────────────────────────────────────────────────
print("  Cargando XMLs...")
doc_tree  = ET.parse(DOC_XML)
rels_tree = ET.parse(RELS_XML)
ct_tree   = ET.parse(CT_XML)

doc_root   = doc_tree.getroot()
body       = doc_root.find(f"{{{W_NS}}}body")
rels_root  = rels_tree.getroot()
ct_root    = ct_tree.getroot()

# ── Registrar las 6 figuras ───────────────────────────────────────────────────
print("  Registrando imágenes...")
FIG = {}  # fname → rId
fig_defs = {
    "fig5_1_arquitectura_general.png": "rIdCap5F1",
    "fig5_2_pipeline_c2_rag.png":      "rIdCap5F2",
    "fig5_3_pipeline_c3_pii.png":      "rIdCap5F3",
    "fig5_4_embeddings_vectorstore.png":"rIdCap5F4",
    "fig5_5_scoring_engine.png":        "rIdCap5F5",
    "fig5_6_extraccion_documentos.png": "rIdCap5F6",
}
for fname, rId in fig_defs.items():
    p = FIGURES_DIR / fname
    if p.exists():
        add_image(p, rels_root, ct_root, rId)
        FIG[fname] = rId
        print(f"    ✓ {fname} → {rId}")
    else:
        print(f"    ✗ {fname} no encontrada")

# EMUs (1 cm = 360000 EMU). Ancho ~16 cm = 5760000 EMU
def _emu(cm): return int(cm * 360000)
SIZES = {
    "fig5_1_arquitectura_general.png": (_emu(16), _emu(9.0)),
    "fig5_2_pipeline_c2_rag.png":      (_emu(15), _emu(7.5)),
    "fig5_3_pipeline_c3_pii.png":      (_emu(15), _emu(6.5)),
    "fig5_4_embeddings_vectorstore.png":(_emu(15), _emu(8.0)),
    "fig5_5_scoring_engine.png":        (_emu(15), _emu(7.0)),
    "fig5_6_extraccion_documentos.png": (_emu(15), _emu(6.5)),
}

def F(fname: str, caption: str) -> list[ET.Element]:
    """Atajo para crear párrafo de imagen + caption."""
    rId = FIG.get(fname)
    if not rId:
        return []
    cx, cy = SIZES[fname]
    return IMG(rId, cx, cy, caption, img_id=random.randint(5200, 9990))


# ── Contenido por sección H2 ──────────────────────────────────────────────────

CONTENT: dict[str, list] = {

"Diseño detallado del pipeline RAG": [
    P("El pipeline RAG (Retrieval-Augmented Generation) de SISTAC constituye el núcleo técnico del sistema. Su diseño responde a la necesidad de superar las limitaciones de los modelos de lenguaje cuando operan exclusivamente con su conocimiento paramétrico: en contextos de selección de talento, donde las competencias requeridas varían significativamente entre organizaciones, sectores y roles, un modelo generalista tiende a sobre o subestimar candidatos cuya experiencia no se alinea con los patrones estadísticamente más frecuentes en su corpus de entrenamiento."),
    P("El diseño propuesto incorpora tres configuraciones experimentales —C1, C2 y C3— que se diferencian en el nivel de información contextual disponible para el modelo en el momento de la evaluación y en la aplicación de mecanismos de protección de datos. Estas configuraciones se describen en detalle en la sección 5.9 y se comparan en el experimento factorial descrito en el Capítulo 6."),
    *F("fig5_1_arquitectura_general.png",
       "Figura 5.1. Arquitectura general del sistema SISTAC con las cuatro configuraciones C0-C3. Fuente: elaboración propia."),
    H3("5.1.1  Principios de diseño"),
    P("La arquitectura del pipeline se rige por cuatro principios fundamentales. El primero es la modularidad: cada componente —extracción de texto, chunking, embedding, retrieval, scoring, anonimización PII— es independiente y puede ser sustituido o actualizado sin afectar al resto del sistema. El segundo es la reproducibilidad: todas las operaciones estocásticas utilizan la semilla RANDOM_SEED = 42, y el modelo de lenguaje se configura con temperatura cero para garantizar determinismo en las evaluaciones. El tercero es la escalabilidad: el vector store (Azure AI Search) soporta corpus de cientos de miles de documentos sin modificación de la arquitectura. El cuarto es la privacidad por diseño: la anonimización PII opera en la capa más temprana posible del pipeline, antes de que los datos sensibles lleguen al índice vectorial o al modelo de lenguaje."),
    H3("5.1.2  Comparación con el estado del arte"),
    P("En contraste con los sistemas de ATS (Applicant Tracking Systems) tradicionales, que realizan búsquedas por palabras clave y aplican filtros heurísticos basados en reglas (Lo et al., 2025), SISTAC utiliza representaciones vectoriales densas que capturan similitud semántica. Esto permite, por ejemplo, identificar que un candidato con experiencia en análisis predictivo con Python es relevante para una vacante de modelado estadístico, aunque los términos exactos no coincidan. Estudios como el de Afzal et al. (2025) demuestran que los enfoques RAG superan en F1 a los modelos LLM puros en tareas de emparejamiento CV-JD en un 8-15%, lo que motivó la hipótesis H2 del presente trabajo."),
],

"Preprocesamiento e indexación de CVs y JDs": [
    P("El preprocesamiento de documentos abarca tres etapas interrelacionadas: la definición del corpus y su origen, la extracción del texto legible a partir de los archivos originales (PDF, DOCX, imágenes), y la segmentación de ese texto en unidades indexables (chunks). Las tres etapas se describen en las subsecciones siguientes."),
    H3("5.2.1  Fuente del corpus: Kaggle Resume Dataset como referencia estadística"),
    P("El corpus de SISTAC emplea CVs generados de forma sintética, pero calibrados a partir de las distribuciones estadísticas observadas en el Kaggle Resume Dataset (UpdatedResumeDataSet, 962 registros en 25 categorías profesionales; disponible públicamente bajo licencia CC0). La decisión de no utilizar directamente los CVs de Kaggle responde a dos razones complementarias. En primer lugar, los documentos del dataset están en inglés y corresponden mayoritariamente al mercado laboral anglosajón, lo que introduce un sesgo de distribución geográfica y cultural incompatible con el objetivo de SISTAC, orientado al contexto hispanohablante rioplatense. En segundo lugar, utilizar datos reales implica riesgos de privacidad y requiere una revisión ética adicional que excede el alcance de este TFE."),
    P("La estrategia adoptada consiste en extraer del dataset de Kaggle las distribuciones estadísticas relevantes: frecuencia de habilidades técnicas por categoría profesional, rangos de años de experiencia, niveles educativos más comunes y densidad léxica típica de los CVs. Estas distribuciones alimentan los parámetros del generador sintético (data/synthetic_corpus_generator.py), garantizando que el corpus SISTAC tenga una estructura estadística verosímil, anclada en datos empíricos reales, aunque los documentos individuales sean ficticios. Este enfoque sigue la metodología de Bruera et al. (2022) para la generación de corpus sintéticos con distribuciones controladas en experimentos de IA para RRHH."),
    H3("5.2.2  Gold Standard híbrido: etiquetado algorítmico y validación experta"),
    P("El Gold Standard —las etiquetas APTO / NO_APTO que se utilizan como ground truth para evaluar H1, H2 y H3— se construye mediante un proceso híbrido de dos etapas. En la primera etapa, un algoritmo de etiquetado transparente y documentado asigna una etiqueta a cada uno de los 300 CVs del corpus. El score algorítmico se compone de cuatro dimensiones: experiencia relevante (0-50 puntos), coincidencia de habilidades con los requisitos del cargo (0-30 puntos), nivel educativo (0-15 puntos) y certificaciones adicionales (0-5 puntos). El umbral de clasificación es score >= 60 para APTO; valores inferiores producen etiqueta NO_APTO. Este umbral difiere del umbral del pipeline (SCORE_THRESHOLD = 70) porque opera sobre puntuaciones calculadas con criterios deterministas conocidos, no sobre estimaciones del LLM."),
    P("En la segunda etapa, un subconjunto de 30 a 50 CVs del conjunto de test es revisado por expertos RRHH de Matriz Uruguay, quienes asignan sus propias etiquetas de forma ciega respecto a las etiquetas algorítmicas. La concordancia entre ambas fuentes se mide mediante el coeficiente kappa de Cohen (κ). Un valor κ >= 0.70 (acuerdo sustancial) valida la calidad del Gold Standard algorítmico y habilita su uso como referencia definitiva para el experimento. Este protocolo híbrido equilibra la reproducibilidad y el control del etiquetado algorítmico con la validez ecológica del juicio experto humano, siguiendo las recomendaciones de Fabris et al. (2025) para la construcción de benchmarks de equidad en sistemas de IA para RRHH."),
    H3("5.2.3  Descripciones de cargo (JDs): adaptación de ofertas reales"),
    P("Las cinco descripciones de cargo (Job Descriptions, JDs) utilizadas en el experimento fueron elaboradas a partir de ofertas de empleo reales publicadas en portales uruguayos (Bumeran, InfoJobs, LinkedIn Uruguay) durante el período 2024-2025. Las ofertas originales fueron anonimizadas —se eliminaron los nombres de las empresas, las direcciones y otros datos identificativos— y adaptadas para estandarizar su extensión y estructura, garantizando que cada JD contenga: título del cargo, resumen del puesto, lista de responsabilidades principales, requisitos técnicos (habilidades y herramientas), requisitos de formación y experiencia, y competencias conductuales esperadas."),
    P("Los cinco perfiles de cargo seleccionados son: (JD_001) Analista de Datos, (JD_002) Desarrollador Backend Python, (JD_003) Especialista en Recursos Humanos, (JD_004) Contador Senior, y (JD_005) Ingeniero de Software. Esta selección cubre tres áreas funcionales distintas (tecnología, administración y RRHH) y representa rangos de seniority y densidad técnica diferentes, lo que incrementa la varianza del experimento y reduce el riesgo de que los resultados sean específicos a un único tipo de cargo. La extensión media de cada JD es de aproximadamente 350 palabras."),
    H3("5.2.4  Extracción de texto"),
    P("La estrategia de extracción varía según el formato del archivo, priorizando siempre soluciones sin costo de API (véase Figura 5.6). Para documentos de texto nativo en PDF, se utiliza la librería pdfplumber (version >= 0.11), que extrae el contenido textual directamente del flujo de objetos PDF sin realizar reconocimiento óptico de caracteres (OCR). Para documentos DOCX, se emplea python-docx, que lee tanto párrafos como contenido tabular, formato habitual en CVs con diseño estructurado."),
    P("En el caso de PDFs escaneados —documentos donde pdfplumber extrae menos de 100 caracteres— y de imágenes (PNG, JPG, WEBP), el sistema recurre a Gemini 2.5 Flash como motor de OCR y comprensión visual. Esta elección se fundamenta en tres ventajas operativas: (1) acepta PDF de forma nativa, sin necesidad de convertirlo previamente a imágenes página por página; (2) dispone de una ventana de contexto de un millón de tokens, lo que permite procesar CVs de varias páginas sin truncamiento; y (3) su costo de procesamiento es aproximadamente siete veces inferior al de Claude Haiku en tareas equivalentes de OCR."),
    *F("fig5_6_extraccion_documentos.png",
       "Figura 5.6. Estrategia de extracción de texto según formato de archivo (doc_extractor.py). Fuente: elaboración propia."),
    H3("5.2.5  Chunking y segmentación"),
    P("Una vez obtenido el texto, el módulo rag/chunking.py aplica RecursiveCharacterTextSplitter de LangChain con los siguientes hiperparámetros: chunk_size = 512 tokens, chunk_overlap = 64 tokens. El solapamiento garantiza que la información semántica que se encuentra en la frontera entre dos chunks no se pierda durante el retrieval."),
    P("Para el experimento, cada CV se combina con cada descripción de cargo en un único documento compuesto, de modo que los chunks resultantes preservan el contexto conjunto CV-JD. Este diseño produce aproximadamente 25 chunks por par. Con 240 CVs de entrenamiento y 5 descripciones de cargo, el índice final contiene aproximadamente 30.000 chunks."),
    H3("5.2.6  División train/test y prevención de data leakage"),
    P("El corpus de 300 CVs sintéticos se divide en una partición de entrenamiento (80%, 240 CVs) y una partición de test (20%, 60 CVs) mediante un muestreo estratificado por (jd_id, expected_label, group_gender), implementado en data/split_corpus.py con RANDOM_SEED = 42. Solo los 240 CVs de entrenamiento se indexan en Azure AI Search. Los 60 CVs de test se reservan para la evaluación de las hipótesis H1, H2 y H3, garantizando que el sistema no haya visto previamente esos documentos durante el retrieval."),
],

"Modelo de embeddings y vector store": [
    P("Los embeddings son representaciones vectoriales densas de alta dimensionalidad que capturan el significado semántico de un fragmento de texto. En SISTAC, los embeddings cumplen dos funciones: primero, poblar el índice vectorial con las representaciones de los chunks de entrenamiento; segundo, transformar la descripción de cargo en el vector de consulta que se utiliza para recuperar los chunks más relevantes durante la evaluación."),
    *F("fig5_4_embeddings_vectorstore.png",
       "Figura 5.4. Modelo de embeddings y arquitectura del índice vectorial en Azure AI Search (HNSW, 768 dims). Fuente: elaboración propia."),
    H3("5.3.1  Modelo de embeddings"),
    P("El modelo seleccionado es paraphrase-multilingual-mpnet-base-v2, disponible en HuggingFace a través de la librería sentence-transformers. Este modelo produce vectores de 768 dimensiones y fue preentrenado sobre más de 50 idiomas, incluyendo español, con especial énfasis en la similitud semántica de párrafos. A diferencia de modelos como text-embedding-3-small de OpenAI, su ejecución es local, lo que elimina la latencia de red y el costo por llamada a API. La latencia de inferencia es de aproximadamente 50 ms por chunk en hardware de consumo (CPU)."),
    P("La dimensionalidad de 768 es un parámetro crítico que debe estar alineada con la configuración del índice en Azure AI Search. Una discrepancia en este valor genera un error HTTP 400 en el momento de la indexación. Durante el desarrollo se detectó que una versión previa del código empleaba el modelo paraphrase-multilingual-MiniLM-L12-v2 (384 dimensiones), lo que habría provocado un fallo silencioso en la carga del índice; este error fue corregido antes de la ejecución del experimento."),
    H3("5.3.2  Índice vectorial en Azure AI Search"),
    P("Azure AI Search implementa el algoritmo HNSW (Hierarchical Navigable Small World) para la búsqueda de vecinos aproximados en alta dimensionalidad. HNSW construye un grafo de proximidad multicapa donde los nodos superiores actúan como puntos de entrada a regiones del espacio vectorial, permitiendo búsquedas sublineales. Esta característica lo hace adecuado para corpus de decenas de miles de documentos, donde la búsqueda exhaustiva resultaría computacionalmente prohibitiva."),
    P("El índice se crea con la API versión 2024-07-01 de Azure AI Search. El schema define nueve campos: identificador de chunk (clave), identificadores de CV y JD (filtrables), texto del chunk (indexable para búsqueda léxica), vector de embedding (768 dims, similitud coseno), indicador de anonimización (filtrable) e índice de posición del chunk. Una diferencia relevante de la API 2024-07-01 respecto a versiones anteriores es que el campo de configuración del ranker semántico utiliza prioritizedContentFields y prioritizedKeywordsFields en lugar de los nombres anteriores contentFields y keywordsFields, cambio que requirió una corrección en el script de creación del índice."),
    H3("5.3.3  Retrieval híbrido"),
    P("Azure AI Search combina dos modalidades de búsqueda en una sola consulta: la búsqueda vectorial (basada en similitud coseno entre el embedding de la consulta y los embeddings del índice) y la búsqueda BM25 (basada en frecuencia de términos, de naturaleza léxica). Esta combinación —denominada retrieval híbrido— captura tanto la similitud conceptual como la coincidencia terminológica, lo que resulta especialmente útil en contextos de selección de talento donde los términos técnicos específicos (nombres de herramientas, certificaciones, lenguajes de programación) tienen valor discriminativo propio."),
],

"Motor de retrieval y reranking": [
    P("Una vez realizado el retrieval híbrido, Azure AI Search aplica su Semantic Ranker para reordenar los resultados recuperados. El Semantic Ranker utiliza un modelo de comprensión de lenguaje natural para evaluar la relevancia contextual de cada chunk frente a la consulta, asignando una puntuación de relevancia semántica que supera la capacidad discriminativa de BM25 y de la similitud coseno aisladas."),
    H3("5.4.1  Configuración del retrieval"),
    P("El sistema recupera los top-k = 5 chunks más relevantes por consulta. Este hiperparámetro se seleccionó como equilibrio entre el enriquecimiento del contexto para el LLM y el riesgo de incluir chunks de baja relevancia que introduzcan ruido en la evaluación. Estudios previos en sistemas RAG para dominio cerrado sugieren que valores de k entre 3 y 7 maximizan la fidelidad en tareas de generación condicionada por recuperación; valores superiores a 10 tienden a degradar la precisión de la respuesta."),
    P("La consulta de retrieval utiliza como vector de entrada el embedding de la descripción de cargo (JD), no el embedding del CV que se está evaluando. Esta elección garantiza que los chunks recuperados sean aquellos que el índice considera más informativos para responder a la pregunta implícita: qué características hacen a un candidato adecuado para este cargo. El resultado es un conjunto de hasta 5 fragmentos que el modelo de lenguaje recibe como contexto adicional."),
    H3("5.4.2  Flujo de evaluación C2 y C3"),
    P("En la configuración C2, el CV del candidato llega al sistema en texto plano. Se extrae su representación textual, se combina con los chunks recuperados y la descripción del cargo, y el conjunto se envía al motor de scoring (sección 5.5). En la configuración C3, el texto del CV pasa primero por el módulo de anonimización PII (sección 5.7) antes de ser procesado por el retrieval y el scoring. Los chunks recuperados provienen del índice C3, que almacena exclusivamente versiones anonimizadas de los CVs de entrenamiento."),
    *F("fig5_2_pipeline_c2_rag.png",
       "Figura 5.2. Flujo del pipeline C2 (LLM + RAG): fases de indexación y evaluación en Azure AI Search. Fuente: elaboración propia."),
    *F("fig5_3_pipeline_c3_pii.png",
       "Figura 5.3. Flujo de anonimización PII previo al pipeline RAG en la configuración C3. Fuente: elaboración propia."),
],

"Motor de scoring y ranking de candidatos (H2)": [
    P("El motor de scoring es el componente central del sistema: recibe el texto del CV, la descripción del cargo y los chunks de contexto RAG (en C2 y C3), y produce una evaluación estructurada de la compatibilidad del candidato con el puesto. La implementación se encuentra en scoring/scorer.py."),
    *F("fig5_5_scoring_engine.png",
       "Figura 5.5. Arquitectura del motor de scoring LLM con cuatro dimensiones ponderadas (scorer.py). Fuente: elaboración propia."),
    H3("5.5.1  Diseño del prompt"),
    P("El prompt de evaluación se estructura en tres componentes: un system prompt que establece el rol del modelo como evaluador experto en selección de talento con instrucción de responder únicamente en JSON válido; un bloque de contexto opcional con los chunks recuperados (solo en C2 y C3); y un user prompt que presenta el CV, la descripción del cargo y las instrucciones de evaluación dimensional."),
    P("El modelo evaluador es claude-sonnet-4-5-20241022, configurado con temperatura = 0.0 para garantizar determinismo en las evaluaciones y max_tokens = 1024 por respuesta. La elección de temperatura cero es fundamental para la reproducibilidad del experimento: dado que múltiples evaluaciones del mismo CV deben producir el mismo score, cualquier componente estocástica del modelo introduciría varianza espuria en las métricas de H2."),
    H3("5.5.2  Dimensiones de evaluación y pesos"),
    P("El score final se compone de cuatro dimensiones ponderadas, calibradas a partir del análisis de las prácticas de evaluación en selección de talento documentadas en la literatura (Gan et al., 2024; Lo et al., 2025):"),
    P("- Competencias técnicas (40%): habilidades específicas del rol, herramientas, lenguajes de programación, certificaciones y licencias profesionales. Recibe el mayor peso porque es el factor con mayor capacidad discriminativa en etapas iniciales de cribado."),
    P("- Experiencia laboral (30%): años de experiencia relevante, roles y responsabilidades similares al cargo, sector de industria y nivel jerárquico. El segundo peso más alto refleja que la experiencia es el predictor más robusto del desempeño laboral en la literatura de psicología industrial."),
    P("- Formación académica (20%): título universitario, institución, posgrados y cursos relevantes. El peso moderado reconoce que la formación formal es condición necesaria en muchos roles pero no suficiente para predecir el desempeño."),
    P("- Soft skills (10%): liderazgo, comunicación efectiva, trabajo en equipo y adaptabilidad, inferidos del lenguaje del CV. El peso menor refleja la dificultad de inferir estas competencias de manera confiable a partir de texto."),
    H3("5.5.3  Umbral de decisión y output"),
    P("El score final es un entero en el rango [0, 100]. La decisión de clasificación se aplica con un umbral SCORE_THRESHOLD = 70: candidatos con score >= 70 son clasificados como APTO, y aquellos con score < 70 como NO_APTO. Este umbral fue calibrado empíricamente durante el piloto de cinco CVs comparando la distribución de scores con las etiquetas del Gold Standard. El mismo umbral se aplica en C1, C2 y C3 para garantizar la comparabilidad de las hipótesis. El output del LLM se parsea con json.loads(); ante JSONDecodeError el sistema aplica un mecanismo de recuperación por expresiones regulares. En las pruebas piloto, la tasa de fallo de parseo fue inferior al 2% con temperature = 0."),
],

"Evaluación técnica del pipeline (in-vitro, H2)": [
    P("La evaluación técnica del pipeline RAG utiliza el framework RAGAS (Retrieval-Augmented Generation Assessment) para medir la calidad del sistema en tres dimensiones ortogonales: fidelidad de la respuesta respecto a los chunks recuperados (faithfulness), relevancia de la respuesta respecto a la pregunta planteada (answer relevancy) y precisión de los chunks recuperados respecto a los documentos relevantes del corpus (context precision)."),
    H3("5.6.1  Configuración de RAGAS"),
    P("RAGAS requiere un LLM juez para calcular las métricas de faithfulness y answer relevancy. Se utiliza Claude Haiku como modelo juez —via ChatAnthropic de LangChain— en lugar de GPT-4, ya que el proyecto opera íntegramente sobre la infraestructura de Anthropic. Esta configuración se inicializa en rag/ragas_eval.py. El dataset de evaluación RAGAS se construye como una lista de registros {question, answer, contexts, ground_truth}, donde question es la descripción del cargo, answer es la justificación generada por el scorer, contexts son los chunks recuperados, y ground_truth es la etiqueta del Gold Standard."),
    H3("5.6.2  Métricas RAGAS y resultados del piloto"),
    P("Las tres métricas principales son: Faithfulness (fidelidad) — mide en qué proporción las afirmaciones de la respuesta están soportadas por los chunks recuperados, detectando alucinaciones del LLM. Answer Relevancy — mide si la justificación generada responde efectivamente a las características del cargo. Context Precision — mide si los chunks recuperados son los más relevantes del corpus para la consulta dada."),
    P("Los resultados del piloto sobre cinco CVs deben interpretarse como una prueba de viabilidad técnica del pipeline, no como métricas definitivas. La evaluación estadística completa se realiza sobre los 60 CVs del conjunto de test en el experimento factorial del Capítulo 6. En caso de incompatibilidad de versiones de RAGAS con el entorno, el sistema dispone de un mecanismo de fallback basado en métricas proxy: overlap ROUGE-L entre la justificación y los chunks para estimar fidelidad, y similitud coseno entre los chunks y la JD para estimar precisión del contexto."),
    H3("5.6.3  Limitaciones de la evaluación in-vitro"),
    P("La evaluación RAGAS mide la calidad técnica del pipeline RAG de forma aislada, pero no puede reemplazar la validación experimental completa con Gold Standard. En particular, una alta fidelidad (faithfulness) no implica necesariamente una alta precisión de clasificación (F1): es posible que el modelo genere justificaciones perfectamente fundamentadas en los chunks pero aplique el umbral de decisión de forma incorrecta. Por esta razón, las métricas RAGAS se reportan como métricas complementarias de diagnóstico en la sección de resultados H2, no como métricas primarias de la hipótesis."),
],

"Módulo de anonimización PII (H3)": [
    P("El módulo de anonimización PII (Personally Identifiable Information) es el componente diferenciador de la configuración C3. Su objetivo es eliminar o sustituir por entidades genéricas todos los datos que permitan identificar directa o indirectamente al candidato antes de que el texto llegue al motor de retrieval o al LLM evaluador. La implementación se encuentra en pii/anonymizer.py mediante la clase SistacAnonymizer."),
    *F("fig5_3_pipeline_c3_pii.png",
       "Figura 5.3. Posición del módulo PII en el pipeline C3: opera antes del chunking y el retrieval. Fuente: elaboración propia."),
    H3("5.7.1  Stack tecnologico: Presidio + spaCy"),
    P("SistacAnonymizer combina dos librerías open source. Microsoft Presidio (version >= 2.2.354) actúa como motor de detección y anonimización de entidades PII, incorporando analizadores predefinidos para más de 20 tipos de entidades: nombres de personas, números de identidad, correos electrónicos, números de teléfono, fechas de nacimiento, entre otros. spaCy (version >= 3.7.0) con el modelo es_core_news_lg proporciona el procesamiento lingüístico en español necesario para que Presidio identifique con precisión las entidades nombradas en el texto."),
    P("La elección de este stack responde al principio de privacidad por diseño establecido en el Reglamento (UE) 2024/1689 (EU AI Act) y en la Ley Uruguaya 18.331 de Protección de Datos Personales. El procesamiento es completamente local —sin llamadas a APIs externas— lo que garantiza que los datos de los candidatos no abandonen el entorno controlado del sistema en ninguna etapa del proceso de anonimización."),
    H3("5.7.2  Entidades detectadas y estrategia de sustitucion"),
    P("El módulo detecta y sustituye las siguientes categorías de entidades: nombres de personas (etiqueta <PERSONA>), números de identidad y documentos (<ID>), direcciones de correo electrónico (<EMAIL>), números de teléfono (<TELEFONO>), fechas de nacimiento y edades explícitas (<EDAD>), referencias de género explícitas en primera persona (<GENERO>), y direcciones físicas (<DIRECCION>). La estrategia de sustitución por etiquetas genéricas —en lugar de eliminación— preserva la estructura sintáctica del texto, lo que mejora la calidad del chunking y del retrieval posterior."),
    H3("5.7.3  Validacion del modulo"),
    P("El módulo PII cuenta con una suite de 10 tests unitarios (pii/test_anonymization.py) que validan la correcta detección y sustitución de cada tipo de entidad, así como el comportamiento ante textos vacíos, textos sin PII y textos con entidades en múltiples formatos (DNI uruguayo, formato europeo, formato anglosajón). Los 10 tests pasan satisfactoriamente en el entorno de desarrollo. Una limitación conocida es que la precisión de Presidio en español es inferior a su precisión en inglés, con tasas de falsos negativos del orden del 5-10% para nombres propios poco frecuentes en el corpus de entrenamiento de es_core_news_lg. Esta limitación se documenta en la discusión de resultados de H3."),
],

"Marco de métricas de equidad algorítmica (H3)": [
    P("La hipótesis H3 postula que la anonimización PII reduce significativamente el sesgo demográfico en las decisiones de selección automatizada. Para operacionalizar esta hipótesis, SISTAC implementa un marco de métricas de equidad algorítmica basado en las definiciones de disparate impact del marco legal EEOC (Equal Employment Opportunity Commission) y en las métricas estadísticas de fairness de la literatura de inteligencia artificial (Chouldechova, 2017; Fabris et al., 2025)."),
    H3("5.8.1  Disparate Impact Ratio (DIR)"),
    P("El Disparate Impact Ratio (DIR) se define como el cociente entre la tasa de selección del grupo protegido y la tasa de selección del grupo de referencia. En el contexto de SISTAC, el grupo protegido es el colectivo femenino y el grupo de referencia es el colectivo masculino (siguiendo la clasificación binaria del corpus sintético). Formalmente: DIR = P(APTO | genero=F) / P(APTO | genero=M)."),
    P("La regla de las cuatro quintas partes (EEOC 4/5 Rule) establece que un sistema de selección es potencialmente discriminatorio si DIR < 0.80. En consecuencia, el umbral de la hipótesis H3 es DIR >= 0.80 para la configuración C3. La hipótesis nula es que la anonimización no modifica el DIR de manera estadísticamente significativa respecto a C2."),
    H3("5.8.2  Statistical Parity Difference (SPD)"),
    P("El Statistical Parity Difference (SPD) mide la diferencia absoluta en las tasas de selección entre grupos demográficos: SPD = P(APTO | genero=F) - P(APTO | genero=M). Un valor SPD = 0 indica paridad estadística perfecta. Valores negativos de SPD indican que el grupo femenino tiene una tasa de selección inferior. El marco de Chouldechova (2017) advierte que la equidad estadística y la equidad calibrada son en general incompatibles cuando las tasas de prevalencia difieren entre grupos, limitación teórica que se discute en el Capítulo 8."),
    H3("5.8.3  Implementacion en evaluation/fairness_metrics.py"),
    P("El módulo evaluation/fairness_metrics.py implementa las funciones fairness_report(), compute_dir() y compute_spd(), que reciben el dataframe de resultados del experimento factorial y calculan DIR y SPD para cada configuración y cada par de grupos demográficos. Los resultados se exportan en formato CSV a paper/tables/ para su inserción en las tablas del Capítulo 7."),
    P("Una consideración metodológica importante es que el corpus sintético garantiza un balance perfecto de género (50% femenino / 50% masculino) y de etiqueta (50% APTO / 50% NO_APTO). En corpus reales con distribuciones desequilibradas, las métricas de equidad deben interpretarse con precaución, ya que el DIR puede verse influenciado por diferencias en la calificación objetiva de los candidatos más que por sesgos del sistema."),
],

"Configuraciones C1, C2 y C3 del experimento": [
    P("El experimento factorial de SISTAC compara tres configuraciones de sistema automatizado —C1, C2 y C3— entre sí y contra la línea base de screening manual C0. Cada configuración instrumenta una capacidad adicional sobre la anterior, permitiendo aislar el efecto de cada componente sobre las hipótesis H1, H2 y H3."),
    H3("5.9.1  Configuracion C1 — LLM puro"),
    P("En C1, el sistema evalúa el par (CV, JD) utilizando exclusivamente la capacidad paramétrica del modelo de lenguaje, sin acceso a documentos externos. El LLM recibe como entrada el texto completo del CV y la descripción del cargo, y genera el score, la decisión y la justificación en formato JSON. Esta configuración constituye la línea base del sistema automatizado y permite medir la mejora marginal atribuible al componente RAG (comparación C1 vs. C2, hipótesis H2) y la reducción de sesgo atribuible a la anonimización PII (comparación C1 vs. C3, hipótesis H3)."),
    H3("5.9.2  Configuracion C2 — LLM + RAG"),
    P("C2 agrega el componente de retrieval sobre el índice vectorial de Azure AI Search. Antes de invocar al scorer, el sistema recupera los cinco chunks más relevantes del corpus de entrenamiento (240 CVs x 5 JDs, sin anonimización) para el cargo evaluado. Estos chunks se incorporan al prompt del LLM como contexto adicional, enriqueciendo la evaluación con información específica del dominio y del rol. La hipótesis H2 predice que C2 alcanzará F1 >= 0.85 frente al Gold Standard, superando a C1."),
    H3("5.9.3  Configuracion C3 — LLM + RAG + PII"),
    P("C3 incorpora el módulo SistacAnonymizer como primer paso del pipeline. El texto del CV, antes de llegar al retrieval y al scorer, es procesado por Presidio + spaCy para sustituir todas las entidades PII por etiquetas genéricas. El índice vectorial de C3 almacena exclusivamente versiones anonimizadas de los CVs de entrenamiento, de modo que ningún dato personal del candidato llega al modelo de lenguaje ni queda persistido en el vector store. La hipótesis H3 predice que DIR(C3) > DIR(C2), es decir, que la anonimización reduce la discriminación algorítmica por género."),
    H3("5.9.4  Resumen comparativo de configuraciones"),
    P("Las cuatro configuraciones del experimento se pueden resumir de la siguiente forma. C0 (Screening Manual): evaluación por un revisor humano, sin automatización, tiempo medio de 5-10 minutos por CV, sirve como línea base para medir eficiencia (H1). C1 (LLM Puro): Claude Sonnet sin RAG ni PII, tiempo de evaluacion aproximado de 8 segundos por CV, métricas F1 y AUC-ROC (H2) y DIR/SPD (H3). C2 (LLM + RAG): Claude Sonnet con Azure AI Search, retrieval híbrido y Semantic Ranker, tiempo aproximado de 12 segundos por CV, métrica principal F1 (H2). C3 (LLM + RAG + PII): Claude Sonnet con Azure AI Search y anonimización Presidio+spaCy, tiempo aproximado de 15 segundos por CV, métrica principal DIR (H3)."),
    P("El orquestador del experimento (experiments/orquestador_c0_c3.py) ejecuta las cuatro configuraciones sobre los 60 CVs del conjunto de test e invoca los módulos de métricas (evaluation/efficiency_metrics.py, evaluation/efficacy_metrics.py, evaluation/fairness_metrics.py) para calcular los resultados que se reportan en el Capítulo 7."),
    *F("fig5_1_arquitectura_general.png",
       "Figura 5.9. Comparativa de las cuatro configuraciones del experimento SISTAC. Fuente: elaboración propia."),
],

}

# ── Insertar en el documento ──────────────────────────────────────────────────
print("  Buscando posiciones H2 en el documento...")

# Recopilar todos los elementos del body como lista
body_children = list(body)
h2_positions = {}

for i, elem in enumerate(body_children):
    style_elem = elem.find(f".//{_w('pStyle')}")
    if style_elem is None:
        continue
    style_val = style_elem.get(_w("val"), "")
    if style_val != "Ttulo2":
        continue
    texts = [t.text or "" for t in elem.findall(f".//{_w('t')}")]
    text = "".join(texts).strip()
    for key in CONTENT:
        if key in text:
            h2_positions[key] = i
            break

print(f"  H2 encontrados ({len(h2_positions)}): {list(h2_positions.keys())}")

# Insertar en orden inverso (para no desplazar índices)
for key in reversed(list(CONTENT.keys())):
    pos = h2_positions.get(key)
    if pos is None:
        print(f"    ✗ No encontrado: {key[:50]}")
        continue

    # Aplanar la lista de contenido (algunos items son listas de elementos)
    flat_elems = []
    for item in CONTENT[key]:
        if isinstance(item, list):
            flat_elems.extend(item)
        elif item is not None:
            flat_elems.append(item)
    flat_elems.append(BLANK())

    # Insertar después del H2 (pos+1), en orden inverso para mantener secuencia
    for elem in reversed(flat_elems):
        body.insert(pos + 1, elem)

    print(f"    ✓ '{key[:45]}...' ({len(flat_elems)} elementos)")

# ── Guardar y reempacar ───────────────────────────────────────────────────────
print("  Guardando XMLs...")
doc_tree.write(DOC_XML,   xml_declaration=True, encoding="UTF-8")
rels_tree.write(RELS_XML, xml_declaration=True, encoding="UTF-8")
ct_tree.write(CT_XML,     xml_declaration=True, encoding="UTF-8")

print("  Reempacando docx...")
with zipfile.ZipFile(DOCX_PATH, "w", zipfile.ZIP_DEFLATED) as zout:
    for file in WORK_DIR.rglob("*"):
        if file.is_file():
            zout.write(file, file.relative_to(WORK_DIR))

shutil.rmtree(WORK_DIR)
print(f"\n  Tamano final: {DOCX_PATH.stat().st_size // 1024} KB")
print(f"\n✓ SISTAC_TFE.docx actualizado (Cap. 5 con XML correcto)")
print(f"  Backup: paper/backups/{backup_name}")
