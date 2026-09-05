"""Arnes del cursor de Caelestia (la gota).

Cada familia de aserciones nacio de un fallo concreto y lo dice en su
docstring. Ninguna se acepta sin haberla visto dar rojo contra ese fallo.

Se corre SIEMPRE contra el build de produccion servido (`npm run build &&
npx vite preview --port 4173`), nunca contra `npm run dev`: el HMR corrompe
las medidas.

TODO hover es hover REAL (`page.hover` / `page.mouse.move`). Un `MouseEvent`
sintetico no dispara `:hover`, y todo lo que hace este dispositivo ocurre en
hover -- es la trampa que ya costo la fase B2.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

FALLOS: list[str] = []

# Los mismos tres selectores que el modulo. Si divergen, el arnes deja de
# medir el modulo y pasa a medir una copia suya.
PRESSABLE = 'button, a[href]:not([target="_blank"])'
NATIVE_ZONE = '.gallery-track, a[target="_blank"], p, li, dd, dt, figcaption, blockquote'
HOVER_SELECT = "button[aria-pressed]"

# Indice de cada escena en la barra de workspaces.
ESCENAS = {"hero": 0, "quien-es": 1, "obra": 2, "creditos": 3, "contacto": 4}


def check(ok: bool, etiqueta: str) -> None:
    print(("  OK   " if ok else "  FAIL ") + etiqueta)
    if not ok:
        FALLOS.append(etiqueta)


def abre(pagina, base: str, escena: str = "creditos") -> None:
    """Abre Caelestia y cambia al workspace pedido pulsando su pastilla.

    Se cambia pulsando, no tocando el hash: el hash lo cambia el shell, y
    forzarlo desde fuera deja el carril a medio camino (lecccion de B4).
    """
    pagina.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=45000)
    pagina.wait_for_timeout(6000)
    if escena != "hero":
        pagina.eval_on_selector_all(".cae-ws", "(bs, i) => bs[i].click()", ESCENAS[escena])
        pagina.wait_for_timeout(1500)


def estado(pagina) -> str:
    return pagina.evaluate("() => window.__caeCursor__ ? window.__caeCursor__.estado() : 'sin-modulo'")


def gate_presencia(navegador, base: str) -> None:
    """Gate 1 -- presencia por tema y las TRES puertas de montaje.

    Falla si el modulo monta donde no debe, y -- lo que de verdad importa --
    si en tactil o con movimiento reducido se DESCARGA el chunk. La puerta
    tiene que estar antes del `import()`, no dentro del modulo: en tactil el
    coste correcto es cero, no "cero animacion". Por eso se vigila la
    peticion de red, no el DOM.
    """
    print("[1] presencia por tema y puertas de montaje")

    for tema, debe in (("caelestia", True), ("vice", False), ("hyprland", False)):
        contexto = navegador.new_context(viewport={"width": 1440, "height": 900})
        pagina = contexto.new_page()
        pagina.goto(f"{base}/?theme={tema}", wait_until="domcontentloaded", timeout=45000)
        pagina.wait_for_timeout(6000)
        hay = pagina.evaluate("() => !!document.querySelector('.cae-cursor')")
        listo = pagina.evaluate(
            "() => document.documentElement.classList.contains('caelestia-cursor-ready')"
        )
        check(hay is debe, f"[1] {tema}: la gota {'monta' if debe else 'NO monta'}")
        check(listo is debe, f"[1] {tema}: la clase ready {'esta' if debe else 'NO esta'}")
        if debe:
            # Nada de esto puede llegar al arbol de accesibilidad: son tres
            # elementos decorativos que siguen al raton.
            ocultos = pagina.evaluate(
                """() => [...document.querySelectorAll('.cae-cursor, .cae-cursor-mancha')]
                     .every(e => e.getAttribute('aria-hidden') === 'true')"""
            )
            check(ocultos, "[1] los elementos del cursor van con aria-hidden")
        contexto.close()

    # Tactil y movimiento reducido: el chunk NO se pide.
    for etiqueta, kwargs in (
        ("movimiento reducido", {"reduced_motion": "reduce", "viewport": {"width": 1440, "height": 900}}),
        ("tactil", {"has_touch": True, "is_mobile": True, "viewport": {"width": 390, "height": 844}}),
    ):
        contexto = navegador.new_context(**kwargs)
        pagina = contexto.new_page()
        pedidos: list[str] = []
        pagina.on("request", lambda r: pedidos.append(r.url))
        pagina.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=45000)
        pagina.wait_for_timeout(6000)
        chunk = [u for u in pedidos if "caelestiaCursor" in u]
        check(not chunk, f"[1] {etiqueta}: el chunk del cursor no se descarga ({len(chunk)})")
        check(
            not pagina.evaluate("() => !!document.querySelector('.cae-cursor')"),
            f"[1] {etiqueta}: la gota no monta",
        )
        contexto.close()


def gate_senales(p_pagina, base: str) -> None:
    """Gate 2 -- el reparto de senales.

    Sustituir el puntero es legitimo; borrar las otras senales no. Y la
    trampa propia de esta pagina: `figcaption` esta en NATIVE_ZONE y vive
    DENTRO de los botones de Obra y de Creditos. Con la resolucion ingenua
    (`closest()` a secas, gana el mas cercano) la gota se apaga sobre la
    leyenda de cada tarjeta y sobre el nombre de cada pieza -- justo encima
    de las dianas.

    NO se afirma nada sobre `.gallery-track`: existe en el DOM pero es
    invisible en Caelestia (lo oculta B3), asi que una asercion suya seria
    tautologica. Su linea en el CSS es preventiva y esta declarada como tal
    en el spec.
    """
    print("[2] reparto de senales")
    pagina = p_pagina

    # Texto corrido: I-beam del sistema y gota apagada.
    abre(pagina, base, "contacto")
    pagina.hover("p.contacto-lead")
    pagina.wait_for_timeout(300)
    check(estado(pagina) == "apagada", "[2] sobre texto corrido la gota se apaga")
    check(
        pagina.eval_on_selector("p.contacto-lead", "el => getComputedStyle(el).cursor") == "text",
        "[2] sobre texto corrido manda el I-beam del sistema",
    )

    # Enlace externo: pointer nativo.
    check(
        pagina.eval_on_selector(
            '.contacto-bar[target="_blank"]', "el => getComputedStyle(el).cursor"
        )
        == "pointer",
        "[2] el enlace externo conserva el pointer nativo",
    )

    # La leyenda de una tarjeta de Obra: DENTRO de un pulsable, manda el pulsable.
    abre(pagina, base, "obra")
    pagina.hover(".cae-obra-card .cae-obra-caption")
    pagina.wait_for_timeout(300)
    check(estado(pagina) == "perla", "[2] sobre la leyenda de una tarjeta la gota sigue encendida")
    check(
        pagina.eval_on_selector(
            ".cae-obra-card .cae-obra-caption", "el => getComputedStyle(el).cursor"
        )
        == "none",
        "[2] la leyenda de una tarjeta no recupera el I-beam",
    )

    # El nombre de una pieza de Creditos: igual, y ademas es familia de roce.
    abre(pagina, base, "creditos")
    pagina.hover(".cae-cred-pieza .cae-cred-nom")
    pagina.wait_for_timeout(400)
    check(estado(pagina) == "derrame", "[2] sobre el nombre de una pieza la gota sigue derramada")


def gate_sin_inercia(pagina, base: str) -> None:
    """Gate 4 -- la posicion NO se suaviza.

    Un cursor con inercia miente sobre donde esta el raton, y en Creditos hay
    23 dianas contiguas donde eso se lee como retraso. La asercion es delta
    CERO tras UN fotograma, no "menor que": un umbral flojo deja pasar
    exactamente el `lerp` que viene a prohibir.
    """
    print("[4] sin inercia en la posicion")
    abre(pagina, base, "creditos")
    pagina.mouse.move(400, 400)
    pagina.wait_for_timeout(300)
    pagina.mouse.move(900, 500)
    medida = pagina.evaluate(
        """() => new Promise(res => requestAnimationFrame(() => {
             const m = new DOMMatrixReadOnly(getComputedStyle(document.querySelector('.cae-cursor')).transform);
             res([m.e, m.f]);
           }))"""
    )
    check(
        abs(medida[0] - 900) < 0.5 and abs(medida[1] - 500) < 0.5,
        f"[4] la gota esta exactamente donde el raton tras un fotograma {medida}",
    )


def gate_dos_momentos(pagina, base: str) -> None:
    """Gate 3 -- los dos momentos del mismo gesto.

    Es la tesis del dispositivo: la diana que YA elige al rozarla se moja al
    entrar, la de clic espera al clic. Si las dos se comportan igual, el
    cursor tiene un solo estado y el spec entero sobra.

    `mancha()` devuelve el avance PINTADO, no el objetivo escrito: sin eso la
    asercion mediria la intencion del modulo contra si misma.
    """
    print("[3] los dos momentos")

    # Familia de roce: se moja SIN ningun clic.
    abre(pagina, base, "creditos")
    pagina.locator(".cae-cred-pieza").nth(2).hover()
    pagina.wait_for_timeout(700)
    check(estado(pagina) == "derrame", "[3] la pieza de Creditos se moja al ENTRAR, sin clic")
    avance = pagina.evaluate("() => window.__caeCursor__.mancha()")
    check(avance > 0.9, f"[3] el derrame llega a llenar la pieza ({avance:.2f})")
    check(
        pagina.evaluate("() => window.__caeCursor__.diana()?.className || ''").startswith(
            "cae-cred-pieza"
        ),
        "[3] la diana mojada es la pieza",
    )

    # Familia de clic: perla al entrar, derrame solo al pulsar.
    abre(pagina, base, "obra")
    pagina.locator(".cae-obra-card").nth(0).hover(position={"x": 200, "y": 70})
    pagina.wait_for_timeout(700)
    check(estado(pagina) == "perla", "[3] la tarjeta de Obra NO se moja al entrar")
    check(
        pagina.evaluate("() => window.__caeCursor__.mancha()") == 0,
        "[3] sin clic la tarjeta esta seca",
    )
    pagina.mouse.down()
    pagina.wait_for_timeout(700)
    check(estado(pagina) == "derrame", "[3] la tarjeta se moja al PULSAR")
    avance = pagina.evaluate("() => window.__caeCursor__.mancha()")
    check(avance > 0.9, f"[3] el derrame llega a llenar la tarjeta ({avance:.2f})")
    pagina.mouse.up()
    pagina.wait_for_timeout(500)
    check(estado(pagina) == "perla", "[3] al soltar, la tarjeta se seca y vuelve la perla")


ARGS = ["--no-sandbox", "--use-gl=swiftshader"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=ARGS)
        contexto = navegador.new_context(viewport={"width": 1440, "height": 900})
        pagina = contexto.new_page()
        errores: list[str] = []
        pagina.on("pageerror", lambda e: errores.append(f"pageerror: {e}"))
        pagina.on(
            "console",
            lambda m: errores.append(f"console.error: {m.text}") if m.type == "error" else None,
        )

        gate_presencia(navegador, args.base)
        gate_senales(pagina, args.base)
        gate_sin_inercia(pagina, args.base)
        gate_dos_momentos(pagina, args.base)

        print("[8] consola")
        check(not errores, f"[8] cero errores de consola ({errores[:3]})")

        navegador.close()

    print()
    if FALLOS:
        print(f"FALLOS ({len(FALLOS)}):")
        for f in FALLOS:
            print("  - " + f)
        return 1
    print("Todo verde.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
