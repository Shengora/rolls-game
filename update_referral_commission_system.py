import re
import json
import os

SERVER_PATH = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\server.py"
REFERRALS_PATH = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\referrals.json"

# 1. Update referrals.json if needed
if os.path.exists(REFERRALS_PATH):
    with open(REFERRALS_PATH, "r", encoding="utf-8") as f:
        ref_data = json.load(f)
    if "earnings" not in ref_data:
        ref_data["earnings"] = {}
    with open(REFERRALS_PATH, "w", encoding="utf-8") as f:
        json.dump(ref_data, f, indent=2, ensure_ascii=False)
    print("referrals.json updated with 'earnings' section.")

with open(SERVER_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# 2. Add distribute_referral_commission and update get_user_referral
old_get_user_referral = '''def get_user_referral(tid):
    tid_str = str(tid)
    invited_list = REFERRALS_DATA.get("referrals", {}).get(tid_str, [])
    invited_count = len(invited_list)
    unclaimed = [r for r in invited_list if not r.get("reward_claimed", False)]
    unclaimed_count = len(unclaimed)
    earnings_ton = round(unclaimed_count * 2.5, 2)
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

new_distribute_and_get_referral = '''def distribute_referral_commission(winner_tid, win_amount_ton, commission_ton=None, game_name="PvP Roulette"):
    """
    Referral Commission System:
    When a referred friend wins in a game (e.g. 100 TON), casino takes 10% commission (10 TON).
    10% of that taken commission (1.0 TON) is credited to the inviter who invited that friend.
    """
    if win_amount_ton <= 0:
        return 0.0
    w_str = str(winner_tid)
    inviter_str = REFERRALS_DATA.get("invited_by", {}).get(w_str)
    if not inviter_str:
        return 0.0

    if commission_ton is None:
        commission_ton = round(win_amount_ton * 0.10, 2)
        
    reward_ton = round(commission_ton * 0.10, 2)
    if reward_ton <= 0 and commission_ton > 0:
        reward_ton = 0.01

    if "earnings" not in REFERRALS_DATA:
        REFERRALS_DATA["earnings"] = {}
    if inviter_str not in REFERRALS_DATA["earnings"]:
        REFERRALS_DATA["earnings"][inviter_str] = {
            "unclaimed_ton": 0.0,
            "total_earned_ton": 0.0,
            "history": []
        }

    ref_entry = REFERRALS_DATA["earnings"][inviter_str]
    ref_entry["unclaimed_ton"] = round(ref_entry.get("unclaimed_ton", 0.0) + reward_ton, 2)
    ref_entry["total_earned_ton"] = round(ref_entry.get("total_earned_ton", 0.0) + reward_ton, 2)
    ref_entry.setdefault("history", []).append({
        "friend_id": winner_tid,
        "game": game_name,
        "win_ton": round(win_amount_ton, 2),
        "commission_ton": round(commission_ton, 2),
        "reward_ton": reward_ton,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })
    save_referrals_data(REFERRALS_DATA)

    try:
        inv_tid = int(inviter_str)
        if inv_tid in USER_REFERRALS:
            USER_REFERRALS[inv_tid]["referral_earnings_ton"] = ref_entry["unclaimed_ton"]
            USER_REFERRALS[inv_tid]["referral_earnings_usd"] = round(ref_entry["unclaimed_ton"] * 5.0, 2)
    except Exception:
        pass

    print(f"[Referral Commission] Inviter {inviter_str} awarded {reward_ton} TON (10% of {commission_ton} TON commission) from friend {winner_tid} win in {game_name}!")
    return reward_ton

def get_user_referral(tid):
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

if old_get_user_referral in text:
    text = text.replace(old_get_user_referral, new_distribute_and_get_referral)
    print("Replaced get_user_referral with commission-based system!")
else:
    print("Target old_get_user_referral not found directly, checking CRLF...")
    old_crlf = old_get_user_referral.replace('\n', '\r\n')
    new_crlf = new_distribute_and_get_referral.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_crlf)
        print("Replaced get_user_referral CRLF successfully!")
    else:
        print("ERROR: old_get_user_referral not found!")

