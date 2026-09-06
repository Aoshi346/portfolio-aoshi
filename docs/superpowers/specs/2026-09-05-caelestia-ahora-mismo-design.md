# Caelestia — la tarjeta «Ahora mismo», rediseño

Estado: en ejecucion
Fecha: 2026-09-05
Rama de trabajo: `fix/repaso-interfaces` (se abrirá rama propia `design/caelestia-ahora-mismo` al planificar)
Origen: sesión de repaso de interfaces con Aoshi. Reabre una pieza cerrada en
`2026-08-26-caelestia-titulo-design.md` (§ «El widget: Ahora mismo»).

---

## Qué se rediseña y por qué

La tarjeta «Ahora mismo» del hero de Caelestia (`#hero .cae-widget`, construida en
`src/sections/hero.ts` y vestida en `src/themes/themes.css`) no gustaba a Aoshi «en general». Al
preguntarle qué le chirriaba marcó las cuatro cosas:

1. **Es una caja**: un rectángulo con `border: 1px solid var(--cae-outline)` flotando sobre un
   escritorio que por lo demás es figuras y fondo.
2. **Parece un CV**: filas con línea encima, dato a la izquierda y valor a la derecha.
3. **No tiene jerarquía**: pastilla, «Freelancer», ubicación y dos filas pesan casi igual.
4. **Dónde está** (arriba a la derecha, compitiendo con la columna de cifras). *Esta la retiró
   después de ver alternativas: la tarjeta se queda donde estaba.*

Además, el spec de B1 preveía para el widget una entrada propia («se dibuja el borde», un trazo
sobre un `<rect>`) que **nunca llegó al código**: hasta el 2026-09-05 el widget aparecía de golpe, y
ese día se le puso un fundido simple como parte del arreglo del hero (`667405a`). Y Lidia dejó dos
hallazgos abiertos sobre esta tarjeta: mezcla una fila de estudios y una de experiencia sin nada que
las distinga, y la disponibilidad se anuncia dos veces (pastilla de la barra y tarjeta).

**El texto no cambia**, salvo un literal: Aoshi sustituye «Freelancer» por «Full Stack Developer».

## Lo que se probó y se descartó (registro del brainstorming, en el visual companion)

Se enseñaron nueve maquetas vivas con la piel real del tema (tokens del motor de color con deslizador
de hora, fuentes reales, GSAP), en tres vueltas:

- **Vuelta 1, sin caja y arriba a la izquierda**: una línea de estado (texto apoyado en el
  escritorio), una pegatina (el texto dentro de una figura de Material 3) y un carril (los datos
  como cronología sobre una línea vertical). **Rechazadas las tres**: ideas de interfaz de sistema,
  sin presencia ni tesis tipográfica. Aoshi pidió «un objeto del escritorio con presencia» y «algo
  vivo», «creatividad pero nada fuera de la temática».
- **Vuelta 2, widgets de Pixel a tamaño real**: «De un vistazo» (losa de 600×250 con figura
  morfante y chips), «La rueda de la hora» (losa cuadrada con el anillo de las 24 horas pintado con
  los matices del tema y una aguja en la hora del visitante) y «El grupo» (dos losas). Aoshi:
  «están mejor, pero no deben ser tan grandes, podemos dejarlo del lado derecho; no tan
  extravagantes, mantener el espíritu del original». **La rueda de la hora queda anotada** como la
  idea más propia del tema (hace visible por qué el escritorio tiene ese color a esa hora) por si
  algún día el tema quiere un widget de reloj.
- **Vuelta 3, la tarjeta original bien resuelta**: superficie tonal sin borde, un primero claro,
  luz viva, dos columnas fechadas, capa de estado, entrada que brota de la luz. Tres acentos vivos en
  la cabecera (solo la luz / una figura pequeña / la rueda pequeña) — **elegida la figura pequeña** —
  y tres jerarquías (la disponibilidad manda / lo que hace ahora / quién y luego todo) — **elegida
  «quién y luego todo»** — y tres tamaños del primero con el literal nuevo — **elegido 27 px en una
  línea** (medido con `Range`: 256 px de texto en 272 px de caja).

