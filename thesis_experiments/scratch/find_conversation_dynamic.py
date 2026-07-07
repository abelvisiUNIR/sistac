import json
import os
from pathlib import Path

brain_dir = Path(r"C:\Users\abelvisi\.gemini\antigravity-ide\brain")
keywords = ["real", "empresa", "vacantes", "públic", "cvs_external", "historial"]

print(f"Buscando en todos los subdirectorios de {brain_dir}...")

# Encontrar todos los transcript.jsonl recursivamente
transcripts = list(brain_dir.glob("**/transcript.jsonl"))
print(f"Encontrados {len(transcripts)} archivos transcript.jsonl.")

for tp in transcripts:
    # Obtener el UUID del path (es el nombre de la carpeta hija directa de brain)
    parts = tp.relative_to(brain_dir).parts
    conv_id = parts[0]
    
    # Omitir el actual si es posible, o incluirlo para buscar en todos
    print(f"\nBuscando en conversacion {conv_id} ({tp.name})...")
    matches = []
    
    try:
        with open(tp, mode="r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    step = json.loads(line)
                    content = step.get("content", "")
                    if not content:
                        content = ""
                    
                    tool_calls_str = ""
                    if "tool_calls" in step and step["tool_calls"]:
                        tool_calls_str = json.dumps(step["tool_calls"])
                        
                    full_text = (content + " " + tool_calls_str).lower()
                    
                    # Buscar ocurrencias
                    found = [kw for kw in keywords if kw.lower() in full_text]
                    if found:
                        matches.append((line_num, step.get("type", ""), step.get("source", ""), content, found))
                except Exception as e:
                    pass
                    
        if matches:
            print(f"  [!] Encontradas {len(matches)} coincidencias en {conv_id}:")
            # Filtrar e imprimir las de origen USER_INPUT
            user_inputs = [m for m in matches if m[1] == "USER_INPUT"]
            for m in user_inputs[:3]:
                print(f"    - L{m[0]} USER: {m[3].strip()[:200]}... (Coincidió: {m[4]})")
            
            # Si no hay USER_INPUT, mostrar las primeras del modelo
            if not user_inputs:
                for m in matches[:2]:
                    print(f"    - L{m[0]} {m[2]}: {m[3].strip()[:200]}... (Coincidió: {m[4]})")
    except Exception as e:
        print(f"  Error al leer {tp}: {e}")
