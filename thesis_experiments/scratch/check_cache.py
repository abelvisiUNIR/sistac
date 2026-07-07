import json
from pathlib import Path

cache_path = Path("data/eval_cache_anthropic.json")
if not cache_path.exists():
    print("Cache file does not exist!")
    exit(1)

with open(cache_path, "r", encoding="utf-8") as f:
    cache = json.load(f)

print(f"Total keys in cache: {len(cache)}")

c1_keys = [k for k in cache.keys() if k.startswith("c1_")]
c2_keys = [k for k in cache.keys() if k.startswith("c2_")]
c3_keys = [k for k in cache.keys() if k.startswith("c3_")]

print(f" - C1 keys: {len(c1_keys)}")
print(f" - C2 keys: {len(c2_keys)}")
print(f" - C3 keys: {len(c3_keys)}")

if len(cache) > 0:
    first_key = list(cache.keys())[0]
    print(f"\nFirst key: {first_key}")
    print(f"First value: {json.dumps(cache[first_key], indent=2)[:500]}")
