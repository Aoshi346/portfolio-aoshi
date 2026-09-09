# Los cimientos (Stack en Hyprland) — plan de implementacion

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sustituir el catastro de la escena "Stack" de Hyprland por los cimientos: tres areas en
columnas sobre un suelo de brasa con los cinco lenguajes base, con entrada mandada por el suelo y
la frase `detail` al rozar, sin tocar Vice, Caelestia ni `credits.ts`.

**Architecture:** Modulo propio `src/components/hyprStackCimientos.ts` (DOM construido desde
`skillGroups`, sin GSAP: `IntersectionObserver` para el disparo, transiciones CSS para los
tiempos), montado desde `src/main.ts` con `import()` diferido bajo `theme.id === "hyprland"`,
como `obraCartel.ts`. El DOM generico de `credits.ts` se oculta entero bajo Hyprland desde
`themes.css`, y `[data-cimientos]` nace oculto en la hoja base. Los gestos 4 y 5 de
`hypr.choreography.ts` (la corriente y el apuntado del catastro), su bloque CSS y su arnes se
retiran. Arnes nuevo `scripts/measure-cimientos.py`, escrito gate a gate ANTES del codigo que
vigila, y visto en rojo cada vez.

**Tech Stack:** Vite 8, TypeScript strict, CSS (custom properties, `clip-path`, `@media`),
`IntersectionObserver`, Playwright (Python) con `--use-gl=swiftshader`.

**Spec:** `docs/superpowers/specs/2026-09-09-hyprland-stack-cimientos-design.md` — el plan
argumenta desde el spec; quien ejecute lee los dos.

## Global Constraints

- **Solo el tema Hyprland.** Vice y Caelestia identicos a `main`, comprobado con `git worktree`
  (nunca `git stash`).
- **`src/data/content.ts` no cambia.** Toda cadena en pantalla sale literal de `skillGroups`
  (`label`, `name`, `detail`); ni un rotulo inventado.
- **`src/components/credits.ts` no se toca en esta fase.** `src/backgrounds/shaderBackground.ts`
  tampoco (lo comparten los tres temas).
- Nunca `any` (usar `unknown` con guardas). Nunca `gsap.from`. Nunca `console.log`. Cero emojis.
  Guardias de `prefers-reduced-motion` intactas y explicitas por selector.
- Nada se presenta ni se retira por `opacity`: recorte, encendido o trazo.
- Tallas solo de la escala cerrada (`--t-1` 12, `--t-2` 16, `--t-3` 21,33, `--t-4` 28,43, `--t-5`
  37,9). Nada de `clamp()`.
- Radio 0, sin sombras, desenfoques, resplandores ni `backdrop-filter`. `--l1` solo en el suelo y
  el rotulo de seccion; `--l3` solo con puntero o foco.
- Ningun pin de ScrollTrigger. Ningun bucle `infinite`.
- Todo el CSS nuevo bajo `:root[data-theme="hyprland"]`, salvo el `display: none` de base.
- Los arneses corren contra el build de produccion servido (`npx vite preview --port 4213`),
  nunca `npm run dev`. Antes de servir: `ss -ltnp | grep 4213`. Al terminar se mata POR PID (el que
  escucha en el puerto segun `ss`), nunca `pkill -f "vite preview"`. Nunca dos arneses a la vez.
- **Ningun gate se acepta sin haberlo visto dar rojo** contra el fallo que dice cazar. Cada tarea
  que anade un gate lo corre primero contra el estado anterior y pega la salida.
- Node 22 en cada shell: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`.
- Un commit por tarea, `tipo(scope): descripcion`, scope `credits`. Sin push. Sin merge a `main`.
- Worktree de trabajo: `/home/aoshi/proyectos/portfolio-aoshi-hypr`, rama `fix/repaso-hyprland`.

---

## Mapa de ficheros

| Fichero | Que hace en este plan |
|---|---|
| `src/components/hyprStackCimientos.ts` | **Crear.** Construye el DOM desde `skillGroups`, dispara la entrada con `IntersectionObserver`, gestiona el apuntado (puntero, foco, toque) y `destroy()`. |
| `src/main.ts` | **Modificar** (~lineas 172-178 y 335). Puerta de montaje bajo Hyprland y `destroy()` en `pagehide`. |
| `src/style.css` | **Modificar** (~linea 1404). `[data-cimientos] { display: none }` de base. |
| `src/themes/themes.css` | **Modificar.** Oculta `.credits-grid` bajo Hyprland; bloque nuevo `LOS CIMIENTOS`; retira el bloque `EL CATASTRO` (lineas 8575-9371, incluido su `@media (max-width: 820px)` y el bloque "contenido de la franja"). |
| `src/themes/hypr.choreography.ts` | **Modificar.** Retira los gestos 4 y 5 (lineas 266-539), la sonda `__hyprSkills`/`__hyprSkillTimers` (lineas 13-27, 77-89) y los imports/constantes que queden sin uso. |
| `scripts/measure-cimientos.py` | **Crear.** Trece gates del spec. |
| `scripts/measure-catastro.py` | **Borrar** (`git rm`). |
| `scripts/verify.py` | **Modificar** (~lineas 1266-1303). El marcador de Hyprland pasa a "`.credits-grid` no se pinta, `[data-cimientos]` si". |
| `.claude/rules/verification.md` | **Modificar.** Fila del arnes nuevo en la tabla. |
| `docs/superpowers/specs/2026-09-09-hyprland-stack-cimientos-design.md` | **Modificar** al cerrar: `Estado: implementado` y `## Registro de implementacion`. |

---

### Task 1: El arnes nace antes que el dispositivo (gates 1, 2 y 13)

**Files:**
- Create: `scripts/measure-cimientos.py`

**Interfaces:**
- Produces: `python3 scripts/measure-cimientos.py --url http://localhost:4213 [--contraste]`,
  codigo de salida 0/1, lineas `FALLO: [contexto] mensaje` y recuento final `N fallo(s)`. Las
  tareas siguientes anaden funciones `gate_N(...)` a este mismo fichero y las registran en
  `main()`.

- [x] **Step 1: Escribir el arnes con los gates 1, 2 y 13**

```python
"""Arnes de los cimientos de "Stack" en Hyprland (spec 2026-09-09).

Trece gates, uno por familia del spec (`## Los gates`). Cada uno nacio de un
fallo real de esta pista o de otra, y ninguno se acepto sin verlo dar rojo
contra el fallo que dice cazar:

  1. Los cimientos se VEN en Hyprland, y el generico `.credits-grid` NO. Sin
     esto los demas gates se autoanulan: un nodo con `display: none` no
     desborda ni descuadra (leccion de measure-placa.py y measure-catastro.py).
  2. Los cimientos NO existen en Vice ni en Caelestia (comprobados por
     separado, no con un AND que taparia un huerfano), y la bandeja de
     Caelestia sigue con sus 23 piezas.
 13. Consola: cero errores y cero "context lost" en las TRES paginas. Sin
     oyente en Vice y Caelestia un fallo global en themes.css dejaba el gate
     en verde (pagado en measure-caelestia-cursor.py).

Los gates 3-12 se documentan en su propia funcion segun se anaden.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

VIEWPORTS = [("escritorio", 1440, 900), ("movil", 390, 844)]
ANCHOS_DESBORDE = [390, 821, 1024, 1200, 1440]


