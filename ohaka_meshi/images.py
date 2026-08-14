import uuid
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

UPLOAD_DIR = Path(__file__).parent / "static" / "uploads"
MAX_EDGE = 1600
JPEG_QUALITY = 85
REQUEST_TIMEOUT = 8
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _process_and_save(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes))
        img.load()
    except Exception:
        return None

    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        rgba = img.convert("RGBA")
        background.paste(rgba, mask=rgba.split()[-1])
        img = background
    else:
        img = img.convert("RGB")

    img.thumbnail((MAX_EDGE, MAX_EDGE))

    filename = f"{uuid.uuid4().hex}.jpg"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    img.save(UPLOAD_DIR / filename, "JPEG", quality=JPEG_QUALITY)
    return filename


def save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    return _process_and_save(file_storage.read())


def save_image_from_url(url):
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        return None
    return _process_and_save(resp.content)


def delete_image(filename):
    if not filename:
        return
    path = UPLOAD_DIR / filename
    if path.exists():
        path.unlink()
