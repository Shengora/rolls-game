import subprocess
import time
import json
import urllib.request
import asyncio
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import websockets

async def run():
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    temp_profile = r'C:\Users\т\.gemini\antigravity\scratch\rolls-game\edge_diag_profile'
    
    p = subprocess.Popen([
        edge,
        '--headless',
        '--remote-debugging-port=9222',
        f'--user-data-dir={temp_profile}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-gpu',
        '--window-size=390,844',
        'http://127.0.0.1:8080/'
    ])
    try:
        await asyncio.sleep(2.5)
        resp = urllib.request.urlopen('http://127.0.0.1:9222/json')
        tabs = json.loads(resp.read().decode('utf-8'))
        tab = [t for t in tabs if t.get('type') == 'page'][0]
        ws_url = tab['webSocketDebuggerUrl']

        async with websockets.connect(ws_url) as ws:
            msg_id = 1
            async def send(method, params=None):
                nonlocal msg_id
                mid = msg_id
                msg_id += 1
                await ws.send(json.dumps({'id': mid, 'method': method, 'params': params or {}}))

            await send('Page.enable')
            await send('Runtime.enable')

            api_errors = []

            async def listen():
                try:
                    async for raw in ws:
                        d = json.loads(raw)
                        if d.get('method') == 'Runtime.consoleAPICalled':
                            args = d.get('params', {}).get('args', [])
                            txt = ' '.join(str(a.get('value', '')) for a in args)
                            if 'API_VALIDATION_ERROR' in txt:
                                print(">>> " + txt, flush=True)
                                api_errors.append(txt)
                except Exception:
                    pass

            lt = asyncio.create_task(listen())

            await asyncio.sleep(3)

            # Test pages
            pages = ['/', '/profile', '/daily-pvp-tournament', '/profile/lombard', '/profile/inventory', '/profile/referral', '/profile/staking', '/profile/tasks']
            for pg in pages:
                print(f"--- Navigating to {pg} ---", flush=True)
                await send('Page.navigate', {'url': f'http://127.0.0.1:8080{pg}'})
                await asyncio.sleep(3)

            lt.cancel()

    finally:
        p.terminate()

asyncio.run(run())
