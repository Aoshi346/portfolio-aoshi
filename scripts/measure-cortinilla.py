#!/usr/bin/env python3
"""Arnes de la hoja de contactos (cortinilla de Hyprland).

Criterios 3 y 4 del spec 2026-08-06-hyprland-cortinilla-hoja-design.md.
Se lanza contra el dev server o contra el build servido. NO usa capturas para
medir animacion: eso llega en la Tarea 4 y muestrea desde dentro de la pagina.
"""
import json
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:5173/?theme=hyprland"
CHROME = "/usr/bin/google-chrome"

# Diferencia maxima tolerada, en px CSS, entre el ancho del encuadre y el
# ancho al que renderiza el plano de 1440x900 una vez escalado. Un factor de
# escala fijo (ver Hallazgo 1) deja hasta 52px vacios en un encuadre de 268px;
# 2px cubre el redondeo normal de `getBoundingClientRect()`/`calc()`, nada mas.
TOLERANCIA_ESCALA = 2

LAYOUT_JS = """() => {
  const panel = document.querySelector('.scene-index');
  const filas = [...panel.querySelectorAll('.scene-index-row')];
  const r = e => { const b = e.getBoundingClientRect();
    return {w: Math.round(b.width), h: Math.round(b.height),
            t: Math.round(b.top), l: Math.round(b.left)}; };
  const primeraFila = filas[0];
  const encuadre = primeraFila?.querySelector('.scene-shot');
  const encuadreRect = encuadre ? encuadre.getBoundingClientRect() : null;
  // El primer hijo NO beam: `.scene-shot-beam` lleva `transform: none` a
  // proposito (cruza el encuadre completo sin escalarse), asi que no sirve
  // para leer el factor de escala real. Cualquier otro hijo si lo lleva.
  const hijoEscalado = encuadre
    ? [...encuadre.children].find(c => !c.classList.contains('scene-shot-beam'))
    : null;
  const matriz = hijoEscalado ? getComputedStyle(hijoEscalado).transform : null;
  // `matrix(a, b, c, d, e, f)` -> el factor de escala horizontal es `a`.
  const escalaX = matriz && matriz.startsWith('matrix(')
    ? parseFloat(matriz.slice(7).split(',')[0])
    : null;
  return {
    filas: filas.map(r),
    rejilla: r(panel),
    scrollInterno: panel.scrollHeight > panel.clientHeight + 1,
    desbordes: filas.map(f => { const b = f.querySelector('.scene-index-blurb');
      return b.scrollWidth > b.clientWidth; }),
    orderUsado: filas.some(f => getComputedStyle(f).order !== '0'),
    paradas: filas.length,
    siluetasVacias: filas.filter(f => {
      const s = f.querySelector('.scene-shot');
      return !s || s.children.length === 0; }).length,
    ariaOcultas: filas.every(f =>
      f.querySelector('.scene-shot')?.getAttribute('aria-hidden') === 'true'),
    ultimaEsContacto: filas[filas.length - 1]?.hash === '#contacto',
    // --- Hallazgo 1 (rejilla fluida + escala de la silueta) ---
    panelDisplay: getComputedStyle(panel).display,
    columnas: getComputedStyle(panel).gridTemplateColumns.trim().split(/\\s+/).length,
    siluetaDisplay: encuadre ? getComputedStyle(encuadre).display : null,
    encuadreAncho: encuadreRect ? encuadreRect.width : null,
    encuadreAlto: encuadreRect ? encuadreRect.height : null,
    escalaX: escalaX,
    planoRenderizadoAncho: escalaX !== null ? escalaX * 1440 : null,
  };
}"""


def abrir(pw, ancho, alto, reducido=False):
    b = pw.chromium.launch(headless=True, executable_path=CHROME,
                           args=["--no-sandbox", "--use-gl=swiftshader"])
    ctx = b.new_context(viewport={"width": ancho, "height": alto},
                        reduced_motion="reduce" if reducido else "no-preference")
    pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded", timeout=40000)
    pg.wait_for_timeout(9000)  # encendido de Ascua + shader
    return b, pg


