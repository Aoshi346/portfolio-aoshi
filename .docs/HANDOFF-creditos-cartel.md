# Traspaso — "Con que construyo" como cartel de reparto (tema Vice)

> **SUPERADO PARCIALMENTE (2026-07-29).** Existe un plan formal con spec y
> checkboxes que es la fuente de verdad para ejecutar esto:
> `docs/superpowers/plans/2026-07-29-creditos-cartel-reparto.md` (spec en
> `docs/superpowers/specs/2026-07-29-creditos-cartel-reparto-design.md`).
> **Empieza por ahi.** Este documento se conserva porque su seccion de
> contenido real (el cruce tecnologia -> proyectos, verificado contra
> `content.ts`) y sus siete restricciones duras siguen siendo validas y el plan
> no las repite. Sigue SIN implementar: no hay rastro de `--font-billing` ni de
> la tipografia condensada en el codigo.

## Que hay que hacer

Rehacer la escena de creditos (`[data-scene="credits"]`) con la direccion **A ·
Cartel de reparto**, elegida por el usuario viendo el mockup: el bloque de
creditos del pie de un cartel de cine — tipografia condensada, versalitas, todo
centrado, sin recuadros ni panel lateral. La seccion deja de ser una interfaz
con lista y ficha y pasa a ser **una pieza tipografica**.

El mockup aprobado esta en
`.superpowers/brainstorm/2975344-1785280534/content/creditos-alternativas.html`
(bloque "A · Cartel de reparto"). Abrelo en un navegador directamente, o
levanta el companion visual con
`scripts/start-server.sh --project-dir <repo> --open` desde
`~/.claude/plugins/cache/claude-plugins-official/superpowers/*/skills/brainstorming/`.

Lo que hay HOY implementado y funcionando es la version anterior (lista
agrupada por area + panel de detalle a la derecha). No esta rota: es el punto de
partida a sustituir, y su comportamiento de datos hay que conservarlo.

## Como arrancar

```bash
# El Node del sistema es 18.19.1 y Vite 8 exige >= 20.
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run dev        # http://127.0.0.1:5173/?theme=vice
npm run build      # tsc + vite build
npm run lint
python3 scripts/verify.py
```

El tema se sortea al azar por visita: usar SIEMPRE `?theme=vice`.

## Donde vive

| Archivo | Que hace |
|---|---|
| `src/components/credits.ts` | Construye el DOM. Compartido por los TRES temas |
| `src/sections/skills.ts` | Monta la seccion (`.credits`, `data-scene="credits"`) |
| `src/style.css` | Base compartida: `.credit`, `.credit-role`, `.credit-name`, `.credit-group-label`, `.credits-panel*`, `.credits-used*` |
| `src/themes/themes.css` | Bloque Vice: reparto agrupado, dos columnas, panel a toda altura |
| `src/themes/vice.choreography.ts` | `scene4Credits` — entrada escalonada + pulso del panel |
| `src/data/content.ts` | `skillGroups`, `secondarySkills`, `caseStudies` |

## Contenido real (ya verificado contra content.ts — no lo re-deduzcas)

Grupos y tecnologias, en este orden:

- **Frontend**: React · TypeScript · Tailwind CSS · Vite
- **Backend**: Python · Django · MySQL
- **Otras herramientas**: JavaScript · HTML · CSS · C · C++

Cruce tecnologia -> proyectos (de `caseStudies[].stack`). **Cuidado: un informe
previo lo tenia mal**; esto esta comprobado parseando el bloque real:

| Tecnologia | Aparece en |
|---|---|
| React | EchoPlan, HyprFinance |
| TypeScript | EchoPlan, TesisFar, HyprFinance |
| Python | EchoPlan, WatchDog |
| Django | EchoPlan |
| Vite | EchoPlan |
| JavaScript | WatchDog |
| C | Editor de texto |
| Tailwind CSS, MySQL, HTML, CSS, C++ | ninguno |

Los cinco sin proyecto **no se rellenan con una frase generica**: hoy el bloque
"Aparece en" se oculta entero (`used.hidden = true`) y eso debe seguir asi.

## Decisiones de diseno que quedan ABIERTAS

El mockup fija la composicion, no el detalle. Hay que resolver, y conviene
enseñarlo en el companion antes de dar por bueno:

1. **Donde vive la frase de cada tecnologia.** En el mockup hay una sola linea
   bajo el bloque que cambia al pasar el raton
   ("React — interfaces con estado complejo · EchoPlan, HyprFinance"). Funciona,
   pero deja "Aparece en" reducido a una coletilla. Alternativas: una linea de
   dos alturas, o un bloque fijo bajo el cartel con su propio ritmo. **Es la
   principal contrapartida de esta direccion — el usuario la acepto sabiendolo,
   pero merece un segundo intento de resolverla mejor.**

2. **Que pasa en movil.** Doce nombres centrados en 390px de ancho se apilan y
   pierden la forma de cartel. Decidir si el cartel se mantiene con cuerpo mas
   pequeno, si se rompe en tres bloques, o si por debajo de cierto ancho se
   vuelve a la lista actual (que ya funciona bien en movil).

3. **Como se marca lo interactivo.** Sin recuadros ni bordes, la afordancia de
   "esto se puede pulsar" desaparece. En escritorio el hover lo resuelve; en
   tactil no hay hover. Hoy existe un `::after` con un "+" que cumple esa
   funcion en la lista — hay que decidir su equivalente aqui.

4. **La tipografia condensada.** El mockup usa Oswald. Ver la restriccion dura
   mas abajo antes de elegir.

