import os
import re
import sys
import subprocess
import time
import json
import urllib.request
import socket

# Force IPv4 to prevent Windows IPv6 routing timeout
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
CLOUDFLARED = os.path.join(os.path.dirname(__file__), "cloudflared.exe")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"bot_token": os.getenv("BOT_TOKEN", ""), "webapp_url": ""}

def set_telegram_menu_button(token, url):
    if not token:
        print("[Bot] No bot token configured, skipping menu button update")
        return
    api_url = f"https://api.telegram.org/bot{token}/setChatMenuButton"
    data = json.dumps({
        "menu_button": {
            "type": "web_app",
            "text": "Play Rolls 🎰",
            "web_app": {"url": url}
        }
    }).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode("utf-8"))
            print(f"[Bot] Menu button updated to: {url} | Result: {res.get('ok')}")
    except Exception as e:
        print(f"[Bot Error] setChatMenuButton: {e}")

def run_tunnel():
    if not os.path.exists(CLOUDFLARED):
        print("cloudflared.exe not found!")
        return
        
    cfg = load_config()
    token = cfg.get("bot_token", os.getenv("BOT_TOKEN", ""))

    print("[Tunnel] Starting Cloudflare Tunnel on 127.0.0.1:8080...")
    proc = subprocess.Popen(
        [CLOUDFLARED, "tunnel", "--protocol", "http2", "--url", "http://127.0.0.1:8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    
    url = None
    url_saved = False
    for line in proc.stdout:
        print(line, end="")
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match and not url_saved:
            url = match.group(0)
            url_saved = True
            print(f"\n=======================================================")
            print(f"🎉 CLOUDFLARE LIVE HTTPS URL: {url}")
            print(f"=======================================================\n")
            
            # Save to config.json
            cfg["webapp_url"] = url
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
                
            set_telegram_menu_button(token, url)
            
    proc.wait()

if __name__ == "__main__":
    while True:
        try:
            run_tunnel()
        except Exception as e:
            print(f"[Tunnel Error] {e}")
        time.sleep(3)
