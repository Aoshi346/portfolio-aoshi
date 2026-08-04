#!/usr/bin/env python3
"""Techo de brillo del fondo generativo de Vice.

El instrumento va antes que el fondo nuevo: sin el, "se ve oscuro" es una
opinion. Este arnes mide, no arregla.

Que mide, y por que:

  Se oculta el contenido (`#app { visibility: hidden }`) para aislar SOLO el
  fondo generativo — con el contenido visible se estaria midiendo tipografia
  y tarjetas, no el shader. Se recorren al menos 12 posiciones de scroll
  (el fondo es generativo/animado y varia con el scroll y con el tiempo) y en
  cada una se calcula:

    - p99.5 de luminancia en la franja vertical 0.06-0.74 del alto de
      VIEWPORT (no de la pagina completa con scroll): es la banda donde vive
      la tipografia, y es contra eso que se calibro el gate de contraste.
    - p99.5 de luminancia del fotograma entero.
    - el pixel mas claro del fotograma entero.

Luminancia perceptual: 0.2126*R + 0.7152*G + 0.0722*B sobre valores 0-255.

Techos (salen 1 si se superan):
    franja:    62
    fotograma: 82
    pixel:     150

Uso:
    npm run build && npx vite preview --port 4173
    python3 scripts/measure-bg-luma.py [--url URL] [--json OUT]

Requiere `executable_path=/usr/bin/google-chrome`: el chromium propio de
Playwright no esta descargado en esta maquina. Y `--use-gl=swiftshader`
para que el fondo WebGL renderice en headless.
"""

from __future__ import annotations

import argparse
import io
import json
import sys

from playwright.sync_api import sync_playwright
from PIL import Image

VIEWPORT = {"width": 1440, "height": 900}
DEFAULT_URL = "http://127.0.0.1:4173/?theme=vice"
CHROME = "/usr/bin/google-chrome"

BANDA_TOP = 0.06
BANDA_BOTTOM = 0.74

TECHO_BANDA = 62.0
TECHO_FOTOGRAMA = 82.0
TECHO_PIXEL = 150.0

# Al menos 12 posiciones de scroll (el brief lo pide explicito): el fondo es
# generativo y varia con el scroll, asi que una sola posicion no lo cubre.
N_POSICIONES = 12


def luminancia(r: int, g: int, b: int) -> float:
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def percentil(valores: list[float], p: float) -> float:
    """Percentil por interpolacion lineal (metodo comun, sin numpy)."""
    if not valores:
        return 0.0
    datos = sorted(valores)
    if len(datos) == 1:
        return datos[0]
    rango = (len(datos) - 1) * (p / 100.0)
    bajo = int(rango)
    alto = min(bajo + 1, len(datos) - 1)
    frac = rango - bajo
    return datos[bajo] + (datos[alto] - datos[bajo]) * frac


def mide_fotograma(png_bytes: bytes, alto_viewport: int) -> dict[str, float]:
    imagen = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    ancho_px, alto_px = imagen.size
    escala_y = alto_px / alto_viewport

    banda_top_px = int(BANDA_TOP * alto_viewport * escala_y)
    banda_bottom_px = int(BANDA_BOTTOM * alto_viewport * escala_y)

    pixeles = imagen.load()
    luminancias_fotograma: list[float] = []
    luminancias_banda: list[float] = []
    maximo = 0.0

    for y in range(alto_px):
        en_banda = banda_top_px <= y < banda_bottom_px
        for x in range(ancho_px):
            r, g, b = pixeles[x, y]
            lum = luminancia(r, g, b)
            luminancias_fotograma.append(lum)
            if en_banda:
                luminancias_banda.append(lum)
            if lum > maximo:
                maximo = lum

    return {
        "banda_p995": percentil(luminancias_banda, 99.5),
        "fotograma_p995": percentil(luminancias_fotograma, 99.5),
        "pixel_max": maximo,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--json", default=None, help="fichero opcional para volcar las medidas")
    args = parser.parse_args()

    fallos: list[str] = []
    medidas: list[dict[str, object]] = []

    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path=CHROME,
            headless=True,
            args=["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"],
        )
        pg = b.new_page(viewport=VIEWPORT)
        pg.goto(args.url, wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(9000)  # leader de apertura + GSAP + arranque del shader

        # Aisla el fondo: sin esto se mide tipografia y tarjetas, no el shader.
        pg.add_style_tag(content="#app { visibility: hidden !important; }")
        pg.wait_for_timeout(300)

        alto_total = pg.evaluate("document.documentElement.scrollHeight")
        alto_viewport = VIEWPORT["height"]
        max_scroll = max(alto_total - alto_viewport, 0)

        posiciones = [
            round(max_scroll * i / (N_POSICIONES - 1)) for i in range(N_POSICIONES)
        ]

        for i, y in enumerate(posiciones):
            pg.evaluate(f"window.scrollTo(0, {y})")
            pg.wait_for_timeout(600)  # asienta Lenis + deja avanzar el shader
            png_bytes = pg.screenshot()
            m = mide_fotograma(png_bytes, alto_viewport)
            medidas.append({"scroll_y": y, **m})

            etiqueta = f"scroll={y}"
            if m["banda_p995"] > TECHO_BANDA:
                fallos.append(
                    f"{etiqueta}: banda p99.5={m['banda_p995']:.1f} > techo {TECHO_BANDA}"
                )
            if m["fotograma_p995"] > TECHO_FOTOGRAMA:
                fallos.append(
                    f"{etiqueta}: fotograma p99.5={m['fotograma_p995']:.1f} > techo {TECHO_FOTOGRAMA}"
                )
            if m["pixel_max"] > TECHO_PIXEL:
                fallos.append(
                    f"{etiqueta}: pixel mas claro={m['pixel_max']:.1f} > techo {TECHO_PIXEL}"
                )
            print(
                f"scroll={y:>5}  banda={m['banda_p995']:6.2f}  "
                f"fotograma={m['fotograma_p995']:6.2f}  pixel={m['pixel_max']:6.2f}"
            )

        b.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"url": args.url, "medidas": medidas, "fallos": fallos}, f, indent=2)
        print(f"\nmedidas volcadas en {args.json}")

    print()
    for fallo in fallos:
        print("FALLO:", fallo)

    if fallos:
        print(f"\n{len(fallos)} superaciones de techo de brillo")
        return 1

    banda_max = max(m["banda_p995"] for m in medidas)
    fotograma_max = max(m["fotograma_p995"] for m in medidas)
    pixel_max = max(m["pixel_max"] for m in medidas)
    print(
        f"TODO OK — peor banda {banda_max:.2f}/{TECHO_BANDA}, "
        f"peor fotograma {fotograma_max:.2f}/{TECHO_FOTOGRAMA}, "
        f"peor pixel {pixel_max:.2f}/{TECHO_PIXEL}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
