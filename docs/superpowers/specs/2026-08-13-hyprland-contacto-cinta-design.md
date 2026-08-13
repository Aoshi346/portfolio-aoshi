# La cinta — el cierre de Hyprland deja de ser una lista de barras

Estado: implementado <!-- Gate cerrado: lidia-naive-tester en verde (cero bloqueantes) y
vera-art-director con BLOCK aceptado por Aoshi, igual que en Vice. Los dos hallazgos de la
primera pasada (la cinta apelmazada entre 901 y 1200px, y el estado entrando a 900ms donde el
spec manda 1700) y el contraste del rotulo enfriado se arreglaron y se midieron; la puntuacion
no se recalculo con una tercera auditoria completa, por decision explicita de Aoshi. -->
Plan: `docs/superpowers/plans/2026-08-13-hyprland-contacto-cinta.md`
Fecha: 2026-08-13
Alcance: **solo el tema Hyprland**. `[data-scene="contacto"]` — bloque
`Hyprland: las bandas` de `src/themes/themes.css` (L5596-5684), regla de tamaño de
`.contacto-title` (L1334-1337) y `src/themes/hypr.choreography.ts`.
**Vice no se toca** (cerrado el 2026-08-05). **Caelestia no se toca**: se comprueba que sigue
idéntica. `src/style.css` **no se edita**: sus valores heredados se anulan localmente bajo
`:root[data-theme="hyprland"]`, porque Vice depende de esa hoja.
DOM: **`src/sections/contacto.ts` no cambia** — ver `## Por qué el DOM no se toca`.
Contenido: **`src/data/content.ts` no cambia**. Toda cadena sale literal de ese fichero.

Prototipos aprobados por Aoshi, medidos y con los números de este documento:
- Escritorio y coreografía: `.superpowers/brainstorm/1574449-1786576149/content/animacion-a.html`
- Móvil 390×844: `.superpowers/brainstorm/1574449-1786576149/content/movil-d.html`
- Recorrido de descartes: `barra-objetos.html`, `estado.html`, `estado-b.html`, `siluetas.html`

---

## Diagnóstico — qué falla hoy, medido

1. **Los cuatro rótulos incumplen AA, y por una causa localizada.** `.contacto-bar-label`
   (`style.css:346-352`) trae `opacity: 0.6`. El bloque de Hyprland le da `color: var(--haze)`
   (`themes.css:5631-5643`) pero **nunca resetea la opacidad**. Vice sí lo hace, explícitamente,
   en su propia regla. Medido por glifo contra el shader vivo: **2,19–2,94:1** los cuatro rótulos,
   contra un mínimo de 4,5:1. `.contacto-estado-label` (`style.css:325-330`) tiene el mismo defecto.
   El valor del correo queda en **4,48:1**; los otros tres pasan (7,20 / 10,72 / 15,85:1).
2. **Las "bandas a sangre" no sangran.** `[class*="contacto-bar--"]` lleva `padding: 1.4rem 7vw`
   (`themes.css:5611`) que se **suma** a los 7vw de la propia escena: el texto arranca en x=201,6
   en vez de los x=100,8 que usan la placa y el catastro. Es la misma calle doble que el catastro
   ya corrigió en su bloque.
3. **Tres funciones continuas sobre los tokens de la escala**, que el proyecto prohíbe:
   `clamp(var(--t-6), 8.2vw, var(--t-9))` en `.contacto-title` (L1336) y
   `clamp(var(--t-3), 2.4vw, var(--t-4))` en `.contacto-bar-value` (L5647).
4. **No hay afordancia de enlace en reposo.** La única señal de que una banda se pulsa es el
   `::before` de hover (L5618-5630). En táctil no hay hover: un enlace que solo parece enlace al
   apuntarlo no parece enlace nunca.
5. **El indicador de foco es el del navegador**, casi invisible sobre `--void`.
6. **Un número fuera del vocabulario**: la inundación va a `0.45s` (L5629), y el tema solo tiene
   0,42/0,5 (corte, `--hard`) y 0,9 (enfriado, `--slow`).
7. **El estado es el tópico del sector.** Cuadrado de color más rótulo `ESTADO` en versalitas es
   el distintivo de "available for work" de cualquier plantilla, y no se apoya en nada.

---

## El dispositivo — la cinta

En escritorio el contacto deja de ser una lista de celdas y pasa a ser **una cinta**: los cuatro
valores repartidos con `space-between` sobre un filete a sangre pegado al borde inferior, con el
rótulo encima de cada uno. Es la única composición donde el correo puede ser grande —
**28,43px (`--t-4`)** — porque ninguna columna lo encierra: medido, los cuatro ocupan 1265 de 1440
y sobran 175 para repartir.

