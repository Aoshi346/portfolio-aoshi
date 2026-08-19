# La luz de mano — el cursor de Hyprland no es un objeto, es una fuente de luz

Estado: en ejecucion
Plan: `docs/superpowers/plans/2026-08-19-hyprland-cursor-luz.md`
Fecha: 2026-08-19
Alcance: **solo el tema Hyprland**. Módulo nuevo `src/components/hyprCursor.ts`, bloque nuevo en
`src/themes/themes.css` bajo `:root[data-theme="hyprland"]`, y la puerta de montaje en
`src/main.ts`. **Vice no se toca** (cerrado el 2026-08-05): `src/components/viceCursor.ts` se lee
como contrato y no se edita. **Caelestia no se toca**: se comprueba que sigue sin cursor propio.
Contenido: **`src/data/content.ts` no cambia**. Este dispositivo no escribe ni un carácter en pantalla.

Prototipo aprobado por Aoshi, medido y con los números de este documento:
`.superpowers/brainstorm/2240085-1787159437/content/cursor-simple.html` (dirección **P**, tecla 2)

---

## Diagnóstico — once propuestas y por qué caen diez

El encargo llegó como "cursor animado temático, dispositivo con estados por sección". Se
recorrieron tres rondas y once direcciones. Las diez descartadas no fallaron por ejecución: cada
tanda murió por una razón distinta y las tres razones son el diseño de esta.

**Ronda 1 y 2 — A, B, C, D, E: sosas.** Compartían esqueleto sin que nadie lo hubiera decidido:
un filete vectorial de 1px que anota la diana. Compuerta, recorte, foco, hilo, marcas de la calle
— cinco geometrías del mismo material. Un contorno de 1px no emite luz; es un alambre. En un tema
que se llama **Ascua** y cuya tesis es *luz con canto*, ninguna de las cinco era luz.

**Ronda 2 bis — F, G, H: fuera de escala.** El ascua con estela de chispas, la quemadura que abre
un agujero en el elemento, el arco eléctrico. Corregían el material pero se pasaban al otro lado:
la estela roza la atmósfera —el tic que Aoshi lee como generado—, la quemadura completa acaba
siendo un hover invertido corriente, y el arco desaparece en cuanto el puntero está *dentro* de la
diana, que es donde está el 100% del tiempo útil.

**Ronda 3 — I, J, K: confusas.** El cuentahílos de `hyprpicker`, el borde `col.active_border`, el
selector de región de `slurp`. Auténticas y reconocibles para quien usa el compositor, y por eso
mismo el fallo: **añadían un segundo idioma a la pantalla**. `1238 × 74`, `01 · TITULAR DE OBRA`,
`#ff5a34`. La persona que evalúa este portfolio es Marta Ruiz, reclutadora no técnica, dos
segundos de atención: para ella esos números no son información, son ruido con aspecto de error.
Un cursor no puede tener manual.

**La regla que sale de las tres:** lo creativo tiene que vivir en **el movimiento y el material**,
que se entienden antes que las palabras, y no en aparato añadido. Y el criterio de éxito no es
"llama la atención" sino "un desconocido sabe qué se pulsa sin que nadie se lo explique".

## Tesis

**El cursor de Hyprland no dibuja nada: ilumina.**

Se lleva una luz en la mano. El charco de luz existe **solo dentro de lo que se puede pulsar**,
recortado a canto vivo por el borde del propio elemento, y sigue a la mano por dentro de él. Sobre
texto corrido no se enciende nada y manda el cursor del sistema.

Tres razones por las que esta y no otra:

1. **No hay vocabulario que aprender.** «Lo que se ilumina responde» es anterior al lenguaje. Cero
   texto, cero números, cero instrumental.
2. **Es la tesis del tema hecha literal.** Luz con canto: la luz es real y difusa en el centro, y
   termina en el filo exacto del elemento. El corte duro es lo que la separa de un resplandor.
3. **Presume del fondo en vez de taparlo.** El shader de Ascua es lo mejor que tiene el tema. Un
   objeto flotando encima lo tapa; una luz que se enciende dentro de una fila lo aprovecha.

## Anatomía

Dos piezas, nada más:

| Pieza | Qué es | Cuándo existe |
|---|---|---|
| **La mano** | Punto caliente de 3,2px en `--catch` con anillo exterior de 1px en `--void` | Siempre que el puntero esté en zona propia |
| **El charco** | Degradado radial centrado en el puntero, recortado al `rect` de la diana, más el canto del elemento a 1px en `--l1` | Solo con diana bajo el puntero |

