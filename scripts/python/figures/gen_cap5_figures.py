"""
scripts/python/figures/gen_cap5_figures.py
Genera todas las figuras del Capítulo 5 de SISTAC_TFE.

Output: paper/figures/cap5/fig5_1_arquitectura.png ... fig5_6_extraccion.png
Resolución: 300 dpi (mínimo exigido por INV-W3)

Uso:
    py -3 scripts/python/figures/gen_cap5_figures.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# INV-16: rutas via PROJECT_ROOT
_SCRIPTS_DIR = Path(__file__).parent.parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent.parent
FIGURES_DIR = _PROJECT_ROOT / "paper" / "figures" / "cap5"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paleta SISTAC ─────────────────────────────────────────────────────────────
C = {
    "azul":     "#1F4E79",
    "azul_mid": "#2E75B6",
    "azul_claro":"#BDD7EE",
    "verde":    "#375623",
    "verde_mid":"#548235",
    "verde_claro":"#E2EFDA",
    "gris":     "#595959",
    "gris_claro":"#F2F2F2",
    "naranja":  "#C55A11",
    "naranja_claro":"#FCE4D6",
    "morado":   "#7030A0",
    "morado_claro":"#EAD1DC",
    "blanco":   "#FFFFFF",
    "negro":    "#1A1A1A",
}

DPI = 300
FONT = "DejaVu Sans"

def _box(ax, x, y, w, h, text, color, text_color="white", fontsize=9,
         radius=0.04, bold=False, wrap=False):
    """Dibuja un rectángulo redondeado con texto centrado."""
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle=f"round,pad=0,rounding_size={radius}",
                          facecolor=color, edgecolor="white", linewidth=1.2,
                          zorder=3)
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=text_color, fontweight=weight, fontfamily=FONT,
            wrap=wrap, zorder=4,
            multialignment="center")

def _arrow(ax, x0, y0, x1, y1, color=C["gris"], lw=1.5, label=""):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=12),
                zorder=2)
    if label:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx + 0.01, my, label, fontsize=7, color=color,
                ha="left", va="center", fontfamily=FONT, zorder=5)


# ─────────────────────────────────────────────────────────────────────────────
# Figura 5.1 — Arquitectura general: C0, C1, C2, C3
# ─────────────────────────────────────────────────────────────────────────────
def fig_51_arquitectura_general():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_facecolor(C["gris_claro"])
    fig.patch.set_facecolor(C["gris_claro"])

    # Título
    ax.text(7, 7.65, "Arquitectura del sistema SISTAC: Configuraciones C0–C3",
            ha="center", va="top", fontsize=13, fontweight="bold",
            color=C["azul"], fontfamily=FONT)
    ax.text(7, 7.35, "Diseño factorial comparativo: screening manual vs. LLM puro vs. LLM+RAG vs. LLM+RAG+PII",
            ha="center", va="top", fontsize=9, color=C["gris"], fontfamily=FONT)

    configs = [
        ("C0", "Screening\nManual", C["gris"], C["gris_claro"]),
        ("C1", "LLM\nPuro", C["azul_mid"], C["azul_claro"]),
        ("C2", "LLM +\nRAG", C["verde_mid"], C["verde_claro"]),
        ("C3", "LLM + RAG\n+ PII", C["morado"], C["morado_claro"]),
    ]

    xs = [1.75, 5.0, 8.25, 11.5]

    for (cfg, label, color, bg), x in zip(configs, xs):
        # Panel de fondo
        panel = FancyBboxPatch((x - 1.45, 0.3), 2.9, 6.7,
                               boxstyle="round,pad=0,rounding_size=0.15",
                               facecolor=bg, edgecolor=color, linewidth=2,
                               zorder=1, alpha=0.6)
        ax.add_patch(panel)

        # Badge configuración
        badge = FancyBboxPatch((x - 0.45, 6.5), 0.9, 0.45,
                               boxstyle="round,pad=0,rounding_size=0.1",
                               facecolor=color, edgecolor="none", zorder=3)
        ax.add_patch(badge)
        ax.text(x, 6.72, cfg, ha="center", va="center", fontsize=11,
                fontweight="bold", color="white", fontfamily=FONT, zorder=4)
        ax.text(x, 6.2, label, ha="center", va="center", fontsize=9,
                fontweight="bold", color=color, fontfamily=FONT, zorder=4,
                multialignment="center")

    # Inputs comunes
    _box(ax, 7, 5.6, 12.5, 0.55, "Entradas: CV del candidato  ·  Descripción de cargo (JD)",
         C["azul"], fontsize=9, bold=True)

    # Fila: Procesamiento
    proc_labels = [
        "Revisor RRHH\nlee el CV\n(5–10 min/CV)",
        "Claude Sonnet\nlee CV + JD\n(~8 seg/CV)",
        "Chunking → Embeddings\n→ Azure AI Search\n→ Claude Sonnet",
        "PII Anonimización\n→ Chunking → Azure\n→ Claude Sonnet",
    ]
    colors_proc = [C["gris"], C["azul_mid"], C["verde_mid"], C["morado"]]

    for x, label, color in zip(xs, proc_labels, colors_proc):
        _box(ax, x, 4.1, 2.6, 1.3, label, color, fontsize=8)
        _arrow(ax, x, 5.32, x, 4.77, color)

    # Fila: Retrieval (solo C2, C3)
    _box(ax, 8.25, 2.8, 2.6, 0.9, "Azure AI Search\nRetrieval (top-k=5)", C["verde_mid"], fontsize=8)
    _arrow(ax, 8.25, 3.45, 8.25, 3.26, C["verde_mid"])

    _box(ax, 11.5, 2.8, 2.6, 0.9, "Azure AI Search\nRetrieval (top-k=5)", C["morado"], fontsize=8)
    _arrow(ax, 11.5, 3.45, 11.5, 3.26, C["morado"])

    # Flechas de C1, C0 saltando retrieval
    _arrow(ax, 1.75, 3.45, 1.75, 2.1, C["gris"])
    _arrow(ax, 5.0,  3.45, 5.0,  2.1, C["azul_mid"])
    _arrow(ax, 8.25, 2.35, 8.25, 2.1, C["verde_mid"])
    _arrow(ax, 11.5, 2.35, 11.5, 2.1, C["morado"])

    # Fila: Output
    output_labels = [
        "Decisión manual\nSin score numérico",
        "Score 0–100\nDecisión: APTO/NO APTO\nJustificación LLM",
        "Score 0–100\nDecisión: APTO/NO APTO\nJustificación + chunks",
        "Score 0–100 (anon.)\nDecisión: APTO/NO APTO\nEquidad verificada",
    ]
    for x, label, color in zip(xs, output_labels, colors_proc):
        _box(ax, x, 1.2, 2.6, 1.7, label, color, fontsize=7.5)

    # Leyenda H1/H2/H3
    legend_items = [
        mpatches.Patch(color=C["azul_claro"], ec=C["azul_mid"], label="H1: Eficiencia (C0 vs C1-C3)"),
        mpatches.Patch(color=C["verde_claro"], ec=C["verde_mid"], label="H2: Eficacia RAG (C1 vs C2)"),
        mpatches.Patch(color=C["morado_claro"], ec=C["morado"], label="H3: Equidad PII (C2 vs C3)"),
    ]
    ax.legend(handles=legend_items, loc="lower center", bbox_to_anchor=(0.5, -0.01),
              ncol=3, fontsize=8, framealpha=0.9, edgecolor=C["gris"])

    plt.tight_layout(pad=0.3)
    out = FIGURES_DIR / "fig5_1_arquitectura_general.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Figura 5.2 — Pipeline RAG C2: flujo de indexación y evaluación
# ─────────────────────────────────────────────────────────────────────────────
def fig_52_pipeline_c2():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor(C["gris_claro"])

    # ── Panel izquierdo: FASE DE INDEXACIÓN ──────────────────────────────────
    ax = axes[0]
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_facecolor(C["verde_claro"])
    ax.set_title("FASE 1 — Indexación (una vez)", fontsize=11,
                 fontweight="bold", color=C["verde"], pad=8)

    steps_index = [
        (3, 6.3, "Corpus de entrenamiento\n240 CVs + 5 JDs", C["verde"]),
        (3, 5.1, "Extracción de texto\npdfplumber / Gemini 2.5 Flash", C["verde_mid"]),
        (3, 3.9, "Chunking\nRecursiveCharacterTextSplitter\n512 tokens · overlap 64", C["verde_mid"]),
        (3, 2.7, "Embeddings\nparaphrase-multilingual-mpnet-base-v2\n768 dimensiones", C["verde_mid"]),
        (3, 1.5, "Azure AI Search\nÍndice HNSW · Distancia coseno\n~30.000 chunks indexados", C["verde"]),
        (3, 0.4, "Índice listo para retrieval", C["azul"]),
    ]

    for x, y, label, color in steps_index:
        bold = color == C["verde"] or color == C["azul"]
        _box(ax, x, y, 5.2, 0.7, label, color, fontsize=8.5, bold=bold)

    for i in range(len(steps_index) - 1):
        _, y1, _, _ = steps_index[i]
        _, y2, _, _ = steps_index[i + 1]
        _arrow(ax, 3, y1 - 0.35, 3, y2 + 0.35, color=C["verde"])

    # ── Panel derecho: FASE DE EVALUACIÓN ────────────────────────────────────
    ax = axes[1]
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_facecolor(C["azul_claro"])
    ax.set_title("FASE 2 — Evaluación de candidato (por CV)", fontsize=11,
                 fontweight="bold", color=C["azul"], pad=8)

    steps_eval = [
        (3, 6.3, "Nuevo CV + Descripción de cargo", C["azul"]),
        (3, 5.1, "Extracción de texto\npdfplumber / Gemini 2.5 Flash", C["azul_mid"]),
        (3, 3.9, "Embedding de la JD\n768 dims → vector consulta", C["azul_mid"]),
        (3, 2.7, "Azure AI Search\nHybrid retrieval + Semantic Ranker\nTop-k = 5 chunks más relevantes", C["azul_mid"]),
        (3, 1.5, "Claude Sonnet\nCV + JD + 5 chunks contexto\n→ Score (0-100) · 4 dimensiones", C["azul"]),
        (3, 0.4, "APTO (≥70) / NO_APTO (<70) + justificación", C["verde_mid"]),
    ]

    for x, y, label, color in steps_eval:
        bold = color in (C["azul"], C["verde_mid"])
        _box(ax, x, y, 5.2, 0.7, label, color, fontsize=8.5, bold=bold)

    for i in range(len(steps_eval) - 1):
        _, y1, _, _ = steps_eval[i]
        _, y2, _, _ = steps_eval[i + 1]
        _arrow(ax, 3, y1 - 0.35, 3, y2 + 0.35, color=C["azul"])

    plt.suptitle("Figura 5.2 — Pipeline C2: LLM + RAG (Azure AI Search)",
                 fontsize=12, fontweight="bold", color=C["negro"], y=1.01)
    plt.tight_layout(pad=1.5)
    out = FIGURES_DIR / "fig5_2_pipeline_c2_rag.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Figura 5.3 — Pipeline C3 con anonimización PII
# ─────────────────────────────────────────────────────────────────────────────
def fig_53_pipeline_c3_pii():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_facecolor(C["gris_claro"])
    fig.patch.set_facecolor(C["gris_claro"])

    ax.text(6, 5.75, "Figura 5.3 — Pipeline C3: LLM + RAG + Anonimización PII",
            ha="center", va="top", fontsize=12, fontweight="bold",
            color=C["negro"], fontfamily=FONT)

    # Flujo principal
    steps = [
        (1.0, 3.0, "CV bruto\n(con PII)", C["gris"]),
        (3.0, 3.0, "SistacAnonymizer\n(Presidio + spaCy)\nes_core_news_lg", C["morado"]),
        (5.3, 3.0, "CV\nAnonimizado", C["morado"]),
        (7.3, 3.0, "Azure AI Search\nRetrieval\n(top-k = 5)", C["azul_mid"]),
        (9.5, 3.0, "Claude Sonnet\n+ chunks anon.\n→ Score JSON", C["azul"]),
        (11.3, 3.0, "APTO /\nNO_APTO\n(equitativo)", C["verde_mid"]),
    ]

    widths = [1.6, 1.8, 1.4, 1.8, 1.8, 1.4]
    for (x, y, label, color), w in zip(steps, widths):
        _box(ax, x, y, w, 0.9, label, color, fontsize=8)

    # Flechas
    xs_pairs = [(1.8, 2.1), (3.9, 4.6), (6.0, 6.4), (8.2, 8.6), (10.4, 10.6)]
    for x0, x1 in xs_pairs:
        _arrow(ax, x0, 3.0, x1, 3.0, color=C["gris"])

    # Destacar el paso PII
    highlight = FancyBboxPatch((2.05, 2.4), 1.9, 1.2,
                                boxstyle="round,pad=0,rounding_size=0.1",
                                facecolor="none", edgecolor=C["morado"],
                                linewidth=2.5, linestyle="--", zorder=5)
    ax.add_patch(highlight)
    ax.text(3.0, 1.95, "Paso único de C3:\npreviene sesgos demográficos (H3)",
            ha="center", va="top", fontsize=8, color=C["morado"],
            fontfamily=FONT, fontweight="bold")

    # Entidades que se anonim
    entities = ["NOMBRE → <PERSONA>", "DNI → <ID>", "EMAIL → <EMAIL>",
                "EDAD → <EDAD>", "GÉNERO → <GÉNERO>", "DIRECCIÓN → <DIRECCIÓN>"]
    for i, ent in enumerate(entities):
        col_i = i // 3
        row_i = i % 3
        ax.text(2.0 + col_i * 2.1, 1.55 - row_i * 0.32, ent,
                ha="left", va="top", fontsize=7, color=C["morado"],
                fontfamily=FONT)

    # JD (entra al retrieval también)
    _box(ax, 7.3, 4.5, 1.8, 0.6, "JD del cargo\n(sin cambios)", C["azul_claro"],
         text_color=C["azul"], fontsize=8)
    _arrow(ax, 7.3, 4.2, 7.3, 3.5, color=C["azul_mid"])

    ax.text(6, 0.25, "Nota: el índice de Azure AI Search contiene CVs anonimizados (C3) o crudos (C2) según la configuración del experimento.",
            ha="center", va="bottom", fontsize=7.5, color=C["gris"],
            fontfamily=FONT, style="italic")

    plt.tight_layout(pad=0.4)
    out = FIGURES_DIR / "fig5_3_pipeline_c3_pii.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Figura 5.4 — Arquitectura de embeddings y Azure AI Search
# ─────────────────────────────────────────────────────────────────────────────
def fig_54_embeddings_vectorstore():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_facecolor(C["gris_claro"])
    fig.patch.set_facecolor(C["gris_claro"])

    ax.text(6.5, 6.75, "Figura 5.4 — Modelo de embeddings y vector store (Azure AI Search)",
            ha="center", va="top", fontsize=12, fontweight="bold",
            color=C["negro"], fontfamily=FONT)

    # ── Columna izquierda: Modelo de embeddings ────────────────────────────────
    ax.text(2.0, 6.2, "Modelo de Embeddings", ha="center", fontsize=10,
            fontweight="bold", color=C["azul"], fontfamily=FONT)

    _box(ax, 2.0, 5.5, 3.5, 0.7,
         "paraphrase-multilingual-mpnet-base-v2\n(sentence-transformers — HuggingFace)",
         C["azul"], fontsize=8.5)
    _box(ax, 2.0, 4.6, 3.5, 0.65,
         "Dimensiones: 768  |  Multilingüe (50+ idiomas)\nEspecializado en similitud semántica párrafos",
         C["azul_mid"], fontsize=8)
    _box(ax, 2.0, 3.7, 3.5, 0.65,
         "Sin llamada a API  |  Ejecución local\nCosto: $0.00  |  Latencia: ~50ms/chunk",
         C["azul_mid"], fontsize=8)

    ax.text(2.0, 3.05, "Ejemplo:", ha="center", fontsize=8, color=C["gris"], fontfamily=FONT)
    _box(ax, 2.0, 2.5, 3.5, 0.65,
         "\"Analista de datos con Python y SQL\"\n→ [0.023, -0.041, 0.178, ..., 0.092]  (768 dims)",
         C["gris"], fontsize=7.5)

    # ── Columna central: Índice HNSW ───────────────────────────────────────────
    ax.text(6.5, 6.2, "Índice Azure AI Search (HNSW)", ha="center", fontsize=10,
            fontweight="bold", color=C["verde"], fontfamily=FONT)

    # Representación visual del índice HNSW
    np.random.seed(42)
    n_nodes = 18
    xs_n = np.random.uniform(4.5, 8.5, n_nodes)
    ys_n = np.random.uniform(1.0, 5.5, n_nodes)

    # Conexiones HNSW (simuladas)
    connections = [(0,3),(0,5),(1,4),(1,7),(2,6),(3,8),(4,9),(5,10),
                   (6,11),(7,12),(8,13),(9,14),(10,15),(11,16),(12,17),
                   (0,8),(1,9),(3,11),(5,13)]
    for i, j in connections:
        ax.plot([xs_n[i], xs_n[j]], [ys_n[i], ys_n[j]],
                color=C["verde_claro"], lw=0.8, zorder=1)

    ax.scatter(xs_n, ys_n, s=60, c=C["verde_mid"], zorder=3, edgecolors=C["verde"], lw=1)

    # Destacar el nodo query
    ax.scatter([6.5], [5.7], s=120, c=C["naranja"], zorder=4,
               edgecolors=C["naranja"], lw=1.5, marker="*")
    ax.text(6.7, 5.75, "Query (JD)", fontsize=7.5, color=C["naranja"],
            fontfamily=FONT, fontweight="bold")

    # Destacar top-5 vecinos
    dists = [np.sqrt((xs_n[i]-6.5)**2 + (ys_n[i]-5.7)**2) for i in range(n_nodes)]
    top5 = np.argsort(dists)[:5]
    ax.scatter(xs_n[top5], ys_n[top5], s=90, c=C["naranja_claro"],
               zorder=4, edgecolors=C["naranja"], lw=1.5)
    for idx in top5:
        ax.plot([6.5, xs_n[idx]], [5.7, ys_n[idx]],
                color=C["naranja"], lw=1.2, linestyle="--", zorder=2)

    ax.text(6.5, 0.6, "HNSW  |  Similitud coseno  |  ~30.000 chunks\nAPI: azure 2024-07-01  |  Semantic Ranker",
            ha="center", fontsize=8, color=C["verde"], fontfamily=FONT, style="italic")

    # ── Columna derecha: Schema del documento ──────────────────────────────────
    ax.text(11.0, 6.2, "Schema del documento", ha="center", fontsize=10,
            fontweight="bold", color=C["azul"], fontfamily=FONT)

    fields = [
        ("id", "key", C["naranja"]),
        ("cv_id", "filterable", C["azul_mid"]),
        ("jd_id", "filterable", C["azul_mid"]),
        ("chunk_text", "searchable", C["verde_mid"]),
        ("embedding", "vector (768)", C["morado"]),
        ("anonymized", "filterable", C["gris"]),
        ("chunk_index", "sortable", C["gris"]),
    ]

    for i, (name, ftype, color) in enumerate(fields):
        y_f = 5.5 - i * 0.6
        _box(ax, 10.1, y_f, 1.6, 0.42, name, color, fontsize=8)
        _box(ax, 11.9, y_f, 1.6, 0.42, ftype, C["gris_claro"],
             text_color=C["gris"], fontsize=7.5)

    ax.text(10.1, 1.4, "Campo", ha="center", fontsize=8, fontweight="bold",
            color=C["azul"], fontfamily=FONT)
    ax.text(11.9, 1.4, "Tipo/Rol", ha="center", fontsize=8, fontweight="bold",
            color=C["azul"], fontfamily=FONT)

    plt.tight_layout(pad=0.4)
    out = FIGURES_DIR / "fig5_4_embeddings_vectorstore.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Figura 5.5 — Motor de scoring multidimensional
# ─────────────────────────────────────────────────────────────────────────────
def fig_55_scoring_engine():
    fig = plt.figure(figsize=(14, 7))
    fig.patch.set_facecolor(C["gris_claro"])

    ax_main = fig.add_axes([0.0, 0.0, 0.65, 1.0])
    ax_dims = fig.add_axes([0.67, 0.08, 0.31, 0.85])

    # ── Panel izquierdo: flujo del scorer ─────────────────────────────────────
    ax_main.set_xlim(0, 8)
    ax_main.set_ylim(0, 7)
    ax_main.axis("off")
    ax_main.set_facecolor(C["gris_claro"])
    ax_main.text(4, 6.75, "Figura 5.5 — Motor de scoring LLM (scorer.py)",
                 ha="center", va="top", fontsize=11, fontweight="bold",
                 color=C["negro"], fontfamily=FONT)

    # Inputs
    _box(ax_main, 2.0, 5.8, 3.0, 0.65, "Texto del CV", C["azul_mid"], fontsize=9)
    _box(ax_main, 5.5, 5.8, 2.0, 0.65, "Descripción\ndel cargo (JD)", C["azul_mid"], fontsize=9)
    _box(ax_main, 2.0, 4.9, 5.8, 0.65, "Chunks de contexto RAG (top-5) — solo C2/C3", C["verde_mid"], fontsize=9)
    ax_main.text(2.0, 4.55, "Opcional — None en C1", ha="center", fontsize=7.5,
                 color=C["gris"], style="italic", fontfamily=FONT)

    _arrow(ax_main, 2.0, 5.47, 2.0, 4.3, C["azul_mid"])
    _arrow(ax_main, 5.5, 5.47, 5.5, 4.3, C["azul_mid"])

    # Prompt builder
    _box(ax_main, 3.75, 3.9, 5.8, 0.75,
         "Construcción del prompt  (temperature = 0.0, max_tokens = 1024)",
         C["azul"], fontsize=9, bold=True)

    _arrow(ax_main, 3.75, 3.52, 3.75, 2.9, C["azul"])

    # Claude API
    _box(ax_main, 3.75, 2.5, 5.8, 0.75,
         "Claude Sonnet — claude-sonnet-4-5-20241022\nget_chat_completion() → respuesta JSON",
         C["azul"], fontsize=9, bold=True)

    _arrow(ax_main, 3.75, 2.12, 3.75, 1.55, C["azul"])

    # Parser
    _box(ax_main, 3.75, 1.2, 5.8, 0.65,
         "json.loads() + validación  |  Fallback ante JSONDecodeError",
         C["gris"], fontsize=8.5)

    _arrow(ax_main, 3.75, 0.87, 3.75, 0.45, C["azul"])
    _box(ax_main, 3.75, 0.2, 5.8, 0.42,
         "Resultado: {score, decision, dimensions, justification}",
         C["verde"], fontsize=8.5, bold=True)

    # ── Panel derecho: dimensiones ─────────────────────────────────────────────
    ax_dims.axis("off")
    ax_dims.set_xlim(0, 4)
    ax_dims.set_ylim(0, 7)
    ax_dims.set_facecolor(C["azul_claro"])

    panel = FancyBboxPatch((0, 0), 4, 7,
                           boxstyle="round,pad=0,rounding_size=0.1",
                           facecolor=C["azul_claro"], edgecolor=C["azul_mid"],
                           linewidth=1.5)
    ax_dims.add_patch(panel)

    ax_dims.text(2, 6.6, "4 Dimensiones de evaluación", ha="center",
                 fontsize=10, fontweight="bold", color=C["azul"], fontfamily=FONT)

    dims = [
        ("Competencias técnicas", 40, C["azul"], "Habilidades, herramientas,\nlicencias profesionales"),
        ("Experiencia laboral", 30, C["verde_mid"], "Años, roles similares,\nsector de industria"),
        ("Formación académica", 20, C["naranja"], "Título, institución,\nposgrados relevantes"),
        ("Soft skills", 10, C["morado"], "Liderazgo, comunicación,\ntrabajo en equipo"),
    ]

    bar_max_w = 3.2
    y_start = 5.8
    for i, (name, pct, color, desc) in enumerate(dims):
        y = y_start - i * 1.4
        ax_dims.text(0.1, y, f"{name}", ha="left", va="top",
                     fontsize=9, fontweight="bold", color=color, fontfamily=FONT)
        ax_dims.text(3.9, y, f"{pct}%", ha="right", va="top",
                     fontsize=10, fontweight="bold", color=color, fontfamily=FONT)

        # Barra de progreso
        bar_bg = FancyBboxPatch((0.1, y - 0.45), bar_max_w, 0.28,
                                 boxstyle="round,pad=0,rounding_size=0.05",
                                 facecolor=C["gris_claro"], edgecolor="none")
        bar_fill = FancyBboxPatch((0.1, y - 0.45), bar_max_w * pct / 100, 0.28,
                                   boxstyle="round,pad=0,rounding_size=0.05",
                                   facecolor=color, edgecolor="none", alpha=0.8)
        ax_dims.add_patch(bar_bg)
        ax_dims.add_patch(bar_fill)
        ax_dims.text(0.1, y - 0.6, desc, ha="left", va="top",
                     fontsize=7.5, color=C["gris"], fontfamily=FONT, style="italic")

    # Umbral
    ax_dims.text(2, 0.55, "Umbral de decisión", ha="center", fontsize=9,
                 fontweight="bold", color=C["negro"], fontfamily=FONT)
    _box(ax_dims, 1.3, 0.2, 2.0, 0.38, "Score ≥ 70 → APTO", C["verde_mid"], fontsize=9)
    _box(ax_dims, 3.0, 0.2, 1.6, 0.38, "Score < 70 → NO_APTO", C["naranja"], fontsize=9)

    plt.savefig(FIGURES_DIR / "fig5_5_scoring_engine.png", dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ fig5_5_scoring_engine.png")


# ─────────────────────────────────────────────────────────────────────────────
# Figura 5.6 — Extracción de documentos (Gemini 2.5 Flash + pdfplumber)
# ─────────────────────────────────────────────────────────────────────────────
def fig_56_extraccion_documentos():
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_facecolor(C["gris_claro"])
    fig.patch.set_facecolor(C["gris_claro"])

    ax.text(6.5, 5.8, "Figura 5.6 — Estrategia de extracción de texto (doc_extractor.py)",
            ha="center", va="top", fontsize=12, fontweight="bold",
            color=C["negro"], fontfamily=FONT)

    # Entrada
    _box(ax, 6.5, 4.8, 12, 0.65, "Archivo de entrada: CV o JD subido por el usuario",
         C["azul"], fontsize=9, bold=True)

    # Detección de formato
    _box(ax, 6.5, 3.85, 12, 0.65,
         "Detección de formato por extensión de archivo (.pdf · .docx · .doc · .txt · .png · .jpg · .webp)",
         C["gris"], fontsize=9)

    _arrow(ax, 6.5, 4.47, 6.5, 4.18, C["gris"])
    _arrow(ax, 6.5, 3.52, 6.5, 3.2, C["gris"])

    # Bifurcaciones por tipo
    branches = [
        (2.0,  2.5, ".txt", ".txt", C["gris"], "Lectura directa\nUTF-8 / Latin-1"),
        (5.0,  2.5, ".docx", ".docx\n.doc", C["azul_mid"], "python-docx\nPárrafos + tablas"),
        (8.0,  2.5, ".pdf\n(nativo)", ".pdf", C["verde_mid"], "pdfplumber\n(sin API)\n≥100 chars → listo"),
        (11.5, 2.5, "imagen\nPDF scan", ".png .jpg\n.webp .pdf*", C["naranja"], "Gemini 2.5 Flash\nVision / PDF nativo\n1M token context"),
    ]

    ax.text(6.5, 3.2, "↓  ↓  ↓  ↓", ha="center", fontsize=11,
            color=C["gris"], fontfamily=FONT)

    for x, y, label, fmt, color, method in branches:
        # Badge formato
        _box(ax, x, 3.55, 2.0, 0.42, fmt, color, fontsize=8)
        _box(ax, x, 2.5, 2.2, 1.1, label + "\n——\n" + method, color, fontsize=8)

    # Convergencia
    ax.text(6.5, 1.45, "↓  ↓  ↓  ↓", ha="center", fontsize=11,
            color=C["gris"], fontfamily=FONT)

    _box(ax, 6.5, 0.85, 12, 0.65,
         "Texto extraído (string) → pipeline SISTAC (chunking → embeddings → scoring)",
         C["azul"], fontsize=9, bold=True)

    # Nota Gemini
    ax.text(11.5, 1.3,
            "* PDF escaneado: si pdfplumber\nextrae <100 chars → fallback Gemini",
            ha="center", va="top", fontsize=7.5, color=C["naranja"],
            fontfamily=FONT, style="italic")

    # Costos
    ax.text(0.2, 0.25,
            "Costo: pdfplumber=$0.00 · python-docx=$0.00 · Gemini 2.5 Flash≈$0.00035/imagen (7× más barato que Claude Haiku)",
            ha="left", va="bottom", fontsize=7.5, color=C["gris"], fontfamily=FONT)

    plt.tight_layout(pad=0.4)
    out = FIGURES_DIR / "fig5_6_extraccion_documentos.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generando figuras del Capítulo 5 → {FIGURES_DIR}\n")
    fig_51_arquitectura_general()
    fig_52_pipeline_c2()
    fig_53_pipeline_c3_pii()
    fig_54_embeddings_vectorstore()
    fig_55_scoring_engine()
    fig_56_extraccion_documentos()
    print(f"\n✓ Todas las figuras generadas ({DPI} dpi)")
