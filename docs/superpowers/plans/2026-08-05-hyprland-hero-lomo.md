# Hero de Ascua "El lomo" — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar el hero del tema Hyprland ("Ascua") con un dispositivo propio (etiqueta de rol
rotada + filete vertical, "el lomo") y una coreografía de entrada bespoke (doble exposición
fusionada con el corte del nombre), sin tocar Vice ni Caelestia.

**Architecture:** El DOM del hero es compartido por los tres temas (`src/sections/hero.ts`); se le
añaden nodos nuevos (divisor, fantasma, spans por palabra) que Vice/Caelestia ocultan por defecto
(`display: none` en `style.css`, patrón ya usado por `.about-pairs`) y que Hyprland reactiva y
posiciona en `themes.css`. El movimiento entero es CSS puro, disparado por la clase `.is-lit` que
`hypr.choreography.ts` **ya** añade a cada escena al entrar en viewport — no hace falta timeline
de GSAP nueva, solo sacar al hero de la receta genérica para que sus piezas no lleven también
`hypr-cut`/`hypr-up`.

**Tech Stack:** TypeScript estricto (DOM manual vía `el()`), CSS puro (custom properties, `clip-path`,
CSS Grid, container queries), GSAP + ScrollTrigger ya presentes en `hypr.choreography.ts`.

## Global Constraints

- Vice y Caelestia no se tocan — verificar con `python3 scripts/verify.py --theme vice` y
  `--theme caelestia` antes y después de cada tarea que toque un archivo compartido.
- `npm run build` (`tsc && vite build`) y `npm run lint` en verde antes de cada commit.
- Nunca `gsap.from`; si se añade cualquier tween nuevo, `fromTo` con los dos extremos escritos a
  mano. (Este plan no añade tweens nuevos — toda la animación queda en CSS.)
- Todo elemento animado nuevo entra en el bloque `@media (prefers-reduced-motion: reduce)` de
  `themes.css` (hoy en las líneas ~1276-1284).
- Sin `any`; `unknown` + guards si hace falta tipar algo dinámico.
- Radio 0 en todo lo nuevo — Ascua es "luz con canto", no debe redondear nada.
- Cortes (`clip-path`/`scaleX`/`scaleY`) en `--hard` (400-500ms, sin rebote); atmosférico
  (fantasma, fades) en `--slow` (900ms+). No introducir una tercera curva.
- Colapso responsive del "lomo" en `max-width: 900px` — mismo umbral que ya usa
  `.contacto-bar-label` (Vice) para el mismo problema, no un breakpoint nuevo.
- Commits frecuentes, uno por tarea, formato `tipo(hero): descripción` (scope `hero` además de
  `hyprland` porque el cambio vive en una sección compartida).

Spec de referencia: `docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md`.

---

## Mapa de archivos

| Archivo | Qué cambia |
|---|---|
| `src/sections/hero.ts` | DOM: nuevos nodos (`.hero-divider`, `.hero-name-wrap`, `.hero-name-ghost`, spans `.hero-name-word`), `.hero-corner` pasa a vivir dentro de `.hero-surface`. |
| `src/style.css` | Reglas por defecto (`display: none`) para los nodos nuevos, para que Vice/Caelestia los ignoren sin CSS propia. |
| `src/themes/themes.css` | Bloque Hyprland del hero (~1158-1284): grid, spine, filete, fantasma, cortes, corner reconstruido, idle, colapso móvil, fallback `prefers-reduced-motion`. |
| `src/themes/hypr.choreography.ts` | Excluir al hero de la `RECETA` genérica; recalibrar la base de `--bx`. |

---

### Task 1: DOM del hero — nodos nuevos, sin romper Vice/Caelestia

**Files:**
- Modify: `src/sections/hero.ts` (reescritura completa, 45 líneas actuales)
- Modify: `src/style.css` (añadir reglas cerca de `.hero-kick`/`.hero-corner`, cerca de la línea 166)

**Interfaces:**
- Produces: `createHero(): HTMLElement` sigue con la misma firma; el `<section data-scene="hero">`
  resultante gana `.hero-divider` y `.hero-name-wrap > (.hero-name-ghost, h1.display-xl > .hero-name-word*)`
  como nodos nuevos, y `.hero-corner` pasa a ser hijo de `.hero-surface` en vez de hermano.
- Consumes: `identity` de `src/data/content.ts` (`name`, `role`, `subheadline`, `location`,
  `email` — ya existen, sin cambios de tipo).

- [x] **Step 1: Reescribir `hero.ts`**