## La tarjeta

Mismo sitio (`top: 30px; right: 48px`), mismo ancho (316 px), mismo DOM de fuente (`hero.ts`
sigue construyéndola con literales de `content.ts`; ver «Anti-mock»).

```
┌──────────────────────────────────────────┐
│ AHORA MISMO                       ✿ 40px │   ← rótulo mono + figura M3 viva (primary-container)
│                                          │
│ Full Stack Developer                     │   ← Fraunces 27px, el único primero
│ Caracas, Venezuela · Desde 2021          │   ← 13px, on-surface-variant
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │   ← filete al 45% de outline (único filete)
│ 10.º SEMESTRE          AGO 2025 — MAY 2026│   ← mono 9,5px, la fecha como etiqueta
│ Ingeniería de          Telefónica        │   ← 12,5px, wght 500
│ Sistemas               Venezuela         │
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│ (● Disponible para proyectos)            │   ← pastilla de azufre, la luz respira
└──────────────────────────────────────────┘
```

### Orden y jerarquía (decisión: «quién, qué hace, estado»)

1. Cabecera: rótulo «Ahora mismo» (`.cae-whd`, como hoy) y, a la derecha, la figura viva.
2. `identity.now` — «Full Stack Developer» — en Fraunces, **27 px**, una línea, `white-space:
   nowrap`. Es el único primero de la tarjeta.
3. `identity.location · Desde identity.since`, 13 px, `--cae-on-surface-variant`.
4. Dos columnas, no dos filas: cada una con la **fecha como etiqueta mono encima** y el nombre
   debajo. Izquierda: el semestre (extraído del paréntesis de `education[0].period`, como hoy) y
   `education[0].degree`. Derecha: `experience[0].period` y `experience[0].organization`. Esto
   responde al hallazgo de Lidia: ya no son dos filas iguales, son dos cosas distintas fechadas.
5. Al pie, sola, la pastilla `identity.availability` con la luz.

### Superficie (decisión: «espíritu del original», sin caja)

- `background: var(--cae-surface-container-high)` (el escalón de la barra y el dock; hoy la tarjeta
  usa `surface-container`, que es el fondo de la ventana en las otras escenas).
- **Sin `border`.** Radio 24 px (el que ya tiene).
- Sombra ambiental por esquema, con el comentario de contra qué se midió: día
  `0 14px 36px -20px rgb(0 0 0 / 0.22)`, noche `0 14px 36px -20px rgb(0 0 0 / 0.5)`. Selector de
  noche: `:root[data-theme="caelestia"][data-cae-esquema="noche"]`, el que ya usa el cajón de Obra.
- Los dos filetes interiores (encima de las columnas y encima de la pastilla): 1 px en
  `color-mix(in oklch, var(--cae-outline) 45%, transparent)`.

### Tipografía

- Nuevo token `--cae-display-axes-ficha: "opsz" 60, "wght" 700, "SOFT" 0, "WONK" 1` para el
  primero. No se reutiliza `--cae-display-axes-texto` (`opsz 9`): a 27 px el tamaño óptico 9 da
  remates pesados y contraste corto; el 60 es el que ya usa el título del cajón de Obra
  (`.cae-obra-drawer-title h3`, hoy como literal — candidato a adoptar este token, fuera de alcance).
- Rótulo y etiquetas de fecha: Martian Mono 9,5 px, tracking 0,04 em (fechas) y 0,2 em (rótulo,
  como hoy).
- Nombres de estudios y empresa: Hanken Grotesk 12,5 px, `wght 500`, `line-height 1.25`.
- Ubicación: Hanken 13 px.

### Lo vivo

