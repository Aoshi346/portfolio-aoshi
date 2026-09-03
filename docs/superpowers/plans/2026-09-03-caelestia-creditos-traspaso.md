# Traspaso — Caelestia B4 (Créditos), sesión de maquetado

Copia el bloque de abajo entero como primer mensaje de una sesión con contexto limpio.

**Modelo:** **modelo top**, **esfuerzo alto**. Es diseño, crítica visual y decisiones con Aoshi
delante. Los subagentes (lidia, vera) van con **`model: sonnet` pinado**: heredan el modelo de la
sesión y un fan-out sin pinear factura todo a tarifa top.

**B4 es la fase más sana de las cinco.** No está rota como Obra: se ve entera, sin errores, y el
cruce "Aparece en" funciona. Lo que falla es composición y jerarquía. **Dimensiona el trabajo a eso
y no reescribas lo que ya sirve.**

---

## Prompt

> Vas a **maquetar la fase B4 de Caelestia — la escena «Créditos»** del portfolio de Aoshi Blanco
> Sanz, en `/home/aoshi/proyectos/portfolio-aoshi`. Es trabajo de **diseño**: no toques `src/`.
>
> **Lee primero, en este orden:**
>
> 1. `docs/superpowers/plans/2026-09-03-caelestia-creditos-maquetado.md` — la agenda: el diagnóstico
>    medido, las maquetas M1-M8, los ocho gates, y **«Lo que NO puede ser»**, que son tres vetos
>    duros. Léelos antes de proponer nada.
> 2. `docs/superpowers/specs/2026-09-03-caelestia-obra-design.md` — el spec de la fase anterior.
>    **Es tu plantilla.**
> 3. `docs/superpowers/specs/2026-08-10-hyprland-stack-catastro-design.md` — **la misma sección en el
>    otro tema**, «el catastro». No para copiarla: **para no repetirla.** Vive en la rama
>    `worktree-hyprland-stack-catastro`, sin fusionar a `main`; si no está en tu árbol,
>    `git show worktree-hyprland-stack-catastro:docs/superpowers/specs/2026-08-10-hyprland-stack-catastro-design.md`.
> 4. `src/components/credits.ts` (619 líneas) — **el DOM lo comparten los tres temas** y la
>    presentación la decide el CSS colgado de `[data-theme]`, nunca una rama en el TS. Respeta ese
>    contrato.
> 5. `CLAUDE.md` y `.claude/CLAUDE.md`. **Aviso: los dos se quedan en B2 y no mencionan B3, que ya
>    está fusionada.** El texto verificado para corregirlos está en `.ai/memory.md`; si vas a
>    hacerlo, hazlo **ahora, al principio**, nunca a media sesión (invalida el prompt cache).
>
> ### Las skills, y cuándo
>
> - **`superpowers:brainstorming`** abre el trabajo. Clasifica la tarea en voz alta antes de la
>   primera pregunta (esta es **arquitectónica**) y **no escribas código de producción hasta que
>   Aoshi apruebe un diseño explícito**. Es una puerta dura.
> - **`/frontend-design:frontend-design` en CADA maqueta, sin excepción.** No es solo para la
>   primera: se invoca antes de escribir cada pantalla. Aoshi lo ha pedido por escrito.
> - **`AskUserQuestion`** cuando la bifurcación sea real. Aoshi responde bien a previsualizaciones
>   ASCII. **Pero** cuando ya haya números sobre la mesa, **recomienda en vez de ofrecer menú**:
>   quiere tu criterio, no un ranking con descartes.
> - **`superpowers:writing-plans`** solo al final, cuando ya exista el spec de B4.
> - **Nunca artifacts.** Toda propuesta va al companion.
>
> ### El companion: cómo se levanta
>
> ```bash
> /root/.claude/plugins/cache/claude-plugins-official/superpowers/6.3.0/skills/brainstorming/scripts/start-server.sh \
>   --project-dir /home/aoshi/proyectos/portfolio-aoshi
> ```
>
> Devuelve JSON con `url` (lleva `?key=…`, **dale siempre la URL completa**) y `screen_dir`. **Sirve
> el fichero más reciente por fecha de modificación**, así que numera las pantallas: `01-…`, `02-…`.
> Escribe **fragmentos**, no documentos completos: si el fichero no empieza por `<!DOCTYPE`, el
> servidor lo envuelve él.
>
> ### El companion: cómo se hace que se vea bien
>
> Esto es lo que más ha costado en las fases anteriores. **La maqueta lleva la piel real del tema, no
> una aproximación.** Aoshi rechazó una hecha con barras grises y monoespaciada con «no se ve nada
> bien… que se muestre lo real».
>
> 1. **Los tokens se leen del sitio en marcha, no de la documentación** — la documentación deriva.
>    ```bash
>    export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
>    npm run build && npx vite preview --port 4173 &
>    ```
>    Con Playwright sobre `http://localhost:4173/?theme=caelestia`, lee las `--cae-*` que
>    `caelestia.color.ts` escribe en `document.documentElement.style`.
> 2. **Copia el motor de color entero** —`CLARO`/`OSCURO`, `hueAt`, `chromaScaleAt`, `isDarkAt`— y pon
>    un **deslizador de hora**. En B4 no es opcional: los 23 iconos de marca traen color propio ajeno
>    a la rueda OkLCH y solo se juzgan viéndolos a las 09:00 y a las 03:00.
> 3. **Las fuentes reales por `@import`**, con los ejes a mano:
>    `Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1`, `Hanken Grotesk`, `Martian Mono`.
>    `"opsz" 144` para lo grande, `"opsz" 9` para 15-30px — hallazgo de B1, dos tokens distintos.
> 4. **El contenido real y literal de `src/data/content.ts`**: los 23 nombres, sus `detail`, los
>    cuatro rótulos de grupo. Hay regla anti-mock. En B1 se coló un dato inventado y Aoshi lo cazó.
>    **El recuento por grupo es derivado (`items.length`), no un campo nuevo.**
> 5. **La ventana a tamaño real**: marco de **1412 × 748 exactos**, escalado con `transform: scale(k)`
>    sobre un envoltorio con `overflow: hidden` y `ResizeObserver`. Barra y dock atenuados.
> 6. **GSAP de verdad**: `cp node_modules/gsap/dist/gsap.min.js "$SCREEN_DIR/"` y
>    `<script src="/files/gsap.min.js">`. No transiciones CSS que se le parezcan.
> 7. **Vivo, no capturas.** La selección de tecnología es el gesto central: móntalo para que Aoshi lo
>    pruebe con el ratón, con **Repetir** y deslizador de **velocidad** (bajar a x0,4 es lo que
>    permite juzgar un gesto).
> 8. **Instrumenta con lecturas numéricas.** En B4 las que tienen que estar siempre a la vista son
>    **el ancho muerto al canto derecho** (hoy 424px, el 30%) y **si el contenedor tiene scroll**
>    (`scrollHeight === clientHeight`; hoy 758 vs 748).
> 9. **Mira la captura antes de enseñar nada.** Playwright, `--use-gl=swiftshader`, escuchando
>    `pageerror` y `console` de tipo error. Si hay errores, no se enseña.
>
> ### Trampas que ya se pagaron
>
> - **`npm` necesita Node 22**: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`. Con
>   Node 18 `vite build` revienta dentro de rolldown con un error sobre `styleText` que no menciona
>   la versión.
> - **El tema se sortea por visita**: toda URL lleva `?theme=caelestia`.
> - **Verifica contra el build servido, nunca contra `npm run dev`.** El HMR corrompe las medidas.
> - **Comprueba que el puerto que usas no lo sirve un fantasma.** El 2026-09-03 había **16 procesos
>   `vite preview` huérfanos** sirviendo el `dist` de dos worktrees ya borrados, y **una medida salió
>   verde contra uno de ellos**. Antes de medir: `ss -ltnp` y mira de qué directorio cuelga el `node`.
>   Mátalos **por PID**: `pkill -f "vite preview"` **se mata a sí mismo** desde el harness de Bash,
>   porque el patrón casa con su propia línea de comando.
> - **Contar nodos del DOM no es contar lo que se ve.** El fallo central de esta fase es justo ese: 4
>   rótulos de grupo en el DOM, **0 pintados**. Filtra siempre por `getClientRects().length > 0`. El
>   mismo error tenía el gate `hay exactamente un h1` de `verify.py`, corregido el 2026-09-03.
> - **Un `<span>` de bloque mide el ancho del contenedor, no el del texto.** Para medir texto,
>   `document.createRange()` + `selectNodeContents()`.
> - **El selector universal `*` NO alcanza a los pseudo-elementos**: una guardia de
>   `prefers-reduced-motion` con `*` dejó animando un `::before` en B2.
> - **Guarda cada sustitución de texto con una aserción.** Un `replace` que no encaja no da error:
>   deja el fichero a medias, y así se quedó un shader con la firma vieja y el gate midiendo 0%.
> - **Al clonar una pantalla para variarla**, si renombras el prefijo de clases con `sed`, renombra
>   también `getElementById` y el `class` del `<div>` raíz. En B1 salió en blanco dos veces por eso.
>
> ### Cómo se cierra la fase
>
> Maquetas aprobadas → spec → revisión → plan con `superpowers:writing-plans` → traspaso con modelo y
> esfuerzo. Y **antes de nada de eso**, rescata al repo lo aprobado que viva en el companion:
> `.superpowers/` está en `.gitignore` (línea 47) y lo que se quede ahí se pierde.
>
> **B4 no está bloqueada por nada** — a diferencia de B3, no espera capturas de Aoshi. Si algo la
> bloquea, es hallazgo tuyo y va escrito en el spec.
>
> Empieza por **M1, el diagnóstico**: reproduce las medidas de la agenda sobre el build de producción
> —los 424px muertos, los cuatro rótulos que existen y no se pintan, los 10px de scroll interno— y
> enséñale a Aoshi el punto de partida antes de proponer nada.
