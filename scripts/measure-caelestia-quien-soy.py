"""Arnes de la escena «Quien soy» de Caelestia (fase B2).

Se lanza a mano contra el build de produccion servido, NUNCA contra `npm run
dev`: el HMR corrompe las medidas.

    npm run build && npx vite preview --port 4173 &
    python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4173
"""
import argparse
import pathlib
import re
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

FALLOS: list[str] = []


def comprobar(condicion: bool, etiqueta: str) -> None:
    print(("  OK   " if condicion else "  FALLO") + f"  {etiqueta}")
    if not condicion:
        FALLOS.append(etiqueta)


def escena_activa(pagina):
    """Lleva el carril a «Quien soy» y devuelve (escena, ventana).

    La ventana es la que CONTIENE la escena, no «la que esta en x=14»: durante
    la transicion del carril esa posicion todavia la ocupa el hero, y medir
    contra el da los numeros de otra escena.
    """
    pagina.click('[data-cae-ws="quien-es"]')
    pagina.wait_for_timeout(1400)
    return pagina.evaluate("""() => {
        const sc = document.querySelector('[data-scene="about"]');
        const v = sc && sc.closest('main[data-cae-track] > *');
        return { hayEscena: !!sc, hayVentana: !!v };
    }""")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
        errores: list[str] = []
        pagina.on("pageerror", lambda e: errores.append(str(e)))
        pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)

        pagina.goto(f"{args.base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        pagina.wait_for_timeout(3000)
        escena_activa(pagina)

        print("\n[1] Cabe en la ventana, y el aire esta repartido")
        medida = pagina.evaluate("""() => {
            const sc = document.querySelector('[data-scene="about"]');
            const ventana = sc.closest('main[data-cae-track] > *');
            const wr = ventana.getBoundingClientRect();
            let top = Infinity, bot = -Infinity;
            // Solo las HOJAS: un contenedor a toda la altura devolveria el alto
            // de la ventana y dejaria el aire en 0/0, que no dice nada.
            const visitar = (el) => {
                for (const h of el.children) {
                    if (h.children.length === 0) {
                        const r = h.getBoundingClientRect();
                        if (r.width > 0 && r.height > 0) {
                            top = Math.min(top, r.top); bot = Math.max(bot, r.bottom);
                        }
                    } else visitar(h);
                }
            };
            visitar(sc);
            return {
                alto: Math.round(bot - top),
                arriba: Math.round(top - wr.top),
                abajo: Math.round(wr.bottom - bot),
                desborde: ventana.scrollHeight - ventana.clientHeight,
                ventana: Math.round(wr.height),
            };
        }""")
        print(f"       alto {medida['alto']} · aire {medida['arriba']}/{medida['abajo']} "
              f"· ventana {medida['ventana']}")
        comprobar(medida["ventana"] == 748, f"la ventana mide 748 px ({medida['ventana']})")
        comprobar(medida["abajo"] >= 0, f"aire bajo el pie >= 0 ({medida['abajo']})")
        comprobar(medida["desborde"] <= 1, f"la ventana no desborda ({medida['desborde']} px)")

        print("\n[2] El nombre esta en 1 linea de caja y no desborda su columna")
        nombre = pagina.evaluate("""() => {
            const n = document.querySelector('[data-ficha-nombre]');
            const lh = parseFloat(getComputedStyle(n).lineHeight);
            const lineas = Math.max(1, Math.round(n.getBoundingClientRect().height / lh));

            // El ancho REAL del texto, con Range: getBoundingClientRect() del
            // propio elemento da el ancho del CONTENEDOR (con white-space:nowrap
            // el elemento no se encoge al texto salvo que sea inline), asi que
            // esa medida da siempre verde y no vigila nada. Range mide el texto.
            const rango = document.createRange();
            rango.selectNodeContents(n);
            const anchoTexto = rango.getBoundingClientRect().width;

            // El ancho disponible NO es el clientWidth de la columna
            // (`cuerpo.children[1]`): esa columna es una pista `1fr` de un
            // grid SIN `minmax(0, 1fr)`, y una pista `1fr` sin ese piso tiene
            // de minimo automatico su propio contenido (`auto` = max-content)
            // — con `white-space: nowrap` el minimo del texto es su ancho
            // entero, asi que la pista SIEMPRE crece hasta igualar el texto y
            // la comprobacion "cabe en su columna" se volveria trivialmente
            // verdadera sea cual sea el tamano de letra (medido: a 8rem,
            // columnaWidth y anchoTexto salian los dos 972.84, identicos).
            // El ancho real y fijo es el PRESUPUESTO: el propio `.ficha-cuerpo`
            // no crece con el contenido (tiene `max-width: 1180px`), asi que
            // cuerpo.width - retrato.width - gap es una cota que no se mueve
            // aunque el nombre la desborde.
            const cuerpo = n.closest('.ficha-cuerpo');
            const cuerpoRect = cuerpo.getBoundingClientRect();
            const retrato = cuerpo.children[0];
            const anchoRetrato = retrato.getBoundingClientRect().width;
            const gap = parseFloat(getComputedStyle(cuerpo).columnGap) || 0;
            const anchoDisponible = cuerpoRect.width - anchoRetrato - gap;

            return {
                lineas,
                anchoTexto: Math.round(anchoTexto),
                anchoDisponible: Math.round(anchoDisponible),
            };
        }""")
        print(f"       ancho del texto {nombre['anchoTexto']} · ancho disponible en la columna {nombre['anchoDisponible']}")
        comprobar(nombre["lineas"] == 1, f"el nombre esta en 1 linea de caja ({nombre['lineas']})")
        comprobar(
            nombre["anchoTexto"] <= nombre["anchoDisponible"],
            f"el texto del nombre cabe en el ancho disponible de su columna "
            f"({nombre['anchoTexto']} <= {nombre['anchoDisponible']})",
        )

        print("\n[3] El filete mide el largo del correo")
        # Se mide el estado ATERRIZADO, no un fotograma de la entrada: el
        # filete se despliega en t=1.6..2.02 s de la timeline y a los 1400 ms
        # que espera `escena_activa` todavia va por 24 px de 249. La espera es
        # acotada y exige ademas ancho > 0, asi que sigue pudiendo fallar: si
        # el filete no se mide nunca se queda en 0 y agota el plazo.
        try:
            pagina.wait_for_function(
                """() => {
                    const r = document.querySelector('[data-ficha-regla]');
                    if (!r) return false;
                    const w = r.getBoundingClientRect().width;
                    const prev = window.__reglaPrev;
                    window.__reglaPrev = w;
                    return w > 0 && prev !== undefined && Math.abs(prev - w) < 0.5;
                }""",
                timeout=6000,
            )
        except Exception as exc:  # noqa: BLE001 - se reporta como FALLO, no se traga
            print(f"       el filete no llego a asentarse: {type(exc).__name__}")
        # Con `Range`, nunca con la caja del <a>: `.ficha-host` es un enlace y su
        # getBoundingClientRect() devolveria el ancho de la COLUMNA, no el del
        # texto — el filete saldria siempre del ancho entero y el gate diria
        # verde midiendo otra cosa. Es la trampa que B1 ya pago con su
        # justificacion.
        filete = pagina.evaluate("""() => {
            const host = document.querySelector('[data-ficha-host]');
            const regla = document.querySelector('[data-ficha-regla]');
            const rg = document.createRange();
            rg.selectNodeContents(host);
            return {
                texto: Math.round(rg.getBoundingClientRect().width),
                regla: Math.round(regla.getBoundingClientRect().width),
                caja: Math.round(host.getBoundingClientRect().width),
            };
        }""")
        print(f"       texto {filete['texto']} px \u00b7 filete {filete['regla']} px "
              f"\u00b7 (caja del <a>: {filete['caja']} px)")
        comprobar(abs(filete["texto"] - filete["regla"]) <= 2,
                  f"el filete mide el largo del texto ({filete['regla']} vs {filete['texto']})")

        print("\n[3b] Volver a pulsar la pastilla activa no relanza la entrada")
        # Barata y con poder de deteccion: la escena ya esta aterrizada (el
        # gate 3 espero a que el filete se asentara), asi que un relanzamiento
        # se delata solo — `reproducir()` pone el comando a "" y el filete a 0
        # en su primer fotograma. Se lee a los 400 ms: dentro del tecleo
        # (0.34-0.78 s) y muy lejos de los 2.02 s en que el filete volveria a
        # estar entero, asi que un relanzamiento NO puede colarse como verde.
        pagina.click('[data-cae-ws="quien-es"]')
        pagina.wait_for_timeout(400)
        repeticion = pagina.evaluate("""() => ({
            comando: document.querySelector('[data-ficha-cmd]').textContent,
            regla: Math.round(document.querySelector('[data-ficha-regla]').getBoundingClientRect().width),
        })""")
        print(f"       tras repulsar: comando {repeticion['comando']!r} "
              f"\u00b7 filete {repeticion['regla']} px")
        comprobar(repeticion["comando"] == "neofetch",
                  f"el comando no se vuelve a teclear ({repeticion['comando']!r})")
        comprobar(repeticion["regla"] > 0,
                  f"el filete no vuelve a cero ({repeticion['regla']})")

        print("\n[6] Movimiento reducido: el pseudo-elemento de la fila tambien se apaga")
        # `*` NO alcanza pseudo-elementos: el guard de arriba
        # ([data-ficha="neofetch"] *) deja fuera a `.ficha-k::before` (la
        # flecha ">" que entra deslizando al rozar una fila), asi que sigue
        # animando bajo movimiento reducido si no se cubre aparte.
        contexto_reduce = navegador.new_context(viewport={"width": 1440, "height": 900},
                                                  reduced_motion="reduce")
        pg_reduce = contexto_reduce.new_page()
        pg_reduce.goto(f"{args.base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        pg_reduce.wait_for_timeout(3000)
        pg_reduce.click('[data-cae-ws="quien-es"]')
        pg_reduce.wait_for_timeout(1400)
        script_pseudo = (
            "() => { const k = document.querySelector('.ficha-k'); "
            "const antes = getComputedStyle(k, '::before'); "
            "return { duracion: antes.transitionDuration }; }"
        )
        pseudo = pg_reduce.evaluate(script_pseudo)
        print(f"       .ficha-k::before transition-duration bajo reduce: {pseudo['duracion']}")
        comprobar(pseudo["duracion"] == "0s",
                  f"el pseudo-elemento .ficha-k::before no anima bajo reduce ({pseudo['duracion']})")

        # «Escena montada, sin recorrido»: bajo reduce la ficha no se teclea ni
        # se despliega, pero tiene que estar ENTERA. Sin esto, un modulo que
        # devolviera pronto bajo reduce dejaria el comando vacio y el filete a
        # cero, y el arnes seguiria verde con la escena a medio pintar.
        reducido = pg_reduce.evaluate("""() => {
            const cmd = document.querySelector('[data-ficha-cmd]');
            const regla = document.querySelector('[data-ficha-regla]');
            const punto = document.querySelector('.ficha-punto');
            const nombre = document.querySelector('[data-ficha-nombre]');
            return {
                comando: cmd.textContent,
                regla: Math.round(regla.getBoundingClientRect().width),
                latido: getComputedStyle(punto).animationName,
                recorte: getComputedStyle(nombre).clipPath,
            };
        }""")
        print(f"       comando {reducido['comando']!r} \u00b7 filete {reducido['regla']} px "
              f"\u00b7 latido {reducido['latido']} \u00b7 recorte {reducido['recorte']}")
        comprobar(reducido["comando"] == "neofetch",
                  f"el comando ya esta escrito ({reducido['comando']!r})")
        comprobar(reducido["regla"] > 0, f"el filete ya esta a su ancho ({reducido['regla']})")
        comprobar(reducido["latido"] == "none", f"el punto no late ({reducido['latido']})")
        contexto_reduce.close()

        print("\n[4] El retrato morfa, no corta")
        pagina.evaluate("""() => {
            window.__morf = [];
            const img = document.querySelector('[data-ficha-retrato] img');
            const tic = () => {
                window.__morf.push(getComputedStyle(img).clipPath);
                if (window.__morf.length < 90) requestAnimationFrame(tic);
            };
            requestAnimationFrame(tic);
        }""")
        # Hover REAL: un MouseEvent sintetico no dispara `:hover`.
        pagina.hover("[data-ficha-retrato]")
        pagina.wait_for_timeout(1400)
        estados = len(set(pagina.evaluate("window.__morf")))
        # Umbral 4 y no 9: un umbral pegado a la medida mide la carga de la
        # maquina, no el diseno. Sin transicion salen exactamente 2.
        comprobar(estados >= 4, f"el clip-path recorre estados intermedios ({estados})")


        print("\n[7] Anti-mock: todo texto visible existe en content.ts")
        # `content.ts` se lee desde la RAIZ del repo: el arnes se lanza con
        # `python3 scripts/measure-...py` desde el raiz, como documenta la
        # cabecera. Si no se encuentra, se falla en alto en vez de saltarse el
        # gate: un anti-mock que se auto-desactiva cuando no halla la fuente es
        # exactamente el instrumento que no puede dar rojo.
        fuente_path = pathlib.Path(__file__).resolve().parent.parent / "src" / "data" / "content.ts"
        comprobar(fuente_path.is_file(), f"se encuentra la fuente de contenido ({fuente_path})")
        fuente = fuente_path.read_text(encoding="utf-8") if fuente_path.is_file() else ""
        textos = pagina.evaluate("""() => {
            const ficha = document.querySelector('[data-ficha="neofetch"]');
            const nodos = ficha.querySelectorAll(
                '[data-ficha-nombre], [data-ficha-host], .ficha-estado, [data-ficha-frase], .ficha-v, .ficha-s');
            return Array.from(nodos)
                .map((n) => (n.firstChild && n.firstChild.nodeType === 3
                    ? n.firstChild.textContent : n.textContent).trim())
                .filter((t) => t.length > 0);
        }""")
        # Los valores compuestos («rol · organizacion») se parten por el
        # separador: cada mitad tiene que existir literal en content.ts. El
        # separador se parte con expresion regular y NO con la cadena " · ":
        # la fila de enfoque une sus dos titulos con DOS espacios a cada lado,
        # asi que un split por la cadena exacta la dejaria entera y daria un
        # fallo falso.
        piezas: list[str] = []
        for texto in textos:
            piezas.extend(p.strip() for p in re.split(r"\s+·\s+", texto) if p.strip())
        # `Desde <cifra>` es la unica composicion de este modulo: el rotulo lo
        # pone la ficha y la cifra sale de `stats`. Se exime EL PREFIJO Y SOLO
        # EL PREFIJO: se le quita "Desde " a la pieza y se compara lo que
        # queda, que es la cifra.
        #
        # Con `not p.startswith("Desde ")` —que es como estaba— la exencion se
        # comia la pieza ENTERA: `Desde 1492` (literal inventado, confirmado en
        # el bundle) salia en verde. Justo la clase de dato falso que este gate
        # existe para cazar.
        comprobar(len(piezas) >= 12, f"el gate ve texto de la ficha ({len(piezas)} piezas)")
        huerfanos = [p for p in piezas if p.removeprefix("Desde ") not in fuente]
        comprobar(not huerfanos, f"todo texto sale de content.ts (huerfanos: {huerfanos})")

        print("\n[8] Los ejes del shell no se han movido")
        # `opsz` en Fraunces no es estilo: son dibujos distintos de la letra
        # segun el tamano al que se lea. El display del shell tiene que seguir
        # en su token (opsz 9) y solo el nombre de la ficha usa el del cartel
        # (opsz 144). Reutilizar un token para los dos es el fallo que B1 vino
        # a cerrar.
        #
        # NO se lee en `.cae-mark`: la marca de la barra es Martian Mono y no
        # lleva ejes variables — medida, devuelve `normal` siempre, asi que una
        # asercion sobre ella no vigila el opsz de nada. De la marca solo se
        # comprueba lo que si es suyo: que sigue siendo la mono del shell.
        #
        # Se lee en el PRIMER `h1` de la pagina, que hoy es el del hero. Ojo
        # con la etiqueta: ese `h1` NO es "el display del shell", es un
        # consumidor cualquiera de `--cae-display-axes` (la regla que se lo da
        # es `[data-display], h1, h2`). Y es fragil: en `main` ya hay un
        # segundo `h1` (`.cae-tit`, de B1), asi que tras el merge este
        # `querySelector` puede acabar mirando otro nodo.
        #
        # Por eso la asercion ROBUSTA de las tres es la que compara los dos
        # TOKENS entre si: no depende de que nodo se elija, y es la que dice
        # literalmente lo que la fase B1 vino a cerrar (dos tokens, nunca uno
        # reutilizado). Las otras dos son la comprobacion de que los tokens,
        # ademas de existir, llegan pintados a donde tienen que llegar.
        ejes = pagina.evaluate("""() => {
            const cs = getComputedStyle(document.documentElement);
            const marca = document.querySelector('.cae-mark');
            return {
                shell: getComputedStyle(document.querySelector('h1')).fontVariationSettings,
                nombre: getComputedStyle(document.querySelector('[data-ficha-nombre]')).fontVariationSettings,
                marcaFamilia: getComputedStyle(marca).fontFamily,
                tokenShell: cs.getPropertyValue('--cae-display-axes').trim(),
                tokenCartel: cs.getPropertyValue('--cae-display-axes-cartel').trim(),
            };
        }""")
        print(f"       primer h1 {ejes['shell']} · nombre de la ficha {ejes['nombre']}")
        print(f"       tokens: shell {ejes['tokenShell']!r} · cartel {ejes['tokenCartel']!r}")
        comprobar('"opsz" 9' in ejes["shell"],
                  f"el primer h1 de la pagina (hoy, el del hero) sigue en opsz 9 "
                  f"({ejes['shell']})")
        comprobar('"opsz" 144' in ejes["nombre"],
                  f"el nombre de la ficha usa opsz 144 ({ejes['nombre']})")
        # La asercion robusta: dos tokens, nunca uno reutilizado. Si alguien
        # apunta el cartel al token del shell, las dos de arriba se caen
        # tambien — pero esta lo dice por su nombre, y sigue valiendo aunque el
        # `querySelector('h1')` acabe eligiendo otro nodo tras el merge de B1.
        comprobar(ejes["tokenShell"] != ejes["tokenCartel"] and ejes["tokenCartel"] != "",
                  f"cartel y shell son tokens distintos ({ejes['tokenCartel']!r})")
        comprobar("Martian" in ejes["marcaFamilia"],
                  f"la marca de la barra sigue en la mono del shell ({ejes['marcaFamilia']})")

        print("\n[9] La escena conserva nombre accesible sin aportar caja")
        # La escena se rehace entera bajo Caelestia y su `<h2>Quién soy</h2>`
        # sobra VISUALMENTE — pero ocultarlo con `display: none` lo saca
        # tambien del arbol de accesibilidad, y era el unico encabezado de la
        # escena: «Quien soy» quedaba como la unica de las cinco sin nombre
        # accesible. El nombre de la ficha es un `<p>`, no lo suple.
        #
        # Se mide contra el ARBOL ARIA de verdad (`aria_snapshot`, que es lo
        # que expone el navegador a un lector de pantalla), no contra la
        # presencia del nodo en el DOM: el nodo sigue ahi con `display: none` y
        # una asercion de DOM saldria verde con el fallo puesto. Esta fase ya
        # pago una asercion titulada «y usa el ancla» que solo leia
        # `outlineStyle` y no demostraba nada.
        #
        # `page.accessibility` NO existe en Playwright Python 1.59 (se retiro);
        # `locator.aria_snapshot()` es la via vigente.
        comprobar(pagina.locator('[data-scene="about"] .hero-kick').count() == 1,
                  "la escena sigue teniendo su .hero-kick en el DOM")
        arbol = pagina.locator('[data-scene="about"]').aria_snapshot()
        print("       arbol ARIA de la escena:")
        for linea in arbol.splitlines()[:6]:
            print(f"         {linea}")
        comprobar('heading "Quién soy"' in arbol,
                  "el h2 sigue en el arbol ARIA de la escena como encabezado")
        comprobar(pagina.locator('[data-scene="about"]')
                  .get_by_role("heading", name="Quién soy").count() == 1,
                  "y se puede alcanzar por rol+nombre (encabezado «Quién soy»)")
        caja = pagina.evaluate("""() => {
            const h = document.querySelector('[data-scene="about"] .hero-kick');
            const sc = document.querySelector('[data-scene="about"]');
            if (!h || !sc) return null;
            const r = h.getBoundingClientRect(), cs = getComputedStyle(h);
            return {
                w: r.width, h: r.height, display: cs.display,
                visibility: cs.visibility, position: cs.position,
                desborde: sc.scrollHeight - sc.clientHeight,
            };
        }""")
        print(f"       caja del h2 {caja['w']:.2f}x{caja['h']:.2f} · display {caja['display']} · "
              f"visibility {caja['visibility']} · desborde de la escena {caja['desborde']}px")
        # Visualmente oculto es EXACTAMENTE eso: sigue pintado (por eso no vale
        # `display:none` ni `visibility:hidden`, que lo borrarian del arbol) y a
        # la vez no ocupa ni una linea de texto.
        comprobar(caja["display"] != "none" and caja["visibility"] != "hidden",
                  f"no se oculta borrandolo del arbol ({caja['display']} / {caja['visibility']})")
        comprobar(caja["w"] <= 1.5 and caja["h"] <= 1.5,
                  f"el h2 no aporta caja visible ({caja['w']:.2f}x{caja['h']:.2f})")
        comprobar(caja["desborde"] <= 1,
                  f"la escena no desborda por el h2 ({caja['desborde']}px)")

        print("\n[5] Contraste de los pares que se pintan, en los dos esquemas")
        # NO se inventa una API para forzar la hora. El motor de color lee el
        # reloj del sistema (`new Date().getHours()`), asi que el esquema se
        # cambia con la ZONA HORARIA del contexto de Playwright, que es real y
        # no toca el codigo de produccion.
        #
        # Dos muestras bastan, y no es un atajo: la fase A dejo demostrado que
        # la claridad de cada rol NO se mueve con el matiz, asi que dentro de
        # un esquema el contraste es invariante a la hora. Lo que cambia el
        # contraste es el ESQUEMA, y esquemas hay dos.
        #
        # Las zonas se ELIGEN EN CALIENTE contra el reloj real, no se fijan en
        # el codigo. Un par fijo no puede garantizar el cruce: la ventana de
        # dia dura 13 h y la de noche 11, asi que para cualquier separacion
        # fija hay horas en que las dos zonas caen del mismo lado — y un par
        # separado 24 h exactas (p. ej. UTC+14 y UTC-10) da SIEMPRE la MISMA
        # hora local, que es el barrido que no cruza el umbral que la fase A ya
        # pago con un reloj congelado.
        CANDIDATAS = (
            "Pacific/Kiritimati", "Pacific/Auckland", "Asia/Tokyo", "Asia/Kolkata",
            "Europe/Madrid", "Atlantic/Reykjavik", "America/New_York",
            "America/Los_Angeles", "Pacific/Honolulu", "Pacific/Midway",
        )
        ahora_utc = datetime.now(timezone.utc)

        def es_noche(zona: str) -> bool:
            local = ahora_utc.astimezone(ZoneInfo(zona))
            minutos = local.hour * 60 + local.minute
            return minutos < 7 * 60 or minutos >= 20 * 60

        zona_dia = next((z for z in CANDIDATAS if not es_noche(z)), None)
        zona_noche = next((z for z in CANDIDATAS if es_noche(z)), None)
        comprobar(zona_dia is not None and zona_noche is not None,
                  f"hay una zona de dia y una de noche ({zona_dia} / {zona_noche})")

        PARES = [
            ("[data-ficha-nombre]", "el nombre"),
            ("[data-ficha-host]", "el correo"),
            (".ficha-estado", "la disponibilidad"),
            ("[data-ficha-frase]", "la frase"),
            (".ficha-k", "las claves"),
            (".ficha-v", "los valores"),
            (".ficha-s", "los detalles"),
        ]
        # Los tokens de Caelestia son `oklch()`, y `getComputedStyle` los
        # devuelve TAL CUAL: "oklch(0.925 0.005 51.3)". Leer esos tres numeros
        # como bytes RGB es el instrumento roto que la fase A ya pago (daba
        # 1.00:1 en todo). Se convierten pintandolos en un lienzo 1x1 y leyendo
        # el pixel: eso da los bytes sRGB que el navegador PINTA de verdad,
        # sea cual sea la sintaxis del token. Se comprueba ademas que la
        # conversion funciona (dos colores distintos dan pixeles distintos):
        # si `fillStyle` rechazara la cadena, se quedaria con el valor anterior
        # y todos los pares saldrian identicos, o sea otra tautologia.
        #
        # Toma `{sel, pseudo}` y no un selector suelto porque uno de los pares
        # del roce es `.ficha-k::before` (el ">"), que NO es un nodo del DOM:
        # la unica via de leer su color es `getComputedStyle(el, "::before")`.
        CONTRASTE_JS = """({ sel, pseudo }) => {
            const el = document.querySelector(sel);
            if (!el) return null;
            const csEl = getComputedStyle(el, pseudo || null);
            const cv = document.createElement("canvas");
            cv.width = cv.height = 1;
            const ctx = cv.getContext("2d", { willReadFrequently: true });
            const bytes = (c, debajo) => {
                ctx.clearRect(0, 0, 1, 1);
                if (debajo) {
                    ctx.fillStyle = `rgb(${debajo[0]},${debajo[1]},${debajo[2]})`;
                    ctx.fillRect(0, 0, 1, 1);
                }
                ctx.fillStyle = "#000";
                ctx.fillStyle = c;
                if (ctx.fillStyle === "#000000" && !/^#0{6}$|black|rgb\\(0, 0, 0\\)/.test(c)) return null;
                ctx.fillRect(0, 0, 1, 1);
                const d = ctx.getImageData(0, 0, 1, 1).data;
                return [d[0], d[1], d[2]];
            };
            const lum = ([r, g, b]) => {
                const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
                return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
            };
            // El fondo REAL: se sube por los ancestros hasta el primero que
            // pinte algo. Comparar contra el rol teorico es como se colo que
            // el reloj de la barra estuviera bajo AA cuatro horas al dia.
            let nodo = el, fondo = null;
            while (nodo && fondo === null) {
                const bg = getComputedStyle(nodo).backgroundColor;
                if (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent") fondo = bg;
                nodo = nodo.parentElement;
            }
            const bFondo = bytes(fondo || "rgb(255,255,255)", [255, 255, 255]);
            const bTexto = bytes(csEl.color, bFondo);
            if (!bFondo || !bTexto) return null;
            const a = lum(bTexto), b = lum(bFondo);
            return {
                ratio: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05),
                texto: bTexto, fondo: bFondo,
                // El ">" entra con `opacity` de 0 a 1. Medir su color mientras
                // sigue a medio camino da un numero que no se pinta: se exige
                // opacidad 1 (o sea, la transicion ya aterrizada) antes de
                // creerse el ratio.
                opacidad: parseFloat(csEl.opacity),
                color: csEl.color,
            };
        }"""

        peor, peor_etiqueta = 21.0, ""
        esquemas_vistos: list[str] = []
        for zona in (z for z in (zona_dia, zona_noche) if z):
            ctx = navegador.new_context(viewport={"width": 1440, "height": 900}, timezone_id=zona)
            pg3 = ctx.new_page()
            pg3.goto(f"{args.base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            pg3.wait_for_timeout(3000)
            pg3.click('[data-cae-ws="quien-es"]')
            pg3.wait_for_timeout(2000)
            esquema = pg3.evaluate("() => document.documentElement.dataset.caeEsquema")
            esquemas_vistos.append(esquema)
            hora = pg3.evaluate("() => new Date().getHours() + ':' + new Date().getMinutes()")
            for selector, etiqueta in PARES:
                medida_par = pg3.evaluate(CONTRASTE_JS, {"sel": selector, "pseudo": None})
                comprobar(medida_par is not None,
                          f"se pudo medir {etiqueta} en esquema {esquema} ({selector})")
                if medida_par is None:
                    continue
                print(f"       {etiqueta}: {medida_par['ratio']:.2f}:1")
                if medida_par["ratio"] < peor:
                    peor, peor_etiqueta = medida_par["ratio"], f"{etiqueta} en esquema {esquema}"

            # --- El ROCE, no solo el reposo ---------------------------------
            # Medir solo el estado en reposo dejaba pasar el fallo que cerro
            # esta rama: `.ficha-fila:hover .ficha-k` pintaba la clave con el
            # ancla sobre `--cae-surface` y daba 1.46:1 de dia (14.11:1 de
            # noche, o sea que un solo esquema tampoco lo habria visto). El
            # gesto que el spec vende como «el prompt marcando la linea que
            # miras» EMPEORABA la legibilidad trece horas al dia.
            #
            # Dos avisos ya pagados en esta fase:
            #  - un `MouseEvent` sintetico NO dispara `:hover` (el navegador no
            #    mueve el puntero real), asi que las reglas de roce no se
            #    aplican y se acaba midiendo el reposo creyendo medir el roce.
            #    Hay que usar el hover de verdad de Playwright.
            #  - el ">" es un `::before`: se lee con el segundo argumento de
            #    `getComputedStyle`.
            # Que `querySelector('.ficha-fila:hover ...')` devuelva algo es la
            # prueba de que el roce llego: si no, la medida sale None y cae.
            pg3.locator("[data-ficha-fila]").first.hover()
            pg3.wait_for_timeout(600)
            PARES_ROCE = [
                (".ficha-fila:hover .ficha-k", None, "la clave rozada"),
                (".ficha-fila:hover .ficha-k", "::before", "el > de la clave rozada"),
            ]
            for selector, pseudo, etiqueta in PARES_ROCE:
                medida_par = pg3.evaluate(CONTRASTE_JS, {"sel": selector, "pseudo": pseudo})
                comprobar(medida_par is not None,
                          f"el roce llego y se pudo medir {etiqueta} en esquema {esquema}")
                if medida_par is None:
                    continue
                comprobar(medida_par["opacidad"] == 1,
                          f"{etiqueta} esta aterrizado (opacidad {medida_par['opacidad']}) "
                          f"en esquema {esquema}")
                print(f"       {etiqueta}: {medida_par['ratio']:.2f}:1 "
                      f"({medida_par['color']} sobre rgb{tuple(medida_par['fondo'])})")
                if medida_par["ratio"] < peor:
                    peor, peor_etiqueta = medida_par["ratio"], f"{etiqueta} en esquema {esquema}"
            print(f"       {zona} (hora local {hora}): esquema {esquema}")
            ctx.close()
        # Si las dos zonas dan el mismo esquema, el gate mide dos veces lo
        # mismo y no vale: un barrido que no cruza el umbral es el fallo que la
        # fase A pago con un reloj congelado.
        comprobar(len(set(esquemas_vistos)) == 2,
                  f"se han visto los DOS esquemas ({esquemas_vistos})")
        print(f"       peor par: {peor:.2f}:1 ({peor_etiqueta})")
        comprobar(peor >= 4.5, f"contraste >= 4.5:1 en los dos esquemas ({peor:.2f}:1, {peor_etiqueta})")

        comprobar(not errores, f"consola sin errores ({len(errores)})")
        navegador.close()

    print(f"\n{'TODO VERDE' if not FALLOS else f'{len(FALLOS)} FALLO(S)'}")
    for f in FALLOS:
        print(f"  - {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
