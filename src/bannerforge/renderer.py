from __future__ import annotations
import io, os
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from .styles import PALETTES, palette_from_image
from .fonts import safe_font, DEFAULT_TITLE_FONTS, DEFAULT_TEXT_FONTS
from .textfit import auto_shrink_text
from .config import DEFAULT_SITE, DEFAULT_TELEGRAM
import segno

MARGIN = 48  # safety margin

# local loader
def _load_image_sync(source: Optional[str], expected_size: Optional[Tuple[int, int]] = None):
    if not source:
        return None
    try:
        if source.startswith("http://") or source.startswith("https://"):
            import requests
            r = requests.get(source, timeout=15)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGBA")
        else:
            img = Image.open(source).convert("RGBA")
        if expected_size:
            img = ImageOps.fit(img, expected_size, Image.LANCZOS)
        return img
    except Exception:
        return None


def circular_crop(img: Image.Image, diameter: int) -> Image.Image:
    img = ImageOps.fit(img, (diameter, diameter), Image.LANCZOS)
    mask = Image.new("L", (diameter, diameter), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter, diameter), fill=255)
    out = Image.new("RGBA", (diameter, diameter))
    out.paste(img, (0, 0), mask)
    return out


def shadow(image: Image.Image, radius: int = 20, opacity: int = 160, offset: tuple[int, int] = (0, 8)) -> Image.Image:
    alpha = image.split()[-1]
    sh = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sh.putalpha(alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(radius))
    canvas = Image.new("RGBA", (image.size[0] + abs(offset[0]) * 2, image.size[1] + abs(offset[1]) * 2), (0, 0, 0, 0))
    tint = Image.new("RGBA", sh.size, (0, 0, 0, opacity))
    tint.putalpha(sh.split()[-1])
    canvas.alpha_composite(tint, (offset[0], offset[1]))
    canvas.alpha_composite(image, (0, 0))
    return canvas


def _draw_urls(draw: ImageDraw.ImageDraw, left: int, y: int, max_w: int, sty, site_url: str | None, telegram_url: str | None):
    if not site_url and not telegram_url:
        return y
    meta_font = safe_font(DEFAULT_TEXT_FONTS, 28)
    line = "  |  ".join([u for u in [site_url, telegram_url] if u])
    draw.text((left, y), line, font=meta_font, fill=sty.secondary)
    return y + meta_font.size + 12


def _qr_image(data: str, scale: int = 8, ecc: str = "M") -> Image.Image:
    qr = segno.make(data, error=ecc)
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=scale, border=2, dark="black", light=None)
    buf.seek(0)
    return Image.open(buf).convert("RGBA")


