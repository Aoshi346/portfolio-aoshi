#!/usr/bin/env python3
"""La escala tipografica de Caelestia (spec 2026-09-07-escala-tipografica).

Dos familias que se vigilan entre si:
  1. ESTATICA, sobre el fuente. Cero `font-size` con literal bajo
     `[data-theme="caelestia"]`, cero `var(--t-N, respaldo)` en todo `src/`,
     y la escala declarada EXACTAMENTE UNA VEZ y en `:root` a secas.
  2. VIVA, sobre el build de produccion servido. El `font-size` COMPUTADO de
     cada nodo que pinta texto propio cae en la escala.

La viva existe porque la estatica se burla sin querer: Tailwind, estilos en
linea desde TS, `style.css` y cualquier regla futura quedan fuera de una
regex sobre `themes.css`. Lo que vale es lo que se pinta.

  npm run build && npx vite preview --port 4173 &
  python3 scripts/measure-escala-tipografica.py --base http://127.0.0.1:4173
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

FALLOS: list[str] = []

# La escala, en px. Es la tabla del spec y la fuente de verdad del arnes.
ESCALA = {
    "--t-00": 9.5,
    "--t-0": 10.67,
    "--t-1": 12.0,
    "--t-2": 16.0,
    "--t-3": 21.33,
    "--t-4": 28.43,
    "--t-5": 37.9,
    "--t-6": 50.52,
    "--t-7": 67.4,
    "--t-8": 89.85,
    "--t-9": 119.77,
    "--t-10": 159.66,
}
VALORES = sorted(ESCALA.values())

# La UNICA excepcion, y es por selector concreto, nunca por categoria: el
# titular de B1 se justifica midiendo el texto y estirandolo hasta la medida
# (`caelestia.titulo.ts:48-52`), asi que su tamano lo decide el ancho de la
# caja y no puede estar en la escala por construccion. Si aparece un segundo
# elemento con tamano en linea, este gate se pone rojo, que es el objetivo.
EXCEPCIONES = ["#hero .cae-ln"]

ESCENAS = ["hero", "quien-es", "obra", "creditos", "contacto"]


def comprobar(condicion: bool, etiqueta: str) -> None:
    print(("  OK   " if condicion else "  FALLO") + f"  {etiqueta}")
    if not condicion:
        FALLOS.append(etiqueta)


def _sin_comentarios(css: str) -> str:
    """Quita los comentarios /* */ antes de buscar reglas: `themes.css` cita
    valores de `font-size` dentro de sus propios comentarios, y contarlos daba
    tres literales fantasma en Vice."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def familia_estatica(raiz: pathlib.Path) -> list[str]:
    print("\n[1] Estatica: el fuente no elige tallas a ojo")
    themes = _sin_comentarios((raiz / "src/themes/themes.css").read_text(encoding="utf-8"))

    # 1a. Ni un `font-size` con literal bajo [data-theme="caelestia"].
    sel = ""
    literales: list[str] = []
    for n, linea in enumerate(themes.split("\n"), 1):
        st = linea.strip()
        if st.endswith("{"):
            sel = st[:-1].strip()
        m = re.search(r"font-size:\s*([0-9.]+)(px|rem)\s*;", linea)
        if m and "caelestia" in sel:
            literales.append(f"L{n} {sel.split('] ')[-1][:40]} = {m.group(0).strip()}")
    comprobar(not literales, f"cero font-size literal en Caelestia ({len(literales)}: {literales[:3]})")

    # 1b. Ni un token con respaldo, en todo src/. Un token que necesita
    # respaldo no esta garantizado: son una segunda escala escondida.
    con_respaldo: list[str] = []
    for f in sorted(raiz.glob("src/**/*.css")) + sorted(raiz.glob("src/**/*.ts")):
        for n, linea in enumerate(_sin_comentarios(f.read_text(encoding="utf-8")).split("\n"), 1):
            if re.search(r"var\(--t-\d+\s*,", linea):
                con_respaldo.append(f"{f.relative_to(raiz)}:{n}")
    comprobar(not con_respaldo, f"cero var(--t-N, respaldo) en src/ ({len(con_respaldo)}: {con_respaldo[:3]})")

    # 1c. Ninguno de los doce tokens de la escala se declara mas de una vez
    # en todo el fichero. Antes esto solo miraba `--t-1`, asi que un
    # `--t-0` fantasma dentro de `:root[data-theme="caelestia"]` (mas
    # especificidad que `:root` a secas, y por tanto el que gana dentro de
    # ese tema) pasaba sin que nada lo cazara -- exactamente el defecto que
    # esta escala vino a eliminar: un token que vale otra cosa segun donde
    # se lea. Se recorren los doce y se exige exactamente una declaracion
    # por token, no solo del que se usaba como testigo de la posicion.
    lineas = themes.split("\n")
    decls_por_token: dict[str, list[int]] = {}
    for token in ESCALA:
        patron = re.compile(rf"^\s*{re.escape(token)}:\s")
        decls_por_token[token] = [n for n, linea in enumerate(lineas, 1) if patron.match(linea)]
    duplicados = [f"{token} ({decls})" for token, decls in decls_por_token.items() if len(decls) != 1]
    comprobar(not duplicados, f"los doce tokens se declaran una sola vez cada uno ({duplicados[:3]})")

    # 1d. Y esa declaracion unica cuelga de `:root` a secas. `--t-1` sirve de
    # testigo de la posicion: los doce tokens viven en el mismo bloque.
    decls = decls_por_token["--t-1"]
    if len(decls) == 1:
        prof, dueno = 0, "?"
        for i in range(decls[0] - 2, -1, -1):
            prof += lineas[i].count("}") - lineas[i].count("{")
            if prof < 0:
                dueno = lineas[i].strip()
                break
        comprobar(dueno.startswith(":root {"), f"la escala cuelga de :root a secas (cuelga de «{dueno[:40]}»)")

    # 1e. Los doce tokens existen con el valor de la tabla.
    for token, px in ESCALA.items():
        m = re.search(rf"{re.escape(token)}:\s*([0-9.]+)px", themes)
        comprobar(m is not None and abs(float(m.group(1)) - px) < 0.005,
                  f"{token} vale {px}px (declarado: {m.group(1) + 'px' if m else 'no existe'})")
    return []


