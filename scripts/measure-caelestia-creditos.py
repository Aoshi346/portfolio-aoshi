"""Arnes de la escena Creditos de Caelestia (fase B4, la bandeja de paquetes).

Cada familia de aserciones nacio de un fallo real, documentado en su propio
docstring. Ninguna se acepta sin haberla visto dar rojo contra ese fallo.

Se corre SIEMPRE contra el build de produccion servido (`npm run build &&
npx vite preview --port 4173`), nunca contra `npm run dev`: el HMR corrompe
las medidas de layout y de ScrollTrigger, y miente en los dos sentidos.
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

FALLOS: list[str] = []


def check(ok: bool, etiqueta: str) -> None:
    print(("  OK   " if ok else "  FAIL ") + etiqueta)
    if not ok:
        FALLOS.append(etiqueta)


def abre(pagina, base: str) -> None:
    """Abre Creditos y espera a que el workspace asiente.

    Se cambia de workspace pulsando la pastilla del shell, no tocando el hash:
    el hash lo cambia el shell, y forzarlo desde fuera deja el carril a medio
    camino."""
    pagina.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=45000)
    pagina.wait_for_timeout(6000)
    pagina.eval_on_selector_all(
        ".cae-ws",
        "bs=>{const b=bs.find(x=>/Cr..?ditos/.test(x.textContent)); if(b) b.click();}",
    )
    pagina.wait_for_timeout(2500)


def gate_sin_scroll(pagina) -> None:
    """La escena NO puede desplazarse por dentro. Es la ley de la fase A: un
    espacio de trabajo no se desplaza, se cambia.

    Visto rojo con: el estado de partida, 758 / 748 — diez pixeles."""
    print("[1] la escena no tiene scroll interno")
    m = pagina.evaluate(
        """() => {
             const e = document.querySelector('[data-scene="credits"]');
             return {alto: e.scrollHeight, caja: e.clientHeight,
                     ancho: e.scrollWidth, cajaX: e.clientWidth};
           }"""
    )
    check(m["alto"] <= m["caja"], f"sin scroll vertical ({m['alto']} / {m['caja']})")
    check(m["ancho"] <= m["cajaX"], f"sin scroll horizontal ({m['ancho']} / {m['cajaX']})")


def gate_rotulos(pagina) -> None:
    """Los cuatro rotulos de territorio tienen que PINTARSE.

    Visto rojo con: el estado de partida, donde los cuatro existian en el DOM y
    no se pintaba ninguno. Contar nodos no es contar lo que se ve — es el modo
    de fallo central de esta fase, asi que se filtra por getClientRects()."""
    print("[3] los cuatro rotulos de territorio se pintan")
    n = pagina.evaluate(
        """() => [...document.querySelectorAll('[data-scene="credits"] .cae-cred-rot')]
                   .filter(e => e.getClientRects().length > 0).length"""
    )
    check(n == 4, f"cuatro rotulos pintados ({n} de 4)")


def gate_piezas(pagina) -> None:
    """Las 23 tecnologias tienen que estar DENTRO de la caja de la escena, sin
    desplazar. En el estado de partida cuatro de los cinco proyectos de Obra
    quedaban fuera de la ventana por el mismo motivo; aqui se comprueba antes de
    que pase.

    Se compara contra la caja de la escena, no contra el viewport: la ventana
    del workspace mide 1412 x 748 y el viewport 1440 x 900.

    El lado se lee con `offsetWidth`, no con `getBoundingClientRect().width`:
    ese ultimo incluye los transforms, y la Task 5 escala la pieza elegida a
    1,07 al rozarla — con `getBoundingClientRect()` el gate veria dos lados
    distintos y fallaria sin que nada estuviera roto."""
    print("[2] las 23 piezas estan dentro de la caja de la escena")
    m = pagina.evaluate(
        """() => {
             const e = document.querySelector('[data-scene="credits"]');
             const c = e.getBoundingClientRect();
             const t = [...e.querySelectorAll('.cae-cred-pieza')]
                         .filter(x => x.getClientRects().length > 0);
             const fuera = t.filter(x => { const r = x.getBoundingClientRect();
               return r.left < c.left - 1 || r.right > c.right + 1
                   || r.top < c.top - 1 || r.bottom > c.bottom + 1; });
             const lados = [...new Set(t.map(x =>
               x.querySelector('.cae-cred-fig').offsetWidth))];
             return {n: t.length, fuera: fuera.length, lados};
           }"""
    )
    check(m["n"] == 23, f"23 piezas pintadas ({m['n']})")
    check(m["fuera"] == 0, f"ninguna fuera de la caja ({m['fuera']})")
    # El tamano no codifica nada: las dos varas posibles mienten (vara global
    # infla Herramientas porque `tooling` esta en los cinco proyectos; vara por
    # territorio hace a JavaScript —una obra— tan grande como Git —cinco—).
    check(len(m["lados"]) == 1, f"un solo lado en todo el DOM ({m['lados']})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    with sync_playwright() as p:
        navegador = p.chromium.launch(
            headless=True, args=["--no-sandbox", "--use-gl=swiftshader"]
        )
        pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
        errores: list[str] = []
        pagina.on("pageerror", lambda e: errores.append(str(e)))
        pagina.on(
            "console",
            lambda m: errores.append(m.text) if m.type == "error" else None,
        )

        abre(pagina, args.base)
        gate_sin_scroll(pagina)
        gate_rotulos(pagina)
        gate_piezas(pagina)

        print("[0] consola")
        check(not errores, f"cero errores de consola ({errores[:3]})")
        navegador.close()

    print(f"\n{'TODO OK' if not FALLOS else str(len(FALLOS)) + ' FALLOS'}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
