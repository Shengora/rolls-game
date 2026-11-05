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

async def get_details():
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    p = subprocess.Popen([edge, '--headless', '--remote-debugging-port=9222', '--disable-gpu', '--window-size=390,844', 'http://127.0.0.1:8080/'])
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
                            # Query properties of error object
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
                                        print(prop.get('name'), '->', prop.get('value', {}).get('value') or prop.get('value', {}).get('description'))
                                        if prop.get('name') == 'error' and prop.get('value', {}).get('objectId'):
                                            # Get error properties
                                            await ws.send(json.dumps({
                                                'id': 100,
                                                'method': 'Runtime.getProperties',
                                                'params': {'objectId': prop['value']['objectId'], 'ownProperties': True}
                                            }))
                                            while True:
                                                m2 = await ws.recv()
                                                d2 = json.loads(m2)
                                                if d2.get('id') == 100:
                                                    for p2 in d2.get('result', {}).get('result', []):
                                                        print('  error.' + p2.get('name'), '->', p2.get('value', {}).get('value') or p2.get('value', {}).get('description'))
                                                    return
    finally:
        p.terminate()

asyncio.run(get_details())
