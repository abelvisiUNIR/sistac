"""
fairness_metrics.py — Métricas de equidad algorítmica para H3

Calcula Disparate Impact Ratio (DIR) y Statistical Parity Difference (SPD)
para evaluar sesgo demográfico entre configuraciones C1, C2, C3.

Autora: Mario A. Belvisi Lescano
"""

import numpy as np
import pandas as pd


def disparate_impact_ratio(
    y_pred: np.ndarray,
    group: np.ndarray,
    privileged_group: int = 1,
    positive_label: int = 1,
) -> float:
    """
    Calcula el Disparate Impact Ratio (DIR).

    DIR = P(ŷ=1 | grupo_minoritario) / P(ŷ=1 | grupo_privilegiado)

    Umbral legal EEOC (regla 4/5): DIR >= 0.80

    Args:
        y_pred: Array de predicciones binarias (1=apto, 0=no apto)
        group:  Array de etiquetas de grupo (1=privilegiado, 0=minoritario)
        privileged_group: Valor que identifica al grupo privilegiado
        positive_label:   Valor de la etiqueta positiva (apto)

    Returns:
        DIR como float. Un valor < 0.80 indica impacto dispar (regla 4/5 EEOC).
    """
    mask_priv = group == privileged_group
    mask_min = group != privileged_group

    p_priv = np.mean(y_pred[mask_priv] == positive_label)
    p_min = np.mean(y_pred[mask_min] == positive_label)

    if p_priv == 0:
        raise ValueError(
            "P(ŷ=1 | grupo_privilegiado) = 0. No se puede calcular DIR."
        )

    return p_min / p_priv


def statistical_parity_difference(
    y_pred: np.ndarray,
    group: np.ndarray,
    privileged_group: int = 1,
    positive_label: int = 1,
) -> float:
    """
    Calcula el Statistical Parity Difference (SPD).

    SPD = P(ŷ=1 | grupo_minoritario) - P(ŷ=1 | grupo_privilegiado)

    Un SPD = 0 indica paridad estadística perfecta.
    Un SPD < 0 indica desventaja para el grupo minoritario.

    Args:
        y_pred: Array de predicciones binarias
        group:  Array de etiquetas de grupo
        privileged_group: Valor que identifica al grupo privilegiado
        positive_label:   Valor de la etiqueta positiva

    Returns:
        SPD como float en [-1, 1].
    """
    mask_priv = group == privileged_group
    mask_min = group != privileged_group

    p_priv = np.mean(y_pred[mask_priv] == positive_label)
    p_min = np.mean(y_pred[mask_min] == positive_label)

    return float(p_min - p_priv)


def fairness_report(
    y_pred: np.ndarray,
    group: np.ndarray,
    config_name: str,
    privileged_group: int = 1,
    positive_label: int = 1,
) -> dict:
    """
    Genera un reporte completo de métricas de equidad para una configuración.

    Args:
        y_pred:      Predicciones del sistema
        group:       Etiquetas de grupo demográfico
        config_name: Nombre de la configuración (e.g., "C3")
        privileged_group: Grupo privilegiado
        positive_label:   Etiqueta positiva

    Returns:
        Dict con DIR, SPD, tasas de selección por grupo y veredicto legal.
    """
    dir_val = disparate_impact_ratio(y_pred, group, privileged_group, positive_label)
    spd_val = statistical_parity_difference(y_pred, group, privileged_group, positive_label)

    mask_priv = group == privileged_group
    mask_min = group != privileged_group

    return {
        "config": config_name,
        "DIR": round(dir_val, 4),
        "SPD": round(spd_val, 4),
        "selection_rate_privileged": round(float(np.mean(y_pred[mask_priv] == positive_label)), 4),
        "selection_rate_minority": round(float(np.mean(y_pred[mask_min] == positive_label)), 4),
        "n_privileged": int(mask_priv.sum()),
        "n_minority": int(mask_min.sum()),
        "passes_4_5_rule": dir_val >= 0.80,
    }
