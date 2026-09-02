# Caelestia B1 — Título Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir la escena `#hero` de Caelestia en el escritorio desnudo del shell — fondo de figuras Material 3 gobernado por la hora, titular justificado a `opsz 144`, firma trazada desde una terminal, cifras en columna y widget «Ahora mismo».

**Architecture:** El DOM de `hero.ts` es compartido por los tres temas: las piezas nuevas se añaden ahí y se ocultan con `display: none` en `style.css` para Vice y Hyprland, que es el patrón que ya usan `.hero-divider` y `.hero-name-ghost`. Lo que no se puede hacer con CSS —justificar tres líneas a una medida común y la entrada de escena— vive en un módulo nuevo, `src/themes/caelestia.titulo.ts`, que llama la coreografía del tema (`choreographyBuildsLayout: true` ya está declarado). El fondo se reescribe entero en `src/backgrounds/caelestiaFiguras.ts` y `caelestiaBlobs.ts` se borra.

**Tech Stack:** Vite 8 · TypeScript ~6 `strict` · Tailwind 4 · GSAP 3 · WebGL crudo (GLSL ES 1.0) · Playwright + Python para los arneses.

**Spec:** `docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md`

**Artefactos aprobados, ya rescatados al repo:**
- `docs/superpowers/specs/2026-08-26-caelestia-titulo-prototipo.glsl` — el shader del fondo, aprobado el 2026-08-26, con la lista de qué quitar al portarlo.
- `docs/superpowers/specs/2026-08-26-caelestia-firma-paths.json` — los 15 contornos de Fraunces de «Aoshi Blanco Sanz», ancho 945.7.

## Global Constraints

- **Node 22.** `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"` antes de cualquier `npm`. Con Node 18 `vite build` revienta dentro de rolldown con `styleText`.
- **Cero `any`.** `strict` está activo; usar `unknown` + guardas.
- **Cero emojis** en código, docs y commits.
- **Nunca `gsap.from`.** Siempre `fromTo` con los dos extremos escritos a mano, y `Array.from(...)` para colecciones vivas.
- **Todo módulo de tema devuelve un handle con `destroy()`**, que `main.ts` llama en `pagehide`. Borrar programa y buffers de WebGL, `cancelAnimationFrame`, matar timelines.
- **`prefers-reduced-motion` en todo lo que se mueva.**
- **Vice no se toca.** Hyprland no se toca. `src/backgrounds/shaderBackground.ts` es compartido: no se modifica.
- **Anti-mock:** todo dato visible sale de `src/data/content.ts` literal. Si no está ahí, no se pinta.
- **Todos los números medidos son a 1412 × 748**, la ventana del carril de workspaces.
- **Verificar contra el build de producción servido** (`npm run build && npx vite preview --port 4173`), nunca contra `npm run dev`: el HMR corrompe las medidas.
- **Commit por tarea**, formato `tipo(scope): descripción` con scope `caelestia`.

---

### Task 1: El arnés y el token de óptica

Primero el instrumento. Sin él, las seis tareas siguientes no tienen contra qué fallar.

**Files:**
- Create: `scripts/measure-caelestia-titulo.py`
- Modify: `src/themes/themes.css` (bloque `:root[data-theme="caelestia"]`, cerca de la línea 3526 donde ya vive `--cae-display-axes`)

**Interfaces:**
- Produces: `--cae-display-axes-cartel`, el token que usarán las tareas 3 y 6.
- Produces: `scripts/measure-caelestia-titulo.py` con `abrir(base, hora=None)` y `assert_que(cond, etiqueta)`, que todas las tareas siguientes amplían.

- [x] **Step 1: Escribir el arnés con su primera aserción, que tiene que fallar**

Crear `scripts/measure-caelestia-titulo.py`:

```python
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
        " const marca = document.querySelector('.cae-mark');"
        " const tit = document.querySelector('#hero .cae-tit .cae-ln');"
        " return {"
        "  token: cs.getPropertyValue('--cae-display-axes-cartel').trim(),"
        "  marca: marca ? getComputedStyle(marca).fontVariationSettings : '',"
        "  titular: tit ? getComputedStyle(tit).fontVariationSettings : ''"
        " }; }"
    )
    assert_que("144" in ejes["token"], f"el token --cae-display-axes-cartel existe y trae opsz 144 ({ejes['token']!r})")
    assert_que('"opsz" 9' in ejes["marca"], f"la marca de la barra sigue en opsz 9 ({ejes['marca']!r})")
    assert_que('"opsz" 144' in ejes["titular"], f"el titular usa opsz 144 ({ejes['titular']!r})")


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

        print("\n[consola] la pagina no tira errores")
        assert_que(not errores, f"cero errores de consola ({errores[:2]})")
        nav.close()

    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print("  - " + f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 2: Correrlo y ver los tres rojos**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npx vite preview --port 4173 &
sleep 4
python3 scripts/measure-caelestia-titulo.py --base http://localhost:4173
```

Esperado: FALLO en el token (cadena vacía) y FALLO en el titular (no existe `.cae-tit`). La aserción de la marca debe salir **OK** ya — si sale roja, algo del shell se ha roto y hay que parar.

- [x] **Step 3: Añadir el token**

En `src/themes/themes.css`, dentro de `:root[data-theme="caelestia"]`, justo debajo de `--cae-display-axes`:

```css
  /*
   * La optica del CARTEL, solo para el titular de la escena Titulo.
   *
   * `opsz` en Fraunces no es estilo: la fuente trae DIBUJOS DISTINTOS segun el
   * tamano al que se vaya a leer. `opsz 9` engorda las finas para que
   * sobrevivan a tamano de texto; a 15px (la marca de la barra) es lo correcto,
   * y ampliado a 84px sale romo y sin contraste.
   *
   * Los ejes de la barra, las pastillas y la firma NO se tocan: ahi el texto se
   * lee a 15-30px y necesita el dibujo de texto.
   */
  --cae-display-axes-cartel: "opsz" 144, "wght" 900, "SOFT" 0, "WONK" 1;
```

- [x] **Step 4: Volver a correr el arnés**

Esperado: el token en verde, la marca en verde, el titular sigue en rojo (aún no existe). Eso es correcto: lo cierra la tarea 3.

- [x] **Step 5: Commit**

```bash
git add scripts/measure-caelestia-titulo.py src/themes/themes.css
git commit -m "test(caelestia): arnes de la escena Titulo y token de optica de cartel"
```

---

### Task 2: El fondo — figuras de Material 3

**Files:**
- Create: `src/backgrounds/caelestiaFiguras.ts`
- Delete: `src/backgrounds/caelestiaBlobs.ts`
- Modify: `src/themes/caelestia.ts:44-47` (el `mountBackground`)
- Modify: `scripts/measure-caelestia-titulo.py` (sección `fondo`)
- Read: `docs/superpowers/specs/2026-08-26-caelestia-titulo-prototipo.glsl`

**Interfaces:**
- Consumes: `mountShaderBackground(container, fragmentShader, uniforms)` de `./shaderBackground`, y el tipo `BackgroundHandle`.
- Consumes: `hueAt`, `chromaScaleAt`, `isDarkAt` de `../themes/caelestia.color` — **son exports públicos ya existentes**, no hay que reimplementarlos.
- Produces: `mountCaelestiaFiguras(container: HTMLElement): BackgroundHandle`.

- [x] **Step 1: Escribir las aserciones del fondo, que tienen que fallar**

Añadir a `scripts/measure-caelestia-titulo.py`, antes de `main()`:

```python
LEE_LIENZO = """() => {
  const c = document.querySelector('canvas');
  if (!c) return null;
  const g = c.getContext('webgl');
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
  return { lo, hi, muestras };
}"""


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
        pg2 = pg.context.new_page()
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
```

Y llamarla en `main()`, después de `optica(pg, args.base)`:

```python
        fondo(pg, args.base)
```

- [x] **Step 2: Correrlo y ver los rojos**

```bash
python3 scripts/measure-caelestia-titulo.py --base http://localhost:4173
```

Esperado: «el fondo se mueve» en **FALLO** con un porcentaje muy bajo (`caelestiaBlobs.ts` mueve las manchas a 0.05 de factor: es el 3 % de referencia).

> **Aviso de duración:** el barrido abre 96 pestañas. Con swiftshader tarda entre 8 y 15 minutos. Es el precio de vigilar las transiciones y solo se paga en esta tarea y en la 8.

- [x] **Step 3: Escribir el módulo del fondo**

Crear `src/backgrounds/caelestiaFiguras.ts`. El shader va **copiado del prototipo** `docs/superpowers/specs/2026-08-26-caelestia-titulo-prototipo.glsl`, quitando lo que su propia cabecera dice que hay que quitar: la rama `uComp` (se deja fija la composición A3, se borran las otras cinco), `uDeriva` y `uVel` (mandos del companion, se dejan en 1.0).

```ts
import { chromaScaleAt, hueAt, isDarkAt } from "../themes/caelestia.color";
import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * El wallpaper de Caelestia: figuras con nombre de Material 3 Expressive que
 * morfan con la hora del visitante.
 *
 * Spec: docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md
 * Prototipo aprobado: docs/superpowers/specs/2026-08-26-caelestia-titulo-prototipo.glsl
 *
 * Sustituye a `caelestiaBlobs.ts`, que su propio comentario marcaba como
 * PROVISIONAL.
 */

/** Los cinco estados del dia. `n` = puntas, `a` = profundidad del lobulo
 *  (negativa = lado concavo, que es lo que hace un "cookie"), `s` = segundo
 *  armonico, que afila la punta. Los nombres son los de la biblioteca de
 *  Material 3 Expressive. */
const FIGURAS: readonly (readonly [n: number, a: number, s: number, elong: number])[] = [
  [4, 0.15, 0.02, 1.1], // 00:00 puffy
  [9, 0.105, 0.03, 1.0], // 04:48 sunny
  [12, -0.058, 0.012, 1.0], // 09:36 12-sided cookie
  [4, 0.265, -0.045, 1.0], // 14:24 4-leaf clover
  [10, 0.175, 0.07, 1.0], // 19:12 soft burst
] as const;

/** El transito ocupa el ultimo 30 % de cada tramo: 86 minutos. */
const TRANSICION = 0.3;

interface Fase {
  a: number;
  b: number;
  s: number;
}

export function faseAt(minutes: number): Fase {
  const f = (minutes / 1440) * 5;
  const i = Math.floor(f) % 5;
  const frac = f - Math.floor(f);
  const bruto = frac <= 1 - TRANSICION ? 0 : (frac - (1 - TRANSICION)) / TRANSICION;
  return { a: i, b: (i + 1) % 5, s: bruto * bruto * (3 - 2 * bruto) };
}

/** Los cuatro rellenos: la superficie base y los tres wall. El croma NO es el
 *  mismo en los dos esquemas — croma 0.09 a claridad 0.30 cae en la zona parda
 *  de OkLCH y da barro. De noche baja a un tercio y la claridad se abre. */
export function rampaAt(minutes: number): readonly (readonly [number, number, number])[] {
  const hue = hueAt(minutes);
  const esc = chromaScaleAt(hue);
  const osc = isDarkAt(minutes);
  return [
    [osc ? 0.185 : 0.98, (osc ? 0.016 : 0.012) * esc, hue],
    [osc ? 0.265 : 0.93, (osc ? 0.034 : 0.09) * esc, hue],
    [osc ? 0.32 : 0.95, (osc ? 0.028 : 0.07) * esc, (hue + 42) % 360],
    [osc ? 0.375 : 0.96, (osc ? 0.022 : 0.06) * esc, (hue + 318) % 360],
  ] as const;
}

const FRAGMENT_SHADER = /* glsl */ `
  … copiar aqui, literal, el cuerpo del prototipo:
  fromHue / toSrgb / tono / hash / radio / sdFigura / relleno / pon / main,
  con la rama A3 unica y sin uComp, uDeriva ni uVel …
