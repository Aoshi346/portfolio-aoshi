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
import sys

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
    print("\n[optica] el titular declara sus ejes y el shell conserva los suyos")
    abrir(pg, base, "13:00")
    ejes = pg.evaluate(
        "() => {"
        " const cs = getComputedStyle(document.documentElement);"
        " const tit = document.querySelector('#hero .cae-tit .cae-ln');"
        " return {"
        "  token: cs.getPropertyValue('--cae-display-axes-cartel').trim(),"
        "  marcaToken: cs.getPropertyValue('--cae-display-axes').trim(),"
        "  titular: tit ? getComputedStyle(tit).fontVariationSettings : ''"
        " }; }"
    )
    assert_que("144" in ejes["token"], f"el token --cae-display-axes-cartel existe y trae opsz 144 ({ejes['token']!r})")
    assert_que('"opsz" 9' in ejes["marcaToken"], f"el token --cae-display-axes del shell sigue en opsz 9 ({ejes['marcaToken']!r})")
    assert_que('"opsz" 144' in ejes["titular"], f"el titular usa opsz 144 ({ejes['titular']!r})")


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


def titular(pg, base: str) -> None:
    print("\n[titular] tres lineas a la misma medida, y el bloque cabe")
    abrir(pg, base, "13:00")
    m = pg.evaluate(
        "() => {"
        " const lns = Array.from(document.querySelectorAll('#hero .cae-tit .cae-ln'));"
        " if (lns.length === 0) return null;"
        " const anchos = lns.map((l) => {"
        "   const r = document.createRange(); r.selectNodeContents(l);"
        "   return r.getBoundingClientRect().width; });"
        " const tam = lns.map((l) => parseFloat(getComputedStyle(l).fontSize));"
        " const head = document.querySelector('#hero .cae-head');"
        " const desk = document.querySelector('#hero');"
        " const dr = desk.getBoundingClientRect();"
        " const libre = dr.top + dr.height - 84 - head.getBoundingClientRect().bottom;"
        " const texto = lns.map((l) => l.textContent ?? '').join(' ');"
        " return { n: lns.length, anchos, tam, libre, texto }; }"
    )
    assert_que(m is not None and m["n"] == 3, "el titular tiene tres lineas")
    if not m:
        return

    # Revision final (Importante 3): el corte manual en `CORTE` (hero.ts) no
    # sale de partir `identity.headline` por espacios -- nada ataba las dos
    # cadenas, asi que podian divergir en silencio si el headline cambiaba en
    # content.ts. El literal de abajo DEBE coincidir con `identity.headline`
    # de `src/data/content.ts`; si ese headline cambia, este assert tiene que
    # cambiar en el mismo commit (o el titular quedaria desactualizado).
    HEADLINE_CONTENT_TS = "Construyo sistemas que aguantan producción, no demos."
    assert_que(
        m["texto"] == HEADLINE_CONTENT_TS,
        f"las tres lineas juntas reproducen identity.headline literal ({m['texto']!r})",
    )

    # Medido con Range, NO con la caja del span: los .ln son de bloque y su
    # getBoundingClientRect devuelve el ancho del CONTENEDOR. Con esa medida las
    # tres lineas salian del mismo tamano y el bloque solo PARECIA justificado.
    ancho = max(m["anchos"]) - min(m["anchos"])
    assert_que(ancho <= 4.0, f"las tres lineas miden lo mismo: {ancho:.1f} px de diferencia (tope 4)")

    # Si los tres tamanos de fuente coinciden, la medida esta mal hecha aunque
    # los anchos cuadren: es exactamente el sintoma del fallo de arriba.
    distintos = len({round(t) for t in m["tam"]}) == 3
    assert_que(distintos, f"los tres tamanos de fuente son distintos entre si ({m['tam']})")

    assert_que(m["libre"] >= -1, f"aire bajo el pie {m['libre']:.0f} px (no pisa el dock)")


