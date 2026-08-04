# La cortinilla de escenas — plan de implementación

> **Para quien ejecute esto:** SUB-SKILL OBLIGATORIA: usa `superpowers:subagent-driven-development`
> (recomendado) o `superpowers:executing-plans` para ir tarea a tarea. Los pasos usan casillas
> (`- [ ]`) y hay que marcarlas **en el momento**, no al final (regla del proyecto:
> `.claude/rules/speckit-progress-tracking.md`).

**Objetivo:** que la navegación de escenas deje de ocupar sitio permanente y pase a llamarse: un
disparador en la esquina superior derecha abre una cortinilla con el índice de las cinco escenas.

**Arquitectura:** `sceneNav.ts` deja de pintar una lista fija y monta dos piezas: un `<button>`
disparador que muestra la escena en curso (mantenida por `IntersectionObserver`, no por la
coreografía) y un panel a pantalla completa con el índice. La lógica de destino, ya medida y
verificada, se extrae intacta a su propio módulo. `.rail-now` se retira del cromo porque el
disparador asume su papel.

**Stack:** Vite 8 + TypeScript estricto + CSS de tema (`themes.css`) + arneses de Playwright en
`scripts/`. Sin framework, sin librería de UI, sin dependencias nuevas.

## Restricciones globales

- **Node 22 para construir.** `source ~/.nvm/nvm.sh && nvm use 22` antes de `npm run build`. Con
  Node 18 rolldown falla por `styleText`.
- **Medir siempre en el build de producción**, nunca en `npm run dev`: el HMR de Vite corrompe las
  medidas de ScrollTrigger. Servir con `npx vite preview --port 4173`.
- **Siempre `?theme=vice`** al verificar: el tema se sortea por visita.
- **El puerto 5173 es de OTRO proyecto del usuario** (`Decision-Maker`). No tocarlo, no matarlo.
- **Cero `any`.** `strict` está activo; usar `unknown` + guards.
- **Nunca `gsap.from`**, siempre `fromTo` con los dos extremos escritos.
- **Ningún literal `px` donde toque un escalón de la escala** (`--t-1`…`--t-10`). Es P0 automático
  en la revisión visual, que va por su tercer aviso. Ojo: una función continua (`clamp` con `vw` o
  `cqi`) sobre tokens de la escala **también** produce valores fuera de escala.
- **Todo módulo devuelve un handle con `destroy()`** que se llama en `pagehide`. Quitar
  escuchadores, observadores y temporizadores ahí.
- **`prefers-reduced-motion` degrada el viaje, nunca la función.**
- **Cero emojis** en código, commits y documentación.
- **Un commit por tarea**, con `tipo(scope): descripción`.

## Ficheros

| Fichero | Responsabilidad |
|---|---|
| `src/components/sceneNav.destino.ts` | **Nuevo.** Los cinco destinos y `destinationFor()`. Nada de DOM propio. Es lo único que conoce el carril de obra. |
| `src/components/sceneNav.ts` | **Reescrito.** Monta disparador + cortinilla, mantiene la escena en curso, gestiona foco y teclado. Devuelve `destroy()`. |
| `src/components/cinemaChrome.ts` | Retirar `.rail-now`. |
| `src/themes/vice.choreography.ts` | Retirar la actualización de `.rail-now` (función `cinemaChrome`, ~línea 1332). |
| `src/data/content.ts` | Añadir `sceneIndex`: los cinco destinos con nombre de escena y descriptor. |
| `src/themes/themes.css` | Estilos de disparador y cortinilla. Retirar los de la lista lateral, el rail del pie y el hueco que le reservaba la última vía. |
| `scripts/measure-nav.py` | Extender: alineación, foco, teclado, tiempos, movimiento reducido, integridad del índice. |
| `scripts/measure-contacto-matriz.py` | El criterio "la navegación tapa texto" cambia de sentido: en reposo no debe haber navegación que pueda tapar nada. |

---

### Tarea 1: Extraer la lógica de destino, sin cambiar comportamiento

Primero se aísla lo que ya funciona, para poder reescribir el resto sin miedo. Al terminar esta
tarea el sitio se ve y se comporta **exactamente igual**.

**Ficheros:**
- Crear: `src/components/sceneNav.destino.ts`
- Modificar: `src/components/sceneNav.ts` (importa de ahí en vez de definirlo)
- Modificar: `scripts/measure-nav.py:37` (la ruta del guardarraíl de acoplamiento)

**Interfaces:**
- Produce: `export interface SceneTarget { id: string; label: string }`,
  `export const TARGETS: SceneTarget[]`, `export function destinationFor(id: string): number | null`,
  y las constantes `OBRA_SETTLED_U`, `OBRA_TOTAL_U`.

- [x] **Paso 1: Crear el módulo con el contenido actual, movido tal cual**

Copiar de `sceneNav.ts` las líneas de `TARGETS`, `OBRA_SETTLED_U`, `OBRA_TOTAL_U` y
`destinationFor()`, **incluidos sus comentarios completos** — el de `OBRA_TOTAL_U` explica por qué
reimplementa la coreografía en vez de importarla, y sin él el siguiente que lo lea lo "arreglará".

