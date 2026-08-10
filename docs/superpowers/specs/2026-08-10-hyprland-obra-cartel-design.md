# El cartel — la obra en Hyprland deja de ser un acordeón y pasa a ser cinco titulares

Estado: pendiente de plan
Plan: `docs/superpowers/plans/2026-08-10-hyprland-obra-cartel.md`
Fecha: 2026-08-10
Alcance: **solo el tema Hyprland**. `[data-scene="obra"]` (`src/sections/obra/projectScene.ts`,
bloque `LA TIRA DE EXPOSICION` de `src/themes/themes.css`, `src/themes/hypr.choreography.ts`).
**Vice no se toca** (cerrado el 2026-08-05). **Caelestia no se toca**: se comprueba que sigue
idéntico. `src/style.css` **no se edita**: su tratamiento de galería se anula localmente bajo
`:root[data-theme="hyprland"]`, porque Vice depende de él.
Contenido: **`src/data/content.ts` no cambia**. Toda cadena sale literal de ese fichero.

Prototipos aprobados por Aoshi, medidos y con los números de este documento:
- Escritorio: `.superpowers/brainstorm/2704850-1786371390/content/obra-titular-z9.html`
- Móvil y tableta: `.superpowers/brainstorm/2704850-1786371390/content/obra-movil-m5.html`

---

## Diagnóstico — por qué el dispositivo actual se retira

1. **El gesto está gastado en tres sitios.** La obra abre por *revelado según la escena en curso*
   (bloque *"el pliegue: solo el abierto muestra su contenido"*), que es literalmente lo que hace la hoja de contactos — comentario
   propio en `themes.css`: *"La exposición hace de navegación: la escena en curso es la única
   revelada"*. Y el *mosaico que redimensiona* ya se descartó para "Quién soy" **por repetir este
   mismo carril** (spec de la placa, tabla de descartes).
2. **Abandona el patrón bajo 821 px.** el bloque *"Bajo 821px o con movimiento reducido"* convierte el carril en una pila
   vertical genérica. Es exactamente lo que el encargo de la placa prohibía.
3. **Los títulos se cortan.** Un panel comprimido mide ~168 px y obligó a `-webkit-line-clamp: 2`
   más reducción de cuerpo (regla `[data-scene="obra"] .display-lg` del bloque de la tira). El título es el dato más importante de la
   ficha y es el que peor se lee.
4. **El hueco de la imagen es prestado.** La galería usa el tratamiento genérico de
   `.gallery-item` / `.gallery-caption` de `src/style.css` — tarjeta de 300 px, borde de 1 px, `border-radius`, hover
   `translateY(-3px)` y rótulo en degradado sobre la imagen. Se diseñó para Vice, que además lo
   reviste aparte (reglas `:root[data-theme="vice"] .gallery-item`). Hyprland no reviste nada y hereda el aspecto base.
   Petición explícita de Aoshi en esta sesión: la imagen necesita cuadro propio.
5. **Cuatro paneles comprimidos no dicen nada.** De cinco proyectos, cuatro ocupan pantalla sin
   aportar más que un título recortado.

---

## Direcciones descartadas, y por qué

Se registran porque el coste de volver a proponerlas es alto.

| Dirección | Motivo |
|---|---|
| La pila maestra (master/stack de un gestor por mosaico) | Construida y descartada al mirarla. El maestro acumulaba diez bloques y se leía sobrecargado; ninguna de las dos versiones aligeradas (maestro callado, maestro partido) lo salvó. |
| El maestro partido en dos ventanas | La captura quedaba en columna vertical de 310×804 y una captura de interfaz **siempre es apaisada**: se veía un recorte central que no cuenta nada. |
| El espacio de trabajo (un proyecto por escritorio, plano que desliza) | Carrusel con pestañas numeradas — la misma familia que ya se descartó en la placa por "resultado por defecto". |
| El pliego (cinco fotogramas a página completa) | Sin gesto. Correcto y olvidable. |
| La persiana (cinco lamas que giran de problema a sistema) | Idea fuerte y descartada por Aoshi tras verla viva. Cabía muy poco por proyecto: cuatro datos y una franja. |
| El canal (la lista se abre en canal y sube la ficha) | Ídem. |
| La letra inundada (la captura dentro de los glifos, por corte lateral, por nivel o tramada) | El cartel tipográfico se aprueba; **meter la imagen dentro de las letras se rechaza explícitamente**. La trama de brasa a dos tintas queda registrada como tratamiento válido por si alguna vez hace falta. |
| La captura como franja bajo el titular, del ancho del título | Obliga a reservar 190 px permanentes o a aceptar un salto de maqueta en cada hover. |
| La captura en ventana fija a la derecha | Deja un hueco muerto grande bajo la imagen. |
| La captura de fondo a sangre, tramada | El texto se apoya sobre una imagen distinta en cada hover: contraste variable e imposible de fijar. |
| Hover de peso variable (`wght` 600→800 en ola) | Funcionaba y se midió (`"wght" 600` → `"wght" 668` en la primera letra a 70 ms con la última intacta), pero Aoshi pidió otro. En su primera versión además ensanchaba la palabra ~10 px y empujaba la maqueta. |
| Hover por corte, por volteo de letra y por apertura de interletraje | Comparados en vivo contra el relevo. El de apertura además crece ~30 px y empuja. |

