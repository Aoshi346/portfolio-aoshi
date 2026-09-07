# Caelestia B6 — el escritorio en el teléfono y en la tableta

Estado: implementado
Fecha: 2026-09-07
Rama de trabajo: `design/caelestia-movil` (worktree `portfolio-aoshi-movil`), desde `main` (`1f41e6c`)
Plan: `docs/superpowers/plans/2026-09-07-caelestia-movil.md`
Origen: Aoshi miró Caelestia en su teléfono al cerrar el repaso de interfaces
(`2026-09-05-caelestia-repaso-interfaces.md`) y las escenas 1 a 4 no se veían. No es una
regresión: B1, B2, B3 y B4 dejaron el móvil fuera de alcance a propósito. Aoshi reabre esa
decisión. Brainstorming en el visual companion (sesión `.superpowers/brainstorm/3734089-1788732735`,
pantallas `01-ley-movil.html`, `02-titulo-movil.html`, `03-titulo-aire.html`).

---

## Qué se diseña y por qué

Caelestia es un escritorio: cinco workspaces en un carril horizontal, cada uno una aplicación
pensada para una ventana de 1412x748. Por debajo de 900 px de ancho ninguna de las cuatro
primeras cabe: Título justifica su titular a 1080 px, Quién soy desborda 847 px de ancho sobre 362,
Obra mide 1316 y Stack 1364. Contacto (B5) sí entra en 390 px desde su propia fase.

**Lo que B6 decide es qué hace un workspace cuando la ventana es un teléfono.** Se probaron tres
respuestas en el companion y Aoshi eligió la primera:

- **A. La ley se relaja: cada workspace se desplaza por dentro.** Elegida.
- B. La ley se mantiene: cada escena se resume a lo que cabe, con un segundo nivel de navegación
  (flechas, «+3», acordeón, «Ficha»). Descartada: cuatro dispositivos nuevos que aprender y
  contenido escondido en cada escena.
- C. En móvil Caelestia deja de ser escritorio: una sola página con scroll. Descartada: el tema
  deja de ser lo que es justo en el formato donde más gente lo verá.

## La ley en móvil

La ley de la fase A dice que **un workspace no se desplaza, se cambia**. En móvil se añade una
excepción de formato, no una derogación:

- **Dos bandas, no una** (ampliación del 2026-09-07, a petición de Aoshi: «arregla móvil y
  tablets en la misma corrida»):
  - **Compacta, hasta 900 px de ancho** (`@media (max-width: 900px)`, el corte que ya usan ocho
    reglas de `themes.css`): teléfono (390) y tableta vertical (768, 820). Una columna.
  - **Media, de 901 a 1365 px**: tableta apaisada (1024, 1180, 1194) y portátil estrecho. NO es
    una columna: hay ancho de sobra y poca altura, así que conserva la composición de escritorio
    y lo que cede es el tamaño de las piezas fijas.
  De 1366 en adelante manda el escritorio y no cambia nada: ese es el ancho que el proyecto ya
  trata como cordura de portátil.

  **Qué está roto en la banda media, medido el 2026-09-07** (`scrollWidth` contra `clientWidth`
  del workspace, y solape real de cajas):

  | Ancho | Título | Quién soy | Obra | Stack | Contacto |
  |---|---|---|---|---|---|
  | 1024 | cabe | cabe | 1160/996 | 1364/996 | el sello tapa la frase |
  | 1180 | cabe | cabe | 1212/1152 | 1364/1152 | el sello tapa la frase |
  | 1280 | cabe | cabe | cabe | 1364/1252 | el sello tapa la frase |

  Título y Quién soy no necesitan nada en la banda media: solo hay que comprobarlo. Obra y Stack
  la necesitan en sus tareas. Contacto la resuelve su propia rama (`fix/caelestia-movil-contacto-dock`),
  fuera de B6, porque B5 la dejó cerrada.
