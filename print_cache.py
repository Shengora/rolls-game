import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

fpath = os.path.join(os.path.dirname(__file__), 'market_prices_cache.json')
with open(fpath, 'r', encoding='utf-8') as f:
    data = json.load(f)

cols = data.get('collections', {})
print('Cached collections count:', len(cols))
for k in list(cols.keys())[:30]:
    c = cols[k]
    print(f" - {c.get('name')} (slug: {c.get('slug')}): {c.get('floor_gram')} TON / Gram")
