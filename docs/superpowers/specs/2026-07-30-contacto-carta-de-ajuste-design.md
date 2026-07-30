# La carta de ajuste — el cierre de Vice, la escala del tema y la navegación

Estado: pendiente de plan
Fecha: 2026-07-30
Alcance: tema Vice. La escala tipográfica y la navegación tocan todas las escenas del tema;
la escena de contacto se rehace entera. Hyprland y Caelestia no se tocan: solo se comprueba
que no se rompen.

## Por qué

"Hablemos" funciona y es el suelo de conversión del portfolio. El encargo empezó midiendo,
en el build de producción con `?theme=vice`, porque un rediseño sin números previos acaba
discutiendo impresiones.

### Lo que hay hoy, medido

| | qué se midió | resultado |
|---|---|---|
| D1 | dónde empieza la escena | 10.687 px de 11.587 (92,2%) en escritorio; 11.470 de 12.314 (93,1%) en móvil |
| D2 | tinta en pantalla | 313 × 201 px = **4,85%** del encuadre en escritorio; 188 × 160 = 9,1% en móvil |
| D3 | hueco sobre la primera letra | **419 px**, de los cuales 202,5 son `padding-top` computado |
| D4 | desviación del bloque respecto al centro geométrico | **69 px** por debajo |
| D5 | diana táctil de los tres enlaces del pie | **14,4 px** de alto sobre cuerpo de 9,6 px |
| D6 | diana táctil de la pastilla de correo | 349,7 × 64,4 px en escritorio, 271,9 × 54,8 en móvil |
| D7 | tamaños tipográficos distintos en la escena | 64 / 22,4 / 16,8 / 10,56 / 9,6 px |
| D8 | títulos de escena en todo el tema | hero 152, obra 73,6, contacto 64, créditos 57,6 px |
| D9 | enlaces de navegación en todo el documento | `nav a` = 0, `a[href^="#"]` = 0 |

Con `prefers-reduced-motion` la escena está sana: documento de 10.753 px en móvil, título sin
trocear a 32 px, todas las opacidades a 1. Cero errores de consola en todas las sesiones.

### Los ocho hallazgos que firman los dos especialistas

`especialista-ux-ui` y `especialista-animaciones` trabajaron en paralelo sobre el mismo brief.
Estos ocho los firman los dos:

- **C-1.** D5 incumple WCAG 2.2 AA SC 2.5.8 (diana mínima 24 × 24 px). D6 sí cumple.
- **C-2.** El hueco de D3 es un defecto, no una decisión: la reserva de letterbox nunca se
  despliega en esta escena. Comprobado: los dos `[data-letterbox]` miden `0px` y el
  `padding-bottom` ya está reclamado, el de arriba no.
- **C-3.** Los 69 px de D4 no los eligió nadie: son el residuo de C-2.
- **C-4.** D7 y D8 son la tercera aparición de la escala tipográfica del tema. Automático P0.
- **C-5.** Los tres `gsap.from` de `scene5Contact` se saldan en este encargo. No es limpieza
  opcional: la navegación crea un camino de ejecución nuevo — llegar con el trigger ya pasado —
  que hoy no está probado, y `from` deduce un extremo leyendo el DOM.
- **C-6.** El estado de navegación existe pero no se puede pulsar (`.rail-now` escribe
  "05 · Fundido" y no es un enlace).
- **C-7.** No hay navegación en ningún tema (D9), y la que se añada vive fuera de
  `.cinema-chrome` porque los tres temas la necesitan.
- **C-8.** La coreografía actual es desproporcionada para lo poco que hay en la escena.

## La dirección: carta de ajuste con gelatinas

Terminó la emisión y lo que queda en pantalla es la carta de ajuste con cómo localizar a quien
emite. Cuatro barras verticales a sangre, una por vía de contacto.

Se eligió sobre otras seis direcciones maquetadas y vivas. Las descartadas y por qué están en
el companion del brainstorm; lo que importa aquí es el criterio: **el hueco negro es imposible
por construcción** — que era el defecto que arrastraban todas las demás — y la escena tiene un
solo gesto grande en vez de varios pequeños.

### Tokens

Las barras son gelatinas de iluminación: filtros translúcidos delante del foco, de modo que el
fondo generativo **sigue vivo debajo** y se tiñe al pasar. Es lo que las distingue de barras
opacas, que taparían el shader en el 56% de la pantalla final.

| barra | vía | valor |
|---|---|---|
| 1 | correo | `#ff2e88` al 30% |
| 2 | linkedin | `#ffd166` al 26% |
| 3 | teléfono | `#fff4e8` al 15% |
| 4 | github | `#0b0513` al 55% |