# 3. Update PurePvPEngine.update_cycle to take 10% commission and call distribute_referral_commission
old_payout = '''                        ton_in_pot = sum(b["amount_ton"] for b in self.bets)
                        stars_in_pot = sum(b.get("amount_stars", 0) for b in self.bets)
                        self.winner_ton_award = round(ton_in_pot, 2)

                        if not winner["is_opponent"]:
                            w_tid = winner["user_id"]
                            set_user_balance(w_tid, get_user_balance(w_tid) + ton_in_pot)
                            if stars_in_pot > 0:
                                set_user_stars(w_tid, get_user_stars(w_tid) + stars_in_pot)
                            w_inv = get_user_inventory(w_tid)
                            for g in all_gifts_in_pot:
                                w_inv.append(g)
                            w_stats = get_user_stats(w_tid)
                            w_stats["total_games"] += 1
                            w_stats["best_win_ton"] = max(w_stats["best_win_ton"], total_pot)
                        else:
                            for rp in real_players:
                                rp_stats = get_user_stats(rp["user_id"])
                                rp_stats["total_games"] += 1'''

new_payout = '''                        ton_in_pot = sum(b["amount_ton"] for b in self.bets)
                        stars_in_pot = sum(b.get("amount_stars", 0) for b in self.bets)

                        # 10% Casino house commission on pot
                        commission_ton = round(total_pot * 0.10, 2)
                        ton_commission = round(ton_in_pot * 0.10, 2)
                        net_ton = max(0.0, round(ton_in_pot - ton_commission, 2))
                        self.winner_ton_award = net_ton

                        w_tid = winner["user_id"]
                        if not winner["is_opponent"]:
                            set_user_balance(w_tid, get_user_balance(w_tid) + net_ton)
                            if stars_in_pot > 0:
                                set_user_stars(w_tid, get_user_stars(w_tid) + stars_in_pot)
                            w_inv = get_user_inventory(w_tid)
                            for g in all_gifts_in_pot:
                                w_inv.append(g)
                            w_stats = get_user_stats(w_tid)
                            w_stats["total_games"] += 1
                            w_stats["best_win_ton"] = max(w_stats["best_win_ton"], total_pot)
                        else:
                            for rp in real_players:
                                rp_stats = get_user_stats(rp["user_id"])
                                rp_stats["total_games"] += 1

                        # Distribute 10% of commission to the inviter who invited the winner
                        distribute_referral_commission(w_tid, total_pot, commission_ton, game_name=f"{self.game_type} PvP")'''

if old_payout in text:
    text = text.replace(old_payout, new_payout)
    print("Updated PurePvPEngine payout with 10% commission & referral reward!")
else:
    old_p_crlf = old_payout.replace('\n', '\r\n')
    new_p_crlf = new_payout.replace('\n', '\r\n')
    if old_p_crlf in text:
        text = text.replace(old_p_crlf, new_p_crlf)
        print("Updated PurePvPEngine payout CRLF successfully!")
    else:
        print("ERROR: old_payout not found in PurePvPEngine!")

# 4. Update referral claim handler
old_claim = '''            earned = ref["referral_earnings_ton"]
            set_user_balance(tid, get_user_balance(tid) + earned)
            tid_str = str(tid)
            for r in REFERRALS_DATA.get("referrals", {}).get(tid_str, []):
                r["reward_claimed"] = True
            save_referrals_data(REFERRALS_DATA)
            ref["referral_earnings_ton"] = 0.0'''

new_claim = '''            earned = ref["referral_earnings_ton"]
            set_user_balance(tid, get_user_balance(tid) + earned)
            tid_str = str(tid)
            if "earnings" in REFERRALS_DATA and tid_str in REFERRALS_DATA["earnings"]:
                REFERRALS_DATA["earnings"][tid_str]["unclaimed_ton"] = 0.0
                save_referrals_data(REFERRALS_DATA)
            ref["referral_earnings_ton"] = 0.0'''

if old_claim in text:
    text = text.replace(old_claim, new_claim)
    print("Updated referral claim endpoint!")
else:
    old_c_crlf = old_claim.replace('\n', '\r\n')
    new_c_crlf = new_claim.replace('\n', '\r\n')
    if old_c_crlf in text:
        text = text.replace(old_c_crlf, new_c_crlf)
        print("Updated referral claim endpoint CRLF successfully!")
    else:
        print("ERROR: old_claim not found in server.py!")

with open(SERVER_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print("All referral commission patches written successfully to server.py!")