```ts
import { identity } from "../data/content";
import { el } from "../utils/dom";

/**
 * Apertura. Suelo de conversion garantizado: nombre, rol y contacto legibles
 * al instante, sin depender de que el video o las animaciones hayan cargado.
 * El layout concreto lo decide el tema (themes.css).
 *
 * Hyprland ("Ascua") anade tres piezas que Vice/Caelestia no muestran nunca
 * (`display: none` en style.css, mismo patron que `.about-pairs`):
 * `.hero-divider` (el filete vertical del "lomo"), `.hero-name-ghost` (la
 * copia fantasma de la doble exposicion, aria-hidden) y el propio nombre
 * dividido en un `<span>` por palabra para el corte palabra-a-palabra.
 * Spec: docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md
 */
export function createHero(): HTMLElement {
  // El valor del atributo declara hacia donde sale cada bloque en el gesto de
  // salida de Vice (`vice.choreography.ts`): lo que esta sobre el nombre se va
  // hacia arriba y lo que esta debajo hacia abajo, de modo que el nombre queda
  // solo en el centro. El selector `[data-hero-fade]` que usan reveal.ts y
  // style.css no distingue valor, asi que los otros dos temas no se enteran.
  const eyebrow = el("p", "hero-kick", [identity.role]);
  eyebrow.setAttribute("data-hero-fade", "up");

  // Un <span> por palabra + el espacio literal entre ellos como nodo de texto
  // aparte: bajo Hyprland el espacio no se usa (el corte usa `gap` de flex),
  // pero para Vice/Caelestia (flujo normal, sin flex) es lo que mantiene el
  // espaciado visible entre palabras identico al de un h1 con texto plano.
  const words = identity.name.split(" ").flatMap((word, i, arr) => {
    const span = el("span", "hero-name-word", [word]);
    return i < arr.length - 1 ? [span, " "] : [span];
  });
  const name = el("h1", "display-xl mt-4 text-[clamp(2.8rem,11vw,9.5rem)]", words);
  name.setAttribute("data-hero-name", "");

  // Decorativo puro (duplica visualmente el nombre real): fuera del arbol de
  // accesibilidad para que un lector de pantalla no lo anuncie dos veces.
  const ghost = el("div", "hero-name-ghost", [identity.name]);
  ghost.setAttribute("aria-hidden", "true");

  const nameWrap = el("div", "hero-name-wrap", [ghost, name]);

  const lead = el("p", "lead mx-auto mt-5 max-w-[32ch] text-paper/85", [identity.subheadline]);
  lead.setAttribute("data-hero-fade", "down");

  const location = el("span", "", [identity.location]);

  const email = el("a", "hero-mail", [identity.email]);
  email.href = `mailto:${identity.email}`;

  const corner = el("div", "hero-corner", [location, email]);
  corner.setAttribute("data-hero-fade", "down");

  // Solo pinta bajo Hyprland (style.css lo oculta por defecto). La chispa y
  // el destello son hijos propios en vez de pseudo-elementos porque un
  // contenedor solo tiene `::before`/`::after` disponibles y el filete ya
  // necesita ambos para el trazo que crece y el corte de la palabra 1.
  const spark = el("span", "hero-divider-spark");
  const landing = el("span", "hero-divider-landing");
  const divider = el("div", "hero-divider", [spark, landing]);
  divider.setAttribute("aria-hidden", "true");

  // Envoltorio comun a los tres temas: Caelestia lo viste como tarjeta
  // Material You (themes.css), Vice y Hyprland lo neutralizan a sangre.
  // El DOM es unico; solo el CSS colgado de [data-theme] decide la piel.
  // `.hero-corner` vive AHORA dentro de la superficie (antes era hermano):
  // en Vice/Caelestia sigue con `position: absolute` (style.css), asi que su
  // posicion visual no cambia pase lo que pase con su padre; en Hyprland pasa
  // a fluir en la columna de contenido del "lomo" (position: static en
  // themes.css, ver Task 2).
  const surface = el("div", "hero-surface", [nameWrap, lead, corner]);

  const section = el(
    "section",
    "hero relative flex min-h-screen flex-col justify-center overflow-hidden px-6 py-24 md:px-12",
    [eyebrow, divider, surface],
  );
  section.setAttribute("data-scene", "hero");

  return section;
}
```

- [x] **Step 2: Ocultar los nodos nuevos por defecto en `style.css`**

Cerca de `.hero-kick`/`.hero-corner` (línea ~166), añadir:

```css
/*
 * Piezas exclusivas del "lomo" de Hyprland (Ascua). Ocultas por defecto,
 * mismo patron que `.about-pairs` (linea 803): Vice y Caelestia comparten el
 * DOM pero nunca las muestran, solo `themes.css` bajo
 * `[data-theme="hyprland"]` las reactiva.
 * Spec: docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md
 */
.hero-divider,
.hero-name-ghost {
  display: none;
}
```

- [x] **Step 3: Build y lint**

Run: `npm run build && npm run lint`
Expected: ambos en verde. `tsc` no debe quejarse — `el()` ya acepta `(Node | string)[]`, y
`flatMap` sobre `string[]` produce `(HTMLSpanElement | string)[]`, compatible.

- [x] **Step 4: Confirmar que Vice y Caelestia no cambiaron**

```bash
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
```

Expected: mismo resultado que antes de este cambio (compara contra la baseline existente — si
algo nuevo aparece, es una regresión de este task, no un fallo preexistente).

- [x] **Step 5: Captura rápida de los tres temas**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for theme in ('vice', 'caelestia', 'hyprland'):
        pg = b.new_page(viewport={'width':1440,'height':900})
        pg.goto(f'http://localhost:5173/?theme={theme}', wait_until='domcontentloaded', timeout=30000)
        pg.wait_for_timeout(2500)
        pg.screenshot(path=f'/tmp/hero-task1-{theme}.png')
        pg.close()
    b.close()