Cada barra lleva un degradado de tinta de 190 px bajo el valor,
`linear-gradient(to top, rgba(11,5,19,.82), transparent)`. **No es adorno**: sobre un fondo
generativo la luminancia se mueve, y sin él el contraste del dato deja de estar garantizado.

### Comportamiento

- **El dato se lee siempre**, sin hover. En táctil no hay hover y el correo no puede depender
  de él.
- **Hover sobre una barra**: `flex-grow` de 1 a 2,6 en 520 ms `cubic-bezier(.22,1,.36,1)`; el
  valor escala 1,14; la marca pasa de 28 a 120 px de ancho.
- **Rótulo vertical** a 34 px con `letter-spacing: .34em` corriendo a lo alto del campo de
  color: llena la barra con tipografía en vez de con vacío, y es como se rotula una carta de
  ajuste de verdad.
- **Foco visible**: `outline: 3px solid #ffd166` con `outline-offset: -6px`.

### Copy

Frase: **"Cuéntame tu idea."** Elegida por el autor entre once alternativas. Va a
`src/data/content.ts`, que es la única fuente.

No lleva plazo de respuesta a propósito: es la promesa más fácil de incumplir y no existe hoy
ningún dato en `content.ts` que la respalde.

### El estado

`ESTADO · Disponible para proyectos`, con el mismo separador con el que el sitio ya escribe un
estado en el chrome ("05 · Fundido"). Al pasar por encima, dos marcas de encuadre de
16 × 16 px y trazo de 2 px entran desde −7 px hasta ajustarse al valor, y rótulo y separador
pasan a ámbar.

Se probaron y se descartaron: la pastilla redondeada con punto latiendo (es el componente más
repetido de la web y no pertenece a este sitio) y el conector ámbar con remate magenta.

## La escala tipográfica del tema

Se cierra **entera**, no solo en contacto. Cuarta, razón 1,333, base 16, suelo duro 12.

| paso | px | uso |
|---|---|---|
| `--t-1` | 12 | rótulos y `.hero-kick`. Absorbe los 10,56 y 9,6 de hoy |
| `--t-2` | 16 | cuerpo pequeño, valores de estado |
| `--t-3` | 21,33 | entradilla |
| `--t-7` | 67,40 | título de escena. Aquí convergen obra 73,6, contacto 64 y créditos 57,6 |
| `--t-8` | 89,85 | |
| `--t-9` | 119,77 | título de contacto en la maqueta aprobada |
| `--t-10` | 159,66 | |

Dos reglas que se aplican en todo el tema:

1. Todo `clamp()` tiene **los dos extremos** en pasos de la escala.
2. Máximo **cuatro tamaños por encuadre**.

**La tabla del carril de obra se rehace después de aplicar la escala, no antes.** Hoy describe
una maquetación que el cambio va a mover, y una tabla de traspaso desactualizada no falla: miente.
Hay que volver a medir las cinco mesetas con el mismo instrumento
(`scripts/measure-obra-rail.py`, `u = 0,225 / 1,675 / 3,125 / 4,575 / 6,025`).

## La navegación

Hoy no existe (D9). Se añade fuera de `.cinema-chrome`, porque los tres temas la necesitan.

**Corte seco.** Decidido por el autor sobre la alternativa de un desplazamiento de un segundo
con `lenis.scrollTo(duration: 1.0, lock: true)`. Razón: la continuidad ya la da el scroll
normal, y quien usa el menú lo usa justamente porque no quiere recorrer el camino.

En el resto coinciden los dos especialistas y no se discute:

- Anclas reales en el `href` (no `href="#"` con JavaScript encima).
- `preventDefault` y **un solo punto de ejecución** del desplazamiento.
- **Nunca escribir `location.hash`**: dispara el salto nativo del navegador y compite con el
  nuestro.
- `history.replaceState` al aterrizar, para que la URL diga dónde estás sin ensuciar el
  historial.

Dos trampas ya identificadas que el plan debe resolver de forma explícita:

- **El destino de obra no es `pin.start`.** Ahí la cartela está a medio montar. El fotograma
  asentado está en `u ≈ 0,42`, es decir `pin.start + (0,42 / 6,25) × presupuesto_pin`, unos
  +339 px. Se lee **en el momento del clic**, nunca cacheado.
- **`scroll-behavior: smooth` en `html` hace que `window.scrollTo({behavior: "auto"})` acabe
  siendo suave**, incluso con `prefers-reduced-motion` — que es justo el camino donde Lenis no
  existe. Hay que pasar `behavior: "instant"` de forma explícita.

