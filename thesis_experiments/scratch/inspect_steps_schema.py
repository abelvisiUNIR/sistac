import sqlite3
from pathlib import Path

conv_dir = Path(r"C:\Users\abelvisi\.gemini\antigravity-ide\conversations")
db_file = conv_dir / "fbfde70d-1937-439e-ace1-4b46e8ad0329.db"

if db_file.exists():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(steps);")
    cols = cursor.fetchall()
    print("Columnas de 'steps':")
    for col in cols:
        print(f"  {col[1]} ({col[2]})")
    
    # Ver los primeros registros
    cursor.execute("SELECT * FROM steps LIMIT 2;")
    rows = cursor.fetchall()
    print("\nPrimeros 2 registros:")
    for row in rows:
        print(f"  {str(row)[:300]}...")
    conn.close()
else:
    print("El archivo fbfde70d-1937-439e-ace1-4b46e8ad0329.db no existe")
