# Caelestia B6 — el escritorio en el teléfono

Estado: pendiente de plan
Fecha: 2026-09-07
Rama de trabajo: `design/caelestia-movil` (worktree `portfolio-aoshi-movil`), desde `main` (`1f41e6c`)
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

- **Un solo corte: 900 px de ancho** (`@media (max-width: 900px)`, el que ya usan ocho reglas de
  `themes.css`). Cubre teléfono (390) y tableta vertical (768). De 901 a 1365 px no hay promesa
  nueva: sigue como hoy. Escritorio no cambia en nada.
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

### Stack

Las cuatro bandas apiladas, cada una con su rótulo, su cuenta y sus piezas a **cuatro columnas de
56 px** (las 23 figuras de 240 vértices, las mismas tablas de `figurasM3.ts`). La ficha de la pieza
elegida en cabecera de la escena. **Rozar no existe en táctil: tocar elige**, y el foco llega a lo
mismo. Se desplaza en vertical.

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

- De 901 a 1365 px de ancho: sin promesa nueva.
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
8. **Tableta.** Las familias 1 a 3 repetidas a 768x1024.
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