"
```

Expected (con `npm run dev` corriendo en paralelo): Vice y Caelestia se ven byte a byte igual que
antes de este task (el fantasma/divisor están ahí en el DOM pero `display: none`); Hyprland
todavía se ve como el hero viejo (sin grid, sin recorte) — normal, la piel nueva llega en las
tareas siguientes.

- [x] **Step 6: Commit**

```bash
git add src/sections/hero.ts src/style.css
git commit -m "feat(hero): nodos del 'lomo' en el DOM compartido, ocultos salvo en hyprland"
```

---

### Task 2: Layout estructural de Hyprland — grid, spine, filete, corner en flujo

**Files:**
- Modify: `src/themes/themes.css:1158-1238` (bloque `.hero`, `.hero-kick`, `.hero-corner`,
  `.hero-mail` de Hyprland — reemplaza el contenido existente)

**Interfaces:**
- Consumes: clases del Task 1 (`.hero-divider`, `.hero-name-wrap`, `.hero-name-ghost`,
  `.hero-name-word`, `.hero-corner` ahora dentro de `.hero-surface`).
- Produces: layout final en reposo (sin animación todavía — eso es la Task 3). Deja el hero
  visualmente correcto a 1440px y a <900px, aunque estático.

- [x] **Step 1: Reemplazar el bloque `.hero`/`.hero-kick`/`.hero-corner`/`.hero-mail`**

Sustituir desde `:root[data-theme="hyprland"] .hero {` (línea 1158) hasta el cierre de
`:root[data-theme="hyprland"] .hero-mail:hover, ... :focus-visible { color: var(--l1); }`
(línea 1237) por:

```css
/*
  "El lomo": grid de 3 columnas (etiqueta rotada | filete | contenido).
  Colapsa a 1 columna en el mismo umbral que ya usa `.contacto-bar-label`
  (Vice, themes.css ~2798) para el mismo problema — etiqueta rotada que deja
  de caber — asi que no se introduce un breakpoint nuevo.
  Spec: docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md
*/
:root[data-theme="hyprland"] .hero {
  display: grid;
  grid-template-columns: 3.4rem 1px 1fr;
  column-gap: 2rem;
  align-items: center;
  /*
    `align-content` no puede quedar en su valor por defecto: CSS Grid
    resuelve `normal` a `stretch` (a diferencia de flexbox, donde resuelve a
    `start`) — con `min-h-screen` (heredado, ver hero.ts) y filas de
    contenido mas cortas que la pantalla, el navegador REPARTE el sobrante
    entre filas en vez de agruparlas. En desktop hay una sola fila (no se
    nota); en el colapso a columna unica (900px, mas abajo) son 3 filas y el
    bug se ve como huecos enormes y desiguales. `center` conserva el mismo
    reparto de aire arriba/abajo que ya tenia el hero via `justify-center`
    (la clase compartida en `hero.ts`), no lo amontona todo abajo.
    Encontrado verificando el mockup a 390x844 real, no en el diseno
    original — ver spec, seccion "Hallazgos de movil".
  */
  align-content: center;
  text-align: left;
}

:root[data-theme="hyprland"] .hero-kick {
  font-family: var(--font-body);
  font-size: var(--t-1);
  font-weight: 600;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--haze);
  margin: 0;
  /* el lomo: etiqueta rotada, texto pegado a la base de su columna */
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  align-self: stretch;
  display: flex;
  align-items: flex-end;
  padding-bottom: 0.5rem;
}

:root[data-theme="hyprland"] .hero-divider {
  display: block;
  background: var(--rule);
  align-self: stretch;
  position: relative;
  overflow: visible;
  container-type: size;
}

:root[data-theme="hyprland"] .hero-surface {
  min-width: 0;
}

/*
  Antes: `position: absolute; bottom: 9%; left/right: 1.5rem` heredado del
  `.hero-corner` compartido (style.css:166) — Vice/Caelestia lo dejan asi a
  proposito (flota sobre el plano, no estorba). Aqui necesita fluir dentro de
  la columna de contenido del "lomo", asi que se reemplaza `position` por
  `relative` (tambien sirve de ancla al filete dibujado, ver Task 3).
*/
:root[data-theme="hyprland"] .hero-corner {
  position: relative;
  display: flex;
  gap: 1.6rem;
  padding-top: 1rem;
  font-size: var(--t-1);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--haze);
}

:root[data-theme="hyprland"] .hero-mail {
  position: relative;
  display: inline-block;
  padding: 2px 1px;
  color: var(--haze);
  text-decoration: none;
  transition: color 0.3s var(--slow);
}
:root[data-theme="hyprland"] .hero-mail:hover,
:root[data-theme="hyprland"] .hero-mail:focus-visible {
  color: var(--l1);
  outline: none;
}

