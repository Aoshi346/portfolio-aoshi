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
        b.close()
    for f in fallos:
        print(f"FALLO {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
