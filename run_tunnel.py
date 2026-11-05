import os
import sys
import time
import json
import re
import subprocess
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"bot_token": os.getenv("BOT_TOKEN", ""), "webapp_url": ""}

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

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

def main():
    while True:
        cfg = load_config()
        token = cfg.get("bot_token", os.getenv("BOT_TOKEN", ""))
        
        print("[Tunnel] Starting SSH tunnel via localhost.run to 127.0.0.1:8080...")
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=30",
            "-o", "ServerAliveCountMax=3",
            "-R", "80:127.0.0.1:8080",
            "nokey@localhost.run"
        ]
        
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        url_found = False
        while True:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    print("[Tunnel] Process exited. Restarting in 3 seconds...")
                    break
                time.sleep(0.1)
                continue
            
            print(line, end="")
            m = re.search(r"https://[a-zA-Z0-9\-]+\.lhr\.life", line)
            if m and not url_found:
                live_url = m.group(0)
                url_found = True
                print(f"\n=======================================================")
                print(f"🎉 TUNNEL ACTIVE: {live_url}")
                print(f"=======================================================\n")
                
                cfg["webapp_url"] = live_url
                save_config(cfg)
                set_telegram_menu_button(token, live_url)
                
        time.sleep(3)

if __name__ == "__main__":
    main()
