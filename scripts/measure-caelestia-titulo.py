#!/usr/bin/env python3
"""
Arnes de la escena Titulo de Caelestia (fase B1).

Spec: docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md

Se lanza SIEMPRE contra el build de produccion servido, nunca contra
`npm run dev`: el HMR de Vite corrompe las medidas de layout.

    export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
    npm run build && npx vite preview --port 4173 &
    python3 scripts/measure-caelestia-titulo.py --base http://localhost:4173

Cada asercion de este fichero nacio de un fallo concreto documentado en el
spec. Ninguna se da por buena sin haberla visto dar rojo contra el fallo que
dice cazar.
"""
import argparse
import base64
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

VENTANA = {"width": 1412, "height": 748}
FALLOS: list[str] = []


def assert_que(cond: bool, etiqueta: str) -> None:
    print(("  OK   " if cond else "  FALLO ") + etiqueta)
    if not cond:
        FALLOS.append(etiqueta)


def abrir(pg, base: str, hora: str | None = None) -> None:
    """Carga Caelestia. `hora` en HH:MM ancla el reloj del visitante a esa hora.

    NO es una foto fija de un solo instante: `Date.now()` sigue avanzando en
    tiempo real desde ese ancla. Congelarlo del todo (un `Date.now()`
    constante) rompe GSAP -- su ticker mide el tiempo transcurrido como
    `Date.now() - _lastUpdate` (`node_modules/gsap/dist/gsap.js:1205`), asi
    que con el reloj parado ese delta es siempre 0 y NINGUNA animacion avanza
    nunca, en ninguna pagina abierta con `hora`. Se descubrio con `roce()`
    (tarea 7): el lienzo no se movia ni con `pg.hover()` ni disparando un
    `PointerEvent` a mano dentro de la pagina -- ni la propia timeline de
    `montarEntrada` avanzaba, solo que nadie lo habia comprobado antes porque
    los tests previos solo miran el estado INICIAL o el de movimiento
    reducido (que se salta GSAP entero). Ancorar y dejar avanzar mantiene la
    hora estable para lo que dura un test (segundos) sin parar el reloj que
    GSAP necesita.
    """
    if hora is not None:
        hh, mm = (int(x) for x in hora.split(":"))
        pg.add_init_script(
            "(() => { const R = Date;"
            " const inicioReal = R.now();"
            f" const inicioAncla = new R(2026, 7, 26, {hh}, {mm}, 0).getTime();"
            " class F extends R {"
            "   constructor(...a){"
            "     return a.length ? new R(...a) : new R(inicioAncla + (R.now() - inicioReal)); }"
            "   static now(){ return inicioAncla + (R.now() - inicioReal); } }"
            " window.Date = F; })()"
        )
    pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(4000)


def optica(pg, base: str) -> None:
    print("\n[optica] el nombre declara sus ejes y el shell conserva los suyos")
    abrir(pg, base, "13:00")
    ejes = pg.evaluate(
        "() => {"
        " const cs = getComputedStyle(document.documentElement);"
        " const tit = document.querySelector('#hero .cae-nombre');"
        " return {"
        "  token: cs.getPropertyValue('--cae-display-axes-cartel').trim(),"
        "  marcaToken: cs.getPropertyValue('--cae-display-axes').trim(),"
        "  nombre: tit ? getComputedStyle(tit).fontVariationSettings : ''"
        " }; }"
    )
    assert_que("144" in ejes["token"], f"el token --cae-display-axes-cartel existe y trae opsz 144 ({ejes['token']!r})")
    assert_que('"opsz" 9' in ejes["marcaToken"], f"el token --cae-display-axes del shell sigue en opsz 9 ({ejes['marcaToken']!r})")
    assert_que('"opsz" 144' in ejes["nombre"], f"el nombre usa opsz 144 ({ejes['nombre']!r})")