/* Colapso a columna unica: mismo umbral que `.contacto-bar-label` (Vice). */
@media (max-width: 900px) {
  :root[data-theme="hyprland"] .hero {
    grid-template-columns: 1fr;
    row-gap: 1.2rem;
  }
  :root[data-theme="hyprland"] .hero-kick {
    writing-mode: horizontal-tb;
    transform: none;
    align-self: auto;
    padding-bottom: 0;
  }
  :root[data-theme="hyprland"] .hero-divider {
    width: 100%;
    height: 1px;
    align-self: auto;
  }
  /*
    El clamp heredado de Ascua para `.display-xl` (min 50.52px, `--t-6`) ya
    era grande en movil ANTES de este rediseno — no es una regresion de esta
    tarea, pero como se esta tocando el hero de todas formas, se le fija un
    tope propio y mas comedido aqui. El resto de usos de `.display-xl`
    (about, contacto) NO se tocan.
  */
  :root[data-theme="hyprland"] [data-scene="hero"] .display-xl {
    font-size: clamp(2rem, 9.5vw, 2.6rem);
  }
  :root[data-theme="hyprland"] [data-scene="hero"] .hero-name-ghost {
    font-size: clamp(2rem, 9.5vw, 2.6rem);
  }
  /*
    El corner se apila: en fila, "Caracas, Venezuela" partia en dos lineas
    apretado contra el ancho que dejaba el correo, mientras el correo
    quedaba en una sola linea — desalineados, con un corte de linea justo
    despues de la coma. Mismo patron que ya usa el sitio para el mismo
    problema en las barras de contacto (rotulo encima del valor bajo 520px).
  */
  :root[data-theme="hyprland"] .hero-corner {
    flex-direction: column;
    gap: 0.4rem;
  }
}
```

- [x] **Step 2: Build y lint**

Run: `npm run build && npm run lint`
Expected: verde. CSS puro, no debería tocar `tsc` en absoluto.

- [x] **Step 3: Verificar visualmente el layout en reposo**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for vp, name in [({'width':1440,'height':900}, 'desktop'), ({'width':390,'height':844}, 'mobile')]:
        pg = b.new_page(viewport=vp)
        pg.goto('http://localhost:5173/?theme=hyprland', wait_until='domcontentloaded', timeout=30000)
        pg.wait_for_timeout(2500)
        pg.screenshot(path=f'/tmp/hero-task2-{name}.png')
        pg.close()
    b.close()
"
```

Expected: en desktop, la etiqueta de rol se lee vertical en el borde izquierdo, con el filete
separándola del nombre/lead/correo a la derecha. En mobile, la etiqueta vuelve a horizontal y todo
se apila en una columna. Revisa las capturas — si el nombre no cabe o el filete se ve cortado,
ajustar `grid-template-columns` antes de seguir.

- [x] **Step 4: Confirmar Vice/Caelestia intactos**

```bash
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
```

Expected: sin cambios respecto al Task 1 (esta tarea solo toca el bloque `[data-theme="hyprland"]`).

