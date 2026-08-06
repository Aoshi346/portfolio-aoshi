# El lomo — el hero de Ascua gana dispositivo propio y coreografía bespoke

Estado: implementado
Plan: `docs/superpowers/plans/2026-08-05-hyprland-hero-lomo.md`
Fecha: 2026-08-05
Alcance: solo el hero del tema Hyprland — `src/sections/hero.ts` (estructura compartida por los
tres temas, con nodos nuevos que solo Hyprland muestra), el bloque Hyprland de
`src/themes/themes.css` (~1091-1284) y `src/themes/hypr.choreography.ts`. **Vice y Caelestia no
se tocan.** Ascua en general sigue "implementado" (spec
`docs/superpowers/specs/2026-08-05-hyprland-ascua-design.md`); este spec es un refinamiento
específico del hero, no una reapertura del tema completo.

## Por qué

Ascua está implementado y mergeado, con los gates de crítica ya pasados (BLOCK aceptado, residual
conocido en imágenes de obra). Pero el hero en concreto usa la receta genérica de revelado que
comparte con el resto de las cinco escenas (`hypr-cut`/`hypr-up` con stagger de 70ms) y ningún
dispositivo propio — a diferencia del resto de Ascua, que se construye sobre objetos con forma
(la tira de exposición, el reparto, las bandas de contacto). Evaluado por Aoshi como "se siente
genérico": ni la composición, ni el movimiento de entrada, tenían nada exclusivo del hero.

Sesión de brainstorming con el companion visual (`superpowers:brainstorming`), iterando en HTML/CSS
puro contra la paleta y tipografía ya aprobadas de Ascua (sin inventar tokens nuevos — ese trabajo
ya está cerrado). Aportes en paralelo de `especialista-ux-ui` (jerarquía, accesibilidad,
responsive) y `especialista-animaciones` (secuenciación, tokens de curva, riesgo de
amontonamiento), pineados a Sonnet.

## Qué se construye

### El dispositivo — "el lomo"

El hero pasa de un apilado plano a una composición asimétrica de 3 columnas en desktop: una
etiqueta de rol rotada (`writing-mode: vertical-rl`) pegada al borde izquierdo, como el lomo de
un libro o un carrete, un filete vertical de 1px que separa esa etiqueta del bloque de contenido,
y el nombre/lead/corner desplazados a la columna derecha.

```
┌────┬─┬─────────────────────────────┐
│ D  │ │  Aoshi Blanco Sanz           │
│ e  │ │  (fantasma detrás, se apaga) │
│ s  │ │                              │
│ a  │ │  "Caracas. Full stack..."    │
│ r  │ │                              │
│ r  │ │  ─────────────────────────   │
│ o  │ │  Caracas, Venezuela  email   │
│... │ │                              │
└────┴─┴─────────────────────────────┘
```

Es un dispositivo **exclusivo del hero** — nadie más en el sitio tiene una etiqueta rotada — pero
reutiliza vocabulario ya existente en Ascua: el filete vertical es una instancia de `.hypr-rule`
(`scaleY` desde `transform-origin: top`, ya definido en `themes.css:1266-1274`), no un mecanismo
nuevo.

**Responsive**: colapsa a una sola columna (etiqueta horizontal encima, filete horizontal) en
`max-width: 900px` — el mismo umbral que ya usa `.contacto-bar-label` (Vice) para el mismo
problema (etiqueta rotada que deja de caber). No se introduce un breakpoint nuevo.

**Hallazgos de móvil, encontrados verificando el mockup a escala real (390×844) — no estaban en
la primera versión de este spec**, porque las capturas anteriores se tomaban antes de que el
bloque `.hero` pasara a `display: grid`:

1. **`align-content` no puede quedar en su valor por defecto.** CSS Grid resuelve `normal` a
   `stretch` (a diferencia de flexbox, donde resuelve a `start`) — con `min-height: 100vh` y filas
   de contenido mucho más cortas que la pantalla, el navegador reparte el sobrante *entre* filas
   en vez de agruparlas, dejando huecos enormes y desiguales entre la etiqueta, el filete y el
   contenido. Fija explícito: `align-content: center` (no `start`) — el hero **ya** ocupa la
   pantalla completa hoy en los tres temas (`min-h-screen` compartido) y su contenido ya se
   centra verticalmente por la clase `justify-center` compartida; `center` conserva ese mismo
   reparto de aire arriba/abajo en vez de amontonarlo todo abajo.
2. **El tamaño mínimo del nombre en móvil ya era grande antes de este rediseño** (`clamp(var(--t-6),
   8.2vw, var(--t-9))`, mínimo 50,52px, heredado de Ascua) — no es una regresión de este spec,
   pero como se está tocando el hero de todas formas, el breakpoint `max-width: 900px` fija un
   tope propio y más comedido para el nombre: `clamp(2rem, 9.5vw, 2.6rem)` (32-41,6px). El resto
   de usos de `.display-xl` (about, contacto) no se tocan.
3. **El corner (ubicación + correo) se apila en vez de ir en fila** dentro del mismo breakpoint de
   900px. En fila, "Caracas, Venezuela" partía en dos líneas apretado contra el ancho que dejaba
   el correo, mientras el correo quedaba en una sola línea — desalineados verticalmente y con un
   corte de línea justo después de la coma. Apilar (`flex-direction: column`) es el mismo patrón
   que ya usa el sitio para el mismo problema en las barras de contacto (rótulo encima del valor
   bajo 520px), aplicado aquí en el breakpoint del propio dispositivo del "lomo".

### La entrada — doble exposición fusionada con el corte

El nombre entra con una copia fantasma desfasada detrás (`--l2`, blur 1px, `mix-blend-mode:
screen`, offset `0.35em / -0.28em` — proporcional al tamaño de fuente, no en `px` fijos, para que
no se desborde en ningún breakpoint) que se sostiene visible hasta el 35% de su animación
(opacidad `.75` → `.68`) y solo entonces empieza a apagarse hacia 0 en 1.4s con `--slow`. El
nombre real se revela palabra por palabra vía `clip-path`, y el **filete vertical y el corte de la
primera palabra arrancan a la vez, mismo trazo** — se leen como un solo gesto, no dos.

Tabla de tiempos (t=0 = `is-lit` en el hero; duraciones de corte en `--hard`, atmosféricas en
`--slow`, sin inventar una tercera curva):

| Pieza | Delay | Duración | Curva |
|---|---|---|---|
| Filete vertical + palabra 1 del nombre (mismo trazo) | 0ms | 500ms | `--hard` |
| Chispa viajando en la punta del filete | 0ms | 500ms | `--hard` |
| Etiqueta de rol (corte, no fade) | 220ms | 500ms | `--hard` |
| Destello al aterrizar el filete | 450ms | 400ms | `--slow` |
| Palabra 2 del nombre | 300ms | 500ms | `--hard` |
| Palabra 3 del nombre | 600ms | 500ms | `--hard` |
| Fantasma (sostén hasta 35%, luego se apaga) | 0ms | 1400ms | `--slow` |
| Lead | 1050ms | 900ms* | `--slow` |
| Filete superior del corner | 1300ms | 500ms | `--hard` |
| "Caracas, Venezuela" (corte) | 1550ms | 420ms | `--hard` |
| Correo (corte) | 1720ms | 420ms | `--hard` |

\* Duración heredada de `.hypr-up` (900ms), no recalibrada en esta sesión.