Tres cosas, y solo tres. Todas bajo `prefers-reduced-motion: no-preference`; con movimiento reducido
la tarjeta es estática y ya aterrizada.

1. **La luz respira.** El punto de la pastilla lleva un anillo (`::after`) que crece y se apaga en
   2,4 s en bucle. Es la única animación continua de texto.
2. **La figura morfa con la hora y mira al cursor.** Un `<span>` de 40×40 en la cabecera, fondo
   `--cae-primary-container`, recortado con `clip-path: polygon()` de **240 vértices** (la cuenta de
   `src/utils/figurasM3.ts`; con distinta cuenta el navegador no interpola). Su forma cambia con la
   hora del visitante como las figuras del fondo: familia de lóbulos que avanza a lo largo del día
   (5 a 9 lóbulos) y una fase que gira despacio (bucle de 24 s, `ease: none`). Al mover el cursor
   dentro de la tarjeta, la figura se inclina hacia él (`rotateX/rotateY` hasta ±18°,
   `transformPerspective 300`, 0,4 s) y vuelve al salir (0,6 s).
3. **Capa de estado al rozar.** Un `::after` con `--cae-primary` al **6 %** (Material 3 pide 8 %
   para hover; aquí 6 porque el fondo ya es tonal — medido contra `surface-container-high` en los
   dos esquemas). El levantamiento (`y: -2`) y el apartar el fondo **ya los hace `montarRoce`**: no
   se duplican.

### La entrada: brota de la luz

Sustituye al fundido del paso 11 de `montarEntrada` (`caelestia.titulo.ts`). Sigue en la misma
timeline, en la misma posición (tras las cifras, `"-=0.2"`):

1. La tarjeta arranca con `clip-path: circle(0 at X Y)`, donde X, Y es el centro de la luz de la
   pastilla **medido en ese instante** (misma trampa que el aterrizaje del trazo: medir antes da la
   caja colapsada).
2. El círculo crece hasta 420 px en 0,85 s, `power3.inOut`; al terminar se limpia el `clip-path`
   inline para que no quede una máscara viva.
3. Los hijos directos de la tarjeta se posan (`opacity 0→1, y 6→0`, 0,3 s, stagger 0,06) solapando
   0,5 s con el círculo.
4. La figura nace como círculo (amplitud 0) y florece a su forma en 0,8 s, `back.out(1.4)`, en
   paralelo con el punto 2.

El estado inicial de todo esto lo escribe `montarEntrada` con `gsap.set` **antes** de retirar
`js-cae-entrada`, como el resto del hero (ver `667405a`): la tarjeta sigue en la lista de
`visibility: hidden` de esa clase.

## El literal nuevo

`identity.now` pasa de `"Freelancer"` a `"Full Stack Developer"` (con espacio, como el propio sitio
escribe «Full stack» en `identity.subheadline`). Se pinta en **cuatro** sitios y cambia en los
cuatro, que es lo correcto: la tarjeta (`hero.ts:151`) y tres de la ficha `neofetch` de «Quién soy»
(`about.ts:99`, `about.ts:329`, `about.ts:461`: pasará a leerse «Ahora · Full Stack Developer»).
Ningún arnés compara ese literal salvo `measure-caelestia-titulo.py::widget`, que lo lleva escrito a
mano y debe pasar a leerlo (ver gates).

## Anti-mock

Todo lo que pinta la tarjeta existe en `content.ts`: `identity.availability`, `identity.now`,
`identity.location`, `identity.since`, `education[0].degree`, el semestre extraído del paréntesis de
`education[0].period`, `experience[0].organization`, `experience[0].period`. Ningún dato derivado
nuevo. La regla del spec de B1 sigue: si no está en `content.ts`, no se pinta.

## Fuera de alcance

