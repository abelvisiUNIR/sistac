"""
Genera las figuras del análisis complementario (Track 3) a 300 dpi.

Lee los CSV producidos por evaluation/analisis_mejoras_estadisticas.py
(en paper/tables/mejoras/) y escribe:

  paper/figures/mejoras/fig_f1_vs_umbral.png      -> para la sección de eficacia
  paper/figures/mejoras/fig_dir_genero_ic.png     -> para la sección de equidad

Uso:
  python sistac/figures/gen_track3_figures.py

Cumple INV-W3 (300 dpi) e INV-16 (rutas relativas).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TAB = PROJECT_ROOT / "paper" / "tables" / "mejoras"
OUT = PROJECT_ROOT / "paper" / "figures" / "mejoras"

COLORS = {"c1": "#1f77b4", "c2": "#ff7f0e", "c3": "#2ca02c"}
LABELS = {"c1": "C1 (LLM puro)", "c2": "C2 (LLM + RAG)", "c3": "C3 (RAG + PII)"}


def fig_f1_vs_umbral():
    curva = pd.read_csv(TAB / "tab_curva_f1_umbral.csv")
    umb = pd.read_csv(TAB / "tab_umbral_optimo.csv")
    fig, ax = plt.subplots(figsize=(7, 4.3), dpi=300)
    for cfg in ["c1", "c2", "c3"]:
        sub = curva[(curva.modelo == "claude") & (curva.config == cfg)].sort_values("umbral")
        ax.plot(sub.umbral, sub.f1_macro, color=COLORS[cfg], label=LABELS[cfg], lw=1.8)
        r = umb[(umb.modelo == "claude") & (umb.config == cfg)].iloc[0]
        ax.scatter([r.thr_f1opt], [r.f1_opt], color=COLORS[cfg], zorder=5, s=45,
                   edgecolor="white")
    ax.axvline(70, color="#888", ls="--", lw=1.2)
    ax.text(70.8, 0.18, "umbral del\nexperimento (70)", fontsize=8, color="#555")
    ax.axhline(0.85, color="#d62728", ls=":", lw=1.2)
    ax.text(2, 0.86, "umbral de aceptación (0.85)", fontsize=8, color="#d62728")
    ax.set_xlabel("Umbral de decisión (puntos)")
    ax.set_ylabel("F₁-score macro")
    ax.set_title("F₁-score macro según el umbral de decisión (Claude Sonnet 4.5)",
                 fontsize=10)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 0.95)
    ax.legend(loc="lower center", fontsize=8, frameon=False, ncol=3)
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "fig_f1_vs_umbral.png", dpi=300, bbox_inches="tight")
    plt.close()


def fig_dir_genero_ic():
    gen = pd.read_csv(TAB / "tab_equidad_genero_ic.csv")
    order = [("claude", "c1"), ("claude", "c2"), ("claude", "c3"),
             ("gemini", "c2"), ("gemini", "c3")]
    fig, ax = plt.subplots(figsize=(7, 4.0), dpi=300)
    for i, (m, c) in enumerate(order):
        sub = gen[(gen.modelo == m) & (gen.config == c)]
        if sub.empty:
            continue
        r = sub.iloc[0]
        ax.errorbar(i, r.DIR,
                    yerr=[[max(r.DIR - r.DIR_IC95_inf, 0)], [max(r.DIR_IC95_sup - r.DIR, 0)]],
                    fmt="o", color="#1f77b4" if m == "claude" else "#9467bd",
                    capsize=5, ms=7, lw=1.5)
        ax.text(i + 0.12, r.DIR, f"p={r.fisher_p:.2f}", fontsize=7, color="#555", va="center")
    ax.axhline(0.80, color="#d62728", ls="--", lw=1.2)
    ax.text(-0.45, 0.82, "umbral 0.80 (EEOC)", fontsize=8, color="#d62728")
    ax.axhline(1.0, color="#2ca02c", ls=":", lw=1.0)
    ax.text(-0.45, 1.02, "paridad (1.0)", fontsize=8, color="#2ca02c")
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels([f"{m.capitalize()}\n{c.upper()}" for m, c in order], fontsize=8)
    ax.set_ylabel("DIR por género (IC 95% bootstrap)")
    ax.set_title("Disparate Impact Ratio por género con intervalos de confianza", fontsize=10)
    ax.set_ylim(0, 2.5)
    ax.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "fig_dir_genero_ic.png", dpi=300, bbox_inches="tight")
    plt.close()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig_f1_vs_umbral()
    fig_dir_genero_ic()
    print("Figuras escritas en:", OUT)


if __name__ == "__main__":
    main()
