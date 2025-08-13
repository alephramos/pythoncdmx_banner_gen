from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    speaker: str
    title: str
    date: str
    venue: str
    photo: Optional[str] = None
    logo: Optional[str] = None
    hashtag: Optional[str] = None
    style: str = Field(default="arc", pattern="^(gradient|split|card|arc|pill-left|glass)$")
    palette: str = Field(default="emerald")
    size: str = Field(default="1080x1080")

    # QR
    qr_data: Optional[str] = None           # if None -> uses site_url default
    qr_ecc: str = Field(default="M", pattern="^[LMQH]$")
    qr_scale: int = Field(default=8, ge=1, le=30)

    # Links / palette
    site_url: Optional[str] = None          # default set in renderer
    telegram_url: Optional[str] = None      # default set in renderer
    palette_from: Optional[str] = None