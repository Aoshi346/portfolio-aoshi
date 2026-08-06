# La hoja de contactos — la cortinilla de Hyprland deja de ser una lista y pasa a ser cinco planos

Estado: pendiente de plan
Plan: `docs/superpowers/plans/2026-08-06-hyprland-cortinilla-hoja.md`
Fecha: 2026-08-06
Alcance: **solo el tema Hyprland**. El disparador (`.scene-nav-trigger`) y la cortinilla
(`.scene-index`), que hoy son el mismo componente vestido igual en los tres temas. **Vice no se
toca** (cerrado el 2026-08-05). **Caelestia no se toca**: se comprueba que sigue idéntico.
Sustituye al handoff `2026-08-06-hyprland-scenenav-handoff.md`, que queda como registro de cómo se
llegó aquí.

Prototipo aprobado por Aoshi, medido y con los números de este documento:
`.superpowers/brainstorm/2163099-1786029203/content/cortinilla-h-v3.html`.

## Por qué

La navegación de escenas funciona y su accesibilidad está resuelta y probada en los tres temas.
El problema es de identidad: `.scene-index` es **hoy idéntica en estructura y piel en los tres
temas**. Vice le quita la caja al disparador y le añade una marca de registro, pero el panel —telón
oscuro, fundido por `clip-path`, cinco renglones numerados— nunca se re-skinea. Hyprland tiene
cuatro líneas propias. Aoshi: "ya Vice usa ese selector de sección, me gustaría que la cortinilla
cambie para Hyprland".

Y el disparador es, además, **el único sitio donde Ascua se contradice**: caja con radio 5px y
borde falso por `box-shadow`, amparada en una excepción ("radio 0 en todo salvo la navegación") que
se escribió para proteger una pastilla concreta. Si la pastilla desaparece, la excepción se queda
sin nada que proteger y se retira con ella.

El encargo explícito fue **otro patrón de interacción**, no un reskin del telón. La opción
conservadora ("mismo patrón, piel propia") se descartó en la sesión anterior.

## Qué se construye

### La hoja

El índice deja de ser cinco renglones de texto y pasa a ser **cinco fotogramas en rejilla**. Cada
uno es un encuadre de 1px de filete en proporción **16:10** —la de la pantalla del sitio— con una
**silueta** de su escena dentro: la estructura y las proporciones reales, sin el detalle fino.

| # | Escena | Qué se reconoce en la silueta |
|---|---|---|
| 01 | Título | El nombre a 96px a sangre, la regla vertical del rótulo girado, el filete con dos extremos |
| 02 | Quién soy | La ficha con borde, el avatar redondo, la escalera rol / base / ahora / estudia |
| 03 | Obra | Las cinco columnas con filete de 1px y el numeral fantasma detrás de cada una |
| 04 | Créditos | Los grupos de palabras bajo sus rótulos, y el panel de detalle con la marca |
| 05 | Fundido | "Hablemos", y las cuatro vías separadas por filete con guion corto antes del valor |

**El haz cruza los cinco.** Es lo único que aparece en todas las escenas del sitio real, y es lo
que hace que la hoja se lea como cinco planos de la misma película en vez de cinco iconos.

Esto resuelve, de paso, un hallazgo de producto que sobrevivió tres revisiones de usuario: los
nombres de cine no comunican su contenido. El descriptor de texto lo parcheaba; un fotograma con
las bandas del cierre lo comunica. **El descriptor sigue estando siempre visible** — ver
"Restricciones".

Primera versión descartada al enseñarla: las miniaturas dibujadas **a fidelidad de captura**, con
todo el texto pequeño real. Se reconocían, pero cinco composiciones densas simultáneas competían
con el pie por la atención. Aoshi: "no debe ser fiel 100%, puedes hacerlo minimalista, solo
similar."

Y una corrección anterior a esa, anotada para no repetirla: las primeras miniaturas eran
**inventadas** —una tira de luces para obra, lámparas en cadena para créditos— porque se dibujaron
desde el spec de Ascua y no desde el sitio. Se rehicieron desde capturas reales con
`?theme=hyprland`. Ninguna se parecía a lo que hay.

### La exposición hace de navegación

La escena en curso es **la única revelada**. Las otras cuatro quedan veladas al 58% y se revelan al
apuntarlas. El vocabulario del tema —luz, exposición— haciendo trabajo de navegación en vez de
decoración.

### El disparador: T-C, el pie del fotograma

