#!/usr/bin/env python3
"""La escala tipografica de Caelestia (spec 2026-09-07-escala-tipografica).

Dos familias que se vigilan entre si:
  1. ESTATICA, sobre el fuente. Cero `font-size` con literal (en cualquier
     unidad valida para `font-size`, no solo `px`/`rem`) bajo
     `[data-theme="caelestia"]`, cero `var(--t-N, respaldo)` en todo `src/`,
     y la escala declarada EXACTAMENTE UNA VEZ y en `:root` a secas, en las
     dos hojas del repo (`themes.css` y `style.css`).
  2. VIVA, sobre el build de produccion servido. El `font-size` COMPUTADO de
     cada nodo que pinta texto propio cae en la escala.

La viva existe porque la estatica se burla sin querer: Tailwind, estilos en
linea desde TS, `style.css` y cualquier regla futura quedan fuera de una
regex sobre `themes.css`. Lo que vale es lo que se pinta.

Revision del 2026-09-08: la viva solo visitaba 1440x900 y 390x844, dos de las
~seis bandas donde Caelestia redefine tipografia por `@media`. Una regla que
aterriza en la banda equivocada (el fallo que el plan avisa DOS veces) era
invisible fuera de esos dos anchos. Se amplia a siete viewports -- 1440x900,
1366x768 (el "portatil", `max-height: 800px`), 1180x820 y 1024x768 (tableta
apaisada, `901-1365px`), 768x1024 (tableta vertical, `641-900px`), 390x844 y
390x740 (telefono, `max-width: 640px` con sus dos sub-bandas de alto) --
reutilizando el patron de dispositivos de `measure-caelestia-movil.py`. Los
dos esquemas (13:00 y 23:00) solo se barren en 1440x900 y 390x844: el
esquema cambia color, no tipografia, y duplicar las cinco bandas nuevas por
dos horas no cazaria nada que la hora sola no cace ya. Con esto el arnes
tarda ~2m35s en esta sandbox con swiftshader (medido, familia viva entera),
frente a ~50s antes de esta revision -- unos 3x, no por las horas sino por
los cinco viewports nuevos.

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
#
# El atributo `[style*="font-size"]` (no solo `#hero .cae-ln`) es lo que la
# acota de verdad: por debajo de 900px `justificarTitular()` no escribe
# `style.fontSize` (guarda explicita en `caelestia.titulo.ts`, porque el
# titular movil usa los tokens fijos `--t-3`/`--t-7` del `@media`, no la
# medida justificada), asi que esas lineas SI viven en la escala en la
# pasada movil. Con la excepcion sin acotar, un tamano en linea colandose
# ahi seguiria en verde en el unico viewport estrecho que la familia viva
# visita -- exime por lo que hace el elemento (llevar un `style` puesto),
# no por lo que podria hacer.
EXCEPCIONES = ['#hero .cae-ln[style*="font-size"]']

ESCENAS = ["hero", "quien-es", "obra", "creditos", "contacto"]

# Las siete bandas que la familia viva pisa, y por que cada una esta aqui
# (ver revision 2026-09-08 en el docstring del modulo):
#   1440x900  -- escritorio, sin @media de banda alguno
#   1366x768  -- "portatil", `@media (max-height: 800px)`
#   1180x820  -- tableta apaisada, `901-1365px`, sin cruzar el `max-height:800`
#   1024x768  -- tableta apaisada, `901-1365px`, cruza TAMBIEN `max-height:800`
#   768x1024  -- tableta vertical, `641-900px`
#   390x844   -- telefono, `max-width:640px`, no entra en `max-height:820|700`
#   390x740   -- telefono, `max-width:640px` Y `max-height:820`
# `movil` decide is_mobile/has_touch/device_scale_factor, igual que
# `measure-caelestia-movil.py`: las bandas de escritorio/tableta apaisada
# (901px en adelante) no llevan touch, las de telefono/tableta vertical si.
VIEWPORTS = [
    (1440, 900, False, (13 * 60, 23 * 60)),
    (390, 844, True, (13 * 60, 23 * 60)),
    (1366, 768, False, (13 * 60,)),
    (1180, 820, False, (13 * 60,)),
    (1024, 768, False, (13 * 60,)),
    (768, 1024, True, (13 * 60,)),
    (390, 740, True, (13 * 60,)),
]

# Unidades validas para `font-size` en CSS. `(px|rem)` dejaba pasar un
# `1.14em` bajo un selector de Caelestia en verde -- la misma forma que el
# `0.92em` real de `.ficha-s`, que solo la familia viva llego a cazar.
UNIDADES_FONT_SIZE = r"(?:px|rem|em|%|pt|ch|ex|vw|vh|vmin|vmax|cqw|cqh|cqi|cqb|cqmin|cqmax)"


def comprobar(condicion: bool, etiqueta: str) -> None:
    print(("  OK   " if condicion else "  FALLO") + f"  {etiqueta}")
    if not condicion:
        FALLOS.append(etiqueta)


def _sin_comentarios(css: str) -> str:
    """Quita los comentarios /* */ antes de buscar reglas, PRESERVANDO los
    saltos de linea (un comentario multilinea colapsado a "" desplaza el
    `L{n}` de todo lo que viene despues respecto al fichero real -- y ese
    numero es justo lo que alguien usa para depurar un fallo). `themes.css`
    cita valores de `font-size` dentro de sus propios comentarios, y
    contarlos daba tres literales fantasma en Vice."""
    def _reemplazar(m: re.Match[str]) -> str:
        return "\n" * m.group(0).count("\n")
    return re.sub(r"/\*.*?\*/", _reemplazar, css, flags=re.DOTALL)


def _literales_font_size(css: str, *, requiere: str | None) -> list[tuple[int, str, str]]:
    """Recorre `css` (ya sin comentarios) llevando el selector de la regla
    actual -- incluidos los que se escriben en varias lineas separadas por
    coma, que el seguimiento anterior perdia (`sel` se quedaba solo con la
    ULTIMA linea antes de `{`, asi que
    `:root[data-theme="caelestia"] .cae-clock,\\n.no-existe {` perdia el
    "caelestia" de la primera linea). Devuelve (numero de linea, selector,
    declaracion) para cada `font-size` literal, filtrando por `requiere` si
    se da (substring que el selector acumulado debe contener)."""
    sel = ""
    pendiente: list[str] = []
    hallazgos: list[tuple[int, str, str]] = []
    for n, linea in enumerate(css.split("\n"), 1):
        st = linea.strip()
        if "{" in st:
            antes = st.split("{", 1)[0].strip()
            partes = [p for p in (*pendiente, antes) if p]
            sel = " ".join(partes)
            pendiente = []
        elif st.endswith(","):
            pendiente.append(st.rstrip(","))
        elif st == "}":
            pendiente = []
        m = re.search(rf"font-size:\s*([0-9.]+)\s*{UNIDADES_FONT_SIZE}\s*;", linea)
        if m and (requiere is None or requiere in sel):
            hallazgos.append((n, sel, m.group(0).strip()))
    return hallazgos


def familia_estatica(raiz: pathlib.Path) -> list[str]:
    print("\n[1] Estatica: el fuente no elige tallas a ojo")
    themes_crudo = (raiz / "src/themes/themes.css").read_text(encoding="utf-8")
    themes = _sin_comentarios(themes_crudo)

    # 1a. Ni un `font-size` con literal (en NINGUNA unidad valida) bajo
    # [data-theme="caelestia"], con el selector reconstruido linea a linea
    # (ver `_literales_font_size`).
    hallados = _literales_font_size(themes, requiere="caelestia")
    literales = [f"L{n} {sel.split('] ')[-1][:40]} = {decl}" for n, sel, decl in hallados]
    comprobar(not literales, f"cero font-size literal en Caelestia ({len(literales)}: {literales[:3]})")

    # 1b. Ni un token con respaldo, en todo src/. Un token que necesita
    # respaldo no esta garantizado: son una segunda escala escondida.
    con_respaldo: list[str] = []
    for f in sorted(raiz.glob("src/**/*.css")) + sorted(raiz.glob("src/**/*.ts")):
        for n, linea in enumerate(_sin_comentarios(f.read_text(encoding="utf-8")).split("\n"), 1):
            if re.search(r"var\(--t-\d+\s*,", linea):
                con_respaldo.append(f"{f.relative_to(raiz)}:{n}")
    comprobar(not con_respaldo, f"cero var(--t-N, respaldo) en src/ ({len(con_respaldo)}: {con_respaldo[:3]})")

    # 1c/1d/1e recorren TODAS las hojas CSS del repo, no solo `themes.css`:
    # el spec exige "una vez en el repo", y una redeclaracion fantasma en
    # `style.css` seria invisible con un solo fichero -- la misma forma que
    # el fantasma `--t-0: 9px` que esta escala tuvo que cazar dentro de
    # `:root[data-theme="caelestia"]`.
    hojas = {
        "src/themes/themes.css": themes,
        "src/style.css": _sin_comentarios((raiz / "src/style.css").read_text(encoding="utf-8")),
    }

    # 1c. Ninguno de los once tokens de la escala se declara mas de una vez
    # en total, sumando las dos hojas. Antes esto solo miraba `--t-1` y solo
    # `themes.css`, asi que un `--t-0` fantasma dentro de
    # `:root[data-theme="caelestia"]` (mas especificidad que `:root` a secas,
    # y por tanto el que gana dentro de ese tema) pasaba sin que nada lo
    # cazara -- exactamente el defecto que esta escala vino a eliminar: un
    # token que vale otra cosa segun donde se lea. Se recorren los once, en
    # las dos hojas, y se exige exactamente una declaracion por token.
    decls_por_token: dict[str, list[str]] = {token: [] for token in ESCALA}
    for ruta, contenido in hojas.items():
        lineas_hoja = contenido.split("\n")
        for token in ESCALA:
            patron = re.compile(rf"^\s*{re.escape(token)}:\s")
            decls_por_token[token] += [
                f"{ruta}:{n}" for n, linea in enumerate(lineas_hoja, 1) if patron.match(linea)
            ]
    duplicados = [f"{token} ({decls})" for token, decls in decls_por_token.items() if len(decls) != 1]
    comprobar(not duplicados, f"los once tokens se declaran una sola vez cada uno, en todo el repo ({duplicados[:3]})")

    # 1d. Y esa declaracion unica cuelga de `:root` a secas. `--t-1` sirve de
    # testigo de la posicion: los once tokens viven en el mismo bloque.
    decls = decls_por_token["--t-1"]
    if len(decls) == 1:
        ruta_decl, linea_decl = decls[0].rsplit(":", 1)
        lineas_hoja = hojas[ruta_decl].split("\n")
        idx = int(linea_decl) - 1
        prof, dueno = 0, "?"
        for i in range(idx - 1, -1, -1):
            prof += lineas_hoja[i].count("}") - lineas_hoja[i].count("{")
            if prof < 0:
                dueno = lineas_hoja[i].strip()
                break
        comprobar(dueno.startswith(":root {"), f"la escala cuelga de :root a secas (cuelga de «{dueno[:40]}» en {ruta_decl})")

    # 1e. Los once tokens existen con el valor de la tabla, en la hoja donde
    # se declaran (sumando las dos, igual que 1c).
    contenido_repo = "\n".join(hojas.values())
    for token, px in ESCALA.items():
        m = re.search(rf"{re.escape(token)}:\s*([0-9.]+)px", contenido_repo)
        comprobar(m is not None and abs(float(m.group(1)) - px) < 0.005,
                  f"{token} vale {px}px (declarado: {m.group(1) + 'px' if m else 'no existe'})")
    return []


def familia_viva(navegador, base: str) -> list[str]:
    print("\n[2] Viva: lo que se PINTA cae en la escala")
    errores: list[str] = []
    for ancho, alto, movil, horas in VIEWPORTS:
        for hora in horas:
            etiqueta_hora = f"{hora // 60:02d}:{hora % 60:02d}"
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
                    f"{ancho}x{alto} {etiqueta_hora} {escena}: todo lo pintado esta en la escala "
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
    viva_ejecutada = not solo or "2" in solo
    if not solo or "1" in solo:
        errores += familia_estatica(raiz)
    if viva_ejecutada:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
            errores += familia_viva(navegador, args.base)
            navegador.close()
    # Este bloque depende de que se haya abierto un navegador: sin la
    # familia viva no hay consola que leer, y una asercion incondicional
    # aqui salia "OK" con `--solo 1` sin haber abierto nada -- no podia
    # fallar nunca en ese modo, la novena forma de instrumento tautologico
    # de este proyecto.
    if viva_ejecutada:
        print(f"\n[3] Consola sin errores")
        comprobar(not errores, f"cero errores de consola ({errores[:2]})")
    else:
        print("\n[3] Consola sin errores -- NO comprobado (--solo 1, ningun navegador se abrio)")
    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print(f"  - {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