def firma_y_cifras(pg, base: str) -> None:
    print("\n[firma] literal de content.ts y cifras al canto derecho")
    abrir(pg, base, "13:00")
    m = pg.evaluate(
        "() => {"
        " const q = (s) => document.querySelector(s);"
        " const col = q('#hero .cae-statcol');"
        " const head = q('#hero .cae-head');"
        " return {"
        "  firma: q('#hero .cae-firma')?.textContent ?? '',"
        "  meta: q('#hero .cae-meta')?.textContent ?? '',"
        "  nowrap: q('#hero .cae-firma') ? getComputedStyle(q('#hero .cae-firma')).whiteSpace : '',"
        "  cifras: Array.from(document.querySelectorAll('#hero .cae-statcol > div'))"
        "    .map((d) => d.textContent.trim()),"
        "  colDer: col ? col.getBoundingClientRect().right : 0,"
        "  headDer: head ? head.getBoundingClientRect().right : 0"
        " }; }"
    )
    assert_que(m["firma"] == "Aoshi Blanco Sanz", f"la firma es identity.name literal ({m['firma']!r})")
    assert_que(
        m["meta"] == "Caracas. Full stack. Desde 2021.",
        f"la meta es identity.subheadline literal, con sus puntos ({m['meta']!r})",
    )
    # Si la firma parte en dos lineas, el aterrizaje de la tarea 6 no cuadra.
    assert_que(m["nowrap"] == "nowrap", f"la firma no parte de linea ({m['nowrap']!r})")
    assert_que(len(m["cifras"]) == 4, f"hay cuatro cifras ({len(m['cifras'])})")
    assert_que(
        abs(m["colDer"] - m["headDer"]) <= 2,
        f"la columna de cifras pega al canto derecho ({m['colDer']:.0f} vs {m['headDer']:.0f})",
    )


def widget(pg, base: str) -> None:
    print("\n[widget] todo lo que pinta existe en content.ts")
    abrir(pg, base, "13:00")
    texto = pg.evaluate(
        "() => document.querySelector('#hero .cae-widget')?.textContent ?? ''"
    )
    esperado = [
        "Disponible para proyectos",   # identity.availability
        "Freelancer",                  # identity.now
        "Caracas, Venezuela",          # identity.location
        "2021",                        # identity.since
        "Ingeniería de Sistemas",      # education[0].degree
        "Telefónica Venezuela",        # experience[0].organization
        "Ago 2025 — May 2026",         # experience[0].period
        # El semestre no es un campo propio: se extrae del parentesis de
        # education[0].period ("2021 — presente (10.º semestre)"), nunca un
        # literal inventado a mano. Ver hero.ts.
        "10.º semestre",
    ]
    for e in esperado:
        assert_que(e in texto, f"el widget dice {e!r}, literal de content.ts")
    # El fallo real que hubo: un dato derivado que no existe en ninguna parte.
    assert_que("Repositorios públicos" not in texto, "el widget no inventa datos derivados")


def entrada(pg, base: str) -> None:
    print("\n[entrada] el trazo existe y el movimiento reducido lo salta")
    abrir(pg, base, "13:00")
    n = pg.evaluate("() => document.querySelectorAll('#hero .cae-trazo path').length")
    assert_que(n == 15, f"el trazo tiene los 15 glifos de la firma ({n})")

    # Con movimiento reducido: sin terminal, sin trazo y todo montado.
    ctx = pg.context.browser.new_context(viewport=VENTANA, reduced_motion="reduce")
    pr = ctx.new_page()
    abrir(pr, base, "13:00")
    est = pr.evaluate(
        "() => {"
        " const t = document.querySelector('#hero .cae-term');"
        " const f = document.querySelector('#hero .cae-firma');"
        " return { term: t ? getComputedStyle(t).display : 'none',"
        "          firma: f ? parseFloat(getComputedStyle(f).opacity) : 0 }; }"
    )
    assert_que(est["term"] == "none", f"con movimiento reducido no hay terminal ({est['term']!r})")
    assert_que(est["firma"] >= 0.99, f"con movimiento reducido la firma esta puesta ({est['firma']})")
    ctx.close()


def roce(pg, base: str) -> None:
    print("\n[roce] el fondo se aparta al pasar el raton")
    abrir(pg, base, "13:00")
    antes = pg.evaluate("() => getComputedStyle(document.querySelector('canvas')).transform")
    pg.hover("#hero .cae-widget")
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
    args = ap.parse_args()

    with sync_playwright() as p:
        nav = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        pg = nav.new_page(viewport=VENTANA)
        errores: list[str] = []
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)

        optica(pg, args.base)
        escritorio_desnudo(pg, args.base)
        fondo(pg, args.base)
        titular(pg, args.base)
        firma_y_cifras(pg, args.base)
        widget(pg, args.base)
        entrada(pg, args.base)
        roce(pg, args.base)

        print("\n[consola] la pagina no tira errores")
        assert_que(not errores, f"cero errores de consola ({errores[:2]})")
        nav.close()

    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print("  - " + f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