- Por debajo del corte, **el carril sigue igual**: cinco workspaces, se cambian con las pastillas
  de la barra, los inactivos `inert`, el documento no se desplaza nunca.
- **Cada workspace se desplaza por dentro**, en vertical: `overflow-y: auto`,
  `overscroll-behavior: contain` (el tirón no sale al documento), sin barra de desplazamiento
  visible. Un workspace se abre siempre por su principio: al cambiar de escena, el desplazamiento
  interior vuelve a cero.
- El panel de cada workspace ocupa el ancho entero menos 14 px de margen por lado y la altura de
  hoy (viewport menos barra y dock). El fondo generativo sigue debajo de todo.

## El shell por debajo de 900 px

- La barra conserva las cinco pastillas con número (hoy ya oculta las etiquetas a 390) y el reloj.
- El dock no cambia.
- La marca «caelestia» de la esquina inferior derecha **no se pinta**: pisaba el dock a 390 px
  (arreglo en curso en `fix/caelestia-movil-contacto-dock`; B6 lo hereda y lo generaliza al corte
  de 900).
- Contacto queda como la dejó B5 más ese arreglo. B6 no la toca.

## Las cuatro escenas

Regla común, heredada de B3 y B4: **lo que no sirve en móvil se oculta por CSS bajo
`[data-theme="caelestia"]`, no se bifurca en TypeScript.** El DOM que comparten los tres temas no
se toca. Todo texto sale de `content.ts` literal; ningún dato derivado nuevo.

### Título: «Silencioso» (maqueta 6, elegida entre seis)

Cabe entero, **sin desplazamiento**. Se probaron antes tres versiones con el titular justificado a
la medida del teléfono, cifras y tarjeta en la misma pantalla (maquetas 1-3) y dos con aire y
estampas (4 y 5); Aoshi las rechazó por sobrecargadas y eligió la callada.

- **Firma arriba**: el nombre en Fraunces a `--cae-display-axes-cartel`, 18 px; debajo, la meta
  (`identity.subheadline`) en mono.
- **El titular a la izquierda, sin justificar**, con los tres cortes de escritorio (`Construyo
  sistemas / que aguantan producción, / no demos.`): las dos primeras líneas a un paso moderado y
  «no demos.» a un paso grande. Los tamaños son **tokens de la escala** cambiados por `@media`,
  nunca un `clamp()` continuo (regla del proyecto). Orientación de la maqueta: ~26 px y ~64 px.
- **Tres líneas de prosa** con lo que la tarjeta dice en escritorio: `identity.now` en negrita y
  `identity.location`; `education[0]` con el «10.º semestre» que ya se saca del paréntesis de su
  `period`; `experience[0]` con su periodo. Hanken, 13 px, interlineado 1,7,
  `--cae-on-surface-variant` con las piezas fuertes en `--cae-on-surface`.
- **Las cuatro cifras como una línea de mono** (dos por renglón), el número en Fraunces a
  `--cae-display-axes-ficha` 15 px y el rótulo en mono mayúsculas. Son los mismos `stats` de
  escritorio.
- **La pastilla de disponibilidad** (`identity.availability`) al final.
- **La tarjeta «Ahora mismo» no se monta**: ni su figura viva, ni su luz, ni su brote. Tampoco la
  columna de cifras de escritorio. Se ocultan con `display: none` bajo el corte; `montarFiguraViva`
  y la parte de la timeline que las anima no corren si el elemento no pinta (`getClientRects`
  vacío), para no animar lo que no se ve.

### Quién soy

La salida de `neofetch` en una columna, **con desplazamiento**: el comando tecleado; el retrato con
su squircle (la misma figura de 240 vértices, 96 px) y el nombre en cartel a su lado; el correo
debajo; el filete (medido con `Range`, como en B2); y los seis campos `clave: valor` apilados, cada
uno en su renglón. El morfado del retrato al rozar no existe en táctil y no se sustituye.

### Obra

