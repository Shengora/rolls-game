import os
import sys
import json
import time
import random
import socket
import asyncio
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from telethon import TelegramClient, events
from telethon.tl import types, functions
from market_price_engine import get_nft_lowest_floor
import telegram_notify

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Force IPv4 resolution to prevent Windows network hangs with api.telegram.org
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

API_ID = 36122528
API_HASH = "5986d2d8aae8d8534ca003efef9cef81"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, "relayer")
CONFIG_PATH = os.path.join(BASE_DIR, "relayer_config.json")
QUEUE_PATH = os.path.join(BASE_DIR, "withdrawals_queue.json")
PRICES_PATH = os.path.join(BASE_DIR, "gift_prices.json")

def get_current_prices():
    if os.path.exists(PRICES_PATH):
        try:
            with open(PRICES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "stars_per_ton": 50.0,
        "unique_gifts": {
            "bondedring": 44.0,
            "diamondring": 37.0,
            "gemsignet": 72.0,
            "crystalball": 15.0,
            "durovsglasses": 159.0
        }
    }

PROCESSED_GIFTS_PATH = os.path.join(BASE_DIR, "processed_gifts.json")
SERVER_URL = "http://127.0.0.1:8080"
RELAYER_SECRET = "shencas_relayer_secret_8830393679_secure"

