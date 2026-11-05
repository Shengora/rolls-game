import os
import re
import urllib.request

BASE_URL = "https://app.rolls.codes/_nuxt"
NUXT_DIR = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public\_nuxt"

with open(os.path.join(NUXT_DIR, "ZEhFy-gV.js"), "r", encoding="utf-8") as f:
    text = f.read()

chunks = set(re.findall(r'import\(["\']\./([^"\']+)["\']\)', text))
print(f"Total chunks found in entry file: {len(chunks)}")

downloaded = set()
to_download = list(chunks)

while to_download:
    chunk_name = to_download.pop(0)
    if chunk_name in downloaded:
        continue
    downloaded.add(chunk_name)
    
    url = f"{BASE_URL}/{chunk_name}"
    local_path = os.path.join(NUXT_DIR, chunk_name)
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            with open(local_path, "wb") as f:
                f.write(content)
            print(f"[OK] {chunk_name} ({len(content)} bytes)")
            
            # Scan this downloaded chunk for any further nested imports!
            text_chunk = content.decode("utf-8", errors="ignore")
            nested = re.findall(r'import\(["\']\./([^"\']+)["\']\)', text_chunk)
            for n in nested:
                if n not in downloaded and n not in to_download:
                    print(f"  -> Found nested chunk: {n}")
                    to_download.append(n)
    except Exception as e:
        print(f"[FAIL] {chunk_name}: {e}")

print(f"\nAll done! Downloaded {len(downloaded)} chunks successfully.")