---

## Dirección elegida — el cartel

La sección deja de ser cinco paneles y pasa a ser **un cartel de cinco titulares**. Los cinco
proyectos están siempre en pantalla, a tamaño de cartel, en una lista de filas separadas por
filete. La tipografía **es** el dispositivo: no hay tarjetas, ni cajas, ni radio.

### Elemento firma

**La captura viaja.** Al apuntar un titular, su captura aparece a la derecha **a la altura de ese
titular y con el alto exacto de las letras**. Al pulsarla, esa misma imagen —el mismo nodo del
DOM— crece hasta el visor grande recorriendo el camino real entre las dos posiciones. No hay una
miniatura que se apaga y un panel que aparece: hay una imagen que se mueve y crece.

### La ley de la sección

> Aquí nada se desvanece. Las cosas **se recortan** o **se relevan**. La opacidad solo entra donde
> hay una fuente de luz (el canto de brasa), nunca para presentar o retirar contenido.

Es el criterio con el que rechazar cualquier añadido futuro: si un gesto necesita un fundido para
funcionar, el gesto está mal.

---

## Composición

Números tomados del prototipo de escritorio, sobre un encuadre de **1400×820** con márgenes de
30 px arriba, 40 px a los lados y 26 px abajo. **Al portar a la sección real, las proporciones
mandan sobre los píxeles**: el encuadre pasa a ser el área de contenido de `[data-scene="obra"]`.

### Fila en reposo

| Pieza | Valor |
|---|---|
| Ordinal (`01`) | `--t-2` 16 px, peso 700, bruma, alineado al pie de la caja del título |
| Título | `--t-8` 89,85 px, peso 600, `letter-spacing: -0.042em`, `line-height: 1.12`, bruma |
| Área (`tag`) | 12 px, tracking `0.26em`, versalitas, bruma, pegada al canto derecho del bloque de texto |
| Miniatura | **144 × 90 px** — 90 px es exactamente la caja del título a `--t-8` con interlínea 1,12 |
| Filete entre filas | 1 px `--rule`, arriba de cada fila y bajo la última |

La miniatura **recorta, no reduce**: `object-fit: cover` con `object-position: 50% 0%`. A ese
tamaño una interfaz entera no se lee, así que muestra la banda superior de la captura — la que
lleva barra de título y cabeceras. La miniatura dice *"hay una captura y es de esto"*; la grande
es la que se lee.

### Estado abierto

| Pieza | Valor |
|---|---|
| Visor grande | **760 × 475** px, anclado a la izquierda, arriba a 132 px del alto del encuadre |
| Ficha | columna de **520 px** a 800 px del borde izquierdo |
| Titular elegido | sube a la primera línea y se queda de cabecera |
| Los otros cuatro | **se apartan a los bordes**, no se encogen: los de arriba salen por arriba, los de abajo por abajo, con 30 ms de escalonado |

La ficha lleva **seis bloques**, en este orden: `lead` (Instrument Serif, `--t-4`), *Qué construí*
(`solution`), *Stack* (línea de texto + fila de marcas), estado con testigo de 8×8 px, *Qué pasaba
antes* (`problem`) y un pie con *Rol* y *Periodo* separado por filete.

**Este ancho está medido, no elegido a ojo.** Con la ficha a 412 px, tres de los cinco proyectos
desbordaban el encuadre por abajo: WatchDog **+64 px**, TesisFar **+39**, «Editor de texto» **+27**.
Ensanchando a 520 (y bajando el visor de 824 a 760, que mantiene la proporción apaisada) cada
párrafo pierde una línea y los cinco terminan **entre 48 y 62 px por encima del borde**. Es margen
real, no al filo.

