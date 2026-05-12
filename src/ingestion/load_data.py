"""
carga datos 
"""
import pandas as pd
def load_csv(path: str) -> pd.DataFrame:
    """
    Carga un archivo CSV y retorna un DataFrame
    """
    try:
        df = pd.read_csv(path)
        print(f"archivo cargaddo correctamete: {path}")
        print(f"file: {len(df)} | Columnas: {len(df.columns)}")
        return df
    except Exception as e:
        print(f"Error al correr archivos: {e}")
        return None

if __name__ == "__main__":
    # prueba simple (despues cambiamos el archivo)
    file_path = "../../data/raw/sample.csv"

    df = load_csv(file_path)

    if df is not None:
        print(df.head())