**Carrusel horizontal con imán** (`scroll-snap-type: x mandatory`) de las cinco tarjetas a 250 px
de ancho, con puntos de posición debajo. **La tarjeta centrada es la elegida**, sin pulsar: el
carrusel dispara la selección al asentar (evento `scrollend`, con `scroll` + estado como reserva
donde no exista). El cajón, debajo, con la ficha entera a una columna (kicker, título, lead, nota
de privado, Problema y Solución). La escena se desplaza en vertical. La inclinación alterna de las
tarjetas no se pinta en móvil.

**En la banda media (901-1365)** la fila de cinco no cabe (1316 px de fila contra 996 útiles a
1024): las tarjetas se estrechan a la medida que quepa manteniendo su proporción 16:10, y si con
cinco no llegan a un tamaño legible, la fila se convierte en el mismo carrusel con imán de la
banda compacta. El cajón sigue debajo, a dos columnas en vez de tres.

### Stack

Las cuatro bandas apiladas, cada una con su rótulo, su cuenta y sus piezas a **cuatro columnas de
56 px** (las 23 figuras de 240 vértices, las mismas tablas de `figurasM3.ts`). La ficha de la pieza
elegida en cabecera de la escena. **Rozar no existe en táctil: tocar elige**, y el foco llega a lo
mismo. Se desplaza en vertical.

**En la banda media (901-1365)** las cuatro bandas de escritorio miden 1364 px fijos y no caben a
ningún ancho de tableta apaisada: la calle del rótulo (158 px) y el módulo (142 px) dejan de ser
valores fijos y pasan a repartirse el ancho disponible, con las 23 piezas siempre en pantalla y
todas del mismo tamaño (la ley de B4: el tamaño no codifica nada).

## Las entradas: un gesto por escena, por debajo de 900 ms

Elegida la opción B entre tres (mantenerlas enteras / versión corta / ninguna). Por debajo del
corte, cada escena conserva **un solo gesto reconocible** y pierde sus capas secundarias:

| Escena | Gesto que queda | Lo que se pierde en móvil |
|---|---|---|
| Título | `whoami` tecleado | trazado de la firma, brote de la tarjeta, volteo de cifras |
| Quién soy | `neofetch` tecleado | la entrada por capas de la ficha |
| Obra | la caída, solo de la tarjeta visible y sus vecinas | la caída de las cinco, las cuatro capas del cajón |
| Stack | la instalación en una sola onda | la onda por territorios |

Cada una conserva el disparador que ya tiene (Obra y Stack escuchan `caelestia:workspace`; Título
arranca al montar, Quién soy con su propio mecanismo: no se unifican aquí), duran menos de 900 ms
declarados, y con `prefers-reduced-motion` no corren ninguna (aterrizan directas), incluidos los
pseudo-elementos, que `*` no alcanza (trampa de B2).

## Fuera de alcance

- De 1366 px en adelante: el escritorio, que no se toca.
- Apaisado en teléfono.
- Contacto (B5, ya en alcance) y el cursor (en táctil no se descarga).
- Cambiar contenido: la tabla estudios/trabajo sin rótulo y la pastilla que parece botón (deuda
  registrada de la tarjeta) no se resuelven aquí; en móvil la tarjeta no existe.
- Las capturas reales de Obra (siguen «CAPTURA PENDIENTE»).

## Ficheros

- `src/themes/themes.css`: el bloque `@media (max-width: 900px)` de Caelestia (ley, shell, las
  cuatro escenas).
- `src/sections/hero.ts`: el bloque de prosa y la línea de cifras de Título (DOM nuevo, oculto en
  escritorio).
- `src/themes/caelestia.titulo.ts`, `caelestia.ficha.ts`, `src/components/caelestiaObraEditorial.ts`,
  `src/components/caelestiaCreditosBandeja.ts`: la rama corta de cada entrada, el carrusel de Obra
  y el toque de Stack.
