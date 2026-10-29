# Título con el nombre en el centro: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** La escena Título de Caelestia muestra solo «Aoshi Blanco Sanz» centrado (dibujado con sus contornos reales) y debajo «Desarrollador full stack en Caracas.», sin eslogan, cifras, tarjeta ni terminal.

**Architecture:** `hero.ts` monta un `<h1>` con el nombre en texto visualmente oculto + uno o dos SVG `aria-hidden` con los 15 glifos de `caelestia.firma.ts` (regenerado a `opsz 144`), y un `<p>` con el rol. `caelestia.titulo.ts` construye una sola timeline GSAP (trazo → relleno → corte del rol). El CSS vive en `themes.css` bajo `:root[data-theme="caelestia"]`, con escalones discretos por ancho.

**Tech Stack:** Vite + TypeScript strict + GSAP (recibido por contexto) + CSS; arneses Python + Playwright.

**Spec:** `docs/superpowers/specs/2026-10-29-caelestia-titulo-nombre-design.md` (léelo entero antes de empezar).

## Global Constraints

- Node 22: anteponer `export PATH=$HOME/.nvm/versions/node/v22.22.3/bin:$PATH;` a `npm`. `node_modules` es un symlink al checkout principal: no ejecutar `npm install`.
- Trabajar SOLO en `/home/aoshi/proyectos/portfolio-aoshi-titulo-nombre` (rama `design/titulo-nombre`). Nunca tocar `/home/aoshi/proyectos/portfolio-aoshi`, nunca push ni merge.
- Nada de `any`, nada de `gsap.from` (solo `fromTo`/`to`/`set` con los dos extremos escritos), `gsap` siempre desestructurado del contexto de la coreografía, nada de `console.log`.
- Tipografía en escalones discretos de tokens (`--t-*`), nunca `clamp()` continuo.
- Commits `tipo(scope): descripción` en español, sin emojis, terminando en `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Navegador de los arneses: `executable_path="/usr/bin/google-chrome"`, args `["--no-sandbox", "--use-gl=swiftshader"]`.
- Servidor de prueba: `npm run build && npx vite preview --port 4810 --strictPort` en el worktree (lanzarlo en segundo plano, guardar el PID y matarlo por PID al terminar). Un solo arnés de navegador a la vez.
- Valores fijos del spec: rol `"Desarrollador full stack en Caracas."`; trazo 760 ms `cubic-bezier(.45,0,.25,1)`, escalonado 55 ms de corrido por los 15 glifos; relleno a los 1550 ms, 420 ms `ease-out`; rol a los 2100 ms, `clip-path` de `inset(0 100% 0 0)` a `inset(0 0 0 0)`, 400 ms, `cubic-bezier(.7,0,.2,1)`.
- Escalones: ≥1101 px `--t-9` una línea; 901–1100 `--t-8`; 641–900 `--t-7`; ≤640 dos líneas («Aoshi» / «Blanco Sanz») a `--t-6`. Rol `--t-4` por encima de 900 px y `--t-3` por debajo. Separación nombre/rol 22 px (>640) y 14 px (≤640).

## Review Focus

1. Ventana de 641 px y de 901 px (bordes de escalón): el nombre cabe sin recorte. → aserción de cabida en Task 2 a 641, 768, 901, 1101 y 1440 de ancho, además de 390.
2. Recarga con la entrada a medias / `js-cae-entrada` que no se retira: nombre y rol tienen que acabar visibles. → aserción en Task 3 de que a los 3,5 s la clase no está y relleno = 1.
3. Movimiento reducido: estado final desde el primer pintado, sin trazo visible. → aserción en Task 3.
4. Esquema de noche: el rol cumple AA sobre el fondo real. → aserción de contraste en Task 2, a 13:00 y a 23:00.
5. Lector de pantalla: el `<h1>` se anuncia «Aoshi Blanco Sanz», no 15 trazados. → aserción de nombre accesible en Task 2.

---

### Task 1: Contornos a opsz 144 y el campo del rol

**Files:**
- Modify: `scripts/gen-firma-paths.py` (`EJES` y el docstring)
- Regenerate: `src/themes/caelestia.firma.ts`
- Modify: `src/data/content.ts` (interfaz `Identity` y `identity`)

**Interfaces:**
- Produces: `FIRMA: { ancho: 790.3; glifos: Glifo[] }` con 15 glifos a `opsz 144, wght 900, SOFT 0, WONK 1`; `identity.intro: string` = `"Desarrollador full stack en Caracas."`.

- [ ] **Step 1:** En `gen-firma-paths.py` poner `EJES = {"opsz": 144, "wght": 900, "SOFT": 0, "WONK": 1}` y actualizar el docstring (ya no son los ejes de la firma del antetítulo, sino los del cartel: `--cae-display-axes-cartel`).
- [ ] **Step 2:** Regenerar siguiendo el docstring del script con un venv en `/tmp/claude-0/-home-aoshi-proyectos-portfolio-aoshi/38c302ef-6d92-4d96-a380-fa35ca8f24c7/scratchpad/fenv` (ya existe, con fonttools) y la TTF ya descargada en `.../scratchpad/fuente/fraunces.ttf`: `.../scratchpad/fenv/bin/python -I scripts/gen-firma-paths.py .../scratchpad/fuente/fraunces.ttf`. Esperado: `15 glifos, ancho 790.3`.
- [ ] **Step 3:** En `content.ts` añadir a `Identity` el campo `intro: string` con un comentario de una línea («El rol de la escena Título.») y el valor `intro: "Desarrollador full stack en Caracas."`. `headline` y `subheadline` se quitan en Task 2, junto con su último lector.
- [ ] **Step 4:** `npm run build` y `npm run lint` limpios. Commit: `feat(titulo): contornos del nombre a opsz 144 y el rol de la escena`.

### Task 2: La escena: DOM, maquetación y su arnés

**Files:**
- Modify: `src/sections/hero.ts` (reescritura de `createHero`)
- Modify: `src/data/content.ts` (quitar `headline` y `subheadline` de la interfaz y del objeto)
- Modify: `src/themes/themes.css` (bloque de la escena Título)
- Modify: `scripts/measure-caelestia-titulo.py`

**Interfaces:**
- Consumes: `FIRMA`, `identity.name`, `identity.intro` (Task 1).
- Produces (los usa Task 3): `#hero h1.cae-nombre` que contiene `span.cae-nombre-txt` (texto, visualmente oculto) y `span.cae-nombre-dib[aria-hidden="true"]` con 1 SVG `svg.cae-nombre-svg` por encima de 640 px y 2 por debajo (ver Step 2); cada `<path>` lleva `pathLength="1"`. `p.cae-rol` con `identity.intro`. Exporta desde `hero.ts` `export function ajustarSvgsNombre(hero: HTMLElement): void`, que pone a cada SVG un `viewBox` con la caja real de sus glifos (`getBBox()`, misma `y`/alto para todos) y ancho/alto en `em` (valor/100).

