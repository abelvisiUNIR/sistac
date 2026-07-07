import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

def calculate_confusion_matrix(cache_file_path):
    if not cache_file_path.exists():
        print(f"No se encontró el archivo: {cache_file_path.name}")
        return
    
    with open(cache_file_path, "r", encoding="utf-8") as f:
        cache = json.load(f)
        
    print(f"\n--- Matrices de Confusión para {cache_file_path.name} ---")
    
    # Agrupar por configuración (c1, c2, c3)
    configs = ["c1", "c2", "c3"]
    for cfg in configs:
        tp, fp, tn, fn = 0, 0, 0, 0
        total = 0
        missing_labels = 0
        
        for key, res in cache.items():
            if not key.startswith(cfg + "_"):
                continue
            
            # Obtener etiquetas
            expected = res.get("expected_label")
            predicted = res.get("decision")
            
            if not expected or not predicted:
                missing_labels += 1
                continue
            
            total += 1
            if expected == "APTO" and predicted == "APTO":
                tp += 1
            elif expected == "NO_APTO" and predicted == "APTO":
                fp += 1
            elif expected == "NO_APTO" and predicted == "NO_APTO":
                tn += 1
            elif expected == "APTO" and predicted == "NO_APTO":
                fn += 1
        
        if total == 0:
            print(f"\nConfiguración {cfg.upper()}: Sin datos evaluados.")
            continue
            
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1_score = 2 * precision * sensitivity / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
        
        print(f"\nConfiguración {cfg.upper()} (Total: {total} pares):")
        print(f"  Matriz:")
        print(f"                   Real APTO    Real NO_APTO")
        print(f"    Pred. APTO      {tp:^9}    {fp:^12}")
        print(f"    Pred. NO_APTO   {fn:^9}    {tn:^12}")
        print(f"  Métricas detalladas:")
        print(f"    - Verdaderos Positivos (VP): {tp}")
        print(f"    - Falsos Positivos (FP):     {fp} (Falsas Alarmas)")
        print(f"    - Verdaderos Negativos (VN): {tn}")
        print(f"    - Falsos Negativos (FN):     {fn}")
        print(f"    - Sensibilidad (Recall):      {sensitivity:.1%}")
        print(f"    - Especificidad:              {specificity:.1%}")
        print(f"    - Precisión:                  {precision:.1%}")
        print(f"    - F1-Score (Apto):            {f1_score:.3f}")

if __name__ == "__main__":
    calculate_confusion_matrix(PROJECT_ROOT / "data" / "eval_cache_anthropic.json")
    calculate_confusion_matrix(PROJECT_ROOT / "data" / "eval_cache_google.json")