El anillo oscuro de la mano no es decoración: garantiza contraste del punto contra cualquier
fotograma del shader sin depender del fondo. Es el mismo recurso que usa `viceCursor.ts`.

## Estados

| Estado | La mano | El charco | Nota |
|---|---|---|---|
| Reposo (sin diana) | Punto de 3,2px | apagado | La página no reacciona |
| Sobre pulsable | Punto de 3,2px | potencia 1, radio `max(alto × 2,4; 120)px` | La luz sigue a la mano dentro del elemento |
| Pulsando | Punto de 2,4px | radio × 1,25 | El punto se contrae y la luz se abre: gesto de presión |
| Activo (`aria-pressed`) | igual | igual | El estado activo lo dice el elemento (`--l3`), no el cursor |
| Zona nativa | apagado | apagado | Vuelve el cursor del sistema en un fotograma |
| Movimiento reducido | no se monta | no se monta | Ni módulo ni lienzo |
| Táctil / puntero grueso | no se monta | no se monta | No hay hover que disparar nada |

La potencia del charco se interpola (`pot += (meta - pot) * 0.22`), la mano no: la posición del
puntero se escribe sin suavizar. Un cursor con inercia en la posición miente sobre dónde está el
ratón, y en los créditos hay 23 dianas contiguas donde eso se nota como retraso.

## Reparto de señal — qué conserva el cursor del sistema

Idéntico al criterio ya cerrado en Vice, porque el problema es el mismo: sustituir el puntero es
legítimo, borrar las otras señales del sistema no.

- **Se sustituye** (`cursor: none`): `button`, `a[href]` interno, y a mano `.scene-nav-trigger` y
  `.scene-index-row`.
- **Se conserva**: la I de texto en `p`, `li`, `dd`, `dt`, `figcaption`, `blockquote` — es la única
  señal de que ese texto se selecciona; la mano de enlace externo en `a[target="_blank"]`; y
  `grab`/`grabbing` en `.gallery-track`.

**Trampa ya localizada:** `sceneNav` monta **fuera** de `[data-scene]` (`sceneNav.ts:328-329`
cuelga disparador y panel de la raíz). Si la lista blanca de `cursor: none` se escribe solo con
selectores de escena, el cursor "se rompe" en cuanto el puntero sale del contenido. Por eso
`.scene-nav-trigger` y `.scene-index-row` van escritos a mano.

## Color y contraste

La luz mete calor detrás de texto claro, así que **baja el contraste de la fila iluminada**.
Medido (`scripts/measure-cursor-luz.py`, asercion 7) por glifo y contra el peor fotograma real del
shader, sobre las dos dianas donde el charco enciende. **Ronda de arreglo 1** (revisión externa,
reproducida con sonda instrumentada) corrigió dos fallos de medida en `.obra-abrir` — detalle
completo en la cabecera del arnés y en el registro de implementación:

- **`.hero-mail`** (enlace con texto propio; en `:hover` — que es cuando el charco enciende —
  pasa de `--haze` a `--l1`, `#ff5a34`): **a los números de partida del prototipo** (centro `rgb(255
  160 60 / 0.30·pot)`, mitad de radio `rgb(255 90 52 / 0.13·pot)`) el charco SÍ es la causa
  dominante del riesgo — medido: **~3,0:1** encendido contra **~4,53:1** apagado (`pot=0`, mismo
  encuadre), una caída de **~1,5**. Bajando el centro y la mitad de radio en pasos de `0.04`
  (manteniendo su proporción original ~2:1) hasta **centro `0.04·pot`, mitad de radio `0.017·pot`**
  (calibración final, ~87% por debajo del prototipo), la caída se reduce a **~0,22–0,28**, estable en
  cinco ejecuciones consecutivas de la ventana completa de 16,8s (encendido 4,22–4,24:1, apagado
  4,45–4,50:1). El baseline sin charco viaja pegado a AA (una decisión de `:hover` a `--l1` en
  `themes.css`, anterior a esta tarea, contra el techo de brillo del shader) — probado hasta
  `0.02`/`0.008` (charco casi apagado), el número no mejora más allá de ~4,2–4,3:1: el resto de la
  brecha hasta AA absoluto no lo cierra esta calibración.
