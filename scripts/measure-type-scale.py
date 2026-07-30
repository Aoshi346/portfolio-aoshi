"""Audita que ningun tamano tipografico de Vice cae fuera de la escala.

Se mide en el build de produccion (puerto 4173) con ?theme=vice, y con
prefers-reduced-motion: el layout puro se mide sin animacion, o se acaban
midiendo fotogramas de la entrada en vez de la maquetacion.
"""
import sys
from playwright.sync_api import sync_playwright

ESCALA = [12, 16, 21.33, 28.43, 37.90, 50.52, 67.40, 89.85, 119.77, 159.66]
TOLERANCIA = 0.5  # px: el redondeo del navegador, no una licencia de diseno
ANCHOS = [(390, 844), (1440, 900)]


def fuera_de_escala(valor: float) -> bool:
    return all(abs(valor - paso) > TOLERANCIA for paso in ESCALA)


def main() -> int:
    fallos = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        for ancho, alto in ANCHOS:
            pg = b.new_page(viewport={"width": ancho, "height": alto}, reduced_motion="reduce")
            pg.goto("http://localhost:4173/?theme=vice", wait_until="networkidle", timeout=30000)
            pg.wait_for_timeout(2000)
            medidas = pg.evaluate(
                """() => {
                    const out = [];
                    for (const n of document.querySelectorAll('[data-scene] *')) {
                      if (!n.textContent || !n.textContent.trim()) continue;
                      if (n.children.length) continue;   // solo hojas: el texto vive ahi
                      // El numeral decorativo de fondo de cada ficha de obra
                      // (`data-decorative`, ademas `aria-hidden`) es un
                      // recurso grafico, no tipografia: no comunica texto, y
                      // encogerlo a un paso de la escala (12-159.66px)
                      // estropearia un tamano deliberadamente gigante
                      // (112-352px). Se excluye por categoria, con motivo
                      // escrito, no ampliando ESCALA/TOLERANCIA para que pase.
                      if (n.closest('[data-decorative]')) continue;
                      const r = n.getBoundingClientRect();
                      if (!r.width || !r.height) continue;
                      out.push({
                        px: parseFloat(getComputedStyle(n).fontSize),
                        escena: n.closest('[data-scene]').dataset.scene,
                        clase: n.className || n.tagName.toLowerCase(),
                      });
                    }
                    return out;
                }"""
            )
            for m in medidas:
                if fuera_de_escala(m["px"]):
                    fallos.append(f"{ancho}x{alto} {m['escena']} {m['clase']} -> {m['px']}px")
            pg.close()
        b.close()

    vistos = sorted(set(fallos))
    for f in vistos:
        print("FUERA DE ESCALA:", f)
    print(f"\n{len(vistos)} tamanos fuera de escala")
    return 1 if vistos else 0


if __name__ == "__main__":
    sys.exit(main())
