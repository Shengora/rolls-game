import re
import os

base_dir = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game"
with open(os.path.join(base_dir, 'public/_nuxt/ZEhFy-gV.js'), 'r', encoding='utf-8') as f:
    text = f.read()

endpoints = set(re.findall(r'url:\s*["\']([^"\']+)["\']', text))
print("--- ALL URLS IN ZEhFy-gV.js ---")
for ep in sorted(endpoints):
    print(ep)
