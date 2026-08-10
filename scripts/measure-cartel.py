"""Arnes del cartel de obra en Hyprland.

Las aserciones nacen de fallos reales, como en `measure-placa.py`:
  1. Los nodos del cartel existen en el DOM y estan OCULTOS en Vice y en
     Caelestia. El patron aditivo se ha roto cuatro veces por olvidar el
     `display: none` de base.
  2. Hay CINCO disparadores y los cinco titulares conservan su texto. Un
     `querySelectorAll` vacio hace que el bucle de comprobacion no itere y
     el arnes salga verde sin comprobar nada: eso paso en la primera
     version de este mismo fichero.
  3. Movil/tableta (Task 6): el mismo dispositivo, no otro. La miniatura
     esta SIEMPRE puesta bajo 1200px (no espera a un hover que no existe),
     el objetivo tactil llega a 44px, y el hueco 1200-1439px (un portatil
     de 1280, sin ninguna regla propia hasta esta tarea) no deja la ficha
     abierta fuera de la pista.
"""
import argparse
import io
import sys

from playwright.sync_api import sync_playwright
from PIL import Image

TEMAS_AJENOS = ["vice", "caelestia"]

# Tokens de Hyprland (themes.css), en RGB 0-255. Fijos y deterministas: lo
# que se mide es el fondo real, no estos valores.
HAZE_RGB = (0xB1, 0x8C, 0x86)     # --haze
PAPEL_RGB = (0xFF, 0xEA, 0xE6)    # --color-paper (titular encendido)
L1_RGB = (0xFF, 0x5A, 0x34)       # --l1
AA_MINIMO = 4.5

# "portatil" (1280) cierra el hueco 1200-1439px que destapo la revision de la
# Task 4: la lupa (760) y la ficha (520, a 800px del borde) suman 1320px y los
# dos `@media` de esta tarea solo cubren hasta 1199 -- sin geometria propia
# aqui, un portatil de 1280 abre la ficha fuera de la pista.
ANCHOS = [("movil", 390, 844), ("tableta", 820, 1024), ("portatil", 1280, 800), ("escritorio", 1440, 900)]


def movil(pg) -> list[str]:
    """La miniatura esta SIEMPRE puesta cuando no hay hover, el objetivo tactil
    llega a 44px, y ninguna fila degrada a pila generica."""
    return pg.evaluate(
        """() => {
          const f = [];
          for (const sec of document.querySelectorAll('[data-scene="obra"]')) {
            const mini = sec.querySelector('[data-obra-mini]');
            const cs = getComputedStyle(mini);
            if (cs.display === 'none') f.push('sin miniatura en movil');
            if (cs.clipPath !== 'none' && cs.clipPath.includes('100%')) {
              f.push('la miniatura espera a un hover que no existe');
            }
            if (sec.getBoundingClientRect().height < 44) f.push('fila por debajo del objetivo tactil');
          }
          return f;
        }"""
    )


