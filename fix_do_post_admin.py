import os

path = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\server.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

bad_post = '''    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
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


        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b""
        data = {}
        if body:
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                pass'''

fixed_post = '''    def do_POST(self):
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
            return self.send_json({"error": "Missing telegram_id"}, status=400)'''

if bad_post in text:
    text = text.replace(bad_post, fixed_post)
    print("Fixed do_POST LF!")
else:
    bad_crlf = bad_post.replace('\n', '\r\n')
    fixed_crlf = fixed_post.replace('\n', '\r\n')
    if bad_crlf in text:
        text = text.replace(bad_crlf, fixed_crlf)
        print("Fixed do_POST CRLF!")
    else:
        print("bad_post not found directly, searching...")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("Updated server.py!")
