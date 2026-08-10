# La placa — "Quién soy" en Hyprland · plan de implementación

> **Para quien ejecute esto:** SUB-SKILL OBLIGATORIA: usar
> `superpowers:subagent-driven-development` (recomendada) o
> `superpowers:executing-plans` para implementar tarea a tarea. Los pasos usan
> casillas (`- [ ]`) para el seguimiento, y hay que marcarlas **al completar cada
> paso**, no al final (`.claude/rules/speckit-progress-tracking.md`).

**Objetivo:** convertir `[data-scene="about"]` en el tema Hyprland en una placa de
características de siete celdas que ocupa el encuadre, sin tocar el contenido ni los otros dos
temas.

**Arquitectura:** patrón aditivo estricto, el mismo que usó el bloque de parejas de Vice. Los nodos
nuevos se construyen en `src/sections/about.ts` para los tres temas y se envían **ocultos** desde
la regla base; solo `:root[data-theme="hyprland"]` los enciende. La composición vive en CSS
(rejilla de 6×3); la coreografía reparte clases y decide *cuándo*, nunca *cuánto* dura.

**Stack:** Vite + TypeScript estricto + CSS propio en `src/themes/themes.css` + GSAP/ScrollTrigger
ya presentes. Sin dependencias nuevas.

**Spec:** `docs/superpowers/specs/2026-08-10-hyprland-quien-soy-placa-design.md`
**Prototipo aprobado:** `.superpowers/brainstorm/1961497-1786322787/content/ficha-b.html`

## Restricciones globales

- **Solo Hyprland.** Vice está cerrado desde el 2026-08-05 y no se toca. Caelestia no se toca: se
  comprueba que sigue idéntico.
- **`src/data/content.ts` no cambia.** Ni una cadena nueva. Si algo hace falta y no está, se para y
  se pregunta.
- **Todo nodo nuevo lleva `display: none` en la regla base compartida** de `themes.css`. Se ha
  pagado cuatro veces; la última ensanchó el disparador de Vice de 168 a 411 px.
- **Nunca `gsap.from`.** `fromTo` con los dos extremos escritos a mano. `Array.from(...)` para
  colecciones vivas.
- **Nada de `clamp()` sobre tokens de escala.** Escalones discretos por `@container`.
- **Dos regímenes de tiempo y ningún tercero:** corte 420 ms `--hard`
  (`cubic-bezier(0.7,0,0.2,1)`), atmósfera 900 ms `--slow` (`cubic-bezier(0.16,0.84,0.28,1)`),
  escalonado 70 ms.
- **`prefers-reduced-motion` nunca deja nada invisible.**
- **Cero `console.log`.** Cero `any`.
- Node 22 obligatorio: `export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH`.
- Playwright: `executable_path="/usr/bin/google-chrome"`, args `--no-sandbox --use-gl=swiftshader`.
- `verify.py` cae si se toca el árbol mientras corre. Correrlo solo, o servir el build.

## Estructura de ficheros

| Fichero | Responsabilidad |
|---|---|
| `src/sections/about.ts` | Construye los nodos de la placa. Solo estructura y lectura de `content.ts`; ni una clase de tema, ni un estilo. |
| `src/themes/themes.css` (regla base) | `display: none` de los nodos nuevos. |
| `src/themes/themes.css` (bloque Hyprland) | Rejilla, celdas, tipografía, scrim, retrato, apuntado, y ocultar lo que la placa sustituye. |
| `src/themes/hypr.choreography.ts` | Reparte las clases de entrada y su retardo diagonal. Nada de duraciones. |
| `scripts/measure-placa.py` | Arnés propio: desbordes, tamaños fuera de escala, y que los otros dos temas no se movieron. |

---

## Tarea 1 · El arnés, antes que nada

Se escribe primero y **hay que verlo rojo** contra defectos reales, no contra un estado anterior
cómodo. Vigila **todas** las celdas, no la primera: `measure-cortinilla.py` miraba una silueta de
cinco y por eso dos defectos graves atravesaron dos revisiones.

**Ficheros:**
- Crear: `scripts/measure-placa.py`

