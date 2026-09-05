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
import io
import math
import sys

from PIL import Image
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
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


def esperar_derrame_lleno(pagina, etiqueta: str) -> None:
    """Espera a que `mancha()` SIENTE en vez de esperar un tiempo fijo: un
    `wait_for_timeout` fijo contra una transicion de 420ms mide la carga de
    la maquina, no el derrame. Si el timeout salta, se reporta como FAIL con
    el ultimo valor leido -- no como excepcion, para no matar el resto de
    gates."""
    try:
        pagina.wait_for_function("() => window.__caeCursor__.mancha() >= 0.99", timeout=2000)
    except PlaywrightTimeoutError:
        pass
    avance = pagina.evaluate("() => window.__caeCursor__.mancha()")
    check(avance >= 0.99, f"[3] el derrame llega a llenar {etiqueta} ({avance:.2f})")


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
    esperar_derrame_lleno(pagina, "la pieza")
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
    esperar_derrame_lleno(pagina, "la tarjeta")
    pagina.mouse.up()
    pagina.wait_for_timeout(500)
    check(estado(pagina) == "perla", "[3] al soltar, la tarjeta se seca y vuelve la perla")

    # El cerco: solo en el clic real, y se limpia solo.
    check(
        pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length") >= 1,
        "[3] el clic deja cerco",
    )
    pagina.wait_for_timeout(1400)
    check(
        pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length") == 0,
        "[3] el cerco se limpia solo antes de 1,4 s",
    )

    # El roce NO deja cerco: la gota deja huella donde actua, no por donde pasa.
    abre(pagina, base, "creditos")
    pagina.locator(".cae-cred-pieza").nth(1).hover()
    pagina.wait_for_timeout(400)
    pagina.locator(".cae-cred-pieza").nth(4).hover()
    pagina.wait_for_timeout(400)
    check(
        pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length") == 0,
        "[3] barrer piezas al roce no deja ningun cerco",
    )

    # El respaldo del cerco: si el movimiento reducido se activa DESPUES de
    # montar (la emulacion de devtools a mitad de sesion, no el arranque en
    # frio que ya cubre gate_presencia), la guardia CSS deja el anillo en
    # `display: none` para siempre. Un elemento que nunca se pinta nunca
    # dispara `animationend` -- ni `animationcancel`, la animacion no llega a
    # arrancar -- asi que sin un respaldo por temporizador el anillo se
    # quedaria colgado el resto de la sesion y cada clic siguiente anadiria
    # otro. `emulate_media` reproduce justo ese cambio tardio: el modulo ya
    # esta montado, asi que este es el unico camino que de verdad lo ejercita.
    abre(pagina, base, "obra")
    pagina.emulate_media(reduced_motion="reduce")
    pagina.locator(".cae-obra-card").nth(0).hover(position={"x": 200, "y": 70})
    pagina.wait_for_timeout(200)
    pagina.mouse.down()
    pagina.wait_for_timeout(120)
    pagina.mouse.up()
    check(
        pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length") >= 1,
        "[3] el cerco se crea aunque el anillo no vaya a pintarse (movimiento reducido tardio)",
    )
    # El anillo nunca dispara `animationend` bajo `display: none`: lo unico
    # que lo retira es el temporizador de respaldo (1200ms en el modulo). Se
    # espera con `wait_for_function` y margen explicito (2500ms, muy por
    # encima de los 1200ms del respaldo) en vez de un `wait_for_timeout` fijo
    # calcado a ese valor, que mediria el reloj del harness contra si mismo.
    try:
        pagina.wait_for_function(
            "() => document.querySelectorAll('.cae-cursor-cerco').length === 0",
            timeout=2500,
        )
    except PlaywrightTimeoutError:
        pass
    restantes = pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length")
    check(
        restantes == 0,
        f"[3] el respaldo retira el cerco aunque 'animationend' nunca llegue ({restantes} restantes)",
    )
    pagina.emulate_media(reduced_motion="no-preference")


