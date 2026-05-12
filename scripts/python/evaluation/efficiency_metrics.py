"""
efficiency_metrics.py — Métricas de eficiencia para H1

Mide tiempo de procesamiento por candidato (T_cand) para cada configuración.
Contrasta C1-C3 contra baseline manual C0.

Autores: David I. Madrid Oyanadel + Mario A. Belvisi Lescano
"""

import time
import numpy as np
from scipy import stats
from typing import Callable


def measure_processing_time(
    func: Callable,
    inputs: list,
    n_warmup: int = 2,
) -> np.ndarray:
    """
    Mide el tiempo de procesamiento de una función sobre una lista de inputs.

    Args:
        func:     Función a medir (e.g., pipeline.process_cv)
        inputs:   Lista de inputs (e.g., lista de CVs)
        n_warmup: Número de ejecuciones de calentamiento (no incluidas en medición)

    Returns:
        Array de tiempos en segundos (uno por input).
    """
    # Calentamiento para estabilizar caché y conexiones
    for inp in inputs[:n_warmup]:
        func(inp)

    times = []
    for inp in inputs:
        start = time.perf_counter()
        func(inp)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return np.array(times)


def efficiency_report(
    times_baseline: np.ndarray,
    times_system: np.ndarray,
    config_name: str,
    alpha: float = 0.05,
) -> dict:
    """
    Reporte de eficiencia: compara T_cand del sistema vs baseline manual.

    Usa Mann-Whitney U (no paramétrico, apropiado para tiempos sesgados).

    Args:
        times_baseline: Array de tiempos de C0 (screening manual)
        times_system:   Array de tiempos de la configuración evaluada
        config_name:    Nombre de la configuración (e.g., "C1")
        alpha:          Nivel de significancia (default: 0.05)

    Returns:
        Dict con medianas, IQR, estadístico U, p-valor, y veredicto H1.
    """
    median_baseline = float(np.median(times_baseline))
    median_system = float(np.median(times_system))

    iqr_baseline = float(np.percentile(times_baseline, 75) - np.percentile(times_baseline, 25))
    iqr_system = float(np.percentile(times_system, 75) - np.percentile(times_system, 25))

    stat, p_value = stats.mannwhitneyu(
        times_system, times_baseline, alternative="less"
    )

    speedup = median_baseline / median_system if median_system > 0 else float("inf")

    return {
        "config": config_name,
        "median_baseline_s": round(median_baseline, 3),
        "median_system_s": round(median_system, 3),
        "IQR_baseline_s": round(iqr_baseline, 3),
        "IQR_system_s": round(iqr_system, 3),
        "speedup_factor": round(speedup, 2),
        "mannwhitney_U": float(stat),
        "p_value": round(float(p_value), 4),
        "H1_accepted": p_value < alpha and median_system < median_baseline,
    }
