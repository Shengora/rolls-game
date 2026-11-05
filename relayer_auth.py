import sys
import os
import json
import asyncio
from telethon import TelegramClient, errors

API_ID = 36122528
API_HASH = "5986d2d8aae8d8534ca003efef9cef81"
SESSION_PATH = os.path.join(os.path.dirname(__file__), "relayer")
STATE_PATH = os.path.join(os.path.dirname(__file__), "relayer_auth_state.json")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "relayer_config.json")

def get_client():
    return TelegramClient(
        SESSION_PATH,
        API_ID,
        API_HASH,
        device_model="Desktop",
        system_version="Windows 11",
        app_version="5.3.1 x64",
        lang_code="en",
        system_lang_code="en"
    )

async def request_code(phone: str):
    client = get_client()
    await client.connect()
    try:
        sent = await client.send_code_request(phone)
        state = {
            "phone": phone,
            "phone_code_hash": sent.phone_code_hash,
            "type": str(type(sent.type).__name__)
        }
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        print("STATUS: CODE_SENT_SUCCESS")
        print(f"PHONE: {phone}")
        print(f"TYPE: {state['type']}")
    except errors.FloodWaitError as e:
        print(f"STATUS: FLOOD_WAIT {e.seconds}")
    except errors.PhoneNumberInvalidError:
        print("STATUS: PHONE_NUMBER_INVALID")
    except Exception as e:
        print(f"STATUS: ERROR {type(e).__name__}: {e}")
    finally:
        await client.disconnect()

async def submit_code(code: str, password: str = None):
    if not os.path.exists(STATE_PATH):
        print("STATUS: NO_PENDING_REQUEST")
        return
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)

    phone = state["phone"]
    phone_code_hash = state["phone_code_hash"]

    client = get_client()
    await client.connect()
    try:
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        except errors.SessionPasswordNeededError:
            if not password:
                print("STATUS: PASSWORD_REQUIRED")
                return
            await client.sign_in(password=password)
        
        me = await client.get_me()
        config = {
            "phone": phone,
            "id": me.id,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "username": me.username,
            "is_bot": me.bot
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        print("STATUS: LOGIN_SUCCESS")
        print(f"USERNAME: {me.username}")
        print(f"NAME: {me.first_name}")
        print(f"ID: {me.id}")
    except errors.PhoneCodeInvalidError:
        print("STATUS: CODE_INVALID")
    except errors.PhoneCodeExpiredError:
        print("STATUS: CODE_EXPIRED")
    except errors.PasswordHashInvalidError:
        print("STATUS: PASSWORD_INVALID")
    except Exception as e:
        print(f"STATUS: ERROR {type(e).__name__}: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: relayer_auth.py request-code <phone> OR relayer_auth.py submit-code <code> [password]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "request-code":
        phone = sys.argv[2]
        if not phone.startswith("+"):
            phone = "+" + phone
        asyncio.run(request_code(phone))
    elif cmd == "submit-code":
        code = sys.argv[2]
        password = sys.argv[3] if len(sys.argv) > 3 else None
        asyncio.run(submit_code(code, password))
