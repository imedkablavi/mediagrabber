# 🎬 MediaGrabber | ميديا جرايبر

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Support](https://img.shields.io/badge/Support-BuyMeACoffee-orange?style=for-the-badge)](https://www.buymeacoffee.com/)

**MediaGrabber** — Multi‑language Media Downloader & Manager  
Inspect • Download • Convert • فحص • تحميل • تحويل

---

## 🌟 Features | المميزات

| Feature / الميزة | Description / الوصف |
|------------------|----------------------|
| ⚡ Fast & Reliable | FastAPI + Uvicorn / سريع وموثوق |
| 📥 Direct Download | `yt-dlp` + FFmpeg merge / تحميل مباشر |
| 🎵 MP3 Conversion | Optional / تحويل اختياري إلى MP3 |
| 🔎 Media Inspection | Extract formats & qualities / فحص الصيغ والجودات |
| 🌍 Multi-language | Arabic (RTL), English, Turkish / تعدد اللغات |
| 🧭 SEO Optimized | canonical, hreflang, OG, Twitter / تحسين SEO |
| 🤖 Robots & Sitemap | Served from backend / تقديم عبر الخادم |
| 🛡️ Cache & Security | Static cache headers, HSTS, custom 404 / أمان وكاش |

---

## 📂 Project Structure | هيكل المشروع

```
server/
└─ main.py                  # FastAPI: static, API, SEO routes
static/
├─ index.html               # Main frontend
├─ css/style.css            # Styles & layout
├─ js/app.js                # Init & language management
├─ i18n/{ar,en,tr}.json     # UI translations
├─ assets/logo.svg          # Logo
├─ pages/{about,privacy,terms,contact}.html
├─ manifest.json            # PWA manifest
robots.txt, sitemap.xml     # SEO files
```

---

## 🚀 Live Demo | العرض الحي
- Production / الإنتاج: https://mediagrabber.imedkablavi.info/
- Local / محليًا: http://127.0.0.1:5051/

<!-- يمكنك إضافة GIF أو لقطات شاشة في هذا القسم لاحقًا عند الحاجة -->

---

## 🌍 Internationalization | التعدد اللغوي
- Auto‑detects browser language with RTL support for Arabic.
- Add/update languages via JSON files in `static/i18n/`.

---

## 🛠️ Local Development | التطوير محليًا

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn server.main:app --host 127.0.0.1 --port 5051 --workers 4
# Open http://127.0.0.1:5051/
```

---

## 🧪 API Overview | نقاط نهاية API
- `POST /api/inspect` — Inspect media / فحص الرابط وإرجاع الصيغ والجودات
- `POST /api/download` — Download media / تنزيل الصيغة المحددة (يدعم تحويل MP3)
- `GET /robots.txt`, `GET /sitemap.xml` — SEO files / تقديم ملفات SEO
- `GET /health` — Health check / فحص صحة التطبيق

---

## 🔐 YouTube Cookies | ملفات كوكيز يوتيوب (اختياري)
بعض الروابط تتطلب مصادقة YouTube. صدّر الكوكيز بصيغة Netscape وحدّد المسار في `YTDLP_COOKIEFILE`.

```env
# .env (see .env.example)
YTDLP_COOKIEFILE=C:\\absolute\\path\\to\\cookies\\youtube.txt
```

مراجع:
- https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp

---

## 🚀 Deployment | النشر
تشغيل مباشر عبر Uvicorn أو خلف بروكسي (OpenLiteSpeed/aaPanel).

```bash
uvicorn server.main:app --host 127.0.0.1 --port 5050 --workers 1
```

- فعّل HTTPS وإعادة التوجيه من HTTP → HTTPS، ويفضل HTTP/2.

---

## 🤝 Contributing | المساهمة
حسّن الواجهة، أضف ترجمات جديدة، أو نقاط نهاية API.
Fork → Develop → Open Pull Request.

---

## 📜 License | الترخيص
MIT License © Imed Kablavi

---

## 💰 Support | الدعم
يمكنك دعم المشروع هنا: [BuyMeACoffee](https://buymeacoffee.com/imed_kablavi)

---
