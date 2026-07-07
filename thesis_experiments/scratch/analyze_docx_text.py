import sys
import re

def search_terms_in_file(file_path):
    # Set console stdout to utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    # We want to search for several things:
    # 1. References to thresholds like 70, 60, etc.
    # 2. Embedding models or chunk sizes
    # 3. Model names like Claude 3.5 Sonnet, Claude Sonnet 4.5, Gemini 2.5 Flash, etc.
    # 4. Gold Standard details
    # 5. Retrieval parameters (top-k)
    # 6. Evaluation metrics or equations
    
    queries = [
        r"\b(?:70|setenta)\b",
        r"\b(?:60|sesenta)\b",
        r"mpnet",
        r"sentence-transformers",
        r"embedding",
        r"chunk",
        r"sonnet",
        r"haiku",
        r"opus",
        r"gemini",
        r"openai",
        r"azure",
        r"vertex",
        r"gold standard",
        r"cohen",
        r"kappa",
        r"κ",
        r"top-k",
        r"top_k",
        r"peso",
        r"competencias",
        r"temperatura",
        r"tokens"
    ]
    
    print("=== SEARCH RESULTS IN DOCX ===")
    for q in queries:
        pattern = re.compile(q, re.IGNORECASE)
        print(f"\n--- Query: {q} ---")
        match_count = 0
        for idx, line in enumerate(lines):
            if pattern.search(line):
                # Print line with context (2 lines before and after if possible)
                print(f"Line {idx+1}: {line.strip()}")
                match_count += 1
                if match_count >= 10:
                    print("... (truncated after 10 matches)")
                    break
        if match_count == 0:
            print("No matches.")

if __name__ == "__main__":
    search_terms_in_file("paper/Talento_sin_nombre_extracted.md")