- [x] **Step 5: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(hero): layout de 'el lomo' en hyprland, grid con colapso a 900px"
```

---

### Task 3: Movimiento — fantasma, cortes, filete con chispa, corner en cadena

**Files:**
- Modify: `src/themes/themes.css` (añadir después del bloque de la Task 2, antes de la sección
  siguiente del archivo)

**Interfaces:**
- Consumes: `.is-lit` — clase que `hypr.choreography.ts` **ya** añade a `[data-scene="hero"]` al
  entrar en viewport (Gesto 1, sin cambios necesarios ahí). Este task no depende de ningún cambio
  en el `.ts`.
- Produces: toda la coreografía de entrada del hero. Depende de que la Task 4
  (`hypr.choreography.ts`) excluya al hero de la `RECETA` genérica — si se salta ese orden, el
  hero recibirá ADEMÁS `hypr-cut`/`hypr-up` en sus piezas y competirá con esta animación. Hacer la
  Task 4 antes de verificar visualmente esta, o verificar ambas juntas.

- [x] **Step 1: Añadir la animación del nombre (fantasma + cortes por palabra)**

```css
/*
  Doble exposicion fusionada con el corte: el filete (Task siguiente) y el
  corte de la PRIMERA palabra arrancan a la vez, mismo trazo — se leen como
  un solo gesto. El fantasma se sostiene visible hasta el 35% de su recorrido
  y solo entonces empieza a apagarse, para que de tiempo a leerlo antes de
  que desaparezca. Duraciones de corte en `--hard` (techo del rango ya
  documentado por la spec de Ascua, 400-500ms) y el fantasma en `--slow`
  extendido a 1.4s (mismo precedente que `hypr-ignite`, que ya dura 1.1s como
  leader de apertura del sitio).
  Spec: docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md
*/
:root[data-theme="hyprland"] .hero-name-wrap {
  position: relative;
}
:root[data-theme="hyprland"] .hero-name-ghost {
  display: block;
  position: absolute;
  inset: 0;
  z-index: 0;
  font-family: var(--font-display);
  font-weight: var(--display-weight);
  letter-spacing: var(--display-tracking);
  line-height: var(--display-leading);
  font-size: clamp(var(--t-6), 8.2vw, var(--t-9));
  color: var(--l2);
  opacity: 0;
  transform: translate(0.35em, -0.28em);
  filter: blur(1px);
  mix-blend-mode: screen;
  pointer-events: none;
}
:root[data-theme="hyprland"] .hero-name-wrap .display-xl {
  position: relative;
  z-index: 1;
}
:root[data-theme="hyprland"] .hero-name-word {
  display: inline-block;
  clip-path: inset(0 100% 0 0);
}
:root[data-theme="hyprland"] .is-lit .hero-name-word {
  animation: hypr-hero-cut 0.5s var(--hard) forwards;
}
:root[data-theme="hyprland"] .is-lit .hero-name-word:nth-of-type(1) {
  animation-delay: 0ms;
}
:root[data-theme="hyprland"] .is-lit .hero-name-word:nth-of-type(2) {
  animation-delay: 300ms;
}
:root[data-theme="hyprland"] .is-lit .hero-name-word:nth-of-type(3) {
  animation-delay: 600ms;
}
:root[data-theme="hyprland"] .is-lit .hero-name-ghost {
  animation: hypr-hero-ghost 1.4s var(--slow) forwards;
}
@keyframes hypr-hero-cut {
  to {
    clip-path: inset(0 0 0 0);
  }
}
@keyframes hypr-hero-ghost {
  0% {
    opacity: 0.75;
    transform: translate(0.35em, -0.28em);
  }
  35% {
    opacity: 0.68;
    transform: translate(0.22em, -0.17em);
  }
  100% {
    opacity: 0;
    transform: translate(0, 0);
  }
}
```

- [x] **Step 2: Añadir la revelación de la etiqueta de rol (spine)**

```css
/*
  Antes: solo fade de opacidad, sola — no se leia como parte del mismo gesto
  que el filete. Ahora se descubre con el mismo lenguaje de corte
  (clip-path), sincronizada con el arranque del filete.
*/
:root[data-theme="hyprland"] .hero-kick {
  clip-path: inset(100% 0 0 0);
}
:root[data-theme="hyprland"] .is-lit .hero-kick {
  animation: hypr-hero-spine 0.5s var(--hard) forwards;
  animation-delay: 220ms;
}
@keyframes hypr-hero-spine {
  to {
    clip-path: inset(0 0 0 0);
  }
}
@media (max-width: 900px) {
  :root[data-theme="hyprland"] .hero-kick {
    /* Solo cambia el punto de partida del corte (de arriba a la izquierda);
       el destino es el mismo `inset(0 0 0 0)` en los dos casos, asi que
       `hypr-hero-spine` (definida arriba, un solo `to`) no necesita
       redefinirse aqui — una animacion de un solo `to` arranca siempre
       desde el `clip-path` estatico vigente en el elemento. */
    clip-path: inset(0 100% 0 0);
  }
}
```

- [x] **Step 3: Añadir el filete con chispa y destello**

```css
/*
  El filete ya no solo crece: una chispa viaja en la punta mientras se
  dibuja, y al llegar abajo hay un destello breve — el mismo vocabulario de
  "canto" que el resto de Ascua, ahora literal en el propio hero.
*/
:root[data-theme="hyprland"] .hero-divider::after {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--l1);
  transform: scaleY(0);
  transform-origin: top;
  transition: transform 0.5s var(--hard);
}
:root[data-theme="hyprland"] .is-lit .hero-divider::after {
  transform: scaleY(1);
}
:root[data-theme="hyprland"] .hero-divider-spark {
  position: absolute;
  left: 50%;
  top: 0;
  width: 10px;
  height: 10px;
  margin-left: -5px;
  margin-top: -5px;
  border-radius: 50%;
  background: var(--l3);
  opacity: 0;
  filter: blur(2px) drop-shadow(0 0 6px var(--l1));
  pointer-events: none;
}
:root[data-theme="hyprland"] .is-lit .hero-divider-spark {
  animation: hypr-hero-spark 0.5s var(--hard) forwards;
}
@keyframes hypr-hero-spark {
  0% {
    transform: translateY(0);
    opacity: 0.9;
  }
  92% {
    opacity: 0.9;
  }
  100% {
    transform: translateY(100cqh);
    opacity: 0;
  }
}
:root[data-theme="hyprland"] .hero-divider-landing {
  position: absolute;
  left: 50%;
  bottom: -3px;
  width: 26px;
  height: 26px;
  margin-left: -13px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--l1) 70%, transparent) 0%, transparent 70%);
  opacity: 0;
  pointer-events: none;
}
:root[data-theme="hyprland"] .is-lit .hero-divider-landing {
  animation: hypr-hero-landing 0.4s var(--slow) forwards;
  animation-delay: 450ms;
}
@keyframes hypr-hero-landing {
  0% {
    opacity: 0;
    transform: scale(0.4);
  }
  40% {
    opacity: 0.9;
    transform: scale(1.1);
  }
  100% {
    opacity: 0;
    transform: scale(1.4);
  }
}
@media (max-width: 900px) {
  :root[data-theme="hyprland"] .hero-divider::after {
    transform: scaleX(0);
    transform-origin: left;
  }
  :root[data-theme="hyprland"] .is-lit .hero-divider::after {
    transform: scaleX(1);
  }
  :root[data-theme="hyprland"] .hero-divider-spark {
    left: 0;
    top: 50%;
    margin-left: -5px;
    margin-top: -5px;
  }
  /*
    Nombre de animacion DISTINTO (no redefinir `hypr-hero-spark` con el mismo
    nombre bajo el media query): a diferencia del spine, aqui el eje de
    `transform` cambia de verdad (Y a X) a lo largo de varios keyframes, no
    solo el punto de partida, asi que no vale la abreviatura de un solo `to`.
    Redeclarar el mismo nombre dentro de un `@media` es CSS valido (gana la
    ultima regla en efecto), pero mas fragil de leer/mantener que dos nombres
    separados — se prefiere explicito.
  */
  :root[data-theme="hyprland"] .is-lit .hero-divider-spark {
    animation-name: hypr-hero-spark-mobile;
  }
  @keyframes hypr-hero-spark-mobile {
    0% {
      transform: translateX(0);
      opacity: 0.9;
    }
    92% {
      opacity: 0.9;
    }
    100% {
      transform: translateX(100cqw);
      opacity: 0;
    }
  }
  :root[data-theme="hyprland"] .hero-divider-landing {
    left: auto;
    right: -3px;
    bottom: auto;
    top: 50%;
    margin-left: 0;
    margin-top: -13px;
  }
}
```

- [x] **Step 4: Añadir la entrada del lead y el corner en cadena de cortes**

```css
:root[data-theme="hyprland"] .lead {
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 1s var(--slow),
    transform 1s var(--slow);
}
:root[data-theme="hyprland"] .is-lit .lead {
  opacity: 0.85;
  transform: none;
  transition-delay: 1050ms;
}