def gate_rancio(pagina, base: str) -> None:
    """Gate 5 -- la diana que se va con el raton quieto.

    Al cambiar de workspace, el carril se lleva la diana y deja otra escena
    debajo del puntero. La premisa escrita en el propio modulo es que eso NO
    emite ningun evento de puntero, y que por eso hace falta `marcarRancio()`
    escuchando `caelestia:workspace`. El raton NO se mueve en toda la prueba
    (el workspace se cambia por TECLADO): si se moviera, `pointerover` lo
    arreglaria solo y ninguna de las dos familias de abajo mediria nada.

    HALLAZGO MEDIDO (no supuesto): esa premisa es FALSA en Chromium para este
    caso concreto. `aislarInactivos()` pone `inert = true` en la escena
    saliente en el mismo tick del clic, y Chromium recalcula el hit-test bajo
    el puntero AUNQUE este no se mueva un pixel: dispara `pointerout`/
    `pointerleave` nativos y REALES sobre la pieza mojada, medidos a ~50ms del
    `Enter` -- muy antes de que el carril termine sus 520ms de transicion.
    Esos eventos llegan al `alEntrar`/`pointerover` normal del modulo (sin
    pasar nunca por `marcarRancio` ni por `stale`) y curan el estado solos.
    En este motor, la via nativa gana la carrera y la escucha de
    `caelestia:workspace` del modulo es defensa en profundidad, no la unica
    via -- ver el comentario junto a esa escucha en `caelestiaCursor.ts`
    sobre por que se queda de todos modos.

    Eso deja el gate con DOS caminos que probar, y ninguno sobra:

    - Family A (abajo, "mecanismo propio"): con los eventos de puntero
      relacionados con hover BLOQUEADOS en fase de CAPTURA sobre `window`
      (`stopImmediatePropagation()`, el primer paso del recorrido del
      evento -- para ahi y no llega a NINGUN listener mas abajo, nativo o
      del modulo). Aisla `marcarRancio -> stale -> tick() ->
      elementFromPoint` de la curacion nativa, y es la unica manera de que
      el sabotaje (retirar esa escucha) de verdad rojo: sin este bloqueo, el
      `pointerout` nativo cura el estado incluso con la escucha
      completamente ausente del bundle, y el gate pasa siempre -- medido:
      esa fue la version que escribi primero y no fallaba con el sabotaje.
      Es el mismo defecto que las nueve aserciones tautologicas ya cazadas
      en este proyecto (`Aserciones que no pueden fallar`).
    - Family B (nueva en esta ronda, "camino del visitante"): la MISMA
      escena, sin bloquear nada -- las condiciones reales, donde Chromium
      cura el estado por su cuenta. Sin esta familia el gate solo prueba
      "si el navegador no curara, el modulo curaria", que es una propiedad
      real del modulo pero NUNCA es lo que un visitante de Chromium
      experimenta. Es la leccion de B4 con los papeles cambiados: "un gate
      que solo mide la rama degradada no vigila el camino que ve el
      visitante" -- aqui la rama que faltaba no era la degradada, era la
      real.

    Las dos familias afirman el mismo estado final (diana suelta, mancha
    seca, fuera de "derrame"); lo que cambia es SI se bloquea la curacion
    nativa, y las etiquetas de cada `check` lo dicen para que nadie las
    confunda leyendo el log.
    """
    print("[5] estado rancio tras cambiar de workspace")

    # ---- Family A: mecanismo propio, con la sanacion nativa suprimida ----
    abre(pagina, base, "creditos")
    pagina.hover(".cae-cred-pieza:nth-child(3)")
    pagina.wait_for_timeout(700)
    check(
        estado(pagina) == "derrame",
        "[5-A] partida (mecanismo propio, sin sanacion nativa): la pieza esta mojada",
    )

    pagina.evaluate(
        """() => {
             window.__caeGateBloqueo = (e) => { e.stopImmediatePropagation(); };
             for (const t of ['pointerover','pointerout','pointerleave','pointerenter','pointermove']) {
               window.addEventListener(t, window.__caeGateBloqueo, true);
             }
           }"""
    )

    # Cambio de workspace SIN mover el raton: se pulsa la pastilla con el
    # teclado, desde el foco.
    pagina.evaluate("() => document.querySelectorAll('.cae-ws')[4].focus()")
    pagina.keyboard.press("Enter")
    pagina.wait_for_timeout(1500)

    check(
        pagina.evaluate("() => window.__caeCursor__.diana() === null"),
        "[5-A] mecanismo propio, sin sanacion nativa: la diana mojada se suelta",
    )
    check(
        estado(pagina) != "derrame",
        f"[5-A] mecanismo propio, sin sanacion nativa: la gota deja de estar derramada ({estado(pagina)})",
    )
    check(
        pagina.evaluate("() => window.__caeCursor__.mancha()") == 0,
        "[5-A] mecanismo propio, sin sanacion nativa: la mancha queda seca",
    )

    pagina.evaluate(
        """() => {
             for (const t of ['pointerover','pointerout','pointerleave','pointerenter','pointermove']) {
               window.removeEventListener(t, window.__caeGateBloqueo, true);
             }
             delete window.__caeGateBloqueo;
           }"""
    )

    # ---- Family B: camino del visitante, nada bloqueado ----
    # Misma escena desde cero: el cambio de workspace de la Family A ya dejo
    # la pagina en "contacto", asi que se vuelve a mojar la pieza de
    # Creditos antes de repetir el cambio, esta vez sin ningun bloqueo.
    abre(pagina, base, "creditos")
    pagina.hover(".cae-cred-pieza:nth-child(3)")
    pagina.wait_for_timeout(700)
    check(
        estado(pagina) == "derrame",
        "[5-B] partida (camino del visitante, nada bloqueado): la pieza esta mojada",
    )

    pagina.evaluate("() => document.querySelectorAll('.cae-ws')[4].focus()")
    pagina.keyboard.press("Enter")
    pagina.wait_for_timeout(1500)

    check(
        pagina.evaluate("() => window.__caeCursor__.diana() === null"),
        "[5-B] camino del visitante, nada bloqueado: la diana mojada se suelta",
    )
    check(
        estado(pagina) != "derrame",
        f"[5-B] camino del visitante, nada bloqueado: la gota deja de estar derramada ({estado(pagina)})",
    )
    check(
        pagina.evaluate("() => window.__caeCursor__.mancha()") == 0,
        "[5-B] camino del visitante, nada bloqueado: la mancha queda seca",
    )