Settle del contenido esencial (nombre + lead + corner): ~2,14s (el correo, última pieza de
lectura, termina su corte a los 1720+420ms). El nombre real está legible (última palabra
cortada) a los 1,1s — dentro del principio ya escrito en `hero.ts` ("nombre, rol y contacto
legibles al instante").

**Por qué el corner deja de usar fade+translateY**: la primera versión mockeada reveló que un
`::before` con la línea ya pintada desde el frame 0 (solo el overlay de color cambiaba encima) no
se leía como animación — casi imperceptible. Se sustituye por el mismo lenguaje de corte que usa
el resto del hero: el filete se dibuja con `scaleX`, y "Caracas, Venezuela"/el correo se descubren
con el mismo `clip-path` que las palabras del nombre, en cadena. Consistencia de mecanismo en todo
el hero, no una mezcla de fades y cortes.

### Idle — un único pulso, gateado

Se descarta el brightness-pulse (rompía el contraste ya medido del degradado — "Medido en el
prototipo: 14,4:1 sobre el campo" es un número sobre el estado estático, no sobre un filtro
oscilando encima) y el idle infinito desde la carga (WCAG 2.2.2, contenido en movimiento >5s sin
mecanismo de pausa). Queda **un solo pulso de opacidad** (`1 → .9 → 1`, ciclo de 6s), activo solo
mientras el puntero o el foco están dentro del hero (`:hover`/`:focus-within`), no desde que carga
la página.

### `--bx`/`--by` — recalibración

El degradado que "engancha" luz en el nombre (`background: radial-gradient(...) fixed;
background-clip: text`) sigue funcionando igual mecánicamente con el nombre desplazado a la
columna derecha (`background-attachment: fixed` posiciona contra el viewport, no contra la caja
del elemento) — pero los **números** sí necesitan ajuste: `--bx` pasa de una base centrada (52%)
a ~70%, para que el barrido de luz que ya mueve `hypr.choreography.ts` (Gesto 3, ligado al scroll
de toda la página) siga cruzando por dentro de las letras y no por el aire vacío a la izquierda de
la nueva columna.

### Accesibilidad — hallazgo independiente del rediseño

El enlace de correo (`.hero-mail`) hoy solo cambia de color en `:focus-visible`, sin ninguna marca
geométrica — más débil que el patrón que el propio tema usa en otros sitios
(`.contacto-bar:focus-visible` con `outline`, `.scene-nav-trigger:focus-visible` con tratamiento
dedicado). Se añade el mismo filete que ya usa en `:hover`, también en `:focus-visible`. Es un fix
aplicable independientemente del resto de este spec.

## Restricciones

- El hero **sale de la `RECETA` genérica** de `hypr.choreography.ts` (ya no recibe `hypr-cut`/
  `hypr-up` de fábrica) y recibe su propio gesto — la receta genérica sigue intacta para las
  otras cuatro escenas.
- `prefers-reduced-motion`: el bloque de neutralización ya existente en `themes.css:1276-1284`
  necesita entradas nuevas para el fantasma (oculto, no solo sin animar), los `<span>` de palabra
  del nombre, el spine, la chispa/destello del filete, las piezas del corner y el idle — el
  resultado final debe ser el layout estático completo, sin ninguna pieza a medio revelar.
- Vice y Caelestia no se tocan. Verificar con `python3 scripts/verify.py --theme vice` y
  `--theme caelestia` antes y después.
- El nombre (`identity.name` en `content.ts`) se divide en 3 `<span>` por palabra ("Aoshi" /
  "Blanco" / "Sanz") — dato real fijo, no una solución genérica para nombres de longitud
  arbitraria.

## Qué se descartó, y por qué

- **Brightness-pulse como idle** (dirección "El filamento" del primer barrido de mockups): filtra
  sobre un degradado ya calibrado en contraste, arriesga el número medido en cada frame del pulso.
- **Idle infinito desde la carga**: problema de WCAG 2.2.2 (movimiento automático sostenido sin
  mecanismo de pausa) además de ser el primer loop infinito del tema sin ninguna convención
  existente que lo respalde.
- **V1 "secuencial"** (filete termina, luego el nombre empieza a cortarse): funcional pero un beat
  perceptible más que la fusión, y con 6+ piezas animadas en <2s el hero corría riesgo de sentirse
  amontonado justo cuando su propia regla es "legible al instante". Se prefirió la fusión (filete
  = corte de la palabra 1) por reducir un beat sin quitar ningún elemento.
- **V2 "ecos múltiples"** (dos copias fantasma, todo arrancando en t=0 sin relación causal):
  descartada por el especialista de animaciones — acumula más beats simultáneos, exactamente el
  riesgo que V1/V3 buscaban evitar.
- **Corte de cámara** y **respiración de brasa** (direcciones B y C del primer barrido, sin
  combinar): descartadas al elegir la combinación A+C explícitamente.
- **Alargar la duración de los cortes individuales** más allá de 500ms al pedir que la animación
  se sintiera más lenta: se alargó el *espacio entre* gestos (stagger) y el atmosférico del
  fantasma en su lugar. Los cortes en sí se quedaron en el techo del rango ya documentado por la
  spec de Ascua (400–500ms) — alargarlos habría roto el contraste de tiempos que es la seña de
  identidad del tema.
- **Duplicar `--bx`/`--by` por layout**: no hace falta un mecanismo nuevo, `background-attachment:
  fixed` ya posiciona contra el viewport — solo se recalibran los números base.

## Verificación

- `npm run build` y `npm run lint` en verde.
- Capturas 1440×900 y 390×844 con `?theme=hyprland` (mobile confirma el colapso del spine a
  horizontal en el breakpoint de 900px).
- Contraste del fantasma medido compuesto sobre el nombre real y sobre el fondo, no asumido a
  partir de la opacidad declarada (mismo principio que ya aplicó el harness al resto de Ascua:
  recorte ajustado al glifo, no a la caja).
- `--bx`/`--by` recalibrados verificados visualmente contra la nueva posición del nombre, no solo
  medidos en el prototipo del companion (el fondo real es el shader, no el `radial-gradient` de
  respaldo usado en los mockups).
- `python3 scripts/verify.py` en verde para `--theme hyprland`, **y también** `--theme vice` y
  `--theme caelestia`, más una pasada `--reduced` para confirmar el fallback completo.
- Foco de teclado: Tab hasta el correo confirma el filete de `:focus-visible`, no solo el cambio
  de color.
- Revisión de Aoshi sobre el sitio real (no solo capturas), como en el resto de Ascua.
- Gates `lidia-naive-tester` y `vera-art-director` si el alcance del cambio lo justifica al cerrar
  la tarea (a decidir en el plan).

**Prototipos de referencia, aprobados en el companion visual** (no se comitean, quedan en
`.superpowers/brainstorm/`, gitignored):
`hero-motion-directions.html` → `-v2.html` (bug de texto invisible corregido) → `hero-motion-v3.html`
(3 direcciones con layout propio) → `hero-ac-refined.html` (combinación A+C, V1 vs V3) →
`hero-ac-v3-slow.html` (timing más lento) → `hero-ac-v3-ghost.html` (fantasma más presente,
versión final del fantasma) → `hero-full-page.html` (hero completo a escala real) →
`hero-full-page-v2.html` (spine/filete/corner con corte propio) → **`hero-full-page-v3.html`**
(versión final aprobada — filete del corner sin línea base estática, Caracas/correo con
`clip-path` en cadena).

## Registro de implementación

Cerrado el 2026-08-06. Seis tareas completas vía `superpowers:subagent-driven-development`
(un implementador + un revisor por tarea, en un worktree aislado), revisión de Aoshi sobre el
build de producción real (`npm run preview`, no dev ni mockup) en los checkpoints de móvil
(antes de la Task 2) y al cierre (Task 6), con vídeo grabado de la entrada real además de
capturas.

### Divergencias respecto al plan

Tres huecos aparecieron verificando contra el mockup y el código real, no al leer el plan
original — el mismo patrón que ya dejó escrito la spec de Ascua:

1. **`align-content` de CSS Grid resuelve `normal` a `stretch`** (a diferencia de flexbox, donde
   resuelve a `start`). Con `min-height: 100vh` y las filas del "lomo" colapsadas a una sola
   columna en móvil, el navegador repartía el sobrante *entre* filas en vez de agruparlas —
   huecos enormes y desiguales entre la etiqueta, el filete y el contenido. Encontrado
   literalmente viendo el mockup en 390×844 en el companion, no en el diseño original de
   escritorio (que solo tiene una fila, donde el bug no se nota). Fijado a `align-content:
   center`, que conserva el mismo reparto de aire arriba/abajo que ya tenía el hero heredado
   antes de este rediseño.
2. **El tamaño mínimo del nombre en móvil ya era grande antes de este spec** (heredado de Ascua,
   clamp con mínimo 50,52px) y **el corner en fila partía "Caracas, Venezuela" en dos líneas**
   desalineadas contra el correo. Ninguno de los dos era una regresión de este rediseño, pero
   como ya se estaba tocando el hero, se corrigieron en el mismo breakpoint de 900px: tope propio
   de `clamp(2rem, 9.5vw, 2.6rem)` para el nombre, y `.hero-corner` apilado
   (`flex-direction: column`) en vez de en fila.
3. **La técnica de degradado de texto (`background-clip: text`) no atraviesa un hijo
   `display: inline-block`.** El plan pedía envolver cada palabra del nombre en un `<span
   class="hero-name-word">` con su propio `clip-path` para el corte palabra-a-palabra — pero
   `background`/`background-clip` no son propiedades heredadas, así que cada span quedaba sin
   fondo y con `color: transparent` heredado: el nombre entero se volvía invisible tal cual
   estaba escrito el plan. El implementador de la Task 3 lo encontró y lo arregló con
   `background: inherit; -webkit-background-clip: inherit; background-clip: inherit;` en
   `.hero-name-word` — cada palabra repinta el mismo degradado (con `background-attachment:
   fixed`, calculado contra el viewport, no contra la caja) y encaja sin costura con sus vecinas.
   Verificado por el revisor de la Task 3 como un arreglo necesario y acotado, no como alcance
   añadido — el bug estaba en el CSS del propio plan, no en la implementación.

Dos correcciones de tracking, sin efecto en el código: el spec no citaba el plan (rompía
`check_spec_plan_consistency`) y se quedó con `Estado: pendiente de plan` mientras el plan ya
existía y estaba en ejecución — arreglado añadiendo la línea `Plan:` y actualizando el estado.

### Hallazgos del harness ajenos a esta rama

`scripts/verify.py` reporta, en las cuatro pasadas de la Task 6 (`hyprland`, `hyprland --reduced`,
`vice`, `caelestia`), fallos que **no** están causados por esta rama — confirmado cruzando
`git diff --stat` contra los cuatro archivos tocados (`hero.ts`, `style.css`, el bloque Hyprland de
`themes.css`, `hypr.choreography.ts`): ninguno menciona `credit`, `Vite`, `GSAP`, ni el disparador
de navegación de escena (`scene-nav-trigger`).

- **Caelestia, 9 fallos**: contraste del disparador de navegación de escena (`"01 · Título"` ...
  `"05 · Fundido"`) en las cinco escenas, ratios 4,05:1–4,24:1 contra el mínimo 4,5:1. Reproducido
  idéntico en dos pasadas consecutivas — no es parpadeo del fondo generativo, es deriva de la
  línea base (`verify-baseline.json` quedó desactualizada respecto al estado real de `main`).
- **Hyprland, 2 fallos**: contraste de los chips "Vite" y "GSAP" en la escena de créditos, ratios
  4,25:1–4,45:1. Mismo patrón: ajeno al hero, reproducido de forma estable, deriva de línea base.

No se tocó `verify-baseline.json` en esta rama — actualizarla es una decisión de alcance del
repo completo, no de este spec.

### Verificación final

`npm run build`/`lint` en verde. `verify.py` en verde para `hyprland`, `hyprland --reduced`,
`vice` y `caelestia` (0 fallos nuevos atribuibles a esta rama en las cuatro pasadas — ver arriba).
Capturas 1440×900 y 390×844 sobre `npm run preview` (build real, no dev): cero errores de consola
en ambas. Foco de teclado confirmado con `Tab` real (no `.focus()` programático, que en Chromium
no dispara `:focus-visible`): el filete y el color de acento se activan en el enlace de correo.
Grep anti-mock limpio en `hero.ts`/`hypr.choreography.ts`.

### Revisión final de toda la rama — lo que las seis revisiones por tarea no podían ver

Las seis tareas de implementación pasaron su revisión individual sin ningún hallazgo Crítico ni
Importante. La revisión final de toda la rama (modelo más capaz, tras cerrar la Task 6) encontró
tres Críticos y dos Importantes reales que ninguna revisión por tarea podía atrapar porque cada
una miraba solo su propio diff aislado:

1. **`.hero-kick` y `.lead` son clases compartidas por las cinco escenas** (about, obra, créditos,
   contacto, hero), no exclusivas del hero. El CSS del "lomo" (grid, `writing-mode: vertical-rl`,
   la animación de entrada bespoke) se había añadido sin acotar a `[data-scene="hero"]` —
   "Quién es", "Contacto", "Con qué construyo" y las cinco etiquetas de obra se renderizaban
   rotadas 90° en Hyprland, y además recibían la animación de entrada del hero encima de la
   receta genérica que la Task 4 ya les dejaba intacta (las dos animando `clip-path` al mismo
   tiempo sobre el mismo elemento — exactamente la colisión que esa tarea existía para evitar).
2. **Mover `.hero-corner` dentro de `.hero-surface` (Task 1) rompía la posición del correo en
   Caelestia.** `.hero-surface` en Caelestia lleva `backdrop-filter` no nulo, que establece
   contenedor de posicionamiento para descendientes `position: absolute` — el correo, que sigue
   siendo `position: absolute` ahí, pasaba a anclarse contra la tarjeta en vez de contra la
   sección (175px de desplazamiento vertical medido). El comentario que justificaba el cambio en
   `hero.ts` decía lo contrario de lo que hace `position: absolute` con un contenedor nuevo.
3. **Mover la etiqueta de rol fuera de `.hero-surface` (Task 1) desplazaba el rótulo en Vice y
   Caelestia** — en Vice 48px hacia arriba (pasa de bloque a ancho completo dentro del padding de
   la superficie a item de flex que se ajusta a su contenido), en Caelestia se salía por completo
   de la tarjeta Material You.

**Arreglo**: un único fix (no uno por hallazgo, según el protocolo) — `.hero-corner` vuelve a ser
hermano de `.hero-surface` en el DOM (como antes de este spec) y Hyprland lo reposiciona solo con
`grid-column`/`grid-row`, sin tocar el árbol compartido; Vice y Caelestia reciben CSS propio de
compensación para la etiqueta de rol (`position: relative; top`, no `margin-top`, porque
`.hero` centra por `justify-content` y un margen ahí redistribuye la altura entre todos los
items). Verificado con comparación de geometría (`getBoundingClientRect`) contra el commit previo
a esta rama, bit a bit idéntica en Vice y Caelestia, en 1440×900 y 390×844. Una regresión de
móvil que el propio arreglo introdujo (el `grid-column: 3` del correo se filtraba a la rejilla de
una sola columna) se encontró y corrigió en la misma pasada. Reverificado con una re-revisión
acotada, independiente del reporte del implementador (medición propia, no solo lectura del
diff): los ocho hallazgos (3 Críticos + 2 Importantes + 3 menores) quedaron atendidos, sin
regresión nueva.

**Lección para el checklist de verificación**: la Task 6 tomó capturas de escritorio y móvil del
hero, pero no de las otras cuatro escenas ni con `full_page=True` — las tres roturas vivían fuera
de ese encuadre. La comparación de geometría contra el commit previo (no solo `verify.py`, que
mide contraste, no posición) es lo que de verdad prueba "byte a byte idéntico" cuando el cambio
toca una clase o un nodo compartido.
