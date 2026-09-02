# Spec de Caelestia — Título: el escritorio se presenta solo

Estado: implementado
Plan: docs/superpowers/plans/2026-08-26-caelestia-titulo.md
Fecha: 2026-08-26
Alcance: la **fase B1** de las seis del rediseño de Caelestia — la escena `#hero` dentro del
workspace. Toca `src/sections/hero.ts` (o el módulo que lo construya, leer el directorio),
el bloque `:root[data-theme="caelestia"]` de `src/themes/themes.css`,
`src/backgrounds/caelestiaBlobs.ts` (se reescribe entero: su propio comentario lo marca
PROVISIONAL) y un gesto nuevo en `src/themes/caelestia.choreography.ts`.

**Vice no se toca** (cerrado el 2026-08-05). **Hyprland no se toca.** `shaderBackground.ts` es
compartido y no se modifica. La fase A (el shell: barra, dock, carril de workspaces, motor de
color) está cerrada y **tampoco se toca**: esta fase vive dentro de la ventana.

---

## Por qué

La fase A cerró el shell y dejó las cinco secciones de dentro sin tocar. Medido sobre el build de
producción, con la ventana de **1412 × 748** que impone el carril de workspaces:

| escena | alto del contenido | ¿cabe en 748? | hallazgo |
|---|---|---|---|
| **Título** | 494 px (y0 255 → y1 749) | sí | **255 px muertos arriba** — un tercio de la ventana. El pie (Caracas, correo) fuera de la tarjeta, huérfano |
| Quién soy | 443 px | sí | la más sana; ficha apretada |
| Obra | **4964 px**, x1 1426 en 1412 | **no** | rota: 6,6 pantallas y 14 px de desbordamiento |
| Créditos | 758 px | roza | tercio derecho vacío |
| Fundido | 542 px | sí | media ventana vacía en la escena de cierre |

El defecto es uno solo repetido cinco veces: **todo se apoya en el canto izquierdo y crece hacia
abajo**, que es como se maqueta una página que se desplaza. La ventana es apaisada y tiene fondo.

Este spec cierra **solo Título**. Las otras cuatro van en B2–B5.

---

## La decisión de partida: cada escena es una aplicación

El workspace no contiene una sección: contiene un programa. Obra será un gestor de archivos,
Créditos un gestor de paquetes, Fundido un compositor de mensaje, Quién soy una ficha del sistema.

**Título no es una aplicación: es el escritorio desnudo.** Es la única escena sin ventana propia
dentro de la ventana — lo que se ve es el fondo, y encima flota un widget. Esa asimetría es
deliberada: distingue la escena de llegada de las cuatro que son programas.

---

## La entrada: `whoami`

Al montar la escena, el shell **ya está puesto** —barra, dock y ventana— y lo único que se anima es
el escritorio.

1. Una línea de terminal aparece centrada: `~ $` y el cursor.
2. Se escribe `whoami` (0,46 s, 6 caracteres). El cursor parpadea tres veces.
3. **La respuesta se traza**: `Aoshi Blanco Sanz` en los contornos reales de Fraunces, recorridos
   con `stroke-dashoffset`, 15 trazados escalonados 45 ms, 0,52 s cada uno. El relleno entra por
   detrás mientras el contorno se apaga.
4. El fondo florece a la vez que se rellenan las letras (0,9 s).
5. El nombre **aterriza en la firma**, sobre el titular, a 30 px de Fraunces (0,66 s,
   `power3.inOut`), y cruza al texto real.
6. Entran la regla, la línea de meta, el titular y las cifras.

**Por qué `whoami` y no «hello, world».** La terminal pregunta y el nombre es la respuesta. Usa la
literalidad de escritorio que gobierna el tema, se salta el saludo de manual —que abre medio
portfolio de programador— y deja el nombre solo en el centro durante segundo y medio. Se
descartaron: «hello, world» escrito (no dice nada propio) y el nombre trazado sin terminal (válido
para cualquier tema; el escritorio no aparece).

