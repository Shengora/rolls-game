import os

SERVER_PATH = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\server.py"
with open(SERVER_PATH, "r", encoding="utf-8") as f:
    text = f.read()

old_func = '''def get_user_referral(tid):
    tid_str = str(tid)
    invited_list = REFERRALS_DATA.get("referrals", {}).get(tid_str, [])
    invited_count = len(invited_list)

    earnings_info = REFERRALS_DATA.get("earnings", {}).get(tid_str, {})
    earnings_ton = round(float(earnings_info.get("unclaimed_ton", 0.0)), 2)
    earnings_usd = round(earnings_ton * 5.0, 2)

    if tid not in USER_REFERRALS:
        USER_REFERRALS[tid] = {
            "invited_count": invited_count,
            "referral_earnings_ton": earnings_ton,
            "referral_earnings_usd": earnings_usd,
            "next_claim_available_at": None,
            "last_claim_at": None
        }
    else:
        ref = USER_REFERRALS[tid]
        ref["invited_count"] = invited_count
        now = datetime.datetime.now(datetime.timezone.utc)
        if ref.get("next_claim_available_at"):
            try:
                nxt = datetime.datetime.fromisoformat(ref["next_claim_available_at"].replace("Z", "+00:00"))
                if now >= nxt:
                    ref["next_claim_available_at"] = None
                    ref["referral_earnings_ton"] = earnings_ton
                    ref["referral_earnings_usd"] = earnings_usd
            except Exception:
                pass
        else:
            ref["referral_earnings_ton"] = earnings_ton
            ref["referral_earnings_usd"] = earnings_usd
    return USER_REFERRALS[tid]'''

new_func = '''def get_user_referral(tid):
    global REFERRALS_DATA
    if os.path.exists(REFERRALS_FILE):
        try:
            with open(REFERRALS_FILE, "r", encoding="utf-8") as f:
                REFERRALS_DATA = json.load(f)
        except Exception:
            pass

    tid_str = str(tid)
    invited_list = REFERRALS_DATA.get("referrals", {}).get(tid_str, [])
    invited_count = len(invited_list)

    earnings_info = REFERRALS_DATA.get("earnings", {}).get(tid_str, {})
    earnings_ton = round(float(earnings_info.get("unclaimed_ton", 0.0)), 2)
    earnings_usd = round(earnings_ton * 5.0, 2)

    if tid not in USER_REFERRALS:
        USER_REFERRALS[tid] = {
            "invited_count": invited_count,
            "referral_earnings_ton": earnings_ton,
            "referral_earnings_usd": earnings_usd,
            "next_claim_available_at": None,
            "last_claim_at": None
        }
    else:
        ref = USER_REFERRALS[tid]
        ref["invited_count"] = invited_count
        ref["referral_earnings_ton"] = earnings_ton
        ref["referral_earnings_usd"] = earnings_usd
        now = datetime.datetime.now(datetime.timezone.utc)
        if ref.get("next_claim_available_at"):
            try:
                nxt = datetime.datetime.fromisoformat(ref["next_claim_available_at"].replace("Z", "+00:00"))
                if now >= nxt:
                    ref["next_claim_available_at"] = None
            except Exception:
                pass
    return USER_REFERRALS[tid]'''

if old_func in text:
    text = text.replace(old_func, new_func)
    print("Replaced get_user_referral LF!")
else:
    old_crlf = old_func.replace('\n', '\r\n')
    new_crlf = new_func.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_crlf)
        print("Replaced get_user_referral CRLF!")
    else:
        print("Could not find old_func!")

with open(SERVER_PATH, "w", encoding="utf-8") as f:
    f.write(text)
print("Updated server.py successfully!")
