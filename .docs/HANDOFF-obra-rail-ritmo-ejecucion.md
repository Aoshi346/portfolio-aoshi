# HANDOFF — ejecutar el ritmo del carril de obra

> **RELEVADO el 2026-07-30.** El plan se ejecutó entero y se mergeó a `main` en `cdcc3ef`. Este
> fichero se queda como registro de lo que se decidió *antes* de implementar; para el estado
> real, ir al registro de implementación del spec. Lo que sigue abierto está en
> `.docs/HANDOFF-obra-siguiente-iteracion.md`.
>
> Qué pasó con lo que este handoff daba por decidido:
>
> - **El dimensionado se respetó entero.** 5040 px de presupuesto, `scrub` 0.5, reposo/tránsito
>   0.45. No se tocó ni una constante.
> - **Los objetivos numéricos de la tabla de abajo se reformularon**, tres de ellos. Estaban
>   calculados contra el final del tween y el instrumento los mide en el cruce de 0,99, que con
>   una cuártica llega un 32% de duración antes. La aritmética que lo demuestra está en el
>   registro del spec. La tabla de abajo es la de entonces: **la vigente es la del spec**.
> - **Una métrica se cayó**: `v_lateral_encuadre_px_s` está roto y se retiró.
> - **Apareció un punto de re-verificación que este handoff no previó**: el propio instrumento
>   medía contra el recorrido lateral en vez de contra el presupuesto del pin.
>
> Escrito el 2026-07-30 al cerrar el diseño. Releva a `HANDOFF-obra-rail-timing.md`, cuyo
> encargo (medir antes de tocar) está cumplido.

## Dónde está todo

- **Spec, con el dimensionado tween por tween:**
  `docs/superpowers/specs/2026-07-30-obra-rail-ritmo-design.md` — `Estado: en ejecucion`
- **Plan, 4 tareas y 27 pasos:** `docs/superpowers/plans/2026-07-30-obra-rail-ritmo.md`
- **Instrumento de medida:** `scripts/measure-obra-rail.py`

Léelos en ese orden. El plan es autocontenido: lleva el código literal de cada paso.

## Qué se decidió, y con qué números

Dirección elegida: **presupuesto 5040 px · `scrub` 0.5 · reposo/tránsito 0.45**.

```
travel = 4 · iw = 5760 px      (el recorrido lateral NO cambia)
T      = 0.56 · iw =  806 px   de scroll por cada 1440 laterales
R      = 0.252 · iw =  363 px  de reposo
end    = 3.5 · iw  = 5040 px   presupuesto del pin (antes 5760)
engranaje 1.79:1 · scrub 0.5 · documento 12307 -> 11587
```

La regla que fijó el `scrub`, medida sobre el mockup: **el reposo solo se siente como reposo
si el asentamiento del scrub es más corto que la meseta.** Con `scrub: 1` (956 ms) y una
meseta de 563 ms, la pieza que peor se posa se queda en 147 px/s por mucho que se alargue el
reposo — ni con la meseta al máximo (849 ms) baja de 92. Con `scrub: 0.5` (480 ms) baja a 18.

## Lo que ya está en `main`

| commit | qué |
|---|---|
| `dcc7998` | **P0**: con `prefers-reduced-motion: reduce` y >=901px, las obras 2 a 5 eran inalcanzables. Verificado 1/5 -> 5/5 |
| `3704a89` | spec + instrumento de medida |
| `e7f578c` | plan de implementación |

## Cómo arrancar

Worktree aparte, **nunca `git stash`** (un `stash --include-untracked` ya se llevó una sesión
entera por delante):

```bash
git worktree add ../portfolio-ritmo -b design/obra-rail-ritmo
```

**Modelo:** la implementación es edición acotada de una función ya dimensionada -> **Sonnet**.
Pinea el modelo de cada subagente: heredan el de la sesión y un fan-out sin pinear factura
todo a tarifa top. Se acordó despachar un subagente por tarea con revisión entre medias.

## Verificación

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
npm run preview -- --port 4173      # SIEMPRE ?theme=vice
python3 scripts/measure-obra-rail.py
python3 scripts/verify.py           # baseline: 12 fallos aceptados, sale 0
```

Objetivos numéricos, en el build de producción a 1440x900:

| | hoy | objetivo |
|---|---|---|
| adelanto de la cartela entera | ~800 px | ≤ 40 px, sin dispersión entre velocidades |
| adelanto del `.lead` | 938-995 px | ≤ 260 px |
| v lateral en el encuadre | 220-245 px/s | ≤ 20 px/s en las cinco piezas |
| permanencia pieza 5 vs central | 33-40% | paridad |
| documento | 12307 px | ~11587 px |

## Las tres trampas que más tiempo cuestan

- **Medir en el build de producción, nunca en `dev`.** El HMR corrompe las medidas de
  ScrollTrigger y miente en los dos sentidos.
- **Nada de `page.screenshot()` para medir ritmo.** Bloquea el compositor y adelanta la
  timeline.
- **`free -h` antes del arnés.** Con menos de ~3GB libres el navegador muere a mitad con
  *execution context was destroyed*: es presión de memoria, no una regresión.

Y una que se pisó en esta sesión: **`scroll-behavior` es `smooth`**, así que un
`window.scrollTo` sin `behavior: "instant"` aterriza corto y da falsos negativos. Costó dos
hipótesis caídas.

## El mockup, por si quieres volver a verlo

Vive en `.superpowers/brainstorm/265690-1785372006/content/banco-de-montaje.html` (la carpeta
está en `.gitignore`, así que existe solo en esta máquina). Para servirlo otra vez:

```bash
/root/.claude/plugins/cache/claude-plugins-official/superpowers/6.2.0/skills/brainstorming/scripts/start-server.sh \
  --project-dir /home/aoshi/proyectos/portfolio-aoshi --open
```

Necesita `npm run preview` en el 4173 para las capturas reales. Los tres diales
(presupuesto, scrub, reposo) siguen abiertos por si quieres re-discutir el dimensionado.

## Fuera de alcance, ya decidido

- **Orientación, índice y salida** durante el carril: es el defecto que el especialista de UX
  puso por encima de todo, pero es navegación, no ritmo. Encargo aparte, junto al hallazgo del
  naive test sobre los ~8600 px hasta el `mailto:`. Acortar el carril lo alivia y no lo cierra.
- **Trampa de teclado, sin verificar:** tabular a un enlace de una obra fuera de pantalla
  podría poner `scrollLeft` en `.obra-rail`, que GSAP no conoce, desalineando el carril de
  forma permanente. Es sospecha, no medida.
- **`will-change: transform` permanente** sobre un track de 7200x900. No medible en
  swiftshader (6 fps con shader frente a 25 sin él es el rasterizador por software, no la GPU).
- **Número de piezas:** decisión de contenido.

## Gate final antes de merge

`lidia-naive-tester` (flujo) y `vera-art-director` (ejecución visual), los dos leyendo su
`memory.md` antes de actuar. En la sesión anterior encontraron un P0 que nadie había visto.
