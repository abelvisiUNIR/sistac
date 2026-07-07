"""
Análisis estadístico complementario para las mejoras del TFE SISTAC (Track 3).

Recalcula, SIN volver a llamar a los modelos, a partir de los caches de
evaluación ya existentes:

  1. Umbral de decisión óptimo (Youden y F1-óptimo) y F1 macro resultante,
     para sustentar la discusión de la hipótesis de eficacia (el problema es
     el punto de corte, no la capacidad discriminativa del modelo).
  2. Curva F1 vs. umbral, exportada como CSV para graficar.
  3. DIR y SPD por género y por edad con intervalos de confianza por bootstrap
     y test exacto de Fisher sobre las tasas de selección (hipótesis de equidad).
  4. Recuentos por subgrupo (n por género y por rango de edad).

Entradas (no se modifican):
  data/eval_cache_anthropic.json   -> Claude Sonnet 4.5 (resultado principal)
  data/eval_cache_google.json      -> Gemini 2.5 Flash (réplica de robustez)

Salidas (CSV) en: paper/tables/mejoras/
  tab_umbral_optimo.csv
  tab_curva_f1_umbral.csv
  tab_equidad_genero_ic.csv
  tab_equidad_edad_ic.csv
  tab_recuentos_subgrupos.csv

Uso:
  python sistac/evaluation/analisis_mejoras_estadisticas.py

Notas:
  - Algunas evaluaciones de Gemini quedaron con "score": null (fallos de
    parseo del modelo). Se excluyen del análisis de umbral (que requiere el
    score numérico) y se informa cuántas se omiten. Para la equidad se usa el
    campo "decision" efectivamente registrado por el modelo.
  - Cumple INV-14 (semilla fijada una vez), INV-15 (imports al inicio),
    INV-16 (rutas relativas con pathlib).
  - Umbral de decisión base del experimento: 70 puntos.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from sklearn.metrics import f1_score, roc_curve

# --- Reproducibilidad (INV-14) -------------------------------------------------
SEED = 42
np.random.seed(SEED)

# --- Configuración -------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "paper" / "tables" / "mejoras"

CACHES = {
    "claude": DATA_DIR / "eval_cache_anthropic.json",
    "gemini": DATA_DIR / "eval_cache_google.json",
}

BASE_THRESHOLD = 70          # umbral del experimento
N_BOOTSTRAP = 1000           # remuestreos para IC
POSITIVE_LABEL = "APTO"
PROTECTED_GENDER = "F"       # grupo protegido (femenino)
REFERENCE_GENDER = "M"       # grupo de referencia (masculino)
AGE_REFERENCE = "23-35"      # grupo de referencia de edad
N_GRID = np.arange(0, 101)   # rejilla de umbrales para la curva F1


# --- Utilidades ----------------------------------------------------------------
def _to_float(v):
    """Convierte a float; devuelve NaN si es None, vacío o no parseable."""
    if v is None:
        return np.nan
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def _label_to_bin(v):
    """APTO -> 1, NO_APTO -> 0, cualquier otra cosa -> NaN."""
    s = str(v).strip().upper() if v is not None else ""
    if s == POSITIVE_LABEL:
        return 1
    if s in ("NO_APTO", "NO APTO", "NOAPTO"):
        return 0
    return np.nan


# --- Carga ---------------------------------------------------------------------
def load_cache(path: Path) -> pd.DataFrame:
    """Aplana un cache de evaluación a un DataFrame de filas por evaluación."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    rows = []
    for entry in raw.values():
        if not isinstance(entry, dict):
            continue
        rows.append(
            {
                "config": str(entry.get("config", "")).lower(),
                "cv_id": entry.get("cv_id"),
                "jd_id": entry.get("jd_id"),
                "score": _to_float(entry.get("score")),
                "y_pred": _label_to_bin(entry.get("decision")),
                "y_true": _label_to_bin(entry.get("expected_label")),
                "gender": str(entry.get("group_gender", "")).strip().upper(),
                "age": str(entry.get("group_age", "")).strip(),
            }
        )
    return pd.DataFrame(rows)