**Por qué aterriza en la firma y no en el widget.** La primera versión llevaba el trazo al nombre
del widget, de 780 px a 21: un aterrizaje tan largo que se lee como «el nombre se encoge y
desaparece». En la firma el recorrido es la mitad y el nombre se queda a un tamaño que se lee.

**Los trazos no son una tipografía de imitación.** Son los contornos de Fraunces instanciada en
`opsz 9 · wght 900 · SOFT 0 · WONK 1`, extraídos del `.ttf` variable con `fontTools` y servidos
como datos de trazado por glifo. El plan debe decidir si se generan en build o se embeben.

---

## El titular

### La óptica: `opsz 144`, no `opsz 9`

`opsz` en Fraunces no es estilo: **la fuente trae dibujos distintos según el tamaño al que se vaya a
leer**. El tema fijó `opsz 9` para el display en la fase A y a 15 px —la marca de la barra— es lo
correcto. **A 84 px es el dibujo equivocado**: `opsz 9` engorda las finas para que sobrevivan a
tamaño de texto, y ampliado sale romo y sin contraste.

**El titular deja de heredar los ejes del shell y declara los suyos.** Un token nuevo junto al que
ya existe:

```css
--cae-display-axes:        "opsz" 9,   "wght" 900, "SOFT" 0, "WONK" 1;  /* ya existe: barra, firma */
--cae-display-axes-cartel: "opsz" 144, "wght" 900, "SOFT" 0, "WONK" 1;  /* nuevo: solo el titular */
```

Los ejes de la barra, las pastillas y la firma **no se tocan**: ahí el texto se lee a 15–30 px y
necesita el dibujo de texto.

### La composición: bloque justificado

Las tres líneas se estiran hasta **medir exactamente lo mismo**, cada una con su propio tamaño
calculado midiendo el texto. El borde derecho deja de estar roto y el bloque es una masa sólida de
tinta. «no demos.» acaba siendo la línea más grande **por aritmética, no por decisión**.

El corte, sobre el texto literal de `identity.headline`:

```
Construyo sistemas
que aguantan producción,
no demos.
```

Se descartaron: la actual (`opsz 9`, tres líneas iguales, «que» colgando al final de la primera),
salida de terminal, el remate a tamaño de cartel, cartel en retícula, columna estrecha a la derecha,
sangría escalonada, una sola línea a todo lo ancho, partida por la coma, remate en negativo y
alineada a la derecha. Están todas construidas y comparables en el companion.

### Dos trampas de la justificación, ya pagadas

**1. Medir la caja del `<span>` no es medir el texto.** Los `.ln` son de bloque: su
`getBoundingClientRect().width` devuelve el ancho del **contenedor**, no el del texto. Con esa
medida las tres líneas salían del **mismo tamaño** y el bloque solo *parecía* justificado. Hay que
medir con `document.createRange()` + `selectNodeContents()`.

**2. La medida común no puede ser fija.** Con esta frase las tres líneas son de 18, 24 y 9
caracteres: forzarlas a una medida ancha dispara el alto de la última y se come el dock. El
algoritmo **estrecha la medida en pasos de 30 px** hasta que el bloque cabe en el alto disponible.
Sin ese bucle, medido: 400 px de bloque y **−138 px de aire** bajo el pie.

### La entrada del titular: barrido de tinta

Cada línea se descubre de izquierda a derecha con `clip-path: inset(0 100% 0 0)` → `inset(0 0% 0 0)`,
0,72 s, `power2.inOut`, escalonadas 0,11 s. Se lee como tinta que se posa, no como un objeto que
entra.

Se descartaron: máscara por línea, palabra a palabra, letra a letra, se descuelga, el remate
primero, **el peso sube** (wght 200 → 900) y **entra en foco óptico** (opsz 9 → 144 con desenfoque).
Las dos últimas son buenas y quedan anotadas por si el barrido cansa: la de foco óptico es la única
que solo se puede hacer con una fuente variable y dice con el movimiento lo mismo que arregla la
óptica.

---

## El subtítulo

### La firma

El antiguo *kicker* pasa a ser una línea de firma sobre el titular:

```
Aoshi Blanco Sanz ──── CARACAS. FULL STACK. DESDE 2021.
```

El nombre en Fraunces a 30 px con los ejes del shell (`opsz 9`, wght 700) — **es el destino del
trazo de la entrada**, y por eso lleva `white-space: nowrap`: si partiera en dos líneas el
aterrizaje no cuadraría. La meta es `identity.subheadline` **literal, con sus puntos**, en Martian
Mono a 10 px con `letter-spacing: .24em`.

### Las cifras: columna a la derecha

Las cuatro entradas de `stats` dejan de ser una fila bajo el titular y se apilan en el **canto
derecho, cada una sobre su filete**, como el colofón de un cartel. El titular se estrecha 230 px
para dejarles sitio. El bloque deja de ser una sola masa y la ventana se reparte en dos columnas de
peso muy distinto.

Se descartaron: firma arriba y cifras abajo (lo que había), meta abajo compartiendo línea con las
cifras, barra de estado monoespaciada y cifras en pastillas Material.

### La entrada del subtítulo: las cifras voltean

Cada bloque de cifra gira sobre su eje X (`rotateX: -82° → 0`, `transformPerspective: 600`, 0,6 s,
`power3.out`, escalonado 0,09 s). La regla crece y la meta entra antes.

Se descartaron: regla y meta, meta mecanografiada, **las cifras suben contando desde cero**, el
rótulo se abre y barra que se llena.

**Nota si alguien recupera el contador:** arrancar 2021 desde `fin − 60` pinta «1961» a mitad de la
animación y se lee como un error. Si se usa, arrancar en 2000.

---

## El widget: «Ahora mismo»

Flota arriba a la derecha, 316 px de ancho, `surface-container` con `outline`:

- pastilla de `identity.availability` en color ancla (azufre)
- `identity.now` en Fraunces 20 px
- `identity.location` · `Desde ${identity.since}` en mono
- dos filas: **Ingeniería de Sistemas → 10.º semestre** (de `education`) y
  **Telefónica Venezuela → Ago 2025 — May 2026** (de `experience`)

**Todo sale de `content.ts` literal.** Una versión anterior llevaba «Repositorios públicos · 2»,
que no existe en ninguna parte del proyecto. La regla anti-mock aplica también a los datos
derivados: si no está en `content.ts`, no se pinta.

Se descartaron: la ficha (estado/lugar/ahora — la más callada, y redundante ahora que la firma vive
abajo) y el **reloj de Caracas** (hora local de Aoshi vía `Intl` con `America/Caracas`, que responde
«¿está despierto?»). El reloj es una buena idea y queda anotada por si el widget se queda corto.

**Entrada: se dibuja el borde.** El contorno del widget se traza con `stroke-dashoffset` sobre un
`<rect rx="23">` en un SVG superpuesto (0,85 s) y luego se rellenan la superficie y las filas.
**Rima con el trazo del nombre**: es el mismo gesto dos veces, y es lo que ata la entrada del
widget a la de la escena.

**Trampa:** el `<rect>` hay que medirlo **cuando el widget ya tiene caja definitiva**. Medirlo al
montar, con el envoltorio todavía colapsado, da 0 y el trazo sale disparado fuera de la tarjeta.

---

## El fondo

Se reescribe `caelestiaBlobs.ts` entero. Su propio comentario ya lo anticipaba: *«PROVISIONAL: el
fondo generativo definitivo es una fase propia y aún no está diseñado»*.

### Lo que dice la referencia

- El lema literal de Caelestia es **«A fluid, morphing shell for your Linux desktop»**, y su
  configuración expone un parámetro **`deformScale`**. Morfar es su identidad.
- Su estética se describe como **«soft pastel colors, rounded corners»**, definida por alejarse del
  look oscuro y áspero del Linux clásico.
- Material 3 Expressive publicó en septiembre de 2025 una **biblioteca de 35 figuras con nombre** y
  morfado entre ellas.

### Las figuras

El fondo son **figuras con nombre de Material 3**, no texturas. Cada una es un radio en función del
ángulo:

```glsl
r(θ) = 1 + a·cos(n·θ) + s·cos(2n·θ)
```

`n` = puntas, `a` = profundidad del lóbulo (**negativa = lado cóncavo**, que es lo que hace un
«cookie»), `s` = segundo armónico, que afila la punta.

| tramo | figura | n | a | s | lectura |
|---|---|---|---|---|---|
| 00:00 — 04:48 | `puffy` | 4 | 0.150 | 0.020 | blanda |
| 04:48 — 09:36 | `sunny` | 9 | 0.105 | 0.030 | amanece |
| 09:36 — 14:24 | `12-sided cookie` | 12 | −0.058 | 0.012 | se ordena |
| 14:24 — 19:12 | `4-leaf clover` | 4 | 0.265 | −0.045 | se abre |
| 19:12 — 24:00 | `soft burst` | 10 | 0.175 | 0.070 | se cierra |

**El morfado no interpola `n`.** Con un número no entero de lóbulos la curva no cierra y aparece una
**costura visible en el ángulo π**. Lo que se interpola son **los dos radios completos**, cada uno
con su `n` entero. Es como morfa Material: se emparejan los contornos, no los parámetros.

Cada tránsito ocupa el **último 30 % de su tramo — 86 minutos**. En una visita normal no se ve
morfar: se ve que a las nueve no era esto.

### La composición: tres en diagonal más cuatro satélites

| pieza | centro (p) | R | tonos |
|---|---|---|---|
| grande | (−0.68, 0.26) | 0.44 | wall-1 → wall-2 |
| media | (−0.02, −0.02) | 0.31 | wall-2 → wall-3 |
| pequeña | (0.58, −0.30) | 0.21 | wall-3 → wall-1 |
| satélite | (0.12, 0.42) | 0.085 | wall-3 → wall-2 |
| satélite | (0.93, 0.05) | 0.075 | wall-2 → wall-1 |
| satélite | (−0.89, 0.47) | 0.055 | wall-1 → wall-3 |
| satélite | (0.40, −0.46) | 0.050 | wall-3 → wall-1 |

Tamaños escalonados bajando de izquierda a derecha: es la única composición con **dirección**. Los
satélites van en los huecos que deja la diagonal, **fuera de las dos zonas ocupadas** —el widget
arriba a la derecha, el bloque de texto abajo a la izquierda— y **dos los corta el canto de la
ventana**: si todos cupieran enteros se leerían como iconos repartidos.

Se descartaron: colosal (una sola mayor que la ventana), dos que se solapan, racimo, eco concéntrico
y enmarcado. Todas construidas y conmutables en el companion.

### El color

Los cuatro rellenos son la superficie base y los tres `--cae-wall-*` que ya define
`caelestia.color.ts`: **tres matices distintos** —la hora, la hora +42° y la hora +318°—, no cuatro
tonos del mismo. Una versión intermedia usó `surface` / `surface-container` /
`surface-container-high` / `primary-container`, todos con croma 0.012–0.062: salía **casi gris**.

**El croma no es el mismo en los dos esquemas:**

| | claro | oscuro |
|---|---|---|
| base | L 0.980, C 0.012 | L 0.185, C 0.016 |
| wall-1 (hora) | L 0.930, C 0.090 | L 0.265, C 0.034 |
| wall-2 (hora +42°) | L 0.950, C 0.070 | L 0.320, C 0.028 |
| wall-3 (hora +318°) | L 0.960, C 0.060 | L 0.375, C 0.022 |

**En OkLCH, croma 0.09 a claridad 0.30 cae en la zona parda: oscuro y saturado da barro** — marrón,
oliva y granate, medido y visto. Material 3 en oscuro no hace eso: sus superficies elevadas llevan
croma bajísimo —**tinte, no color**— y la separación la da la **claridad**. De noche el croma baja a
un tercio y la rampa de claridad se abre al doble.

Cada figura se rellena con un **degradado interno** entre dos de esos tonos, en la dirección de la
luz nominal del sistema (arriba-izquierda), interpolado en **lineal, antes de la gamma**.

