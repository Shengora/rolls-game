import re
import json

with open(r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public\_nuxt\ZEhFy-gV.js", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('m.f=[')
if idx != -1:
    end = text.find(']', idx)
    raw_array = text[idx+4:end+1]
    # parse array
    files = json.loads(raw_array)
    print(f"Total dependencies in m.f: {len(files)}")
    with open(r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\all_deps.json", "w", encoding="utf-8") as out:
        json.dump(files, out, indent=2)
    print("Saved to all_deps.json")
else:
    print("m.f not found!")
