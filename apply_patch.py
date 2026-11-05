import sys

path = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\server.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target1 = '        if path.startswith("/api/"):\n            api_path = path[4:]'
target1_crlf = '        if path.startswith("/api/"):\r\n            api_path = path[4:]'

replace1 = '        if path.startswith("/api/") or path.startswith("/v1/"):\n            api_path = path[4:] if path.startswith("/api/") else path'
replace1_crlf = '        if path.startswith("/api/") or path.startswith("/v1/"):\r\n            api_path = path[4:] if path.startswith("/api/") else path'

target2 = '            new_uid = data.get("user_id")\n            dname = data.get("display_name", "Friend")'
target2_crlf = '            new_uid = data.get("user_id")\r\n            dname = data.get("display_name", "Friend")'

replace2 = '            new_uid = data.get("user_id") or data.get("new_user_id")\n            dname = data.get("display_name") or data.get("name", "Friend")'
replace2_crlf = '            new_uid = data.get("user_id") or data.get("new_user_id")\r\n            dname = data.get("display_name") or data.get("name", "Friend")'

if target1_crlf in text:
    text = text.replace(target1_crlf, replace1_crlf)
    print("Replaced target1 CRLF")
elif target1 in text:
    text = text.replace(target1, replace1)
    print("Replaced target1 LF")

if target2_crlf in text:
    text = text.replace(target2_crlf, replace2_crlf)
    print("Replaced target2 CRLF")
elif target2 in text:
    text = text.replace(target2, replace2)
    print("Replaced target2 LF")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Patch applied to server.py!")
