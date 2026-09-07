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
 8b. Obra/Stack en banda media, 1024x768 y 1180x820 (Tasks 4b/5b)
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


def gate_titulo(navegador, base: str, dispositivo: str = "movil") -> list[str]:
    print(f"\n[3] Titulo silencioso ({dispositivo}): sin tarjeta ni columna, prosa y cifras literales, cabe entero")
    ctx, pg, err = abrir(navegador, base, dispositivo=dispositivo)
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


def gate_obra(navegador, base: str) -> list[str]:
    print("\n[4] Obra: carrusel con iman, la centrada es la elegida, el cajon la sigue")
    ctx, pg, err = abrir(navegador, base)
    ir_a(pg, "obra", 2600)
    n = pg.evaluate("() => document.querySelectorAll('#obra .cae-obra-card').length")
    comprobar(n == 5, f"hay cinco tarjetas ({n})")
    for i in range(5):
        r = pg.evaluate(
            """(i) => new Promise(res => {
            const cards = [...document.querySelectorAll('#obra .cae-obra-card')]; const c = cards[i];
            const pista = c.parentElement;
            // Desviacion de instrumento (no de plan): `c.offsetLeft` cuenta
            // desde el ancestro POSICIONADO mas cercano, que aqui es el
            // carril de workspaces, no `pista` -- incluye el desplazamiento
            // de Obra como tercer panel y da un `x` disparatado (814px de
            // mas, medido). Se mide la posicion real con
            // `getBoundingClientRect()`, restando el rectangulo de `pista`.
            const cr0 = c.getBoundingClientRect(), pr0 = pista.getBoundingClientRect();
            const relLeft = cr0.left - pr0.left + pista.scrollLeft;
            const x = relLeft - (pista.clientWidth - c.offsetWidth) / 2;
            pista.scrollTo({ left: x, behavior: 'instant' });
            pista.dispatchEvent(new Event('scrollend'));
            setTimeout(() => { const pr = pista.getBoundingClientRect(), cr = c.getBoundingClientRect();
              const centrada = Math.abs((cr.left + cr.right) / 2 - (pr.left + pr.right) / 2) < 24;
              const sel = c.classList.contains('is-sel');
              const titulo = document.querySelector('#obra .cae-obra-drawer-title h3')?.textContent?.trim();
              res({ centrada, sel, titulo, esperado: c.querySelector('.cae-obra-caption')?.textContent?.trim() }); }, 600); })""",
            i,
        )
        comprobar(r["centrada"], f"tarjeta {i + 1} llega al centro con scrollTo")
        comprobar(r["sel"], f"tarjeta {i + 1} centrada es la elegida")
        comprobar(
            bool(r["titulo"]) and bool(r["esperado"]) and r["esperado"].startswith(r["titulo"][:6]),
            f"el cajon muestra la tarjeta {i + 1} («{r['titulo']}»)",
        )
    ctx.close()
    return err


def gate_obra_banda_media(navegador, base: str) -> list[str]:
    """Familia 8b, banda media (901-1365): tableta apaisada real, sin touch
    (a diferencia de `abrir`, que fuerza is_mobile/has_touch para la banda
    compacta). Anchos del spec: 1024x768 y 1180x820. Ancla la aseveracion al
    scrollWidth/clientWidth del workspace, no a un pixel fijo, y comprueba
    ademas que las cinco tarjetas siguen dentro de la caja."""
    print("\n[8b] Obra en banda media (901-1365): sin desbordamiento horizontal, las cinco caben")
    resultado_final: list[str] = []
    for ancho, alto in ((1024, 768), (1180, 820)):
        print(f"  -- {ancho}x{alto} --")
        ctx = navegador.new_context(viewport={"width": ancho, "height": alto})
        errores: list[str] = []
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        try:
            pg.wait_for_function(
                "document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000
            )
        except Exception:
            pg.wait_for_timeout(3000)
        pg.wait_for_timeout(300)
        ir_a(pg, "obra", 1600)
        ws = workspace_activo(pg)
        comprobar(
            ws is not None and ws["scrollWidth"] <= ws["clientWidth"] + 1,
            f"{ancho}x{alto}: Obra no desborda (scrollWidth={ws and ws['scrollWidth']} / clientWidth={ws and ws['clientWidth']})",
        )
        cajas = pg.evaluate(
            """() => { const pista = document.querySelector('#obra .cae-obra-row');
                const pr = pista.getBoundingClientRect();
                return [...document.querySelectorAll('#obra .cae-obra-card')].map(c => {
                    const cr = c.getBoundingClientRect();
                    return cr.left >= pr.left - 1 && cr.right <= pr.right + 1;
                }); }"""
        )
        comprobar(
            len(cajas) == 5 and all(cajas),
            f"{ancho}x{alto}: las cinco tarjetas caben dentro de la fila ({cajas})",
        )
        ctx.close()
        resultado_final += errores
    return resultado_final