`;

const REFRESH_MS = 750;

export function mountCaelestiaFiguras(container: HTMLElement): BackgroundHandle {
  let cache = { min: -1, leido: -Infinity };
  let fase: Fase = { a: 0, b: 1, s: 0 };
  let rampa = rampaAt(0);

  function refresh(): void {
    const ahora = performance.now();
    if (ahora - cache.leido < REFRESH_MS) return;
    cache.leido = ahora;
    const d = new Date();
    const min = d.getHours() * 60 + d.getMinutes();
    if (min === cache.min) return;
    cache.min = min;
    fase = faseAt(min);
    rampa = rampaAt(min);
  }

  const leer = <T>(f: () => T) => (): T => {
    refresh();
    return f();
  };

  return mountShaderBackground(container, FRAGMENT_SHADER, {
    uMezcla: leer(() => fase.s),
    uFigA: leer(() => [...FIGURAS[fase.a]].slice(0, 3) as [number, number, number]),
    uFigB: leer(() => [...FIGURAS[fase.b]].slice(0, 3) as [number, number, number]),
    uElong: leer(() => [FIGURAS[fase.a][3], FIGURAS[fase.b][3]] as [number, number]),
    uL0: leer(() => rampa[0][0]), uC0: leer(() => rampa[0][1]), uH0: leer(() => rampa[0][2]),
    uL1: leer(() => rampa[1][0]), uC1: leer(() => rampa[1][1]), uH1: leer(() => rampa[1][2]),
    uL2: leer(() => rampa[2][0]), uC2: leer(() => rampa[2][1]), uH2: leer(() => rampa[2][2]),
    uL3: leer(() => rampa[3][0]), uC3: leer(() => rampa[3][1]), uH3: leer(() => rampa[3][2]),
  });
}
```

> **Comprobar antes de escribir:** `shaderBackground.ts` (232 líneas) tiene que aceptar uniforms `vec2` y `vec3`. Si solo admite `float`, hay dos salidas y **ninguna es tocar ese fichero**, que es compartido con Vice: pasar `uFigA`/`uFigB`/`uElong` como floats sueltos (`uFigAn`, `uFigAa`, …), o ampliarlo detrás de una comprobación de tipo que no cambie el comportamiento existente. Leerlo en el paso 1 y decidir antes de escribir el módulo.

- [x] **Step 4: Cambiar el `mountBackground` del tema**

En `src/themes/caelestia.ts`, sustituir el cuerpo de `mountBackground`:

```ts
  async mountBackground(container) {
    const { mountCaelestiaFiguras } = await import("../backgrounds/caelestiaFiguras");
    return mountCaelestiaFiguras(container);
  },
```

- [x] **Step 5: Borrar el fondo viejo y comprobar que no queda nada apuntándole**

```bash
git rm src/backgrounds/caelestiaBlobs.ts
grep -rn "caelestiaBlobs\|mountCaelestiaBlobs" src/ docs/ scripts/ .claude/ README.md CLAUDE.md
```

Esperado: solo aparece en documentos que describen la fase A en pasado. Si sale en `src/`, arreglarlo.

- [x] **Step 6: Build, lint y arnés**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
npx vite preview --port 4173 &
python3 scripts/measure-caelestia-titulo.py --base http://localhost:4173
```

Esperado: las tres del fondo en verde. Movimiento ≥ 10 %, peor contraste del día ≥ 4.5:1.

- [x] **Step 7: Comprobar a ojo que Vice y Hyprland siguen intactos**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for t in ('vice','hyprland','caelestia'):
        pg = b.new_page(viewport={'width':1440,'height':900})
        pg.goto(f'http://localhost:4173/?theme={t}', wait_until='domcontentloaded', timeout=30000)
        pg.wait_for_timeout(9000)
        pg.screenshot(path=f'/tmp/tema-{t}.png', full_page=False)
        pg.close()
    b.close()
"
```

Abrir las tres capturas. Vice y Hyprland tienen que estar **exactamente igual** que antes.

- [x] **Step 8: Commit**

```bash
git add -A src/backgrounds src/themes/caelestia.ts scripts/measure-caelestia-titulo.py
git commit -m "feat(caelestia): el fondo pasa a ser figuras de Material 3 morfadas por la hora"
```

---

### Task 3: El bloque justificado

**Files:**
- Create: `src/themes/caelestia.titulo.ts`
- Modify: `src/sections/hero.ts` (añadir el bloque del titular al DOM compartido)
- Modify: `src/themes/caelestia.choreography.ts` (llamar al módulo nuevo)
- Modify: `src/style.css` (ocultar las piezas nuevas en Vice y Hyprland)
- Modify: `src/themes/themes.css` (la piel de Caelestia)
- Modify: `scripts/measure-caelestia-titulo.py`