Sin caja. Número pequeño arriba, nombre en display debajo, y un filete de 1px encima que se
calienta **de derecha a izquierda** al apuntar — el mismo sentido en el que está anclado. Es una
celda de la hoja que abre: el disparador es el estado cerrado de su propio dispositivo.

**Tiene dos estados y el cambio es informativo, no decorativo:**

| | línea superior | nombre |
|---|---|---|
| cerrado | `03` | `Obra` |
| abierto | `Esc` | `Cerrar` |

Al abrir, el filete se queda encendido —el estado se ve sin leer nada— y el rótulo **se corta y
sube**, no se funde: el corte es la gramática del tema. La línea de arriba pasa a decir qué tecla
cierra, que es información real que hoy no está en ninguna parte.

Los 44px de área de toque los da `min-height`, no una caja visible.

### Movimiento

**Apertura, 480ms.** Una barra de luz cruza de izquierda a derecha y cada fotograma **se expone a
su paso**: su propio recorte se abre cuando la barra le llega al borde izquierdo, con un golpe de
luz que sobreexpone y asienta.

Los escalonados no son un ritmo elegido a ojo, son geometría: rejilla de 1128px centrada en 1216
(margen 44, paso 228), barra a 1216px/480ms = 2,533 px/ms, luego la barra llega a cada fotograma a
los **17 / 107 / 197 / 287 / 377 ms**. Cada exposición dura **140ms** mientras la barra tarda 85 en
cruzar un fotograma, así que el revelado **asienta por detrás del instrumento y nunca por delante**.

| momento | qué | cuánto | curva |
|---|---|---|---|
| barrido (barra + borde del telón) | recorrido completo | 480 ms | `linear` |
| exposición de cada fotograma | recorte propio, escalonado por geometría | 140 ms | `cubic-bezier(.7,0,.2,1)` |
| golpe de luz | sobreexpone y asienta | 300 ms | `cubic-bezier(.7,0,.2,1)` |
| cierre — fotogramas | orden **inverso**, escalonados 20 ms | 110 ms | `cubic-bezier(.7,0,.2,1)` |
| cierre — telón | se recoge detrás del contenido | 200 ms | `cubic-bezier(.7,0,.2,1)` |
| hover de un fotograma | velado → revelado | 200 ms | `cubic-bezier(.7,0,.2,1)` |
| cambio de rótulo del disparador | corte y subida | 200 ms | `cubic-bezier(.7,0,.2,1)` |

**La apertura va lineal y es deliberado.** Ascua declara los cortes en `cubic-bezier(.7,0,.2,1)`,
pero una barra de luz que cruza es un instrumento físico a velocidad constante: con `ease-out`
frenaría al llegar al borde y volvería a leerse como un panel de interfaz. **El instrumento va
lineal; los eventos que provoca llevan la curva del tema.** Es la única desviación de la tabla de
movimiento de Ascua y queda escrita aquí para que no se "corrija" por descuido.

**El cierre no es el barrido al revés.** La barra es un gesto de un solo sentido —un paso de
exposición— y rebobinarla sería otra metáfora, más débil, y obligaría a ver la animación entera
para algo que se quiere terminar ya. El contenido se va antes que la sábana. Se mantiene la
asimetría que ya declara la cortinilla actual ("entrar puede ser una ceremonia, salir nunca") sin
heredar sus 140 ms, calibrados para otra curva y otro tema.

**CSS, no GSAP.** Con el recorte y la barra en la misma unidad relativa del mismo eje, el navegador
las interpola en el mismo fotograma; GSAP no aportaría sincronía y sí un ciclo de vida que
mantener. Además el criterio de aceptación 5 de la cortinilla actual existe precisamente porque
`transitionDuration` es determinista y verificable sin cronómetro. Si en implementación aparece un
motivo real para GSAP, la condición no negociable es `fromTo` con los dos extremos escritos a mano.

### Movimiento reducido

Con `prefers-reduced-motion: reduce` la hoja aparece y desaparece con duración 0 y sin escalonado,
y **la barra de luz se retira por completo** (no se acelera): un elemento que atraviesa la pantalla
es en sí mismo el efecto de movimiento, no solo su duración. Acelerarlo a 1ms sigue siendo algo que
cruza la pantalla a ojos de quien pidió `reduce`. Foco, `Esc`, clic fuera y bloqueo de scroll no
cambian: son lógica de `sceneNav.ts`, independiente del CSS de transición.

### Cambio de contenido

`Quién es` → **`Quién soy`** en `src/data/content.ts`. El rótulo de la propia escena en el sitio
también dice `QUIÉN ES`: **los dos cambian juntos** o el índice y la escena se contradicen.

## Restricciones