### Lo que el fondo NO lleva: relieve

Se construyó y se descarta. La normal del campo, la luz lambertiana y el canto encendido dan
volumen, y **repujar es un lenguaje material duro** —cartón, letterpress— mientras que Caelestia es
plano, claro y blando. El relieve peleaba contra la marca.

Queda anotado lo aprendido por si alguien lo reintenta: con la derivada cruda la normal recoge el
escalón del ruido y salen **facetas triangulares** en las zonas planas; y la ganancia tiene que ir
partida por esquema, porque con una sola el rango de luminancia en claro pasó de 17 % a **47 %** y
el contraste de 13:1 a 8.68:1.

### El movimiento

**Dos relojes separados a propósito.**

**El morfado** entre figuras lo manda la hora: una vez por tramo, 86 minutos de tránsito.

**El ambiente** corre a su propio ritmo, para que se note en los treinta segundos que dura una
visita. Con el factor inicial la figura giraba **2 grados en medio minuto**: matemáticamente se
movía, humanamente estaba quieta.

- **Deriva (el gesto principal):** cada figura **orbita** alrededor de su sitio. Las dos
  frecuencias —X e Y— son **distintas y no son múltiplos**, así que el recorrido es una curva de
  Lissajous abierta y **nunca repite el mismo camino**. Recorrido de **52 a 193 px**, órbita
  completa entre **32 y 107 s**. Una traslación recta se lee como una pegatina arrastrada; una
  órbita se lee como algo que flota.
- **Giro:** una vuelta entre **4,6 y 14,4 min**, en segundo plano.
- **Latido:** las puntas laten con periodo de **26 s**.
- **Tramado:** ±0.0035 atado a un reloj lento e independiente, para que acelerar el ambiente no le
  meta parpadeo. Sin él, los degradados internos hacen bandas.

`prefers-reduced-motion`: sin trazo, sin terminal, sin órbita, sin giro. El escritorio aparece
montado y el fondo congelado (`uTime = 0`).

---

## La micro-interacción: el fondo se aparta

Al pasar el ratón por el widget, las cifras, las pastillas de la barra o el dock, **el fondo se
desplaza unos píxeles al lado contrario** —como si la tarjeta lo empujara— y el elemento sube 2 px.
Desplazamiento proporcional a la distancia del elemento al centro de la ventana: 14 px en X, 10 en
Y, `power3.out`, 0,7 s de ida y 0,8 de vuelta.

Es la única que usa las figuras del fondo como parte de la interacción en vez de tratar fondo e
interfaz como dos capas independientes.

Se descartaron: capa de estado Material, el ancla aparece (filete de azufre), la luz sigue al
puntero (la sombra se desplaza), la forma se deforma (redondeos asimétricos con muelle), muelle con
rebote y el contenido se asienta.

---

## Color y contraste

El contraste **no depende de la composición**: depende de la paleta. Las seis composiciones dan el
mismo número porque el píxel más claro y el más oscuro son los mismos tonos en todas.

Medido leyendo los píxeles del lienzo y comparando contra `--cae-on-surface`:

| momento | peor contraste | rango de luminancia |
|---|---|---|
| 09:36 — 14:24 (`cookie`) | 13.00:1 | 14.8 % |
| 14:24 — 19:12 (`clover`) | 12.69:1 | 17.7 % |
| 19:12 — 24:00 (`soft burst`) | 8.04:1 | 5.0 % |
| 00:00 — 04:48 (`puffy`) | 8.08:1 | 5.0 % |
| 04:48 — 09:36 (`sunny`) | 8.00:1 | 5.1 % |

Todo **AAA**. La invariancia sigue viniendo de la fase A: la claridad de cada rol no se mueve con el
matiz, así que se mide una vez y vale para las 1.440 posiciones del reloj.

---

## Los gates

El arnés nuevo, `scripts/measure-caelestia-titulo.py`, tiene que comprobar al menos:

1. **El barrido de las 24 h.** 96 muestras cada 15 minutos, peor contraste del día ≥ 4.5:1. Un
   **morfado puede producir una silueta que ninguno de los cinco estados tiene por separado**, así
   que medir solo los cinco asentados deja las transiciones sin vigilar.
