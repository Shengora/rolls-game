import os
import json
import time
import urllib.request
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
WALLET_CONFIG_PATH = os.path.join(BASE_DIR, "wallet_config.json")
PROCESSED_TXS_PATH = os.path.join(BASE_DIR, "ton_processed_txs.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

_cfg = load_config()
PROJECT_TON_WALLET = os.getenv("PROJECT_TON_WALLET", _cfg.get("project_ton_wallet", "UQAUKFlbadxR5WFvN4V-Y5mo0vYSez0qnR9IN2eS1zYluvvB"))
RAW_TON_ADDRESS = os.getenv("RAW_TON_ADDRESS", _cfg.get("raw_ton_address", "0:1428595b69dc51e5616f37857e6399a8d2f6127b3d2a9d1f48376792d73625ba"))

def get_project_wallet():
    return PROJECT_TON_WALLET

def load_processed_txs():
    if os.path.exists(PROCESSED_TXS_PATH):
        try:
            with open(PROCESSED_TXS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_processed_tx(tx_hash, data):
    txs = load_processed_txs()
    txs[tx_hash] = data
    try:
        with open(PROCESSED_TXS_PATH, "w", encoding="utf-8") as f:
            json.dump(txs, f, indent=2)
    except Exception as e:
        print(f"[TON WALLET] Error saving processed tx: {e}")

def check_incoming_blockchain_transactions():
    """
    Scans TonAPI for incoming transfers to the owner's TON wallet.
    Returns list of newly received payments: [{tx_hash, sender, amount_ton, telegram_id, comment}]
    """
    url = f"https://tonapi.io/v2/blockchain/accounts/{RAW_TON_ADDRESS}/transactions?limit=15"
    req = urllib.request.Request(url, headers={"User-Agent": "ShencasRolls/1.0"})
    
    new_payments = []
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            txs = data.get("transactions", [])
            processed = load_processed_txs()
            
            for tx in txs:
                tx_hash = tx.get("hash")
                if not tx_hash or tx_hash in processed:
                    continue
                    
                in_msg = tx.get("in_msg", {})
                val_nano = in_msg.get("value", 0)
                amount_ton = round(val_nano / 1e9, 4)
                
                # We only care about positive incoming transfers
                if amount_ton <= 0:
                    processed[tx_hash] = {"status": "ignored_non_positive"}
                    continue
                    
                source_addr = in_msg.get("source", {}).get("address", "")
                decoded_body = in_msg.get("decoded_body", {})
                comment = decoded_body.get("text", "") if isinstance(decoded_body, dict) else ""
                
                # Check if comment contains a telegram ID: e.g. "rolls_6644911092" or "6644911092"
                tid = None
                if comment:
                    for part in comment.replace("_", " ").replace("-", " ").split():
                        if part.isdigit() and len(part) >= 6:
                            tid = int(part)
                            break
                            
                new_payments.append({
                    "tx_hash": tx_hash,
                    "amount_ton": amount_ton,
                    "sender": source_addr,
                    "comment": comment,
                    "telegram_id": tid,
                    "utime": tx.get("utime")
                })
                
                save_processed_tx(tx_hash, {
                    "amount_ton": amount_ton,
                    "sender": source_addr,
                    "comment": comment,
                    "telegram_id": tid,
                    "processed_at": datetime.now(timezone.utc).isoformat()
                })
                
    except Exception as e:
        print(f"[TON WALLET] Error scanning blockchain: {e}")
        
    return new_payments

if __name__ == "__main__":
    print(f"Project TON Wallet: {PROJECT_TON_WALLET}")
    print("Testing blockchain scanner...")
    incoming = check_incoming_blockchain_transactions()
    print(f"New incoming payments: {len(incoming)}")
