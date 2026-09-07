# Caelestia B6 (el escritorio en el teléfono) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que las escenas Título, Quién soy, Obra y Stack de Caelestia se vean y se usen por debajo de 1366 px: en la banda **compacta** (hasta 900 px: teléfono 390x844 y tableta vertical 768x1024) con cada workspace desplazándose por dentro en una columna, y en la banda **media** (901 a 1365: tableta apaisada 1024x768 y 1180x820) conservando la composición de escritorio con las piezas fijas encogidas. De 1366 en adelante no se toca nada.

**Architecture:** Un solo bloque `@media (max-width: 900px)` en `themes.css` bajo `[data-theme="caelestia"]` re-maqueta las cuatro escenas sobre el DOM que ya existe (lo que no sirve en móvil se oculta; Título gana un bloque nuevo de prosa en `hero.ts`). El carril, `inert` y el motor de color no cambian. Cada entrada conserva un solo gesto por debajo del corte, decidido en TypeScript leyendo si la pieza pinta (`getClientRects().length`), nunca por ancho de ventana. Un arnés nuevo, `scripts/measure-caelestia-movil.py`, con diez familias, cada una vista en rojo antes de aceptarse.

**Tech Stack:** Vite 8, TypeScript strict, GSAP 3, CSS (`@media`, `scroll-snap`), Playwright Python con `--use-gl=swiftshader`.

**Spec:** `docs/superpowers/specs/2026-09-07-caelestia-movil-design.md`

## Global Constraints

- Worktree `/home/aoshi/proyectos/portfolio-aoshi-movil`, rama `design/caelestia-movil`. Nunca tocar `/home/aoshi/proyectos/portfolio-aoshi`.
- Node 22: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"` en cada comando npm/npx.
- Preview de producción en el puerto **4213**: `npm run build && (nohup npx vite preview --port 4213 --strictPort > /tmp/preview-4213.log 2>&1 & echo $! > /tmp/preview-4213.pid)`. Antes de cada rebuild `kill $(cat /tmp/preview-4213.pid)`. Nunca `pkill -f`, nunca `npm run dev`, nunca otro puerto.
- **Un solo arnés a la vez** (la máquina murió por OOM con tres). Los largos con `nohup ... & PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done` en el MISMO comando Bash (timeout 600000). No terminar el turno «esperando».
- Dos cortes de B6: `@media (max-width: 900px)` (banda compacta) y `@media (min-width: 901px) and (max-width: 1365px)` (banda media). El shell conserva su bloque propio de 51.25rem (fase A); no se unifican.
- **Solo Obra y Stack necesitan banda media**, medido el 2026-09-07: a 1024 de ancho Obra desborda 1160 sobre 996 y Stack 1364 sobre 996; Stack sigue desbordando hasta 1280 (1364 sobre 1252). Título y Quién soy ya caben a 1024 y a 1180: en sus tareas la banda media entra solo como comprobación de no regresión, no como trabajo. Contacto la resuelve su propia rama, fuera de B6.
- Skin por CSS bajo `:root[data-theme="caelestia"]`, nunca ramas TypeScript por tema. Las ramas cortas de las entradas se deciden por «¿pinta la pieza?» (`el.getClientRects().length === 0`), no por `innerWidth`.
- Nunca `any`, nunca `gsap.from` (siempre `fromTo` con los dos extremos), nunca `console.log`, nunca `clamp()` continuo para tamaños de texto (tokens cambiados por `@media`), toda animación con rama `prefers-reduced-motion` explícita (el `*` no alcanza pseudo-elementos).
- Todo texto sale de `src/data/content.ts` literal; ningún campo derivado nuevo. El «10.º semestre» se extrae como ya hace `hero.ts` (paréntesis de `education[0].period`).
- No tocar `src/sections/obra/projectScene.ts`, `src/components/credits.ts`, `shaderBackground.ts`, Vice ni Hyprland.
- Cada gate nuevo se ve en ROJO contra su sabotaje antes de aceptarse; las dos líneas literales (rojo y verde) van al mensaje de commit.
- Playwright: en Caelestia el hash no cambia de workspace; se pulsa la pastilla `[data-cae-ws="<id>"]` (ids: `hero`, `quien-es`, `obra`, `creditos`, `contacto`). Contexto móvil: `viewport 390x844, device_scale_factor=2, is_mobile=True, has_touch=True`. Tableta: `768x1024`, mismo resto.
- Commits `tipo(scope): descripción`, cero emojis, sin push, sin fusionar en `main`.

---

### Task 0: Punto de partida y esqueleto del arnés (gates 1 y 2 en rojo)

**Files:**
- Modify: `docs/superpowers/specs/2026-09-07-caelestia-movil-design.md` (línea 3, `Estado:`)
- Create: `scripts/measure-caelestia-movil.py`

**Interfaces:**
- Produces (las usan todas las tareas siguientes):
  - `comprobar(condicion: bool, etiqueta: str) -> None` (imprime OK/FALLO y acumula en `FALLOS`).
  - `abrir(navegador, base, *, dispositivo="movil", reduced_motion=None) -> tuple[ctx, pg, errores]`: contexto móvil (`movil` = 390x844) o `tableta` (768x1024), oyentes de `pageerror`/`console error`, carga `?theme=caelestia`, espera 3000 ms.
  - `ir_a(pg, id: str, espera_ms: int = 1400) -> None`: pulsa `[data-cae-ws="<id>"]` y espera.
  - `ESCENAS = ["hero", "quien-es", "obra", "creditos", "contacto"]` con su `data-scene` real: `{"hero": "hero", "quien-es": "about", "obra": None, "creditos": "credits", "contacto": "contacto"}` — Obra no lleva `data-scene`, es `div#obra.obra-rail`.
  - `workspace_activo(pg) -> dict` con `id, scrollWidth, clientWidth, scrollHeight, clientHeight, scrollTop`.

- [x] **Step 1: El spec pasa a `en ejecucion`**

En la línea 3 del spec: `Estado: pendiente de plan` → `Estado: en ejecucion`.

```bash
git add docs/superpowers/specs/2026-09-07-caelestia-movil-design.md
git commit -m "docs(caelestia): el spec de B6 pasa a en ejecucion"
```

- [x] **Step 2: Build verde y preview en 4213**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && (nohup npx vite preview --port 4213 --strictPort > /tmp/preview-4213.log 2>&1 & echo $! > /tmp/preview-4213.pid); sleep 3; ss -ltnp | grep ':4213 '
```
Esperado: `BUILD` sin errores y una línea con `:4213`.

- [x] **Step 3: Escribir el esqueleto del arnés con los gates 1 y 2**

Crear `scripts/measure-caelestia-movil.py`:

```python
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
    pg.wait_for_timeout(3000)
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
```

- [x] **Step 4: Verlo en ROJO contra el build actual**

```bash
python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4213 --solo 1,2
```
Esperado: gate 2 en rojo en `quien-es` (847 > 362), `obra` (1316) y `creditos` (1364). Gate 1: la aserción «vuelve a cero» puede salir roja (hoy nadie reinicia el `scrollTop`). Copiar las líneas `FALLO` literales.

- [x] **Step 5: Commit del arnés en rojo**

```bash
git add scripts/measure-caelestia-movil.py
git commit -m "test(caelestia): arnes de B6 con los gates 1 y 2, en rojo contra el build actual

