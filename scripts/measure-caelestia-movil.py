#!/usr/bin/env python3
"""Caelestia B6: el escritorio en el telefono (spec 2026-09-07-caelestia-movil).

Diez familias, cada una vista en rojo contra su sabotaje antes de aceptarse:
  1. la ley: el documento no se desplaza; cada workspace responde a un scroll
     interior; al cambiar de escena el desplazamiento vuelve a cero
  2. sin desbordamiento horizontal en las cinco escenas
  3. Titulo silencioso (Task 2)
  4. Obra: carrusel, la centrada es la elegida (Task 4)
  5. Stack: tocar elige, 23 dentro, rotulos pintados (Task 5)
  6. entradas cortas, ancladas a estado (Tasks 2-5)
  7. contraste de los pares nuevos (Task 6)
  8. tableta: 1-3 a 768x1024 (Task 6)
  9. escritorio intacto: los arneses de escritorio se corren aparte (Task 6)
 10. consola sin errores

Se lanza contra el build de produccion servido (nunca `npm run dev`):
  python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4213
"""
from __future__ import annotations

import argparse
import sys

from playwright.sync_api import sync_playwright

FALLOS: list[str] = []

ESCENAS = ["hero", "quien-es", "obra", "creditos", "contacto"]
# Obra no lleva data-scene (es div#obra.obra-rail): se localiza por id.
SELECTOR = {
    "hero": '[data-scene="hero"]',
    "quien-es": '[data-scene="about"]',
    "obra": "#obra",
    "creditos": '[data-scene="credits"]',
    "contacto": '[data-scene="contacto"]',
}
DISPOSITIVOS = {
    "movil": {"width": 390, "height": 844},
    "tableta": {"width": 768, "height": 1024},
}


def comprobar(condicion: bool, etiqueta: str) -> None:
    print(("  OK   " if condicion else "  FALLO") + f"  {etiqueta}")
    if not condicion:
        FALLOS.append(etiqueta)


def abrir(navegador, base: str, *, dispositivo: str = "movil", reduced_motion=None):
    kwargs = {
        "viewport": DISPOSITIVOS[dispositivo],
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
    }
    if reduced_motion:
        kwargs["reduced_motion"] = reduced_motion
    ctx = navegador.new_context(**kwargs)
    errores: list[str] = []
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errores.append(str(e)))
    pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
    pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    # Desviacion del plan (instrumento, no producto): 3000ms fijos era una
    # carrera contra el montaje real de la coreografia. Medido en esta
    # sandbox (swiftshader): `data-cae-shell="workspaces"` tarda ~5000ms en
    # aparecer (import() diferido de gsap + ScrollTrigger + la propia
    # coreografia), asi que a los 3000ms el documento todavia es la pagina
    # apilada sin montar -- exactamente la trampa "el cronometro miente en
    # esta sandbox" que ya documenta CLAUDE.md para B5. Se espera al hito real
    # en vez de a un numero de milisegundos, con una espera fija de reserva
    # solo si el montaje no llega (nunca debe fallar el harness por esto).
    try:
        pg.wait_for_function(
            "document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000
        )
    except Exception:
        pg.wait_for_timeout(3000)
    pg.wait_for_timeout(300)
    return ctx, pg, errores


def ir_a(pg, id_escena: str, espera_ms: int = 1400) -> None:
    pg.click(f'[data-cae-ws="{id_escena}"]')
    pg.wait_for_timeout(espera_ms)


def workspace_activo(pg) -> dict:
    return pg.evaluate("""() => {
        const ws = [...document.querySelectorAll('main[data-cae-track] > *')].find(e => !e.inert);
        if (!ws) return null;
        return { id: ws.id, scrollWidth: ws.scrollWidth, clientWidth: ws.clientWidth,
                 scrollHeight: ws.scrollHeight, clientHeight: ws.clientHeight, scrollTop: ws.scrollTop };
    }""")


