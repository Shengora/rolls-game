with open("C:/Users/т/.gemini/antigravity/scratch/rolls-game/relayer.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('                return"\n', '                return\n')
c = c.replace('                return"\r\n', '                return\r\n')

with open("C:/Users/т/.gemini/antigravity/scratch/rolls-game/relayer.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Fixed syntax error in relayer.py")