FALLO <pegar las lineas literales del Step 4>"
```

---

### Task 1: La ley y el shell por debajo de 900 px

**Files:**
- Modify: `src/themes/themes.css` (nuevo bloque al final de la sección de Caelestia, después de la regla `main[data-cae-track] > *::-webkit-scrollbar-thumb`, ~línea 6525)
- Modify: `src/themes/caelestia.choreography.ts:124-135` (`irA`)

**Interfaces:**
- Produces: el bloque `@media (max-width: 900px)` que las Tasks 2-5 extienden con sus reglas (todas dentro del MISMO bloque, con comentario de cabecera por escena).

- [x] **Step 1: Volver a cero el desplazamiento interior al cambiar de escena**

En `src/themes/caelestia.choreography.ts`, dentro de `irA`, justo después de `aislarInactivos(destino);`:

```ts
    // Un workspace se abre siempre por su principio (spec B6, «La ley en
    // movil»): en escritorio no hay nada que desplazar y esto no cambia
    // nada; en el telefono, volver a Stack tras leerla hasta abajo la
    // encontraba a mitad. Se hace en el destino, no en el origen, para que
    // el carril no muestre el salto durante el deslizamiento.
    if (destino !== origen) escenas[destino].scrollTop = 0;
```

- [x] **Step 2: El bloque de B6 en `themes.css`**

Añadir tras la regla `::-webkit-scrollbar-thumb` del carril:

```css
/*
 * B6 — el escritorio en el telefono (spec 2026-09-07-caelestia-movil).
 * Un solo corte, 900px: telefono (390) y tableta vertical (768). Por debajo,
 * el carril no cambia (cinco workspaces, `inert`, sin scroll de documento) y
 * cada ventana se desplaza por dentro: `overflow-y: auto` y
 * `overscroll-behavior: contain` ya vienen de la regla general del carril; lo
 * que este bloque hace es que el CONTENIDO quepa en el ancho. Lo que no sirve
 * en el telefono se oculta aqui, no se bifurca en TypeScript (patron B3/B4).
 * El shell conserva su bloque propio de 51.25rem (fase A).
 */
@media (max-width: 900px) {
  :root[data-theme="caelestia"] main[data-cae-track] > * {
    /* Sin barra visible: el pulgar ya sabe que una app se desplaza. */
    scrollbar-width: none;
  }
  :root[data-theme="caelestia"] main[data-cae-track] > *::-webkit-scrollbar {
    width: 0;
  }
  /* La marca de la esquina (themeSignature) pisa el dock a 390: fuera. */
  :root[data-theme="caelestia"] .theme-signature {
    display: none;
  }
}
```
Comprobar el selector real de la marca inferior: `grep -n 'class' src/components/themeSignature.ts` y usar su clase raíz (si es `theme-signature`, queda así; si no, sustituir). Si la rama `fix/caelestia-movil-contacto-dock` ya fusionó una regla equivalente en `main`, no duplicarla: dejar la suya y quitar esta.

- [x] **Step 3: Build, gate 1 en verde**

```bash
kill $(cat /tmp/preview-4213.pid); npm run build && (nohup npx vite preview --port 4213 --strictPort > /tmp/preview-4213.log 2>&1 & echo $! > /tmp/preview-4213.pid); sleep 3
python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4213 --solo 1
```
Esperado: gate 1 entero en verde (el 2 sigue rojo hasta las Tasks 3-5). `npm run lint` limpio.

- [x] **Step 4: Commit**

```bash
git add src/themes/themes.css src/themes/caelestia.choreography.ts
git commit -m "feat(caelestia): la ley en movil, el workspace vuelve a cero al cambiar y sin barra visible

Gate 1 (measure-caelestia-movil.py): rojo <linea literal> / verde <linea literal>"
```

---

### Task 2: Título «Silencioso»

**Files:**
- Modify: `src/sections/hero.ts:150-215` (bloque `.cae-movil` nuevo, montado junto a `widget` y `caeHead`)
- Modify: `src/themes/themes.css` (dentro del bloque de B6)
- Modify: `src/themes/caelestia.titulo.ts:111-335` (`montarEntrada`: rama corta) y `433-460` (`montarFiguraViva`: no montar si no pinta)
- Modify: `scripts/measure-caelestia-movil.py` (gates 3 y 6-Título)

**Interfaces:**
- Produces: DOM `.cae-movil` con hijos `.cae-mv-prosa` (tres `<span class="cae-mv-linea">`), `.cae-mv-cifras` (cuatro `<span class="cae-mv-cifra">` con `<b>` valor y `<small>` rótulo) y `.cae-mv-pie` (la pastilla `.cae-pilla` clonada como segundo nodo `cae-pilla-mv`).
- Consumes: `abrir`, `ir_a`, `comprobar` de Task 0.

- [x] **Step 1: Gate 3 (Título silencioso) y 6-Título en el arnés, en rojo**

Añadir a `scripts/measure-caelestia-movil.py` (antes de `main`), y en `main` las llamadas `if not solo or 3 in solo: errores += gate_titulo(navegador, args.base)` y `if not solo or 6 in solo: errores += gate_entradas(navegador, args.base)`:

```python
def literal_content(campo: str) -> str:
    """Lee un literal de src/data/content.ts sin evaluarlo (regex sobre el fuente)."""
    import pathlib, re
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
    trazo = pg.evaluate("() => { const p = document.querySelector('#hero .cae-trazo path'); return p ? getComputedStyle(p).strokeDashoffset : 'sin-trazo'; }")
    comprobar(typed is not None, "Titulo: la terminal existe")
    aterrizo = pg.evaluate("""() => new Promise(res => { const t0 = performance.now();
        const mira = () => { const f = document.querySelector('#hero .cae-firma');
          const ok = f && getComputedStyle(f).opacity === '1' && !document.documentElement.classList.contains('js-cae-entrada');
          if (ok || performance.now() - t0 > 6000) res({ ok, ms: Math.round(performance.now() - t0) }); else requestAnimationFrame(mira); };
        mira(); })""")
    comprobar(aterrizo["ok"], f"Titulo aterriza (firma visible, {aterrizo['ms']} ms de espera)")
    comprobar(pg.evaluate("() => document.querySelector('#hero .cae-trazo-stage').getClientRects().length === 0"),
              "Titulo: el trazo de la firma no pinta en movil")
    # Las tres siguientes se completan en las Tasks 3, 4 y 5 (una comprobacion por escena).
    ctx.close()
    # Reduce: nada corre.
    ctx, pg, err2 = abrir(navegador, base, reduced_motion="reduce")
    est = pg.evaluate("() => ({ typed: document.querySelector('#hero .cae-term-typed')?.textContent, entrada: document.documentElement.classList.contains('js-cae-entrada') })")
    comprobar(not est["entrada"], "reduce: Titulo aterriza directo (sin js-cae-entrada)")
    ctx.close()
    return err + err2
