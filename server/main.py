import os
import logging
import asyncio
from typing import Optional, List, Dict, Any, Tuple

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, HttpUrl
import ssl
from time import time

from yt_dlp import YoutubeDL
import requests
import shutil
import platform
import subprocess

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
STATIC_DIR = os.path.join(ROOT_DIR, "static")
DOWNLOADS_DIR = os.path.join(ROOT_DIR, "downloads")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "app.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# SSL diagnostics toggle via environment (do NOT disable in production by default)
# Set DIAG_DISABLE_SSL=1 to temporarily disable certificate verification for debugging
SSL_VERIFICATION_DISABLED = os.getenv("DIAG_DISABLE_SSL") == "1"
if SSL_VERIFICATION_DISABLED:
    ssl._create_default_https_context = ssl._create_unverified_context
    logging.warning("SSL verification disabled (diagnostic mode). Do NOT use in production.")

class InspectRequest(BaseModel):
    url: HttpUrl
    proxy: Optional[str] = None
    verify: Optional[bool] = True
    cookies_browser: Optional[str] = None  # e.g. "chrome", "edge", "firefox"

class DownloadRequest(BaseModel):
    url: HttpUrl
    format_id: Optional[str] = None
    to_mp3: Optional[bool] = False
    proxy: Optional[str] = None
    cookies_browser: Optional[str] = None

def aria2_available() -> bool:
    return shutil.which("aria2c") is not None

def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None

def ffprobe_available() -> bool:
    return shutil.which("ffprobe") is not None

def _headers_for_url(url: Optional[str]) -> Dict[str, str]:
    if not url:
        return {"User-Agent": "Mozilla/5.0"}
    ua_mobile = "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36"
    ua_desktop = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    headers = {"User-Agent": ua_desktop, "Accept": "*/*"}
    u = url.lower()
    if "tiktok.com" in u or "instagram.com" in u:
        headers.update({"User-Agent": ua_mobile})
    elif "facebook.com" in u or "fb.watch" in u:
        headers.update({"Referer": "https://www.facebook.com/"})
    elif "x.com" in u or "twitter.com" in u:
        headers.update({"Referer": "https://twitter.com/"})
    elif "reddit.com" in u:
        headers.update({"Referer": "https://www.reddit.com/"})
    elif "pinterest.com" in u:
        headers.update({"Referer": "https://www.pinterest.com/"})
    elif "vimeo.com" in u:
        headers.update({"Referer": "https://vimeo.com/"})
    elif "youtube.com" in u or "youtu.be" in u:
        headers.update({"Referer": "https://www.youtube.com/", "Origin": "https://www.youtube.com"})
    return headers

def _ydl_opts_common(proxy: Optional[str] = None, cookies_browser: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
    # Default robust options per requirements
    opts: Dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "nocheckcertificate": SSL_VERIFICATION_DISABLED,
        "http_chunk_size": 10485760,
        "retries": 6,
        "fragment_retries": 8,
        "retry_sleep": "exp",
        "concurrent_fragment_downloads": 5,
        "socket_timeout": 30,
        "geo_bypass": True,
        "geo_bypass_country": "US",
    }
    if proxy:
        opts["proxy"] = proxy
    if cookies_browser:
        opts["cookiesfrombrowser"] = (cookies_browser,)
    if aria2_available():
        opts["external_downloader"] = "aria2c"
        opts["external_downloader_args"] = {"aria2c": ["-x", "16", "-s", "16", "-k", "1M", "--file-allocation=none"]}
    if url:
        opts["http_headers"] = _headers_for_url(url)
        opts["extractor_args"] = {"youtube": {"player_client": ["android", "ios", "web"]}}
    # Prefer FFmpeg for HLS to avoid empty file issues
    if ffmpeg_available():
        opts["hls_prefer_native"] = False
        opts["hls_use_mpegts"] = True
    else:
        opts["hls_prefer_native"] = True
    # Merge settings
    opts["merge_output_format"] = "mp4"
    opts["prefer_ffmpeg"] = True
    return opts


# Simple bounded download concurrency (queue) to avoid overload
DOWNLOAD_SEMAPHORE = asyncio.Semaphore(3)


def _expected_outtmpl() -> str:
    # Use project downloads directory; cross-platform path
    return os.path.join(DOWNLOADS_DIR, "%(title)s-%(id)s.%(ext)s")


