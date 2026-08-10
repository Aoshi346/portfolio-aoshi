"""Arnes del cartel de obra en Hyprland.

Las aserciones nacen de fallos reales, como en `measure-placa.py`:
  1. Los nodos del cartel existen en el DOM y estan OCULTOS en Vice y en
     Caelestia. El patron aditivo se ha roto cuatro veces por olvidar el
     `display: none` de base.
  2. El boton de apertura no altera la maquetacion de Vice ni de Caelestia.
     Chrome computa `display: inline` como `inline-block` en un <button>
     salvo que se ponga `appearance: none`; ese fallo exacto ya se pago en
     el marcador de identidad de los creditos.
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


def boton_neutral(pg) -> list[str]:
    return pg.evaluate(
        """() => {
          const fallos = [];
          for (const b of document.querySelectorAll('[data-obra-abrir]')) {
            const cs = getComputedStyle(b);
            if (cs.display !== 'inline') fallos.push(`display ${cs.display}, esperaba inline`);
            if (cs.appearance !== 'none') fallos.push(`appearance ${cs.appearance}`);
            if (parseFloat(cs.paddingLeft) !== 0) fallos.push('padding heredado del UA');
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
            fallos += [f"[{tema}] {f}" for f in boton_neutral(pg)]
        b.close()
    for f in fallos:
        print(f"FALLO {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