def gate_ley(navegador, base: str, dispositivo: str = "movil") -> list[str]:
    print(f"\n[1] La ley ({dispositivo}): el documento no se desplaza; el workspace si, y vuelve a cero")
    ctx, pg, err = abrir(navegador, base, dispositivo=dispositivo)
    doc = pg.evaluate("""() => { window.scrollTo(0, 400); return { y: window.scrollY,
        sh: document.documentElement.scrollHeight, ch: document.documentElement.clientHeight }; }""")
    comprobar(doc["y"] == 0 and doc["sh"] <= doc["ch"] + 1,
              f"el documento no se desplaza (scrollY={doc['y']}, {doc['sh']}/{doc['ch']})")
    for id_escena in ESCENAS:
        ir_a(pg, id_escena)
        antes = workspace_activo(pg)
        comprobar(antes is not None, f"{id_escena}: hay un workspace activo")
        # Responde a un scroll programatico (no scrollHeight===clientHeight, que
        # miente con transform+overflow:clip, trampa de B5). Si el contenido
        # cabe entero (Titulo silencioso), scrollTop se queda en 0 y eso es OK.
        r = pg.evaluate("""() => {
            const ws = [...document.querySelectorAll('main[data-cae-track] > *')].find(e => !e.inert);
            ws.scrollTop = 200; const st = ws.scrollTop; return { st, cabe: ws.scrollHeight <= ws.clientHeight + 1 };
        }""")
        comprobar(r["cabe"] or r["st"] > 0,
                  f"{id_escena}: el workspace responde a un scroll interior (scrollTop={r['st']}, cabe={r['cabe']})")
    # Volver a cero al cambiar: dejar Stack desplazado, ir a Titulo y volver.
    ir_a(pg, "creditos")
    pg.evaluate("""() => { const ws = [...document.querySelectorAll('main[data-cae-track] > *')].find(e => !e.inert); ws.scrollTop = 200; }""")
    ir_a(pg, "hero")
    ir_a(pg, "creditos")
    despues = workspace_activo(pg)
    comprobar(despues is not None and despues["scrollTop"] == 0,
              f"al volver a Stack el desplazamiento interior esta a cero ({despues and despues['scrollTop']})")
    ctx.close()
    return err


def gate_desbordamiento(navegador, base: str, dispositivo: str = "movil") -> list[str]:
    print(f"\n[2] Sin desbordamiento horizontal ({dispositivo})")
    ctx, pg, err = abrir(navegador, base, dispositivo=dispositivo)
    for id_escena in ESCENAS:
        ir_a(pg, id_escena)
        ws = workspace_activo(pg)
        comprobar(ws is not None and ws["scrollWidth"] <= ws["clientWidth"] + 1,
                  f"{id_escena}: scrollWidth {ws and ws['scrollWidth']} <= clientWidth {ws and ws['clientWidth']}")
    ctx.close()
    return err


def literal_content(campo: str) -> str:
    """Lee un literal de src/data/content.ts sin evaluarlo (regex sobre el fuente)."""
    import pathlib
    import re

    fuente = (pathlib.Path(__file__).resolve().parent.parent / "src/data/content.ts").read_text(encoding="utf-8")
    m = re.search(rf'^\s*{re.escape(campo)}:\s*"([^"]+)"', fuente, re.MULTILINE)
    if not m:
        raise SystemExit(f"content.ts no tiene el literal {campo}")
    return m.group(1)


def gate_titulo(navegador, base: str) -> list[str]:
    print("\n[3] Titulo silencioso: sin tarjeta ni columna, prosa y cifras literales, cabe entero")
    ctx, pg, err = abrir(navegador, base)
    pintan = pg.evaluate("""() => {
        const p = sel => { const e = document.querySelector(sel); return e ? e.getClientRects().length : -1; };
        return { widget: p('#hero .cae-widget'), statcol: p('#hero .cae-statcol'), trazo: p('#hero .cae-trazo-stage'),
                 movil: p('#hero .cae-movil'), fig: !!document.querySelector('#hero .cae-wfig[style*="clip-path"]') };
    }""")
    comprobar(pintan["widget"] == 0, f"la tarjeta Ahora mismo no pinta (rects={pintan['widget']})")
    comprobar(pintan["statcol"] == 0, f"la columna de cifras no pinta (rects={pintan['statcol']})")
    comprobar(pintan["movil"] > 0, f"el bloque movil pinta (rects={pintan['movil']})")
    comprobar(not pintan["fig"], "la figura viva no se monta (sin clip-path inline en .cae-wfig)")
    texto = pg.evaluate("() => document.querySelector('#hero .cae-movil')?.textContent ?? ''")
    for campo in ("now", "location", "availability"):
        lit = literal_content(campo)
        comprobar(lit in texto, f"la prosa lleva el literal identity.{campo} («{lit}»)")
    cifras = pg.evaluate("() => [...document.querySelectorAll('#hero .cae-mv-cifra b')].map(b => b.textContent.trim())")
    comprobar(cifras == ["2021", "10", "5", "1"], f"las cuatro cifras son las de stats ({cifras})")
    tam = pg.evaluate("""() => { const ln = [...document.querySelectorAll('#hero .cae-ln')].map(e => parseFloat(getComputedStyle(e).fontSize));
        const ws = document.querySelector('[data-scene="hero"]'); return { ln, cabe: ws.scrollHeight <= ws.clientHeight + 1 }; }""")
    comprobar(len(tam["ln"]) == 3 and tam["ln"][2] > tam["ln"][0] and tam["ln"][2] > tam["ln"][1],
              f"«no demos.» es la linea mas grande ({tam['ln']})")
    comprobar(tam["cabe"], "Titulo cabe entero sin desplazamiento")
    ctx.close()
    return err