/*
  El corner deja el fade+translateY generico: en el primer mockup, con la
  linea base ya pintada desde el frame 0 y solo un overlay de color
  cambiando encima, no se leia como animacion. Ahora el filete se DIBUJA
  (scaleX) y "Caracas, Venezuela"/el correo se descubren con el mismo
  clip-path que las palabras del nombre, en cadena.
*/
:root[data-theme="hyprland"] .hero-corner::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--l1);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.5s var(--hard);
}
:root[data-theme="hyprland"] .is-lit .hero-corner::before {
  transform: scaleX(1);
  transition-delay: 1300ms;
}
:root[data-theme="hyprland"] .hero-corner > span,
:root[data-theme="hyprland"] .hero-corner > a {
  display: inline-block;
  clip-path: inset(0 100% 0 0);
}
:root[data-theme="hyprland"] .is-lit .hero-corner > span {
  animation: hypr-hero-cut 0.42s var(--hard) forwards;
  animation-delay: 1550ms;
}
:root[data-theme="hyprland"] .is-lit .hero-corner > a {
  animation: hypr-hero-cut 0.42s var(--hard) forwards;
  animation-delay: 1720ms;
}
```

- [x] **Step 5: Añadir el idle — un único pulso, gateado al hover/foco**

```css
/*
  Un solo pulso de opacidad (no el brightness descartado: filtraria sobre un
  degradado ya calibrado en contraste). Gateado a :hover/:focus-within, no
  infinito desde la carga — evita el problema de WCAG 2.2.2 (movimiento
  automatico sostenido sin mecanismo de pausa) sin perder el gesto para quien
  interactua con el hero.
*/
:root[data-theme="hyprland"] .hero:hover .hero-name-wrap .display-xl,
:root[data-theme="hyprland"] .hero:focus-within .hero-name-wrap .display-xl {
  animation: hypr-hero-idle 6s ease-in-out infinite;
}
@keyframes hypr-hero-idle {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.9;
  }
}
```

- [x] **Step 6: Recalibrar el filete superior de `.hero-mail` en `:focus-visible`**

Añadir al final del bloque de `.hero-mail` (junto a lo escrito en la Task 2):

```css
:root[data-theme="hyprland"] .hero-mail::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -2px;
  height: 1px;
  width: 0;
  background: var(--l1);
  transition: width 0.5s var(--hard);
}
:root[data-theme="hyprland"] .hero-mail:hover::after,
:root[data-theme="hyprland"] .hero-mail:focus-visible::after {
  width: 100%;
}
```

- [x] **Step 7: Build y lint**

Run: `npm run build && npm run lint`
Expected: verde.

- [x] **Step 8: Verificación visual con `npm run dev`**

Abrir `http://localhost:5173/?theme=hyprland` en un navegador real (no headless, para ver la
animación con fluidez — swiftshader va lento y distorsiona el ritmo). Confirmar:
- El nombre se revela palabra por palabra con el fantasma asentándose detrás.
- La etiqueta de rol se corta a la vez que arranca el filete.
- La chispa viaja por el filete y hay un destello al llegar abajo.
- "Caracas, Venezuela" y el correo se cortan en cadena después del filete del corner.
- Al pasar el ratón sobre el hero, el nombre pulsa suavemente; al quitarlo, para.
- Tab hasta el correo: aparece el filete de foco, no solo cambio de color.

Esto se confirma con más rigor en la Task 6 (verificación completa); aquí basta una revisión
manual rápida antes de seguir.

- [x] **Step 9: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(hero): entrada del hero en hyprland — fantasma, cortes en cadena, filete con chispa"
```

---

### Task 4: Sacar al hero de la receta genérica y recalibrar `--bx`

**Files:**
- Modify: `src/themes/hypr.choreography.ts:39-50` (Gesto 0 — RECETA), `:99-108` (Gesto 3 — luz)

**Interfaces:**
- Consumes: nada nuevo — sigue leyendo `root.querySelectorAll('[data-scene]')` como hoy.
- Produces: nada que otras tareas consuman; este task es el que hace que la Task 3 funcione sin
  interferencia (si se ejecuta después de la Task 3, la verificación visual de esa tarea habrá
  mostrado el problema: el nombre/lead del hero también recibirían `hypr-cut`/`hypr-up` de la
  receta genérica, compitiendo con la animación bespoke).

- [x] **Step 1: Excluir la escena "hero" del reparto de clases genérico**

En `scenes.forEach((scene) => { ... RECETA.forEach ... })` (línea ~39), añadir un `return`
temprano:

```ts
  scenes.forEach((scene) => {
    // El hero lleva su propio gesto (ver themes.css, bloque
    // `.hero-name-word`/`.hero-kick`/`.hero-corner` bajo `.is-lit`): si
    // tambien recibe `hypr-cut`/`hypr-up` de la receta generica, las dos
    // animaciones compiten sobre las mismas propiedades (clip-path/opacity)
    // en el mismo elemento.
    if (scene.dataset.scene === "hero") return;

    let n = 0;
    RECETA.forEach(([selector, clase]) => {
      Array.from(scene.querySelectorAll<HTMLElement>(selector)).forEach((node) => {
        if (node.classList.contains(clase)) return;
        node.classList.add(clase);
        // 70ms por pieza: el mismo escalonado que el prototipo aprobado.
        node.style.setProperty("--hypr-d", `${n * 70}ms`);
        n += 1;
      });
    });
  });