```

Correr `--solo 3,6`: esperado ROJO en «la tarjeta no pinta», «el bloque movil pinta», «el trazo no pinta». Copiar las líneas.

- [x] **Step 2: El DOM del bloque móvil en `hero.ts`**

Justo después de la construcción de `widget` (tras `el("div", "cae-wpie", [disponible]),\n  ]);`), añadir:

```ts
  /*
   * B6 (spec 2026-09-07-caelestia-movil, «Titulo: Silencioso»): por debajo de
   * 900px la tarjeta no se monta y lo que dice se lee en tres lineas de
   * prosa, mas las cuatro cifras como una linea de mono. Es OTRO DOM, oculto
   * en escritorio desde themes.css: no se reescala la tarjeta. Los literales
   * son los mismos de arriba (identity, education[0], experience[0], stats);
   * `semestre` es el parentesis de education[0].period, ya extraido.
   */
  const lineaProsa = (fuerte: string, resto: string): HTMLElement =>
    el("span", "cae-mv-linea", [el("b", "", [fuerte]), resto]);
  const prosa = el("p", "cae-mv-prosa", [
    lineaProsa(identity.now, ` en ${identity.location}.`),
    lineaProsa(education[0].degree, `, ${semestre}.`),
    lineaProsa(experience[0].organization, `, ${experience[0].period}.`),
  ]);
  const cifrasMovil = el(
    "p",
    "cae-mv-cifras",
    stats.map((s) => el("span", "cae-mv-cifra", [el("b", "", [s.value]), el("small", "", [s.label])])),
  );
  const luzMovil = el("i", "cae-wluz", []);
  luzMovil.setAttribute("aria-hidden", "true");
  const pillaMovil = el("span", "cae-pilla cae-pilla-mv", [luzMovil, identity.availability]);
  const bloqueMovil = el("div", "cae-movil", [prosa, cifrasMovil, el("div", "cae-mv-pie", [pillaMovil])]);
```
Comprobar que `stats` está importado en `hero.ts` (ya se usa para `statcol`; si el nombre difiere, usar el mismo que `statcol`). Añadir `bloqueMovil` al `section` después de `caeHead`: `[eyebrow, divider, surface, widget, caeHead, bloqueMovil, corner, term, trazoStage]`.

- [x] **Step 3: El CSS de Título en el bloque de B6**

Dentro de `@media (max-width: 900px) { ... }` de Task 1, añadir:

```css
  /* ---- Titulo: Silencioso (maqueta 6) ---- */
  :root[data-theme="caelestia"] .cae-widget,
  :root[data-theme="caelestia"] .cae-statcol,
  :root[data-theme="caelestia"] .cae-trazo-stage {
    display: none;
  }
  :root[data-theme="caelestia"] .cae-movil {
    display: block;
    padding: 0 1.375rem 1.5rem;
  }
  :root[data-theme="caelestia"] .cae-head {
    /* la cabecera deja de ser el bloque absoluto de 1080px: fluye */
    position: static;
    width: auto;
    padding: 1.625rem 1.375rem 0;
  }
  :root[data-theme="caelestia"] .cae-kicker {
    display: block;
  }
  :root[data-theme="caelestia"] .cae-firma {
    font-size: 1.125rem; /* 18px */
  }
  :root[data-theme="caelestia"] .cae-regla {
    display: none;
  }
  :root[data-theme="caelestia"] .cae-meta {
    display: block;
    margin-top: 0.375rem;
    font-size: 0.5625rem;
  }
  :root[data-theme="caelestia"] .cae-tit {
    margin-top: 7.5rem; /* el titular a media altura: aire, no relleno */
    text-align: left;
  }
  :root[data-theme="caelestia"] .cae-tit .cae-ln {
    display: block;
    white-space: nowrap;
    /* Paso discreto de la escala, no clamp: dos moderadas y una grande. */
    font-size: var(--t-3);
    line-height: 1.02;
  }
  :root[data-theme="caelestia"] .cae-tit .cae-ln:last-child {
    font-size: var(--t-7);
    margin-top: 0.25rem;
    line-height: 0.92;
  }
  :root[data-theme="caelestia"] .cae-mv-prosa {
    margin: 1.625rem 0 0;
    font-size: 0.8125rem;
    line-height: 1.7;
    color: var(--cae-on-surface-variant);
  }
  :root[data-theme="caelestia"] .cae-mv-linea {
    display: block;
  }
  :root[data-theme="caelestia"] .cae-mv-linea b {
    font-weight: 600;
    color: var(--cae-on-surface);
  }
  :root[data-theme="caelestia"] .cae-mv-cifras {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.25rem 1rem;
    margin: 1.375rem 0 0;
    font-family: var(--font-mono);
    font-size: 0.625rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--cae-on-surface-variant);
  }
  :root[data-theme="caelestia"] .cae-mv-cifra b {
    font-family: var(--font-display);
    font-variation-settings: var(--cae-display-axes-ficha);
    font-size: 0.9375rem;
    letter-spacing: 0;
    text-transform: none;
    color: var(--cae-on-surface);
    margin-right: 0.25rem;
  }
  :root[data-theme="caelestia"] .cae-mv-pie {
    margin-top: 1.375rem;
  }
```
Y FUERA del `@media`, en la sección de Título de escritorio (junto a `.cae-widget`), la regla que oculta el bloque en escritorio: `:root[data-theme="caelestia"] .cae-movil { display: none; }` más `.cae-movil { display: none; }` en `style.css` junto a `.cae-head` (Vice/Hyprland no lo enseñan nunca). Comprobar con `grep -n '\-\-t-3\|--t-7' src/themes/themes.css src/style.css` que los tokens existen; si la escala se llama distinto, usar los dos pasos equivalentes (~26 px y ~64 px medidos) y anotarlo en el commit. **Comprobar a mano** que `justificarTitular` (`caelestia.titulo.ts:32`) no escribe `font-size` inline sobre `.cae-ln` en móvil: si lo hace, en Step 4 se le pasa por alto cuando `statcol` no pinta.

- [x] **Step 4: La rama corta de la entrada y la figura viva**

En `src/themes/caelestia.titulo.ts`, en `montarEntrada`, tras la lectura de refs y antes del bloque de `prefers-reduced-motion`:

```ts
  // B6: por debajo del corte la tarjeta, la columna y el trazo no pintan
  // (themes.css). Se decide por «pinta o no», nunca por innerWidth: asi el
  // mismo criterio vale para tableta y para cualquier corte futuro.
  const corto = widget !== null && widget.getClientRects().length === 0;
