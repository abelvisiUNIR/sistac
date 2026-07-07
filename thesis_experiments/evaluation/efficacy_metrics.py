"""
efficacy_metrics.py — Métricas de eficacia para H2

Calcula F1-score y AUC-ROC con intervalos de confianza bootstrap.
Compara predicciones del sistema contra el Gold Standard de expertos.

Autor: David I. Madrid Oyanadel
"""

import numpy as np
from sklearn.metrics import f1_score, roc_auc_score, classification_report


import sys
from pathlib import Path

# Agregar sistac/ al path (INV-16)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from sistac.config import H2_F1_THRESHOLD, H2_AUC_THRESHOLD

def compute_f1(y_true: np.ndarray, y_pred: np.ndarray, average: str = "macro") -> float:
    """
    Calcula F1-score.

    Args:
        y_true:  Etiquetas del Gold Standard
        y_pred:  Predicciones del sistema
        average: 'macro' (default), 'micro', 'weighted', o 'binary'

    Returns:
        F1-score como float.
    """
    return float(f1_score(y_true, y_pred, average=average))


def compute_auc_roc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Calcula AUC-ROC.

    Args:
        y_true:  Etiquetas binarias del Gold Standard
        y_score: Probabilidades o scores del sistema (no etiquetas binarias)

    Returns:
        AUC-ROC como float.
    """
    return float(roc_auc_score(y_true, y_score))


def bootstrap_ci_auc(
    y_true: np.ndarray,
    y_score: np.ndarray,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    random_seed: int = 42,
) -> tuple[float, float]:
    """
    Calcula intervalo de confianza bootstrap para AUC-ROC.

    Args:
        y_true:      Etiquetas del Gold Standard
        y_score:     Scores del sistema
        n_bootstrap: Número de iteraciones bootstrap (default: 1000)
        alpha:       Nivel de significancia (default: 0.05 → IC 95%)
        random_seed: Semilla de aleatoriedad (INV-14)

    Returns:
        Tupla (lower_bound, upper_bound) del IC (1-alpha)*100%.
    """
    rng = np.random.default_rng(random_seed)
    n = len(y_true)
    auc_scores = []

    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        try:
            auc = roc_auc_score(y_true[idx], y_score[idx])
            auc_scores.append(auc)
        except ValueError:
            # Muestra bootstrap sin ambas clases — ignorar
            continue

    lower = float(np.percentile(auc_scores, 100 * alpha / 2))
    upper = float(np.percentile(auc_scores, 100 * (1 - alpha / 2)))
    return lower, upper


def efficacy_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_score: np.ndarray,
    config_name: str,
    f1_threshold: float = H2_F1_THRESHOLD,
    auc_threshold: float = H2_AUC_THRESHOLD,
) -> dict:
    """
    Reporte completo de eficacia para una configuración.

    Args:
        y_true:        Etiquetas Gold Standard
        y_pred:        Predicciones binarias del sistema
        y_score:       Scores continuos del sistema
        config_name:   Nombre de la configuración
        f1_threshold:  Umbral de aceptación para F1 (default: H2_F1_THRESHOLD de config.py)
        auc_threshold: Umbral de aceptación para AUC-ROC (default: H2_AUC_THRESHOLD de config.py)

    Returns:
        Dict con F1, AUC-ROC, IC bootstrap, y veredicto H2.
    """
    f1 = compute_f1(y_true, y_pred)
    auc = compute_auc_roc(y_true, y_score)
    ci_lower, ci_upper = bootstrap_ci_auc(y_true, y_score)

    return {
        "config": config_name,
        "F1_macro": round(f1, 4),
        "AUC_ROC": round(auc, 4),
        "AUC_ROC_CI_lower": round(ci_lower, 4),
        "AUC_ROC_CI_upper": round(ci_upper, 4),
        "n_samples": len(y_true),
        "H2_accepted": f1 >= f1_threshold and auc >= auc_threshold,
    }
