# 🎬 MediaGrabber

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge\&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Support](https://img.shields.io/badge/Support-BuyMeACoffee-orange?style=for-the-badge)](https://buymeacoffee.com/imed_kablavi)

**MediaGrabber** — A multilingual media downloader and manager.
Inspect • Download • Convert

---

## 🌟 Features

| Feature              | Description                                                 |
| -------------------- | ----------------------------------------------------------- |
| ⚡ Fast & Reliable    | Built with FastAPI and Uvicorn                              |
| 📥 Direct Download   | Download supported media using `yt-dlp`                     |
| 🎵 MP3 Conversion    | Optional audio conversion with FFmpeg                       |
| 🔎 Media Inspection  | Extract available formats, qualities, and media details     |
| 🌍 Multi-language    | Arabic, English, and Turkish interface support              |
| ↔️ RTL Support       | Proper right-to-left layout support for Arabic              |
| 🧭 SEO Ready         | canonical, hreflang, Open Graph, and Twitter metadata       |
| 🤖 Robots & Sitemap  | `robots.txt` and `sitemap.xml` served from the backend      |
| 🛡️ Cache & Security | Static cache headers, HSTS support, and custom 404 handling |

---

## 📂 Project Structure

```text
server/
└─ main.py                  # FastAPI app, static files, API routes, SEO routes

static/
├─ index.html               # Main frontend
├─ css/style.css            # Styles and layout
├─ js/app.js                # App initialization and language handling
├─ i18n/{ar,en,tr}.json     # UI translations
├─ assets/logo.svg          # Project logo
├─ pages/
│  ├─ about.html            # About page
│  ├─ privacy.html          # Privacy policy
│  ├─ terms.html            # Terms page
│  └─ contact.html          # Contact page
├─ manifest.json            # PWA manifest
├─ robots.txt               # Robots file
└─ sitemap.xml              # Sitemap file
```

---

## 🚀 Live Demo

* Production: https://mediagrabber.imedkablavi.info/
* Local: http://127.0.0.1:5051/

<!-- Add screenshots or a demo GIF here when available. -->

---

## 🌍 Internationalization

MediaGrabber supports multiple interface languages through JSON translation files.

* Browser language detection
* Arabic RTL layout support
* Easy translation updates through `static/i18n/`
* Current languages: Arabic, English, Turkish

To add or update a language, edit or create a JSON file inside:

```text
static/i18n/
```

---

## 🛠️ Local Development

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
.\venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the development server:

```bash
python -m uvicorn server.main:app --host 127.0.0.1 --port 5051 --workers 4
```

Open the app:

```text
http://127.0.0.1:5051/
```

---

## 🧪 API Overview

| Method | Endpoint        | Description                                      |
| ------ | --------------- | ------------------------------------------------ |
| `POST` | `/api/inspect`  | Inspect a media URL and return available formats |
| `POST` | `/api/download` | Download selected media format                   |
| `GET`  | `/robots.txt`   | Serve robots file                                |
| `GET`  | `/sitemap.xml`  | Serve sitemap file                               |
| `GET`  | `/health`       | Basic health check                               |

---

## 🔐 YouTube Cookies

Some YouTube links may require cookies for access.
Export cookies in Netscape format and set the cookie file path using `YTDLP_COOKIEFILE`.

Example `.env` value:

```env
YTDLP_COOKIEFILE=C:\\absolute\\path\\to\\cookies\\youtube.txt
```

Reference:

```text
https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
```

---

## 🚀 Deployment

MediaGrabber can run directly with Uvicorn or behind a reverse proxy such as OpenLiteSpeed, Nginx, Apache, or aaPanel.

Example production command:

```bash
uvicorn server.main:app --host 127.0.0.1 --port 5050 --workers 1
```

Recommended production setup:

* Enable HTTPS
* Redirect HTTP to HTTPS
* Use HTTP/2 when available
* Keep `.env` values private
* Run the app behind a reverse proxy
* Use a process manager such as `systemd`, `supervisor`, or similar

---

## ⚠️ Usage Notice

MediaGrabber is intended for personal, educational, and lawful use only.
Make sure you have the right to download or process any media you use with this project.

---

## 🤝 Contributing

Contributions are welcome.

You can help by:

* Improving the interface
* Adding new translations
* Fixing bugs
* Improving API behavior
* Updating documentation

Basic workflow:

```text
Fork → Create Branch → Make Changes → Open Pull Request
```

---

## 📜 License

MIT License © Imed Kablavi

---

## 💰 Support

If you like this project, you can support it here:

[BuyMeACoffee](https://buymeacoffee.com/imed_kablavi)

---