- `src/components/caelestiaShell.ts`: volver a cero el desplazamiento interior al cambiar.
- `scripts/measure-caelestia-movil.py`: nuevo.
- `.claude/rules/verification.md`: fila nueva. `CLAUDE.md`: bloque de B6 al cerrar.

## Los gates (`scripts/measure-caelestia-movil.py`)

Contra el build de producción servido. Contexto móvil real: 390x844, `device_scale_factor` 2,
`is_mobile`, `has_touch`; y tableta 768x1024. En Caelestia el hash no cambia de workspace: se
pulsa la pastilla. **Cada familia se ve en rojo contra su sabotaje antes de aceptarse.**

1. **La ley.** El documento no se desplaza a ningún ancho; cada workspace activo **responde a un
   scroll programático interior** (no `scrollHeight === clientHeight`, que B5 demostró mentiroso
   con `transform`); al cambiar de escena el desplazamiento interior vuelve a cero.
2. **Sin desbordamiento horizontal** en las cinco escenas: `scrollWidth === clientWidth` del
   workspace (hoy 847, 1316 y 1364 contra 362).
3. **Título silencioso.** La tarjeta y la columna de escritorio no pintan (`getClientRects` vacío,
   no `display` leído); la prosa y la línea de cifras son literales de `content.ts` (mismo gate
   anti-mock que ya lee `identity`, `education`, `experience` y `stats`); «no demos.» es la línea
   más grande; el bloque entero cabe sin desplazamiento; la figura viva no se monta.
4. **Obra.** Las cinco tarjetas alcanzables (cada una llega al centro con un `scrollTo` del
   carrusel); la centrada es la elegida y el cajón cambia con ella.
5. **Stack.** Tocar elige (`tap` real, nunca un `MouseEvent` sintético); las 23 piezas dentro de
   la caja; los cuatro rótulos pintados (contar nodos no es contar lo que se ve, trampa de B4).
6. **Entradas cortas.** Cada escena dispara su gesto al llegar al workspace y aterriza, **anclado
   a estado**: se lee el primer fotograma sincrónico del gesto en el mismo `evaluate()` que el
   cambio (técnica de B5), nunca un cronómetro; duración declarada < 900 ms; con movimiento
   reducido ninguna corre, pseudo-elementos incluidos.
7. **Contraste** de los pares nuevos (prosa, línea de cifras, rótulos de banda, puntos del
   carrusel) en los dos esquemas, apilando fondos translúcidos hasta el primero opaco.
8. **Tableta.** Las familias 1 a 3 repetidas a 768x1024 (banda compacta) y, para la banda media,
   una familia propia a **1024x768 y 1180x820**: ninguna de las cinco escenas desborda en
   horizontal (`scrollWidth <= clientWidth`), las cinco tarjetas de Obra son alcanzables y las 23
   piezas de Stack están dentro de la caja. Título y Quién soy entran aquí solo como comprobación
   de no regresión: hoy ya caben.
9. **Escritorio intacto.** A 1440x900 los arneses de Título, Quién soy, Obra, Stack y hora siguen
   en verde sin tocar sus aserciones (se corren, no se asume).
10. **Consola** sin errores en todo el recorrido, en los dos contextos.

Además: capturas reales de las cinco escenas a 390x844 y 768x1024 en los dos esquemas,
`verify.py` con 0 nuevos, y los críticos `lidia-naive-tester` y `vera-art-director` sobre el
móvil antes de cerrar. Un arnés a la vez (la máquina ha muerto por OOM con tres).

## Gates de crítica

Al cerrar: Lidia (¿en el teléfono se entiende quién es y cómo contactar en dos segundos?) y Vera
(jerarquía, rejilla, tokens, y que el móvil sea el mismo tema que el escritorio). Un P0 se arregla
antes de cerrar; los P1 se registran.

---

## Registro de implementación