```ts
// src/components/sceneNav.destino.ts
export interface SceneTarget {
  id: string;
  label: string;
}

export const TARGETS: SceneTarget[] = [
  { id: "hero", label: "Título" },
  { id: "quien-es", label: "Quién es" },
  { id: "obra", label: "Obra" },
  { id: "creditos", label: "Créditos" },
  { id: "contacto", label: "Fundido" },
];

/* (pegar aquí el bloque de comentario de OBRA_TOTAL_U tal cual está hoy) */
export const OBRA_SETTLED_U = 0.42;
export const OBRA_TOTAL_U = 6.25;

export function destinationFor(id: string): number | null {
  const target = document.getElementById(id);
  if (!target) return null;
  const top = target.getBoundingClientRect().top + window.scrollY;
  if (id === "obra") {
    const budget = Math.max(0, target.offsetHeight - window.innerHeight);
    return top + (OBRA_SETTLED_U / OBRA_TOTAL_U) * budget;
  }
  return top;
}
```

- [x] **Paso 2: Que `sceneNav.ts` lo importe y borre sus copias**

```ts
import { TARGETS, destinationFor } from "./sceneNav.destino";
```

Borrar de `sceneNav.ts` las definiciones que acaban de moverse. No tocar nada más todavía.

- [x] **Paso 3: Apuntar el guardarraíl del arnés al fichero nuevo**

En `scripts/measure-nav.py`, dentro de `comprueba_acoplamiento()`:

```python
total = _constante("src/components/sceneNav.destino.ts", "OBRA_TOTAL_U")
```

- [x] **Paso 4: Comprobar que el guardarraíl sigue vivo**

Este arnés falla ruidosamente si no encuentra la constante, así que si la ruta quedó mal, lo dice.

```bash
source ~/.nvm/nvm.sh && nvm use 22 && npm run build
npx vite preview --port 4173 &
python3 scripts/measure-nav.py
```
Esperado: `OK acoplamiento: OBRA_TOTAL_U 6.25 coincide con la coreografia` y
`0 anclas fuera de tolerancia` (15 de 15, tres temas).

- [x] **Paso 5: Commit**

```bash
git add src/components/sceneNav.destino.ts src/components/sceneNav.ts scripts/measure-nav.py
git commit -m "refactor(nav): aislar la logica de destino antes de rehacer la navegacion"
```

---

### Tarea 2: Los cinco destinos con su descriptor, en el contenido

**Ficheros:**
- Modificar: `src/data/content.ts`
- Modificar: `src/components/sceneNav.destino.ts`

**Interfaces:**
- Consume: `SceneTarget` de la Tarea 1.
- Produce: `export const sceneIndex: SceneEntry[]` en `content.ts`, con
  `interface SceneEntry { id: string; label: string; blurb: string }`.

- [x] **Paso 1: Declarar el índice en el contenido**

Va en `content.ts` porque es la fuente única de verdad del proyecto y es donde mira quien cambia
una escena. **No se lee del DOM**: se comprobó y `#obra .hero-kick` devuelve "Gestión de campañas",
que es el rótulo del primer proyecto, no de la escena.

```ts
export interface SceneEntry {
  id: string;
  /** Nombre de cine. Es lo que se lee grande en el indice. */
  label: string;
  /** Lo que la escena contiene, en llano. Cierra el hallazgo de que
   *  "Fundido" no comunica "contacto" a quien llega de fuera. */
  blurb: string;
}

export const sceneIndex: SceneEntry[] = [
  { id: "hero", label: "Título", blurb: "Desarrollador full stack" },
  { id: "quien-es", label: "Quién es", blurb: "Trayectoria y cifras" },
  { id: "obra", label: "Obra", blurb: "Cinco proyectos" },
  { id: "creditos", label: "Créditos", blurb: "Con qué construyo" },
  { id: "contacto", label: "Fundido", blurb: "Contacto" },
];
```

- [x] **Paso 2: Que el módulo de destino consuma el índice**

En `sceneNav.destino.ts`, sustituir `TARGETS` por una reexportación, para que no haya dos listas.
`SceneEntry` sustituye a `SceneTarget`: **borrar la interfaz `SceneTarget` y su lista literal** que
la Tarea 1 movió aquí, o quedarán dos tipos describiendo lo mismo y el siguiente que llegue no
sabrá cuál es el bueno.

```ts
import { sceneIndex, type SceneEntry } from "../data/content";

export type { SceneEntry };
export const TARGETS: SceneEntry[] = sceneIndex;
```

- [x] **Paso 3: Añadir la aserción de integridad al arnés**

En `scripts/measure-nav.py`, junto a `comprueba_acoplamiento()`:

```python
def comprueba_indice() -> list[str]:
    """Cinco entradas, ninguna vacia. Que digan la VERDAD es cosa de quien
    cambie la escena; por eso viven en content.ts, que es donde se mira al
    cambiarla. Lo que si se puede comprobar aqui es que no falte ninguna ni
    se quede en blanco."""
    texto = (RAIZ / "src/data/content.ts").read_text(encoding="utf-8")
    bloque = re.search(r"sceneIndex: SceneEntry\[\] = \[(.*?)\];", texto, re.S)
    if bloque is None:
        return ["no encuentro sceneIndex en content.ts"]
    entradas = re.findall(r'blurb:\s*"([^"]*)"', bloque.group(1))
    if len(entradas) != 5:
        return [f"sceneIndex tiene {len(entradas)} descriptores, esperaba 5"]
    vacios = [i for i, e in enumerate(entradas) if not e.strip()]
    if vacios:
        return [f"descriptores vacios en las posiciones {vacios}"]
    print(f"OK indice: 5 descriptores, ninguno vacio")
    return []
```

Y llamarla en `main()`: `fallos = comprueba_acoplamiento() + comprueba_indice()`.

- [x] **Paso 4: Verla fallar antes de creerle**

Cambiar temporalmente un `blurb` a `""` en `content.ts`, correr el arnés y confirmar que reporta
`descriptores vacios en las posiciones [0]`. Restaurar con `git checkout -- src/data/content.ts`.
Un arnés que nunca se ha visto en rojo no ha demostrado que mida nada.

- [x] **Paso 5: Build y arnés en verde, y commit**

```bash
npm run build && python3 scripts/measure-nav.py
git add src/data/content.ts src/components/sceneNav.destino.ts scripts/measure-nav.py
git commit -m "feat(nav): el indice de escenas y su descriptor, en el contenido"
```

---

### Tarea 3: El disparador, fuera del cromo y vivo en los tres temas

**Ficheros:**
- Modificar: `src/components/sceneNav.ts`
- Modificar: `src/components/cinemaChrome.ts` (retirar `.rail-now`)
- Modificar: `src/themes/vice.choreography.ts` (~1332, retirar su actualización)
- Modificar: `src/themes/themes.css` (estilos del disparador)

**Interfaces:**
- Consume: `TARGETS`, `destinationFor` (Tarea 1); `sceneIndex` (Tarea 2).
- Produce: en el DOM, `button.scene-nav-trigger` con `aria-expanded` y `aria-controls="scene-index"`.

- [x] **Paso 1: Montar el disparador**

Reemplaza la construcción de la lista en `mountSceneNav`. **Fuera de `.cinema-chrome`**: ese
contenedor es `aria-hidden="true"` y, medido, con `prefers-reduced-motion` pasa a `display: none`
dejando `.rail` en 0×0 — un disparador ahí dentro dejaría sin navegación a quien pide movimiento
reducido.

```ts
const trigger = document.createElement("button");
trigger.type = "button";
trigger.className = "scene-nav-trigger";
trigger.setAttribute("aria-expanded", "false");
trigger.setAttribute("aria-controls", "scene-index");
trigger.setAttribute("aria-haspopup", "dialog");

const triggerLabel = document.createElement("span");
triggerLabel.className = "scene-nav-trigger-label";
trigger.append(triggerLabel);
```

- [x] **Paso 2: Mantener la escena en curso por observación, no por coreografía**

Tiene que funcionar en Hyprland y Caelestia, donde no hay coreografía que lo actualice.

```ts
const pinta = (i: number): void => {
  const n = String(i + 1).padStart(2, "0");
  triggerLabel.textContent = `${n} · ${TARGETS[i].label}`;
};
pinta(0);

// La escena "en curso" es la ultima cuyo borde superior ya cruzo el tercio
// alto del viewport. Con `rootMargin` negativo arriba, una escena solo cuenta
// como actual cuando de verdad esta ocupando la pantalla, no cuando asoma.
const observer = new IntersectionObserver(
  (entradas) => {
    for (const e of entradas) {
      if (!e.isIntersecting) continue;
      const i = TARGETS.findIndex((t) => t.id === e.target.id);
      if (i >= 0) pinta(i);
    }
  },
  { rootMargin: "-33% 0px -60% 0px", threshold: 0 },
);
for (const t of TARGETS) {
  const s = document.getElementById(t.id);
  if (s) observer.observe(s);
}
```

- [x] **Paso 3: Retirar `.rail-now` del cromo y su actualización**

En `cinemaChrome.ts`, borrar el `el("span", "rail-now", ["01 · Título"])` de la barra. En
`vice.choreography.ts` (~1332, función `cinemaChrome`), borrar la línea que hace
`document.querySelector<HTMLElement>(".rail-now")` y todo lo que dependa de ella. Un elemento, una
verdad: quien dice en qué escena estás es ahora el disparador.

- [x] **Paso 4: Estilos del disparador**

En `themes.css`. Tamaños de la escala, nunca literales.

