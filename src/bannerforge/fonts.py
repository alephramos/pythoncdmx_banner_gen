from __future__ import annotations
import os
from PIL import ImageFont

# CommitMono Nerd Font primary (override with assets/fonts)
DEFAULT_TITLE_FONTS = [
    "assets/fonts/CommitMono/CommitMonoNerdFontMono-Regular.otf",
    "assets/fonts/CommitMono/CommitMonoNerdFont-Bold.otf",
    "assets/fonts/CommitMono/CommitMonoNerdFontMono-Bold.otf",
    "assets/fonts/DejaVuSans/DejaVuSans.ttf",
    "assets/fonts/DejaVuSans/DejaVuSans-Bold.ttf"
]
DEFAULT_TEXT_FONTS = [
    "assets/fonts/CommitMono/CommitMonoNerdFontMono-Regular.otf",
    "assets/fonts/CommitMono/CommitMonoNerdFont-Regular.otf",
    "assets/fonts/CommitMono/CommitMonoNerdFont-Regular.otf",
    "assets/fonts/DejaVuSans/DejaVuSans-Bold.ttf",
    "assets/fonts/DejaVuSans/DejaVuSans.ttf"
]

ASSET_FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "assets", "fonts")


def safe_font(paths, size: int):
    candidates = []
    if isinstance(paths, (list, tuple)):
        candidates.extend(paths)
    elif isinstance(paths, str):
        candidates.append(paths)

    # Asset fonts (project-level override)
    if os.path.isdir(ASSET_FONT_DIR):
        for fn in os.listdir(ASSET_FONT_DIR):
            if fn.lower().endswith(".ttf"):
                p = os.path.join(ASSET_FONT_DIR, fn)
                if "bold" in fn.lower():
                    candidates.insert(0, p)
                else:
                    candidates.append(p)

    # System fallbacks
    candidates += [
        "assets/fonts/DejaVuSans/DejaVuSans-Bold.ttf",
        "assets/fonts/DejaVuSans/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]

    for p in candidates + list(paths if isinstance(paths, (list, tuple)) else [paths]):
        try:
            if isinstance(p, str) and os.path.exists(p):
                return ImageFont.truetype(p, size=size)
        except Exception:
            pass
    return ImageFont.load_default()