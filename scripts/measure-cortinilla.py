#!/usr/bin/env python3
"""Arnes de la hoja de contactos (cortinilla de Hyprland).

Criterios 3 y 4 del spec 2026-08-06-hyprland-cortinilla-hoja-design.md. Se
lanza SIEMPRE contra el build SERVIDO (`--base`, obligatorio para el arnes
entero) -- nunca contra el dev server de Vite, cuyo HMR corrompe el layout
(ver `_es_dev_server`). NO usa capturas para medir animacion: eso llega en la
Tarea 4 y muestrea desde dentro de la pagina.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

CHROME = "/usr/bin/google-chrome"
RAIZ = Path(__file__).parent.parent

# NO hay URL por defecto: `--base` es obligatorio para el arnes ENTERO (ver
# `main()`), no solo para la seccion de firmas. Antes solo la seccion de
# firmas respetaba `--base`; las seis familias preexistentes (layout,
# sincronia, tiempos, estados/foco, ajenos, contraste) seguian midiendo
# contra este literal -- incluidas las que miden la GEOMETRIA de las
# siluetas, que son justo las que tendrian que haber cazado el defecto de
# `obra` saliendose del plano. El comando documentado en
# `rules/verification.md` (`--base http://localhost:4173`, build servido, sin
# dev server) reventaba con connection refused antes de llegar a las firmas.
def _url(base, tema="hyprland"):
    return f"{base}/?theme={tema}"

# Diferencia maxima tolerada, en px CSS, entre el ancho del encuadre y el
# ancho al que renderiza el plano de 1440x900 una vez escalado. Un factor de
# escala fijo (ver Hallazgo 1) deja hasta 52px vacios en un encuadre de 268px;
# 2px cubre el redondeo normal de `getBoundingClientRect()`/`calc()`, nada mas.
TOLERANCIA_ESCALA = 2

# El haz debe cubrir el encuadre entero. 1% de margen para el redondeo de
# `getBoundingClientRect()`; el defecto real cubria 0,18 del ancho.
TOLERANCIA_HAZ = 0.01

LAYOUT_JS = """() => {
  const panel = document.querySelector('.scene-index');
  const filas = [...panel.querySelectorAll('.scene-index-row')];
  const r = e => { const b = e.getBoundingClientRect();
    return {w: Math.round(b.width), h: Math.round(b.height),
            t: Math.round(b.top), l: Math.round(b.left)}; };
  /*
   * Se mide CADA UNA de las cinco siluetas, no `filas[0]`.
   *
   * Mirar solo la primera dejaba entrar en verde exactamente los dos defectos
   * que esta rama ya pago: con el plano de las filas 2-5 roto, 106 de 113
   * piezas caian fuera del encuadre y el arnes seguia verde; con el haz
   * encogido en esas filas, tambien. Un arnes que vigila un quinto de lo que
   * dice vigilar es peor que no tenerlo, porque se lee como cobertura.
   */
  const mide = fila => {
    const encuadre = fila.querySelector('.scene-shot');
    if (!encuadre) return null;
    const er = encuadre.getBoundingClientRect();
    const plano = encuadre.querySelector('.scene-shot-plano');
    const haz = encuadre.querySelector('.scene-shot-beam');
    // El ancho renderizado del plano se MIDE, no se deduce multiplicando la
    // escala por un 1440 escrito aqui. Ese literal vive tambien en el CSS
    // (`.scene-shot-plano { width: 1440px }`) y son dos sitios que hay que
    // cambiar a la vez sin nada que avise — el patron `OBRA_TRANSIT` que
    // CLAUDE.md documenta. Comprobado: con el plano a 1280px el arnes salia
    // verde dejando un 11% del encuadre vacio.
    const pr = plano ? plano.getBoundingClientRect() : null;
    const cs = plano ? getComputedStyle(plano).transform : null;
    const escala = cs && cs.startsWith('matrix(')
      ? parseFloat(cs.slice(7).split(',')[0]) : null;
    const piezas = plano
      ? [...plano.children].filter(x => getComputedStyle(x).display !== 'none')
      : [];
    /*
     * El recorte VERTICAL puede ser legitimo y el HORIZONTAL nunca lo es.
     *
     * El plano es 16:10 y el encuadre tambien... salvo el quinto en movil, que
     * es un panoramico a proposito (`padding-top: 31.25%`). Como la escala se
     * deriva del ancho, ese fotograma ensena una banda del plano y deja fuera
     * el resto: es un encuadre distinto de la misma escena, no un defecto.
     * Medido: 8 de sus 10 piezas caen por debajo, y la silueta se ve bien.
     *
     * Lo que no admite excusa es que una pieza se salga por los lados: eso
     * significa que el plano no esta alineado o no esta escalado al ancho, que
     * es justo el defecto que esta rama pago dos veces. Se separan los dos.
     */
    // Deteccion de recorte PARCIAL, no solo de pieza enteramente fuera.
    // La version anterior (`b.left > er.right - 1 || b.right < er.left + 1`)
    // solo contaba una pieza si el encuadre y la pieza no se tocaban en
    // absoluto -- eso deja pasar el defecto real de `obra`: dos piezas que
    // SI se solapaban con el encuadre pero se salian por un borde (la quinta
    // fila y su miniatura, cortadas por `overflow: hidden`), asi que este
    // arnes nunca las vio pese a estar vigilando la geometria exacta que las
    // contenia. Ahora cualquier pieza cuyo borde asome fuera del encuadre
    // cuenta, este total o parcialmente fuera.
    const fueraX = piezas.filter(x => {
      const b = x.getBoundingClientRect();
      return b.left < er.left - 1 || b.right > er.right + 1;
    });
    const fueraY = piezas.filter(x => {
      const b = x.getBoundingClientRect();
      return b.top < er.top - 1 || b.bottom > er.bottom + 1;
    });
    return {
      escena: fila.hash,
      encuadreAncho: er.width,
      encuadreAlto: er.height,
      siluetaDisplay: getComputedStyle(encuadre).display,
      escalaX: escala,
      planoRenderizadoAncho: pr ? pr.width : null,
      haz: haz && er.width
        ? (() => { const b = haz.getBoundingClientRect();
            return {ancho: b.width, alto: b.height,
                    cubreAncho: b.width / er.width,
                    cubreAlto: b.height / er.height}; })()
        : null,
      piezasFuera: plano
        ? {total: piezas.length, fueraX: fueraX.length, fueraY: fueraY.length}
        : null,
    };
  };
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
    siluetas: filas.map(mide),
  };
}"""


def abrir(pw, ancho, alto, base, reducido=False):
    b = pw.chromium.launch(headless=True, executable_path=CHROME,
                           args=["--no-sandbox", "--use-gl=swiftshader"])
    ctx = b.new_context(viewport={"width": ancho, "height": alto},
                        reduced_motion="reduce" if reducido else "no-preference")
    pg = ctx.new_page()
    pg.goto(_url(base), wait_until="domcontentloaded", timeout=40000)
    pg.wait_for_timeout(9000)  # encendido de Ascua + shader
    return b, pg


def abrir_cortinilla(pg):
    pg.click(".scene-nav-trigger")
    pg.wait_for_timeout(1200)


def medir_layout(ancho, alto, base):
    with sync_playwright() as pw:
        b, pg = abrir(pw, ancho, alto, base)
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
    # Las CINCO siluetas, una por una. Antes esto miraba `filas[0]` y dejaba
    # pasar en verde los dos defectos historicos si ocurrian en las filas 2-5.
    for s in datos["siluetas"]:
        if s is None:
            fallos.append(f"{ancho}: una fila no tiene `.scene-shot`")
            continue
        eti = f"{ancho} {s['escena']}"
        if s["siluetaDisplay"] == "none":
            fallos.append(f"{eti}: la silueta esta oculta (display:none)")
            continue
        if s["planoRenderizadoAncho"] is None:
            fallos.append(f"{eti}: no hay `.scene-shot-plano`")
            continue
        if s["escalaX"] is None:
            fallos.append(
                f"{eti}: el plano no lleva escala (`transform` sin matriz). Se dibuja a "
                f"1440x900 dentro de un encuadre de {s['encuadreAncho']:.0f}px"
            )
        diff = abs(s["planoRenderizadoAncho"] - s["encuadreAncho"])
        if diff > TOLERANCIA_ESCALA:
            fallos.append(
                f"{eti}: el plano renderiza a {s['planoRenderizadoAncho']:.1f}px pero el "
                f"encuadre mide {s['encuadreAncho']:.1f}px "
                f"(diferencia {diff:.1f}px > {TOLERANCIA_ESCALA}px)"
            )
        if s["encuadreAncho"] and s["encuadreAlto"]:
            proporcion = s["encuadreAlto"] / s["encuadreAncho"]
            # El quinto fotograma es mas ancho que alto a proposito en movil.
            esperada = 0.3125 if (ancho <= 640 and s["escena"] == "#contacto") else 0.625
            if abs(proporcion - esperada) > 0.01:
                fallos.append(
                    f"{eti}: el encuadre no respeta la proporcion "
                    f"(alto/ancho={proporcion:.3f}, se esperaba {esperada})"
                )
        pf = s["piezasFuera"]
        if pf is None:
            fallos.append(f"{eti}: no se pudieron leer las piezas del plano")
        elif pf["total"] == 0:
            # `siluetasVacias` cuenta hijos del DOM y no distingue oculto de
            # dibujado: es vacuo desde que existe `.scene-shot-plano`, que
            # siempre esta. Esta comprobacion no.
            fallos.append(f"{eti}: la silueta no dibuja ni una pieza")
        else:
            if pf["fueraX"]:
                fallos.append(
                    f"{eti}: {pf['fueraX']} de {pf['total']} piezas se salen por los LADOS "
                    f"del encuadre; el plano no esta alineado o no esta escalado al ancho"
                )
            # El recorte vertical solo es legitimo donde el encuadre no es 16:10
            # (el quinto fotograma en movil, panoramico a proposito).
            panoramico = ancho <= 640 and s["escena"] == "#contacto"
            if pf["fueraY"] and not panoramico:
                fallos.append(
                    f"{eti}: {pf['fueraY']} de {pf['total']} piezas caen fuera por ARRIBA o "
                    f"por ABAJO y las recorta `overflow: hidden`"
                )
            if pf["fueraY"] == pf["total"]:
                fallos.append(f"{eti}: el encuadre no ensena ni una pieza")
        haz = s["haz"]
        if haz is None:
            fallos.append(f"{eti}: no hay `.scene-shot-beam`")
        else:
            for eje in ("cubreAncho", "cubreAlto"):
                if abs(haz[eje] - 1) > TOLERANCIA_HAZ:
                    fallos.append(
                        f"{eti}: el haz cubre {haz[eje]:.3f} del encuadre en "
                        f"{eje[5:].lower()} ({haz['ancho']:.1f}x{haz['alto']:.1f}px); debe "
                        f"cubrirlo entero. Sin haz la silueta no se ve: se dibuja en "
                        f"--rule sobre --color-ink"
                    )
    return fallos


SINCRO_JS = """() => new Promise(res => {
  const panel = document.querySelector('.scene-index');
  const filas = [...panel.querySelectorAll('.scene-index-row')];
  const caja = panel.getBoundingClientRect();
  const pct = el => {
    const m = getComputedStyle(el).clipPath.match(/inset\\(([^)]*)\\)/);
    if (!m) return 0;
    const p = m[1].split(' ')[1];
    return p ? parseFloat(p) : 0;
  };
  const out = [];
  const t0 = performance.now();
  document.querySelector('.scene-nav-trigger').click();
  function tick() {
    const t = performance.now() - t0;
    const borde = caja.width * (1 - pct(panel) / 100);
    let cont = null;
    for (const f of filas) {
      const rp = pct(f);
      if (rp >= 99.9) continue;            // aun sin revelar: no es contenido
      const r = f.getBoundingClientRect();
      const x = (r.left - caja.left) + r.width * (1 - rp / 100);
      if (cont === null || x > cont) cont = x;
    }
    out.push({t: Math.round(t), borde: Math.round(borde),
              cont: cont === null ? null : Math.round(cont)});
    if (t < 620) requestAnimationFrame(tick); else res(out);
  }
  requestAnimationFrame(tick);
})"""


def medir_sincronia(base):
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900, base)
        filas = pg.evaluate(SINCRO_JS)
        b.close()
    adelantos = [f["cont"] - f["borde"] for f in filas if f["cont"] is not None]
    return max(adelantos) if adelantos else None


TIEMPOS_JS = """() => {
  const panel = document.querySelector('.scene-index');
  const fila = panel.querySelector('.scene-index-row');
  const flash = panel.querySelector('.scene-index-flash');
  const bar = panel.querySelector('.scene-index-bar');
  const trig = document.querySelector('.scene-nav-trigger');
  const nom = trig.querySelector('.scene-nav-trigger-name-a');
  const cs = e => getComputedStyle(e);
  return {
    telonAbierto: cs(panel).transitionDuration,
    telonCurva: cs(panel).transitionTimingFunction,
    fila: cs(fila).transitionDuration,
    filaRetardo: cs(fila).transitionDelay,
    flash: cs(flash).animationDuration,
    barra: cs(bar).animationDuration,
    barraCurva: cs(bar).animationTimingFunction,
    barraDisplay: cs(bar).display,
    // La barra podia estar sin animacion asignada o con 0px de ancho y el gate
    // salia verde: solo comparaba su duracion y su curva DECLARADAS. Un
    // instrumento invisible no es un instrumento. Su opacidad NO se lee aqui:
    // en reposo vale 0 porque la animacion ya termino — se muestrea durante el
    // barrido, en `medir_tiempos`.

    barraAnimacion: cs(bar).animationName,
    barraAncho: bar.getBoundingClientRect().width,
    rotulo: nom ? cs(nom).transitionDuration : null,
  };
}"""

# Con `.is-open` puesto. La curva del telon abierto es `linear` a proposito:
# el borde del telon ES la barra, y un instrumento fisico va a velocidad
# constante (ver el comentario del bloque en themes.css).
TIEMPOS_ESPERADOS = {
    "telonAbierto": "0.48s",
    "telonCurva": "linear",
    "fila": "0.14s, 0.2s",
    "filaRetardo": "0.009s, 0s",
    "flash": "0.3s",
    "barra": "0.48s",
    "barraCurva": "linear",
}


# Pico de opacidad de la barra DURANTE el barrido. En reposo vale 0 (la
# animacion ya acabo), asi que leerla despues no dice nada: hay que muestrear
# mientras corre. Se abre y se muestrea en cada fotograma durante 600ms, que
# cubre los 480 declarados.
PICO_BARRA_JS = """() => new Promise(res => {
  const bar = document.querySelector('.scene-index-bar');
  if (!bar) { res(0); return; }
  let pico = 0;
  const t0 = performance.now();
  const tick = () => {
    pico = Math.max(pico, parseFloat(getComputedStyle(bar).opacity) || 0);
    if (performance.now() - t0 < 600) requestAnimationFrame(tick);
    else res(pico);
  };
  requestAnimationFrame(tick);
})"""


def medir_tiempos(reducido, base):
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900, base, reducido=reducido)
        pg.click(".scene-nav-trigger")
        pico = pg.evaluate(PICO_BARRA_JS)
        pg.wait_for_timeout(900)
        datos = pg.evaluate(TIEMPOS_JS)
        datos["barraOpacidadPico"] = round(pico, 3)
        # Con la cortinilla abierta, Tab debe seguir dando cinco paradas.
        paradas = pg.evaluate(
            "() => document.querySelectorAll('.scene-index .scene-index-row').length"
        )
        b.close()
    datos["paradas"] = paradas
    return datos


def comprobar_tiempos(datos, reducido):
    fallos = []
    if reducido:
        if datos["telonAbierto"] not in ("0s", "0ms"):
            fallos.append(f"reducido: el telon dura {datos['telonAbierto']}, debe ser 0s")
        if datos["filaRetardo"].replace(" ", "") not in ("0s,0s", "0ms,0ms"):
            fallos.append(f"reducido: retardos vivos ({datos['filaRetardo']})")
        if datos["barraDisplay"] != "none":
            fallos.append("reducido: la barra de luz sigue existiendo (debe retirarse, no acelerarse)")
        # `fila` y `flash` se median y no se comprobaban: con las filas barriendo
        # 140ms y el golpe de luz 300ms bajo `reduce`, el gate salia VERDE. Es la
        # regla no negociable 3 del proyecto, no un detalle.
        for clave, etiqueta in (("fila", "la exposicion de las filas"),
                                ("flash", "el golpe de luz"),
                                ("rotulo", "el cambio de rotulo del disparador"),
                                ("barra", "la barra de luz")):
            valor = str(datos.get(clave, "")).replace(" ", "")
            if valor and any(t not in ("0s", "0ms") for t in valor.split(",")):
                fallos.append(f"reducido: {etiqueta} dura {datos[clave]}, debe ser 0s")
        if datos["paradas"] != 5:
            fallos.append(f"reducido: {datos['paradas']} filas, la funcion no puede degradarse")
    else:
        if datos["barraOpacidadPico"] < 0.05:
            fallos.append(
                f"la barra de luz no llega a verse durante el barrido (opacidad maxima "
                f"{datos['barraOpacidadPico']}): el instrumento que lo marca es invisible"
            )
        if datos["barraAnimacion"] in ("none", "", None):
            fallos.append("la barra de luz no tiene animacion asignada, asi que no barre")
        if not datos["barraAncho"]:
            fallos.append("la barra de luz mide 0px de ancho")
        for k, v in TIEMPOS_ESPERADOS.items():
            real = datos[k].replace(" ", "") if isinstance(datos[k], str) else datos[k]
            if real != v.replace(" ", ""):
                fallos.append(f"tiempos: {k} = {datos[k]}, declarado {v}")
    return fallos


# Que version del rotulo se ve se decide por POSICION, no leyendo el
# `transform`: `getComputedStyle` devuelve una matriz y compararla es fragil.
# Un span se ve si su caja cae dentro de la de su celda.
ESTADO_JS = """() => {
  const trig = document.querySelector('.scene-nav-trigger');
  const tc = trig.querySelector('.scene-nav-trigger-tc');
  const caja = tc.getBoundingClientRect();
  const dentro = sel => {
    const e = trig.querySelector(sel);
    if (!e) return null;
    const b = e.getBoundingClientRect();
    return b.top >= caja.top - 2 && b.bottom <= caja.bottom + 2;
  };
  return {
    expanded: trig.getAttribute('aria-expanded'),
    numA: dentro('.scene-nav-trigger-num-a'),
    numB: dentro('.scene-nav-trigger-num-b'),
    nameA: dentro('.scene-nav-trigger-name-a'),
    nameB: dentro('.scene-nav-trigger-name-b'),
    textoA: trig.querySelector('.scene-nav-trigger-name-a')?.textContent,
    textoB: trig.querySelector('.scene-nav-trigger-name-b')?.textContent,
  };
}"""


def medir_estados_y_foco(base):
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900, base)
        cerrado = pg.evaluate(ESTADO_JS)
        abrir_cortinilla(pg)
        abierto = pg.evaluate(ESTADO_JS)

        # Criterio 5: Tab da exactamente cinco paradas y vuelve a la primera.
        visitados = []
        for _ in range(7):
            visitados.append(pg.evaluate(
                "() => document.activeElement?.getAttribute('href')"
                " ?? (document.activeElement?.classList.contains('scene-nav-trigger')"
                "     ? 'disparador' : null)"))
            pg.keyboard.press("Tab")
            pg.wait_for_timeout(60)
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(400)
        tras_esc = pg.evaluate(
            "() => document.activeElement?.classList.contains('scene-nav-trigger') ?? false")
        b.close()
    return cerrado, abierto, visitados, tras_esc


def comprobar_estados(cerrado, abierto, visitados, tras_esc):
    fallos = []
    if cerrado["expanded"] != "false" or abierto["expanded"] != "true":
        fallos.append("aria-expanded no conmuta")
    if not (cerrado["numA"] and cerrado["nameA"]):
        fallos.append("cerrado: no se ve la version de escena del rotulo")
    if cerrado["numB"] or cerrado["nameB"]:
        fallos.append("cerrado: se ve la version 'Esc / Cerrar'")
    if not (abierto["numB"] and abierto["nameB"]):
        fallos.append("abierto: no se ve 'Esc / Cerrar'")
    if abierto["numA"] or abierto["nameA"]:
        fallos.append("abierto: se sigue viendo la version de escena")
    if abierto["textoB"] != "Cerrar":
        fallos.append(f"el rotulo abierto dice {abierto['textoB']!r}, debe decir 'Cerrar'")
    # Seis paradas, no cinco: las cinco filas MAS el disparador. Entro en la
    # trampa porque en Hyprland es el boton visible de cerrar ("Esc / Cerrar") y
    # ciclar solo las filas lo dejaba inalcanzable con el teclado.
    unicos = [v for v in visitados[:5] if v]
    if len(set(unicos)) != 5:
        fallos.append(f"Tab no da cinco paradas de escena distintas: {visitados}")
    if visitados[5] != "disparador":
        fallos.append(
            f"Tab no llega al disparador, que es el boton visible de cerrar: {visitados}")
    if visitados[6] != visitados[0]:
        fallos.append(f"Tab no vuelve a la primera fila: {visitados}")
    if not tras_esc:
        fallos.append("tras Esc el foco no vuelve al disparador")
    return fallos


# El pie de dos estados se anade en los TRES temas y solo Hyprland lo estiliza.
# Sin `display: none` de base se cuela como texto suelto: medido, el disparador
# pasaba de 168,81 a 415,31 px en Vice y de 152 a 308,22 en Caelestia, pintando
# "01ESCTÍTULOCERRAR" junto al rotulo. El arnes de esta tarea solo miraba
# Hyprland y por eso no lo vio; esta comprobacion es el guardarrail que faltaba.
#
# Se mide el ANCHO del disparador y no la existencia del nodo: el nodo debe
# existir en los tres temas (lo pone `sceneNav.ts`), lo que no debe existir es
# su huella. Y se compara el texto renderizado (`innerText`, que respeta
# `display: none`) contra el rotulo compartido, que es lo unico que esos dos
# temas deben mostrar.
AJENO_JS = """() => {
  const t = document.querySelector('.scene-nav-trigger');
  const tc = t.querySelector('.scene-nav-trigger-tc');
  return {
    tcEnElDom: !!tc,
    tcDisplay: tc ? getComputedStyle(tc).display : null,
    anchoDisparador: Math.round(t.getBoundingClientRect().width * 100) / 100,
    textoRenderizado: t.innerText.trim(),
    rotulo: t.querySelector('.scene-nav-trigger-label')?.textContent ?? '',
  };
}"""

# Anchos del disparador en el merge-base c1cacf1, medidos a 1440x900 antes de
# que existiera el pie de dos estados. Si vuelven a moverse, es que algo de
# Hyprland se ha escapado a los otros dos temas.
#
# Los numeros son exactos, no aproximados: 15 muestras entre 500 ms y 9 s, en el
# worktree del merge-base, en el dev server de la rama y en el build servido,
# dan 167,94 en las 15. La rama deja Vice IDENTICO, no "casi igual". Aqui estuvo
# 168,81 durante un rato, que no es reproducible por ninguna via; y como este es
# el unico registro escrito de como estaba un tema CERRADO, un numero de mas
# habria convertido el arnes en el modo de fallo de `OBRA_TRANSIT`: no falla,
# miente.
ANCHO_AJENO = {"vice": 167.94, "caelestia": 152.0}
TOLERANCIA_AJENO = 1.5


def medir_ajenos(base):
    datos = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, executable_path=CHROME,
                               args=["--no-sandbox", "--use-gl=swiftshader"])
        for tema in ANCHO_AJENO:
            ctx = b.new_context(viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            pg.goto(_url(base, tema),
                    wait_until="domcontentloaded", timeout=40000)
            pg.wait_for_timeout(6000)
            datos[tema] = pg.evaluate(AJENO_JS)
            ctx.close()
        b.close()
    return datos


def comprobar_ajenos(datos):
    fallos = []
    for tema, d in datos.items():
        if not d["tcEnElDom"]:
            fallos.append(f"{tema}: falta `.scene-nav-trigger-tc` en el DOM")
            continue
        if d["tcDisplay"] != "none":
            fallos.append(
                f"{tema}: `.scene-nav-trigger-tc` no esta oculto (display={d['tcDisplay']})")
        deriva = abs(d["anchoDisparador"] - ANCHO_AJENO[tema])
        if deriva > TOLERANCIA_AJENO:
            fallos.append(
                f"{tema}: el disparador mide {d['anchoDisparador']}px y en el merge-base "
                f"medía {ANCHO_AJENO[tema]}px (deriva {round(deriva, 2)}px)")
        if d["textoRenderizado"].casefold() != d["rotulo"].casefold():
            fallos.append(
                f"{tema}: el disparador pinta {d['textoRenderizado']!r}, "
                f"debe pintar solo el rotulo {d['rotulo']!r}")
    return fallos


# El rotulo del disparador se apoya en el fondo generativo, sin caja: es lo que
# pide el criterio 4. `verify.py` no puede medirlo — excluye el texto cuyo fondo
# no es solido, y este no lo es (desviacion tipica 27,7 sobre un limite de 18) —
# asi que el unico elemento del widget que quedaba medido era la version
# ESCONDIDA del rotulo, desplazada fuera del contenedor recortado: un OK
# fantasma de 17,75:1 sobre texto que en reposo no se ve. Corregido en verify.py;
# la medida del rotulo VISIBLE se hace aqui, que es donde se conoce el widget.
#
# Se oculta solo el texto para leer el fondo puro bajo su caja y se barre el
# scroll: el haz del fondo pasa por detras y el peor momento no es el reposo.
# El minimo es el de WCAG AA para texto pequeno, no una tolerancia inventada.
CONTRASTE_MIN = 4.5
# El barrido fino encuentra el peor momento en el 42,4% del scroll (5,08:1), y
# el muestreo saltaba de 0,40 a 0,50 justo por encima: declaraba 5,75 de margen
# donde el real es 5,08. Se anaden los puntos del valle.
MUESTRAS_SCROLL = (0, 0.15, 0.3, 0.4, 0.42, 0.44, 0.46, 0.5, 0.65, 0.8, 1.0)
PIEZAS_ROTULO = (".scene-nav-trigger-num-a", ".scene-nav-trigger-name-a")


def _luminancia(c):
    def canal(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * canal(c[0]) + 0.7152 * canal(c[1]) + 0.0722 * canal(c[2])


def _ratio(a, b):
    l1, l2 = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def medir_contraste_rotulo(base):
    from PIL import Image
    import io
    peor = {}
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900, base)
        alto = pg.evaluate("document.body.scrollHeight")
        for frac in MUESTRAS_SCROLL:
            pg.evaluate(f"window.scrollTo(0, {int((alto - 900) * frac)})")
            pg.wait_for_timeout(1400)
            cajas = pg.evaluate(
                "(sels) => Object.fromEntries(sels.map(s => {"
                "  const e = document.querySelector(s); if (!e) return [s, null];"
                "  const r = e.getBoundingClientRect();"
                "  return [s, {x: r.x, y: r.y, w: r.width, h: r.height,"
                "              color: getComputedStyle(e).color}];"
                "}))", list(PIEZAS_ROTULO))
            pg.evaluate("(sels) => sels.forEach(s => {const e = document.querySelector(s);"
                        " if (e) e.style.visibility = 'hidden';})", list(PIEZAS_ROTULO))
            pg.wait_for_timeout(120)
            img = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
            pg.evaluate("(sels) => sels.forEach(s => {const e = document.querySelector(s);"
                        " if (e) e.style.visibility = '';})", list(PIEZAS_ROTULO))
            for sel, d in cajas.items():
                if not d:
                    continue
                xs = range(max(int(d["x"]), 0), min(int(d["x"] + d["w"]), 1440))
                ys = range(max(int(d["y"]), 0), min(int(d["y"] + d["h"]), 900))
                px = [img.getpixel((x, y)) for x in xs for y in ys]
                if not px:
                    continue
                fondo = tuple(sum(c[i] for c in px) // len(px) for i in range(3))
                frente = tuple(int(v) for v in
                               d["color"].removeprefix("rgb(").rstrip(")").split(","))
                r = round(_ratio(frente, fondo), 2)
                if sel not in peor or r < peor[sel]["ratio"]:
                    peor[sel] = {"ratio": r, "fondo": list(fondo), "enScroll": round(frac, 2)}
        b.close()
    return peor


def comprobar_contraste(peor):
    fallos = []
    for sel in PIEZAS_ROTULO:
        d = peor.get(sel)
        if d is None:
            fallos.append(f"no se pudo medir el contraste de {sel}")
        elif d["ratio"] < CONTRASTE_MIN:
            fallos.append(
                f"{sel}: {d['ratio']}:1 sobre el fondo {d['fondo']} al {int(d['enScroll'] * 100)}% "
                f"del scroll; el minimo AA para texto pequeno es {CONTRASTE_MIN}:1"
            )
    return fallos


############################################################################
# Firmas estructurales del indice de escenas.
#
# NO comprueba que la silueta sea correcta. No sabe si `src/components/
# sceneNav.siluetas.ts` dibuja lo que hay que dibujar — esa es una pregunta
# semantica, y un arnes geometrico no tiene acceso a ella (medido: ver el
# spec `docs/superpowers/specs/2026-09-10-hyprland-selector-siluetas-design.md`,
# donde un indice de similitud silueta-vs-escena se probo contra las cinco
# escenas en mas de diez configuraciones distintas y el orden que dio salio
# invertido respecto a lo que un humano juzga fiel).
#
# Lo que SI comprueba: que ninguna escena real ha cambiado de estructura
# desde la ULTIMA VEZ que alguien miro su silueta a proposito y la bendijo.
# La pregunta no es "¿se parece la silueta a la escena?", es "¿ha cambiado
# la escena sin que nadie pasara por delante de su silueta?". El silencio es
# el fallo que de verdad ocurrio aqui (creditos, quien-es y contacto
# derivaron sin que nada avisara), no la deriva en si — la deriva es
# inevitable en un fichero que es una copia a mano; el silencio no lo era.
#
# Limite de granularidad (medido con un <p> de prueba, ver el spec citado
# arriba): contenido nuevo que cae DENTRO de una celda de la rejilla 12x8 que
# ya estaba entintada por otra pieza no mueve la UNION de celdas — la celda
# ya contaba como "tinta" y sigue contandolo. Con el hash sobre el
# multiconjunto de cajas de pieza (`calcular_firma`, revision final del gate)
# este caso concreto SI se cierra: una pieza nueva anade una tupla
# `(c0,r0,c1,r1)` al multiconjunto aunque no anada ninguna celda nueva a la
# union, y el hash la ve. Lo que sigue sin ver el gate es una pieza que
# cambia de tamano o posicion SIN cruzar el limite de su propia celda: sigue
# siendo la misma caja en celdas, mismo hash. Es un limite mas estrecho que
# antes, dicho con la misma franqueza que el parrafo de arriba.
############################################################################

FIRMAS_PATH = Path(__file__).parent / "scene-nav-firmas.json"

# Se sondea `/@vite/client` en vez de fiar la deteccion a una lista de
# puertos. Una lista de un solo puerto (antes: `{5173}`) fallaba en cuanto
# 5173 estaba ocupado -- que aqui es lo normal, Vite sigue con 5174, 5175...
# Y ningun numero de puerto, ni siquiera uno "de preview", prueba nada: este
# mismo proyecto tiene registrado que los vite huerfanos sirven dist viejo
# (un `vite preview` de un worktree borrado sigue respondiendo en su puerto
# con el ultimo build que sirvio). `/@vite/client` es la ruta que SOLO el
# servidor de desarrollo inyecta (el cliente de HMR); `vite preview` sirve
# `dist/` estatico y no la tiene, sea cual sea el puerto.
#
# El status 200 SOLO no basta: `vite preview` es una SPA con fallback de
# historial, asi que CUALQUIER ruta sin match -- `/@vite/client` incluida --
# le devuelve `index.html` con 200. Medido contra este mismo build servido:
# `/@vite/client` respondia 200 con `Content-Type: text/html` (el propio
# `index.html`). El dev server real sirve ese modulo como JS. Se exige
# ademas el content-type, que es lo que de verdad distingue "existe la ruta"
# de "cualquier ruta cae en el index".
#
# NUNCA falla abierto. Un `except: return False` trataria en silencio
# cualquier fallo de red del sondeo (timeout, DNS, conexion rechazada) como
# "no es dev server" -- exactamente el caso que este arnes existe para
# rechazar, tratado como si nunca hubiera pasado. El criterio del proyecto
# es que un instrumento que no puede medir lo diga, en vez de medir otra
# cosa (`rules/verification.md`, "Deriva de la documentacion" / doctrina de
# gates). Por eso hay TRES resultados, no dos: `True` (es dev server),
# `False` (se sondeo y no lo es) y `None` ("no se pudo determinar" -- el
# sondeo fallo por una razon de red, no porque la ruta no exista). Quien
# llama debe tratar `None` como un fallo explicito y abortar, nunca como un
# `False` silencioso.
def _es_dev_server(base):
    try:
        with urllib.request.urlopen(f"{base}/@vite/client", timeout=5) as r:
            tipo = r.headers.get("Content-Type", "")
            return r.status == 200 and "javascript" in tipo
    except (urllib.error.URLError, ValueError, OSError) as e:
        print(
            f"AVISO: no se pudo sondear {base}/@vite/client para decidir si "
            f"es un dev server de Vite ({e}). No se interpreta como "
            f"'no es dev server' -- ver `_es_dev_server`.",
            file=sys.stderr,
        )
        return None


# Hitos de montaje real de los modulos que llegan por `import()` diferido en
# `src/main.ts` (`obraCartel`, `hyprStackCimientos`). Sin esto, "el layout no
# se movio entre dos sondeos" es COINCIDENCIA de que las secciones son de
# alto por contenido, no prueba de que el modulo hubiera llegado: los dos
# sondeos de ~30ms del `domcontentloaded` podian caer ANTES de que el
# `import()` resolviera, y la firma de `obra`/`creditos` acababa dependiendo
# de si esos modulos habian montado o no en el instante del muestreo.
HITOS_MONTAJE = ("[data-obra-panel]", "[data-cimientos]")


def _esperar_dom_estable(pg, selectores, hitos=HITOS_MONTAJE, timeout=15000):
    """Ancla la espera al ESTADO real del layout, nunca al reloj.

    La leccion ya esta pagada en este mismo proyecto (spec
    2026-09-04-caelestia-fundido): bajo `--use-gl=swiftshader` el
    `requestAnimationFrame`/`setTimeout` de la pagina llega cada 200-400ms en
    vez de cada ~16, asi que un `wait_for_timeout` fijo mide la carga de la
    maquina, no si el layout de verdad asento.

    Se comparan dos cosas entre dos lecturas consecutivas: que los HITOS de
    montaje (arriba) ya existan en el DOM, y que la salida de `FIRMA_JS` --
    exactamente lo que se va a hashear, no un proxy de `top/left/width/height`
    del CONTENEDOR de la escena -- coincida. El proxy anterior se satisfacia
    con layouts a medio construir: una escena puede dejar de mover su
    contenedor exterior mientras las piezas de DENTRO siguen cambiando (una
    imagen que llega, un modulo que aun no monto), y eso es justo lo que la
    firma hashea. Solo se sigue cuando las dos lecturas coinciden dos veces
    seguidas, con `document.fonts` cargadas.

    Si nunca se estabiliza, esto FALLA con un mensaje explicito en vez de
    devolver el control y dejar que se mida un layout a medio asentar --
    "los cortes se anclan al ESTADO, nunca al reloj; si el punto de corte no
    llega, el gate FALLA en vez de medir otra cosa".
    """
    selectores_js = json.dumps(selectores)
    hitos_js = json.dumps(list(hitos))
    pg.evaluate("() => { window.__firmaSigPrev = undefined; }")
    js = f"""() => {{
      if (document.fonts && document.fonts.status !== 'loaded') return false;
      const hitos = {hitos_js};
      for (const h of hitos) {{ if (!document.querySelector(h)) return false; }}
      const firmaDe = {FIRMA_JS};
      const sels = {selectores_js};
      const sig = sels.map((s) => JSON.stringify(firmaDe(s))).join('|');
      if (window.__firmaSigPrev !== undefined && window.__firmaSigPrev === sig) return true;
      window.__firmaSigPrev = sig;
      return false;
    }}"""
    try:
        pg.wait_for_function(js, timeout=timeout)
    except PlaywrightTimeoutError as e:
        faltantes = [h for h in hitos if not pg.evaluate(
            "(h) => !!document.querySelector(h)", h)]
        detalle = f" -- hitos de montaje sin llegar: {faltantes}" if faltantes else ""
        raise RuntimeError(
            f"las firmas no se pudieron medir: el layout de las escenas "
            f"({selectores}) no se estabilizo en {timeout}ms{detalle}. Puede "
            f"ser fuentes sin cargar, una animacion que no respeta "
            f"prefers-reduced-motion, o un build a medio montar -- no se "
            f"sigue midiendo sobre un layout que no ha asentado."
        ) from e

# Selector real de cada escena. `obra` no es `[data-scene="obra"]` (eso
# selecciona solo la PRIMERA de las cinco tarjetas de proyecto): es el
# envoltorio `#obra` que las agrupa a las cinco, el mismo nodo al que apunta
# el ancla de navegacion (ver `src/main.ts`, `obraRail.id = "obra"`).
FIRMA_SELECTORES = {
    "hero": '[data-scene="hero"]',
    "quien-es": '[data-scene="about"]',
    "obra": "#obra",
    "creditos": '[data-scene="credits"]',
    "contacto": '[data-scene="contacto"]',
}

# Rejilla de cuantizacion, en celdas sobre el marco PROPIO de cada escena
# (1440 de ancho x su alto real, no 900 fijo: `obra` mide ~550px de alto
# real a 1440 de ancho, y forzar 900 la recortaria). 12x8 se eligio por
# rango, no al tanteo: mas fino (16x10, 20x12) es mas sensible a un cambio
# real pero tambien a redondeos de subpixel del renderizador; mas grueso
# (6x4, 8x5) sigue siendo estable pero empieza a perder cambios de una sola
# pieza pequeña. Las tres resoluciones probadas (8x5, 12x8, 16x10) salieron
# BIT A BIT identicas en tres corridas seguidas contra el mismo build (ver
# el informe), asi que la eleccion es de sensibilidad, no de estabilidad: se
# toma la del medio.
FIRMA_GRID = (12, 8)

############################################################################
# Comprobaciones ESTATICAS sobre `sceneNav.siluetas.ts`, sin navegador.
#
# No hay interprete de TypeScript en este arnes: se parsea el fichero a mano
# con regex, aprovechando que `SILUETAS` tiene un formato rigido (una escena
# por bloque, una pieza por linea, sin objetos anidados dentro de una
# pieza). Compartido por las tres comprobaciones de abajo.
############################################################################

SILUETAS_TS_PATH = RAIZ / "src/components/sceneNav.siluetas.ts"
CONTENT_TS_PATH = RAIZ / "src/data/content.ts"

# Fuentes de contenido real contra las que se contrastan los `disp` de las
# siluetas (copy literal, escrito a mano). `content.ts` es la fuente unica
# del proyecto para casi todo, pero no para todo: "Hablemos" del fotograma de
# `contacto` vive en `src/sections/contacto.ts`, no en `content.ts`.
FUENTES_CONTENIDO = [CONTENT_TS_PATH, *sorted((RAIZ / "src/sections").rglob("*.ts"))]


def _parse_siluetas_piezas():
    """`{escena: [pieza, ...]}` parseando `SILUETAS` a mano. Cada pieza es un
    dict con las claves numericas/de texto que trae (`clase`, `x`, `y`, `w`,
    `h`, `tam`, `texto`) cuando estan presentes en el literal."""
    texto = SILUETAS_TS_PATH.read_text(encoding="utf-8")
    m = re.search(r"export const SILUETAS:.*?=\s*\{(.*?)\n\};\n", texto, re.S)
    if not m:
        raise RuntimeError(f"no se pudo parsear SILUETAS en {SILUETAS_TS_PATH}")
    escenas = {}
    for em in re.finditer(r'^  "?([\w-]+)"?:\s*\[\n(.*?)\n  \],', m.group(1), re.M | re.S):
        piezas = []
        for pm in re.finditer(r"\{([^{}]*)\}", em.group(2)):
            campo = pm.group(1)
            pieza = {}
            cm = re.search(r'clase:\s*"(\w+)"', campo)
            if cm:
                pieza["clase"] = cm.group(1)
            for num in ("x", "y", "w", "h", "tam"):
                nm = re.search(rf"\b{num}:\s*(-?[\d.]+)", campo)
                if nm:
                    pieza[num] = float(nm.group(1))
            tm = re.search(r'texto:\s*"((?:[^"\\]|\\.)*)"', campo)
            if tm:
                pieza["texto"] = tm.group(1)
            piezas.append(pieza)
        escenas[em.group(1)] = piezas
    return escenas


def _parse_scene_index_ids():
    """Ids de `sceneIndex` en `content.ts`, en el orden en que aparecen."""
    texto = CONTENT_TS_PATH.read_text(encoding="utf-8")
    m = re.search(r"export const sceneIndex: SceneEntry\[\] = \[(.*?)\n\];", texto, re.S)
    if not m:
        raise RuntimeError(f"no se pudo parsear sceneIndex en {CONTENT_TS_PATH}")
    return re.findall(r'id:\s*"([\w-]+)"', m.group(1))


def verificar_piezas_dentro_del_plano():
    """El plano es 1440x900 y representa lo que el visitante VE: ninguna
    pieza puede caer fuera de el (ver cabecera de `sceneNav.siluetas.ts`).
    Comprobacion barata y estatica: `x+w <= 1440`, `y+h <= 900`, para toda
    pieza que declara `w`/`h` (las piezas de solo texto, sin caja explicita,
    las cubre la comprobacion en vivo de recorte parcial en `comprobar()`).

    Nacio del defecto real de `obra`: sus coordenadas eran las de
    `getBoundingClientRect()` en un scroll concreto de la pagina real, no las
    de su propio marco -- la quinta fila y su miniatura caian a y=940/941,
    fuera del plano de 900, y el `overflow: hidden` del encuadre las
    recortaba en silencio con este arnes en verde."""
    fallos = []
    for escena, piezas in _parse_siluetas_piezas().items():
        for p in piezas:
            if "w" not in p or "h" not in p:
                continue
            x, y = p.get("x", 0.0), p.get("y", 0.0)
            xw, yh = x + p["w"], y + p["h"]
            if xw > 1440 + 0.01 or yh > 900 + 0.01:
                fallos.append(
                    f"silueta {escena}: pieza {p.get('clase')} en x={x:g} y={y:g} "
                    f"w={p['w']:g} h={p['h']:g} se sale del plano de 1440x900 "
                    f"(x+w={xw:g}, y+h={yh:g})"
                )
    return fallos


def verificar_listas_de_escenas():
    """Tres listas independientes tienen que nombrar las mismas cinco
    escenas: las claves de `SILUETAS`, los selectores de `FIRMA_SELECTORES`
    (este mismo fichero) y los `id` de `sceneIndex` en `content.ts`. Hoy nada
    las cruzaba, asi que una escena nueva podia quedar sin silueta, sin
    firma, o sin las dos, y ningun arnes lo veria: cambiar un texto casi
    nunca cambia la ocupacion de celdas de la firma, y una silueta que falta
    del todo no es una que "cambio de estructura"."""
    fallos = []
    ids_siluetas = set(_parse_siluetas_piezas())
    ids_firma = set(FIRMA_SELECTORES)
    ids_content = _parse_scene_index_ids()
    if ids_siluetas != ids_firma:
        fallos.append(
            f"SILUETAS ({sorted(ids_siluetas)}) y FIRMA_SELECTORES "
            f"({sorted(ids_firma)}) no coinciden"
        )
    if ids_siluetas != set(ids_content):
        fallos.append(
            f"SILUETAS ({sorted(ids_siluetas)}) y el sceneIndex de content.ts "
            f"({ids_content}) no coinciden"
        )
    if set(ids_content) != ids_firma:
        fallos.append(
            f"el sceneIndex de content.ts ({ids_content}) y FIRMA_SELECTORES "
            f"({sorted(ids_firma)}) no coinciden"
        )
    return fallos


def verificar_disp_contra_contenido():
    """Los `disp` de las siluetas son copy literal copiado A MANO de
    `content.ts`/`src/sections/*.ts` ("Aoshi Blanco Sanz", "EchoPlan",
    "JavaScript", "Hablemos"...). Si Aoshi renombra un proyecto o cambia una
    cifra, la silueta miente y el gate de FIRMAS no se entera -- cambiar un
    texto casi nunca mueve la celda que ocupa. Esta comprobacion es la unica
    red para ese caso: que cada `texto` de un `disp` siga apareciendo, tal
    cual, en alguna de las fuentes de contenido del proyecto."""
    fallos = []
    fuente = "\n".join(
        p.read_text(encoding="utf-8") for p in FUENTES_CONTENIDO if p.exists()
    )
    for escena, piezas in _parse_siluetas_piezas().items():
        for p in piezas:
            if p.get("clase") != "disp" or "texto" not in p:
                continue
            if p["texto"] not in fuente:
                fallos.append(
                    f"silueta {escena}: el texto {p['texto']!r} no aparece en "
                    f"ninguna fuente de contenido "
                    f"({', '.join(str(f.relative_to(RAIZ)) for f in FUENTES_CONTENIDO)}) "
                    f"-- puede que el copy real haya cambiado y la silueta mienta"
                )
    return fallos


# Igual que `REAL_JS`/`LAYOUT_JS` de las siluetas: solo cuenta como "tinta"
# un nodo con texto propio (longitud >= 2 para no contar cada `<i>` suelto
# de la animacion de caracteres de los titulos de Obra — un titulo de 8
# letras deja 16 `<i>` de una sola letra cada uno, puro ruido de montaje) o
# un elemento con borde visible, leido LADO A LADO (`border-top-width`, etc.)
# y no como "tiene borde en algun sitio": una `<section>` con solo
# `border-top` no es una caja completa, y marcarla como tal infla la firma
# con tres lados que no existen.
FIRMA_JS = """(sel) => {
  const wrap = document.querySelector(sel);
  if (!wrap) return null;
  const origin = wrap.getBoundingClientRect();
  const out = [];
  const walker = document.createTreeWalker(wrap, NodeFilter.SHOW_ELEMENT);
  let node = walker.currentNode;
  const consider = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    const ownText = [...el.childNodes].filter((n) => n.nodeType === 3)
      .map((n) => n.textContent.trim()).join('').trim();
    const hasOwnText = ownText.length >= 2;
    const sides = {
      top: parseFloat(cs.borderTopWidth) > 0,
      bottom: parseFloat(cs.borderBottomWidth) > 0,
      left: parseFloat(cs.borderLeftWidth) > 0,
      right: parseFloat(cs.borderRightWidth) > 0,
    };
    const anyBorder = sides.top || sides.bottom || sides.left || sides.right;
    if (!hasOwnText && !anyBorder) return;
    out.push({
      x: r.left - origin.left, y: r.top - origin.top, w: r.width, h: r.height,
      filled: hasOwnText, sides,
    });
  };
  while (node) { consider(node); node = walker.nextNode(); }
  return {w: origin.width, h: origin.height, pieces: out};
}"""


def _bounds_celda(p, w, h, cols, rows):
    """Caja de una pieza en celdas: `(c0, r0, c1, r1)`, o `None` si cae fuera
    del marco. Compartida por `_celdas_pieza` (la union de celdas encendidas,
    para el mapa legible) y por `calcular_firma` (el multiconjunto de cajas,
    para el hash sensible a transposicion)."""
    pw = max(p["w"], 1)
    ph = max(p["h"], 1)
    x0 = max(p["x"], 0)
    y0 = max(p["y"], 0)
    x1 = min(p["x"] + pw, w)
    y1 = min(p["y"] + ph, h)
    if x1 <= x0 or y1 <= y0 or not w or not h:
        return None
    c0 = max(0, min(cols - 1, int(x0 / w * cols)))
    c1 = max(0, min(cols - 1, int((x1 - 0.001) / w * cols)))
    r0 = max(0, min(rows - 1, int(y0 / h * rows)))
    r1 = max(0, min(rows - 1, int((y1 - 0.001) / h * rows)))
    return c0, r0, c1, r1


def _celdas_pieza(p, w, h, cols, rows):
    b = _bounds_celda(p, w, h, cols, rows)
    if b is None:
        return
    c0, r0, c1, r1 = b
    if p.get("filled", True):
        for cx in range(c0, c1 + 1):
            for cy in range(r0, r1 + 1):
                yield (cx, cy)
        return
    # Solo borde: solo se marcan los lados que de verdad estan pintados, no
    # el perimetro entero de la caja (ver comentario de `FIRMA_JS`).
    sides = p.get("sides") or {"top": True, "bottom": True, "left": True, "right": True}
    if sides.get("top"):
        for cx in range(c0, c1 + 1):
            yield (cx, r0)
    if sides.get("bottom"):
        for cx in range(c0, c1 + 1):
            yield (cx, r1)
    if sides.get("left"):
        for cy in range(r0, r1 + 1):
            yield (c0, cy)
    if sides.get("right"):
        for cy in range(r0, r1 + 1):
            yield (c1, cy)


def _ocupacion_grid(celdas, cols, rows):
    """`celdas` ("x:y" encendidas) a `rows` filas de `cols` caracteres
    ('#'/'.'). Es la MISMA rejilla que se hashea, en forma legible en un
    diff: cuesta cero computo extra (las celdas ya se calculan) y dos
    entradas cuyo diff cambia de forma se ven distintas a ojo, no solo en un
    sha256 de 64 hex que no dice QUE cambio."""
    encendidas = {tuple(int(v) for v in c.split(":")) for c in celdas}
    return ["".join("#" if (x, y) in encendidas else "." for x in range(cols))
            for y in range(rows)]


def calcular_firma(datos, cols, rows):
    """De `{w, h, pieces}` a `(hash, celdas_ordenadas, cajas_ordenadas)`.
    Determinista: mismo layout, mismo hash — es justo lo que exige la prueba
    de estabilidad.

    El hash NO es solo la union de celdas encendidas: esa union, sola, tenia
    dos limites declarados y aceptados como "conocidos" -- una transposicion
    fila/columna que cubre el MISMO conjunto de celdas da identico hash, y
    una pieza nueva que cae DENTRO de una celda ya encendida no mueve nada.
    El orquestador decidio cerrar el primero, y cerrarlo cierra el segundo de
    paso: se anade al hash el MULTICONJUNTO (con repetidos, sin deduplicar)
    de cajas de pieza en celdas `(c0, r0, c1, r1)`. Dos columnas altas dan
    `(0,0,5,7),(6,0,11,7)`; su transpuesta da `(0,0,11,3),(0,4,11,7)` --
    conjuntos de tuplas distintos, sin heuristica de forma. Y una pieza nueva
    dentro de una celda ya pintada anade una tupla al multiconjunto aunque no
    anada ninguna celda nueva a la union.
    """
    celdas = set()
    cajas = []
    for p in datos["pieces"]:
        celdas.update(_celdas_pieza(p, datos["w"], datos["h"], cols, rows))
        b = _bounds_celda(p, datos["w"], datos["h"], cols, rows)
        if b is not None:
            cajas.append(b)
    ordenadas = sorted(f"{x}:{y}" for x, y in celdas)
    cajas_ordenadas = sorted(cajas)  # multiconjunto: SIN deduplicar
    cajas_texto = ",".join(f"{c0}:{r0}:{c1}:{r1}" for c0, r0, c1, r1 in cajas_ordenadas)
    firma = hashlib.sha256(
        (",".join(ordenadas) + "|" + cajas_texto).encode()
    ).hexdigest()
    return firma, ordenadas, cajas_ordenadas


def abrir_firmas(pw, base):
    b = pw.chromium.launch(headless=True, executable_path=CHROME,
                           args=["--no-sandbox", "--use-gl=swiftshader"])
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    pg = ctx.new_page()
    consola = []
    pg.on("console", lambda m: consola.append(m.text) if m.type == "error" else None)
    pg.goto(f"{base}/?theme=hyprland", wait_until="domcontentloaded", timeout=40000)
    # encendido de Ascua + shader: se espera a que el layout de las cinco
    # escenas deje de moverse (estado), no un numero fijo de ms (reloj).
    _esperar_dom_estable(pg, list(FIRMA_SELECTORES.values()))
    return b, ctx, pg, consola


def medir_firmas(base):
    """Firma actual de las cinco escenas contra el build en `base`. Se mide
    con `reduced_motion="reduce"` a proposito: esto es maquetacion, no la
    entrada — con movimiento normal la escena de Obra se lee a medio barrer
    y la firma saldria distinta cada vez que cambiara el instante del
    muestreo, que es justo el fallo de instrumento que la prueba de
    estabilidad esta aqui para cazar."""
    with sync_playwright() as pw:
        b, ctx, pg, consola = abrir_firmas(pw, base)
        cols, rows = FIRMA_GRID
        salida = {}
        for id_, sel in FIRMA_SELECTORES.items():
            pg.evaluate("(sel) => document.querySelector(sel)?.scrollIntoView({block: 'start'})", sel)
            # El scroll asienta cuando ESA escena deja de moverse, no a los
            # 500ms: mismo argumento que en `abrir_firmas`.
            _esperar_dom_estable(pg, [sel])
            datos = pg.evaluate(FIRMA_JS, sel)
            if datos is None:
                salida[id_] = {"hash": None, "celdas": [], "cajas": [], "piezas": 0}
                continue
            firma, celdas, cajas = calcular_firma(datos, cols, rows)
            salida[id_] = {
                "hash": firma, "celdas": celdas, "cajas": cajas,
                "piezas": len(datos["pieces"]),
            }
        ctx.close()
        b.close()
    return salida, consola


def _commit_actual():
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent.parent,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "desconocido"


def _arbol_sucio():
    """True si hay cambios sin commitear (`git status --porcelain` no vacio).
    Bendecir con el arbol sucio deja en el JSON un commit que no refleja lo
    que de verdad se midio: el hash de `rev-parse HEAD` apunta al ultimo
    commit, pero el DOM pudo salir de un `src/` con cambios locales encima."""
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"], cwd=Path(__file__).parent.parent,
            capture_output=True, text=True, check=True,
        )
        return bool(r.stdout.strip())
    except Exception:
        return None  # no se pudo comprobar; no se afirma nada


def cargar_firmas_bendecidas():
    if not FIRMAS_PATH.exists():
        return {}
    return json.loads(FIRMAS_PATH.read_text(encoding="utf-8"))


def guardar_firmas_bendecidas(actuales, escenas):
    """Escribe `scene-nav-firmas.json`. Bendecir es un acto deliberado que se
    revisa en el diff (igual que `--update-baseline` en `verify.py`): este
    metodo nunca se llama solo desde el camino de comprobacion, solo desde
    `--update-firmas`.

    Bendecir es POR ESCENA, nunca todo-o-nada: `escenas` es la lista
    NOMBRADA en `--update-firmas`, y solo esas entradas se tocan. La premisa
    del gate es "bendecir = alguien paso por delante de esa silueta a
    proposito"; un `--update-firmas` que bendijera las cinco siempre negaba
    esa premisa -- derivan `obra` y `creditos` la misma semana, alguien
    revisa y arregla solo `creditos`, y bendecir con el viejo comando
    enterraba el rojo de `obra` sin que nadie la hubiera mirado.

    Dentro de las escenas nombradas, una cuyo hash NO cambio respecto a lo ya
    bendecido se deja intacta -- ni `commit` ni `bendecidoEn` se reescriben.
    Sin esto el diff de bendecir CUALQUIER escena tocaba las cinco entradas
    cada vez (los metadatos se recalculaban siempre), y de esas cinco solo
    una decia algo.

    Si el arbol de trabajo tenia cambios sin commitear en el momento de
    bendecir, queda anotado en el propio JSON (`arbolSucio`) en vez de
    fingir que el commit registrado es lo unico que se midio.

    Devuelve `(bendecidas, cambiadas)`: el diccionario completo escrito y la
    lista de ids que de verdad se reescribieron."""
    existentes = cargar_firmas_bendecidas()
    commit = _commit_actual()
    sucio = _arbol_sucio()
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cols, rows = FIRMA_GRID
    cambiadas = []
    for id_ in escenas:
        d = actuales.get(id_)
        if d is None or d.get("hash") is None:
            continue  # ya se reporta como fallo aparte; no se bendice nada
        anterior = existentes.get(id_)
        if (
            anterior is not None
            and anterior.get("hash") == d["hash"]
            and list(anterior.get("grid", [])) == list(FIRMA_GRID)
        ):
            continue  # sin cambios: no reescribir commit/bendecidoEn
        existentes[id_] = {
            "hash": d["hash"],
            "grid": list(FIRMA_GRID),
            "ocupacion": _ocupacion_grid(d["celdas"], cols, rows),
            "commit": commit,
            "bendecidoEn": ahora,
            "arbolSucio": sucio,
        }
        cambiadas.append(id_)
    FIRMAS_PATH.write_text(
        json.dumps(existentes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return existentes, cambiadas


def comprobar_firmas(actuales, bendecidas):
    fallos = []
    for id_ in FIRMA_SELECTORES:
        act = actuales.get(id_, {})
        ben = bendecidas.get(id_)
        if act.get("hash") is None:
            fallos.append(f"firma {id_}: no se encontro la escena en el DOM ({FIRMA_SELECTORES[id_]})")
            continue
        if ben is None:
            fallos.append(
                f"firma {id_}: no hay firma bendecida en {FIRMAS_PATH.name}. "
                f"Revisa su silueta en sceneNav.siluetas.ts y bendice con "
                f"--update-firmas {id_}."
            )
            continue
        # Sin `grid` en la entrada bendecida, `.get("grid", FIRMA_GRID)`
        # pasaba como si coincidiera -- una entrada que no declara con que
        # rejilla se midio no es una entrada valida, no una que "por
        # defecto" coincide con la actual.
        if "grid" not in ben or list(ben["grid"]) != list(FIRMA_GRID):
            fallos.append(
                f"firma {id_}: bendecida con una rejilla distinta o ausente "
                f"({ben.get('grid')} != {list(FIRMA_GRID)}). Vuelve a bendecir "
                f"con --update-firmas {id_}."
            )
            continue
        if act["hash"] != ben["hash"]:
            fallos.append(
                f"firma {id_}: la escena cambio de estructura desde que se bendijo "
                f"(commit {ben.get('commit', '?')[:8]}, {ben.get('bendecidoEn', '?')}). "
                f"Revisa `src/components/sceneNav.siluetas.ts` para \"{id_}\": si la silueta "
                f"sigue representando la escena, vuelve a bendecir con "
                f"--update-firmas {id_}; si no, arregla la silueta primero y "
                f"bendice despues."
            )
    return fallos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base", required=True,
        help="Origen del build SERVIDO a medir -- para el arnes ENTERO, no "
             "solo para las firmas (p.ej. http://127.0.0.1:4173) -- NUNCA el "
             "dev server de Vite: su HMR corrompe el layout y miente en los "
             "dos sentidos (rules/verification.md). Sin default a proposito: "
             "un default que apuntara al dev server permitia medir o "
             "bendecir contra un DOM que nunca deberia contar como "
             "referencia. Obligatorio.",
    )
    parser.add_argument(
        "--update-firmas", nargs="+", metavar="ESCENA", default=None,
        choices=list(FIRMA_SELECTORES),
        help="Bendice SOLO las escenas nombradas (una o mas de: "
             f"{', '.join(FIRMA_SELECTORES)}) contra --base y las "
             "sobreescribe en scene-nav-firmas.json; las demas quedan "
             "intactas. Bendecir es un acto deliberado por escena, nunca "
             "todo-o-nada: nombra solo la que de verdad has revisado. "
             "No corre el resto del arnes.",
    )
    args = parser.parse_args()
    args.base = args.base.rstrip("/")  # evita `//?theme=...` si --base trae barra final

    es_dev = _es_dev_server(args.base)
    if es_dev is None:
        print(
            f"ERROR: no se pudo determinar si --base ({args.base}) es un "
            f"dev server de Vite -- el sondeo a /@vite/client fallo por una "
            f"razon de red (ver el AVISO anterior), no porque la ruta no "
            f"exista. Un arnes que no puede decidir esto no puede medir ni "
            f"bendecir nada contra ese origen: comprueba que --base esta "
            f"vivo y sirve el build ('npm run build && npx vite preview "
            f"--port 4173') antes de reintentar.",
            file=sys.stderr,
        )
        return 2
    if es_dev:
        print(
            f"ERROR: --base ({args.base}) es un dev server de Vite (responde "
            f"en /@vite/client). No se puede medir ni bendecir una firma "
            f"contra el, porque el HMR corrompe el layout "
            f"(rules/verification.md). Sirve el build "
            f"('npm run build && npx vite preview --port 4173') y apunta ahi.",
            file=sys.stderr,
        )
        return 2

    if args.update_firmas is not None:
        actuales, consola = medir_firmas(args.base)
        sucio = _arbol_sucio()
        if sucio is None:
            print(
                "aviso: no se pudo comprobar si el arbol de trabajo tiene "
                "cambios sin commitear (`git status` fallo) -- se bendice de "
                "todos modos, pero revisalo a mano antes de confiar en esta "
                "bendicion.",
                file=sys.stderr,
            )
        elif sucio:
            print(
                "aviso: el arbol de trabajo tiene cambios sin commitear -- la "
                "firma que se va a bendecir queda registrada contra el commit "
                "actual, pero puede NO reflejar lo que de verdad se midio. "
                "Revisa `git status` antes de dar por buena esta bendicion.",
                file=sys.stderr,
            )
        if consola:
            print(
                "ERROR: hubo errores de consola durante la medida -- no se "
                "bendice sobre un build que puede estar a medio montar. "
                "Arregla los errores y vuelve a intentarlo:",
                file=sys.stderr,
            )
            for m in consola:
                print(" -", m, file=sys.stderr)
            return 1
        bendecidas, cambiadas = guardar_firmas_bendecidas(actuales, args.update_firmas)
        print(json.dumps(bendecidas, indent=2, ensure_ascii=False))
        if cambiadas:
            print(f"\nfirmas bendecidas en {FIRMAS_PATH}: {cambiadas}")
        else:
            print(
                f"\nsin cambios: las escenas nombradas ({args.update_firmas}) ya "
                f"coincidian con lo bendecido en {FIRMAS_PATH}"
            )
        return 0

    fallos = []

    # --- Comprobaciones ESTATICAS, sin navegador: fallan rapido y no
    # dependen de que `--base` este sirviendo nada todavia. ---
    print("== estatico: SILUETAS dentro del plano de 1440x900")
    fallos_plano = verificar_piezas_dentro_del_plano()
    for f in fallos_plano:
        print(" -", f)
    if not fallos_plano:
        print(" (ninguna pieza se sale del plano)")
    fallos += fallos_plano

    print("\n== estatico: las tres listas de escenas concuerdan")
    fallos_listas = verificar_listas_de_escenas()
    for f in fallos_listas:
        print(" -", f)
    if not fallos_listas:
        print(" (SILUETAS, FIRMA_SELECTORES y sceneIndex coinciden)")
    fallos += fallos_listas

    print("\n== estatico: los textos de las siluetas siguen en el contenido real")
    fallos_disp = verificar_disp_contra_contenido()
    for f in fallos_disp:
        print(" -", f)
    if not fallos_disp:
        print(" (todos los `disp` de SILUETAS aparecen en su fuente de contenido)")
    fallos += fallos_disp

    for ancho, alto in ((1440, 900), (390, 844)):
        datos = medir_layout(ancho, alto, args.base)
        print(f"\n== {ancho}x{alto}")
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        fallos += comprobar(datos, ancho)

    adelanto = medir_sincronia(args.base)
    print(f"\nadelanto maximo del contenido sobre la barra: {adelanto} px")
    if adelanto is None:
        fallos.append("sincronia: no se midio ni un fotograma revelandose")
    elif adelanto > 0:
        fallos.append(f"sincronia: el contenido adelanta a la barra {adelanto}px (debe ser <= 0)")

    for reducido in (False, True):
        d = medir_tiempos(reducido, args.base)
        print(f"\n== tiempos ({'reducido' if reducido else 'normal'})")
        print(json.dumps(d, indent=2, ensure_ascii=False))
        fallos += comprobar_tiempos(d, reducido)

    c, a, v, esc = medir_estados_y_foco(args.base)
    print("\n== disparador y foco")
    print(json.dumps({"cerrado": c, "abierto": a, "tab": v, "escDevuelveFoco": esc},
                     indent=2, ensure_ascii=False))
    fallos += comprobar_estados(c, a, v, esc)

    ajenos = medir_ajenos(args.base)
    print("\n== el disparador en los temas que NO son Hyprland")
    print(json.dumps(ajenos, indent=2, ensure_ascii=False))
    fallos += comprobar_ajenos(ajenos)

    contraste = medir_contraste_rotulo(args.base)
    print("\n== contraste del rotulo visible del disparador (peor momento del scroll)")
    print(json.dumps(contraste, indent=2, ensure_ascii=False))
    fallos += comprobar_contraste(contraste)

    actuales, consola_firmas = medir_firmas(args.base)
    print("\n== firmas estructurales de las cinco escenas")
    print(json.dumps(
        {id_: {"hash": d["hash"], "piezas": d["piezas"]} for id_, d in actuales.items()},
        indent=2, ensure_ascii=False,
    ))
    if consola_firmas:
        print("consola (errores durante la medida de firmas):", consola_firmas)
        fallos += [f"firmas: error de consola: {m}" for m in consola_firmas]
    bendecidas = cargar_firmas_bendecidas()
    fallos += comprobar_firmas(actuales, bendecidas)

    if fallos:
        print("\nFALLOS:")
        for f in fallos:
            print(" -", f)
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