def gate_entradas(navegador, base: str) -> list[str]:
    """Anclado a estado: se lee el primer fotograma sincrono del gesto en la
    misma evaluate que dispara el cambio (tecnica de B5), y luego se espera
    al aterrizaje con tope. Con movimiento reducido nada corre."""
    print("\n[6] Entradas cortas: un gesto por escena, aterrizan; con reduce ninguna")
    ctx, pg, err = abrir(navegador, base)
    # Titulo: la terminal teclea whoami y NO hay trazo de firma.
    typed = pg.evaluate("() => document.querySelector('#hero .cae-term-typed')?.textContent ?? null")
    comprobar(typed is not None, "Titulo: la terminal existe")
    aterrizo = pg.evaluate("""() => new Promise(res => { const t0 = performance.now();
        const mira = () => { const f = document.querySelector('#hero .cae-firma');
          const ok = f && getComputedStyle(f).opacity === '1' && !document.documentElement.classList.contains('js-cae-entrada');
          if (ok || performance.now() - t0 > 6000) res({ ok, ms: Math.round(performance.now() - t0) }); else requestAnimationFrame(mira); };
        mira(); })""")
    comprobar(aterrizo["ok"], f"Titulo aterriza (firma visible, {aterrizo['ms']} ms de espera)")
    comprobar(pg.evaluate("() => document.querySelector('#hero .cae-trazo-stage').getClientRects().length === 0"),
              "Titulo: el trazo de la firma no pinta en movil")
    # Quien soy: el neofetch se teclea y la ficha aterriza; las filas no entran por capas.
    ir_a(pg, "quien-es", 200)
    primer = pg.evaluate("() => document.querySelector('[data-ficha-cmd]')?.textContent ?? null")
    comprobar(primer is not None and primer != "neofetch", f"Quien soy: la entrada arranca tecleando (primer fotograma «{primer}»)")
    fin = pg.evaluate("""() => new Promise(res => { const t0 = performance.now();
        const mira = () => { const c = document.querySelector('[data-ficha-cmd]'); const ok = c && c.textContent === 'neofetch';
          if (ok || performance.now() - t0 > 4000) res({ ok, ms: Math.round(performance.now() - t0) }); else requestAnimationFrame(mira); }; mira(); })""")
    comprobar(fin["ok"] and fin["ms"] < 2500, f"Quien soy: aterriza en menos de 2,5 s de sandbox ({fin['ms']} ms)")
    ctx.close()
    # Las tres siguientes se completan en las Tasks 3, 4 y 5 (una comprobacion por escena).
    # Reduce: nada corre.
    ctx, pg, err2 = abrir(navegador, base, reduced_motion="reduce")
    est = pg.evaluate("() => ({ typed: document.querySelector('#hero .cae-term-typed')?.textContent, entrada: document.documentElement.classList.contains('js-cae-entrada') })")
    comprobar(not est["entrada"], "reduce: Titulo aterriza directo (sin js-cae-entrada)")
    ctx.close()
    return err + err2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:4213")
    ap.add_argument("--solo", default="", help="familias a correr, p.ej. 1,2")
    args = ap.parse_args()
    solo = {int(x) for x in args.solo.split(",") if x.strip()}
    errores: list[str] = []
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        if not solo or 1 in solo:
            errores += gate_ley(navegador, args.base)
        if not solo or 2 in solo:
            errores += gate_desbordamiento(navegador, args.base)
        if not solo or 3 in solo:
            errores += gate_titulo(navegador, args.base)
        if not solo or 6 in solo:
            errores += gate_entradas(navegador, args.base)
        navegador.close()
    print("\n[10] Consola sin errores")
    comprobar(not errores, f"cero errores de consola ({errores[:3]})")
    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print("  -", f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