def _lum(px: tuple[int, int, int]) -> float:
    f = []
    for v in px:
        v /= 255
        f.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]


def _ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = _lum(a) + 0.05, _lum(b) + 0.05
    return max(la, lb) / min(la, lb)


def _contraste_glifo(pagina, selector: str) -> float:
    """Contraste real del texto de `selector` contra su fondo, PIXEL A PIXEL.

    Dos capturas del mismo recorte: una normal y otra con la tinta apagada
    (`color: transparent`). Los pixeles que cambian entre las dos son los
    glifos; el mismo pixel en la segunda captura es su fondo exacto.

    Por que asi y no con `getComputedStyle`: el derrame va ENCIMA con
    `mix-blend-mode`, asi que ni el texto ni el fondo se pintan del color que
    declaran. Un numero sacado de los estilos seria de otra pagina.

    Por que el percentil 90 y no el minimo: el antialias deja un halo de
    pixeles a medio camino entre tinta y fondo, y su contraste es siempre
    peor que el del trazo. El minimo mediria el borde de la letra; el
    percentil 90 mide el NUCLEO SOLIDO, que es lo que se lee.
    """
    caja = pagina.locator(selector).first.bounding_box()
    recorte = {k: caja[k] for k in ("x", "y", "width", "height")}

    con = Image.open(io.BytesIO(pagina.screenshot(clip=recorte))).convert("RGB")
    previo = pagina.eval_on_selector(
        selector,
        "el => { const p = el.style.color;"
        " el.style.setProperty('color', 'transparent', 'important');"
        " el.querySelectorAll('*').forEach(d => d.style.setProperty('color','transparent','important'));"
        " return p; }",
    )
    sin = Image.open(io.BytesIO(pagina.screenshot(clip=recorte))).convert("RGB")
    pagina.eval_on_selector(
        selector,
        "(el, prev) => { if (prev) el.style.color = prev; else el.style.removeProperty('color');"
        " el.querySelectorAll('*').forEach(d => d.style.removeProperty('color')); }",
        previo,
    )

    pares = [
        (a, b)
        for a, b in zip(con.getdata(), sin.getdata())
        if math.dist(a, b) > 12  # pixel con tinta encima
    ]
    if not pares:
        return 0.0  # no hay glifo que medir: lo trata el llamador
    ratios = sorted(_ratio(a, b) for a, b in pares)
    return ratios[int(len(ratios) * 0.9)]