def familia_viva(navegador, base: str) -> list[str]:
    print("\n[2] Viva: lo que se PINTA cae en la escala")
    errores: list[str] = []
    for ancho, alto, movil in ((1440, 900, False), (390, 844, True)):
        for hora, etiqueta in ((13 * 60, "13:00"), (23 * 60, "23:00")):
            kwargs = {"viewport": {"width": ancho, "height": alto}}
            if movil:
                kwargs |= {"device_scale_factor": 2, "is_mobile": True, "has_touch": True}
            ctx = navegador.new_context(**kwargs)
            pg = ctx.new_page()
            pg.on("pageerror", lambda e: errores.append(str(e)))
            pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            try:
                pg.wait_for_function(
                    "document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000
                )
            except Exception:
                pg.wait_for_timeout(3000)
            pg.evaluate("(m) => window.__CAE_SET_MINUTOS__(m)", hora)
            pg.wait_for_timeout(600)
            for escena in ESCENAS:
                pg.click(f'[data-cae-ws="{escena}"]')
                pg.wait_for_timeout(1600)
                fuera = pg.evaluate(
                    """([valores, excepciones]) => {
                        const ws = [...document.querySelectorAll('main[data-cae-track] > *')].find(e => !e.inert);
                        if (!ws) return null;
                        const raiz = [ws, document.querySelector('.cae-bar'), document.querySelector('.cae-dock')];
                        const malos = [];
                        for (const r of raiz) {
                            if (!r) continue;
                            for (const e of [r, ...r.querySelectorAll('*')]) {
                                if (e.getClientRects().length === 0) continue;
                                if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
                                if (excepciones.some(s => e.matches(s))) continue;
                                const px = parseFloat(getComputedStyle(e).fontSize);
                                if (!valores.some(v => Math.abs(v - px) < 0.01)) {
                                    malos.push(e.tagName + '.' + String(e.className).slice(0, 30) + ' = ' + px.toFixed(2) + 'px');
                                }
                            }
                        }
                        return malos;
                    }""",
                    [VALORES, EXCEPCIONES],
                )
                comprobar(
                    fuera is not None and not fuera,
                    f"{ancho}x{alto} {etiqueta} {escena}: todo lo pintado esta en la escala "
                    f"({len(fuera or [])} fuera, p.ej. {(fuera or [])[:3]})",
                )
            ctx.close()
    return errores


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:4173")
    ap.add_argument("--solo", default="", help="familias a correr: 1, 2")
    args = ap.parse_args()
    solo = {x.strip() for x in args.solo.split(",") if x.strip()}
    raiz = pathlib.Path(__file__).resolve().parent.parent
    errores: list[str] = []
    if not solo or "1" in solo:
        errores += familia_estatica(raiz)
    if not solo or "2" in solo:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
            errores += familia_viva(navegador, args.base)
            navegador.close()
    print(f"\n[3] Consola sin errores")
    comprobar(not errores, f"cero errores de consola ({errores[:2]})")
    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print(f"  - {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
