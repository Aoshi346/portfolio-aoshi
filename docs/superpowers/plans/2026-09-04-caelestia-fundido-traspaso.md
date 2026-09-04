# Traspaso — Caelestia B5 (Fundido), sesión de maquetado

Copia el bloque de abajo entero como primer mensaje de una sesión con contexto limpio.

**Modelo:** **modelo top**, **esfuerzo alto**. Es diseño, crítica visual y decisiones con Aoshi
delante. Los subagentes (lidia, vera) van con **`model: sonnet` pinado**: heredan el modelo de la
sesión y un fan-out sin pinear factura todo a tarifa top.

**B5 cierra Caelestia.** Es la escena con la peor ocupación de las cinco (78% de la ventana vacía) y
la única con la jerarquía tipográfica invertida por medida, no por opinión.

---

## Prompt

> Vas a **maquetar la fase B5 de Caelestia — la escena «Fundido»**, el contacto, del portfolio de
> Aoshi Blanco Sanz, en `/home/aoshi/proyectos/portfolio-aoshi`. Es la **última** de las seis fases y
> cierra el rediseño del tema. Es trabajo de **diseño**: no toques `src/`.
>
> **Lee primero, en este orden:**
>
> 1. `docs/superpowers/plans/2026-09-04-caelestia-fundido-maquetado.md` — la agenda: el diagnóstico
>    medido, las maquetas M1-M8, los ocho gates, y **«Lo que NO puede ser»**, que son cuatro vetos
>    duros. Léelos antes de proponer nada.
> 2. `docs/superpowers/specs/2026-09-03-caelestia-obra-design.md` — spec de referencia. **Es tu
>    plantilla.**
> 3. `docs/superpowers/specs/2026-08-13-hyprland-contacto-cinta-design.md` y
>    `docs/superpowers/specs/2026-07-30-contacto-carta-de-ajuste-design.md` — **la misma sección en
>    los otros dos temas.** No para copiarlas: **para no repetirlas.** Es la tercera vez que este
>    apartado se resuelve, así que el listón de originalidad es más alto, no más bajo.
> 4. `src/sections/contacto.ts` (51 líneas) — **el DOM lo comparten los tres temas** y la piel la
>    decide el CSS colgado de `[data-theme]`, nunca una rama en el TS. Respeta ese contrato, y lee sus
>    comentarios: hay dos decisiones ya tomadas (el dato se lee sin hover, el `tel:` va sin espacios)
>    que **no se reabren**.
> 5. `CLAUDE.md` y `.claude/CLAUDE.md`. **Aviso: se quedan en B2 y no mencionan B3 ni B4.** El texto
>    verificado de B3 está en `.ai/memory.md`; si vas a corregirlos, hazlo **al principio**, nunca a
>    media sesión (invalida el prompt cache).
>
> ### Las skills, y cuándo
>
> - **`superpowers:brainstorming`** abre el trabajo. Clasifica la tarea en voz alta antes de la
>   primera pregunta (esta es **arquitectónica**) y **no escribas código de producción hasta que Aoshi
>   apruebe un diseño explícito**. Es una puerta dura.
> - **`/frontend-design:frontend-design` en CADA maqueta, sin excepción.** No solo la primera: se
>   invoca antes de escribir cada pantalla. Aoshi lo ha pedido por escrito.
> - **`AskUserQuestion`** cuando la bifurcación sea real; Aoshi responde bien a previsualizaciones
>   ASCII. **Pero** con números sobre la mesa, **recomienda en vez de ofrecer menú**: quiere criterio,
>   no un ranking con descartes.
> - **`superpowers:writing-plans`** solo al final, cuando exista el spec de B5.
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
> el fichero más reciente por fecha de modificación**: numera las pantallas `01-…`, `02-…`. Escribe
> **fragmentos**, no documentos completos: si no empieza por `<!DOCTYPE`, el servidor lo envuelve él.
>
> ### El companion: cómo se hace que se vea bien
>
> **La maqueta lleva la piel real del tema, no una aproximación.** Aoshi rechazó una hecha con barras
> grises y monoespaciada con «no se ve nada bien… que se muestre lo real».
>
> 1. **Los tokens se leen del sitio en marcha, no de la documentación** — la documentación deriva.
>    ```bash
>    export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
>    npm run build && npx vite preview --port <puerto libre> &
>    ```
>    Con Playwright sobre `?theme=caelestia`, lee las `--cae-*` que `caelestia.color.ts` escribe en
>    `document.documentElement.style`.
> 2. **Copia el motor de color entero** —`CLARO`/`OSCURO`, `hueAt`, `chromaScaleAt`, `isDarkAt`— y pon
>    un **deslizador de hora**: la escena hay que verla a las 09:00 y a las 03:00.
> 3. **Las fuentes reales por `@import`**, ejes a mano:
>    `Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1`, `Hanken Grotesk`, `Martian Mono`.
>    **Dos tokens distintos y nunca intercambiables**: `--cae-display-axes-cartel` (`opsz 144`) para lo
>    grande, `--cae-display-axes` (`opsz 9`) para 15-30px. Hallazgo de B1.
> 4. **Contenido literal de `src/data/content.ts`**: los cuatro canales, `identity.invitation`,
>    `identity.availability`. Hay regla anti-mock; en B1 se coló un dato inventado y Aoshi lo cazó.
> 5. **La ventana a tamaño real**: marco de **1412 × 748 exactos**, escalado con `transform: scale(k)`
>    sobre un envoltorio con `overflow: hidden` y `ResizeObserver`. Barra y dock atenuados.
> 6. **GSAP de verdad**: `cp node_modules/gsap/dist/gsap.min.js "$SCREEN_DIR/"` y
>    `<script src="/files/gsap.min.js">`. No transiciones CSS que se le parezcan.
> 7. **Vivo, no capturas**: con **Repetir** y deslizador de **velocidad** (a x0,4 es donde se juzga un
>    gesto).
> 8. **Instrumenta con lecturas numéricas.** En B5, siempre a la vista: **el tamaño del titular frente
>    al de su lead** (hoy 16 contra 20, invertido) y **el ancho muerto al canto derecho medido con
>    `Range`** (hoy 1106px, el 78%).
> 9. **Mira la captura antes de enseñar nada.** Playwright, `--use-gl=swiftshader`, escuchando
>    `pageerror` y `console` de tipo error. Si hay errores, no se enseña.
>
> ### Trampas que ya se pagaron
>
> - **`npm` necesita Node 22**: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`. Con
>   Node 18 `vite build` revienta dentro de rolldown con un error sobre `styleText` que no menciona la
>   versión.
> - **B4 está en implementación en paralelo** (`design/caelestia-creditos-b4`) y tiene sus propios
>   `vite preview` vivos sobre este mismo repo. **No los mates y no midas contra su `dist`**, que
>   lleva Créditos a medias. Mide en un **worktree aislado**
>   (`git worktree add <ruta> HEAD`, nunca `git stash`) y en un puerto libre.
> - **Comprueba siempre quién sirve tu puerto**: `ss -ltnp` y mira de qué directorio cuelga el `node`.
>   El 2026-09-03 había 16 `vite preview` huérfanos de worktrees borrados y **una medida salió verde
>   contra uno de ellos**. Si hay que matar, **por PID**: `pkill -f "vite preview"` **se mata a sí
>   mismo** desde el harness de Bash porque el patrón casa con su propia línea de comando.
> - **Un `<span>` de bloque mide el ancho del contenedor, no el del texto.** Esta trampa **ya falseó
>   el diagnóstico de esta fase**: midiendo cajas daba «0px muertos» sobre una escena con el 78%
>   vacío. Para texto, `document.createRange()` + `selectNodeContents()`.
> - **Contar nodos del DOM no es contar lo que se ve.** Filtra por `getClientRects().length > 0` — así
>   se cazó en B4 que los cuatro rótulos de grupo existían y ninguno se pintaba.
> - **Un `MouseEvent` sintético NO dispara `:hover`.** Trampa de B2, y aquí importa: hay un gate sobre
>   que el dato se lea sin hover.
> - **El selector universal `*` NO alcanza a los pseudo-elementos** en una guardia de
>   `prefers-reduced-motion`.
> - **Guarda cada sustitución de texto con una aserción.** Un `replace` que no encaja no da error:
>   deja el fichero a medias, y así se quedó un shader con la firma vieja y su gate midiendo 0%.
> - **El tema se sortea por visita**: toda URL lleva `?theme=caelestia`.
> - **Verifica contra el build servido, nunca contra `npm run dev`**: el HMR corrompe las medidas.
>
> ### Cómo se cierra la fase
>
> Maquetas aprobadas → spec → revisión → plan con `superpowers:writing-plans` → traspaso con modelo y
> esfuerzo. Y **antes de nada de eso**, rescata al repo lo aprobado que viva en el companion:
> `.superpowers/` está en `.gitignore` (línea 47) y lo que se quede ahí se pierde.
>
> **B5 no está bloqueada por nada**: el dato está completo y no espera material de Aoshi. Al cerrarla
> se cierra Caelestia entera, así que en el spec **deja escrito qué queda pendiente del tema en
> conjunto** — hoy, como mínimo, las nueve capturas reales de Obra.
>
> Empieza por **M1, el diagnóstico**: reproduce las medidas de la agenda —el titular a 16px contra su
> lead a 20, los 1106px muertos medidos con `Range`, la escena sin entrada de coreografía— y enséñale
> a Aoshi el punto de partida antes de proponer nada.
