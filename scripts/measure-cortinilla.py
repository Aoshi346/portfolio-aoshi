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

# El haz debe cubrir el encuadre entero. 1% de margen para el redondeo de
# `getBoundingClientRect()`; el defecto real cubria 0,18 del ancho.
TOLERANCIA_HAZ = 0.01

LAYOUT_JS = """() => {
  const panel = document.querySelector('.scene-index');
  const filas = [...panel.querySelectorAll('.scene-index-row')];
  const r = e => { const b = e.getBoundingClientRect();
    return {w: Math.round(b.width), h: Math.round(b.height),
            t: Math.round(b.top), l: Math.round(b.left)}; };
  const primeraFila = filas[0];
  const encuadre = primeraFila?.querySelector('.scene-shot');
  const encuadreRect = encuadre ? encuadre.getBoundingClientRect() : null;
  // El primer hijo NO beam: el haz se dibuja sobre el ENCUADRE, no sobre el
  // plano de 1440x900, asi que no se escala y no sirve para leer el factor.
  // Cualquier otro hijo si lo lleva.
  //
  // Este comentario decia antes que el haz "lleva `transform: none`". Lo
  // llevaba escrito y no lo cumplia: perdia por especificidad contra la regla
  // de escala ((0,3,0) contra (0,3,1)) y se encogia a 49,1x30,7 px dentro de un
  // encuadre de 266x166,3. El arnes miraba a otro lado justo donde estaba el
  // fallo, y por eso hace falta `haz` aqui abajo: se mide, no se declara.
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
    // El haz es lo que levanta la silueta del negro: sin el, el fotograma es
    // un rectangulo vacio (las piezas se dibujan en `--rule`, #3d1c1c sobre
    // #0b0404). Debe cubrir el encuadre entero, no una esquina.
    haz: (() => {
      const h = encuadre?.querySelector('.scene-shot-beam');
      if (!h || !encuadreRect) return null;
      const b = h.getBoundingClientRect();
      return {ancho: b.width, alto: b.height,
              cubreAncho: b.width / encuadreRect.width,
              cubreAlto: b.height / encuadreRect.height};
    })(),
    // La asercion que faltaba, y la unica que habria cazado que las piezas
    // caian fuera del encuadre: no basta con que la silueta EXISTA
    // (`siluetasVacias`) ni con que el factor de escala cuadre, porque el
    // factor se lee del plano y el plano puede medir bien mientras sus piezas
    // quedan recortadas. Se cuentan las que caen fuera de verdad.
    piezasFuera: (() => {
      if (!encuadre || !encuadreRect) return null;
      const plano = encuadre.querySelector('.scene-shot-plano');
      if (!plano) return null;
      const piezas = [...plano.children];
      const fuera = piezas.filter(p => {
        const b = p.getBoundingClientRect();
        return b.top > encuadreRect.bottom - 1 || b.bottom < encuadreRect.top + 1
            || b.left > encuadreRect.right - 1 || b.right < encuadreRect.left + 1;
      });
      return {total: piezas.length, fuera: fuera.length};
    })(),
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
    pf = datos.get("piezasFuera")
    if pf is None:
        fallos.append(f"{ancho}: no hay `.scene-shot-plano` en el primer encuadre")
    elif pf["fuera"]:
        fallos.append(
            f"{ancho}: {pf['fuera']} de {pf['total']} piezas de la silueta caen fuera del "
            f"encuadre y las recorta `overflow: hidden`"
        )
    haz = datos.get("haz")
    if haz is None:
        fallos.append(f"{ancho}: no hay `.scene-shot-beam` en el primer encuadre")
    else:
        for eje in ("cubreAncho", "cubreAlto"):
            if abs(haz[eje] - 1) > TOLERANCIA_HAZ:
                fallos.append(
                    f"{ancho}: el haz cubre {haz[eje]:.3f} del encuadre en {eje[5:].lower()} "
                    f"({haz['ancho']:.1f}x{haz['alto']:.1f}px); debe cubrirlo entero. "
                    f"Sin haz la silueta no se ve: se dibuja en --rule sobre --color-ink"
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


def medir_tiempos(reducido):
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900, reducido=reducido)
        abrir_cortinilla(pg)
        datos = pg.evaluate(TIEMPOS_JS)
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
        if datos["paradas"] != 5:
            fallos.append(f"reducido: {datos['paradas']} filas, la funcion no puede degradarse")
    else:
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
        for _ in range(6):
            visitados.append(pg.evaluate(
                "() => document.activeElement?.getAttribute('href') ?? null"))
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
    unicos = [v for v in visitados[:5] if v]
    if len(set(unicos)) != 5:
        fallos.append(f"Tab no da cinco paradas distintas: {visitados}")
    if visitados[5] != visitados[0]:
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
ANCHO_AJENO = {"vice": 168.81, "caelestia": 152.0}
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


def main():
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

    if fallos:
        print("\nFALLOS:")
        for f in fallos:
            print(" -", f)
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