### Las marcas del stack

Fila de tiles cuadrados de **34 px** con filete de brasa al 42 %, radio 0, monocromas. React, Vite
y Electron llevan su silueta real; el resto, monograma en Bricolage (`Py`, `dj`, `TS`, `JS`, `N`,
`Rx`, `Z`, `GS`, `C`, `GTK`).

**Decisión y motivo:** los logotipos oficiales traen su propio color —el azul de Python, el cian de
React, el verde de Django— y meterían cinco paletas ajenas en una sección que sólo tiene tinta,
papel y brasa. Un juego monocromo uniforme además no se rompe cuando aparezca una tecnología nueva.
Si alguna vez se quieren los logos de marca en color, es un cambio de criterio, no un ajuste.

### El cuadro de la imagen

Se abandona por completo el tratamiento heredado de `.gallery-item` / `.gallery-caption` de `src/style.css`. El cuadro propio de
Hyprland:

- **Sin borde, sin radio, sin sombra, sin hover que levanta.**
- **Sin duotono.** Se probó y se descartó: una interfaz en naranja sobre naranja pierde justo la
  información que la captura venía a dar. Queda `brightness(0.96)` y un velo de `--l1` al 8 %.
- **El pie va fuera de la imagen**, en una banda sólida de tinta al fondo del visor grande, en
  bruma a 12 px. Nada de rótulo en degradado encima de la foto.
- Aparece **por corte lateral** con un canto de brasa de 3 px por delante; nunca por opacidad.

Habrá capturas reales (confirmado por Aoshi el 2026-08-10). Hoy los nueve ficheros de
`public/media/obra/*.webp` son placeholders que dicen *"CAPTURA PENDIENTE — <fichero> — placeholder,
no es captura real"*, y por eso existe la bandera `--allow-gallery-placeholder` de `verify.py`.
**El diseño no lleva estado de "captura ausente"**: el `.gallery-fallback` actual se conserva como
red de seguridad ante un fallo de carga puntual, que es su propósito legítimo.

---

## Tipografía

Escalones **discretos** por `@media`, nunca `clamp()` continuo sobre tokens de escala. Es la regla
que `CLAUDE.md` marca como "Never Do".

| Elemento | < 821 | ≥ 821 | ≥ 1200 |
|---|---|---|---|
| Título | `--t-4` 28,43 | `--t-6` 50,52 | `--t-8` 89,85 |
| Lead de la ficha | `--t-3` | `--t-3` | `--t-4` |
| Cuerpo de la ficha | 14 px | 15 px | `--t-2` 16 |
| Rótulo | 10 px < 821, 12 px ≥ 821, tracking 0,24-0,26em | | |

**Coste conocido:** partir las palabras en letras (necesario para el relevo) **pierde los pares de
kerning**, porque cada letra pasa a ser una caja `inline-block`. Los titulares quedan un punto más
abiertos que compuestos de corrido. Si se nota en el sitio real, se compensa bajando el
`letter-spacing` un par de milésimas — **no** volviendo a componer de corrido, que mataría el
dispositivo.

---

## Color y contraste

Tokens de Hyprland. Bruma `--haze` #b18c86 para lo apagado, papel #ffeae6 para lo encendido, brasa
`--l1` #ff5a34 sólo para **una** cosa: la pieza activa (el ordinal de la fila abierta, el canto que
recorre, el filete de los tiles y el enlace al repositorio). Cuerpo de la ficha en **#e8c9c2**
sólido, no en `text-paper/80`: una opacidad se calibra contra un scrim concreto y reutilizarla
entre temas es lo que este proyecto tiene prohibido.

**El contraste se mide contra el fondo real**, que no es un plano: la página lleva el shader más
`--bg-fallback`, que sube hasta #3a1008. Referencias ya medidas en el repo: `--haze` sobre tinta
6,81:1; `--haze` sobre #3a1008 5,54:1; `--l1` sobre tinta 6,61:1. **Pendiente de medir con el
arnés** en este diseño: bruma sobre el fondo real en la zona alta del cartel, donde el haz es más
brillante, y el papel del titular encendido.

---

## Movimiento

Los dos regímenes del tema y ninguno más: **corte** con `--hard` (`cubic-bezier(0.7,0,0.2,1)`) y
**atmósfera** con `--slow` (`cubic-bezier(0.16,0.84,0.28,1)`). Se fijan con `CustomEase` para que
no pueda colarse un tercero.