Rama `design/caelestia-movil`, worktree `portfolio-aoshi-movil`, sobre `main` (`1f41e6c`) más el
arreglo de Contacto de `fix/caelestia-movil-contacto-dock`, que entra fusionado dentro de esta
rama porque B6 lo necesita como base (la escena 5 era la única que ya declaraba 390 px en alcance
y aun así se rompía en teléfonos cortos y en tabletas).

### Lo que quedó construido

- **La ley (opción A).** El documento no se desplaza a ningún ancho; cada workspace se desplaza
  por dentro y vuelve a cero al cambiar de escena (`caelestia.choreography.ts`, dentro de `irA`:
  `if (destino !== origen) escenas[destino].scrollTop = 0;`).
- **Título silencioso.** Por debajo de 900 px no pintan ni la tarjeta «Ahora mismo» ni la columna
  de cifras ni la figura viva: en su lugar, `.cae-movil` con tres líneas de prosa, cuatro cifras y
  un pie. La rama corta se decide por `widget.getClientRects().length === 0` —lo que de verdad se
  pinta—, no por un ancho leído en TS.
- **Quién soy** en una columna, con el `neofetch` tecleado como único gesto.
- **Obra**, carrusel con imán: la tarjeta centrada es la elegida y el cajón la sigue. La centrada
  se resuelve con `getBoundingClientRect()` contra la pista, y se confirma con `scrollend` más un
  `scroll` con 120 ms de reposo (Safari no tiene `scrollend`).
- **Stack**, bandas apiladas; tocar elige; la instalación entra como una sola onda.
- **Tableta**: banda compacta (≤900) y banda media (901-1365) para Obra, Stack y Contacto, con
  sub-bandas por altura en Contacto.

### Las trampas pagadas

1. **Un gate tautológico que salía verde contra el fallo real.** «La cabecera no se parte en dos
   líneas» contaba `getClientRects().length` sobre un elemento flex: devuelve 1 se parta o no. El
   primer arreglo (un `Range` sobre el contenido) contaba 4 porque incluía el nodo oculto fuera de
   flujo. La versión buena mide la altura contra el `line-height` calculado.
2. **Un cronómetro disfrazado de gate.** «La entrada arranca tecleando» leía el comando 200 ms
   después del cambio de escena; al comprimir la entrada a 0,86 s se puso rojo contra un
   comportamiento correcto. Se cambió por un `MutationObserver` instalado ANTES del cambio, que
   afirma valores intermedios: con `dTecleo: 0` da 0 pasos (rojo) y con la tabla real, 6.
3. **Especificidad de CSS, cinco veces.** Las reglas de escritorio llevan una clase o un camino de
   más (`.contacto-bar[data-canal="acto"]`, `main[data-cae-track] > [data-scene="contacto"]`); una
   regla móvil sin ese peso pierde el desempate y no se aplica, en silencio. Se comprueba siempre
   con `getComputedStyle`.
4. **Un `replace` que aterrizó en el `@media` equivocado**, porque el mismo texto de regla existe
   en dos bandas. Se cazó grepeando el CSS **construido** (`dist/assets/*.css`), no el fuente.
5. **Un estilo en línea gana a cualquier `@media`.** `.cae-cred-fig` fijaba tamaño con
   `fig.style.width/height`, así que ninguna consulta de medios podía encogerla. Se sustituyó por
   una propiedad personalizada `--lado`.
6. **`offsetLeft` medido contra el carril de workspaces** y no contra la pista del carrusel: solo
   la tarjeta 1 llegaba nunca al centro. El error estaba en el código Y en el gate.
7. **La carga produce rojos falsos** (tres veces): el gate 13 de Fundido y dos familias del dino
   salieron rojos con dos previews y un arnés vivos, y verdes al repetirlos en vacío.
