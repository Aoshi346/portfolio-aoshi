# Caelestia — Obra (fase B3) Implementation Plan

> **Tracking: historico.** Las 9 tareas de este plan (46 casillas) estan hechas y commiteadas en
> `main` — el trabajo se siguio en vivo con el ledger de SDD de la sesion, no ticando las casillas
> de este fichero, y no se marcan ahora en bloque: ticar 46 pasos que nadie siguio uno a uno
> falsificaria el registro en vez de completarlo. El registro real vive en el historial de git y en
> `docs/superpowers/specs/2026-09-03-caelestia-obra-design.md`.
>
> Esta marca existe para que `scripts/verify.py::check_spec_plan_consistency` sepa distinguir "no
> se siguio aqui" de "esta a medias". En los planes nuevos se marca al completar cada paso, como
> pide `.claude/rules/speckit-progress-tracking.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the scene-per-project stacked layout Caelestia currently inherits for `#obra`
(4964px tall, 1-of-5 projects reachable, scroll inside a workspace that must never scroll) with the
**Editorial** composition: a fixed row of five magazine-style cards and a drawer below it that opens
per selection — entirely new code, no shared files touched.

**Architecture:** One new component module (`src/components/caelestiaObraEditorial.ts`, mount/destroy
pattern identical to `src/components/obraCartel.ts`) builds the row + drawer directly from
`caseStudies` (not by scraping the generic `[data-scene="obra"]` sections — those get hidden
outright under Caelestia via CSS). Wired into `src/main.ts` behind `theme.id === "caelestia"`,
exactly like the Hyprland cartel is wired behind `theme.id === "hyprland"`. All new CSS lives under
`:root[data-theme="caelestia"]` in `src/themes/themes.css`. GSAP loaded via the same deferred
`import("gsap")` pattern the rest of the codebase uses.

