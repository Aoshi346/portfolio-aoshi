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

Asercion 7, contraste por glifo del charco (Task 5 del plan): mide, con el
charco encendido, el ratio WCAG del texto de la diana contra el peor fondo
real capturado detras de ella. Se hace sobre los dos tipos de diana que el
charco SI enciende (verificados arriba): ".hero-mail" (enlace con texto
propio) y ".obra-abrir" (boton transparente que cubre la fila del titular de
obra; su propio texto es vacio, el glifo visible es el <h2 data-title> que
tapa). ".hero-kick" queda fuera: es texto corrido, el charco nunca se
enciende ahi (asercion 2), asi que no hay riesgo de contraste que medir.

El borrador del brief traia dos supuestos que no se sostienen contra la
pagina real, verificados con `getComputedStyle` (no adivinados):

  1. Suponia que el texto de TODAS las dianas es `--text` (`#ffeae6`). Falso:
     `.hero-mail` en reposo pinta con `--haze` (`#b18c86`) y en `:hover` --
     que es el estado en el que el charco esta encendido, porque el charco
     solo se enciende con el mouse encima -- pasa a `--l1` (`#ff5a34`), un
     naranja saturado nada blanco. Y el titular tras `.obra-abrir` pinta
     `--haze` siempre (no cambia con el hover del boton que lo cubre; es la
     misma atenuacion de "titular en reposo" ya documentada para el cartel
     de obra en `2026-08-10-hyprland-obra-cartel`). Comparar el pixel mas
     claro del fondo contra un `#ffeae6` fijo mide un color que casi nunca
     esta en pantalla durante el propio riesgo que se quiere medir --
     mide otra cosa, con un numero que ademas sale mas favorable de lo real
     porque el blanco nominal es mas dificil de tragarse que el naranja o el
     `--haze` real. La correccion: leer `getComputedStyle(...).color` del
     nodo que de verdad lleva el glifo, EN EL MOMENTO del hover, y usarlo
     como color de texto de esa medida en concreto.
  2. Comparaba pixel a pixel por igualdad exacta contra el color nominal del
     texto para decidir que es "fondo". Falso incluso arreglado el punto 1:
     el antialias del renderer de fuentes produce una rampa continua entre
     el color del glifo y el fondo, asi que casi ningun pixel del borde de
     una letra es el color puro y la mayoria de los pixeles "!= texto" son
     en realidad tinta de texto diluida -- de hecho los MAS CLAROS de toda
     la caja, asi que arrastran el "peor fondo" hacia el propio glifo y dan
     un contraste falso, no el que hay detras. Medido con `.hero-mail`: un
     filtro por distancia euclidea a 60 (bastante generoso) todavia dejaba
     pasar pixeles de borde a distancia 66 del texto, con luminancia 0.60 --
     visualmente indistinguibles del glifo real. La correccion: en vez de
     separar el glifo del fondo por color, se APAGA el glifo (color
     transparente por CSS, sin tocar layout) mientras el charco sigue
     encendido y se fotografia el fondo desnudo -- cero pixeles de glifo que
     clasificar mal, porque no hay ningun pixel de glifo en la captura.
  3. Con el glifo ya apagado seguia saliendo un pixel puntual clarisimo --
     que no es fondo ni glifo, es LA MANO: el punto de `hyprCursor.ts`
     (`ctx.fillStyle = "#ffd9cc"`, radio `PUNTO_REPOSO` 3,2px + anillo de
     1px) que sigue al raton se dibuja SIEMPRE en la posicion del puntero, y
     `apuntar()` deja el puntero dentro de la propia caja para que el charco
     se encienda. Es un artefacto de donde decide pararse el arnes, no un
     fondo real que vaya a estar ahi para cualquier visitante.

     El primer intento la descarto por color (distancia euclidea a
     `#ffd9cc`), y volvio a caer en la MISMA trampa del punto 2: el borde
     antialiasado del punto -- un circulo relleno de 3,2px con anillo, no un
     bloque solido -- mezcla su color con el fondo igual que el borde de una
     letra, asi que un pixel a 3px del centro del puntero (medido:
     `rgb(238, 196, 181)`, a 35 de distancia de `#ffd9cc`, fuera de un
     filtro de color a 20) sigue siendo la mano diluida, no fondo. La
     correccion definitiva: excluir por GEOMETRIA, no por color -- cualquier
     pixel a menos de `MANO_RADIO_EXCLUSION` del punto exacto donde
     `apuntar()` puso el raton (el mismo punto que consume `hyprCursor.ts`
     para centrar el degradado) no puede ser fondo, sea cual sea su color.
  4. `bounding_box()` devuelve la caja de BORDE (incluye padding). El canto
     del charco (`ctx.strokeRect` en `hyprCursor.ts`) se dibuja justo en ese
     borde -- fuera del area de contenido, donde nunca hay tinta de ningun
     glifo. Medido en ".hero-mail" (padding 2px/1px): el trazo del canto,
     con el mismo color base que el texto en `:hover` (`--l1`), caia
     DENTRO de la caja de borde y se leia como "el peor fondo detras del
     texto" cuando en realidad nunca esta detras de ninguna letra.
     Correccion: se recorta la caja al area de CONTENIDO, restando el
     padding computado, antes de fotografiar.
  5. El shader `hyprEmber.ts` varia con el tiempo, no con el scroll -- y su
     brillo en un punto fijo de pantalla oscila con un periodo mas largo que
     una ventana corta de muestreo. Con 12 muestras de 280ms (~3,4s) el
     mismo punto exacto de la pagina, en la MISMA calibracion del charco,
     media entre 4,05:1 y 4,58:1 segun cuando arrancaba el arnes -- la
     ventana no alcanzaba a capturar el ciclo completo. `measure-cartel.py`
     ya se topo con el mismo shader y lo resolvio con una ventana de 16,8s
     (48 muestras); aqui se toma prestada la misma duracion de ventana
     (`MUESTRAS_POR_DIANA` x `INTERVALO_MUESTRA`, no el percentil -- aqui
     cada muestra ya es "el pixel mas claro DENTRO de la caja", asi que el
     MINIMO de esas lecturas a lo largo de la ventana es el peor caso, sin
     necesitar un percentil que además diluiria el minimo real) para que el
     numero no dependa de cuando se lanza el arnes.
