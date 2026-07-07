import json
from pathlib import Path

# Paths
brain_dir = Path(r"C:\Users\abelvisi\.gemini\antigravity-ide\brain")
uuid = "fbfde70d-1937-439e-ace1-4b46e8ad0329"
transcript_path = brain_dir / uuid / ".system_generated" / "logs" / "transcript.jsonl"

base_dir = Path(r"c:\Users\abelvisi\Documents\Google_Drive\Mi unidad\Máster UNIR\IA Y Data\TFE\Entregas_TFE_Terminal\clo-author")
output_md = base_dir / "paper" / "sections" / "conversacion_preprocesamiento_datos_reales.md"

if not transcript_path.exists():
    print(f"No se encontró el archivo de log: {transcript_path}")
    exit(1)

print("Leyendo y formateando la conversación...")

md_content = [
    f"# Conversación Recuperada: Preprocesamiento y Datos Reales",
    f"",
    f"Esta es la conversación recuperada del historial técnico (ID: `{uuid}`), donde se discute la estrategia de incorporar datos reales de vacantes y postulantes (CVs), traducción, tratamiento de datos y simulación de la validación experimental.",
    f"",
    f"---",
    f""
]

with open(transcript_path, mode="r", encoding="utf-8", errors="replace") as f:
    for line in f:
        try:
            step = json.loads(line)
            step_type = step.get("type", "")
            source = step.get("source", "")
            content = step.get("content", "")
            
            if not content:
                continue
                
            if step_type == "USER_INPUT":
                # Limpiar metadatos adicionales del prompt si existen
                clean_content = content
                if "<USER_REQUEST>" in clean_content:
                    clean_content = clean_content.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0]
                
                md_content.append(f"## 👤 Usuario (Pregunta/Requerimiento)")
                md_content.append(f"")
                md_content.append(clean_content.strip())
                md_content.append(f"")
                md_content.append(f"---")
                md_content.append(f"")
                
            elif step_type == "PLANNER_RESPONSE":
                md_content.append(f"### 🤖 Asistente (Respuesta/Propuesta)")
                md_content.append(f"")
                md_content.append(content.strip())
                md_content.append(f"")
                md_content.append(f"---")
                md_content.append(f"")
                
        except Exception as e:
            pass

# Guardar a archivo md
output_md.parent.mkdir(parents=True, exist_ok=True)
output_md.write_text("\n".join(md_content), encoding="utf-8-sig")

print(f"Éxito: Conversación exportada a {output_md}")