**Interfaces:**
- Consumes: `--cae-display-axes-cartel` de la tarea 1.
- Produces: `justificarTitular(root: HTMLElement, medida?: number, altoMax?: number): void` y `montarTitulo(ctx: { gsap: GSAPType; root: HTMLElement }): TituloHandle`, donde `interface TituloHandle { destroy: () => void }`.
- Produces las clases `.cae-tit`, `.cae-ln`, que usan las tareas 6 y 7.

- [x] **Step 1: Escribir las aserciones de la justificación, que tienen que fallar**

Añadir a `scripts/measure-caelestia-titulo.py`:

```python
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
```

Llamarla en `main()` tras `fondo(...)`.

- [x] **Step 2: Correrlo y ver el rojo**

Esperado: FALLO en «el titular tiene tres líneas» — `.cae-tit` no existe.

- [x] **Step 3: Añadir el bloque al DOM compartido**

En `src/sections/hero.ts`, antes del `const section = el(...)`, añadir:

```ts
  /*
   * El titular de Caelestia. Vive en el DOM COMUN y `style.css` lo oculta en
   * Vice y Hyprland (`display: none`), que es el mismo patron que ya usan
   * `.hero-divider` y `.hero-name-ghost`.
   *
   * Las tres lineas van escritas a mano y no salen de partir
   * `identity.headline` por espacios: el corte es una decision de diseno
   * (el spec explica por que "que" no puede quedar colgando al final de la
   * primera linea) y el texto sigue siendo literal de `content.ts`.
   */
  const CORTE = ["Construyo sistemas", "que aguantan producción,", "no demos."] as const;
  const lineas = CORTE.map((texto) => el("span", "cae-ln", [texto]));
  const titular = el("p", "cae-tit", lineas);
  titular.setAttribute("data-cae-titular", "");

  const caeHead = el("div", "cae-head", [titular]);
```

Y meter `caeHead` en el array de hijos de `section`, después de `surface`:

```ts
    [eyebrow, divider, surface, caeHead, corner],
```

- [x] **Step 4: Ocultarlo en los otros dos temas**

En `src/style.css`, junto a las reglas que ya ocultan `.hero-divider`:

```css
/* Piezas que solo pinta Caelestia (fase B1). Mismo patron que .hero-divider:
   viven en el DOM comun y los otros dos temas las apagan. */
.cae-head {
  display: none;
}
```

Y en `src/themes/themes.css`, dentro del bloque de Caelestia:

```css
:root[data-theme="caelestia"] .cae-head {
  display: block;
  margin-top: auto;
  position: relative;
  padding-right: 230px; /* el hueco de la columna de cifras (tarea 4) */
}

:root[data-theme="caelestia"] .cae-tit {
  font-family: var(--font-display);
  margin: 0;
}

:root[data-theme="caelestia"] .cae-tit .cae-ln {
  display: block;
  white-space: nowrap;
  line-height: 0.9;
  letter-spacing: -0.018em;
  font-variation-settings: var(--cae-display-axes-cartel);
}

/* Caelestia esconde el hero de los otros temas: aqui manda .cae-head. */
:root[data-theme="caelestia"] .hero-surface,
:root[data-theme="caelestia"] .hero-kick,
:root[data-theme="caelestia"] .hero-corner {
  display: none;
}
```

> **Comprobar:** las reglas de `.hero-surface` para Caelestia que ya existen en `themes.css` (la tarjeta Material con `backdrop-filter`) dejan de aplicarse. Buscarlas y borrarlas en el mismo commit, no dejarlas muertas.

- [x] **Step 5: Escribir el módulo que justifica**

Crear `src/themes/caelestia.titulo.ts`:

```ts
/**
 * La escena Titulo de Caelestia: lo que no se puede hacer con CSS.
 *
 * Spec: docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md
 */

/**
 * Estira las lineas del titular hasta que todas midan lo mismo.
 *
 * DOS TRAMPAS, las dos pagadas ya:
 *
 * 1. Medir la caja del <span> NO es medir el texto. Los `.cae-ln` son de
 *    bloque: `getBoundingClientRect().width` devuelve el ancho del CONTENEDOR.
 *    Con esa medida las tres lineas salen del MISMO tamano y el bloque solo
 *    PARECE justificado. Hay que usar `Range` + `selectNodeContents`.
 *
 * 2. La medida comun no puede ser fija. Con esta frase las lineas son de 18, 24
 *    y 9 caracteres: forzarlas a una medida ancha dispara el alto de la ultima
 *    y se come el dock (medido: 400 px de bloque, -138 px de aire). Por eso el
 *    bucle estrecha la medida en pasos hasta que cabe.
 */
export function justificarTitular(root: HTMLElement, medida = 1080, altoMax = 250): void {
  const tit = root.querySelector<HTMLElement>(".cae-tit");
  if (!tit) return;
  const lineas = Array.from(tit.querySelectorAll<HTMLElement>(".cae-ln"));
  if (lineas.length === 0) return;

  const aplicar = (objetivo: number): void => {
    for (const linea of lineas) {
      linea.style.fontSize = "100px";
      const rango = document.createRange();
      rango.selectNodeContents(linea);
      const ancho = rango.getBoundingClientRect().width;
      if (ancho > 0) linea.style.fontSize = `${Math.round((objetivo / ancho) * 100)}px`;
    }
  };

  let objetivo = medida;
  aplicar(objetivo);
  while (objetivo > 380 && tit.getBoundingClientRect().height > altoMax) {
    objetivo -= 30;
    aplicar(objetivo);
  }
}

export interface TituloHandle {
  destroy: () => void;
}

export function montarTitulo(root: HTMLElement): TituloHandle {
  const rejustificar = (): void => justificarTitular(root);

  // Las fuentes variables cargan despues del primer pintado: justificar antes
  // mide Georgia (el respaldo) y los tamanos salen mal.
  void document.fonts.ready.then(rejustificar);
  rejustificar();
  window.addEventListener("resize", rejustificar);

  return {
    destroy: () => window.removeEventListener("resize", rejustificar),
  };
}
```