def gate_stack(navegador, base: str) -> list[str]:
    print("\n[5] Stack: tocar elige, las 23 dentro de la caja, los cuatro rotulos pintan")
    ctx, pg, err = abrir(navegador, base)
    ir_a(pg, "creditos", 2600)
    caja = pg.evaluate("""() => { const ws = document.querySelector('[data-scene="credits"]'); const w = ws.getBoundingClientRect();
        const piezas = [...ws.querySelectorAll('.cae-cred-pieza')].map(b => { const r = b.getBoundingClientRect();
          return r.left >= w.left - 1 && r.right <= w.right + 1; });
        const rotulos = [...ws.querySelectorAll('.cae-cred-rot')].map(r => r.getClientRects().length > 0 && getComputedStyle(r).opacity !== '0');
        return { n: piezas.length, dentro: piezas.filter(Boolean).length, rotulos }; }""")
    comprobar(caja["n"] == 23 and caja["dentro"] == 23, f"las 23 piezas dentro del ancho de la caja ({caja['dentro']}/{caja['n']})")
    comprobar(len(caja["rotulos"]) == 4 and all(caja["rotulos"]), f"los cuatro rotulos pintan ({caja['rotulos']})")
    # Tocar elige: tap real sobre la sexta pieza (ni hover ni MouseEvent sintetico).
    objetivo = pg.evaluate("() => document.querySelectorAll('.cae-cred-pieza')[5].dataset.pieza")
    pg.evaluate("() => document.querySelectorAll('.cae-cred-pieza')[5].scrollIntoView({ block: 'center' })")
    pg.wait_for_timeout(300)
    pg.tap(".cae-cred-pieza >> nth=5")
    pg.wait_for_timeout(500)
    est = pg.evaluate("""() => { const b = document.querySelectorAll('.cae-cred-pieza')[5];
        return { pressed: b.getAttribute('aria-pressed'), nombre: document.querySelector('.cae-cred-nombre')?.textContent?.trim() }; }""")
    comprobar(est["pressed"] == "true" and est["nombre"] == objetivo, f"tocar elige («{objetivo}» -> ficha «{est['nombre']}», aria-pressed={est['pressed']})")
    # is-tocando no se queda pegado tras el tap (sin mouseleave en tactil).
    pg.wait_for_timeout(300)
    pegado = pg.evaluate("() => document.querySelector('.cae-cred-grid')?.classList.contains('is-tocando')")
    comprobar(not pegado, f"is-tocando no se queda pegado tras el tap ({pegado})")
    ctx.close()
    return err


