import os
import json
import time
import urllib.request
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "market_prices_cache.json")
TGGIFTS_MODELS_URL = "https://tggifts.com/data/models-daily.json"
TGGIFTS_FLOORS_URL = "https://tggifts.com/data/floors-daily.json"

# In-memory store
_MARKET_CACHE = {
    "last_updated": 0,
    "collections": {},  # slug -> { name, floor_gram, source }
    "models": {},       # f"{col_slug}:{model_slug}" -> { name, floor_gram, source }
}

def normalize_key(s):
    if not s:
        return ""
    return "".join(c for c in s.lower() if c.isalnum())

def fetch_live_market_floors():
    """
    Fetches real-time / daily cheapest floor prices directly from
    Telegram NFT trackers (Fragment / TG Gifts / see.tg style indexers).
    Picks the lowest active floor price (eng arzoni).
    """
    global _MARKET_CACHE
    print("[MARKET ENGINE] Fetching latest live NFT floors from market indexer...")
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    collections_data = {}
    models_data = {}

    # 1. Fetch collection-level floors
    try:
        req = urllib.request.Request(TGGIFTS_FLOORS_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for col_slug, info in data.get("collections", {}).items():
                name = info.get("name", col_slug)
                days = info.get("days", [])
                latest = days[-1] if days else None
                # latest format: [date, floor_gram, recent_sales]
                floor_gram = float(latest[1]) if latest and len(latest) > 1 and latest[1] is not None else 0.0
                if floor_gram > 0:
                    norm_k = normalize_key(col_slug)
                    collections_data[norm_k] = {
                        "slug": col_slug,
                        "name": name,
                        "floor_gram": floor_gram,
                        "date": latest[0] if latest else "",
                        "source": "Fragment / TG Gifts"
                    }
        print(f"[MARKET ENGINE] Loaded {len(collections_data)} collection floors.")
    except Exception as e:
        print(f"[MARKET ENGINE] Collection fetch error: {e}")

    # 2. Fetch model-level floors (cheapest buy-now per model)
    try:
        req = urllib.request.Request(TGGIFTS_MODELS_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for col_slug, c_info in data.get("collections", {}).items():
                col_name = c_info.get("name", col_slug)
                col_norm = normalize_key(col_slug)
                for m_name, m_info in c_info.get("models", {}).items():
                    m_slug = m_info.get("slug", m_name)
                    days = m_info.get("days", [])
                    latest = days[-1] if days else None
                    # latest format: [date, floor_gram, listings]
                    floor_gram = float(latest[1]) if latest and len(latest) > 1 and latest[1] is not None else 0.0
                    if floor_gram > 0:
                        m_norm = normalize_key(m_name)
                        key = f"{col_norm}:{m_norm}"
                        models_data[key] = {
                            "collection": col_name,
                            "collection_slug": col_slug,
                            "model_name": m_name,
                            "model_slug": m_slug,
                            "floor_gram": floor_gram,
                            "date": latest[0] if latest else "",
                            "source": "Fragment / TG Gifts"
                        }
        print(f"[MARKET ENGINE] Loaded {len(models_data)} model-specific floors.")
    except Exception as e:
        print(f"[MARKET ENGINE] Model fetch error: {e}")

    if collections_data:
        _MARKET_CACHE["last_updated"] = time.time()
        _MARKET_CACHE["collections"] = collections_data
        _MARKET_CACHE["models"] = models_data
        
        # Save cache to disk
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(_MARKET_CACHE, f, indent=2)
            print(f"[MARKET ENGINE] Successfully saved market cache to {CACHE_FILE}")
        except Exception as e:
            print(f"[MARKET ENGINE] Error saving cache: {e}")
            
    return _MARKET_CACHE

def load_cached_market():
    global _MARKET_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _MARKET_CACHE = json.load(f)
                return _MARKET_CACHE
        except Exception:
            pass
    return fetch_live_market_floors()

def get_nft_lowest_floor(title="", model="", collection="", fallback=10.0):
    """
    Finds the cheapest / lowest floor price (Gram) for a given Telegram NFT gift.
    Rule 2: 'eng arzoni' (Cheapest available market floor).
    Rule 3: Non-NFT gifts are excluded.
    """
    cache = _MARKET_CACHE
    if not cache.get("collections") or time.time() - cache.get("last_updated", 0) > 3600 * 6:
        cache = load_cached_market()

    col_k = normalize_key(collection) or normalize_key(title)
    mod_k = normalize_key(model)
    
    # 1. Exact model match: e.g. "resistancedog:satoshi" or "algorithmcup:gold"
    if col_k and mod_k:
        combo_key = f"{col_k}:{mod_k}"
        if combo_key in cache.get("models", {}):
            return cache["models"][combo_key]["floor_gram"], cache["models"][combo_key]

    # 2. Check title against models
    full_str = f"{title} {model} {collection}".lower()
    for m_key, m_val in cache.get("models", {}).items():
        m_name_lower = m_val["model_name"].lower()
        c_name_lower = m_val["collection"].lower()
        if m_name_lower in full_str and (c_name_lower in full_str or m_val["collection_slug"] in full_str):
            return m_val["floor_gram"], m_val

    # 3. Check collection floor
    for c_key, c_val in cache.get("collections", {}).items():
        c_name_lower = c_val["name"].lower()
        c_slug_lower = c_val["slug"].lower()
        if c_name_lower in full_str or c_slug_lower in full_str or c_key in full_str.replace(" ", ""):
            return c_val["floor_gram"], c_val

    # 4. Fallback if not listed yet on Fragment
    return float(fallback), {"source": "Fallback baseline", "floor_gram": float(fallback)}

if __name__ == "__main__":
    fetch_live_market_floors()
    
    # Test lookups
    test_cases = [
        ("Resistance Dog", "Satoshi"),
        ("Resistance Dog", "Sheikh"),
        ("Algorithm Cup", "Gold"),
        ("Artisan Brick", "Chocolate"),
        ("Astral Shard", "Gold 999"),
        ("Pepe Crown", ""),
        ("Lucky Locket", "")
    ]
    
    print("\n--- TEST LIVE FLOOR LOOKUPS (Gram) ---")
    for col, mod in test_cases:
        price, details = get_nft_lowest_floor(collection=col, model=mod)
        print(f"🎁 {col} ({mod}) => {price} Gram (Source: {details.get('source')})")
