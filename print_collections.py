import sys
sys.path.append(r'C:\Users\т\.gemini\antigravity\scratch\rolls-game')
import market_price_engine

sys.stdout.reconfigure(encoding='utf-8')
cache = market_price_engine._MARKET_CACHE
print('Collections count:', len(cache.get('collections', {})))
print('Models count:', len(cache.get('models', {})))

print('\nReal Collections in Telegram:')
for name, data in list(cache.get('collections', {}).items())[:30]:
    print(f" - {name}: floor {data.get('floor')} TON")
