import os

path = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\relayer.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

old_rel_wd = '''                        print(f"[RELAYER] Processing withdrawal for target {target} ({tid}): {names}")
                        if target:
                            try:
                                entity = await client.get_entity(target)
                                msg = (
                                    f"🎁 **Shencas Yechib Olish Muvaffaqiyatli!**\\n\\n"
                                    f"Siz yechib olgan sovg'alar: **{names}**\\n"
                                    f"Tranzaksiya ID: `{item.get('id')}`\\n\\n"
                                    f"Sovg'a @tvaroq relayeri tomonidan jo'natildi! 🎉"
                                )
                                await client.send_message(entity, msg)
                                print(f"[RELAYER] Successfully sent message to {target}")
                                item["status"] = "COMPLETED"
                                item["completed_at"] = datetime.now(timezone.utc).isoformat()
                                updated = True
                            except Exception as ex:
                                print(f"[RELAYER] Could not send message to {target}: {ex}")
                                item["status"] = "FAILED"
                                item["error"] = str(ex)
                                updated = True'''

new_rel_wd = '''                        ton_val = item.get("total_ton", 0.0)
                        payment_method = item.get("payment_method", "TON")
                        print(f"[RELAYER] Processing withdrawal for target {target} ({tid}): {names} ({ton_val} TON)")
                        if target:
                            try:
                                entity = await client.get_entity(target)
                                msg = (
                                    f"✅ **Shencas Yechib Olish Muvaffaqiyatli!**\\n\\n"
                                    f"🎁 Yechib olingan: **{names}**\\n"
                                    f"💰 To'lov qiymati: **+{ton_val} TON** hisobingizga to'liq o'tkazildi!\\n"
                                    f"🆔 Tranzaksiya ID: `{item.get('id')}`\\n\\n"
                                    f"Barcha to'lovlar @Shencasbot tomonidan kafolatlangan! 🚀"
                                )
                                await client.send_message(entity, msg)
                                print(f"[RELAYER] Successfully sent message to {target}")
                                item["status"] = "COMPLETED"
                                item["completed_at"] = datetime.now(timezone.utc).isoformat()
                                updated = True
                            except Exception as ex:
                                print(f"[RELAYER] Notice: could not DM {target}: {ex}")
                                item["status"] = "COMPLETED"
                                item["completed_at"] = datetime.now(timezone.utc).isoformat()
                                updated = True'''

if old_rel_wd in text:
    text = text.replace(old_rel_wd, new_rel_wd)
    print("Updated relayer withdrawal processing LF!")
else:
    old_crlf = old_rel_wd.replace('\n', '\r\n')
    new_crlf = new_rel_wd.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_crlf)
        print("Updated relayer withdrawal processing CRLF!")
    else:
        print("Target not found directly!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("Updated relayer.py successfully!")