LEE_LIENZO = """() => new Promise(resolve => {
  /* La lectura tiene que caer DENTRO de un requestAnimationFrame: sin
     `preserveDrawingBuffer` (que shaderBackground.ts no pide, a proposito,
     por coste), el navegador libera el buffer de dibujo tras componer el
     fotograma, y un readPixels que llega despues -- que es lo que hace un
     evaluate() normal, corre en una macrotarea aparte -- lee CEROS siempre,
     tanto si el fondo se mueve como si no. Medido: fuera de RAF, promedio 0
     en 100% de los pixeles; dentro, promedio 248 (fondo claro real). */
  requestAnimationFrame(() => {
    const c = document.querySelector('canvas');
    if (!c) { resolve(null); return; }
    const g = c.getContext('webgl');
    if (!g) { resolve(null); return; }
    const px = new Uint8Array(c.width * c.height * 4);
    g.readPixels(0, 0, c.width, c.height, g.RGBA, g.UNSIGNED_BYTE, px);
    const lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    let lo = 1, hi = 0, muestras = [];
    const sx = Math.max(1, Math.floor(c.width / 180)), sy = Math.max(1, Math.floor(c.height / 90));
    for (let y = 0; y < c.height; y += sy) for (let x = 0; x < c.width; x += sx) {
      const i = (y * c.width + x) * 4;
      const L = 0.2126 * lin(px[i]) + 0.7152 * lin(px[i+1]) + 0.0722 * lin(px[i+2]);
      if (L < lo) lo = L; if (L > hi) hi = L;
      muestras.push(px[i]);
    }
    resolve({ lo, hi, muestras });
  });
})"""


def contraste(a: float, b: float) -> float:
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def luz_texto(pg) -> float:
    return pg.evaluate(
        "() => { const cv = document.createElement('canvas'); cv.width = cv.height = 1;"
        " const k = cv.getContext('2d');"
        " k.fillStyle = getComputedStyle(document.documentElement)"
        "   .getPropertyValue('--cae-on-surface').trim();"
        " k.fillRect(0,0,1,1); const d = k.getImageData(0,0,1,1).data;"
        " const lin = (v) => { v /= 255; return v <= 0.04045 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };"
        " return 0.2126*lin(d[0]) + 0.7152*lin(d[1]) + 0.0722*lin(d[2]); }"
    )


def fondo(pg, base: str) -> None:
    print("\n[fondo] el shader compila, se mueve y aguanta las 24 h")

    # 1. Compila. Un shader roto deja el lienzo negro y hace que la asercion de
    #    movimiento de mas abajo de 0 %, que es justo su sintoma. Sin esta
    #    asercion el fallo se lee como "no se mueve" y se busca donde no es.
    abrir(pg, base, "13:00")
    compila = pg.evaluate(
        "() => { const c = document.querySelector('canvas');"
        " if (!c) return false; const g = c.getContext('webgl');"
        " return !!g && g.getParameter(g.CURRENT_PROGRAM) !== null; }"
    )
    assert_que(bool(compila), "el shader compila y hay programa activo")

    # 2. Se mueve. Con solo giro y latido cambiaba el 3 % de las muestras en 8 s;
    #    con la orbita, el 28,8 %. El piso se pone en 10 %.
    a = pg.evaluate(LEE_LIENZO)
    pg.wait_for_timeout(8000)
    b = pg.evaluate(LEE_LIENZO)
    if a and b:
        cambian = sum(1 for x, y in zip(a["muestras"], b["muestras"]) if abs(x - y) > 2)
        pct = 100 * cambian / max(1, len(a["muestras"]))
    else:
        pct = 0.0
    assert_que(pct >= 10.0, f"el fondo se mueve: {pct:.1f} % de las muestras cambian en 8 s (piso 10 %)")

    # 3. Barrido de las 24 h. Un morfado puede producir una silueta que NINGUNO
    #    de los cinco estados tiene por separado: medir solo los cinco asentados
    #    deja las transiciones sin vigilar.
    peor, cuando = 99.0, ""
    for minutos in range(0, 1440, 15):
        hora = f"{minutos // 60:02d}:{minutos % 60:02d}"
        pg2 = pg.context.browser.new_page()
        pg2.set_viewport_size(VENTANA)
        abrir(pg2, base, hora)
        lienzo = pg2.evaluate(LEE_LIENZO)
        if lienzo:
            lt = luz_texto(pg2)
            c = min(contraste(lt, lienzo["lo"]), contraste(lt, lienzo["hi"]))
            if c < peor:
                peor, cuando = c, hora
        pg2.close()
    assert_que(peor >= 4.5, f"peor contraste del dia {peor:.2f}:1 a las {cuando} (piso AA 4.5:1)")


