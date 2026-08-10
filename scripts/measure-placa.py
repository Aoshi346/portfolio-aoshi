"""Arnes de la placa de "Quien soy" en Hyprland.

Tres aserciones, y las tres nacieron de un fallo real del prototipo:
  1. Ninguna celda desborda su caja. Es el fallo de "las letras se montan
     encima de otras", que se colo dos veces y no se ve a ojo.
  2. Ningun tamano de fuente cae fuera de los diez pasos de la escala. Un
     `clamp()` sobre tokens devolvia 54,5px a 1440, que no existe.
  3. La placa no existe en Vice ni en Caelestia. El patron aditivo se ha
     roto cuatro veces por olvidar el `display: none` de base.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

ESCALA = [12, 16, 21.33, 28.43, 37.9, 50.52, 67.4, 89.85, 119.77, 159.66]
VIEWPORTS = [("escritorio", 1440, 900), ("movil", 390, 844)]


def ir_a_about(pg):
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"about\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        return False
    pg.evaluate(f"window.scrollTo(0, {top})")
    pg.wait_for_timeout(2500)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:4173")
    args = ap.parse_args()

    fallos = []
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--use-gl=swiftshader"],
        )

        for nombre, w, h in VIEWPORTS:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(f"{args.url}/?theme=hyprland", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(9000)
            if not ir_a_about(pg):
                fallos.append(f"[{nombre}] no existe [data-scene=about]")
                pg.close()
                continue

            celdas = pg.evaluate(
                "() => Array.from(document.querySelectorAll('[data-placa-celda]')).map(c => ({"
                " k: c.dataset.placaCelda, sh: c.scrollHeight, ch: c.clientHeight,"
                " sw: c.scrollWidth, cw: c.clientWidth }))"
            )
            if not celdas:
                fallos.append(f"[{nombre}] la placa no tiene celdas")
            for c in celdas:
                if c["sh"] > c["ch"] + 2 or c["sw"] > c["cw"] + 2:
                    fallos.append(
                        f"[{nombre}] celda '{c['k']}' desborda: "
                        f"{c['sw']}x{c['sh']} en {c['cw']}x{c['ch']}"
                    )

            tallas = pg.evaluate(
                "() => Array.from(document.querySelectorAll('[data-placa] *'))"
                ".filter(e => e.childElementCount === 0 && e.textContent.trim())"
                ".map(e => ({ t: e.textContent.trim().slice(0, 24),"
                " s: parseFloat(getComputedStyle(e).fontSize) }))"
            )
            for t in tallas:
                if not any(abs(t["s"] - paso) < 0.06 for paso in ESCALA):
                    fallos.append(f"[{nombre}] '{t['t']}' a {t['s']}px, fuera de la escala")
            pg.close()

        # La placa no puede existir en los otros dos temas.
        for tema in ("vice", "caelestia"):
            pg = b.new_page(viewport={"width": 1440, "height": 900})
            pg.goto(f"{args.url}/?theme={tema}", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(9000)
            ir_a_about(pg)
            visible = pg.evaluate(
                "() => { const n = document.querySelector('[data-placa]');"
                " if (!n) return false;"
                " const r = n.getBoundingClientRect();"
                " return getComputedStyle(n).display !== 'none' && r.width > 0 && r.height > 0; }"
            )
            if visible:
                fallos.append(f"[{tema}] la placa esta VISIBLE y no deberia")
            pg.close()

        b.close()

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
