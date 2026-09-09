"""Arnes de los cimientos de "Stack" en Hyprland (spec 2026-09-09).

Trece gates, uno por familia del spec (`## Los gates`). Cada uno nacio de un
fallo real de esta pista o de otra, y ninguno se acepto sin verlo dar rojo
contra el fallo que dice cazar:

  1. Los cimientos se VEN en Hyprland, y el generico `.credits-grid` NO. Sin
     esto los demas gates se autoanulan: un nodo con `display: none` no
     desborda ni descuadra (leccion de measure-placa.py y measure-catastro.py).
  2. Los cimientos NO existen en Vice ni en Caelestia (comprobados por
     separado, no con un AND que taparia un huerfano), y la bandeja de
     Caelestia sigue con sus 23 piezas.
 13. Consola: cero errores y cero "context lost" en las TRES paginas. Sin
     oyente en Vice y Caelestia un fallo global en themes.css dejaba el gate
     en verde (pagado en measure-caelestia-cursor.py).

Los gates 3-12 se documentan en su propia funcion segun se anaden.

Nota sobre el contador de 23 nombres (gate 1): solo se comprueba SI
`[data-cimientos]` se ve. Contra el catastro actual el nodo no existe, y
contar 0 nombres sobre un dispositivo que aun no existe no es un fallo nuevo
-- es el mismo fallo que ya reporta la primera comprobacion de este gate. Sin
la condicion, el catastro daria 6 fallos (3 por viewport) en vez de los 4 que
el propio dispositivo-cero de la tarea 1 espera ver, y el tercero seria ruido
que tapa la senal real. Una vez exista `[data-cimientos]`, el contador vuelve
a mandar de verdad.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

VIEWPORTS = [("escritorio", 1440, 900), ("movil", 390, 844)]
ANCHOS_DESBORDE = [390, 821, 1024, 1200, 1440]


def abrir(b, url: str, tema: str, w: int, h: int, errores: list, reduce: bool = False):
    """Pagina nueva con oyente de consola SIEMPRE puesto. `errores` acumula
    los de todas las paginas: el gate 13 los lee al final."""
    ctx = b.new_context(
        viewport={"width": w, "height": h},
        reduced_motion="reduce" if reduce else "no-preference",
    )
    pg = ctx.new_page()
    etiqueta = f"{tema} {w}x{h}"
    pg.on(
        "console",
        lambda m: errores.append(f"[{etiqueta}] {m.type}: {m.text}")
        if m.type == "error" or "context lost" in m.text.lower()
        else None,
    )
    pg.on("pageerror", lambda e: errores.append(f"[{etiqueta}] pageerror: {e}"))
    pg.goto(f"{url}/?theme={tema}", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(9000)
    return pg


def ir_a_credits(pg, offset: int = 0) -> bool:
    """Coloca el borde superior de la escena a `offset` px del tope. Lenis
    sigue desplazando tras un scrollTo: se espera a que asiente."""
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"credits\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        return False
    pg.evaluate(f"window.scrollTo(0, {top + offset})")
    pg.wait_for_timeout(2500)
    return True


def se_ve(pg, selector: str) -> bool:
    return pg.evaluate(
        "(sel) => { const n = document.querySelector(sel); if (!n) return false;"
        " const s = getComputedStyle(n); const r = n.getBoundingClientRect();"
        " return s.display !== 'none' && s.visibility !== 'hidden'"
        "   && parseFloat(s.opacity) > 0 && r.width > 0 && r.height > 0; }",
        selector,
    )


def gate_1_se_ven(pg, nombre: str, fallos: list) -> None:
    cimientos_visibles = se_ve(pg, "[data-cimientos]")
    if not cimientos_visibles:
        fallos.append(f"[{nombre}] gate 1: [data-cimientos] NO se ve en Hyprland")
    if se_ve(pg, ".credits-grid"):
        fallos.append(f"[{nombre}] gate 1: el generico .credits-grid SE PINTA bajo Hyprland")
    if cimientos_visibles:
        n = pg.evaluate("() => document.querySelectorAll('[data-cimientos] .cim-nombre').length")
        if n != 23:
            fallos.append(f"[{nombre}] gate 1: {n} nombres en los cimientos, esperados 23")


def gate_2_no_existen_en_otros(b, url: str, errores: list, fallos: list) -> None:
    for tema in ("vice", "caelestia"):
        pg = abrir(b, url, tema, 1440, 900, errores)
        ir_a_credits(pg)
        if se_ve(pg, "[data-cimientos]"):
            fallos.append(f"[{tema}] gate 2: [data-cimientos] esta VISIBLE y no deberia")
        if tema == "caelestia":
            piezas = pg.evaluate("() => document.querySelectorAll('.cae-cred-pieza').length")
            if piezas != 23:
                fallos.append(f"[caelestia] gate 2: la bandeja tiene {piezas} piezas, esperadas 23")
        pg.context.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:4173")
    ap.add_argument("--contraste", action="store_true", help="gate 10 (hallazgo de producto abierto)")
    args = ap.parse_args()

    fallos: list[str] = []
    errores: list[str] = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])

        for nombre, w, h in VIEWPORTS:
            pg = abrir(b, args.url, "hyprland", w, h, errores)
            if not ir_a_credits(pg):
                fallos.append(f"[{nombre}] no existe [data-scene=credits]")
                pg.context.close()
                continue
            gate_1_se_ven(pg, nombre, fallos)
            pg.context.close()

        gate_2_no_existen_en_otros(b, args.url, errores, fallos)
        b.close()

    for e in errores:
        fallos.append(f"gate 13: consola: {e}")

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