def gate_stack_banda_media(navegador, base: str) -> list[str]:
    """Familia 8b (Stack): tableta apaisada real, sin touch. Anchos del spec:
    1024x768 y 1180x820. Las 23 piezas dentro de la caja de la escena y todas
    del mismo lado (ley de B4: el tamano no codifica nada) -- se mide el
    `getBoundingClientRect().width` de las 23, no de tres."""
    print("\n[8b] Stack en banda media (901-1365): sin desbordamiento horizontal, las 23 caben y miden igual")
    resultado_final: list[str] = []
    for ancho, alto in ((1024, 768), (1180, 820)):
        print(f"  -- {ancho}x{alto} --")
        ctx = navegador.new_context(viewport={"width": ancho, "height": alto})
        errores: list[str] = []
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        try:
            pg.wait_for_function(
                "document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000
            )
        except Exception:
            pg.wait_for_timeout(3000)
        pg.wait_for_timeout(300)
        ir_a(pg, "creditos", 1600)
        ws = workspace_activo(pg)
        comprobar(
            ws is not None and ws["scrollWidth"] <= ws["clientWidth"] + 1,
            f"{ancho}x{alto}: Stack no desborda (scrollWidth={ws and ws['scrollWidth']} / clientWidth={ws and ws['clientWidth']})",
        )
        datos = pg.evaluate("""() => { const ws = document.querySelector('[data-scene="credits"]'); const w = ws.getBoundingClientRect();
            const piezas = [...ws.querySelectorAll('.cae-cred-pieza')].map(b => { const r = b.getBoundingClientRect();
              return { dentro: r.left >= w.left - 1 && r.right <= w.right + 1, ancho: Math.round(r.width) }; });
            return { n: piezas.length, dentro: piezas.filter(p => p.dentro).length, anchos: piezas.map(p => p.ancho) }; }""")
        comprobar(
            datos["n"] == 23 and datos["dentro"] == 23,
            f"{ancho}x{alto}: las 23 piezas dentro de la caja ({datos['dentro']}/{datos['n']})",
        )
        anchos_unicos = sorted(set(datos["anchos"]))
        comprobar(
            len(anchos_unicos) == 1,
            f"{ancho}x{alto}: las 23 piezas miden todas lo mismo ({anchos_unicos})",
        )
        ctx.close()
        resultado_final += errores
    return resultado_final


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
    # Quien soy: el neofetch se TECLEA (no aparece de golpe) y la ficha
    # aterriza. Anclado a ESTADO con un MutationObserver puesto ANTES del
    # cambio, no a un cronometro: la version corta de movil dura 0,86 s
    # declarados y un muestreo a los 200 ms ya la encuentra terminada, asi
    # que un gate con reloj daba rojo contra una entrada correcta. Lo que
    # define «tecleado» es que el nodo pase por valores intermedios, y eso
    # el observador lo ve pase lo que pase con los fotogramas.
    pg.evaluate("""() => {
        window.__pasos = [];
        const nodo = document.querySelector('[data-ficha-cmd]');
        if (!nodo) return;
        window.__obs = new MutationObserver(() => window.__pasos.push(nodo.textContent));
        window.__obs.observe(nodo, { childList: true, characterData: true, subtree: true });
    }""")
    ir_a(pg, "quien-es", 2000)
    pasos = pg.evaluate("() => { window.__obs && window.__obs.disconnect(); return window.__pasos || []; }")
    intermedios = [p for p in pasos if p and p != "neofetch"]
    comprobar(len(intermedios) >= 2,
              f"Quien soy: la entrada TECLEA el comando, no lo pone de golpe "
              f"({len(intermedios)} pasos intermedios, p.ej. {intermedios[:3]})")
    fin = pg.evaluate("""() => new Promise(res => { const t0 = performance.now();
        const mira = () => { const c = document.querySelector('[data-ficha-cmd]'); const ok = c && c.textContent === 'neofetch';
          if (ok || performance.now() - t0 > 4000) res({ ok, ms: Math.round(performance.now() - t0) }); else requestAnimationFrame(mira); }; mira(); })""")
    comprobar(fin["ok"] and fin["ms"] < 2500, f"Quien soy: aterriza en menos de 2,5 s de sandbox ({fin['ms']} ms)")
    # Obra: la caida, solo de la tarjeta visible y sus vecinas; el primer
    # fotograma tras el cambio la tiene en el aire y luego aterriza entera.
    ir_a(pg, "obra", 60)
    aire = pg.evaluate("() => [...document.querySelectorAll('#obra .cae-obra-card')].map(c => getComputedStyle(c).opacity)")
    comprobar(any(o != "1" for o in aire), f"Obra: la entrada arranca (opacidades {aire})")
    pg.wait_for_timeout(2600)
    suelo = pg.evaluate("() => [...document.querySelectorAll('#obra .cae-obra-card')].map(c => getComputedStyle(c).opacity)")
    comprobar(all(o == "1" for o in suelo), f"Obra: las cinco aterrizan ({suelo})")
    # Stack: la instalacion en una sola onda (< 900 ms declarados).
    ir_a(pg, "creditos", 60)
    ret = pg.evaluate("() => [...document.querySelectorAll('.cae-cred-fig')].map(f => parseFloat(f.style.getPropertyValue('--retardo')) || 0)")
    comprobar(bool(ret) and max(ret) < 900, f"Stack: el ultimo retardo de la onda es < 900 ms (max {ret and max(ret)})")
    ctx.close()
    # Reduce: nada corre.
    ctx, pg, err2 = abrir(navegador, base, reduced_motion="reduce")
    est = pg.evaluate("() => ({ typed: document.querySelector('#hero .cae-term-typed')?.textContent, entrada: document.documentElement.classList.contains('js-cae-entrada') })")
    comprobar(not est["entrada"], "reduce: Titulo aterriza directo (sin js-cae-entrada)")
    ctx.close()
    return err + err2


