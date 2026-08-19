#!/usr/bin/env python3
"""El haz al mando — verificacion del fondo de Hyprland.

No arregla nada: mide, contra el build de produccion servido (nunca
`npm run dev`: el HMR corrompe las medidas). Cinco aserciones, las que fija
el spec en docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md,
seccion "## Verificacion":

  1. Techo de banda tipografica <= 46 (p99.5), 12 posiciones de scroll x 3
     viewports (390x844, 768x1024, 1440x900).
  2. El corte del segundo haz cae en el limite REAL de la seccion de
     creditos (su offsetTop / alto desplazable), no en un literal fijo.
  3. Sin deriva temporal: a scroll fijo, >= 160s de muestreo, recorrido de
     la mediana de luma <= 2.0.
  4. Canto duro visible: salto de luminancia >= 12 entre pixeles contiguos
     en la banda del haz, en los tres viewports.
  5. `prefers-reduced-motion`: dos capturas separadas 5s a scroll fijo,
     identicas.

Uso:
    npm run build && npx vite preview --port 4173
    python3 scripts/measure-fondo-haz.py [--base URL] [--json OUT]

Requiere `executable_path=/usr/bin/google-chrome` (el chromium propio de
Playwright no esta descargado en esta maquina) y `--use-gl=swiftshader`
para que el fondo WebGL renderice en headless.
"""

from __future__ import annotations

import argparse
import io
import json
import statistics
import sys

from playwright.sync_api import sync_playwright
from PIL import Image

CHROME = "/usr/bin/google-chrome"
DEFAULT_BASE = "http://127.0.0.1:4173"

VIEWPORTS = [
    {"width": 390, "height": 844},
    {"width": 768, "height": 1024},
    {"width": 1440, "height": 900},
]

BANDA_TOP = 0.06
BANDA_BOTTOM = 0.74
TECHO_BANDA = 46.0

N_POSICIONES = 12
DERIVA_SEGUNDOS = 160
DERIVA_PASO = 14
DERIVA_MAX_RECORRIDO = 2.0

CANTO_SALTO_MIN = 12.0

HIDE_CONTENT_CSS = (
    "#app > *:not(.bg-theme):not(.bg-noise) { visibility: hidden !important; }"
)


def luminancia(r: int, g: int, b: int) -> float:
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def percentil(valores: list[float], p: float) -> float:
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


def banda_p995(png_bytes: bytes, alto_viewport: int) -> float:
    imagen = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    ancho_px, alto_px = imagen.size
    escala_y = alto_px / alto_viewport
    top_px = int(BANDA_TOP * alto_viewport * escala_y)
    bottom_px = int(BANDA_BOTTOM * alto_viewport * escala_y)

    pixeles = imagen.load()
    luminancias: list[float] = []
    for y in range(top_px, bottom_px):
        for x in range(ancho_px):
            r, g, b = pixeles[x, y]
            luminancias.append(luminancia(r, g, b))
    return percentil(luminancias, 99.5)


def fila_luma(png_bytes: bytes, frac_y: float) -> list[float]:
    """Luminancia a lo largo de una fila horizontal, para el salto de canto."""
    imagen = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    ancho_px, alto_px = imagen.size
    y = min(int(frac_y * alto_px), alto_px - 1)
    pixeles = imagen.load()
    return [luminancia(*pixeles[x, y]) for x in range(ancho_px)]


def mayor_salto(fila: list[float]) -> float:
    return max((abs(fila[i + 1] - fila[i]) for i in range(len(fila) - 1)), default=0.0)


def imagenes_iguales(a: bytes, b: bytes, margen: float = 1.0) -> bool:
    im_a = Image.open(io.BytesIO(a)).convert("RGB")
    im_b = Image.open(io.BytesIO(b)).convert("RGB")
    if im_a.size != im_b.size:
        return False
    px_a, px_b = im_a.load(), im_b.load()
    ancho, alto = im_a.size
    diffs = []
    for y in range(0, alto, 4):  # muestreo cada 4px: rapido, suficiente
        for x in range(0, ancho, 4):
            ra, ga, ba = px_a[x, y]
            rb, gb, bb = px_b[x, y]
            diffs.append(abs(luminancia(ra, ga, ba) - luminancia(rb, gb, bb)))
    return statistics.mean(diffs) <= margen