def abre(pg, base: str, tema: str) -> None:
    pg.goto(f"{base}/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(4000)


def ir_a_obra(pg) -> bool:
    """Desplaza hasta la primera fila de obra y espera a que se asiente.

    Sin esto, la fila mide su titulo con el offset de entrada de `.hypr-up`
    (translateY 14px, Gesto 0 de `hypr.choreography.ts`) todavia puesto: a
    scroll 0 la escena de obra vive muy por debajo del pliegue y ni la red
    por posicion ni el observador la encienden. El patron es el mismo que
    `ir_a_about` en `measure-placa.py`.
    """
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"obra\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        return False
    pg.evaluate(f"window.scrollTo(0, {top})")
    pg.wait_for_timeout(2500)
    return True


def nodos_ocultos(pg) -> list[str]:
    return pg.evaluate(
        """() => {
          const fallos = [];
          for (const sel of ['[data-obra-mini]', '[data-obra-marcas]']) {
            const nodos = Array.from(document.querySelectorAll(sel));
            if (nodos.length !== 5) { fallos.push(`${sel}: ${nodos.length} nodos, esperaba 5`); }
            for (const n of nodos) {
              if (getComputedStyle(n).display !== 'none') { fallos.push(`${sel} visible`); break; }
            }
          }
          return fallos;
        }"""
    )


# `Zustand` no existe en `simple-icons`: no pinta tile a proposito (Task 5).
STACK_SIN_MARCA = {"Zustand"}


def marcas_del_stack(pg) -> list[str]:
    """Cada proyecto tiene una marca `.obra-marca` por cada tecnologia de su
    stack con slug CONOCIDO en `simple-icons` -- ni una de menos (falta un
    icono) ni una de mas (aparece un tile fantasma), y nunca el total del
    stack sin filtrar `STACK_SIN_MARCA` (con la ficha vacia esa cuenta seria
    vacuamente exigente: 0 esperadas, 0 encontradas, verde falso). Ademas,
    ningun SVG trae su color de marca: todos deben heredar `currentColor`
    del contenedor.

    Ronda de revision 1: la version anterior localizaba la `dd` del stack
    buscando cual de las `dd` de `.obra-meta` contenia el separador ' · ',
    y se saltaba la seccion entera (`continue`, sin fallo) si ninguna lo
    llevaba -- un proyecto con un solo elemento en el stack (sin ' · ') se
    dejaria de comprobar en silencio, la misma familia de fallo que ya
    pago esta suite cuatro veces. Se arregla en dos frentes:
      1. La `dd` del stack se localiza por lo que ES (la entrada cuyo `dt`
         dice literalmente "Stack", el mismo texto que escribe
         `metaEntry("Stack", ...)` en `projectScene.ts`), no por si su
         contenido tiene o no un separador.
      2. Se cuenta cuantas secciones se han comprobado de verdad y se
         exige que sean 5 -- sin este conteo, una seccion sin entrada de
         Stack (marcado roto, o la entrada renombrada) se saltaria igual
         de silenciosa.
    """
    return pg.evaluate(
        """(sinMarca) => {
          const f = [];
          const secciones = document.querySelectorAll('[data-scene="obra"]');
          let comprobadas = 0;
          for (const sec of secciones) {
            const entrada = Array.from(sec.querySelectorAll('.obra-meta > div'))
              .find(d => d.querySelector('dt')?.textContent === 'Stack');
            const dd = entrada?.querySelector('dd');
            if (!dd) { f.push('seccion sin entrada "Stack" en .obra-meta'); continue; }
            comprobadas += 1;
            const esperadas = dd.textContent.split(' · ').filter(n => !sinMarca.includes(n)).length;
            const tiles = sec.querySelectorAll('[data-obra-marcas] .obra-marca').length;
            if (tiles !== esperadas) f.push(`${tiles} marcas, esperaba ${esperadas}`);
            for (const svg of sec.querySelectorAll('[data-obra-marcas] svg')) {
              const fill = getComputedStyle(svg).fill;
              if (fill !== getComputedStyle(svg.parentElement).color) {
                f.push(`marca con color propio: ${fill}`);
              }
            }
          }
          // 5, no `secciones.length`: si `querySelectorAll('[data-scene="obra"]')`
          // devolviera menos de 5 filas por un fallo de render, comparar
          // contra su propia longitud lo daria vacuamente por bueno.
          if (comprobadas !== 5) {
            f.push(`${comprobadas} secciones comprobadas, esperaba 5`);
          }
          return f;
        }""",
        list(STACK_SIN_MARCA),
    )


def titulo_intacto(pg) -> list[str]:
    """El titular sigue diciendo lo que dice `content.ts` despues de que el
    tema lo parta en caracteres, y hay CINCO disparadores.

    El conteo no es decorativo: sin el, un `querySelectorAll` que devuelve 0
    hace que el bucle no itere, no se empuje ningun fallo y el arnes salga
    verde sin haber comprobado nada. Es el modo de fallo que destapo la
    revision de la Task 1.
    """
    return pg.evaluate(
        """() => {
          const fallos = [];
          const botones = document.querySelectorAll('[data-obra-abrir]');
          if (botones.length !== 5) fallos.push(`${botones.length} disparadores, esperaba 5`);
          const titulos = Array.from(document.querySelectorAll('[data-scene="obra"] h2.display-lg'));
          if (titulos.length !== 5) fallos.push(`${titulos.length} titulares, esperaba 5`);
          for (const t of titulos) {
            const texto = (t.textContent || '').trim();
            if (!texto) fallos.push('titular sin texto tras el split de caracteres');
          }
          return fallos;
        }"""
    )


# Orden de `src/data/content.ts` (`caseStudies`). Se hardcodea aqui a
# proposito: es la unica forma de distinguir "nombre accesible correcto" de
# "nombre accesible duplicado" sin volver a implementar el split en Python.
TITULOS = ["EchoPlan", "TesisFar", "HyprFinance", "WatchDog", "Editor de texto"]


def nombre_accesible_intacto(pg) -> list[str]:
    """El <h2> sigue siendo un encabezado con el titulo real como nombre
    accesible, no la ristra de letras duplicadas que deja el split visual.

    Se lee `aria-label` (no el `textContent`, que sigue duplicado: eso es
    intencion, las letras visuales quedan `aria-hidden`) y se compara contra
    los CINCO titulos de `content.ts`, en orden. El conteo es explicito por
    el mismo motivo que en `titulo_intacto`: una coleccion vacia no debe
    poder dar un arnes verde.
    """
    nombres = pg.evaluate(
        """() => {
          const titulos = Array.from(document.querySelectorAll('[data-scene="obra"] h2.display-lg'));
          return titulos.map(t => t.getAttribute('aria-label'));
        }"""
    )
    fallos = []
    if len(nombres) != 5:
        return [f"{len(nombres)} titulares, esperaba 5"]
    for nombre, esperado in zip(nombres, TITULOS):
        if nombre != esperado:
            fallos.append(f"nombre accesible '{nombre}' distinto del titulo '{esperado}'")
    return fallos


ESCALA = [12, 16, 21.33, 28.43, 37.9, 50.52, 67.4, 89.85, 119.77, 159.66]


def cartel_en_reposo(pg, ancho: int) -> list[str]:
    """El cartel se VE, las cinco filas caben, y la miniatura mide lo que las letras.

    Sin la primera comprobacion el arnes sale verde con el cartel apagado: los
    nodos existen en el DOM desde la Task 1, asi que contarlos no prueba nada.

    La igualdad EXACTA miniatura/titulo solo se exige a partir de 1200px, que
    es donde el titulo vale `--t-8`. Por debajo el titulo encoge a `--t-6`
    (caja de 56,6px) y a `--t-4` (31,8px), y una miniatura de ese tamano no
    enseñaria nada -- el diseno le da medidas propias (152x95 en tableta,
    96x60 en movil), deliberadamente distintas de la caja del titulo.
    """
    return pg.evaluate(
        """(ancho) => {
          const fallos = [];
          const filas = Array.from(document.querySelectorAll('[data-scene="obra"]'));
          if (filas.length !== 5) return [`${filas.length} filas, esperaba 5`];
          const vp = window.innerHeight;
          for (const f of filas) {
            const r = f.getBoundingClientRect();
            if (r.height < 40) fallos.push('fila sin alto: el cartel no esta encendido');
            const t = f.querySelector('h2.display-lg');
            const m = f.querySelector('[data-obra-mini]');
            if (!t || !m) { fallos.push('falta titulo o miniatura'); continue; }
            const tr = t.getBoundingClientRect(), mr = m.getBoundingClientRect();
            // La miniatura mide EXACTAMENTE la caja del titulo: 2px de holgura
            // por redondeo de subpixel, ni uno mas. SOLO a partir de 1200px --
            // por debajo la miniatura lleva medida propia (ver docstring).
            if (ancho >= 1200 && Math.abs(mr.height - tr.height) > 2) {
              fallos.push(`miniatura ${Math.round(mr.height)}px vs titulo ${Math.round(tr.height)}px`);
            }
            if (Math.abs((mr.top + mr.height / 2) - (tr.top + tr.height / 2)) > 3) {
              fallos.push('miniatura desalineada del titulo');
            }
            // El titulo NUNCA se corta: es el defecto que retira el acordeon.
            if (t.scrollWidth > t.clientWidth + 1) fallos.push('titulo recortado');
          }
          const total = filas[4].getBoundingClientRect().bottom - filas[0].getBoundingClientRect().top;
          if (total > vp) fallos.push(`las 5 filas miden ${Math.round(total)}px en un viewport de ${vp}`);
          return fallos;
        }""",
        ancho,
    )


def escala_tipografica(pg) -> list[str]:
    return pg.evaluate(
        """(escala) => {
          const fallos = [];
          const nodos = document.querySelectorAll('[data-scene="obra"] h2.display-lg, [data-scene="obra"] .hero-kick');
          for (const n of nodos) {
            const px = parseFloat(getComputedStyle(n).fontSize);
            if (!escala.some(p => Math.abs(p - px) < 0.6)) {
              fallos.push(`${n.className}: ${px}px fuera de la escala`);
            }
          }
          return fallos;
        }""",
        ESCALA,
    )


# Constantes declaradas en `src/components/obraCartel.ts` (relevo por hover).
# Se duplican aqui a proposito, como `OBRA_TRANSIT`/`OBRA_REST` en
# `vice.choreography.ts`: si cambian alli y no aqui, esta funcion mide la ola
# equivocada sin fallar sola. Mantenerlas en sync es responsabilidad de quien
# toque `relevo()`.
PASO_RELEVO_S = 0.024
DURACION_RELEVO_S = 0.42


def relevo_es_ola(pg) -> list[str]:
    """El relevo RECORRE la palabra: la primera letra arranca antes que la
    ultima, no a la vez. Sin esta medida, un cambio simultaneo disfrazado
    pasaria el arnes.

    Version anterior: comprobaba un unico instante fijo (70ms) contra un
    umbral de sub-pixel. Bajo swiftshader esos 70ms de reloj de pared no
    garantizan un numero fijo de ticks de rAF -- GSAP solo avanza en cada
    tick, y con la maquina cargada el numero de ticks que caben en 70ms
    fluctua. La medida cazaba carga de maquina, no la animacion (ver
    `.claude/rules/verification.md`, "no pongas un umbral mas estrecho que
    el ruido del instrumento").

    Arreglo: en vez de leer una instantanea, se SONDEA en una ventana
    generosa (~6x la duracion declarada del relevo) hasta ver que cada letra
    se ha movido, y se compara el ORDEN/RETRASO relativo entre el arranque de
    la primera y el de la ultima -- no un instante absoluto. El margen minimo
    exigido sale del stagger declarado (`PASO_RELEVO_S` por letra) con un
    factor de seguridad, asi que sigue siendo el valor determinista del
    codigo, no un numero inventado. El cronometro (la ventana de sondeo) es
    solo la comprobacion de cordura, con margen explicito frente al peor caso
    realista (relevo completo + varios frames perdidos).

    No se juzga por captura: `page.screenshot()` bloquea el compositor en
    headless y adelanta la timeline.
    """
    n_tiras = pg.evaluate(
        """() => document.querySelectorAll('[data-scene="obra"]')[1]
          .querySelectorAll('.obra-rl').length"""
    )
    if n_tiras < 4:
        return ["el titulo no esta partido en letras"]

    # `t0` se toma DENTRO del navegador, en el mismo tick que el disparo del
    # gesto: cada sondeo posterior tambien lee `performance.now()` alli
    # mismo, asi que el tiempo transcurrido que se compara es reloj del
    # navegador contra reloj del navegador. El viaje IPC de Playwright
    # (10-40ms por `evaluate()` medidos en esta maquina) queda fuera de la
    # medida -- es justo el ruido que rompia la version anterior, que
    # contaba "pasos de sondeo" asumidos en vez de tiempo real transcurrido.
    t0 = pg.evaluate(
        """() => {
          const fila = document.querySelectorAll('[data-scene="obra"]')[1];
          fila.querySelector('.obra-abrir').dispatchEvent(
            new PointerEvent('pointerenter', {bubbles: true}),
          );
          return performance.now();
        }"""
    )

    # Ventana de sondeo: duracion declarada del relevo + el retraso maximo
    # declarado entre la primera y la ultima letra, con margen x3. Es el
    # cronometro-comprobacion-de-cordura, generoso a proposito frente al
    # peor caso realista (relevo completo + varios frames de rAF perdidos).
    retraso_declarado_ms = (n_tiras - 1) * PASO_RELEVO_S * 1000
    ventana_ms = round((DURACION_RELEVO_S * 1000 + retraso_declarado_ms) * 3)
    primera_en: float | None = None
    ultima_en: float | None = None
    while True:
        t_rel, primera, ultima = pg.evaluate(
            """(t0) => {
              const fila = document.querySelectorAll('[data-scene="obra"]')[1];
              const tiras = fila.querySelectorAll('.obra-rl');
              const y = e => new DOMMatrixReadOnly(getComputedStyle(e).transform).m42;
              return [performance.now() - t0, y(tiras[0]), y(tiras[tiras.length - 1])];
            }""",
            t0,
        )
        if primera_en is None and primera <= -0.5:
            primera_en = t_rel
        if ultima_en is None and ultima <= -0.5:
            ultima_en = t_rel
        if primera_en is not None and ultima_en is not None:
            break
        if t_rel > ventana_ms:
            break
        pg.wait_for_timeout(15)

    fallos: list[str] = []
    if primera_en is None:
        fallos.append(f"la primera letra no se movio en {ventana_ms}ms")
    if ultima_en is None:
        fallos.append(f"la ultima letra no se movio en {ventana_ms}ms")
    if primera_en is not None and ultima_en is not None:
        # Se exige solo el 50% del retraso declarado: margen explicito frente
        # a que el sondeo (paso de 15ms) recorte la medida por el lado bajo,
        # pero de sobra para distinguir una ola real (~139ms medidos en esta
        # maquina para un titulo de 8 letras, contra un declarado de 168ms)
        # de un cambio simultaneo disfrazado (diferencia ~0ms).
        margen_min_ms = retraso_declarado_ms * 0.5
        diferencia = ultima_en - primera_en
        if diferencia < margen_min_ms:
            fallos.append(
                f"la primera y la ultima letra arrancaron con {diferencia:.0f}ms de diferencia "
                f"(reloj del navegador), esperaba >= {margen_min_ms:.0f}ms "
                f"(retraso declarado {retraso_declarado_ms:.0f}ms)"
            )
    return fallos


# Numero exacto de bloques que `bloquesDeFicha()` mueve a la ficha: lead,
# las DOS columnas de `[data-mask]` (Problema/Solucion), las marcas de stack
# y la fila de metadatos. Los cinco existen SIEMPRE en `projectScene.ts`
# (incluso `data-obra-marcas`, vacio hasta la Task 5), asi que el numero es
# constante y no un ">0" que una ficha vacia tambien pasaria.
BLOQUES_FICHA = 5


def apertura(pg) -> list[str]:
    """La miniatura y la grande son EL MISMO nodo, la ficha no desborda, la
    ficha cerrada no roba el puntero, Y la ficha abierta lleva sus 5 bloques
    de contenido (no una caja vacia: `ficha.children.length === N`, no
    `> 0` — con la ficha vacia la altura es 0 y "no desborda" saldria
    vacuamente cierto, exactamente el verde falso que dejaria pasar el
    defecto (b) de `cierra()` vaciando antes de animar).

    Lo del puntero es un defecto medido en el prototipo: con `opacity: 0` el
    panel sigue siendo alcanzable y tapa las filas — el arnes se quedo 30s
    intentando pulsar hasta que Chrome dijo que elemento interceptaba.
    """
    # Contenido de referencia de cada `.lead`, leido ANTES de abrir nada: sirve
    # para comprobar en la segunda pasada que la fila reabierta trae SU propio
    # contenido, no el de la fila visitada entre medias (la regresion real:
    # "abrir A, cerrar, abrir B, volver a A" perdia el contenido de A).
    leads_originales = pg.evaluate(
        """() => Array.from(document.querySelectorAll('[data-scene="obra"] .lead'))
          .map(n => n.textContent)"""
    )
    fallos = pg.evaluate(
        """() => {
          const f = [];
          const ficha = document.querySelector('[data-obra-ficha]');
          if (!ficha) return ['no hay ficha'];
          if (getComputedStyle(ficha).pointerEvents !== 'none') {
            f.push('la ficha cerrada captura el puntero');
          }
          return f;
        }"""
    )

    def abre_y_comprueba(i: int) -> list[str]:
        pg.eval_on_selector_all("[data-obra-abrir]", f"ns => ns[{i}].click()")
        pg.wait_for_timeout(900)
        return pg.evaluate(
            """(args) => {
              const [i, leadEsperado, nBloques] = args;
              const f = [];
              const secs = document.querySelectorAll('[data-scene="obra"]');
              const abierta = secs[i];
              if (!abierta.classList.contains('is-abierto')) f.push(`fila ${i}: no se abrio`);
              const lupa = document.querySelector('[data-obra-lupa]');
              const mini = document.querySelector(`[data-check-fila="${i}"]`);
              if (!lupa || !mini || mini.parentElement !== lupa) f.push(`fila ${i}: la captura no viajo a la lupa`);
              const ficha = document.querySelector('[data-obra-ficha]');
              const pista = document.querySelector('[data-obra-track]');
              const desborde = ficha.getBoundingClientRect().bottom - pista.getBoundingClientRect().bottom;
              if (desborde > 0) f.push(`fila ${i}: la ficha desborda ${Math.round(desborde)}px`);
              // El hueco 1200-1439px (Task 6): lupa (760) + ficha (520, a 800px
              // del borde) suman 1320px en pixeles fijos. Sin geometria propia
              // ahi, un portatil de 1280 saca la ficha por la DERECHA de la
              // pista sin que el desborde vertical de arriba lo note nunca.
              const desbordeH = ficha.getBoundingClientRect().right - pista.getBoundingClientRect().right;
              if (desbordeH > 1) f.push(`fila ${i}: la ficha desborda ${Math.round(desbordeH)}px por la derecha`);
              if (getComputedStyle(ficha).pointerEvents !== 'auto') f.push(`fila ${i}: ficha abierta sin puntero`);
              if (ficha.children.length !== nBloques) {
                f.push(`fila ${i}: ficha con ${ficha.children.length} bloques, esperaba ${nBloques}`);
              }
              const lead = ficha.querySelector('.lead');
              if (!lead || lead.textContent !== leadEsperado) {
                f.push(`fila ${i}: el lead de la ficha no es el de esta fila`);
              }
              // La miniatura YA DENTRO de la lupa: sin `.obra-lupa .obra-mini`
              // se queda con alto `auto` (no llena la lupa), sin `overflow`
              // (la imagen se desborda) y con `position: static` (el pie
              // absoluto deja de anclarse a la foto y flota donde le toque a
              // la lupa). Se exigen valores concretos, no una iteracion que
              // pase con cualquier caja no vacia.
              if (!mini) { f.push(`fila ${i}: sin miniatura en la lupa, no se puede medir la caja`); return f; }
              const img = mini.querySelector('.obra-mini-img');
              const pie = mini.querySelector('.obra-mini-pie');
              if (!img || !pie) { f.push(`fila ${i}: miniatura sin imagen o sin pie`); return f; }
              const mr = mini.getBoundingClientRect();
              const ir = img.getBoundingClientRect();
              const pr = pie.getBoundingClientRect();
              const lr = lupa.getBoundingClientRect();
              if (Math.abs(mr.height - lr.height) > 1 || Math.abs(mr.width - lr.width) > 1) {
                f.push(`fila ${i}: miniatura ${Math.round(mr.width)}x${Math.round(mr.height)} no llena la lupa (${Math.round(lr.width)}x${Math.round(lr.height)})`);
              }
              if (Math.abs(ir.height - mr.height) > 1 || Math.abs(ir.width - mr.width) > 1) {
                f.push(`fila ${i}: imagen ${Math.round(ir.width)}x${Math.round(ir.height)} no llena la miniatura (${Math.round(mr.width)}x${Math.round(mr.height)})`);
              }
              const despegue = Math.abs(pr.bottom - ir.bottom);
              if (despegue > 1) {
                f.push(`fila ${i}: el pie esta a ${Math.round(despegue)}px del borde inferior de la foto, no pegado`);
              }
              return f;
            }""",
            [i, leads_originales[i], BLOQUES_FICHA],
        )

    for i in range(5):
        # Se marca la miniatura de la fila ANTES del clic: una vez viaja a la
        # lupa (que vive al nivel de `.obra-track`, no dentro de `abierta`)
        # cambia de posicion en el orden del documento, asi que recuperarla
        # por indice tras el viaje señalaria un nodo distinto. La marca
        # sobrevive el viaje porque es un atributo del propio nodo, no de su
        # posicion.
        pg.evaluate(
            """(i) => {
              const secs = document.querySelectorAll('[data-scene="obra"]');
              const mini = secs[i].querySelector('[data-obra-mini]');
              if (mini) mini.setAttribute('data-check-fila', String(i));
            }""",
            i,
        )
        fallos += [f"pasada 1, {f}" for f in abre_y_comprueba(i)]
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)

    # Segunda pasada: REABRIR filas ya visitadas, no solo recorrer 0..4 una
    # vez. La primera pasada nunca vuelve atras, asi que "abrir A, cerrar,
    # abrir B, volver a A" —la regresion real que corrigio esta tarea, donde
    # A se quedaba sin ficha— vivia solo en un script de autorrevision
    # desechable y el arnes no la veria. Se visita B (fila 3) entre A y la
    # reapertura de A (fila 0), y se repite con otro par (fila 1 tras fila 4).
    for a, b in [(0, 3), (1, 4)]:
        pg.evaluate(
            """(i) => {
              const secs = document.querySelectorAll('[data-scene="obra"]');
              const mini = secs[i].querySelector('[data-obra-mini]');
              if (mini) mini.setAttribute('data-check-fila', String(i));
            }""",
            b,
        )
        fallos += [f"pasada 2 (via fila {b}), {f}" for f in abre_y_comprueba(b)]
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
        pg.evaluate(
            """(i) => {
              const secs = document.querySelectorAll('[data-scene="obra"]');
              const mini = secs[i].querySelector('[data-obra-mini]');
              if (mini) mini.setAttribute('data-check-fila', String(i));
            }""",
            a,
        )
        fallos += [f"reapertura de fila {a} tras fila {b}, {f}" for f in abre_y_comprueba(a)]
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
    return fallos


