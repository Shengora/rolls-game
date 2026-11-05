import os
import sys
import time
import json
import urllib.request
import urllib.parse
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

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"bot_token": "", "webapp_url": ""}

def telegram_api(token, method, data=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[TG API Error] {method}: {e}")
        time.sleep(2)
        return None

def set_menu_button(token, webapp_url):
    data = {
        "menu_button": {
            "type": "web_app",
            "text": "Play Rolls 🎰",
            "web_app": {
                "url": webapp_url
            }
        }
    }
    res = telegram_api(token, "setChatMenuButton", data)
    print("[Bot] Menu button configured:", res)

def start_bot(token):
    print(f"[Bot] Starting Telegram bot polling for Shencasbot...")
    offset = 0
    while True:
        try:
            cfg = load_config()
            webapp_url = cfg.get("webapp_url", "")
            
            updates = telegram_api(token, "getUpdates", {"offset": offset, "timeout": 20})
            if updates and updates.get("ok"):
                for item in updates.get("result", []):
                    offset = item["update_id"] + 1
                    msg = item.get("message")
                    if not msg:
                        continue
                    
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    user_name = msg.get("from", {}).get("first_name", "Do'stim")
                    
                    if text.startswith("/start"):
                        parts = text.split()
                        inviter_id = None
                        user_uname = msg.get("from", {}).get("username", "player")
                        if len(parts) > 1:
                            raw_param = parts[1].replace("ref_", "").strip()
                            if raw_param.isdigit():
                                inviter_id = raw_param
                                try:
                                    req_data = json.dumps({
                                        "inviter_id": inviter_id,
                                        "user_id": chat_id,
                                        "display_name": user_name,
                                        "username": user_uname
                                    }).encode("utf-8")
                                    reg_req = urllib.request.Request(
                                        "http://127.0.0.1:8080/api/v1/referral/register",
                                        data=req_data,
                                        headers={"Content-Type": "application/json"}
                                    )
                                    with urllib.request.urlopen(reg_req, timeout=3) as reg_resp:
                                        print(f"[Bot] Registered referral: inviter={inviter_id}, new_user={chat_id}")
                                except Exception as e:
                                    print(f"[Bot] Referral register error: {e}")

                        if inviter_id:
                            welcome_text = (
                                f"Assalomu alaykum, <b>{user_name}</b>!\n\n"
                                f"🎁 Siz do'stingiz taklifi bilan kirdingiz!\n"
                                f"🎰 <b>Rolls Game Mini App</b>ga xush kelibsiz!\n\n"
                                f"Pastdagi tugmani bosing va o'yinni boshlang:"
                            )
                        else:
                            welcome_text = (
                                f"Assalomu alaykum, <b>{user_name}</b>!\n\n"
                                f"🎰 <b>Rolls Game Mini App</b>ga xush kelibsiz!\n\n"
                                f"Pastdagi tugmani bosing va o'yinni boshlang:"
                            )

                        app_url = f"{webapp_url}?ref={inviter_id}" if inviter_id else webapp_url
                        keyboard = {
                            "inline_keyboard": [
                                [
                                    {
                                        "text": "🚀 O'yinni boshlash (Play Rolls)",
                                        "web_app": {"url": app_url}
                                    }
                                ]
                            ]
                        }
                        telegram_api(token, "sendMessage", {
                            "chat_id": chat_id,
                            "text": welcome_text,
                            "parse_mode": "HTML",
                            "reply_markup": keyboard
                        })
            else:
                time.sleep(1)
        except Exception as e:
            print(f"[Polling Error] {e}")
            time.sleep(3)

if __name__ == "__main__":
    cfg = load_config()
    token = sys.argv[1] if len(sys.argv) > 1 else cfg.get("bot_token")
    if not token:
        print("Bot token topilmadi!")
        sys.exit(1)
    start_bot(token)