**Interfaces:**
- Produce: ejecutable con `python3 scripts/measure-placa.py [--url URL]`. Sale **0** si todo pasa,
  **1** con el detalle de cada fallo por `stdout`.

- [x] **Paso 1: escribir el arnés**

```python
"""Arnes de la placa de "Quien soy" en Hyprland.

Tres aserciones, y las tres nacieron de un fallo real del prototipo:
  1. Ninguna celda desborda su caja. Es el fallo de "las letras se montan
     encima de otras", que se colo dos veces y no se ve a ojo.
  2. Ningun tamano de fuente cae fuera de los diez pasos de la escala. Un
     `clamp()` sobre tokens devolvia 54,5px a 1440, que no existe.
  3. La placa no existe en Vice ni en Caelestia. El patron aditivo se ha
     roto cuatro veces por olvidar el `display: none` de base.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

ESCALA = [12, 16, 21.33, 28.43, 37.9, 50.52, 67.4, 89.85, 119.77, 159.66]
VIEWPORTS = [("escritorio", 1440, 900), ("movil", 390, 844)]


def ir_a_about(pg):
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"about\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        return False
    pg.evaluate(f"window.scrollTo(0, {top})")
    pg.wait_for_timeout(2500)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:4173")
    args = ap.parse_args()

    fallos = []
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--use-gl=swiftshader"],
        )

        for nombre, w, h in VIEWPORTS:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(f"{args.url}/?theme=hyprland", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(9000)
            if not ir_a_about(pg):
                fallos.append(f"[{nombre}] no existe [data-scene=about]")
                pg.close()
                continue

            celdas = pg.evaluate(
                "() => Array.from(document.querySelectorAll('[data-placa-celda]')).map(c => ({"
                " k: c.dataset.placaCelda, sh: c.scrollHeight, ch: c.clientHeight,"
                " sw: c.scrollWidth, cw: c.clientWidth }))"
            )
            if not celdas:
                fallos.append(f"[{nombre}] la placa no tiene celdas")
            for c in celdas:
                if c["sh"] > c["ch"] + 2 or c["sw"] > c["cw"] + 2:
                    fallos.append(
                        f"[{nombre}] celda '{c['k']}' desborda: "
                        f"{c['sw']}x{c['sh']} en {c['cw']}x{c['ch']}"
                    )

            tallas = pg.evaluate(
                "() => Array.from(document.querySelectorAll('[data-placa] *'))"
                ".filter(e => e.childElementCount === 0 && e.textContent.trim())"
                ".map(e => ({ t: e.textContent.trim().slice(0, 24),"
                " s: parseFloat(getComputedStyle(e).fontSize) }))"
            )
            for t in tallas:
                if not any(abs(t["s"] - paso) < 0.06 for paso in ESCALA):
                    fallos.append(f"[{nombre}] '{t['t']}' a {t['s']}px, fuera de la escala")
            pg.close()

        # La placa no puede existir en los otros dos temas.
        for tema in ("vice", "caelestia"):
            pg = b.new_page(viewport={"width": 1440, "height": 900})
            pg.goto(f"{args.url}/?theme={tema}", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(9000)
            ir_a_about(pg)
            visible = pg.evaluate(
                "() => { const n = document.querySelector('[data-placa]');"
                " if (!n) return false;"
                " const r = n.getBoundingClientRect();"
                " return getComputedStyle(n).display !== 'none' && r.width > 0 && r.height > 0; }"
            )
            if visible:
                fallos.append(f"[{tema}] la placa esta VISIBLE y no deberia")
            pg.close()

        b.close()

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Paso 2: verlo rojo contra el estado actual**

```bash
export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH
npm run build && npx vite preview --port 4173 --strictPort &
sleep 5
python3 scripts/measure-placa.py
```

Esperado: **FALLO** con `la placa no tiene celdas` en los dos viewports, porque todavía no existe.
Si sale verde, el arnés no mide nada y hay que arreglarlo antes de seguir.

- [x] **Paso 3: commit**

```bash
git add scripts/measure-placa.py
git commit -m "test(about): arnes de la placa de Quien soy"
```

---

## Tarea 2 · Los nodos, ocultos en los tres temas

**Ficheros:**
- Modificar: `src/sections/about.ts`
- Modificar: `src/themes/themes.css` (regla base, junto al resto de `display: none` compartidos)

**Interfaces:**
- Produce: `createPlaca(): HTMLElement`, un `<dl>` con `data-placa` y once hijos con
  `data-placa-celda="<clave>"`. Claves: `quien`, `retrato`, `estado`, `hace`, `obra`, `puesto`,
  `estudia`. Se añade a `createAbout()` como último hijo de `.about-body`.

- [x] **Paso 1: escribir el constructor**

En `src/sections/about.ts`, tras `createPairs()`:

```ts
/** Una celda de la placa: rotulo, dato, detalle y pie, en ese orden. */
function celda(clave: string, rotulo: string, nodos: Node[]): HTMLElement {
  const cell = el("div", "placa-c", [el("dt", "placa-k", [rotulo]), ...nodos]);
  cell.setAttribute("data-placa-celda", clave);
  // Focalizable: el apuntado tiene que existir tambien por teclado.
  cell.tabIndex = 0;
  return cell;
}