def accesibilidad(pg) -> list[str]:
    """Los cinco disparadores tienen nombre accesible, orden de tabulacion
    visual (nada de `tabindex` negativo) y hay una region `aria-live` para
    anunciar apertura/cierre. El conteo explicito de disparadores sigue el
    mismo patron que el resto del arnes: un `querySelectorAll` vacio no debe
    poder dar un verde vacuo."""
    return pg.evaluate(
        """() => {
          const f = [];
          const botones = Array.from(document.querySelectorAll('[data-obra-abrir]'));
          if (botones.length !== 5) f.push(`${botones.length} disparadores, esperaba 5`);
          for (const b of botones) {
            const etiqueta = b.getAttribute('aria-label') || '';
            if (!etiqueta.startsWith('Mostrar ')) f.push('disparador sin nombre accesible');
            if (b.tabIndex < 0) f.push('disparador fuera del orden de tabulacion');
          }
          const anuncio = document.querySelector('[data-obra-anuncio]');
          if (!anuncio || anuncio.getAttribute('aria-live') !== 'polite') f.push('sin region aria-live');
          return f;
        }"""
    )


def movimiento_reducido(pg_reducido) -> list[str]:
    """Con `reduce` el dispositivo sigue COMPLETO: se pierde el movimiento, no
    la informacion. Es la diferencia entre degradar y desactivar: la
    miniatura ya esta asentada (recorte en reposo) en vez de esperar a un
    barrido que no va a llegar, y la barra de entrada ni se crea."""
    return pg_reducido.evaluate(
        """() => {
          const f = [];
          for (const sec of document.querySelectorAll('[data-scene="obra"]')) {
            const mini = sec.querySelector('[data-obra-mini]');
            const cp = getComputedStyle(mini).clipPath;
            if (cp !== 'none' && cp.includes('100%')) f.push('captura oculta con movimiento reducido');
          }
          if (document.querySelector('.obra-barrido')) f.push('la barra de entrada existe con reduce');
          return f;
        }"""
    )