```css
.scene-nav-trigger {
  position: fixed;
  top: 1.05rem;
  right: 1.5rem;
  z-index: 42;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 44px;
  padding: 0.45rem 0.7rem;
  border: 0;
  border-radius: 5px;
  background: transparent;
  box-shadow: inset 0 0 0 1px rgb(255 209 102 / 0.5);
  font-family: inherit;
  font-size: var(--t-1, 0.75rem);
  font-weight: 700;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--accent-amber, #ffd166);
  cursor: pointer;
  transition:
    background 200ms cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 200ms cubic-bezier(0.22, 1, 0.36, 1);
}

.scene-nav-trigger:hover {
  background: rgb(255 209 102 / 0.14);
  box-shadow: inset 0 0 0 1px rgb(255 209 102 / 0.85);
}

.scene-nav-trigger:focus-visible {
  outline: 3px solid var(--accent-amber, #ffd166);
  outline-offset: 3px;
}
```

- [x] **Paso 5: Comprobar que sobrevive donde el cromo no**

```bash
npm run build
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for tema in ("vice", "hyprland", "caelestia"):
        for rm in ("no-preference", "reduce"):
            pg = b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion=rm)
            pg.goto(f"http://localhost:4173/?theme={tema}", wait_until="domcontentloaded")
            pg.wait_for_timeout(9000)
            r = pg.evaluate("""() => {
                const t = document.querySelector('.scene-nav-trigger');
                if (!t) return null;
                const b = t.getBoundingClientRect();
                return {w: Math.round(b.width), h: Math.round(b.height), txt: t.textContent.trim()};
            }""")
            assert r and r["w"] >= 44 and r["h"] >= 44, f"{tema}/{rm}: {r}"
            print(tema, rm, r)
            pg.close()
    b.close()
PY
```
Esperado: seis líneas, todas con caja ≥44×44 y texto "01 · Título". Es el criterio 7 del spec, y
lo que hoy mide 0×0 en el cromo con movimiento reducido.

- [x] **Paso 6: Commit**

```bash
git add src/components/ src/themes/ 
git commit -m "feat(nav): el disparador vive fuera del cromo y sobrevive a movimiento reducido"
```

---

### Tarea 4: La cortinilla y su índice

**Ficheros:**
- Modificar: `src/components/sceneNav.ts`
- Modificar: `src/themes/themes.css`

**Interfaces:**
- Consume: `sceneIndex` (Tarea 2), `destinationFor` (Tarea 1), el disparador (Tarea 3).
- Produce: en el DOM, `div#scene-index.scene-index` con cinco `a.scene-index-row`; la clase
  `.is-open` en el mismo nodo gobierna abierto/cerrado.

- [x] **Paso 1: Construir el panel**

```ts
const panel = document.createElement("div");
panel.className = "scene-index";
panel.id = "scene-index";
panel.setAttribute("role", "dialog");
panel.setAttribute("aria-modal", "true");
panel.setAttribute("aria-label", "Selección de escenas");

const heading = document.createElement("p");
heading.className = "scene-index-title";
heading.textContent = "Selección de escenas";
panel.append(heading);

for (const [i, entry] of sceneIndex.entries()) {
  const row = document.createElement("a");
  row.className = "scene-index-row";
  row.href = `#${entry.id}`;           // sin JS sigue navegando
  row.dataset.scene = entry.id;

  const num = document.createElement("span");
  num.className = "scene-index-num";
  num.textContent = String(i + 1).padStart(2, "0");

  const name = document.createElement("span");
  name.className = "scene-index-name";
  name.textContent = entry.label;

  const guide = document.createElement("span");
  guide.className = "scene-index-guide";
  guide.setAttribute("aria-hidden", "true");   // la guia es decorativa

  const blurb = document.createElement("span");
  blurb.className = "scene-index-blurb";
  blurb.textContent = entry.blurb;

  row.append(num, name, guide, blurb);
  panel.append(row);
}
```

- [x] **Paso 2: Abrir, cerrar y navegar**

```ts
let abierto = false;

const setAbierto = (v: boolean): void => {
  abierto = v;
  panel.classList.toggle("is-open", v);
  trigger.setAttribute("aria-expanded", v ? "true" : "false");
};

trigger.addEventListener("click", () => setAbierto(!abierto));

panel.addEventListener("click", (event: MouseEvent) => {
  const row = (event.target as HTMLElement).closest<HTMLAnchorElement>("a[href^='#']");
  if (!row) return;
  const id = row.hash.slice(1);
  const destination = destinationFor(id);
  if (destination === null) return;
  event.preventDefault();
  setAbierto(false);
  // `instant` explicito: `html { scroll-behavior: smooth }` hace que "auto"
  // resuelva a suave incluso con prefers-reduced-motion puesto.
  window.scrollTo({ top: destination, behavior: "instant" });
  history.replaceState(null, "", `#${id}`);
});
```

- [x] **Paso 3: Estilos de la cortinilla**

El detalle que **no** se puede perder: los números **cuelgan** (posición absoluta) para que el
rótulo y los cinco nombres compartan borde izquierdo, y la fila es `align-items: center` para que
número, guía y descriptor compartan eje. Con `baseline` el descriptor se sienta sobre la línea base
del nombre —que en Passion One grande cae muy abajo— y cae por debajo de sus propios puntos.

```css
.scene-index {
  --sangria: 2.8rem;
  position: fixed;
  inset: 0;
  z-index: 41;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 5.5%;
  background: rgb(8 3 14 / 0.985);
  clip-path: inset(0 0 100% 0);
  pointer-events: none;
  transition: clip-path 140ms ease-in;
}

