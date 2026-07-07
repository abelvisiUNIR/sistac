import os
from pathlib import Path

# Raíz del proyecto
base_dir = Path(r"c:\Users\abelvisi\Documents\Google_Drive\Mi unidad\Máster UNIR\IA Y Data\TFE\Entregas_TFE_Terminal\clo-author")

def clean_empty_folders(root_dir: Path):
    deleted_count = 0
    # Recorremos bottom-up (de abajo hacia arriba) para que si al vaciar una subcarpeta 
    # la carpeta padre queda vacía, también se elimine en la misma pasada.
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        current_path = Path(dirpath)
        
        # Evitar tocar directorios de control como .git
        if ".git" in current_path.parts:
            continue
            
        # Eliminar archivos invisibles de sistema de Windows/Mac si existen en esta carpeta
        # para que la carpeta pueda ser detectada como vacía
        for filename in filenames:
            if filename.lower() in ("desktop.ini", ".ds_store"):
                file_path = current_path / filename
                try:
                    file_path.unlink()
                    print(f"Eliminado archivo de sistema: {file_path.relative_to(root_dir)}")
                except Exception as e:
                    print(f"No se pudo eliminar {file_path.name}: {e}")
                    
        # Volver a verificar el contenido después de limpiar archivos de sistema
        try:
            items = list(current_path.iterdir())
        except Exception:
            continue
            
        if not items:
            # Si no queda ningún archivo ni subcarpeta, eliminamos la carpeta
            try:
                current_path.rmdir()
                deleted_count += 1
                print(f"Eliminada carpeta vacía: {current_path.relative_to(root_dir)}")
            except Exception as e:
                print(f"No se pudo eliminar la carpeta vacía {current_path.relative_to(root_dir)}: {e}")
                
    return deleted_count

if __name__ == "__main__":
    print(f"Buscando y eliminando carpetas vacías en: {base_dir}")
    print("-" * 60)
    count = clean_empty_folders(base_dir)
    print("-" * 60)
    print(f"Proceso finalizado. Total de carpetas eliminadas: {count}")