- Móvil (390 px): fuera, como en todo B1.
- Cambiar la posición o el ancho (Aoshi lo retiró).
- La rueda de la hora (anotada como idea, no se construye).
- Adoptar `--cae-display-axes-ficha` en el título del cajón de Obra.
- El hallazgo de Lidia sobre la disponibilidad duplicada (barra + tarjeta): se mantiene, la pastilla
  es el estado de la tarjeta y la de la barra es el estado del sistema.

## Ficheros

- `src/data/content.ts`: el literal.
- `src/sections/hero.ts`: el DOM de la tarjeta (cabecera con figura, columnas, pastilla al pie).
- `src/themes/themes.css`: bloque `.cae-widget` reescrito; token nuevo; sombra por esquema; capa de
  estado; `@media (prefers-reduced-motion: no-preference)` para la luz.
- `src/themes/caelestia.titulo.ts`: `montarEntrada` (paso 11: brota de la luz; estado inicial),
  y un módulo pequeño para la figura viva (morfa con la hora, mira al cursor) montado desde
  `montarRoce` o al lado, con `destroy()` que mate su tween en bucle.
- `scripts/measure-caelestia-titulo.py`: gate `widget` ampliado (abajo).

## Los gates (`measure-caelestia-titulo.py`, familia `widget`)

Cada uno tiene que verse en **rojo** contra el código actual antes de aceptarse.

1. **Anti-mock, con el literal leído.** La lista `esperado` deja de llevar `"Freelancer"` a mano:
   el arnés lee `src/data/content.ts` como texto y saca `now: "..."` con una expresión regular
   (falla si no la encuentra), igual que hace con el resto de literales que no puede importar.
   Rojo contra el código actual porque, con el literal ya cambiado en `content.ts`, el widget viejo
   sigue diciendo lo que dice `content.ts` — así que este gate por sí solo no distingue; el que
   distingue es el 4 (orden) y el 2 (sin caja). Se acepta que el 1 sea de regresión, no de cambio.
2. **Sin caja.** `borderTopWidth === "0px"` y `backgroundColor` igual al de `.cae-bar`
   (`surface-container-high`), distinto del de `#hero`.
3. **Jerarquía.** El `font-size` computado de `identity.now` es el mayor de la tarjeta y cabe en
   una línea: medido con `Range`, ancho ≤ ancho de la caja − 44 px de padding, y una sola
   `getClientRects()`.
4. **Orden en el DOM.** Los hijos directos, en orden: cabecera, primero, ubicación, columnas,
   pastilla. Las columnas son dos (`grid-template-columns` con dos valores) y cada una lleva la
   etiqueta mono antes del nombre.
5. **La luz respira** con movimiento: `getAnimations()` del `::after` del punto (o `animationName`
   computado) distinto de `none`; con `reduced_motion="reduce"`, `none`.
6. **La figura vive.** Existe, su `clip-path` es un `polygon()` de 240 pares, y **cambia** entre dos
   lecturas separadas (anclado a estado: leer, esperar a que cambie hasta 5 s, fallar si no).
   Con movimiento reducido no cambia.
7. **La entrada brota de la luz.** En la misma `evaluate()` en que se muestrea el arranque de la
   entrada (el gate `entrada` ya muestrea desde el `commit`), la tarjeta tiene un `clip-path`
   `circle(` con radio < 20 px en algún momento antes de aterrizar, y al aterrizar no tiene
   `clip-path` inline. Con movimiento reducido: nunca hay `clip-path`.
8. **Contraste en las 24 horas.** Se añaden al barrido los pares reales de la tarjeta: primero y
   ubicación sobre `surface-container-high`, etiqueta mono sobre `surface-container-high`,
   texto de la pastilla sobre `--cae-anchor`, **con la capa de estado puesta** (hover real con
   `page.hover()`, nunca un `MouseEvent` sintético). AA en todos.

## Registro de implementación

Cada gate se vio en rojo contra el código anterior antes de aceptarse. Lo que rompía cada uno,
literal, y las medidas finales:

- **Task 1 — literal `identity.now`.** Rojo esperado y visto: `FALLO el widget dice 'Freelancer',
  literal de content.ts` (el arnés llevaba el literal viejo a mano). Verde tras leer `content.ts`
  con regex: `OK el widget dice 'Full Stack Developer', literal de content.ts`. Se comprobó además
  que el literal nuevo llega a la ficha `neofetch` de «Quién soy» sin tocar `about.ts`.

- **Task 2 — orden y columnas.** Rojo: el DOM viejo (`cae-whd`, `cae-pilla`, `cae-wnow`, `cae-wsub`,
  `cae-wfila`, `cae-wfila`) no cumplía ni el orden de hijos ni las dos columnas fechadas. Verde tras
  reescribir `hero.ts`: hijos directos en orden `cae-wcab`/`cae-wnow`/`cae-wsub`/`cae-wdos`/`cae-wpie`,
  y con el CSS de la Task 3 puesto, `grid-template-columns` midió **`117.766px 140.234px`** (dos
  pistas, ninguna igual — la fecha por columna no reserva el mismo ancho que el nombre).

- **Task 3 — superficie, tipografía, luz.** Rojo: borde `1px`, fondo `surface-container` (el de la
  ventana, no el de la barra), tamaño óptico `opsz 9` y el anillo de la luz en `none` (no respiraba).
  Verde: `borde 0px`; fondo `oklch(0.925 0.026 255)` — igual al de `.cae-bar`, distinto del de
  `#hero`; el primero mide **27px**, es el texto más grande de la tarjeta y **cabe en una línea: 256
  de 272px de caja** (medido con `Range`, no con la caja de bloque del `<span>`); ejes
  `"opsz" 60, "wght" 700`; el anillo anima como `caeLuzRespira` y con movimiento reducido es `none`.

- **Task 4 — la figura viva.** Rojo: `clip-path: none` en `.cae-wfig` (0 pares, sin figura). Verde:
  `polygon()` de **240 pares** siempre, cambia de forma sola en el barrido con tope de 6s (anclado a
  estado, no a un tiempo fijo), y con movimiento reducido queda fija tras una sola pintura.

- **Task 5 — la entrada brota de la luz.** Rojo: la tarjeta entraba con un `fromTo` de opacidad, sin
  ningún `circle(` en su `clip-path` durante el muestreo. Verde: se registró un `circle()` con radio
  mínimo de **0.0px** (arranca en el punto de la luz y crece hasta 420px, `power3.inOut`), y al
  aterrizar la tarjeta **no** conserva `clip-path` inline (`''`). Con movimiento reducido nunca
  aparece `clip-path`.

- **Task 6 — contraste con la capa de estado.** Sabotaje (`.cae-wfecha { color: var(--cae-outline) }`,
  build, correr): **`FALLO peor par de la tarjeta fecha a las 06:30: 1.19:1 (piso AA 4.5)`** — la
  `outline` de noche cae muy por debajo de AA, el mismo fallo real que ya se pagó en B4. Revertido,
  build, correr: **`OK peor par de la tarjeta ubicacion a las 12:30: 5.01:1 (piso AA 4.5)`**. El
  barrido de las 24 horas con hover real (`pg.hover`, nunca un `MouseEvent` sintético) y la capa de
  estado apilada sobre el fondo antes de medir dejó el arnés completo en **0 fallo(s)**.

### Verificación final (Task 6, Step 2)

- `npm run build`: exit 0. `npm run lint`: exit 0.
- `measure-caelestia-titulo.py`: **0 fallo(s)** (peor par 5.01:1, ver arriba).
- `measure-caelestia-hora.py`: `OK — motor de color de Caelestia en verde` (el shell de la fase A
  sigue intacto).
