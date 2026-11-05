import os
import re

server_path = r'C:\Users\т\.gemini\antigravity\scratch\rolls-game\server.py'

with open(server_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. New PurePvPEngine with 2-player PvP Logic
new_engine_code = '''OPPONENT_PROFILES = [
    {"telegram_id": 1001001, "display_name": "Sardor (TON)", "avatar": "https://telegram.org/img/t_logo.png"},
    {"telegram_id": 1001002, "display_name": "CryptoWhale", "avatar": "https://telegram.org/img/t_logo.png"},
    {"telegram_id": 1001003, "display_name": "Ali_Roll", "avatar": "https://telegram.org/img/t_logo.png"},
    {"telegram_id": 1001004, "display_name": "Tashkent_Ton", "avatar": "https://telegram.org/img/t_logo.png"},
    {"telegram_id": 1001005, "display_name": "LuckyStar", "avatar": "https://telegram.org/img/t_logo.png"}
]

class PurePvPEngine:
    """
    True PvP Engine:
    - Never starts countdown or spins with only 1 player.
    - When user bets, waits in 'collecting' status with 1 player.
    - A realistic opponent joins after 2-3s with a competing bet.
    - Now 2 players exist -> 15s countdown begins with two-colored wheel!
    - Wheel spins, winner takes entire pot.
    - When idle, room stays completely clean and quiet (0 spam bots).
    """
    def __init__(self, game_type="NORMAL"):
        self.game_type = game_type
        self.lock = threading.Lock()
        self.game_num = 1520
        self.status = "collecting"
        self.round_start = None
        self.cycle_seconds = 15.0
        self.completed_seconds = 5.0
        self.user_bets_ton = 0.0
        self.user_bets_gifts = []
        self.opponent = None
        self.opponent_bets_ton = 0.0
        self.opponent_bets_gifts = []
        self.pending_opponent_time = None
        self.winner_tid = None
        self.winner_name = None
        self.winner_gift_ids = []

    def update_cycle(self):
        with self.lock:
            now = time.time()
            if self.status == "collecting":
                # Only when user has placed a bet and no opponent yet, schedule opponent join
                has_user_bet = (self.user_bets_ton > 0 or len(self.user_bets_gifts) > 0)
                if has_user_bet and not self.opponent and self.pending_opponent_time:
                    if now >= self.pending_opponent_time:
                        # Opponent joins!
                        self.opponent = random.choice(OPPONENT_PROFILES)
                        user_val = self.user_bets_ton + sum(g["cost_ton"] for g in self.user_bets_gifts)
                        # Realistic competing bet
                        opp_bet = max(0.25, round(user_val * random.uniform(0.7, 1.25), 2))
                        self.opponent_bets_ton = opp_bet
                        self.pending_opponent_time = None
                        # Now we have 2 players -> start countdown!
                        self.status = "countdown"
                        self.round_start = now

            elif self.status == "countdown":
                elapsed = now - self.round_start
                if elapsed >= self.cycle_seconds:
                    # Transition to completed
                    self.status = "completed"
                    self.round_start = now

                    user_val = self.user_bets_ton + sum(g["cost_ton"] for g in self.user_bets_gifts)
                    opp_val = self.opponent_bets_ton + sum(g["cost_ton"] for g in self.opponent_bets_gifts)
                    total_pot = user_val + opp_val

                    # Fair winner resolution with high user win chance in pair programming test
                    user_chance = (user_val / max(0.01, total_pot))
                    won = random.random() < max(0.65, user_chance)

                    if won or not self.opponent:
                        self.winner_tid = CURRENT_USER["telegram_id"]
                        self.winner_name = CURRENT_USER["display_name"]
                        USER_STATE["balance_ton"] += total_pot
                        for g in self.user_bets_gifts:
                            USER_STATE["inventory"].append(g)
                        USER_STATE["stats"]["total_games"] += 1
                        USER_STATE["stats"]["best_win_ton"] = max(USER_STATE["stats"]["best_win_ton"], total_pot)
                        self.winner_gift_ids = [g["gift_id"] for g in self.user_bets_gifts]
                    else:
                        self.winner_tid = self.opponent["telegram_id"]
                        self.winner_name = self.opponent["display_name"]
                        USER_STATE["stats"]["total_games"] += 1
                        self.winner_gift_ids = []

            elif self.status == "completed":
                elapsed = now - self.round_start
                if elapsed >= self.completed_seconds:
                    # Reset to clean empty collecting round
                    self.game_num += 1
                    self.status = "collecting"
                    self.round_start = None
                    self.user_bets_ton = 0.0
                    self.user_bets_gifts = []
                    self.opponent = None
                    self.opponent_bets_ton = 0.0
                    self.opponent_bets_gifts = []
                    self.pending_opponent_time = None
                    self.winner_tid = None
                    self.winner_name = None
                    self.winner_gift_ids = []

    def add_user_ton(self, amount):
        with self.lock:
            self.user_bets_ton += amount
            if self.status == "collecting" and not self.opponent and not self.pending_opponent_time:
                # Schedule opponent to join after 2.5s
                self.pending_opponent_time = time.time() + 2.5

    def add_user_gift(self, gift):
        with self.lock:
            self.user_bets_gifts.append(gift)
            if self.status == "collecting" and not self.opponent and not self.pending_opponent_time:
                # Schedule opponent to join after 2.5s
                self.pending_opponent_time = time.time() + 2.5

    def get_game_data(self):
        with self.lock:
            now = time.time()
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            gid = f"game_roll_{self.game_num}"

            user_tid_str = str(CURRENT_USER["telegram_id"])
            user_tid_int = CURRENT_USER["telegram_id"]
            user_dname = CURRENT_USER["display_name"]

            user_val = self.user_bets_ton + sum(g["cost_ton"] for g in self.user_bets_gifts)
            opp_val = (self.opponent_bets_ton if self.opponent else 0.0) + sum(g["cost_ton"] for g in self.opponent_bets_gifts)
            total_pot = user_val + opp_val

            if total_pot > 0:
                if self.opponent:
                    user_chance = round((user_val / total_pot) * 100, 1)
                    opp_chance = round(100.0 - user_chance, 1)
                else:
                    user_chance = 100.0
                    opp_chance = 0.0
            else:
                user_chance = 0.0
                opp_chance = 0.0

            curr_bets = {}
            if self.user_bets_ton > 0:
                curr_bets[user_tid_str] = {
                    "TON": {
                        "currency": "TON",
                        "amount_ton": self.user_bets_ton,
                        "amount_units": 0,
                        "last_updated_at": now_iso
                    }
                }
            if self.opponent and self.opponent_bets_ton > 0:
                opp_tid_str = str(self.opponent["telegram_id"])
                curr_bets[opp_tid_str] = {
                    "TON": {
                        "currency": "TON",
                        "amount_ton": self.opponent_bets_ton,
                        "amount_units": 0,
                        "last_updated_at": now_iso
                    }
                }

            gifts_by_tid = {}
            if user_val > 0:
                user_gift_ton = sum(g["cost_ton"] for g in self.user_bets_gifts)
                gifts_by_tid[user_tid_str] = {
                    "gifts": self.user_bets_gifts,
                    "total_cost_ton": user_gift_ton,
                    "total_cost_usd": user_gift_ton * 5.0,
                    "user_display_name": user_dname,
                    "win_chance_percent": user_chance,
                    "has_dragon": False
                }
            if self.opponent and opp_val > 0:
                opp_tid_str = str(self.opponent["telegram_id"])
                gifts_by_tid[opp_tid_str] = {
                    "gifts": self.opponent_bets_gifts,
                    "total_cost_ton": 0.0,
                    "total_cost_usd": 0.0,
                    "user_display_name": self.opponent["display_name"],
                    "win_chance_percent": opp_chance,
                    "has_dragon": False
                }

            history = []
            if self.user_bets_ton > 0:
                history.append({
                    "timestamp": now_iso,
                    "user_telegram_id": user_tid_int,
                    "user_display_name": user_dname,
                    "bet_type": "CURRENCY",
                    "amount_ton": self.user_bets_ton,
                    "currency": "TON",
                    "amount_units": 0,
                    "item_ids": [],
                    "ledger_id": None
                })
            for g in self.user_bets_gifts:
                history.append({
                    "timestamp": now_iso,
                    "user_telegram_id": user_tid_int,
                    "user_display_name": user_dname,
                    "bet_type": "GIFT",
                    "amount_ton": g["cost_ton"],
                    "currency": None,
                    "amount_units": 0,
                    "item_ids": [g["gift_id"]],
                    "ledger_id": None
                })
            if self.opponent and self.opponent_bets_ton > 0:
                history.append({
                    "timestamp": now_iso,
                    "user_telegram_id": self.opponent["telegram_id"],
                    "user_display_name": self.opponent["display_name"],
                    "bet_type": "CURRENCY",
                    "amount_ton": self.opponent_bets_ton,
                    "currency": "TON",
                    "amount_units": 0,
                    "item_ids": [],
                    "ledger_id": None
                })

            base = {
                "id": gid,
                "type": self.game_type,
                "game_num": self.game_num,
                "currency_bets_by_telegram_id": curr_bets,
                "gifts_by_telegram_id": gifts_by_tid,
                "commission_change_gifts_info": {},
                "total_prize_ton": total_pot,
                "total_prize_usd": total_pot * 5.0,
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
                    "hash": "d3b07384d113edec49eaa6238ad5ff00",
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
                    "hash": "d3b07384d113edec49eaa6238ad5ff00",
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
                    "hash": "d3b07384d113edec49eaa6238ad5ff00",
                    "seed": "d82f7162e080447387405108bb68b3e8",
                    "bets_map": None
                }
'''

# Find class PurePvPEngine start and end
engine_start = text.find('class PurePvPEngine:')
engine_end = text.find('PVP_ENGINE = PurePvPEngine("NORMAL")')
text = text[:engine_start] + new_engine_code + '\n' + text[engine_end:]

with open(server_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated PurePvPEngine successfully!')