**Tech Stack:** TypeScript (strict), vanilla DOM (`el()`/`elFromMarkup` from `src/utils/dom.ts`),
GSAP 3 (dynamic import), Tailwind utility classes only where the project already uses them (this
module writes its own CSS block instead, matching `obraCartel.ts`'s precedent — see Task 1).

**Spec:** `docs/superpowers/specs/2026-09-03-caelestia-obra-design.md`

## Global Constraints

- **No `any`** — `strict: true`. Use `unknown` + guards if a type is genuinely unknown.
- **Anti-mock**: every visible string comes from `caseStudies` in `src/data/content.ts`, literal.
  `tooling` is never pinted. A missing `period` removes the whole metadata row, never a placeholder.
- **`Zustand` has no `simple-icons` slug** (`slugDeStack("Zustand") === null`) — render its name as
  plain text, never invent a logo.
- **Never `gsap.from`** — always `fromTo` with both ends written by hand.
- **WebGL/GSAP cleanup**: the new module returns `{ destroy: () => void }`; `destroy()` kills every
  GSAP tween/timeline it created and removes the DOM it injected. Wired into the existing
  `pagehide` cleanup block in `src/main.ts`.
- **`prefers-reduced-motion: reduce`**: the scene lands with the first project already selected,
  the drawer already populated, zero animation.
- **Vice and Hyprland are not touched.** `src/sections/obra/projectScene.ts` is not modified —
  every change is additive CSS scoped to `:root[data-theme="caelestia"]` plus new files. Verify both
  other themes render unchanged (Task 9).
- **Real icons only**: stack marks reuse `getIconMarkup`/`slugDeStack` from
  `src/utils/icons.ts` / `src/utils/stackIcons.ts` — monochrome, `currentColor`, never a brand color.
- **Capture treatment tokens**: 16:10 box, `border-radius: 16px`, 1px `--cae-outline` border. Rest:
  `filter: saturate(.52)` + a `::after` veil in `--cae-surface-container-high` at 16% opacity,
  `mix-blend-mode: multiply`. Selected: `saturate(1)`, veil `opacity: 0`, `outline: 2px solid
  var(--cae-primary)`.
- **Entrance is "Caída"**: cards fall from `y:-46 rotate:(per-card tilt)` to `y:0 rotate:0`,
  `ease: bounce.out`, `stagger: .08`, tilts `[-5, 4, -3, 5, -4]` deg, `transformOrigin: 50% 0%`. Then
  the drawer reveals in four layers in this order: title (clip-path sweep, `power2.inOut`), then
  `kick` + preview (`power2.out`), then metadata rows (stagger `.06`), then `problem`/`solution`
  blocks (stagger `.08`).
- **Selection axis is Y** (not X): clicking a different card re-populates the drawer and tweens it
  `y:14→0, opacity:0→1`, `.3s`, `ease: cubic-bezier(0.7,0,0.2,1)` ("hard" curve). Hovering a card
  without clicking only lifts it (`translateY(-6px)`, shadow grows, tilt straightens to 0) — never
  opens the drawer.
- **Build gate**: `npm run build` (`tsc && vite build`) and `npm run lint` clean before any task is
  considered done.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/components/caelestiaObraEditorial.ts` (new) | Builds the row + drawer from `caseStudies`, owns selection state, entrance choreography, hover, cleanup. Mirrors `obraCartel.ts`'s `mount*(root): Promise<Handle>` shape. |
| `src/themes/themes.css` (modify, append to the `caelestia"]` block) | Hides the generic per-project sections under Caelestia; styles `.cae-obra-row`, `.cae-obra-card`, `.cae-obra-drawer`, capture treatment, footer states. |
| `src/main.ts` (modify) | Deferred-imports and mounts the new module behind `theme.id === "caelestia"`; adds `caeObraHandle?.destroy()` to the existing `pagehide` listener. |
| `scripts/measure-caelestia-obra.py` (new) | Gate harness — the nine assertions from the spec's `## Los gates`. |

No changes to `src/sections/obra/projectScene.ts`, `src/data/content.ts`, `src/utils/icons.ts`, or
`src/utils/stackIcons.ts`.

---

### Task 1: Hide the generic Obra layout under Caelestia, reserve the CSS block

**Files:**
- Modify: `src/themes/themes.css` (append after the existing `:root[data-theme="caelestia"]
  .scene-surface` rule around line 3599 — find it with `grep -n 'caelestia"\] \.scene-surface'
  src/themes/themes.css`)

**Interfaces:**
- Produces: CSS classes `.cae-obra-row`, `.cae-obra-card`, `.cae-obra-thumb`, `.cae-obra-drawer`,
  `.cae-obra-drawer-title`, `.cae-obra-drawer-preview`, `.cae-obra-drawer-meta`,
  `.cae-obra-drawer-prose`, `.cae-obra-foot` — consumed by Task 2.

- [ ] **Step 1: Hide the five stacked project sections under Caelestia**

```css
/*
 * Fase B3 — Obra deja de ser cinco escenas apiladas y pasa a ser la
 * Editorial: una fila fija de tarjetas + un cajon. El DOM generico que
 * `projectScene.ts` construye para los tres temas (titulo a pantalla
 * completa, columnas Problema/Solucion, `.obra-meta`) no sirve aqui — se
 * oculta entero y `caelestiaObraEditorial.ts` construye su propio arbol
 * leyendo `caseStudies` directamente, no el DOM oculto.
 */
:root[data-theme="caelestia"] [data-obra-track] {
  display: none;
}

:root[data-theme="caelestia"] .obra-rail {
  overflow: visible;
  height: auto;
}
```

- [ ] **Step 2: Reserve the row + card CSS**

```css
:root[data-theme="caelestia"] .cae-obra-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 18px;
  padding: 15px 0;
}

:root[data-theme="caelestia"] .cae-obra-card {
  display: flex;
  flex-direction: column;
  background: var(--cae-surface-container-high);
  padding: 8px 8px 12px;
  border-radius: 3px;
  box-shadow: 0 10px 22px -8px rgb(0 0 0 / 0.4);
  cursor: pointer;
  position: relative;
  border: 0;
  text-align: inherit;
  font: inherit;
  color: inherit;
}

:root[data-theme="caelestia"] .cae-obra-card.is-sel {
  box-shadow:
    0 0 0 2px var(--cae-primary),
    0 14px 26px -8px rgb(0 0 0 / 0.45);
}

:root[data-theme="caelestia"] .cae-obra-caption {
  font-family: "Fraunces", serif;
  font-style: italic;
  font-variation-settings: "opsz" 30, "wght" 520;
  font-size: 14px;
  text-align: center;
  color: var(--cae-on-surface);
  line-height: 1.25;
  margin-top: 9px;
}

:root[data-theme="caelestia"] .cae-obra-tag {
  display: block;
  font-family: "Martian Mono", monospace;
  font-style: normal;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--cae-on-surface-variant);
  text-align: center;
  margin-top: 2px;
}
```

- [ ] **Step 3: Reserve the capture treatment CSS (M4 of the spec)**

```css
:root[data-theme="caelestia"] .cae-obra-thumb {
  aspect-ratio: 16 / 10;
  width: 100%;
  border-radius: 16px;
  border: 1px solid var(--cae-outline);
  position: relative;
  overflow: hidden;
}

:root[data-theme="caelestia"] .cae-obra-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  filter: saturate(0.52);
  transition:
    filter 0.3s ease,
    transform 0.3s ease;
}

:root[data-theme="caelestia"] .cae-obra-thumb::after {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--cae-surface-container-high);
  mix-blend-mode: multiply;
  opacity: 0.16;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

:root[data-theme="caelestia"] .cae-obra-card.is-sel .cae-obra-thumb img {
  filter: saturate(1);
}

:root[data-theme="caelestia"] .cae-obra-card.is-sel .cae-obra-thumb {
  outline: 2px solid var(--cae-primary);
  outline-offset: 0;
}

:root[data-theme="caelestia"] .cae-obra-card.is-sel .cae-obra-thumb::after {
  opacity: 0;
}
```

- [ ] **Step 4: `npm run build` — confirm zero errors (no consumer of these classes yet, so nothing
  should visually change)**

```bash
npm run build
```
Expected: build succeeds; `?theme=caelestia` still renders the (now-empty, since `[data-obra-track]`
is hidden and nothing replaces it yet) Obra workspace with no console errors.

- [ ] **Step 5: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(caelestia): reserva el bloque CSS de la Editorial de Obra y oculta el layout generico"
```

---

### Task 2: `caelestiaObraEditorial.ts` — mount skeleton, build the row from `caseStudies`

**Files:**
- Create: `src/components/caelestiaObraEditorial.ts`
- Modify: `src/main.ts` (wiring — see Task 8, not here; this task only creates the module and can be
  smoke-tested by temporarily calling it from the browser console)

**Interfaces:**
- Consumes: `caseStudies` (`src/data/content.ts`), `el`/`elFromMarkup` (`src/utils/dom.ts`),
  `slugDeStack` (`src/utils/stackIcons.ts`), `getIconMarkup` (`src/utils/icons.ts`).
- Produces: `export async function mountCaelestiaObraEditorial(root: HTMLElement): Promise<{ destroy: () => void }>`
  — consumed by Task 8 (`main.ts` wiring).

- [ ] **Step 1: Write the module with the row-building half only (drawer comes in Task 3)**

```typescript
import { caseStudies } from "../data/content";
import { el } from "../utils/dom";

export interface CaelestiaObraEditorialHandle {
  destroy: () => void;
}

const TILTS = [-5, 4, -3, 5, -4];

/**
 * La Editorial: la fila de cinco tarjetas nunca se mueve (es la "lista
 * quieta" del eje compartido de Material 3) y el cajon que abre debajo es
 * lo unico que entra o cambia. Construye TODO desde `caseStudies`, no
 * desde el DOM generico de `projectScene.ts` — ese DOM sigue existiendo
 * para Vice/Hyprland pero `themes.css` lo oculta entero bajo Caelestia
 * (Task 1), asi que raspar su texto seria leer un arbol invisible.
 */
export async function mountCaelestiaObraEditorial(
  root: HTMLElement,
): Promise<CaelestiaObraEditorialHandle> {
  const rail = root.querySelector<HTMLElement>("[data-obra-rail]");
  if (!rail) throw new Error("La Editorial de Obra necesita [data-obra-rail]");

  const row = el(
    "div",
    "cae-obra-row",
    caseStudies.map((project, index) => buildCard(project.title, project.tag, index)),
  );

  rail.append(row);

  const cards = Array.from(row.querySelectorAll<HTMLButtonElement>(".cae-obra-card"));

  return {
    destroy: () => {
      row.remove();
    },
  };
}

function buildCard(title: string, tag: string, index: number): HTMLButtonElement {
  const project = caseStudies[index];
  const shot = project.gallery[0];

  const thumb = el("div", "cae-obra-thumb", []);
  if (shot) {
    const img = el("img") as HTMLImageElement;
    img.src = shot.src;
    img.alt = shot.caption;
    img.loading = "lazy";
    img.decoding = "async";
    thumb.append(img);
  }

  const card = el("button", "cae-obra-card", [
    thumb,
    el("figcaption", "cae-obra-caption", [title, el("span", "cae-obra-tag", [tag])]),
  ]);
  card.type = "button";
  card.dataset.obraCard = String(index);
  card.setAttribute("aria-label", `Ver ${title}`);

  return card;
}
```

`el()`'s generic is keyed by `HTMLElementTagNameMap`, so `el("button", ...)` already returns
`HTMLButtonElement` and `el("figcaption", ...)` already returns `HTMLElement` — no casts needed
anywhere in this file.

- [ ] **Step 2: `npm run build` — confirm zero type errors**

```bash
npm run build
```
Expected: zero TypeScript errors.

- [ ] **Step 3: Smoke-test in the browser**

```bash
npx vite preview --port 4173 &
```
Open `http://localhost:4173/?theme=caelestia#obra` (or navigate to the Obra workspace pill), open
devtools console, run:
```js
import("/src/components/caelestiaObraEditorial.ts").then(m => m.mountCaelestiaObraEditorial(document.querySelector("main")))
```
Expected: five cards appear in a row inside the Obra workspace, each with a captura preview (still
the Vice-palette placeholder `.webp` — that's expected, real captures are the documented blocker)
and a title in Fraunces italic. No console errors.

- [ ] **Step 4: Commit**

```bash
git add src/components/caelestiaObraEditorial.ts
git commit -m "feat(caelestia): fila de cinco tarjetas de la Editorial de Obra"
```

---

### Task 3: The drawer — populate on selection, Y-axis reveal (M5)

**Files:**
- Modify: `src/components/caelestiaObraEditorial.ts`
- Modify: `src/themes/themes.css` (drawer CSS)

**Interfaces:**
- Consumes: `slugDeStack`, `getIconMarkup` (as in Global Constraints).
- Produces: internal `abrir(index: number, animado: boolean): void`, called by card click handlers
  (Task 3) and by the entrance choreography (Task 5, with `animado` driving which tween runs).

- [ ] **Step 1: Add the drawer CSS**

```css
:root[data-theme="caelestia"] .cae-obra-drawer {
  margin-top: 14px;
  padding: 20px 24px;
  border-radius: 18px;
  border: 1px solid var(--cae-outline);
  background: var(--cae-surface-container);
  display: flex;
  align-items: center;
  gap: 26px;
}

:root[data-theme="caelestia"] .cae-obra-drawer-title {
  flex: 0 0 230px;
}

:root[data-theme="caelestia"] .cae-obra-drawer-kick {
  font-family: "Martian Mono", monospace;
  font-size: 10.5px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--cae-primary);
}

:root[data-theme="caelestia"] .cae-obra-drawer-title h3 {
  font-family: "Fraunces", serif;
  font-variation-settings: "opsz" 60, "wght" 640;
  font-size: 34px;
  margin: 4px 0 8px;
  line-height: 1.04;
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .cae-obra-drawer-lead {
  font-size: 13.5px;
  color: var(--cae-on-surface-variant);
  line-height: 1.4;
}

:root[data-theme="caelestia"] .cae-obra-drawer-preview {
  flex: 0 0 200px;
}

:root[data-theme="caelestia"] .cae-obra-drawer-meta {
  flex: 0 0 200px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

:root[data-theme="caelestia"] .cae-obra-drawer-meta dt {
  font-family: "Martian Mono", monospace;
  font-size: 9.5px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--cae-on-surface-variant);
}

:root[data-theme="caelestia"] .cae-obra-drawer-meta dd {
  font-size: 13px;
  color: var(--cae-on-surface);
  margin: 3px 0 0;
}

:root[data-theme="caelestia"] .cae-obra-stack {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
  margin-top: 3px;
}

:root[data-theme="caelestia"] .cae-obra-stack .obra-marca {
  width: 24px;
  height: 24px;
  border-radius: 7px;
  background: var(--cae-surface-container-high);
  color: var(--cae-on-surface-variant);
  display: flex;
  align-items: center;
  justify-content: center;
}

:root[data-theme="caelestia"] .cae-obra-stack .obra-marca svg {
  width: 14px;
  height: 14px;
}

:root[data-theme="caelestia"] .cae-obra-stack-text {
  font-family: "Martian Mono", monospace;
  font-size: 10.5px;
  padding: 0 7px;
  height: 24px;
  display: flex;
  align-items: center;
  border-radius: 7px;
  background: var(--cae-surface-container-high);
  color: var(--cae-on-surface-variant);
}

:root[data-theme="caelestia"] .cae-obra-prose {
  flex: 1 1 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 22px;
  min-width: 0;
}

:root[data-theme="caelestia"] .cae-obra-prose h4 {
  font-family: "Martian Mono", monospace;
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--cae-on-surface-variant);
  margin: 0 0 5px;
}

:root[data-theme="caelestia"] .cae-obra-prose p {
  font-size: 13px;
  line-height: 1.5;
  color: var(--cae-on-surface);
  margin: 0;
}

/*
 * M7 — los dos estados de pie. El enlace es la unica parada de tabulador
 * de la ficha; la nota de privado lleva un testigo apagado, nunca el color
 * activo, para no leerse como algo pulsable.
 */
:root[data-theme="caelestia"] .cae-obra-foot {
  margin-top: 10px;
  font-family: "Martian Mono", monospace;
}

:root[data-theme="caelestia"] .cae-obra-foot a {
  color: var(--cae-primary);
  text-decoration: none;
  font-size: 12.5px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 5px;
  padding: 2px 3px;
  margin: -2px -3px;
}

:root[data-theme="caelestia"] .cae-obra-foot a:hover {
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .cae-obra-foot a:focus-visible {
  outline: 2px solid var(--cae-primary);
  outline-offset: 3px;
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .cae-obra-foot-private {
  color: var(--cae-on-surface-variant);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

:root[data-theme="caelestia"] .cae-obra-foot-private i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--cae-outline);
  display: inline-block;
}
```

- [ ] **Step 2: Extend the module — drawer build + `abrir()`**

Add to `src/components/caelestiaObraEditorial.ts`:

```typescript
import { getIconMarkup } from "../utils/icons";
import { slugDeStack } from "../utils/stackIcons";
import type { CaseStudy } from "../data/content";
```

Replace the `mountCaelestiaObraEditorial` body from `rail.append(row);` onward:

```typescript
  rail.append(row);

  const cards = Array.from(row.querySelectorAll<HTMLButtonElement>(".cae-obra-card"));
  const drawer = el("div", "cae-obra-drawer", []);
  drawer.setAttribute("aria-live", "polite");
  rail.append(drawer);

  let seleccionado = -1;

  function poblarCajon(index: number): void {
    const project = caseStudies[index];
    drawer.replaceChildren(
      el("div", "cae-obra-drawer-title", [
        el("div", "cae-obra-drawer-kick", [project.tag]),
        el("h3", "", [project.title]),
        el("p", "cae-obra-drawer-lead", [project.lead]),
        buildFoot(project),
      ]),
      buildPreview(project),
      buildMeta(project),
      el("div", "cae-obra-prose", [
        el("div", "", [el("h4", "", ["Problema"]), el("p", "", [project.problem])]),
        el("div", "", [el("h4", "", ["Solución"]), el("p", "", [project.solution])]),
      ]),
    );
  }

  function abrir(index: number): void {
    if (index === seleccionado) return;
    cards[seleccionado]?.classList.remove("is-sel");
    seleccionado = index;
    cards[seleccionado]?.classList.add("is-sel");
    poblarCajon(index);
  }

  cards.forEach((card, index) => {
    card.addEventListener("click", () => abrir(index));
  });

  abrir(0);

  return {
    destroy: () => {
      row.remove();
      drawer.remove();
    },
  };
}

function buildPreview(project: CaseStudy): HTMLElement {
  const shot = project.gallery[0];
  const thumb = el("div", "cae-obra-thumb is-sel", []);
  if (shot) {
    const img = el("img") as HTMLImageElement;
    img.src = shot.src;
    img.alt = shot.caption;
    img.loading = "lazy";
    img.decoding = "async";
    thumb.append(img);
  }
  return el("div", "cae-obra-drawer-preview", [thumb]);
}

function buildMeta(project: CaseStudy): HTMLElement {
  const rows: HTMLElement[] = [
    el("div", "", [el("dt", "", ["Rol"]), el("dd", "", [project.role])]),
  ];
  if (project.period) {
    rows.push(el("div", "", [el("dt", "", ["Periodo"]), el("dd", "", [project.period])]));
  }
  rows.push(
    el("div", "", [
      el("dt", "", ["Stack"]),
      el(
        "dd",
        "cae-obra-stack",
        project.stack.map((nombre) => {
          const slug = slugDeStack(nombre);
          if (!slug) return el("span", "cae-obra-stack-text", [nombre]);
          const tile = el("span", "obra-marca", [
            elFromMarkup("obra-marca-svg", getIconMarkup(slug)),
          ]);
          tile.title = nombre;
          return tile;
        }),
      ),
    ]),
  );
  rows.push(el("div", "", [el("dt", "", ["Estado"]), el("dd", "", [project.status])]));
  return el("dl", "cae-obra-drawer-meta", rows);
}

function buildFoot(project: CaseStudy): HTMLElement {
  const foot = el("div", "cae-obra-foot", []);
  if (project.link) {
    const link = el("a", "", [`${project.link.label} →`]) as HTMLAnchorElement;
    link.href = project.link.href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    foot.append(link);
  } else if (project.privateProject) {
    foot.append(
      el("span", "cae-obra-foot-private", [
        el("i", "", []),
        "Proyecto privado de empresa",
      ]),
    );
  }
  return foot;
}
```

Also add `elFromMarkup` to the `../utils/dom` import at the top of the file.

- [ ] **Step 3: `npm run build`**

```bash
npm run build
```
Expected: zero errors.

- [ ] **Step 4: Manual check — clicking a card swaps the drawer**

Repeat the Step 3 smoke test from Task 2. Click each of the five cards in turn.
Expected: the drawer's title, metadata, prose, and footer state (link vs. private note) update to
match the clicked project; `TesisFar` is the only one with no "Periodo" row; `HyprFinance`'s stack
row shows four icon tiles and one `Zustand` text chip.

- [ ] **Step 5: Commit**

```bash
git add src/components/caelestiaObraEditorial.ts src/themes/themes.css
git commit -m "feat(caelestia): el cajon de la Editorial se puebla y cambia con la seleccion"
```

---

### Task 4: Selection tween (Y-axis) and hover-without-click

**Files:**
- Modify: `src/components/caelestiaObraEditorial.ts`

**Interfaces:**
- Consumes: dynamic `import("gsap")`, same pattern as `obraCartel.ts` Step 1 of its mount function.
- Produces: nothing new consumed elsewhere — this task makes the existing `abrir()`/hover behavior
  from Task 3 actually move.

- [ ] **Step 1: Write the (currently failing, since no animation exists yet) manual verification
  script** — there is no automated test framework in this project (verified: no `test` script in
  `package.json`, verification is Playwright-driven per `rules/verification.md`), so this task's
  "test" is the harness assertion added in Task 9. Confirm that before this task, clicking a card
  swaps the drawer content **instantly**, with no motion — that's the state to change.

- [ ] **Step 2: Add GSAP and the reduced-motion guard**

At the top of `mountCaelestiaObraEditorial`, before building the row:

```typescript
  const { default: gsap } = await import("gsap");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
```

- [ ] **Step 3: Tween the drawer on selection, skip the tween when `reduce`**

Replace `poblarCajon(index)`'s call site inside `abrir()`:

```typescript
  function abrir(index: number): void {
    if (index === seleccionado) return;
    cards[seleccionado]?.classList.remove("is-sel");
    seleccionado = index;
    cards[seleccionado]?.classList.add("is-sel");
    poblarCajon(index);
    if (reduce) return;
    gsap.fromTo(
      drawer,
      { opacity: 0, y: 14 },
      { opacity: 1, y: 0, duration: 0.3, ease: "cubic-bezier(0.7,0,0.2,1)" },
    );
  }
```

- [ ] **Step 4: Hover-without-click lifts the card, never opens the drawer**

```typescript
  cards.forEach((card, index) => {
    card.addEventListener("click", () => abrir(index));
    if (reduce) return;
    const tilt = TILTS[index] ?? 0;
    card.addEventListener("pointerenter", () => {
      gsap.to(card, {
        y: -6,
        rotate: 0,
        boxShadow: "0 18px 34px -8px rgba(0,0,0,.5)",
        duration: 0.22,
        ease: "power2.out",
      });
    });
    card.addEventListener("pointerleave", () => {
      gsap.to(card, {
        y: 0,
        rotate: tilt,
        boxShadow: "0 10px 22px -8px rgba(0,0,0,.4)",
        duration: 0.22,
        ease: "power2.out",
      });
    });
  });
```

Note: `tilt` is only meaningful once the entrance choreography (Task 5) sets each card's resting
`rotate` to its tilt value — before Task 5 this hover will straighten a card that was never tilted,
which is harmless (rotates 0→0) but confirms the wiring is correct ahead of Task 5.

- [ ] **Step 5: `npm run build`, then manually confirm in the browser: clicking a different card now
  visibly slides the drawer up 14px while fading in; hovering a card (without clicking) lifts it
  without touching the drawer.**

```bash
npm run build
```

- [ ] **Step 6: Commit**

```bash
git add src/components/caelestiaObraEditorial.ts
git commit -m "feat(caelestia): la seleccion de Obra entra por el eje Y, el roce solo levanta la tarjeta"
```

---

### Task 5: Entrance choreography — "Caída"

**Files:**
- Modify: `src/components/caelestiaObraEditorial.ts`

**Interfaces:**
- Consumes: `gsap` (already imported in Task 4).
- Produces: nothing new consumed elsewhere — this is the mount-time animation, replacing the
  instant `abrir(0)` call from Task 3 with the full choreography from the spec's `## La entrada de
  escena`.

- [ ] **Step 1: Give each drawer field an addressable hook for the layered reveal**

Modify `poblarCajon` so the pieces the entrance needs to stagger are queryable. Add `data-*`
attributes in the builders from Task 3:

```typescript
  function poblarCajon(index: number): void {
    const project = caseStudies[index];
    const titleBlock = el("div", "cae-obra-drawer-title", [
      el("div", "cae-obra-drawer-kick", [project.tag]),
      el("h3", "", [project.title]),
      el("p", "cae-obra-drawer-lead", [project.lead]),
      buildFoot(project),
    ]);
    titleBlock.querySelector("h3")?.setAttribute("data-cae-obra-h3", "");
    const preview = buildPreview(project);
    const meta = buildMeta(project);
    const prose = el("div", "cae-obra-prose", [
      el("div", "", [el("h4", "", ["Problema"]), el("p", "", [project.problem])]),
      el("div", "", [el("h4", "", ["Solución"]), el("p", "", [project.solution])]),
    ]);
    drawer.replaceChildren(titleBlock, preview, meta, prose);
  }
```

- [ ] **Step 2: Replace the unconditional `abrir(0);` call with the entrance timeline**

```typescript
  if (reduce) {
    abrir(0);
  } else {
    entrarConCaida();
  }

  function entrarConCaida(): void {
    cards.forEach((card, index) => {
      const tilt = TILTS[index] ?? 0;
      gsap.set(card, { opacity: 0, y: -46, rotate: tilt, transformOrigin: "50% 0%" });
    });

    seleccionado = 0;
    cards[0]?.classList.add("is-sel");
    poblarCajon(0);

    const h3 = drawer.querySelector<HTMLElement>("[data-cae-obra-h3]");
    const kick = drawer.querySelector<HTMLElement>(".cae-obra-drawer-kick");
    const lead = drawer.querySelector<HTMLElement>(".cae-obra-drawer-lead");
    const foot = drawer.querySelector<HTMLElement>(".cae-obra-foot");
    const preview = drawer.querySelector<HTMLElement>(".cae-obra-drawer-preview");
    const rows = Array.from(drawer.querySelectorAll<HTMLElement>(".cae-obra-drawer-meta > div"));
    const blocks = Array.from(drawer.querySelectorAll<HTMLElement>(".cae-obra-prose > div"));

    gsap.set(drawer, { opacity: 0 });
    if (h3) gsap.set(h3, { clipPath: "inset(0 100% 0 0)" });
    gsap.set([kick, lead, foot].filter(Boolean), { opacity: 0, y: 6 });
    if (preview) gsap.set(preview, { opacity: 0, scale: 0.94 });
    gsap.set(rows, { opacity: 0, y: 8 });
    gsap.set(blocks, { opacity: 0, y: 8 });

    const tl = gsap.timeline();
    tl.fromTo(
      cards,
      { opacity: 0, y: -46, rotate: (i: number) => TILTS[i] ?? 0 },
      { opacity: 1, y: 0, rotate: 0, duration: 0.5, ease: "bounce.out", stagger: 0.08 },
    )
      .to(drawer, { opacity: 1, duration: 0.01 }, "-=.1")
      .to(kick, { opacity: 1, y: 0, duration: 0.2, ease: "power2.out" }, "-=.05")
      .to(h3, { clipPath: "inset(0 0% 0 0)", duration: 0.42, ease: "power2.inOut" }, "-=.05")
      .to(preview, { opacity: 1, scale: 1, duration: 0.32, ease: "power2.out" }, "-=.3")
      .to([lead, foot], { opacity: 1, y: 0, duration: 0.22, ease: "power2.out", stagger: 0.06 }, "-=.18")
      .to(rows, { opacity: 1, y: 0, duration: 0.24, ease: "power2.out", stagger: 0.06 }, "-=.1")
      .to(blocks, { opacity: 1, y: 0, duration: 0.26, ease: "power2.out", stagger: 0.08 }, "-=.12");
  }
```

Note: after `entrarConCaida()` runs, each card's resting `rotate` is 0 (the timeline animates `rotate`
to `0`, not to `tilt`) — Task 4's hover-leave handler restores `rotate: tilt`, which would un-flatten
a card that just landed flat. **Fix Task 4's `pointerleave` handler now**: change
`rotate: tilt` to `rotate: 0` in that handler, since the landed resting state is always flat (the
tilt only exists during the fall, per the spec: cards "se asientan con `ease: bounce.out`" — they
land at `rotate: 0`, not at their tilt). Re-run the Task 4 manual check after this fix.

- [ ] **Step 3: `npm run build`**

```bash
npm run build
```
Expected: zero errors.

- [ ] **Step 4: Manual verification — watch the entrance**

```bash
npx vite preview --port 4173 &
```
Open `http://localhost:4173/?theme=caelestia`, navigate to the Obra workspace pill fresh (reload the
page first so the entrance replays). Expected, in order: the five cards fall from above with visibly
different rotations, bounce once, and settle flat in a row; then the first card's drawer content
appears in layers — title swept open left-to-right, then the kick label and preview, then the four
metadata rows in a quick cascade, then the two prose paragraphs.

- [ ] **Step 5: Commit**

```bash
git add src/components/caelestiaObraEditorial.ts
git commit -m "feat(caelestia): entrada Caida de Obra — tarjetas fisicas, cajon en cuatro capas"
```

---

### Task 6: Reduced motion lands instantly

**Files:**
- Modify: `src/components/caelestiaObraEditorial.ts` (verification only — the `if (reduce)` branches
  written in Tasks 4-5 already implement this; this task is the explicit check + any gaps found)

- [ ] **Step 1: Audit every `gsap.set`/`gsap.to`/`gsap.fromTo` call added in Tasks 4-5 and confirm
  each sits behind a `reduce` guard or inside `entrarConCaida()`, which is itself only called in the
  `else` branch of `if (reduce) { abrir(0); } else { entrarConCaida(); }`.** The hover listeners in
  Task 4 already `return` early when `reduce` is true, before attaching `pointerenter`/`pointerleave`
  — confirm that guard is still in place after Task 5's edits (it lives above the `TILTS[index]`
  line inside the `cards.forEach` in Task 4's Step 4).

- [ ] **Step 2: Manual verification with reduced motion forced**

Chromium DevTools → Rendering tab → "Emulate CSS media feature prefers-reduced-motion: reduce".
Reload `http://localhost:4173/?theme=caelestia` and navigate to Obra.
Expected: all five cards are visible immediately, flat, no rotation; the first card shows `is-sel`;
the drawer is fully populated with EchoPlan's data with no fade-in; clicking a different card swaps
the drawer instantly (no 0.3s tween); hovering a card does nothing.

- [ ] **Step 3: If any gap is found, fix it inline in `caelestiaObraEditorial.ts` and re-run Step 2.**

- [ ] **Step 4: Commit (only if Step 3 required a change; otherwise this task produces no diff and
  is folded into Task 5's commit)**

```bash
git add src/components/caelestiaObraEditorial.ts
git commit -m "fix(caelestia): cierra un hueco de movimiento reducido en la Editorial de Obra"
```

---

### Task 7: Wire the module into `main.ts`

**Files:**
- Modify: `src/main.ts:150-157` (right after the existing Hyprland `cartelHandle` block — find the
  exact lines with `grep -n "cartelHandle" src/main.ts`)
- Modify: `src/main.ts:274` area (the `pagehide` listener — find with `grep -n "cartelHandle?.destroy" src/main.ts`)

**Interfaces:**
- Consumes: `mountCaelestiaObraEditorial` from `./components/caelestiaObraEditorial` (Task 2-6).

- [ ] **Step 1: Add the deferred mount, mirroring the Hyprland cartel block exactly**

Insert immediately after the existing block that ends `cartelHandle = await mountObraCartel(app); });`
(around line 157):

```typescript
// La Editorial de Obra en Caelestia: fila de cinco tarjetas + cajon. Import
// diferido, igual que el resto de modulos de tema.
let caeObraHandle: { destroy: () => void } | null = null;
if (theme.id === "caelestia") {
  void import("./components/caelestiaObraEditorial").then(
    async ({ mountCaelestiaObraEditorial }) => {
      caeObraHandle = await mountCaelestiaObraEditorial(app);
    },
  );
}
```

- [ ] **Step 2: Add cleanup to the existing `pagehide` listener**

Find the line `caeShellHandle?.destroy();` inside the `pagehide` listener and add immediately after
it:

```typescript
    caeObraHandle?.destroy();
```

- [ ] **Step 3: `npm run build`**

```bash
npm run build
```
Expected: zero errors. `mountCaelestiaObraEditorial` must already be exported with that exact name
from Task 2 — if `tsc` reports a missing export, the name drifted between this task and Task 2; fix
the mismatch in `caelestiaObraEditorial.ts`, not here.

- [ ] **Step 4: Full-theme smoke test — confirm Vice and Hyprland are untouched**

```bash
npx vite preview --port 4173 &
```
Visit `http://localhost:4173/?theme=vice`, `?theme=hyprland`, and `?theme=caelestia` in turn, each
navigated to the Obra section/workspace. Expected: Vice's obra rail still scrolls horizontally with
the five full-screen scenes exactly as before; Hyprland's cartel (five titulares + captura on hover)
still works exactly as before; Caelestia now shows the Editorial row + drawer with the Caída entrance.
Zero console errors on all three.

- [ ] **Step 5: Commit**

```bash
git add src/main.ts
git commit -m "feat(caelestia): monta la Editorial de Obra desde main.ts"
```

---

### Task 8: `scripts/measure-caelestia-obra.py` — the gate harness

**Files:**
- Create: `scripts/measure-caelestia-obra.py`

**Interfaces:**
- Consumes: the built site served at `--base` (default `http://localhost:4173`), Playwright (sync
  API, already a project dependency per `rules/verification.md`).

- [ ] **Step 1: Write the harness skeleton with the "fits, no internal scroll" assertion — the
  reason this phase exists**

```python
#!/usr/bin/env python3
"""
Arnes de la fase B3 (Obra) de Caelestia. Ver
docs/superpowers/specs/2026-09-03-caelestia-obra-design.md, seccion "## Los gates".

Uso:
    npm run build && npx vite preview --port 4173 &
    python3 scripts/measure-caelestia-obra.py --base http://localhost:4173
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

FALLOS = []


def assert_true(cond: bool, mensaje: str) -> None:
    if not cond:
        FALLOS.append(mensaje)


def ir_a_obra(page) -> None:
    page.click('[data-cae-ws="obra"]')
    page.wait_for_timeout(2500)  # cubre la entrada Caida completa a velocidad real


def medir_cabe(page) -> None:
    rect = page.evaluate(
        """
        () => {
          const rail = document.querySelector('[data-obra-rail]');
          const r = rail.getBoundingClientRect();
          let maxBottom = 0;
          rail.querySelectorAll('*').forEach(el => {
            const er = el.getBoundingClientRect();
            maxBottom = Math.max(maxBottom, er.bottom - r.top);
          });
          const win = rail.closest('[data-cae-track] > *') || rail.parentElement;
          return { contenido: maxBottom, ventana: win.getBoundingClientRect().height };
        }
        """
    )
    desborda = rect["contenido"] - rect["ventana"]
    assert_true(desborda <= 2, f"Cabe: contenido {rect['contenido']:.0f}px vs ventana {rect['ventana']:.0f}px (desborda {desborda:.0f}px)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:4173")
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{args.base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        ir_a_obra(page)
        medir_cabe(page)
        browser.close()

    if FALLOS:
        print(f"FALLA ({len(FALLOS)}):")
        for f in FALLOS:
            print(f"  - {f}")
        return 1
    print("Todo verde.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it against `main` BEFORE this feature's changes are checked out, to confirm it
  fails for the right reason**

```bash
git stash
npm run build && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-obra.py --base http://localhost:4173
```
Expected: FAIL, with the "Cabe" message reporting the pre-existing overflow (contenido ~4964px vs
ventana ~748px — the exact numbers from the spec's `## Por qué` table). This is the check required
by "Ningún gate se da por bueno sin haberlo visto dar rojo contra el fallo que dice cazar."
```bash
git stash pop
```

- [ ] **Step 3: Run it against this feature's branch**

```bash
npm run build && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-obra.py --base http://localhost:4173
```
Expected: PASS (desborda ≤ 2px).

- [ ] **Step 4: Add the remaining eight assertions from the spec's `## Los gates`, following the
  same `assert_true`/`FALLOS` pattern as Step 1** — each one below is its own sub-step; run the full
  script after each and confirm no regression in the assertions already passing.

  - [ ] **4a. Los cinco proyectos son alcanzables** — `page.query_selector_all('.cae-obra-card')`
    returns 5 elements, each with a bounding box fully inside `[data-obra-rail]`'s box, and each
    reachable via `Tab` (assert `document.activeElement` cycles through all five `data-obra-card`
    values when pressing `Tab` from the workspace pill).
  - [ ] **4b. Ninguna captura queda cortada** — for each `.cae-obra-thumb`, assert its
    `getBoundingClientRect()` is fully within the viewport and within `[data-obra-rail]`'s box.
  - [ ] **4c. Anti-mock** — assert every visible title/tag/role/status/problem/solution string
    returned by `page.evaluate` matches one of the five entries hard-coded in the script from
    `caseStudies` (copy the five titles/tags as a Python list at the top of the file); assert
    `"tooling"` never appears in any rendered text; assert the "Periodo" `<dt>` is absent exactly
    for the card whose title is `"TesisFar"` and present for the other four.
  - [ ] **4d. Aguanta los dos extremos** — click the EchoPlan card, assert the drawer's `.cae-obra-prose p`
    elements are non-empty and their bottom edge is within `[data-obra-rail]`; repeat for TesisFar.
  - [ ] **4e. Contraste** — reuse `check_contrast_wcag`-style sampling (see `scripts/verify.py` for
    the existing implementation) against `.cae-obra-drawer-title h3`, `.cae-obra-drawer-kick`,
    `.cae-obra-foot a`, sweeping 4 sample hours (00:00, 06:00, 12:00, 18:00) via
    `page.evaluate` re-dispatching `caelestia:esquema` is not available headlessly — instead, mock
    the clock by evaluating `Date` is out of scope for this harness; **document this as a known gap**
    in a comment (the full 24h sweep technique lives in `measure-caelestia-hora.py` and should be
    reused in a follow-up if this becomes a real requirement — see `scripts/measure-caelestia-hora.py`
    for the pattern of overriding the system clock before page load).
  - [ ] **4f. Movimiento reducido** — new `page.context()` created with
    `reduced_motion="reduce"`, reload, assert `.cae-obra-card.is-sel` exists immediately after
    `wait_for_timeout(300)` (not 2500) and assert no `.cae-obra-card` has a non-zero `transform`
    translateY at that point.
  - [ ] **4g. Foco visible** — `Tab` to the visible link inside the drawer (EchoPlan is private, so
    first click TesisFar which has a link), assert `document.activeElement` matches the anchor and
    `getComputedStyle(document.activeElement).outlineStyle !== "none"`.
  - [ ] **4h. Vice y Hyprland intactos** — repeat `medir_cabe`-style height checks are N/A (those
    themes are allowed to differ); instead assert `document.querySelector('[data-obra-track]')` is
    **visible** (`display !== "none"`) under `?theme=vice` and `?theme=hyprland`, and **hidden**
    under `?theme=caelestia` — the one invariant Task 1's CSS establishes.

- [ ] **Step 5: `npm run lint` on the new Python file is N/A (project lint is JS/TS only per
  `package.json`); instead run the script once more standalone to confirm it exits 0**

```bash
python3 scripts/measure-caelestia-obra.py --base http://localhost:4173
```
Expected: `Todo verde.`, exit code 0.

- [ ] **Step 6: Commit**

```bash
git add scripts/measure-caelestia-obra.py
git commit -m "test(caelestia): arnes de la fase B3 (Obra) — nueve aserciones del spec"
```

---

### Task 9: Full verification pass and PROGRESS.json close-out

**Files:** none created; this task only runs checks and updates tracking files already required by
`.claude/rules/progress-tracking.md`.

- [ ] **Step 1: `npm run build && npm run lint`** — both clean.

- [ ] **Step 2: `python3 scripts/verify.py`** against the served production build — code 0 (or only
  the known pre-existing fixtures in `scripts/verify-baseline.json`, per that script's own rules).

- [ ] **Step 3: `python3 scripts/measure-caelestia-obra.py --base http://localhost:4173`** — all nine
  assertions green.

- [ ] **Step 4: Screenshots** — 1440×900 and 390×844, `?theme=caelestia`, Obra workspace, one with
  the first card selected (default) and one after clicking a second card. Confirm visually: real
  captures still show the Vice-palette placeholders (expected — the documented blocker), the drawer
  layout matches the spec's composition diagram, no layout breakage at 390px (mobile is out of scope
  per fase A but must not visibly crash).

- [ ] **Step 5: Update `docs/superpowers/specs/2026-09-03-caelestia-obra-design.md`'s `Estado:`
  header from `pendiente de plan` to `implementado`** — but **only the structural/interaction gate**;
  the spec's `## Bloqueo de implementación` section stays as-is and must NOT be marked resolved,
  since the nine real captures are still pending. If the spec's self-consistency checker
  (`check_spec_plan_consistency()` in `scripts/verify.py`) objects to `implementado` with an open
  blocker noted in prose, use `en ejecucion` instead — check which the script accepts before
  committing.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/specs/2026-09-03-caelestia-obra-design.md
git commit -m "docs(caelestia): la fase B3 (Obra) queda implementada, capturas reales pendientes"
```

---

## What stays out of scope

- **The nine real captures.** `public/media/obra/*.webp` keep their Vice-palette placeholders after
  this plan. Swapping them in is a follow-up task once Aoshi supplies the files — no code change
  needed beyond dropping the new files in place, since `caseStudies[].gallery[].src` already points
  at those exact paths.
- **Mobile layout for Obra.** Out of scope for the whole B1-B5 arc per the fase A decision recorded
  in the spec.
- **The 24h contrast sweep** for the gate harness (Task 8, step 4e) — flagged as a known gap with a
  pointer to the existing pattern in `measure-caelestia-hora.py`, not blocking this plan.
