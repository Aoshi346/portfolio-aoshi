"""Arnes de la escena «Fundido» de Caelestia (fase B5, contraportada del escritorio).

Se lanza a mano contra el build de produccion servido, NUNCA contra `npm run
dev`: el HMR corrompe las medidas. En ESTE worktree el `vite preview` corre en
el puerto 4193 (Ruling H) — el 4173 sirve OTRO repositorio de otra sesion.

    export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
    npm run build
    python3 scripts/measure-caelestia-fundido.py --base http://localhost:4193

Los catorce gates (ver el spec, seccion `## Los gates`):
  1. jerarquia tipografica (el titular > acto > destino, valor exacto)
  2. los ejes de cierre, no los del cartel
  3. la ocupacion, medida con Range (no con la caja de bloque)
  4. sin scroll interno, en 1440 y en 390
  5. los cuatro canales siguen accionables (mailto/tel/rel)
  6. el dato se lee sin hover
  7. contraste AA en los dos esquemas, solo los pares que se pintan de verdad
  8. el fundido suena una vez; la entrada, todas
  9. la entrada cabe dentro del deslizamiento del carril (440 < 520)
  10. `prefers-reduced-motion` aterriza la escena en 0 ms
  11. 390 px: paso exacto, ocupacion, blancos >= 48x48, sello cuadrado
  12. Vice y Hyprland no se alteran (`contacto.ts` es compartido)
  13. el fundido interrumpido aterriza del todo (bicho, nube, suelo, zancada)
  14. rozar responde y el teclado llega a lo mismo (el P1 de `vera-art-director`)
"""
import argparse
import pathlib
import re
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

FALLOS: list[str] = []
RAIZ = pathlib.Path(__file__).resolve().parent.parent


def comprobar(condicion: bool, etiqueta: str) -> None:
    print(("  OK   " if condicion else "  FALLO") + f"  {etiqueta}")
    if not condicion:
        FALLOS.append(etiqueta)