```
Y en la construcción de la timeline, envolver los pasos que no existen en móvil:
- Pasos 5, 6 y 7 (trazo, relleno, aterrizaje de la firma trazada): `if (!corto) { ... } else { tl.set(firma, { opacity: 1 }); }` — la firma se muestra directa tras irse la terminal.
- Paso 10 (volteo de cifras): `if (!corto && bloques.length) { ... }`.
- Paso 11 (brote de la tarjeta y figura): `if (!corto && widget) { ... }`.
- Los pasos 8 y 9 (regla y barrido de las líneas) se conservan: la regla no pinta (`display: none`) y GSAP sobre un nodo oculto no cuesta nada; el barrido de las tres líneas es lo que hace que el titular «llegue». Duración total declarada en `corto`: terminal 0,26 + tecleo (~0,5) + parpadeo 0,56 + salida 0,26 + barrido ~0,4 solapado → comprobar que `tl.duration()` < 0,9 s; si el tecleo va a más, en `corto` usar `duration: 0.3` en el paso 2.
- `justificarTitular(root, medida)`: al principio, `if (root.querySelector('.cae-statcol')?.getClientRects().length === 0) return;` (en móvil las líneas no se justifican; el spec lo dice).

En `montarFiguraViva`, al principio:
```ts
  const figura = root.querySelector<HTMLElement>("#hero .cae-wfig");
  if (!figura || figura.getClientRects().length === 0) return FIGURA_NULA;
```
(comprobar el nombre real de la constante nula que ya exporta el módulo, `FIGURA_NULA` en la firma de `montarEntrada`).

- [x] **Step 5: Build, lint, gates 3 y 6 en verde, y el arnés de Título de escritorio intacto**

```bash
kill $(cat /tmp/preview-4213.pid); npm run build && (nohup npx vite preview --port 4213 --strictPort > /tmp/preview-4213.log 2>&1 & echo $! > /tmp/preview-4213.pid); sleep 3; npm run lint
python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4213 --solo 3,6
python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4213
```
Esperado: 3 y 6 verdes; el arnés de Título (escritorio, 1440x900) en `0 fallo(s)`. Captura 390x844 a 13:00 y 23:00 (`window.__CAE_SET_MINUTOS__(min)` tras cargar) en `/tmp/b6-titulo-*.png`, y MIRARLA: firma, titular en tres líneas con «no demos.» grande, prosa, cifras, pastilla; nada cortado.

- [x] **Step 6: Commit**

```bash
git add src/sections/hero.ts src/themes/themes.css src/style.css src/themes/caelestia.titulo.ts scripts/measure-caelestia-movil.py
git commit -m "feat(hero): Titulo silencioso en movil, sin tarjeta y con la entrada corta

Gates 3 y 6 (Titulo): rojo <literal> / verde <literal>"
```

---

### Task 3: Quién soy en columna

**Files:**
- Modify: `src/themes/themes.css` (bloque de B6)
- Modify: `src/themes/caelestia.ficha.ts:82-140` (`reproducir`: rama corta)
- Modify: `scripts/measure-caelestia-movil.py` (gate 6-Quién soy)

- [x] **Step 1: Gate 6-Quién soy en el arnés, en rojo**

En `gate_entradas`, tras el bloque de Título y antes de `ctx.close()`:

```python
    # Quien soy: el neofetch se teclea y la ficha aterriza; las filas no entran por capas.
    ir_a(pg, "quien-es", 200)
    primer = pg.evaluate("() => document.querySelector('[data-ficha-cmd]')?.textContent ?? null")
    comprobar(primer is not None and primer != "neofetch", f"Quien soy: la entrada arranca tecleando (primer fotograma «{primer}»)")
    fin = pg.evaluate("""() => new Promise(res => { const t0 = performance.now();
        const mira = () => { const c = document.querySelector('[data-ficha-cmd]'); const ok = c && c.textContent === 'neofetch';
          if (ok || performance.now() - t0 > 4000) res({ ok, ms: Math.round(performance.now() - t0) }); else requestAnimationFrame(mira); }; mira(); })""")
    comprobar(fin["ok"] and fin["ms"] < 2500, f"Quien soy: aterriza en menos de 2,5 s de sandbox ({fin['ms']} ms)")