def _oklab_to_srgb255(l: float, a_: float, b_: float) -> tuple[float, float, float]:
    """OKLab -> sRGB (0..255). Mismas matrices que `scripts/verify.py` y
    `scripts/measure-caelestia-obra.py` (Bjorn Ottosson)."""

    def clamp01(v: float) -> float:
        return max(0.0, min(1.0, v))

    l_ = l + 0.3963377774 * a_ + 0.2158037573 * b_
    m_ = l - 0.1055613458 * a_ - 0.0638541728 * b_
    s_ = l - 0.0894841775 * a_ - 1.2914855480 * b_
    l3, m3, s3 = l_**3, m_**3, s_**3

    lin_r = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    lin_g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    lin_b = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3

    def to_gamma(c: float) -> float:
        c = clamp01(c)
        return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

    return to_gamma(lin_r) * 255, to_gamma(lin_g) * 255, to_gamma(lin_b) * 255


def _parse_rgb(css: str) -> tuple[float, float, float, float] | None:
    """Parser minimo de color computado: `rgb()`/`rgba()` y `oklch()` (lo que
    Chromium devuelve para los tokens de Caelestia, resueltos via `oklch()`
    en `themes.css`). Si no reconoce el formato devuelve `None` y la
    asercion de contraste lo reporta en vez de fallar en silencio."""
    css = css.strip()

    if css.startswith("oklch("):
        inner = css[css.index("(") + 1 : css.rindex(")")]
        comps, _, alpha_s = inner.partition("/")
        vals = comps.split()
        ell, c, h = float(vals[0]), float(vals[1]), float(vals[2])
        import math

        rad = math.radians(h)
        a_ = c * math.cos(rad)
        b_ = c * math.sin(rad)
        r, g, b = _oklab_to_srgb255(ell, a_, b_)
        a = float(alpha_s.strip()) if alpha_s.strip() else 1.0
        return r, g, b, a

    if css.startswith("rgb(") or css.startswith("rgba("):
        inner = css[css.index("(") + 1 : css.rindex(")")]
        parts = [p.strip() for p in inner.replace("/", ",").split(",") if p.strip()]
        if len(parts) < 3:
            return None
        r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
        a = float(parts[3]) if len(parts) > 3 else 1.0
        return r, g, b, a

    return None