## Restricciones duras — verificadas, no las descubras a golpes

1. **La tipografia condensada tiene que ser un token NUEVO.** `scripts/verify.py`
   comprueba que `--font-display` contenga "Passion One" y `--font-body`
   contenga "Manrope", y que ninguno resuelva a monoespaciada. Declara algo como
   `--font-billing` y usalo solo en el cartel; NO reasignes los otros dos.
   Ademas hay que darla de alta en los DOS sitios donde se piden fuentes: el
   `fontHrefs` del script inline de `index.html` (que es quien las pide antes
   del primer pintado) y el `fontHref` de `src/themes/vice.ts`. Si solo tocas
   uno, degrada a la via lenta en silencio.

2. **`.credit-role` no se puede eliminar del DOM.** `verify.py` exige que exista
   y este oculto por CSS para validar el re-skin a pildoras de
   Hyprland/Caelestia. Hoy se oculta con `display:none` solo bajo
   `[data-theme="vice"]`. Mantenlo.

3. **`credits.ts` lo comparten los tres temas.** Hyprland y Caelestia presentan
   la misma lista como pildoras. Cualquier cambio de DOM tiene que ser aditivo:
   si el cartel necesita estructura nueva, que sean nodos que los otros dos
   temas puedan ignorar por CSS, no una reorganizacion que les rompa el
   `flex-wrap`.

4. **Los encabezados de grupo son hermanos planos, nunca envoltorios.**
   `scene4Credits` anima los hijos DIRECTOS de `[data-credit-roll]`. Meter un
   contenedor por grupo reduciria el escalonado de doce filas a tres bloques.

5. **`gsap.from` esta prohibido de facto en este repo.** Deduce un extremo
   leyendo el DOM y ha causado tres regresiones reales (bloques del hero que no
   volvian nunca, doce filas de creditos desplazadas 34px para siempre, el pie
   de contacto invisible). **Usa `fromTo` con los dos extremos escritos a mano**,
   y materializa colecciones con `Array.from(...)`: pasar una `HTMLCollection`
   viva fue el detonante en dos de los tres casos.

6. **Un `transform` inline de GSAP gana siempre a una regla CSS.** Si un
   elemento recibe entrada con GSAP, su hover no puede usar `transform` en CSS:
   hay que animar un hijo o el envoltorio. Ya mordio en `.credit` (por eso el
   desplazamiento del hover vive en `.credit-name`) y en el CTA de contacto.

7. **Nada de `focusin` con scroll automatico.** Existio un manejador global que
   hacia `lenis.scrollTo` a cualquier elemento enfocado; como `focusin` tambien
   dispara con el raton, cada clic en una fila desplazaba la pagina 412px y
   sacaba el panel del encuadre. Hoy `wireFocusScroll` (`src/utils/reveal.ts`)
   solo actua con `:focus-visible` y solo si el elemento no se ve entero. No lo
   revientes al reorganizar.

## Accesibilidad — invariantes

- Cada tecnologia sigue siendo un `<button>` real, enfocable con Tab, con
  `aria-pressed` y `aria-controls` apuntando al contenedor de detalle.
- El contenedor de detalle sigue siendo `role="status"` con `aria-live="polite"`.
- Objetivo tactil de 44px (WCAG 2.5.5). En un cartel centrado con nombres
  seguidos esto es MAS dificil que en una lista: hay que dar padding real a cada
  nombre, no confiar en el alto de linea.
- El icono de la tecnologia es decorativo: `aria-hidden` + `data-decorative`
  (esto ultimo lo exime del gate de contraste; nunca uses `aria-hidden` para
  eximir del contraste).
- Contraste AA. El fondo es la bruma generativa de `viceHaze.ts`, que acota su
  brillo por shader: la escena actual mide entre 7:1 y 15:1. Si el cartel
  prescinde del scrim de `.credits-list`, vuelve a medir con
  `scripts/verify.py::check_contrast_wcag` — no lo des por hecho.

## Estado del arnes

`python3 scripts/verify.py` deja **12 fallos, todos preexistentes** y ajenos a
esta seccion: 9 rellenos de galeria en `public/media/obra/` y 3 ficheros
`public/media/vice-*` (el video de fixture, que ya no carga nadie desde que el
fondo es el shader; borrarlos cerraria esos 3 y esta pendiente de decision del
usuario). Cualquier fallo distinto de esos 12 lo has introducido tu.

`npm run build` y `npm run lint` en verde. Mantenlos.

## Como medir sin enganarte

- **`page.screenshot()` en headless perturba las animaciones**: bloquea el
  compositor y GSAP salta hacia delante, con lo que una timeline parece
  completarse antes de tiempo sin que sea cierto. Para medir ritmo, muestrea
  desde dentro de la pagina con `setInterval` sobre `tl.progress()`; para
  capturar fotogramas concretos, `tl.pause()` y `tl.progress(x)`.
- El shader de fondo hace que headless con `--use-gl=swiftshader` vaya
  lentisimo. Mientras depuras la seccion, bloquealo:
  `page.route("**/viceHaze*", r => r.abort())`.
- Verificacion visual obligatoria en 1440x900 y 390x844 antes de dar nada por
  hecho.

## Estilo de codigo

TypeScript strict, cero `any`. Cero emojis. Comentarios en espanol **sin
tildes**, densos, que expliquen POR QUE y no QUE — es el estilo del repo y
suele incluir la medicion que motivo la decision. Todo gesto respeta
`prefers-reduced-motion` (ojo: `initScrollReveal` hace early-return con
reduced-motion, asi que cualquier motion que muevas a CSS necesita su propia
media query).