### Entrada — el barrido

**Una sola causa.** Una barra de brasa de 2-3 px cruza el cartel de izquierda a derecha una vez, en
**1,05 s** con `ease: none`, y todo lo demás cuelga de ella:

- Los cinco filetes **los traza la barra**: misma duración, misma curva.
- Cada letra se suelta **cuando la barra llega a su columna, no a su línea**. El retardo no se
  escribe a mano: sale de `(x de la letra / ancho del cartel) × 1,05 s`. El efecto es que la barra
  atraviesa los cinco titulares a la vez, revelándolos por columnas.
- Las letras llegan a `wght 800` y **se enfrían a 600** en 900 ms con `--slow`.
- El área entra cuando la barra pasa por su columna, que está a la derecha: la fila se cierra sola.

Es **distinto en especie** del montaje de la placa (`.placa-in`), que hace llegar celdas
desde el borde más cercano con retardo diagonal. Repetir aquel gesto aquí sería el fallo de firma
más caro de la propuesta.

### Hover — el relevo

Cada letra vive dentro de una mirilla de su propio alto (`overflow: hidden`, `height: 1.12em`) y
guarda debajo **una gemela ya encendida**. Al apuntar, la tira sube un 50 % y la letra apagada es
**sustituida** por la encendida, una detrás de otra con **24 ms** de desfase, 420 ms en `--hard`.
Al salir, el relevo vuelve **desde el final** — por donde entró. Nada se desvanece y la maqueta no
se mueve ni un píxel.

Medido en navegador a 70 ms: la primera tira ha subido 5,56 px y la última sigue en `none`. La ola
es real, no un cambio simultáneo disfrazado.

Cada letra lleva **dos transforms independientes**: `.en` para la entrada y `.rl` para el relevo.
Sin esa separación, entrada y hover se pisan.

### Apertura — Flip

La miniatura y la imagen grande **son el mismo elemento**. `Flip.getState` mide, el nodo se
reubica en el visor, y `Flip.from` anima el recorrido real, **620 ms** en `--hard`. Los otros
titulares se apartan a los bordes con 30 ms de escalonado; la ficha se escribe por líneas detrás de
un recorte (`SplitText` con `mask`, 400 ms, 45 ms de escalonado), y las marcas del stack entran por
corte lateral con 50 ms de escalonado. Al cerrar, la captura vuelve a su fila por el mismo camino.

### Qué está prohibido

- Cualquier `opacity` que presente o retire contenido.
- Bucles infinitos. El tema ya gasta su único `infinite` en el hero (`hypr-hero-idle 6s`).
- `backdrop-filter`, desenfoques, resplandores, sombras exteriores, esquinas redondeadas.
- Cualquier `--l1` que no signifique "esto está activo".
- Monoespaciada, prompts, cursores parpadeantes, rutas de fichero, badges de terminal.
- Un pin de ScrollTrigger. El cartel ocupa una pantalla y es interactivo, no scrubbed; añadir un
  pin obligaría a entrar en la escalera de `refreshPriority` y no compra nada.

---

## Por debajo de 821 px

**El mismo dispositivo, sin hover.** Cambian tres cosas y sólo tres:

1. **La miniatura está siempre puesta**, no espera al apuntado. En un móvil no hay "apuntar", y
   esconderla detrás del primer toque obligaría a tocar dos veces para ver una imagen. El toque
   hace una sola cosa: abrir.
2. **El área baja debajo del título**, porque el canto derecho lo ocupa la miniatura.
3. **El relevo se dispara al abrir**, no al apuntar. En puntero fino sigue viviendo en el hover, y
   la separación se hace con `@media (hover: hover)` — **por capacidad del dispositivo, no por
   ancho de pantalla**.

Medidas del prototipo:

| | Móvil 390×844 | Tableta 820×1024 |
|---|---|---|
| Márgenes del cartel | 58 / 27 / 44 | 70 / 57 / 54 |
| Título | `--t-4` 28,43 | `--t-6` 50,52 |
| Miniatura | 96 × 60 | 152 × 95 |
| Visor grande | 336 × 190 | 592 × 370 |
| Objetivo táctil de fila | ~86 px de alto | ~120 px |

