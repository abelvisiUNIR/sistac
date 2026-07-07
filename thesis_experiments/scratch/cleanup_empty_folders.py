import shutil
from pathlib import Path

# Raíz del proyecto
base_dir = Path(r"c:\Users\abelvisi\Documents\Google_Drive\Mi unidad\Máster UNIR\IA Y Data\TFE\Entregas_TFE_Terminal\clo-author")

# Carpetas a limpiar que no deben estar en la estructura simplificada
target_folders = [
    "docs",
    "experiments",
    "explorations",
    "master_supporting_docs",
    "quality_reports",
    "src",
    "templates",
    "tests"
]

def clean_folder_recursive(folder_path: Path):
    if not folder_path.exists() or not folder_path.is_dir():
        return
    
    # Primero limpiar subcarpetas de forma recursiva
    for item in list(folder_path.iterdir()):
        if item.is_dir():
            clean_folder_recursive(item)
            
    # Eliminar archivos ignorados por git que impiden borrar el directorio (como desktop.ini)
    for item in list(folder_path.iterdir()):
        if item.is_file() and item.name.lower() in ("desktop.ini", ".ds_store"):
            try:
                item.unlink()
                print(f"Eliminado archivo de sistema: {item.relative_to(base_dir)}")
            except Exception as e:
                print(f"No se pudo eliminar {item.name}: {e}")
                
    # Si la carpeta quedó totalmente vacía, eliminarla
    if not any(folder_path.iterdir()):
        try:
            folder_path.rmdir()
            print(f"Eliminada carpeta vacía: {folder_path.relative_to(base_dir)}")
        except Exception as e:
            print(f"No se pudo eliminar la carpeta {folder_path.name}: {e}")

for folder_name in target_folders:
    folder_path = base_dir / folder_name
    if folder_path.exists():
        print(f"Procesando limpieza de: {folder_name}...")
        clean_folder_recursive(folder_path)

print("Proceso de limpieza completado.")
