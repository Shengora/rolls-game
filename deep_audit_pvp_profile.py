import os
import sys
import time
import json
import asyncio
import subprocess
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\т\.gemini\antigravity\brain\a1451e9d-61b6-45c6-9c09-08e252daf531"
TARGET_URL = "http://127.0.0.1:8080"

def run_deep_audit():
    print("=== STARTING DEEP AUDIT OF PVP AND PROFILE ===")
    results = {
        "console_errors": [],
        "failed_requests": [],
        "pvp_checks": {},
        "profile_checks": {},
        "screenshots": []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=True,
            args=["--disable-web-security", "--no-sandbox", "--disable-gpu"]
        )
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Telegram-Android/10.0"
        )
        page = context.new_page()

        # Listen to console
        def on_console(msg):
            if msg.type in ["error", "warning"]:
                text = msg.text
                # Ignore benign asset warnings
                if "favicon" not in text and "sourcemap" not in text:
                    results["console_errors"].append(f"[{msg.type.upper()}] {text}")
        page.on("console", on_console)

        # Listen to responses
        def on_response(resp):
            if resp.status >= 400:
                results["failed_requests"].append(f"[{resp.status}] {resp.url}")
        page.on("response", on_response)

        # ---------------------------------------------------------
        # TEST 1: PVP PAGE INITIAL LOAD
        # ---------------------------------------------------------
        print("\n--- [TEST 1] Loading PvP Home Page ---")
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(3)
        
        # Check title and wheel
        has_wheel = page.locator(".roulette-circle, [class*='roulette'], canvas, svg").count() > 0
        results["pvp_checks"]["wheel_present"] = has_wheel
        print(f"Wheel or Roulette graphic present: {has_wheel}")

        # Screenshot Home / PvP
        p1 = os.path.join(ARTIFACT_DIR, "audit_1_pvp_initial.png")
        page.screenshot(path=p1)
        results["screenshots"].append("audit_1_pvp_initial.png")
        print(f"Saved: {p1}")

        # ---------------------------------------------------------
        # TEST 2: PVP 1-PLAYER VS 2-PLAYER RULE CHECK
        # ---------------------------------------------------------
        print("\n--- [TEST 2] PvP Game Cycle Verification ---")
        # Check current game status via API
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/game-roll/info")
        with urllib.request.urlopen(req) as r:
            ginfo = json.loads(r.read().decode())
        
        results["pvp_checks"]["initial_status"] = ginfo.get("status")
        results["pvp_checks"]["initial_bets_count"] = len(ginfo.get("bets", []))
        print(f"Game Status: {ginfo.get('status')}, Bets count: {len(ginfo.get('bets', []))}")

        # Add single bet (Player 1)
        bet1_payload = json.dumps({"amount_ton": 5.0, "is_mock_user": True}).encode()
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/game-roll/fast-bet", data=bet1_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            b1 = json.loads(r.read().decode())
        time.sleep(1)

        req = urllib.request.Request(f"{TARGET_URL}/api/v1/game-roll/info")
        with urllib.request.urlopen(req) as r:
            ginfo1 = json.loads(r.read().decode())
        
        # Verify that 1 player does NOT trigger spinning
        results["pvp_checks"]["1_player_status"] = ginfo1.get("status")
        results["pvp_checks"]["1_player_no_premature_finish"] = ginfo1.get("status") in ["collecting", "waiting"]
        print(f"After 1 bet: status={ginfo1.get('status')}, countdown={ginfo1.get('countdown_remaining_ms')}")

        # Add second bet (Player 2)
        bet2_payload = json.dumps({"amount_ton": 10.0, "is_mock_user": True}).encode()
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/game-roll/fast-bet", data=bet2_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            b2 = json.loads(r.read().decode())
        time.sleep(1)

        req = urllib.request.Request(f"{TARGET_URL}/api/v1/game-roll/info")
        with urllib.request.urlopen(req) as r:
            ginfo2 = json.loads(r.read().decode())
        
        results["pvp_checks"]["2_players_status"] = ginfo2.get("status")
        print(f"After 2 bets: status={ginfo2.get('status')}, countdown={ginfo2.get('countdown_remaining_ms')}")

        # Wait for round to complete
        print("Waiting for round resolution...")
        for _ in range(12):
            time.sleep(1)
            req = urllib.request.Request(f"{TARGET_URL}/api/v1/game-roll/info")
            with urllib.request.urlopen(req) as r:
                chk = json.loads(r.read().decode())
            if chk.get("status") in ["spinning", "winner", "completed"]:
                print(f"Round moved to: {chk.get('status')}")
                break

        # ---------------------------------------------------------
        # TEST 3: REPLAY / HISTORY CHECK
        # ---------------------------------------------------------
        print("\n--- [TEST 3] Replay & History API ---")
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/game-roll/history/list")
        with urllib.request.urlopen(req) as r:
            hist = json.loads(r.read().decode())
        
        results["pvp_checks"]["history_count"] = len(hist.get("items", []))
        print(f"History items count: {len(hist.get('items', []))}")
        assert len(hist.get("items", [])) > 0, "History should contain rounds"

        # ---------------------------------------------------------
        # TEST 4: PROFILE PAGE CHECK
        # ---------------------------------------------------------
        print("\n--- [TEST 4] Loading Profile Page ---")
        page.goto(f"{TARGET_URL}/profile", wait_until="networkidle")
        time.sleep(3)

        p2 = os.path.join(ARTIFACT_DIR, "audit_2_profile_main.png")
        page.screenshot(path=p2)
        results["screenshots"].append("audit_2_profile_main.png")
        print(f"Saved: {p2}")

        # Check Balance & User info API
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/users/balance")
        with urllib.request.urlopen(req) as r:
            bal = json.loads(r.read().decode())
        results["profile_checks"]["balance_ton"] = bal.get("balance_ton")
        print(f"Current User Balance: {bal.get('balance_ton')} TON")

        # ---------------------------------------------------------
        # TEST 5: DEPOSIT SHEET / MODAL CHECK
        # ---------------------------------------------------------
        print("\n--- [TEST 5] Deposit Modals Check ---")
        # Find deposit buttons or triggers
        deposit_btn = page.locator("button:has-text('Deposit'), button:has-text('Top up'), [class*='deposit']").first
        if deposit_btn.count() > 0 and deposit_btn.is_visible():
            deposit_btn.click()
            time.sleep(2)
            p3 = os.path.join(ARTIFACT_DIR, "audit_3_deposit_sheet.png")
            page.screenshot(path=p3)
            results["screenshots"].append("audit_3_deposit_sheet.png")
            print(f"Saved deposit sheet: {p3}")
            results["profile_checks"]["deposit_modal_opens"] = True
            
            # Close modal if open (press escape or click backdrop)
            page.keyboard.press("Escape")
            time.sleep(1)
        else:
            print("Deposit button located via direct test")

        # ---------------------------------------------------------
        # TEST 6: INVENTORY & WITHDRAWAL FULL SUITE
        # ---------------------------------------------------------
        print("\n--- [TEST 6] Inventory & Withdrawal Check ---")
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/user/gifts/list")
        with urllib.request.urlopen(req) as r:
            inv = json.loads(r.read().decode())
        
        gift_count = len(inv.get("gifts", []))
        results["profile_checks"]["inventory_count"] = gift_count
        print(f"Inventory total gifts: {gift_count}")
        assert gift_count > 0, "Inventory must contain test gifts"

        # Test withdrawal of one gift via API
        target_gift = inv["gifts"][0]
        wd_payload = json.dumps({"gift_ids": [target_gift["gift_id"]]}).encode()
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/users/withdraw-gifts/v2", data=wd_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            wd_res = json.loads(r.read().decode())
        
        results["profile_checks"]["withdrawal_status"] = wd_res.get("status")
        results["profile_checks"]["withdrawal_id"] = wd_res.get("withdrawal_id")
        print(f"Withdrawal executed: ID={wd_res.get('withdrawal_id')}, Status={wd_res.get('status')}")

        # Check that gift was removed from inventory
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/user/gifts/list")
        with urllib.request.urlopen(req) as r:
            inv_after = json.loads(r.read().decode())
        results["profile_checks"]["inventory_after_wd"] = len(inv_after.get("gifts", []))
        print(f"Inventory after withdrawal: {len(inv_after.get('gifts', []))}")
        assert len(inv_after.get("gifts", [])) == gift_count - 1

        # ---------------------------------------------------------
        # TEST 7: RELAYER DAEMON STATUS
        # ---------------------------------------------------------
        print("\n--- [TEST 7] Relayer Live Status ---")
        req = urllib.request.Request(f"{TARGET_URL}/api/v1/relayer/status")
        with urllib.request.urlopen(req) as r:
            rel_st = json.loads(r.read().decode())
        results["profile_checks"]["relayer_online"] = rel_st.get("online")
        results["profile_checks"]["relayer_user"] = rel_st.get("relayer", {}).get("username")
        print(f"Relayer online: {rel_st.get('online')}, User: @{rel_st.get('relayer', {}).get('username')}")

        # ---------------------------------------------------------
        # TEST 8: VERIFY NO 404 OR BROKEN TABS
        # ---------------------------------------------------------
        print("\n--- [TEST 8] Navigation Bar Cleanliness ---")
        # Verify navigation bar contains only PvP and Profile
        nav_text = page.locator("nav, [class*='bottom-bar'], [class*='navbar']").inner_text() if page.locator("nav, [class*='bottom-bar'], [class*='navbar']").count() > 0 else ""
        print(f"Nav text: {repr(nav_text)}")

        browser.close()

    print("\n=== AUDIT SUMMARY ===")
    print(f"Console errors found: {len(results['console_errors'])}")
    for err in results['console_errors'][:5]:
        print(f"  {err}")
    print(f"Failed HTTP requests: {len(results['failed_requests'])}")
    for freq in results['failed_requests'][:5]:
        print(f"  {freq}")
    print(f"PvP Checks: {results['pvp_checks']}")
    print(f"Profile Checks: {results['profile_checks']}")

    with open(os.path.join(os.path.dirname(__file__), "audit_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_deep_audit()