### El descriptor no puede pasar a hover

Sigue siempre visible. Esconderlo detrás de un hover reabriría un hallazgo ya cerrado —los nombres
de cine no comunican su contenido, y el descriptor fue la solución que permitió conservar la
personalidad— y en táctil no hay hover: en móvil desaparecería del todo. Las miniaturas **añaden**
comprensión, no la sustituyen.

### Un `<a>` por fotograma, no dos elementos

Cada fotograma es **un único `<a href="#id">`** que envuelve miniatura y pie. Si la miniatura o el
pie fueran interactivos por separado, Tab daría 10 paradas en vez de 5 y rompería un criterio ya
probado. La miniatura va `aria-hidden="true"` en su envoltorio: es decorativa y además contiene
fragmentos de copy que un lector de pantalla leería fuera de contexto y duplicados respecto al pie.
`aria-current="true"` en la escena en curso, como hoy. `role="dialog" aria-modal="true"` se
mantiene: la rejilla cambia la composición, no el modelo de interacción.

### Nada de `order` para adelantar contacto

El quinto fotograma va **el último en el DOM** y toma `grid-column: 1 / -1`. Adelantarlo con
`order` para "priorizar" contacto rompería la correspondencia entre el recorrido de Tab y lo que se
ve, que es la trampa de foco de WCAG 2.4.3 — y es fácil caer en ella justo aquí, porque contacto es
el que más se quiere que se pulse.

### Fuga a los otros dos temas

`.scene-nav-trigger` y `.scene-index` no son compartidas entre escenas de un tema: son compartidas
entre **los tres temas completos**, y el disparador vive fuera del árbol de cualquier escena. No
hay un `[data-scene]` que lo contenga por accidente. Cualquier regla nueva sin
`:root[data-theme="hyprland"]` en el selector se filtra a Vice y Caelestia de inmediato. Nodos DOM
nuevos en `sceneNav.ts` (TypeScript compartido) van con `display: none` por defecto, reactivados
solo bajo Hyprland — el patrón que ya validó el hero.

### Sin scroll interno en el panel

A 390 la hoja **cabe** (ver criterio 3). Si en algún cambio futuro dejara de caber, la salida es
reducir proporción o hueco, **no** introducir scroll dentro del panel: un contenedor con scroll
propio mientras Lenis está bloqueado a nivel de documento es superficie nueva que el doble cerrojo
actual no cubre. Si no hubiera más remedio, exige `overscroll-behavior: contain`, o en iOS el
gesto táctil se filtra a la página de detrás pese al `overflow: hidden`.

## Criterios de aceptación

Cada uno con su instrumento y su umbral.

1. **La hoja no adelanta a la barra.** Muestreo del `clip-path` calculado del telón y de cada
   fotograma en cada `requestAnimationFrame` durante la apertura, desde dentro de la página.
   Umbral: el borde derecho del contenido revelado de cualquier fotograma **nunca** supera el borde
   del telón. Medido en el prototipo: máximo adelanto **−15 px** (siempre por detrás, entre 15 y
   84 px). Antes del arreglo llegaba a **+83 px** a mitad de apertura y se retrasaba al final: iban
   descoordinados en los dos sentidos.

   **No se mide con capturas.** `page.screenshot()` en headless perturba el compositor y salta la
   animación hacia delante — en este mismo trabajo un fotograma intermedio de cierre salía ya
   cerrado a los 45 ms de una animación de 200. Es la trampa ya documentada en `verification.md`.

2. **Tiempos declarados.** `transitionDuration` / `animationDuration` de cada pieza contra la tabla
   de Movimiento. Determinista. El cronómetro desde el clic hasta `transitionend` es solo
   comprobación de sanidad, con margen explícito de +150 ms.

3. **390 × 844 sin scroll interno.** Instrumento: `getBoundingClientRect` y `scrollHeight` del
   panel. Umbrales medidos en el prototipo, que deben mantenerse: fotogramas de **172 × 197**, el
   quinto **356 × 201**, rejilla de **621 px** de alto sobre 844 disponibles. Ningún descriptor
   desborda su columna (`scrollWidth <= clientWidth` en los cinco).

4. **Área de toque del disparador.** `getBoundingClientRect` sobre el propio botón. Umbral:
   ≥44×44 px, sin caja visible. Medido en el prototipo: **104 × 44,5**. Se mide la caja del botón,
   no un pseudo-elemento ampliado: un `::after` con `inset` negativo agranda la zona clicable pero
   no mueve lo que el criterio mide.