def _luminancia(rgb: tuple[float, float, float]) -> float:
    def canal(c: float) -> float:
        cs = c / 255
        return cs / 12.92 if cs <= 0.03928 else ((cs + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def _ratio(fg: tuple[float, float, float], bg: tuple[float, float, float]) -> float:
    """Ratio de contraste WCAG. Reusa `contraste()` (ya definido arriba para
    el barrido del shader), que opera sobre luminancias -- aqui se le pasan
    las de dos colores parseados en vez de las del canvas."""
    return contraste(_luminancia(fg), _luminancia(bg))


def literal_intro() -> str:
    """`identity.intro` tal como esta escrito en content.ts. El arnes no puede
    importar TypeScript, asi que lo lee como texto; si no lo encuentra FALLA en
    vez de devolver un valor por defecto (un gate que adivina no vigila)."""
    fuente = (Path(__file__).resolve().parent.parent / "src" / "data" / "content.ts").read_text(encoding="utf-8")
    m = re.search(r'^\s*intro:\s*"([^"]+)",', fuente, re.M)
    assert m, "no se encuentra `intro: \"...\"` en content.ts"
    return m.group(1)


MIDE_CAJAS = """() => {
  const r = (e) => { const b = e.getBoundingClientRect();
    return { l: b.left, r: b.right, t: b.top, b: b.bottom, cx: (b.left + b.right) / 2, cy: (b.top + b.bottom) / 2 }; };
  const hero = document.querySelector('#hero');
  const dib = hero && hero.querySelector('.cae-nombre-dib');
  const rol = hero && hero.querySelector('.cae-rol');
  const svgs = hero ? Array.from(hero.querySelectorAll('.cae-nombre-svg')).filter(s => s.getClientRects().length > 0) : [];
  return {
    hero: hero ? r(hero) : null,
    dib: dib ? r(dib) : null,
    rol: rol ? r(rol) : null,
    svgs: svgs.map(r),
  };
}"""


MIDE_DIBUJO = """() => {
  const fs = parseFloat(getComputedStyle(document.querySelector('#hero .cae-nombre')).fontSize);
  const svgs = Array.from(document.querySelectorAll('#hero .cae-nombre-svg'))
    .filter((s) => s.getClientRects().length > 0)
    .map((s) => { const b = s.getBoundingClientRect(); return { w: b.width, h: b.height }; });
  return { fs, svgs };
}"""


def dibujo_visible(pg, etiqueta: str) -> None:
    """El nombre que se ve tiene caja real: cada SVG mostrado mide > 0 x > 0 y
    el mas ancho llega al 60 % de lo esperado para su escalon (7,903 em en una
    linea; 5,2 em la linea larga, «Blanco Sanz», en dos). Caza el SVG medido
    con getBBox mientras estaba oculto (0 x 0 y el nombre desaparece)."""
    d = pg.evaluate(MIDE_DIBUJO)
    svgs = d["svgs"]
    assert_que(bool(svgs) and all(x["w"] > 0 and x["h"] > 0 for x in svgs), f"[{etiqueta}] cada SVG mostrado tiene caja > 0 ({svgs})")
    esperado_em = 5.2 if len(svgs) == 2 else 7.903
    ancho = max((x["w"] for x in svgs), default=0)
    assert_que(ancho >= 0.6 * esperado_em * d["fs"], f"[{etiqueta}] el nombre visible llega al 60 % de su ancho ({ancho:.0f} px de {esperado_em * d['fs']:.0f})")


def nombre(pg, base: str) -> None:
    print("\n[nombre] el nombre y el rol de la escena: DOM accesible, centrado, dentro de la ventana, contraste")
    intro = literal_intro()
    pg.emulate_media(reduced_motion="reduce")
    try:
        for hora in ("13:00", "23:00"):
            abrir(pg, base, hora)
            pg.set_viewport_size(VENTANA)
            pg.wait_for_timeout(600)

            h1s = pg.locator("#hero h1").count()
            assert_que(h1s == 1, f"[{hora}] #hero tiene exactamente un h1 ({h1s})")
            titulos = pg.locator("#hero").get_by_role("heading", level=1)
            accesible = titulos.first.inner_text() if titulos.count() == 1 else ""
            assert_que(accesible.strip() == "Aoshi Blanco Sanz", f"[{hora}] nombre accesible del h1 ({accesible!r})")
            # Los SVG de una y de dos lineas conviven en el DOM: cuenta los del
            # juego que se ve (los 15 glifos del nombre, una sola vez).
            n_paths = pg.evaluate(
                "() => Array.from(document.querySelectorAll('#hero .cae-nombre-svg'))"
                ".filter((s) => s.getClientRects().length > 0)"
                ".reduce((n, s) => n + s.querySelectorAll('path').length, 0)"
            )
            oculto = pg.evaluate(
                "() => { const d = document.querySelector('#hero .cae-nombre-dib');"
                " return d ? d.getAttribute('aria-hidden') : null; }"
            )
            assert_que(oculto == "true", f"[{hora}] .cae-nombre-dib va aria-hidden ({oculto!r})")
            assert_que(n_paths == 15, f"[{hora}] el dibujo visible tiene 15 path en total ({n_paths})")
            rol = pg.evaluate(
                "() => { const e = document.querySelector('#hero p.cae-rol'); return e ? e.textContent : null; }"
            )
            assert_que(rol == intro, f"[{hora}] el rol es el literal de content.ts ({rol!r})")

            c = pg.evaluate(MIDE_CAJAS)
            if c["hero"] and c["dib"] and c["rol"]:
                assert_que(
                    abs(c["dib"]["cx"] - c["hero"]["cx"]) <= 2,
                    f"[{hora}] el dibujo esta centrado en horizontal ({c['dib']['cx']:.1f} vs {c['hero']['cx']:.1f})",
                )
                assert_que(
                    abs(c["rol"]["cx"] - c["hero"]["cx"]) <= 2,
                    f"[{hora}] el rol esta centrado en horizontal ({c['rol']['cx']:.1f} vs {c['hero']['cx']:.1f})",
                )
                bloque_cy = (c["dib"]["t"] + c["rol"]["b"]) / 2
                assert_que(
                    abs(bloque_cy - c["hero"]["cy"]) <= 4,
                    f"[{hora}] el bloque nombre+rol esta centrado en vertical ({bloque_cy:.1f} vs {c['hero']['cy']:.1f})",
                )
            else:
                assert_que(False, f"[{hora}] existen #hero, .cae-nombre-dib y .cae-rol para medir el centrado")

        abrir(pg, base, "13:00")
        for ancho, alto, esperados in ((390, 844, 2), (641, 900, 1), (768, 900, 1), (901, 900, 1), (1101, 900, 1), (1440, 900, 1)):
            pg.set_viewport_size({"width": ancho, "height": alto})
            pg.wait_for_timeout(500)
            c = pg.evaluate(MIDE_CAJAS)
            assert_que(len(c["svgs"]) == esperados, f"[{ancho}] hay {esperados} SVG visibles ({len(c['svgs'])})")
            if c["hero"]:
                dentro = all(
                    s["l"] >= c["hero"]["l"] - 0.5 and s["r"] <= c["hero"]["r"] + 0.5
                    and s["t"] >= c["hero"]["t"] - 0.5 and s["b"] <= c["hero"]["b"] + 0.5
                    for s in c["svgs"]
                )
                assert_que(bool(c["svgs"]) and dentro, f"[{ancho}] cada SVG queda dentro de #hero ({c['svgs']})")

        # Spec: dos lineas hasta 640 px; a 641 ya es una (el brief decia 2, el spec manda).
        # El dibujo sobrevive al cambio de ancho (medido una sola vez, en em).
        for inicio, final in (((390, 844), (1440, 900)), ((1440, 900), (390, 844))):
            pg.set_viewport_size({"width": inicio[0], "height": inicio[1]})
            abrir(pg, base, "13:00")
            dibujo_visible(pg, f"carga a {inicio[0]}")
            pg.set_viewport_size({"width": final[0], "height": final[1]})
            pg.wait_for_timeout(500)
            dibujo_visible(pg, f"{inicio[0]} -> {final[0]}")

        # Contraste del rol sobre el fondo real: la captura bajo su caja.
        for hora in ("13:00", "23:00"):
            abrir(pg, base, hora)
            pg.set_viewport_size(VENTANA)
            pg.wait_for_timeout(600)
            d = pg.evaluate(
                "() => { const e = document.querySelector('#hero p.cae-rol'); if (!e) return null;"
                " const b = e.getBoundingClientRect();"
                " return { fg: getComputedStyle(e).color, x: b.left, y: b.top, w: b.width, h: b.height }; }"
            )
            assert_que(d is not None, f"[{hora}] existe el rol para medir su contraste")
            if d is None:
                continue
            fg = _parse_rgb(d["fg"])
            if not fg:
                assert_que(False, f"[{hora}] no se pudo parsear el color del rol ({d['fg']})")
                continue
            # Se oculta el texto para muestrear solo el fondo bajo la caja.
            pg.add_style_tag(content="#hero p.cae-rol { color: transparent !important; }")
            png = pg.screenshot(clip={"x": d["x"], "y": d["y"], "width": max(d["w"], 1), "height": max(d["h"], 1)})
            muestra = pg.evaluate(
                """async (b64) => {
                  const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
                  const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height;
                  const k = cv.getContext('2d'); k.drawImage(img, 0, 0);
                  const px = k.getImageData(0, 0, cv.width, cv.height).data;
                  let r = 0, g = 0, b = 0, n = 0;
                  for (let i = 0; i < px.length; i += 4) { r += px[i]; g += px[i+1]; b += px[i+2]; n++; }
                  return [r / n, g / n, b / n];
                }""",
                base64.b64encode(png).decode(),
            )
            ratio = _ratio(fg[:3], tuple(muestra))
            assert_que(ratio >= 4.5, f"[{hora}] el rol cumple AA sobre el fondo real: {ratio:.2f}:1 (piso 4.5)")
    finally:
        pg.emulate_media(reduced_motion="no-preference")
        pg.set_viewport_size(VENTANA)


def sin_recorte(clip: str | None) -> bool:
    """`none` o un inset() con todos los lados a cero (GSAP lo deja en 0%)."""
    if clip == "none":
        return True
    m = re.fullmatch(r"inset\(([^)]*)\)", clip or "")
    return bool(m) and all(float(x.rstrip("px%")) == 0 for x in m.group(1).split())


LEE_TRAZO = """() => {
  const vis = (p) => { const s = p.ownerSVGElement; return !!s && s.getClientRects().length > 0; };
  const todos = Array.from(document.querySelectorAll('#hero .cae-nombre-dib path'));
  const f = (p) => ({ fill: parseFloat(getComputedStyle(p).fillOpacity), stroke: parseFloat(getComputedStyle(p).strokeOpacity), off: parseFloat(getComputedStyle(p).strokeDashoffset) });
  const rol = document.querySelector('#hero .cae-rol');
  return {
    clase: document.documentElement.classList.contains('js-cae-entrada'),
    total: todos.length,
    visibles: todos.filter(vis).map(f),
    ocultos: todos.filter((p) => !vis(p)).map(f),
    rol: rol ? getComputedStyle(rol).clipPath : null,
    dur: window.__CAE_ENTRADA__ ? window.__CAE_ENTRADA__.duracion : null,
  };
}"""


def entrada(pg, base: str) -> None:
    print("\n[entrada] el nombre se dibuja a trazo y el rol se corta despues")
    # Movimiento normal. Pagina propia, sin reloj anclado: lo que se mide es
    # la entrada desde que la coreografia monta (window.__CAE_ENTRADA__).
    ctx = pg.context.browser.new_context(viewport=VENTANA)
    pn = ctx.new_page()
    pn.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    try:
        pn.wait_for_function("() => !!window.__CAE_ENTRADA__", timeout=20000)
    except Exception:
        assert_que(False, "la entrada expone window.__CAE_ENTRADA__ al montar")
        ctx.close()
        return
    ini = pn.evaluate(LEE_TRAZO)
    assert_que(ini["total"] == 30, f"hay 30 path en el DOM (15 + 5 + 10) ({ini['total']})")
    assert_que(len(ini["visibles"]) == 15, f"a 1412 px se ven 15 glifos ({len(ini['visibles'])})")
    assert_que(
        all(x["fill"] < 0.1 for x in ini["visibles"]),
        f"al montar, antes de 300 ms, ningun glifo visible esta relleno ({[x['fill'] for x in ini['visibles']][:3]}...)",
    )
    assert_que(not ini["clase"], "js-cae-entrada ya se retiro al escribir los estados iniciales")
    assert_que(not sin_recorte(ini["rol"]), f"el rol arranca recortado ({ini['rol']!r})")
    # Los tiempos DECLARADOS (deterministas): 2,5 s +- 0,05.
    assert_que(
        ini["dur"] is not None and abs(ini["dur"] - 2.5) <= 0.05,
        f"la timeline declara 2,5 s +- 0,05 ({ini['dur']})",
    )
    # Escalonado: a ~0,5 s el primer glifo ya traza y el ultimo (que arranca a
    # los 0,77 s, 14 x 55 ms) aun no ha empezado.
    pn.wait_for_timeout(350)
    mid = pn.evaluate(LEE_TRAZO)["visibles"]
    assert_que(
        mid[0]["off"] < 0.95 and mid[-1]["off"] > 0.99,
        f"a ~0,5 s el primer glifo ya traza y el ultimo no ha empezado (off {mid[0]['off']:.2f} / {mid[-1]['off']:.2f})",
    )
    # Final: duracion declarada + 1,5 s de margen explicito.
    pn.wait_for_timeout(3100)
    fin = pn.evaluate(LEE_TRAZO)
    assert_que(not fin["clase"], "no queda js-cae-entrada en <html>")
    assert_que(
        len(fin["visibles"]) == 15 and all(x["fill"] > 0.99 and x["stroke"] < 0.01 for x in fin["visibles"]),
        "los 15 glifos visibles quedan rellenos y sin contorno",
    )
    assert_que(
        len(fin["ocultos"]) == 15 and all(x["fill"] > 0.99 and x["stroke"] < 0.01 for x in fin["ocultos"]),
        "los 15 glifos del otro juego tambien terminan en el estado final",
    )
    assert_que(sin_recorte(fin["rol"]), f"el rol queda sin recorte ({fin['rol']!r})")
    ctx.close()

    # Movimiento reducido: a los 300 ms el estado ya es el final.
    ctx = pg.context.browser.new_context(viewport=VENTANA, reduced_motion="reduce")
    pr = ctx.new_page()
    pr.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    try:
        pr.wait_for_function(
            "() => document.querySelectorAll('#hero .cae-nombre-dib path').length === 30", timeout=20000
        )
    except Exception:
        pass
    pr.wait_for_timeout(300)
    est = pr.evaluate(LEE_TRAZO)
    assert_que(
        est["total"] == 30 and all(x["fill"] > 0.99 for x in est["visibles"]),
        "con movimiento reducido el nombre esta relleno a los 300 ms",
    )
    pr.wait_for_timeout(3500)
    est = pr.evaluate(LEE_TRAZO)
    assert_que(
        all(x["fill"] > 0.99 and x["stroke"] < 0.01 for x in est["visibles"] + est["ocultos"])
        and not est["clase"]
        and sin_recorte(est["rol"]),
        f"con movimiento reducido el estado final es estable ({est['rol']!r})",
    )
    ctx.close()


def roce(pg, base: str) -> None:
    print("\n[roce] el fondo se aparta al pasar el raton")
    abrir(pg, base, "13:00")
    antes = pg.evaluate("() => getComputedStyle(document.querySelector('canvas')).transform")
    pg.hover(".cae-dock-item")
    pg.wait_for_timeout(900)
    durante = pg.evaluate("() => getComputedStyle(document.querySelector('canvas')).transform")
    assert_que(antes != durante, f"el lienzo se desplaza con el raton encima ({antes!r} -> {durante!r})")
    pg.mouse.move(2, 2)
    pg.wait_for_timeout(1100)
    despues = pg.evaluate("() => getComputedStyle(document.querySelector('canvas')).transform")
    assert_que(despues == antes, "y vuelve a su sitio al salir")


def escritorio_desnudo(pg, base: str) -> None:
    """Revision final (Importante 4): el fix P0 del gate de Vera (commit
    b341ad2) puso `background: transparent` en `#hero` para que el fondo
    generativo se viera a traves, sin panel opaco heredado de la regla
    generica de la fase A (`main[data-cae-track] > *` pinta `--cae-elev-1`
    a las otras cuatro escenas, que SI son ventanas de aplicacion). Esa regla
    no tenia ningun assert propio: un cambio futuro en el selector generico
    podia volver a tapar el 78% del fondo (la cifra medida por Vera) sin que
    nada lo cazara. Visto en rojo a mano contra el fallo real que dice cazar:
    comentando la excepcion de themes.css, esta asercion cae de OK a FALLO
    leyendo `rgb(...)` de `--cae-elev-1` en vez de transparente.
    """
    print("\n[escritorio_desnudo] el hero no hereda el panel opaco de las otras escenas")
    abrir(pg, base, "13:00")
    fondo_hero = pg.evaluate(
        "() => getComputedStyle(document.querySelector('#hero')).backgroundColor"
    )
    # Un `background: transparent` se reporta como `rgba(0, 0, 0, 0)` en
    # getComputedStyle (Chromium) -- comprobamos por alpha 0, no por el
    # string exacto, para no depender del formato que use el motor.
    alpha = pg.evaluate(
        "(v) => { const m = v.match(/rgba?\\(([^)]+)\\)/);"
        " if (!m) return 1;"
        " const partes = m[1].split(',').map((x) => parseFloat(x));"
        " return partes.length === 4 ? partes[3] : 1; }",
        fondo_hero,
    )
    assert_que(
        alpha == 0,
        f"#hero no pinta background opaco heredado de la fase A ({fondo_hero!r})",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    ap.add_argument("--solo", default="", help="familias separadas por coma (p. ej. optica,nombre)")
    args = ap.parse_args()

    with sync_playwright() as p:
        nav = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--use-gl=swiftshader"])
        pg = nav.new_page(viewport=VENTANA)
        errores: list[str] = []
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)

        familias = {
            "optica": optica,
            "escritorio_desnudo": escritorio_desnudo,
            "fondo": fondo,
            "nombre": nombre,
            "entrada": entrada,
            "roce": roce,
        }
        elegidas = [x for x in args.solo.split(",") if x] or list(familias)
        for clave in elegidas:
            familias[clave](pg, args.base)

        print("\n[consola] la pagina no tira errores")
        assert_que(not errores, f"cero errores de consola ({errores[:2]})")
        nav.close()

    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print("  - " + f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
