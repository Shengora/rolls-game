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

async def get_upgrade_errors():
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    p = subprocess.Popen([edge, '--headless', '--remote-debugging-port=9222', '--disable-gpu', '--window-size=390,844', 'http://127.0.0.1:8080/solo/upgrade'])
    await asyncio.sleep(2)
    try:
        tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode('utf-8'))
        tab = [t for t in tabs if t.get('type') == 'page'][0]
        async with websockets.connect(tab['webSocketDebuggerUrl']) as ws:
            await ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
            
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get('method') == 'Runtime.consoleAPICalled':
                    params = data.get('params', {})
                    args = params.get('args', [])
                    if len(args) > 1 and args[0].get('value') == 'api error':
                        obj_id = args[1].get('objectId')
                        if obj_id:
                            await ws.send(json.dumps({
                                'id': 99,
                                'method': 'Runtime.getProperties',
                                'params': {'objectId': obj_id, 'ownProperties': True}
                            }))
                            while True:
                                res_msg = await ws.recv()
                                res_data = json.loads(res_msg)
                                if res_data.get('id') == 99:
                                    props = res_data.get('result', {}).get('result', [])
                                    for prop in props:
                                        if prop.get('name') in ['error', 'url', 'message']:
                                            print(prop.get('name'), '->', prop.get('value', {}).get('value') or prop.get('value', {}).get('description'))
                                    return
    finally:
        p.terminate()

asyncio.run(get_upgrade_errors())