# --- Umbral óptimo -------------------------------------------------------------
def optimal_thresholds(df_cfg: pd.DataFrame) -> dict:
    """Umbral de Youden y umbral que maximiza F1 macro, con sus F1.

    Usa solo filas con score y etiqueta verdadera válidos.
    """
    valid = df_cfg.dropna(subset=["score", "y_true"])
    n_valid = len(valid)
    n_drop = len(df_cfg) - n_valid
    if n_valid == 0 or valid["y_true"].nunique() < 2:
        return {"n_valid": n_valid, "n_descartadas": n_drop,
                "f1_base_thr70": np.nan, "thr_youden": np.nan,
                "f1_youden": np.nan, "thr_f1opt": np.nan, "f1_opt": np.nan,
                "f1_curve": []}

    y_true = valid["y_true"].to_numpy().astype(int)
    score = valid["score"].to_numpy()

    # Youden J sobre la curva ROC
    fpr, tpr, thr = roc_curve(y_true, score)
    thr_youden = float(thr[int(np.argmax(tpr - fpr))])

    # Barrido de umbrales para F1 macro
    best_f1, best_thr, f1_curve = -1.0, BASE_THRESHOLD, []
    for t in N_GRID:
        y_pred = (score >= t).astype(int)
        f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        f1_curve.append((int(t), round(f1, 4)))
        if f1 > best_f1:
            best_f1, best_thr = f1, int(t)

    f1_base = f1_score(y_true, (score >= BASE_THRESHOLD).astype(int),
                       average="macro", zero_division=0)
    f1_youden = f1_score(y_true, (score >= thr_youden).astype(int),
                         average="macro", zero_division=0)
    return {
        "n_valid": n_valid,
        "n_descartadas": n_drop,
        "f1_base_thr70": round(f1_base, 4),
        "thr_youden": round(thr_youden, 2),
        "f1_youden": round(f1_youden, 4),
        "thr_f1opt": best_thr,
        "f1_opt": round(best_f1, 4),
        "f1_curve": f1_curve,
    }


# --- Equidad -------------------------------------------------------------------
def _rate(dec: np.ndarray) -> float:
    return float(np.mean(dec)) if len(dec) else np.nan


def dir_spd(protected: np.ndarray, reference: np.ndarray):
    r_p, r_r = _rate(protected), _rate(reference)
    dir_ = (r_p / r_r) if (r_r and r_r > 0) else np.nan
    return dir_, r_p - r_r, r_p, r_r


def bootstrap_ci(protected, reference, n=N_BOOTSTRAP):
    """IC al 95% (percentil) de DIR y SPD por bootstrap sobre cada subgrupo."""
    p, r = np.asarray(protected, float), np.asarray(reference, float)
    if len(p) == 0 or len(r) == 0:
        return (np.nan, np.nan), (np.nan, np.nan)
    dirs, spds = [], []
    for _ in range(n):
        d, s, _, _ = dir_spd(np.random.choice(p, len(p), replace=True),
                             np.random.choice(r, len(r), replace=True))
        dirs.append(d)
        spds.append(s)
    return ((np.nanpercentile(dirs, 2.5), np.nanpercentile(dirs, 97.5)),
            (np.nanpercentile(spds, 2.5), np.nanpercentile(spds, 97.5)))


def fisher_p(protected, reference) -> float:
    """Test exacto de Fisher sobre la tabla 2x2 grupo x decisión (APTO/NO)."""
    p, r = np.asarray(protected, int), np.asarray(reference, int)
    if len(p) == 0 or len(r) == 0:
        return np.nan
    table = [[int(p.sum()), int((1 - p).sum())],
             [int(r.sum()), int((1 - r).sum())]]
    try:
        return float(fisher_exact(table)[1])
    except ValueError:
        return np.nan


def _round(x, d=4):
    return round(x, d) if isinstance(x, (int, float)) and x == x else np.nan


def gender_equity(df_cfg: pd.DataFrame) -> dict:
    valid = df_cfg.dropna(subset=["y_pred"])
    prot = valid.loc[valid["gender"] == PROTECTED_GENDER, "y_pred"].to_numpy()
    ref = valid.loc[valid["gender"] == REFERENCE_GENDER, "y_pred"].to_numpy()
    dir_, spd, r_p, r_r = dir_spd(prot, ref)
    (dlo, dhi), (slo, shi) = bootstrap_ci(prot, ref)
    return {
        "n_protegido": len(prot), "n_referencia": len(ref),
        "tasa_protegido": _round(r_p), "tasa_referencia": _round(r_r),
        "DIR": _round(dir_), "DIR_IC95_inf": _round(dlo), "DIR_IC95_sup": _round(dhi),
        "SPD": _round(spd), "SPD_IC95_inf": _round(slo), "SPD_IC95_sup": _round(shi),
        "fisher_p": _round(fisher_p(prot, ref)),
    }