def abrir(b, url: str, tema: str, w: int, h: int, errores: list, reduce: bool = False):
    """Pagina nueva con oyente de consola SIEMPRE puesto. `errores` acumula
    los de todas las paginas: el gate 13 los lee al final."""
    ctx = b.new_context(
        viewport={"width": w, "height": h},
        reduced_motion="reduce" if reduce else "no-preference",
    )
    pg = ctx.new_page()
    etiqueta = f"{tema} {w}x{h}"
    pg.on(
        "console",
        lambda m: errores.append(f"[{etiqueta}] {m.type}: {m.text}")
        if m.type == "error" or "context lost" in m.text.lower()
        else None,
    )
    pg.on("pageerror", lambda e: errores.append(f"[{etiqueta}] pageerror: {e}"))
    pg.goto(f"{url}/?theme={tema}", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(9000)
    return pg


def ir_a_credits(pg, offset: int = 0) -> bool:
    """Coloca el borde superior de la escena a `offset` px del tope. Lenis
    sigue desplazando tras un scrollTo: se espera a que asiente."""
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"credits\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        return False
    pg.evaluate(f"window.scrollTo(0, {top + offset})")
    pg.wait_for_timeout(2500)
    return True


def se_ve(pg, selector: str) -> bool:
    return pg.evaluate(
        "(sel) => { const n = document.querySelector(sel); if (!n) return false;"
        " const s = getComputedStyle(n); const r = n.getBoundingClientRect();"
        " return s.display !== 'none' && s.visibility !== 'hidden'"
        "   && parseFloat(s.opacity) > 0 && r.width > 0 && r.height > 0; }",
        selector,
    )


def gate_1_se_ven(pg, nombre: str, fallos: list) -> None:
    if not se_ve(pg, "[data-cimientos]"):
        fallos.append(f"[{nombre}] gate 1: [data-cimientos] NO se ve en Hyprland")
    if se_ve(pg, ".credits-grid"):
        fallos.append(f"[{nombre}] gate 1: el generico .credits-grid SE PINTA bajo Hyprland")
    n = pg.evaluate("() => document.querySelectorAll('[data-cimientos] .cim-nombre').length")
    if n != 23:
        fallos.append(f"[{nombre}] gate 1: {n} nombres en los cimientos, esperados 23")


def gate_2_no_existen_en_otros(b, url: str, errores: list, fallos: list) -> None:
    for tema in ("vice", "caelestia"):
        pg = abrir(b, url, tema, 1440, 900, errores)
        ir_a_credits(pg)
        if se_ve(pg, "[data-cimientos]"):
            fallos.append(f"[{tema}] gate 2: [data-cimientos] esta VISIBLE y no deberia")
        if tema == "caelestia":
            piezas = pg.evaluate("() => document.querySelectorAll('.cae-cred-pieza').length")
            if piezas != 23:
                fallos.append(f"[caelestia] gate 2: la bandeja tiene {piezas} piezas, esperadas 23")
        pg.context().close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:4173")
    ap.add_argument("--contraste", action="store_true", help="gate 10 (hallazgo de producto abierto)")
    args = ap.parse_args()

    fallos: list[str] = []
    errores: list[str] = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])

        for nombre, w, h in VIEWPORTS:
            pg = abrir(b, args.url, "hyprland", w, h, errores)
            if not ir_a_credits(pg):
                fallos.append(f"[{nombre}] no existe [data-scene=credits]")
                pg.context().close()
                continue
            gate_1_se_ven(pg, nombre, fallos)
            pg.context().close()

        gate_2_no_existen_en_otros(b, args.url, errores, fallos)
        b.close()

    for e in errores:
        fallos.append(f"gate 13: consola: {e}")

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 2: Servir el build actual (sin cimientos) y ver el gate 1 en rojo**

```bash
cd /home/aoshi/proyectos/portfolio-aoshi-hypr
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && ss -ltnp | grep 4213 || (npx vite preview --port 4213 --strictPort >/tmp/cim-preview.log 2>&1 &)
sleep 3
python3 scripts/measure-cimientos.py --url http://localhost:4213
```

Esperado: `FALLO: [escritorio] gate 1: [data-cimientos] NO se ve en Hyprland`, lo mismo en
movil, y `gate 1: el generico .credits-grid SE PINTA bajo Hyprland` en los dos; gate 2 y 13 sin
fallos. `4 fallo(s)`. Pegar la salida literal en el informe de la tarea.

- [x] **Step 3: El spec pasa a `en ejecucion` y commit**

En `docs/superpowers/specs/2026-09-09-hyprland-stack-cimientos-design.md`, la linea `Estado:
pendiente de plan` pasa a `Estado: en ejecucion` (vocabulario cerrado de `verify.py`).

```bash
git add scripts/measure-cimientos.py docs/superpowers/specs/2026-09-09-hyprland-stack-cimientos-design.md
git commit -m "test(credits): arnes de los cimientos, gates 1, 2 y 13, en rojo contra el catastro"
```

---

### Task 2: El modulo, el montaje y la maquetacion en reposo (gates 7, 8, 9 y 12)

**Files:**
- Create: `src/components/hyprStackCimientos.ts`
- Modify: `src/main.ts:172-178` (nueva puerta), `src/main.ts:335` (`pagehide`)
- Modify: `src/style.css:1404-1408` (base)
- Modify: `src/themes/themes.css` (nuevo bloque tras la linea 8574, delante de `Hyprland: el catastro`)
- Modify: `scripts/measure-cimientos.py`

**Interfaces:**
- Produces: `mountHyprStackCimientos(root: HTMLElement): HyprStackCimientosHandle` con
  `destroy(): void`. DOM: `div.cim[data-cimientos]` > `div.cim-cols` (3 x `section.cim-col`) +
  `div.cim-suelo` (`span.cim-linea`, `div.cim-cab` con `h3.cim-rot` y `p.cim-frase`,
  `ul.cim-lenguajes`). Cada tecnologia es `button.cim-nombre[type=button][aria-pressed]
  [data-cim-nombre]` con `span.cim-icono` y `span.cim-txt`. Clases de estado que ponen las tareas
  4 y 5: `cimientos-lit` sobre `.cim`, `is-viva` sobre `.cim-cab`.

- [x] **Step 1: Anadir al arnes los gates 7, 8, 9 y 12 y verlos en rojo (no existe el nodo)**

Anadir a `scripts/measure-cimientos.py`, antes de `main()`:

```python
ESCALA = [12, 16, 21.33, 28.43, 37.9, 50.52, 67.4, 89.85, 119.77, 159.66]
DIANA_MINIMA = 44

GEOMETRIA_JS = """() => {
  const cim = document.querySelector('[data-cimientos]');
  if (!cim) return null;
  const r = e => { const b = e.getBoundingClientRect(); return {l: b.left, t: b.top, r: b.right, b: b.bottom, w: b.width, h: b.height}; };
  const visible = e => { const s = getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden' && e.getClientRects().length > 0; };
  const caja = r(cim);
  const cols = Array.from(cim.querySelectorAll('.cim-col')).map(r);
  const suelo = r(cim.querySelector('.cim-linea'));
  const fuera = Array.from(cim.querySelectorAll('.cim-txt, .cim-rot, .cim-frase, .cim-icono'))
    .filter(visible)
    .map(e => ({ t: e.textContent.trim().slice(0, 24), ...r(e) }))
    .filter(x => x.l < caja.l - 1 || x.r > caja.r + 1 || x.t < caja.t - 1 || x.b > caja.b + 1);
  const tallas = Array.from(cim.querySelectorAll('*'))
    .filter(e => e.childElementCount === 0 && e.textContent.trim() && visible(e))
    .map(e => ({ t: e.textContent.trim().slice(0, 24), s: parseFloat(getComputedStyle(e).fontSize) }));
  const dianas = Array.from(cim.querySelectorAll('.cim-nombre')).filter(visible).map(e => r(e).h);
  return { caja, cols, suelo, fuera, tallas, dianas };
}"""


def gate_7_8_9_12_geometria(pg, nombre: str, w: int, fallos: list) -> None:
    """7: nada desborda la caja de [data-cimientos], medido con rects, nunca
    con scrollWidth/scrollHeight (mienten con un transform dentro de un
    overflow: clip, pagado en B6). 8: las columnas nacen a la misma cota y el
    suelo esta a 48px del pie de la mas alta (solo en escritorio). 9: tallas
    en la escala. 12: diana tactil >= 44px en movil, solo sobre visibles."""
    g = pg.evaluate(GEOMETRIA_JS)
    if g is None:
        fallos.append(f"[{nombre}] gates 7-12: no existe [data-cimientos]")
        return
    for x in g["fuera"]:
        fallos.append(f"[{nombre}] gate 7: '{x['t']}' desborda la caja de los cimientos")
    if w >= 821:
        if len(g["cols"]) != 3:
            fallos.append(f"[{nombre}] gate 8: {len(g['cols'])} columnas, esperadas 3")
        else:
            tops = {round(c["t"]) for c in g["cols"]}
            if len(tops) != 1:
                fallos.append(f"[{nombre}] gate 8: las columnas no nacen a la misma cota: {sorted(tops)}")
            pie = max(c["b"] for c in g["cols"])
            aire = g["suelo"]["t"] - pie
            if abs(aire - 48) > 1:
                fallos.append(f"[{nombre}] gate 8: el suelo esta a {aire:.1f}px del pie de las columnas, esperados 48")
    for t in g["tallas"]:
        if not any(abs(t["s"] - paso) < 0.06 for paso in ESCALA):
            fallos.append(f"[{nombre}] gate 9: '{t['t']}' a {t['s']}px, fuera de la escala")
    if w < 821:
        if not g["dianas"]:
            fallos.append(f"[{nombre}] gate 12: ningun nombre visible que medir")
        elif min(g["dianas"]) < DIANA_MINIMA:
            fallos.append(f"[{nombre}] gate 12: diana tactil minima {min(g['dianas']):.1f}px, piso {DIANA_MINIMA}")


def gate_7_anchos(b, url: str, errores: list, fallos: list) -> None:
    """El desborde se mide en los cinco anchos del spec, no solo en los dos
    viewports principales: el hueco 1200-1439 del cartel se pago por no
    ejercitar el tramo intermedio."""
    for w in ANCHOS_DESBORDE:
        pg = abrir(b, url, "hyprland", w, 900, errores)
        if ir_a_credits(pg):
            g = pg.evaluate(GEOMETRIA_JS)
            if g is None:
                fallos.append(f"[{w}px] gate 7: no existe [data-cimientos]")
            else:
                for x in g["fuera"]:
                    fallos.append(f"[{w}px] gate 7: '{x['t']}' desborda la caja de los cimientos")
        pg.context().close()
```

Y en `main()`, dentro del bucle de `VIEWPORTS`, tras `gate_1_se_ven(...)`:

```python
            gate_7_8_9_12_geometria(pg, nombre, w, fallos)
```

y tras `gate_2_no_existen_en_otros(...)`:

```python
        gate_7_anchos(b, args.url, errores, fallos)
```

Correr contra el build servido de la Task 1. Esperado: los `gates 7-12: no existe
[data-cimientos]` en escritorio y movil y `gate 7: no existe` en los cinco anchos, ademas de los
cuatro de la Task 1. Pegar la salida.

- [x] **Step 2: Crear el modulo**

`src/components/hyprStackCimientos.ts`:

```ts
import { skillGroups } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { getIconMarkup } from "../utils/icons";

export interface HyprStackCimientosHandle {
  destroy: () => void;
}

/**
 * Los cimientos (spec 2026-09-09-hyprland-stack-cimientos): tres areas en
 * columnas sobre un suelo de brasa con los cinco lenguajes base. DOM propio
 * montado como hermano de `.credits` dentro de `[data-scene="credits"]`; el
 * generico se oculta entero desde themes.css (patron B3/B4 de Caelestia).
 *
 * Sin GSAP: el disparo de la entrada es un IntersectionObserver anclado a la
 * caja del PROPIO dispositivo (top 80%), no a la seccion — con `is-lit` de
 * la seccion a `top 90%` la placa de "Quien soy" corria su montaje entero
 * 119px bajo el pliegue y nadie lo vio nunca (fallo 1 del repaso). Los
 * tiempos los marca el CSS.
 */
const ROTULO_SUELO = "Lenguajes base";

function construirNombre(name: string, slug: string, detail: string): HTMLButtonElement {
  const icono = elFromMarkup("cim-icono", getIconMarkup(slug));
  icono.setAttribute("aria-hidden", "true");
  icono.setAttribute("data-decorative", "");
  const boton = el("button", "cim-nombre", [icono, el("span", "cim-txt", [name])]);
  boton.type = "button";
  boton.setAttribute("aria-pressed", "false");
  boton.dataset.cimNombre = name;
  boton.dataset.cimDetail = detail;
  return boton;
}

function construirLista(clase: string, items: ReadonlyArray<{ name: string; slug: string; detail: string }>): HTMLUListElement {
  return el(
    "ul",
    clase,
    items.map((it) => el("li", "", [construirNombre(it.name, it.slug, it.detail)])),
  );
}

export function mountHyprStackCimientos(root: HTMLElement): HyprStackCimientosHandle {
  const escena = root.querySelector<HTMLElement>('[data-scene="credits"]');
  if (!escena) return { destroy: () => undefined };

  const suelo = skillGroups.find((g) => g.label === ROTULO_SUELO);
  const areas = skillGroups.filter((g) => g.label !== ROTULO_SUELO);
  if (!suelo || areas.length !== 3) return { destroy: () => undefined };

  const columnas = areas.map((g, i) => {
    const col = el("section", "cim-col", [
      el("h3", "cim-rot", [g.label]),
      construirLista("cim-lista", g.items),
    ]);
    col.style.setProperty("--cim-c", String(i));
    return col;
  });

  const linea = el("span", "cim-linea", []);
  linea.setAttribute("aria-hidden", "true");
  const frase = el("p", "cim-frase", []);
  frase.setAttribute("aria-live", "polite");
  const cab = el("div", "cim-cab", [el("h3", "cim-rot", [suelo.label]), frase]);
  const lenguajes = construirLista("cim-lenguajes", suelo.items);

  const cim = el("div", "cim", [
    el("div", "cim-cols", columnas),
    el("div", "cim-suelo", [linea, cab, lenguajes]),
  ]);
  cim.setAttribute("data-cimientos", "");
  escena.append(cim);

  return {
    destroy: () => {
      cim.remove();
    },
  };
}
```

- [x] **Step 3: La puerta de montaje en `main.ts` y el `destroy()` en `pagehide`**

Tras el bloque del cartel (`src/main.ts:172-178`):

```ts
// Los cimientos de Stack en Hyprland: tres areas sobre un suelo de lenguajes
// base. Import diferido, igual que el resto de modulos de tema.
let cimientosHandle: { destroy: () => void } | null = null;
if (theme.id === "hyprland") {
  void import("./components/hyprStackCimientos").then(({ mountHyprStackCimientos }) => {
    cimientosHandle = mountHyprStackCimientos(app);
  });
}
```

Y en el `pagehide` (`src/main.ts:335`), tras `cartelHandle?.destroy();`:

```ts
    cimientosHandle?.destroy();
```

- [x] **Step 4: El `display: none` de base y la ocultacion del generico**

En `src/style.css`, junto a `.credits-parcela, .credits-strip { display: none; }` (~linea 1404):

```css
/*
 * Los cimientos de Hyprland. Nacen apagados para los tres temas y solo
 * `:root[data-theme="hyprland"]` los enciende. Mismo motivo que las parcelas
 * de arriba: el patron aditivo se ha roto cuatro veces por saltarse esto.
 */
[data-cimientos] {
  display: none;
}
```

En `src/themes/themes.css`, justo antes de `/* ---- Hyprland: el catastro */` (linea 8575):

```css
/* ------------------------------------------------ Hyprland: los cimientos */
/*
  LOS CIMIENTOS — spec docs/superpowers/specs/2026-09-09-hyprland-stack-cimientos-design.md.
  Dos estratos dentro del margen: tres areas en columnas proporcionales (8/5/5)
  y, debajo, la linea del suelo con los cinco lenguajes base. Sin perimetro,
  sin tapa ni suelo cerrado: el gate del catastro dictamino que su envase era
  identico al de la placa.

  El DOM generico de credits.ts (`.credits-grid`) se oculta ENTERO: el
  catastro construia sus nodos ahi y este dispositivo tiene los suyos
  (`hyprStackCimientos.ts`). credits.ts no se toca en esta fase.
*/
:root[data-theme="hyprland"] .credits-grid {
  display: none;
}

:root[data-theme="hyprland"] [data-cimientos] {
  display: block;
  width: 100%;
  max-width: 1296px;
  margin: 40px auto 0;
  color: var(--text);
}

:root[data-theme="hyprland"] .cim-cols {
  display: grid;
  grid-template-columns: minmax(240px, 8fr) minmax(240px, 5fr) minmax(240px, 5fr);
  align-items: start;
}

:root[data-theme="hyprland"] .cim-col {
  padding: 0 32px;
}
:root[data-theme="hyprland"] .cim-col:first-child {
  padding-left: 0;
}
:root[data-theme="hyprland"] .cim-col + .cim-col {
  border-left: 1px solid var(--rule);
}

:root[data-theme="hyprland"] .cim-rot {
  margin: 0;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: var(--t-1);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--haze);
  line-height: 15px;
}

:root[data-theme="hyprland"] .cim-lista,
:root[data-theme="hyprland"] .cim-lenguajes {
  list-style: none;
  margin: 0;
  padding: 0;
}
:root[data-theme="hyprland"] .cim-lista {
  margin-top: 24px;
  display: grid;
  row-gap: 8px;
}

:root[data-theme="hyprland"] .cim-nombre {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  padding: 0;
  border: 0;
  background: none;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  /* Caja de 34px: nombre a --t-4 con line-height 1.2 */
  min-height: 34px;
}
:root[data-theme="hyprland"] .cim-nombre:focus-visible {
  outline: 2px solid var(--l1);
  outline-offset: -2px;
}

:root[data-theme="hyprland"] .cim-icono {
  width: 20px;
  height: 20px;
  flex: 0 0 20px;
  color: var(--haze);
}
:root[data-theme="hyprland"] .cim-icono svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
}

:root[data-theme="hyprland"] .cim-txt {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--t-4);
  line-height: 1.2;
  letter-spacing: var(--display-tracking);
  color: var(--text);
}

/* El suelo */
:root[data-theme="hyprland"] .cim-suelo {
  margin-top: 48px;
}
:root[data-theme="hyprland"] .cim-linea {
  display: block;
  height: 2px;
  background: var(--l1);
}
:root[data-theme="hyprland"] .cim-cab {
  display: flex;
  align-items: baseline;
  gap: 24px;
  margin-top: 22px;
  /* La linea del rotulo tiene la altura de la frase desde el principio:
     nada se mueve al rozar. */
  min-height: 28px;
}
:root[data-theme="hyprland"] .cim-frase {
  margin: 0;
  font-family: var(--font-said);
  font-style: italic;
  font-weight: 400;
  font-size: var(--t-3);
  line-height: 28px;
  color: var(--catch);
}
:root[data-theme="hyprland"] .cim-lenguajes {
  display: flex;
  flex-wrap: wrap;
  column-gap: 0.55em;
  row-gap: 8px;
  margin-top: 8px;
  font-size: var(--t-5);
}
:root[data-theme="hyprland"] .cim-lenguajes .cim-nombre {
  min-height: 45px;
}
:root[data-theme="hyprland"] .cim-lenguajes .cim-txt {
  font-size: var(--t-5);
}

/* Movil y tableta vertical: las columnas se apilan como filas. */
@media (max-width: 820px) {
  :root[data-theme="hyprland"] [data-cimientos] {
    margin-top: 24px;
  }
  :root[data-theme="hyprland"] .cim-cols {
    grid-template-columns: 1fr;
  }
  :root[data-theme="hyprland"] .cim-col {
    padding: 0;
  }
  :root[data-theme="hyprland"] .cim-col + .cim-col {
    border-left: 0;
    border-top: 1px solid var(--rule);
    margin-top: 16px;
    padding-top: 16px;
  }
  :root[data-theme="hyprland"] .cim-lista {
    grid-template-columns: 1fr 1fr;
    column-gap: 16px;
    row-gap: 0;
    margin-top: 16px;
  }
  :root[data-theme="hyprland"] .cim-nombre {
    min-height: 44px; /* diana tactil: 34 de caja + 5 y 5 */
    gap: 8px;
  }
  :root[data-theme="hyprland"] .cim-icono {
    width: 16px;
    height: 16px;
    flex-basis: 16px;
  }
  :root[data-theme="hyprland"] .cim-txt,
  :root[data-theme="hyprland"] .cim-lenguajes .cim-txt {
    font-size: var(--t-3);
  }
  :root[data-theme="hyprland"] .cim-cab {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    min-height: 0;
  }
  :root[data-theme="hyprland"] .cim-frase {
    font-size: var(--t-2);
    line-height: 24px;
    min-height: 48px; /* dos lineas fijas: al tocar nada se mueve (aceptado por Aoshi) */
  }
  :root[data-theme="hyprland"] .cim-lenguajes .cim-nombre {
    min-height: 44px;
  }
}
```

