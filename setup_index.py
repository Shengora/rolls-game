path = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public\index.html"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

mock_tag = '<script src="/telegram-mock.js"></script>'
if mock_tag not in content:
    content = content.replace("<head>", f"<head>\n{mock_tag}", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Mock script successfully injected into index.html")
else:
    print("Mock script already present")