- [ ] **Step 1: Arnés primero.** En `measure-caelestia-titulo.py`:
  - Añadir `executable_path="/usr/bin/google-chrome"` al `launch`.
  - Borrar las familias `titular`, `firma_y_cifras`, `widget`, `tarjeta_orden`, `tarjeta_superficie`, `tarjeta_figura`, `tarjeta_contraste`, `tarjeta_portatil`, `tarjeta_figura_visible` y `literal_now`.
  - En `optica`, medir `#hero .cae-nombre` en lugar de `.cae-tit .cae-ln`: su `font-variation-settings` es el token `--cae-display-axes-cartel`.
  - Escribir la familia `nombre(pg, base)`, que con movimiento reducido (`page.emulate_media(reduced_motion="reduce")`), a 13:00 y 23:00, comprueba:
    - `#hero h1` existe, es el único `h1` de `#hero` y su nombre accesible (`pg.get_by_role("heading", level=1)` dentro de `#hero`) es `"Aoshi Blanco Sanz"`.
    - `span.cae-nombre-dib` tiene `aria-hidden="true"` y hay 15 `path` en total.
    - `p.cae-rol` tiene el texto literal de `identity.intro`, leído de `content.ts` con el mismo patrón que tenía `literal_now`.
    - Los centros horizontales del dibujo del nombre y del rol coinciden con el de `#hero` (tolerancia 2 px) y el bloque nombre+rol está centrado en vertical (tolerancia 4 px).
    - A anchos 390, 641, 768, 901, 1101 y 1440 (alto 900, 844 en 390), la caja de cada SVG queda dentro de la de `#hero`, medida con `getBoundingClientRect()` sobre los SVG, no con `scrollWidth`. A 390 y 641 hay 2 SVG; a 768, 901, 1101 y 1440, 1.
    - El rol cumple 4.5:1 sobre el fondo real: reutilizar `_parse_rgb`, `_luminancia` y `_ratio` del propio fichero, muestreando la captura bajo la caja del rol como hacía `tarjeta_contraste`.
    - Llamarla desde `main()` en lugar de las familias borradas.
