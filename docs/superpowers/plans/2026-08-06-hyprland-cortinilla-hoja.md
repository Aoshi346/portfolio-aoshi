# La hoja de contactos — plan de implementación

> **Para agentes:** SUB-SKILL OBLIGATORIA: usar `superpowers:subagent-driven-development`
> (recomendada) o `superpowers:executing-plans` para ejecutar este plan tarea a tarea. Los pasos
> usan casillas (`- [ ]`) para el seguimiento. Marca cada casilla **en el momento** en que
> completas su paso, nunca en bloque al final (`rules/speckit-progress-tracking.md`).

Spec: `docs/superpowers/specs/2026-08-06-hyprland-cortinilla-hoja-design.md`
Rama: `design/hyprland-cortinilla-hoja` (ya creada, con el spec commiteado en `b82fa58`)

**Goal:** Convertir la cortinilla de navegación de Hyprland de cinco renglones de texto en cinco
fotogramas con la silueta de cada escena, y su disparador en un pie de fotograma sin caja con dos
estados, sin tocar Vice ni Caelestia.

**Architecture:** `sceneNav.ts` construye un único DOM para los tres temas. Los nodos nuevos
(silueta, golpe de luz, disparador de dos estados) se añaden **incondicionalmente** y van
`display: none` en la hoja base; solo `:root[data-theme="hyprland"]` los enciende. Es el patrón que
ya validó el hero. Las siluetas viven en su propio módulo de datos, construidas como nodos DOM (no
`innerHTML`). Todo el movimiento es CSS declarativo, sin GSAP.

**Tech Stack:** TypeScript estricto, CSS en `src/themes/themes.css`, arneses de verificación en
Python con Playwright.

## Global Constraints

Copiadas del spec y de `CLAUDE.md`. **Aplican a todas las tareas.**

- **Prohibido `any`.** `strict` está activo. Usar `unknown` + guards.
- **Prohibido `gsap.from`.** Si hiciera falta GSAP: `fromTo` con los dos extremos escritos a mano.
  Este plan no usa GSAP.
- **Ninguna regla CSS nueva sin `:root[data-theme="hyprland"]` en el selector.**
  `.scene-nav-trigger` y `.scene-index` son compartidas por los tres temas y el disparador vive
  fuera del árbol de cualquier escena: no hay `[data-scene]` que lo contenga por accidente.
- **Todo nodo nuevo que `sceneNav.ts` añada necesita su `display: none` de base.** El módulo se
  ejecuta en los tres temas; si solo Hyprland le da estilo, en Vice y Caelestia el nodo se cuela
  como hijo suelto de un contenedor `flex`. Ya ha pasado cuatro veces
  (`.scene-nav-trigger-mark`; luego `.scene-shot` / `.scene-index-flash` / `.scene-index-bar` en la
  Tarea 3; y `.scene-nav-trigger-tc` en la Tarea 5, que ensanchó el disparador de 168,81 a 411,06 px
  en **Vice**, que está cerrado). La regla va a la lista compartida de `themes.css`, sin prefijo de
  tema, y el bloque de Hyprland la revierte al `display` que toque.
  **Y el arnés de la tarea tiene que abrir los otros dos temas:** `measure-cortinilla.py` solo
  miraba `?theme=hyprland` y por eso no lo vio; lo delató `verify.py --theme caelestia` con menos
  fallos de contraste y ratios peores, que es la firma de estar midiendo otra cosa.
- **Prohibido `order` en la rejilla.** El quinto fotograma va el último en el DOM con
  `grid-column: 1 / -1`.
- **Prohibido `innerHTML` para construir las siluetas.** Nodos a mano, como `src/utils/dom.ts`.
- **Prohibido `console.log`** en código de producción.
- **Cero emojis** en código, docs y commits.
- **Curvas:** instrumento (barrido) `linear`; todo lo demás `cubic-bezier(.7,0,.2,1)`.
- **Tiempos declarados:** barrido 480 ms · exposición 140 ms con retardos
  **9/102/195/289/382 ms** · golpe de luz 300 ms · cierre fotogramas 110 ms escalonados 20 ms en
  orden inverso · cierre telón 200 ms · hover 200 ms · cambio de rótulo del disparador 200 ms.
- **`prefers-reduced-motion: reduce`:** duración 0, sin escalonado, y la barra de luz **no existe**
  (no basta con acelerarla). Foco, `Esc`, clic fuera y bloqueo de scroll no cambian.
- **Verificar con Node 22**, no con el del sistema: `export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH`.
  Con Node 18 `npm run dev` revienta con `node:util does not provide an export named 'styleText'`.
- **Playwright:** en esta máquina el chromium propio no está descargado. Lanzar contra
  `/usr/bin/google-chrome`. `/usr/bin/chromium-browser` NO existe.
- **Nunca medir animación con capturas.** `page.screenshot()` en headless perturba el compositor.
  Muestrear desde dentro de la página en `requestAnimationFrame`.
- **Nunca `git stash`** para comparar contra HEAD: usar `git worktree add`. Y `git stash` solo
  esconde lo **no commiteado**: un A/B así no prueba nada sobre lo que ya commitearon las tareas
  anteriores de la propia rama. Para saber si algo es preexistente hay que medirlo contra el
  merge-base, en un worktree.
- **Caelestia sale en rojo también en `main`, y es normal.** Medido en el merge-base `c1cacf1`
  sirviendo la rama en un worktree: `verify.py --theme caelestia` reporta **9 fallos de contraste
  AA** sobre el rótulo del disparador (`span "0N · Nombre"`, `fg=(108,79,216)`, ratios 4,06–4,24
  contra un mínimo de 4,5). No están en `verify-baseline.json` y **no se meten**: es un hallazgo de
  accesibilidad real de un tema que este trabajo no toca, y esconderlo en la base es justo el modo
  de fallo que la base venía a evitar. El gate correcto para Caelestia es **exactamente esos 9 y
  ninguno más**, no "0 fallos".

## Estructura de ficheros

| Fichero | Responsabilidad | Acción |
|---|---|---|
| `docs/superpowers/prototypes/2026-08-06-cortinilla-hoja.html` | El prototipo aprobado, como artefacto versionado. Fuente de los valores exactos de las siluetas. | Crear (Tarea 0) |
| `src/data/content.ts:396` | `label` del índice de escenas | Modificar (Tarea 1) |
| `src/sections/about.ts:302` | Rótulo de la escena | Modificar (Tarea 1) |
| `src/components/sceneNav.siluetas.ts` | **Solo datos + constructor de nodos** de las cinco siluetas. Nada de estado ni de eventos. | Crear (Tarea 2) |
| `src/components/sceneNav.ts` | Añade los nodos nuevos a cada fila y al disparador. No cambia su lógica de foco, `Esc`, clic fuera ni bloqueo de scroll. | Modificar (Tareas 2 y 5) |
| `src/themes/themes.css` | Bloque nuevo de Hyprland para la hoja (Tarea 3), su movimiento (Tarea 4) y el disparador (Tarea 5) | Modificar |
| `scripts/measure-cortinilla.py` | Arnés de los criterios 1–6 del spec | Crear (Tarea 3, ampliado en 4 y 5) |

---

### Tarea 0: Versionar el prototipo aprobado

`.superpowers/` está en `.gitignore` (línea 47). El prototipo es la fuente de los valores exactos de
las siluetas y del movimiento: si el harness limpia esa carpeta, el plan se queda sin referencia.

**Files:**
- Create: `docs/superpowers/prototypes/2026-08-06-cortinilla-hoja.html`

**Interfaces:**
- Produces: el fichero de referencia que las Tareas 2, 3, 4 y 5 citan para valores exactos.

- [ ] **Step 1: Copiar el prototipo aprobado**

```bash
mkdir -p docs/superpowers/prototypes
cp .superpowers/brainstorm/2163099-1786029203/content/cortinilla-h-v3.html \
   docs/superpowers/prototypes/2026-08-06-cortinilla-hoja.html
```

- [ ] **Step 2: Comprobar que llegó entero**

Run: `grep -c "SC = \[" docs/superpowers/prototypes/2026-08-06-cortinilla-hoja.html && grep -c "h-frame" docs/superpowers/prototypes/2026-08-06-cortinilla-hoja.html`
Expected: `1` y un número ≥ 15.