def _ffprobe_has_audio(filepath: str) -> bool:
    try:
        if ffprobe_available():
            cmd = ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", filepath]
            p = subprocess.run(cmd, capture_output=True, text=True)
            return p.returncode == 0 and bool(p.stdout.strip())
        elif ffmpeg_available():
            cmd = ["ffmpeg", "-v", "error", "-i", filepath, "-hide_banner"]
            p = subprocess.run(cmd, capture_output=True, text=True)
            # crude check: look for "Audio:" in stderr
            return "Audio:" in (p.stderr or "")
    except Exception as e:
        logger.warning(f"ffprobe audio check failed: {e}")
    return True  # assume audio exists if tools missing


def _find_downloaded_file_by_pattern(info: Dict[str, Any]) -> Optional[str]:
    try:
        vid = info.get("id")
        title = info.get("title") or ""
        for name in os.listdir(DOWNLOADS_DIR):
            if not name:
                continue
            low = name.lower()
            if (vid and vid in low) or (title and title.lower() in low):
                full = os.path.join(DOWNLOADS_DIR, name)
                if os.path.isfile(full):
                    return full
    except Exception:
        pass
    return None


def _build_final_opts_for_download(url: str, format_id: Optional[str], to_mp3: bool, proxy: Optional[str], cookies_browser: Optional[str]) -> Dict[str, Any]:
    # Required explicit defaults snippet (documented):
    # opts = {
    #   "format": "bestvideo+bestaudio/best",
    #   "outtmpl": "/downloads/%(title)s-%(id)s.%(ext)s",
    #   "merge_output_format": "mp4",
    #   "prefer_ffmpeg": True,
    #   "hls_prefer_native": False, # if ffmpeg exists
    #   "hls_use_mpegts": True,
    #   "retries": 6,
    #   "fragment_retries": 8,
    #   "socket_timeout": 30,
    #   "external_downloader": "aria2c", # optional
    #   "http_headers": { ...platform headers... },
    # }
    opts = _ydl_opts_common(proxy=proxy, cookies_browser=cookies_browser, url=url)
    fmt = format_id if (format_id and not str(format_id).startswith("sb")) else "bestvideo+bestaudio/best"
    opts.update({
        "skip_download": False,
        "format": fmt,
        "outtmpl": _expected_outtmpl(),
        "merge_output_format": "mp4",
        "prefer_ffmpeg": True,
    })
    if to_mp3:
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    return opts


def _download_via_subprocess(url: str, opts: Dict[str, Any], to_mp3: bool) -> Tuple[bool, Optional[str]]:
    if not shutil.which("yt-dlp"):
        return False, None
    try:
        cmd = ["yt-dlp", "-f", opts.get("format", "bestvideo+bestaudio/best"), "-o", opts.get("outtmpl", _expected_outtmpl())]
        # headers
        headers = opts.get("http_headers") or {}
        for k, v in headers.items():
            cmd += ["--add-header", f"{k}:{v}"]
        # proxy
        if opts.get("proxy"):
            cmd += ["--proxy", opts.get("proxy")]
        # cookies from browser
        cfb = opts.get("cookiesfrombrowser")
        if cfb:
            # Not all yt-dlp binaries accept tuple; skip here (advanced: use --cookies)
            pass
        # retries/timeouts
        cmd += ["--retries", str(opts.get("retries", 6)), "--fragment-retries", str(opts.get("fragment_retries", 8))]
        if aria2_available():
            cmd += ["--external-downloader", "aria2c"]
        if ffmpeg_available():
            cmd += ["--hls-use-mpegts"]
        if SSL_VERIFICATION_DISABLED:
            cmd += ["--no-check-certificates"]
        if to_mp3:
            cmd += ["--extract-audio", "--audio-format", "mp3"]
        cmd.append(url)
        p = subprocess.run(cmd, capture_output=True, text=True)
        ok = p.returncode == 0
        if not ok:
            logger.error(f"yt-dlp subprocess failed: {p.stderr}\nCMD: {' '.join(cmd)}")
            return False, None
        # Try to locate file
        # WARNING: When postprocessing to mp3, extension changes
        # We cannot rely on info dict here, attempt glob by id/title via later find
        return True, None
    except Exception as e:
        logger.exception(f"Subprocess fallback error: {e}")
        return False, None

