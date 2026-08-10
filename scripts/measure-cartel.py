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
        b.close()
    for f in fallos:
        print(f"FALLO {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
