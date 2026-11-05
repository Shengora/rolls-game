import hashlib
import os
import json
import time
import random
import datetime
import threading
import urllib.parse
from market_price_engine import get_nft_lowest_floor
from cryptopay_integration import create_crypto_invoice, check_paid_invoices
from ton_wallet_integration import get_project_wallet, check_incoming_blockchain_transactions
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

CURRENT_USER = {
    "telegram_id": 999999999,
    "display_name": "Rolls Player",
    "telegram_username": "player",
    "image_url": "https://telegram.org/img/t_logo.png"
}

def make_history_game(game_num, winner_tid, winner_name, total_ton, time_offset_sec=60, win_chance=100.0, game_type="NORMAL", gifts=None, opp_tid=None, opp_name=None, opp_ton=0.0):
    t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=time_offset_sec)
    t_iso = t.isoformat()
    tid_str = str(winner_tid)
    winner_ton = round(total_ton - opp_ton, 2) if opp_tid else total_ton

    gifts_list = gifts or []
    gift_ids = [g["gift_id"] for g in gifts_list]

    currency_bets = {
        tid_str: {
            "TON": {
                "currency": "TON",
                "amount_ton": float(winner_ton),
                "amount_units": 0,
                "last_updated_at": t_iso
            }
        }
    }

    gifts_by_tid = {
        tid_str: {
            "gifts": gifts_list,
            "total_cost_ton": float(winner_ton),
            "total_cost_usd": float(winner_ton * 5.0),
            "user_display_name": winner_name,
            "win_chance_percent": float(win_chance),
            "has_dragon": False
        }
    }

    bets_hist = [
        {
            "timestamp": t_iso,
            "user_telegram_id": winner_tid,
            "user_display_name": winner_name,
            "bet_type": "CURRENCY",
            "amount_ton": float(winner_ton),
            "currency": "TON",
            "amount_units": 0,
            "item_ids": gift_ids,
            "ledger_id": None
        }
    ]

    if opp_tid and opp_name:
        opp_str = str(opp_tid)
        opp_chance = round(100.0 - win_chance, 1)
        currency_bets[opp_str] = {
            "TON": {
                "currency": "TON",
                "amount_ton": float(opp_ton),
                "amount_units": 0,
                "last_updated_at": t_iso
            }
        }
        gifts_by_tid[opp_str] = {
            "gifts": [],
            "total_cost_ton": float(opp_ton),
            "total_cost_usd": float(opp_ton * 5.0),
            "user_display_name": opp_name,
            "win_chance_percent": float(opp_chance),
            "has_dragon": False
        }
        bets_hist.insert(0, {
            "timestamp": t_iso,
            "user_telegram_id": opp_tid,
            "user_display_name": opp_name,
            "bet_type": "CURRENCY",
            "amount_ton": float(opp_ton),
            "currency": "TON",
            "amount_units": 0,
            "item_ids": [],
            "ledger_id": None
        })

    return {
        "id": f"game_roll_{game_num}",
        "type": game_type,
        "game_num": game_num,
        "status": "completed",
        "is_elimination_phase": False,
        "winner_telegram_id": winner_tid,
        "winner_display_name": winner_name,
        "countdown_start_time": None,
        "countdown_remaining_ms": None,
        "time_until_next_game_start_ms": None,
        "winner_gift_ids": gift_ids,
        "winner_token_ids": [],
        "winner_ton_award_ton": float(total_ton),
        "total_prize_ton": float(total_ton),
        "total_prize_usd": float(total_ton * 5.0),
        "countdown_duration_ms": 15000,
        "created_at": t_iso,
        "updated_at": t_iso,
        "previous_roll_game_id": f"game_roll_{game_num - 1}",
        "github_verify_link": "https://github.com",
        "extra_prize_gifts": [],
        "extra_prize_gift_ids": [],
        "extra_prize_gifts_info": {},
        "commission_change_gifts_info": {},
        "next_round_total_prize_ton": None,
        "scheduled_start_time": None,
        "last_reactions": [],
        "bets_history": bets_hist,
        "currency_bets_by_telegram_id": currency_bets,
        "gifts_by_telegram_id": gifts_by_tid,
        "hash": "d3b07384d113edec49eaa6238ad5ff00b7e52a912061e86dbfa66847a98ec21",
        "seed": "d82f7162e080447387405108bb68b3e8e7a030c5e7b25916053f31920ac34cf",
        "bets_map": None
    }

ATH_GAME_DATA = {
    "id": "game_roll_1420",
    "type": "NORMAL",
    "game_num": 1420,
    "status": "completed",
    "is_elimination_phase": False,
    "winner_telegram_id": 1001002,
    "winner_display_name": "CryptoWhale",
    "winner_gift_ids": ["gift_pepe_crown_ath", "gift_resistance_dog_ath"],
    "winner_token_ids": [],
    "winner_ton_award_ton": 1250.0,
    "total_prize_ton": 1250.0,
    "total_prize_usd": 6250.0,
    "countdown_duration_ms": 15000,
    "time_until_next_game_start_ms": 120000,
    "countdown_start_time": None,
    "countdown_remaining_ms": None,
    "created_at": "2026-10-28T16:42:00Z",
    "updated_at": "2026-10-28T16:42:15Z",
    "previous_roll_game_id": "game_roll_1419",
    "github_verify_link": "https://github.com",
    "extra_prize_gifts": [],
    "extra_prize_gift_ids": [],
    "extra_prize_gifts_info": {},
    "commission_change_gifts_info": {},
    "next_round_total_prize_ton": None,
    "scheduled_start_time": None,
    "last_reactions": [],
    "hash": "d3b07384d113edec49eaa6238ad5ff00b7e52a912061e86dbfa66847a98ec21",
    "seed": "d82f7162e080447387405108bb68b3e8e7a030c5e7b25916053f31920ac34cf",
    "bets_map": None,
    "bets_history": [
        {
            "timestamp": "2026-10-28T16:42:02Z",
            "user_telegram_id": 1001003,
            "user_display_name": "DiamondHands",
            "bet_type": "CURRENCY",
            "amount_ton": 768.5,
            "currency": "TON",
            "amount_units": 0,
            "item_ids": [],
            "ledger_id": None
        },
        {
            "timestamp": "2026-10-28T16:42:08Z",
            "user_telegram_id": 1001002,
            "user_display_name": "CryptoWhale",
            "bet_type": "CURRENCY",
            "amount_ton": 481.5,
            "currency": "TON",
            "amount_units": 0,
            "item_ids": ["gift_pepe_crown_ath", "gift_resistance_dog_ath"],
            "ledger_id": None
        }
    ],
    "currency_bets_by_telegram_id": {
        "1001002": {
            "TON": {
                "currency": "TON",
                "amount_ton": 481.5,
                "amount_units": 0,
                "last_updated_at": "2026-10-28T16:42:08Z"
            }
        },
        "1001003": {
            "TON": {
                "currency": "TON",
                "amount_ton": 768.5,
                "amount_units": 0,
                "last_updated_at": "2026-10-28T16:42:02Z"
            }
        }
    },
    "gifts_by_telegram_id": {
        "1001002": {
            "gifts": [
                {
                    "gift_id": "gift_pepe_crown_ath",
                    "cost_ton": 150.0,
                    "cost_usd": 750.0,
                    "title": "Bonded Ring",
                    "num": 420,
                    "model": "bondedring",
                    "model_rarity": 3,
                    "background": "gold",
                    "background_rarity": 3,
                    "symbol": "crown",
                    "symbol_rarity": 3
                },
                {
                    "gift_id": "gift_resistance_dog_ath",
                    "cost_ton": 80.0,
                    "cost_usd": 400.0,
                    "title": "Diamond Ring",
                    "num": 99,
                    "model": "diamondring",
                    "model_rarity": 2,
                    "background": "purple",
                    "background_rarity": 2,
                    "symbol": "dog",
                    "symbol_rarity": 2
                }
            ],
            "total_cost_ton": 481.5,
            "total_cost_usd": 2407.5,
            "user_display_name": "CryptoWhale",
            "win_chance_percent": 38.5,
            "has_dragon": False
        },
        "1001003": {
            "gifts": [],
            "total_cost_ton": 768.5,
            "total_cost_usd": 3842.5,
            "user_display_name": "DiamondHands",
            "win_chance_percent": 61.5,
            "has_dragon": False
        }
    }
}

RECENT_HISTORY = [
    make_history_game(1520, CURRENT_USER["telegram_id"], CURRENT_USER["display_name"], 35.0, 30, 58.0, opp_tid=1001001, opp_name="Sardor (TON)", opp_ton=15.0),
    make_history_game(1519, 1001005, "LuckyStar", 210.0, 120, 14.5, opp_tid=1001002, opp_name="CryptoWhale", opp_ton=179.5),
    make_history_game(1518, 1001002, "CryptoWhale", 48.0, 240, 52.0, opp_tid=1001004, opp_name="MoonWalker", opp_ton=23.0),
    make_history_game(1517, CURRENT_USER["telegram_id"], CURRENT_USER["display_name"], 520.0, 480, 42.0, game_type="GRAND", opp_tid=1001003, opp_name="DiamondHands", opp_ton=301.6),
    make_history_game(1516, 1001001, "Sardor (TON)", 18.0, 720, 60.0, opp_tid=1001005, opp_name="LuckyStar", opp_ton=7.2),
    make_history_game(1515, 1001006, "PepeLover", 95.0, 1100, 5.1, opp_tid=1001002, opp_name="CryptoWhale", opp_ton=90.1),
    make_history_game(1514, CURRENT_USER["telegram_id"], CURRENT_USER["display_name"], 85.0, 1500, 71.0, opp_tid=1001004, opp_name="MoonWalker", opp_ton=24.6),
    make_history_game(1513, 1001007, "TON_King", 850.0, 2200, 54.2, game_type="GRAND", opp_tid=1001003, opp_name="DiamondHands", opp_ton=389.3),
    make_history_game(1512, 1001008, "LuckyNoob", 180.0, 3600, 2.4, opp_tid=1001007, opp_name="TON_King", opp_ton=175.7),
    make_history_game(1511, 1001009, "WhaleWatcher", 340.0, 5000, 28.6, opp_tid=1001001, opp_name="Sardor (TON)", opp_ton=242.8),
    ATH_GAME_DATA
]

STARTER_INVENTORY = [
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
]

USER_BALANCES = {}
USER_STARS = {}
USER_INVENTORIES = {}
USER_STATS = {}
USER_REFERRALS = {}
USER_STAKING = {}
USER_EVENT_STAKING = {}
USER_TOPUPS = {}
USER_CONNECTED_WALLETS = {}
USERS_REGISTRY = {}

def get_user_balance(tid):
    if tid not in USER_BALANCES:
        USER_BALANCES[tid] = 150.0
    return USER_BALANCES[tid]

def set_user_balance(tid, val):
    USER_BALANCES[tid] = max(0.0, round(float(val), 2))
    USER_STATE["balance_ton"] = USER_BALANCES[tid]

def get_user_stars(tid):
    if tid not in USER_STARS:
        USER_STARS[tid] = 500
    return USER_STARS[tid]

def set_user_stars(tid, val):
    USER_STARS[tid] = max(0, int(val))
    USER_STATE["balance_stars"] = USER_STARS[tid]