```
Y en `gate_desbordamiento` ya está cubierto el ancho. Correr `--solo 2,6`: rojo en `quien-es` (847) y, si la entrada larga tarda más, en el tiempo.

- [x] **Step 2: El CSS de la ficha en columna**

En el bloque de B6:

```css
  /* ---- Quien soy: la salida de neofetch en una columna ---- */
  :root[data-theme="caelestia"] .ficha {
    padding: 1.25rem 1.25rem 1.875rem;
  }
  :root[data-theme="caelestia"] .ficha-cuerpo {
    display: flex;
    flex-direction: column;
    gap: 0.875rem;
  }
  :root[data-theme="caelestia"] .ficha-arte {
    width: 6rem; /* 96px, el retrato como logotipo pequeno */
    height: 6rem;
    flex: none;
  }
  :root[data-theme="caelestia"] .ficha-id {
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  :root[data-theme="caelestia"] .ficha-nombre {
    font-size: 1.625rem;
    line-height: 1;
  }
  :root[data-theme="caelestia"] .ficha-filas {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.625rem;
  }
  :root[data-theme="caelestia"] .ficha-fila {
    display: block;
  }
  :root[data-theme="caelestia"] .ficha-k {
    display: block;
    margin-bottom: 0.125rem;
  }
  :root[data-theme="caelestia"] .ficha-v {
    display: block;
    line-height: 1.4;
  }
```
Leer primero `src/sections/about.ts` y las reglas de escritorio de `.ficha-cuerpo`/`.ficha-col` (themes.css ~4639) para ajustar los selectores a la anidación real (`.ficha-col` puede ser el envoltorio de las columnas: en ese caso `flex-direction: column` va en `.ficha-col` y `.ficha-cuerpo` queda como está). El objetivo medible es el gate 2: `scrollWidth <= clientWidth` en `quien-es`, y que el filete (`[data-ficha-regla]`) mida el ancho del nombre, como en B2.

- [x] **Step 3: La rama corta de la entrada de la ficha**

En `caelestia.ficha.ts`, dentro de `reproducir`, tras el bloque `if (reduce) {...}`:

```ts
    // B6: si la escena esta en una columna (el retrato es pequeno porque no
    // pinta a su tamano de escritorio), la entrada conserva solo el tecleo;
    // las capas de grupos y filas aterrizan de golpe al terminar el comando.
    const corto = (host?.getClientRects()[0]?.width ?? 0) < 700;
```
(Usar como testigo el ancho pintado de `host` u otro nodo cuyo ancho de escritorio sea > 700 px y en móvil < 400: comprobarlo con `getBoundingClientRect` a 1440 y a 390 antes de fijar el umbral, y anotar los dos números en el comentario.) Y donde la timeline añade los tweens de `grupos`, `filas` y `tonos`: `if (corto) { linea.set([...grupos, ...filas, ...tonos], { opacity: 1, x: 0, scale: 1, scaleX: 1, clearProps: "transform" }); } else { ...los tweens actuales... }`. El tecleo, el cursor, la regla y el `clip-path` del nombre se quedan.

- [x] **Step 4: Build, lint, gates 2 (quien-es) y 6 en verde, arnés de Quién soy de escritorio intacto**

```bash
kill $(cat /tmp/preview-4213.pid); npm run build && (nohup npx vite preview --port 4213 --strictPort > /tmp/preview-4213.log 2>&1 & echo $! > /tmp/preview-4213.pid); sleep 3; npm run lint
python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4213 --solo 2,6
python3 scripts/measure-caelestia-quien-soy.py --base http://127.0.0.1:4213
```
Captura 390x844 de `quien-es` a 13:00 y mirarla.

- [x] **Step 5: Commit**

```bash
git add src/themes/themes.css src/themes/caelestia.ficha.ts scripts/measure-caelestia-movil.py
git commit -m "feat(about): Quien soy en columna en movil, con solo el neofetch tecleado

Gate 2 (quien-es): rojo <literal> / verde <literal>. Gate 6: <literal>"
```

---

### Task 4: Obra como carrusel con imán

**Files:**
- Modify: `src/themes/themes.css` (bloque de B6)
- Modify: `src/components/caelestiaObraEditorial.ts:186-300` (selección por `scrollend`, entrada corta)
- Modify: `scripts/measure-caelestia-movil.py` (gate 4, gate 6-Obra)

**Interfaces:**
- Consumes: `abrir(index)` ya existente en el módulo (privada), `cards: HTMLButtonElement[]`, `drawer`.
- Produces: el contenedor de tarjetas (leer su clase real en `buildCard`/montaje: es el padre común de `.cae-obra-card`) gana `data-cae-carrusel` en móvil solo por CSS; el módulo escucha `scrollend` en ese padre.

- [x] **Step 1: Gates 4 y 6-Obra en rojo**

```python
def gate_obra(navegador, base: str) -> list[str]:
    print("\n[4] Obra: carrusel con iman, la centrada es la elegida, el cajon la sigue")
    ctx, pg, err = abrir(navegador, base)
    ir_a(pg, "obra", 2600)
    n = pg.evaluate("() => document.querySelectorAll('#obra .cae-obra-card').length")
    comprobar(n == 5, f"hay cinco tarjetas ({n})")
    for i in range(5):
        r = pg.evaluate("""(i) => new Promise(res => {
            const cards = [...document.querySelectorAll('#obra .cae-obra-card')]; const c = cards[i];
            const pista = c.parentElement; const x = c.offsetLeft - (pista.clientWidth - c.offsetWidth) / 2;
            pista.scrollTo({ left: x, behavior: 'instant' });
            pista.dispatchEvent(new Event('scrollend'));
            setTimeout(() => { const pr = pista.getBoundingClientRect(), cr = c.getBoundingClientRect();
              const centrada = Math.abs((cr.left + cr.right) / 2 - (pr.left + pr.right) / 2) < 24;
              const sel = c.classList.contains('is-sel');
              const titulo = document.querySelector('#obra .cae-obra-drawer-title h3')?.textContent?.trim();
              res({ centrada, sel, titulo, esperado: c.querySelector('.cae-obra-caption')?.textContent?.trim() }); }, 600); })""", i)
        comprobar(r["centrada"], f"tarjeta {i+1} llega al centro con scrollTo")
        comprobar(r["sel"], f"tarjeta {i+1} centrada es la elegida")
        comprobar(r["titulo"] and r["esperado"] and r["esperado"].startswith(r["titulo"][:6]),
                  f"el cajon muestra la tarjeta {i+1} («{r['titulo']}»)")
    ctx.close()
    return err
```
En `gate_entradas`, tras Quién soy:
```python
    # Obra: la caida, solo de la tarjeta visible y sus vecinas; el primer fotograma tras el cambio la tiene en el aire.
    ir_a(pg, "obra", 60)
    aire = pg.evaluate("() => [...document.querySelectorAll('#obra .cae-obra-card')].map(c => getComputedStyle(c).opacity)")
    comprobar(any(o != "1" for o in aire), f"Obra: la entrada arranca (opacidades {aire})")
    pg.wait_for_timeout(2600)
    suelo = pg.evaluate("() => [...document.querySelectorAll('#obra .cae-obra-card')].map(c => getComputedStyle(c).opacity)")
    comprobar(all(o == "1" for o in suelo), f"Obra: las cinco aterrizan ({suelo})")
```
Correr `--solo 4,6`: rojo en «centrada es la elegida» (hoy se elige con clic) y posiblemente en el centrado (hoy no hay carrusel).

- [x] **Step 2: El CSS del carrusel y del cajón**

Leer `mountCaelestiaObraEditorial` para el nombre del contenedor de tarjetas (aquí `.cae-obra-row` a modo de ejemplo; sustituir por el real) y añadir al bloque de B6:

```css
  /* ---- Obra: carrusel con iman y cajon a una columna ---- */
  :root[data-theme="caelestia"] .obra-rail {
    padding: 1rem 0 1.625rem;
    overflow-y: auto;
  }
  :root[data-theme="caelestia"] .cae-obra-row {
    display: flex;
    gap: 0.75rem;
    padding: 0 1.25rem;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
    /* en escritorio la fila mide 1316: aqui la pista es el viewport y desplaza */
    width: auto;
  }
  :root[data-theme="caelestia"] .cae-obra-row::-webkit-scrollbar {
    width: 0;
    height: 0;
  }
  :root[data-theme="caelestia"] .cae-obra-card {
    flex: 0 0 15.625rem; /* 250px */
    scroll-snap-align: center;
    /* la inclinacion alterna no se pinta en movil */
    transform: none !important;
    rotate: 0deg;
  }
  :root[data-theme="caelestia"] .cae-obra-drawer {
    margin: 0.875rem 1rem 0;
    display: block;
    height: auto;
    container-type: normal;
  }
  :root[data-theme="caelestia"] .cae-obra-drawer-preview {
    height: auto;
    aspect-ratio: 16 / 10;
    max-height: none;
  }
```
El `!important` en `transform` está justificado: la inclinación la escribe GSAP inline (`rotate: tilt` en `prepararEstadoInicial`); en Step 3 se deja de escribir en móvil y entonces el `!important` se quita (no se acepta en el commit final). Comprobar que el cajón de escritorio usa `grid-template-areas` (~línea 3837): en móvil `display: block` apila `texto / captura / meta` en el orden del DOM; si el orden visual del DOM no es kicker-título-lead-captura-meta, usar `display: grid; grid-template-areas: "texto" "captura" "meta"` con las mismas áreas que escritorio.

- [x] **Step 3: La selección por `scrollend` y la entrada corta**

En `mountCaelestiaObraEditorial`, tras `cards.forEach((card, index) => { card.addEventListener("click", ...` :

```ts
  // B6: en el carrusel (movil) la tarjeta centrada es la elegida, sin pulsar.
  // Se decide por estado, no por ancho: solo si la pista desplaza en X.
  const pista = cards[0]?.parentElement ?? null;
  const elegirCentrada = (): void => {
    if (!pista || pista.scrollWidth <= pista.clientWidth + 1) return;
    const centro = pista.scrollLeft + pista.clientWidth / 2;
    let mejor = 0;
    let dist = Number.POSITIVE_INFINITY;
    cards.forEach((c, i) => {
      const d = Math.abs(c.offsetLeft + c.offsetWidth / 2 - centro);
      if (d < dist) {
        dist = d;
        mejor = i;
      }
    });
    abrir(mejor);
  };
  // `scrollend` donde exista; `scroll` con reposo de 120 ms como reserva.
  let reposo = 0;
  const alDesplazar = (): void => {
    window.clearTimeout(reposo);
    reposo = window.setTimeout(elegirCentrada, 120);
  };
  pista?.addEventListener("scrollend", elegirCentrada);
  pista?.addEventListener("scroll", alDesplazar, { passive: true });
```
Y en `destroy`: `pista?.removeEventListener("scrollend", elegirCentrada); pista?.removeEventListener("scroll", alDesplazar); window.clearTimeout(reposo);`.

Entrada corta: en `prepararEstadoInicial` y `jugarEntrada`, calcular `const enCarrusel = pista !== null && pista.scrollWidth > pista.clientWidth + 1;` y, si es así, (a) no escribir `rotate: tilt` (dejar `rotate: 0`) y (b) animar solo `cards.slice(Math.max(0, seleccionado - 1), seleccionado + 2)`; el resto se pone directo con `gsap.set(otras, { opacity: 1, y: 0, rotate: 0 })`. El cajón entra en un solo paso: `.to(drawer, { opacity: 1, duration: 0.24 })` y `gsap.set` del resto de capas al estado final. Duración total en móvil < 0,9 s (`tl.duration()`).

- [x] **Step 4: Build, lint, gates 2 (obra), 4 y 6 en verde; arnés de Obra de escritorio como estaba**

```bash
kill $(cat /tmp/preview-4213.pid); npm run build && (nohup npx vite preview --port 4213 --strictPort > /tmp/preview-4213.log 2>&1 & echo $! > /tmp/preview-4213.pid); sleep 3; npm run lint
python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4213 --solo 2,4,6
python3 scripts/measure-caelestia-obra.py --base http://127.0.0.1:4213
```
El arnés de Obra de escritorio arrastra tres fallos de contraste conocidos (su propio instrumento, documentado en CLAUDE.md): la comparación es «los mismos tres, ninguno nuevo». Captura 390x844 de `obra` a 13:00 y mirarla: dos tarjetas y media, la central marcada, el cajón debajo.

- [x] **Step 4b: La banda media (901-1365)**

La fila de cinco tarjetas mide 1316 px fijos y no cabe a ningún ancho de tableta apaisada
(medido: 1160 sobre 996 útiles a 1024x768, 1212 sobre 1152 a 1180x820). En
`@media (min-width: 901px) and (max-width: 1365px)`, las tarjetas dejan de tener ancho fijo y se
reparten el disponible manteniendo la proporción 16:10 de la captura:

```css
@media (min-width: 901px) and (max-width: 1365px) {
  :root[data-theme="caelestia"] .cae-obra-row {
    /* Cinco columnas iguales del ancho que haya, no cinco anchos fijos. El
       hueco entre tarjetas se mantiene; lo que cede es la tarjeta. */
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem;
  }
  :root[data-theme="caelestia"] .cae-obra-card {
    width: auto;
    min-width: 0;
  }
}
```
Comprobar el nombre real del contenedor (`.cae-obra-row` es una suposición: leerlo del módulo) y
que la leyenda en Fraunces itálica sigue cabiendo sin partirse. Si a 1024 la tarjeta baja de
150 px de ancho, no encoger más: convertir la fila en el mismo carrusel con imán de la banda
compacta, reutilizando la regla que ya escribiste, y decirlo en el commit.

Gate: en el arnés, familia 8b (banda media), a 1024x768 y 1180x820 el workspace de Obra no
desborda (`scrollWidth <= clientWidth`) y las cinco tarjetas están dentro de la caja. Verlo en
rojo antes: hoy sale 1160/996.

- [x] **Step 5: Commit**

```bash
git add src/themes/themes.css src/components/caelestiaObraEditorial.ts scripts/measure-caelestia-movil.py
git commit -m "feat(obra): la Editorial es un carrusel con iman en movil y la centrada es la elegida

Gates 2 (obra), 4 y 6: rojo <literal> / verde <literal>"
```

---

### Task 5: Stack en bandas apiladas, tocar elige

**Files:**
- Modify: `src/themes/themes.css` (bloque de B6)
- Modify: `src/components/caelestiaCreditosBandeja.ts:196-260` (toque, onda única)
- Modify: `scripts/measure-caelestia-movil.py` (gate 5, gate 6-Stack)

- [x] **Step 1: Gates 5 y 6-Stack en rojo**

```python
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
    comprobar(est["pressed"] == "true" and est["nombre"] == objetivo, f"tocar elige («{objetivo}» → ficha «{est['nombre']}», aria-pressed={est['pressed']})")
    ctx.close()
    return err
```
En `gate_entradas`, tras Obra:
```python
    # Stack: la instalacion en una sola onda (< 900 ms declarados).
    ir_a(pg, "creditos", 60)
    ret = pg.evaluate("() => [...document.querySelectorAll('.cae-cred-fig')].map(f => parseFloat(f.style.getPropertyValue('--retardo')) || 0)")
    comprobar(ret and max(ret) < 900, f"Stack: el ultimo retardo de la onda es < 900 ms (max {ret and max(ret)})")
```
Correr `--solo 5,6`: rojo en «dentro de la caja» (1364 de ancho) y en el retardo (hoy el último es 260 + 3·190 + 7·34 = 1068).

- [x] **Step 2: El CSS de las bandas**

```css
  /* ---- Stack: bandas apiladas, piezas a cuatro columnas ---- */
  :root[data-theme="caelestia"] .cae-cred-wrap {
    padding: 0.875rem 1rem 1.625rem;
    height: auto;
  }
  :root[data-theme="caelestia"] .cae-cred-cab {
    min-height: 0;
    display: flex;
    gap: 0.75rem;
    align-items: center;
    padding: 0.375rem 0.25rem 0.875rem;
  }
  :root[data-theme="caelestia"] .cae-cred-grid {
    display: block;
  }
  :root[data-theme="caelestia"] .cae-cred-banda {
    display: block;
    border-top: 1px solid var(--cae-outline);
    padding: 0.75rem 0 0.875rem;
  }
  :root[data-theme="caelestia"] .cae-cred-banda:first-child {
    border-top: 0;
  }
  :root[data-theme="caelestia"] .cae-cred-rot {
    text-align: left;
    width: auto;
    margin-bottom: 0.625rem;
  }
  :root[data-theme="caelestia"] .cae-cred-tira {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.625rem 0.5rem;
  }
  :root[data-theme="caelestia"] .cae-cred-pieza {
    width: auto;
    height: auto;
    padding: 0;
  }
  :root[data-theme="caelestia"] .cae-cred-fig {
    width: 3.5rem; /* 56px */
    height: 3.5rem;
    margin: 0 auto;
  }
  :root[data-theme="caelestia"] .cae-cred-nom {
    font-size: 0.53rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
```
Leer las reglas de escritorio (themes.css 5018-5140) y ajustar los nombres de clase a los reales de `construirPieza` y del montaje de bandas (`.cae-cred-rot`, `.cae-cred-tira`, `.cae-cred-terr`: comprobar cuál es el rótulo y cuál la tira de piezas).

- [x] **Step 3: Tocar elige y la onda única**

En `mountCaelestiaCreditosBandeja`, `entrar` ya se dispara con `click` (y un tap dispara `click`): comprobar que `is-tocando` no se queda pegado tras el tap (no hay `mouseleave` en táctil): añadir `b.addEventListener("pointerup", salir)` cuando `pointerType === "touch"`:

```ts
    const soltarToque = (ev: PointerEvent): void => {
      if (ev.pointerType === "touch") salir();
    };
    b.addEventListener("pointerup", soltarToque);
    escuchas.push(() => b.removeEventListener("pointerup", soltarToque));
```
Onda única: donde se calcula `--retardo`, decidir por estado (la banda no es una rejilla de 4 filas si está apilada: `grid.getClientRects()[0].height > grid.clientHeight` no vale; usar el testigo de que las bandas se apilan: `botones[0].getBoundingClientRect().width < 100`, medido en escritorio 88+padding, en móvil 56):

```ts
    const apilada = (botones[0]?.getBoundingClientRect().width ?? 200) < 100;
    // B6: en movil una sola onda para las 23 (max 260 + 22*26 = 832 ms < 900).
    fig?.style.setProperty("--retardo", apilada ? `${260 + indice * 26}ms` : `${260 + gi * 190 + i * 34}ms`);
```
(`indice` es el contador global que ya existe en ese bucle.) Con `reduce` no se toca: la rama ya no pone retardos.

- [x] **Step 4: Build, lint, gates 2 (creditos), 5 y 6 en verde; arnés de Créditos de escritorio (nohup + PID) en verde**

```bash
kill $(cat /tmp/preview-4213.pid); npm run build && (nohup npx vite preview --port 4213 --strictPort > /tmp/preview-4213.log 2>&1 & echo $! > /tmp/preview-4213.pid); sleep 3; npm run lint
python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4213 --solo 2,5,6
nohup python3 scripts/measure-caelestia-creditos.py --base http://127.0.0.1:4213 > /tmp/creditos-b6.log 2>&1 & PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -20 /tmp/creditos-b6.log
```
Captura 390x844 de `creditos` a 13:00 y mirarla.

- [x] **Step 4b: La banda media (901-1365)**

Las cuatro bandas miden 1364 px fijos —la calle del rótulo son 158 px y cada módulo 142— y no
caben a ningún ancho de tableta apaisada: desbordan a 1024 (1364 sobre 996), a 1180 (sobre 1152) y
todavía a 1280 (sobre 1252). En `@media (min-width: 901px) and (max-width: 1365px)` la calle y el
módulo dejan de ser fijos y se reparten el ancho:

```css
@media (min-width: 901px) and (max-width: 1365px) {
  :root[data-theme="caelestia"] .cae-cred-banda {
    /* La calle del rotulo cede primero (de 158 a lo que haya, con un minimo
       legible); la tira de piezas se queda con el resto. */
    grid-template-columns: minmax(6rem, 158px) 1fr;
  }
  :root[data-theme="caelestia"] .cae-cred-tira {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 0.5rem;
  }
  :root[data-theme="caelestia"] .cae-cred-pieza {
    width: auto;
    min-width: 0;
  }
}
```
Ocho columnas es el máximo de piezas que tiene una banda (Interfaz). **Las 23 piezas siguen
midiendo todas lo mismo** (la ley de B4: el tamaño no codifica nada), así que si el reparto
fluido las deja de tamaños distintos por banda, fijar el lado al de la banda más llena y
alinearlas, no dejar que cada banda escale por su cuenta. Comprobarlo midiendo las 23.

Gate: familia 8b, a 1024x768 y 1180x820 el workspace de Stack no desborda y las 23 piezas están
dentro de la caja y miden lo mismo. Verlo en rojo antes: hoy sale 1364/996.

- [x] **Step 5: Commit**

```bash
git add src/themes/themes.css src/components/caelestiaCreditosBandeja.ts scripts/measure-caelestia-movil.py
git commit -m "feat(credits): la bandeja se apila en movil, tocar elige y la instalacion es una sola onda

Gates 2 (creditos), 5 y 6: rojo <literal> / verde <literal>"
```

---

### Task 6: Contraste, tableta, escritorio intacto, críticos y cierre

**Files:**
- Modify: `scripts/measure-caelestia-movil.py` (gates 7 y 8)
- Modify: `docs/superpowers/specs/2026-09-07-caelestia-movil-design.md` (`Estado`, registro, gates de crítica)
- Modify: `.claude/rules/verification.md` (fila nueva), `CLAUDE.md` (bloque de B6)

- [x] **Step 1: Gate 7 (contraste) en rojo con sabotaje**

Copiar de `scripts/measure-caelestia-titulo.py` las funciones de parseo y ratio (`_parse_rgb`, `_ratio` o `contraste`/`luz_texto`, y el parseo de `oklch` si lo lleva; `grep -n "def _ratio\|def contraste\|def _parse_rgb\|oklch" scripts/measure-caelestia-titulo.py`) y añadir:

```python
def gate_contraste(navegador, base: str) -> list[str]:
    print("\n[7] Contraste AA de los pares nuevos, en los dos esquemas")
    PARES = [
        ("hero", "#hero .cae-mv-linea b"), ("hero", "#hero .cae-mv-prosa"), ("hero", "#hero .cae-mv-cifra b"), ("hero", "#hero .cae-mv-cifra small"),
        ("creditos", ".cae-cred-rot"), ("creditos", ".cae-cred-nom"),
        ("obra", "#obra .cae-obra-caption"),
    ]
    peor = (99.0, "", "")
    for hora in (13 * 60, 23 * 60):
        ctx, pg, err = abrir(navegador, base)
        pg.evaluate("(m) => window.__CAE_SET_MINUTOS__(m)", hora)
        pg.wait_for_timeout(800)
        for escena, sel in PARES:
            ir_a(pg, escena, 2600)
            d = pg.evaluate("""(sel) => { const e = document.querySelector(sel); if (!e) return null;
                let n = e, bg = null; while (n && n !== document.documentElement) { const b = getComputedStyle(n).backgroundColor;
                  if (b && !b.startsWith('rgba(0, 0, 0, 0)') && !b.endsWith(', 0)')) { bg = b; break; } n = n.parentElement; }
                return { fg: getComputedStyle(e).color, bg: bg ?? getComputedStyle(document.body).backgroundColor }; }""", sel)
            comprobar(d is not None, f"existe {sel}")
            if d is None:
                continue
            fg, bg = _parse_rgb(d["fg"]), _parse_rgb(d["bg"])
            if not fg or not bg:
                comprobar(False, f"no se pudo parsear {sel} ({d})")
                continue
            r = _ratio(fg[:3], bg[:3])
            if r < peor[0]:
                peor = (r, sel, "13:00" if hora == 780 else "23:00")
        ctx.close()
    comprobar(peor[0] >= 4.5, f"peor par {peor[1]} a las {peor[2]}: {peor[0]:.2f}:1 (piso AA 4.5)")
    return []
```
Nota: el fondo se resuelve subiendo hasta el primer ancestro con fondo NO transparente; si algún par cae sobre el fondo generativo (Título es «el escritorio desnudo»), medir contra `--cae-surface` como hace el arnés de Título para el titular, y decirlo en el comentario. **Sabotaje:** `.cae-mv-prosa { color: var(--cae-outline) }` dentro del bloque de B6 → build → rojo (≈1,8:1 de noche); deshacer → verde. Pegar las dos líneas.

- [x] **Step 2: Gate 8 (tableta compacta y media) y gate 9 (escritorio intacto, documentado)**

Además de repetir las familias 1 a 3 a 768x1024, añadir la **familia 8b, banda media**, a
1024x768 y 1180x820: las cinco escenas sin desbordamiento horizontal, las cinco tarjetas de Obra
alcanzables, las 23 piezas de Stack dentro y del mismo tamaño, y Título y Quién soy sin regresión
(hoy ya caben, así que aquí solo se vigilan).

En `main`: `if not solo or 8 in solo: errores += gate_ley(navegador, args.base, "tableta") + gate_desbordamiento(navegador, args.base, "tableta")` y añadir a `gate_titulo` un parámetro `dispositivo` para correrlo también en tableta. El gate 9 no vive en este arnés: es correr los cinco arneses de escritorio (Título, Quién soy, Obra con sus tres conocidos, Créditos con nohup, hora) contra este build; se deja escrito en el docstring y en `verification.md`.

- [ ] **Step 3: Verificación completa**

```bash
kill $(cat /tmp/preview-4213.pid); npm run build && (nohup npx vite preview --port 4213 --strictPort > /tmp/preview-4213.log 2>&1 & echo $! > /tmp/preview-4213.pid); sleep 3; npm run lint
python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4213            # 0 fallo(s)
python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4213
python3 scripts/measure-caelestia-quien-soy.py --base http://127.0.0.1:4213
python3 scripts/measure-caelestia-obra.py --base http://127.0.0.1:4213             # los tres conocidos, ninguno nuevo
nohup python3 scripts/measure-caelestia-creditos.py --base http://127.0.0.1:4213 > /tmp/cred.log 2>&1 & PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -20 /tmp/cred.log
nohup python3 scripts/measure-caelestia-hora.py --base http://127.0.0.1:4213 > /tmp/hora.log 2>&1 & PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -5 /tmp/hora.log
python3 scripts/measure-caelestia-fundido.py --base http://127.0.0.1:4213
python3 scripts/verify.py --url http://127.0.0.1:4213                              # 12 conocidos, 0 nuevos
```
Capturas: las cinco escenas a 390x844 y a 768x1024, a 13:00 y 23:00 (20 imágenes), más las cinco a 1440x900 a 13:00; en `/tmp/b6-final-*.png`. Mirarlas todas: nada cortado, nada pisado, el escritorio igual que antes.

- [ ] **Step 4: Gates de crítica**

Lanzar `lidia-naive-tester` (contexto móvil 390x844, pregunta: ¿en el teléfono se entiende quién es y cómo contactar en dos segundos?) y `vera-art-director` (móvil y tableta; jerarquía, rejilla 4/8, tokens, que el móvil sea el mismo tema), uno tras otro, con PROHIBIDO editar producción. Un P0 se arregla antes de cerrar (con su gate en rojo); los P1 se registran en el spec.

- [ ] **Step 5: Cerrar el spec y la documentación**

- Spec: `Estado: implementado`; sección `## Registro de implementación` (qué rompió cada gate en rojo, medidas finales: tamaños del titular, retardo máximo de la onda, peor contraste, scrollWidth por escena antes/después; desviaciones respecto al spec) y `### Resultado` bajo «Gates de crítica».
- `.claude/rules/verification.md`: fila para `measure-caelestia-movil.py` (las diez familias, «un arnés a la vez», que el gate 9 son los arneses de escritorio corridos aparte).
- `CLAUDE.md` (raíz) y `.claude/CLAUDE.md`: bloque «Caelestia B6 (móvil)» tras el del repaso de interfaces: la ley en móvil, el corte de 900, Título silencioso, lo que perdieron las entradas, y las trampas nuevas que hayan salido.
- Memoria de sesión (la escribe el orquestador).

- [ ] **Step 6: Commit y cierre de rama**

```bash
git add scripts/measure-caelestia-movil.py docs/superpowers/specs/2026-09-07-caelestia-movil-design.md docs/superpowers/plans/2026-09-07-caelestia-movil.md CLAUDE.md
git commit -m "feat(caelestia): B6 cierra con contraste, tableta y los gates de critica"
```
Después, `superpowers:finishing-a-development-branch`: fusionar `design/caelestia-movil` en `main` (con `--no-ff`, después de que `fix/caelestia-movil-contacto-dock` esté en `main`, para heredar la marca oculta y el sello), retirar el worktree, matar el preview por PID.