- [x] **Step 6: Llamarlo desde la coreografía**

En `src/themes/caelestia.choreography.ts`, dentro de `caelestiaChoreography`, después de que el carril esté montado:

```ts
  // El titular se justifica midiendo texto real, asi que necesita el DOM ya
  // colocado. `root` ES el <main>: ver el docstring de arriba.
  const titulo = montarTitulo(root);
```

y añadir `titulo.destroy()` a la limpieza que ya devuelve la función.

- [x] **Step 7: Build, lint y arnés**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-titulo.py --base http://localhost:4173
```

Esperado: las cuatro del titular en verde, y la de `optica` del titular también (ya existe `.cae-ln`).

- [x] **Step 8: Commit**

```bash
git add src/sections/hero.ts src/themes/caelestia.titulo.ts src/themes/caelestia.choreography.ts src/style.css src/themes/themes.css scripts/measure-caelestia-titulo.py
git commit -m "feat(caelestia): titular justificado a medida comun en la escena Titulo"
```

---

### Task 4: La firma y la columna de cifras

**Files:**
- Modify: `src/sections/hero.ts`
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-caelestia-titulo.py`

**Interfaces:**
- Consumes: `.cae-head` de la tarea 3.
- Produces: `.cae-firma` (destino del aterrizaje de la tarea 6), `.cae-meta`, `.cae-regla`, `.cae-statcol` y sus `.cae-v2` (que voltea la tarea 7).

- [x] **Step 1: Aserciones — texto literal y anti-mock**

```python
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
```

- [x] **Step 2: Correrlo y ver los rojos**

Esperado: los cinco en FALLO.

- [x] **Step 3: Añadir firma y columna al DOM**

En `src/sections/hero.ts`, dentro del bloque de Caelestia que creaste en la tarea 3, antes de `const caeHead`:

```ts
  const firma = el("span", "cae-firma", [identity.name]);
  const regla = el("span", "cae-regla");
  regla.setAttribute("aria-hidden", "true");
  const meta = el("span", "cae-meta", [identity.subheadline]);
  const kicker = el("p", "cae-kicker", [firma, regla, meta]);

  const statcol = el(
    "div",
    "cae-statcol",
    stats.map((s) => {
      const valor = el("span", "cae-v2", [s.value]);
      valor.setAttribute("data-n", s.value);
      return el("div", "", [valor, el("span", "cae-k", [s.label])]);
    }),
  );
```

y cambiar `caeHead` para que los recoja:

```ts
  const caeHead = el("div", "cae-head", [kicker, titular, statcol]);
```

Añadir `stats` al import de la primera línea:

```ts
import { identity, stats } from "../data/content";
```

- [x] **Step 4: La piel**

En `src/themes/themes.css`, en el bloque de Caelestia:

```css
:root[data-theme="caelestia"] .cae-kicker {
  display: flex;
  align-items: baseline;
  gap: 18px;
  margin: 0 0 14px;
}

:root[data-theme="caelestia"] .cae-firma {
  font-family: var(--font-display);
  /* Los ejes del SHELL, no los del cartel: aqui se lee a 30px. Y `nowrap`
     porque esta linea es el destino del trazo de la entrada — si partiera en
     dos, el aterrizaje no cuadraria. */
  font-variation-settings: "opsz" 9, "wght" 700, "SOFT" 0, "WONK" 1;
  font-size: 30px;
  line-height: 1;
  letter-spacing: -0.015em;
  white-space: nowrap;
}

:root[data-theme="caelestia"] .cae-regla {
  display: block;
  width: 46px;
  height: 1px;
  background: var(--cae-outline);
  transform-origin: left center;
}

:root[data-theme="caelestia"] .cae-meta {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--cae-on-surface-variant);
  white-space: nowrap;
}

:root[data-theme="caelestia"] .cae-statcol {
  position: absolute;
  right: 0;
  bottom: 0;
  display: grid;
  gap: 14px;
  text-align: right;
}

:root[data-theme="caelestia"] .cae-statcol > div {
  border-top: 1px solid var(--cae-outline);
  padding-top: 7px;
  min-width: 168px;
}

:root[data-theme="caelestia"] .cae-v2 {
  display: block;
  font-family: var(--font-display);
  font-variation-settings: "opsz" 9, "wght" 700, "SOFT" 0, "WONK" 1;
  font-size: 26px;
  line-height: 1;
  font-feature-settings: "tnum";
}

:root[data-theme="caelestia"] .cae-k {
  display: block;
  margin-top: 3px;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--cae-on-surface-variant);
}
```

- [x] **Step 5: Build, lint y arnés**

Esperado: las cinco de `firma_y_cifras` en verde, y **la de «aire bajo el pie» de la tarea 3 sigue en verde** — la columna añade alto y es donde se destapó el desbordamiento de 138 px. Si sale roja, bajar `medida` en `justificarTitular` antes de tocar nada más.

- [x] **Step 6: Commit**

```bash
git add src/sections/hero.ts src/themes/themes.css scripts/measure-caelestia-titulo.py
git commit -m "feat(caelestia): firma sobre el titular y cifras en columna al canto derecho"
```