- [ ] **Step 2: Verlo rojo.** Build + preview, correr solo `optica` y `nombre` (comentar temporalmente las demás llamadas en `main()`, o una bandera `--solo nombre,optica` si es menos invasivo). Esperado: FALLO en todas las aserciones de `nombre` y en `optica`.
- [ ] **Step 3: DOM.** Reescribir `createHero()` en `hero.ts`. La sección conserva sus clases y `data-scene="hero"`; por hijos, un contenedor `div.cae-presenta` con el `h1` y el `p` descritos en Interfaces. El SVG se genera como hoy con `elFromMarkup` a partir de `FIRMA.glifos`. Los dos SVG de móvil y el de una línea van en el DOM a la vez: `span.cae-linea` × 2, con `FIRMA.glifos.slice(0, 5)` y `slice(5)`, más `span.cae-linea-una` con los 15. El CSS enseña unos u otros según el ancho. Cada `path` lleva `style="--i:N"` con N de 0 a 14 de corrido. Fuera todo lo demás que construye hoy (titular, kicker, statcol, widget, bloque móvil, terminal, `cae-trazo-stage`) y los imports que queden sin uso. Quitar `headline` y `subheadline` de `content.ts`.
- [ ] **Step 4: CSS.**
  - En `themes.css`, sustituir las reglas de la escena Título que pintan piezas retiradas y escribir las nuevas:
    - `.cae-presenta`: flex en columna, centrado en los dos ejes, `text-align: center`, alto completo de la ventana.
    - `.cae-nombre`: Fraunces, `font-variation-settings: var(--cae-display-axes-cartel)`, `line-height: 1`, `color: var(--color-paper)`, `font-size` con los escalones de Global Constraints.
    - `.cae-nombre-txt`: visualmente oculto (`position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap`).
    - `.cae-nombre-svg path`: `fill: currentColor; stroke: currentColor; stroke-width: 1.1`.
    - `.cae-rol`: Hanken Grotesk 400, el color secundario que hoy usa `.cae-meta`, con sus escalones.
  - En la regla de `.js-cae-entrada`, dejar ocultos solo `.cae-nombre-dib` y `.cae-rol`.
  - Llamar `ajustarSvgsNombre` al final de `createHero`, dentro de un `requestAnimationFrame`: `getBBox` necesita el SVG en el documento. Si la sección aún no está montada, que la llame la coreografía en Task 3.
- [ ] **Step 5: Verlo verde.** Build + preview, correr `optica`, `nombre`, `escritorio_desnudo`, `fondo` y `roce`. Esperado: 0 fallos en `optica` y `nombre`. `roce` puede fallar (todavía apunta a `.cae-widget`), y lo arregla Task 3; anotarlo. `npm run lint` limpio.
- [ ] **Step 6: Commit.** `feat(titulo): el nombre en el centro y el rol debajo`.

### Task 3: La entrada de trazo

**Files:**
- Modify: `src/themes/caelestia.titulo.ts`
- Modify: `src/themes/caelestia.choreography.ts` (las llamadas de la escena Título)
- Modify: `src/main.ts` (solo el comentario de `js-cae-entrada`)
- Modify: `scripts/measure-caelestia-titulo.py` (familias `entrada` y `roce`)

