# Rolls Game Telegram Mini App & Bot Platform

To'liq funksional Telegram Mini App ekotizimi — Rolls Game replikasi. TON blockchain, TonConnect, CryptoBot to'lovlari, Telegram Star Gifts relayeri, admin paneli va avtomatik Cloudflare tunnellash bilan ta'minlangan.

---

## 🌟 Imkoniyatlar

- **Frontend:** Nuxt 3 / Vue asosidagi to'liq WebApp interfeysi (`public/` papkasida).
- **Backend:** `server.py` — barcha o'yin rejimlari, PvP, profil, inventar, keyslar, yechib olish va tranzaksiyalar uchun HTTP API serveri.
- **Telegram Bot:** `bot.py` — Telegram polling va WebApp menyu tugmasini boshqaruvchi bot.
- **TonConnect Integratsiyasi:** Dinamik manifest, Tonkeeper va boshqa TON hamyonlar orqali depozit qilish.
- **CryptoPay Integratsiyasi:** `@CryptoBot` orqali USDT, TON va boshqa kriptovalyutalarda to'lovlarni qabul qilish.
- **Star Gifts Relayer:** `relayer.py` — Telethon asosidagi relayer hisob (gifts qabul qilish va tekshirish).
- **Admin Panel:** `admin.html` — Yechib olish so'rovlarini ko'rish, boshqarish va foydalanuvchilar holatini monitoring qilish.
- **Avtomatik Tunnel:** `tunnel.py` — Cloudflare tunnel orqali bepul HTTPS URL yaratish va bot menyusiga avtomatik ulash.

---

## 📁 Loyiha Tuzilishi

```text
├── public/                     # Statik frontend (Nuxt 3 build, HTML, JS, CSS, assets)
│   ├── assets/                 # Rasmlar, Lottie/TGS animatsiyalar, 3D modellar
│   ├── _nuxt/                  # Komponentlar va sahifa chunklari
│   ├── index.html              # Bosh sahifa
│   └── tonconnect-manifest.json# TonConnect manifesti
├── server.py                   # Asosiy backend server (port 8080)
├── bot.py                      # Telegram bot xizmati
├── tunnel.py                   # Cloudflare tunnel va dinamik URL menejeri
├── relayer.py                  # Telethon MTProto Star Gifts relayeri
├── relayer_auth.py             # Relayer akkauntga bir marta kirish skripti
├── telegram_notify.py          # Adminga Telegram orqali xabarnomalar yuborish
├── cryptopay_integration.py    # CryptoBot API integratsiyasi
├── ton_wallet_integration.py   # TON Blockchain on-chain skaner
├── market_price_engine.py      # Star Gifts narxlari hisoblash mexanizmi
├── admin.html                  # Admin boshqaruv paneli
├── config.example.json         # Konfiguratsiya namunasi
├── .env.example                # Muhit o'zgaruvchilari namunasi
├── start.bat                   # Windows uchun qulay ishga tushirish fayli
└── README.md                   # Loyiha qo'llanmasi
```

---

## ⚙️ O'rnatish va Sozlash

### 1. Talablar
- Python 3.10 yoki undan yuqori
- `pip install telethon urllib3`

### 2. Konfiguratsiya
`config.example.json` faylidan nusxa olib `config.json` yarating:
```bash
cp config.example.json config.json
```
Yoki `.env` faylidan foydalanishingiz mumkin (`.env.example` ga qarang).

`config.json` ichidagi parametrlarni to'ldiring:
```json
{
  "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "webapp_url": "https://your-domain.com",
  "cryptopay_token": "YOUR_CRYPTOPAY_API_TOKEN",
  "admin_telegram_id": 1234567890,
  "project_ton_wallet": "YOUR_TON_WALLET_ADDRESS",
  "raw_ton_address": "YOUR_RAW_TON_HEX_ADDRESS"
}
```

> ⚠️ **Muhim:** `config.json`, `.session` va `.env` fayllari `.gitignore` ga kiritilgan va maxfiy ma'lumotlarni saqlash uchun xavfsizdir.

---

## 🚀 Ishga Tushirish

### 1. Avtomatik ishga tushirish (Windows):
Loyiha ildizidagi `start.bat` faylini ishga tushiring:
```cmd
start.bat
```

### 2. Alohida servislar:
- **Backend server:**
  ```bash
  python server.py
  ```
- **Cloudflare Tunnel (tashqi internetga chiqarish):**
  ```bash
  python tunnel.py
  ```
- **Telegram Bot:**
  ```bash
  python bot.py
  ```
- **Telegram Gifts Relayer:**
  ```bash
  python relayer.py
  ```

---

## 🛡️ Xavfsizlik

- Maxfiy Telethon sessiyalari (`*.session`) va shaxsiy auth ma'lumotlari repositoryga yuklanmaydi.
- API tokenlar va kalitlar kod ichida emas, `config.json` yoki tizim muhit o'zgaruvchilarida (`.env`) saqlanadi.
- Barcha to'lovlar va yechib olishlar admin xabarnomalari bilan himoyalangan.