"""
import argparse
import io
import re
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

VIEWPORT_ESCRITORIO = {"width": 1440, "height": 900}
VIEWPORT_MOVIL = {"width": 390, "height": 844}
LIENZO = "canvas.hypr-cursor-canvas"
PULSABLE = ".hero-mail"
PARRAFO = ".hero-kick"
PULSABLE_SCROLL = ".obra-abrir"

AA_MINIMO = 4.5
# Ventana de ~16,8s (igual que `measure-cartel.py`, ver punto 5 de la
# cabecera): a 280ms/muestra 12 muestras (~3,4s) no alcanzaban a cubrir el
# ciclo de brillo del shader y el numero variaba con cuando arrancaba el
# arnes.
MUESTRAS_POR_DIANA = 42
INTERVALO_MUESTRA_MS = 400
_RGB_RE = re.compile(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)")

# Radio de exclusion geometrica alrededor del punto donde `apuntar()` deja
# el raton (ver punto 3 de la cabecera): `PUNTO_REPOSO` (3,2px) + el anillo
# de 1px + margen de antialiasado. Cualquier pixel mas cerca que esto del
# puntero es la mano, nunca fondo.
MANO_RADIO_EXCLUSION = 8


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


def apuntar(pg, selector, punto: "tuple[float, float] | None" = None) -> tuple[float, float]:
    """Devuelve el punto (viewport) donde queda el puntero, para que quien
    mida contraste pueda excluirlo como "mano" en vez de fondo real.

    Sin `punto` explicito, usa el 40% del ancho de `selector` -- valido para
    dianas pequenas (".hero-mail") pero FALSO para ".obra-abrir": ese boton
    es `position: absolute; inset: 0` sobre la fila entera (1440px de ancho),
    asi que su 40% (x=576) cae fuera del radio del charco (260px) alrededor
    del titular real (x=114-447) -- medido: el charco quedaba practicamente
    apagado encima del titular, garantizando por construccion que "encendido"
    y "apagado" dieran el mismo numero. Por eso el llamador que mide
    ".obra-abrir" pasa el CENTRO del `<h2 data-title>` como `punto`: sigue
    dentro de la caja de ".obra-abrir" (la cubre entera) asi que el
    pointerenter/hover se dispara igual, pero el gradiente queda centrado en
    el titular real, no en un punto arbitrario de una caja diez veces mas
    ancha que el texto."""
    pg.locator(selector).first.scroll_into_view_if_needed()
    pg.wait_for_timeout(600)
    if punto is None:
        caja = pg.locator(selector).first.bounding_box()
        punto = (caja["x"] + caja["width"] * 0.4, caja["y"] + caja["height"] / 2)
    pg.mouse.move(*punto, steps=8)
    pg.wait_for_timeout(500)
    return punto


def _lin(v: float) -> float:
    v = v / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _lum(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _distancia(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def _contraste(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1, l2 = _lum(fg) + 0.05, _lum(bg) + 0.05
    return max(l1, l2) / min(l1, l2)


def _color_computado(handle) -> tuple[int, int, int]:
    rgb = handle.evaluate("(el) => getComputedStyle(el).color")
    m = _RGB_RE.match(rgb)
    assert m, f"no se pudo parsear el color computado: {rgb!r}"
    return tuple(round(float(v)) for v in m.groups())  # type: ignore[return-value]


def contraste_por_glifo(
    pg, selector_glifo: str, punto: tuple[float, float], selector_color: "str | None" = None
) -> tuple[float, tuple[int, int, int]]:
    """Ratio WCAG del texto de una diana contra su propio fondo iluminado.

    `selector_glifo` apunta al nodo que de verdad pinta el glifo visible
    (puede no ser el pulsable: en ".obra-abrir" el boton no tiene texto
    propio, lo que se ve es el <h2> que tapa) y se usa para la caja
    (bounding box + recorte de padding) y para APAGAR toda la tinta bajo el.
    Se llama con el charco YA encendido (el llamador tiene que haber
    apuntado antes al pulsable con `apuntar()`, y pasar aqui el punto
    (viewport) que esa llamada devolvio).

    `selector_color` (por defecto `selector_glifo`) es el nodo del que se
    lee el color REALMENTE visible en este estado -- pueden no coincidir:
    en ".obra-abrir" el `<h2>` no tiene color propio, son los DOS `<i>`
    apilados de `obraCartel.ts` los que lo tienen, y cual de los dos se ve
    depende del relevo (`i:first-child` en reposo, `i:last-child` con el
    hover puesto). Se lee `getComputedStyle(...).color` DEL NODO DE COLOR en
    el momento de la medida, no un hex fijo del spec -- `.hero-mail` cambia
    de `--haze` a `--l1` justo al entrar en `:hover`, que es cuando el
    charco esta encendido, asi que un color nominal fijo mediria un estado
    que no coincide con el riesgo real (ver cabecera del modulo).

    Fondo "peor caso": en vez de separar glifo de fondo por color de pixel
    (fragil por el antialias, ver cabecera), se APAGA el glifo por CSS
    (`color: transparent`, sin tocar layout ni bounding box) y se fotografia
    la caja desnuda -- cualquier pixel de la captura es fondo real (shader +
    charco), nunca tinta de letra. El shader es generativo y el charco tiene
    su propia rampa de opacidad (`POT_SMOOTHING` en `hyprCursor.ts`), asi que
    un solo fotograma no es el peor caso: se toman `MUESTRAS_POR_DIANA`
    capturas espaciadas `INTERVALO_MUESTRA_MS` (~16,8s por diana, ver punto 5
    de la cabecera del modulo) y de cada una se guarda el pixel de MENOR
    CONTRASTE contra el texto -- NO el de mayor luminancia. Con un texto
    claro (blanco/naranja) ambos criterios coinciden porque el contraste
    solo puede caer si el fondo sube hacia el; pero con `--haze` (luminancia
    ~0,30, ni claro ni oscuro) un fondo que se ACERCA a esa luminancia desde
    abajo empeora el contraste tanto o mas que uno que se aleja por arriba
    -- el shader de Hyprland baja hasta ~0,20 de luminancia en frames
    oscuros, mas cerca de 0,30 que muchos fondos "claros". Tomar el pixel
    mas claro se perdia ese caso. El numero que se devuelve es el MINIMO de
    esas `MUESTRAS_POR_DIANA` lecturas de contraste -- el peor de los
    peores, no el fotograma medio ni el primero.
    """
    nodo = pg.locator(selector_glifo).first
    handle = nodo.element_handle()
    color_handle = pg.locator(selector_color or selector_glifo).first.element_handle()
    texto_rgb = _color_computado(color_handle)
    caja_borde = nodo.bounding_box()
    # `bounding_box()` devuelve la caja de BORDE (incluye padding). El canto
    # del charco (`ctx.strokeRect`) se dibuja justo en ese borde -- fuera del
    # area de contenido, asi que ningun glifo pinta ahi. Medir con el
    # padding puesto encuentra ese trazo (mismo color base que el texto en
    # `:hover`, `--l1`) y lo cuenta como "el peor fondo detras del texto"
    # cuando en realidad nunca esta detras de ninguna letra. Se recorta al
    # area de CONTENIDO (donde si puede haber tinta) restando el padding
    # computado.
    pad = handle.evaluate(
        "(el) => { const cs = getComputedStyle(el);"
        " return [parseFloat(cs.paddingTop), parseFloat(cs.paddingRight),"
        " parseFloat(cs.paddingBottom), parseFloat(cs.paddingLeft)]; }"
    )
    pad_top, pad_right, pad_bottom, pad_left = pad
    caja = {
        "x": caja_borde["x"] + pad_left,
        "y": caja_borde["y"] + pad_top,
        "width": max(caja_borde["width"] - pad_left - pad_right, 1),
        "height": max(caja_borde["height"] - pad_top - pad_bottom, 1),
    }
    # Punto del raton en coordenadas LOCALES de esta caja de contenido (la
    # caja del glifo puede no ser la caja donde se apunto -- en
    # ".obra-abrir" son dos elementos distintos, ver cabecera).
    punto_local = (punto[0] - caja["x"], punto[1] - caja["y"])
    # El titular de obra en Hyprland es el relevo por letra del cartel
    # (`obraCartel.ts`): cada caracter son DOS <i> apilados con su PROPIO
    # color explicito (`.obra-rl i:first-child` en --haze, `i:last-child` en
    # --color-paper -- ver themes.css). Apagar solo el color heredado del
    # <h2> no les llega: tienen su propia regla, mas especifica que la
    # herencia. Se apaga el nodo Y todos sus descendientes.
    color_previo = handle.evaluate("(el) => el.style.color")
    handle.evaluate(
        "(el) => {"
        " el.style.setProperty('color', 'transparent', 'important');"
        " el.querySelectorAll('*').forEach((d) => d.style.setProperty('color', 'transparent', 'important'));"
        " }"
    )
    try:
        peores = []
        for _ in range(MUESTRAS_POR_DIANA):
            pg.wait_for_timeout(INTERVALO_MUESTRA_MS)
            tiro = pg.screenshot(clip=caja)
            img = Image.open(io.BytesIO(tiro)).convert("RGB")
            w = img.size[0]
            candidatos = [
                px
                for i, px in enumerate(img.getdata())
                if _distancia((i % w, i // w), punto_local) > MANO_RADIO_EXCLUSION
            ]
            # defensive: si la mano tapa la caja entera (caja diminuta) no
            # hay fondo que leer en este fotograma -- se salta en vez de
            # fallar sobre una lista vacia.
            if not candidatos:
                continue
            # El peor fondo es el de MENOR contraste contra el texto, no el
            # de mayor luminancia (ver docstring): con `--haze` de por medio
            # el shader puede empeorar el contraste ACERCANDOSE por abajo,
            # no solo alejandose por arriba.
            peor_contraste = min(_contraste(texto_rgb, px) for px in candidatos)
            peores.append(peor_contraste)
        # defensive: esto es un fallo de INSTRUMENTACION (caja mal calculada,
        # radio de exclusion mayor que la propia caja), no un resultado de
        # producto -- se sigue abortando (a diferencia del `assert` de
        # `main()` para el baseline, que SI acumula en `fallos`: ese es un
        # estado transitorio esperable del shader/Lenis, esto no lo es).
        assert peores, f"ningun pixel de fondo fuera del radio de la mano en {MUESTRAS_POR_DIANA} capturas de {selector_glifo}"
    finally:
        # el color se restaura siempre, incluso si una captura revienta --
        # si no, la diana se queda con el glifo apagado para el resto del
        # arnes (asercion 3 usa PULSABLE_SCROLL despues de esta).
        handle.evaluate(
            "(el, prev) => {"
            " if (prev) { el.style.color = prev; } else { el.style.removeProperty('color'); }"
            " el.querySelectorAll('*').forEach((d) => d.style.removeProperty('color'));"
            " }",
            color_previo,
        )
    return min(peores), texto_rgb


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

        # 7. contraste por glifo contra el peor fotograma del shader, con el
        # charco encendido. Solo sobre las dianas donde el charco enciende.
        # `.obra-abrir` no tiene texto propio (boton transparente que cubre
        # la fila entera, 1440px de ancho): el glifo visible es el
        # <h2 data-title> de esa misma tarjeta, verificado por
        # closest('section').
        #
        # Ronda de arreglo 1 (revision externa, reproducida con sonda
        # instrumentada) tumbo dos supuestos de la primera version:
        #
        #   - El punto donde se apuntaba ".obra-abrir" (40% de su ancho,
        #     x=576 en una caja de 1440px) caia FUERA del radio del charco
        #     (260px) alrededor del titular real (x=114-447): el charco
        #     quedaba practicamente apagado encima del texto, asi que
        #     "encendido" y "apagado" daban el mismo numero POR
        #     CONSTRUCCION, no porque el charco no importe. Corregido:
        #     `apuntar()` acepta ahora un punto explicito, y aqui se pasa el
        #     CENTRO del `<h2 data-title>` -- sigue dentro de ".obra-abrir"
        #     (la cubre entera) asi que el hover se dispara igual.
        #   - El color de texto se leia de `getComputedStyle(h2)`, que
        #     siempre da `--haze` -- el titular NO tiene color propio, son
        #     los DOS `<i>` apilados de `obraCartel.ts` los que lo tienen
        #     (`.obra-rl i:first-child` en --haze, `i:last-child` en
        #     --color-paper) y el hover real (`pointerenter` en
        #     `fila.seccion`, `obraCartel.ts:175-177`) dispara `relevo()`,
        #     que corre `.obra-rl` -50% y deja el `i:last-child` (papel) a
        #     la vista. Medir siempre contra `--haze` comparaba el mismo
        #     glifo en los dos estados. Corregido: se lee el color del `i`
        #     que de verdad queda visible en cada estado (`i:first-child` en
        #     reposo, `i:last-child` con el hover puesto), y se espera a que
        #     el tween de `relevo()` termine (`RELEVO_ESPERA_MS`, cubre
        #     duracion 0.42s + stagger de hasta 13 letras a 0.024s/letra,
        #     con margen) antes de fotografiar -- en los dos estados, para
        #     que el baseline compare la MISMA escena en reposo real y no
        #     una transicion a medio camino.
        #
        # El gate tambien cambio: era un escalon en AA_MINIMO (si el
        # baseline sin charco ya cumplia 4,5 exigia AA absoluto, si no
        # exigia baseline-0,3) y el baseline de ".hero-mail" oscila justo
        # alrededor de 4,5 segun el fotograma del shader -- la revision lo
        # reprodujo: en una corrida el baseline daba 4,48 (objetivo 4,18,
        # pasaba) y en otra 4,50 (objetivo salta a 4,50, no pasaba) con el
        # MISMO codigo. Un umbral mas fino que el ruido del propio
        # instrumento (regla ya escrita en CLAUDE.md). Corregido: el margen
        # se aplica SIEMPRE, sin escalon ni caso especial por AA_MINIMO.
        MARGEN_CHARCO = 0.3
        PUNTO_LEJOS = (-500.0, -500.0)
        # 0,42s de duracion + hasta 13 letras (titulo mas largo del
        # catalogo, "Editor de texto" sin contar espacios) x 0,024s de
        # stagger = 0,732s. Con margen.
        RELEVO_ESPERA_MS = 900

        DIANAS_CONTRASTE = (
            # (diana, glifo (bbox+ocultar), color_apagado, color_encendido, punto explicito)
            (PULSABLE, PULSABLE, PULSABLE, PULSABLE, None),
            (
                PULSABLE_SCROLL,
                "section:has(.obra-abrir) [data-title]",
                "section:has(.obra-abrir) .obra-rl i:first-child",
                "section:has(.obra-abrir) .obra-rl i:last-child",
                "section:has(.obra-abrir) [data-title]",
            ),
        )

        for diana, glifo, color_apagado_sel, color_encendido_sel, punto_sel in DIANAS_CONTRASTE:
            # Baseline con el charco apagado: se deja la diana en pantalla
            # (mismo encuadre de scroll que la medida "encendida" de abajo)
            # pero el raton se aparta a una esquina fuera de cualquier
            # pulsable -- `potencia(pg)` cae a 0 y el relevo del cartel (si
            # lo hay) vuelve a su reposo.
            pg.locator(diana).first.scroll_into_view_if_needed()
            pg.wait_for_timeout(600)
            pg.mouse.move(2, 2, steps=1)
            # Lenis sigue desplazando tras `scroll_into_view_if_needed` (trampa
            # ya pagada en este repo, ver rules/verification.md), `pot` decae
            # con la misma rampa que sube (`POT_SMOOTHING`), y el relevo del
            # cartel (si lo hay) tiene que volver a su reposo -- las tres
            # cosas caben en RELEVO_ESPERA_MS + margen.
            pg.wait_for_timeout(1200 + RELEVO_ESPERA_MS)
            pot_baseline = potencia(pg)
            if pot_baseline >= 0.05:
                # Se acumula en `fallos` en vez de abortar el resto del
                # arnes (antes era un `assert` que tumbaba la ejecucion
                # entera por un estado transitorio del shader/Lenis).
                fallos.append(f"charco no apagado para el baseline de {diana}: pot={pot_baseline}")
            ratio_apagado, _ = contraste_por_glifo(pg, glifo, PUNTO_LEJOS, color_apagado_sel)

            if punto_sel is not None:
                punto_diana = pg.locator(punto_sel).first.bounding_box()
                punto_explicito = (
                    punto_diana["x"] + punto_diana["width"] / 2,
                    punto_diana["y"] + punto_diana["height"] / 2,
                )
            else:
                punto_explicito = None
            punto = apuntar(pg, diana, punto_explicito)
            pg.wait_for_timeout(RELEVO_ESPERA_MS)
            ratio, texto_rgb = contraste_por_glifo(pg, glifo, punto, color_encendido_sel)

            objetivo = max(ratio_apagado - MARGEN_CHARCO, 0)
            print(
                f"contraste {diana} (glifo {glifo}, color rgb{texto_rgb}): "
                f"{ratio:.2f}:1 con el charco encendido, {ratio_apagado:.2f}:1 con el charco "
                f"apagado, objetivo {objetivo:.2f}:1 (peor de {MUESTRAS_POR_DIANA} muestras "
                "en cada caso)"
            )
            if ratio < objetivo:
                fallos.append(
                    f"contraste en {diana}: {ratio:.2f}:1 encendido < objetivo {objetivo:.2f}:1 "
                    f"(apagado {ratio_apagado:.2f}:1)"
                )

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
