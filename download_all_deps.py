import os
import json
import urllib.request

BASE_URL = "https://app.rolls.codes/_nuxt"
NUXT_DIR = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public\_nuxt"

with open(r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\all_deps.json", "r", encoding="utf-8") as f:
    deps = json.load(f)

print(f"Starting download of {len(deps)} dependencies...")
downloaded = 0
failed = 0

for dep in deps:
    filename = dep.lstrip("./")
    local_path = os.path.join(NUXT_DIR, filename)
    if os.path.exists(local_path):
        continue
    url = f"{BASE_URL}/{filename}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            with open(local_path, "wb") as out:
                out.write(content)
            downloaded += 1
            print(f"[OK] {filename} ({len(content)} bytes)")
    except Exception as e:
        failed += 1
        print(f"[FAIL] {filename}: {e}")

print(f"\nCompleted: {downloaded} downloaded, {failed} failed.")
