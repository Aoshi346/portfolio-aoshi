# Traspaso — Caelestia B3 (Obra), sesión de maquetado

Copia el bloque de abajo entero como primer mensaje de una sesión con contexto limpio.

**Modelo:** **modelo top**. Esto es diseño, crítica visual y decisiones con Aoshi delante — no es
ejecución mecánica. La norma de `/home/aoshi/proyectos/CLAUDE.md` manda arquitectura y decisiones de
diseño al modelo top; el maquetado entra ahí. **Esfuerzo alto.**
Los subagentes que se lancen (lidia, vera) van con **`model: sonnet` pinado**: heredan el modelo de
la sesión y un fan-out sin pinear factura todo a tarifa top.

**B3 es la fase con el problema estructural más grande de las cinco** — hoy cuatro de los cinco
proyectos no existen en la ventana y el carril tiene un scroll interno de 6,6 pantallas. No es
acabado: es composición.

---

## Prompt

> Vas a **maquetar la fase B3 de Caelestia — la escena «Obra»** del portfolio de Aoshi Blanco Sanz,
> en `/home/aoshi/proyectos/portfolio-aoshi`. Es trabajo de **diseño**: no toques `src/`.
>
> **Lee primero, en este orden:**
>
> 1. `docs/superpowers/plans/2026-09-02-caelestia-obra-maquetado.md` — la agenda: el diagnóstico
>    medido, qué maquetas hay que construir (M1–M8), contra qué se miden, y qué está ya decidido y
>    no se reabre. Incluye **lo que NO puede ser**: léelo antes de proponer nada.
> 2. `docs/superpowers/specs/2026-09-02-caelestia-quien-soy-design.md` — el spec de la fase
>    anterior. **Es tu plantilla.** Vive en el worktree
>    `/home/aoshi/proyectos/portfolio-aoshi-b2` mientras B2 no se fusione; si ya está fusionada,
>    está en `docs/superpowers/specs/` sin más.
> 3. `docs/superpowers/specs/2026-08-10-hyprland-obra-cartel-design.md` — **la misma sección en el
>    otro tema.** No para copiarla: para no repetirla. Su gesto (la captura viaja con GSAP Flip
>    hasta un visor grande) queda vetado en Caelestia.
> 4. `CLAUDE.md` y `.claude/CLAUDE.md`.
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
> - **`superpowers:writing-plans`** solo al final, cuando ya exista el spec de B3.
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
>    `--cae-*` que `caelestia.color.ts` escribe en `document.documentElement.style`: `--cae-surface`,
>    `--cae-on-surface`, `--cae-outline`, `--cae-primary`, `--cae-anchor`, `--cae-wall-1/2/3`,
>    `--cae-hue`.
>
> 2. **Mejor aún: copia el motor de color entero** dentro de la maqueta —`CLARO`/`OSCURO`, `hueAt`,
>    `chromaScaleAt`, `isDarkAt`— y pon un **deslizador de hora**. En B3 no es opcional: la escena
>    lleva imágenes de colores ajenos, y **solo se puede juzgar viéndola a las 09:00 y a las 03:00**.
>
> 3. **Las fuentes reales, por `@import`**, con los ejes escritos a mano:
>    `Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1`, `Hanken Grotesk`, `Martian Mono`.
>    `"opsz" 144` para lo grande, `"opsz" 9` para 15–30 px — esa distinción es un hallazgo de B1.
>
> 4. **El contenido real de `src/data/content.ts`, literal.** Hay regla anti-mock en el repo. En B1
>    se coló «Repositorios públicos · 2», que no existe en ninguna parte, y Aoshi lo cazó. Aquí el
>    riesgo equivalente es inventarle a un proyecto un `period` que no tiene o pintar `tooling`.
>
> 5. **La ventana a tamaño real.** Dibuja el marco a **1412 × 748 exactos** y escálalo con
>    `transform: scale(k)` sobre un envoltorio con `overflow: hidden`, calculando `k` con un
>    `ResizeObserver`. Incluye la barra y el dock atenuados: **en B3 el dock importa**, porque hoy
>    se come 139 px del único proyecto visible.
>
> 6. **GSAP de verdad**, no transiciones CSS que se le parezcan:
>    `cp node_modules/gsap/dist/gsap.min.js "$SCREEN_DIR/"` y `<script src="/files/gsap.min.js">`.
>
> 7. **Las capturas: caja neutra, nunca los `.webp` actuales.** Los nueve ficheros de
>    `public/media/obra/` son marcadores «CAPTURA PENDIENTE» de 1600 × 1000 pintados con la paleta de
>    **Vice** (morado y ámbar). Metidos en una maqueta de Caelestia envenenan cualquier juicio de
>    color. Dibuja el hueco con la relación **16:10** y una retícula de marcador propia, en tokens de
>    Caelestia. Si en algún momento hacen falta imágenes de verdad: el servidor del companion **no
>    sirve assets hermanos** (`media/x.webp` da 404) — referéncialas contra el preview
>    (`http://localhost:4173/media/…`) dejándolo corriendo, o embébelas en base64. Lo que copies al
>    `screen_dir` sí se sirve, bajo `/files/`.
>
> 8. **Vivo, no capturas.** La selección entre proyectos es el gesto central de esta escena: monta la
>    demo para que Aoshi la pruebe con el ratón, con botón de **Repetir** y deslizador de
>    **velocidad** — bajar a ×0,4 es lo que permite juzgar un gesto.
>
> 9. **Instrumenta la maqueta con lecturas numéricas.** No es adorno: en B1 la medida bajo la ventana
>    cazó que el bloque se comía el dock por 138 px y que la justificación **no era justificación**.
>    En B3 el número que tiene que estar siempre a la vista es **el alto sobrante de la ventana** y
>    **si el contenedor tiene scroll** (`scrollHeight === clientHeight`).
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
> - **B2 está viva en otro worktree** (`/home/aoshi/proyectos/portfolio-aoshi-b2`, rama
>   `design/caelestia-quien-soy`). Si levantas un preview, **usa un puerto que no sea el 4173** o
>   comprueba antes que está libre: dos sesiones midiendo contra el mismo servidor se corrompen las
>   medidas mutuamente, y eso ya produjo un P0 falso en este proyecto.
> - **Al clonar una pantalla para variarla**, si renombras el prefijo de clases con `sed`, renombra
>   también `getElementById` y el atributo `class` del `<div>` raíz. En B1 se quedaron a medias dos
>   veces y la pantalla salía en blanco o sin estilo.
> - **Guarda cada sustitución de texto con una aserción.** Un `replace` que no encaja no da error:
>   deja el fichero a medias. En B1 dejó un shader con la firma vieja, el lienzo negro, y el gate
>   del movimiento marcando 0 % — que era justo el síntoma que se estaba midiendo.
> - **Un `<span>` de bloque mide el ancho del contenedor, no el del texto.** Para medir texto,
>   `document.createRange()` + `selectNodeContents()`.
> - **Los barridos largos van por trozos con `requestAnimationFrame`.** 96 `readPixels` seguidos
>   congelan la pestaña varios segundos y el botón se queda pulsado.
> - **`projectScene.ts` lo comparten los tres temas.** Cualquier cambio que propongas ahí hay que
>   verificarlo en Vice —que está **cerrado**— y en Hyprland. Si crees que hay que tocarlo, dilo
>   explícitamente en el spec en vez de darlo por hecho.
>
> ### Cómo se cierra la fase
>
> Cuando Aoshi apruebe las maquetas: spec → revisión → plan con `superpowers:writing-plans` →
> traspaso con modelo y esfuerzo. Y **antes de nada de eso**, rescata al repo cualquier artefacto
> aprobado que viva en el companion: `.superpowers/` está en `.gitignore` (línea 47) y lo que se
> quede ahí se pierde.
>
> **Deja escrito en el spec, en su sitio, que la implementación de B3 está bloqueada hasta que
> existan las nueve capturas reales de `public/media/obra/`.** No es deuda de diseño: es un encargo
> a Aoshi, y el gate visual de la fase no se da por bueno con marcadores.
>
> Empieza por **M1, el diagnóstico**: reproduce las medidas de la agenda sobre el build de
> producción —los 4964 px en una ventana de 748, el scroll interno, los 139 px que se come el dock,
> los cuatro proyectos inalcanzables— y enséñale a Aoshi el punto de partida antes de proponer nada.