2. **El bloque cabe.** Alto del titular, pieza más ancha contra los 1316 px útiles y **aire bajo el
   pie ≥ 0**. Este gate ya cazó dos desbordamientos de 138 y 142 px.
3. **La justificación es real.** Las tres líneas miden lo mismo **con `Range`, no con la caja del
   `<span>`** — y sus tamaños de fuente son **distintos entre sí**. Si salen iguales, la medida está
   mal y el bloque solo lo parece.
4. **El fondo se mueve.** Muestrear el lienzo con 8 s de diferencia: ≥ 10 % de las muestras cambian.
   Con solo giro y latido cambiaba el 3 %; con la órbita, el 28,8 %.
5. **El fondo compila.** Un `pon()` con la firma cambiada dejó el lienzo negro y el gate 4 dio
   **0 %** — que es exactamente el síntoma que venía a medir. Comprobar `COMPILE_STATUS` y fallar
   con el log, no en silencio.
6. **Movimiento reducido.** Con `reduced_motion="reduce"`: sin terminal, sin trazo, fondo congelado
   y escritorio montado.
7. **Anti-mock.** Todo dato visible del widget y del pie existe en `content.ts`.
8. **Los ejes del shell no se han movido.** La marca de la barra sigue en `opsz 9`; solo el titular
   usa `opsz 144`.

**Ningún gate se da por bueno sin haberlo visto dar rojo contra el fallo que dice cazar.** Es la
lección que más costó en la fase A: ocho veces el fallo estuvo en el instrumento, no en el diseño.

---

## Lo que queda fuera

- Las escenas **Quién soy, Obra, Créditos y Fundido** (fases B2–B5). Sus maquetas están hechas y
  aprobadas en dirección —gestor de archivos, ficha del sistema, gestor de paquetes, compositor de
  mensaje— pero no especificadas.
- **Las nueve capturas de `public/media/obra/`**, que siguen siendo marcadores «CAPTURA PENDIENTE»
  con la paleta de Vice. Bloquean B3 (Obra), no esta fase.
- **Móvil.** Todo lo medido aquí es a 1412 × 748. El carril de workspaces en pantalla estrecha es
  una decisión abierta desde la fase A.

---

## Maquetas

Todas vivas y conmutables en el companion de brainstorming
(`.superpowers/brainstorm/2412334-1787752791/content/`, no versionado):

| pantalla | qué contiene |
|---|---|
| `01-diagnostico` | las cinco escenas medidas contra la ventana |
| `04-titulo-entrada` | las tres entradas de escena, con los trazos de Fraunces |
| `05-titulo-widget` | tres widgets × cuatro entradas del widget |
| `06-titular` | la óptica `opsz 9` vs `144` y cinco tratamientos |
| `07` y `08` | diez composiciones de titular, cinco de subtítulo, ocho y seis entradas |
| `15-fondo-composicion` | el fondo definitivo: seis composiciones, reloj, deriva y barrido de 24 h |

---

## Registro de implementación

Las tareas 1-7 se implementaron sobre `main`, un commit por tarea, sin desviaciones del spec que
merezcan registro propio (a diferencia de la fase A, aquí los números se sostuvieron tal cual).
Lo que sí deja rastro es el cierre (tarea 8): los ocho gates de `measure-caelestia-titulo.py` se
rompieron uno por uno a propósito, cada uno confirmado en rojo contra el fallo exacto que dice
cazar, y revertido con diff limpio antes de pasar al siguiente. Es la misma disciplina que pagó la
fase A — **ningún gate se da por bueno sin haberlo visto dar rojo** — y aquí los ocho la superaron:

1. **Óptica.** `.cae-tit .cae-ln` apuntado a `--cae-display-axes` (el token del shell, `opsz 9`) en
   vez de `--cae-display-axes-cartel` (`opsz 144`). Rojo inmediato: "el titular usa opsz 144" cae
   a `opsz 9` — la marca de la barra, que no se tocó, siguió en verde, confirmando que los dos
   tokens son de verdad independientes y no uno reciclado con casos especiales.