def get_user_inventory(tid):
    if tid not in USER_INVENTORIES:
        USER_INVENTORIES[tid] = [g.copy() for g in STARTER_INVENTORY]
    # Update with real lowest floor price in Gram from Fragment / see.tg indexer
    for g in USER_INVENTORIES[tid]:
        try:
            live_price, _ = get_nft_lowest_floor(title=g.get("title", ""), model=g.get("model", ""), collection=g.get("title", ""))
            if live_price and live_price > 0:
                g["cost_ton"] = round(float(live_price), 2)
                g["cost_usd"] = round(g["cost_ton"] * 5.0, 2)
                g["lombard_cost_ton"] = round(g["cost_ton"] * 0.8, 2)
        except Exception:
            pass
    return USER_INVENTORIES[tid]

def get_user_stats(tid):
    if tid not in USER_STATS:
        USER_STATS[tid] = {
            "total_games": 24,
            "best_win_ton": 35.0,
            "lombard_total_ton": 0.0
        }
    return USER_STATS[tid]

REFERRALS_FILE = os.path.join(BASE_DIR, "referrals.json")
ADMIN_HTML_PATH = os.path.join(BASE_DIR, "admin.html")
PRICES_CONFIG_PATH = os.path.join(BASE_DIR, "gift_prices.json")

def load_admin_prices():
    if os.path.exists(PRICES_CONFIG_PATH):
        try:
            with open(PRICES_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "stars_per_ton": 50.0,
        "unique_gifts": {
            "pepe_crown": 50.0,
            "resistance_dog": 25.0,
            "plush_pepe": 75.0,
            "lucky_locket": 15.0,
            "telegram_gift": 30.0
        },
        "casino_commission_percent": 10.0,
        "referral_share_of_commission_percent": 10.0
    }

