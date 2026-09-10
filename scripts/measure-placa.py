"""Arnes de la placa de "Quien soy" en Hyprland.

Cinco aserciones, y todas nacieron de un fallo real:
  1. La placa se VE en Hyprland. Sin esto el arnes sale verde con la placa
     apagada: los nodos existen en el DOM de los tres temas desde que se
     anaden, asi que contar celdas no prueba nada, y una celda con
     `display: none` no desborda y no tiene tamano fuera de escala. Es decir,
     las otras tres aserciones se autoanulan si esta falta. Medido: con los
     nodos ya en el DOM y todavia sin encender, el arnes daba 0 fallos.
  2. Ninguna celda desborda su caja. Es el fallo de "las letras se montan
     encima de otras", que se colo dos veces y no se ve a ojo.
  3. Ningun tamano de fuente cae fuera de los diez pasos de la escala. Un
     `clamp()` sobre tokens devolvia 54,5px a 1440, que no existe.
  4. La placa no existe en Vice ni en Caelestia. El patron aditivo se ha
     roto cuatro veces por olvidar el `display: none` de base.
  5. La entrada se VE. El disparador de las celdas era `is-lit` de la
     SECCION (`start: "top 90%"`), no de la placa: la placa esta 239px por
     debajo del borde superior de la seccion en escritorio y 161px en movil,
     asi que cuando la seccion se encendia la placa ya estaba 119px bajo el
     pliegue a 900px de alto (1019 sobre 900) y 41px bajo el pliegue a 844
     (885 sobre 844) — las siete celdas aterrizaban a los 1200ms enteras
     fuera de pantalla. Esta asercion baja hasta un punto en que la seccion
     ya recibio `is-lit` pero la placa sigue entera bajo el pliegue y
     comprueba que NINGUNA celda ha aterrizado todavia; luego sube hasta que
     la placa entra en su propio umbral y comprueba que las siete aterrizan
     de verdad. Contra el codigo sin arreglar, el primer paso sale ROJO
     (aterrizan las 7 de 7 sin que la placa se vea).
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


def placa_visible(pg) -> bool:
    return pg.evaluate(
        "() => { const n = document.querySelector('[data-placa]');"
        " if (!n) return false;"
        " const r = n.getBoundingClientRect();"
        " return getComputedStyle(n).display !== 'none' && r.width > 0 && r.height > 0; }"
    )


def entrada_se_ve(pg, fallos: list, nombre: str) -> None:
    """Asercion 5: la entrada de la placa corre entera EN pantalla.

    Pagina propia, sin scroll previo (las otras aserciones ya han hecho
    scroll y contaminarian esta medida).
    """
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"about\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        fallos.append(f"[{nombre}] entrada: no existe [data-scene=about]")
        return

    inner_h = pg.evaluate("() => window.innerHeight")

    # Paso A: la seccion ya cruzo su umbral (top 90%) pero la placa entera
    # sigue bajo el pliegue.
    pg.evaluate(f"window.scrollTo(0, {top} - {inner_h} * 0.9 + 20)")
    pg.wait_for_timeout(400)
    placa_top_a = pg.evaluate(
        "() => { const p = document.querySelector('[data-placa]');"
        " return p ? p.getBoundingClientRect().top : -1; }"
    )
    if placa_top_a < inner_h:
        fallos.append(
            f"[{nombre}] entrada paso A: la placa no quedo bajo el pliegue "
            f"(top {placa_top_a}px, viewport {inner_h}px) — el arnes no puede "
            f"plantear este escenario en este viewport"
        )
        return

    pg.wait_for_timeout(1500)
    opacidades_a = pg.evaluate(
        "() => Array.from(document.querySelectorAll('[data-placa-celda]'))"
        ".map(c => getComputedStyle(c).opacity)"
    )
    if not opacidades_a:
        fallos.append(f"[{nombre}] entrada paso A: la placa no tiene celdas")
        return
    aterrizadas_de_mas = [op for op in opacidades_a if op != "0"]
    if aterrizadas_de_mas:
        fallos.append(
            f"[{nombre}] entrada paso A: {len(aterrizadas_de_mas)}/{len(opacidades_a)} "
            f"celdas aterrizaron con la placa a {placa_top_a}px bajo el pliegue "
            f"(deberian seguir en opacity 0): {aterrizadas_de_mas}"
        )

    # Paso B: sube hasta que la placa entra en SU propio umbral (top 80%).
    placa_doc_y = pg.evaluate(
        "() => { const p = document.querySelector('[data-placa]');"
        " const r = p.getBoundingClientRect(); return r.top + window.scrollY; }"
    )
    pg.evaluate(f"window.scrollTo(0, {placa_doc_y} - {inner_h} * 0.5)")
    pg.wait_for_timeout(1500)
    placa_top_b = pg.evaluate(
        "() => { const p = document.querySelector('[data-placa]');"
        " return p ? p.getBoundingClientRect().top : -1; }"
    )
    if placa_top_b >= inner_h * 0.8:
        fallos.append(
            f"[{nombre}] entrada paso B: la placa sigue fuera de su umbral "
            f"(top {placa_top_b}px, umbral {inner_h * 0.8}px)"
        )
        return

    lit = pg.evaluate(
        "() => { const p = document.querySelector('[data-placa]');"
        " return p ? p.classList.contains('placa-lit') : false; }"
    )
    if not lit:
        fallos.append(f"[{nombre}] entrada paso B: la placa no lleva 'placa-lit'")

    celdas_b = pg.evaluate(
        "() => Array.from(document.querySelectorAll('[data-placa-celda]'))"
        ".map(c => ({ op: getComputedStyle(c).opacity, tf: getComputedStyle(c).transform }))"
    )
    sin_aterrizar = [c for c in celdas_b if c["op"] != "1" or c["tf"] != "none"]
    if sin_aterrizar:
        fallos.append(
            f"[{nombre}] entrada paso B: {len(sin_aterrizar)}/{len(celdas_b)} "
            f"celdas no aterrizaron dentro de su propio umbral: {sin_aterrizar}"
        )


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

            if not placa_visible(pg):
                fallos.append(f"[{nombre}] la placa NO se ve en Hyprland")

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

        # Asercion 5, pagina propia por viewport: no reutiliza las de arriba,
        # que ya han hecho scroll.
        for nombre, w, h in VIEWPORTS:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(f"{args.url}/?theme=hyprland", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(9000)
            entrada_se_ve(pg, fallos, nombre)
            pg.close()

        # La placa no puede existir en los otros dos temas.
        for tema in ("vice", "caelestia"):
            pg = b.new_page(viewport={"width": 1440, "height": 900})
            pg.goto(f"{args.url}/?theme={tema}", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(9000)
            ir_a_about(pg)
            if placa_visible(pg):
                fallos.append(f"[{tema}] la placa esta VISIBLE y no deberia")
            pg.close()

        b.close()

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