---

### Task 5: El widget «Ahora mismo»

**Files:**
- Modify: `src/sections/hero.ts`
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-caelestia-titulo.py`

**Interfaces:**
- Produces: `.cae-widget` y sus hijos directos `.cae-wfila` (que anima la tarea 7).

- [x] **Step 1: Aserción anti-mock**

```python
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
    ]
    for e in esperado:
        assert_que(e in texto, f"el widget dice {e!r}, literal de content.ts")
    # El fallo real que hubo: un dato derivado que no existe en ninguna parte.
    assert_que("Repositorios públicos" not in texto, "el widget no inventa datos derivados")
```

- [x] **Step 2: Correrlo y ver los ocho rojos**

- [x] **Step 3: Añadir el widget al DOM**

En `src/sections/hero.ts`, antes de `const caeHead`:

```ts
  const disponible = el("span", "cae-pilla", [identity.availability]);
  const wnow = el("p", "cae-wnow", [identity.now]);
  const wsub = el("p", "cae-wsub", [`${identity.location} · Desde ${identity.since}`]);

  const wfila = (izq: string, der: string): HTMLElement =>
    el("div", "cae-wfila", [el("span", "", [izq]), el("span", "cae-wn", [der])]);

  const widget = el("div", "cae-widget", [
    el("p", "cae-whd", ["Ahora mismo"]),
    disponible,
    wnow,
    wsub,
    wfila(education[0].degree, "10.º semestre"),
    wfila(experience[0].organization, experience[0].period),
  ]);
```

y añadirlo a `section`, **hermano** de `caeHead`:

```ts
    [eyebrow, divider, surface, widget, caeHead, corner],
```

Ampliar el import:

```ts
import { education, experience, identity, stats } from "../data/content";
```

> **Ojo con «10.º semestre»:** en `content.ts` el semestre vive dentro de
> `education[0].period` (`"2021 — presente (10.º semestre)"`), no como campo
> propio. O se extrae con una constante local documentada, o se usa `period`
> entero. **No inventar un campo.**

- [x] **Step 4: La piel del widget**

```css
:root[data-theme="caelestia"] .cae-widget {
  display: block;
  position: absolute;
  top: 30px;
  right: 48px;
  width: 316px;
  padding: 20px 22px;
  border-radius: 24px;
  background: var(--cae-surface-container);
  border: 1px solid var(--cae-outline);
}
```

y en `src/style.css`, junto a `.cae-head`:

```css
.cae-widget {
  display: none;
}
```

(El resto de reglas —`.cae-whd`, `.cae-pilla`, `.cae-wnow`, `.cae-wsub`, `.cae-wfila`, `.cae-wn`— van en `themes.css` con los mismos valores de la maqueta: mono 9px `letter-spacing: .2em` para el rótulo, pastilla de `--cae-anchor` sobre `--cae-on-anchor`, Fraunces 20px para `now`.)

- [x] **Step 5: Build, lint y arnés. Commit**

```bash
git add src/sections/hero.ts src/themes/themes.css src/style.css scripts/measure-caelestia-titulo.py
git commit -m "feat(caelestia): widget Ahora mismo en la escena Titulo"
```

---

### Task 6: La entrada de escena — `whoami` y el trazo

**Files:**
- Create: `scripts/gen-firma-paths.py`
- Create: `src/themes/caelestia.firma.ts` (generado, se commitea)
- Modify: `src/themes/caelestia.titulo.ts`
- Modify: `src/sections/hero.ts`
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-caelestia-titulo.py`
- Read: `docs/superpowers/specs/2026-08-26-caelestia-firma-paths.json`

**Interfaces:**
- Consumes: `.cae-firma` de la tarea 4 (destino del aterrizaje).
- Produces: `FIRMA: { ancho: number; glifos: readonly { c: string; d: string }[] }` en `caelestia.firma.ts`, y `montarEntrada(gsap, root): { destroy: () => void }` en `caelestia.titulo.ts`.

- [x] **Step 1: Aserciones de la entrada**

```python
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
```

- [x] **Step 2: Correrlo y ver los rojos**

- [x] **Step 3: Escribir el generador de contornos**

Crear `scripts/gen-firma-paths.py`:

```python
#!/usr/bin/env python3
"""
Genera `src/themes/caelestia.firma.ts` — los contornos de Fraunces para el
trazo del nombre de la escena Titulo.

NO es una tipografia de imitacion: son los contornos reales de Fraunces
instanciada en opsz 9 / wght 900 / SOFT 0 / WONK 1, los mismos ejes que usa la
firma en reposo.

Se corre a mano cuando cambie `identity.name` o los ejes del display. El
resultado se COMMITEA: no hay descarga en tiempo de ejecucion.

    python3 -m venv /tmp/fenv && /tmp/fenv/bin/pip install fonttools
    curl -sL -o /tmp/fraunces.ttf \\
      'https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf'
    /tmp/fenv/bin/python scripts/gen-firma-paths.py /tmp/fraunces.ttf
"""
import sys

from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

TEXTO = "Aoshi Blanco Sanz"
EJES = {"opsz": 9, "wght": 900, "SOFT": 0, "WONK": 1}
TAM = 100
DESTINO = "src/themes/caelestia.firma.ts"


def main(ttf: str) -> int:
    fuente = instantiateVariableFont(TTFont(ttf), EJES, inplace=True)
    glifos, cmap = fuente.getGlyphSet(), fuente.getBestCmap()
    upem, hmtx = fuente["head"].unitsPerEm, fuente["hmtx"]

    escala, x, salida = TAM / upem, 0.0, []
    for ch in TEXTO:
        nombre = cmap.get(ord(ch))
        if nombre is None:
            x += TAM * 0.30
            continue
        pluma = SVGPathPen(glifos)
        glifos[nombre].draw(TransformPen(pluma, Transform(escala, 0, 0, -escala, x, 0)))
        d = pluma.getCommands()
        if d:
            # Dos decimales: el trazo se dibuja a 780 px de ancho, asi que la
            # tercera cifra es ruido y son 8 KB menos en el bundle.
            d = " ".join(
                f"{float(t):.2f}" if t.replace(".", "", 1).replace("-", "", 1).isdigit() else t
                for t in d.replace("-", " -").split()
            )
            salida.append({"c": ch, "d": d})
        x += hmtx[nombre][0] * escala

    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(
            "/* GENERADO por scripts/gen-firma-paths.py — no editar a mano. */\n"
            "export interface Glifo {\n  readonly c: string;\n  readonly d: string;\n}\n\n"
            "export const FIRMA: { readonly ancho: number; readonly glifos: readonly Glifo[] } = {\n"
            f"  ancho: {x:.1f},\n  glifos: [\n"
        )
        for g in salida:
            f.write(f'    {{ c: {g["c"]!r}, d: "{g["d"]}" }},\n'.replace("'", '"'))
        f.write("  ],\n};\n")

    print(f"{DESTINO}: {len(salida)} glifos, ancho {x:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/fraunces.ttf"))
```

