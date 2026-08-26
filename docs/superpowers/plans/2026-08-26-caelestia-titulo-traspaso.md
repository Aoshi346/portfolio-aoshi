# Traspaso — Caelestia B1 (Título)

Este fichero es el **prompt de arranque** para la sesión que implemente la fase B1. Cópialo entero
como primer mensaje de una sesión con contexto limpio.

---

## Modelo y esfuerzo recomendados

| | recomendación | por qué |
|---|---|---|
| **Modelo de la sesión** | **Sonnet** | El plan ya trae el código escrito y las decisiones de diseño cerradas. El grueso es ejecución mecánica sobre ficheros nombrados: siete tareas, cada una con sus pasos y sus comandos. La norma de `/home/aoshi/proyectos/CLAUDE.md` es explícita — mecánico y edición dirigida van a Sonnet, no al modelo top. |
| **Esfuerzo de razonamiento** | **medio**, y **alto** en dos puntos concretos | Ver abajo. |
| **Escalar al modelo top** | **una vez, y solo si aparece uno de los dos riesgos abiertos** | Están señalados en el plan: (1) si `shaderBackground.ts` no acepta uniforms `vec2`/`vec3` — es un fichero **compartido con Vice**, que está cerrado, y ahí la decisión no es mecánica; (2) si el barrido de 24 h de la tarea 2 da por debajo de 4.5:1 — significa que la rampa de color hay que recalibrarla, y eso es diseño. |
| **Subagentes** | **`model: sonnet` pinado en cada uno**, sin excepción | Los subagentes **heredan el modelo de la sesión**: un fan-out sin pinear en una sesión top factura todo a tarifa top. Aplica también a `lidia-naive-tester` y `vera-art-director` de la tarea 8. |
| **Modo de ejecución** | **subagent-driven**, un subagente por tarea con revisión entre tareas | Las ocho tareas son independientes y cada una termina en un entregable verificable con su propio comando. Es exactamente la forma que pide `superpowers:subagent-driven-development`. |

**Dónde sí hace falta esfuerzo alto, dentro de una sesión Sonnet:**

- **Tarea 2, portar el shader.** Hay que quitar tres uniforms del prototipo sin romper el resto, y
  decidir cómo pasar `vec2`/`vec3` sin tocar `shaderBackground.ts`. Es la única tarea donde el
  código no está escrito del todo en el plan.
- **Tarea 8, ver cada gate dar rojo.** Requiere romper a propósito ocho cosas distintas y confirmar
  que el instrumento las caza. Es tedioso y es donde se cuela el error de la fase A si se hace
  deprisa.

**Presupuesto de tiempo.** Las tareas 2 y 8 corren el barrido de 24 horas: 96 pestañas de Playwright
con swiftshader, entre 8 y 15 minutos cada vez. No es un cuelgue.

---

## Prompt de arranque

> Vas a implementar la fase **B1** del rediseño de Caelestia en `/home/aoshi/proyectos/portfolio-aoshi`
> — la escena Título del portfolio de Aoshi Blanco Sanz.
>
> **Lee primero, en este orden:**
>
> 1. `docs/superpowers/plans/2026-08-26-caelestia-titulo.md` — el plan, tarea por tarea. Es lo que
>    tienes que ejecutar.
> 2. `docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md` — el spec, que es de dónde el
>    plan saca sus razones. Léelo entero antes de la tarea 2.
> 3. `CLAUDE.md` y `.claude/CLAUDE.md` — las reglas del repo.
> 4. `docs/superpowers/specs/2026-08-26-caelestia-titulo-prototipo.glsl` — el shader aprobado,
>    cuando llegues a la tarea 2.
>
> **Usa `superpowers:subagent-driven-development`**, un subagente por tarea, y **pina `model: sonnet`
> en todos**.
>
> **Cinco cosas que te van a morder si no las sabes de antemano:**
>
> 1. **Node 22.** `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"` antes de cualquier
>    `npm`. Con el Node 18 del PATH por defecto, `vite build` revienta dentro de rolldown con un
>    error sobre `styleText` que no dice nada de la versión.
> 2. **Verifica contra el build servido**, `npm run build && npx vite preview --port 4173`, nunca
>    contra `npm run dev`. El HMR de Vite corrompe las medidas de layout y miente en los dos
>    sentidos.
> 3. **El tema se sortea por visita.** Toda URL de comprobación lleva `?theme=caelestia`.
> 4. **`root` ES el `<main>`** en la coreografía de Caelestia — `reveal.ts` llama
>    `initScrollReveal(main, theme)`. Un `querySelector("main")` devuelve `null` y la coreografía
>    se sale en silencio sin ejecutar nada. Está en el docstring de
>    `src/themes/caelestia.choreography.ts`; léelo entero antes de tocarlo.
> 5. **Vice está cerrado y Hyprland no se toca.** `src/backgrounds/shaderBackground.ts` es
>    compartido por los tres temas: si crees que hay que modificarlo, **para y pregunta**.
>
> **Cuando termines cada tarea**, corre `npm run build`, `npm run lint` y
> `python3 scripts/measure-caelestia-titulo.py --base http://localhost:4173`, y commitea. No pases
> a la siguiente con el arnés en rojo.
>
> **No declares DONE sin** build verde, lint limpio, los cuatro arneses en código 0 (el nuevo,
> `measure-caelestia-hora.py`, `measure-obra-rail.py` y `verify.py`), y una captura real del
> navegador que hayas mirado.
>
> Empieza por la **tarea 1**.

---

## Estado al entregar

- **Spec:** `docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md` — `Estado: pendiente de plan`.
  La sesión que ejecute lo pasa a `implementado` en la tarea 8.
- **Artefactos aprobados, ya en el repo** (el companion de brainstorming **no está versionado**):
  - `docs/superpowers/specs/2026-08-26-caelestia-titulo-prototipo.glsl` — 154 líneas, el shader del
    fondo con la lista de qué quitar al portarlo.
  - `docs/superpowers/specs/2026-08-26-caelestia-firma-paths.json` — 15 glifos, ancho 945.7, para
    contrastar contra lo que genere `scripts/gen-firma-paths.py`.
- **Sin empezar:** las fases **B2** (Quién soy), **B3** (Obra), **B4** (Créditos) y **B5** (Fundido).
  Tienen dirección aprobada —cada escena es una aplicación— pero **no tienen spec**.
- **Bloqueo externo, que no afecta a B1:** las nueve capturas de `public/media/obra/` siguen siendo
  marcadores «CAPTURA PENDIENTE» con la paleta de Vice. Bloquean B3, no esta fase.
