"""Arnes de la escena «Quien soy» de Caelestia (fase B2).

Se lanza a mano contra el build de produccion servido, NUNCA contra `npm run
dev`: el HMR corrompe las medidas.

    npm run build && npx vite preview --port 4173 &
    python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4173
"""
import argparse
import sys
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

        comprobar(not errores, f"consola sin errores ({len(errores)})")
        navegador.close()

    print(f"\n{'TODO VERDE' if not FALLOS else f'{len(FALLOS)} FALLO(S)'}")
    for f in FALLOS:
        print(f"  - {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
