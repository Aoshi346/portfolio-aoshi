"""Arnes del cartel de obra en Hyprland.

Las aserciones nacen de fallos reales, como en `measure-placa.py`:
  1. Los nodos del cartel existen en el DOM y estan OCULTOS en Vice y en
     Caelestia. El patron aditivo se ha roto cuatro veces por olvidar el
     `display: none` de base.
  2. Hay CINCO disparadores y los cinco titulares conservan su texto. Un
     `querySelectorAll` vacio hace que el bucle de comprobacion no itere y
     el arnes salga verde sin comprobar nada: eso paso en la primera
     version de este mismo fichero.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

TEMAS_AJENOS = ["vice", "caelestia"]


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


def cartel_en_reposo(pg) -> list[str]:
    """El cartel se VE, las cinco filas caben, y la miniatura mide lo que las letras.

    Sin la primera comprobacion el arnes sale verde con el cartel apagado: los
    nodos existen en el DOM desde la Task 1, asi que contarlos no prueba nada.
    """
    return pg.evaluate(
        """() => {
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
            // por redondeo de subpixel, ni uno mas.
            if (Math.abs(mr.height - tr.height) > 2) {
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
        }"""
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


def relevo_es_ola(pg) -> list[str]:
    """El relevo RECORRE la palabra: a 70ms la primera letra se ha movido y la
    ultima no. Sin esta medida, un cambio simultaneo disfrazado pasaria el
    arnes. No se juzga por captura: `page.screenshot()` bloquea el compositor
    en headless y adelanta la timeline."""
    pg.eval_on_selector('[data-scene="obra"]:nth-child(2) .obra-abrir', "n => n.dispatchEvent(new PointerEvent('pointerenter', {bubbles:true}))")
    pg.wait_for_timeout(70)
    return pg.evaluate(
        """() => {
          const fila = document.querySelectorAll('[data-scene="obra"]')[1];
          const tiras = fila.querySelectorAll('.obra-rl');
          if (tiras.length < 4) return ['el titulo no esta partido en letras'];
          const y = e => new DOMMatrixReadOnly(getComputedStyle(e).transform).m42;
          const primera = y(tiras[0]), ultima = y(tiras[tiras.length - 1]);
          const fallos = [];
          if (primera >= -0.5) fallos.push('la primera letra no se ha movido a 70ms');
          if (ultima < -0.5) fallos.push('la ultima letra ya se movio: no es una ola');
          return fallos;
        }"""
    )


def apertura(pg) -> list[str]:
    """La miniatura y la grande son EL MISMO nodo, la ficha no desborda, y la
    ficha cerrada no roba el puntero.

    Lo ultimo es un defecto medido en el prototipo: con `opacity: 0` el panel
    sigue siendo alcanzable y tapa las filas — el arnes se quedo 30s
    intentando pulsar hasta que Chrome dijo que elemento interceptaba.
    """
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
        pg.eval_on_selector_all(
            "[data-obra-abrir]", f"ns => ns[{i}].click()"
        )
        pg.wait_for_timeout(900)
        fallos += pg.evaluate(
            """(i) => {
              const f = [];
              const secs = document.querySelectorAll('[data-scene="obra"]');
              const abierta = secs[i];
              if (!abierta.classList.contains('is-abierto')) f.push(`fila ${i}: no se abrio`);
              const lupa = document.querySelector('[data-obra-lupa]');
              // el MISMO nodo, no una copia: se recupera por la marca puesta
              // antes del clic, no por posicion en el documento (que cambia
              // cuando el nodo viaja a la lupa).
              const mini = document.querySelector(`[data-check-fila="${i}"]`);
              if (!lupa || !mini || mini.parentElement !== lupa) f.push(`fila ${i}: la captura no viajo a la lupa`);
              const ficha = document.querySelector('[data-obra-ficha]');
              const pista = document.querySelector('[data-obra-track]');
              const desborde = ficha.getBoundingClientRect().bottom - pista.getBoundingClientRect().bottom;
              if (desborde > 0) f.push(`fila ${i}: la ficha desborda ${Math.round(desborde)}px`);
              if (getComputedStyle(ficha).pointerEvents !== 'auto') f.push(`fila ${i}: ficha abierta sin puntero`);
              return f;
            }""",
            i,
        )
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
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
            fallos += [f"[hyprland] {f}" for f in cartel_en_reposo(pg)]
            fallos += [f"[hyprland] {f}" for f in escala_tipografica(pg)]
            fallos += [f"[hyprland] {f}" for f in relevo_es_ola(pg)]
            fallos += [f"[hyprland] {f}" for f in nombre_accesible_intacto(pg)]
            fallos += [f"[hyprland] {f}" for f in apertura(pg)]
        b.close()
    for f in fallos:
        print(f"FALLO {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