# Indices en `content.ts` (`caseStudies`) con 2 capturas frente a 1 sola.
# EchoPlan/TesisFar/HyprFinance/WatchDog declaran 2; Editor de texto, 1.
CON_SEGUNDA_CAPTURA = [0, 1, 2, 3]
SIN_SEGUNDA_CAPTURA = [4]


def segunda_captura(pg) -> list[str]:
    """Los proyectos con 2 capturas en `content.ts` muestran su segunda foto
    como tile bajo la lupa cuando la fila abre; el proyecto con 1 sola
    (Editor de texto) no pinta ningun tile ni deja un hueco vacio.

    El conteo es explicito (no un `> 0`): con la ficha vacia una condicion
    vacua tambien pasaria en verde -- el mismo modo de fallo que ya pago
    esta suite varias veces."""
    fallos: list[str] = []
    for i in CON_SEGUNDA_CAPTURA:
        pg.eval_on_selector_all("[data-obra-abrir]", f"ns => ns[{i}].click()")
        pg.wait_for_timeout(900)
        n = pg.evaluate(
            """() => document.querySelectorAll('.obra-track > .obra-otras .obra-otra').length"""
        )
        if n != 1:
            fallos.append(f"fila {i}: {n} tiles de captura restante, esperaba 1")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
    for i in SIN_SEGUNDA_CAPTURA:
        pg.eval_on_selector_all("[data-obra-abrir]", f"ns => ns[{i}].click()")
        pg.wait_for_timeout(900)
        n = pg.evaluate(
            """() => document.querySelectorAll('.obra-track > .obra-otras .obra-otra').length"""
        )
        if n != 0:
            fallos.append(f"fila {i}: {n} tiles de captura restante, esperaba 0 (una sola captura)")
        hueco = pg.evaluate(
            """() => {
              const otras = document.querySelector('.obra-track > .obra-otras');
              return otras ? otras.getBoundingClientRect().height : 0;
            }"""
        )
        if hueco > 1:
            fallos.append(f"fila {i}: la banda de capturas restantes deja un hueco de {round(hueco)}px")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
    return fallos