const dato = (texto: string): HTMLElement => el("dd", "placa-v", [texto]);
const detalle = (texto: string): HTMLElement => el("dd", "placa-s", [texto]);
const pie = (texto: string): HTMLElement => el("dd", "placa-p", [texto]);

/**
 * La placa de "Quien soy" en Hyprland. Se anade al DOM de los tres temas y se
 * envia oculta (`display: none` en la regla base de themes.css, visible solo
 * bajo `:root[data-theme="hyprland"]`). Patron aditivo estricto: el tema se
 * sortea por visita y se cambia sin recargar, asi que no se puede construir
 * segun `data-theme`.
 *
 * Cero datos nuevos: todo sale de content.ts. Tres campos que no se usaban en
 * ningun tema entran aqui — `identity.headline`, `identity.subheadline` y
 * `aboutCopy[0]`.
 */
function createPlaca(): HTMLElement {
  const foto = el("img", "placa-foto-img");
  foto.src = identity.githubAvatar;
  foto.alt = identity.name;
  foto.width = 150;
  foto.height = 150;
  foto.loading = "lazy";
  foto.decoding = "async";
  const retrato = celda("retrato", "", [el("span", "placa-foto", [foto])]);

  const placa = el("dl", "placa", [
    celda("quien", "Quién", [
      dato(identity.name),
      detalle(`${identity.role} · ${identity.location}. ${identity.headline}`),
      pie(identity.subheadline),
    ]),
    retrato,
    celda("estado", "Estado", [
      dato(identity.availability),
      detalle(aboutCopy[0] ?? ""),
      pie(`Ahora · ${identity.now}`),
    ]),
    celda(
      "hace",
      "Hace",
      focusAreas.flatMap((area) => [
        el("dd", "placa-par", [el("b", "", [area.title]), el("span", "", [area.detail])]),
      ]),
    ),
    celda("obra", statValue("Proyectos") ? "Obra" : "Obra", [
      el("dd", "placa-num", [statValue("Proyectos")]),
      detalle("proyectos"),
      pie(`${statValue("En producción")} en producción`),
    ]),
    celda("puesto", "Último puesto", [
      dato(experience[0]?.organization ?? ""),
      detalle(`${experience[0]?.role ?? ""}. ${experience[0]?.description ?? ""}`),
      pie(experience[0]?.period ?? ""),
    ]),
    celda("estudia", "Estudia", [
      dato(education[0]?.degree ?? ""),
      detalle(`${education[0]?.institution ?? ""}. ${aboutCopy[1] ?? ""}`),
      pie(education[0]?.period ?? ""),
    ]),
  ]);
  placa.setAttribute("data-placa", "");
  return placa;
}
```

Y en `createAbout()`, añadir `createPlaca()` como último hijo de `body`.

- [x] **Paso 2: el `display: none` de base**

En `src/themes/themes.css`, junto al resto de nodos compartidos ocultos (busca
`.about-pairs { display: none }`):

```css
/* Solo Hyprland enciende la placa. Sin esto sale en los tres temas y
   ensancha Vice, que es el fallo que ya se ha pagado cuatro veces. */