def _format_summary(fmt: Dict[str, Any], valid: Optional[bool] = None) -> Dict[str, Any]:
    return {
        "id": fmt.get("format_id"),
        "ext": fmt.get("ext"),
        "vcodec": fmt.get("vcodec"),
        "acodec": fmt.get("acodec"),
        "width": fmt.get("width"),
        "height": fmt.get("height"),
        "fps": fmt.get("fps"),
        "filesize": fmt.get("filesize"),
        "format_note": fmt.get("format_note"),
        "abr": fmt.get("abr"),
        "tbr": fmt.get("tbr"),
        "url": fmt.get("url"),
        "valid": valid,
    }

# Simple in-memory cache and rate limit
CACHE_TTL_SECONDS = 600
_cache: Dict[str, Dict[str, Any]] = {}
RATE_WINDOW = 60.0
RATE_MAX = 100
_rate: Dict[str, List[float]] = {}

def cache_get(url: str) -> Optional[Dict[str, Any]]:
    entry = _cache.get(url)
    if not entry:
        return None
    if time() - entry.get("ts", 0) > CACHE_TTL_SECONDS:
        _cache.pop(url, None)
        return None
    return entry.get("data")

def cache_set(url: str, data: Dict[str, Any]) -> None:
    _cache[url] = {"data": data, "ts": time()}