def _leer_lupa_y_tile(pg) -> tuple[str, str]:
    lupa = pg.evaluate(
        """() => document.querySelector('[data-obra-lupa] .obra-mini-img')?.src ?? ''"""
    )
    tile = pg.evaluate(
        """() => document.querySelector('.obra-track > .obra-otras .obra-otra-img')?.src ?? ''"""
    )
    return lupa, tile


def pulsar_intercambia_y_vuelve(pg) -> list[str]:
    """Pulsar el tile INTERCAMBIA su foto con la de la lupa: un conmutador
    reversible, no un selector. Con un solo tile (proyectos de 2 capturas),
    un SEGUNDO clic sobre el mismo tile debe deshacer el primero -- se puede
    volver a la primera captura sin cerrar la ficha, que es precisamente la
    regresion que reporto la ronda de revision 1 (antes, `restauraMini()`
    solo se llamaba desde `cierra()`).

    Se comprueban tanto la lupa como el propio tile en los tres momentos
    (antes / tras el primer clic / tras el segundo), porque un intercambio
    a medias (solo la lupa cambia, el tile se queda con la misma foto que ya
    tenia) pasaria una asercion que solo mirara la lupa."""
    fallos: list[str] = []
    i = 0  # EchoPlan: 2 capturas
    pg.eval_on_selector_all("[data-obra-abrir]", f"ns => ns[{i}].click()")
    pg.wait_for_timeout(900)
    lupa0, tile0 = _leer_lupa_y_tile(pg)
    if not lupa0 or not tile0:
        return ["no se pudo leer la imagen de la lupa o del tile"]

    pg.eval_on_selector_all(".obra-track > .obra-otras .obra-otra", "ns => ns[0].click()")
    pg.wait_for_timeout(700)
    lupa1, tile1 = _leer_lupa_y_tile(pg)
    if lupa1 != tile0:
        fallos.append(f"tras el 1er clic la lupa muestra '{lupa1}', esperaba la del tile '{tile0}'")
    if tile1 != lupa0:
        fallos.append(f"tras el 1er clic el tile muestra '{tile1}', esperaba la de la lupa '{lupa0}'")

    # SEGUNDO clic sobre el MISMO tile, sin cerrar la ficha: debe deshacer el
    # primero. Esta es la comprobacion que faltaba en la ronda anterior.
    pg.eval_on_selector_all(".obra-track > .obra-otras .obra-otra", "ns => ns[0].click()")
    pg.wait_for_timeout(700)
    lupa2, tile2 = _leer_lupa_y_tile(pg)
    if lupa2 != lupa0:
        fallos.append(f"tras el 2o clic (vuelta) la lupa muestra '{lupa2}', esperaba la original '{lupa0}'")
    if tile2 != tile0:
        fallos.append(f"tras el 2o clic (vuelta) el tile muestra '{tile2}', esperaba el original '{tile0}'")

    pg.keyboard.press("Escape")
    pg.wait_for_timeout(700)
    return fallos


