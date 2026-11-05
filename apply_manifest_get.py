import os

server_py = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\server.py"

with open(server_py, "r", encoding="utf-8") as f:
    content = f.read()

manifest_block = '''        # TON Connect manifest handler (Required for Tonkeeper / Telegram Wallet)
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
'''

# 1. Clean up from do_POST if present
content = content.replace(manifest_block, "")

# 2. Add to do_GET
target_get = "    def do_GET(self):\n        parsed = urllib.parse.urlparse(self.path)\n        path = parsed.path\n"
if target_get in content:
    content = content.replace(target_get, target_get + manifest_block)
    print("Success: added to do_GET (LF)")
else:
    # try CRLF
    target_get_crlf = "    def do_GET(self):\r\n        parsed = urllib.parse.urlparse(self.path)\r\n        path = parsed.path\r\n"
    if target_get_crlf in content:
        content = content.replace(target_get_crlf, target_get_crlf + manifest_block.replace("\n", "\r\n"))
        print("Success: added to do_GET (CRLF)")
    else:
        print("Failed to find target in do_GET")

with open(server_py, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated server.py")