# El fondo del pixel real, no el rol teorico: convertir `oklch()` leyendolo
# como bytes RGB es el instrumento roto que la fase A ya pago (1.00:1 en todo
# el reloj). Se pinta en un lienzo 1x1 y se lee el pixel que el navegador
# PINTA de verdad, tal como ya hace `measure-caelestia-quien-soy.py`.
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
    // El fondo REAL: se sube por los ancestros hasta el primero que pinte
    // algo. Comparar contra el rol teorico es como se colo que el reloj de
    // la barra estuviera bajo AA cuatro horas al dia.
    // De paso se ACUMULA la opacidad: un ancestro con `opacity` atenua a su
    // descendiente igual que la propia, y leer solo la del nodo deja pasar
    // cualquier atenuacion puesta un nivel mas arriba -- el mismo modo de
    // fallo que la trampa de `getComputedStyle().color`, un piso mas alto. Se
    // multiplica desde el elemento HASTA el que pinta el fondo, sin incluirlo:
    // de ese hacia arriba, texto y fondo se atenuan juntos y el ratio no se
    // mueve.
    //
    // Y NO SE PARA EN EL PRIMERO QUE PINTE: se para en el primero que pinte
    // OPACO, apilando por el camino los que pintan a medias. Pararse en el
    // primero valia mientras nada pintaba translucido; en cuanto los canales
    // ganaron su capa de estado (`currentColor` al 10 %), el gate componia esa
    // capa sobre BLANCO —el fondo por defecto del lienzo— y devolvia 1,03:1
    // para un texto que en pantalla se lee perfectamente. El instrumento, otra
    // vez: media la capa contra un fondo que no existe.
    const pila = [];
    let nodo = el, alfaAcum = 1, opaco = null;
    while (nodo && opaco === null) {
        const cs = getComputedStyle(nodo);
        const bg = cs.backgroundColor;
        if (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent") {
            const m = bg.match(/[\\d.]+/g);
            // Sin cuarto canal es opaco; `color(srgb ...)` y `oklab(...)` lo
            // llevan al final igual que `rgba()`.
            const a = m && m.length >= 4 ? parseFloat(m[m.length - 1]) : 1;
            if (a >= 0.999) { opaco = bg; break; }
            pila.push(bg);
        }
        const o = parseFloat(cs.opacity);
        if (!Number.isNaN(o)) alfaAcum *= o;
        nodo = nodo.parentElement;
    }
    // Se compone de abajo arriba: el opaco primero, y encima las capas a
    // medias en el orden en que las ve el pintor (la mas lejana del texto
    // primero, que es el final de la pila).
    let bFondo = bytes(opaco || "rgb(255,255,255)", [255, 255, 255]);
    for (let i = pila.length - 1; i >= 0 && bFondo; i--) bFondo = bytes(pila[i], bFondo);
    let bTexto = bytes(csEl.color, bFondo);
    if (!bFondo || !bTexto) return null;
    // `getComputedStyle(...).color` NO SE MUEVE CON `opacity`: sigue devolviendo
    // el color OPACO del texto aunque `--fundido-dim` lo este atenuando de
    // verdad en pantalla. Es la misma trampa que la Task 6/B2 ya documentaron
    // para otro caso (opacidad independiente del color computado) -- aqui la
    // paga el propio gate si no se corrige: los rotulos del pie y el estado
    // pintan a `opacity: var(--fundido-dim)`, y sin blanquear el color con esa
    // opacidad contra el fondo, el gate mide el texto a opacidad 1 SIEMPRE,
    // sea cual sea `--fundido-dim` -- un gate que no puede fallar.
    const alfa = alfaAcum;
    if (!Number.isNaN(alfa) && alfa < 1) {
        bTexto = [0, 1, 2].map((i) => Math.round(alfa * bTexto[i] + (1 - alfa) * bFondo[i]));
    }
    const a = lum(bTexto), b = lum(bFondo);
    return {
        ratio: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05),
        texto: bTexto, fondo: bFondo, color: csEl.color, opacidad: alfa,
    };
}"""


def nueva_pagina_en_contacto(navegador, base, *, viewport=None, timezone_id=None, reduced_motion=None):
    """Abre una pagina fresca en Caelestia y lleva el carril a «contacto».

    Es la primera visita al workspace SIEMPRE (contexto nuevo, `fundidoVisto`
    empieza en `false`), asi que dispara `reproducir()`. Se espera a que el
    fundido de 1900 ms termine del todo antes de devolver el control: medir
    antes de eso es medir un fotograma a medio fundir.
    """
    kwargs = {"viewport": viewport or {"width": 1440, "height": 900}}
    if timezone_id:
        kwargs["timezone_id"] = timezone_id
    if reduced_motion:
        kwargs["reduced_motion"] = reduced_motion
    ctx = navegador.new_context(**kwargs)
    errores: list[str] = []
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errores.append(str(e)))
    pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
    pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(3000)
    pg.click('[data-cae-ws="contacto"]')
    pg.wait_for_timeout(2600)
    return ctx, pg, errores


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4193")
    args = ap.parse_args()
    base = args.base

    errores_totales: list[str] = []

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])

        # ================================================================
        # [1] La jerarquia no esta invertida
        # ================================================================
        print("\n[1] La jerarquia tipografica: titular > acto > destino")
        ctx, pg, err = nueva_pagina_en_contacto(navegador, base)
        errores_totales += err
        jerarquia = pg.evaluate("""() => {
            const px = (sel) => parseFloat(getComputedStyle(document.querySelector(sel)).fontSize);
            return {
                titular: px('.contacto-lead'),
                acto: px('[data-canal="acto"] .contacto-bar-value'),
                destino: px('[data-canal="destino"] .contacto-bar-value'),
            };
        }""")
        print(f"       titular {jerarquia['titular']} · acto {jerarquia['acto']} "
              f"· destino {jerarquia['destino']}")
        comprobar(abs(jerarquia["titular"] - 159.66) < 0.5,
                  f"el titular mide exactamente --t-10 (159.66px, medido {jerarquia['titular']})")
        comprobar(jerarquia["titular"] > jerarquia["acto"] > jerarquia["destino"],
                  f"la jerarquia no esta invertida (titular {jerarquia['titular']} > "
                  f"acto {jerarquia['acto']} > destino {jerarquia['destino']})")
        ctx.close()

        # ================================================================
        # [2] Los ejes son los que tocan: --cae-display-axes-cierre
        # ================================================================
        print("\n[2] Los ejes de cierre, no los del cartel ni los del shell")
        ctx, pg, err = nueva_pagina_en_contacto(navegador, base)
        errores_totales += err
        ejes = pg.evaluate("""() => {
            const cs = getComputedStyle(document.documentElement);
            return {
                lead: getComputedStyle(document.querySelector('.contacto-lead')).fontVariationSettings,
                tokenCierre: cs.getPropertyValue('--cae-display-axes-cierre').trim(),
                tokenShell: cs.getPropertyValue('--cae-display-axes').trim(),
                tokenCartel: cs.getPropertyValue('--cae-display-axes-cartel').trim(),
            };
        }""")
        print(f"       .contacto-lead {ejes['lead']}")
        print(f"       tokens: cierre {ejes['tokenCierre']!r} · shell {ejes['tokenShell']!r} "
              f"· cartel {ejes['tokenCartel']!r}")
        comprobar('"opsz" 144' in ejes["lead"] and '"wght" 300' in ejes["lead"],
                  f"la frase usa opsz 144 / wght 300, el eje de cierre ({ejes['lead']})")
        comprobar('"wght" 900' not in ejes["lead"],
                  f"la frase NO se queda en la voz de cabecera (wght 900) ({ejes['lead']})")
        comprobar(
            ejes["tokenCierre"] not in ("", ejes["tokenShell"], ejes["tokenCartel"]),
            "--cae-display-axes-cierre es un token propio, distinto de shell y cartel",
        )
        ctx.close()

        # ================================================================
        # [3] La ocupacion, medida con Range
        # ================================================================
        print("\n[3] La ocupacion del titular, medida con Range (no con la caja de bloque)")
        ctx, pg, err = nueva_pagina_en_contacto(navegador, base)
        errores_totales += err
        ocupacion = pg.evaluate("""() => {
            const lead = document.querySelector('.contacto-lead');
            const troquel = document.querySelector('[data-fundido-troquel]');
            const lineas = [...document.querySelectorAll('.cae-fundido-linea')];
            const anchoBloque = Math.round(lead.getBoundingClientRect().width);
            // El extremo derecho REAL del texto, con Range: la caja de bloque
            // de `lead` YA viene encogida a su contenido (`.contacto-band` usa
            // `align-items: flex-start`, no `stretch`), asi que comparar el
            // bloque CONTRA SI MISMO da 0 px muertos SIEMPRE, sea cual sea el
            // texto — es la propia trampa que el spec describe: mide algo,
            // pero no la ocupacion. La comparacion que si dice algo es contra
            // el HUECO real disponible hasta el troquel, medido con Range.
            let anchoTexto = 0;
            for (const linea of lineas) {
                const r = document.createRange();
                r.selectNodeContents(linea);
                anchoTexto = Math.max(anchoTexto, r.getBoundingClientRect().width);
            }
            const leadRect = lead.getBoundingClientRect();
            const troquelRect = troquel.getBoundingClientRect();
            const hueco = Math.round(troquelRect.left - leadRect.left);
            return {
                anchoBloque, anchoTexto: Math.round(anchoTexto), hueco,
                lineas: lineas.length,
            };
        }""")
        print(f"       ancho de bloque (encogido a su contenido) {ocupacion['anchoBloque']} · "
              f"ancho de texto (Range) {ocupacion['anchoTexto']} · hueco hasta el troquel "
              f"{ocupacion['hueco']} · lineas {ocupacion['lineas']}")
        comprobar(ocupacion["lineas"] >= 1, f"el titular se parte en lineas trazables ({ocupacion['lineas']})")
        # La trampa que este gate esquiva, IMPRESA y no aseverada: comparar el
        # bloque contra si mismo da 0 px muertos siempre, por construccion. Era
        # un `comprobar()` y se quito — una asercion que no puede ponerse roja
        # engorda la cuenta de verdes sin vigilar nada, que es exactamente el
        # instrumento tautologico que esta pista lleva nueve veces pagando. El
        # gate real compara contra el HUECO hasta el troquel, no contra la caja.
        print(f"       (la trampa, para el lector: bloque contra si mismo = "
              f"{ocupacion['anchoBloque'] - ocupacion['anchoBloque']}px muertos, siempre)")
        muerto = ocupacion["hueco"] - ocupacion["anchoTexto"]
        print(f"       espacio muerto real (hueco - texto por Range): {muerto}px")
        # El texto ocupa la mayor parte del hueco (no flota diminuto en el
        # campo de color) pero deja un margen real antes del troquel — ni 0
        # (invadiria el troquel) ni la mayoria del hueco (flotaria perdido).
        comprobar(ocupacion["anchoTexto"] < ocupacion["hueco"],
                  f"el texto no invade el troquel ({ocupacion['anchoTexto']} < {ocupacion['hueco']})")
        comprobar(100 <= muerto <= 250,
                  f"hay un margen real y acotado antes del troquel, medido con Range ({muerto}px)")
        ctx.close()

        # ================================================================
        # [4] Sin scroll interno, en 1440 y en 390
        # ================================================================
        print("\n[4] Sin scroll interno, en 1440 y en 390")
        # `scrollHeight` NO sirve de instrumento aqui: el campo de color crece
        # por `transform: scale(...)`, y ese desbordamiento por transform sigue
        # contando en `scrollHeight` incluso con `overflow: clip` puesto (medido:
        # 1813 contra un `clientHeight` de 748, con el `overflow: clip` de la
        # Task 6 ya aplicado) — es un dato real del motor de layout, no un
        # sintoma de que la escena sea desplazable. Lo que de verdad importa —
        # y lo que Task 6 verifico con Playwright — es si el contenedor
        # RESPONDE a un scroll programatico. Se intenta desplazar y se
        # comprueba si se movio.
        for ancho, alto in ((1440, 900), (390, 844)):
            ctx, pg, err = nueva_pagina_en_contacto(navegador, base, viewport={"width": ancho, "height": alto})
            errores_totales += err
            desborde = pg.evaluate("""() => {
                const sc = document.querySelector('[data-scene="contacto"]');
                const ventana = sc.closest('main[data-cae-track] > *');
                const antes = { top: ventana.scrollTop, left: ventana.scrollLeft };
                ventana.scrollTop = 600;
                ventana.scrollLeft = 600;
                const despues = { top: ventana.scrollTop, left: ventana.scrollLeft };
                ventana.scrollTop = antes.top;
                ventana.scrollLeft = antes.left;
                return {
                    canScrollV: despues.top !== 0, canScrollH: despues.left !== 0,
                    scrollWidthDoc: document.documentElement.scrollWidth,
                    clientWidthDoc: document.documentElement.clientWidth,
                };
            }""")
            print(f"       {ancho}px: canScrollV {desborde['canScrollV']} · canScrollH "
                  f"{desborde['canScrollH']} · doc scrollWidth {desborde['scrollWidthDoc']} / "
                  f"clientWidth {desborde['clientWidthDoc']}")
            comprobar(not desborde["canScrollV"], f"la ventana no se desplaza en vertical a {ancho}px")
            comprobar(not desborde["canScrollH"], f"la ventana no se desplaza en horizontal a {ancho}px")
            comprobar(desborde["scrollWidthDoc"] - desborde["clientWidthDoc"] <= 1,
                      f"sin barra horizontal a nivel de documento a {ancho}px "
                      f"({desborde['scrollWidthDoc']} vs {desborde['clientWidthDoc']})")
            ctx.close()

        # ================================================================
        # [5] Los cuatro canales siguen accionables
        # ================================================================
        print("\n[5] Los cuatro canales: mailto/tel bien formados, externos con rel completo")
        ctx, pg, err = nueva_pagina_en_contacto(navegador, base)
        errores_totales += err
        canales = pg.evaluate("""() => [...document.querySelectorAll('.contacto-bar')].map((a) => ({
            canal: a.dataset.canal, href: a.getAttribute('href'),
            target: a.getAttribute('target'), rel: a.getAttribute('rel'),
        }))""")
        print(f"       {canales}")
        comprobar(len(canales) == 4, f"hay cuatro canales en el DOM ({len(canales)})")
        mailto = next((c for c in canales if c["href"].startswith("mailto:")), None)
        comprobar(mailto is not None and re.match(r"^mailto:[^\s@]+@[^\s@]+\.[^\s@]+$", mailto["href"]),
                  f"el mailto: esta bien formado ({mailto and mailto['href']})")
        tel = next((c for c in canales if c["href"].startswith("tel:")), None)
        comprobar(tel is not None and re.match(r"^tel:\+?\d+$", tel["href"]),
                  f"el tel: no lleva espacios ni guiones ({tel and tel['href']})")
        externos = [c for c in canales if c["target"] == "_blank"]
        comprobar(len(externos) == 2, f"hay dos canales externos ({len(externos)})")
        for c in externos:
            rel = (c["rel"] or "").split()
            # Los dos externos son los dos `destino`: sin el href, las dos
            # etiquetas salian identicas y un fallo no decia cual de los dos era.
            comprobar("noopener" in rel and "noreferrer" in rel,
                      f"el destino {c['href']} lleva las dos palabras de rel ({c['rel']!r})")
        ctx.close()

        # ================================================================
        # [6] El dato se lee sin hover
        # ================================================================
        print("\n[6] El dato se lee SIN hover")
        # No se simula nada: un MouseEvent sintetico NO dispara `:hover`, asi
        # que una prueba que lo simule mide su propia simulacion. Se lee y ya.
        ctx, pg, err = nueva_pagina_en_contacto(navegador, base)
        errores_totales += err
        visibles = pg.evaluate("""() => [...document.querySelectorAll(
            '[data-scene="contacto"] .contacto-bar-value')].filter(v => {
                const cs = getComputedStyle(v);
                return v.textContent.trim().length > 0 && cs.visibility !== 'hidden'
                    && cs.display !== 'none' && parseFloat(cs.opacity) > 0.05;
            }).length""")
        comprobar(visibles == 4, f"los cuatro datos se leen sin hover ({visibles}/4)")
        ctx.close()

        # ================================================================
        # [7] Contraste AA, en los dos esquemas, solo lo que se pinta de verdad
        # ================================================================
        print("\n[7] Contraste AA en los dos esquemas (pares que se pintan de verdad)")
        # No se inventa una API para forzar la hora: el motor de color lee
        # `new Date().getHours()`, asi que el esquema se cambia con la ZONA
        # HORARIA del contexto de Playwright — real, sin tocar produccion.
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

        # Gate 7 · contraste: SOLO LOS PARES QUE SE PINTAN DE VERDAD.
        #
        # Vigilar los roles `on-X` contra `X` en abstracto es lo que dejo al reloj
        # de la fase A bajo AA cuatro horas al dia con el arnes en verde. Y dos
        # pares que NO se miden, a proposito:
        #   · las nubes (2,19:1) son decorado, y WCAG exime el decorado;
        #   · el ojo de dia NO EXISTE — de dia el ojo es el hueco, en
        #     `--cae-surface`, no en `--cae-anchor`. Medirlo es medir un par que
        #     nunca se pinta.
        PARES = [
            ("la frase", ".contacto-lead", '[data-scene="contacto"]'),
            ("valor del acto", '[data-canal="acto"] .contacto-bar-value', '[data-scene="contacto"]'),
            ("rotulo del acto", '[data-canal="acto"] .contacto-bar-label', '[data-scene="contacto"]'),
            ("el estado", ".contacto-estado", '[data-scene="contacto"]'),
        ]

        peor, peor_etiqueta = 21.0, ""
        esquemas_vistos: list[str] = []
        for zona in (z for z in (zona_dia, zona_noche) if z):
            ctx, pg, err = nueva_pagina_en_contacto(navegador, base, timezone_id=zona)
            errores_totales += err
            esquema = pg.evaluate("() => document.documentElement.dataset.caeEsquema")
            esquemas_vistos.append(esquema)
            hora = pg.evaluate("() => new Date().getHours() + ':' + new Date().getMinutes()")
            for etiqueta, selector, _contenedor in PARES:
                medida = pg.evaluate(CONTRASTE_JS, {"sel": selector, "pseudo": None})
                comprobar(medida is not None,
                          f"se pudo medir {etiqueta} en esquema {esquema} ({selector})")
                if medida is None:
                    continue
                print(f"       {etiqueta}: {medida['ratio']:.2f}:1 en esquema {esquema}")
                if medida["ratio"] < peor:
                    peor, peor_etiqueta = medida["ratio"], f"{etiqueta} en esquema {esquema}"
            print(f"       {zona} (hora local {hora}): esquema {esquema}")
            ctx.close()
        comprobar(len(set(esquemas_vistos)) == 2,
                  f"se han visto los DOS esquemas ({esquemas_vistos})")
        print(f"       peor par: {peor:.2f}:1 ({peor_etiqueta})")
        comprobar(peor >= 4.5, f"contraste >= 4.5:1 en los dos esquemas ({peor:.2f}:1, {peor_etiqueta})")

        # ================================================================
        # [8] El fundido suena una vez; la entrada, todas
        # ================================================================
        print("\n[8] El fundido suena una vez; la entrada, todas")
        # Discriminador robusto y SIN depender de la cadencia de frames de este
        # entorno (el `requestAnimationFrame`/`setTimeout` de este sandbox
        # dispara de forma muy irregular con `--use-gl=swiftshader`, medido:
        # intervalos de 200-400ms en vez de los 16ms de un frame — un
        # cronometro por frames aqui mide el jitter de la maquina, no la
        # coreografia). GSAP renderiza el valor DE ARRANQUE de cada tween de
        # una timeline de forma SINCRONA en cuanto la timeline se crea y se
        # reproduce, sin esperar a ningun frame — asi que basta leer el estilo
        # computado EN LA MISMA VUELTA DE `evaluate()` que dispara el clic,
        # sin ningun `wait`, para ver el primer fotograma real:
        #
        #   reproducir(): `tl.fromTo(troquel, {scale:0}, ...)`      -> 0
        #   entrar():     `tlEntrada.fromTo(troquel, {scale:0.965}, ...)` -> 0.965
        #   nada:         el troquel se queda en su valor aterrizado -> 1
        #
        # Medido en la construccion de este arnes: los tres valores salen
        # exactamente `matrix(0,...)`, `matrix(0.965,...)` y sin cambio,
        # respectivamente — ver el informe.
        def escala_troquel(matriz: str) -> float:
            numeros = re.findall(r"-?[\d.]+", matriz)
            return float(numeros[0]) if numeros else -1.0

        CLIC_Y_LEER_JS = (
            "() => { document.querySelector('[data-cae-ws=\"contacto\"]').click();"
            " return getComputedStyle(document.querySelector('[data-fundido-troquel]')).transform; }"
        )

        ctx, pg, err = nueva_pagina_en_contacto(navegador, base)
        errores_totales += err
        # Ya aterrizado (primera visita, fundido completo ya jugado por
        # `nueva_pagina_en_contacto`: la escala esta en 1).
        antes = escala_troquel(pg.evaluate(
            "() => getComputedStyle(document.querySelector('[data-fundido-troquel]')).transform"
        ))
        # Pulsar la pastilla YA ACTIVA:
        tras_repulso = escala_troquel(pg.evaluate(CLIC_Y_LEER_JS))
        print(f"       escala del troquel: aterrizada {antes} · justo tras repulsar {tras_repulso}")
        comprobar(abs(tras_repulso - antes) < 0.01,
                  f"pulsar el workspace activo no dispara nada (escala {antes} -> {tras_repulso})")

        # Volver desde el workspace 4 ("creditos"): dispara SOLO la entrada.
        pg.click('[data-cae-ws="creditos"]')
        pg.wait_for_timeout(900)
        tras_volver = escala_troquel(pg.evaluate(CLIC_Y_LEER_JS))
        print(f"       escala del troquel justo tras volver desde «creditos»: {tras_volver} "
              f"(entrar() arranca en 0.965; reproducir() arrancaria en 0)")
        comprobar(0.9 <= tras_volver <= 1.0,
                  f"volver desde el 4 dispara la ENTRADA (arranca en ~0.965), no el fundido completo "
                  f"(arrancaria en 0) — medido {tras_volver}")
        pg.wait_for_timeout(900)
        ctx.close()

        # ================================================================
        # [9] La entrada cabe dentro del deslizamiento del carril
        # ================================================================
        print("\n[9] La entrada (440ms) cabe dentro del deslizamiento del carril (520ms)")
        fundido_src = (RAIZ / "src" / "themes" / "caelestia.fundido.ts").read_text(encoding="utf-8")
        choreo_src = (RAIZ / "src" / "themes" / "caelestia.choreography.ts").read_text(encoding="utf-8")
        m_entrada = re.search(r"ENTRADA_MS\s*=\s*([\d.]+)", fundido_src)
        m_duracion = re.search(r"DURACION\s*=\s*([\d.]+)", choreo_src)
        comprobar(m_entrada is not None, "ENTRADA_MS se encuentra en caelestia.fundido.ts")
        comprobar(m_duracion is not None, "DURACION se encuentra en caelestia.choreography.ts")
        if m_entrada and m_duracion:
            entrada_ms = float(m_entrada.group(1))
            duracion_ms = float(m_duracion.group(1)) * 1000
            print(f"       ENTRADA_MS = {entrada_ms} · DURACION del carril = {duracion_ms}")
            comprobar(entrada_ms < duracion_ms,
                      f"la entrada cabe dentro del deslizamiento ({entrada_ms} < {duracion_ms})")

        # ================================================================
        # [10] prefers-reduced-motion aterriza la escena en 0 ms
        # ================================================================
        print("\n[10] Movimiento reducido: la escena aterriza sin recorrido")
        # OJO: NO se usa `nueva_pagina_en_contacto` aqui -- su espera de 2600ms
        # tras el clic es mas larga que el fundido completo (1900ms), asi que
        # si la guarda `if (reduce) return` desapareciera la timeline habria
        # tenido tiempo de sobra para terminar SOLA y aterrizar igual, dejando
        # este gate en verde aunque la guarda no exista. Se mide a 200ms, a
        # mitad de un fundido de 1900ms si es que llegara a correr -- la misma
        # ventana que uso la Task 7 para ver esto en rojo.
        ctx = navegador.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        pg = ctx.new_page()
        errores: list[str] = []
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(3000)
        pg.click('[data-cae-ws="contacto"]')
        pg.wait_for_timeout(200)
        errores_totales += errores
        reducido = pg.evaluate("""() => {
            const troquel = document.querySelector('[data-fundido-troquel]');
            const linea = document.querySelector('.cae-fundido-linea');
            const acto = document.querySelector('[data-canal="acto"]');
            const suelo = document.querySelector('[data-fundido-suelo]');
            const nube = document.querySelector('.cae-fundido-nube');
            const oculto = (el) => /100(\\.0+)?%/.test(getComputedStyle(el).clipPath) ? 1 : 0;
            return {
                fraseOculta: linea ? oculto(linea) : null,
                actoOculto: acto ? oculto(acto) : null,
                troquelTransform: troquel ? getComputedStyle(troquel).transform : null,
                sueloTransform: suelo ? getComputedStyle(suelo).transform : null,
                nubeOpacidad: nube ? getComputedStyle(nube).opacity : null,
            };
        }""")
        print(f"       {reducido}")
        comprobar(reducido["fraseOculta"] == 0, f"la frase esta puesta, no oculta ({reducido['fraseOculta']})")
        comprobar(reducido["actoOculto"] == 0, f"el acto esta puesto, no oculto ({reducido['actoOculto']})")
        # Comparar la matriz ENTERA contra el literal "matrix(0, 0, 0, 0, 0, 0)"
        # es una asercion que no puede fallar donde de verdad importa: el
        # troquel lleva `transform: translateY(-50%)` en su CSS base, asi que
        # su matriz en reposo YA trae un componente de traslacion (`-230` en
        # 1440px) — un `scale(0)` sobre eso da `matrix(0, 0, 0, 0, 0, -230)`,
        # que el string exacto de arriba no cazaba (visto en rojo al construir
        # este gate: con la guarda de reduced-motion saboteada, esa comparacion
        # devolvia "OK" con el troquel invisible de verdad). Se lee el
        # componente `a` de la matriz (la escala X), que es 0 solo si de verdad
        # esta encogido a la nada.
        m = re.findall(r"-?[\d.]+", reducido["troquelTransform"] or "")
        escala_troquel_reducido = float(m[0]) if m else -1.0
        comprobar(escala_troquel_reducido > 0.5,
                  f"el troquel esta de pie, no en scale(0) "
                  f"({reducido['troquelTransform']}, escala {escala_troquel_reducido})")
        comprobar(reducido["nubeOpacidad"] == "1", f"las nubes estan puestas ({reducido['nubeOpacidad']})")
        ctx.close()

        # ================================================================
        # [11] 390 px
        # ================================================================
        print("\n[11] 390 px: paso exacto, ocupacion, blancos >= 48x48, sello cuadrado")
        ctx, pg, err = nueva_pagina_en_contacto(navegador, base, viewport={"width": 390, "height": 844})
        errores_totales += err
        movil = pg.evaluate("""() => {
            const lead = document.querySelector('.contacto-lead');
            const troquel = document.querySelector('[data-fundido-troquel]');
            const bars = [...document.querySelectorAll('.contacto-bar')];
            const lineas = [...document.querySelectorAll('.cae-fundido-linea')];
            let anchoTexto = 0;
            for (const linea of lineas) {
                const r = document.createRange();
                r.selectNodeContents(linea);
                anchoTexto = Math.max(anchoTexto, r.getBoundingClientRect().width);
            }
            const tr = troquel.getBoundingClientRect();
            return {
                fontSize: parseFloat(getComputedStyle(lead).fontSize),
                anchoTexto: Math.round(anchoTexto),
                anchoUtil: Math.round(lead.getBoundingClientRect().width),
                troquelW: Math.round(tr.width), troquelH: Math.round(tr.height),
                troquelLeft: Math.round(tr.left), troquelRight: Math.round(tr.right),
                blancos: bars.map((b) => {
                    const r = b.getBoundingClientRect();
                    return { w: Math.round(r.width), h: Math.round(r.height) };
                }),
                anchoViewport: window.innerWidth,
                scrollDoc: document.documentElement.scrollWidth,
            };
        }""")
        print(f"       titular {movil['fontSize']}px · texto (Range) {movil['anchoTexto']} "
              f"sobre util {movil['anchoUtil']}")
        print(f"       troquel {movil['troquelW']}x{movil['troquelH']} "
              f"[{movil['troquelLeft']}, {movil['troquelRight']}] sobre viewport {movil['anchoViewport']}")
        print(f"       blancos: {movil['blancos']}")
        # --t-7 (67.4px), no --t-8: es el paso que de verdad cabe, medido con
        # Range sobre el build — --t-8 se sale 32px de la medida util (ver el
        # comentario en `themes.css`, junto a esta misma regla).
        comprobar(abs(movil["fontSize"] - 67.4) < 0.5,
                  f"el titular esta en su paso exacto a 390px, --t-7 (67.4px, medido {movil['fontSize']})")
        comprobar(movil["anchoTexto"] <= movil["anchoUtil"],
                  f"la linea mas larga cabe en la medida util ({movil['anchoTexto']} <= {movil['anchoUtil']})")
        comprobar(all(b["w"] >= 48 and b["h"] >= 48 for b in movil["blancos"]),
                  f"ningun blanco baja de 48x48 ({movil['blancos']})")
        comprobar(abs(movil["troquelW"] - movil["troquelH"]) <= 1,
                  f"el sello es cuadrado ({movil['troquelW']}x{movil['troquelH']})")
        comprobar(movil["troquelLeft"] >= 0 and movil["troquelRight"] <= movil["anchoViewport"],
                  f"el sello no sangra a 390px ([{movil['troquelLeft']}, {movil['troquelRight']}] "
                  f"dentro de [0, {movil['anchoViewport']}])")
        comprobar(movil["scrollDoc"] <= movil["anchoViewport"],
                  f"sin barra horizontal a 390px (scrollWidth {movil['scrollDoc']} <= "
                  f"viewport {movil['anchoViewport']})")
        ctx.close()

        # ================================================================
        # [12] Vice y Hyprland no se alteran
        # ================================================================
        print("\n[12] Vice y Hyprland no se alteran: contacto.ts es compartido")
        for tema in ("vice", "hyprland"):
            ctx = navegador.new_context(viewport={"width": 1440, "height": 900})
            errores: list[str] = []
            pg = ctx.new_page()
            pg.on("pageerror", lambda e: errores.append(str(e)))
            pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
            pg.goto(f"{base}/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(2500)
            comprobar(pg.locator('[data-scene="contacto"]').count() == 1,
                      f"la escena de contacto sigue existiendo en {tema}")
            fuga = pg.evaluate("""() => {
                const sc = document.querySelector('[data-scene="contacto"]');
                const lead = sc && sc.querySelector('.contacto-lead');
                const estadoLabel = sc && sc.querySelector('.contacto-estado-label');
                return {
                    troquel: !!sc.querySelector('.cae-fundido-troquel'),
                    campo: !!sc.querySelector('.cae-fundido-campo'),
                    corn: !!sc.querySelector('.cae-fundido-corn'),
                    bicho: !!sc.querySelector('.cae-fundido-bicho'),
                    leadEjes: lead ? getComputedStyle(lead).fontVariationSettings : null,
                    leadFontSize: lead ? parseFloat(getComputedStyle(lead).fontSize) : null,
                    // `.hero-kick`/`.contacto-estado-label`/`.contacto-estado-sep`
                    // se apagan en Caelestia (`display: none`) porque ahi el
                    // rotulo de seccion lo lleva la esquina y el estado baja al
                    // pie -- pero en Vice y Hyprland esa etiqueta SI se ve
                    // (tienen su propia regla de color para ella, sin tocar
                    // `display`). Si la regla de Caelestia perdiera su guarda de
                    // tema, este es el selector COMPARTIDO por el que se cuela:
                    // ni el troquel ni el `fontVariationSettings` lo detectan
                    // (el custom property de los ejes no resuelve fuera de su
                    // scope, y el resto de selectores compartidos ya tienen su
                    // propio override de mayor o igual especificidad en cada
                    // tema) -- pero `display: none` no tiene competencia en
                    // ninguno de los dos temas y SI se cuela. Visto en rojo al
                    // construir este gate (Task 8): las dos etiquetas
                    // desaparecian con solo quitar `[data-theme="caelestia"]`
                    // de esa regla.
                    estadoLabelDisplay: estadoLabel ? getComputedStyle(estadoLabel).display : null,
                };
            }""")
            print(f"       {tema}: {fuga}")
            comprobar(not (fuga["troquel"] or fuga["campo"] or fuga["corn"] or fuga["bicho"]),
                      f"ningun elemento de Caelestia (troquel/campo/corn/bicho) se monta en {tema}")
            comprobar(fuga["estadoLabelDisplay"] != "none",
                      f"el rotulo «Estado» de {tema} sigue visible, no apagado por la regla de "
                      f"Caelestia ({fuga['estadoLabelDisplay']})")
            if fuga["leadEjes"] is not None:
                comprobar('"opsz" 144' not in fuga["leadEjes"],
                          f"la voz de cierre de Caelestia no se cuela en {tema} ({fuga['leadEjes']})")
            errores_totales += errores
            ctx.close()

        # ================================================================
        # [13] El fundido interrumpido aterriza del todo
        # ================================================================
        print("\n[13] El fundido interrumpido aterriza del todo (ida y vuelta a media pasada)")
        # El camino que ningun gate miraba: irse de «contacto» ANTES de que los
        # 1900 ms del fundido acaben. `entrar()` mata la timeline y llama a
        # `aterrizado()`, asi que todo lo que la partitura toca y `aterrizado()`
        # no devuelva se queda CONGELADO donde lo mato el `kill()` — para el
        # resto de la visita, porque `fundidoVisto` ya es `true` y el fundido no
        # vuelve a sonar. Medido en rojo contra el codigo anterior a este gate:
        # el bicho en `translateX(-105px)` (medio fuera del sello), la nube en
        # `opacity: 0` y el suelo en `scaleX: 0.91`.
        #
        # Y la zancada: `pararZancada()` es el `onComplete` del tween del bicho,
        # y `kill()` NO dispara `onComplete` — el reloj de fotogramas se queda
        # encendido y el dino corre en el sitio para siempre.
        #
        # TODA la orquestacion va DENTRO de la pagina (un `async` con
        # `setTimeout`), nunca con esperas desde fuera: el puente de Playwright
        # mete 100-300 ms de ida y vuelta por llamada, que es justo el orden de
        # magnitud de los cortes que este gate tiene que hacer (250 ms y 400 ms).
        # Con `page.click()` + `wait_for_timeout()` no se estaria cortando donde
        # se cree — ese instrumento ya mintio una vez en esta fase.
        #
        # Se corta DOS veces, en dos paginas frescas, porque la partitura no es
        # homogenea: a 250 ms el bicho todavia entra y la nube no ha salido; el
        # tween de los ejes del titular no arranca hasta 520 ms y no acaba hasta
        # 1300, asi que un corte a 250 no puede dejar un `wght` intermedio en
        # linea y esa asercion no podria ponerse roja nunca. El corte a 900 ms la
        # pone roja de verdad. Un solo corte era un gate a medias.
        #
        # El corte NO se cronometra: se ANCLA AL ESTADO. Medido en esta maquina,
        # `setTimeout` dentro de la pagina con `--use-gl=swiftshader` llega con
        # cientos de ms de retraso y de forma irregular, asi que un `dormir(250)`
        # cortaba unas veces con el bicho a media entrada y otras con el fundido
        # practicamente acabado: el mismo gate salia rojo bajo carga y verde en
        # vacio. Es el instrumento, no el diseno — la trampa que esta pista ya ha
        # pagado once veces. Aqui se mira cada frame hasta que la escena esta de
        # verdad en el punto que se quiere cortar, y si ese punto NUNCA llega, el
        # gate FALLA en vez de medir otra cosa.
        #
        #   corte «bicho»: el dino a media entrada (translateX entre -260 y -20)
        #   corte «ejes»:  el titular con un `wght` intermedio en linea (<850)
        INTERRUMPE_JS = r"""async (corte) => {
            const frame = () => new Promise(r => requestAnimationFrame(r));
            const dormir = ms => new Promise(r => setTimeout(r, ms));
            const q = s => document.querySelector(s);
            const pulsa = id => q(`[data-cae-ws="${id}"]`).click();
            const tr = s => { const e = q(s); return e ? getComputedStyle(e).transform : null; };
            // `matrix(a, b, c, d, e, f)`: 0 es la escala en X, 4 el desplazamiento.
            const val = (sel, i, sinTransform) => {
                const m = tr(sel);
                if (!m || m === 'none') return sinTransform;
                const n = m.match(/-?[\d.]+/g);
                return n ? parseFloat(n[i]) : NaN;
            };
            const pesoEnLinea = () => {
                const v = q('[data-fundido-lead]').style.fontVariationSettings;
                const m = v && v.match(/"wght"\s+(\d+)/);
                return m ? parseFloat(m[1]) : null;
            };
            const enElPunto = corte === 'bicho'
                ? () => { const x = val('.cae-fundido-bicho', 4, 0); return x < -20 && x > -260; }
                : () => { const w = pesoEnLinea(); return w !== null && w < 850; };

            pulsa('contacto');
            let llego = false;
            const t0 = performance.now();
            while (performance.now() - t0 < 6000) {
                if (enElPunto()) { llego = true; break; }
                await frame();
            }
            pulsa('creditos');
            await dormir(400);
            pulsa('contacto');   // vuelve: entrar(), no reproducir()
            await dormir(1600);  // de sobra para que la entrada (440ms) acabe

            // La zancada, si sigue corriendo, cambia el dibujo del cuerpo cada
            // 85 ms: se mira el LARGO del marcado en reposo durante ~1,8 s.
            const cuerpo = q('.cae-fundido-bicho [data-dino-cuerpo]');
            const dibujos = new Set();
            for (let i = 0; i < 40; i++) {
                dibujos.add(cuerpo ? cuerpo.innerHTML.length : -1);
                await dormir(45);
            }
            return {
                llegoAlPuntoDeCorte: llego,
                bichoX:  val('.cae-fundido-bicho', 4, 0),
                sueloX:  val('[data-fundido-suelo]', 0, 1),
                troquel: val('[data-fundido-troquel]', 0, 1),
                campo:   val('.cae-fundido-campo', 0, 1),
                escenaX: val('[data-scene="contacto"]', 4, 0),
                nubeOp:  parseFloat(getComputedStyle(q('.cae-fundido-nube')).opacity),
                ejesEnLinea: q('[data-fundido-lead]').style.fontVariationSettings,
                dibujosDistintos: dibujos.size,
            };
        }"""

        for corte in ("bicho", "ejes"):
            ctx = navegador.new_context(viewport={"width": 1440, "height": 900})
            errores: list[str] = []
            pg = ctx.new_page()
            pg.on("pageerror", lambda e: errores.append(str(e)))
            pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
            pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(3000)
            d = pg.evaluate(INTERRUMPE_JS, corte)
            print(f"       --- corte «{corte}» ---")
            for k, v in d.items():
                print(f"       {k}: {v}")
            comprobar(d["llegoAlPuntoDeCorte"],
                      f"[{corte}] la escena llego al punto de corte: se interrumpe donde se cree "
                      f"y no en otro sitio")
            comprobar(abs(d["bichoX"]) < 1.0,
                      f"[{corte}] el bicho vuelve a su sitio dentro del sello "
                      f"(translateX {d['bichoX']}, se espera 0)")
            comprobar(d["nubeOp"] > 0.99,
                      f"[{corte}] la nube queda visible (opacity {d['nubeOp']}, se espera 1)")
            comprobar(abs(d["sueloX"] - 1) < 0.01,
                      f"[{corte}] el horizonte queda a su trazo entero "
                      f"(scaleX {d['sueloX']}, se espera 1)")
            comprobar(abs(d["troquel"] - 1) < 0.01,
                      f"[{corte}] el troquel queda a escala 1 (medido {d['troquel']})")
            comprobar(abs(d["campo"] - 1) < 0.01,
                      f"[{corte}] el campo de color queda a escala 1, sin tapar la escena "
                      f"(medido {d['campo']})")
            comprobar(abs(d["escenaX"]) < 1.0,
                      f"[{corte}] la escena queda en su sitio (translateX {d['escenaX']}, se espera 0)")
            comprobar(d["ejesEnLinea"] == "",
                      f"[{corte}] el eje variable en linea del titular se retira: lo escribe el "
                      f"`onUpdate` en `style`, asi que `clearProps` no lo alcanza "
                      f"(medido «{d['ejesEnLinea']}»)")
            comprobar(d["dibujosDistintos"] == 1,
                      f"[{corte}] la zancada esta parada en reposo: un solo dibujo del cuerpo "
                      f"en 1,8 s (medidos {d['dibujosDistintos']})")
            errores_totales += errores
            ctx.close()

        # ================================================================
        # [14] Rozar responde, y el teclado llega a lo mismo
        # ================================================================
        print("\n[14] Rozar responde, y el teclado llega a lo mismo")
        # `vera-art-director` lo levanto como P1 y era cierto: Caelestia era la
        # unica de las tres pieles cuya llamada a la accion principal no
        # reaccionaba al raton — `background`, `color`, `transform` y
        # `text-decoration` identicos antes y despues, y el unico cambio el
        # `cursor: pointer` del navegador.
        #
        # Con `hover()` DE VERDAD, nunca un `MouseEvent` sintetico: no dispara
        # `:hover`. Trampa ya pagada en B2 y en B4.
        LEE_ESTADO_JS = """(sel) => {
            const a = document.querySelector(sel);
            const et = a.querySelector('.contacto-bar-label');
            const v = a.querySelector('.contacto-bar-value');
            return {
                fondo: getComputedStyle(a).backgroundColor,
                rotuloOp: parseFloat(getComputedStyle(et).opacity),
                valorColor: getComputedStyle(v).color,
                enfocado: document.activeElement === a,
            };
        }"""
        # `rgba(..., 0)` y `transparent` son el mismo pixel: no pinta nada.
        def pinta(color: str) -> bool:
            n = re.findall(r"[\d.]+", color or "")
            if color in (None, "", "transparent"):
                return False
            return len(n) < 4 or float(n[3]) > 0.01

        ctx, pg, err = nueva_pagina_en_contacto(navegador, base)
        errores_totales += err
        # Cada barra se marca con un atributo propio y se apunta a el: el
        # colofon reordena con `order`, asi que `nth-of-type` no dice lo mismo
        # que el orden que se ve.
        cuantas = pg.evaluate("""() => {
            const bs = [...document.querySelectorAll('.contacto-bar')];
            bs.forEach((a, i) => a.setAttribute('data-medida', String(i)));
            return bs.length;
        }""")
        canales_sel = [f'[data-medida="{i}"]' for i in range(cuantas)]

        for sel in canales_sel:
            reposo = pg.evaluate(LEE_ESTADO_JS, sel)
            pg.hover(sel)
            pg.wait_for_timeout(400)   # la capa de estado funde en 180 ms
            rozado = pg.evaluate(LEE_ESTADO_JS, sel)
            # Se despega el raton para no contaminar la barra siguiente.
            pg.mouse.move(2, 2)
            pg.wait_for_timeout(300)
            print(f"       {sel}: fondo {reposo['fondo']} -> {rozado['fondo']} · "
                  f"rotulo {reposo['rotuloOp']} -> {rozado['rotuloOp']}")
            comprobar(not pinta(reposo["fondo"]),
                      f"{sel} no pinta caja en reposo ({reposo['fondo']})")
            comprobar(pinta(rozado["fondo"]),
                      f"{sel} PINTA su caja accionable al rozar ({rozado['fondo']}) — el P1 de "
                      f"`vera-art-director`: era la unica piel sin respuesta al raton")
            comprobar(rozado["rotuloOp"] > reposo["rotuloOp"] + 0.05,
                      f"{sel} enciende su rotulo al rozar ({reposo['rotuloOp']} -> "
                      f"{rozado['rotuloOp']})")
            # El contraste del dato NO puede caer de AA por la capa de estado:
            # se mide sobre el fondo que de verdad se pinta debajo, ya rozado.
            pg.hover(sel)
            pg.wait_for_timeout(400)
            c = pg.evaluate(CONTRASTE_JS, {"sel": f"{sel} .contacto-bar-value", "pseudo": None})
            print(f"       {sel} rozado: contraste del dato {c['ratio']:.2f}:1")
            comprobar(c["ratio"] >= 4.5,
                      f"{sel} mantiene AA con la capa de estado puesta ({c['ratio']:.2f}:1)")
            pg.mouse.move(2, 2)
            pg.wait_for_timeout(300)

        # El teclado llega a LO MISMO. Con `Tab` de verdad, no `el.focus()`:
        # `:focus-visible` depende de como se llego al elemento.
        alcanzados = 0
        for _ in range(40):
            pg.keyboard.press("Tab")
            # La capa de estado funde en 180 ms: leer en el mismo instante del
            # `Tab` devuelve el fotograma de arranque, con alfa ~0, y el gate
            # acusa al CSS de un fallo que es del cronometro. Visto: la barra 1
            # daba `oklab(0 0 0 / 0)` —el valor a mitad de transicion— mientras
            # las otras tres, leidas mas tarde por el bucle, daban la capa ya
            # puesta.
            pg.wait_for_timeout(400)
            est = pg.evaluate("""() => {
                const a = document.activeElement;
                if (!a || !a.classList || !a.classList.contains('contacto-bar')) return null;
                const et = a.querySelector('.contacto-bar-label');
                return {
                    sel: a.getAttribute('data-medida'),
                    fondo: getComputedStyle(a).backgroundColor,
                    rotuloOp: parseFloat(getComputedStyle(et).opacity),
                };
            }""")
            if est is None:
                continue
            alcanzados += 1
            print(f"       teclado -> barra {est['sel']}: fondo {est['fondo']} · "
                  f"rotulo {est['rotuloOp']}")
            comprobar(pinta(est["fondo"]),
                      f"la barra {est['sel']} pinta la MISMA caja con el foco de teclado "
                      f"({est['fondo']}) — raton y teclado no pueden divergir")
            if alcanzados == len(canales_sel):
                break
        comprobar(alcanzados == len(canales_sel),
                  f"el tabulador alcanza los cuatro canales ({alcanzados} de {len(canales_sel)})")
        ctx.close()

        # ================================================================
        # Consola limpia en todas las paginas abiertas
        # ================================================================
        comprobar(not errores_totales, f"consola sin errores en ninguna pagina ({len(errores_totales)})")
        for e in errores_totales:
            print(f"       error de consola: {e}")

        navegador.close()

    print(f"\n{'TODO VERDE' if not FALLOS else f'{len(FALLOS)} FALLO(S)'}")
    for f in FALLOS:
        print(f"  - {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