- [x] **Step 5: Build, lint, y el arnes en verde en los gates 1, 7, 8, 9 y 12**

```bash
npm run build && npm run lint
# reiniciar el preview: matar por PID el que escucha en 4213 (ss -ltnp | grep 4213), relanzar
python3 scripts/measure-cimientos.py --url http://localhost:4213
```

Esperado: `0 fallo(s)`. Si el gate 8 da un aire distinto de 48 o el 9 una talla fuera, se ajusta
el CSS (no el gate) hasta que el numero coincida con el spec. Si alguna talla del `h2.hero-kick`
compartido entra en la medida, esta fuera de `[data-cimientos]` y no cuenta.

- [x] **Step 6: Captura de reposo en los dos anchos y en Vice, con oyente**

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for tema, w, h in [('hyprland',1440,900),('hyprland',390,844),('vice',1440,900)]:
        pg = b.new_page(viewport={'width':w,'height':h}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.goto(f'http://localhost:4213/?theme={tema}', wait_until='domcontentloaded'); pg.wait_for_timeout(9000)
        top = pg.evaluate("document.querySelector('[data-scene=\"credits\"]').getBoundingClientRect().top + scrollY")
        pg.evaluate(f"window.scrollTo(0,{top})"); pg.wait_for_timeout(3000)
        pg.screenshot(path=f'/tmp/cim-t2-{tema}-{w}.png'); print(tema, w, 'consola:', errs or 'limpia'); pg.close()
    b.close()
EOF
```

Mirar las tres capturas. En Vice tiene que seguir el rodillo de creditos de siempre.

- [x] **Step 7: Commit**

```bash
git add src/components/hyprStackCimientos.ts src/main.ts src/style.css src/themes/themes.css scripts/measure-cimientos.py
git commit -m "feat(credits): los cimientos en reposo, modulo propio y generico oculto bajo Hyprland"
```

---

### Task 3: Retirar el catastro (gestos 4 y 5, CSS, arnes, marcador de verify.py)

**Files:**
- Modify: `src/themes/hypr.choreography.ts:1-27, 77-89, 266-539`
- Modify: `src/themes/themes.css:8575-9371`
- Delete: `scripts/measure-catastro.py`
- Modify: `scripts/verify.py:1266-1303`

**Interfaces:**
- Consumes: el DOM de la Task 2 (`[data-cimientos]`, `.credits-grid` oculto).
- Produces: `hyprChoreography` sin gestos 4 y 5; `verify.py` con el marcador nuevo de Hyprland.

- [x] **Step 1: Retirar los gestos 4 y 5 de la coreografia**

En `src/themes/hypr.choreography.ts`:
1. Borrar desde el comentario `// Gesto 4 — la corriente.` (linea 266) hasta el cierre del
   `if (parcelas.length > 0) { ... }` que termina justo antes del `};` final del modulo (linea
   539). El fichero queda cerrado con `};` tras el gesto 3.
2. Borrar la sonda: el tipo `HyprTimerWindow` (linea 26), el bloque de limpieza de
   `__hyprSkillTimers` / `is-caught` / `__hyprSkills` (lineas 82-89) y los comentarios de cabecera
   que la describen (lineas 13-27 y 40-50, los que hablan de `__hyprSkills`). Conservar la
   limpieza de `placa-lit` anadida en el fallo 1.
3. Borrar el import `STRIP_REPAINT_EVENT, type StripRepaintDetail` (linea 1) y, si `npm run lint`
   marca sin uso `Gsap`, `HARD` o `SLOW`, borrarlos tambien. **`gsap` sigue desestructurado del
   contexto** aunque ya no se use en ningun tween: si `eslint` lo marca como no usado, dejarlo con
   `_gsap` NO — quitarlo del destructuring y anotar en el comentario de cabecera que la
   coreografia de Hyprland ya no crea tweens; si en el futuro los crea, vuelve a desestructurarse
   (nunca un `gsap` suelto: el `gsap is not defined` de este tema se pago semanas).

- [x] **Step 2: Retirar el bloque CSS del catastro**

En `src/themes/themes.css` borrar desde `/* ---- Hyprland: el catastro */` (linea 8575, ya
desplazada por el bloque nuevo de la Task 2: buscar el comentario, no el numero) hasta la linea
anterior a `/* ---- Hyprland: las bandas */`. Incluye `Hyprland: contenido de la franja` y el
`@media (max-width: 820px)` del catastro. Comprobar con `grep -n "credits-parcela\|credit-group-toggle\|credits-strip\|hypr-lampara" src/themes/themes.css`: cero resultados bajo Hyprland (los de `style.css` base se quedan).

- [x] **Step 3: Borrar el arnes del catastro y cambiar el marcador de `verify.py`**

```bash
git rm scripts/measure-catastro.py
```

En `scripts/verify.py`, sustituir las tres comprobaciones `catastro` del bloque
`if theme == "hyprland":` (desde el comentario `# El catastro (2026-08-10)` hasta el `check(...)`
de `roleDisplay`) por:

```python
        # Los cimientos (2026-09-09): el generico `.credits-grid` no se pinta
        # bajo Hyprland y el dispositivo propio `[data-cimientos]` si. Si
        # alguien reintroduce el catastro (rejilla sobre `.credits-list`) o
        # el generico vuelve a asomar por debajo de los cimientos, esto salta.
        cimientos = page.evaluate("""(() => {
          const grid = document.querySelector('.credits-grid');
          const cim = document.querySelector('[data-cimientos]');
          const ve = n => { if (!n) return false; const s = getComputedStyle(n);
            const r = n.getBoundingClientRect();
            return s.display !== 'none' && r.width > 0 && r.height > 0; };
          return { gridVisible: ve(grid), cimVisible: ve(cim),
                   nombres: document.querySelectorAll('[data-cimientos] .cim-nombre').length };
        })()""")
        check(
            cimientos is not None and not cimientos["gridVisible"],
            f"hyprland: el generico .credits-grid no se pinta bajo los cimientos "
            f"(gridVisible={cimientos['gridVisible'] if cimientos else None})",
        )
        check(
            cimientos is not None and cimientos["cimVisible"] and cimientos["nombres"] == 23,
            f"hyprland: [data-cimientos] se pinta con sus 23 nombres "
            f"(cimVisible={cimientos['cimVisible'] if cimientos else None}, "
            f"nombres={cimientos['nombres'] if cimientos else None})",
        )
```

Actualizar el docstring de esa funcion (parrafo *"Hyprland: el catastro (2026-08-10)..."*) con
una frase: *"Hyprland: los cimientos (2026-09-09). El generico se oculta entero y el dispositivo
propio `[data-cimientos]` lo sustituye."*

- [x] **Step 4: Build, lint, arnes, verify.py**

```bash
npm run build && npm run lint
# reiniciar preview por PID
python3 scripts/measure-cimientos.py --url http://localhost:4213
python3 scripts/verify.py --url http://localhost:4213
```

Esperado: cimientos `0 fallo(s)`; `verify.py` *"TODO OK — 12 fallos conocidos, 0 nuevos"* y
codigo 0. Si `verify.py` marca un fallo nuevo en Vice o Caelestia, la Task 2 o esta han tocado
algo compartido: parar y mirar el diff de `themes.css` fuera del bloque de Hyprland.

- [x] **Step 5: Vice y Caelestia identicos a `main`**

```bash
git worktree add /tmp/cim-main main
# servir /tmp/cim-main/dist en 4214 tras `npm run build` alli (enlazar node_modules), y comparar:
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
import hashlib
def foto(url, tema):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
        pg = b.new_page(viewport={'width':1440,'height':900}, reduced_motion='reduce')
        pg.route("**/*.webp", lambda r: r.abort())
        pg.goto(f'{url}/?theme={tema}', wait_until='domcontentloaded'); pg.wait_for_timeout(6000)
        top = pg.evaluate("document.querySelector('[data-scene=\"credits\"]').getBoundingClientRect().top + scrollY")
        pg.evaluate(f"window.scrollTo(0,{top})"); pg.wait_for_timeout(2500)
        html = pg.evaluate("document.querySelector('[data-scene=\"credits\"]').outerHTML")
        b.close(); return hashlib.sha1(html.encode()).hexdigest()
for tema in ('vice','caelestia'):
    print(tema, foto('http://localhost:4213', tema) == foto('http://localhost:4214', tema))
EOF
git worktree remove /tmp/cim-main
```

Esperado: `vice True`, `caelestia True`. (El DOM de la escena bajo Vice y Caelestia no lleva
`[data-cimientos]` porque el modulo solo monta bajo Hyprland; si sale `False`, mirar que ha
cambiado en el `outerHTML` antes de seguir.)

- [x] **Step 6: Commit**

```bash
git add -A src/themes/hypr.choreography.ts src/themes/themes.css scripts/measure-catastro.py scripts/verify.py
git commit -m "refactor(credits): retira el catastro de Hyprland: gestos 4 y 5, CSS, arnes y marcador"
```

---

### Task 4: La entrada — el suelo se enciende primero (gate 3)

**Files:**
- Modify: `src/components/hyprStackCimientos.ts`
- Modify: `src/themes/themes.css` (bloque `LOS CIMIENTOS`)
- Modify: `scripts/measure-cimientos.py`

**Interfaces:**
- Produces: clase `cimientos-lit` sobre `[data-cimientos]`; variable `--cim-d` (ms) inline en cada
  `.cim-lenguajes .cim-nombre`; `--cim-c` (indice) en cada `.cim-col` (ya puesta en la Task 2).

- [x] **Step 1: Gate 3 en el arnes, y verlo en rojo (hoy todo se pinta al montar)**

```python
ENTRADA_JS = """() => {
  const cim = document.querySelector('[data-cimientos]');
  if (!cim) return null;
  const linea = cim.querySelector('.cim-linea');
  const cols = Array.from(cim.querySelectorAll('.cim-col'));
  const lens = Array.from(cim.querySelectorAll('.cim-lenguajes .cim-txt'));
  const tf = getComputedStyle(linea).transform;
  return {
    top: cim.getBoundingClientRect().top, innerH: innerHeight,
    lit: cim.classList.contains('cimientos-lit'),
    lineaTrazada: tf === 'none' || /matrix\\(1,/.test(tf),
    colsAbiertas: cols.filter(c => { const cp = getComputedStyle(c).clipPath; return cp === 'none' || cp === 'inset(0px)' || cp === 'inset(0px 0px 0px 0px)'; }).length,
    lensEncendidos: lens.filter(t => getComputedStyle(t).color === 'rgb(255, 234, 230)').length,
  };
}"""


def gate_3_la_entrada_se_ve(b, url: str, errores: list, fallos: list) -> None:
    """Paso A: seccion encendida (is-lit) y los cimientos ENTEROS bajo el
    pliegue; tras 1500ms nada ha arrancado. Paso B: los cimientos al 80% y
    tras 2000ms todo aterrizo. Anclado a ESTADO (con setTimeout el gate 13
    de B5 salia rojo bajo carga y verde en vacio). Si el paso A no puede
    colocar los cimientos bajo el pliegue, el arnes FALLA en vez de medir
    otra cosa."""
    for nombre, w, h in VIEWPORTS:
        pg = abrir(b, url, "hyprland", w, h, errores)
        top = pg.evaluate(
            "() => { const c = document.querySelector('[data-cimientos]');"
            " return c ? c.getBoundingClientRect().top + window.scrollY : -1; }"
        )
        if top < 0:
            fallos.append(f"[{nombre}] gate 3: no existe [data-cimientos]")
            pg.context().close()
            continue
        # A: la seccion pasa el 90% (is-lit) pero los cimientos quedan enteros bajo el pliegue
        seccion_top = pg.evaluate(
            "() => document.querySelector('[data-scene=\"credits\"]').getBoundingClientRect().top + window.scrollY"
        )
        pg.evaluate(f"window.scrollTo(0, {seccion_top - h * 0.9 + 20})")
        pg.wait_for_timeout(1500)
        a = pg.evaluate(ENTRADA_JS)
        if a["top"] < a["innerH"]:
            fallos.append(f"[{nombre}] gate 3: el arnes no pudo dejar los cimientos bajo el pliegue (top {a['top']:.0f} < {a['innerH']})")
        elif a["lit"] or a["lineaTrazada"] or a["colsAbiertas"] > 0 or a["lensEncendidos"] > 0:
            fallos.append(
                f"[{nombre}] gate 3 paso A: la entrada arranco con los cimientos bajo el pliegue "
                f"(lit={a['lit']}, linea={a['lineaTrazada']}, cols={a['colsAbiertas']}, lenguajes={a['lensEncendidos']})"
            )
        # B: los cimientos al 80%
        pg.evaluate(f"window.scrollTo(0, {top - h * 0.8 + 40})")
        pg.wait_for_timeout(2500)
        bst = pg.evaluate(ENTRADA_JS)
        if not (bst["lit"] and bst["lineaTrazada"] and bst["colsAbiertas"] == 3 and bst["lensEncendidos"] == 5):
            fallos.append(
                f"[{nombre}] gate 3 paso B: la entrada no aterrizo "
                f"(lit={bst['lit']}, linea={bst['lineaTrazada']}, cols={bst['colsAbiertas']}/3, lenguajes={bst['lensEncendidos']}/5)"
            )
        pg.context().close()
```

Registrar en `main()` tras `gate_7_anchos(...)`: `gate_3_la_entrada_se_ve(b, args.url, errores, fallos)`.

Correr contra el build de la Task 3. Esperado: `gate 3 paso A: la entrada arranco...` con
`linea=True, cols=3, lenguajes=5` en los dos anchos (todo se pinta ya al montar: es el sabotaje
natural). Pegar la salida.

- [x] **Step 2: Los estados de entrada en CSS**

Anadir al bloque `LOS CIMIENTOS` de `themes.css`, antes del `@media (max-width: 820px)`:

```css
/*
  ENTRADA — el suelo se enciende primero. La linea se traza (500ms corte);
  cada lenguaje se enciende cuando la linea llega a su columna (`--cim-d`,
  que escribe hyprStackCimientos.ts a partir de su x real); despues las
  columnas crecen del suelo por recorte (900ms atmosfera, 90ms por columna).
  Nada por opacidad. El disparo (`cimientos-lit`) lo pone el modulo con un
  IntersectionObserver anclado a la caja de los cimientos, no a la seccion.
*/
:root[data-theme="hyprland"] .cim-linea {
  transform: scaleX(0);
  transform-origin: left center;
}
:root[data-theme="hyprland"] .cimientos-lit .cim-linea {
  transform: scaleX(1);
  transition: transform 0.5s var(--hard);
}
:root[data-theme="hyprland"] .cim-lenguajes .cim-txt,
:root[data-theme="hyprland"] .cim-lenguajes .cim-icono {
  color: var(--rule);
}
:root[data-theme="hyprland"] .cimientos-lit .cim-lenguajes .cim-txt {
  color: var(--text);
  transition: color 0.42s var(--hard) var(--cim-d, 0ms);
}
:root[data-theme="hyprland"] .cimientos-lit .cim-lenguajes .cim-icono {
  color: var(--haze);
  transition: color 0.42s var(--hard) var(--cim-d, 0ms);
}
:root[data-theme="hyprland"] .cim-col {
  clip-path: inset(100% 0 0 0);
}
:root[data-theme="hyprland"] .cimientos-lit .cim-col {
  clip-path: inset(0 0 0 0);
  transition: clip-path 0.9s var(--slow) calc(520ms + var(--cim-c, 0) * 90ms);
}
```

- [x] **Step 3: El disparo en el modulo**

En `mountHyprStackCimientos`, tras `escena.append(cim);` y antes del `return`:

```ts
  // El retardo de cada lenguaje sale de SU x real sobre el ancho del suelo:
  // la linea tarda 500ms en cruzar, y el nombre se enciende cuando la linea
  // llega a su columna. Se mide tras el append, con layout ya disponible.
  const anchoSuelo = lenguajes.getBoundingClientRect().width || 1;
  const izq = lenguajes.getBoundingClientRect().left;
  for (const boton of Array.from(lenguajes.querySelectorAll<HTMLElement>(".cim-nombre"))) {
    const x = boton.getBoundingClientRect().left - izq;
    boton.style.setProperty("--cim-d", `${Math.round((x / anchoSuelo) * 500)}ms`);
  }

  // Disparo anclado a la caja de los cimientos: top al 80% de la ventana.
  // `rootMargin` negativo abajo recorta el 20% inferior del viewport, asi que
  // "intersecta" equivale a "el borde superior ha cruzado el 80%". Con
  // movimiento reducido no hay entrada: el estado final se pone al montar.
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let observador: IntersectionObserver | null = null;
  if (reduce) {
    cim.classList.add("cimientos-lit");
  } else {
    observador = new IntersectionObserver(
      (entradas) => {
        if (entradas.some((e) => e.isIntersecting)) {
          cim.classList.add("cimientos-lit");
          observador?.disconnect();
          observador = null;
        }
      },
      { rootMargin: "0px 0px -20% 0px", threshold: 0 },
    );
    observador.observe(cim);
  }
```

Y en `destroy`:

```ts
    destroy: () => {
      observador?.disconnect();
      cim.remove();
    },
```

- [x] **Step 4: Build, lint, arnes en verde, captura a media entrada**

```bash
npm run build && npm run lint
# reiniciar preview por PID
python3 scripts/measure-cimientos.py --url http://localhost:4213
```

Esperado `0 fallo(s)`. Captura a media entrada, leyendo el estado en el mismo `evaluate` (el
cronometro miente bajo swiftshader; se busca el fotograma por estado):

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4213/?theme=hyprland', wait_until='domcontentloaded'); pg.wait_for_timeout(9000)
    top = pg.evaluate("document.querySelector('[data-cimientos]').getBoundingClientRect().top + scrollY")
    pg.evaluate(f"window.scrollTo(0,{top-680})")
    # sondeo dentro de la pagina: linea trazada y aun ninguna columna abierta
    pg.evaluate("""async () => { const c=document.querySelector('[data-cimientos]'); const dl=performance.now()+4000;
      while (performance.now()<dl) { const tf=getComputedStyle(c.querySelector('.cim-linea')).transform;
        const abiertas=[...c.querySelectorAll('.cim-col')].filter(x=>getComputedStyle(x).clipPath==='inset(0px)').length;
        if (c.classList.contains('cimientos-lit') && abiertas===0 && tf!=='matrix(0, 0, 0, 1, 0, 0)') return; await new Promise(r=>setTimeout(r,10)); } }""")
    pg.screenshot(path='/tmp/cim-t4-mitad.png'); b.close()
EOF
```

Mirar `/tmp/cim-t4-mitad.png`: el suelo trazado o trazandose, lenguajes encendiendose, columnas
aun recortadas (o apenas asomando).

- [x] **Step 5: Commit**

```bash
git add src/components/hyprStackCimientos.ts src/themes/themes.css scripts/measure-cimientos.py
git commit -m "feat(credits): la entrada de los cimientos, el suelo se enciende primero"
```

---

### Task 5: El apuntado — la frase al rozar (gates 4, 5 y 6)

**Files:**
- Modify: `src/components/hyprStackCimientos.ts`
- Modify: `src/themes/themes.css` (bloque `LOS CIMIENTOS`)
- Modify: `scripts/measure-cimientos.py`

**Interfaces:**
- Produces: `aria-pressed="true"` en el unico nombre apuntado; `is-viva` en `.cim-cab`; el texto de
  `.cim-frase` es el `detail` del nombre apuntado.

- [x] **Step 1: Gates 4, 5 y 6 en el arnes, y verlos en rojo (hoy rozar no hace nada)**

```python
L3 = "rgb(255, 160, 60)"


def gate_4_5_6_apuntado(b, url: str, errores: list, fallos: list) -> None:
    """4: ningun nombre en --l3 en reposo, y el apuntado se apaga al salir
    (el P0 del catastro: tras un barrido quedaban cuatro encendidos). Con
    hover() REAL: un MouseEvent sintetico no dispara :hover. 5: la frase no
    mueve nada: rects del suelo y de los lenguajes identicos al pixel antes
    y despues de rozar cinco nombres. 6: la frase es el `detail` literal y
    en reposo la linea esta vacia."""
    pg = abrir(b, url, "hyprland", 1440, 900, errores)
    if not ir_a_credits(pg):
        fallos.append("[escritorio] gate 4-6: no existe la escena")
        pg.context().close()
        return
    pg.wait_for_timeout(2500)  # entrada aterrizada
    RECTS = """() => Array.from(document.querySelectorAll('[data-cimientos] .cim-linea, [data-cimientos] .cim-lenguajes .cim-nombre, [data-cimientos] .cim-col'))
      .map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; })"""
    antes = pg.evaluate(RECTS)
    frase0 = pg.evaluate("() => document.querySelector('[data-cimientos] .cim-frase').textContent.trim()")
    if frase0 != "":
        fallos.append(f"[escritorio] gate 6: la frase no esta vacia en reposo: '{frase0}'")
    encendidos0 = pg.evaluate(
        "() => Array.from(document.querySelectorAll('[data-cimientos] .cim-txt')).filter(t => getComputedStyle(t).color === '%s').length" % L3
    )
    if encendidos0 != 0:
        fallos.append(f"[escritorio] gate 4: {encendidos0} nombres en --l3 en reposo")

    nombres = pg.query_selector_all("[data-cimientos] .cim-nombre")
    muestra = [nombres[i] for i in (0, 3, 9, 14, 20)]
    for n in muestra:
        n.hover()
        pg.wait_for_timeout(600)
        esperado = n.get_attribute("data-cim-detail")
        visto = pg.evaluate("() => document.querySelector('[data-cimientos] .cim-frase').textContent.trim()")
        if visto != esperado:
            fallos.append(f"[escritorio] gate 6: al rozar '{n.get_attribute('data-cim-nombre')}' la frase es '{visto}', esperada '{esperado}'")
        pressed = pg.evaluate("() => document.querySelectorAll('[data-cimientos] .cim-nombre[aria-pressed=\"true\"]').length")
        if pressed != 1:
            fallos.append(f"[escritorio] gate 4: {pressed} nombres con aria-pressed=true al rozar uno")
    despues = pg.evaluate(RECTS)
    if antes != despues:
        fallos.append("[escritorio] gate 5: rozar movio el suelo, las columnas o los lenguajes")

    pg.mouse.move(5, 5)
    pg.wait_for_timeout(1200)
    encendidos1 = pg.evaluate(
        "() => Array.from(document.querySelectorAll('[data-cimientos] .cim-txt')).filter(t => getComputedStyle(t).color === '%s').length" % L3
    )
    pressed1 = pg.evaluate("() => document.querySelectorAll('[data-cimientos] .cim-nombre[aria-pressed=\"true\"]').length")
    if encendidos1 != 0 or pressed1 != 0:
        fallos.append(f"[escritorio] gate 4: tras salir quedan {encendidos1} en --l3 y {pressed1} con aria-pressed")
    pg.context().close()

    # Movil: el toque abre, el segundo toque sobre el mismo cierra, y la altura no cambia.
    pg = abrir(b, url, "hyprland", 390, 844, errores)
    if ir_a_credits(pg):
        pg.wait_for_timeout(2500)
        alto0 = pg.evaluate("() => document.querySelector('[data-cimientos]').getBoundingClientRect().height")
        primero = pg.query_selector("[data-cimientos] .cim-nombre")
        primero.tap()
        pg.wait_for_timeout(600)
        visto = pg.evaluate("() => document.querySelector('[data-cimientos] .cim-frase').textContent.trim()")
        if visto != primero.get_attribute("data-cim-detail"):
            fallos.append(f"[movil] gate 6: al tocar, la frase es '{visto}'")
        alto1 = pg.evaluate("() => document.querySelector('[data-cimientos]').getBoundingClientRect().height")
        if round(alto0) != round(alto1):
            fallos.append(f"[movil] gate 5: tocar cambio la altura de los cimientos {alto0:.0f} -> {alto1:.0f}")
        primero.tap()
        pg.wait_for_timeout(600)
        pressed = pg.evaluate("() => document.querySelectorAll('[data-cimientos] .cim-nombre[aria-pressed=\"true\"]').length")
        if pressed != 0:
            fallos.append(f"[movil] gate 4: el segundo toque no apago el nombre ({pressed} con aria-pressed)")
    pg.context().close()
```

Para el movil, `abrir()` necesita contexto tactil: anadir el parametro `tactil: bool = False` a
`abrir()` y pasar `is_mobile=tactil, has_touch=tactil, device_scale_factor=2 if tactil else 1`
a `new_context`; en esta funcion, la segunda `abrir(...)` lleva `tactil=True`.

Registrar en `main()` tras el gate 3: `gate_4_5_6_apuntado(b, args.url, errores, fallos)`.
Correr contra el build de la Task 4. Esperado: `gate 6: al rozar 'React' la frase es ''...` (x5),
`gate 4: 0 nombres con aria-pressed=true al rozar uno` (x5), y en movil `gate 6: al tocar, la
frase es ''`. Pegar la salida.

- [x] **Step 2: El apuntado en el modulo**

En `mountHyprStackCimientos`, tras el bloque del observador:

```ts
  // El apuntado. Rozar (puntero) o dar foco escribe la frase; en tactil el
  // toque abre y el segundo toque sobre el mismo nombre cierra. `click` se
  // ignora cuando viene de raton: el hover ya lo ha hecho, y un toggle lo
  // cerraria. Un solo nombre encendido a la vez, y NUNCA se queda encendido
  // al salir: es el P0 del catastro.
  const botones = Array.from(cim.querySelectorAll<HTMLButtonElement>(".cim-nombre"));
  let activo: HTMLButtonElement | null = null;
  let ultimoPuntero = "mouse";

  const encender = (boton: HTMLButtonElement): void => {
    if (activo === boton) return;
    if (activo) activo.setAttribute("aria-pressed", "false");
    activo = boton;
    boton.setAttribute("aria-pressed", "true");
    frase.textContent = boton.dataset.cimDetail ?? "";
    cab.classList.add("is-viva");
  };
  const apagar = (): void => {
    if (!activo) return;
    activo.setAttribute("aria-pressed", "false");
    activo = null;
    cab.classList.remove("is-viva");
    // El texto se queda mientras la frase se retira por recorte y se vacia al
    // terminar la transicion. Con movimiento reducido no hay transicion ni
    // `transitionend`: se vacia en seco.
    if (reduce) frase.textContent = "";
  };
  const alTerminar = (ev: TransitionEvent): void => {
    if (ev.propertyName === "clip-path" && !cab.classList.contains("is-viva")) frase.textContent = "";
  };
  frase.addEventListener("transitionend", alTerminar);

  const escuchas: Array<() => void> = [];
  for (const boton of botones) {
    const entrar = (ev: PointerEvent): void => {
      if (ev.pointerType === "mouse") encender(boton);
    };
    const foco = (): void => encender(boton);
    const salir = (): void => apagar();
    const pulsar = (ev: PointerEvent): void => {
      ultimoPuntero = ev.pointerType;
    };
    const clic = (): void => {
      if (ultimoPuntero === "mouse") return;
      if (activo === boton) salir();
      else encender(boton);
    };
    boton.addEventListener("pointerenter", entrar);
    boton.addEventListener("pointerleave", salir);
    boton.addEventListener("focus", foco);
    boton.addEventListener("blur", salir);
    boton.addEventListener("pointerdown", pulsar);
    boton.addEventListener("click", clic);
    escuchas.push(() => {
      boton.removeEventListener("pointerenter", entrar);
      boton.removeEventListener("pointerleave", salir);
      boton.removeEventListener("focus", foco);
      boton.removeEventListener("blur", salir);
      boton.removeEventListener("pointerdown", pulsar);
      boton.removeEventListener("click", clic);
    });
  }
```

Y en `destroy`, antes de `cim.remove()`:

```ts
      for (const off of escuchas) off();
      frase.removeEventListener("transitionend", alTerminar);
```

- [x] **Step 3: El apuntado en CSS**

Anadir al bloque `LOS CIMIENTOS`, antes del `@media (max-width: 820px)`:

```css
/*
  APUNTADO — la frase al rozar. El nombre pasa a --l3 (encender es un
  corte, 420ms) y vuelve a --text enfriandose (900ms atmosfera). La frase
  entra y sale por recorte lateral en la linea del rotulo del suelo, que ya
  tiene su altura: nada se mueve.
*/
:root[data-theme="hyprland"] .cim-txt {
  transition: color 0.9s var(--slow);
}
:root[data-theme="hyprland"] .cim-nombre[aria-pressed="true"] .cim-txt {
  color: var(--l3);
  transition: color 0.42s var(--hard);
}
:root[data-theme="hyprland"] .cim-frase {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 0.9s var(--slow);
}
:root[data-theme="hyprland"] .cim-cab.is-viva .cim-frase {
  clip-path: inset(0 0 0 0);
  transition: clip-path 0.42s var(--hard);
}
```

Aviso: los lenguajes tambien llevan `.cim-txt` con transicion de entrada retardada por `--cim-d`.
Mientras un lenguaje esta apuntado gana la regla de `[aria-pressed="true"]`; al soltar volveria a
la de entrada y el enfriado heredaria el retardo `--cim-d`. El retardo solo hace falta la primera
vez: el modulo marca `cim-entrado` sobre `.cim` al terminar la entrada, y a partir de ahi el
enfriado de los lenguajes va sin retardo.

```ts
  const marcarEntrado = (ev: TransitionEvent): void => {
    if (ev.propertyName === "clip-path") cim.classList.add("cim-entrado");
  };
  cim.addEventListener("transitionend", marcarEntrado);
  if (reduce) cim.classList.add("cim-entrado");
```

(y `cim.removeEventListener("transitionend", marcarEntrado)` en `destroy`), con la regla:

```css
:root[data-theme="hyprland"] .cim-entrado .cim-lenguajes .cim-nombre:not([aria-pressed="true"]) .cim-txt {
  transition-delay: 0ms;
}
```

- [x] **Step 4: Build, lint, arnes en verde, captura rozando**

```bash
npm run build && npm run lint
# reiniciar preview por PID
python3 scripts/measure-cimientos.py --url http://localhost:4213
```

Esperado `0 fallo(s)`. Captura con `hover()` real sobre "React" a 1440x900 y con `tap()` sobre
"Python" a 390x844 (contexto tactil), `/tmp/cim-t5-hover.png` y `/tmp/cim-t5-tap.png`, y mirarlas:
la frase a la derecha de "LENGUAJES BASE" en escritorio, bajo el rotulo en movil.

- [x] **Step 5: Commit**

```bash
git add src/components/hyprStackCimientos.ts src/themes/themes.css scripts/measure-cimientos.py
git commit -m "feat(credits): la frase al rozar en la linea del suelo, sin mover nada"
```

---

### Task 6: Movimiento reducido (gate 11)

**Files:**
- Modify: `src/themes/themes.css` (bloque `LOS CIMIENTOS`)
- Modify: `scripts/measure-cimientos.py`

- [x] **Step 1: Gate 11 en el arnes, y verlo en rojo**

```python
def gate_11_movimiento_reducido(b, url: str, errores: list, fallos: list) -> None:
    """Bajo reduce: todo en su estado final sin haber hecho scroll (el
    modulo pone cimientos-lit al montar), y ninguna transicion viva sobre
    los nodos del dispositivo (transition-duration 0s en todos). `*` en una
    media query NO alcanza a los pseudo-elementos (pagado en B2): aqui no hay
    pseudo-elementos, y este gate lo comprueba tambien."""
    for nombre, w, h in VIEWPORTS:
        pg = abrir(b, url, "hyprland", w, h, errores, reduce=True)
        if not ir_a_credits(pg):
            pg.context().close()
            continue
        st = pg.evaluate(ENTRADA_JS)
        if not (st and st["lit"] and st["lineaTrazada"] and st["colsAbiertas"] == 3 and st["lensEncendidos"] == 5):
            fallos.append(f"[{nombre} reduce] gate 11: el dispositivo no esta en su estado final: {st}")
        vivas = pg.evaluate(
            """() => Array.from(document.querySelectorAll('[data-cimientos], [data-cimientos] *'))
              .flatMap(e => [getComputedStyle(e), getComputedStyle(e, '::before'), getComputedStyle(e, '::after')])
              .filter(s => s.transitionDuration.split(',').some(d => parseFloat(d) > 0.02) || (s.animationName && s.animationName !== 'none')).length"""
        )
        if vivas != 0:
            fallos.append(f"[{nombre} reduce] gate 11: {vivas} nodos con transicion o animacion viva bajo reduce")
        pg.context().close()
```

Registrar tras el gate 4-6. Correr: esperado `gate 11: N nodos con transicion o animacion viva`
en los dos anchos (las transiciones de `.cim-txt`, `.cim-frase`, `.cim-col`, `.cim-linea` siguen
declaradas). Pegar la salida.

- [x] **Step 2: La guardia, selector a selector**

Al final del bloque `LOS CIMIENTOS`:

```css
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .cim-linea,
  :root[data-theme="hyprland"] .cimientos-lit .cim-linea {
    transform: none;
    transition: none;
  }
  :root[data-theme="hyprland"] .cim-col,
  :root[data-theme="hyprland"] .cimientos-lit .cim-col {
    clip-path: none;
    transition: none;
  }
  :root[data-theme="hyprland"] .cim-lenguajes .cim-txt,
  :root[data-theme="hyprland"] .cimientos-lit .cim-lenguajes .cim-txt {
    color: var(--text);
    transition: none;
  }
  :root[data-theme="hyprland"] .cim-lenguajes .cim-icono,
  :root[data-theme="hyprland"] .cimientos-lit .cim-lenguajes .cim-icono {
    color: var(--haze);
    transition: none;
  }
  :root[data-theme="hyprland"] .cim-txt,
  :root[data-theme="hyprland"] .cim-nombre[aria-pressed="true"] .cim-txt {
    transition: none;
  }
  :root[data-theme="hyprland"] .cim-frase,
  :root[data-theme="hyprland"] .cim-cab.is-viva .cim-frase {
    transition: none;
  }
}
```

- [x] **Step 3: Build, lint, arnes en verde, y el gate 4-6 sigue verde bajo reduce**

```bash
npm run build && npm run lint
# reiniciar preview por PID
python3 scripts/measure-cimientos.py --url http://localhost:4213
```

Esperado `0 fallo(s)`.

- [x] **Step 4: Commit**

```bash
git add src/themes/themes.css scripts/measure-cimientos.py
git commit -m "feat(credits): los cimientos bajo movimiento reducido, guardia por selector"
```

---

### Task 7: Contraste contra el fondo real (gate 10) y los arneses vecinos

**Files:**
- Modify: `scripts/measure-cimientos.py`

- [x] **Step 1: Gate 10, detras de `--contraste`**

`verify.py` no expone una funcion por par (`check_contrast_wcag` barre el viewport entero). La
tecnica se copia de `scripts/measure-cartel.py::contraste_fondo_real` (lineas 1002-1100): el
shader de Hyprland es `position: fixed` y no depende del scroll, asi que se lee el fondo bajo el
`rect` de cada glifo ocultando el contenido y muestreando fotogramas. Anadir al arnes:

```python
import io
from PIL import Image