def destroy_revierte_intercambio(pg) -> list[str]:
    """`destroy()` (disparado en `pagehide`, la ruta real de la bfcache) debe
    deshacer cualquier intercambio pendiente ANTES de soltar el modulo. Sin
    esto, `obra-mini-img.src`/`.alt` y el pie quedan mutados en el DOM real:
    al volver de la bfcache la pagina no se remonta, y el siguiente
    `partirTitulo()` leeria esa mutacion como si fuera `gallery[0]` --
    `gallery[0]` quedaria inaccesible el resto de la sesion.

    Se dispara `pagehide` de verdad (el listener real de `main.ts`, no una
    llamada directa a `destroy()` que no existe en el `window`), se
    intercambia ANTES de dispararlo, y se comprueba el `src` real tras el
    evento -- el punto exacto que reporto la ronda de revision 1.
    """
    i = 0  # EchoPlan: 2 capturas
    pg.eval_on_selector_all("[data-obra-abrir]", f"ns => ns[{i}].click()")
    pg.wait_for_timeout(900)
    lupa0, _ = _leer_lupa_y_tile(pg)
    if not lupa0:
        return ["no se pudo leer la imagen original de la lupa"]
    pg.eval_on_selector_all(".obra-track > .obra-otras .obra-otra", "ns => ns[0].click()")
    pg.wait_for_timeout(700)
    lupa_tras_clic, _ = _leer_lupa_y_tile(pg)
    if lupa_tras_clic == lupa0:
        return ["el clic no intercambio nada, la prueba de destroy() no comprueba nada real"]

    pg.evaluate("""() => window.dispatchEvent(new Event('pagehide'))""")
    pg.wait_for_timeout(300)
    fallo = pg.evaluate(
        """(esperado) => {
          const secs = document.querySelectorAll('[data-scene="obra"]');
          const mini = secs[0].querySelector('[data-obra-mini] .obra-mini-img');
          if (!mini) return 'sin miniatura tras destroy()';
          if (mini.src !== esperado) {
            return `la miniatura quedo en '${mini.src}' tras destroy(), esperaba la original '${esperado}'`;
          }
          return null;
        }""",
        lupa0,
    )
    return [fallo] if fallo else []


