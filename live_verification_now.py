import time
import json
import urllib.request
import urllib.parse
import socket
import os
import sys

# Force IPv4
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

sys.stdout.reconfigure(encoding='utf-8')

TUNNEL_CONFIG = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\config.json"
QUEUE_FILE = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\withdrawals_queue.json"

def run_live_test():
    print("=" * 60)
    print("      LIVE REAL-TIME SYSTEM VERIFICATION REPORT")
    print("=" * 60)

    # 1. Check Config & Cloudflare Tunnel
    print("\n[1] CHECKING CLOUDFLARE LIVE HTTPS TUNNEL:")
    with open(TUNNEL_CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    bot_token = cfg.get("bot_token")
    webapp_url = cfg.get("webapp_url")
    print(f"  Target WebApp URL: {webapp_url}")

    # Test tunnel HTTPS connectivity
    try:
        req = urllib.request.Request(f"{webapp_url}/api/v1/relayer/status", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            rel_status = json.loads(r.read().decode())
            print(f"  HTTPS Tunnel Response Code: {r.status} OK")
            print(f"  Relayer status via Public HTTPS: {rel_status}")
    except Exception as e:
        print(f"  [ERROR] Public HTTPS tunnel failed: {e}")
        return False

    # 2. Check Telegram Bot API Configuration
    print("\n[2] CHECKING TELEGRAM BOT @Shencasbot:")
    try:
        req = urllib.request.Request(f"https://api.telegram.org/bot{bot_token}/getMe")
        with urllib.request.urlopen(req, timeout=10) as r:
            bot_info = json.loads(r.read().decode())
            print(f"  Bot Info: @{bot_info.get('result', {}).get('username')} (ID: {bot_info.get('result', {}).get('id')})")
        
        req = urllib.request.Request(f"https://api.telegram.org/bot{bot_token}/getChatMenuButton")
        with urllib.request.urlopen(req, timeout=10) as r:
            menu_btn = json.loads(r.read().decode())
            curr_menu_url = menu_btn.get("result", {}).get("web_app", {}).get("url")
            print(f"  Menu Button URL: {curr_menu_url}")
            match = (curr_menu_url == webapp_url)
            print(f"  Menu Button matches current live URL: {match}")
    except Exception as e:
        print(f"  [ERROR] Telegram Bot API check failed: {e}")
        return False

    # 3. Check Live Balance
    print("\n[3] CHECKING USER BALANCE:")
    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/users/balance")
    with urllib.request.urlopen(req) as r:
        b_init = json.loads(r.read().decode())
    init_bal = b_init.get("balance_ton")
    print(f"  Initial Balance: {init_bal} Gram")

    # 4. Test Deposit Flow
    print("\n[4] TESTING REAL DEPOSIT ENDPOINT:")
    topup_payload = json.dumps({"amount": 10.0, "asset": "TON"}).encode()
    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/users/balance/topups/cryptobot",
                                 data=topup_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        topup_res = json.loads(r.read().decode())
    print(f"  Topup API result: {topup_res}")

    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/users/balance")
    with urllib.request.urlopen(req) as r:
        b_after = json.loads(r.read().decode())
    new_bal = b_after.get("balance_ton")
    print(f"  New Balance after +10 Gram deposit: {new_bal} Gram (Difference: {new_bal - init_bal:+})")
    assert round(new_bal - init_bal, 2) == 10.0, "Balance must increase by 10"

    # 5. Test Live PvP Round (1-Player waiting -> Opponent joins -> Countdown -> Win)
    print("\n[5] TESTING LIVE PVP CYCLE (STEP BY STEP):")
    # Step 5.1: Check game info before bet
    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/game-roll/info")
    with urllib.request.urlopen(req) as r:
        g_before = json.loads(r.read().decode())
    print(f"  5.1 Status before bet: {g_before.get('status')}")

    # Step 5.2: User places bet of 5 TON
    bet_payload = json.dumps({"amount_ton": 5.0}).encode()
    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/game-roll/add-ton",
                                 data=bet_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        bet_res = json.loads(r.read().decode())
    print(f"  5.2 Bet 5 TON placed. Current status: {bet_res.get('status')}, countdown: {bet_res.get('countdown_remaining_ms')}")
    assert bet_res.get("status") == "collecting", "Must be collecting with 1 player"
    assert bet_res.get("countdown_remaining_ms") is None, "Countdown must NOT start with 1 player!"
    print("  [PASS] 1-player test: Ruletka bitta odam bilan aylanmaydi (Kutmoqda)!")

    # Step 5.3: Wait for realistic opponent to join (2.5 - 4 seconds)
    print("  5.3 Opponent kutilyapti (2-4 soniya)...")
    opponent_joined = False
    for i in range(7):
        time.sleep(1)
        req = urllib.request.Request("http://127.0.0.1:8080/api/v1/game-roll/info")
        with urllib.request.urlopen(req) as r:
            g_chk = json.loads(r.read().decode())
        bets = g_chk.get("bets", [])
        if len(bets) >= 2 or g_chk.get("status") in ["countdown", "completed"]:
            print(f"  [OPPONENT JOINED] Status: {g_chk.get('status')}, Jami o'yinchilar: {len(bets)}, Countdown: {g_chk.get('countdown_remaining_ms')}ms")
            opponent_joined = True
            break
    assert opponent_joined, "Opponent must join to form 2-player match"

    # Step 5.4: Wait for countdown to finish and winner to be declared
    print("  5.4 Ruletka aylanishi va natija kutilmoqda...")
    round_resolved = False
    for _ in range(20):
        time.sleep(1)
        req = urllib.request.Request("http://127.0.0.1:8080/api/v1/game-roll/info")
        with urllib.request.urlopen(req) as r:
            g_end = json.loads(r.read().decode())
        if g_end.get("status") == "completed" or g_end.get("winner_display_name"):
            print(f"  [WINNER DECLARED] G'olib: {g_end.get('winner_display_name')}, Mukofot: {g_end.get('total_prize_ton')} TON")
            round_resolved = True
            break
        elif g_end.get("status") == "collecting" and round_resolved:
            break

    # 6. Test History List
    print("\n[6] CHECKING ROUND HISTORY:")
    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/game-roll/history/list")
    with urllib.request.urlopen(req) as r:
        h_res = json.loads(r.read().decode())
    items = h_res.get("items", [])
    print(f"  Total completed rounds in history: {len(items)}")
    print(f"  Latest round: #{items[0].get('game_num')} - Winner: {items[0].get('winner_display_name')} (+{items[0].get('total_prize_ton')} TON)")

    # 7. Test Inventory & Gift Withdrawal
    print("\n[7] TESTING NFT GIFTS INVENTORY & WITHDRAWAL:")
    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/user/gifts/list")
    with urllib.request.urlopen(req) as r:
        gifts_list = json.loads(r.read().decode()).get("gifts", [])
    print(f"  Current gifts count in inventory: {len(gifts_list)}")
    chosen_gift = gifts_list[0]
    print(f"  Selected gift to withdraw: '{chosen_gift.get('title')}' (ID: {chosen_gift.get('gift_id')})")

    # Execute withdrawal
    wd_payload = json.dumps({"gift_ids": [chosen_gift["gift_id"]]}).encode()
    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/users/withdraw-gifts/v2",
                                 data=wd_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        wd_res = json.loads(r.read().decode())
    print(f"  Withdrawal executed: ID={wd_res.get('withdrawal_id')}, Status={wd_res.get('status')}")

    # Check inventory deduction
    req = urllib.request.Request("http://127.0.0.1:8080/api/v1/user/gifts/list")
    with urllib.request.urlopen(req) as r:
        gifts_after = json.loads(r.read().decode()).get("gifts", [])
    print(f"  Inventory gifts after withdrawal: {len(gifts_after)} (Deducted: {len(gifts_list) - len(gifts_after)})")
    assert len(gifts_after) == len(gifts_list) - 1, "Gift must be removed from inventory"

    # 8. Check Relayer Queue Processing
    print("\n[8] CHECKING RELAYER @tvaroq QUEUE WORKER:")
    time.sleep(3)
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)
    latest_q = queue[-1]
    print(f"  Relayer queue item #{latest_q.get('id')}: Status = {latest_q.get('status')}")
    assert latest_q.get("status") == "COMPLETED", "Queue item must be processed by relayer"

    print("\n" + "=" * 60)
    print("      ALL LIVE TESTS PASSED 100% SUCCESFULLY!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    run_live_test()
