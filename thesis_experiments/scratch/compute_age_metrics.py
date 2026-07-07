import json
from pathlib import Path
import numpy as np

# Load cache
cache_path = Path("data/eval_cache_anthropic.json")
with open(cache_path, "r", encoding="utf-8") as f:
    cache = json.load(f)

# Group results by configuration
c2_results = []
c3_results = []

for key, val in cache.items():
    if key.startswith("c2_"):
        c2_results.append(val)
    elif key.startswith("c3_"):
        c3_results.append(val)

def print_age_metrics(results, config_name):
    print(f"\n--- Age Metrics for {config_name} ---")
    y_pred = np.array([1 if r["decision"] == "APTO" else 0 for r in results])
    group_age = np.array([r.get("group_age", "desconocido") for r in results])
    
    # Privileged group: "23-35"
    priv_mask = (group_age == "23-35")
    n_priv = np.sum(priv_mask)
    n_priv_sel = np.sum(y_pred[priv_mask])
    rate_priv = n_priv_sel / n_priv if n_priv > 0 else 0.0
    print(f"Privileged (23-35): rate = {rate_priv:.4f} ({n_priv_sel}/{n_priv})")
    
    for age_grp in ["23-35", "36-45", "46-58"]:
        mask = (group_age == age_grp)
        n_grp = np.sum(mask)
        if n_grp == 0:
            continue
        n_grp_sel = np.sum(y_pred[mask])
        rate_grp = n_grp_sel / n_grp
        
        dir_val = rate_grp / rate_priv if rate_priv > 0 else 0.0
        spd_val = rate_grp - rate_priv
        print(f"Group {age_grp}: rate = {rate_grp:.4f} ({n_grp_sel}/{n_grp}) | DIR = {dir_val:.4f} | SPD = {spd_val:.4f}")

print_age_metrics(c2_results, "C2 (LLM + RAG)")
print_age_metrics(c3_results, "C3 (LLM + RAG + PII)")