def generate_banner(
    speaker_name: str,
    talk_title: str,
    date: str,
    venue: str,
    photo: Optional[str] = None,
    logo: Optional[str] = None,
    hashtag: Optional[str] = None,
    style: str = "arc",
    palette: str = "emerald",
    size: tuple[int, int] = (1080, 1080),
    output: Optional[str] = None,
    output_pdf: Optional[str] = None,
    # QR & links
    qr_data: Optional[str] = None,
    qr_ecc: str = "M",
    qr_scale: int = 8,
    site_url: Optional[str] = None,
    telegram_url: Optional[str] = None,
    palette_from: Optional[str] = None,
) -> Image.Image:
    W, H = size
    sty = PALETTES.get(palette, PALETTES["emerald"]) if not palette_from else palette_from_image("custom", palette_from)

    site_url = site_url or DEFAULT_SITE
    telegram_url = telegram_url or DEFAULT_TELEGRAM

    canvas = Image.new("RGBA", (W, H), sty.bg + (255,))
    draw = ImageDraw.Draw(canvas)

    # Styles
    if style == "gradient":
        top = Image.new("RGBA", (W, H), (*sty.primary, 255))
        bottom = Image.new("RGBA", (W, H), (*sty.accent, 255))
        grad = Image.linear_gradient("L").resize((1, H)).resize((W, H))
        bg = Image.composite(top, bottom, grad).filter(ImageFilter.GaussianBlur(30))
        canvas = Image.alpha_composite(canvas, bg.putalpha(220) or bg)
        draw = ImageDraw.Draw(canvas)
    elif style == "split":
        draw.rectangle((0, 0, int(W * 0.42), H), fill=(*sty.primary, 255))
        draw.rectangle((int(W * 0.42), 0, W, H), fill=(*sty.bg, 255))
    elif style == "card":
        card_rect = (MARGIN, int(H * 0.08), W - MARGIN, int(H * 0.92))
        draw.rounded_rectangle(card_rect, radius=40, fill=(28, 28, 32, 255))
    elif style == "arc":
        arc_w = int(min(W, H) * 0.85)
        arc_img = Image.new("RGBA", (arc_w, arc_w), (0, 0, 0, 0))
        arc_draw = ImageDraw.Draw(arc_img)
        arc_draw.ellipse((0, 0, arc_w, arc_w), fill=(*sty.primary, 255))
        hole = int(arc_w * 0.75)
        arc_draw.ellipse(((arc_w - hole)//2, (arc_w - hole)//2, (arc_w + hole)//2, (arc_w + hole)//2), fill=(0, 0, 0, 0))
        canvas.alpha_composite(arc_img, (W - arc_w - 40, H - arc_w//2))
    elif style == "pill-left":
        pill = Image.new("RGBA", (int(W*0.56), H - 2*MARGIN), (0,0,0,0))
        ImageDraw.Draw(pill).rounded_rectangle((0,0,pill.width,pill.height), radius=48, fill=(*sty.primary, 255))
        canvas.alpha_composite(pill, (MARGIN, MARGIN))
    elif style == "glass":
        frosted = Image.new("RGBA", (W - 2*MARGIN, H - 2*MARGIN), (255,255,255,48))
        ImageDraw.Draw(frosted).rounded_rectangle((0,0,frosted.width,frosted.height), radius=32, fill=(255,255,255,48))
        canvas.alpha_composite(frosted, (MARGIN, MARGIN))

    # Photo
    avatar = _load_image_sync(photo)
    if avatar is not None:
        if style in {"split", "pill-left"}:
            area = (int(W * 0.62), MARGIN, W - MARGIN, H - MARGIN)
            aw, ah = area[2] - area[0], area[3] - area[1]
            aimg = ImageOps.fit(avatar, (aw, ah), Image.LANCZOS)
            aimg = Image.alpha_composite(aimg, Image.new("RGBA", (aw, ah), (0,0,0,30)))
            canvas.alpha_composite(aimg, (area[0], area[1]))
        elif style == "arc":
            diameter = int(min(W, H) * 0.50)
            circ = circular_crop(avatar, diameter)
            circ = shadow(circ, radius=22, opacity=130, offset=(0, 10))
            canvas.alpha_composite(circ, (int(W*0.52), int(H*0.36)))
        else:
            diameter = int(min(W, H) * 0.25)
            circ = circular_crop(avatar, diameter)
            circ = shadow(circ, radius=24, opacity=140, offset=(0, 10))
            canvas.alpha_composite(circ, (MARGIN, int(H * 0.18)))

    # Text
    content_left = int(W * 0.48) if style == "split" else int(W * 0.42)
    if style in {"pill-left"}:
        content_left = int(W * 0.12)
    if style in {"arc", "glass", "gradient", "card"}:
        content_left = int(W * 0.08)

    title_max_w = int(W * 0.52) if style in {"split", "pill-left"} else int(W * 0.6)
    title_font, title_txt = auto_shrink_text(draw, talk_title, DEFAULT_TITLE_FONTS, title_max_w, max_font=96, min_font=40)
    title_y = int(H * 0.18)
    draw.multiline_text((content_left, title_y), title_txt, font=title_font, fill=(255,255,255), spacing=6)

    speaker_font = safe_font(DEFAULT_TEXT_FONTS, 44)
    draw.text((content_left, title_y + title_font.size * (title_txt.count('\n') + 1) + 18), speaker_name, font=speaker_font, fill=sty.secondary)

    meta_font = safe_font(DEFAULT_TEXT_FONTS, 34)
    meta_y = title_y + title_font.size * (title_txt.count('\n') + 1) + 18 + speaker_font.size + 14
    draw.text((content_left, meta_y), f"{date}  •  {venue}", font=meta_font, fill=sty.secondary)

    row_y = meta_y + meta_font.size + 24
    if hashtag:
        tag_font = safe_font(DEFAULT_TEXT_FONTS, 30)
        tw = int(draw.textlength(hashtag, font=tag_font)) + 28
        th = tag_font.size + 20
        draw.rounded_rectangle((content_left, row_y, content_left + tw, row_y + th), radius=th // 2, fill=(sty.accent[0], sty.accent[1], sty.accent[2], 220))
        draw.text((content_left + 14, row_y + (th - tag_font.size) // 2 - 2), hashtag, font=tag_font, fill=(255, 255, 255))
        row_y += th + 18

    row_y = _draw_urls(draw, content_left, row_y, title_max_w, sty, site_url, telegram_url)

    # QR (auto from qr_data or site)
    qr_payload = qr_data or site_url
    if qr_payload:
        qr_img = _qr_image(qr_payload, scale=qr_scale, ecc=qr_ecc)
        qr_img.thumbnail((int(W*0.14), int(H*0.2)), Image.LANCZOS)
        canvas.alpha_composite(qr_img, (W - qr_img.width - MARGIN, int(H*0.12)))

    # Logo bottom-left (fixed)
    if logo:
        logo_img = _load_image_sync(logo)
        if logo_img is not None:
            logo_img.thumbnail((int(W*0.22), int(H*0.16)), Image.LANCZOS)
            canvas.alpha_composite(logo_img, (MARGIN, H - logo_img.height - MARGIN))

    draw.rectangle((0, H - 8, W, H), fill=(*sty.primary, 255))

    if output:
        os.makedirs(os.path.dirname(output) or '.', exist_ok=True)
        canvas.convert("RGB").save(output, format="PNG", optimize=True)
    if output_pdf:
        os.makedirs(os.path.dirname(output_pdf) or '.', exist_ok=True)
        canvas.convert("RGB").save(output_pdf, format="PDF")
    return canvas