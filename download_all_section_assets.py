import os
import urllib.request

ASSETS = [
    # Staking
    "/assets/staking/glow.svg",
    "/assets/staking/stars-v2.svg",
    "/assets/rewards/staking-object.webp",
    "/assets/staking/glow-title.svg",
    "/assets/staking-earned-24h.webp",
    "/assets/staking/gift.webp",
    # Referral
    "/assets/referral/glow-title.svg",
    "/assets/referral/stars.svg",
    "/assets/referral/glow.svg",
    "/assets/referral/rays.svg",
    "/assets/referral/card-glow-inner.svg",
    "/assets/referral/card-glow-outer.svg",
    # Daily / Redo Tournament
    "/assets/daily/trophy-small.webp",
    "/assets/daily/bg1.webp",
    "/assets/redo-tournament/banner-rays.webp",
    "/assets/redo-tournament/char-gifts-left.webp",
    "/assets/redo-tournament/char-banner-2.webp",
    "/assets/redo-tournament/char-banner-3.webp",
    "/assets/redo-tournament/center.webp",
    "/assets/redo-tournament/char-gifts-right.webp"
]

BASE_URL = "https://app.rolls.codes"
PUBLIC_DIR = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for a in ASSETS:
    target = os.path.join(PUBLIC_DIR, a.lstrip("/").replace("/", os.sep))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    try:
        req = urllib.request.Request(BASE_URL + a, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(target, "wb") as f:
                f.write(data)
            print(f"SUCCESS: {a} ({len(data)} bytes)")
    except Exception as e:
        print(f"FAILED: {a}: {e}")
