"""Arnes de los cimientos de "Stack" en Hyprland (spec 2026-09-09).

Trece gates, uno por familia del spec (`## Los gates`). Cada uno nacio de un
fallo real de esta pista o de otra, y ninguno se acepto sin verlo dar rojo
contra el fallo que dice cazar:

  1. Los cimientos se VEN en Hyprland, y el generico `.credits-grid` NO. Sin
     esto los demas gates se autoanulan: un nodo con `display: none` no
     desborda ni descuadra (leccion de measure-placa.py y measure-catastro.py).
  2. Los cimientos NO existen en Vice ni en Caelestia (comprobados por
     separado, no con un AND que taparia un huerfano), y la bandeja de
     Caelestia sigue con sus 23 piezas.
 13. Consola: cero errores y cero "context lost" en las TRES paginas. Sin
     oyente en Vice y Caelestia un fallo global en themes.css dejaba el gate
     en verde (pagado en measure-caelestia-cursor.py).

Los gates 3-12 se documentan en su propia funcion segun se anaden.

Nota sobre el contador de 23 nombres (gate 1): solo se comprueba SI
`[data-cimientos]` se ve. Contra el catastro actual el nodo no existe, y
contar 0 nombres sobre un dispositivo que aun no existe no es un fallo nuevo
-- es el mismo fallo que ya reporta la primera comprobacion de este gate. Sin
la condicion, el catastro daria 6 fallos (3 por viewport) en vez de los 4 que
el propio dispositivo-cero de la tarea 1 espera ver, y el tercero seria ruido
que tapa la senal real. Una vez exista `[data-cimientos]`, el contador vuelve
a mandar de verdad.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

VIEWPORTS = [("escritorio", 1440, 900), ("movil", 390, 844)]
ANCHOS_DESBORDE = [390, 821, 1024, 1200, 1440]


def abrir(b, url: str, tema: str, w: int, h: int, errores: list, reduce: bool = False):
    """Pagina nueva con oyente de consola SIEMPRE puesto. `errores` acumula
    los de todas las paginas: el gate 13 los lee al final."""
    ctx = b.new_context(
        viewport={"width": w, "height": h},
        reduced_motion="reduce" if reduce else "no-preference",
    )
    pg = ctx.new_page()
    etiqueta = f"{tema} {w}x{h}"
    pg.on(
        "console",
        lambda m: errores.append(f"[{etiqueta}] {m.type}: {m.text}")
        if m.type == "error" or "context lost" in m.text.lower()
        else None,
    )
    pg.on("pageerror", lambda e: errores.append(f"[{etiqueta}] pageerror: {e}"))
    pg.goto(f"{url}/?theme={tema}", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(9000)
    return pg


def ir_a_credits(pg, offset: int = 0) -> bool:
    """Coloca el borde superior de la escena a `offset` px del tope. Lenis
    sigue desplazando tras un scrollTo: se espera a que asiente."""
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"credits\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        return False
    pg.evaluate(f"window.scrollTo(0, {top + offset})")
    pg.wait_for_timeout(2500)
    return True


def se_ve(pg, selector: str) -> bool:
    return pg.evaluate(
        "(sel) => { const n = document.querySelector(sel); if (!n) return false;"
        " const s = getComputedStyle(n); const r = n.getBoundingClientRect();"
        " return s.display !== 'none' && s.visibility !== 'hidden'"
        "   && parseFloat(s.opacity) > 0 && r.width > 0 && r.height > 0; }",
        selector,
    )


def gate_1_se_ven(pg, nombre: str, fallos: list) -> None:
    cimientos_visibles = se_ve(pg, "[data-cimientos]")
    if not cimientos_visibles:
        fallos.append(f"[{nombre}] gate 1: [data-cimientos] NO se ve en Hyprland")
    if se_ve(pg, ".credits-grid"):
        fallos.append(f"[{nombre}] gate 1: el generico .credits-grid SE PINTA bajo Hyprland")
    if cimientos_visibles:
        n = pg.evaluate("() => document.querySelectorAll('[data-cimientos] .cim-nombre').length")
        if n != 23:
            fallos.append(f"[{nombre}] gate 1: {n} nombres en los cimientos, esperados 23")


def gate_2_no_existen_en_otros(b, url: str, errores: list, fallos: list) -> None:
    for tema in ("vice", "caelestia"):
        pg = abrir(b, url, tema, 1440, 900, errores)
        ir_a_credits(pg)
        if se_ve(pg, "[data-cimientos]"):
            fallos.append(f"[{tema}] gate 2: [data-cimientos] esta VISIBLE y no deberia")
        if tema == "caelestia":
            piezas = pg.evaluate("() => document.querySelectorAll('.cae-cred-pieza').length")
            if piezas != 23:
                fallos.append(f"[caelestia] gate 2: la bandeja tiene {piezas} piezas, esperadas 23")
        pg.context.close()


ESCALA = [12, 16, 21.33, 28.43, 37.9, 50.52, 67.4, 89.85, 119.77, 159.66]
DIANA_MINIMA = 44

GEOMETRIA_JS = """() => {
  const cim = document.querySelector('[data-cimientos]');
  if (!cim) return null;
  const r = e => { const b = e.getBoundingClientRect(); return {l: b.left, t: b.top, r: b.right, b: b.bottom, w: b.width, h: b.height}; };
  const visible = e => { const s = getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden' && e.getClientRects().length > 0; };
  const caja = r(cim);
  const cols = Array.from(cim.querySelectorAll('.cim-col')).map(r);
  const suelo = r(cim.querySelector('.cim-linea'));
  const fuera = Array.from(cim.querySelectorAll('.cim-txt, .cim-rot, .cim-frase, .cim-icono'))
    .filter(visible)
    .map(e => ({ t: e.textContent.trim().slice(0, 24), ...r(e) }))
    .filter(x => x.l < caja.l - 1 || x.r > caja.r + 1 || x.t < caja.t - 1 || x.b > caja.b + 1);
  const tallas = Array.from(cim.querySelectorAll('*'))
    .filter(e => e.childElementCount === 0 && e.textContent.trim() && visible(e))
    .map(e => ({ t: e.textContent.trim().slice(0, 24), s: parseFloat(getComputedStyle(e).fontSize) }));
  const dianas = Array.from(cim.querySelectorAll('.cim-nombre')).filter(visible).map(e => r(e).h);
  return { caja, cols, suelo, fuera, tallas, dianas };
}"""


def gate_7_8_9_12_geometria(pg, nombre: str, w: int, fallos: list) -> None:
    """7: nada desborda la caja de [data-cimientos], medido con rects, nunca
    con scrollWidth/scrollHeight (mienten con un transform dentro de un
    overflow: clip, pagado en B6). 8: las columnas nacen a la misma cota y el
    suelo esta a 48px del pie de la mas alta (solo en escritorio). 9: tallas
    en la escala. 12: diana tactil >= 44px en movil, solo sobre visibles."""
    g = pg.evaluate(GEOMETRIA_JS)
    if g is None:
        fallos.append(f"[{nombre}] gates 7-12: no existe [data-cimientos]")
        return
    for x in g["fuera"]:
        fallos.append(f"[{nombre}] gate 7: '{x['t']}' desborda la caja de los cimientos")
    if w >= 821:
        if len(g["cols"]) != 3:
            fallos.append(f"[{nombre}] gate 8: {len(g['cols'])} columnas, esperadas 3")
        else:
            tops = {round(c["t"]) for c in g["cols"]}
            if len(tops) != 1:
                fallos.append(f"[{nombre}] gate 8: las columnas no nacen a la misma cota: {sorted(tops)}")
            pie = max(c["b"] for c in g["cols"])
            aire = g["suelo"]["t"] - pie
            if abs(aire - 48) > 1:
                fallos.append(f"[{nombre}] gate 8: el suelo esta a {aire:.1f}px del pie de las columnas, esperados 48")
    for t in g["tallas"]:
        if not any(abs(t["s"] - paso) < 0.06 for paso in ESCALA):
            fallos.append(f"[{nombre}] gate 9: '{t['t']}' a {t['s']}px, fuera de la escala")
    if w < 821:
        if not g["dianas"]:
            fallos.append(f"[{nombre}] gate 12: ningun nombre visible que medir")
        elif min(g["dianas"]) < DIANA_MINIMA:
            fallos.append(f"[{nombre}] gate 12: diana tactil minima {min(g['dianas']):.1f}px, piso {DIANA_MINIMA}")


ENTRADA_JS = """() => {
  const cim = document.querySelector('[data-cimientos]');
  if (!cim) return null;
  const linea = cim.querySelector('.cim-linea');
  const cols = Array.from(cim.querySelectorAll('.cim-col'));
  const lens = Array.from(cim.querySelectorAll('.cim-lenguajes .cim-txt'));
  const tf = getComputedStyle(linea).transform;
  return {
    top: cim.getBoundingClientRect().top, innerH: innerHeight,
    lit: cim.classList.contains('cimientos-lit'),
    lineaTrazada: tf === 'none' || /matrix\\(1,/.test(tf),
    colsAbiertas: cols.filter(c => { const cp = getComputedStyle(c).clipPath; return cp === 'none' || cp === 'inset(0px)' || cp === 'inset(0px 0px 0px 0px)'; }).length,
    lensEncendidos: lens.filter(t => getComputedStyle(t).color === 'rgb(255, 234, 230)').length,
  };
}"""


def gate_3_la_entrada_se_ve(b, url: str, errores: list, fallos: list) -> None:
    """Paso A: seccion encendida (is-lit) y los cimientos ENTEROS bajo el
    pliegue; tras 1500ms nada ha arrancado (asentamiento tras el scroll, la
    asercion es que NADA paso, asi que un tiempo fijo aqui solo endurece la
    prueba). Paso B: los cimientos al 80% y se sondea el estado DENTRO de la
    pagina (sin ida y vuelta de Playwright por muestra) hasta que aterriza o
    se agota una fecha limite de 6000ms, que es un tope de FALLO, nunca un
    tiempo de espera. Anclado a ESTADO de verdad en los dos pasos (con
    setTimeout fijo el gate 13 de B5 salia rojo bajo carga y verde en vacio,
    y este mismo gate 3 tuvo el mismo defecto en su paso B hasta la ronda de
    arreglo 1: el docstring decia "anclado a estado" mientras el corte era un
    wait_for_timeout(2500) fijo, con solo 900ms de margen sobre el peor caso
    real de la coreografia -- 520 + 2*90 + 900 = 1600ms). Si el paso A no
    puede colocar los cimientos bajo el pliegue, el arnes FALLA en vez de
    medir otra cosa."""
    for nombre, w, h in VIEWPORTS:
        pg = abrir(b, url, "hyprland", w, h, errores)
        top = pg.evaluate(
            "() => { const c = document.querySelector('[data-cimientos]');"
            " return c ? c.getBoundingClientRect().top + window.scrollY : -1; }"
        )
        if top < 0:
            fallos.append(f"[{nombre}] gate 3: no existe [data-cimientos]")
            pg.context.close()
            continue
        # A: la seccion pasa el 90% (is-lit) pero los cimientos quedan enteros bajo el pliegue
        seccion_top = pg.evaluate(
            "() => document.querySelector('[data-scene=\"credits\"]').getBoundingClientRect().top + window.scrollY"
        )
        pg.evaluate(f"window.scrollTo(0, {seccion_top - h * 0.9 + 20})")
        pg.wait_for_timeout(1500)
        a = pg.evaluate(ENTRADA_JS)
        if a["top"] < a["innerH"]:
            fallos.append(f"[{nombre}] gate 3: el arnes no pudo dejar los cimientos bajo el pliegue (top {a['top']:.0f} < {a['innerH']})")
        elif a["lit"] or a["lineaTrazada"] or a["colsAbiertas"] > 0 or a["lensEncendidos"] > 0:
            fallos.append(
                f"[{nombre}] gate 3 paso A: la entrada arranco con los cimientos bajo el pliegue "
                f"(lit={a['lit']}, linea={a['lineaTrazada']}, cols={a['colsAbiertas']}, lenguajes={a['lensEncendidos']})"
            )
        # B: los cimientos al 80%. Anclado a ESTADO: se sondea DENTRO de la
        # pagina hasta que aterriza, con fecha limite de FALLO (no de espera).
        pg.evaluate(f"window.scrollTo(0, {top - h * 0.8 + 40})")
        bst = pg.evaluate(
            f"""async () => {{
              const leer = {ENTRADA_JS};
              const dl = performance.now() + 6000;
              let ult = leer();
              while (performance.now() < dl) {{
                ult = leer();
                if (ult.lit && ult.lineaTrazada && ult.colsAbiertas === 3 && ult.lensEncendidos === 5) {{
                  return {{ ok: true, ...ult }};
                }}
                await new Promise(r => setTimeout(r, 25));
              }}
              return {{ ok: false, ...ult }};
            }}"""
        )
        if not bst["ok"]:
            fallos.append(
                f"[{nombre}] gate 3 paso B: la entrada no aterrizo en 6000ms "
                f"(lit={bst['lit']}, linea={bst['lineaTrazada']}, cols={bst['colsAbiertas']}/3, lenguajes={bst['lensEncendidos']}/5)"
            )
        pg.context.close()


def gate_7_anchos(b, url: str, errores: list, fallos: list) -> None:
    """El desborde se mide en los cinco anchos del spec, no solo en los dos
    viewports principales: el hueco 1200-1439 del cartel se pago por no
    ejercitar el tramo intermedio."""
    for w in ANCHOS_DESBORDE:
        pg = abrir(b, url, "hyprland", w, 900, errores)
        if ir_a_credits(pg):
            g = pg.evaluate(GEOMETRIA_JS)
            if g is None:
                fallos.append(f"[{w}px] gate 7: no existe [data-cimientos]")
            else:
                for x in g["fuera"]:
                    fallos.append(f"[{w}px] gate 7: '{x['t']}' desborda la caja de los cimientos")
        pg.context.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:4173")
    ap.add_argument("--contraste", action="store_true", help="gate 10 (hallazgo de producto abierto)")
    args = ap.parse_args()

    fallos: list[str] = []
    errores: list[str] = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])

        for nombre, w, h in VIEWPORTS:
            pg = abrir(b, args.url, "hyprland", w, h, errores)
            if not ir_a_credits(pg):
                fallos.append(f"[{nombre}] no existe [data-scene=credits]")
                pg.context.close()
                continue
            gate_1_se_ven(pg, nombre, fallos)
            gate_7_8_9_12_geometria(pg, nombre, w, fallos)
            pg.context.close()

        gate_2_no_existen_en_otros(b, args.url, errores, fallos)
        gate_7_anchos(b, args.url, errores, fallos)
        gate_3_la_entrada_se_ve(b, args.url, errores, fallos)
        b.close()

    for e in errores:
        fallos.append(f"gate 13: consola: {e}")

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