Si el fichero de origen ya no existe (el servidor del companion se limpió), **para y avísalo**: hay
que reconstruirlo desde el spec antes de seguir. No inventes las siluetas.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/prototypes/2026-08-06-cortinilla-hoja.html
git commit -m "docs(nav): versionar el prototipo aprobado de la hoja de contactos"
```

---

### Tarea 1: "Quién es" → "Quién soy"

Los dos sitios cambian juntos o el índice y la escena se contradicen. **El `id` NO cambia**:
`quien-es` es un ancla real (`href="#quien-es"`, `history.replaceState`) y renombrarlo rompería los
enlaces que alguien tenga guardados y el arnés `measure-nav.py`.

**Files:**
- Modify: `src/data/content.ts:396`
- Modify: `src/sections/about.ts:302`

**Interfaces:**
- Consumes: nada.
- Produces: `sceneIndex[1].label === "Quién soy"`.

- [ ] **Step 1: Cambiar el rótulo del índice**

En `src/data/content.ts:396`, cambiar solo el `label`:

```ts
  { id: "quien-es", label: "Quién soy", blurb: "Trayectoria y cifras" },
```

- [ ] **Step 2: Cambiar el rótulo de la escena**

En `src/sections/about.ts:302`:

```ts
    [el("h2", "hero-kick", ["Quién soy"]), el("div", "about-grid", [createCard(), body])],
```

- [ ] **Step 3: Comprobar que no queda ninguno y que el id sigue intacto**

Run: `grep -rn "Quién es" src/ ; grep -rn "quien-es" src/ | wc -l`
Expected: la primera orden no imprime nada; la segunda imprime `2` — `content.ts` y `main.ts`.
`about.ts` **no** lleva el literal `quien-es`: su sección se marca con `data-scene="about"` y el
mapeo a id vive en `main.ts:120`. Si sale `3`, alguien ha metido el id donde no iba.

- [ ] **Step 4: Build**

Run: `export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH && npm run build && npm run lint`
Expected: ambos en verde.

- [ ] **Step 5: Commit**

```bash
git add src/data/content.ts src/sections/about.ts
git commit -m "content(nav): la segunda escena pasa a llamarse Quien soy"
```

---

### Tarea 2: El módulo de siluetas y sus nodos en el DOM

**Files:**
- Create: `src/components/sceneNav.siluetas.ts`
- Modify: `src/components/sceneNav.ts:96` (el `row.append(...)`)
- Modify: `src/themes/themes.css` (una regla de base, `display: none`)

**Interfaces:**
- Consumes: `SceneEntry.id` de `sceneNav.destino.ts`.
- Produces:
  - `export interface Pieza` con los campos `clase`, `x`, `y`, `w?`, `h?`, `texto?`, `tam?`,
    `tono?`, `opac?`.
  - `export const SILUETAS: Readonly<Record<string, readonly Pieza[]>>`
  - `export function construirSilueta(id: string): HTMLElement` — devuelve un
    `<span class="scene-shot">` con las piezas dentro, o un `<span class="scene-shot">` vacío si el
    id no está en `SILUETAS` (defensivo: `content.ts` puede crecer antes que este módulo).

- [ ] **Step 1: Escribir el módulo con la primera silueta completa**

Crear `src/components/sceneNav.siluetas.ts`. Las coordenadas están en el plano de **1440×900** —el
encuadre real del sitio— y el CSS lo escala al fotograma. Esta es la silueta 01 completa, portada
del prototipo (`docs/superpowers/prototypes/2026-08-06-cortinilla-hoja.html`, array `SC`, entrada
`id:'hero'`):

```ts
/**
 * Siluetas del indice de escenas: cada escena reducida a su estructura, en
 * coordenadas del plano real de 1440x900. El CSS las escala al fotograma.
 *
 * Son una COPIA a mano de la maqueta de cada escena, no se leen del DOM: el
 * indice se pinta con la cortinilla cerrada y las escenas ni siquiera estan
 * montadas del todo. El precio es que pueden envejecer — si una escena cambia
 * de dispositivo y su silueta no, la hoja miente en silencio. Vigilado por
 * `scripts/measure-cortinilla.py`, que comprueba que hay cinco y ninguna vacia.
 */

/** Una pieza de la silueta. `x`/`y`/`w`/`h` en pixeles del plano de 1440x900. */
export interface Pieza {
  /** `rl` filete, `bar` bloque de texto abstraido, `box` caja, `dot` circulo,
   *  `disp` texto real en la cara de display, `beam` el haz. */
  readonly clase: "rl" | "bar" | "box" | "dot" | "disp" | "beam";
  readonly x?: number;
  readonly y?: number;
  readonly w?: number;
  readonly h?: number;
  readonly texto?: string;
  readonly tam?: number;
  readonly tono?: string;
  readonly opac?: number;
}

export const SILUETAS: Readonly<Record<string, readonly Pieza[]>> = {
  hero: [
    { clase: "beam", opac: 1 },
    { clase: "rl", x: 190, y: 300, w: 1, h: 280 },
    { clase: "disp", x: 222, y: 340, tam: 96, tono: "#fff4ee", texto: "Aoshi Blanco Sanz" },
    { clase: "bar", x: 570, y: 470, w: 300, h: 6, opac: 0.42 },
    { clase: "rl", x: 267, y: 530, w: 1120, h: 1, tono: "#ff5a34", opac: 0.5 },
    { clase: "bar", x: 267, y: 552, w: 180, h: 5, opac: 0.3 },
    { clase: "bar", x: 1180, y: 552, w: 207, h: 5, opac: 0.3 },
  ],
  // "quien-es", "obra", "creditos", "contacto": ver Step 2.
};

export function construirSilueta(id: string): HTMLElement {
  const shot = document.createElement("span");
  shot.className = "scene-shot";
  for (const p of SILUETAS[id] ?? []) {
    const n = document.createElement("span");
    n.className = `scene-shot-${p.clase}`;
    if (p.x !== undefined) n.style.left = `${p.x}px`;
    if (p.y !== undefined) n.style.top = `${p.y}px`;
    if (p.w !== undefined) n.style.width = `${p.w}px`;
    if (p.h !== undefined) n.style.height = `${p.h}px`;
    if (p.tam !== undefined) n.style.fontSize = `${p.tam}px`;
    if (p.tono !== undefined) n.style.background = p.tono;
    if (p.opac !== undefined) n.style.opacity = String(p.opac);
    // `textContent`, nunca `innerHTML`: es contenido propio y estatico, pero la
    // regla del proyecto es construir DOM a mano y no abrir la puerta.
    if (p.texto !== undefined) {
      n.textContent = p.texto;
      n.style.background = "";
      if (p.tono !== undefined) n.style.color = p.tono;
    }
    shot.append(n);
  }
  return shot;
}
```

Nota sobre `tono`: en `bar`/`rl`/`box`/`dot` pinta el fondo; en `disp` pinta el color del texto. El
`if` de arriba lo resuelve. No añadas un campo aparte.

- [ ] **Step 2: Portar las otras cuatro siluetas**

Abrir `docs/superpowers/prototypes/2026-08-06-cortinilla-hoja.html` y traducir las entradas
`quien`, `obra`, `creditos` y `contacto` del array `SC` a `Pieza[]`, **con las mismas coordenadas**.
La correspondencia de clases del prototipo a `Pieza.clase` es directa:

| prototipo | `clase` |
|---|---|
| `<span class="beam">` | `beam` |
| `<span class="rl">` | `rl` |
| `<span class="bar">` | `bar` |
| `<span class="box">` | `box` |
| `<span class="dot">` | `dot` |
| `<span class="disp">` | `disp` |
| `<span class="lab">` | `bar` con `tono: "#ff5a34"` (el rótulo naranja se abstrae a un bloque) |

Las claves del objeto son los **ids de `content.ts`**, no los del prototipo:
`hero`, `quien-es`, `obra`, `creditos`, `contacto`. Ojo con `quien` → `quien-es`.

- [ ] **Step 3: Añadir los nodos a cada fila**

En `src/components/sceneNav.ts`, importar arriba junto al import existente:

```ts
import { construirSilueta } from "./sceneNav.siluetas";
```

y sustituir la línea 96 (`row.append(num, name, guide, blurb);`) por:

```ts
    /*
     * Silueta y golpe de luz: los añaden los tres temas y solo Hyprland les da
     * estilo (ver themes.css, `display: none` de base). Mismo patron que
     * `.scene-nav-trigger-mark`. `aria-hidden` en el envoltorio, no pieza a
     * pieza: la silueta es decorativa y ademas lleva fragmentos de copy
     * ("Aoshi Blanco Sanz", "Hablemos") que un lector de pantalla leeria
     * fuera de contexto y duplicados respecto al descriptor.
     */
    const shot = construirSilueta(entry.id);
    shot.setAttribute("aria-hidden", "true");

    const flash = document.createElement("span");
    flash.className = "scene-index-flash";
    flash.setAttribute("aria-hidden", "true");

    row.append(shot, flash, num, name, guide, blurb);
