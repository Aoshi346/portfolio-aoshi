# Caelestia · Título: el nombre en el centro

- **Fecha:** 2026-10-29
- **Estado:** diseño, pendiente de aprobación
- **Rama:** `design/titulo-nombre` (worktree `../portfolio-aoshi-titulo-nombre`)
- **Maqueta aprobada:** variante **B · Trazo, sin pastilla**, en el visual companion
  (`.superpowers/brainstorm/2113111-1793308751/content/titulo-entradas-v4.html`; el generador está
  en el scratchpad de la sesión y se copia a `docs/superpowers/maquetas/` al implementar).
- **Sustituye a:** la composición y la entrada de la fase B1 (`2026-08-26-caelestia-titulo`) y la
  tarjeta «Ahora mismo» (`2026-09-05-caelestia-ahora-mismo`).

## Intención

Aoshi quiere que la primera pantalla diga quién es y qué hace, sin nada más. Hoy la escena de
Título carga un eslogan («Construyo sistemas que aguantan producción, no demos.»), un antetítulo
con «Desde 2021», una columna de cuatro cifras y la tarjeta «Ahora mismo». Todo eso sale. Queda su
nombre, grande y en el centro, y debajo su rol en una frase llana. La persona que evalúa el
portfolio (una reclutadora no técnica, menos de 2 s) tiene que leer nombre y rol sin descifrar
nada.

La entrada actual (una terminal que teclea `whoami` y una firma trazada que aterriza en el
antetítulo con un desplazamiento) desaparece. La sustituye un gesto en el sitio: el nombre se
dibuja letra a letra con sus contornos reales de Fraunces, se rellena y se queda donde está.

## Decidido por Aoshi

1. **Nombre en el centro, rol debajo.** El rol es literal: «Desarrollador full stack en Caracas.»
2. **Fuera** el eslogan, «Desde 2021» del antetítulo, las cifras (desde 2021, 10.º semestre,
   5 proyectos, 1 en producción) en escritorio **y** en móvil, y la tarjeta «Ahora mismo».
3. **Entrada B · Trazo**, sin la pastilla «Disponible para proyectos».

## Lo que se ve

**Escritorio (ventana de la escena 1412 x 748 dentro de una página 1440 x 900).**

```
+--------------------------------- barra ---------------------------------+
|                                                                          |
|                                                                          |
|                     Aoshi Blanco Sanz          <- Fraunces cartel, t-9   |
|              Desarrollador full stack en Caracas.   <- Hanken, t-4        |
|                                                                          |
|                                                                          |
+---------------------------------- dock ----------------------------------+
```

- Nombre y rol centrados en los dos ejes dentro de la ventana de la escena, alineación centrada.
- **Nombre:** Fraunces con los ejes de cartel ya existentes, `--cae-display-axes-cartel`
  (`opsz 144, wght 900, SOFT 0, WONK 1`), tamaño `--t-9` (119,77 px), una línea, `line-height: 1`,
  color `--color-paper`. No hay que inventar tokens.
- **Rol:** Hanken Grotesk 400, `--t-4` (28,43 px), color secundario de la escena (el mismo token
  que hoy usa `.cae-meta`: `oklch(.47 .032 240)` de día, `oklch(.795 .008 37.5)` de noche, medidos).
- Separación nombre/rol: 22 px en escritorio, 14 px en móvil (la maqueta).

**Escalones por ancho** (decisión del implementador, marcada como tal). El nombre en una línea
mide 7,903 em (ancho 790,3 a tamaño 100), así que cada escalón elige el mayor token que cabe en la
ventana de la escena con aire a los lados:

| Ancho de página | Nombre | Tamaño | Ancho del nombre | Rol |
|---|---|---|---|---|
| ≥ 1101 px | una línea | `--t-9` (119,77 px) | 947 px | `--t-4` |
| 901–1100 px | una línea | `--t-8` (89,85 px) | 710 px | `--t-4` |
| 641–900 px (banda tableta del tema) | una línea | `--t-7` (67,4 px) | 533 px | `--t-3` |
| ≤ 640 px | dos líneas, «Aoshi» / «Blanco Sanz» | `--t-6` (50,52 px) | 263 px la más larga | `--t-3` |