def is_already_processed(msg_id):
    if os.path.exists(PROCESSED_GIFTS_PATH):
        try:
            with open(PROCESSED_GIFTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return str(msg_id) in data
        except Exception:
            return False
    return False

def mark_as_processed(msg_id, sender_id, gift_title, value_ton):
    data = {}
    if os.path.exists(PROCESSED_GIFTS_PATH):
        try:
            with open(PROCESSED_GIFTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[str(msg_id)] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sender_id": sender_id,
        "gift_title": gift_title,
        "value_ton": value_ton
    }
    try:
        with open(PROCESSED_GIFTS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[RELAYER] Error saving processed gifts: {e}")

def notify_server_gift(sender_id, sender_username, gift_name="Telegram Star Gift", value_ton=10.0, model="star_gift", background="gold", rarity=2, num=100, msg_id="0"):
    try:
        url = f"{SERVER_URL}/api/v1/relayer/gift-received"
        payload = json.dumps({
            "sender_id": sender_id,
            "sender_username": sender_username,
            "gift_name": gift_name,
            "value_ton": value_ton,
            "model": model,
            "background": background,
            "rarity": rarity,
            "num": num,
            "msg_id": str(msg_id)
        }).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Relayer-Secret": RELAYER_SECRET
            }
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[RELAYER] Server response: {data}")
            return data
    except Exception as e:
        print(f"[RELAYER] Error calling server: {e}")
        return None

async def process_withdrawals(client):
    while True:
        try:
            if os.path.exists(QUEUE_PATH):
                with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                    queue = json.load(f)
                
                updated = False
                for item in queue:
                    if item.get("status") == "PENDING":
                        tid = item.get("telegram_id")
                        gifts = item.get("gifts", [])
                        names = ", ".join([g.get("title", "Sovg'a") for g in gifts]) or "Sovg'a"
                        
                        target = item.get("username") or tid
                        if isinstance(target, str) and not target.startswith("@") and not target.isdigit():
                            target = f"@{target}"
                        
                        ton_val = item.get("total_ton", 0.0)
                        payment_method = item.get("payment_method", "TON")
                        print(f"[RELAYER] Processing withdrawal for target {target} ({tid}): {names} ({ton_val} TON)")
                        
                        if target:
                            try:
                                entity = await client.get_entity(target)
                                
                                # Real Telegram NFT Transfer Attempt
                                real_nft_transferred = False
                                try:
                                    req_gifts = functions.payments.GetSavedStarGiftsRequest(
                                        peer=await client.get_input_entity("me"),
                                        offset="",
                                        limit=50
                                    )
                                    res_gifts = await client(req_gifts)
                                    saved_gifts_list = res_gifts.gifts if hasattr(res_gifts, "gifts") else []
                                    
                                    for g_item in gifts:
                                        target_slug = g_item.get("slug")
                                        target_title = g_item.get("title", "").lower()
                                        
                                        matching_saved = None
                                        for sg in saved_gifts_list:
                                            sg_gift = getattr(sg, "gift", None)
                                            sg_slug = getattr(sg_gift, "slug", "")
                                            sg_title = getattr(sg_gift, "title", "").lower()
                                            if (target_slug and target_slug == sg_slug) or (target_title and target_title in sg_title):
                                                matching_saved = sg
                                                break
                                                
                                        if matching_saved:
                                            sg_gift = getattr(matching_saved, "gift", None)
                                            if hasattr(sg_gift, "slug") and sg_gift.slug:
                                                input_gift = types.InputSavedStarGiftSlug(slug=sg_gift.slug)
                                            else:
                                                input_gift = types.InputSavedStarGiftUser(msg_id=matching_saved.msg_id)
                                                
                                            await client(functions.payments.TransferStarGiftRequest(
                                                stargift=input_gift,
                                                to_id=await client.get_input_entity(entity)
                                            ))
                                            print(f"[RELAYER] 🎉 REAL TELEGRAM NFT TRANSFERRED to {target}: {getattr(sg_gift, 'title', 'Gift')}")
                                            real_nft_transferred = True
                                            saved_gifts_list.remove(matching_saved)
                                except Exception as nft_ex:
                                    print(f"[RELAYER] Note on NFT transfer check: {nft_ex}")

                                if real_nft_transferred:
                                    print(f"[RELAYER] Real NFT successfully transferred to {target}")
                                    item["status"] = "COMPLETED"
                                    item["completed_at"] = datetime.now(timezone.utc).isoformat()
                                    try:
                                        telegram_notify.notify_nft_withdrawal_request(
                                            tid, item.get("username"), gifts, ton_val, item.get("id"), relayer_sent=True
                                        )
                                    except Exception as ex_n:
                                        print(f"[RELAYER] Notification error: {ex_n}")
                                else:
                                    print(f"[RELAYER] NFT NOT found in relayer. Notifying admin for manual delivery to {target}")
                                    item["status"] = "PENDING_ADMIN"
                                    item["completed_at"] = datetime.now(timezone.utc).isoformat()
                                    item["admin_notified"] = True
                                    try:
                                        telegram_notify.notify_nft_withdrawal_request(
                                            tid, item.get("username"), gifts, ton_val, item.get("id"), relayer_sent=False
                                        )
                                    except Exception as ex_n:
                                        print(f"[RELAYER] Notification error: {ex_n}")
                                updated = True
                            except Exception as ex:
                                print(f"[RELAYER] Error processing withdrawal for {target}: {ex}")
                                item["status"] = "PENDING_ADMIN"
                                item["completed_at"] = datetime.now(timezone.utc).isoformat()
                                item["admin_notified"] = True
                                try:
                                    telegram_notify.notify_nft_withdrawal_request(
                                        tid, item.get("username"), gifts, ton_val, item.get("id"), relayer_sent=False
                                    )
                                except Exception as ex_n:
                                    pass
                                updated = True
                
                if updated:
                    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
                        json.dump(queue, f, indent=2)
        except Exception as e:
            print(f"[RELAYER] Queue worker error: {e}")
        
        await asyncio.sleep(3)

async def main():
    print("[RELAYER] Starting Telethon Relayer Client...")
    client = TelegramClient(
        SESSION_PATH,
        API_ID,
        API_HASH,
        device_model="Desktop",
        system_version="Windows 11",
        app_version="5.3.1 x64",
        lang_code="en",
        system_lang_code="en"
    )

    await client.start()
    me = await client.get_me()
    print(f"[RELAYER] Logged in as: @{me.username} ({me.first_name}), ID: {me.id}")

    # Listen for incoming private messages / genuine gifts
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if not event.is_private:
            return
        
        sender = await event.get_sender()
        sender_id = event.sender_id
        sender_username = getattr(sender, 'username', '') or getattr(sender, 'first_name', '')
        text = (event.raw_text or "").strip()
        msg_id = event.message.id
        
        action = getattr(event.message, 'action', None)
        action_name = type(action).__name__ if action else "None"
        
        print(f"[RELAYER] Msg {msg_id} from {sender_id} (@{sender_username}), action: {action_name}, text: '{text[:80]}'")

        # STRICT VERIFICATION: ONLY genuine Telegram gift actions are accepted!
        # Plain text commands like /deposit or text containing 'sovga' MUST NEVER trigger deposits!
        is_real_gift = isinstance(action, (
            types.MessageActionStarGift,
            types.MessageActionStarGiftUnique,
            types.MessageActionGiftTon,
            types.MessageActionGiftStars
        ))

        if is_real_gift:
            if is_already_processed(msg_id):
                print(f"[RELAYER] Msg {msg_id} already processed. Skipping duplicate.")
                return

            prices_cfg = get_current_prices()
            stars_rate = float(prices_cfg.get("stars_per_ton", 50.0))
            unique_cfg = prices_cfg.get("unique_gifts", {})

            if isinstance(action, types.MessageActionStarGift):
                # RULE 3: Plain non-NFT star gifts do NOT participate (hisoblash kerak emas)
                # Silent mode: do not reply in chat
                # await event.reply(reply_msg)
                print(f"[RELAYER] Rejected non-NFT star gift from {sender_id} (Rule: only real NFTs)")
                return

            elif isinstance(action, types.MessageActionStarGiftUnique):
                # RULE 1 & 2: Real live market floor from Fragment / see.tg style indexer (eng arzon floor)
                nft_gift = action.gift
                gift_title = getattr(nft_gift, "title", "Unique NFT Gift")
                num = getattr(nft_gift, "num", 1)
                
                model_name = ""
                attrs = getattr(nft_gift, "attributes", []) or []
                for a in attrs:
                    if hasattr(a, "name") and ("Model" in a.__class__.__name__ or hasattr(a, "model")):
                        model_name = getattr(a, "name", "")
                        break
                        
                # Query market_price_engine for the lowest active floor price across markets in Gram
                price_gram, m_details = get_nft_lowest_floor(title=gift_title, model=model_name, collection=gift_title, fallback=25.0)
                value_ton = price_gram # 1 Gram = 1 TON in game balance
                model = normalize_key(gift_title) or "nft_gift"
                background = "gold" if value_ton >= 50.0 else "purple"
                rarity = 3 if value_ton >= 50.0 else 2
                source_label = m_details.get("source", "Fragment / TG Market")

            elif isinstance(action, types.MessageActionGiftTon):
                value_ton = float(getattr(action, "amount", 10.0))
                gift_title = f"TON Gift ({value_ton} Gram)"
                model, background, rarity, num = "ton_gift", "cyan", 2, 1
                source_label = "TON Blockchain"

            else:
                # Other non-NFT gift -> reject per Rule 3
                # Silent mode: do not reply in chat
                # await event.reply(reply_msg)
                return

            # Notify game server with secret key
            res = notify_server_gift(
                sender_id=sender_id,
                sender_username=sender_username,
                gift_name=gift_title,
                value_ton=value_ton,
                model=model,
                background=background,
                rarity=rarity,
                num=num,
                msg_id=msg_id
            )

            mark_as_processed(msg_id, sender_id, gift_title, value_ton)

            # Silent mode: gift credited silently without sending message in chat
            # await event.reply(reply_msg)
            print(f"[RELAYER] Real gift credited for {sender_id}: {gift_title} ({value_ton} TON)")

        else:
            # User sent plain text or tried to send fake deposit command
            if text.startswith("/") or "deposit" in text.lower() or "sovga" in text.lower() or "sovg'a" in text.lower() or "podarok" in text.lower():
                reply_msg = (
                    f"⛔️ **Matnli buyruqlar orqali depozit qabul qilinmaydi!**\n\n"
                    f"Hech qanday matn yoki buyruq (masalan, `/deposit ...`) orqali o'yinga sovg'a qo'shib bo'lmaydi.\n\n"
                    f"🎁 **Haqiqiy sovg'a yuborish bo'yicha ko'rsatma:**\n"
                    f"1. Profilimga kiring (@{me.username})\n"
                    f"2. Yuqori o'ng burchakdagi **•••** (uch nuqta) tugmasini bosing\n"
                    f"3. **'Send a Gift' (Sovg'a yuborish)** tugmasini tanlang va Telegram orqali haqiqiy sovg'a yuboring\n\n"
                    f"Yuborilgan har bir haqiqiy Telegram sovg'asi relayer tomonidan avtomat tekshirilib, darhol profilingizga tushiriladi! 🛡"
                )
            else:
                reply_msg = (
                    f"👋 **Assalomu alaykum!**\n\n"
                    f"Men **Shencas / Rolls** o'yinining rasmiy avtomat relayeriman (@{me.username}).\n\n"
                    f"🎁 O'yinga depozit qilish uchun profilimdagi **'Send a Gift'** funksiyasi orqali haqiqiy Telegram sovg'asi yuborishingiz kerak.\n"
                    f"U avtomatik tarzda o'yindagi hisobingizga qo'shiladi."
                )
            # Silent mode: ignore plain text without writing message in chat
            # await event.reply(reply_msg)
            print(f"[RELAYER] (Silent) Ignored text/fake deposit from {sender_id}")

    # Launch background queue worker
    asyncio.create_task(process_withdrawals(client))

    print("[RELAYER] Relayer is ACTIVE and listening for authentic gifts & withdrawals...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"[RELAYER] Exception in main loop: {e}. Reconnecting in 5s...")
            time.sleep(5)