- `measure-caelestia-quien-soy.py`: `TODO VERDE` (peor par 5.72:1, la ficha con el literal nuevo).
- `scripts/verify.py --url http://127.0.0.1:4193`: `TODO OK — 12 fallos conocidos, 0 nuevos
  (verify-baseline.json)` — la línea base no cambió, ningún fallo nuevo, ninguno resuelto sin
  quitar de la base.
- Capturas 1440×900 de `?theme=caelestia` a las 13:00 y 23:00, y de `?theme=vice` y `?theme=hyprland`:
  las cuatro con cero errores de consola/`pageerror`. Vice e Hyprland se ven igual que antes de la
  Task 6 (`.cae-widget` sigue sin pintarse fuera de Caelestia).

### Hallazgo abierto, no arreglado en esta tarea: 1366×768

A esa resolución (portátil habitual, fuera del viewport oficial 1440×900 del tema) la pastilla
`.cae-pilla` se solapa con la primera fila de la columna de cifras (`.cae-statcol`), medido con
`getBoundingClientRect()`:

```
widget:  { top: 98,  left: 988,  right: 1304, bottom: 366, width: 316, height: 268 }
statcol: { top: 344, left: 1136, right: 1304, bottom: 588, width: 168, height: 244 }
overlap: true
```

La tarjeta no cambia de posición/ancho con el viewport (ambos son `absolute` con coordenadas fijas
en `px`), así que por debajo de cierta altura de página la tarjeta y la columna de cifras siempre
van a coincidir en Y. No estaba en el alcance de esta tarea arreglarlo — el spec fija el viewport
oficial en 1440×900 y deja 390px fuera de alcance, pero no dice nada de 1366×768 — así que queda
registrado como hallazgo, no como regresión introducida por el rediseño (la tarjeta ya vivía en esa
misma posición antes del rediseño de la Task 6).

### Hallazgo cerrado, repaso de interfaces 2026-09-06: 1366×768

El hallazgo de arriba (dejado abierto al cerrar la Task 6) es el hallazgo A del repaso de
interfaces de Vera. Arreglo: un `@media (max-height: 800px)` en `.cae-widget`/`.cae-wcab`/
`.cae-wsub`/`.cae-wdos`/`.cae-wpie` (mismo patrón que `.cae-obra-drawer`/`.cae-obra-prose p` un poco
más arriba en `themes.css`) que aprieta paddings y márgenes entre filas sin tocar `.cae-statcol`
(es de B1) ni el tamaño del primero (bajarlo de 27 a 24px rompía la aserción `tarjeta_superficie`
de que el primero es el texto más grande de la tarjeta y mide `>= 26px` — esa aserción corre con la
MISMA ventana de 748px de alto del resto del arnés, así que la media query también se activa ahí, a
propósito, y se verificó que sigue en verde).

Medido antes/después con `getBoundingClientRect()` a 1366×768, 13:00:

```
antes:   widget.bottom=366  statcol.top=344  hueco=-22px (solape)
despues: widget.bottom=326  statcol.top=344  hueco=18px
```

A 1440×900 no cambia nada (`widget.bottom=366` en los dos casos, `max-height: 800px` no se activa
a 900 de alto).

Gate nuevo `tarjeta_portatil` en `measure-caelestia-titulo.py` (contexto/página propios con
viewport 1366×768, el resto del arnés sigue usando 1412×748): visto en rojo contra el CSS anterior
— `FALLO a 1366x768 hay >=8px entre el pie de la tarjeta y la columna de cifras
(widget.bottom=366, statcol.top=344, hueco=-22px)` — y en verde tras el arreglo — `OK a 1366x768
hay >=8px entre el pie de la tarjeta y la columna de cifras (widget.bottom=326, statcol.top=344,
hueco=18px)`.

## Gates de crítica

Al cerrar: `lidia-naive-tester` (¿se lee en dos segundos qué es y si está disponible?) y
`vera-art-director` (jerarquía, rejilla 4/8, tokens). Como en B1, un BLOCK de Vera con P0 se
arregla; los P1 se registran.