5. **Cinco paradas de Tab, no diez.** Playwright con teclado real: Tab recorre los cinco fotogramas
   y vuelve al primero; `Esc` cierra y devuelve el foco al disparador; `aria-expanded` refleja el
   estado. Umbral: exactamente 5 paradas dentro del panel.

6. **Orden de tabulación = orden visual.** El quinto fotograma es el último tanto en el DOM como en
   pantalla. Umbral: 0 usos de `order` en la rejilla.

7. **Contraste del pie.** Los tres textos del pie (número, nombre, descriptor) sobre el fondo del
   fotograma, muestreados **sobre el píxel compuesto y con recorte ajustado al glifo**, no a la
   caja del bloque — medir una caja ancha y casi vacía devuelve la variación del fondo y ya dio un
   falso 1,5:1 sobre un texto que estaba en 7,9:1. Umbral: ≥4,5:1.

   Este es el criterio con más riesgo real: el descriptor ya era **el ratio más ajustado de todo el
   tema (4,74:1 contra un umbral de 4,5)** y aquí cambia de superficie. El color de `.h-foot .bl`
   se declara explícitamente y se calibra contra **este** fondo; no se hereda una opacidad de otro
   sitio, que es una regla ya escrita del proyecto.

8. **Las anclas no se mueven.** `scripts/measure-nav.py` sin cambios de umbral: 15 de 15 a ±8 px en
   los tres temas.

9. **Los otros dos temas, intactos.** `verify.py --theme vice` y `--theme caelestia` antes y
   después, además de `--theme hyprland` y una pasada `--reduced`. Umbral: 0 fallos nuevos sobre la
   línea base. Vice está cerrado y aceptado con su gate BLOCK: cualquier diferencia es un defecto
   de este trabajo.

10. **Movimiento reducido.** Con `reduced_motion="reduce"`: la hoja abre y cierra con duración 0, la
    barra de luz **no existe** (no basta con que sea rápida), y el criterio 5 se sigue cumpliendo
    entero.

11. **Escala tipográfica.** `scripts/measure-type-scale.py`: 0 fallos nuevos sobre su línea base.
    Cualquier tamaño de la hoja debe ser un escalón declarado, no un valor continuo.

12. **Build y lint verdes**, `verify.py` con 0 fallos nuevos sobre su línea base, y capturas reales
    a 1440×900 y 390×844 con `?theme=hyprland`. En esta máquina el chromium de Playwright no está
    descargado: hay que lanzar contra `/usr/bin/google-chrome`.

13. **Gates finales**: `lidia-naive-tester` y `vera-art-director` (umbral 7,5/10), y revisión de
    Aoshi **sobre el sitio real**, no sobre capturas.

## Riesgos

**Las miniaturas pueden envejecer.** Son siluetas dibujadas a mano: si una escena cambia de
dispositivo y su fotograma no, la hoja miente en silencio. Es el mismo trato que ya tienen los
descriptores de `content.ts` y las constantes del carril de obra: se acepta la copia y se vigila.
El arnés debe comprobar que hay exactamente cinco fotogramas y que ninguno está vacío; que se
parezcan a su escena es responsabilidad de quien cambie la escena.

**Cinco miniaturas compitiendo pueden ralentizar el escaneo.** Cada una por separado se lee bien,
pero cinco a la vez es otra cosa, y la persona de referencia decide en menos de dos segundos. No se
puede predecir desde el HTML: `lidia-naive-tester` debe medir explícitamente **tiempo hasta la
primera pulsación correcta** sobre esta rejilla, no solo dar una impresión estética.

**El golpe de luz puede leerse como efecto gratuito.** Está justificado por la metáfora —una hoja
de contactos se expone— pero si en la revisión sobre el sitio real no aporta, se quita: es la
pieza más prescindible de todo el conjunto y quitarla no rompe nada.

## Fuera de alcance

Caelestia, que sigue con la cortinilla compartida. Vice, cerrado.

Quedan en los prototipos de `.superpowers/brainstorm/2163099-1786029203/content/`, por si alguna
vez se quiere volver: las cinco direcciones que se exploraron y no se eligieron —el carrete (rail
lateral en cuña), el corte (telón a pantalla completa con cuña viajera), la tira (acordeón de cinco
luces), el regulador (atenuador arrastrable) y la ficha (el disparador creciendo en su sitio)— y
los ocho disparadores descartados: el filamento, la brasa, el escalón, el vúmetro, la cuña, el
corchete, el fotograma y la tira.

El barrido no está en esa lista: se exploró como dirección propia y acabó **absorbido** como gesto
de apertura de la hoja, que es donde hace más trabajo.