def hide_content(pg) -> None:
    pg.add_style_tag(content=HIDE_CONTENT_CSS)
    pg.wait_for_timeout(300)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    url = f"{args.base.rstrip('/')}/?theme=hyprland"
    fallos: list[str] = []
    reporte: dict[str, object] = {}

    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path=CHROME,
            headless=True,
            args=["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"],
        )

        # --- 1. Techo de banda, 3 viewports x 12 posiciones ---
        techo_reporte = []
        for viewport in VIEWPORTS:
            pg = b.new_page(viewport=viewport)
            pg.goto(url, wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(6000)
            hide_content(pg)

            alto_total = pg.evaluate("document.documentElement.scrollHeight")
            max_scroll = max(alto_total - viewport["height"], 0)
            posiciones = [round(max_scroll * i / (N_POSICIONES - 1)) for i in range(N_POSICIONES)]

            peor = 0.0
            for y in posiciones:
                pg.evaluate(f"window.scrollTo(0, {y})")
                pg.wait_for_timeout(500)
                png = pg.screenshot()
                banda = banda_p995(png, viewport["height"])
                peor = max(peor, banda)
                if banda > TECHO_BANDA:
                    fallos.append(
                        f"[1-techo] {viewport['width']}x{viewport['height']} scroll={y}: "
                        f"banda p99.5={banda:.1f} > techo {TECHO_BANDA}"
                    )
            techo_reporte.append({"viewport": viewport, "peor_banda": peor})
            print(f"[1] {viewport['width']}x{viewport['height']}: peor banda p99.5={peor:.2f}")
            pg.close()
        reporte["techo"] = techo_reporte

        # --- 2. Corte del segundo haz en el limite real ---
        pg = b.new_page(viewport=VIEWPORTS[-1])
        pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(6000)

        entrada_esperada = pg.evaluate(
            """() => {
                const creditos = document.getElementById('creditos');
                const scrollable = document.documentElement.scrollHeight - window.innerHeight;
                if (!creditos || scrollable <= 0) return null;
                return creditos.offsetTop / scrollable;
            }"""
        )
        if entrada_esperada is None:
            fallos.append("[2-corte] no se pudo calcular el offsetTop de #creditos")
        else:
            hide_content(pg)
            alto_total = pg.evaluate("document.documentElement.scrollHeight")
            max_scroll = alto_total - VIEWPORTS[-1]["height"]

            # Barre uScroll entre 0.70 y 0.80 en pasos finos y detecta el
            # salto de luminancia del segundo haz por el crecimiento del
            # maximo de la banda respecto al fotograma anterior.
            pasos = [0.70 + i * 0.002 for i in range(51)]
            anterior = None
            salto_en = None
            for frac in pasos:
                y = round(max_scroll * frac)
                pg.evaluate(f"window.scrollTo(0, {max(y, 0)})")
                pg.wait_for_timeout(150)
                png = pg.screenshot()
                banda = banda_p995(png, VIEWPORTS[-1]["height"])
                if anterior is not None and banda - anterior > 2.0 and salto_en is None:
                    salto_en = frac
                anterior = banda

            if salto_en is None:
                fallos.append(
                    "[2-corte] no se detecto salto de luminancia del segundo haz "
                    "entre uScroll 0.70 y 0.80"
                )
            elif abs(salto_en - entrada_esperada) > 0.03:
                fallos.append(
                    f"[2-corte] corte detectado en uScroll={salto_en:.3f}, "
                    f"esperado (offsetTop de #creditos)={entrada_esperada:.3f}"
                )
            print(
                f"[2] corte esperado={entrada_esperada:.3f} "
                f"detectado={salto_en if salto_en is not None else 'ninguno'}"
            )
            reporte["corte"] = {"esperado": entrada_esperada, "detectado": salto_en}
        pg.close()

        # --- 3. Sin deriva temporal, a scroll fijo ---
        pg = b.new_page(viewport=VIEWPORTS[-1])
        pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(6000)
        hide_content(pg)
        alto_total = pg.evaluate("document.documentElement.scrollHeight")
        pg.evaluate(f"window.scrollTo(0, {round((alto_total - 900) * 0.4)})")
        pg.wait_for_timeout(500)

        muestras = []
        t = 0
        while t <= DERIVA_SEGUNDOS:
            png = pg.screenshot()
            muestras.append(banda_p995(png, VIEWPORTS[-1]["height"]))
            pg.wait_for_timeout(DERIVA_PASO * 1000)
            t += DERIVA_PASO

        mediana = statistics.median(muestras)
        recorrido = max(muestras) - min(muestras)
        if recorrido > DERIVA_MAX_RECORRIDO:
            fallos.append(
                f"[3-deriva] recorrido de mediana={recorrido:.2f} > "
                f"maximo {DERIVA_MAX_RECORRIDO} (mediana={mediana:.2f}, muestras={muestras})"
            )
        print(f"[3] deriva: recorrido={recorrido:.2f} (max {DERIVA_MAX_RECORRIDO}), mediana={mediana:.2f}")
        reporte["deriva"] = {"recorrido": recorrido, "mediana": mediana, "muestras": muestras}
        pg.close()

        # --- 4. Canto duro visible, 3 viewports ---
        canto_reporte = []
        for viewport in VIEWPORTS:
            pg = b.new_page(viewport=viewport)
            pg.goto(url, wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(6000)
            hide_content(pg)
            png = pg.screenshot()
            salto = mayor_salto(fila_luma(png, 0.5))
            canto_reporte.append({"viewport": viewport, "salto": salto})
            if salto < CANTO_SALTO_MIN:
                fallos.append(
                    f"[4-canto] {viewport['width']}x{viewport['height']}: "
                    f"mayor salto={salto:.1f} < minimo {CANTO_SALTO_MIN}"
                )
            print(f"[4] {viewport['width']}x{viewport['height']}: mayor salto={salto:.1f}")
            pg.close()
        reporte["canto"] = canto_reporte

        # --- 5. prefers-reduced-motion: estatico ---
        ctx = b.new_context(viewport=VIEWPORTS[-1], reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(4000)
        hide_content(pg)
        primera = pg.screenshot()
        pg.wait_for_timeout(5000)
        segunda = pg.screenshot()
        if not imagenes_iguales(primera, segunda):
            fallos.append("[5-reduced-motion] dos capturas separadas 5s no son identicas")
        print(f"[5] reduced-motion: {'estatico' if imagenes_iguales(primera, segunda) else 'CAMBIA'}")
        pg.close()
        ctx.close()

        b.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"url": url, "reporte": reporte, "fallos": fallos}, f, indent=2)
        print(f"\nmedidas volcadas en {args.json}")

    print()
    for fallo in fallos:
        print("FALLO:", fallo)

    if fallos:
        print(f"\n{len(fallos)} aserciones fallidas de 5")
        return 1

    print("\nTODO OK — las 5 aserciones del haz al mando pasan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