def abrir_cortinilla(pg):
    pg.click(".scene-nav-trigger")
    pg.wait_for_timeout(1200)


def medir_layout(ancho, alto):
    with sync_playwright() as pw:
        b, pg = abrir(pw, ancho, alto)
        abrir_cortinilla(pg)
        datos = pg.evaluate(LAYOUT_JS)
        caja = pg.locator(".scene-nav-trigger").bounding_box()
        b.close()
    datos["disparador"] = {"w": round(caja["width"], 1), "h": round(caja["height"], 1)}
    return datos


def comprobar(datos, ancho):
    fallos = []
    if datos["paradas"] != 5:
        fallos.append(f"{ancho}: hay {datos['paradas']} filas, deben ser 5")
    if datos["scrollInterno"]:
        fallos.append(f"{ancho}: el panel tiene scroll interno (prohibido, ver spec)")
    if any(datos["desbordes"]):
        fallos.append(f"{ancho}: descriptores desbordados: {datos['desbordes']}")
    if datos["orderUsado"]:
        fallos.append(f"{ancho}: se ha usado `order` en la rejilla (prohibido)")
    if datos["siluetasVacias"]:
        fallos.append(f"{ancho}: {datos['siluetasVacias']} siluetas vacias")
    if not datos["ariaOcultas"]:
        fallos.append(f"{ancho}: alguna silueta sin aria-hidden")
    if not datos["ultimaEsContacto"]:
        fallos.append(f"{ancho}: la ultima fila del DOM no es contacto")
    d = datos["disparador"]
    if d["w"] < 44 or d["h"] < 44:
        fallos.append(f"{ancho}: disparador {d['w']}x{d['h']}, minimo 44x44")

    # --- Hallazgo 1/2: la rejilla es de verdad una rejilla, y la silueta
    # llena el encuadre en vez de sobrar un margen fijo. ---
    if datos["panelDisplay"] != "grid":
        fallos.append(f"{ancho}: .scene-index no es display:grid ({datos['panelDisplay']})")
    columnas_esperadas = 2 if ancho <= 640 else 5
    if datos["columnas"] != columnas_esperadas:
        fallos.append(
            f"{ancho}: {datos['columnas']} columnas en la rejilla, "
            f"se esperaban {columnas_esperadas}"
        )
    if datos["siluetaDisplay"] == "none":
        fallos.append(f"{ancho}: la silueta (.scene-shot) esta oculta (display:none)")
    if datos["encuadreAncho"] is not None and datos["planoRenderizadoAncho"] is not None:
        diff = abs(datos["planoRenderizadoAncho"] - datos["encuadreAncho"])
        if diff > TOLERANCIA_ESCALA:
            fallos.append(
                f"{ancho}: el plano renderiza a {datos['planoRenderizadoAncho']:.1f}px "
                f"pero el encuadre mide {datos['encuadreAncho']:.1f}px "
                f"(diferencia {diff:.1f}px > {TOLERANCIA_ESCALA}px)"
            )
    else:
        fallos.append(f"{ancho}: no se pudo leer la escala del primer hijo escalado")
    if datos["encuadreAncho"] and datos["encuadreAlto"]:
        proporcion = datos["encuadreAlto"] / datos["encuadreAncho"]
        if abs(proporcion - 0.625) > 0.01:
            fallos.append(
                f"{ancho}: el encuadre no respeta 16:10 (alto/ancho={proporcion:.3f}, "
                f"se esperaba 0.625 +-0.01)"
            )
    return fallos


def main():
    fallos = []
    for ancho, alto in ((1440, 900), (390, 844)):
        datos = medir_layout(ancho, alto)
        print(f"== {ancho}x{alto}")
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        fallos += comprobar(datos, ancho)
    if fallos:
        print("\nFALLOS:")
        for f in fallos:
            print(" -", f)
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
