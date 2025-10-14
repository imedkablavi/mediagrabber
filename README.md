# 🎬 MediaGrabber | ميديا جرايبر

[![Python](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python)](https://www.python.org/) 
[![FastAPI](https://img.shields.io/badge/FastAPI-FF0050?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/) 
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE) 
[![BuyMeACoffee](https://img.shields.io/badge/Support-BuyMeACoffee-orange?style=for-the-badge)](https://www.buymeacoffee.com/)

**MediaGrabber** — Multi-language Media Downloader & Manager  
Inspect • Download • Convert • فحص • تحميل • تحويل  

---

## 🌟 Features | المميزات

| Feature / الميزة | Description / الوصف |
|-----------------|-------------------|
| ⚡ Fast & Reliable | Built with FastAPI + Uvicorn / سريع وموثوق |
| 📥 Direct Download | Using `yt-dlp` + FFmpeg / تحميل مباشر مع دمج FFmpeg |
| 🎵 MP3 Conversion | Optional conversion / تحويل اختياري إلى MP3 |
| 🔎 Media Inspection | Extract formats & qualities before downloading / استخراج الصيغ والجودات قبل التحميل |
| 🌍 Multi-language | Arabic (RTL) • English • Turkish / دعم العربية، الإنجليزية، التركية |
| 🧭 SEO Optimized | canonical, hreflang, Open Graph, Twitter Cards / تحسين SEO شامل |
| 🤖 Robots & Sitemap | `robots.txt` & `sitemap.xml` served from server / تقديم ملفات SEO |
| 🛡️ Cache & Security | HSTS, custom 404 page, static file headers / ترويسات أمان وكاش، صفحة 404 مخصصة |

---

## 📂 Project Structure | هيكل المشروع
server/
└─ main.py # FastAPI app: static files, API & SEO
static/
├─ index.html # Main frontend
├─ css/style.css # Styles & layout
├─ js/app.js # Frontend init & language management
├─ i18n/{ar,en,tr}.json # UI translations
├─ assets/logo.svg # Logo
├─ pages/{about,privacy,terms,contact}.html
├─ manifest.json # PWA manifest
robots.txt, sitemap.xml # SEO files

yaml
Copy code

---

## 🚀 Live Demo | العرض الحي
- Production / الإنتاج: [https://mediagrabber.imedkablavi.info/](https://mediagrabber.imedkablavi.info/)  
- Local / محليًا: `http://127.0.0.1:5051/`  

### Screenshots / لقطات
![Home Page](./docs/screenshots/home.png)  
![Download Example](./docs/screenshots/download.png)  
<!-- يمكنك إضافة GIF توضيحي -->
![Demo GIF](./docs/screenshots/demo.gif)  

---

## 🌍 Internationalization | التعدد اللغوي
- Auto-detect browser language & RTL support for Arabic / اكتشاف لغة المتصفح تلقائيًا ودعم RTL للعربية  
- Add/update languages via JSON files in `static/i18n/` / أضف أو حدّث اللغات عبر ملفات JSON

---

## 🛠️ Local Development | التطوير محليًا
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn server.main:app --host 127.0.0.1 --port 5051 --workers 4
# Open http://127.0.0.1:5051/
🧪 API Overview | نقاط نهاية API
POST /api/inspect — Inspect media / فحص الرابط وإرجاع الصيغ والجودات

POST /api/download — Download media / تنزيل الصيغة المحددة (supports MP3 conversion)

GET /robots.txt, GET /sitemap.xml — SEO files / تقديم ملفات SEO

GET /health — Health check / فحص صحة التطبيق

🔐 YouTube Cookies | ملفات كوكيز يوتيوب (Optional / عند الحاجة)
Some links require YouTube authentication / بعض الروابط تحتاج مصادقة YouTube

Export cookies in Netscape format & set YTDLP_COOKIEFILE path / صدّر الكوكيز بصيغة Netscape وحدّد المسار في YTDLP_COOKIEFILE

env
Copy code
# .env (see .env.example)
YTDLP_COOKIEFILE=C:\\absolute\\path\\to\\cookies\\youtube.txt
🚀 Deployment | النشر
Run directly via Uvicorn / تشغيل مباشر:

bash
Copy code
uvicorn server.main:app --host 127.0.0.1 --port 5050 --workers 1
Use behind OpenLiteSpeed/aaPanel as proxy / استخدم خلف بروكسي

Enable HTTPS, redirect HTTP → HTTPS, prefer HTTP/2 / تفعيل HTTPS وإعادة التوجيه من HTTP → HTTPS، ويفضل HTTP/2

Manage process with Supervisor or system service / إدارة العملية عبر Supervisor أو خدمات النظام

🤝 Contributing | المساهمة
Improve frontend, add new translations, or API endpoints / تحسين الواجهة أو إضافة ترجمات أو نقاط نهاية API

Fork → Develop → Open Pull Request

📜 License | الترخيص
MIT License © Imed Kablavi

💰 Support | الدعم
If you like the project, support me:
 ☕

يمكنك دعم المشروع هنا: BuyMeACoffee