PARES_CONTRASTE = [
    ("[data-cimientos] .cim-col .cim-txt", 4.5, "nombre --text"),
    ("[data-cimientos] .cim-rot", 4.5, "rotulo --haze"),
    ("[data-cimientos] .cim-lenguajes .cim-txt", 4.5, "lenguaje --text"),
    ("[data-cimientos] .cim-icono", 3.0, "icono decorativo --haze"),
    ("[data-cimientos] .cim-nombre[aria-pressed='true'] .cim-txt", 4.5, "apuntado --l3"),
    ("[data-cimientos] .cim-cab.is-viva .cim-frase", 4.5, "frase --catch"),
]


def _lum(rgb: tuple[int, int, int]) -> float:
    def c(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def _contraste(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    a, b = _lum(fg), _lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def _rgb(css: str) -> tuple[int, int, int]:
    n = [int(float(x)) for x in css[css.index("(") + 1 : css.index(")")].split(",")[:3]]
    return (n[0], n[1], n[2])


def gate_10_contraste_fondo_real(b, url: str, errores: list, fallos: list) -> None:
    """Contraste POR GLIFO contra el fondo real: rects y colores computados
    ANTES de ocultar el contenido; despues solo queda el shader y se toman
    24 fotogramas a 350ms; por cada par, el peor (p99,5) de la luminancia en
    una franja de 5px alrededor de su rect. La primera medida del cartel
    muestreo el viewport entero y sobrestimo el problema (1,01:1): no se
    repite. Los iconos son decorativos: piso 3:1 (WCAG 1.4.11)."""
    pg = abrir(b, url, "hyprland", 1440, 900, errores)
    if not ir_a_credits(pg):
        pg.context().close()
        return
    pg.wait_for_timeout(2500)
    pg.query_selector("[data-cimientos] .cim-nombre").hover()
    pg.wait_for_timeout(800)
    dianas = []
    for sel, piso, nombre in PARES_CONTRASTE:
        info = pg.evaluate(
            """(sel) => { const e = document.querySelector(sel); if (!e) return null;
              const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
              return { l: r.left, t: r.top, w: r.width, h: r.height, color: s.color }; }""",
            sel,
        )
        if info is None:
            fallos.append(f"gate 10: no existe '{nombre}' ({sel})")
        else:
            dianas.append((nombre, piso, info))
    pg.add_style_tag(content="#app > *:not(.bg-theme):not(.bg-noise) { visibility: hidden !important; }")
    pg.wait_for_timeout(300)
    peores: dict[str, list[float]] = {n: [] for n, _, _ in dianas}
    for _ in range(24):
        pg.wait_for_timeout(350)
        img = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
        px = img.load()
        for nombre, _piso, info in dianas:
            x0, y0 = max(0, int(info["l"]) - 5), max(0, int(info["t"]) - 5)
            x1, y1 = min(img.width, int(info["l"] + info["w"]) + 5), min(img.height, int(info["t"] + info["h"]) + 5)
            lums = sorted(_lum(px[x, y]) for y in range(y0, y1, 2) for x in range(x0, x1, 2))
            if lums:
                peores[nombre].append(lums[int(len(lums) * 0.995) - 1])
    for nombre, piso, info in dianas:
        if not peores[nombre]:
            fallos.append(f"gate 10: sin muestras para '{nombre}'")
            continue
        fg = _rgb(info["color"])
        peor_lum = max(peores[nombre])
        # el ratio se calcula contra un gris de esa luminancia: es el techo real
        v = int(round(255 * (peor_lum ** (1 / 2.2))))
        ratio = _contraste(fg, (v, v, v))
        print(f"  gate 10: {nombre}: peor caso {ratio:.2f}:1 (piso {piso})")
        if ratio < piso:
            fallos.append(f"gate 10: '{nombre}' cae a {ratio:.2f}:1 bajo el piso {piso}")
    pg.context().close()
```

En `main()`, tras el gate 11: `if args.contraste: gate_10_contraste_fondo_real(b, args.url, errores, fallos)`.
Correr con `--contraste` y pegar la tabla en el informe: son los numeros que van al spec. Si
`.cim-rot` (`--haze`) cae bajo 4,5 en su peor caso, es el techo de brillo del shader ya conocido:
se anota literal en el registro del spec y no se recalibra aqui.

- [x] **Step 2: Los arneses vecinos, uno detras de otro, nunca a la vez**

```bash
python3 scripts/measure-placa.py --url http://localhost:4213
python3 scripts/measure-cartel.py --base http://localhost:4213
nohup python3 scripts/measure-cursor-luz.py --base http://localhost:4213 > /tmp/cursor-luz.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -30 /tmp/cursor-luz.log
```

Esperado: 0 fallos en los tres. `measure-cursor-luz.py` tiene 23 dianas nuevas (`button.cim-nombre`
sobre el shader): si su gate de familia "oscurece" las coge y una cae, anotar el numero literal;
no se recalibra el cursor aqui (es el fallo 3 del repaso).

- [x] **Step 3: Commit**

```bash
git add scripts/measure-cimientos.py
git commit -m "test(credits): contraste de los cimientos contra el fondo real, tras --contraste"
```

---

### Task 8: Cierre — docs, capturas finales, verify.py, y los gates de critica

**Files:**
- Modify: `.claude/rules/verification.md` (tabla de arneses)
- Modify: `docs/superpowers/specs/2026-09-09-hyprland-stack-cimientos-design.md`

- [x] **Step 1: Fila del arnes nuevo en `rules/verification.md`**

Anadir a la tabla, tras la fila de `measure-placa.py`:

```markdown
| `measure-cimientos.py` | Los cimientos de Stack en Hyprland (spec 2026-09-09): que se ven y el generico no; que no existen en Vice ni Caelestia; **que la entrada se ve** (anclada a estado, con el dispositivo bajo el pliegue nada arranca y al 80 % aterriza todo); que ningun nombre queda encendido al salir (el P0 del catastro); que la frase al rozar es el `detail` literal y no mueve nada; desborde en cinco anchos medido con rects, nunca con `scrollWidth`; pies de columna y suelo a 48 px; tallas en la escala; diana tactil; movimiento reducido por selector; contraste contra el fondo real tras `--contraste`; y consola en las tres paginas. Sustituye a `measure-catastro.py`. | `npm run build && npx vite preview --port 4173 &`<br>`python3 scripts/measure-cimientos.py --url http://localhost:4173` |
```

- [x] **Step 2: Capturas finales con oyente**

A 390x844, 821x1024 y 1440x900, `?theme=hyprland`: reposo, a media entrada (sondeo por estado
como en la Task 4) y con "React" apuntado. Rutas `/tmp/cim-final-<ancho>-<estado>.png`. Mirarlas.

- [x] **Step 3: `verify.py` completo y el spec cerrado**

```bash
python3 scripts/verify.py --url http://localhost:4213   # codigo 0, 0 nuevos
```

En el spec: `Estado: implementado`, y un `## Registro de implementacion` con: la tabla de
contraste de la Task 7, las medidas finales (anchos de columna, aire al suelo, alto en movil),
cualquier desviacion respecto al plan y su motivo, y los gates vistos en rojo (con su salida
resumida) antes de aceptarse. Marcar todas las casillas de este plan.

- [x] **Step 4: Commit y matar el preview por PID**

```bash
git add .claude/rules/verification.md docs/superpowers/specs/2026-09-09-hyprland-stack-cimientos-design.md docs/superpowers/plans/2026-09-09-hyprland-stack-cimientos.md
git commit -m "docs(credits): cierra los cimientos: registro de implementacion y fila del arnes"
ss -ltnp | grep 4213   # y `kill <pid>` del que escucha
```

- [x] **Step 5: Gates de critica**

Con el build servido por tailnet (`--host 0.0.0.0`) para que Aoshi lo vea en el sitio real:
lanzar `lidia-naive-tester` y `vera-art-director` (pineados a `sonnet`), en secuencia, contra
`?theme=hyprland` con foco en la escena Stack. Umbral 7,5/10. Un P0 se arregla antes de
aceptar; un BLOCK residual lo acepta Aoshi explicitamente o no se acepta. **No se declara DONE sin
la revision de Aoshi en el sitio real.**
