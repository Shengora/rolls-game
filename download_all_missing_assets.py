import os
import re
import urllib.request

bundle_dir = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public\_nuxt"
public_dir = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public"

all_assets = set()
for f in os.listdir(bundle_dir):
    if f.endswith(".js"):
        with open(os.path.join(bundle_dir, f), "r", encoding="utf-8", errors="ignore") as fp:
            c = fp.read()
            for m in re.finditer(r'/assets/[a-zA-Z0-9_\-\/\.]+\.(?:webp|svg|png|jpg|json)', c):
                all_assets.add(m.group(0))

print(f"Total assets found in bundle: {len(all_assets)}")
missing = []
for a in all_assets:
    local_p = os.path.join(public_dir, a.lstrip("/").replace("/", os.sep))
    if not os.path.exists(local_p):
        missing.append(a)

print(f"Missing assets count: {len(missing)}")
for m in sorted(missing):
    print("  Missing:", m)

# Download missing assets from app.rolls.codes
BASE_URL = "https://app.rolls.codes"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

downloaded = 0
for a in missing:
    target = os.path.join(public_dir, a.lstrip("/").replace("/", os.sep))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    try:
        req = urllib.request.Request(BASE_URL + a, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
            with open(target, "wb") as fp:
                fp.write(data)
            print(f"DOWNLOADED: {a} ({len(data)} bytes)")
            downloaded += 1
    except Exception as e:
        print(f"Failed {a}: {e}")

print(f"\nTotal downloaded: {downloaded} / {len(missing)}")
