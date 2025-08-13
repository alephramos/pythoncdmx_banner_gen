from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()
CACHE_DIR = os.getenv("BANNERFORGE_CACHE", ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)
DEFAULT_SITE = "https://pythoncdmx.org"
DEFAULT_TELEGRAM = "https://t.me/PythonCDMX"