.scene-index.is-open {
  clip-path: inset(0 0 0 0);
  pointer-events: auto;
  transition: clip-path 460ms cubic-bezier(0.22, 1, 0.36, 1);
}

.scene-index-title {
  margin: 0 0 1.1rem var(--sangria);
  font-size: var(--t-1, 0.75rem);
  font-weight: 700;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: rgb(255 244 232 / 0.42);
}

.scene-index-row {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.28rem 0 0.28rem var(--sangria);
  min-height: 44px;
  text-decoration: none;
  opacity: 0;
  transform: translateY(14px);
  filter: blur(5px);
  transition:
    opacity 110ms ease-in,
    transform 110ms ease-in,
    filter 110ms ease-in;
}

.scene-index.is-open .scene-index-row {
  opacity: 1;
  transform: none;
  filter: none;
  transition:
    opacity 380ms cubic-bezier(0.22, 1, 0.36, 1),
    transform 460ms cubic-bezier(0.22, 1, 0.36, 1),
    filter 380ms cubic-bezier(0.22, 1, 0.36, 1);
}

.scene-index.is-open .scene-index-row:nth-of-type(1) { transition-delay: 110ms; }
.scene-index.is-open .scene-index-row:nth-of-type(2) { transition-delay: 165ms; }
.scene-index.is-open .scene-index-row:nth-of-type(3) { transition-delay: 220ms; }
.scene-index.is-open .scene-index-row:nth-of-type(4) { transition-delay: 275ms; }
.scene-index.is-open .scene-index-row:nth-of-type(5) { transition-delay: 330ms; }

.scene-index-num {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--t-1, 0.75rem);
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0.14em;
  color: rgb(255 244 232 / 0.38);
}

.scene-index-name {
  flex: none;
  font-family: var(--font-display, "Passion One"), sans-serif;
  font-size: var(--t-5);
  line-height: 1.05;
  color: rgb(255 244 232 / 0.55);
  transition: color 200ms cubic-bezier(0.22, 1, 0.36, 1);
}

.scene-index-guide {
  flex: 1;
  height: 1px;
  margin: 0 0.2rem;
  opacity: 0.55;
  background-image: radial-gradient(circle, rgb(255 244 232 / 0.3) 1px, transparent 1px);
  background-size: 6px 1px;
  background-repeat: repeat-x;
  transition: opacity 200ms cubic-bezier(0.22, 1, 0.36, 1);
}

.scene-index-blurb {
  flex: none;
  font-size: var(--t-2, 1rem);
  font-weight: 600;
  line-height: 1;
  color: rgb(255 244 232 / 0.5);
  transition: color 200ms cubic-bezier(0.22, 1, 0.36, 1);
}