.placa {
  display: none;
}
```

- [x] **Paso 3: comprobar que no se ha movido nada**

```bash
export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH
npm run build && npm run lint
```

Esperado: build y lint verdes. Con el preview levantado:

```bash
python3 scripts/measure-placa.py
```

Esperado: **FALLO** con `la placa no tiene celdas` en Hyprland (aún oculta), y **sin** fallos de
Vice ni Caelestia. Si alguno de esos dos aparece, el `display: none` no está donde debe.

- [x] **Paso 4: commit**

```bash
git add src/sections/about.ts src/themes/themes.css
git commit -m "feat(about): nodos de la placa, ocultos en los tres temas"
```

---

## Tarea 3 · La rejilla y las celdas en Hyprland

**Ficheros:**
- Modificar: `src/themes/themes.css`, bloque `:root[data-theme="hyprland"]`

**Interfaces:**
- Consume: las clases `.placa`, `.placa-c`, `.placa-k`, `.placa-v`, `.placa-s`, `.placa-p`,
  `.placa-num`, `.placa-par`, `.placa-foto` de la tarea 2.

- [x] **Paso 1: encender y componer**

```css
/*
  LA PLACA — "Quien soy" deja de ser una pila de bloques.
  Rejilla de 6 columnas con celdas de distinto ancho: una rejilla uniforme es
  una tabla, y anchos desiguales ordenan por importancia sin cambiar el
  tamano de la letra. Spec: 2026-08-10-hyprland-quien-soy-placa-design.md
*/
:root[data-theme="hyprland"] .placa {
  display: grid;
  position: relative;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  margin: 0;
  background: var(--rule);
  border: 1px solid var(--rule);
}
@container (min-width: 900px) {
  :root[data-theme="hyprland"] .placa {
    grid-template-columns: repeat(6, 1fr);
    grid-template-rows: 1.02fr 0.98fr 1.05fr;
  }
  :root[data-theme="hyprland"] [data-placa-celda="quien"]   { grid-area: 1 / 1 / 2 / 4; }
  :root[data-theme="hyprland"] [data-placa-celda="retrato"] { grid-area: 1 / 4 / 2 / 5; }
  :root[data-theme="hyprland"] [data-placa-celda="estado"]  { grid-area: 1 / 5 / 3 / 7; }
  :root[data-theme="hyprland"] [data-placa-celda="hace"]    { grid-area: 2 / 1 / 3 / 4; }
  :root[data-theme="hyprland"] [data-placa-celda="obra"]    { grid-area: 2 / 4 / 3 / 5; }
  :root[data-theme="hyprland"] [data-placa-celda="puesto"]  { grid-area: 3 / 1 / 4 / 4; }
  :root[data-theme="hyprland"] [data-placa-celda="estudia"] { grid-area: 3 / 4 / 4 / 7; }
}

/* El contenido va PEGADO al borde superior. Separar rotulo y dato con
   `space-between` dejaba un hueco muerto en el centro de cada celda: ese era
   el motivo real de que la placa se viera vacia, no la falta de contenido. */
:root[data-theme="hyprland"] .placa-c {
  position: relative;
  overflow: hidden;
  min-height: 0;
  padding: 0.8rem 1rem 0.9rem;
  background: #0c0403;
  display: flex;
  flex-direction: column;
  gap: 0.32rem;
}
/* El pie se ancla abajo. Ojo: `.placa dd { margin: 0 }` (0-1-1) gana a
   `.placa-p` (0-1-0) y anularia el `auto`. */
:root[data-theme="hyprland"] .placa dd { margin: 0; }
:root[data-theme="hyprland"] .placa .placa-p { margin-top: auto; }
```

- [x] **Paso 2: ocultar lo que la placa sustituye**

```css
/* La placa dice todo esto y mejor. No se borran del DOM: los otros dos temas
   los siguen usando tal cual. */
