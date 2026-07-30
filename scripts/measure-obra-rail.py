#!/usr/bin/env python3
"""Retrato numerico del ritmo del carril horizontal de obra (tema Vice).

No arregla nada: mide. Nacio del encargo "va bien, pero siento que el timing no
es perfecto", que sin numeros previos acaba en tanteo.

Que mide, y por que ese y no otro:

  M1  Retardo scroll -> carril. `scrub: 1` y Lenis (`duration: 1.15`) son DOS
      suavizados encadenados. Se mide el desfase entre donde deberia estar el
      carril para el `scrollY` actual y donde esta de verdad.
  M2  Desincronia entre la entrada de la cartela y el encuadre de su pieza.
      Las entradas son de TIEMPO (`toggleActions`, duracion fija) montadas
      sobre un recorrido que manda el usuario: pueden terminar mucho antes de
      que la pieza llegue.
  M3  Acento de llegada. Con `ease: "none"` la velocidad lateral es constante;
      se comprueba comparando la velocidad en el instante de encuadre contra la
      de transito.
  M4  Reparto del tiempo en pantalla por pieza. Cinco piezas, cuatro
      transiciones: los extremos pueden no recibir lo mismo que el centro.
  M5  Enganche y liberacion del pin.

Se muestrea DESDE DENTRO de la pagina por fotograma. No se usa
`page.screenshot()` para medir ritmo: bloquea el compositor y adelanta la
timeline (trampa ya pagada, ver rules/verification.md).

Uso:
    npm run build && npm run preview -- --port 4173
    python3 scripts/measure-obra-rail.py [--url URL] [--shader] [--json OUT]

Por defecto BLOQUEA el shader de fondo: con `--use-gl=swiftshader` el rAF va
lentisimo y contamina toda medida de ritmo. `--shader` lo deja pasar, para el
A/B que separa coste de render de coste de coreografia.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys

from playwright.sync_api import sync_playwright

VIEWPORT = {"width": 1440, "height": 900}
DEFAULT_URL = "http://localhost:4173/?theme=vice"

# Tres velocidades de rueda. El delta y la pausa son la ORDEN; la velocidad
# real se mide de los datos y se reporta, porque Lenis y el navegador no
# entregan exactamente lo que se les pide.
SPEEDS = [
    ("lenta", 40, 40),
    ("normal", 100, 30),
    ("flick", 300, 16),
]

# Margen antes y despues del pin, para capturar enganche y liberacion.
MARGIN = 600

SAMPLER = """
() => {
  window.__samples = [];
  window.__sampling = true;
  const track = document.querySelector('[data-obra-track]');
  const scenes = Array.from(document.querySelectorAll('[data-scene="obra"]'));
  const leads = scenes.map(s => s.querySelector('.lead'));
  const gals = scenes.map(s => s.querySelector('[data-gallery]'));
  const op = el => el ? parseFloat(getComputedStyle(el).opacity) : null;
  const tick = () => {
    if (!window.__sampling) return;
    const m = new DOMMatrixReadOnly(getComputedStyle(track).transform);
    window.__samples.push({
      t: performance.now(),
      y: window.scrollY,
      x: m.m41,
      lead: leads.map(op),
      gal: gals.map(op),
    });
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
"""

GEOMETRY = """
() => {
  const rail = document.querySelector('[data-obra-rail]');
  const track = document.querySelector('[data-obra-track]');
  const scenes = document.querySelectorAll('[data-scene="obra"]');
  // GSAP envuelve el nodo fijado en un .pin-spacer; el inicio del pin es el
  // tope absoluto de ese envoltorio, no el del carril.
  const spacer = rail.closest('.pin-spacer') || rail.parentElement;
  const r = spacer.getBoundingClientRect();
  return {
    railStart: r.top + window.scrollY,
    spacerHeight: r.height,
    scrollWidth: track.scrollWidth,
    sceneCount: scenes.length,
    innerWidth: window.innerWidth,
    docHeight: document.documentElement.scrollHeight,
  };
}
"""


def settle(page, target_y: float) -> None:
    """Mueve solo el delta real y espera a que `scrollY` deje de cambiar.

    Replica `_scroll_to_and_settle` de verify.py. NO resetear a 0 nunca: Lenis
    intercepta el wheel y lleva su propio target interno, asi que `scrollTo`
    mueve el scroll nativo pero deja a Lenis apuntando a la posicion anterior y
    el siguiente delta se suma a un target rancio.
    """
    current = page.evaluate("window.scrollY")
    remaining = target_y - current
    direction = 1 if remaining >= 0 else -1
    remaining = abs(remaining)
    while remaining > 1:
        step = min(120, remaining)
        page.mouse.wheel(0, direction * step)
        remaining -= step
        page.wait_for_timeout(12)

    last = None
    stable = 0
    for _ in range(120):
        page.wait_for_timeout(50)
        now = page.evaluate("window.scrollY")
        if last is not None and abs(now - last) < 0.5:
            stable += 1
            if stable >= 3:
                return
        else:
            stable = 0
        last = now


def run_pass(page, geo: dict, delta: int, pause_ms: int) -> list[dict]:
    """Un barrido a velocidad constante por todo el pin, mas margen."""
    start_y = max(geo["railStart"] - MARGIN, 0)
    end_y = geo["railStart"] + geo["spacerHeight"] + MARGIN

    settle(page, start_y)
    page.wait_for_timeout(400)

    page.evaluate(SAMPLER)
    page.wait_for_timeout(100)

    travelled = 0.0
    target = end_y - start_y
    while travelled < target:
        page.mouse.wheel(0, delta)
        travelled += delta
        page.wait_for_timeout(pause_ms)

    # Cola en silencio: aqui se mide cuanto tarda el carril en asentarse una
    # vez el dedo se levanta (M1).
    page.wait_for_timeout(2500)
    page.evaluate("() => { window.__sampling = false; }")
    return page.evaluate("() => window.__samples")


def measure_settle(page, geo: dict) -> dict:
    """M1 — cuanto tarda el carril en pararse cuando el dedo se levanta.

    Tiene que medirse A MITAD de carril. Al final del recorrido el tween esta
    topado en `-distance` y el carril ya esta quieto antes de soltar la rueda:
    medido asi daba 0ms, que no es que no haya retardo sino que no habia nada
    que medir.
    """
    mid = geo["railStart"] + geo["distance"] * 0.45
    settle(page, mid)
    page.wait_for_timeout(600)

    page.evaluate(SAMPLER)
    page.wait_for_timeout(80)

    # Rafaga corta y parada en seco.
    for _ in range(12):
        page.mouse.wheel(0, 120)
        page.wait_for_timeout(16)
    stop_marker = page.evaluate("() => performance.now()")

    page.wait_for_timeout(3000)
    page.evaluate("() => { window.__sampling = false; }")
    samples = page.evaluate("() => window.__samples")

    if len(samples) < 5:
        return {"error": "muestras insuficientes"}

    after = [s for s in samples if s["t"] >= stop_marker]
    if len(after) < 3:
        return {"error": "sin cola tras la parada"}

    final_x = after[-1]["x"]
    final_y = after[-1]["y"]
    x_at_stop = after[0]["x"]
    y_at_stop = after[0]["y"]

    settle_ms = 0.0
    for s in after:
        if abs(s["x"] - final_x) > 1.0:
            settle_ms = s["t"] - after[0]["t"]

    scroll_settle_ms = 0.0
    for s in after:
        if abs(s["y"] - final_y) > 1.0:
            scroll_settle_ms = s["t"] - after[0]["t"]

    return {
        "asentamiento_carril_ms": round(settle_ms, 1),
        "asentamiento_scroll_lenis_ms": round(scroll_settle_ms, 1),
        "deriva_lateral_tras_soltar_px": round(abs(final_x - x_at_stop), 1),
        "deriva_scroll_tras_soltar_px": round(abs(final_y - y_at_stop), 1),
    }


def analyse(samples: list[dict], geo: dict, label: str) -> dict:
    n = geo["sceneCount"]
    scene_w = geo["scrollWidth"] / n
    distance = max(geo["scrollWidth"] - geo["innerWidth"], 0)
    rail_start = geo["railStart"]

    if len(samples) < 10:
        return {"speed": label, "error": "muestras insuficientes"}

    t0 = samples[0]["t"]
    for s in samples:
        s["t"] -= t0

    # --- velocidad real de scroll durante el barrido (px/s)
    moving = [s for s in samples if s["t"] < samples[-1]["t"] - 2400]
    if len(moving) > 2:
        dt = (moving[-1]["t"] - moving[0]["t"]) / 1000.0
        dy = moving[-1]["y"] - moving[0]["y"]
        real_speed = dy / dt if dt > 0 else 0.0
    else:
        real_speed = 0.0

    # --- M1: desfase entre el carril real y el que tocaria para ese scrollY
    def ideal_x(y: float) -> float:
        p = (y - rail_start) / distance if distance else 0.0
        p = min(max(p, 0.0), 1.0)
        return -p * distance

    lags = [
        abs(s["x"] - ideal_x(s["y"]))
        for s in moving
        if rail_start < s["y"] < rail_start + distance
    ]
    lag_peak = max(lags) if lags else 0.0
    lag_med = statistics.median(lags) if lags else 0.0

    # --- M3/M4: por escena, instante de encuadre y permanencia
    #
    # Todo se acota a la ventana del pin. Fuera de ella el carril esta topado
    # (`x = 0` antes de engancharse, `x = -distance` despues de soltarse), asi
    # que las piezas 1 y 5 acumularian como "permanencia" el margen de
    # aproximacion y la cola en silencio del barrido: la primera version de
    # este script le daba a la pieza 5 casi 10s de los que 2,5 eran el propio
    # instrumento parado.
    pinned = [s for s in samples if rail_start <= s["y"] <= rail_start + distance]

    per_scene = []
    for i in range(n):
        framed_x = -i * scene_w
        # instante en que el carril cruza el encuadre de la pieza i
        cross = None
        for a, b in zip(samples, samples[1:]):
            lo, hi = sorted((a["x"], b["x"]))
            if lo <= framed_x <= hi:
                cross = b
                break

        # permanencia: fotogramas DENTRO del pin con la pieza a menos de un 20%
        # de viewport del encuadre exacto
        near = [s for s in pinned if abs(s["x"] - framed_x) < geo["innerWidth"] * 0.2]
        dwell = (near[-1]["t"] - near[0]["t"]) if len(near) > 1 else 0.0

        # velocidad lateral en el encuadre vs. media de transito
        v_framed = None
        if cross:
            idx = samples.index(cross)
            lo = max(idx - 3, 0)
            hi = min(idx + 3, len(samples) - 1)
            dt = (samples[hi]["t"] - samples[lo]["t"]) / 1000.0
            if dt > 0:
                v_framed = abs(samples[hi]["x"] - samples[lo]["x"]) / dt

        # --- M2: cuando termina de montarse la cartela (lead opaco y estable)
        entry_done = None
        for s in samples:
            v = s["lead"][i]
            if v is not None and v >= 0.99:
                entry_done = s["t"]
                break

        gap_ms = None
        gap_px = None
        # La pieza 1 esta encuadrada en el instante mismo en que el pin
        # engancha (`x = 0`), asi que su entrada se dispara antes de que empiece
        # el muestreo y su "adelanto" no mide nada. Se reporta como no aplicable
        # en vez de como un numero que invita a leerse.
        if entry_done is not None and cross is not None and i > 0:
            gap_ms = cross["t"] - entry_done
            gap_px = abs(gap_ms / 1000.0 * real_speed)

        per_scene.append(
            {
                "pieza": i + 1,
                "encuadre_t_ms": round(cross["t"], 1) if cross else None,
                "entrada_lista_t_ms": round(entry_done, 1) if entry_done is not None else None,
                "adelanto_entrada_ms": round(gap_ms, 1) if gap_ms is not None else None,
                "adelanto_entrada_px": round(gap_px, 1) if gap_px is not None else None,
                "permanencia_ms": round(dwell, 1),
                "v_lateral_encuadre_px_s": round(v_framed, 1) if v_framed else None,
                "nota": "encuadrada al enganchar el pin: sin llegada que acentuar" if i == 0 else None,
            }
        )

    transit_v = [p["v_lateral_encuadre_px_s"] for p in per_scene if p["v_lateral_encuadre_px_s"]]
    v_mean = statistics.mean(transit_v) if transit_v else 0.0

    return {
        "speed": label,
        "velocidad_scroll_real_px_s": round(real_speed, 1),
        "muestras": len(samples),
        "fps_medio": round(len(samples) / (samples[-1]["t"] / 1000.0), 1) if samples[-1]["t"] else None,
        "M1_desfase_lateral_pico_px": round(lag_peak, 1),
        "M1_desfase_lateral_mediana_px": round(lag_med, 1),
        "M3_v_lateral_media_px_s": round(v_mean, 1),
        "M3_dispersion_v_encuadre_px_s": round(statistics.pstdev(transit_v), 1) if len(transit_v) > 1 else 0.0,
        "por_pieza": per_scene,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--shader", action="store_true", help="deja pasar el shader de fondo")
    ap.add_argument("--json", help="volcar el informe crudo a un fichero")
    args = ap.parse_args()

    report: dict = {"url": args.url, "shader": args.shader}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--use-gl=swiftshader"],
        )
        page = browser.new_page(viewport=VIEWPORT)
        if not args.shader:
            # A/B barato: sin el shader el rAF respira y el ritmo medido es el
            # de la coreografia, no el del software rasterizer.
            page.route("**/viceHaze*", lambda r: r.abort())

        page.goto(args.url, wait_until="domcontentloaded", timeout=30000)
        # Leader de apertura (~1,6s) + GSAP + refresh de ScrollTrigger.
        page.wait_for_timeout(9000)

        geo = page.evaluate(GEOMETRY)
        geo["distance"] = max(geo["scrollWidth"] - geo["innerWidth"], 0)
        report["geometria"] = geo
        print("Geometria medida:")
        for k, v in geo.items():
            print(f"  {k}: {v}")
        print()

        report["pasadas"] = []
        for label, delta, pause in SPEEDS:
            print(f"Barrido '{label}' (delta {delta}px cada {pause}ms)...")
            samples = run_pass(page, geo, delta, pause)
            res = analyse(samples, geo, label)
            report["pasadas"].append(res)
            print(f"  velocidad real: {res.get('velocidad_scroll_real_px_s')} px/s"
                  f"  fps: {res.get('fps_medio')}")
            print(f"  M1 desfase pico: {res.get('M1_desfase_lateral_pico_px')} px"
                  f"  mediana: {res.get('M1_desfase_lateral_mediana_px')} px")
            for ps in res.get("por_pieza", []):
                print(f"    pieza {ps['pieza']}: entrada lista {ps['entrada_lista_t_ms']} ms, "
                      f"encuadre {ps['encuadre_t_ms']} ms, "
                      f"adelanto {ps['adelanto_entrada_ms']} ms / {ps['adelanto_entrada_px']} px, "
                      f"permanencia {ps['permanencia_ms']} ms")
            print()

        print("Parada en seco a mitad de carril (M1)...")
        report["asentamiento"] = measure_settle(page, geo)
        for k, v in report["asentamiento"].items():
            print(f"  {k}: {v}")
        print()

        browser.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"Informe crudo en {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