.scene-index-row:hover .scene-index-name,
.scene-index-row:focus-visible .scene-index-name { color: var(--color-paper, #fff4e8); }
.scene-index-row:hover .scene-index-blurb,
.scene-index-row:focus-visible .scene-index-blurb { color: var(--accent-amber, #ffd166); }
.scene-index-row:hover .scene-index-guide { opacity: 1; }

.scene-index-row:focus-visible {
  outline: 3px solid var(--accent-amber, #ffd166);
  outline-offset: 4px;
  border-radius: 3px;
}

.scene-index-row[aria-current="true"] .scene-index-name,
.scene-index-row[aria-current="true"] .scene-index-num { color: var(--accent-amber, #ffd166); }
```

- [x] **Paso 4: Marcar la escena en curso también en el índice**

Dentro de `pinta(i)`, añadir:

```ts
panel.querySelectorAll<HTMLElement>(".scene-index-row").forEach((row, j) => {
  if (j === i) row.setAttribute("aria-current", "true");
  else row.removeAttribute("aria-current");
});
```

- [x] **Paso 5: Medir la alineación, que es lo que se rompe solo**

```bash
npm run build
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4173/?theme=vice", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    pg.click(".scene-nav-trigger")
    pg.wait_for_timeout(900)
    r = pg.evaluate("""() => {
        const izq = n => Math.round(n.getBoundingClientRect().left);
        const cen = n => { const b = n.getBoundingClientRect(); return (b.top + b.bottom) / 2; };
        const filas = [...document.querySelectorAll('.scene-index-row')];
        return {
          titulo: izq(document.querySelector('.scene-index-title')),
          nombres: filas.map(f => izq(f.querySelector('.scene-index-name'))),
          desfases: filas.map(f => Math.abs(cen(f.querySelector('.scene-index-blurb'))
                                          - cen(f.querySelector('.scene-index-guide')))),
        };
    }""")
    assert len(set(r["nombres"] + [r["titulo"]])) == 1, r      # un solo borde izquierdo
    assert max(r["desfases"]) <= 1, r                          # un solo eje vertical
    print("alineacion OK", r)
    b.close()
PY
```
Esperado: un único valor de borde izquierdo para el rótulo y los cinco nombres, y desfase vertical
≤1 px entre guía y descriptor. Es el criterio 4 del spec.

- [x] **Paso 6: Comprobar los tiempos**

Criterio 5 del spec. Se comprueba la duración DECLARADA, que es determinista; el cronómetro va
detrás, solo como comprobación de sanidad y con margen explícito. La primera versión de este paso
cronometraba contra 480/160 ms y lo que medía era la carga de la máquina, no la animación.

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.route("**/viceHaze*", lambda r: r.abort())   # el shader compite por el hilo principal
    pg.goto("http://localhost:4173/?theme=vice", wait_until="domcontentloaded")
    pg.wait_for_timeout(6000)
    dec = pg.evaluate("""() => {
        const p = document.querySelector('.scene-index');
        const cerrado = getComputedStyle(p).transitionDuration;
        p.classList.add('is-open');
        const abierto = getComputedStyle(p).transitionDuration;
        p.classList.remove('is-open');
        return {abierto, cerrado};
    }""")
    assert dec["abierto"] == "0.46s", dec
    assert dec["cerrado"] == "0.14s", dec
    medir = """() => new Promise(res => {
        const panel = document.querySelector('.scene-index');
        const t0 = performance.now();
        const fin = e => { if (e.propertyName !== 'clip-path') return;
            panel.removeEventListener('transitionend', fin);
            res(Math.round(performance.now() - t0)); };
        panel.addEventListener('transitionend', fin);
        document.querySelector('.scene-nav-trigger').click();
    })"""
    a = pg.evaluate(medir); pg.wait_for_timeout(400)
    c = pg.evaluate(medir)
    print("declarado", dec, "| cronometro apertura", a, "cierre", c)
    assert a <= 460 + 150, f"apertura {a} ms > 610"
    assert c <= 140 + 150, f"cierre {c} ms > 290"
    b.close()
EOF
```
Esperado: declarado `0.46s` y `0.14s` exactos, y el cronómetro dentro del margen.

- [x] **Paso 7: Commit**

```bash
git add src/components/sceneNav.ts src/themes/themes.css
git commit -m "feat(nav): la cortinilla con el indice de escenas"
```

---

### Tarea 5: Teclado, foco y movimiento reducido

**Ficheros:**
- Modificar: `src/components/sceneNav.ts`
- Modificar: `src/themes/themes.css`

**Interfaces:**
- Consume: `setAbierto`, `panel`, `trigger` (Tarea 4).

- [x] **Paso 1: Foco al abrir, devuelto al cerrar, y Esc**

```ts
const filas = (): HTMLAnchorElement[] =>
  Array.from(panel.querySelectorAll<HTMLAnchorElement>(".scene-index-row"));

const onKeydown = (event: KeyboardEvent): void => {
  if (!abierto) return;
  if (event.key === "Escape") {
    setAbierto(false);
    trigger.focus();
    return;
  }
  if (event.key !== "Tab") return;
  // Foco atrapado: mientras la cortinilla esta abierta, tabular no debe
  // llevarte a la pagina que hay debajo, que esta tapada.
  const f = filas();
  if (f.length === 0) return;
  const i = f.indexOf(document.activeElement as HTMLAnchorElement);
  event.preventDefault();
  f[(i + (event.shiftKey ? -1 : 1) + f.length) % f.length].focus();
};

document.addEventListener("keydown", onKeydown);
```

Y en `setAbierto`, tras alternar la clase:

```ts
if (v) filas()[0]?.focus();
else trigger.focus();
```

- [x] **Paso 2: Cerrar al pulsar fuera**

```ts
const onDocClick = (event: MouseEvent): void => {
  if (!abierto) return;
  const t = event.target as HTMLElement;
  if (t.closest(".scene-index") || t.closest(".scene-nav-trigger")) return;
  setAbierto(false);
};
document.addEventListener("click", onDocClick);
```

- [x] **Paso 3: Degradar el viaje, no la función**

En `themes.css`, al final del bloque global (no dentro de ningún `@media` de ancho):

```css
@media (prefers-reduced-motion: reduce) {
  .scene-index,
  .scene-index.is-open,
  .scene-index .scene-index-row,
  .scene-index.is-open .scene-index-row {
    transition: none;
    transition-delay: 0ms;
    transform: none;
    filter: none;
  }
}
```

- [x] **Paso 4: Completar el `destroy()`**

Sin esto se filtran un observador y dos escuchadores de documento en cada cambio de página.

```ts
return {
  destroy: () => {
    observer.disconnect();
    document.removeEventListener("keydown", onKeydown);
    document.removeEventListener("click", onDocClick);
    trigger.remove();
    panel.remove();
  },
};
```

- [x] **Paso 5: Medir teclado y foco de verdad**

```bash
npm run build
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for rm in ("no-preference", "reduce"):
        pg = b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion=rm)
        pg.goto("http://localhost:4173/?theme=vice", wait_until="domcontentloaded")
        pg.wait_for_timeout(9000)
        pg.click(".scene-nav-trigger")
        pg.wait_for_timeout(700)
        act = lambda: pg.evaluate("() => document.activeElement.className")
        assert "scene-index-row" in act(), f"{rm}: el foco no entro, {act()}"
        for _ in range(5):
            pg.keyboard.press("Tab")
        assert "scene-index-row" in act(), f"{rm}: el foco se escapo, {act()}"
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(400)
        assert "scene-nav-trigger" in act(), f"{rm}: el foco no volvio, {act()}"
        assert pg.get_attribute(".scene-nav-trigger", "aria-expanded") == "false"
        print(rm, "teclado OK")
        pg.close()
    b.close()
PY
```
Esperado: dos líneas `teclado OK`. Es el criterio 6 del spec, y el 7 en la pasada con `reduce`.

- [x] **Paso 6: Commit**

```bash
git add src/components/sceneNav.ts src/themes/themes.css
git commit -m "feat(nav): teclado, foco atrapado y degradado con movimiento reducido"
```

---

### Tarea 6: Retirar lo que sostenía al rail

Tres piezas existían solo para sostener una navegación permanente. Se van con ella, y esta tarea
es la que de verdad cobra el rediseño.

**Ficheros:**
- Modificar: `src/themes/themes.css` (lista lateral, rail del pie, hueco de la última vía)
- Modificar: `src/components/sceneNav.ts` (mecanismo de tránsito)
- Modificar: `scripts/measure-contacto-matriz.py`

- [x] **Paso 1: Borrar los estilos de la navegación vieja**

En `themes.css`, borrar `.scene-nav`, `.scene-nav ul`, `.scene-nav li`, `.scene-nav a` y sus
estados, el bloque `@media (max-width: 1079px)` del rail numerado con su `counter-reset`, y las
reglas de `.scene-nav--transito`. Buscar `scene-nav` y no dejar ninguna que no sea
`.scene-nav-trigger` o `.scene-index`.

- [x] **Paso 2: Borrar el mecanismo de tránsito**

En `sceneNav.ts`, borrar los escuchadores de `scroll`, `touchmove` y `wheel`, el `matchMedia`, el
temporizador `quieto` y la clase `scene-nav--transito`. Existían porque una capa fija sobre
contenido en movimiento roba el toque; sin capa fija, no hay de qué apartarse. Quitar también sus
`removeEventListener` del `destroy()`.

- [x] **Paso 3: Devolver su hueco a la última vía de contacto**

Borrar de `themes.css` el bloque `@media (max-width: 1079px)` con
`.contacto-bar:last-child { padding-bottom: 4.25rem; }`. Reservaba sitio al rail del pie.

- [x] **Paso 4: Dar la vuelta al criterio de la matriz**

En `measure-contacto-matriz.py`, el bloque que comprueba que la navegación no tape texto ya no
aplica: en reposo no hay navegación que pueda tapar nada. Sustituirlo por lo contrario, que es lo
que el rediseño promete:

```python
            # En reposo NO puede haber navegacion ocupando la escena. Antes se
            # comprobaba que no tapase texto; ahora se comprueba que no este.
            # El disparador es lo unico permitido, y vive en el cromo de arriba.
            invasion = pg.evaluate("""() => {
                const nav = document.querySelector('.scene-index');
                if (!nav || getComputedStyle(nav).pointerEvents !== 'none') {
                    return 'la cortinilla esta activa en reposo';
                }
                const t = document.querySelector('.scene-nav-trigger');
                if (!t) return 'no hay disparador';
                const r = t.getBoundingClientRect();
                for (const bar of document.querySelectorAll('.contacto-bar')) {
                    const b = bar.getBoundingClientRect();
                    if (Math.min(r.right, b.right) - Math.max(r.left, b.left) > 0 &&
                        Math.min(r.bottom, b.bottom) - Math.max(r.top, b.top) > 0) {
                        return 'el disparador solapa una via de contacto';
                    }
                }
                return null;
            }""")
            if invasion:
                fallos.append(f"{ancho}px reposo: {invasion}")
```

- [x] **Paso 5: Los dos arneses que prueban que el rediseño valió la pena**

```bash
npm run build
python3 scripts/measure-contacto-matriz.py
```
Esperado: `65 combinaciones medidas, 0 con recorte`.

Y el barrido del toque, que es el hallazgo que costó tres revisiones:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for w, h in ((390, 844), (1029, 900)):
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto("http://localhost:4173/?theme=vice", wait_until="domcontentloaded")
        pg.wait_for_timeout(9000)
        tope = pg.evaluate("""() => {const s = document.querySelector('[data-scene="contacto"]');
            return s.getBoundingClientRect().top + scrollY;}""")
        pg.evaluate(f'window.scrollTo({{top:{tope - 400}, behavior:"instant"}})')
        pg.wait_for_timeout(700)
        robos = puntos = 0
        for _ in range(46):
            pg.mouse.wheel(0, 30)
            for roba in pg.evaluate("""() => {
                const out = [];
                for (const bar of document.querySelectorAll('.contacto-bar')) {
                    const b = bar.getBoundingClientRect();
                    for (let f = 0.2; f <= 0.8; f += 0.2) {
                        const y = b.top + b.height * f;
                        if (y < 0 || y > innerHeight) continue;
                        const e = document.elementFromPoint(innerWidth * 0.5, y);
                        if (e) out.push(!e.closest('.contacto-bar'));
                    }
                }
                return out;
            }"""):
                puntos += 1
                robos += 1 if roba else 0
        print(w, "puntos", puntos, "robados", robos)
        assert robos == 0, f"{w}px: {robos} puntos robados"
        pg.close()
    b.close()
PY
```
Esperado: 0 robados en los dos anchos.

- [x] **Paso 6: Commit**

```bash
git add src/ scripts/
git commit -m "refactor(nav): retirar el rail, su hueco reservado y su mecanismo de transito"
```

---

### Tarea 7: Cierre — arneses completos y gate

- [x] **Paso 1: Los cinco arneses y el build**

```bash
source ~/.nvm/nvm.sh && nvm use 22
npm run build && npm run lint
python3 scripts/measure-nav.py              # 15/15 anclas, acoplamiento e indice
python3 scripts/measure-contacto.py         # contraste y reduced motion
python3 scripts/measure-contacto-matriz.py  # 65/65
python3 scripts/measure-type-scale.py       # 0 nuevos sobre su linea base
python3 scripts/verify.py --url http://localhost:4173   # 0 nuevos
```
Todos deben salir con código 0. Si `verify.py` protesta por la aserción del cromo con movimiento
reducido —comprueba que `.cinema-chrome` no aparece—, **no silenciarla**: el cromo sigue
ocultándose, lo que cambió es que la navegación ya no depende de él. Comprobar que la aserción
sigue midiendo lo que dice y ajustar su texto si nombra `.rail-now`, que ya no existe.

- [x] **Paso 2: Contraste de la cortinilla sobre el fondo generativo**

Añadir a `scripts/measure-contacto.py` el muestreo de `.scene-index-name` y `.scene-index-blurb`
con la cortinilla abierta, con los mismos umbrales que ya usa: 4,5:1 el texto normal y 3,0:1 el de
≥24 px, sobre el píxel renderizado y en tres fotogramas separados 2 s. Es el criterio 9 del spec.

- [x] **Paso 3: Que la cortinilla no descoloque el carril de obra**

Riesgo del spec: es una capa a pantalla completa sobre una página con pines de ScrollTrigger. Si
abrirla dispara un `refresh`, el carril de obra se recoloca y la escena queda mal. Se comprueba
midiendo la posición del carril antes y después de abrir y cerrar, no razonando sobre ello.

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4173/?theme=vice", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    pg.evaluate("""() => {const s = document.getElementById('obra');
        window.scrollTo({top: s.getBoundingClientRect().top + scrollY + 1200, behavior: 'instant'});}""")
    pg.wait_for_timeout(3500)
    pos = """() => {const t = document.querySelector('[data-scene="obra"] .obra-track')
        || document.querySelector('#obra');
        const r = t.getBoundingClientRect();
        return [Math.round(r.left), Math.round(r.top), Math.round(scrollY)];}"""
    antes = pg.evaluate(pos)
    pg.click(".scene-nav-trigger"); pg.wait_for_timeout(700)
    pg.keyboard.press("Escape"); pg.wait_for_timeout(900)
    despues = pg.evaluate(pos)
    print("antes", antes, "despues", despues)
    assert antes == despues, f"la cortinilla movio el carril: {antes} -> {despues}"
    b.close()
PY
```
Esperado: misma posición antes y después. Si difiere, hay un `ScrollTrigger.refresh()` disparándose
y hay que evitar que abrir la cortinilla cambie la altura del documento (revisar `overflow` en
`body` mientras está abierta).

- [x] **Paso 4: Capturas en los tres anchos**

390×844, 1029×900 y 1440×900, con la cortinilla cerrada y abierta, en `?theme=vice`. Mirarlas: un
arnés en verde no prueba que se vea bien.

- [x] **Paso 5: Actualizar el estado del spec**

En `docs/superpowers/specs/2026-08-03-nav-cortinilla-design.md`, `Estado: implementado` y añadir
`Plan: docs/superpowers/plans/2026-08-03-nav-cortinilla.md`. `verify.py` cruza spec y plan: si el
spec dice implementado y quedan casillas sin marcar aquí, falla — y con razón.

- [x] **Paso 6: Gate**

Lanzar `lidia-naive-tester` y `vera-art-director` **con el modelo pineado** (heredan el de la
sesión; sin pinear, un fan-out en sesión top factura todo a tarifa top). Cada uno lee su
`memory.md` primero. A Lidia hay que preguntarle explícitamente por el hallazgo de "Fundido", que
lleva tres revisiones abierto y que esta entrega pretende cerrar con el descriptor del índice.

- [x] **Paso 7: Pedir el merge**

Nunca hacerlo por cuenta propia.