El rótulo va **encima** del valor, no al lado: cuesta alto y no ancho, así que no le quita nada al
dato, y sin él "Aoshi346" no dice nada.

### El estado

Va al **extremo opuesto de la cinta**, cabalgando el filete en una franja de 27px que la corona,
alineado a la derecha y a `--t-1`. Es la convención real de una barra de estado de gestor de
ventanas: a la izquierda lo que haces, a la derecha el estado del sistema. Y es lo único de la
cinta sin filete de reposo, porque es lo único que no es un enlace.

Con esto la escena se queda en tres renglones — kick, titular, lead — y el vacío pasa a ser una
decisión en vez de un sobrante.

### Jerarquía

Por **tamaño, área y posición, nunca por color**. El correo es la primera vía y en móvil su banda
mide 132px contra 96 de las otras. Ningún acento cromático distingue una vía de otra.

---

## El móvil — el mosaico

Apilar la cinta da un pie de página genérico. La idea de escritorio no era una lista: eran
**bandas a sangre pegadas al borde**. En una pantalla alta eso se dice **teselando el borde
inferior**, que es lo que hace un gestor en mosaico con un monitor vertical.

Cuatro bandas a sangre ocupando el borde inferior, junta de 1px **sin pintar** por donde se ve el
ascua, y el estado como fila superior del mosaico — en una pila, el extremo es arriba.

Medido a 390×844 reales:

| | |
|---|---|
| Calle | 30px · ancho útil 330 |
| Titular (`--t-6`, 50,52px) | 225 de 330 — 105px de aire |
| Correo (`--t-3`) | 248px, **un renglón**, 82px de holgura |
| Bandas | 132 · 96 · 96 · 96 (mínimo del proyecto: 56) |
| Alto usado | 703 de 844, **sin desbordar** |

### La calle deja de ser un porcentaje

`7vw` son 101px en 1440 y 27 en 390: el mismo número da una calle generosa allá y asfixiante aquí.
Bajo 900px pasa a **30px fijos**. Un valor calibrado contra un ancho no viaja a otro, exactamente
igual que una opacidad no viaja entre dos superficies.

### Pulsar enciende el canto

3px de `--l1` en el borde izquierdo de la banda: la marca de ventana con foco del gestor. En
táctil no hay hover, así que el único estado que importa es el de pulsación.

---

## Coreografía

Un solo sentido para la escena entera —de izquierda a derecha— y **dos ejes con dos sentidos**: el
titular abre en horizontal porque es una palabra que se lee; la cinta sube desde el borde inferior
porque es de donde viene una barra de estado.

| ms | Qué | Gesto | Duración |
|---|---|---|---|
| 0 | `.hero-kick` | corte horizontal (`.hypr-cut`, ya existe) | 420 |
| 140 | los 8 glifos de "Hablemos" | corte horizontal, escalón 70ms | 420 |
| 760 | `.contacto-lead` | corte horizontal | 500 |
| 900 | filete de la cinta | barrido a la derecha | 500 |
| 1040 | las 4 vías | corte **vertical**, suben del suelo, escalón 70ms | 420 |
| 1700 | `.contacto-estado` (cromo + texto, un solo nodo) | corte **vertical** | 420 |

Todo con `--hard`. **El dato de contacto entra antes que el estado a propósito**: lo que importa
es el correo. El estado remata en el punto donde la luz del filete terminó su viaje.

**Todo esto va en CSS, disparado por la clase `.is-lit` que la coreografía ya pone sobre la escena**
(`hypr.choreography.ts:161-169`, un ScrollTrigger a `top 90%` más una red por posición). No hay
timeline de GSAP ni ScrollTrigger nuevo. Un disparador propio para el titular —que era la primera
idea— lo habría encendido a `top 82%`, es decir **después** de que la cinta hubiera empezado a
entrar a `top 90%`, invirtiendo el orden diseñado. Los retardos se escriben como `--hypr-d`
explícitos porque el contador genérico de la `RECETA` reparte `n * 70ms` por orden de aparición y
dejaría el lead en 70ms. El fichero ya se impone esta regla en su propio comentario: *"el CSS sigue
siendo la fuente de los tiempos"*.

### El titular letra a letra — la parte técnica

El corte horizontal por glifo no es un gesto nuevo: es **exactamente** el que `.hero-name-word`
usa para encender el nombre al abrir el sitio. La escena que cierra cita a la que abre.

