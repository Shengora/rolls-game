import subprocess
import time
import json
import urllib.request
import asyncio
import sys
import base64

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import websockets

async def check():
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    p = subprocess.Popen([edge, '--headless', '--remote-debugging-port=9222', '--disable-gpu', '--window-size=390,844', 'http://127.0.0.1:8080/'])
    await asyncio.sleep(2)
    try:
        tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode('utf-8'))
        tab = [t for t in tabs if t.get('type') == 'page'][0]
        async with websockets.connect(tab['webSocketDebuggerUrl']) as ws:
            await ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
            
            # Watch for 25 seconds (one full PvP cycle)
            print("Watching PvP Roulette for 25 seconds...")
            for i in range(5):
                await asyncio.sleep(5)
                await ws.send(json.dumps({
                    'id': 10 + i,
                    'method': 'Runtime.evaluate',
                    'params': {'expression': 'document.body.innerText'}
                }))
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get('id') == 10 + i:
                        text = data.get('result', {}).get('result', {}).get('value', '').replace('\n', ' ')
                        print(f"[{i*5}s] Text snippet: {text[:160]}")
                        break

            # Capture screenshot
            await ws.send(json.dumps({'id': 99, 'method': 'Page.captureScreenshot'}))
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get('id') == 99:
                    img = base64.b64decode(data['result']['data'])
                    with open(r'C:\Users\т\.gemini\antigravity\brain\a1451e9d-61b6-45c6-9c09-08e252daf531\screenshot_pvp_stable.png', 'wb') as f:
                        f.write(img)
                    print("Saved screenshot_pvp_stable.png")
                    break
    finally:
        p.terminate()

asyncio.run(check())