def _delta_medio(pagina, selector: str) -> float:
    """Diferencia media de canal entre la diana CON derrame y SIN el.

    Es la mitad que falta del gate: un derrame que no baje de AA porque no
    se ve no es un derrame. El arnes apaga la mancha con `display: none`,
    y puede hacerlo porque el modulo nunca escribe esa propiedad (contrato
    de la cabecera del modulo).

    La diana esta sobre un panel OPACO (la ventana o la propia tarjeta), asi
    que el shader del fondo no entra en el recorte y las dos capturas son
    comparables. Contra el fondo generativo no lo serian: se mueve solo.
    """
    caja = pagina.locator(selector).first.bounding_box()
    recorte = {k: caja[k] for k in ("x", "y", "width", "height")}
    con = Image.open(io.BytesIO(pagina.screenshot(clip=recorte))).convert("RGB")
    pagina.eval_on_selector(".cae-cursor-mancha", "el => { el.style.display = 'none'; }")
    sin = Image.open(io.BytesIO(pagina.screenshot(clip=recorte))).convert("RGB")
    pagina.eval_on_selector(".cae-cursor-mancha", "el => { el.style.removeProperty('display'); }")
    total = sum(
        abs(a[i] - b[i]) for a, b in zip(con.getdata(), sin.getdata()) for i in range(3)
    )
    return total / (con.size[0] * con.size[1] * 3)


# AA para texto normal. La leyenda de la tarjeta es Fraunces 14px y el texto
# de la pastilla 12px: ninguno llega a "texto grande", asi que el umbral es
# 4.5 y no 3.
AA = 4.5
# Medido el 2026-09-05 (barrido en dos mitades, --mitad 1 y --mitad 2,
# build de produccion en :4173): el peor delta medio de las 4 medidas de
# perceptibilidad (obra/creditos x 09:00/03:00) fue 13.25 en "obra 09:00".
# UMBRAL_NOTA es la MITAD de ese valor -- margen explicito frente al ruido
# del compositor, no un umbral pegado a la medida. No lo bajes despues para
# que pase: si el derrame no se nota, el derrame esta mal.
UMBRAL_NOTA = 6.625
# Cada 30 minutos: 48 posiciones del reloj. El matiz avanza 0,25 grados por
# minuto y la marea de croma es continua, asi que 30 min no se salta ningun
# extremo -- y el cruce de esquema (07:00 y 20:00) cae dentro del barrido.
PASO_MINUTOS = 30