## Vocabulario de medida

Nombres canónicos para el spec, el código de medida y los informes de los gates. Existen
porque el encargo del carril perdió tiempo tres veces midiendo dos cosas distintas con el
mismo nombre.

| nombre | qué es |
|---|---|
| `y_contacto` | desplazamiento al que empieza la escena de contacto |
| `y_max` | desplazamiento máximo del documento |
| `presupuesto_cierre` | `y_max − y_contacto` |
| `recorrido_composicion` | recorrido que consume la composición dentro de la escena |
| `p_cierre` | `y_contacto / y_max` |
| `y_destino(tipo)` | destino calculado de un ancla, por tipo de escena |
| `y_reposo` | desplazamiento tras asentar Lenis |
| `hueco_superior` | píxeles vacíos sobre la primera letra |
| `caja_tinta_central` | caja del bloque de texto central |
| `desviacion_centro` | distancia del bloque al centro geométrico del encuadre |

"Tinta real" (suma de rectángulos, sin caja envolvente) se reporta pero **no es umbral**: no
hay valor histórico con el que compararlo.

## Criterios de aceptación

Cada uno dice con qué instrumento y en qué umbral se mide, en la misma frase.

1. **Diana táctil.** Ningún objetivo interactivo de la escena mide menos de 24 × 24 px CSS,
   medido con `getBoundingClientRect()` en el build de producción a 390 × 844 y 1440 × 900.
2. **Hueco superior.** `hueco_superior` baja de los 419 px de hoy a menos de 120 px, medido
   con el mismo instrumento que D3 a 1440 × 900.
3. **Ocupación.** La tinta de la escena pasa del 4,85% actual a más del 35% del encuadre,
   medido como suma de las cajas de barras y bloque de título a 1440 × 900.
4. **Contraste del dato.** Cada valor de barra alcanza al menos 4,5:1 contra el píxel
   renderizado justo detrás, muestreado sobre captura del build de producción **con el shader
   real**, en tres fotogramas separados 2 s.
5. **Contraste del estado.** El ámbar del valor de estado alcanza al menos 4,5:1 con el mismo
   instrumento y el mismo muestreo de tres fotogramas.
6. **Escala.** Cero tamaños tipográficos fuera de la escala en todo el tema, comprobado
   recorriendo `getComputedStyle().fontSize` de todos los elementos con texto en las cinco
   escenas.
7. **Movimiento reducido.** Con `prefers-reduced-motion: reduce`, ni las marcas de encuadre
   ni el crecimiento de barra se mueven, comprobado midiendo la geometría antes y después de
   un hover sintético.
8. **Navegación.** Cada ancla aterriza con `|y_reposo − y_destino(tipo)| <= 8 px`, medido tras
   3,5 s de asentamiento de Lenis, en las cinco escenas y en los tres temas.
9. **Sin regresión de deuda.** Cero `gsap.from` en `vice.choreography.ts`, comprobado por grep.
10. **Arnés.** `python3 scripts/verify.py` sale con código 0 y `npm run build` en verde.

## Lo que no se hace

- **Formulario.** No hay backend, y `import.meta.env.VITE_*` va al bundle público. El correo
  es `mailto:` y el teléfono `tel:`. Lo rechazan los dos especialistas.
- **Tocar Hyprland y Caelestia** más allá de comprobar que no se rompen.
- **Rehacer la tabla del carril antes de aplicar la escala** (ver arriba).

## Riesgos

- **El fondo aún no está definido en `main`.** Todas las medidas de contraste de la maqueta
  están tomadas sobre una aproximación en CSS, no sobre el shader. Los criterios 4 y 5 se
  miden con el shader real o no se miden. Si algún fotograma baja de 4,5:1, la corrección es
  subir el relleno de la gelatina a un valor opaco, **no** oscurecer el ámbar.
- **La escala toca cinco escenas.** Es el cambio con más superficie del encargo y el que más
  probablemente mueva la maquetación del carril.
- **Una animación con `fill-mode: both` retiene su `transform` al terminar y gana a la regla
  del hover.** Pasó en la propia maqueta: el conector se alargaba en el CSS y no se movía un
  píxel en pantalla. Es la misma familia de trampa que los transforms inline de GSAP contra
  el hover en CSS, que el proyecto ya tiene documentada.

## Origen

- Encargo: `.docs/BRIEF-contacto-hablemos.md`
- Maqueta aprobada: companion del brainstorm, pantalla `carta-de-ajuste`
- Gate final antes de `main`: `lidia-naive-tester` y `vera-art-director`, los dos leyendo su
  `memory.md` antes
