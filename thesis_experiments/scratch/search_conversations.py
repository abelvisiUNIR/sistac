import sqlite3
from pathlib import Path

conv_dir = Path(r"C:\Users\abelvisi\.gemini\antigravity-ide\conversations")

db_files = list(conv_dir.glob("*.db"))

print(f"Encontrados {len(db_files)} archivos de base de datos de conversaciones:")

keywords = ["real", "empresa", "extern", "cvs_external"]

for db_file in db_files:
    print(f"\nBuscando en {db_file.name}...")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Obtener nombres de las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Tablas: {tables}")
        
        # Buscar en las tablas posibles
        for table in tables:
            # Intentar obtener las columnas de la tabla para ver si contiene texto de mensaje
            cursor.execute(f"PRAGMA table_info({table});")
            cols = [col[1] for col in cursor.fetchall()]
            
            # Buscar columnas candidatas para texto (ej: content, text, body, value, etc.)
            text_cols = [c for c in cols if any(k in c.lower() for k in ["content", "text", "body", "value", "prompt", "response", "message"])]
            
            if text_cols:
                for col in text_cols:
                    for kw in keywords:
                        try:
                            # Hacer una búsqueda de texto parcial (case-insensitive usando LOWER o LIKE)
                            query = f"SELECT ROWID, {col} FROM {table} WHERE {col} LIKE ?"
                            cursor.execute(query, (f"%{kw}%",))
                            results = cursor.fetchall()
                            if results:
                                print(f"    [!] Coincidencia en tabla '{table}', columna '{col}' para '{kw}':")
                                for rowid, val in results[:5]: # Mostrar las primeras 5 coincidencias
                                    val_str = str(val)[:150].replace('\n', ' ')
                                    print(f"      - ROWID {rowid}: {val_str}...")
                        except Exception as e:
                            # Ignorar errores de columnas
                            pass
        conn.close()
    except Exception as e:
        print(f"  Error abriendo {db_file.name}: {e}")
