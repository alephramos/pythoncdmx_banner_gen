from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from ..models import GenerateRequest
from ..renderer import generate_banner

app = FastAPI(title="BannerForge")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/generate")
def api_generate(payload: GenerateRequest):
    try:
        w, h = _parse_size(payload.size)
        img = generate_banner(
            speaker_name=payload.speaker,
            talk_title=payload.title,
            date=payload.date,
            venue=payload.venue,
            photo=payload.photo,
            logo=payload.logo,
            hashtag=payload.hashtag,
            style=payload.style,
            palette=payload.palette,
            size=(w, h),
            qr_data=payload.qr_data,
            qr_ecc=payload.qr_ecc,
            qr_scale=payload.qr_scale,
            site_url=payload.site_url,
            telegram_url=payload.telegram_url,
            palette_from=payload.palette_from,
        )
    except Exception as e:
        raise HTTPException(400, str(e))
    import io
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=True)
    return Response(content=buf.getvalue(), media_type="image/png")


def _parse_size(s: str) -> tuple[int, int]:
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception:
        return 1600, 900