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

        print("\n[1] La ficha existe y esta en el DOM")
        hay = pagina.evaluate('() => !!document.querySelector(\'[data-ficha="neofetch"]\')')
        comprobar(hay, "la ficha [data-ficha=neofetch] existe en el DOM")

        comprobar(not errores, f"consola sin errores ({len(errores)})")
        navegador.close()

    print(f"\n{'TODO VERDE' if not FALLOS else f'{len(FALLOS)} FALLO(S)'}")
    for f in FALLOS:
        print(f"  - {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
