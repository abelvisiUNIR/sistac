import csv
from pathlib import Path

# Paths
base_dir = Path(r"c:\Users\abelvisi\Documents\Google_Drive\Mi unidad\Máster UNIR\IA Y Data\TFE\Entregas_TFE_Terminal\clo-author")
gt_path = base_dir / "data" / "raw" / "gold_standard" / "ground_truth.csv"

if not gt_path.exists():
    print(f"File not found: {gt_path}")
    exit(1)

# Read current rows
with open(gt_path, mode="r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames) if reader.fieldnames else []
    rows = list(reader)

# Check if 'eval_source' is already in fieldnames
if "eval_source" not in fieldnames:
    fieldnames.append("eval_source")

# Update rows
updated_count = 0
for row in rows:
    if not row.get("eval_source"):
        cv_id = row.get("cv_id", "")
        try:
            num = int(cv_id.split("_")[1])
            if num <= 300:
                row["eval_source"] = "sintetico_original"
            else:
                row["eval_source"] = "aplicacion_interactiva"
        except (IndexError, ValueError):
            row["eval_source"] = "sintetico_original"
        updated_count += 1

# Write back
with open(gt_path, mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Updated {updated_count} rows in ground_truth.csv with 'eval_source'.")
