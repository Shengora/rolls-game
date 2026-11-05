import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\т\.gemini\antigravity\scratch\rolls-game\public\_nuxt\ZEhFy-gV.js', 'r', encoding='utf-8') as f:
    text = f.read()

for s in ['BR=', 'MN=', 'hO=', 'QO=']:
    idx = text.find(s)
    if idx != -1:
        print(f"=== {s} ===")
        print(text[idx:idx+300])