2. **Compila.** Un `;` de más en `caelestiaFiguras.ts` **no basta cualquiera**: `float t = uTime *
   0.28;;;` sigue siendo GLSL válido (sentencias vacías) y no rompe nada. El punto real es partir
   una lista de argumentos — `vec3 col = tono(0;);` — que sí falla a compilar. Con eso roto,
   `CURRENT_PROGRAM` da `null` y el gate de movimiento cae en cascada a 0 %: es exactamente el
   síntoma que el spec ya anotaba (`## Los gates`, punto 5) y confirma por qué la aserción de
   compilación tiene que ir separada de la de movimiento, no inferirse de ella.
3. **Se mueve.** Aislado del punto anterior: con el shader compilando bien pero
   `shaderBackground.ts` forzado a `draw(0)` en vez de `draw((timestamp - start) / 1000)` dentro
   de `animate()`, "compila" se mantuvo en verde y "se mueve" cayó solo a 0.0 % (piso 10 %) — la
   prueba de que las dos aserciones cazan fallos distintos y no se solapan.
4. **Barrido de 24 h.** La primera rotura intentada — subir `--cae-wall-3` (el token CSS que
   genera `caelestia.color.ts`) a 0.70 de noche — **no movió la aguja**: ese token solo alimenta
   `--bg-fallback`, un degradado CSS detrás del lienzo, no algo que el lector de píxeles WebGL
   pueda ver. El wall-3 que de verdad pinta el fondo vive **duplicado** en
   `caelestiaFiguras.ts::rampaAt()` (cuarto elemento del array de rellenos, `0.375` de noche).
   Subido a `0.7` ahí, un barrido reducido de horas oscuras (00:00, 02:00, 04:00, 22:00, 23:00,
   23:45 — no las 96 muestras completas del arnés oficial, por presupuesto de tiempo) dio
   2.13:1 a las 23:00, muy por debajo del piso AA 4.5:1. Queda anotado porque es una trampa real:
   hay dos sistemas de color con el mismo nombre de rol y solo uno alimenta el shader.
5. **Justificación.** `linea.getBoundingClientRect().width` en vez de `Range().getBoundingClientRect().width`
   reprodujo el fallo palabra por palabra que ya describía el comentario del código: las tres
   líneas salen con el **mismo** tamaño de fuente (90.7372 px las tres) porque la caja de bloque
   del `<span>` mide el contenedor, no el texto — y la diferencia de ancho salta de 2.9 px a
   593.5 px (tope del gate: 4 px). El bloque "parece" justificado y no lo está.
6. **Cabe.** Quitar el `while` que estrecha `objetivo` en `justificarTitular` hizo que "aire bajo
   el pie" pasara de 12 px a **-31 px**: el bloque pisa el dock. Coincide con los dos
   desbordamientos de 138 y 142 px que el spec ya documentaba (`## Los gates`, punto 2) — el
   bucle de estrechado no es cosmético, es lo único que evita ese choque.
7. **Anti-mock.** Añadir `wfila("Repositorios públicos", "2")` al widget (un dato que no existe en
   ningún sitio de `content.ts`) tumbó la única aserción negativa del arnés: "el widget no inventa
   datos derivados". El resto de literales, sin tocar, siguieron en verde.
8. **Movimiento reducido.** Neutralizar la guarda de `matchMedia("(prefers-reduced-motion:
   reduce)")` en `montarEntrada` (`if (false)` en vez del `if` real) dejó la terminal en
   `display: flex` y la firma en opacidad 0 con `reduced_motion="reduce"` activo — ambas
   aserciones cayeron. Sin la guarda, la escena entera depende de que GSAP corra la timeline
   completa, que es justo lo que el modo reducido tiene que evitar.

Tras las ocho reversiones, `git diff` sobre el árbol quedó vacío en cada una (no solo al final) y
el arnés oficial completo volvió a dar **0 fallo(s)**.