- **`.obra-abrir`** (botón transparente que cubre la fila entera del titular, 1440px de ancho; el
  glifo visible es el `<h2 data-title>` que tapa). La primera versión de esta medida apuntaba al 40%
  del ancho del BOTÓN (x≈576) en vez de al centro del titular real (x=114–447): el radio del charco
  (260px para esa fila) no llegaba hasta ahí, así que el charco quedaba prácticamente apagado
  encima del texto y "encendido"/"apagado" daban el mismo número **por construcción** — no porque
  el charco no importara. Además el color leído (`getComputedStyle` del `<h2>`) siempre daba
  `--haze`: el titular no tiene color propio, son los DOS `<i>` apilados del relevo del cartel
  (`obraCartel.ts`) los que lo tienen, y con el hover puesto (`pointerenter` en `fila.seccion`
  dispara `relevo()`, que corre `.obra-rl` -50%) el que queda a la vista es `--color-paper`
  (`#ffeae6`), no `--haze`. **Corregido y remedido** apuntando al centro real del `<h2>` y leyendo
  el color del `<i>` que de verdad está visible en cada estado (esperando a que el tween de
  `relevo()` termine antes de fotografiar): **~4,0:1** con el charco encendido — el titular pasa a
  `--color-paper`, mucho más claro que `--haze`, así que el contraste MEJORA pese al calor del
  charco — contra **~1,4:1** en reposo (`--haze` sin encender nada), estable en cinco ejecuciones
  consecutivas. El bajo número EN REPOSO es el mismo techo de brillo del shader ya documentado y
  aceptado para el cartel de obra (`2026-08-10-hyprland-obra-cartel`, ver `CLAUDE.md` "Color y
  contraste" de Hyprland) — pero, medido correctamente, el charco de esta tarea no lo empeora: lo
  mejora, porque el propio hover del cartel cambia el texto a un color más claro al mismo tiempo
  que el charco enciende.

El gate del arnés aplica el MISMO margen a las dos dianas, siempre, sin escalón: el charco encendido
no puede caer más de 0,3 por debajo de su propio baseline apagado (mismo encuadre, mismo estado de
relevo). La primera versión tenía un escalón en `AA_MINIMO` (si el baseline sin charco ya cumplía
4,5 exigía AA absoluto; si no, exigía baseline−0,3) que resultó no determinista: el baseline de
`.hero-mail` oscila justo alrededor de 4,5 según el fotograma del shader, y en una corrida daba 4,48
(pasaba) y en otra 4,50 (el objetivo saltaba a 4,50 y el encendido, 4,22–4,24, no llegaba) — mismo
código, resultado distinto. Un umbral más fino que el ruido del propio instrumento, que es
justamente la regla que ya recoge `CLAUDE.md`. Quitado el escalón, cinco ejecuciones consecutivas
salen en verde con números estables (delta observado 0,22–0,28 en `.hero-mail`, muy por debajo del
margen de 0,3; `.obra-abrir` en verde por margen amplio, el charco la mejora).

**Corrección de método frente al borrador inicial del brief** (ver cabecera de
`scripts/measure-cursor-luz.py` para el detalle completo): no todo el texto de las dianas es
`--text` `#ffeae6` — se lee el color computado real del nodo que de verdad pinta el glifo visible en
cada estado, no un hex fijo; separar glifo de fondo por igualdad/distancia de color falla por el
antialias de fuentes (cuenta borde de letra como fondo) — se apaga el glifo por CSS y se fotografía
el fondo desnudo; la propia mano del cursor y el trazo del canto en el borde de la caja (fuera del
área de contenido) son artefactos de la medida, no fondo real, y se excluyen por geometría/recorte
de padding; una ventana de muestreo corta (~3,4s) no cubre el ciclo de brillo del shader — se amplió
a ~16,8s (42 muestras), el mismo criterio que ya usa `measure-cartel.py` para el mismo shader; el
peor píxel de cada fotograma se elige por MENOR CONTRASTE contra el texto, no por mayor luminancia
— con `--haze` (luminancia ~0,30) un fondo que se acerca a esa luminancia desde abajo empeora el
contraste tanto o más que uno que se aleja por arriba, y el shader baja hasta ~0,20; y el punto
donde se enciende el charco para medir ".obra-abrir" es explícito (el centro del `<h2>` real), no
un porcentaje del ancho de un botón diez veces más ancho que el texto.

Efecto a favor, medido también: el canto del elemento a `--l1` sube el contraste del **borde**, que
es lo que delimita la zona pulsable — no se mide con número aparte porque el gate de arriba ya lo
cubre (el borde queda excluido de la caja de contenido, así que si algo lo empeorase se vería en el
propio número del glifo).

## Rendimiento y limpieza

- **Un solo `<canvas>`** a pantalla completa, `pointer-events: none`, DPR limitado a 2.
- **Un solo `requestAnimationFrame`**. Nada de un rAF por pieza.
- El `rect` de la diana se relee cada fotograma **solo mientras hay diana**. Con el puntero en
  reposo no se toca el layout.
- La zona se resuelve en `pointerover`, no en `pointermove` — `pointermove` dispara decenas de
  veces por segundo y `closest()` en cada uno es trabajo tirado.
- Al desplazar, lo que hay bajo el puntero cambia sin que el ratón se mueva: bandera `stale` y
  `document.elementFromPoint` en el siguiente `pointermove`. Sin esto el charco se queda encendido
  en una fila que ya no está debajo.
- `destroy()` cancela el rAF, quita el lienzo y aborta los escuchas con `AbortController`. Se
  llama desde `pagehide` en `main.ts`, junto a los demás handles.
- La clase `hypr-cursor-ready` (la que activa `cursor: none`) se pone **solo si el montaje llegó
  hasta el final**. Si el módulo falla a medio camino, el visitante se queda con el cursor del
  sistema, no sin cursor.

## Montaje

Las mismas tres puertas que Vice, más el encendido de Hyprland:

```
theme.id === "hyprland"
  && !prefersReducedMotion
  && matchMedia("(hover: hover) and (pointer: fine)").matches
```

Hyprland tiene su propio gesto de apertura (`hyprIgnition`). A diferencia del leader de Vice, hoy
**no emite ningún evento** que avise de que ha soltado la pantalla. El plan decidirá entre esperar
un retardo fijo o hacer que `hyprIgnition` emita el evento; lo segundo es más limpio y toca un
módulo de Hyprland, que está en curso, así que es admisible.

## Lo que este dispositivo NO hace

- No escribe texto, números, etiquetas ni hex en pantalla. Ninguna excepción.
- No dibuja marcos, retículas, guías ni nada que cruce la página fuera del elemento apuntado.
- No deja estela ni partículas.
- No cambia de forma por sección. El encargo original pedía "estados por sección"; once rondas
  demostraron que la variación por sección es justo lo que produce el ruido. **Lo que varía es el
  tamaño del charco, y lo dicta la altura del elemento** — así una fila de créditos de 35px y un
  titular de 74px reciben la misma ley y se ven distintos sin que nadie programe casos.
- No toca Vice ni Caelestia.

## Criterio de aceptación

1. `npm run build` y `npm run lint` en verde.
2. Capturas reales a 1440×900 y 390×844 con `?theme=hyprland`: charco recortado dentro de la
   diana, nada encendido en reposo, nada encendido en zona nativa.
3. En móvil (390×844) el módulo **no se descarga**: comprobado por red, no por inspección visual.
4. Con `prefers-reduced-motion: reduce` no hay lienzo en el DOM.
5. Contraste por glifo de cada tipo de diana iluminada contra el peor fotograma del shader,
   documentado en este spec con el número obtenido.
6. Vice intacto: `?theme=vice` renderiza igual y su cursor sigue siendo el suyo.
7. Cero errores en consola, y `destroy()` verificado dejando el DOM sin lienzo.

## Registro de implementación

**Task 5 (2026-08-19) — contraste por glifo y calibración.** `scripts/measure-cursor-luz.py` gana
una asercion 7 que mide, por glifo y contra el peor fotograma real del shader (ventana de 16,8s,
42 muestras — ver cabecera del arnés), el contraste de las dos dianas donde el charco enciende.
Metodología corregida frente al borrador del brief en cuatro puntos (color de texto no es un hex
fijo, separación glifo/fondo por color falla por antialias, la mano del cursor y el canto del
charco contaminan la caja de borde, y una ventana corta no cubre el ciclo del shader) — detalle
completo en la cabecera de `scripts/measure-cursor-luz.py`.

Calibración final de `src/components/hyprCursor.ts`: centro del charco `0.30·pot → 0.04·pot`,
mitad de radio `0.13·pot → 0.017·pot` (radio sin tocar). A los números de partida del prototipo el
charco causaba una caída de contraste de ~1,5 en `.hero-mail` (3,0:1 encendido); calibrado, la
caída queda en ~0,2–0,3 (encendido ~4,2–4,3:1 contra ~4,45–4,5:1 apagado, dos ejecuciones
consecutivas de la ventana completa). `.obra-abrir` no depende del charco (su bajo contraste,
~1,3–1,6:1, es el mismo con el charco apagado del todo): es el mismo techo de brillo del shader ya
documentado y aceptado para el cartel de obra, no un riesgo de este dispositivo.

Arnés completo: `python3 scripts/measure-cursor-luz.py --base http://localhost:4173` → `0 fallos`
(dos ejecuciones consecutivas). `npm run build` y `npm run lint` en verde.

Corrección de alcance menor, arrastrada de una revisión anterior: la referencia a
`sceneNav.ts:327-328` (en este spec y en el comentario del bloque CSS nuevo de
`src/themes/themes.css`) estaba desalineada en una línea frente al código real
(`sceneNav.ts:328-329`, verificado con grep) — corregida en los dos sitios.

**Ronda de arreglo 1 (2026-08-19) — revisión externa con sonda instrumentada.** Dos críticos y un
importante, los tres reproducidos:

1. La medida "encendida" de `.obra-abrir` apuntaba al 40% del ancho del BOTÓN (x≈576 de una caja de
   1440px), fuera del radio del charco (260px) alrededor del titular real (x=114–447) — el charco
   quedaba prácticamente apagado encima del texto, así que "encendido" y "apagado" daban el mismo
   número por construcción. Corregido: `apuntar()` acepta ahora un punto explícito; para
   `.obra-abrir` se pasa el centro del `<h2 data-title>` real.
2. El color de texto leído (`getComputedStyle` del `<h2>`) siempre daba `--haze`: el titular no
   tiene color propio, son los dos `<i>` apilados del relevo del cartel (`obraCartel.ts`) los que lo
   tienen, y con el hover puesto el visible es `--color-paper`, no `--haze`. Corregido:
   `contraste_por_glifo()` gana un parámetro `selector_color` separado del nodo de caja/ocultado, y
   se espera a que el tween de `relevo()` termine (`RELEVO_ESPERA_MS`) antes de fotografiar, en los
   dos estados.
3. El gate tenía un escalón en `AA_MINIMO` (baseline≥4,5 exige AA absoluto, si no exige
   baseline−0,3) que resultó no determinista: el baseline de `.hero-mail` oscila justo alrededor de
   4,5 según el fotograma del shader. Corregido: el margen de 0,3 se aplica siempre, sin escalón.

Menores del mismo revisor, corregidos de paso: el `assert` de `main()` sobre el baseline apagado
ahora acumula en `fallos` en vez de abortar el arnés entero; el "peor píxel" de cada muestra se
elige por menor contraste contra el texto, no por mayor luminancia (con `--haze`, luminancia ~0,30,
un fondo que se acerca a esa luminancia desde abajo empeora el contraste igual o más que uno que se
aleja por arriba, y el shader baja hasta ~0,20).

Remedido con las correcciones: `.hero-mail` sin cambios sustanciales (~4,22–4,24:1 encendido, sigue
por encima del objetivo). `.obra-abrir` cambia por completo: **~4,0:1 con el charco encendido**
contra **~1,4:1 en reposo** — el charco MEJORA el contraste (el hover del cartel cambia el texto a
`--color-paper`, mucho más claro, al mismo tiempo que enciende), no lo empeora. El bajo número en
reposo sigue siendo el techo de brillo del shader ya documentado para el cartel de obra, pero ya no
hace falta invocarlo como excusa: con la medida correcta, `.obra-abrir` pasa el mismo gate de margen
que `.hero-mail`, sin necesitar ningún trato especial.

Arnés completo, cinco ejecuciones consecutivas: `python3 scripts/measure-cursor-luz.py --base
http://localhost:4173` → `0 fallos` en las cinco, con números estables (no una coincidencia de una
sola corrida). `npm run build` y `npm run lint` en verde. La calibración de `hyprCursor.ts`
(`0.04`/`0.017`) NO se tocó en esta ronda -- la evidencia de `.hero-mail` ya la justificaba y seguía
justificándola tras el arreglo.