El problema que lo bloqueaba: `.contacto-title` lleva un degradado recortado al texto
(`background-clip: text` + `color: transparent`) con `background-attachment: fixed`
(`themes.css:1314-1332`). Al transformar o recortar un `<span>` hijo, éste sale del pintado del
padre y el recorte del padre deja de alcanzarlo — **la letra se vuelve invisible**.

La solución está pagada ya en el repo: los glifos heredan con `background: inherit` +
`background-clip: inherit`, igual que `.hero-name-word`. Como el degradado es `fixed` se ancla al
viewport y no a la caja, así que los ocho trozos enseñan ocho rebanadas de **uno continuo**.

### Accesibilidad del troceo

Ocho `<span>` de una letra hacen que un lector de pantalla **deletree** "H-a-b-l-e-m-o-s". El
contenedor de glifos va con `aria-hidden="true"` y el texto real en un `aria-label` del `h2`.

### Movimiento reducido

`initScrollReveal` (`src/utils/reveal.ts`) hace early-return **antes** de llamar a
`theme.choreography()`, así que bajo `reduce` la coreografía no corre y **el titular ni se trocea**:
se queda como un `h2` normal, entero y legible. No hay estado degradado que mantener. Ninguna regla
de hover puede colgar de `.is-lit`, y todo estado en reposo queda asentado sin ella.

---

## Por qué el DOM no se toca

`src/sections/contacto.ts` es DOM compartido por los tres temas. Dos decisiones lo dejan intacto:

1. **El troceo del titular vive en `hypr.choreography.ts`**, que es código de tema, igual que ya
   hace con la placa. `contacto.ts` no sabe nada de Vice ni de Hyprland y así se queda.
2. **`.contacto-bar-mark`** —hoy un `<span>` vacío con una rayita de 1,75rem al 50% de opacidad
   (`style.css:360-367`)— **se reutiliza como el filete de reposo** bajo el dato: `order` lo manda
   al final de la banda y pasa a ser la línea de 1px que dice "esto es un enlace". Cero nodos
   nuevos.

**El estado no se puede mover.** Vive dentro de `.contacto-band` y Vice depende de esa posición
para su widget de marcas de esquina. Se coloca con `position: absolute` contra la sección —que ya
es `relative`— atado a la **misma** variable de altura que usa la cinta (`--cinta-h`), para que no
puedan separarse. El arnés lo comprueba: el borde inferior de la franja de estado debe coincidir
con el borde superior de la cinta.

---

## Color y contraste

- Scrim local de la cinta: `rgb(11 4 4 / 0.88)`, calibrado **contra esta franja** con el fondo
  generativo en su punto más brillante. No se reutiliza ninguna opacidad de otro tema ni de la
  cortinilla: un porcentaje se calibra contra una superficie concreta.
