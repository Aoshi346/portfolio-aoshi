"""Arnes del cursor "luz de mano" de Hyprland.

Cada asercion nace de un fallo real ya pagado en este repo:
  1. El lienzo EXISTE en Hyprland y NO existe en Vice ni en Caelestia. Sin
     esto el arnes sale verde con el cursor apagado: el patron aditivo se ha
     roto cuatro veces en este proyecto por olvidar el caso base.
  2. El charco se enciende sobre un pulsable y NO se enciende sobre texto
     corrido. Es la unica asercion que prueba el reparto de senal.
  3. Tras desplazar con el raton QUIETO, el estado se recalcula. Medido en
     Vice: parado sobre texto tras desplazar, la marca seguia dibujandose
     encima del I-beam.
  4. Con `prefers-reduced-motion: reduce` no hay lienzo en el DOM.
  5. En movil (390x844) el modulo NO se descarga. Se comprueba por red, no
     por inspeccion visual: un modulo cargado y luego oculto sigue costando.
  6. `destroy()` deja el DOM sin lienzo y sin la clase `.hypr-cursor-ready`.

Selectores de la asercion 2, verificados contra la pagina real servida (no
adivinados): el brief traia ".obra-titular, [data-cartel] button, button" a
ciegas y ninguno de los tres es lo bastante concreto.
  - Pulsable dentro de una escena: ".hero-mail" — el enlace mailto del hero
    (`data-scene="hero"`), es un <a href> real, unico en la pagina (count=1)
    y visible sin hacer scroll.
  - Parrafo de texto corrido dentro de una escena: ".hero-kick" — el kicker
    del hero ("Desarrollador Full Stack"), es un <p> real dentro de la misma
    escena. La clase se repite en otras escenas (contacto la reutiliza), por
    eso `apuntar()` usa `.first`.
  - Para la asercion 3 (estado tras desplazar) se necesita un pulsable que
    aparezca varias veces, uno por tarjeta de obra, para que el scroll
    tenga sentido: ".obra-abrir". Se descarto el bare "button" del brief:
    el primer <button> del DOM es ".obra-otra" y esta con `display: none`
    en reposo (solo aparece al abrir el visor), y Playwright agota el
    timeout de `scroll_into_view_if_needed` esperando a que un elemento
    invisible se vuelva estable. Medido: 30s de timeout exacto.

Patron de nombre de chunk verificado en la asercion 5: tras `npm run build`
los modulos diferidos de este repo salen como `<nombreDelImport>-<hash>.js`
(medido: `viceCursor-Dw5UovF7.js`, `obraCartel-DlQRTBvw.js`,
`hyprIgnition-Z8RwRkMh.js`). El modulo de esta tarea aun no existe, pero su
import sera `./components/hyprCursor`, asi que Vite generara
`hyprCursor-<hash>.js` y la subcadena "hyprCursor" es correcta para cazarlo
por red en cuanto exista.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

VIEWPORT_ESCRITORIO = {"width": 1440, "height": 900}
VIEWPORT_MOVIL = {"width": 390, "height": 844}
LIENZO = "canvas.hypr-cursor-canvas"
PULSABLE = ".hero-mail"
PARRAFO = ".hero-kick"
PULSABLE_SCROLL = ".obra-abrir"


def abrir(p, base, tema="hyprland", viewport=None, reduced=False):
    navegador = p.chromium.launch(
        headless=True, args=["--no-sandbox", "--use-gl=swiftshader"]
    )
    contexto = navegador.new_context(
        viewport=viewport or VIEWPORT_ESCRITORIO,
        reduced_motion="reduce" if reduced else "no-preference",
    )
    pg = contexto.new_page()
    pg.goto(f"{base}/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(4000)
    return navegador, pg


def hay_lienzo(pg) -> bool:
    return pg.evaluate(f"() => document.querySelector('{LIENZO}') !== null")


def potencia(pg) -> float:
    """Potencia del charco publicada por el modulo. 0 = apagado."""
    return pg.evaluate("() => window.__hyprCursor__ ? window.__hyprCursor__.pot() : -1")


def apuntar(pg, selector):
    pg.locator(selector).first.scroll_into_view_if_needed()
    pg.wait_for_timeout(600)
    caja = pg.locator(selector).first.bounding_box()
    pg.mouse.move(caja["x"] + caja["width"] * 0.4, caja["y"] + caja["height"] / 2, steps=8)
    pg.wait_for_timeout(500)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()
    fallos = []

    with sync_playwright() as p:
        # 1. presencia por tema
        for tema, espera in (("hyprland", True), ("vice", False), ("caelestia", False)):
            nav, pg = abrir(p, args.base, tema)
            if hay_lienzo(pg) is not espera:
                fallos.append(f"lienzo en {tema}: {hay_lienzo(pg)}, esperado {espera}")
            nav.close()

        nav, pg = abrir(p, args.base, "hyprland")

        # 2. reparto de senal
        apuntar(pg, PULSABLE)
        if potencia(pg) < 0.8:
            fallos.append(f"charco apagado sobre pulsable: pot={potencia(pg)}")
        apuntar(pg, PARRAFO)
        if potencia(pg) > 0.05:
            fallos.append(f"charco encendido sobre texto: pot={potencia(pg)}")

        # 3. estado rancio tras desplazar sin mover el raton
        apuntar(pg, PULSABLE_SCROLL)
        pg.evaluate("window.scrollBy(0, 900)")
        pg.wait_for_timeout(900)
        pg.mouse.move(720, 450, steps=2)
        pg.wait_for_timeout(400)
        bajo = pg.evaluate(
            "() => { const e = document.elementFromPoint(720, 450);"
            " return e ? (e.closest('button, a[href]:not([target=\"_blank\"])') ? 'pulsable' : 'otro') : 'nada'; }"
        )
        pot = potencia(pg)
        if bajo != "pulsable" and pot > 0.05:
            fallos.append(f"charco rancio tras desplazar: bajo={bajo} pot={pot}")
        nav.close()

        # 4. movimiento reducido
        nav, pg = abrir(p, args.base, "hyprland", reduced=True)
        if hay_lienzo(pg):
            fallos.append("hay lienzo con prefers-reduced-motion: reduce")
        nav.close()

        # 5. movil: el modulo no se descarga
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        contexto = navegador.new_context(
            viewport=VIEWPORT_MOVIL, has_touch=True, is_mobile=True
        )
        pedidos = []
        pg = contexto.new_page()
        pg.on("request", lambda r: pedidos.append(r.url))
        pg.goto(f"{args.base}/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(4000)
        if any("hyprCursor" in u for u in pedidos):
            fallos.append("el modulo del cursor se descarga en movil")
        navegador.close()

        # 6. limpieza
        nav, pg = abrir(p, args.base, "hyprland")
        pg.evaluate("() => window.__hyprCursor__ && window.__hyprCursor__.destroy()")
        pg.wait_for_timeout(300)
        if hay_lienzo(pg):
            fallos.append("destroy() deja el lienzo en el DOM")
        if pg.evaluate("() => document.documentElement.classList.contains('hypr-cursor-ready')"):
            fallos.append("destroy() deja la clase hypr-cursor-ready")
        nav.close()

    for f in fallos:
        print(f"FALLO: {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