```

- [x] **Step 2: Recalibrar la base de `--bx`**

En el Gesto 3 (`ScrollTrigger.create({ id: `${ID}-light`, ... onUpdate ... })`, línea ~106),
cambiar la base de `52` a `70` — el nombre ya no está centrado, vive en la columna derecha del
grid, y el barrido de luz debe seguir cruzando por dentro de las letras:

```ts
    onUpdate: (self) => {
      const p = self.progress;
      // Base 70% (antes 52%, centrado): el nombre vive ahora en la columna
      // derecha del grid del "lomo" (themes.css), no centrado en el hero.
      root.style.setProperty("--bx", `${70 + Math.sin(p * Math.PI * 1.4) * 15}%`);
      root.style.setProperty("--by", `${26 + p * 32}%`);
    },
```

- [x] **Step 3: Build y lint**

Run: `npm run build && npm run lint`
Expected: verde.

- [x] **Step 4: Verificar que las otras cuatro escenas siguen recibiendo la receta genérica**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:5173/?theme=hyprland', wait_until='domcontentloaded', timeout=30000)
    pg.wait_for_timeout(2000)
    about_kick = pg.eval_on_selector('[data-scene=\"about\"] .hero-kick', 'el => el.className')
    hero_kick = pg.eval_on_selector('[data-scene=\"hero\"] .hero-kick', 'el => el.className')
    print('about .hero-kick classList:', about_kick)
    print('hero  .hero-kick classList:', hero_kick)
    b.close()
"
```

Expected: `about .hero-kick` sigue incluyendo `hypr-cut` (recibió la receta genérica);
`hero .hero-kick` NO incluye `hypr-cut` ni `hypr-up` (solo lleva la clase base `hero-kick`, sin
`--hypr-d` puesto).

- [x] **Step 5: Confirmar Vice/Caelestia intactos**

```bash
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
```

Expected: sin cambios — este archivo es exclusivo de Hyprland.

- [x] **Step 6: Commit**

```bash
git add src/themes/hypr.choreography.ts
git commit -m "feat(hero): hero fuera de la receta generica, --bx recalibrado a la columna derecha"
```

---

### Task 5: Fallback de `prefers-reduced-motion`

**Files:**
- Modify: `src/themes/themes.css:1276-1284` (bloque `@media (prefers-reduced-motion: reduce)`
  existente de Hyprland — añadir entradas, no crear un bloque nuevo)

**Interfaces:**
- Consumes: todas las clases añadidas en la Task 3.
- Produces: estado final. Con movimiento reducido, el layout completo debe verse exactamente como
  al terminar la animación, sin ningún elemento a medio revelar.

- [x] **Step 1: Ampliar el bloque existente**

El bloque actual (línea 1276) neutraliza `.hypr-cut`/`.hypr-up`/`.hypr-rule`. Añadir las piezas
nuevas del hero:

```css
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .hypr-cut,
  :root[data-theme="hyprland"] .hypr-up,
  :root[data-theme="hyprland"] .hypr-rule {
    clip-path: none;
    opacity: 1;
    transform: none;
    transition: none;
  }

  /* Hero: el layout final estatico, sin ninguna pieza a medio revelar. */
  :root[data-theme="hyprland"] .hero-kick,
  :root[data-theme="hyprland"] .hero-name-word,
  :root[data-theme="hyprland"] .hero-corner > span,
  :root[data-theme="hyprland"] .hero-corner > a {
    clip-path: none !important;
    animation: none !important;
  }
  :root[data-theme="hyprland"] .hero-name-ghost {
    display: none !important;
  }
  :root[data-theme="hyprland"] .hero-divider::after {
    transform: scaleY(1) !important;
    transition: none !important;
  }
  @media (max-width: 900px) {
    :root[data-theme="hyprland"] .hero-divider::after {
      transform: scaleX(1) !important;
    }
  }
  :root[data-theme="hyprland"] .hero-divider-spark,
  :root[data-theme="hyprland"] .hero-divider-landing {
    display: none !important;
  }
  :root[data-theme="hyprland"] .hero-corner::before {
    transform: scaleX(1) !important;
    transition: none !important;
  }
  :root[data-theme="hyprland"] .lead {
    opacity: 0.85 !important;
    transform: none !important;
    transition: none !important;
  }
  :root[data-theme="hyprland"] .hero:hover .hero-name-wrap .display-xl,
  :root[data-theme="hyprland"] .hero:focus-within .hero-name-wrap .display-xl {
    animation: none !important;
  }
}
```

**Nota sobre `!important`:** el proyecto ya usa este patrón en `style.css` (ver comentario junto a
`:root.js-intro [data-hero-name]`) precisamente para blindar el fallback de reduced-motion contra
reglas más específicas — mismo motivo aquí: las reglas de `.is-lit` tienen mayor especificidad
(incluyen `.is-lit` como clase extra) y ganarían por cascada normal sin el `!important`.

- [x] **Step 2: Build y lint**

Run: `npm run build && npm run lint`
Expected: verde.