def gate_contraste(pagina, base: str, mitad: int | None = None) -> None:
    """Gate 6 -- el contraste bajo el derrame, en las 24 horas.

    Lo que NO es invariante por construccion: la perla y la mancha mezclan
    (`multiply` de dia, `screen` de noche) con lo que hay debajo, y el
    pigmento pierde dos tercios de croma cuando la marea pasa por el naranja
    y el magenta. La invariancia del motor de color vale para los ROLES, no
    para una mezcla encima. Un cursor calibrado a una sola hora no esta
    calibrado.

    Antes de creerse un solo numero: la consola en verde. Toda la
    calibracion del cursor de Hyprland se midio contra una pagina cuya
    coreografia estaba rota, y ninguna asercion pudo detectarlo porque todas
    comparaban la pagina consigo misma.

    `mitad` (1, 2 o `None`): un barrido completo son 96 medidas -- 48
    posiciones del reloj x 2 dianas -- con DOS capturas cada una, y eso no
    cabe en una sola llamada de Bash en primer plano (limite practico de
    ~10 min). `--mitad 1` cubre 00:00-11:30, `--mitad 2` cubre 12:00-23:30;
    sin la bandera (`None`, el default) se barren las 24 horas enteras, que
    es como debe correr el gate para cualquiera que lo lance normalmente.
    La perceptibilidad (540 y 180 minutos, dentro de la primera mitad) se
    mide siempre que la mitad activa la cubra, para que las dos mitades
    combinadas sigan viendo las mismas horas que el barrido completo.
    """
    print(f"[6] contraste bajo el derrame, barrido de 24 horas (mitad={mitad or 'completa'})")

    if mitad == 1:
        rango_horas = range(0, 720, PASO_MINUTOS)
    elif mitad == 2:
        rango_horas = range(720, 1440, PASO_MINUTOS)
    else:
        rango_horas = range(0, 1440, PASO_MINUTOS)
    horas_perceptibilidad = [m for m in (540, 180) if m in rango_horas or mitad is None]

    peor_contraste = (99.0, "")
    peor_delta = (999.0, "")

    for escena, diana, texto, accion in (
        ("obra", ".cae-obra-card", ".cae-obra-caption", "clic"),
        ("creditos", ".cae-cred-pieza:nth-child(3)", ".cae-cred-pieza:nth-child(3) .cae-cred-nom", "roce"),
    ):
        abre(pagina, base, escena)
        pagina.hover(diana, position={"x": 40, "y": 30})
        if accion == "clic":
            pagina.mouse.down()
        pagina.wait_for_timeout(700)

        for minutos in rango_horas:
            pagina.evaluate(f"() => window.__CAE_SET_MINUTOS__({minutos})")
            pagina.wait_for_timeout(120)
            ratio = _contraste_glifo(pagina, texto)
            etiqueta = f"{escena} {minutos // 60:02d}:{minutos % 60:02d}"
            if 0 < ratio < peor_contraste[0]:
                peor_contraste = (ratio, etiqueta)
            if ratio == 0.0:
                check(False, f"[6] {etiqueta}: no se encontro ni un pixel de glifo que medir")

        # La perceptibilidad se mide en dos horas, no en las 48: es una
        # propiedad del derrame, no del reloj.
        for minutos in horas_perceptibilidad:
            pagina.evaluate(f"() => window.__CAE_SET_MINUTOS__({minutos})")
            pagina.wait_for_timeout(200)
            delta = _delta_medio(pagina, diana)
            if delta < peor_delta[0]:
                peor_delta = (delta, f"{escena} {minutos // 60:02d}:00")

        if accion == "clic":
            pagina.mouse.up()

    check(
        peor_contraste[0] >= AA,
        f"[6] AA bajo el derrame en las 24 horas (peor {peor_contraste[0]:.2f}:1 en {peor_contraste[1]})",
    )
    # UMBRAL_NOTA se fija con la primera medida y se anota en el spec. No lo
    # bajes para que pase: si el derrame no se nota, el derrame esta mal.
    check(
        peor_delta[0] >= UMBRAL_NOTA,
        f"[6] el derrame se NOTA (peor delta medio {peor_delta[0]:.2f} en {peor_delta[1]})",
    )


ARGS = ["--no-sandbox", "--use-gl=swiftshader"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    ap.add_argument(
        "--mitad",
        type=int,
        choices=(1, 2),
        default=None,
        help=(
            "Gate 6 solo: barre media rueda del reloj (1: 00:00-11:30, "
            "2: 12:00-23:30) en vez de las 24 horas completas. Existe "
            "porque el barrido entero (96 medidas, dos capturas cada una) "
            "no cabe en una sola llamada de Bash en primer plano; sin la "
            "bandera el gate barre el dia completo, que es como debe "
            "correr para cualquiera que lo lance normalmente."
        ),
    )
    ap.add_argument(
        "--solo-gate6",
        action="store_true",
        help="Salta los gates 1-5, 7 y 8 -- solo corre el gate de contraste (util junto a --mitad).",
    )
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

        if not args.solo_gate6:
            gate_presencia(navegador, args.base)
            gate_senales(pagina, args.base)
            gate_sin_inercia(pagina, args.base)
            gate_dos_momentos(pagina, args.base)
            gate_rancio(pagina, args.base)
        gate_contraste(pagina, args.base, mitad=args.mitad)

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
