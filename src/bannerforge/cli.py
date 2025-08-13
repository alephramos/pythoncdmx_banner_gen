from __future__ import annotations
import typer
from .renderer import generate_banner

app = typer.Typer(add_completion=False, help="Generate event banners")

@app.command()
def main(
    speaker: str = typer.Option(..., help="Speaker name"),
    title: str = typer.Option(..., help="Talk title"),
    date: str = typer.Option(..., help="Date string"),
    venue: str = typer.Option(..., help="Venue string"),
    photo: str | None = typer.Option(None, help="URL or path to speaker photo"),
    logo: str | None = typer.Option(None, help="URL or path to logo"),
    hashtag: str | None = typer.Option(None, help="Hashtag or short tagline"),
    style: str = typer.Option("arc", help="Style"),
    palette: str = typer.Option("emerald", help="Palette"),
    size: str = typer.Option("1080x1080", help="Canvas size WxH"),
    output: str = typer.Option("out/banner.png", help="Output PNG path"),
    pdf: str | None = typer.Option(None, help="Optional PDF output path"),
    site_url: str | None = typer.Option(None, help="Site URL (default pythoncdmx.org)"),
    telegram_url: str | None = typer.Option(None, help="Telegram URL (default t.me/PythonCDMX)"),
    palette_from: str | None = typer.Option(None, help="Image to extract palette"),
    qr_data: str | None = typer.Option(None, help="Data for QR (defaults to site_url)"),
    qr_ecc: str = typer.Option("M", help="QR ECC L/M/Q/H"),
    qr_scale: int = typer.Option(8, help="QR scale (px per module)"),
):
    w, h = _parse_size(size)
    img = generate_banner(
        speaker_name=speaker,
        talk_title=title,
        date=date,
        venue=venue,
        photo=photo,
        logo=logo,
        hashtag=hashtag,
        style=style,
        palette=palette,
        size=(w, h),
        output=output,
        output_pdf=pdf,
        site_url=site_url,
        telegram_url=telegram_url,
        palette_from=palette_from,
        qr_data=qr_data,
        qr_ecc=qr_ecc,
        qr_scale=qr_scale,
    )
    typer.echo(f"Saved: {output}{' and ' + pdf if pdf else ''}")


def _parse_size(s: str) -> tuple[int, int]:
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception:
        return 1600, 900

if __name__ == "__main__":
    app()