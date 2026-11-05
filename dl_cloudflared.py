import os
import urllib.request
import time

dest = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\cloudflared.exe"
url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

def resume_download():
    headers = {"User-Agent": "Mozilla/5.0"}
    existing = os.path.getsize(dest) if os.path.exists(dest) else 0
    print(f"Current size: {existing} bytes")
    
    # Check if already complete (~30MB-35MB)
    if existing > 25 * 1024 * 1024:
        # Try to execute --version to test if it's already valid!
        import subprocess
        try:
            res = subprocess.run([dest, "--version"], capture_output=True, text=True)
            if res.returncode == 0:
                print("cloudflared is ALREADY COMPLETE and working:", res.stdout.strip())
                return True
        except Exception as e:
            print("Executable not complete yet:", e)

    req = urllib.request.Request(url, headers=headers)
    if existing > 0:
        req.add_header("Range", f"bytes={existing}-")
        
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            mode = "ab" if existing > 0 else "wb"
            with open(dest, mode) as f:
                while True:
                    chunk = resp.read(1024 * 64)
                    if not chunk:
                        break
                    f.write(chunk)
                    existing += len(chunk)
                    print(f"\rDownloaded {existing / 1024 / 1024:.2f} MB", end="", flush=True)
        print("\nDownload finished!")
        return True
    except Exception as e:
        print(f"\nDownload error: {e}")
        return False

if __name__ == "__main__":
    for i in range(10):
        if resume_download():
            break
        time.sleep(2)
