import docx
from pathlib import Path

tables_dir = Path("paper/tables")

for doc_path in sorted(tables_dir.glob("tab_resultados_h*.docx")):
    print(f"\n=== Table: {doc_path.name} ===")
    doc = docx.Document(doc_path)
    for table in doc.tables:
        for row in table.rows:
            text = [cell.text.strip() for cell in row.cells]
            print(" | ".join(text))