def _oklab_to_srgb255(l: float, a_: float, b_: float) -> tuple[float, float, float]:
    """OKLab -> sRGB (0..255). Copiado de `measure-caelestia-titulo.py`
    (mismas matrices, Bjorn Ottosson)."""

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
    Chromium devuelve para los tokens de Caelestia). Copiado de
    `measure-caelestia-titulo.py`. Si no reconoce el formato devuelve `None`
    y la asercion de contraste lo reporta en vez de fallar en silencio."""
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


def _contraste(a: float, b: float) -> float:
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def _ratio(fg: tuple[float, float, float], bg: tuple[float, float, float]) -> float:
    """Ratio de contraste WCAG entre dos colores ya parseados."""
    return _contraste(_luminancia(fg), _luminancia(bg))


def gate_contraste(navegador, base: str) -> list[str]:
    """Contraste AA de los pares nuevos de B6, en los dos esquemas (13:00 /
    23:00). El fondo se resuelve subiendo por los ancestros hasta el primero
    con `background-color` NO transparente; Titulo es "el escritorio
    desnudo" (sin panel opaco, el fondo real es el canvas generativo), asi
    que si la subida no encuentra nada opaco se mide contra el token
    `--cae-surface`, igual que hace `measure-caelestia-titulo.py` para el
    titular (no contra `document.body`, que en Caelestia tampoco pinta
    fondo y daria un `rgba(0,0,0,0)` que no es el fondo real de nadie)."""
    print("\n[7] Contraste AA de los pares nuevos, en los dos esquemas")
    PARES = [
        ("hero", "#hero .cae-mv-linea b"),
        ("hero", "#hero .cae-mv-prosa"),
        ("hero", "#hero .cae-mv-cifra b"),
        ("hero", "#hero .cae-mv-cifra small"),
        ("creditos", ".cae-cred-rot"),
        ("creditos", ".cae-cred-nom"),
        ("obra", "#obra .cae-obra-caption"),
    ]
    peor = (99.0, "", "")
    for hora_min in (13 * 60, 23 * 60):
        etiqueta_hora = f"{hora_min // 60:02d}:{hora_min % 60:02d}"
        ctx, pg, err = abrir(navegador, base)
        pg.evaluate("(m) => window.__CAE_SET_MINUTOS__(m)", hora_min)
        pg.wait_for_timeout(800)
        for escena, sel in PARES:
            ir_a(pg, escena, 2600)
            d = pg.evaluate(
                """(sel) => { const e = document.querySelector(sel); if (!e) return null;
                let n = e, bg = null; while (n && n !== document.documentElement) { const b = getComputedStyle(n).backgroundColor;
                  if (b && !b.startsWith('rgba(0, 0, 0, 0)') && !b.endsWith(', 0)')) { bg = b; break; } n = n.parentElement; }
                if (!bg) bg = getComputedStyle(document.documentElement).getPropertyValue('--cae-surface').trim();
                return { fg: getComputedStyle(e).color, bg }; }""",
                sel,
            )
            comprobar(d is not None, f"existe {sel}")
            if d is None:
                continue
            fg, bg = _parse_rgb(d["fg"]), _parse_rgb(d["bg"])
            if not fg or not bg:
                comprobar(False, f"no se pudo parsear {sel} ({d})")
                continue
            r = _ratio(fg[:3], bg[:3])
            comprobar(r >= 4.5, f"{escena} {sel} a las {etiqueta_hora}: {r:.2f}:1 (piso AA 4.5, bg={d['bg']})")
            if r < peor[0]:
                peor = (r, sel, etiqueta_hora)
        ctx.close()
    comprobar(peor[0] >= 4.5, f"peor par {peor[1]} a las {peor[2]}: {peor[0]:.2f}:1 (piso AA 4.5)")
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:4213")
    ap.add_argument("--solo", default="", help="familias a correr, p.ej. 1,2 o 8b")
    args = ap.parse_args()
    # Cadenas, no enteros: la familia de banda media es "8b" (spec la nombra
    # asi), no un numero.
    solo = {x.strip() for x in args.solo.split(",") if x.strip()}
    errores: list[str] = []
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        if not solo or "1" in solo:
            errores += gate_ley(navegador, args.base)
        if not solo or "2" in solo:
            errores += gate_desbordamiento(navegador, args.base)
        if not solo or "3" in solo:
            errores += gate_titulo(navegador, args.base)
        if not solo or "4" in solo:
            errores += gate_obra(navegador, args.base)
        if not solo or "5" in solo:
            errores += gate_stack(navegador, args.base)
        if not solo or "6" in solo:
            errores += gate_entradas(navegador, args.base)
        if not solo or "7" in solo:
            errores += gate_contraste(navegador, args.base)
        if not solo or "8" in solo:
            print("\n[8] Tableta compacta (768x1024): familias 1-3 repetidas")
            errores += gate_ley(navegador, args.base, "tableta")
            errores += gate_desbordamiento(navegador, args.base, "tableta")
            errores += gate_titulo(navegador, args.base, "tableta")
        if not solo or "8b" in solo:
            errores += gate_obra_banda_media(navegador, args.base)
            errores += gate_stack_banda_media(navegador, args.base)
        navegador.close()
    print("\n[10] Consola sin errores")
    comprobar(not errores, f"cero errores de consola ({errores[:3]})")
    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print("  -", f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