def enlace_en_ficha(pg) -> list[str]:
    """El pie del proyecto (enlace al repositorio o nota de "Proyecto
    privado") viaja a la ficha abierta: `bloquesDeFicha()` lo incluye desde
    la Task 7. El conteo de bloques (`BLOQUES_FICHA`) no lo detecta -- sigue
    siendo 5 porque el pie sustituye a `problem` -- asi que hay que mirar el
    CONTENIDO de la ficha abierta, no solo su tamano."""
    con_link = [1, 3, 4]  # TesisFar, WatchDog, Editor de texto (content.ts)
    con_nota = [0, 2]  # EchoPlan, HyprFinance
    fallos: list[str] = []
    for i in con_link:
        pg.eval_on_selector_all("[data-obra-abrir]", f"ns => ns[{i}].click()")
        pg.wait_for_timeout(900)
        fallo = pg.evaluate(
            """() => {
              const ficha = document.querySelector('[data-obra-ficha]');
              // Acotado a `[data-obra-pie] a[href]`, no a la ficha entera: la
              // Task 8 anade botones (tiles de capturas) a la ficha, y un
              // `a[href]` suelto en cualquier otro bloque haria pasar esta
              // asercion por el motivo equivocado.
              const link = ficha.querySelector('[data-obra-pie] a[href]');
              if (!link) return 'sin enlace visible en la ficha';
              const r = link.getBoundingClientRect();
              if (r.width === 0 || r.height === 0) return 'enlace presente pero sin caja visible';
              return null;
            }"""
        )
        if fallo:
            fallos.append(f"fila {i}: {fallo}")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
    for i in con_nota:
        pg.eval_on_selector_all("[data-obra-abrir]", f"ns => ns[{i}].click()")
        pg.wait_for_timeout(900)
        fallo = pg.evaluate(
            """() => {
              const ficha = document.querySelector('[data-obra-ficha]');
              const nota = Array.from(ficha.querySelectorAll('p'))
                .find(p => p.textContent.includes('Proyecto privado'));
              if (!nota) return 'sin nota de proyecto privado en la ficha';
              const r = nota.getBoundingClientRect();
              if (r.width === 0 || r.height === 0) return 'nota presente pero sin caja visible';
              return null;
            }"""
        )
        if fallo:
            fallos.append(f"fila {i}: {fallo}")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
    return fallos


def _lin(c: float) -> float:
    cs = c / 255
    return cs / 12.92 if cs <= 0.03928 else ((cs + 0.055) / 1.055) ** 2.4