:root[data-theme="hyprland"] .about-card,
:root[data-theme="hyprland"] .about-stats,
:root[data-theme="hyprland"] .about-track,
:root[data-theme="hyprland"] .about-pairs,
:root[data-theme="hyprland"] .about-body > [data-line] {
  display: none;
}
:root[data-theme="hyprland"] .about-grid { grid-template-columns: 1fr; }
```

- [x] **Paso 3: medir**

```bash
export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH
npm run build && python3 scripts/measure-placa.py
```

Esperado: se acabaron los `no tiene celdas`. Es probable que salgan desbordes y tallas fuera de
escala: **eso es correcto en este punto**, los cierran las tareas 4 y 5. Anotar cuáles salen.

- [x] **Paso 4: captura**

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",
                          args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4173/?theme=hyprland", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(9000)
    top = pg.evaluate("() => { const s=document.querySelector('[data-scene=\"about\"]');"
                      " return s.getBoundingClientRect().top + window.scrollY; }")
    pg.evaluate(f"window.scrollTo(0, {top})"); pg.wait_for_timeout(2500)
    pg.screenshot(path="/tmp/placa-t3.png")
    b.close()
EOF
```

Mirarla al lado de `.superpowers/brainstorm/1961497-1786322787/content/ficha-b.html`. Si el arnés
pasa y la captura no convence, **el arnés mide lo que no es**.

- [x] **Paso 5: commit**

```bash
git add src/themes/themes.css
git commit -m "feat(about): rejilla de la placa en Hyprland"
```

---

## Tarea 4 · Tipografía, retrato y contraste

**Ficheros:**
- Modificar: `src/themes/themes.css`, bloque Hyprland

- [x] **Paso 1: escala discreta y superficies**

```css
/* Escalones DISCRETOS. Un `clamp()` sobre tokens devolvia 54,5px a 1440, que
   no es ninguno de los diez pasos del tema. */
:root[data-theme="hyprland"] .placa-k {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: var(--haze);
}
:root[data-theme="hyprland"] .placa-v {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--t-3);
  line-height: 1.02;
  letter-spacing: -0.018em;
  color: var(--color-paper);
}
:root[data-theme="hyprland"] .placa-s { font-size: var(--t-1); line-height: 1.5; color: var(--haze); }
:root[data-theme="hyprland"] .placa-p {
  font-size: var(--t-1);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--haze);
}
:root[data-theme="hyprland"] .placa-num {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: var(--t-5);
  line-height: 0.9;
  letter-spacing: -0.04em;
  color: var(--color-paper);
}
:root[data-theme="hyprland"] .placa-par b {
  display: block;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--t-3);
  line-height: 1.04;
  letter-spacing: -0.018em;
  color: var(--color-paper);
}
:root[data-theme="hyprland"] .placa-par span {
  display: block;
  margin-top: 0.15rem;
  font-size: var(--t-1);
  line-height: 1.45;
  color: var(--haze);
}
:root[data-theme="hyprland"] .placa-par + .placa-par { margin-top: 0.55rem; }

@container (min-width: 1200px) {
  :root[data-theme="hyprland"] [data-placa-celda="quien"] .placa-v { font-size: var(--t-5); }
  :root[data-theme="hyprland"] .placa-num { font-size: var(--t-6); }
}

/* La celda caliente: el estado es lo unico que se enciende, asi que es lo
   primero que se lee sin necesidad de ser lo mas grande. */
:root[data-theme="hyprland"] [data-placa-celda="estado"] {
  background: linear-gradient(152deg, #33130a, #0c0403 68%);
}
:root[data-theme="hyprland"] [data-placa-celda="estado"] .placa-v {
  color: var(--l1);
  font-size: var(--t-4);
}
:root[data-theme="hyprland"] [data-placa-celda="estado"]::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 14px;
  height: 14px;
  border-top: 1px solid var(--l1);
  border-left: 1px solid var(--l1);
}

/* Retrato en duotono de brasa. `contain`, no `cover`: con `cover` se
   recortaba la cara. Y el filtro va SOLO en la imagen — puesto en el
   envoltorio, el `grayscale` agrisa tambien la capa de brasa antes de
   mezclarla y el duotono desaparece. */
:root[data-theme="hyprland"] [data-placa-celda="retrato"] { padding: 0; }
:root[data-theme="hyprland"] [data-placa-celda="retrato"] .placa-k { display: none; }
:root[data-theme="hyprland"] .placa-foto {
  position: absolute;
  inset: 12px;
  overflow: hidden;
  background: #2a1310;
}
:root[data-theme="hyprland"] .placa-foto-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: grayscale(1) contrast(1.4) brightness(0.58);
}
:root[data-theme="hyprland"] .placa-foto::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(196deg, rgba(255, 90, 52, 0.7), rgba(224, 29, 60, 0.28) 46%, rgba(255, 160, 60, 0.1) 76%);
  mix-blend-mode: screen;
}
```