- [x] **Step 3: Verificar con Playwright en modo reduced-motion**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    ctx = b.new_context(viewport={'width':1440,'height':900}, reduced_motion='reduce')
    pg = ctx.new_page()
    pg.goto('http://localhost:5173/?theme=hyprland', wait_until='domcontentloaded', timeout=30000)
    pg.wait_for_timeout(500)
    word_clip = pg.eval_on_selector('.hero-name-word', 'el => getComputedStyle(el).clipPath')
    ghost_display = pg.eval_on_selector('.hero-name-ghost', 'el => getComputedStyle(el).display')
    lead_opacity = pg.eval_on_selector('[data-scene=\"hero\"] .lead', 'el => getComputedStyle(el).opacity')
    print('word clip-path:', word_clip)
    print('ghost display:', ghost_display)
    print('lead opacity:', lead_opacity)
    pg.screenshot(path='/tmp/hero-reduced.png')
    b.close()
"
```

Expected: `word clip-path` es `none` (nombre completo visible sin esperar ninguna animación),
`ghost display` es `none`, `lead opacity` es `0.85` — todo visible de inmediato, sin animación
pendiente, a los 500ms de cargar (no a los ~2,1s que tarda la secuencia completa con movimiento).

- [x] **Step 4: `verify.py --reduced`**

```bash
python3 scripts/verify.py --theme hyprland --reduced
```

Expected: verde (o mismos fallos preexistentes de la baseline, ninguno nuevo).

- [x] **Step 5: Commit**

```bash
git add src/themes/themes.css
git commit -m "fix(hero): fallback de prefers-reduced-motion para las piezas nuevas del hero"
```

---

### Task 6: Verificación completa y cierre

**Files:** ninguno (solo verificación — si algo falla aquí, vuelve a la tarea correspondiente,
corrige, y repite esta tarea).

**Interfaces:** N/A — tarea de cierre.

- [x] **Step 1: Build y lint limpios**

Run: `npm run build && npm run lint`
Expected: cero errores TypeScript, cero fallos de build, cero errores de lint.

- [x] **Step 2: `verify.py` en los tres temas + reduced**

```bash
python3 scripts/verify.py --theme hyprland
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
python3 scripts/verify.py --theme hyprland --reduced
```

Expected: los cuatro en verde contra la baseline (`scripts/verify-baseline.json`) — si algo de
esta rama arregló un fallo que ya estaba en la baseline, actualízala:
`python3 scripts/verify.py --update-baseline` y revisa el diff antes de commitear.

- [x] **Step 3: Capturas reales, mobile y desktop, con el sitio servido**

```bash
npm run build && npm run preview &
sleep 3
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for vp, name in [({'width':1440,'height':900}, 'desktop'), ({'width':390,'height':844}, 'mobile')]:
        pg = b.new_page(viewport=vp)
        pg.goto('http://localhost:4173/?theme=hyprland', wait_until='domcontentloaded', timeout=30000)
        pg.wait_for_timeout(3500)
        pg.screenshot(path=f'/tmp/hero-final-{name}.png', full_page=False)
        errors = pg.evaluate('window.__consoleErrors || []')
        print(name, 'console errors:', errors)
        pg.close()
    b.close()
"
kill %1
```

Expected: cero errores de consola, layout correcto en ambos tamaños, animación de entrada visible
en las capturas (el timing exacto depende de cuándo dispara el screenshot dentro de los ~2,1s de
secuencia — no es un fallo si captura un frame intermedio).

- [x] **Step 4: Grep anti-mock**

```bash
grep -rE "mockData|fakeData|hardcoded|TODO.*real|// fake|demo_data|placeholder|lorem ipsum|Lorem" \
  src/sections/hero.ts src/themes/hypr.choreography.ts
```

Expected: sin resultados (el nombre/rol/email vienen de `identity`, dato real).

- [x] **Step 5: Foco de teclado manual**

Con `npm run preview` corriendo, abrir `http://localhost:4173/?theme=hyprland` en un navegador
real, pulsar Tab hasta llegar al enlace de correo. Confirmar visualmente que aparece el filete
(`::after` con `width: 100%`) y el color cambia a `--l1` — no solo el contorno por defecto del
navegador.

- [x] **Step 6: Revisión de Aoshi sobre el sitio real**

Enseñar el hero funcionando en `npm run dev` (no solo capturas) — scroll de entrada, hover del
nombre, tab hasta el correo, y el colapso a mobile con las devtools en modo responsive. Solo tras
esta confirmación se considera la tarea DONE.

- [x] **Step 7: Actualizar el spec a "implementado"**

En `docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md`, cambiar la cabecera:

```markdown
Estado: implementado
```

Y añadir al final del documento una sección `## Registro de implementación` breve (fecha, qué
divergió del plan si algo divergió, números medidos si hubo que remedir contraste).

- [x] **Step 8: Commit final**

```bash
git add docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md
git commit -m "docs(hero): cerrar el rediseno del hero de hyprland con el registro de implementacion"
```

---

## Self-Review

**Cobertura del spec:** las 4 secciones del spec (dispositivo/lomo, entrada fusionada, idle
gateado, `--bx`/`--by`, accesibilidad) están cubiertas por las Tasks 1-5; la verificación completa
de la sección "Verificación" del spec está en la Task 6.

**Placeholders:** ninguno — cada step trae el código completo, no hay "TODO" ni "similar a la
tarea N" sin repetir el contenido.

**Consistencia de nombres:** `.hero-divider`, `.hero-divider-spark`, `.hero-divider-landing`,
`.hero-name-wrap`, `.hero-name-ghost`, `.hero-name-word` se usan con el mismo nombre exacto en
`hero.ts` (Task 1) y en cada selector CSS de las Tasks 2-5 — verificado cruzando cada clase
mencionada en el DOM contra su selector correspondiente.
