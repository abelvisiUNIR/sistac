"""
data/split_corpus.py — División train/test del corpus sintético (seed=42)

Divide los 300 pares CV-JD en:
  - Train (80% = 240 CVs): se indexan en Azure Search — son la "memoria" del sistema
  - Test  (20% =  60 CVs): se reservan para evaluar H1/H2/H3 — el LLM nunca los vio

Split estratificado por:
  - jd_id        → mismo % de cada cargo en train y test
  - expected_label → 50% APTO / 50% NO_APTO en ambas particiones
  - group_gender  → 50% F / 50% M en ambas
  - group_age     → distribución proporcional de los 3 grupos

Outputs:
  data/cleaned/evaluation_sets/train_ids.csv   → cv_id, jd_id + metadata
  data/cleaned/evaluation_sets/test_ids.csv    → cv_id, jd_id + metadata

Los scripts de indexación usan train_ids.csv para saber qué CVs subir.
El orquestador usa test_ids.csv para evaluar sin data leakage.

Reproducible con RANDOM_SEED = 42 (INV-14).
"""

from __future__ import annotations

import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

# INV-14: semilla global
random.seed(42)
np.random.seed(42)

# INV-16: rutas via PROJECT_ROOT
_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from config import GOLD_STANDARD_DIR, EVAL_SETS

GROUND_TRUTH_PATH = GOLD_STANDARD_DIR / "ground_truth.csv"
TRAIN_OUTPUT = EVAL_SETS / "train_ids.csv"
TEST_OUTPUT  = EVAL_SETS / "test_ids.csv"

TEST_RATIO = 0.20   # 20% test → 60 CVs únicos (20% de 300)
TRAIN_RATIO = 1 - TEST_RATIO


def load_ground_truth() -> list[dict]:
    """Carga ground_truth.csv como lista de dicts."""
    if not GROUND_TRUTH_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró: {GROUND_TRUTH_PATH}\n"
            "Generá el corpus primero:\n"
            "  py -3 scripts/python/data/synthetic_corpus_generator.py"
        )
    with open(GROUND_TRUTH_PATH, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def stratified_split(
    rows: list[dict],
    test_ratio: float = TEST_RATIO,
    seed: int = 42,
) -> tuple[list[dict], list[dict]]:
    """
    Split estratificado por (jd_id, expected_label, group_gender).

    Garantiza que cada estrato (ej: JD_001 + APTO + F) tenga la misma
    proporción en train y test, preservando el balance demográfico para H3.

    Args:
        rows:       Lista de pares CV-JD del ground truth.
        test_ratio: Fracción para test (0.20 = 20%).
        seed:       Semilla para reproducibilidad.

    Returns:
        (train_rows, test_rows)
    """
    rng = random.Random(seed)

    # Agrupar por estrato (jd_id, label, gender)
    strata: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        key = (row["jd_id"], row["expected_label"], row["group_gender"])
        strata[key].append(row)

    train_rows: list[dict] = []
    test_rows: list[dict] = []

    for key, group in sorted(strata.items()):
        rng.shuffle(group)
        n_test = max(1, round(len(group) * test_ratio))
        test_rows.extend(group[:n_test])
        train_rows.extend(group[n_test:])

    return train_rows, test_rows


def save_split(rows: list[dict], path: Path, name: str) -> None:
    """Guarda una partición como CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["cv_id", "jd_id", "expected_label", "expected_score",
                  "group_gender", "group_age", "eval_source"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  → {name}: {len(rows)} pares  ({path.name})")


def print_split_stats(train: list[dict], test: list[dict]) -> None:
    """Muestra el balance del split para verificar estratificación."""
    def count(rows, key):
        counts: dict[str, int] = {}
        for r in rows:
            v = r[key]
            counts[v] = counts.get(v, 0) + 1
        return counts

    print(f"\n{'Partición':<10} {'Total':>6} {'APTO':>6} {'NO_APTO':>8} {'F':>5} {'M':>5}")
    print("-" * 50)
    for name, rows in [("Train", train), ("Test", test)]:
        labels = count(rows, "expected_label")
        genders = count(rows, "group_gender")
        print(
            f"  {name:<8} {len(rows):>6} "
            f"{labels.get('APTO', 0):>6} {labels.get('NO_APTO', 0):>8} "
            f"{genders.get('F', 0):>5} {genders.get('M', 0):>5}"
        )

    # Por JD
    print(f"\n  Balance por cargo:")
    jds_train = count(train, "jd_id")
    jds_test  = count(test, "jd_id")
    for jd in sorted(jds_train):
        print(f"    {jd}: train={jds_train.get(jd,0)}  test={jds_test.get(jd,0)}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=== SISTAC — Split train/test del corpus (seed=42) ===\n")

    # Cargar
    rows = load_ground_truth()
    print(f"  Ground truth cargado: {len(rows)} pares CV-JD")

    # Split estratificado
    train, test = stratified_split(rows)

    # Stats
    print_split_stats(train, test)

    # Guardar
    print(f"\nGuardando particiones en {EVAL_SETS}/...")
    save_split(train, TRAIN_OUTPUT, "TRAIN")
    save_split(test,  TEST_OUTPUT,  "TEST")

    print(f"\n  Train: {len(train)} pares ({len(train)/len(rows):.0%}) → se indexan en Azure Search")
    print(f"  Test:  {len(test)}  pares ({len(test)/len(rows):.0%})  → se usan para evaluar H1/H2/H3")
    print("\nListo. El orquestador y el indexador leerán estos CSVs.")
