"""
sistac/figures/insert_cap5_docx.py  (v2 — XML correcto)
Inserta el contenido del Capítulo 5 en SISTAC_TFE.docx.

Correcciones respecto a v1:
  - Párrafos Normal sin declarar pStyle (herencia) + lang=es-UY correcto
  - Imágenes con fromstring() para preservar namespaces inline
  - Captions con estilo Piedefoto-tabla (el de la plantilla UNIR)
  - Sin make_list_item: los bullets son párrafos normales con guión
  - Ttulo3 con estructura exacta del documento real

Uso:
    py -3 -X utf8 sistac/figures/insert_cap5_docx.py
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

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCX_PATH   = _PROJECT_ROOT / "paper" / "Talento sin nombre anonimización, LLMs y RAG en el cribado curricular grupo 4 ESIT.docx"
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

# EMUs (1 cm = 360000 EMU). Ancho ~15 cm = 5400000 EMU
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

# ── Cargar borrador Markdown dinámicamente (Desacoplado) ──────────────────────
MD_SOURCE_PATH = _PROJECT_ROOT / "paper" / "sections" / "Capitulo_4_arquitectura_implementacion.md"

def parse_markdown_to_content(md_path: Path) -> dict[str, list]:
    content = {}
    if not md_path.exists():
        print(f"  [ERROR] No se encontró el borrador Markdown en: {md_path}")
        return content
        
    print(f"  [Parser] Cargando texto desde {md_path.name}...")
    md_text = md_path.read_text(encoding="utf-8")
    lines = md_text.splitlines()
    
    current_heading2 = None
    current_elements = []
    
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Bloques de código (Mermaid/Python)
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            continue
            
        # Tablas Markdown simples
        if stripped.startswith("|"):
            continue
            
        # Encabezado Nivel 2
        if stripped.startswith("## "):
            if current_heading2 and current_elements:
                content[current_heading2] = current_elements
            
            # Limpiar número de sección (ej: "4.3. Pipeline RAG" -> "Pipeline RAG")
            raw_title = stripped[3:].strip()
            import re
            cleaned_title = re.sub(r"^\d+(\.\d+)*\.\s*", "", raw_title)
            current_heading2 = cleaned_title
            current_elements = []
            continue
            
        if not current_heading2:
            continue
            
        # Encabezado Nivel 3
        if stripped.startswith("### "):
            title3 = stripped[4:].strip()
            import re
            title3_clean = re.sub(r"^\d+(\.\d+)*\.\s*", "", title3)
            current_elements.append(H3(title3_clean))
            continue
            
        # Pie de foto / Figura (ej: "*Figura 4.x. ...*") o tag de imagen
        if (("figura" in stripped.lower() and ("fuente:" in stripped.lower() or "elaboración" in stripped.lower())) or 
                stripped.startswith("![") or (".png" in stripped.lower() and ("fig5_" in stripped.lower() or "fig4_" in stripped.lower()))):
            
            img_file = None
            text_lower = stripped.lower()
            if "arquitectura general" in text_lower or "figura 4.1" in text_lower or "figura 5.1" in text_lower or "fig5_1" in text_lower:
                img_file = "fig5_1_arquitectura_general.png"
            elif "flujo del pipeline c2" in text_lower or "figura 4.7" in text_lower or "figura 5.2" in text_lower or "fig5_2" in text_lower:
                img_file = "fig5_2_pipeline_c2_rag.png"
            elif "posición del módulo pii" in text_lower or "figura 4.9" in text_lower or "figura 5.3" in text_lower or "fig5_3" in text_lower or "modulo pii" in text_lower:
                img_file = "fig5_3_pipeline_c3_pii.png"
            elif "embeddings" in text_lower or "figura 4.4" in text_lower or "figura 5.4" in text_lower or "fig5_4" in text_lower:
                img_file = "fig5_4_embeddings_vectorstore.png"
            elif "scoring" in text_lower or "figura 4.8" in text_lower or "figura 5.5" in text_lower or "fig5_5" in text_lower:
                img_file = "fig5_5_scoring_engine.png"
            elif "extracción" in text_lower or "figura 4.6" in text_lower or "figura 5.6" in text_lower or "fig5_6" in text_lower:
                img_file = "fig5_6_extraccion_documentos.png"
                
            if img_file:
                caption_text = stripped.replace("*", "").replace("![", "").replace("]", "").strip()
                caption_text = re.sub(r"\(.*?\)", "", caption_text).strip()
                current_elements.extend(F(img_file, caption_text))
            continue
            
        # Listas
        if stripped.startswith("* ") or stripped.startswith("- "):
            text = "• " + stripped[2:].strip()
            current_elements.append(P(text))
        else:
            current_elements.append(P(stripped))
            
    # Última sección
    if current_heading2 and current_elements:
        content[current_heading2] = current_elements
        
    return content

CONTENT = parse_markdown_to_content(MD_SOURCE_PATH)

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
