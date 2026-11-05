import urllib.request
import os

ASSETS = [
    # Profile
    "/assets/profile/wallet.svg",
    "/assets/profile/stat-total-games.webp",
    "/assets/profile/row-inventory.webp",
    "/assets/profile/stat-best-win.webp",
    "/assets/profile/row-stakings.webp",
    "/assets/profile/row-lombard.webp",
    "/assets/profile/row-referrals.webp",
    "/assets/crash/settings.svg",
    # Solo
    "/assets/solo/cases-card.webp",
    "/assets/solo/crash-card.webp",
    "/assets/solo/lucky-card.webp",
    "/assets/solo/mono-card.webp",
    "/assets/solo/hi-lo-card_v2.webp",
    "/assets/solo/limbo-card.webp",
    "/assets/solo/custom-rolls-card.webp",
    "/assets/solo/giveaways-tile/gift.webp",
    "/assets/solo/giveaways-tile/light-1.svg",
    "/assets/solo/giveaways-tile/light-2.svg",
    "/assets/solo/giveaways-tile/light-3.svg",
    "/assets/solo/giveaways-tile/light-4-overlay.svg",
    "/assets/solo/giveaways-tile/rays.svg",
    "/assets/solo/giveaways-tile/sparkles-overlay.svg"
]

BASE_URL = "https://app.rolls.codes"
PUBLIC_DIR = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for asset in ASSETS:
    target_path = os.path.join(PUBLIC_DIR, asset.lstrip("/").replace("/", os.sep))
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    url = BASE_URL + asset
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(target_path, "wb") as f:
                f.write(data)
            print(f"Downloaded: {asset} ({len(data)} bytes)")
    except Exception as e:
        print(f"Failed {asset}: {e}")
