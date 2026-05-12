"""
orquestador_c0_c3.py — Orquestador del experimento factorial C0-C3

Ejecuta las cuatro condiciones experimentales y consolida los resultados
en tablas Word (.docx) y CSV para insertar en paper/SISTAC_TFE.docx.

Autores: David I. Madrid Oyanadel + Mario A. Belvisi Lescano

CÓMO EJECUTAR:
    python scripts/python/experiments/orquestador_c0_c3.py

OUTPUTS (en paper/tables/):
    tab_resultados_h1.docx   — Tabla de tiempos (H1)
    tab_resultados_h1.csv
    tab_resultados_h2.docx   — Tabla F1/AUC-ROC (H2)
    tab_resultados_h2.csv
    tab_resultados_h3.docx   — Tabla DIR/SPD (H3)
    tab_resultados_h3.csv
    tab_comparativa.docx     — Comparativa integrada C0-C3
"""

import random
import sys
from pathlib import Path

import numpy as np

# Semilla global (INV-14: set.seed equivalente Python)
random.seed(42)
np.random.seed(42)

SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from config import TABLES_DIR, EVAL_SETS, ensure_dirs


def run_baseline_c0():
    """
    C0: Screening manual — carga tiempos de C0 desde archivo de log.
    Los tiempos de C0 son registrados manualmente por los evaluadores RRHH.
    """
    # TODO: Cargar tiempos de C0 desde EVAL_SETS / "gold_standard_times.csv"
    raise NotImplementedError("C0: cargar tiempos del Gold Standard manual")


def run_c1_llm_pure():
    """C1: LLM puro sin RAG."""
    # TODO: Implementar con rag/pipeline.py (modo sin retrieval)
    raise NotImplementedError("C1: implementar pipeline LLM puro")


def run_c2_llm_rag():
    """C2: LLM + RAG."""
    # TODO: Implementar con rag/pipeline.py (modo con retrieval)
    raise NotImplementedError("C2: implementar pipeline LLM+RAG")


def run_c3_llm_rag_pii():
    """C3: LLM + RAG + PII anonimización."""
    # TODO: Implementar con pii/anonymizer.py → rag/pipeline.py
    raise NotImplementedError("C3: implementar pipeline LLM+RAG+PII")


def save_csv(data: list[dict], filename: str):
    """Guarda resultados como CSV en paper/tables/."""
    import csv
    ensure_dirs()
    path = TABLES_DIR / filename
    if not data:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"  → CSV: {path}")


def save_word_table(
    headers: list[str],
    rows: list[list[str]],
    caption: str,
    filename: str,
    note: str = "",
):
    """
    Guarda una tabla de resultados como .docx en paper/tables/.

    Requiere: pip install python-docx
    El archivo .docx generado puede insertarse directamente en SISTAC_TFE.docx
    copiando la tabla (Ctrl+A en el .docx de tabla → pegar en SISTAC_TFE.docx).
    """
    try:
        from docx import Document as DocxDocument
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
    except ImportError:
        print("  ADVERTENCIA: python-docx no instalado. Instalar con: pip install python-docx")
        print("  Solo se generará el CSV.")
        return

    ensure_dirs()
    doc = DocxDocument()

    # Título de la tabla
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(caption)
    run.bold = True
    run.font.size = Pt(11)

    # Tabla
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"

    # Encabezados
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].runs[0].bold = True
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Filas de datos
    for r_idx, row in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
            row_cells[c_idx].paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            )

    # Nota al pie
    if note:
        p_note = doc.add_paragraph()
        run_note = p_note.add_run(f"Nota. {note}")
        run_note.italic = True
        run_note.font.size = Pt(10)

    path = TABLES_DIR / filename
    doc.save(str(path))
    print(f"  → Word: {path}")


def main():
    print("=" * 60)
    print("SISTAC — Experimento Factorial C0-C3")
    print("=" * 60)

    # TODO: Una vez implementadas las funciones run_cX():
    # 1. Ejecutar C0-C3 con el mismo dataset de evaluación
    # 2. Calcular métricas H1 (efficiency_metrics.py)
    # 3. Calcular métricas H2 (efficacy_metrics.py)
    # 4. Calcular métricas H3 (fairness_metrics.py)
    # 5. Guardar resultados con save_word_table() y save_csv()
    # 6. Insertar tablas en paper/SISTAC_TFE.docx (sección 7)

    print("\nNOTA: Las funciones run_cX() aún no están implementadas.")
    print("Implementar rag/pipeline.py y pii/anonymizer.py primero.")
    print("\nCuando los experimentos estén listos, ejecutar este script.")
    print("Los outputs se guardarán en:")
    print(f"  {TABLES_DIR}/")
    print("\nFormato de outputs: .docx (insertar en SISTAC_TFE.docx) + .csv (respaldo)")
    print("\nEjemplo de estructura de tabla H2 (completar con datos reales):")

    # Ejemplo de tabla vacía para verificar el pipeline de exportación
    example_h2_headers = ["Configuración", "F1-score (macro)", "AUC-ROC", "IC 95% AUC-ROC", "H2 aceptada"]
    example_h2_rows = [
        ["C1 (LLM puro)",         "TODO", "TODO", "(TODO, TODO)", "TODO"],
        ["C2 (LLM + RAG)",        "TODO", "TODO", "(TODO, TODO)", "TODO"],
        ["C3 (LLM + RAG + PII)",  "TODO", "TODO", "(TODO, TODO)", "TODO"],
    ]
    save_word_table(
        headers=example_h2_headers,
        rows=example_h2_rows,
        caption="Tabla 4. Métricas de eficacia por configuración frente al Gold Standard (H2)",
        filename="tab_resultados_h2_template.docx",
        note="IC 95% calculados con bootstrap (B = 1000). Umbral H2: F1 ≥ 0.85. TODO = completar tras experimentos.",
    )


if __name__ == "__main__":
    main()
