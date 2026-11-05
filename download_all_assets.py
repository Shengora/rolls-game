import os
import re
import urllib.request

BASE_URL = "https://app.rolls.codes"
PUBLIC_DIR = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public"

# Remove the fake .map files that were downloaded as index.html
for f in ["_nuxt/ZEhFy-gV.js.map", "assets/vendor/tgs-player-2.0.12.js.map"]:
    p = os.path.join(PUBLIC_DIR, f.replace("/", os.sep))
    if os.path.exists(p):
        os.remove(p)

# Scan css and js
files_to_scan = [
    os.path.join(PUBLIC_DIR, "_nuxt", "entry.CUIRCfqw.css"),
    os.path.join(PUBLIC_DIR, "_nuxt", "ZEhFy-gV.js")
]

asset_urls = set()
for fpath in files_to_scan:
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    # Find /_nuxt/... or /assets/...
    found = re.findall(r'["\'](/(?:_nuxt|assets)/[a-zA-Z0-9_\-\./]+\.(?:webp|png|jpg|jpeg|svg|mp3|ogg|wav|json|woff2?|ttf))["\']', content)
    asset_urls.update(found)
    # url(...) in CSS
    found_css = re.findall(r'url\(["\']?(/[^"\'\)]+)["\']?\)', content)
    asset_urls.update(found_css)

print(f"Found {len(asset_urls)} referenced media assets.")

downloaded = 0
for rel in sorted(asset_urls):
    clean_rel = rel.lstrip("/").split("?")[0].split("#")[0]
    local_p = os.path.join(PUBLIC_DIR, clean_rel.replace("/", os.sep))
    if os.path.exists(local_p):
        continue
    os.makedirs(os.path.dirname(local_p), exist_ok=True)
    full_url = f"{BASE_URL}/{clean_rel}"
    try:
        req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(local_p, "wb") as out:
                out.write(data)
            downloaded += 1
            print(f"[+] Downloaded {clean_rel} ({len(data)} bytes)")
    except Exception as e:
        print(f"[-] Skipped {clean_rel}: {e}")

print(f"\nDone! Downloaded {downloaded} new assets.")
