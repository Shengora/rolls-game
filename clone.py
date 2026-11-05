import os
import re
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://app.rolls.codes"
OUTPUT_DIR = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game"
SRC_DIR = os.path.join(OUTPUT_DIR, "source_code")
PUBLIC_DIR = os.path.join(OUTPUT_DIR, "public")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

visited_urls = set()
downloaded_files = set()

def download_file(rel_path):
    rel_path = rel_path.lstrip("/")
    url = f"{BASE_URL}/{rel_path}"
    if url in downloaded_files:
        return None
    downloaded_files.add(url)
    
    # Target file path
    local_path = os.path.join(PUBLIC_DIR, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            with open(local_path, "wb") as f:
                f.write(content)
            print(f"[OK] {rel_path} ({len(content)} bytes)")
            return content, rel_path
    except Exception as e:
        print(f"[FAIL] {rel_path}: {e}")
        return None

def extract_sourcemap(content, rel_path):
    try:
        data = json.loads(content.decode("utf-8", errors="ignore"))
        sources = data.get("sources", [])
        sources_content = data.get("sourcesContent", [])
        
        if not sources or not sources_content:
            return
            
        print(f"[*] Extracting {len(sources)} source files from {rel_path}...")
        for src_path, src_code in zip(sources, sources_content):
            if not src_code:
                continue
            # Clean path (e.g. webpack:///, nuxt:///, ../, etc)
            clean_path = src_path
            clean_path = re.sub(r"^[a-zA-Z0-9_\-]+:///?", "", clean_path)
            clean_path = clean_path.replace("webpack/runtime/", "runtime/")
            clean_path = clean_path.replace("..", "__")
            clean_path = clean_path.replace("?", "_")
            
            target_file = os.path.join(SRC_DIR, clean_path.replace("/", os.sep))
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(src_code)
    except Exception as e:
        print(f"[ERR] extracting sourcemap {rel_path}: {e}")

def main():
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(SRC_DIR, exist_ok=True)
    
    print("[1] Fetching index.html...")
    req = urllib.request.Request(BASE_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html_content = resp.read().decode("utf-8", errors="ignore")
    
    with open(os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] index.html saved ({len(html_content)} chars)")
    
    # Find all linked assets in HTML
    asset_paths = set()
    for match in re.finditer(r'(?:src|href)=["\'](/[^"\']+)["\']', html_content):
        asset_paths.add(match.group(1))
        
    print(f"[2] Found {len(asset_paths)} assets directly in index.html")
    
    js_files = set()
    map_files = set()
    
    for path in asset_paths:
        res = download_file(path)
        if path.endswith(".js"):
            js_files.add(path)
            map_files.add(path + ".map")
            
    # Parse downloaded JS files to find other chunks and assets
    print("[3] Scanning JS files for chunk imports and assets...")
    scanned_js = set()
    
    while js_files - scanned_js:
        current_batch = list(js_files - scanned_js)
        for js_path in current_batch:
            scanned_js.add(js_path)
            local_js = os.path.join(PUBLIC_DIR, js_path.lstrip("/").replace("/", os.sep))
            if os.path.exists(local_js):
                try:
                    with open(local_js, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                    
                    # Look for Nuxt chunks: e.g. "/_nuxt/XXXXX.js" or "XXXXX.js" or "entry.XXXX.css"
                    found_chunks = re.findall(r'["\'](/_nuxt/[a-zA-Z0-9_\-\.]+\.(?:js|css|webp|png|svg|json|woff2?))["\']', code)
                    # Also look for relative chunks like "foo.B1NsEFyX.js"
                    found_rel_chunks = re.findall(r'["\']([a-zA-Z0-9_\-]{8,}\.(?:js|css|webp|png|svg))["\']', code)
                    for rel in found_rel_chunks:
                        found_chunks.append("/_nuxt/" + rel)
                        
                    for chunk in set(found_chunks):
                        if chunk not in downloaded_files:
                            res = download_file(chunk)
                            if chunk.endswith(".js"):
                                js_files.add(chunk)
                                map_files.add(chunk + ".map")
                except Exception as e:
                    print(f"Error reading {js_path}: {e}")
                    
    print(f"[4] Downloading {len(map_files)} sourcemaps and unpacking original Vue source...")
    for map_path in map_files:
        res = download_file(map_path)
        if res:
            content, r_path = res
            extract_sourcemap(content, r_path)
            
    print("\n[FINISHED] Cloning and extraction complete!")
    print(f"Public bundle: {PUBLIC_DIR}")
    print(f"Unpacked original source code: {SRC_DIR}")

if __name__ == "__main__":
    main()
