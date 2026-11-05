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

async def check_button():
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    p = subprocess.Popen([edge, '--headless', '--remote-debugging-port=9222', '--disable-gpu', '--window-size=390,844', 'http://127.0.0.1:8080/'])
    await asyncio.sleep(2)
    try:
        tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode('utf-8'))
        tab = [t for t in tabs if t.get('type') == 'page'][0]
        async with websockets.connect(tab['webSocketDebuggerUrl']) as ws:
            await ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
            await asyncio.sleep(3)

            for i in range(10):
                await ws.send(json.dumps({
                    'id': 100 + i,
                    'method': 'Runtime.evaluate',
                    'params': {'expression': 'Array.from(document.querySelectorAll("button")).map(b => b.innerText.trim()).filter(x => x.length > 0)'},
                    'returnByValue': True
                }))
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get('id') == 100 + i:
                        btns = data.get('result', {}).get('result', {}).get('value', [])
                        pvp_btns = [b for b in btns if any(k in b.lower() for k in ['pvp', 'add', 'roll', 'wait', 'next', 'gram'])]
                        print(f"Step {i+1}:", pvp_btns)
                        break
                await asyncio.sleep(2)
    finally:
        p.terminate()

asyncio.run(check_button())