**`verify.py` (el gate de todo el repo) sale en código 1**, pero por un motivo ajeno a esta fase:
`check_spec_plan_consistency()` señala dos specs de OTRAS fases —
`docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md` (dice "implementado" con su plan
sin marcar) y el plan de maquetado de la fase B2
(`docs/superpowers/plans/2026-08-26-caelestia-quien-soy-maquetado.md`, sin spec que lo reclame) —
que ya estaban así en `main` antes de esta rama (confirmado con `git show main:...`). No es una
regresión de B1 ni de este spec, y arreglarlas queda fuera del alcance de ficheros de esta fase:
que quede anotado aquí para que nadie las persiga pensando que las causó el Título.

**Móvil se confirmó roto, tal y como este spec ya anticipaba** (`## Lo que queda fuera`): a
390×844 el titular se desborda del viewport — la medida de justificación es un objetivo fijo de
1080 px sin salto a viewport estrecho, así que en las capturas reales las líneas salen cortadas
("Co", "que", "n") y la columna de cifras se solapa con el texto del titular. Es lo esperado, no
una regresión que perseguir.

## Gates de crítica

**`lidia-naive-tester`: verde.** 7,1/10, "Algo Claro" / "Contactaría, con matices", cero P0. El
titular ("Construyo sistemas que aguantan producción, no demos.") y la ficha de cifras concretas
son lo que la hace quedarse; nada dispara el umbral de "No contactaría". Hallazgos abiertos, sin
bloquear: P1 — la tarjeta "Ahora mismo" mezcla una fila de estudios y una de experiencia sin
encabezado que las distinga. P2 — el dato del semestre aparece dos veces (widget y columna de
cifras), no hay ningún botón con texto tipo "contáctame" (solo iconos), y la disponibilidad se
anuncia dos veces (pastilla + tarjeta). Ninguno de los tres alcanza el umbral de tres versiones
para escalar a P0 automático — todos son hallazgos nuevos de esta v12.

**`vera-art-director`: BLOCK inicial, 6,36/10 contra el gate de 7,5 — P0 arreglado, veredicto no
repetido tras el fix.** El hallazgo dominante (F-001, P0) era estructural, no de acabado: la regla
genérica de panel de la fase A (`main[data-cae-track] > *`, pensada para las cuatro escenas que sí
son "aplicaciones" con ventana) le daba a Título el mismo `background: var(--cae-elev-1)` opaco que
a las demás — medido, 78,04 % de cobertura opaca del viewport, idéntico en claro y oscuro. El fondo
de figuras al que esta fase dedica su sección más larga solo asomaba en un marco de 14–84 px.
Contradecía la premisa central del spec ("el escritorio desnudo", `## La decisión de partida`) con
una causa de una sola regla, así que se corrigió antes de aceptar el gate, no después: una excepción
de mayor especificidad para `[data-scene="hero"]` que solo toca `background` (revisada, con
comentario explicando el porqué de la excepción, sin fuga a las otras cuatro escenas ni a Vice ni a
Hyprland, confirmada con el arnés oficial completo en 0 fallos tras el cambio).

Quedan tres hallazgos de acabado, no vueltos a medir tras el fix (no cambian con él) y aceptados
como conocidos, en la misma línea que los P1 de Vice y de la fase A:
- **F-002 (P0 por recurrencia, fuera de alcance de B1).** Ocho tamaños de fuente sueltos
  (9–30 px) en el widget/firma/cifras, sin escala de tokens. Es la 5ª vez que este patrón aparece
  entre Vice, Hyprland y la fase A de Caelestia — un problema de todo el proyecto, no algo que B1
  pueda resolver solo sin tocar los otros temas.
- **F-003 (P1).** Seis de siete valores de padding/gap del widget caen fuera de la rejilla 4/8 px.
- **F-004 (P2).** El eje `wght 700` de Fraunces se repite tres veces como literal en vez de como
  token.

Aceptado explícitamente: el P0 estructural (F-001) está corregido y verificado; F-002/F-003/F-004
quedan como decisión de producto/deuda conocida, documentada aquí para que quien retome B2–B5 no
las redescubra desde cero.
