import os
import urllib.request
import urllib.parse
import json
import socket
import datetime

# Force IPv4 for Windows compatibility
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

_cfg = load_config()
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", _cfg.get("admin_telegram_id", 0)))
BOT_TOKEN = os.getenv("BOT_TOKEN", _cfg.get("bot_token", ""))

def send_admin_alert(text):
    """Sends a Telegram notification to the Admin (Shen: 6644911092)."""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_TELEGRAM_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res.get("ok", False)
    except Exception as e:
        print(f"[ADMIN_ALERT] Failed to send alert: {e}")
        return False

def notify_nft_withdrawal_request(tid, username, gifts, total_ton, wd_id, relayer_sent=False):
    """Notifies admin about an NFT withdrawal with full NFT metadata."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uname_clean = username.lstrip("@") if username else ""
    user_link = f"<a href='https://t.me/{uname_clean}'>@{uname_clean}</a>" if uname_clean else f"<code>{tid}</code>"
    
    gift_cards = []
    for i, g in enumerate(gifts, 1):
        title = g.get("title") or g.get("name") or "Telegram NFT"
        num = g.get("num") or g.get("serial_number") or ""
        num_str = f" #{num}" if num else ""
        cost = g.get("cost_ton", 0.0)
        cost_usd = round(cost * 5.0, 2)
        bg = g.get("background") or "Standard"
        sym = g.get("symbol") or "Default"
        model = g.get("model") or title.lower().replace(" ", "_")
        gid = g.get("gift_id", "")
        
        card = (
            f"<b>{i}. {title}{num_str}</b>\n"
            f"   • 🏷 <b>Model:</b> <code>{model}</code>\n"
            f"   • 🔢 <b>Raqami (Serial):</b> #{num if num else 'Yoq'}\n"
            f"   • 🎨 <b>Orqa foni (Backdrop):</b> {bg.capitalize()}\n"
            f"   • 🔮 <b>Belgisi (Symbol):</b> {sym.capitalize()}\n"
            f"   • 💰 <b>Bozor narxi:</b> {cost} TON (~${cost_usd})\n"
            f"   • 🆔 <b>Gift ID:</b> <code>{gid}</code>"
        )
        gift_cards.append(card)
    
    gifts_text = "\n\n".join(gift_cards) if gift_cards else "• Telegram NFT (Tafsilotlar mavjud emas)"
    
    if relayer_sent:
        text = (
            f"✅ <b>NFT Muvaffaqiyatli Yetkazildi!</b>\n\n"
            f"👤 <b>Qabul qiluvchi:</b> {user_link} (ID: <code>{tid}</code>)\n"
            f"💰 <b>Jami qiymat:</b> {total_ton} TON\n"
            f"🆔 <b>Tranzaksiya:</b> <code>{wd_id}</code>\n"
            f"📅 <b>Vaqt:</b> {now_str}\n\n"
            f"🎁 <b>Yuborilgan Sovg'alar:</b>\n{gifts_text}\n\n"
            f"<i>Relayer (@tvaroq) tomonidan o'yinchiga Telegram orqali to'g'ridan-to'g'ri o'tkazildi!</i>"
        )
    else:
        text = (
            f"⚠️ <b>Yangi NFT Yechib Olish So'rovi!</b>\n\n"
            f"👤 <b>O'yinchi:</b> {user_link} (ID: <code>{tid}</code>)\n"
            f"💰 <b>Jami qiymat:</b> {total_ton} TON\n"
            f"🆔 <b>Tranzaksiya:</b> <code>{wd_id}</code>\n"
            f"📅 <b>Vaqt:</b> {now_str}\n\n"
            f"🎁 <b>Yechib olingan NFT tafsilotlari:</b>\n{gifts_text}\n\n"
            f"❌ <b>Holat:</b> Ushbu sovg'a relayerda mavjud emas, shuning uchun avtomatik yuborilmadi.\n"
            f"ℹ️ <b>Eslatma:</b> O'yinchiga TON berilmadi (balansi oshirilmadi).\n\n"
            f"👉 <b>Nima qilish kerak?</b>\n"
            f"1. {user_link} havolasini bosing.\n"
            f"2. O'yinchiga Telegram orqali yuqoridagi NFT sovg'asini qo'lda sovg'a qiling (Send Gift)."
        )
    return send_admin_alert(text)
