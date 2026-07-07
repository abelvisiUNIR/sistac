import json
from pathlib import Path

brain_dir = Path(r"C:\Users\abelvisi\.gemini\antigravity-ide\brain")
uuids = [
    "0ed2b58f-f7a8-4c63-bb85-4529ff706ff2",
    "48f1b58a-c6b8-424a-8fd8-d809e776fc7b",
    "5aaea146-cb4a-42b6-8641-4f4ba3fdc243",
    "bd90abaf-3a64-4d58-9349-2c57d7b7ea6d",
    "d2d7a09b-aed2-4145-aee4-a47d29c56c90",
    "fbfde70d-1937-439e-ace1-4b46e8ad0329"
]

keywords = ["real", "empresa", "extern", "cvs_external"]

print("Buscando en los archivos transcript.jsonl de las conversaciones...")

for uuid in uuids:
    transcript_path = brain_dir / uuid / ".system_generated" / "logs" / "transcript.jsonl"
    if not transcript_path.exists():
        # Intentar en otra estructura de directorios si existe
        continue
        
    print(f"\nAnalizando conversación: {uuid}...")
    matches_found = 0
    
    try:
        with open(transcript_path, mode="r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    step = json.loads(line)
                    # El texto puede estar en 'content' (mensajes del usuario o respuestas)
                    content = step.get("content", "")
                    if not content:
                        content = ""
                    
                    # También buscar en tool_calls si aplica
                    tool_calls_str = ""
                    if "tool_calls" in step and step["tool_calls"]:
                        tool_calls_str = json.dumps(step["tool_calls"])
                    
                    full_text = (content + " " + tool_calls_str).lower()
                    
                    # Verificar si contiene alguna de las palabras clave
                    found_kws = [kw for kw in keywords if kw.lower() in full_text]
                    if found_kws:
                        # Extraer un fragmento descriptivo
                        # Si es de USER_INPUT, es de especial interés
                        step_type = step.get("type", "")
                        source = step.get("source", "")
                        
                        snippet = content[:200].replace('\n', ' ')
                        print(f"  - Línea {line_num} | Tipo: {step_type} | Origen: {source} | Coincidió: {found_kws}")
                        print(f"    Texto: {snippet}...")
                        matches_found += 1
                        
                        if matches_found >= 5:
                            print("  (Truncando más coincidencias en esta conversación)")
                            break
                except Exception as e:
                    pass
    except Exception as e:
        print(f"  Error leyendo {uuid}: {e}")