**No se cae ningún bloque**: la ficha abierta lleva los mismos seis. La hoja abierta se desplaza
dentro de sí misma entre **27 y 85 px en móvil** y entre **43 y 74 px en tableta**, según el
proyecto — el pie de Rol y Periodo queda medio dedo por debajo del pliegue en los de texto más
largo. Es el único scroll interno que este diseño acepta.

---

## Accesibilidad

- **No es un `tablist`.** Los cinco titulares están visibles a la vez, no hay panel oculto asociado
  a una pestaña, y queremos que las cinco filas sean tabulables porque también son contenido.
- Cada fila es un `<button>` que envuelve su contenido, con un `<span class="sr-only">` al principio:
  *"Mostrar "*. Lectura: *"Mostrar HyprFinance, Finanzas personales, botón"*.
- Foco visible: `outline: 2px solid var(--l1)` con `outline-offset: -2px`. `--l1` sobre la
  superficie de la fila da 6,54:1, muy por encima del 3:1 que pide 1.4.11.
- Al abrir **no se mueve el foco**. Una región `aria-live="polite"` anuncia el cambio.
- `prefers-reduced-motion`: sin transiciones. El relevo se resuelve en un fotograma, la apertura
  también, y la barra de entrada no aparece. **El dispositivo sigue siendo el mismo**: la
  información no se degrada, sólo el movimiento.

---

## Trampas conocidas — que no se vuelvan a pagar

1. **La ficha cerrada roba el puntero.** Con `opacity: 0` el panel sigue siendo alcanzable y tapa
   las filas: el arnés se quedó 30 s intentando pulsar hasta que el navegador dijo qué elemento
   interceptaba. Lleva `pointer-events: none` en reposo y `auto` al abrir. **Estaba en las dos
   versiones del prototipo, escritorio y móvil.**
2. **`data-scene` no se toca.** Es como el sitio marca sus cinco secciones y como la coreografía las
   recorre; además `:root[data-theme="vice"] [data-scene]` reparte 202,5 px de relleno.
3. **Todo el CSS nuevo bajo `:root[data-theme="hyprland"]`.** `.obra-rail` y `.obra-track` los crea
   `src/main.ts` para los tres temas, y `scripts/measure-obra-rail.py` reimplementa la timeline del
   carril de Vice: si el track cambia de altura para todos, ese arnés no falla, **miente**.
4. **Se retira el Gesto 2 de `hypr.choreography.ts`** (*"la tira de exposicion"*) (la tira de exposición con
   `pointerenter` e `is-open`). No puede convivir con el cartel: competirían por el mismo estado en
   los mismos nodos.
5. **Verificar en el build de producción**, no en dev: el HMR de Vite corrompe las medidas de
   ScrollTrigger y miente en los dos sentidos.
6. **`page.screenshot()` perturba GSAP en headless.** El fotograma intermedio de una animación no se
   juzga por captura: se muestrea desde dentro de la página, como se hizo con el relevo.

---

## Criterios de aceptación

- `npm run build` y `npm run lint` en verde.
- `python3 scripts/verify.py` con código 0 contra su línea base.
- Capturas en 390×844, 820×1024 y 1440×900, con `?theme=hyprland`.
- Vice y Caelestia **idénticos** a `main`, comprobado con `git worktree` (nunca `git stash`).
- Contraste AA medido con el arnés **contra el fondo real**, no contra negro plano.
- Las cinco filas alcanzables con teclado, foco visible, y anuncio al abrir.
- `prefers-reduced-motion`: el dispositivo completo, sin movimiento.
- Revisión de Aoshi **en el sitio real**, no sobre capturas.
- Gates `lidia-naive-tester` y `vera-art-director` (umbral 7,5/10).

---

## Preguntas abiertas para el plan

1. **De dónde sale la miniatura.** La galería (`components/gallery.ts`) construye un carril
   arrastrable; el cartel necesita **una** imagen por proyecto. Hay que decidir si se reutiliza el
   primer `.gallery-item` vía CSS o si `projectScene.ts` expone un gancho propio.
2. **Reordenación de `projectScene.ts`.** La fila necesita ordinal, título, área y miniatura como
   hermanos directos; el resto pasa a ser la ficha. Hay que ver cuánto se puede resolver con CSS
   antes de tocar la estructura que comparten los tres temas.
3. **El ordinal gigante actual** (`projectScene.ts`, `clamp(7rem,26vw,22rem)` a
   `paper/[0.06]`) es un dispositivo de Vice. En el cartel se sustituye por `01` a 16 px. Hay que
   ocultarlo sólo en Hyprland.
