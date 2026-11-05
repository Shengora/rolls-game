import os
import json

server_path = os.path.join(os.path.dirname(__file__), "server.py")
with open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """        # Withdraw Gifts v2 (TON or Stars)
        if path.endswith("/v1/users/withdraw-gifts/v2"):
            gift_ids = data.get("gift_ids", [])
            for gid in gift_ids:
                matching = next((g for g in USER_STATE["inventory"] if g["gift_id"] == gid), None)
                if matching:
                    USER_STATE["inventory"].remove(matching)
            return self.send_json({
                "withdrawal_id": f"wd_{int(time.time()*1000)}",
                "status": "COMPLETED",
                "gift_count": len(gift_ids),
                "total_ton": 0.0,
                "total_stars": 0,
                "invoice_url": None
            })"""

replacement = """        # Relayer Deposit Webhook
        if path.endswith("/relayer/gift-received") or path.endswith("/v1/relayer/gift-received"):
            sender_id = data.get("sender_id", CURRENT_USER.get("telegram_id", 0))
            sender_username = data.get("sender_username", "")
            title = data.get("gift_name", "Telegram Gift")
            cost_ton = float(data.get("value_ton", 10.0))
            new_gift = {
                "gift_id": f"gift_relayer_{int(time.time()*1000)}",
                "cost_ton": cost_ton,
                "cost_usd": round(cost_ton * 5.0, 2),
                "lombard_cost_ton": round(cost_ton * 0.8, 2),
                "title": title,
                "num": random.randint(100, 9999),
                "model": "telegram_gift",
                "model_rarity": 2 if cost_ton >= 20 else 1,
                "background": "gold" if cost_ton >= 50 else "purple",
                "background_rarity": 2,
                "symbol": "gift",
                "symbol_rarity": 1
            }
            USER_STATE["inventory"].append(new_gift)
            return self.send_json({
                "success": True,
                "message": "Gift credited successfully",
                "gift": new_gift,
                "inventory_count": len(USER_STATE["inventory"])
            })

        # Withdraw Gifts v2 (TON or Stars)
        if path.endswith("/v1/users/withdraw-gifts/v2"):
            gift_ids = data.get("gift_ids", [])
            removed_gifts = []
            for gid in gift_ids:
                matching = next((g for g in USER_STATE["inventory"] if g["gift_id"] == gid), None)
                if matching:
                    USER_STATE["inventory"].remove(matching)
                    removed_gifts.append(matching)

            wd_id = f"wd_{int(time.time()*1000)}"
            queue_item = {
                "id": wd_id,
                "telegram_id": CURRENT_USER.get("telegram_id"),
                "username": CURRENT_USER.get("telegram_username"),
                "gifts": removed_gifts,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": "PENDING"
            }
            try:
                q_file = os.path.join(os.path.dirname(__file__), "withdrawals_queue.json")
                cur_queue = []
                if os.path.exists(q_file):
                    with open(q_file, "r", encoding="utf-8") as qf:
                        cur_queue = json.load(qf)
                cur_queue.append(queue_item)
                with open(q_file, "w", encoding="utf-8") as qf:
                    json.dump(cur_queue, qf, indent=2)
            except Exception as e:
                print(f"Error queueing withdrawal: {e}")

            return self.send_json({
                "withdrawal_id": wd_id,
                "status": "COMPLETED",
                "gift_count": len(gift_ids),
                "total_ton": 0.0,
                "total_stars": 0,
                "invoice_url": None
            })"""

if target in content:
    content = content.replace(target, replacement, 1)
    print("Replaced withdraw-gifts/v2 with relayer deposit & withdrawal queue")
else:
    print("Target withdraw-gifts/v2 not found!")

get_target = '            # User info\n            if api_path.endswith("/v1/users/info"):'
get_replacement = """            # Relayer Status
            if api_path.endswith("/relayer/status") or api_path.endswith("/v1/relayer/status"):
                config_path = os.path.join(os.path.dirname(__file__), "relayer_config.json")
                info = {}
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as cf:
                        info = json.load(cf)
                return self.send_json({
                    "online": True,
                    "relayer": info
                })

            # User info
            if api_path.endswith("/v1/users/info"):"""

if get_target in content:
    content = content.replace(get_target, get_replacement, 1)
    print("Replaced get_target with relayer status")
else:
    print("Get target not found!")

with open(server_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Saved server.py")
