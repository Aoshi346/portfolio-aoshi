#!/usr/bin/env python3
"""Arnes de la hoja de contactos (cortinilla de Hyprland).

Criterios 3 y 4 del spec 2026-08-06-hyprland-cortinilla-hoja-design.md.
Se lanza contra el dev server o contra el build servido. NO usa capturas para
medir animacion: eso llega en la Tarea 4 y muestrea desde dentro de la pagina.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:5173/?theme=hyprland"
CHROME = "/usr/bin/google-chrome"

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
    const fueraX = piezas.filter(x => {
      const b = x.getBoundingClientRect();
      return b.left > er.right - 1 || b.right < er.left + 1;
    });
    const fueraY = piezas.filter(x => {
      const b = x.getBoundingClientRect();
      return b.top > er.bottom - 1 || b.bottom < er.top + 1;
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


def medir_sincronia():
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900)
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


def medir_tiempos(reducido):
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900, reducido=reducido)
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


def medir_estados_y_foco():
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900)
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


def medir_ajenos():
    datos = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, executable_path=CHROME,
                               args=["--no-sandbox", "--use-gl=swiftshader"])
        for tema in ANCHO_AJENO:
            ctx = b.new_context(viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            pg.goto(URL.replace("theme=hyprland", f"theme={tema}"),
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


def medir_contraste_rotulo():
    from PIL import Image
    import io
    peor = {}
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900)
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
# informe `.superpowers/informe-gate-siluetas.md`, donde un indice de
# similitud silueta-vs-escena se probo contra las cinco escenas en mas de
# diez configuraciones distintas y el orden que dio salio invertido respecto
# a lo que un humano juzga fiel).
#
# Lo que SI comprueba: que ninguna escena real ha cambiado de estructura
# desde la ULTIMA VEZ que alguien miro su silueta a proposito y la bendijo.
# La pregunta no es "¿se parece la silueta a la escena?", es "¿ha cambiado
# la escena sin que nadie pasara por delante de su silueta?". El silencio es
# el fallo que de verdad ocurrio aqui (creditos, quien-es y contacto
# derivaron sin que nada avisara), no la deriva en si — la deriva es
# inevitable en un fichero que es una copia a mano; el silencio no lo era.
############################################################################

FIRMAS_PATH = Path(__file__).parent / "scene-nav-firmas.json"

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


def _celdas_pieza(p, w, h, cols, rows):
    pw = max(p["w"], 1)
    ph = max(p["h"], 1)
    x0 = max(p["x"], 0)
    y0 = max(p["y"], 0)
    x1 = min(p["x"] + pw, w)
    y1 = min(p["y"] + ph, h)
    if x1 <= x0 or y1 <= y0 or not w or not h:
        return
    c0 = max(0, min(cols - 1, int(x0 / w * cols)))
    c1 = max(0, min(cols - 1, int((x1 - 0.001) / w * cols)))
    r0 = max(0, min(rows - 1, int(y0 / h * rows)))
    r1 = max(0, min(rows - 1, int((y1 - 0.001) / h * rows)))
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


def calcular_firma(datos, cols, rows):
    """De `{w, h, pieces}` a `(hash, celdas_ordenadas)`. Determinista: mismo
    layout, mismo hash — es justo lo que exige la prueba de estabilidad."""
    celdas = set()
    for p in datos["pieces"]:
        celdas.update(_celdas_pieza(p, datos["w"], datos["h"], cols, rows))
    ordenadas = sorted(f"{x}:{y}" for x, y in celdas)
    firma = hashlib.sha256(",".join(ordenadas).encode()).hexdigest()
    return firma, ordenadas


def abrir_firmas(pw, base):
    b = pw.chromium.launch(headless=True, executable_path=CHROME,
                           args=["--no-sandbox", "--use-gl=swiftshader"])
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    pg = ctx.new_page()
    consola = []
    pg.on("console", lambda m: consola.append(m.text) if m.type == "error" else None)
    pg.goto(f"{base}/?theme=hyprland", wait_until="domcontentloaded", timeout=40000)
    pg.wait_for_timeout(6000)  # encendido de Ascua + shader, layout asentado
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
            pg.wait_for_timeout(500)
            datos = pg.evaluate(FIRMA_JS, sel)
            if datos is None:
                salida[id_] = {"hash": None, "celdas": [], "piezas": 0}
                continue
            firma, celdas = calcular_firma(datos, cols, rows)
            salida[id_] = {"hash": firma, "celdas": celdas, "piezas": len(datos["pieces"])}
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


def cargar_firmas_bendecidas():
    if not FIRMAS_PATH.exists():
        return {}
    return json.loads(FIRMAS_PATH.read_text(encoding="utf-8"))


def guardar_firmas_bendecidas(actuales):
    """Escribe `scene-nav-firmas.json`. Bendecir es un acto deliberado que se
    revisa en el diff (igual que `--update-baseline` en `verify.py`): este
    metodo nunca se llama solo desde el camino de comprobacion, solo desde
    `--update-firmas`."""
    commit = _commit_actual()
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    bendecidas = {
        id_: {
            "hash": d["hash"],
            "grid": list(FIRMA_GRID),
            "commit": commit,
            "bendecidoEn": ahora,
        }
        for id_, d in actuales.items()
    }
    FIRMAS_PATH.write_text(json.dumps(bendecidas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return bendecidas


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
                f"Revisa su silueta en sceneNav.siluetas.ts y bendice con --update-firmas."
            )
            continue
        if list(ben.get("grid", FIRMA_GRID)) != list(FIRMA_GRID):
            fallos.append(
                f"firma {id_}: bendecida con una rejilla distinta ({ben.get('grid')} != "
                f"{list(FIRMA_GRID)}). Vuelve a bendecir con --update-firmas."
            )
            continue
        if act["hash"] != ben["hash"]:
            fallos.append(
                f"firma {id_}: la escena cambio de estructura desde que se bendijo "
                f"(commit {ben.get('commit', '?')[:8]}, {ben.get('bendecidoEn', '?')}). "
                f"Revisa `src/components/sceneNav.siluetas.ts` para \"{id_}\": si la silueta "
                f"sigue representando la escena, vuelve a bendecir con --update-firmas; si no, "
                f"arregla la silueta primero y bendice despues."
            )
    return fallos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base", default="http://127.0.0.1:5173",
        help="Origen del build a medir (el build servido, nunca el dev server, para las firmas)",
    )
    parser.add_argument(
        "--update-firmas", action="store_true",
        help="Recalcula las cinco firmas estructurales contra --base y sobreescribe "
             "scene-nav-firmas.json. No corre el resto del arnes.",
    )
    args = parser.parse_args()

    if args.update_firmas:
        actuales, consola = medir_firmas(args.base)
        bendecidas = guardar_firmas_bendecidas(actuales)
        print(json.dumps(bendecidas, indent=2, ensure_ascii=False))
        print(f"\nfirmas bendecidas en {FIRMAS_PATH}")
        if consola:
            print("\naviso: hubo errores de consola durante la medida:")
            for m in consola:
                print(" -", m)
        return 0

    fallos = []
    for ancho, alto in ((1440, 900), (390, 844)):
        datos = medir_layout(ancho, alto)
        print(f"== {ancho}x{alto}")
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        fallos += comprobar(datos, ancho)

    adelanto = medir_sincronia()
    print(f"\nadelanto maximo del contenido sobre la barra: {adelanto} px")
    if adelanto is None:
        fallos.append("sincronia: no se midio ni un fotograma revelandose")
    elif adelanto > 0:
        fallos.append(f"sincronia: el contenido adelanta a la barra {adelanto}px (debe ser <= 0)")

    for reducido in (False, True):
        d = medir_tiempos(reducido)
        print(f"\n== tiempos ({'reducido' if reducido else 'normal'})")
        print(json.dumps(d, indent=2, ensure_ascii=False))
        fallos += comprobar_tiempos(d, reducido)

    c, a, v, esc = medir_estados_y_foco()
    print("\n== disparador y foco")
    print(json.dumps({"cerrado": c, "abierto": a, "tab": v, "escDevuelveFoco": esc},
                     indent=2, ensure_ascii=False))
    fallos += comprobar_estados(c, a, v, esc)

    ajenos = medir_ajenos()
    print("\n== el disparador en los temas que NO son Hyprland")
    print(json.dumps(ajenos, indent=2, ensure_ascii=False))
    fallos += comprobar_ajenos(ajenos)

    contraste = medir_contraste_rotulo()
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
