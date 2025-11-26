# core/config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = BASE_DIR / "static" / "media"   # сюда сохраняем картинки
MEDIA_URL = "/media/"