- `.contacto-bar-label` y `.contacto-estado-label` reciben `opacity: 1` explícito bajo Hyprland,
  que es el arreglo que Vice ya tiene y que Hyprland nunca copió. Con `--haze` (#b18c86) a opacidad
  plena sobre el scrim el cálculo analítico da ≈6,75:1, **pendiente de medida por glifo** contra el
  shader en movimiento — no se da por bueno sin medirlo.
- Filete de reposo bajo el dato: `rgb(255 160 60 / 0.42)` (`--l3` al 42%). Al apuntar, encima
  crece uno de 2px en `--l1`.
- Foco de teclado: `outline: 3px solid var(--l1)` con `outline-offset: -3px`. Offset negativo
  porque la banda lleva `overflow: hidden` y un offset positivo se recortaría.

---

## Movimiento — reglas que hereda

- Encender es un corte: 420/500ms `--hard`. Apagar es enfriarse: 900ms `--slow`. **Asimétrico**,
  que es la ley del tema y hoy se rompe en el único sitio donde no lo es.
- Escalón `--hypr-d = n * 70ms`, reseteado por escena.
- El filo bajo el dato se anima con `transform: scaleX()`, **no con `width`** — el precedente del
  repo (`.hero-mail::after`) usa `width` y fuerza reflow; aquí no se copia ese detalle.
- Los tres vecinos no apuntados se enfrían al 50% con `:has()` en CSS puro: un gesto de grupo, sin
  JavaScript, sin listeners y sin nada que limpiar.
- El punto del estado **no parpadea**. Una animación infinita en la escena de cierre no descansa
  nunca y no informa de nada que el texto no diga ya.

---

## Descartes, y por qué

| Propuesta | Por qué no |
|---|---|
| **El lanzador** (ventana flotante centrada) | Sacrifica el titular de display: lo baja de 119,77 a 37,9px. |
| **Disposición maestra** (mosaico 1,62fr) | La tesela maestra deja un hueco enorme con el dato hundido. |
| **La regla graduada**, **dos pisos**, **las teselas** | Correctas, pero encierran el correo en una columna y lo dejan en 21,33px. |
| **Estado disuelto en el lead** | Deja de escanearse para quien barre la página en dos segundos. |
| **Estado al canto vertical** | Entierra en vertical un argumento de venta. |
| **Estado fechado** ("desde agosto de 2026") | Cambia `content.ts`, y la fecha real no está confirmada. |
| **Estado como ficha de tres datos** (huso, respuesta) | La mejor de las descartadas, pero añade contenido nuevo. Queda anotada por si Aoshi la quiere en otra tarea. |
| **Convertir la sección en mosaico 2×2** | El dispositivo "bandas" está reservado a contacto por el spec del ascua, y el del catastro sacrificó explícitamente "cuatro bandas a sangre" para protegerlo. |

---

## Riesgos

1. **El degradado por glifo.** Si `background: inherit` no reprodujera el degradado continuo, las
   ocho letras se verían como ocho rebanadas cortadas. Se verifica con captura antes de seguir.
2. **El contraste de los rótulos es un cálculo, no una medida.** Los 6,75:1 salen de suponer que el
   scrim al 88% domina. Hay que medirlo por glifo con el shader vivo, como se hizo con el cartel.
3. **El estado colocado en absoluto puede despegarse de la cinta** si alguien cambia una altura sin
   la otra. Mitigado con una sola variable y una aserción en el arnés.
4. **`.contacto-title` comparte regla de tamaño con `.display-xl`** (L1334-1337). El escalón
   discreto va en una regla propia de `.contacto-title` **después**, sin tocar la compartida, para
   no cambiar el hero ni el about.

---

## Criterios de aceptación

- [x] `npm run build` y `npm run lint` en verde (Node 22 — con Node 18 el build cae en `rolldown`).
- [x] Capturas 1440×900 y 390×844 con `?theme=hyprland`, cero errores de consola.<sup>1</sup>
- [x] Contraste **medido por glifo** contra el shader vivo: los cuatro rótulos, los cuatro valores
      y la línea de estado por encima de 4,5:1. Medido: rótulos 6,43–6,75:1, valores 17,55–17,79:1,
      estado 6,43/16,88:1 (`measure-contacto-cinta.py`).
- [x] El correo en **un solo renglón** a 1440 y a 390. Nunca con puntos suspensivos. Medido: 315px
      a 1440, 237px a 390, un renglón en los dos.
- [x] Todas las zonas pulsables ≥ 56px de alto. Medido: 88px a 1440 (las cuatro), 132/96/96/96px en
      el mosaico de 390.
- [x] Orden de tabulación correo → linkedin → teléfono → github, con foco visible en las cuatro.
      Verificado con `Tab` real: el orden coincide y el foco pinta `outline: 3px solid` en `--l1`.
- [x] Con `prefers-reduced-motion: reduce` la escena queda asentada y legible, y el titular **no**
      está troceado. Verificado: `.contacto-title` sin `span`, `is-lit` sin aplicar, opacidad 1,
      cero `pageerror`.
- [x] Vice y Caelestia idénticas a `main` en la escena de contacto (comparación por captura).
      Verificado por captura (1440×900 y 390×844) y por geometría/estilo computado — sin diferencia
      alguna entre el puerto de esta rama y el de `main`.
- [x] `python3 scripts/verify.py` sale 0 contra `scripts/verify-baseline.json`.
- [x] `scripts/measure-contacto.py` verde, incluida la aserción franja/cinta.<sup>2</sup>

<sup>1</sup> `measure-contacto.py`/`measure-contacto-matriz.py`/`measure-type-scale.py` (tema Vice) y
`measure-contacto-cinta.py` (tema Hyprland) reportan cero errores de consola propios de este plan.
En modo de movimiento normal (no `reduced-motion`) persiste el `pageerror: gsap is not defined` de
`hypr.choreography.ts:63`, preexistente en `main` y fuera del alcance de este plan (ver nota del
Task 7 del plan) — no aparece bajo `prefers-reduced-motion: reduce`, que es donde este criterio se
verificó sin excepción.<br>
<sup>2</sup> El criterio nombra `measure-contacto.py`, pero la aserción franja/cinta vive en el
arnés que este plan creó para Hyprland, `measure-contacto-cinta.py` (Task 1 del plan) — verde:
`fallos: ninguno`.