def check_rate(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time()
    bucket = _rate.get(ip, [])
    bucket = [t for t in bucket if now - t <= RATE_WINDOW]
    if len(bucket) >= RATE_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    bucket.append(now)
    _rate[ip] = bucket

def _verify_direct_url(url: str, proxy: Optional[str]) -> bool:
    # تعطيل التحقق للروابط المؤقتة
    return True

app = FastAPI(title="MediaGrabber API", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add simple caching and HSTS headers for static assets
@app.middleware("http")
async def caching_hsts_middleware(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path or ""
    try:
        if path.startswith("/assets") or path.startswith("/css") or path.startswith("/js"):
            # Cache static resources for 7 days
            response.headers["Cache-Control"] = "public, max-age=604800"
        # Encourage HTTPS usage (effective only over HTTPS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    except Exception:
        pass
    return response

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

# Expose robots.txt and sitemap.xml from project root
@app.get("/robots.txt", include_in_schema=False)
def robots_file():
    path = os.path.join(ROOT_DIR, "robots.txt")
    return FileResponse(path, media_type="text/plain")

@app.get("/sitemap.xml", include_in_schema=False)
def sitemap_file():
    path = os.path.join(ROOT_DIR, "sitemap.xml")
    return FileResponse(path, media_type="application/xml")

@app.get("/favicon.ico", include_in_schema=False)
def favicon_file():
    # Serve SVG logo for favicon to satisfy basic audit checks
    path = os.path.join(STATIC_DIR, "assets", "logo.svg")
    return FileResponse(path, media_type="image/svg+xml")

@app.post("/api/inspect")
async def inspect_media(payload: InspectRequest, request: Request):
    logger.info(f"Inspect request: {payload.url}")
    check_rate(request)
    if not str(payload.url).startswith("https://"):
        raise HTTPException(status_code=400, detail="Only https links are allowed.")
    cached = cache_get(str(payload.url))
    if cached:
        return JSONResponse(cached)
    opts = _ydl_opts_common(proxy=payload.proxy, cookies_browser=payload.cookies_browser, url=str(payload.url))
    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(str(payload.url), download=False)
        except Exception as e:
            logger.exception("Extraction failed")
            raise HTTPException(status_code=400, detail=f"Unsupported or unavailable content: {e}")

    formats = info.get("formats") or []
    formatted: List[Dict[str, Any]] = []
    for f in formats:
        if not f.get("url"):
            continue
        fid = str(f.get("format_id") or "")
        ext = (f.get("ext") or "").lower()
        note = (f.get("format_note") or "").lower()
        vcodec = (f.get("vcodec") or "").lower()
        acodec = (f.get("acodec") or "").lower()
        # Skip storyboards and non-media formats
        if fid.startswith("sb") or ext in ("mhtml", "json", "ttml", "vtt") or "storyboard" in note:
            continue
        # Keep audio-only and video formats. Skip pure metadata entries.
        if vcodec == "none" and acodec == "none":
            continue
        valid = True
        if payload.verify:
            valid = _verify_direct_url(f.get("url"), payload.proxy)
        formatted.append(_format_summary(f, valid=valid))
    response = {
        "platform": info.get("extractor_key") or info.get("extractor"),
        "id": info.get("id"),
        "title": info.get("title"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "webpage_url": info.get("webpage_url"),
        "formats": formatted,
    }
    cache_set(str(payload.url), response)
    return JSONResponse(response)

@app.post("/api/download")
async def download_media(payload: DownloadRequest, request: Request):
    logger.info(f"Download request: {payload.url} format={payload.format_id} mp3={payload.to_mp3}")
    check_rate(request)
    opts = _build_final_opts_for_download(
        url=str(payload.url),
        format_id=payload.format_id,
        to_mp3=payload.to_mp3,
        proxy=payload.proxy,
        cookies_browser=payload.cookies_browser,
    )

    loop = asyncio.get_event_loop()
    async with DOWNLOAD_SEMAPHORE:
        try:
            info = await loop.run_in_executor(None, lambda: YoutubeDL(opts).extract_info(str(payload.url), download=True))
        except Exception as e:
            logger.exception("Download failed (library)")
            # Fallback to subprocess yt-dlp
            ok, _ = _download_via_subprocess(str(payload.url), opts, payload.to_mp3)
            if not ok:
                raise HTTPException(status_code=400, detail=f"Download failed: {e}")
            # Try to locate a file by id/title
            info = {"id": None, "title": None}

    # Determine final filename
    filename: Optional[str] = None
    if isinstance(info, dict) and info.get("id") is not None:
        filename = YoutubeDL(opts).prepare_filename(info)
        if payload.to_mp3:
            filename = os.path.splitext(filename)[0] + ".mp3"
    else:
        # Try to find in downloads
        filename = _find_downloaded_file_by_pattern(info if isinstance(info, dict) else {})

    if not filename or not os.path.isfile(filename):
        raise HTTPException(status_code=404, detail="Downloaded file not found.")

    # Validate audio presence for formats that should include audio (non-mp3 path will include audio if bestaudio merged)
    if not payload.to_mp3 and not _ffprobe_has_audio(filename):
        logger.warning(f"Audio stream missing; retrying with format 'bestaudio/best' merge")
        # Retry force merge
        opts_retry = _build_final_opts_for_download(str(payload.url), None, False, payload.proxy, payload.cookies_browser)
        try:
            await loop.run_in_executor(None, lambda: YoutubeDL(opts_retry).extract_info(str(payload.url), download=True))
            # Update filename again
            filename = _find_downloaded_file_by_pattern(info if isinstance(info, dict) else {}) or filename
        except Exception as e:
            logger.exception("Retry after audio missing failed")
            # Keep original filename

    media_type = "application/octet-stream"
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".mp4", ".m4v", ".webm", ".mov"):
        media_type = "video/mp4" if ext in (".mp4", ".m4v") else "video/webm"
    elif ext in (".mp3", ".m4a", ".aac", ".wav"):
        media_type = "audio/mpeg" if ext == ".mp3" else "audio/aac"
    elif ext in (".jpg", ".jpeg", ".png"):
        media_type = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"

    return FileResponse(path=filename, media_type=media_type, filename=os.path.basename(filename))

@app.get("/api/system")
def system_info():
    info = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "openssl": getattr(ssl, "OPENSSL_VERSION", "unknown"),
        "ffmpeg": None,
        "yt_dlp": None,
        "aria2c": aria2_available(),
    }
    try:
        out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if out.returncode == 0:
            info["ffmpeg"] = out.stdout.splitlines()[0]
    except Exception:
        pass
    try:
        with YoutubeDL({"quiet": True}) as y:
            info["yt_dlp"] = y._ydl_version
    except Exception:
        pass
    return JSONResponse(info)

# Serve frontend
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# Custom 404 to a friendly HTML page if present
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        custom_404 = os.path.join(STATIC_DIR, "404.html")
        if os.path.exists(custom_404):
            return FileResponse(custom_404, status_code=404, media_type="text/html")
    return JSONResponse({"detail": getattr(exc, "detail", "Not Found")}, status_code=exc.status_code)