- [x] **Paso 2: el scrim, medido contra el fondo real**

El fondo no es un plano: la página lleva el shader más `--bg-fallback`, que sube hasta `#3a1008`.
Hay precedente en el repo — `.about-pairs` necesitó un scrim al 78 % porque el texto secundario
caía a 3,20:1 (`themes.css:1877-1886`). Aquí el fondo de celda `#0c0403` ya hace de superficie,
así que el scrim solo cubre las juntas:

```css
:root[data-theme="hyprland"] .placa {
  background: color-mix(in srgb, var(--color-ink) 62%, var(--rule));
}
```

- [x] **Paso 3: medir contraste con el shader activo**

```bash
python3 scripts/verify.py --theme hyprland --url http://localhost:4173
```

Esperado: sin fallos de contraste nuevos respecto a `scripts/verify-baseline.json`. Si aparece
alguno, subir el porcentaje del scrim y **volver a medir**, no estimar.

- [x] **Paso 4: el arnés en verde en tallas y desbordes**

```bash
python3 scripts/measure-placa.py
```

Esperado: **cero** fallos de `fuera de la escala` y **cero** desbordes en los dos viewports. Si una
celda desborda, bajar un escalón el tamaño de esa celda concreta — nunca meter un `clamp`.

- [x] **Paso 5: commit**

```bash
git add src/themes/themes.css
git commit -m "feat(about): tipografia discreta, retrato en duotono y scrim de la placa"
```

---

## Tarea 5 · El apuntado: el corte de tinta

**Ficheros:**
- Modificar: `src/themes/themes.css`, bloque Hyprland

- [ ] **Paso 1: la cuña**

```css
/*
  ELEMENTO FIRMA — el corte de tinta.
  Una cuna de brasa entra en diagonal por el borde izquierdo y cubre la celda.
  La superficie cambia; el contenido no se mueve ni un pixel. Compositor puro:
  ni maquetacion ni repintado del arbol.

  Encender es un CORTE (420ms --hard), apagar es enfriarse (900ms --slow). La
  asimetria se declara en reglas separadas porque la transicion la dicta el
  estado de destino.
*/
:root[data-theme="hyprland"] .placa-c::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background: linear-gradient(112deg, rgba(255, 90, 52, 0.22), rgba(224, 29, 60, 0.06) 58%, transparent 82%);
  clip-path: polygon(0 0, 0 0, -12% 100%, -12% 100%);
  transition: clip-path 0.9s var(--slow);
}
:root[data-theme="hyprland"] .placa-c:hover::after,
:root[data-theme="hyprland"] .placa-c:focus-within::after {
  clip-path: polygon(0 0, 118% 0, 100% 100%, -12% 100%);
  transition: clip-path 0.42s var(--hard);
}
/* El contenido por encima de la cuna. */
:root[data-theme="hyprland"] .placa-c > * { position: relative; z-index: 1; }
:root[data-theme="hyprland"] .placa-c .placa-k { transition: color 0.9s var(--slow); }
:root[data-theme="hyprland"] .placa-c:hover .placa-k,
:root[data-theme="hyprland"] .placa-c:focus-within .placa-k {
  color: var(--l3);
  transition: color 0.42s var(--hard);
}
/* Anillo de foco propio: el del sistema casi no separa sobre esta tinta. */
:root[data-theme="hyprland"] .placa-c:focus-visible {
  outline: 2px solid var(--l3);
  outline-offset: -3px;
}
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .placa-c::after { transition: none; }
}
```