8. **`scrollHeight` miente**, y esta vez también en horizontal. Los gates 1 y 2 leían
   `scrollWidth`/`scrollHeight` del workspace: en Contacto el campo inundado es un `<span>` con
   `transform: scale(5,7)` dentro de un `overflow: clip`, e infla `scrollWidth` a 1835 y
   `scrollHeight` a 1629 sobre una escena que se ve entera. Los dos gates se reescribieron para
   medir el CONTENIDO —los nodos con texto propio o accionables contra el
   `getBoundingClientRect()` del workspace— con una excepción explícita para lo alcanzable
   deslizando (si un ancestro tiene `overflow` auto/scroll en ese eje, estar fuera de la caja no
   es un defecto: es el carrusel de Obra). Vistos en rojo con `.contacto-lead` a 1400 px (+104 por
   la derecha) y con `.contacto-estado` a 400 px de margen (+282 por debajo).
9. **Un subagente corrió `pkill -9 -f chrome-headless-shell`** y probablemente mató el arnés de
   otra sesión. Prohibido explícitamente en todos los briefs posteriores.
10. **Los subagentes se quedan parados** esperando un proceso en segundo plano. La instrucción que
    lo evita: esperar POR PID dentro del MISMO comando de Bash, nunca terminar el turno esperando.

### Números finales

- `scripts/measure-caelestia-movil.py`: **10 familias, 123 comprobaciones, 0 fallos**, a 390x844,
  768x1024, 1024x768 y 1180x820.
- Peor par de contraste de B6: **6,43:1** (`.cae-mv-prosa` a las 13:00), piso AA 4,5.
- Contacto entra a 390x844, 390x740, 390x667, 390x620, 768x1024, 820x1180, 1024x768, 1180x820 y
  1440x900.

### Los gates de critica

`lidia-naive-tester` **7/10, cero P0**: en los tres formatos entiende quien es Aoshi, que hace y
como contactarlo, y Contacto se lleva el elogio explicito. `vera-art-director` **6,22/10, BLOCK**
sobre un gate de 7,5 — el mismo residual aceptado en Vice, el shell, B1 y B4.

**Los dos convergieron en el mismo P0, y era real:** en tableta apaisada (1024x768) el nombre de
Quien soy quedaba 12 px por debajo de la barra fija. La causa no estaba en B6 sino en la fase B2:
`[data-ficha="neofetch"]` centra con `justify-content: center` y con `height: 100%`, asi que en una
caja mas baja que su contenido el sobrante se reparte a los dos lados **y lo que sale por arriba no
lo alcanza nadie**. Se cambio a `safe center`, que cae a `start` solo cuando desborda (donde ya
cabia no mueve nada), y en la banda media la caja crece (`height: auto; min-height: 100%`) para que
el sobrante se alcance desplazando el panel. **El mismo fallo estaba en `main` sin B6**, en
portatiles corrientes: 11 px a 1366x768 y 35 px a 1280x720, los dos con el comando `~ $ neofetch`
metido bajo la barra. El arreglo los cubre.

De los P1 se cerro uno en la misma corrida: a 768 px las cinco pastillas se quedaban solo con el
numero. El corte estaba en 820 px y baja a 640: medido, a 641 los cinco nombres terminan en 502 y
el reloj empieza en 572, asi que caben con holgura y solo el telefono se queda con los numeros.

Quedan abiertos, anotados y no arreglados aqui:
- **La escala tipografica** (Vera, septima aparicion en el proyecto). Es deuda de todo el sitio, no
  de esta fase; arreglarla es una fase propia.
- **La entrada del titular** todavia tecleando a 1,5 s. Medido bajo `swiftshader`, donde el
  cronometro miente por diseno de la sandbox; pendiente de mirarlo en un telefono real.
- **La banda negra de 27 px** bajo el panel, en las tres escenas con panel desplazable y en los dos
  esquemas. No sale a 1440x900, no sale en Titulo ni en Contacto, **y sale igual en `main` sin
  B6** — solo bajo emulacion de movil/tableta, lo que apunta al compositor del headless. Pendiente
  de confirmar en un telefono real.