Los cortes 900 y 640 son los que ya usa el tema; 1100 es nuevo y existe solo porque `--t-9` no
cabe por debajo. Siempre escalones discretos (`@media` que cambia un token por otro), nunca
`clamp()` continuo, por la regla de la escala tipográfica.

**Sin el bloque móvil «Silencioso».** Hoy, por debajo de 900 px, la escena muestra tres líneas de
prosa (rol, carrera, empresa), las cifras y la pastilla. Todo eso es contenido de la tarjeta y de
las cifras que Aoshi ha pedido quitar, así que sale también: en móvil se ve lo mismo que en
escritorio, nombre y rol.

## La entrada: B · Trazo

Una sola timeline, en este orden y con estos tiempos (los de la maqueta aprobada):

1. **Trazo.** Cada uno de los 15 glifos del nombre dibuja su contorno: `stroke-dashoffset` de 1 a 0
   con `pathLength="1"` (así cada glifo se dibuja entero midan lo que midan sus contornos), 760 ms,
   `cubic-bezier(.45,0,.25,1)`, escalonado 55 ms por glifo **de corrido por los 15 glifos**,
   también en móvil cuando el nombre va en dos SVG (la segunda línea sigue a la primera).
2. **Relleno.** A los 1.550 ms, `fill-opacity` 0→1 y `stroke-opacity` 1→0 a la vez, 420 ms,
   `ease-out`.
3. **Rol.** A los 2.100 ms, corte seco de izquierda a derecha: `clip-path: inset(0 100% 0 0)` →
   `inset(0 0 0 0)`, 400 ms, `cubic-bezier(.7,0,.2,1)`. Es el mismo gesto de corte que ya usa el
   tema; contraste de tiempos entre lo blando (trazo) y lo seco (rol).

No hay desplazamiento, ni aterrizaje, ni terminal. El nombre se dibuja en su sitio final.

**El nombre visible es el SVG.** Los contornos se generan a los mismos ejes del cartel
(`opsz 144, wght 900, SOFT 0, WONK 1`), así que el SVG relleno **es** el nombre en Fraunces; no se
cambia a texto vivo al final (no hay salto). Para lectores de pantalla y buscadores, el `<h1>`
lleva el texto real «Aoshi Blanco Sanz» en un elemento visualmente oculto y el SVG va
`aria-hidden`. El SVG se dimensiona con la caja real de sus glifos (`getBBox()`), en `em`, para
que herede el tamaño del token. En móvil son dos SVG, uno por línea, con la misma altura. Las
posiciones de cada glifo ya incluyen el avance del espacio (el generador suma el `hmtx` de cada
carácter, espacio incluido), así que la separación entre palabras sale de la fuente; para la
segunda línea basta con recortar el `viewBox` a sus glifos (comprobado en la maqueta).

**Contornos.** `scripts/gen-firma-paths.py` pasa a `EJES = {"opsz": 144, ...}` y se regenera
`src/themes/caelestia.firma.ts` (15 glifos, ancho 790,3 a tamaño 100). El script documenta el
procedimiento (venv con fonttools y la TTF variable de google/fonts). El fichero sigue
commiteado, sin descarga en tiempo de ejecución.

**Antes del primer pintado.** Se conserva el mecanismo de `js-cae-entrada` (main.ts la pone, la
entrada la retira en cuanto ha escrito los estados iniciales con `gsap.set`, seguro de 3 s). Ahora
oculta solo el nombre y el rol.

**Movimiento reducido.** Sin entrada: nombre relleno y rol visibles desde el primer pintado.

**GSAP.** La timeline se construye con `fromTo` (regla del proyecto: nada de `gsap.from`) y con
el `gsap` que recibe la coreografía.

## Qué sale del código

