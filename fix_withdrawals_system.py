import os

path = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\server.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

old_block = '''        # Withdraw Gifts v2 (TON or Stars)
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
            })

        # Withdraw Gifts v1
        if path.endswith("/v1/users/withdraw-gifts"):
            gift_ids = data.get("gift_ids", [])
            for gid in gift_ids:
                matching = next((g for g in USER_STATE["inventory"] if g["gift_id"] == gid), None)
                if matching:
                    USER_STATE["inventory"].remove(matching)
            return self.send_json({
                "withdrawal_id": f"wd_{int(time.time()*1000)}",
                "total_stars": 0,
                "gift_count": len(gift_ids),
                "invoice_url": "https://t.me/$invoice_placeholder"
            })'''

new_block = '''        # Withdraw Gifts v2 (TON or Stars)
        if path.endswith("/v1/users/withdraw-gifts/v2"):
            tid, dname, uname, photo = self.get_caller_user()
            gift_ids = data.get("gift_ids", [])
            payment_method = data.get("payment_method", "TON")
            user_inv = get_user_inventory(tid)
            removed_gifts = []
            total_ton = 0.0
            for gid in gift_ids:
                matching = next((g for g in user_inv if g["gift_id"] == gid), None)
                if matching:
                    user_inv.remove(matching)
                    removed_gifts.append(matching)
                    total_ton += matching.get("cost_ton", 0.0)

            total_ton = round(total_ton, 2)
            total_stars = int(total_ton * 50)

            # Credit TON or Stars directly to player balance!
            if payment_method == "TON":
                set_user_balance(tid, get_user_balance(tid) + total_ton)
            elif payment_method == "STARS":
                set_user_stars(tid, get_user_stars(tid) + total_stars)

            wd_id = f"wd_{int(time.time()*1000)}"
            queue_item = {
                "id": wd_id,
                "telegram_id": tid,
                "username": uname,
                "gifts": removed_gifts,
                "payment_method": payment_method,
                "total_ton": total_ton,
                "total_stars": total_stars,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": "COMPLETED"
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
                "gift_count": len(removed_gifts),
                "total_ton": total_ton,
                "total_stars": total_stars,
                "invoice_url": None
            })

        # Withdraw Gifts v1
        if path.endswith("/v1/users/withdraw-gifts"):
            tid, dname, uname, photo = self.get_caller_user()
            gift_ids = data.get("gift_ids", [])
            user_inv = get_user_inventory(tid)
            removed_gifts = []
            total_ton = 0.0
            for gid in gift_ids:
                matching = next((g for g in user_inv if g["gift_id"] == gid), None)
                if matching:
                    user_inv.remove(matching)
                    removed_gifts.append(matching)
                    total_ton += matching.get("cost_ton", 0.0)

            total_ton = round(total_ton, 2)
            set_user_balance(tid, get_user_balance(tid) + total_ton)

            wd_id = f"wd_{int(time.time()*1000)}"
            queue_item = {
                "id": wd_id,
                "telegram_id": tid,
                "username": uname,
                "gifts": removed_gifts,
                "payment_method": "TON",
                "total_ton": total_ton,
                "total_stars": int(total_ton * 50),
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": "COMPLETED"
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
                "total_stars": 0,
                "gift_count": len(removed_gifts),
                "invoice_url": None
            })'''

if old_block in text:
    text = text.replace(old_block, new_block)
    print("Replaced withdrawal block LF!")
else:
    old_crlf = old_block.replace('\n', '\r\n')
    new_crlf = new_block.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_crlf)
        print("Replaced withdrawal block CRLF!")
    else:
        print("Could not find old_block!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("Updated server.py withdrawal handlers successfully!")
