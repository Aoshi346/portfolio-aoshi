# Prompt — rediseñar "Quién soy" (Hyprland)

Pegar en una sesión nueva. Está escrito para repetir lo que funcionó en el rediseño
de la cortinilla (2026-08-06/07), incluidas las trampas que salieron caras.

---

Vamos a rediseñar la sección **"Quién soy"** (`src/sections/about.ts`,
`data-scene="about"`, contenido en `src/data/content.ts`) del tema **Hyprland**.
Solo Hyprland: Vice está cerrado y no se toca, Caelestia queda fuera de alcance.

## Cómo quiero que trabajes

**1. Empieza por `superpowers:brainstorming`, no por el código.** No propongas
una dirección: propón varias, radicalmente distintas entre sí, y enséñamelas en
el **visual companion** como mockups **vivos** — con animación y estados reales,
no capturas ni artifacts. Antes de enseñármelos, mira tú la captura: en la
sesión de la cortinilla me enseñaste miniaturas inventadas y hubo que rehacerlas.

Cuando elija una dirección, hazla **fiel a la página real primero** (levanta el
sitio y mírala) y **luego** simplifícala. Ese orden importa: al revés se inventa.

**2. Usa los especialistas para converger, no para rankear.** `especialista-ux-ui`
y `especialista-animaciones`. Quiero opciones que los dos firmen, no una lista
con descartes. Píneales el modelo (`sonnet`) — heredan el de la sesión y un
fan-out sin pinear factura todo a tarifa top.

**3. Spec → plan → ejecución con `superpowers:subagent-driven-development`.**
En el plan, cada tarea con sus criterios y su arnés. Píneale el modelo a cada
subagente.

## Lo que NO quiero que se repita

Estas cinco cosas pasaron en la cortinilla. Las cinco costaron tiempo real.

- **Ningún número sustituye a mirar la captura al lado del prototipo.** Dos
  defectos graves (las siluetas no se dibujaban, el haz encogido a una esquirla)
  atravesaron dos revisiones y todos los arneses en verde, porque los arneses
  medían propiedades intermedias que eran ciertas mientras el resultado estaba
  roto. Si un arnés pasa y la captura no convence, el arnés mide lo que no es.
- **Un arnés no vale hasta verlo rojo contra el defecto real**, no contra un
  estado anterior conveniente. Y que vigile **todos** los elementos, no el
  primero: `measure-cortinilla.py` miraba una silueta de cinco.
- **Nada de constantes que reimplementen algo que se puede medir.** El proyecto
  ya tiene el caso `OBRA_TRANSIT` documentado: un número que nadie vuelve a
  medir no falla, miente. Mide el DOM.
- **Todo nodo nuevo que se cree en los tres temas necesita su `display: none` de
  base** en la lista compartida de `themes.css`. Se ha pagado cuatro veces; la
  última ensanchó el disparador de Vice de 168 a 411 px.
- **Para comparar contra el estado previo, `git worktree`, NUNCA `git stash`.**
  Un `stash --include-untracked` ya se llevó una sesión entera por delante.

## Gates antes de darlo por hecho

`npm run build`, `npm run lint`, `python3 scripts/verify.py` en los tres temas
más la pasada `--reduced`, y capturas reales del **build de producción** (no de
`npm run dev`: el HMR corrompe las medidas de ScrollTrigger).

Luego `lidia-naive-tester` y `vera-art-director` (umbral 7,5), pineados a
`sonnet`. A Lidia pídele que mida algo concreto y cronometrable, no una
impresión estética — en la cortinilla fue "tiempo hasta la primera pulsación
correcta", y fue lo que destapó que en móvil las miniaturas eran manchones.

Y al final, revisión de rama con **revisores independientes de lentes distintas**
(aislamiento entre temas / arneses que mienten / código y accesibilidad). En la
cortinilla, el de los arneses fue el único que devolvió CAMBIOS REQUERIDOS y
tenía razón.

## Cosas del entorno que te van a morder

- **Node 22 obligatorio**: `export PATH=~/.nvm/versions/node/v22.22.3/bin:$PATH`.
  Con Node 18 `npm run dev` revienta con `node:util does not provide an export
  named 'styleText'`.
- **Playwright**: `executable_path="/usr/bin/google-chrome"` y args
  `--no-sandbox --use-gl=swiftshader`. El chromium propio no está descargado y
  `/usr/bin/chromium-browser` no existe.
- **No canalices procesos largos por `tail`**: no emite nada hasta que acaban y
  la sesión se queda colgada. Redirige a fichero.
- **`verify.py` cae si tocas el árbol mientras corre** (Vite recarga por HMR y
  se lleva el contexto por delante). Córrelo solo, o sirve el build.

## Antes de empezar

Pregúntame lo que necesites saber sobre la sección — qué quiero que comunique y
a quién — antes de proponer nada. La persona de referencia es Marta Ruiz, 39,
reclutadora no técnica que decide en menos de dos segundos.
