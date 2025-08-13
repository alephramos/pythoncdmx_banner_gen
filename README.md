# BannerForge

Genera banners de eventos con tipografía **CommitMono Nerd Fonts**, QR automático y exportación a PNG/PDF.

### Presets de tamaño
- 1080x1080 (square)
- 1920x1080 (landscape)
- 1200x628 (social preview)

### Quickstart
```bash
pip install -e .
uvicorn bannerforge.api.server:app --reload --port 8080
```

### CLI ejemplo
```bash
bannerforge \
  --speaker "Juan Gomez" \
  --title "Escalando tus aplicaciones Python con Ray" \
  --date "Agosto 12 · 18:30" \
  --venue "Jardín Chapultepec" \
  --photo assets/samples/sample.jpg \
  --logo assets/samples/logo_pythoncdmx.png \
  --hashtag "#pythoncdmx" \
  --style arc \
  --palette emerald \
  --size 1080x1080 \
  --output out/banner-1080.png \
  --pdf out/banner-1080.pdf
```

### Paleta desde imagen
Usa `--palette-from /ruta/imagen_referencia.png` para extraer colores automáticamente.

### QR automático
Si no pasas `--qr-data`, el QR codifica `https://pythoncdmx.org` por defecto. Puedes cambiarlo con `--qr-data`.
```

---

## .gitignore
```gitignore
__pycache__/
*.py[cod]
.venv/
.env
out/
*.png
node_modules/
```

---

## .dockerignore
```
.git
__pycache__
.venv
out
node_modules
*.png