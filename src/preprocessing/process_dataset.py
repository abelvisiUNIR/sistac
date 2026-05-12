import pandas as pd
from clean_text import clean_text

def process_dataset(input_path: str, output_path: str) -> None:
    """
    Carga un csv, limpia columnas de texto y guarda un nuevo csv procesado.
    """
    df = pd.read_csv(input_path)
    
    text_columns = ["nombre", "experiencia", "habilidades"]

    for column in text_columns:
        if column in df.columns:
            df[column + "_limpio"] = df[column].apply(clean_text)

    df["texto_completo_normalizado"] = (
        "Candidato: " + df["nombre_limpio"] +
        ". Experiencia: " + df["experiencia_limpio"] +
        ". Habilidades: " + df["habilidades_limpio"] + "."
    )




    df.to_csv(output_path, index=False, encoding = "utf-8-sig")
    

    print("Dataset procesado correctamente")
    print(f"Archivo origen: {input_path}")
    print(f"Archivo salida: {output_path}")

    print(df.head())

if __name__ == "__main__":
    input_file = "data/raw/sample.csv"
    output_path = "data/processed/sample_clean.csv"


    process_dataset(input_file, output_path)
        