def age_equity(df_cfg: pd.DataFrame) -> list:
    valid = df_cfg.dropna(subset=["y_pred"])
    ref = valid.loc[valid["age"] == AGE_REFERENCE, "y_pred"].to_numpy()
    out = []
    for grupo in sorted(g for g in valid["age"].unique() if g and g != AGE_REFERENCE):
        prot = valid.loc[valid["age"] == grupo, "y_pred"].to_numpy()
        dir_, spd, _, _ = dir_spd(prot, ref)
        (dlo, dhi), _ = bootstrap_ci(prot, ref)
        out.append({
            "grupo_edad": grupo, "n_grupo": len(prot), "n_referencia": len(ref),
            "DIR": _round(dir_), "DIR_IC95_inf": _round(dlo), "DIR_IC95_sup": _round(dhi),
            "SPD": _round(spd), "fisher_p": _round(fisher_p(prot, ref)),
        })
    return out


# --- Orquestación --------------------------------------------------------------
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    umbral_rows, curva_rows, gen_rows, edad_rows, conteo_rows = [], [], [], [], []

    for modelo, path in CACHES.items():
        if not path.exists():
            print(f"[AVISO] No se encontró {path}; se omite {modelo}.")
            continue
        df = load_cache(path)
        n_null = int(df["score"].isna().sum())
        print(f"[{modelo}] {len(df)} evaluaciones cargadas; "
              f"{n_null} con score nulo (excluidas del análisis de umbral).")

        for cfg in sorted(df["config"].unique()):
            d = df[df["config"] == cfg]
            if d.empty:
                continue

            thr = optimal_thresholds(d)
            umbral_rows.append({
                "modelo": modelo, "config": cfg,
                "n_valido": thr["n_valid"], "n_descartadas": thr["n_descartadas"],
                "f1_base_thr70": thr["f1_base_thr70"],
                "thr_youden": thr["thr_youden"], "f1_youden": thr["f1_youden"],
                "thr_f1opt": thr["thr_f1opt"], "f1_opt": thr["f1_opt"],
            })
            for t, f1 in thr["f1_curve"]:
                curva_rows.append({"modelo": modelo, "config": cfg,
                                   "umbral": t, "f1_macro": f1})

            g = gender_equity(d)
            g.update({"modelo": modelo, "config": cfg})
            gen_rows.append(g)

            for fila in age_equity(d):
                fila.update({"modelo": modelo, "config": cfg})
                edad_rows.append(fila)

            conteo_rows.append({
                "modelo": modelo, "config": cfg, "n_total": len(d),
                "n_score_nulo": int(d["score"].isna().sum()),
                "n_femenino": int((d["gender"] == PROTECTED_GENDER).sum()),
                "n_masculino": int((d["gender"] == REFERENCE_GENDER).sum()),
                **{f"n_edad_{k}": int((d["age"] == k).sum())
                   for k in sorted(x for x in d["age"].unique() if x)},
            })

    pd.DataFrame(umbral_rows).to_csv(OUT_DIR / "tab_umbral_optimo.csv", index=False)
    pd.DataFrame(curva_rows).to_csv(OUT_DIR / "tab_curva_f1_umbral.csv", index=False)
    pd.DataFrame(gen_rows).to_csv(OUT_DIR / "tab_equidad_genero_ic.csv", index=False)
    pd.DataFrame(edad_rows).to_csv(OUT_DIR / "tab_equidad_edad_ic.csv", index=False)
    pd.DataFrame(conteo_rows).to_csv(OUT_DIR / "tab_recuentos_subgrupos.csv", index=False)

    print("\nListo. CSVs escritos en:", OUT_DIR)
    print("Revisar tab_umbral_optimo.csv: si f1_opt >> f1_base_thr70, se confirma")
    print("que la eficacia está limitada por el punto de corte y no por el modelo.")


if __name__ == "__main__":
    main()