```

- [ ] **Step 4: Apagar los nodos nuevos en la hoja base**

En `src/themes/themes.css`, justo detrás del bloque de `.scene-nav-trigger-mark` (busca
`.scene-nav-trigger-mark {`), añadir:

```css
/*
 * `sceneNav.ts` añade la silueta y el golpe de luz en los TRES temas, pero solo
 * Hyprland los usa. Sin este `display: none` de base se cuelan en Vice y
 * Caelestia como hijos sueltos de una fila que es `display: flex` — mismo modo
 * de fallo que ya tuvo `.scene-nav-trigger-mark` (hallazgo M1 de la revision
 * final de rama del hero).
 */
.scene-shot,
.scene-index-flash {
  display: none;
}
```

- [ ] **Step 5: Verificar que Vice y Caelestia no se han movido**

Run:
```bash
export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH
npm run build && npm run lint
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
```
Expected: build y lint verdes. `--theme vice` con **0 fallos nuevos** (código de salida 0).
`--theme caelestia` con **exactamente los 9 fallos de contraste preexistentes** descritos en las
restricciones globales y ninguno más — ahí el código de salida es 1 en `main` también, así que un 1
no dice nada por sí solo: hay que leer la lista.

- [ ] **Step 6: Commit**

```bash
git add src/components/sceneNav.siluetas.ts src/components/sceneNav.ts src/themes/themes.css
git commit -m "feat(nav): siluetas de escena en el indice, apagadas fuera de Hyprland"
```

---

### Tarea 3: La hoja — rejilla, fotogramas y velo

**Files:**
- Modify: `src/themes/themes.css` (bloque nuevo de Hyprland)
- Create: `scripts/measure-cortinilla.py`

**Interfaces:**
- Consumes: `.scene-shot` y `.scene-index-flash` de la Tarea 2; `.scene-index-row`, `-num`,
  `-name`, `-blurb`, `-guide` de `sceneNav.ts`.
- Produces: la clase `.scene-index` en Hyprland como rejilla de 5 columnas, y el arnés
  `scripts/measure-cortinilla.py` con los subcomandos `layout` y `toque`, que las Tareas 4 y 5
  amplían.

- [ ] **Step 1: Escribir el arnés primero, y verlo fallar**

Crear `scripts/measure-cortinilla.py`. Este es el fichero completo de esta tarea (las Tareas 4 y 5
le añaden funciones):

```python
#!/usr/bin/env python3
"""Arnes de la hoja de contactos (cortinilla de Hyprland).

Criterios 3 y 4 del spec 2026-08-06-hyprland-cortinilla-hoja-design.md.
Se lanza contra el dev server o contra el build servido. NO usa capturas para
medir animacion: eso llega en la Tarea 4 y muestrea desde dentro de la pagina.
"""
import json
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:5173/?theme=hyprland"
CHROME = "/usr/bin/google-chrome"

LAYOUT_JS = """() => {
  const panel = document.querySelector('.scene-index');
  const filas = [...panel.querySelectorAll('.scene-index-row')];
  const r = e => { const b = e.getBoundingClientRect();
    return {w: Math.round(b.width), h: Math.round(b.height),
            t: Math.round(b.top), l: Math.round(b.left)}; };
  return {
    filas: filas.map(r),
    rejilla: r(panel),
    scrollInterno: panel.scrollHeight > panel.clientHeight + 1,
    desbordes: filas.map(f => { const b = f.querySelector('.scene-index-blurb');
      return b.scrollWidth > b.clientWidth; }),
    orderUsado: filas.some(f => getComputedStyle(f).order !== '0'),
    paradas: filas.length,
    siluetasVacias: filas.filter(f => {
      const s = f.querySelector('.scene-shot');
      return !s || s.children.length === 0; }).length,
    ariaOcultas: filas.every(f =>
      f.querySelector('.scene-shot')?.getAttribute('aria-hidden') === 'true'),
    ultimaEsContacto: filas[filas.length - 1]?.hash === '#contacto',
  };
}"""


def abrir(pw, ancho, alto, reducido=False):
    b = pw.chromium.launch(headless=True, executable_path=CHROME,
                           args=["--no-sandbox", "--use-gl=swiftshader"])
    ctx = b.new_context(viewport={"width": ancho, "height": alto},
                        reduced_motion="reduce" if reducido else "no-preference")
    pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded", timeout=40000)
    pg.wait_for_timeout(9000)  # encendido de Ascua + shader
    return b, pg


def abrir_cortinilla(pg):
    pg.click(".scene-nav-trigger")
    pg.wait_for_timeout(1200)


def medir_layout(ancho, alto):
    with sync_playwright() as pw:
        b, pg = abrir(pw, ancho, alto)
        abrir_cortinilla(pg)
        datos = pg.evaluate(LAYOUT_JS)
        caja = pg.locator(".scene-nav-trigger").bounding_box()
        b.close()
    datos["disparador"] = {"w": round(caja["width"], 1), "h": round(caja["height"], 1)}
    return datos


def comprobar(datos, ancho):
    fallos = []
    if datos["paradas"] != 5:
        fallos.append(f"{ancho}: hay {datos['paradas']} filas, deben ser 5")
    if datos["scrollInterno"]:
        fallos.append(f"{ancho}: el panel tiene scroll interno (prohibido, ver spec)")
    if any(datos["desbordes"]):
        fallos.append(f"{ancho}: descriptores desbordados: {datos['desbordes']}")
    if datos["orderUsado"]:
        fallos.append(f"{ancho}: se ha usado `order` en la rejilla (prohibido)")
    if datos["siluetasVacias"]:
        fallos.append(f"{ancho}: {datos['siluetasVacias']} siluetas vacias")
    if not datos["ariaOcultas"]:
        fallos.append(f"{ancho}: alguna silueta sin aria-hidden")
    if not datos["ultimaEsContacto"]:
        fallos.append(f"{ancho}: la ultima fila del DOM no es contacto")
    d = datos["disparador"]
    if d["w"] < 44 or d["h"] < 44:
        fallos.append(f"{ancho}: disparador {d['w']}x{d['h']}, minimo 44x44")
    return fallos


def main():
    fallos = []
    for ancho, alto in ((1440, 900), (390, 844)):
        datos = medir_layout(ancho, alto)
        print(f"== {ancho}x{alto}")
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        fallos += comprobar(datos, ancho)
    if fallos:
        print("\\nFALLOS:")
        for f in fallos:
            print(" -", f)
        return 1
    print("\\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verlo fallar**

Run (en una terminal el dev server, en otra el arnés — **y sin editar nada mientras corre**, que el
HMR de Vite se lleva por delante el contexto de la página):
```bash
export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH && npm run dev
```
```bash
python3 scripts/measure-cortinilla.py
```
Expected: FALLA. A 390 el panel arrastra scroll interno o los descriptores desbordan, y el
disparador aún no cumple 44 de alto en Hyprland. Anota los números que salen: son la línea de
partida.

- [ ] **Step 3: Escribir el CSS de la hoja**

En `src/themes/themes.css`, al final del bloque de Hyprland (busca
`:root[data-theme="hyprland"] .scene-nav-trigger` y trabaja debajo), añadir:

```css
/* ==========================================================================
   La hoja de contactos: el indice de escenas de Hyprland deja de ser cinco
   renglones y pasa a cinco fotogramas con la silueta de su escena.
   Spec: docs/superpowers/specs/2026-08-06-hyprland-cortinilla-hoja-design.md
   Cualquier selector va bajo [data-theme="hyprland"]: `.scene-index` es el mismo
   nodo en los tres temas y no hay `[data-scene]` que lo contenga.
   ========================================================================== */
:root[data-theme="hyprland"] .scene-index {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  align-content: center;
  justify-content: center;
  padding: 26px;
}

:root[data-theme="hyprland"] .scene-index-title {
  grid-column: 1 / -1;
  margin: 0 0 2px;
}

:root[data-theme="hyprland"] .scene-index-row {
  position: relative;
  display: block;
  overflow: hidden;
  padding: 0;
  border: 1px solid var(--rule);
  background: #070302;
}

:root[data-theme="hyprland"] .scene-index-row:hover,
:root[data-theme="hyprland"] .scene-index-row[aria-current="true"] {
  border-color: var(--l1);
}

/* El filete superior marca la escena en curso sin gastar color en el texto. */
:root[data-theme="hyprland"] .scene-index-row[aria-current="true"]::before {
  content: "";
  position: absolute;
  inset: -1px -1px auto;
  height: 2px;
  background: var(--l1);
  z-index: 6;
}

/* La guia punteada une dos extremos de una linea. Aqui no hay linea. */
:root[data-theme="hyprland"] .scene-index-guide {
  display: none;
}

/* El encuadre: 16:10, la proporcion de la pantalla del sitio, para que la
   silueta se lea como un plano y no como un icono. */
:root[data-theme="hyprland"] .scene-shot {
  display: block;
  position: relative;
  width: 100%;
  padding-top: 62.5%;
  overflow: hidden;
}

/* El plano se dibuja a 1440x900 y se escala. `--escala` la fija cada encuadre
   segun su ancho: 216/1440 en escritorio. No se calcula con JS. */
:root[data-theme="hyprland"] .scene-shot > span {
  position: absolute;
  transform-origin: 0 0;
}

/* La exposicion hace de navegacion: la escena en curso es la unica revelada. */
:root[data-theme="hyprland"] .scene-shot::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 5;
  background: var(--color-ink);
  opacity: 0.58;
  transition: opacity 200ms cubic-bezier(0.7, 0, 0.2, 1);
}

:root[data-theme="hyprland"] .scene-index-row[aria-current="true"] .scene-shot::after {
  opacity: 0;
}

:root[data-theme="hyprland"] .scene-index-row:hover .scene-shot::after {
  opacity: 0.05;
}

/* El pie del fotograma: numero, nombre y descriptor. El descriptor SIEMPRE
   visible, nunca solo en hover — es lo que cerro el hallazgo de que los
   nombres de cine no comunican, y en tactil no hay hover. */
:root[data-theme="hyprland"] .scene-index-num,
:root[data-theme="hyprland"] .scene-index-name,
:root[data-theme="hyprland"] .scene-index-blurb {
  position: static;
  display: block;
}
```

**Falta declarar el escalado y los colores del pie.** Eso es el Step 4: el escalado necesita saber
el ancho del encuadre, y el color del descriptor necesita medirse (criterio 7). No lo adivines
aquí.

- [ ] **Step 4: Declarar el escalado del plano y los colores del pie**

Añadir, en el mismo bloque:

```css
/* 1440 -> ancho del encuadre. En escritorio el encuadre mide 216px de ancho
   (rejilla de 1128 centrada en 1216 con paso 228), luego 216/1440 = 0.15.
   Se declara con un factor por encuadre y no con `zoom` ni con JS: `zoom` no
   se anima ni se hereda igual entre navegadores. */
:root[data-theme="hyprland"] .scene-shot {
  --escala: 0.15;
}

:root[data-theme="hyprland"] .scene-shot > span {
  transform: scale(var(--escala));
}

:root[data-theme="hyprland"] .scene-shot-rl,
:root[data-theme="hyprland"] .scene-shot-bar,
:root[data-theme="hyprland"] .scene-shot-dot {
  background: var(--haze);
  opacity: 0.5;
}

:root[data-theme="hyprland"] .scene-shot-box {
  border: 1px solid var(--rule);
}

:root[data-theme="hyprland"] .scene-shot-dot {
  border-radius: 50%;
}

:root[data-theme="hyprland"] .scene-shot-disp {
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: -0.032em;
  line-height: 0.94;
  white-space: nowrap;
  color: var(--color-paper);
}

/* El haz cruza los cinco encuadres: es lo unico que aparece en todas las
   escenas del sitio real, y es lo que hace que la hoja se lea como cinco
   planos de la misma pelicula en vez de cinco iconos. */
:root[data-theme="hyprland"] .scene-shot-beam {
  inset: 0;
  transform: none;
  background: linear-gradient(
    106deg,
    transparent 20%,
    rgba(255, 90, 52, 0.26) 34%,
    rgba(255, 90, 52, 0.4) 43%,
    rgba(224, 29, 60, 0.18) 56%,
    transparent 74%
  );
}
```

Y el pie. **El color de `.scene-index-blurb` se declara explícito y se mide** (criterio 7): el
descriptor ya era el ratio más ajustado del tema, 4,74:1 contra un umbral de 4,5, y aquí cambia de
superficie. Empieza por `var(--haze)` y compruébalo en el Step 7; si no llega, súbelo hacia
`var(--catch)`, **no** reutilices una opacidad de otro sitio.

```css
:root[data-theme="hyprland"] .scene-index-row > .scene-index-num {
  padding: 9px 11px 0;
  border-top: 1px solid var(--rule);
  /* `--t-1` (12px), no los 9,5px del prototipo: el criterio 11 exige que todo
     tamano sea un escalon declarado, y la escala de Ascua no baja de 12. El
     numero queda del mismo tamano que el descriptor, asi que lo que lo separa
     es el `letter-spacing` y el color, no el cuerpo. */
  font-size: var(--t-1);
  letter-spacing: 0.18em;
  color: var(--haze);
}

:root[data-theme="hyprland"] .scene-index-name {
  padding: 5px 11px 0;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--t-3);
  line-height: 1;
  letter-spacing: -0.034em;
  color: var(--color-paper);
  transition: color 200ms cubic-bezier(0.7, 0, 0.2, 1);
}

:root[data-theme="hyprland"] .scene-index-blurb {
  padding: 4px 11px 11px;
  font-size: var(--t-1);
  color: var(--haze);
}

:root[data-theme="hyprland"] .scene-index-row:hover .scene-index-name,
:root[data-theme="hyprland"] .scene-index-row[aria-current="true"] .scene-index-name,
:root[data-theme="hyprland"] .scene-index-row[aria-current="true"] > .scene-index-num {
  color: var(--l3);
}
```

**Tokens de Ascua, comprobados en `themes.css:1131-1144` — no inventes nombres.** El prototipo usaba
`--void`, `--text` y literales; en el repo **no existen**. Los reales son:

| prototipo | repo |
|---|---|
| `--void` | `--color-ink` (`#0b0404`) |
| `--text` | `--color-paper` (`#ffeae6`) |
| `--l1` `--l2` `--l3` `--catch` `--rule` `--haze` | iguales, existen tal cual |

Y la escala es `--t-1: 12px`, `--t-2: 16px`, `--t-3: 21.33px`, `--t-4: 28.43px`. El prototipo usaba
9,5 / 19 / 10,5 px, que no son escalones: el número y el descriptor suben a `--t-1` y el nombre a
`--t-3`. Es una desviación consciente del prototipo, exigida por el criterio 11.

- [ ] **Step 5: El layout de 390**

Añadir, al final del bloque:

```css
/* Dos, dos y la quinta a lo ancho. El quinto fotograma va el ULTIMO en el DOM
   y toma `grid-column: 1 / -1`: adelantarlo con `order` para "priorizar"
   contacto romperia la correspondencia entre el recorrido de Tab y lo que se
   ve (WCAG 2.4.3), y es facil caer en ello justo aqui. */
@media (max-width: 640px) {
  :root[data-theme="hyprland"] .scene-index {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 13px;
    padding: 56px 16px 16px;
    align-content: start;
  }

  :root[data-theme="hyprland"] .scene-index-row:last-of-type {
    grid-column: 1 / -1;
  }

  /* 172/1440 = 0.1194 para los cuatro de dos columnas; el quinto mide 356. */
  :root[data-theme="hyprland"] .scene-shot {
    --escala: 0.1194;
  }

  :root[data-theme="hyprland"] .scene-index-row:last-of-type .scene-shot {
    --escala: 0.2472;
    padding-top: 31.25%;
  }
}
```

- [ ] **Step 6: Correr el arnés hasta verde**

Run: `python3 scripts/measure-cortinilla.py`
Expected: `OK`, y en los números impresos: 5 filas; a 1440 los fotogramas rondan 216 de ancho; a
390, 172×197 los cuatro y 356×201 el quinto, rejilla de unos 621px sobre 844; sin scroll interno;
sin descriptores desbordados; sin `order`.

Los valores del spec son los del prototipo: **±10px es tolerancia razonable**, una desviación mayor
significa que el padding o el hueco no son los declarados. Si no cuadra, ajusta el CSS, no el arnés.

- [ ] **Step 7: Medir el contraste del pie**

Criterio 7. Sobre **píxel compuesto y con recorte ajustado al glifo**, no a la caja del bloque:
medir una caja ancha y casi vacía devuelve la variación del fondo y ya dio un falso 1,5:1 sobre un
texto que estaba en 7,9:1. Usa el mismo procedimiento que ya emplea `scripts/verify.py` para el
contraste (búscalo con `grep -n "contrast" scripts/verify.py`) y aplícalo a `.scene-index-num`,
`.scene-index-name` y `.scene-index-blurb` con la cortinilla abierta.

Umbral: ≥4,5:1 los tres. Si el descriptor no llega con `var(--haze)`, súbelo. Anota los tres
números: van al registro de implementación del spec.

- [ ] **Step 8: Los otros dos temas, intactos**

Run:
```bash
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
python3 scripts/verify.py --theme hyprland
```
Expected: los tres con 0 fallos nuevos sobre la línea base.

- [ ] **Step 9: Commit**

```bash
git add src/themes/themes.css scripts/measure-cortinilla.py
git commit -m "feat(nav): la cortinilla de Hyprland pasa a rejilla de cinco fotogramas"
```

---

### Tarea 4: El movimiento — barrido, exposición y cierre

**Files:**
- Modify: `src/themes/themes.css` (bloque de Hyprland)
- Modify: `src/components/sceneNav.ts:49-59` (un nodo nuevo: la barra)
- Modify: `scripts/measure-cortinilla.py` (añadir el muestreo del criterio 1)

**Interfaces:**
- Consumes: `.scene-index`, `.scene-index-row`, `.scene-index-flash` de las Tareas 2 y 3.
- Produces: `.scene-index-bar` (la barra de luz) en el DOM del panel, y la función
  `medir_sincronia()` en el arnés.

- [ ] **Step 1: Añadir la barra al panel**

En `src/components/sceneNav.ts`, tras el `panel.append(heading);` de la línea 59:

```ts
  /*
   * La barra de luz del barrido de apertura. Solo Hyprland la usa (ver
   * themes.css, `display: none` de base). Va al final del panel para que
   * quede por encima de los fotogramas sin necesidad de z-index alto.
   */
  const bar = document.createElement("span");
  bar.className = "scene-index-bar";
  bar.setAttribute("aria-hidden", "true");
```

y antes del `root.append(panel);` de la línea 234, añadir `panel.append(bar);`.

En `themes.css`, junto al `display: none` de base de la Tarea 2, añadir `.scene-index-bar` a la
lista de selectores.

- [ ] **Step 2: Ampliar el arnés con el muestreo de sincronía, y verlo fallar**

Añadir a `scripts/measure-cortinilla.py`:

```python
SINCRO_JS = """() => new Promise(res => {
  const panel = document.querySelector('.scene-index');
  const filas = [...panel.querySelectorAll('.scene-index-row')];
  const caja = panel.getBoundingClientRect();
  const pct = el => {
    const m = getComputedStyle(el).clipPath.match(/inset\\(([^)]*)\\)/);
    if (!m) return 0;
    const p = m[1].split(' ')[1];
    return p ? parseFloat(p) : 0;
  };
  const out = [];
  const t0 = performance.now();
  document.querySelector('.scene-nav-trigger').click();
  function tick() {
    const t = performance.now() - t0;
    const borde = caja.width * (1 - pct(panel) / 100);
    let cont = null;
    for (const f of filas) {
      const rp = pct(f);
      if (rp >= 99.9) continue;            // aun sin revelar: no es contenido
      const r = f.getBoundingClientRect();
      const x = (r.left - caja.left) + r.width * (1 - rp / 100);
      if (cont === null || x > cont) cont = x;
    }
    out.push({t: Math.round(t), borde: Math.round(borde),
              cont: cont === null ? null : Math.round(cont)});
    if (t < 620) requestAnimationFrame(tick); else res(out);
  }
  requestAnimationFrame(tick);
})"""


def medir_sincronia():
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900)
        filas = pg.evaluate(SINCRO_JS)
        b.close()
    adelantos = [f["cont"] - f["borde"] for f in filas if f["cont"] is not None]
    return max(adelantos) if adelantos else None
```

y en `main()`, antes del `if fallos:`:

```python
    adelanto = medir_sincronia()
    print(f"\\nadelanto maximo del contenido sobre la barra: {adelanto} px")
    if adelanto is None:
        fallos.append("sincronia: no se midio ni un fotograma revelandose")
    elif adelanto > 0:
        fallos.append(f"sincronia: el contenido adelanta a la barra {adelanto}px (debe ser <= 0)")
```

Run: `python3 scripts/measure-cortinilla.py`
Expected: FALLA en sincronía.

**Aviso, medido al ejecutar esta tarea: ese rojo no sale.** La transición compartida recorta en
vertical (`inset(0 0 100% 0)`), así que no hay información horizontal que comparar y la aserción
no puede dar positivo por ausencia de datos, no por acierto. Un rojo que no llega no es prueba de
nada, pero tampoco lo es cambiar la aserción hasta que salga.

Lo que sí demuestra que el arnés caza lo que dice cazar: **forzar el modo de fallo real**. Cambia
temporalmente la curva de apertura de `linear` a `cubic-bezier(.7,0,.2,1)` —que es la causa número
uno de un adelanto positivo, según el propio Step 5— y vuelve a medir. Debe dar un adelanto
claramente positivo (al ejecutarlo salió **+193 px**). Restaura el CSS después y comprueba con
`diff` que quedó idéntico.

- [ ] **Step 3: Escribir el movimiento**

En `themes.css`, en el bloque de Hyprland:

```css
/* --------------------------------------------------------------------------
   Movimiento de la hoja.

   La APERTURA va `linear` y es deliberado: el borde del telon ES la barra, y
   una barra de luz que cruza es un instrumento fisico a velocidad constante;
   con la curva de corte del tema frenaria al llegar al borde y volveria a
   leerse como un panel de interfaz. El instrumento va lineal; los EVENTOS que
   provoca (exposicion, golpe de luz, cierre) llevan cubic-bezier(.7,0,.2,1).
   Es la unica desviacion de la tabla de movimiento de Ascua: no la "corrijas".
   -------------------------------------------------------------------------- */
:root[data-theme="hyprland"] .scene-index {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 200ms cubic-bezier(0.7, 0, 0.2, 1);
}

:root[data-theme="hyprland"] .scene-index.is-open {
  clip-path: inset(0 0 0 0);
  transition: clip-path 480ms linear;
}

:root[data-theme="hyprland"] .scene-index-bar {
  display: block;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 2px;
  background: var(--l3);
  box-shadow: 0 0 22px 6px rgba(255, 90, 52, 0.55);
  opacity: 0;
  pointer-events: none;
}

/* En % del mismo eje que el recorte, no en px: con un valor fijo la barra y el
   borde de revelado se despegan en cuanto cambia el ancho de pantalla. */
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-bar {
  animation: hypr-barrido 480ms linear forwards;
}

@keyframes hypr-barrido {
  0% { left: 0; opacity: 1; }
  82% { opacity: 1; }
  100% { left: 100%; opacity: 0; }
}

/* Cada fotograma se expone AL PASO de la barra. Los retardos no son un ritmo
   elegido a ojo: son el momento en que la barra llega a su borde izquierdo.

   Geometria REAL, medida (no la del prototipo): `.scene-index` es
   `position: fixed; inset: 0`, o sea 1440 de ancho en escritorio, no los 1216
   del prototipo. Con `padding: 26px` y `gap: 12px`, el contenido mide 1388 y
   cada fotograma (1388 - 4*12) / 5 = 268, con paso 280. Bordes izquierdos:
   26, 306, 586, 866, 1146. La barra recorre 1440px en 480ms = 3,0 px/ms:
     26->9   306->102   586->195   866->289   1146->382.

   Estos retardos son fijos en ms y la rejilla es fluida, asi que solo son
   exactos a 1440. Medida la deriva: a 1024 los bordes caen en las fracciones
   0,025 / 0,218 / 0,410 / 0,602 / 0,794 frente a 0,018 / 0,213 / 0,407 /
   0,601 / 0,796 a 1440 — menos de 0,008 del ancho, es decir **por debajo de
   4ms**. No compensa complicarlo.

   Cada exposicion dura 140ms mientras la barra tarda 268/3 = 89ms en cruzar un
   fotograma, asi que el revelado ASIENTA por detras del instrumento y nunca
   por delante. Verificado por scripts/measure-cortinilla.py. */
:root[data-theme="hyprland"] .scene-index-row {
  clip-path: inset(0 100% 0 0);
  transition:
    clip-path 110ms cubic-bezier(0.7, 0, 0.2, 1),
    border-color 200ms cubic-bezier(0.7, 0, 0.2, 1);
}

:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row {
  clip-path: inset(0 0 0 0);
  transition:
    clip-path 140ms cubic-bezier(0.7, 0, 0.2, 1),
    border-color 200ms cubic-bezier(0.7, 0, 0.2, 1);
}

:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(1) { transition-delay: 9ms, 0ms; }
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(2) { transition-delay: 102ms, 0ms; }
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(3) { transition-delay: 195ms, 0ms; }
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(4) { transition-delay: 289ms, 0ms; }
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(5) { transition-delay: 382ms, 0ms; }

/* Cierre: orden INVERSO, se apaga primero el ultimo que se encendio. El
   contenido se va antes que la sabana (110ms escalonados 20 = 190ms, dentro
   de los 200 del telon). Salir nunca es ceremonia. */
:root[data-theme="hyprland"] .scene-index-row:nth-of-type(1) { transition-delay: 80ms, 0ms; }
:root[data-theme="hyprland"] .scene-index-row:nth-of-type(2) { transition-delay: 60ms, 0ms; }
:root[data-theme="hyprland"] .scene-index-row:nth-of-type(3) { transition-delay: 40ms, 0ms; }
:root[data-theme="hyprland"] .scene-index-row:nth-of-type(4) { transition-delay: 20ms, 0ms; }
:root[data-theme="hyprland"] .scene-index-row:nth-of-type(5) { transition-delay: 0ms, 0ms; }

/* El golpe de luz: sobreexpone y asienta. No es brillo decorativo — es el
   unico momento en que el fotograma dice "acabo de revelarse", que es
   literalmente lo que hace una hoja de contactos. */
:root[data-theme="hyprland"] .scene-index-flash {
  display: block;
  position: absolute;
  inset: 0;
  z-index: 8;
  pointer-events: none;
  opacity: 0;
  background: linear-gradient(106deg, rgba(255, 160, 110, 0.55), rgba(255, 90, 52, 0.22));
}

:root[data-theme="hyprland"] .scene-index.is-open .scene-index-flash {
  animation: hypr-exposicion 300ms cubic-bezier(0.7, 0, 0.2, 1) forwards;
}

:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(1) .scene-index-flash { animation-delay: 9ms; }
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(2) .scene-index-flash { animation-delay: 102ms; }
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(3) .scene-index-flash { animation-delay: 195ms; }
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(4) .scene-index-flash { animation-delay: 289ms; }
:root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(5) .scene-index-flash { animation-delay: 382ms; }

@keyframes hypr-exposicion {
  from { opacity: 1; }
  to { opacity: 0; }
}
```

- [ ] **Step 4: Movimiento reducido**

El bloque `@media (prefers-reduced-motion: reduce)` que ya existe (busca
`.scene-index.is-open .scene-index-row:nth-of-type(1)` dentro de una media query) **no alcanza a
estos selectores**: los de Hyprland pesan más porque llevan `:root[data-theme]` delante. Es
exactamente el fallo que ya se pagó una vez —duración 0 con los retardos intactos, cinco chasquidos
escalonados en vez de una aparición— y aquí volvería a pasar.

Añadir un bloque propio:

```css
/*
 * La barra de luz NO se acelera: se retira. Un elemento que atraviesa la
 * pantalla es en si mismo el efecto de movimiento, no solo su duracion —
 * a 1ms sigue siendo algo que cruza la pantalla a ojos de quien pidio
 * `reduce`. Se degrada el viaje, nunca la funcion: foco, Esc, clic fuera y
 * bloqueo de scroll no cambian, son logica de sceneNav.ts.
 */
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .scene-index,
  :root[data-theme="hyprland"] .scene-index.is-open,
  :root[data-theme="hyprland"] .scene-index .scene-index-row,
  :root[data-theme="hyprland"] .scene-index.is-open .scene-index-row,
  :root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(1),
  :root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(2),
  :root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(3),
  :root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(4),
  :root[data-theme="hyprland"] .scene-index.is-open .scene-index-row:nth-of-type(5) {
    transition: none;
    transition-delay: 0ms;
  }

  :root[data-theme="hyprland"] .scene-index-bar,
  :root[data-theme="hyprland"] .scene-index.is-open .scene-index-bar {
    display: none;
    animation: none;
  }

  :root[data-theme="hyprland"] .scene-index-flash,
  :root[data-theme="hyprland"] .scene-index.is-open .scene-index-flash {
    animation: none;
    opacity: 0;
  }
}
```

- [ ] **Step 5: Correr el arnés hasta verde**

Run: `python3 scripts/measure-cortinilla.py`
Expected: `OK`, y el adelanto máximo del contenido sobre la barra **≤ 0** (en el prototipo salió
−15 px; se espera algo parecido).

Si sale positivo, el error casi seguro es uno de estos dos: la rejilla no mide 1128 centrada en
1216 —y entonces los retardos ya no corresponden a la geometría— o alguien puso la apertura del
telón con curva en vez de `linear`. Recalcula los retardos con la geometría real, no los ajustes a
ojo hasta que pase.

- [ ] **Step 6: Comprobar los tiempos declarados y el movimiento reducido**

Criterios 2 y 10. Lo que se comprueba es la duración **declarada**, que es determinista. Un
cronómetro desde el clic mide la carga de la máquina, no la animación: el spec anterior lo pagó con
609–684 ms medidos sobre una animación declarada en 460.

Añadir a `scripts/measure-cortinilla.py`:

```python
TIEMPOS_JS = """() => {
  const panel = document.querySelector('.scene-index');
  const fila = panel.querySelector('.scene-index-row');
  const flash = panel.querySelector('.scene-index-flash');
  const bar = panel.querySelector('.scene-index-bar');
  const trig = document.querySelector('.scene-nav-trigger');
  const nom = trig.querySelector('.scene-nav-trigger-name-a');
  const cs = e => getComputedStyle(e);
  return {
    telonAbierto: cs(panel).transitionDuration,
    telonCurva: cs(panel).transitionTimingFunction,
    fila: cs(fila).transitionDuration,
    filaRetardo: cs(fila).transitionDelay,
    flash: cs(flash).animationDuration,
    barra: cs(bar).animationDuration,
    barraCurva: cs(bar).animationTimingFunction,
    barraDisplay: cs(bar).display,
    rotulo: nom ? cs(nom).transitionDuration : null,
  };
}"""

# Con `.is-open` puesto. La curva del telon abierto es `linear` a proposito:
# el borde del telon ES la barra, y un instrumento fisico va a velocidad
# constante (ver el comentario del bloque en themes.css).
TIEMPOS_ESPERADOS = {
    "telonAbierto": "0.48s",
    "telonCurva": "linear",
    "fila": "0.14s, 0.2s",
    "filaRetardo": "0.009s, 0s",
    "flash": "0.3s",
    "barra": "0.48s",
    "barraCurva": "linear",
}


def medir_tiempos(reducido):
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900, reducido=reducido)
        abrir_cortinilla(pg)
        datos = pg.evaluate(TIEMPOS_JS)
        # Con la cortinilla abierta, Tab debe seguir dando cinco paradas.
        paradas = pg.evaluate(
            "() => document.querySelectorAll('.scene-index .scene-index-row').length"
        )
        b.close()
    datos["paradas"] = paradas
    return datos


def comprobar_tiempos(datos, reducido):
    fallos = []
    if reducido:
        if datos["telonAbierto"] not in ("0s", "0ms"):
            fallos.append(f"reducido: el telon dura {datos['telonAbierto']}, debe ser 0s")
        if datos["filaRetardo"].replace(" ", "") not in ("0s,0s", "0ms,0ms"):
            fallos.append(f"reducido: retardos vivos ({datos['filaRetardo']})")
        if datos["barraDisplay"] != "none":
            fallos.append("reducido: la barra de luz sigue existiendo (debe retirarse, no acelerarse)")
        if datos["paradas"] != 5:
            fallos.append(f"reducido: {datos['paradas']} filas, la funcion no puede degradarse")
    else:
        for k, v in TIEMPOS_ESPERADOS.items():
            real = datos[k].replace(" ", "") if isinstance(datos[k], str) else datos[k]
            if real != v.replace(" ", ""):
                fallos.append(f"tiempos: {k} = {datos[k]}, declarado {v}")
    return fallos
```

y en `main()`, antes del `if fallos:`:

```python
    for reducido in (False, True):
        d = medir_tiempos(reducido)
        print(f"\\n== tiempos ({'reducido' if reducido else 'normal'})")
        print(json.dumps(d, indent=2, ensure_ascii=False))
        fallos += comprobar_tiempos(d, reducido)
```

Run: `python3 scripts/measure-cortinilla.py`
Expected: `OK` en las dos pasadas.

Si `fila` sale como `0.14s, 0.2s` pero el arnés se queja del orden, es que en el CSS declaraste
`border-color` antes que `clip-path` en el `transition`. El orden importa: los retardos van
posicionales.

- [ ] **Step 7: Commit**

```bash
git add src/components/sceneNav.ts src/themes/themes.css scripts/measure-cortinilla.py
git commit -m "feat(nav): barrido de exposicion y cierre en cascada inversa de la hoja"
```

---

### Tarea 5: El disparador T-C

**Files:**
- Modify: `src/components/sceneNav.ts:40-42` y `:196-211` (`pinta`)
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-cortinilla.py`

**Interfaces:**
- Consumes: `trigger`, `triggerLabel` y `pinta(i)` existentes.
- Produces: `.scene-nav-trigger-tc` con cuatro spans:
  `.scene-nav-trigger-num-a`, `-num-b`, `-name-a`, `-name-b`.

- [x] **Step 1: Añadir la estructura de dos estados**

En `src/components/sceneNav.ts`, tras el `trigger.append(triggerLabel);` de la línea 42:

```ts
  /*
   * Disparador de Hyprland: el pie de un fotograma, con dos estados. La
   * estructura se añade en los tres temas y solo Hyprland le da estilo (ver
   * themes.css). Vice y Caelestia siguen con `.scene-nav-trigger-label`.
   *
   * El rotulo NO se funde entre estados: se corta y sube, que es la gramatica
   * del tema. Por eso hacen falta las dos versiones en el DOM a la vez, y por
   * eso el cambio lo hace el CSS y no este modulo: JS solo mantiene la parte
   * que depende de la escena.
   */
  const tc = document.createElement("span");
  tc.className = "scene-nav-trigger-tc";
  tc.setAttribute("aria-hidden", "true"); // el nombre accesible lo da `.scene-nav-trigger-label`

  const tcNumA = document.createElement("span");
  tcNumA.className = "scene-nav-trigger-num-a";

  const tcNumB = document.createElement("span");
  tcNumB.className = "scene-nav-trigger-num-b";
  tcNumB.textContent = "Esc";

  const tcNameA = document.createElement("span");
  tcNameA.className = "scene-nav-trigger-name-a";

  const tcNameB = document.createElement("span");
  tcNameB.className = "scene-nav-trigger-name-b";
  tcNameB.textContent = "Cerrar";

  tc.append(tcNumA, tcNumB, tcNameA, tcNameB);
  trigger.append(tc);
```

`aria-hidden` en `tc` es deliberado: duplicaría el rótulo que ya anuncia
`.scene-nav-trigger-label`, y `aria-expanded` ya dice el estado. El lector de pantalla no pierde
nada; quien mira, gana.

- [x] **Step 2: Alimentarlo desde `pinta`**

Dentro de `pinta`, junto a la línea que fija `triggerLabel.textContent` (línea 206), añadir:

```ts
    // Las versiones "b" son estaticas ("Esc"/"Cerrar"): el CSS decide cual se
    // ve. Aqui solo va lo que depende de la escena.
    tcNumA.textContent = n;
    tcNameA.textContent = TARGETS[i].label;
```

No toques la línea de `triggerLabel`: Vice y Caelestia dependen de ella.

- [x] **Step 3: Escribir el CSS del disparador**

En `themes.css`, **sustituyendo** el bloque actual de cuatro líneas de
`:root[data-theme="hyprland"] .scene-nav-trigger` (líneas ~2119-2131, el que dice "Radio 5px
heredado: la navegacion es la unica excepcion al radio 0 del tema"):

```css
/*
 * El disparador de Hyprland: el pie de un fotograma. Sin caja.
 *
 * Se retira la excepcion de radio del spec de Ascua ("radio 0 en todo salvo la
 * navegacion"): esa excepcion se escribio para proteger una pastilla concreta,
 * y con la hoja de contactos la pastilla deja de existir. El tema se queda sin
 * su unica contradiccion interna.
 *
 * Los 44px de area de toque los da `min-height`, no una caja visible. Se mide
 * la caja del BOTON: un `::after` con `inset` negativo agranda la zona
 * clicable pero no mueve lo que el criterio mide.
 */
:root[data-theme="hyprland"] .scene-nav-trigger {
  display: block;
  min-width: 6.5rem;
  min-height: 44px;
  padding: 9px 0 5px;
  border-radius: 0;
  background: none;
  box-shadow: none;
  text-align: right;
}

:root[data-theme="hyprland"] .scene-nav-trigger:hover {
  background: none;
}

:root[data-theme="hyprland"] .scene-nav-trigger[aria-expanded="true"] {
  background: none;
}

/* El filete de arriba se calienta de DERECHA a izquierda: el mismo sentido en
   el que el disparador esta anclado. */
:root[data-theme="hyprland"] .scene-nav-trigger::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 1px;
  background: var(--rule);
}

:root[data-theme="hyprland"] .scene-nav-trigger::after {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 1px;
  background: linear-gradient(90deg, var(--l2), var(--l3));
  box-shadow: 0 0 8px 1px rgba(255, 90, 52, 0.7);
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 320ms cubic-bezier(0.7, 0, 0.2, 1);
}

:root[data-theme="hyprland"] .scene-nav-trigger:hover::after,
:root[data-theme="hyprland"] .scene-nav-trigger:focus-visible::after,
:root[data-theme="hyprland"] .scene-nav-trigger[aria-expanded="true"]::after {
  transform: scaleX(1);
}

/* En Hyprland el rotulo compartido deja el sitio a la version de dos estados,
   pero NO se quita del DOM: es el nombre accesible del boton. */
:root[data-theme="hyprland"] .scene-nav-trigger-label {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

:root[data-theme="hyprland"] .scene-nav-trigger-tc {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 12px 22px;
  row-gap: 4px;
  justify-items: end;
  overflow: hidden;
}

/* Las dos versiones ocupan la MISMA celda: se apilan y una sube tapando a la
   otra. Nada de `opacity`: el corte es la gramatica del tema. */
:root[data-theme="hyprland"] .scene-nav-trigger-num-a,
:root[data-theme="hyprland"] .scene-nav-trigger-num-b {
  grid-row: 1;
  grid-column: 1;
  font-size: var(--t-1);
  line-height: 12px;
  letter-spacing: 0.18em;
  color: var(--haze);
  transition: transform 200ms cubic-bezier(0.7, 0, 0.2, 1);
}

:root[data-theme="hyprland"] .scene-nav-trigger-name-a,
:root[data-theme="hyprland"] .scene-nav-trigger-name-b {
  grid-row: 2;
  grid-column: 1;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--t-3);
  line-height: 22px;
  letter-spacing: -0.034em;
  text-transform: none;
  color: var(--color-paper);
  transition:
    transform 200ms cubic-bezier(0.7, 0, 0.2, 1),
    color 200ms cubic-bezier(0.7, 0, 0.2, 1);
}

:root[data-theme="hyprland"] .scene-nav-trigger-num-b,
:root[data-theme="hyprland"] .scene-nav-trigger-name-b {
  transform: translateY(100%);
}

:root[data-theme="hyprland"] .scene-nav-trigger[aria-expanded="true"] .scene-nav-trigger-num-a,
:root[data-theme="hyprland"] .scene-nav-trigger[aria-expanded="true"] .scene-nav-trigger-name-a {
  transform: translateY(-100%);
}

:root[data-theme="hyprland"] .scene-nav-trigger[aria-expanded="true"] .scene-nav-trigger-num-b,
:root[data-theme="hyprland"] .scene-nav-trigger[aria-expanded="true"] .scene-nav-trigger-name-b {
  transform: translateY(0);
}

:root[data-theme="hyprland"] .scene-nav-trigger:hover .scene-nav-trigger-name-a,
:root[data-theme="hyprland"] .scene-nav-trigger[aria-expanded="true"] .scene-nav-trigger-name-b {
  color: var(--l3);
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .scene-nav-trigger::after,
  :root[data-theme="hyprland"] .scene-nav-trigger-num-a,
  :root[data-theme="hyprland"] .scene-nav-trigger-num-b,
  :root[data-theme="hyprland"] .scene-nav-trigger-name-a,
  :root[data-theme="hyprland"] .scene-nav-trigger-name-b {
    transition: none;
  }
}
```

Ojo con `position`: `.scene-nav-trigger` base es `position: fixed`, así que los pseudo-elementos ya
tienen contenedor. No añadas `position: relative`, que rompería el `top: 0; right: 3rem` heredado.

- [x] **Step 4: Ampliar el arnés con los dos estados y el foco**

Criterios 4 y 5. Añadir a `scripts/measure-cortinilla.py`:

```python
# Que version del rotulo se ve se decide por POSICION, no leyendo el
# `transform`: `getComputedStyle` devuelve una matriz y compararla es fragil.
# Un span se ve si su caja cae dentro de la de su celda.
ESTADO_JS = """() => {
  const trig = document.querySelector('.scene-nav-trigger');
  const tc = trig.querySelector('.scene-nav-trigger-tc');
  const caja = tc.getBoundingClientRect();
  const dentro = sel => {
    const e = trig.querySelector(sel);
    if (!e) return null;
    const b = e.getBoundingClientRect();
    return b.top >= caja.top - 2 && b.bottom <= caja.bottom + 2;
  };
  return {
    expanded: trig.getAttribute('aria-expanded'),
    numA: dentro('.scene-nav-trigger-num-a'),
    numB: dentro('.scene-nav-trigger-num-b'),
    nameA: dentro('.scene-nav-trigger-name-a'),
    nameB: dentro('.scene-nav-trigger-name-b'),
    textoA: trig.querySelector('.scene-nav-trigger-name-a')?.textContent,
    textoB: trig.querySelector('.scene-nav-trigger-name-b')?.textContent,
  };
}"""


def medir_estados_y_foco():
    with sync_playwright() as pw:
        b, pg = abrir(pw, 1440, 900)
        cerrado = pg.evaluate(ESTADO_JS)
        abrir_cortinilla(pg)
        abierto = pg.evaluate(ESTADO_JS)

        # Criterio 5: Tab da exactamente cinco paradas y vuelve a la primera.
        visitados = []
        for _ in range(6):
            visitados.append(pg.evaluate(
                "() => document.activeElement?.getAttribute('href') ?? null"))
            pg.keyboard.press("Tab")
            pg.wait_for_timeout(60)
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(400)
        tras_esc = pg.evaluate(
            "() => document.activeElement?.classList.contains('scene-nav-trigger') ?? false")
        b.close()
    return cerrado, abierto, visitados, tras_esc


def comprobar_estados(cerrado, abierto, visitados, tras_esc):
    fallos = []
    if cerrado["expanded"] != "false" or abierto["expanded"] != "true":
        fallos.append("aria-expanded no conmuta")
    if not (cerrado["numA"] and cerrado["nameA"]):
        fallos.append("cerrado: no se ve la version de escena del rotulo")
    if cerrado["numB"] or cerrado["nameB"]:
        fallos.append("cerrado: se ve la version 'Esc / Cerrar'")
    if not (abierto["numB"] and abierto["nameB"]):
        fallos.append("abierto: no se ve 'Esc / Cerrar'")
    if abierto["numA"] or abierto["nameA"]:
        fallos.append("abierto: se sigue viendo la version de escena")
    if abierto["textoB"] != "Cerrar":
        fallos.append(f"el rotulo abierto dice {abierto['textoB']!r}, debe decir 'Cerrar'")
    unicos = [v for v in visitados[:5] if v]
    if len(set(unicos)) != 5:
        fallos.append(f"Tab no da cinco paradas distintas: {visitados}")
    if visitados[5] != visitados[0]:
        fallos.append(f"Tab no vuelve a la primera fila: {visitados}")
    if not tras_esc:
        fallos.append("tras Esc el foco no vuelve al disparador")
    return fallos
```

y en `main()`, antes del `if fallos:`:

```python
    c, a, v, esc = medir_estados_y_foco()
    print("\\n== disparador y foco")
    print(json.dumps({"cerrado": c, "abierto": a, "tab": v, "escDevuelveFoco": esc},
                     indent=2, ensure_ascii=False))
    fallos += comprobar_estados(c, a, v, esc)
```

- [x] **Step 5: Correr todo**

Run:
```bash
python3 scripts/measure-cortinilla.py
python3 scripts/measure-nav.py
python3 scripts/measure-type-scale.py
export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH && npm run build && npm run lint
```
Expected: `measure-cortinilla` OK; `measure-nav` 15 de 15 a ±8 px en los tres temas;
`measure-type-scale` con 0 fallos nuevos; build y lint verdes.

- [x] **Step 6: Commit**

```bash
git add src/components/sceneNav.ts src/themes/themes.css scripts/measure-cortinilla.py
git commit -m "feat(nav): el disparador de Hyprland pasa a pie de fotograma con dos estados"
```

---

### Tarea 6: Verificación de cierre y registro

**Files:**
- Modify: `docs/superpowers/specs/2026-08-06-hyprland-cortinilla-hoja-design.md` (estado y registro)
- Modify: `scripts/verify-baseline.json` (solo si procede, ver Step 3)

- [x] **Step 1: Los tres temas y la pasada reducida**

Run:
```bash
python3 scripts/verify.py --theme hyprland
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
python3 scripts/verify.py --theme hyprland --reduced
```
Expected: `hyprland`, `hyprland --reduced` y `vice` con **0 fallos nuevos** sobre la línea base.
Ojo: `hyprland` sale con **código 1 aunque no haya fallos nuevos**, por deriva preexistente de la
base (tres fixtures de `vice-hero` que figuran como "arreglados"); pasa igual en `main`. Ese es el
caso que el Step 3 resuelve con `--update-baseline`.
`caelestia` con exactamente los 9 fallos de contraste preexistentes y ninguno más.
**Vice está cerrado y aceptado: cualquier diferencia ahí es un defecto de este trabajo, no una
línea base que actualizar.**

- [x] **Step 2: Capturas reales**

Con el **build de producción servido**, no con `npm run dev` (el HMR de Vite corrompe las medidas de
ScrollTrigger y miente en los dos sentidos):

```bash
export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH
npm run build && npm run preview
```

Capturar 1440×900 y 390×844 con `?theme=hyprland`, cortinilla cerrada y abierta. Cuatro imágenes.

- [x] **Step 3: Línea base**

Si arreglaste algún fallo que estaba **en** `scripts/verify-baseline.json`, hay que quitarlo de la
base o el arnés sale en rojo a propósito:

```bash
python3 scripts/verify.py --update-baseline
git diff scripts/verify-baseline.json   # revisar ANTES de commitear
```

Si no arreglaste ninguno, no toques el fichero.

**Lo que pasó de verdad, y por qué el Step partía de una premisa falsa.** Los 3 fixtures de
`vice-hero` NO estaban arreglados: `check_fixture_assets()` vivía dentro del bloque
`if theme == "vice"`, así que en hyprland y caelestia esa comprobación no se ejecutaba y el arnés
la leía como "arreglada" contra una línea base que es una lista plana común a los tres temas.
`--update-baseline` desde una pasada de hyprland habría reescrito el fichero con los 9 fallos de
esa pasada y **borrado las 12 entradas reales**. La línea base no se toca; lo que se movió es la
llamada, que no depende del tema. Resultado: hyprland pasa a **exit 0** por primera vez.

- [x] **Step 4: Cerrar el spec**

En `docs/superpowers/specs/2026-08-06-hyprland-cortinilla-hoja-design.md`:
- cambiar `Estado: pendiente de plan` por `Estado: implementado`
- añadir una sección `## Registro de implementación` con: los tres ratios de contraste medidos en la
  Tarea 3 Step 7, el adelanto máximo medido en la Tarea 4, las medidas reales a 390, y cualquier
  divergencia entre lo planeado y lo hecho.

**El spec no puede decir `implementado` con casillas de este plan sin marcar**:
`check_spec_plan_consistency()` en `verify.py` lo cruza y falla. Marca las casillas conforme
avanzas, no en bloque al final.

- [ ] **Step 5: Gates**

Lanzar `lidia-naive-tester` y `vera-art-director` (umbral 7,5/10), **pineados a Sonnet**
(`CLAUDE.md` regla 3: los subagentes heredan el modelo de la sesión).

A `lidia-naive-tester` hay que pedirle explícitamente que mida **tiempo hasta la primera pulsación
correcta** sobre la rejilla, no solo una impresión estética: el riesgo abierto del spec es que cinco
miniaturas compitiendo ralenticen el escaneo, y eso no se ve en una captura.

- [ ] **Step 6: Revisión de Aoshi sobre el sitio real**

Sobre el sitio, haciendo scroll y abriendo la cortinilla. No sobre capturas.

- [ ] **Step 7: Commit final**

```bash
git add docs/superpowers/specs/2026-08-06-hyprland-cortinilla-hoja-design.md docs/superpowers/plans/2026-08-06-hyprland-cortinilla-hoja.md
git commit -m "docs(nav): cerrar la hoja de contactos con el registro de implementacion"
```

---

## Si algo se tuerce

- **El golpe de luz se lee como efecto gratuito.** Está previsto en el spec: es la pieza más
  prescindible del conjunto y quitarla no rompe nada. Borra el bloque de `.scene-index-flash` y
  anótalo en el registro.
- **A 390 no cabe.** Reduce proporción o hueco. **No** metas scroll dentro del panel: un contenedor
  con scroll propio mientras Lenis está bloqueado a nivel de documento es superficie que el doble
  cerrojo actual no cubre, y en iOS el gesto táctil se filtra a la página de detrás pese al
  `overflow: hidden`. Si no hubiera más remedio, exige `overscroll-behavior: contain`.
- **El descriptor no llega a 4,5:1.** Súbelo hacia `var(--catch)`. **No** reutilices una opacidad
  de otro tema ni de otra superficie: una opacidad se calibra contra el scrim concreto sobre el que
  se mide, y esa regla ya está escrita en `CLAUDE.md`.
- **Algo se movió en Vice o Caelestia.** Es una fuga de selector. Busca la regla nueva que no lleva
  `:root[data-theme="hyprland"]`. Para comparar contra HEAD usa `git worktree add`, **nunca**
  `git stash`: un `stash --include-untracked` ya se llevó por delante una sesión entera.