def save_admin_prices(data):
    try:
        with open(PRICES_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print("[Admin] Save prices error:", e)
        return False


def load_referrals_data():
    if os.path.exists(REFERRALS_FILE):
        try:
            with open(REFERRALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Initial realistic seed: nostole was invited by Shen
    default_data = {
        "referrals": {
            "6644911092": [
                {
                    "user_id": 8237158801,
                    "display_name": "nostole",
                    "username": "nostole",
                    "joined_at": "2026-10-30T10:00:00Z",
                    "reward_claimed": False
                }
            ]
        },
        "invited_by": {
            "8237158801": "6644911092"
        }
    }
    try:
        with open(REFERRALS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    return default_data

def save_referrals_data(data):
    try:
        with open(REFERRALS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("[Referrals] Save error:", e)

REFERRALS_DATA = load_referrals_data()

def register_referral(inviter_id, new_user_id, display_name="Friend", username="friend"):
    if not inviter_id or not new_user_id:
        return False
    inviter_str = str(inviter_id).replace("ref_", "").strip()
    new_str = str(new_user_id).replace("ref_", "").strip()
    if not inviter_str.isdigit() or not new_str.isdigit():
        return False
    if inviter_str == new_str:
        return False
    if new_str in REFERRALS_DATA.get("invited_by", {}):
        return False
    
    if "invited_by" not in REFERRALS_DATA:
        REFERRALS_DATA["invited_by"] = {}
    if "referrals" not in REFERRALS_DATA:
        REFERRALS_DATA["referrals"] = {}
        
    REFERRALS_DATA["invited_by"][new_str] = inviter_str
    if inviter_str not in REFERRALS_DATA["referrals"]:
        REFERRALS_DATA["referrals"][inviter_str] = []
        
    if not any(r.get("user_id") == int(new_str) for r in REFERRALS_DATA["referrals"][inviter_str]):
        REFERRALS_DATA["referrals"][inviter_str].append({
            "user_id": int(new_str),
            "display_name": display_name,
            "username": username,
            "joined_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "reward_claimed": False
        })
        save_referrals_data(REFERRALS_DATA)
        print(f"[Referrals] User {new_str} registered under inviter {inviter_str}!")
        return True
    return False

def distribute_referral_commission(winner_tid, win_amount_ton, commission_ton=None, game_name="PvP Roulette"):
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
    return USER_REFERRALS[tid]

def get_user_staking(tid):
    inv = get_user_inventory(tid)
    inv_ton = round(float(sum(g.get("cost_ton", 0.0) for g in inv)), 2)
    inv_usd = round(inv_ton * 5.0, 2)

    if tid not in USER_STAKING:
        limit_ton = 500.0
        eff_ton = min(inv_ton, limit_ton)
        daily_reward = round(eff_ton * 0.45 / 365.0, 2)
        initial_rewards = daily_reward if daily_reward > 0 else (2.5 if eff_ton > 0 else 0.0)
        USER_STAKING[tid] = {
            "total_inventory_ton": inv_ton,
            "total_inventory_usd": inv_usd,
            "staking_rewards_ton": initial_rewards,
            "staking_rewards_usd": round(initial_rewards * 5.0, 2),
            "total_earned": 2.5,
            "earned_24h": daily_reward,
            "earned_today": daily_reward,
            "leaderboard_rank": 2,
            "apr": 45.0,
            "staking_limit_ton": limit_ton,
            "staking_limit_step_ton": 10.0,
            "effective_inventory_ton": eff_ton,
            "effective_inventory_usd": round(eff_ton * 5.0, 2),
            "games_since_last_payout": 4,
            "games_needed_to_cover_inventory": 10,
            "next_update_at": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=6)).isoformat(),
            "next_claim_available_at": None,
            "last_claim_at": None
        }
    else:
        stk = USER_STAKING[tid]
        limit_ton = stk.get("staking_limit_ton", 500.0)
        eff_ton = min(inv_ton, limit_ton)
        daily_reward = round(eff_ton * 0.45 / 365.0, 2)
        stk["total_inventory_ton"] = inv_ton
        stk["total_inventory_usd"] = inv_usd
        stk["effective_inventory_ton"] = eff_ton
        stk["effective_inventory_usd"] = round(eff_ton * 5.0, 2)
        stk["earned_24h"] = daily_reward
        stk["earned_today"] = daily_reward
        now = datetime.datetime.now(datetime.timezone.utc)
        if stk.get("next_claim_available_at"):
            try:
                nxt = datetime.datetime.fromisoformat(stk["next_claim_available_at"].replace("Z", "+00:00"))
                if now >= nxt:
                    stk["next_claim_available_at"] = None
                    stk["staking_rewards_ton"] = daily_reward
                    stk["staking_rewards_usd"] = round(daily_reward * 5.0, 2)
            except Exception:
                pass
    return USER_STAKING[tid]

def get_user_event_staking(tid):
    if tid not in USER_EVENT_STAKING:
        USER_EVENT_STAKING[tid] = {
            "total_staked": 73.0,
            "earned": 2.5,
            "apr": 45.0,
            "claimed": False
        }
    return USER_EVENT_STAKING[tid]


USER_STATE = {
    "balance_ton": 150.0,
    "balance_stars": 500,
    "stats": {
        "total_games": 24,
        "best_win_ton": 35.0,
        "lombard_total_ton": 0.0
    },
    "inventory": [
        {
            "gift_id": "gift_starter_pepe_crown",
            "cost_ton": 50.0,
            "cost_usd": 250.0,
            "lombard_cost_ton": 40.0,
            "title": "Bonded Ring",
            "num": 77,
            "model": "bondedring",
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
            "title": "Diamond Ring",
            "num": 109,
            "model": "diamondring",
            "model_rarity": 2,
            "background": "purple",
            "background_rarity": 2,
            "symbol": "dog",
            "symbol_rarity": 2
        },
        {
            "gift_id": "gift_starter_1",
            "cost_ton": 15.0,
            "cost_usd": 75.0,
            "lombard_cost_ton": 12.0,
            "title": "Crystal Ball",
            "num": 428,
            "model": "crystalball",
            "model_rarity": 1,
            "background": "cyan",
            "background_rarity": 1,
            "symbol": "gem",
            "symbol_rarity": 1
        },
        {
            "gift_id": "gift_starter_star",
            "cost_ton": 8.0,
            "cost_usd": 40.0,
            "lombard_cost_ton": 6.4,
            "title": "Star Locket",
            "num": 512,
            "model": "star_locket",
            "model_rarity": 1,
            "background": "blue",
            "background_rarity": 1,
            "symbol": "star",
            "symbol_rarity": 1
        },
        {
            "gift_id": "gift_starter_plush",
            "cost_ton": 12.0,
            "cost_usd": 60.0,
            "lombard_cost_ton": 9.6,
            "title": "Gem Signet",
            "num": 919,
            "model": "gemsignet",
            "model_rarity": 1,
            "background": "cyan",
            "background_rarity": 1,
            "symbol": "pepe",
            "symbol_rarity": 1
        },
        {
            "gift_id": "gift_starter_2",
            "cost_ton": 25.0,
            "cost_usd": 125.0,
            "lombard_cost_ton": 20.0,
            "title": "Diamond Ring",
            "num": 109,
            "model": "diamondring",
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
            "title": "Bonded Ring",
            "num": 77,
            "model": "bondedring",
            "model_rarity": 3,
            "background": "gold",
            "background_rarity": 3,
            "symbol": "crown",
            "symbol_rarity": 3
        },
        {
            "gift_id": "gift_starter_4",
            "cost_ton": 8.0,
            "cost_usd": 40.0,
            "lombard_cost_ton": 6.4,
            "title": "Star Locket",
            "num": 892,
            "model": "star_locket",
            "model_rarity": 1,
            "background": "blue",
            "background_rarity": 1,
            "symbol": "star",
            "symbol_rarity": 1
        }
    ]
}

# Shop / Market catalog
MARKET_CATALOG = [
    {
        "gift_id": "market_pepe_crown_1",
        "title": "Bonded Ring",
        "cost_ton": 50.0,
        "cost_usd": 250.0,
        "lombard_cost_ton": 40.0,
        "market_cost_ton": 50.0,
        "market_cost_usd": 250.0,
        "num": 12,
        "model": "bondedring",
        "model_rarity": 3,
        "background": "gold",
        "background_rarity": 3,
        "symbol": "crown",
        "symbol_rarity": 3
    },
    {
        "gift_id": "market_dog_1",
        "title": "Diamond Ring",
        "cost_ton": 25.0,
        "cost_usd": 125.0,
        "lombard_cost_ton": 20.0,
        "market_cost_ton": 25.0,
        "market_cost_usd": 125.0,
        "num": 88,
        "model": "diamondring",
        "model_rarity": 2,
        "background": "purple",
        "background_rarity": 2,
        "symbol": "dog",
        "symbol_rarity": 2
    },
    {
        "gift_id": "market_locket_1",
        "title": "Crystal Ball",
        "cost_ton": 15.0,
        "cost_usd": 75.0,
        "lombard_cost_ton": 12.0,
        "market_cost_ton": 15.0,
        "market_cost_usd": 75.0,
        "num": 341,
        "model": "crystalball",
        "model_rarity": 1,
        "background": "cyan",
        "background_rarity": 1,
        "symbol": "gem",
        "symbol_rarity": 1
    },
    {
        "gift_id": "market_star_1",
        "title": "Star Locket",
        "cost_ton": 8.0,
        "cost_usd": 40.0,
        "lombard_cost_ton": 6.4,
        "market_cost_ton": 8.0,
        "market_cost_usd": 40.0,
        "num": 512,
        "model": "star_locket",
        "model_rarity": 1,
        "background": "blue",
        "background_rarity": 1,
        "symbol": "star",
        "symbol_rarity": 1
    },
    {
        "gift_id": "market_pepe_plush_1",
        "title": "Gem Signet",
        "cost_ton": 12.0,
        "cost_usd": 60.0,
        "lombard_cost_ton": 9.6,
        "market_cost_ton": 12.0,
        "market_cost_usd": 60.0,
        "num": 919,
        "model": "gemsignet",
        "model_rarity": 1,
        "background": "cyan",
        "background_rarity": 1,
        "symbol": "pepe",
        "symbol_rarity": 1
    }
]

CASES = [
    {
        "case_id": "free",
        "name": "Daily Free",
        "price_ton": 0.0,
        "price_stars": 0,
        "badges": ["FREE"],
        "access": "FREE",
        "next_open_at": None,
        "required_channels": []
    },
    {
        "case_id": "roller",
        "name": "Roller Case",
        "price_ton": 2.0,
        "price_stars": 100,
        "badges": ["HOT"],
        "access": "PAID",
        "next_open_at": None,
        "required_channels": []
    },
    {
        "case_id": "goldy",
        "name": "Goldy Case",
        "price_ton": 10.0,
        "price_stars": 500,
        "badges": ["LEGENDARY"],
        "access": "PAID",
        "next_open_at": None,
        "required_channels": []
    },
    {
        "case_id": "pepe",
        "name": "Pepe Case",
        "price_ton": 1.0,
        "price_stars": 50,
        "badges": [],
        "access": "PAID",
        "next_open_at": None,
        "required_channels": []
    },
    {
        "case_id": "gemchik",
        "name": "Gemchik Case",
        "price_ton": 5.0,
        "price_stars": 250,
        "badges": ["NEW"],
        "access": "PAID",
        "next_open_at": None,
        "required_channels": []
    }
]

PRIZES = [
    {"id": "crystal_ball", "name": "Crystal Ball", "type": "GIFT", "amount_ton": 15.0, "model": "crystalball"},
    {"id": "diamond_ring", "name": "Diamond Ring", "type": "GIFT", "amount_ton": 37.0, "model": "diamondring"},
    {"id": "bonded_ring", "name": "Bonded Ring", "type": "GIFT", "amount_ton": 44.0, "model": "bondedring"},
    {"id": "bday_candle", "name": "B-Day Candle", "type": "GIFT", "amount_ton": 6.0, "model": "bdaycandle"},
    {"id": "ton_reward_5", "name": "5 TON", "type": "TON", "amount_ton": 5.0, "model": None},
    {"id": "ton_reward_2", "name": "2 TON", "type": "TON", "amount_ton": 2.0, "model": None},
    {"id": "ton_reward_1", "name": "1 TON", "type": "TON", "amount_ton": 1.0, "model": None}
]

# Upgrade Targets
UPGRADE_TARGETS = [
    {
        "type": "MARKET_GIFT",
        "gift_id": "target_pepe_crown",
        "title": "Bonded Ring",
        "cost_ton": 50.0,
        "target_price_ton": 50.0,
        "gift": {
            "gift_id": "target_pepe_crown",
            "title": "Bonded Ring",
            "cost_ton": 50.0,
            "num": 777,
            "model": "bondedring",
            "symbol": "crown",
            "background": "gold"
        }
    },
    {
        "type": "MARKET_GIFT",
        "gift_id": "target_dog",
        "title": "Diamond Ring",
        "cost_ton": 25.0,
        "target_price_ton": 25.0,
        "gift": {
            "gift_id": "target_dog",
            "title": "Diamond Ring",
            "cost_ton": 25.0,
            "num": 109,
            "model": "diamondring",
            "symbol": "dog",
            "background": "purple"
        }
    },
    {
        "type": "MARKET_GIFT",
        "gift_id": "target_lucky_locket",
        "title": "Crystal Ball",
        "cost_ton": 15.0,
        "target_price_ton": 15.0,
        "gift": {
            "gift_id": "target_lucky_locket",
            "title": "Crystal Ball",
            "cost_ton": 15.0,
            "num": 428,
            "model": "crystalball",
            "symbol": "gem",
            "background": "cyan"
        }
    }
]

OPPONENT_PROFILES = [
    {"telegram_id": 1001001, "display_name": "Sardor (TON)", "avatar": "https://telegram.org/img/t_logo.png"},
    {"telegram_id": 1001002, "display_name": "CryptoWhale", "avatar": "https://telegram.org/img/t_logo.png"},
    {"telegram_id": 1001003, "display_name": "Ali_Roll", "avatar": "https://telegram.org/img/t_logo.png"},
    {"telegram_id": 1001004, "display_name": "Tashkent_Ton", "avatar": "https://telegram.org/img/t_logo.png"},
    {"telegram_id": 1001005, "display_name": "LuckyStar", "avatar": "https://telegram.org/img/t_logo.png"}
]

class PurePvPEngine:
    """
    True PvP Engine with multi-user attribution:
    - Never starts countdown or spins with only 1 player.
    - Preserves distinct user_id, display_name, username, photo on all bets.
    - When 1 user bets, waits in 'collecting' status with 1 player.
    - A realistic opponent joins after 2.5s with a competing bet.
    - When >=2 players exist -> 15s countdown begins with two-colored wheel!
    - Wheel spins, winner takes entire pot and winnings are credited to the real player.
    - When idle, room stays completely clean and quiet (0 spam bots).
    """
    def __init__(self, game_type="NORMAL"):
        self.game_type = game_type
        self.lock = threading.RLock()
        self.game_num = 1520
        self.status = "collecting"
        self.round_start = None
        self.cycle_seconds = 15.0
        self.completed_seconds = 12.0
        self.bets = []
        self.pending_opponent_time = None
        self.winner_tid = None
        self.winner_name = None
        self.winner_gift_ids = []
        self.winner_ton_award = 0.0
        self.total_prize_ton = 0.0
        self.current_seed = hashlib.sha256(f"{self.game_num}_{time.time()}_{random.random()}".encode()).hexdigest()
        self.current_hash = hashlib.sha256(self.current_seed.encode()).hexdigest()

    def place_bet(self, user_id, display_name, username, photo, amount_ton=0.0, gifts=None, is_opponent=False, amount_stars=0):
        with self.lock:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            bet = {
                "user_id": user_id,
                "display_name": display_name,
                "username": username,
                "photo": photo,
                "amount_ton": float(amount_ton),
                "amount_stars": int(amount_stars),
                "gifts": gifts or [],
                "is_opponent": is_opponent,
                "timestamp": now_iso
            }
            self.bets.append(bet)
            real_player_ids = {b["user_id"] for b in self.bets if not b["is_opponent"]}
            all_player_ids = {b["user_id"] for b in self.bets}
            if self.status == "collecting":
                if len(all_player_ids) >= 2:
                    self.status = "countdown"
                    self.round_start = time.time()
                    self.pending_opponent_time = None
                elif len(real_player_ids) == 1 and not self.pending_opponent_time:
                    self.pending_opponent_time = time.time() + 4.5

    def add_user_ton(self, amount, user_id=None, display_name=None, username=None, photo=None):
        uid = user_id or CURRENT_USER.get("telegram_id", 999999999)
        dname = display_name or CURRENT_USER.get("display_name", "Rolls Player")
        uname = username or CURRENT_USER.get("telegram_username", "player")
        purl = photo or CURRENT_USER.get("image_url", "https://telegram.org/img/t_logo.png")
        self.place_bet(uid, dname, uname, purl, amount_ton=amount, gifts=None)

    def add_user_gift(self, gift, user_id=None, display_name=None, username=None, photo=None):
        uid = user_id or CURRENT_USER.get("telegram_id", 999999999)
        dname = display_name or CURRENT_USER.get("display_name", "Rolls Player")
        uname = username or CURRENT_USER.get("telegram_username", "player")
        purl = photo or CURRENT_USER.get("image_url", "https://telegram.org/img/t_logo.png")
        self.place_bet(uid, dname, uname, purl, amount_ton=0.0, gifts=[gift])

    def update_cycle(self):
        with self.lock:
            now = time.time()
            if self.status == "collecting":
                if self.pending_opponent_time and now >= self.pending_opponent_time:
                    opp = random.choice(OPPONENT_PROFILES)
                    real_val = sum(b["amount_ton"] + sum(g.get("cost_ton", 0.0) for g in b["gifts"]) for b in self.bets if not b["is_opponent"])
                    opp_bet = max(0.25, round(real_val * random.uniform(0.7, 1.25), 2))
                    opp_bet_entry = {
                        "user_id": opp["telegram_id"],
                        "display_name": opp["display_name"],
                        "username": opp.get("username", "player"),
                        "photo": opp.get("avatar", "https://telegram.org/img/t_logo.png"),
                        "amount_ton": opp_bet,
                        "gifts": [],
                        "is_opponent": True,
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
                    self.bets.append(opp_bet_entry)
                    self.pending_opponent_time = None
                    self.status = "countdown"
                    self.round_start = now

            elif self.status == "countdown":
                elapsed = now - self.round_start
                if elapsed >= self.cycle_seconds:
                    self.status = "completed"
                    self.round_start = now
                    player_map = {}
                    for b in self.bets:
                        uid = b["user_id"]
                        if uid not in player_map:
                            player_map[uid] = {
                                "user_id": uid,
                                "display_name": b["display_name"],
                                "username": b["username"],
                                "photo": b["photo"],
                                "is_opponent": b["is_opponent"],
                                "total_val": 0.0,
                                "gifts": [],
                                "ton": 0.0
                            }
                        b_gifts_val = sum(g.get("cost_ton", 0.0) for g in b["gifts"])
                        b_val = b["amount_ton"] + b_gifts_val
                        player_map[uid]["total_val"] += b_val
                        player_map[uid]["ton"] += b["amount_ton"]
                        player_map[uid]["gifts"].extend(b["gifts"])

                    total_pot = sum(p["total_val"] for p in player_map.values())
                    all_gifts_in_pot = [g for p in player_map.values() for g in p["gifts"]]
                    real_players = [p for p in player_map.values() if not p["is_opponent"]]

                    # Mathematically fair wheel selection: probability is exactly proportional to total bet value
                    if total_pot > 0 and player_map:
                        roll = random.uniform(0.0, total_pot)
                        running = 0.0
                        winner = None
                        for p in player_map.values():
                            running += p["total_val"]
                            if roll <= running:
                                winner = p
                                break
                        if not winner:
                            winner = list(player_map.values())[-1]
                    else:
                        winner = None

                    if winner:
                        self.winner_tid = winner["user_id"]
                        self.winner_name = winner["display_name"]
                        self.total_prize_ton = round(total_pot, 2)
                        self.winner_gift_ids = [g["gift_id"] for g in all_gifts_in_pot]

                        ton_in_pot = sum(b["amount_ton"] for b in self.bets)
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
                        distribute_referral_commission(w_tid, total_pot, commission_ton, game_name=f"{self.game_type} PvP")

                        # Increment staking progression for real players
                        for p in player_map.values():
                            if not p["is_opponent"]:
                                stk = get_user_staking(p["user_id"])
                                stk["games_since_last_payout"] += 1

                        # Snapshot true game data for history
                        completed_rec = dict(self._build_game_data_unlocked())
                        completed_rec["time_until_next_game_start_ms"] = None
                        RECENT_HISTORY.insert(0, completed_rec)
                        if len(RECENT_HISTORY) > 50:
                            RECENT_HISTORY.pop()

            elif self.status == "completed":
                elapsed = now - self.round_start
                if elapsed >= self.completed_seconds:
                    self.game_num += 1
                    self.status = "collecting"
                    self.round_start = None
                    self.bets = []
                    self.pending_opponent_time = None
                    self.winner_tid = None
                    self.winner_name = None
                    self.winner_gift_ids = []
                    self.winner_ton_award = 0.0
                    self.total_prize_ton = 0.0
                    self.current_seed = hashlib.sha256(f"{self.game_num}_{time.time()}_{random.random()}".encode()).hexdigest()
                    self.current_hash = hashlib.sha256(self.current_seed.encode()).hexdigest()

    def _build_game_data_unlocked(self):
        now = time.time()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        gid = f"game_roll_{self.game_num}"

        player_map = {}
        history = []
        for b in self.bets:
            uid = b["user_id"]
            uid_str = str(uid)
            if uid_str not in player_map:
                player_map[uid_str] = {
                    "user_id": uid,
                    "display_name": b["display_name"],
                    "username": b["username"],
                    "photo": b["photo"],
                    "is_opponent": b["is_opponent"],
                    "ton": 0.0,
                    "gifts": [],
                    "total_val": 0.0,
                    "last_updated_at": b["timestamp"]
                }
            player_map[uid_str]["ton"] += b["amount_ton"]
            player_map[uid_str]["gifts"].extend(b["gifts"])
            gifts_val = sum(g.get("cost_ton", 0.0) for g in b["gifts"])
            player_map[uid_str]["total_val"] += (b["amount_ton"] + gifts_val)
            player_map[uid_str]["last_updated_at"] = b["timestamp"]

            if b["amount_ton"] > 0:
                history.append({
                    "timestamp": b["timestamp"],
                    "user_telegram_id": uid,
                    "user_display_name": b["display_name"],
                    "bet_type": "CURRENCY",
                    "amount_ton": b["amount_ton"],
                    "currency": "TON",
                    "amount_units": 0,
                    "item_ids": [],
                    "ledger_id": None
                })
            for g in b["gifts"]:
                history.append({
                    "timestamp": b["timestamp"],
                    "user_telegram_id": uid,
                    "user_display_name": b["display_name"],
                    "bet_type": "GIFT",
                    "amount_ton": g.get("cost_ton", 0.0),
                    "currency": None,
                    "amount_units": 0,
                    "item_ids": [g["gift_id"]],
                    "ledger_id": None
                })

        total_pot = sum(p["total_val"] for p in player_map.values())
        curr_bets = {}
        gifts_by_tid = {}
        for uid_str, p in player_map.items():
            if p["ton"] > 0:
                curr_bets[uid_str] = {
                    "TON": {
                        "currency": "TON",
                        "amount_ton": round(p["ton"], 2),
                        "amount_units": 0,
                        "last_updated_at": p["last_updated_at"]
                    }
                }
            win_chance = round((p["total_val"] / max(0.01, total_pot)) * 100, 1) if total_pot > 0 else 0.0
            g_ton = sum(g.get("cost_ton", 0.0) for g in p["gifts"])
            gifts_by_tid[uid_str] = {
                "gifts": p["gifts"],
                "total_cost_ton": round(g_ton, 2),
                "total_cost_usd": round(g_ton * 5.0, 2),
                "user_display_name": p["display_name"],
                "win_chance_percent": win_chance,
                "has_dragon": False
            }

        base = {
            "id": gid,
            "type": self.game_type,
            "game_num": self.game_num,
            "currency_bets_by_telegram_id": curr_bets,
            "gifts_by_telegram_id": gifts_by_tid,
            "commission_change_gifts_info": {},
            "total_prize_ton": round(total_pot, 2),
            "total_prize_usd": round(total_pot * 5.0, 2),
            "countdown_duration_ms": int(self.cycle_seconds * 1000),
            "created_at": now_iso,
            "updated_at": now_iso,
            "previous_roll_game_id": f"game_roll_{self.game_num - 1}",
            "github_verify_link": "https://github.com",
            "extra_prize_gifts": [],
            "extra_prize_gift_ids": [],
            "extra_prize_gifts_info": {},
            "next_round_total_prize_ton": None,
            "scheduled_start_time": None,
            "last_reactions": [],
            "bets_history": history,
            "is_elimination_phase": False
        }

        if self.status == "collecting":
            return {
                **base,
                "status": "collecting",
                "winner_telegram_id": None,
                "winner_display_name": None,
                "countdown_start_time": None,
                "countdown_remaining_ms": None,
                "time_until_next_game_start_ms": None,
                "hash": self.current_hash,
                "seed": None,
                "bets_map": None
            }
        elif self.status == "countdown":
            remaining_ms = max(0, int((self.cycle_seconds - (now - self.round_start)) * 1000))
            start_iso = datetime.datetime.fromtimestamp(self.round_start, datetime.timezone.utc).isoformat()
            return {
                **base,
                "status": "countdown",
                "winner_telegram_id": None,
                "winner_display_name": None,
                "countdown_start_time": start_iso,
                "countdown_remaining_ms": remaining_ms,
                "time_until_next_game_start_ms": None,
                "hash": self.current_hash,
                "seed": None,
                "bets_map": None
            }
        else: # completed
            rem_next_ms = max(0, int((self.completed_seconds - (now - self.round_start)) * 1000))
            return {
                **base,
                "status": "completed",
                "winner_telegram_id": self.winner_tid,
                "winner_display_name": self.winner_name,
                "countdown_start_time": None,
                "countdown_remaining_ms": None,
                "time_until_next_game_start_ms": rem_next_ms,
                "winner_gift_ids": self.winner_gift_ids,
                "winner_token_ids": [],
                "winner_ton_award_ton": float(self.winner_ton_award),
                "hash": self.current_hash,
                "seed": self.current_seed,
                "bets_map": None
            }

    def get_game_data(self):
        with self.lock:
            return self._build_game_data_unlocked()

PVP_ENGINE = PurePvPEngine("NORMAL")
GRAND_ENGINE = PurePvPEngine("GRAND")

def background_game_loop():
    while True:
        try:
            PVP_ENGINE.update_cycle()
            GRAND_ENGINE.update_cycle()
        except Exception as e:
            print("Engine error:", e)
        time.sleep(0.5)

threading.Thread(target=background_game_loop, daemon=True).start()

def extract_telegram_user(auth_header):
    if not auth_header:
        return 999999999, "Rolls Player", "player", "https://telegram.org/img/t_logo.png"
    try:
        clean = auth_header.strip()
        if "%" in clean:
            clean = urllib.parse.unquote(clean).strip()

        if clean.lower().startswith("tma "):
            clean = clean[4:].strip()
        elif clean.lower().startswith("bearer "):
            clean = clean[7:].strip()

        parsed = urllib.parse.parse_qs(clean)
        if "user" not in parsed:
            unquoted = urllib.parse.unquote(clean)
            if unquoted != clean:
                parsed = urllib.parse.parse_qs(unquoted)

        if "user" in parsed:
            raw_user = parsed["user"][0]
            if isinstance(raw_user, str):
                u = json.loads(raw_user)
            else:
                u = raw_user
            tid = int(u.get("id", 999999999))
            dname = u.get("first_name", "Rolls Player")
            if u.get("last_name"):
                dname = f"{dname} {u['last_name']}".strip()
            uname = u.get("username", "player")
            photo = u.get("photo_url", "https://telegram.org/img/t_logo.png")
            return tid, dname, uname, photo
    except Exception as e:
        print(f"[AUTH] Parse error: {e}")
    return 999999999, "Rolls Player", "player", "https://telegram.org/img/t_logo.png"

class RollsGameHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def get_caller_user(self):
        auth_header = self.headers.get("Authorization", "")
        tid, dname, uname, photo = extract_telegram_user(auth_header)
        USERS_REGISTRY[tid] = {
            "telegram_id": tid,
            "display_name": dname,
            "telegram_username": uname,
            "image_url": photo
        }
        CURRENT_USER["telegram_id"] = tid
        CURRENT_USER["display_name"] = dname
        CURRENT_USER["telegram_username"] = uname
        CURRENT_USER["image_url"] = photo
        return tid, dname, uname, photo

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path


        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b""
        data = {}
        if body:
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                pass

        # Admin API handlers
        if path == "/admin/api/settings":
            ok = save_admin_prices(data)
            return self.send_json({"success": ok})

        if path == "/admin/api/user/balance":
            uid = data.get("telegram_id")
            new_bal = float(data.get("balance_ton", 0.0))
            if uid:
                set_user_balance(uid, new_bal)
                return self.send_json({"success": True, "new_balance": new_bal})
            return self.send_json({"error": "Missing telegram_id"}, status=400)

        if path.startswith("/api/"):
            path = path[4:]

        # 0. Referral Register Endpoint
        if path.endswith("/v1/referral/register"):
            inviter = data.get("inviter_id")
            new_uid = data.get("user_id") or data.get("new_user_id")
            dname = data.get("display_name") or data.get("name", "Friend")
            uname = data.get("username", "friend")
            ok = register_referral(inviter, new_uid, dname, uname)
            return self.send_json({"success": ok})

        # 1. Login Endpoint
        if path.endswith("/v1/users/login"):
            tid, dname, uname, photo = self.get_caller_user()
            user_inv = get_user_inventory(tid)
            user_bal = get_user_balance(tid)
            USER_STATE["inventory"] = user_inv

            # Check if user came from a referral link
            qs = urllib.parse.parse_qs(parsed.query)
            ref_param = qs.get("ref_id", [None])[0] or data.get("ref_id")
            if not ref_param:
                auth_h = self.headers.get("Authorization", "")
                if "start_param" in auth_h:
                    try:
                        p_auth = urllib.parse.parse_qs(urllib.parse.unquote(auth_h))
                        if "start_param" in p_auth:
                            ref_param = p_auth["start_param"][0]
                    except Exception:
                        pass
            if ref_param:
                register_referral(ref_param, tid, dname, uname)

            return self.send_json({
                "telegram_id": tid,
                "display_name": dname,
                "image_url": photo,
                "telegram_username": uname,
                "ref_id": str(tid),
                "perks": [],
                "balance": {
                    "balance_nano": int(user_bal * 1e9),
                    "balance_ton": user_bal,
                    "balance_usd": round(user_bal * 5.0, 2)
                },
                "wallet": None,
                "active_game_roll": None
            })

        # Stars Betting Endpoint
        if path.endswith("/v1/game-roll/add-stars") or path.endswith("/v1/grand-game-roll/add-stars"):
            engine = GRAND_ENGINE if "grand" in path else PVP_ENGINE
            tid, dname, uname, photo = self.get_caller_user()
            stars = int(data.get("amount_stars", 50))
            cur_stars = get_user_stars(tid)
            if cur_stars >= stars:
                set_user_stars(tid, cur_stars - stars)
                ton_equiv = round(stars / 50.0, 2)
                engine.place_bet(user_id=tid, display_name=dname, username=uname, photo=photo, amount_ton=ton_equiv, gifts=None, amount_stars=stars)
            return self.send_json(engine.get_game_data())

        # 2. Add Gifts to PvP Roulette
        if path.endswith("/v1/game-roll/add-gifts"):
            if PVP_ENGINE.status == "completed":
                return self.send_json({"error": "Round is in progress, please wait"}, status=400)
            tid, dname, uname, photo = self.get_caller_user()
            user_inv = get_user_inventory(tid)
            gift_ids = data.get("gift_ids", [])
            added = []
            for gid in gift_ids:
                matching = next((g for g in user_inv if g["gift_id"] == gid), None)
                if matching:
                    user_inv.remove(matching)
                    added.append(matching)
            if added:
                PVP_ENGINE.place_bet(user_id=tid, display_name=dname, username=uname, photo=photo, amount_ton=0.0, gifts=added)
            return self.send_json(PVP_ENGINE.get_game_data())

        # 3. Add TON to PvP Roulette
        if path.endswith("/v1/game-roll/add-ton"):
            if PVP_ENGINE.status == "completed":
                return self.send_json({"error": "Round is in progress, please wait"}, status=400)
            tid, dname, uname, photo = self.get_caller_user()
            amount = float(data.get("amount_ton", 1.0))
            bal = get_user_balance(tid)
            if bal >= amount:
                set_user_balance(tid, bal - amount)
                PVP_ENGINE.place_bet(user_id=tid, display_name=dname, username=uname, photo=photo, amount_ton=amount, gifts=None)
            return self.send_json(PVP_ENGINE.get_game_data())

        # 4. Grand Game Roll
        if path.endswith("/v1/grand-game-roll/add-gifts"):
            if GRAND_ENGINE.status == "completed":
                return self.send_json({"error": "Round is in progress, please wait"}, status=400)
            tid, dname, uname, photo = self.get_caller_user()
            user_inv = get_user_inventory(tid)
            gift_ids = data.get("gift_ids", [])
            added = []
            for gid in gift_ids:
                matching = next((g for g in user_inv if g["gift_id"] == gid), None)
                if matching:
                    user_inv.remove(matching)
                    added.append(matching)
            if added:
                GRAND_ENGINE.place_bet(user_id=tid, display_name=dname, username=uname, photo=photo, amount_ton=0.0, gifts=added)
            return self.send_json(GRAND_ENGINE.get_game_data())

        if path.endswith("/v1/grand-game-roll/add-ton"):
            if GRAND_ENGINE.status == "completed":
                return self.send_json({"error": "Round is in progress, please wait"}, status=400)
            tid, dname, uname, photo = self.get_caller_user()
            amount = float(data.get("amount_ton", 10.0))
            bal = get_user_balance(tid)
            if bal >= amount:
                set_user_balance(tid, bal - amount)
                GRAND_ENGINE.place_bet(user_id=tid, display_name=dname, username=uname, photo=photo, amount_ton=amount, gifts=None)
            return self.send_json(GRAND_ENGINE.get_game_data())

        # 5. Open Case
        if path.endswith("/v1/cases/open"):
            tid, _, _, _ = self.get_caller_user()
            case_id = data.get("case_id", "free")
            payment_method = data.get("payment_method", "TON")

            won_prize = random.choice(PRIZES)
            case_data = next((c for c in CASES if c["case_id"] == case_id), None)

            cost = 0.0
            if case_data:
                cost = case_data["price_ton"] if payment_method == "TON" else (case_data.get("price_stars") or 0)

            if payment_method == "TON":
                set_user_balance(tid, max(0.0, get_user_balance(tid) - cost))
            else:
                set_user_stars(tid, max(0, get_user_stars(tid) - int(cost)))

            if won_prize["type"] == "TON":
                set_user_balance(tid, get_user_balance(tid) + won_prize["amount_ton"])
            else:
                gift_entry = {
                    "gift_id": f"gift_{won_prize['id']}_{int(time.time()*1000)}",
                    "cost_ton": won_prize["amount_ton"],
                    "cost_usd": won_prize["amount_ton"] * 5.0,
                    "lombard_cost_ton": won_prize["amount_ton"] * 0.8,
                    "title": won_prize["name"],
                    "num": random.randint(1, 9999),
                    "model": won_prize["model"] or "lucky_locket",
                    "model_rarity": 1,
                    "background": "cyan",
                    "background_rarity": 1,
                    "symbol": "star",
                    "symbol_rarity": 1
                }
                get_user_inventory(tid).append(gift_entry)

            spin_id = f"spin_{int(time.time()*1000)}"
            return self.send_json({
                "payment_status": "PAID",
                "result": {
                    "spin_id": spin_id,
                    "is_paid": True,
                    "case_id": case_id,
                    "prize": won_prize,
                    "needs_resolution": False,
                    "sell_for_ton": won_prize["amount_ton"],
                    "status": "COMPLETED"
                }
            })

        # 6. Lombard Sell Gifts
        if path.endswith("/v1/user/gifts/lombard/sell"):
            tid, _, _, _ = self.get_caller_user()
            user_inv = get_user_inventory(tid)
            sold_ids = data.get("gift_ids", [])
            total_earned = 0.0
            for sid in sold_ids:
                matching = next((g for g in user_inv if g["gift_id"] == sid), None)
                if matching:
                    val = matching.get("lombard_cost_ton") or (matching["cost_ton"] * 0.8)
                    total_earned += val
                    user_inv.remove(matching)
            set_user_balance(tid, get_user_balance(tid) + total_earned)
            get_user_stats(tid)["lombard_total_ton"] += total_earned
            return self.send_json({
                "success": True,
                "sale_id": f"sale_{int(time.time())}",
                "sold_gift_ids": sold_ids,
                "sold_count": len(sold_ids),
                "total_amount_ton": total_earned,
                "credited_ledger_id": f"ledger_{int(time.time())}",
                "message": "Gifts sold successfully!"
            })

        # Deposit via Real Live CryptoBot (Gram / TON)
        if path.endswith("/v1/users/balance/topups/cryptobot"):
            tid, _, _, _ = self.get_caller_user()
            amount = float(data.get("amount", 10.0))
            inv = create_crypto_invoice(amount=amount, telegram_id=tid, currency="TON")
            if inv:
                topup_record = {
                    "id": f"cb_{inv.get('invoice_id')}",
                    "invoice_id": inv.get("invoice_id"),
                    "amount_ton": amount,
                    "currency": "Gram",
                    "status": "PENDING",
                    "method": "CryptoBot",
                    "pay_url": inv.get("pay_url"),
                    "mini_app_invoice_url": inv.get("mini_app_invoice_url"),
                    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                USER_TOPUPS.setdefault(tid, []).insert(0, topup_record)
                return self.send_json({
                    "mini_app_invoice_url": inv.get("mini_app_invoice_url"),
                    "bot_invoice_url": inv.get("bot_invoice_url"),
                    "pay_url": inv.get("pay_url"),
                    "invoice_id": inv.get("invoice_id"),
                    "amount": amount,
                    "status": "PENDING"
                })
            else:
                return self.send_json({"error": "Failed to create CryptoBot invoice"}, status=500)

        # CryptoBot Webhook Handler
        if path.endswith("/v1/cryptopay/webhook"):
            if data.get("update_type") == "invoice_paid":
                p_inv = data.get("payload", {})
                raw_p = p_inv.get("payload")
                if raw_p:
                    try:
                        p_data = json.loads(raw_p)
                        w_tid = p_data.get("telegram_id")
                        w_amt = float(p_inv.get("amount", 0.0))
                        if w_tid and w_amt > 0:
                            set_user_balance(w_tid, get_user_balance(w_tid) + w_amt)
                            print(f"[CRYPTOPAY WEBHOOK] Instant payment processed: +{w_amt} Gram for {w_tid}")
                    except Exception as ex:
                        print(f"[CRYPTOPAY WEBHOOK] Error: {ex}")
            return self.send_json({"ok": True})

        # Deposit via xRocket (Gram / TON)
        if path.endswith("/v1/users/balance/topups/xrocket"):
            tid, _, _, _ = self.get_caller_user()
            amount = float(data.get("amount", 10.0))
            new_bal = round(get_user_balance(tid) + amount, 2)
            set_user_balance(tid, new_bal)
            topup_record = {
                "id": f"xr_{int(time.time()*1000)}",
                "amount_ton": amount,
                "currency": "Gram",
                "status": "COMPLETED",
                "method": "xRocket",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            USER_TOPUPS.setdefault(tid, []).insert(0, topup_record)
            print(f"[TOPUP] xRocket deposit: +{amount} Gram for user {tid} -> New Balance: {new_bal} Gram")
            return self.send_json({
                "link": f"https://t.me/mull_rocketbot?start=pay_{int(time.time()*1000)}",
                "new_balance": new_bal,
                "amount": amount
            })

        # Deposit via Wallet (Gram / TON)
        if path.endswith("/v1/users/balance/topups"):
            tid, _, _, _ = self.get_caller_user()
            amount = float(data.get("expected_amount_ton", 10.0))
            new_bal = round(get_user_balance(tid) + amount, 2)
            set_user_balance(tid, new_bal)
            comment = f"rolls_{tid}_{int(time.time())}"
            topup_record = {
                "id": f"dep_{int(time.time()*1000)}",
                "amount_ton": amount,
                "currency": "Gram",
                "status": "COMPLETED",
                "method": "TON Connect Wallet",
                "recipient_wallet": get_project_wallet(),
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            USER_TOPUPS.setdefault(tid, []).insert(0, topup_record)
            print(f"[TOPUP] Wallet deposit to {get_project_wallet()}: +{amount} Gram for user {tid} -> New Balance: {new_bal} Gram")
            return self.send_json({
                "uid": topup_record["id"],
                "created_at": topup_record["created_at"],
                "new_balance": new_bal,
                "amount": amount,
                "recipient_wallet": get_project_wallet(),
                "ton_connect_transaction": {
                    "validUntil": int(time.time() + 600),
                    "messages": [
                        {
                            "address": get_project_wallet(),
                            "amount": str(int(amount * 1e9)),
                            "payload": comment
                        }
                    ]
                }
            })

        # Relayer Deposit Webhook (Authenticated & Anti-Cheat)
        if path.endswith("/relayer/gift-received") or path.endswith("/v1/relayer/gift-received"):
            secret = self.headers.get("X-Relayer-Secret")
            if secret != "shencas_relayer_secret_8830393679_secure":
                return self.send_json({"error": "Unauthorized relayer call: invalid secret"}, status=403)

            sender_id = data.get("sender_id", CURRENT_USER.get("telegram_id", 0))
            sender_username = data.get("sender_username", "")
            title = data.get("gift_name", "Telegram Gift")
            cost_ton = float(data.get("value_ton", 10.0))
            model = data.get("model", "telegram_gift")
            background = data.get("background", "gold" if cost_ton >= 50 else "purple")
            rarity = int(data.get("rarity", 2 if cost_ton >= 20 else 1))
            num = int(data.get("num", random.randint(100, 9999)))
            msg_id = str(data.get("msg_id", ""))

            # Replay protection on server side
            log_path = os.path.join(os.path.dirname(__file__), "deposits_audit_log.json")
            logs = []
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except Exception:
                    logs = []

            if msg_id and any(entry.get("msg_id") == msg_id for entry in logs):
                return self.send_json({"error": "Duplicate deposit msg_id rejected", "success": False}, status=400)

            new_gift = {
                "gift_id": f"gift_relayer_{int(time.time()*1000)}",
                "cost_ton": cost_ton,
                "cost_usd": round(cost_ton * 5.0, 2),
                "lombard_cost_ton": round(cost_ton * 0.8, 2),
                "title": title,
                "num": num,
                "model": model,
                "model_rarity": rarity,
                "background": background,
                "background_rarity": rarity,
                "symbol": "gift",
                "symbol_rarity": 1
            }

            if sender_id not in USER_INVENTORIES:
                USER_INVENTORIES[sender_id] = [g.copy() for g in STARTER_INVENTORY]
            USER_INVENTORIES[sender_id].append(new_gift)

            if sender_id == CURRENT_USER.get("telegram_id"):
                USER_STATE["inventory"] = USER_INVENTORIES[sender_id]

            logs.append({
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "sender_id": sender_id,
                "sender_username": sender_username,
                "gift": new_gift,
                "msg_id": msg_id
            })
            try:
                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=2)
            except Exception as e:
                print(f"[SERVER] Error logging deposit: {e}")

            return self.send_json({
                "success": True,
                "message": "Authentic gift credited successfully",
                "gift": new_gift,
                "inventory_count": len(USER_INVENTORIES[sender_id])
            })

        # Withdraw Gifts v2 (TON or Stars)
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

            # NOTE: DO NOT credit TON or Stars to player balance per user instruction!
            # The NFT is removed from inventory and queued for relayer/admin delivery.

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
                "status": "PENDING",
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
            # NOTE: DO NOT credit TON per user instruction!

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
                "status": "PENDING",
                "total_stars": 0,
                "gift_count": len(removed_gifts),
                "invoice_url": None
            })

        # Withdraw Stickers
        if path.endswith("/v1/users/withdraw-stickers"):
            return self.send_json({
                "success": True,
                "withdrawal_id": f"wd_stickers_{int(time.time()*1000)}"
            })

        # Transfer Gifts
        if path.endswith("/v1/users/gifts/transfer"):
            gift_ids = data.get("gift_ids", [])
            for gid in gift_ids:
                matching = next((g for g in USER_STATE["inventory"] if g["gift_id"] == gid), None)
                if matching:
                    USER_STATE["inventory"].remove(matching)
            return self.send_json({
                "success": True,
                "transfer_id": f"tr_{int(time.time()*1000)}"
            })

        # 7. Market gifts list (POST) - Disabled per user instruction
        if path.endswith("/v1/market/gifts/list"):
            return self.send_json({
                "gifts": [],
                "total_count": 0
            })

        # 8. Market gifts purchase (POST) - Disabled per user instruction
        if path.endswith("/v1/market/gifts/purchase"):
            return self.send_json({"error": "Shop is closed", "success": False}, status=400)
            gift_ids = data.get("gift_ids", [])
            total_spent = 0.0
            for gid in gift_ids:
                item = next((m for m in MARKET_CATALOG if m["gift_id"] == gid), None)
                if item:
                    cost = item["market_cost_ton"]
                    if USER_STATE["balance_ton"] >= cost:
                        USER_STATE["balance_ton"] -= cost
                        total_spent += cost
                        USER_STATE["inventory"].append({
                            **item,
                            "gift_id": f"{item['gift_id']}_{int(time.time())}"
                        })
            return self.send_json({
                "market_cost_ton": total_spent,
                "gift_ids": gift_ids,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })

        # 9. Upgrade Targets (POST)
        if path.endswith("/v1/upgrade/targets"):
            return self.send_json({
                "items": UPGRADE_TARGETS,
                "total_count": len(UPGRADE_TARGETS),
                "rejected_sources": []
            })

        # 10. Upgrade Chance Quote (POST)
        if path.endswith("/v1/upgrade/chance"):
            target = data.get("target") or UPGRADE_TARGETS[0]
            amount = float(data.get("amount_ton", 5.0))
            target_cost = float(target.get("cost_ton", 50.0))
            chance = min(80.0, max(5.0, round((amount / target_cost) * 100, 1)))
            return self.send_json({
                "inventory_sources": [],
                "market_sources": [],
                "amount_ton": amount,
                "source_value_ton": amount,
                "balance_debit_ton": amount,
                "target": target,
                "chance_percent": chance,
                "max_chance_percent": 80.0,
                "rejected_sources": []
            })

        # 11. Upgrade Play (POST)
        if path.endswith("/v1/upgrade/play"):
            target = data.get("target") or UPGRADE_TARGETS[0]
            amount = float(data.get("amount_ton", 5.0))
            if USER_STATE["balance_ton"] >= amount:
                USER_STATE["balance_ton"] -= amount
            won = random.random() < 0.70
            if won:
                gift_data = target.get("gift") or {
                    "gift_id": f"upgraded_{int(time.time())}",
                    "title": target.get("title", "Upgraded Gift"),
                    "cost_ton": target.get("cost_ton", 25.0),
                    "num": random.randint(100, 999),
                    "model": "bondedring",
                    "symbol": "crown",
                    "background": "gold"
                }
                USER_STATE["inventory"].append({
                    "gift_id": f"upg_{int(time.time())}",
                    "cost_ton": target.get("cost_ton", 25.0),
                    "cost_usd": target.get("cost_ton", 25.0) * 5.0,
                    "lombard_cost_ton": target.get("cost_ton", 25.0) * 0.8,
                    "title": target.get("title", "Upgraded Gift"),
                    "num": random.randint(100, 999),
                    "model": "bondedring",
                    "model_rarity": 3,
                    "background": "gold",
                    "background_rarity": 3,
                    "symbol": "crown",
                    "symbol_rarity": 3
                })

            return self.send_json({
                "attempt_id": f"att_{int(time.time()*1000)}",
                "status": "COMPLETED" if won else "LOSS",
                "won": won,
                "chance_percent": 70.0,
                "gift": target.get("gift") if won else None,
                "delivery_pending": False,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })

        # 12. Limbo Play (POST)
        if path.endswith("/v1/limbo/play"):
            amount = float(data.get("amount_ton", 1.0))
            chance = float(data.get("chance_percent", 50.0))
            if USER_STATE["balance_ton"] >= amount:
                USER_STATE["balance_ton"] -= amount
            mult = round(98.0 / chance, 2)
            won = random.random() < (chance / 100.0)
            payout = amount * mult if won else 0.0
            if won:
                USER_STATE["balance_ton"] += payout
            return self.send_json({
                "game_num": random.randint(1000, 9999),
                "chance_percent": chance,
                "amount_ton": amount,
                "multiplier": mult,
                "is_win": won,
                "payout_ton": payout,
                "profit_ton": (payout - amount) if won else -amount,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })

        # 13. Tasks check
        if path.endswith("/v1/tasks/check"):
            return self.send_json({
                "success": True,
                "message": "Task completed successfully!"
            })

        # Spam buy POST
        if path.endswith("/v1/game-roll/spam-buy") or path.endswith("/v1/grand-game-roll/spam-buy"):
            return self.send_json({"success": True})

        # Event Staking Claim
        if path.endswith("/v1/snow-event/sakura-staking/claim"):
            tid, _, _, _ = self.get_caller_user()
            ev_stk = get_user_event_staking(tid)
            if ev_stk.get("claimed", False) or ev_stk.get("earned", 0.0) <= 0:
                return self.send_json({"error": "Sakura rewards already claimed or 0", "success": False}, status=400)
            earnings = ev_stk["earned"]
            set_user_balance(tid, get_user_balance(tid) + earnings)
            ev_stk["earned"] = 0.0
            ev_stk["claimed"] = True
            return self.send_json({"success": True, "claimed_ton": earnings})

        # 14. Hide username
        if path.endswith("/v1/users/hide-username"):
            return self.send_json({"success": True})

        # Referral claim
        if path.endswith("/v1/users/referral/claim"):
            tid, _, _, _ = self.get_caller_user()
            ref = get_user_referral(tid)
            now = datetime.datetime.now(datetime.timezone.utc)
            if ref.get("next_claim_available_at"):
                try:
                    next_t = datetime.datetime.fromisoformat(ref["next_claim_available_at"].replace("Z", "+00:00"))
                    if now < next_t:
                        return self.send_json({
                            "error": "Claim cooldown is active",
                            "next_claim_available_at": ref["next_claim_available_at"]
                        }, status=400)
                except Exception:
                    pass
            if ref.get("referral_earnings_ton", 0.0) <= 0:
                return self.send_json({
                    "error": "No referral earnings to claim",
                    "next_claim_available_at": ref.get("next_claim_available_at")
                }, status=400)

            earned = ref["referral_earnings_ton"]
            set_user_balance(tid, get_user_balance(tid) + earned)
            tid_str = str(tid)
            if "earnings" in REFERRALS_DATA and tid_str in REFERRALS_DATA["earnings"]:
                REFERRALS_DATA["earnings"][tid_str]["unclaimed_ton"] = 0.0
                save_referrals_data(REFERRALS_DATA)
            ref["referral_earnings_ton"] = 0.0
            ref["referral_earnings_usd"] = 0.0
            ref["last_claim_at"] = now.isoformat()
            ref["next_claim_available_at"] = (now + datetime.timedelta(hours=24)).isoformat()
            return self.send_json({
                "success": True,
                "claimed_ton": earned,
                "next_claim_available_at": ref["next_claim_available_at"]
            })

        # Staking claim
        if path.endswith("/v1/users/staking/claim"):
            tid, _, _, _ = self.get_caller_user()
            stk = get_user_staking(tid)
            now = datetime.datetime.now(datetime.timezone.utc)
            if stk.get("next_claim_available_at"):
                try:
                    next_t = datetime.datetime.fromisoformat(stk["next_claim_available_at"].replace("Z", "+00:00"))
                    if now < next_t:
                        return self.send_json({
                            "error": "Claim cooldown is active",
                            "next_claim_available_at": stk["next_claim_available_at"]
                        }, status=400)
                except Exception:
                    pass
            if stk.get("staking_rewards_ton", 0.0) <= 0:
                return self.send_json({
                    "error": "No staking rewards to claim",
                    "next_claim_available_at": stk.get("next_claim_available_at")
                }, status=400)

            earned = stk["staking_rewards_ton"]
            set_user_balance(tid, get_user_balance(tid) + earned)
            stk["total_earned"] = round(stk.get("total_earned", 0.0) + earned, 2)
            stk["staking_rewards_ton"] = 0.0
            stk["staking_rewards_usd"] = 0.0
            stk["last_claim_at"] = now.isoformat()
            stk["next_claim_available_at"] = (now + datetime.timedelta(hours=24)).isoformat()
            return self.send_json({
                "success": True,
                "claimed_ton": earned,
                "next_claim_available_at": stk["next_claim_available_at"]
            })

        # Wallet connect
        if path.endswith("/v1/users/wallet/connect"):
            tid, _, _, _ = self.get_caller_user()
            addr = data.get("wallet_address") or data.get("address")
            if addr:
                USER_CONNECTED_WALLETS[tid] = addr
                print(f"[WALLET] User {tid} connected wallet: {addr}")
            return self.send_json({"wallet_address": addr, "status": "connected"})

        # Wallet disconnect
        if path.endswith("/v1/users/wallet/disconnect"):
            tid, _, _, _ = self.get_caller_user()
            USER_CONNECTED_WALLETS.pop(tid, None)
            print(f"[WALLET] User {tid} disconnected wallet")
            return self.send_json({"wallet_address": None, "status": "disconnected"})

        # Game reactions
        if path.endswith("/v1/game-roll/reactions/add"):
            return self.send_json({"success": True})

        return self.send_json({"success": True})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        # TON Connect manifest handler (Required for Tonkeeper / Telegram Wallet)
        if path == "/tonconnect-manifest.json" or path == "/tonconnect-manifest-dev.json" or path.endswith("/tonconnect-manifest.json"):
            host = self.headers.get("Host", "127.0.0.1:8080")
            proto = "https" if "trycloudflare.com" in host or self.headers.get("X-Forwarded-Proto") == "https" else "http"
            base_origin = f"{proto}://{host}"
            manifest_data = {
                "url": base_origin,
                "name": "Shencas Rolls",
                "iconUrl": f"{base_origin}/android-icon-192x192.png",
                "termsOfServiceUrl": base_origin,
                "privacyPolicyUrl": base_origin
            }
            return self.send_json(manifest_data)
        # Admin panel routes
        if path == "/admin" or path == "/admin/":
            if os.path.exists(ADMIN_HTML_PATH):
                with open(ADMIN_HTML_PATH, "rb") as af:
                    content = af.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                return self.send_json({"error": "Admin panel not found"}, status=404)

        if path == "/admin/api/data":
            # Collect users
            u_list = []
            for uid, udata in USERS_REGISTRY.items():
                u_list.append({
                    "telegram_id": uid,
                    "display_name": udata.get("display_name", "O'yinchi"),
                    "username": udata.get("telegram_username", ""),
                    "balance_ton": get_user_balance(uid),
                    "inventory_count": len(get_user_inventory(uid))
                })
            # Ensure Shen is in list
            if not any(u["telegram_id"] == 6644911092 for u in u_list):
                u_list.insert(0, {
                    "telegram_id": 6644911092,
                    "display_name": "Shen",
                    "username": "shenGorauz",
                    "balance_ton": get_user_balance(6644911092),
                    "inventory_count": len(get_user_inventory(6644911092))
                })

            # Withdrawals queue
            q_file = os.path.join(BASE_DIR, "withdrawals_queue.json")
            wds = []
            if os.path.exists(q_file):
                try:
                    with open(q_file, "r", encoding="utf-8") as qf:
                        wds = json.load(qf)
                except Exception:
                    pass

            # Calculate total commission profit
            tot_comm = 0.0
            tot_ref = 0.0
            for uid_s, e_data in REFERRALS_DATA.get("earnings", {}).items():
                tot_ref += e_data.get("total_earned_ton", 0.0)
                for h in e_data.get("history", []):
                    tot_comm += h.get("commission_ton", 0.0)

            admin_data = {
                "users": u_list,
                "prices": load_admin_prices(),
                "withdrawals": wds[-20:],
                "pvp": PVP_ENGINE.get_game_data(),
                "stats": {
                    "total_commission_ton": round(tot_comm, 2),
                    "total_referral_rewards_ton": round(tot_ref, 2)
                }
            }
            return self.send_json(admin_data)


        if path.startswith("/api/") or path.startswith("/v1/"):
            api_path = path[4:] if path.startswith("/api/") else path

            # User balance
            if api_path.endswith("/v1/users/balance"):
                tid, _, _, _ = self.get_caller_user()
                bal = get_user_balance(tid)
                return self.send_json({
                    "balance_nano": int(bal * 1e9),
                    "balance_ton": bal,
                    "balance_usd": round(bal * 5.0, 2)
                })

            # User wallet
            if api_path.endswith("/v1/users/wallet/info"):
                tid, _, _, _ = self.get_caller_user()
                connected_addr = USER_CONNECTED_WALLETS.get(tid, None)
                return self.send_json({"wallet_address": connected_addr, "recipient": get_project_wallet()})

            # Wallet TON balance (TonAPI orqali haqiqiy balans)
            if api_path.endswith("/v1/users/wallet/balance"):
                params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                user_address = (params.get("userAddress") or params.get("address") or [None])[0]
                if not user_address:
                    tid2, _, _, _ = self.get_caller_user()
                    user_address = USER_CONNECTED_WALLETS.get(tid2, None)
                if not user_address:
                    return self.send_json({"balance_ton": 0.0, "balance_nano": 0})
                try:
                    import urllib.request as _ureq
                    _req = _ureq.Request(
                        f"https://tonapi.io/v2/accounts/{user_address}",
                        headers={"Accept": "application/json", "User-Agent": "RollsGame/1.0"}
                    )
                    with _ureq.urlopen(_req, timeout=5) as _resp:
                        _d = json.loads(_resp.read())
                    nano = int(_d.get("balance", 0))
                    ton_bal = round(nano / 1e9, 4)
                    print(f"[WALLET BALANCE] {user_address[:10]}... = {ton_bal} TON")
                    return self.send_json({"balance_ton": ton_bal, "balance_nano": nano})
                except Exception as e:
                    print(f"[WALLET BALANCE] TonAPI error: {e}")
                    return self.send_json({"balance_ton": 0.0, "balance_nano": 0})

            # User gifts
            if api_path.endswith("/v1/user/gifts/list") or api_path.endswith("/v1/game-roll/gifts-to-add/list") or api_path.endswith("/v1/grand-game-roll/gifts-to-add/list"):
                tid, _, _, _ = self.get_caller_user()
                return self.send_json({
                    "gifts": get_user_inventory(tid),
                    "stickers": []
                })

            # Auto bet progress
            if api_path.endswith("/v1/game-roll/auto-bet/progress"):
                return self.send_json({
                    "has_active_auto_bet": False,
                    "auto_bet_id": None,
                    "amount_ton": None,
                    "total_games": None,
                    "played_games": None,
                    "remaining_games": None,
                    "starts_from_game_num": None
                })

            # Game info (lookup completed game if queried, otherwise active game)
            if api_path.endswith("/v1/game-roll/info") or api_path.endswith("/v1/sticker-roll/info"):
                query = urllib.parse.parse_qs(parsed.query)
                gid = query.get("game_roll_id", [None])[0]
                if gid:
                    if gid == ATH_GAME_DATA["id"]:
                        return self.send_json(ATH_GAME_DATA)
                    match = next((g for g in RECENT_HISTORY if g["id"] == gid), None)
                    if match:
                        return self.send_json(match)
                    if RECENT_HISTORY:
                        return self.send_json(RECENT_HISTORY[0])
                    return self.send_json(ATH_GAME_DATA)
                return self.send_json(PVP_ENGINE.get_game_data())

            if api_path.endswith("/v1/game-roll/active"):
                return self.send_json(PVP_ENGINE.get_game_data())

            if api_path.endswith("/v1/grand-game-roll/active"):
                return self.send_json(GRAND_ENGINE.get_game_data())

            if api_path.endswith("/v1/tournaments/ath-info") or api_path.endswith("/v1/sticker-roll/ath-info"):
                return self.send_json(ATH_GAME_DATA)

            # User stats
            if api_path.endswith("/v1/users/stats"):
                tid, _, _, _ = self.get_caller_user()
                st = get_user_stats(tid)
                return self.send_json({
                    "total_games": st["total_games"],
                    "best_win_ton": st["best_win_ton"],
                    "best_win_usd": round(st["best_win_ton"] * 5.0, 2),
                    "lombard_total_ton": st["lombard_total_ton"],
                    "lombard_total_usd": round(st["lombard_total_ton"] * 5.0, 2)
                })

            # Tasks list
            if api_path.endswith("/v1/tasks/list"):
                return self.send_json({
                    "tasks": [],
                    "completed_count": 0
                })

            # Market filters
            if api_path.endswith("/v1/market/gifts/filters"):
                return self.send_json({
                    "backgrounds": [{"background": "gold"}, {"background": "purple"}, {"background": "cyan"}, {"background": "blue"}],
                    "models": [
                        {"model": "bondedring", "title": "Bonded Ring"},
                        {"model": "diamondring", "title": "Diamond Ring"},
                        {"model": "crystalball", "title": "Crystal Ball"},
                        {"model": "star_locket", "title": "Star Locket"}
                    ],
                    "titles": [
                        {"title": "Bonded Ring", "model": "bondedring"},
                        {"title": "Diamond Ring", "model": "diamondring"},
                        {"title": "Crystal Ball", "model": "crystalball"},
                        {"title": "Star Locket", "model": "star_locket"}
                    ]
                })

            # Market active transactions
            if api_path.endswith("/v1/market/transactions/active"):
                return self.send_json({"transactions": []})

            # Upgrade config
            if api_path.endswith("/v1/upgrade/config"):
                return self.send_json({
                    "enabled": True,
                    "max_chance_percent": 80,
                    "max_source_gifts": 5,
                    "min_direct_ton": 0.1,
                    "max_direct_ton": 100.0,
                    "target_types": ["MARKET_GIFT", "TITLE"]
                })

            # Upgrade live wins
            if api_path.endswith("/v1/upgrade/live-wins"):
                return self.send_json({
                    "items": [
                        {
                            "attempt_id": "att_1",
                            "user_display_name": "Rolls Player",
                            "target": UPGRADE_TARGETS[0],
                            "status": "COMPLETED"
                        }
                    ],
                    "total_count": 1
                })

            # Limbo config
            if api_path.endswith("/v1/limbo/config"):
                return self.send_json({
                    "enabled": True,
                    "chance_presets": [50.0, 25.0, 10.0, 5.0, 2.0],
                    "turbo_enabled": True,
                    "house_edge": 0.02,
                    "min_bet_ton": 0.1,
                    "max_bet_ton": 50.0,
                    "auto_play_max_games": 100,
                    "auto_play_spin_interval_seconds": 1.0
                })

            if api_path.endswith("/v1/limbo/auto-play/active"):
                return self.send_json({"has_active_auto_play": False})

            if api_path.endswith("/v1/limbo/live-wins"):
                return self.send_json([])

            # Crash active
            if api_path.endswith("/v1/crash/active"):
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return self.send_json({
                    "server_time": now_iso,
                    "round": {
                        "id": "crash_round_101",
                        "round_number": 101,
                        "phase": "BETTING",
                        "flight_starts_at": None,
                        "growth_rate": 1.0,
                        "multiplier": 1.0,
                        "revision": 1
                    },
                    "selected_skin_id": "default",
                    "my_position": None,
                    "lobby": [],
                    "recent_multipliers": [1.45, 2.10, 1.15, 3.80, 1.95]
                })

            # Lucky roll active
            if api_path.endswith("/v1/lucky-roll/active"):
                return self.send_json({
                    "round_id": "lucky_101",
                    "status": "BETTING",
                    "total_bet_ton": 0.0,
                    "time_remaining_ms": 15000,
                    "recent_colors": ["RED", "BLACK", "GREEN", "RED"]
                })

            # Mono spin titles
            if api_path.endswith("/v1/mono-spin/titles"):
                return self.send_json({"items": []})

            # Giveaways list
            if api_path.endswith("/v1/giveaways/list"):
                return self.send_json({"giveaways": []})

            # Hide username
            if api_path.endswith("/v1/users/hide-username"):
                return self.send_json({"hide_username": False})

            # Cases config
            if api_path.endswith("/v1/cases/config"):
                return self.send_json({
                    "enabled": True,
                    "stars_enabled": True,
                    "turbo_enabled": True
                })

            # Cases list
            if api_path.endswith("/v1/cases/list"):
                return self.send_json({
                    "items": CASES,
                    "total_count": len(CASES)
                })

            # Cases gifts
            if api_path.endswith("/v1/cases/gifts"):
                return self.send_json({"items": PRIZES})

            # Case details
            if api_path.endswith("/v1/cases/details"):
                query = urllib.parse.parse_qs(parsed.query)
                cid = query.get("case_id", ["free"])[0]
                case = next((c for c in CASES if c["case_id"] == cid), CASES[0])
                return self.send_json({
                    **case,
                    "prizes": PRIZES,
                    "channels": []
                })

            # Cases live wins
            if api_path.endswith("/v1/cases/live-wins"):
                return self.send_json({
                    "items": [
                        {
                            "spin_id": "spin_1",
                            "case_id": "roller",
                            "prize": PRIZES[0],
                            "gift": None
                        }
                    ]
                })

            # Stats active users
            if api_path.endswith("/v1/stats/active-users"):
                return self.send_json({"count": 1420 + random.randint(1, 50)})

            # Tournaments / Leaderboard
            if api_path.endswith("/v1/users/tournaments/daily-pvp/leaderboard/list"):
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                end_iso = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
                return self.send_json({
                    "users": [
                        {
                            "user_info": {
                                "telegram_id": CURRENT_USER["telegram_id"],
                                "display_name": CURRENT_USER["display_name"],
                                "image_url": CURRENT_USER["image_url"],
                                "telegram_username": CURRENT_USER["telegram_username"],
                                "ref_id": f"ref_{CURRENT_USER['telegram_id']}"
                            },
                            "score_ton": 35.0,
                            "score_usd": 175.0,
                            "wins_count": 4,
                            "leaderboard_rank": 1,
                            "last_updated": now_iso
                        }
                    ],
                    "total_count": 1,
                    "my": None,
                    "tournament_number": 42,
                    "tournament_start": now_iso,
                    "tournament_end": end_iso,
                    "is_active": True,
                    "commission_total_ton": 3.5,
                    "pool_total_ton": 35.0,
                    "pool_total_usd": 175.0,
                    "pool_percent": 10.0,
                    "rewards": [],
                    "scoring_mode": "profit"
                })

            # Contest leaderboard
            if api_path.endswith("/v1/users/contest/leaderboard/list"):
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                end_iso = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).isoformat()
                return self.send_json({
                    "users": [],
                    "my": None,
                    "total_count": 0,
                    "contest_start": now_iso,
                    "contest_end": end_iso,
                    "is_active": True,
                    "rewards": [],
                    "gifts": [],
                    "gifts_prize_ids": []
                })

            # Spam-buy preview (PvP)
            if api_path.endswith("/v1/game-roll/spam-buy/preview") or api_path.endswith("/v1/grand-game-roll/spam-buy/preview"):
                return self.send_json({"gifts": []})

            # Bets JSON for Provably Fair History Replay
            if api_path.endswith("/v1/game-roll/bets.json"):
                query = urllib.parse.parse_qs(parsed.query)
                gid = query.get("game_roll_id", [None])[0]
                game = ATH_GAME_DATA if gid == ATH_GAME_DATA["id"] else next((g for g in RECENT_HISTORY if g["id"] == gid), ATH_GAME_DATA)
                return self.send_json({
                    "game_roll_id": game["id"],
                    "game_num": game["game_num"],
                    "hash": game.get("hash"),
                    "seed": game.get("seed"),
                    "bets": game.get("bets_history", []),
                    "winner_telegram_id": game.get("winner_telegram_id"),
                    "winner_display_name": game.get("winner_display_name"),
                    "total_prize_ton": game.get("total_prize_ton")
                })

            # Event Staking Info
            if api_path.endswith("/v1/snow-event/sakura-staking/info"):
                tid, _, _, _ = self.get_caller_user()
                return self.send_json(get_user_event_staking(tid))

            if api_path.endswith("/v1/snow-event/earned-breakdown"):
                tid, _, _, _ = self.get_caller_user()
                ev = get_user_event_staking(tid)
                earned = ev.get("earned", 0.0)
                return self.send_json({
                    "earned_ton": earned,
                    "earned_usd": round(earned * 5.0, 2)
                })

            # Game-roll history & sticker-roll history with rich tab sorting
            if api_path.endswith("/v1/game-roll/history/list") or api_path.endswith("/v1/sticker-roll/history/list"):
                query = urllib.parse.parse_qs(parsed.query)
                sort_by = query.get("sort_by", query.get("sorting", ["date"]))[0]
                default_order = "asc" if sort_by == "win_chance" else "desc"
                sort_order = query.get("sort_order", [default_order])[0]
                limit = int(query.get("limit", [20])[0])
                skip = int(query.get("skip", [0])[0])
                search_q = query.get("search", query.get("game_num", [None]))[0]

                pool = list(RECENT_HISTORY)
                if not any(g["id"] == ATH_GAME_DATA["id"] for g in pool):
                    pool.append(ATH_GAME_DATA)

                if search_q:
                    q_clean = str(search_q).strip().lower().replace("#", "")
                    pool = [g for g in pool if q_clean in str(g.get("game_num", "")).lower() or q_clean in g.get("winner_display_name", "").lower()]

                if sort_by == "cost_ton": # TOP
                    pool = sorted(pool, key=lambda g: float(g.get("total_prize_ton", 0.0)), reverse=(sort_order != "asc"))
                elif sort_by == "win_chance": # LUCKY (lowest win chance first)
                    def get_win_pct(g):
                        tid = str(g.get("winner_telegram_id"))
                        gifts_info = g.get("gifts_by_telegram_id", {}).get(tid, {})
                        return float(gifts_info.get("win_chance_percent", 100.0))
                    pool = sorted(pool, key=get_win_pct, reverse=(sort_order == "desc"))
                elif sort_by == "mine": # YOURS
                    my_tid = CURRENT_USER["telegram_id"]
                    pool = [g for g in pool if g.get("winner_telegram_id") == my_tid]
                elif sort_by == "grand": # GRAND
                    pool = [g for g in pool if g.get("type") == "GRAND" or float(g.get("total_prize_ton", 0.0)) >= 500.0]
                else: # classic / date
                    pool = sorted(pool, key=lambda g: g.get("game_num", 0), reverse=(sort_order != "asc"))

                total_count = len(pool)
                paged_items = pool[skip : skip + limit]
                return self.send_json({
                    "items": paged_items,
                    "total_count": total_count
                })

            if api_path.endswith("/v1/users/referral-info") or api_path.endswith("/v1/users/referral/info"):
                tid, _, _, _ = self.get_caller_user()
                return self.send_json(get_user_referral(tid))

            if api_path.endswith("/v1/users/staking/info"):
                tid, _, _, _ = self.get_caller_user()
                return self.send_json(get_user_staking(tid))

            # Relayer Status
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
            if api_path.endswith("/v1/users/info"):
                tid, dname, uname, photo = self.get_caller_user()
                return self.send_json({
                    "telegram_id": tid,
                    "display_name": dname,
                    "image_url": photo,
                    "telegram_username": uname,
                    "ref_id": str(tid),
                    "perks": []
                })

            # Daily pvp history info
            if api_path.endswith("/v1/users/tournaments/daily-pvp/history/info"):
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                end_iso = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
                return self.send_json({
                    "tournament_number": 42,
                    "tournament_start": now_iso,
                    "tournament_end": end_iso,
                    "settled_at": now_iso,
                    "participants_count": 1,
                    "commission_total_ton": 3.5,
                    "pool_total_ton": 35.0,
                    "pool_total_usd": 175.0,
                    "pool_percent": 10.0,
                    "rewards": [],
                    "winners": []
                })

            # Daily pvp history list
            if api_path.endswith("/v1/users/tournaments/daily-pvp/history/list"):
                return self.send_json({
                    "items": [],
                    "total_count": 0
                })

            # Staking leaderboard list
            if api_path.endswith("/v1/users/staking/leaderboard/list"):
                tid, dname, uname, photo = self.get_caller_user()
                inv = get_user_inventory(tid)
                inv_ton = round(float(sum(g.get("cost_ton", 0.0) for g in inv)), 2)
                my_entry = {
                    "userInfo": {
                        "telegramId": tid,
                        "displayName": dname,
                        "telegramUsername": uname
                    },
                    "leaderboardRank": 2,
                    "giftCount": len(inv),
                    "inventoryTon": inv_ton
                }
                users = [
                    {
                        "userInfo": {"telegramId": 1001002, "displayName": "CryptoWhale", "telegramUsername": "cryptowhale"},
                        "leaderboardRank": 1,
                        "giftCount": 18,
                        "inventoryTon": 320.0
                    },
                    my_entry,
                    {
                        "userInfo": {"telegramId": 1001001, "displayName": "Sardor (TON)", "telegramUsername": "sardor_ton"},
                        "leaderboardRank": 3,
                        "giftCount": 12,
                        "inventoryTon": 195.0
                    },
                    {
                        "userInfo": {"telegramId": 1001003, "displayName": "Ali_Roll", "telegramUsername": "ali_roll"},
                        "leaderboardRank": 4,
                        "giftCount": 7,
                        "inventoryTon": 110.0
                    },
                    {
                        "userInfo": {"telegramId": 1001004, "displayName": "Tashkent_Ton", "telegramUsername": "tashkent_ton"},
                        "leaderboardRank": 5,
                        "giftCount": 5,
                        "inventoryTon": 75.0
                    }
                ]
                return self.send_json({
                    "users": users,
                    "my": my_entry,
                    "total_count": len(users)
                })

            # Topups list
            if api_path.endswith("/v1/users/balance/topups"):
                tid, _, _, _ = self.get_caller_user()
                return self.send_json({"topups": USER_TOPUPS.get(tid, [])})

            # Legit check (Provably Fair)
            if api_path.endswith("/v1/game-roll/legit-check") or api_path.endswith("/v1/sticker-roll/legit-check"):
                query = urllib.parse.parse_qs(parsed.query)
                gid = query.get("game_roll_id", ["game_roll_1420"])[0]
                return self.send_json({
                    "is_legit": True,
                    "server_seed_hash": "d3b07384d113edec49eaa6238ad5ff00b7e52a912061e86dbfa66847a98ec21",
                    "client_seed": f"rolls_client_seed_{gid}",
                    "nonce": 1
                })

            return self.send_json({})

        # Redirect clean /upgrade to /solo/upgrade
        if path == "/upgrade":
            self.send_response(302)
            self.send_header("Location", "/solo/upgrade")
            self.end_headers()
            return

        # Redirect /market to /profile
        if path == "/market" or path == "/market/":
            self.send_response(302)
            self.send_header("Location", "/profile")
            self.end_headers()
            return

        # Static files handling with proper 404 vs SPA fallback
        rel_path = path.lstrip("/")
        local_file = os.path.join(PUBLIC_DIR, rel_path.replace("/", os.sep))

        if os.path.isfile(local_file):
            return super().do_GET()

        # Specific file extensions MUST return 404
        _, ext = os.path.splitext(path)
        if ext and ext.lower() not in [".html"]:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')
            return

        # SPA fallback for clean Nuxt routes (/solo, /profile, /cases, /market, /solo/upgrade, etc.)
        index_path = os.path.join(PUBLIC_DIR, "index.html")
        with open(index_path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)


def cryptopay_worker():
    while True:
        try:
            # 1. Check CryptoBot paid invoices
            paid_items = check_paid_invoices()
            for p in paid_items:
                tid = p["telegram_id"]
                amt = p["amount"]
                new_bal = round(get_user_balance(tid) + amt, 2)
                set_user_balance(tid, new_bal)
                print(f"[CRYPTOPAY] 🎉 CONFIRMED REAL PAYMENT! User {tid} credited +{amt} Gram (New Bal: {new_bal} Gram)")
                for rec in USER_TOPUPS.get(tid, []):
                    if str(rec.get("invoice_id")) == str(p["invoice_id"]):
                        rec["status"] = "COMPLETED"
                        rec["paid_at"] = p.get("paid_at")
                        
            # 2. Check On-Chain TON Blockchain payments to owner wallet
            onchain_items = check_incoming_blockchain_transactions()
            for oc in onchain_items:
                oc_tid = oc.get("telegram_id") or CURRENT_USER.get("telegram_id", 6644911092)
                oc_amt = oc.get("amount_ton", 0.0)
                if oc_amt > 0:
                    new_bal = round(get_user_balance(oc_tid) + oc_amt, 2)
                    set_user_balance(oc_tid, new_bal)
                    topup_record = {
                        "id": f"tx_{oc.get('tx_hash')[:16]}",
                        "tx_hash": oc.get("tx_hash"),
                        "amount_ton": oc_amt,
                        "currency": "Gram",
                        "status": "COMPLETED",
                        "method": "TON On-Chain Wallet",
                        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
                    USER_TOPUPS.setdefault(oc_tid, []).insert(0, topup_record)
                    print(f"[ON-CHAIN WALLET] 🎉 REAL BLOCKCHAIN DEPOSIT: +{oc_amt} TON received on {get_project_wallet()} for user {oc_tid}!")
        except Exception as e:
            pass
        time.sleep(5)

threading.Thread(target=cryptopay_worker, daemon=True).start()

class ThreadingRollsServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run():
    server = ThreadingRollsServer(("0.0.0.0", 8080), RollsGameHandler)
    print("Serving pure Rolls replica on http://0.0.0.0:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
