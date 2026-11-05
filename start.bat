@echo off
chcp 65001 > nul
echo ====================================================
echo           Rolls Game Mini App & Bot Launcher
echo ====================================================
echo.

if not exist config.json (
    echo {"bot_token": "", "webapp_url": "http://localhost:8080"} > config.json
)

echo [1/2] Mahalliy server ishga tushirilmoqda (http://localhost:8080)...
start "Rolls Game Server" python server.py

echo.
echo [2/2] Telegram Bot tekshirilmoqda...
python -c "import json; cfg=json.load(open('config.json')); exit(0 if cfg.get('bot_token') else 1)"
if %errorlevel% neq 0 (
    echo.
    echo [DIQQAT] Bot token hali kiritilmagan!
    echo config.json fayliga BotFather bergan tokenni yozing.
    echo.
) else (
    echo Bot ishga tushirilmoqda...
    start "Rolls Telegram Bot" python bot.py
)

echo ====================================================
echo Tayyor! Brauzeringizda ochish uchun: http://localhost:8080
echo ====================================================
pause
