import json
from pathlib import Path

brain_dir = Path(r"C:\Users\abelvisi\.gemini\antigravity-ide\brain")
uuid = "fbfde70d-1937-439e-ace1-4b46e8ad0329"
transcript_path = brain_dir / uuid / ".system_generated" / "logs" / "transcript.jsonl"

if not transcript_path.exists():
    print("El archivo no existe.")
    exit(1)

print(f"=== Conversación {uuid} ===")
with open(transcript_path, mode="r", encoding="utf-8", errors="replace") as f:
    for line in f:
        try:
            step = json.loads(line)
            step_type = step.get("type", "")
            source = step.get("source", "")
            content = step.get("content", "")
            
            # Solo mostrar USER_INPUT (entradas del usuario) y respuestas del PLANNER_RESPONSE (el asistente)
            if step_type in ("USER_INPUT", "PLANNER_RESPONSE"):
                print(f"\n--- [{source}] ---")
                # Mostrar el texto completo
                print(content.strip()[:1000]) # Primeros 1000 caracteres
                if len(content) > 1000:
                    print("... [TRUNCADO]")
        except Exception as e:
            pass
