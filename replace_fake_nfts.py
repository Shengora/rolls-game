import os, sys
sys.stdout.reconfigure(encoding='utf-8')

server_path = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\server.py"
with open(server_path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace STARTER_INVENTORY with authentic Telegram gifts
old_starter = '''STARTER_INVENTORY = [
    {
        "gift_id": "gift_starter_pepe_crown",
        "cost_ton": 50.0,
        "cost_usd": 250.0,
        "lombard_cost_ton": 40.0,
        "title": "Pepe Crown",
        "num": 77,
        "model": "pepe_crown",
        "model_rarity": 3,
        "background": "gold",
        "background_rarity": 3,
        "symbol": "crown",
        "symbol_rarity": 3
    },
    {
        "gift_id": "gift_starter_dog",
        "cost_ton": 25.0,
        "cost_usd": 125.0,
        "lombard_cost_ton": 20.0,
        "title": "Resistance Dog",
        "num": 109,
        "model": "resistance_dog",
        "model_rarity": 2,
        "background": "purple",
        "background_rarity": 2,
        "symbol": "dog",
        "symbol_rarity": 2
    },
    {
        "gift_id": "gift_starter_3",
        "cost_ton": 50.0,
        "cost_usd": 250.0,
        "lombard_cost_ton": 40.0,
        "title": "Pepe Crown",
        "num": 12,
        "model": "pepe_crown",
        "model_rarity": 3,
        "background": "gold",
        "background_rarity": 3,
        "symbol": "crown",
        "symbol_rarity": 3
    }
]'''

new_starter = '''STARTER_INVENTORY = [
    {
        "gift_id": "gift_starter_bonded_ring",
        "cost_ton": 44.0,
        "cost_usd": 220.0,
        "lombard_cost_ton": 35.2,
        "title": "Bonded Ring",
        "num": 77,
        "model": "bondedring",
        "model_rarity": 3,
        "background": "gold",
        "background_rarity": 3,
        "symbol": "ring",
        "symbol_rarity": 3
    },
    {
        "gift_id": "gift_starter_diamond_ring",
        "cost_ton": 37.0,
        "cost_usd": 185.0,
        "lombard_cost_ton": 29.6,
        "title": "Diamond Ring",
        "num": 109,
        "model": "diamondring",
        "model_rarity": 2,
        "background": "purple",
        "background_rarity": 2,
        "symbol": "diamond",
        "symbol_rarity": 2
    },
    {
        "gift_id": "gift_starter_crystal_ball",
        "cost_ton": 15.0,
        "cost_usd": 75.0,
        "lombard_cost_ton": 12.0,
        "title": "Crystal Ball",
        "num": 12,
        "model": "crystalball",
        "model_rarity": 2,
        "background": "cyan",
        "background_rarity": 2,
        "symbol": "ball",
        "symbol_rarity": 2
    }
]'''

if old_starter in code:
    code = code.replace(old_starter, new_starter)
    print("Replaced STARTER_INVENTORY with real Telegram gifts")
else:
    print("Warning: old_starter not matched exactly")

# Replace PRIZES
old_prizes = '''PRIZES = [
    {"id": "lucky_locket", "name": "Lucky Locket", "type": "GIFT", "amount_ton": 15.0, "model": "lucky_locket"},
    {"id": "resistance_dog", "name": "Resistance Dog", "type": "GIFT", "amount_ton": 25.0, "model": "resistance_dog"},
    {"id": "pepe_crown", "name": "Pepe Crown", "type": "GIFT", "amount_ton": 50.0, "model": "pepe_crown"},
    {"id": "star_locket", "name": "Star Locket", "type": "GIFT", "amount_ton": 8.0, "model": "star_locket"},
    {"id": "ton_reward_5", "name": "5 TON", "type": "TON", "amount_ton": 5.0, "model": None},
    {"id": "ton_reward_2", "name": "2 TON", "type": "TON", "amount_ton": 2.0, "model": None},
    {"id": "ton_reward_1", "name": "1 TON", "type": "TON", "amount_ton": 1.0, "model": None}
]'''

new_prizes = '''PRIZES = [
    {"id": "crystal_ball", "name": "Crystal Ball", "type": "GIFT", "amount_ton": 15.0, "model": "crystalball"},
    {"id": "diamond_ring", "name": "Diamond Ring", "type": "GIFT", "amount_ton": 37.0, "model": "diamondring"},
    {"id": "bonded_ring", "name": "Bonded Ring", "type": "GIFT", "amount_ton": 44.0, "model": "bondedring"},
    {"id": "bday_candle", "name": "B-Day Candle", "type": "GIFT", "amount_ton": 6.0, "model": "bdaycandle"},
    {"id": "ton_reward_5", "name": "5 TON", "type": "TON", "amount_ton": 5.0, "model": None},
    {"id": "ton_reward_2", "name": "2 TON", "type": "TON", "amount_ton": 2.0, "model": None},
    {"id": "ton_reward_1", "name": "1 TON", "type": "TON", "amount_ton": 1.0, "model": None}
]'''

if old_prizes in code:
    code = code.replace(old_prizes, new_prizes)
    print("Replaced PRIZES with real Telegram gifts")
else:
    print("Warning: old_prizes not matched exactly")

# Replace UPGRADE_TARGETS
old_target = '''UPGRADE_TARGETS = [
    {
        "type": "MARKET_GIFT",
        "gift_id": "target_pepe_crown",
        "title": "Pepe Crown",
        "price_ton": 50.0,
        "chance_pct": 20.0,
        "gift": {
            "gift_id": "target_pepe_crown",
            "title": "Pepe Crown",
            "cost_ton": 50.0,
            "num": 777,
            "model": "pepe_crown",
            "symbol": "crown",
            "background": "gold",
            "upgradeEligible": False
        }
    }
]'''

new_target = '''UPGRADE_TARGETS = [
    {
        "type": "MARKET_GIFT",
        "gift_id": "target_durovs_glasses",
        "title": "Durov’s Glasses",
        "price_ton": 159.0,
        "chance_pct": 15.0,
        "gift": {
            "gift_id": "target_durovs_glasses",
            "title": "Durov’s Glasses",
            "cost_ton": 159.0,
            "num": 777,
            "model": "durovsglasses",
            "symbol": "glasses",
            "background": "gold",
            "upgradeEligible": False
        }
    }
]'''

if old_target in code:
    code = code.replace(old_target, new_target)
    print("Replaced UPGRADE_TARGETS with real Telegram gift (Durov's Glasses)")
else:
    print("Warning: old_target not matched exactly")

with open(server_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied to server.py!")