- [x] **Step 4: Generar el módulo y comprobarlo**

```bash
python3 -m venv /tmp/fenv && /tmp/fenv/bin/pip install -q fonttools
curl -sL -o /tmp/fraunces.ttf \
  'https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf'
/tmp/fenv/bin/python scripts/gen-firma-paths.py /tmp/fraunces.ttf
grep -c '{ c:' src/themes/caelestia.firma.ts   # esperado: 15
```

Contrastar el `ancho` con el del artefacto aprobado: `docs/superpowers/specs/2026-08-26-caelestia-firma-paths.json` dice **945.7**. Si no coincide, los ejes o la fuente no son los mismos.

- [x] **Step 5: Escribir la entrada**

Añadir a `src/themes/caelestia.titulo.ts` la función `montarEntrada(gsap, root)`. Piezas, en orden y con sus tiempos:

1. `.cae-term` aparece (`fromTo` opacidad 0→1, y 8→0, 0.26 s, `power2.out`).
2. Se escribe `whoami` — `gsap.to` sobre un objeto `{ i: 0 }`, 0.46 s, `ease: "none"`, escribiendo `typed.textContent` en `onUpdate`.
3. El cursor parpadea: `repeat: 3, yoyo: true`, 0.14 s.
4. El trazo: por cada `path`, `strokeDasharray` y `strokeDashoffset` = `path.getTotalLength()`, y `gsap.to(..., { strokeDashoffset: 0, duration: 0.52, ease: "power1.inOut", stagger: 0.045 })`.
5. Relleno: `fillOpacity` 0→1, 0.3 s, stagger 0.03, en `-=0.42`; y `strokeOpacity` 1→0 en `<`.
6. La terminal se va (`-=0.15`).
7. **El aterrizaje**, dentro de un `tl.add(() => { … })` porque hay que medir en ese instante:

```ts
    const a = svg.getBoundingClientRect();
    const b = firma.getBoundingClientRect();
    gsap.to(svg, {
      x: b.left + b.width / 2 - (a.left + a.width / 2),
      y: b.top + b.height / 2 - (a.top + a.height / 2),
      scale: b.width / a.width,
      duration: 0.66,
      ease: "power3.inOut",
    });
    gsap.to(svg, { opacity: 0, duration: 0.2, delay: 0.54, ease: "power2.in" });
    gsap.to(firma, { opacity: 1, duration: 0.2, delay: 0.56, ease: "power2.out" });
```

> **Sin escala del bastidor.** En el companion había que dividir por `k` porque la ventana iba escalada con `transform: scale()`. En el sitio real **no hay escalado**: si se copia la división, el aterrizaje cae fuera.

8. Guarda de movimiento reducido: si `matchMedia("(prefers-reduced-motion: reduce)").matches`, no se construye la timeline — se pone el estado final con `gsap.set` y `.cae-term` a `display: none`.

- [x] **Step 6: Build, lint, arnés. Commit**

```bash
git add scripts/gen-firma-paths.py src/themes/caelestia.firma.ts src/themes/caelestia.titulo.ts src/sections/hero.ts src/themes/themes.css scripts/measure-caelestia-titulo.py
git commit -m "feat(caelestia): la escena Titulo entra con whoami y el nombre trazado"
```

---

### Task 7: Barrido de tinta, volteo de cifras y el roce

**Files:**
- Modify: `src/themes/caelestia.titulo.ts`
- Modify: `scripts/measure-caelestia-titulo.py`

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: nada nuevo. Cierra la coreografía de la escena.

- [x] **Step 1: Aserción del roce**

```python
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
```

- [x] **Step 2: Correrlo y ver los rojos**

- [x] **Step 3: Implementar los tres gestos**

En la timeline de `montarEntrada`, después del aterrizaje:

- **Regla y meta:** `scaleX` 0→1, 0.4 s `power3.out`; meta opacidad 0→1 con `x` −8→0.
- **Barrido de tinta del titular:** `gsap.fromTo(lineas, { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.72, ease: "power2.inOut", stagger: 0.11 })`.
- **Volteo de las cifras:** `gsap.set(bloques, { transformPerspective: 600 })` y `fromTo` de `{ opacity: 0, rotateX: -82, y: 6 }` a `{ opacity: 1, rotateX: 0, y: 0, duration: 0.6, ease: "power3.out", stagger: 0.09 }`.