def _luminancia(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _contraste(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1, l2 = _luminancia(fg) + 0.05, _luminancia(bg) + 0.05
    return max(l1, l2) / min(l1, l2)


def _percentil(datos: list[float], p: float) -> float:
    if not datos:
        return 0.0
    rango = (len(datos) - 1) * (p / 100.0)
    bajo = int(rango)
    alto = min(bajo + 1, len(datos) - 1)
    frac = rango - bajo
    return datos[bajo] + (datos[alto] - datos[bajo]) * frac


def contraste_fondo_real(pg) -> list[str]:
    """El fondo NO es un plano: la pagina lleva el shader `hyprEmber.ts` mas
    `--bg-fallback`, que sube hasta #3a1008 en su version estatica. El shader
    mezcla directamente el color de `--l1` (`vec3(1.0, 0.353, 0.204)` =
    `#ff5a34`) en el haz -- el mismo hex que la marca activa -- asi que el
    techo real de brillo NO es el `#3a1008` del fallback, es lo que el haz
    alcanza en movimiento.

    `.bg-theme` es `position: fixed` (`style.css`) y el shader solo depende
    de `uTime`/`uResolution`, NUNCA de scroll (a diferencia de Vice, que si
    lo consume) -- confirmado leyendo `hyprEmber.ts` y `shaderBackground.ts`.
    Eso significa que el pixel de fondo en una coordenada de VIEWPORT es el
    mismo sea cual sea el scroll de la pagina: fijar la fila a un encuadre de
    scroll concreto (`scrollIntoView` vs `scrollTo`) solo cambia CUAL
    fotograma del shader queda detras, no anade cobertura. El cartel no
    lleva pin de ScrollTrigger (decision del spec), asi que en un scroll
    libre la fila puede terminar de descansar en cualquier alto de viewport.

    Por eso se mide el VIEWPORT ENTERO (no solo el rect de una fila) durante
    16.8s (48 fotogramas): cubre cualquier altura donde la fila pueda posarse
    y suficiente tiempo del barrido generativo. Se usa el p99.5 de
    luminancia como "peor caso real" (mismo criterio que `measure-bg-luma.py`
    para el techo de Vice) y se identifica el tercio de pantalla (alto/medio/
    bajo) donde cae, para relacionarlo con "la zona alta" que describe el
    spec.
    """
    alto_viewport = pg.viewport_size["height"]
    ancho_viewport = pg.viewport_size["width"]

    pg.add_style_tag(
        content="#app > *:not(.bg-theme):not(.bg-noise) { visibility: hidden !important; }"
    )
    pg.wait_for_timeout(300)

    muestras: list[tuple[tuple[int, int, int], int]] = []  # (rgb, y_px)
    for _ in range(48):
        pg.wait_for_timeout(350)
        png = pg.screenshot()
        img = Image.open(io.BytesIO(png)).convert("RGB")
        w, h = img.size
        px = img.load()
        for y in range(0, h, 4):
            for x in range(0, w, 4):
                muestras.append((px[x, y], y))

    luminancias = sorted(_luminancia(p) for p, _ in muestras)
    objetivo = _percentil(luminancias, 99.5)
    peor_pixel, peor_y = min(muestras, key=lambda m: abs(_luminancia(m[0]) - objetivo))
    tercio = "alto" if peor_y < h / 3 else ("medio" if peor_y < 2 * h / 3 else "bajo")

    c_haze = _contraste(HAZE_RGB, peor_pixel)
    c_papel = _contraste(PAPEL_RGB, peor_pixel)
    c_l1 = _contraste(L1_RGB, peor_pixel)

    print(
        f"    [contraste] peor fondo real medido (p99.5, 16.8s, viewport {ancho_viewport}x{alto_viewport}, "
        f"tercio {tercio}) = rgb{peor_pixel} -- haze {c_haze:.2f}:1, papel {c_papel:.2f}:1, l1 {c_l1:.2f}:1"
    )

    fallos: list[str] = []
    if c_haze < AA_MINIMO:
        fallos.append(
            f"--haze {c_haze:.2f}:1 contra el fondo real (peor caso medido, tercio {tercio}) < {AA_MINIMO}:1 AA"
        )
    if c_papel < AA_MINIMO:
        fallos.append(
            f"papel (titular encendido) {c_papel:.2f}:1 contra el fondo real (tercio {tercio}) < {AA_MINIMO}:1 AA"
        )
    return fallos


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://localhost:4173")
    args = p.parse_args()
    fallos: list[str] = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        for tema in TEMAS_AJENOS:
            abre(pg, args.base, tema)
            fallos += [f"[{tema}] {f}" for f in nodos_ocultos(pg)]
            fallos += [f"[{tema}] {f}" for f in titulo_intacto(pg)]
        abre(pg, args.base, "hyprland")
        if not ir_a_obra(pg):
            fallos.append("[hyprland] no existe [data-scene=\"obra\"]")
        else:
            # 1440 (escritorio) es donde viven relevo por hover, marcas del stack
            # y el nombre accesible -- lo que ya cubria el arnes antes de esta
            # tarea. Los tres anchos nuevos (movil/tableta/portatil) se prueban
            # abajo, cada uno en su propia pagina.
            fallos += [f"[hyprland escritorio] {f}" for f in cartel_en_reposo(pg, 1440)]
            fallos += [f"[hyprland escritorio] {f}" for f in escala_tipografica(pg)]
            fallos += [f"[hyprland escritorio] {f}" for f in relevo_es_ola(pg)]
            fallos += [f"[hyprland escritorio] {f}" for f in nombre_accesible_intacto(pg)]
            fallos += [f"[hyprland escritorio] {f}" for f in marcas_del_stack(pg)]
            fallos += [f"[hyprland escritorio] {f}" for f in apertura(pg)]
            fallos += [f"[hyprland escritorio] {f}" for f in accesibilidad(pg)]
            fallos += [f"[hyprland escritorio] {f}" for f in enlace_en_ficha(pg)]
            fallos += [f"[hyprland escritorio] {f}" for f in segunda_captura(pg)]
            fallos += [f"[hyprland escritorio] {f}" for f in pulsar_intercambia_y_vuelve(pg)]
            # SIEMPRE la ultima prueba en esta pagina: dispara `destroy()`
            # de verdad (via `pagehide`), asi que cualquier asercion
            # posterior en `pg` correria contra un modulo ya desmontado.
            fallos += [f"[hyprland escritorio] {f}" for f in destroy_revierte_intercambio(pg)]

            # Contraste contra el fondo REAL (Task 9): pagina propia, limpia
            # y SIN ficha abierta -- la de arriba ya la abrio `apertura()`, y
            # la ficha tapa justo la zona alta que hay que medir.
            pg_contraste = b.new_page(viewport={"width": 1440, "height": 900})
            abre(pg_contraste, args.base, "hyprland")
            if ir_a_obra(pg_contraste):
                fallos += [f"[hyprland contraste] {f}" for f in contraste_fondo_real(pg_contraste)]
            else:
                fallos.append('[hyprland contraste] no existe [data-scene="obra"]')
            pg_contraste.close()
        b.close()

        # Movimiento reducido: contexto propio con `reduced_motion="reduce"`,
        # nunca la misma pagina que ya corrio con movimiento completo.
        b3 = pw.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        ctx_reducido = b3.new_context(
            viewport={"width": 1440, "height": 900}, reduced_motion="reduce"
        )
        pg3 = ctx_reducido.new_page()
        abre(pg3, args.base, "hyprland")
        if not ir_a_obra(pg3):
            fallos.append('[hyprland reduce] no existe [data-scene="obra"]')
        else:
            fallos += [f"[hyprland reduce] {f}" for f in movimiento_reducido(pg3)]
        b3.close()

        # Movil, tableta y portatil (Task 6): el mismo dispositivo, no otro.
        # Cada ancho en su propia pagina -- `apertura()` deja la pagina con
        # cinco filas desplazadas y una ficha poblada, y reutilizar la misma
        # pagina entre anchos arrastraria ese estado al siguiente viewport.
        for nombre, ancho, alto in ANCHOS:
            if nombre == "escritorio":
                continue
            b2 = pw.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
            pg2 = b2.new_page(viewport={"width": ancho, "height": alto})
            abre(pg2, args.base, "hyprland")
            if not ir_a_obra(pg2):
                fallos.append(f"[hyprland {nombre}] no existe [data-scene=\"obra\"]")
                b2.close()
                continue
            fallos += [f"[hyprland {nombre}] {f}" for f in cartel_en_reposo(pg2, ancho)]
            fallos += [f"[hyprland {nombre}] {f}" for f in escala_tipografica(pg2)]
            if nombre in ("movil", "tableta"):
                fallos += [f"[hyprland {nombre}] {f}" for f in movil(pg2)]
            fallos += [f"[hyprland {nombre}] {f}" for f in apertura(pg2)]
            b2.close()
    for f in fallos:
        print(f"FALLO {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
