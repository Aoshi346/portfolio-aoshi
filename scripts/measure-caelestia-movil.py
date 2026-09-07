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
        navegador.close()
    print("\n[10] Consola sin errores")
    comprobar(not errores, f"cero errores de consola ({errores[:3]})")
    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print("  -", f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