Y el roce, fuera de la timeline, sobre `.cae-widget`, `.cae-statcol > div`, `.cae-ws` de la barra y `.cae-dock-item`:

```ts
  const lienzo = document.querySelector<HTMLCanvasElement>("canvas");
  const ventana = root.getBoundingClientRect();
  const entrar = (el: HTMLElement) => () => {
    if (!lienzo) return;
    const r = el.getBoundingClientRect();
    const dx = (r.left + r.width / 2 - (ventana.left + ventana.width / 2)) / (ventana.width / 2);
    const dy = (r.top + r.height / 2 - (ventana.top + ventana.height / 2)) / (ventana.height / 2);
    gsap.to(lienzo, { x: -dx * 14, y: -dy * 10, duration: 0.7, ease: "power3.out" });
    gsap.to(el, { y: -2, duration: 0.3, ease: "power3.out" });
  };
```

con su `pointerleave` devolviendo a 0, y **todos los listeners guardados para quitarlos en `destroy()`**.

- [x] **Step 4: Build, lint, arnés completo. Commit**

```bash
git add src/themes/caelestia.titulo.ts scripts/measure-caelestia-titulo.py
git commit -m "feat(caelestia): barrido del titular, volteo de cifras y el fondo que se aparta"
```

---

### Task 8: Cierre

**Files:**
- Modify: `scripts/verify-baseline.json` (si cambia la línea base)
- Modify: `docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md` (`Estado:` y `Plan:`)
- Modify: `CLAUDE.md` y `.claude/CLAUDE.md` (estado de los temas)
- Modify: `.claude/rules/verification.md` (la tabla de arneses)

- [x] **Step 1: Arnés completo en verde, y contra los tres temas**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
npx vite preview --port 4173 &
python3 scripts/measure-caelestia-titulo.py --base http://localhost:4173
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173   # la fase A no se ha roto
python3 scripts/measure-obra-rail.py --base http://localhost:4173        # Vice intacto
python3 scripts/verify.py
```

Los cuatro tienen que salir con código 0.

- [x] **Step 2: Ver cada gate dar rojo**

Uno por uno, romper a propósito lo que cada aserción dice cazar y confirmar que enrojece. **Ningún gate se da por bueno sin esto** — es la lección que más costó en la fase A: ocho veces el fallo estuvo en el instrumento.

| gate | cómo romperlo |
|---|---|
| óptica | poner `--cae-display-axes` en el titular |
| compila | meter un `;` de más en el shader |
| se mueve | poner `uTime` a 0 en el bucle |
| barrido 24 h | subir la claridad de `wall-3` a 0.70 en oscuro |
| justificación | medir con `getBoundingClientRect()` del span en vez de `Range` |
| cabe | quitar el bucle que estrecha la medida |
| anti-mock | añadir «Repositorios públicos · 2» al widget |
| reducido | quitar la guarda de `matchMedia` |

- [x] **Step 3: Capturas reales, móvil y escritorio**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for w,h,n in ((1412,748,'desktop'),(390,844,'movil')):
        pg = b.new_page(viewport={'width':w,'height':h})
        pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded', timeout=30000)
        pg.wait_for_timeout(9000)
        pg.screenshot(path=f'/tmp/b1-{n}.png')
        pg.close()
    b.close()
"
```

Mirarlas. **Móvil está fuera del alcance de esta fase** (el carril de workspaces en pantalla estrecha es una decisión abierta desde la fase A): si sale roto, anotarlo, no arreglarlo.

- [x] **Step 4: Actualizar spec y documentos**

- En el spec: `Estado: implementado` y añadir `Plan: docs/superpowers/plans/2026-08-26-caelestia-titulo.md`.
- En `CLAUDE.md` y `.claude/CLAUDE.md`, en el estado de los temas: la fase B1 cerrada, B2–B5 pendientes, y que `caelestiaBlobs.ts` ya no existe.
- En `.claude/rules/verification.md`, añadir `measure-caelestia-titulo.py` a la tabla de arneses.

- [x] **Step 5: Gates de crítica**

Lanzar `lidia-naive-tester` y `vera-art-director` sobre `?theme=caelestia`, **pinando el modelo** (`model: sonnet`) según la norma de `/home/aoshi/proyectos/CLAUDE.md`. Anotar el resultado en el spec, aceptando o no el BLOCK explícitamente, como en Vice y en la fase A.

- [x] **Step 6: Commit final**

```bash
git add -A docs/ CLAUDE.md .claude/ scripts/
git commit -m "docs(caelestia): la fase B1 (Titulo) queda implementada"
```

---

## Self-review

**Cobertura del spec.** Entrada `whoami` → tarea 6. Titular justificado y `opsz 144` → tareas 1 y 3. Firma y cifras → tarea 4. Widget → tarea 5. Fondo (figuras, color, morfado, deriva) → tarea 2. Micro-interacción N4 → tarea 7. Los ocho gates → repartidos entre las tareas 1–7 y cerrados en la 8. Movimiento reducido → tarea 6.

**Riesgo abierto que el ejecutor tiene que resolver en la tarea 2:** `shaderBackground.ts` puede no aceptar uniforms `vec2`/`vec3`. Está señalado en el paso 3 con las dos salidas posibles y la prohibición de tocar ese fichero a la ligera.

**Riesgo abierto en la tarea 5:** «10.º semestre» no es un campo de `content.ts`; vive dentro de `education[0].period`. Señalado, con la prohibición de inventar un campo.