**Interfaces:**
- Consumes: el DOM de Task 2 (`.cae-nombre-dib path`, `.cae-rol`) y `ajustarSvgsNombre`.
- Produces: `export function montarEntrada(gsap: Gsap, root: HTMLElement): EntradaHandle` (sin el tercer parámetro `figura`). `montarRoce(gsap, root)` se queda con el selector `".cae-ws, .cae-dock-item"`.

- [ ] **Step 1: Arnés primero.** Reescribir la familia `entrada`:
  - **Movimiento normal:** al cargar, antes de 300 ms, los `path` visibles tienen `fill-opacity` < 0.1. A los 3.500 ms no queda `js-cae-entrada` en `<html>`, los 15 `path` tienen `fill-opacity` 1 y `stroke-opacity` 0, y el `clip-path` de `.cae-rol` es `inset(0px)` o `none`. Se mide con `getComputedStyle`, con margen explícito y no contra el cronómetro.
  - **Movimiento reducido:** a los 300 ms el estado ya es el final.
  - **Los tiempos declarados**, leyendo la timeline: exponer `window.__CAE_ENTRADA__ = { duracion: tl.duration() }`, igual que el patrón del proyecto `__CONTENT_SHAPE__`. La duración es 2,5 s ± 0,05 (fin del corte del rol).
  - **`roce`:** pasar el puntero por `.cae-dock-item` en lugar de `.cae-widget`.
  - Verlo rojo con el build de Task 2.
- [ ] **Step 2: Entrada.** En `caelestia.titulo.ts`:
  - Borrar `justificarTitular`, `montarTitulo`, `TituloHandle`, `montarFiguraViva`, `FiguraVivaHandle`, `FIGURA_NULA` y los pasos de terminal, aterrizaje, regla/meta, barrido del titular, volteo de cifras y tarjeta.
  - Reescribir `montarEntrada`. Primero los estados iniciales con `gsap.set`: `strokeDashoffset: 1`, `fillOpacity: 0` y `strokeOpacity: 1` en los path, y `clipPath: "inset(0 100% 0 0)"` en el rol. Después retirar `js-cae-entrada` y construir la timeline con `fromTo`/`to` y los valores de Global Constraints.
  - Con movimiento reducido, `gsap.set` al estado final, retirar la clase y salir.
  - Mantener los tres caminos de salida que retiran la clase, como documenta el docstring actual, y reescribir ese docstring para la entrada nueva.
- [ ] **Step 3: Coreografía.** En `caelestia.choreography.ts`, quitar `montarTitulo(root)` y `montarFiguraViva`, llamar `ajustarSvgsNombre(hero)` antes de `montarEntrada(gsap, root)` y ajustar los comentarios. En `main.ts`, reescribir el comentario de `js-cae-entrada`: ahora oculta el nombre y el rol.
- [ ] **Step 4: Verlo verde.** Build + preview, correr el arnés completo. Esperado: `0 fallo(s)` y consola sin errores. `npm run lint` limpio.
- [ ] **Step 5: Commit.** `feat(titulo): la entrada dibuja el nombre en su sitio`.

### Task 4: Poda, gates y capturas (la hace el lead, no un subagente)

- [ ] Pasar `clases-muertas.mjs` y la búsqueda de `@keyframes` huérfanos sobre `themes.css` y `style.css`. Build y commit: `refactor(css): fuera las reglas del Titulo retirado`.
- [ ] Revisar a mano `.cae-*` del Título que pudieran seguir vivas por un literal suelto.
- [ ] `scripts/verify.py --url <preview>`: rc=0 contra su línea base.
- [ ] Gate de capturas `snap.py`, con línea base del `main` actual. Las capturas `*-quien-es`, `*-obra`, `*-creditos` y `*-contacto` tienen que salir idénticas. Las `*-hero` cambian a propósito y se miran a mano.
- [ ] Capturas reales de escritorio y móvil, de día y de noche, mirándolas.
- [ ] `lidia-naive-tester` y `vera-art-director` en Sonnet, avisados de que no editen nada.
- [ ] Copiar la maqueta aprobada y su generador a `docs/superpowers/maquetas/`, y anotar el cierre en `docs/estado-de-los-temas.md` (bloque de la fase B1).