- [ ] **Paso 2: comprobar el teclado**

Levantar el preview, tabular por la sección y confirmar que **cada una de las siete celdas** recibe
foco visible y dispara la cuña. Es el mismo criterio que ya usa el gesto 2 del tema:
`pointerenter` y `focusin` en paralelo, nunca solo hover.

- [ ] **Paso 3: commit**

```bash
git add src/themes/themes.css
git commit -m "feat(about): el corte de tinta como apuntado de la placa"
```

---

## Tarea 6 · La entrada: el montaje

**Ficheros:**
- Modificar: `src/themes/hypr.choreography.ts`
- Modificar: `src/themes/themes.css`, bloque Hyprland

**Interfaces:**
- Consume: `data-placa-celda` de la tarea 2 y las `grid-area` de la tarea 3.
- Produce: clase `placa-in` en cada celda, con `--placa-d` en milisegundos.

- [ ] **Paso 1: el CSS de la entrada**

```css
/*
  ENTRADA — el montaje. Las celdas no aparecen: llegan desde el borde de la
  placa que les queda mas cerca y encajan en su hueco.

  La OPACIDAD entra mas tarde que el desplazamiento a proposito: sin ese
  retardo el texto se ve cortado a media llegada contra el `overflow: hidden`
  de su celda, y lee como fallo en vez de como pieza encajando. Se detecto
  mirando el fotograma intermedio, no razonando.
*/
:root[data-theme="hyprland"] .placa-in {
  opacity: 0;
  transform: translate(var(--placa-tx, 0), var(--placa-ty, 0));
}
:root[data-theme="hyprland"] .is-lit .placa-in {
  opacity: 1;
  transform: none;
  transition:
    transform 0.42s var(--hard) var(--placa-d, 0ms),
    opacity 0.24s linear calc(var(--placa-d, 0ms) + 0.2s);
}
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .placa-in {
    opacity: 1;
    transform: none;
  }
}
```

- [ ] **Paso 2: la coreografía reparte**

En `src/themes/hypr.choreography.ts`, dentro del gesto 0, tras el bucle de la `RECETA`:

```ts
  // Gesto 0b — el montaje de la placa.
  // El retardo sale de la POSICION en la rejilla, no del orden del DOM: fila
  // mas columna, asi que la llegada cruza la placa en diagonal en vez de
  // recorrer una lista. Y la direccion sale de la misma lectura, no de una
  // tabla escrita a mano que habria que mantener en dos sitios.
  Array.from(root.querySelectorAll<HTMLElement>("[data-placa-celda]")).forEach((celda) => {
    const area = getComputedStyle(celda).gridArea.split("/").map((n) => parseInt(n, 10));
    const [fila, col, filaFin, colFin] = area;
    if (Number.isNaN(fila) || Number.isNaN(col)) return;
    celda.classList.add("placa-in");
    celda.style.setProperty("--placa-d", `${(fila - 1 + (col - 1)) * 70}ms`);
    celda.style.setProperty("--placa-tx", col <= 2 ? "-22px" : colFin >= 6 ? "22px" : "0px");
    celda.style.setProperty("--placa-ty", fila === 1 ? "-18px" : filaFin >= 4 ? "18px" : "0px");
  });
```

- [ ] **Paso 3: comprobar el fotograma intermedio, que es donde falla**

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",
                          args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4173/?theme=hyprland", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(9000)
    top = pg.evaluate("() => { const s=document.querySelector('[data-scene=\"about\"]');"
                      " return s.getBoundingClientRect().top + window.scrollY; }")
    pg.evaluate("() => document.querySelector('[data-scene=\"about\"]').classList.remove('is-lit')")
    pg.evaluate(f"window.scrollTo(0, {top})")
    pg.wait_for_timeout(700)
    pg.screenshot(path="/tmp/placa-entrada-medio.png")
    pg.wait_for_timeout(2500)
    pg.screenshot(path="/tmp/placa-entrada-fin.png")
    b.close()
