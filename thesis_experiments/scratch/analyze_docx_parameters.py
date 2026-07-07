import sys
import re

def search_parameters(file_path):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    # Let's search for "umbral" or "score" or "70" or "60" or "corte"
    print("--- SCORES & THRESHOLDS ---")
    pattern_score = re.compile(r"(umbral|score|70|setenta|60|sesenta|corte)", re.IGNORECASE)
    for idx, line in enumerate(lines):
        if pattern_score.search(line):
            # Print if it contains numbers like 70, 60 or specific threshold terms
            if any(term in line.lower() for term in ["umbral", "corte", "score", "70", "setenta", "60", "sesenta"]):
                print(f"L{idx+1}: {line.strip()}")
                
    print("\n--- EMBEDDING & CHUNKING ---")
    pattern_emb = re.compile(r"(mpnet|sentence-transformers|embedding|chunk|512|2048|overlap|solapamiento|dimension|setecientas|768)", re.IGNORECASE)
    for idx, line in enumerate(lines):
        if pattern_emb.search(line):
            if any(term in line.lower() for term in ["mpnet", "transformer", "chunk", "overlap", "solapamiento", "768", "setecientas"]):
                print(f"L{idx+1}: {line.strip()}")

    print("\n--- MODEL & PROVIDERS ---")
    pattern_model = re.compile(r"(sonnet|haiku|opus|gemini|openai|azure|vertex|claude|gpt|provider|vector)", re.IGNORECASE)
    for idx, line in enumerate(lines):
        if pattern_model.search(line):
            if any(term in line.lower() for term in ["sonnet", "haiku", "opus", "gemini", "gpt", "vertex", "claude"]):
                print(f"L{idx+1}: {line.strip()}")

    print("\n--- GOLD STANDARD & KAPPA ---")
    pattern_gs = re.compile(r"(gold standard|cohen|kappa|κ|acuerdo|rrhh|experto|evaluador)", re.IGNORECASE)
    for idx, line in enumerate(lines):
        if pattern_gs.search(line):
            print(f"L{idx+1}: {line.strip()}")

if __name__ == "__main__":
    search_parameters("paper/Talento_sin_nombre_extracted.md")
