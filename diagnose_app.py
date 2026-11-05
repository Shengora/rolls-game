import subprocess
import time
import json
import urllib.request
import asyncio
import base64
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import websockets

class CDPClient:
    def __init__(self, ws):
        self.ws = ws
        self.msg_id = 1
        self.pending = {}
        self.console_logs = []
        self.network_errors = []
        self.loop_task = asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for raw in self.ws:
                data = json.loads(raw)
                if 'id' in data and data['id'] in self.pending:
                    self.pending[data['id']].set_result(data)
                elif 'method' in data:
                    m = data['method']
                    if 'Console' in m or 'Log' in m:
                        self.console_logs.append(data.get('params', {}))
                    elif m == 'Runtime.consoleAPICalled':
                        self.console_logs.append(data.get('params', {}))
                    elif m == 'Runtime.exceptionThrown':
                        self.console_logs.append({'exception': data.get('params', {}).get('exceptionDetails')})
                    elif m == 'Network.responseReceived':
                        resp = data.get('params', {}).get('response', {})
                        if resp.get('status', 0) >= 400:
                            self.network_errors.append({'status': resp['status'], 'url': resp['url']})
        except asyncio.CancelledError:
            pass
        except Exception as e:
            pass

    async def send(self, method, params=None):
        mid = self.msg_id
        self.msg_id += 1
        fut = asyncio.get_event_loop().create_future()
        self.pending[mid] = fut
        payload = {'id': mid, 'method': method}
        if params:
            payload['params'] = params
        await self.ws.send(json.dumps(payload))
        res = await fut
        del self.pending[mid]
        return res

    async def close(self):
        self.loop_task.cancel()

async def run():
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    temp_profile = r'C:\Users\т\.gemini\antigravity\scratch\rolls-game\edge_diag_profile'
    os.makedirs(temp_profile, exist_ok=True)
    
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
            cdp = CDPClient(ws)
            await cdp.send('Page.enable')
            await cdp.send('Runtime.enable')
            await cdp.send('Console.enable')
            await cdp.send('Network.enable')

            await asyncio.sleep(3)

            # 1. Elements on PvP
            pvp_elements_expr = """
            (() => {
                const buttons = Array.from(document.querySelectorAll('button, [role=\"button\"]')).map((b, i) => ({
                    index: i,
                    text: b.innerText.trim().replace(/\\n/g, ' '),
                    tag: b.tagName
                }));
                const links = Array.from(document.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim().replace(/\\n/g, ' '),
                    href: a.getAttribute('href')
                }));
                return { buttons, links };
            })()
            """
            res = await cdp.send('Runtime.evaluate', {'expression': pvp_elements_expr, 'returnByValue': True})
            elements = res.get('result', {}).get('result', {}).get('value', {})
            print("PvP page interactive buttons:", flush=True)
            for b in elements.get('buttons', []):
                print(f"  [{b['index']}] {b['text'][:50]}", flush=True)

            # 2. Click 'Add to PvP' / 'Place Gifts to start play'
            click_add_expr = """
            (() => {
                const btns = Array.from(document.querySelectorAll('button, [role=\"button\"]'));
                const addBtn = btns.find(b => b.innerText.includes('Add to PvP') || b.innerText.includes('Place Gifts'));
                if (addBtn) {
                    addBtn.click();
                    return 'Clicked: ' + addBtn.innerText;
                }
                return 'Add button not found';
            })()
            """
            res = await cdp.send('Runtime.evaluate', {'expression': click_add_expr, 'returnByValue': True})
            print("Click Add to PvP result:", res.get('result', {}).get('result', {}).get('value'), flush=True)

            await asyncio.sleep(2)

            # Check if bottom sheet opened
            sheet_check_expr = """
            (() => {
                const modal = document.querySelector('[role=\"dialog\"], .fixed.inset-0, [data-headlessui-state=\"open\"]');
                return {
                    hasModal: !!modal,
                    modalText: modal ? modal.innerText.replace(/\\n/g, ' ').substring(0, 300) : null
                };
            })()
            """
            res = await cdp.send('Runtime.evaluate', {'expression': sheet_check_expr, 'returnByValue': True})
            print("Modal after click:", res.get('result', {}).get('result', {}).get('value'), flush=True)

            # Check Daily tournament button / link
            click_tourney_expr = """
            (() => {
                const btns = Array.from(document.querySelectorAll('button, a, [role=\"button\"]'));
                const tBtn = btns.find(b => b.innerText.includes('Daily Tournament') || b.innerText.includes('Tournament'));
                if (tBtn) {
                    tBtn.click();
                    return 'Clicked tournament: ' + tBtn.innerText.replace(/\\n/g, ' ');
                }
                return 'Tournament button not found';
            })()
            """
            res = await cdp.send('Runtime.evaluate', {'expression': click_tourney_expr, 'returnByValue': True})
            print("Tournament click:", res.get('result', {}).get('result', {}).get('value'), flush=True)

            await asyncio.sleep(2)
            res = await cdp.send('Runtime.evaluate', {'expression': 'window.location.pathname + " | " + document.body.innerText.replace(/\\n/g, " ").substring(0, 300)'})
            print("After Tournament click:", res.get('result', {}).get('result', {}).get('value'), flush=True)

            # Navigate to Profile
            print("\n--- Navigating to /profile ---", flush=True)
            await cdp.send('Page.navigate', {'url': 'http://127.0.0.1:8080/profile'})
            await asyncio.sleep(3)

            # Check Profile links
            res = await cdp.send('Runtime.evaluate', {'expression': """
            Array.from(document.querySelectorAll('a')).map(a => ({ text: a.innerText.trim().replace(/\\n/g, ' '), href: a.getAttribute('href') }))
            """, 'returnByValue': True})
            print("Profile links:", res.get('result', {}).get('result', {}).get('value'), flush=True)

            # Test Profile subpages
            for sub in ['/profile/lombard', '/profile/inventory', '/profile/referral', '/profile/staking', '/profile/tasks']:
                print(f"\n--- Testing {sub} ---", flush=True)
                await cdp.send('Page.navigate', {'url': f'http://127.0.0.1:8080{sub}'})
                await asyncio.sleep(2)
                res = await cdp.send('Runtime.evaluate', {'expression': 'document.body.innerText.replace(/\\n/g, " ").substring(0, 300)'})
                print(f"{sub} text:", repr(res.get('result', {}).get('result', {}).get('value', '')), flush=True)

            print("\n=== NETWORK ERRORS (HTTP >= 400) ===")
            for ne in cdp.network_errors:
                print(f"  HTTP {ne['status']}: {ne['url']}")

            print("\n=== CONSOLE EXCEPTIONS / LOGS ===")
            for cl in cdp.console_logs:
                print("  ", cl)

            await cdp.close()

    finally:
        p.terminate()

asyncio.run(run())