- `hero.ts`: el titular de tres líneas (`.cae-tit`/`.cae-ln`), el antetítulo (`.cae-kicker`,
  `.cae-firma`, `.cae-regla`, `.cae-meta`), la columna de cifras (`.cae-statcol`), la tarjeta
  (`.cae-widget` y su figura), el bloque móvil (`.cae-movil`), la terminal (`.cae-term`) y el
  escenario del trazo que aterrizaba (`.cae-trazo-stage`).
- `caelestia.titulo.ts`: `justificarTitular`/`montarTitulo` (justificaban el eslogan), los pasos
  de terminal, aterrizaje, barrido del titular, volteo de cifras y brote de la tarjeta, y
  `montarFiguraViva` (la figura de la tarjeta). `montarRoce` se queda, pero sin `.cae-widget` ni
  `.cae-statcol > div` en su selector (siguen las pastillas de la barra y el dock).
- `content.ts`: `identity.headline` y `identity.subheadline` dejan de usarse; se quitan, y con
  ellos el literal que `measure-caelestia-titulo.py` comparaba. `stats` **se queda**: `about.ts`
  lo usa para «Desde» en la ficha de Quién soy. `identity.role` («Desarrollador Full Stack»)
  **no se toca**: lo usa la fila «Rol» de esa misma ficha. El rol de Título entra como campo
  nuevo, `identity.intro: "Desarrollador full stack en Caracas."`, nunca como literal en
  `hero.ts`. El `<title>` y las meta de `index.html` no cambian.
- CSS de todo lo anterior, con la pasada de clases muertas que ya se usó en esta rama de trabajo.

## No objetivos

- No se toca el fondo de figuras, la barra, el dock ni las otras cuatro escenas.
- No se añade otro widget en lugar de «Ahora mismo».
- No cambia el color por hora ni ningún token.

## Anti-objetivos (aunque funcione, sería un fracaso)

- Que el nombre salte o cambie de forma al terminar la entrada.
- Que en móvil el nombre se corte o desborde la ventana (el punto de «no demos.» ya se cortaba;
  esta escena no puede heredar ese defecto).
- Que el nombre deje de ser texto para lectores de pantalla.
- Un fade-and-slide genérico en lugar del trazo.

## Verificación

- `npm run build` y `npm run lint` limpios; consola sin errores.
- `scripts/measure-caelestia-titulo.py`: las familias que miden lo retirado (titular justificado,
  firma y cifras, widget, tarjeta, figura viva, terminal y aterrizaje) se sustituyen por
  aserciones de lo nuevo, y cada aserción nueva se ve dar rojo antes de aceptarse:
  - nombre y rol centrados en la ventana (tolerancia 2 px);
  - el nombre cabe en la ventana a 390, 768 y 1440, sin recorte (contenido medido, no
    `scrollWidth`);
  - el `<h1>` expone «Aoshi Blanco Sanz» como nombre accesible y el SVG es `aria-hidden`;
  - el rol es el literal de `content.ts`;
  - estado final: relleno a 1 y trazo a 0 en los 15 glifos;
  - con movimiento reducido, estado final desde el primer pintado;
  - contraste AA del rol sobre el fondo real, de día y de noche.
- `scripts/verify.py` en verde contra la línea base.
- Las otras cuatro escenas idénticas píxel a píxel (gate de capturas ya usado en esta sesión,
  excluyendo la escena de Título).
- Capturas reales de escritorio y móvil, de día y de noche, mirándolas antes de declarar nada.
- Gate de crítica del proyecto: `lidia-naive-tester` y `vera-art-director`, en Sonnet.

## Decisiones tomadas al cerrar el diseño (no las dictó Aoshi)

- Los escalones de tamaño por ancho (tabla de arriba), incluido el corte nuevo de 1100 px.
- El campo nuevo `identity.intro` en vez de reescribir `identity.role`.
- El escalonado del trazo, de corrido por los 15 glifos también en móvil.

## Lo que se deja al implementador

- Cómo se reparte la timeline entre `caelestia.titulo.ts` y la coreografía, siempre que una sola
  timeline gobierne trazo, relleno y rol.
- El nombre del campo de `content.ts` para el rol.
- La estructura de clases nuevas (`cae-*`), siguiendo el patrón del tema.