EOF
```

Esperado en `/tmp/placa-entrada-medio.png`: **ningún texto cortado a media palabra**. Si lo hay,
subir el retardo de la opacidad, no acortar el recorrido.
Esperado en `/tmp/placa-entrada-fin.png`: la placa completa, sin nada a medio camino.

- [ ] **Paso 4: comprobar movimiento reducido**

```bash
python3 scripts/verify.py --theme hyprland --reduced --url http://localhost:4173
```

Esperado: la placa entera legible sin haber interactuado y sin nada invisible.

- [ ] **Paso 5: commit**

```bash
git add src/themes/hypr.choreography.ts src/themes/themes.css
git commit -m "feat(about): el montaje como entrada de la placa"
```

---

## Tarea 7 · Móvil, gates y cierre

**Ficheros:**
- Modificar: `src/themes/themes.css` si el móvil lo pide

- [ ] **Paso 1: mirar 390×844 de verdad**

Por debajo de 900 la placa cae a dos columnas y las `grid-area` no aplican, así que manda el orden
del DOM: quién, retrato, estado, hace, obra, puesto, estudia. Comprobar que ese orden se lee bien y
que ninguna celda desborda.

```bash
python3 scripts/measure-placa.py
```

- [ ] **Paso 2: los cuatro gates**

```bash
export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH
npm run build
npm run lint
python3 scripts/verify.py --theme vice --url http://localhost:4173
python3 scripts/verify.py --theme hyprland --url http://localhost:4173
python3 scripts/verify.py --theme caelestia --url http://localhost:4173
python3 scripts/verify.py --theme hyprland --reduced --url http://localhost:4173
python3 scripts/measure-placa.py
```

Todos en verde. `verify.py` **se corre solo y sin editar nada**: Vite recarga por HMR ante
cualquier edición y se lleva el contexto de la página por delante.

- [ ] **Paso 3: anti-mock**

```bash
grep -rE "mockData|fakeData|hardcoded|TODO.*real|// fake|demo_data|placeholder|lorem ipsum|Lorem" \
  src/ --include="*.ts"
```

Esperado: sin resultados en lo tocado.

- [ ] **Paso 4: los dos críticos**

Lanzar `lidia-naive-tester` **con una métrica concreta y cronometrable** — propuesta: *tiempo hasta
decir en voz alta si Aoshi está disponible y qué hace*, en móvil — y `vera-art-director` con umbral
7,5. Los dos pineados a `sonnet`.

- [ ] **Paso 5: cerrar el registro**

Cambiar `Estado:` del spec de `pendiente de plan` a `implementado` **solo cuando todas las casillas
de este plan estén marcadas**: `check_spec_plan_consistency()` cruza las dos cosas y falla si el
spec dice `implementado` con pasos sin marcar.

- [ ] **Paso 6: commit final**

```bash
git add -A
git commit -m "feat(about): la placa de Quien soy en Hyprland"
```

---

## Autorrevisión del plan

- **Cobertura del spec:** composición (T3), tipografía discreta (T4), contraste y scrim (T4),
  retrato sin recortar (T4), apuntado (T5), entrada (T6), movimiento reducido (T6), accesibilidad
  de foco (T2 `tabIndex` + T5 anillo), aislamiento entre temas (T2 + arnés T1), verificación (T7).
  Sin huecos.
- **Sin marcadores de posición:** todos los pasos llevan el código o el comando literal.
- **Consistencia de nombres:** `data-placa`, `data-placa-celda`, `.placa-c/-k/-v/-s/-p/-num/-par`,
  `.placa-foto`, `.placa-in`, `--placa-d/-tx/-ty`. Mismos nombres en las tareas 2 a 6 y en el arnés.
- **Fuera de alcance, anotado en el spec:** el defecto de `stackOf("Frontend")`, que toca a Vice.
