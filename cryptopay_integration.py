import os
import json
import time
import urllib.request
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
PROCESSED_FILE = os.path.join(BASE_DIR, "cryptopay_processed.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

_cfg = load_config()
CRYPTO_PAY_TOKEN = os.getenv("CRYPTOPAY_TOKEN", _cfg.get("cryptopay_token", ""))
API_BASE = "https://pay.crypt.bot/api"

def load_processed_invoices():
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_processed_invoice(invoice_id, data):
    processed = load_processed_invoices()
    processed[str(invoice_id)] = data
    try:
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(processed, f, indent=2)
    except Exception as e:
        print(f"[CRYPTOPAY] Error saving processed invoice: {e}")

def create_crypto_invoice(amount, telegram_id, currency="TON"):
    """
    Creates a real live invoice in @CryptoBot for the user.
    Funds will go directly to the owner's CryptoBot account!
    """
    url = f"{API_BASE}/createInvoice"
    payload = {
        "asset": currency,
        "amount": str(round(float(amount), 2)),
        "description": f"Shencas Rolls: {amount} Gram to'ldirish",
        "hidden_message": "To'lov qabul qilindi! O'yindagi Gram balansingiz muvaffaqiyatli to'ldirildi. Omad!",
        "payload": json.dumps({
            "telegram_id": int(telegram_id),
            "amount": float(amount),
            "created_at": time.time()
        }),
        "allow_comments": False,
        "allow_anonymous": True
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN,
            "Content-Type": "application/json",
            "User-Agent": "ShencasRolls/1.0"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode("utf-8"))
            if res.get("ok"):
                item = res.get("result", {})
                print(f"[CRYPTOPAY] Created live invoice #{item.get('invoice_id')} for user {telegram_id}: {amount} {currency}")
                return item
            else:
                print(f"[CRYPTOPAY] createInvoice error: {res}")
                return None
    except Exception as e:
        print(f"[CRYPTOPAY] createInvoice request failed: {e}")
        return None

def check_paid_invoices():
    """
    Queries @CryptoBot API for recently paid invoices.
    Returns list of newly paid items: [{invoice_id, telegram_id, amount}]
    """
    url = f"{API_BASE}/getInvoices?status=paid&count=20"
    req = urllib.request.Request(
        url,
        headers={
            "Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN,
            "User-Agent": "ShencasRolls/1.0"
        }
    )
    
    newly_paid = []
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            res = json.loads(r.read().decode("utf-8"))
            if res.get("ok"):
                items = res.get("result", {}).get("items", [])
                processed = load_processed_invoices()
                
                for item in items:
                    inv_id = str(item.get("invoice_id"))
                    if inv_id in processed:
                        continue
                        
                    raw_payload = item.get("payload")
                    tid = None
                    amount = float(item.get("amount", 0.0))
                    
                    if raw_payload:
                        try:
                            p_data = json.loads(raw_payload)
                            tid = p_data.get("telegram_id")
                            if "amount" in p_data:
                                amount = float(p_data["amount"])
                        except Exception:
                            pass
                            
                    if tid and amount > 0:
                        newly_paid.append({
                            "invoice_id": inv_id,
                            "telegram_id": tid,
                            "amount": amount,
                            "asset": item.get("asset", "TON"),
                            "paid_at": item.get("paid_at", datetime.now(timezone.utc).isoformat())
                        })
                        save_processed_invoice(inv_id, {
                            "telegram_id": tid,
                            "amount": amount,
                            "paid_at": item.get("paid_at")
                        })
    except Exception as e:
        print(f"[CRYPTOPAY] check_paid_invoices error: {e}")
        
    return newly_paid

if __name__ == "__main__":
    print("Testing cryptopay_integration.py...")
    inv = create_crypto_invoice(10.0, 6644911092)
    if inv:
        print("Invoice created successfully!")
        print("Mini app invoice url:", inv.get("mini_app_invoice_url"))
        print("Pay URL:", inv.get("pay_url"))
    paid = check_paid_invoices()
    print("Newly paid count:", len(paid))
