import subprocess
import time
import json
import urllib.request
import asyncio
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import websockets

TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/"

async def check_page():
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    proc = subprocess.Popen([
        edge_path,
        "--headless",
        "--remote-debugging-port=9222",
        "--disable-gpu",
        TARGET_URL
    ])
    
    await asyncio.sleep(4)
    
    try:
        req = urllib.request.urlopen("http://127.0.0.1:9222/json")
        tabs = json.loads(req.read().decode("utf-8"))
        page_tabs = [t for t in tabs if t.get("type") == "page"]
        if not page_tabs:
            print("No page tab found!")
            return
        page_tab = page_tabs[0]
        ws_url = page_tab["webSocketDebuggerUrl"]
        print("Connecting to CDP:", ws_url)
        
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            await ws.send(json.dumps({"id": 2, "method": "Log.enable"}))
            
            start = time.time()
            while time.time() - start < 7:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(msg)
                    method = data.get("method", "")
                    
                    if "consoleAPICalled" in method:
                        args = [str(a.get("value", a.get("description", ""))) for a in data["params"]["args"]]
                        print(f"[CONSOLE {data['params']['type']}]", " ".join(args))
                    elif "exceptionThrown" in method:
                        desc = str(data["params"]["exceptionDetails"].get("exception", {}).get("description", ""))
                        text = str(data["params"]["exceptionDetails"].get("text", ""))
                        msg = f"[EXCEPTION] {text}: {desc}".encode("ascii", errors="replace").decode("ascii")
                        print(msg)
                except asyncio.TimeoutError:
                    pass
                    
            async def eval_js(msg_id, expr):
                await ws.send(json.dumps({
                    "id": msg_id,
                    "method": "Runtime.evaluate",
                    "params": {"expression": expr}
                }))
                while True:
                    m = json.loads(await ws.recv())
                    if m.get("id") == msg_id:
                        return m.get("result", {}).get("result", {}).get("value", "")

            nuxt_len = await eval_js(10, "document.getElementById('__nuxt')?.innerHTML?.length || 0")
            print(f"\n[NUXT HTML LENGTH]: {nuxt_len}")

            body_text = await eval_js(11, "document.body.innerText")
            print(f"[BODY INNER TEXT]:\n{body_text[:300]}")

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(check_page())
