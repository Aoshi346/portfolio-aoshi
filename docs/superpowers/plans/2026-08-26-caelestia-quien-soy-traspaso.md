# Traspaso — Caelestia B2 (Quién soy), sesión de maquetado

Copia el bloque de abajo entero como primer mensaje de una sesión con contexto limpio.

**Modelo:** **modelo top**. Esto es diseño, crítica visual y decisiones con Aoshi delante — no es
ejecución mecánica. La norma de `/home/aoshi/proyectos/CLAUDE.md` manda arquitectura y decisiones de
diseño al modelo top; el maquetado entra ahí. **Esfuerzo alto.**
Los subagentes que se lancen (lidia, vera) van con **`model: sonnet` pinado**: heredan el modelo de
la sesión y un fan-out sin pinear factura todo a tarifa top.

---

## Prompt

> Vas a **maquetar la fase B2 de Caelestia — la escena «Quién soy»** del portfolio de Aoshi Blanco
> Sanz, en `/home/aoshi/proyectos/portfolio-aoshi`. Es trabajo de **diseño**: no toques `src/`.
>
> **Lee primero, en este orden:**
>
> 1. `docs/superpowers/plans/2026-08-26-caelestia-quien-soy-maquetado.md` — la agenda: qué maquetas
>    hay que construir (M1–M7), contra qué se miden y qué está ya decidido y no se reabre.
> 2. `docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md` — el spec de la fase anterior.
>    **Es tu plantilla**: la mitad de sus secciones son idénticas en B2, y su
>    `## Los gates` te dice qué disciplina se espera.
> 3. `CLAUDE.md` y `.claude/CLAUDE.md`.
>
> ### Las skills, y cuándo
>
> - **`superpowers:brainstorming`** abre el trabajo. Clasifica la tarea en voz alta antes de la
>   primera pregunta (esta es **arquitectónica**) y **no escribas código de producción hasta que
>   Aoshi apruebe un diseño explícito**. Es una puerta dura.
> - **`/frontend-design:frontend-design` en CADA maqueta, sin excepción.** No es opcional ni es para
>   la primera nada más: se invoca antes de escribir cada pantalla. Aoshi lo ha pedido por escrito.
> - **`AskUserQuestion`** cuando la bifurcación sea real y cambie lo que construyes. Aoshi responde
>   bien a preguntas con previsualización ASCII. **Pero**: cuando ya haya números sobre la mesa,
>   **recomienda en vez de ofrecer menú** — quiere tu criterio, no un ranking.
> - **`superpowers:writing-plans`** solo al final, cuando ya exista el spec de B2.
> - **Nunca artifacts.** Toda propuesta va al companion.
>
> ### El companion: cómo se levanta
>
> ```bash
> /root/.claude/plugins/cache/claude-plugins-official/superpowers/6.3.0/skills/brainstorming/scripts/start-server.sh \
>   --project-dir /home/aoshi/proyectos/portfolio-aoshi
> ```
>
> Devuelve JSON con `url` (lleva `?key=…`, **dale siempre la URL completa**) y `screen_dir`. Con
> `--project-dir` reutiliza el puerto entre reinicios. **El servidor sirve el fichero más reciente
> por fecha de modificación**, así que numera las pantallas: `01-…`, `02-…`.
>
> Escribe **fragmentos**, no documentos completos: si el fichero no empieza por `<!DOCTYPE`, el
> servidor lo envuelve él y le pone la cabecera y el andamiaje.
>
> ### El companion: cómo se hace que se vea bien
>
> Esto es lo que más ha costado en las fases anteriores. **La maqueta tiene que llevar la piel real
> del tema, no una aproximación.** Aoshi rechazó una maqueta hecha con barras grises y monoespaciada
> con «no se ve nada bien… que se muestre lo real».
>
> 1. **Los tokens se leen del sitio en marcha, no de la documentación** — la documentación deriva.
>
>    ```bash
>    export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
>    npm run build && npx vite preview --port 4173 &
>    ```
>
>    Luego, con Playwright sobre `http://localhost:4173/?theme=caelestia`, lee las propiedades
>    `--cae-*` que `caelestia.color.ts` escribe en `document.documentElement.style`. Son los valores
>    de la hora en que corras: `--cae-surface`, `--cae-on-surface`, `--cae-outline`, `--cae-primary`,
>    `--cae-anchor`, `--cae-wall-1/2/3`, `--cae-hue`.
>
> 2. **Mejor aún: copia el motor de color entero** dentro de la maqueta —las tablas `CLARO`/`OSCURO`,
>    `hueAt`, `chromaScaleAt`, `isDarkAt`— y pon un **deslizador de hora**. Así Aoshi ve la propuesta
>    a las 09:00, a las 19:55 y a las 03:00, que es la única forma de juzgar un tema gobernado por el
>    reloj. Se hizo así en B1 y fue lo que más ayudó.
>
> 3. **Las fuentes reales, por `@import`**, con los ejes escritos a mano:
>    `Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1`, `Hanken Grotesk`, `Martian Mono`.
>    Display con `font-variation-settings: "opsz" 9, "wght" 900, "SOFT" 0, "WONK" 1` para textos de
>    15–30 px y **`"opsz" 144` para lo grande** — esa distinción es un hallazgo de B1.
>
> 4. **El contenido real de `src/data/content.ts`, literal.** Hay regla anti-mock en el repo. En B1
>    se coló «Repositorios públicos · 2», que no existe en ninguna parte, y Aoshi lo cazó.
>
> 5. **La ventana a tamaño real.** Dibuja el marco a **1412 × 748 exactos** y escálalo con
>    `transform: scale(k)` sobre un envoltorio con `overflow: hidden`, calculando `k` con un
>    `ResizeObserver`. Así las proporciones son verdad y no una aproximación. Incluye la barra y el
>    dock atenuados, para que se vea que el shell ya está montado.
>
> 6. **GSAP de verdad**, no transiciones CSS que se le parezcan:
>    `cp node_modules/gsap/dist/gsap.min.js "$SCREEN_DIR/"` y `<script src="/files/gsap.min.js">`.
>
> 7. **El servidor no sirve assets hermanos.** `media/x.webp` da 404. Para imágenes reales,
>    referéncialas contra el preview (`http://localhost:4173/media/…`) y deja el preview corriendo, o
>    embébelas en base64. Los ficheros que copies al `screen_dir` sí se sirven, bajo `/files/`.
>
> 8. **Vivo, no capturas.** Si la propuesta tiene estados, hover o animación, monta la demo para que
>    la pruebe con el ratón, con botón de **Repetir** y deslizador de **velocidad** — bajar a ×0,4 es
>    lo que permite juzgar un gesto.
>
> 9. **Instrumenta la maqueta con lecturas numéricas.** No es adorno: en B1 la medida bajo la ventana
>    cazó que el bloque se comía el dock por 138 px, que la justificación **no era justificación**, y
>    que un shader no compilaba. Pon el número donde Aoshi pueda verlo.
>
> 10. **Mira la captura antes de enseñar nada.** Playwright, `--use-gl=swiftshader` si hay WebGL,
>     escuchando `pageerror` y `console` de tipo error. Si hay errores, no se enseña.
>
> ### Trampas que ya se pagaron, para que no las repitas
>
> - **`npm` necesita Node 22.** `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`. Con
>   Node 18, `vite build` revienta dentro de rolldown con un error sobre `styleText` que no dice
>   nada de la versión.
> - **El tema se sortea por visita**: toda URL lleva `?theme=caelestia`.
> - **Verifica contra el build servido, nunca contra `npm run dev`.** El HMR corrompe las medidas.
> - **Al clonar una pantalla para variarla**, si renombras el prefijo de clases con `sed`, renombra
>   también `getElementById` y el atributo `class` del `<div>` raíz. En B1 se quedaron a medias dos
>   veces y la pantalla salía en blanco o sin estilo.
> - **Guarda cada sustitución de texto con una aserción.** Un `replace` que no encaja no da error:
>   deja el fichero a medias. En B1 dejó un shader con la firma vieja, el lienzo negro, y el gate
>   del movimiento marcando 0 % — que era justo el síntoma que se estaba midiendo.
> - **Con `preserveDrawingBuffer: true`** en el contexto WebGL si vas a leer píxeles, y comprueba
>   `getShaderParameter(fs, COMPILE_STATUS)`: un shader roto falla en silencio.
> - **Un `<span>` de bloque mide el ancho del contenedor, no el del texto.** Para medir texto,
>   `document.createRange()` + `selectNodeContents()`.
> - **Los barridos largos van por trozos con `requestAnimationFrame`.** 96 `readPixels` seguidos
>   congelan la pestaña varios segundos y el botón se queda pulsado.
>
> ### Cómo se cierra la fase
>
> Cuando Aoshi apruebe las maquetas: spec → revisión → plan con `superpowers:writing-plans` →
> traspaso con modelo y esfuerzo. Y **antes de nada de eso**, rescata al repo cualquier artefacto
> aprobado que viva en el companion: `.superpowers/` está en `.gitignore` (línea 47) y lo que se
> quede ahí se pierde. Hay precedente en `docs/superpowers/specs/`:
> `2026-08-26-caelestia-titulo-prototipo.glsl` y `2026-08-26-caelestia-firma-paths.json`.
>
> Empieza por **M1, el diagnóstico**: captura la escena `#about` en la ventana de 1412 × 748 sobre el
> build de producción, mide su alto real y el aire que le sobra, y enséñale a Aoshi el punto de
> partida antes de proponer nada.
