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

async def check_zod():
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    p = subprocess.Popen([edge, '--headless', '--remote-debugging-port=9222', '--disable-gpu', '--window-size=390,844', 'http://127.0.0.1:8080/'])
    await asyncio.sleep(2)
    try:
        tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode('utf-8'))
        tab = [t for t in tabs if t.get('type') == 'page'][0]
        async with websockets.connect(tab['webSocketDebuggerUrl']) as ws:
            await ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
            
            # Hook console.error and console.log to print the exact error object JSON
            hook_expr = """
            (() => {
                const origLog = console.log;
                console.log = function(...args) {
                    origLog.apply(console, args);
                    if (args[0] === 'api error' && args[1] && args[1].error) {
                        window.__LAST_ZOD_ERROR = {
                            issues: args[1].error.issues,
                            message: args[1].error.message,
                            responseUrl: args[1].url || args[1].config?.url
                        };
                    }
                };
            })()
            """
            await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': hook_expr}}))
            
            await asyncio.sleep(4)
            
            # Fetch the error
            await ws.send(json.dumps({
                'id': 3,
                'method': 'Runtime.evaluate',
                'params': {'expression': 'JSON.stringify(window.__LAST_ZOD_ERROR)', 'returnByValue': True}
            }))
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get('id') == 3:
                    print("ZOD ERROR DETAILS:")
                    print(data.get('result', {}).get('result', {}).get('value'))
                    break
    finally:
        p.terminate()

asyncio.run(check_zod())
