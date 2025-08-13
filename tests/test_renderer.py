from __future__ import annotations
from bannerforge.renderer import generate_banner

def test_generate_banner(tmp_path):
    out = tmp_path / "banner.png"
    img = generate_banner(
        speaker_name="Test Speaker",
        talk_title="Testing Title",
        date="2025-08-13",
        venue="Test Venue",
        photo=None,
        style="arc",
        palette="emerald",
        size=(800, 800),
        output=str(out),
    )
    assert out.exists()
    assert img.size == (800, 800)