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
    """Carga Caelestia. `hora` en HH:MM congela el reloj del visitante."""
    if hora is not None:
        hh, mm = (int(x) for x in hora.split(":"))
        pg.add_init_script(
            "(() => { const R = Date;"
            f" const fijo = new R(2026, 7, 26, {hh}, {mm}, 0);"
            " class F extends R {"
            "   constructor(...a){ return a.length ? new R(...a) : new R(fijo); }"
            "   static now(){ return fijo.getTime(); } }"
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
        " return { n: lns.length, anchos, tam, libre }; }"
    )
    assert_que(m is not None and m["n"] == 3, "el titular tiene tres lineas")
    if not m:
        return

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
        fondo(pg, args.base)
        titular(pg, args.base)
        firma_y_cifras(pg, args.base)

        print("\n[consola] la pagina no tira errores")
        assert_que(not errores, f"cero errores de consola ({errores[:2]})")
        nav.close()

    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print("  - " + f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
