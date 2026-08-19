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

La luz mete calor detrás de texto claro, así que **podría bajar el contraste de la fila
iluminada** — ese es el riesgo que declaraba el prototipo. Medido con el método correcto (ver
abajo), el efecto real del charco sobre las dos dianas es **prácticamente nulo**.

**Método (Ronda de arreglo 2 — el que vale, los anteriores quedan superados).** Las dos primeras
rondas medían "encendido" (ratón puesto) contra "apagado" (ratón apartado a otra esquina) y
atribuían la diferencia al charco. Es una comparación entre DOS ESCENAS DE DOM DISTINTAS: apartar
el ratón deshace el `:hover` (`.hero-mail` vuelve a `--haze`) o el relevo del cartel
(`.obra-abrir` vuelve a `--haze` en vez de `--color-paper`), así que gran parte de la diferencia
medida era el cambio de color, no el charco. El método correcto (`contraste_pareado()`) aísla el
charco solo: el ratón se queda FIJO en el mismo punto durante toda la medida — nunca se mueve —
así que el texto tiene el MISMO color en las dos condiciones que se comparan. La única diferencia
entre condiciones es si el `<canvas>` del cursor está pintado en pantalla o no
(`style.visibility`); las dos capturas de cada par se toman una detrás de otra, casi en el mismo
fotograma del shader, y varios pares se intercalan a lo largo de una ventana de 16,8s. El número
que importa es el DELTA por par (canvas oculto − canvas visible): positivo si el charco empeora el
contraste, negativo si lo mejora, y una banda ancha de deltas en torno a 0 significa que el charco
no tiene un efecto sistemático apreciable.

Medido así, en siete ejecuciones consecutivas (rango real observado, no el mejor tramo):

- **`.hero-mail`** (enlace con texto propio, `:hover` fijo en `--l1` `#ff5a34` durante toda la
  medida): delta del charco en **[−0,08, 0,08]** a lo largo de las siete corridas — sin sesgo hacia
  empeorar. Peor contraste con el charco pintado: **4,21–4,27:1**, prácticamente igual al peor
  contraste con el canvas oculto en la misma corrida (4,27–4,29:1). Sigue por debajo de AA (4,5:1)
  por una décima o dos, pero eso no es el charco: es `--l1` de `:hover` (una decisión de
  `themes.css` anterior a esta tarea) contra el techo de brillo del shader.
- **`.obra-abrir`** (botón transparente que cubre la fila entera del titular; el glifo visible es
  el `<i>` de `--color-paper` del relevo del cartel, `obraCartel.ts`, con el hover fijo durante toda
  la medida): delta del charco en **[−0,09, 0,07]** a lo largo de las siete corridas — igual de sin
  sesgo. Peor contraste con el charco pintado: **3,47–3,63:1**, contra 3,47–3,62:1 con el canvas
  oculto en la misma corrida — la misma banda. **El titular sigue por debajo de AA en hover**, pero
  no por el charco: es el techo de brillo del propio shader `hyprEmber.ts` en ese punto de
  pantalla, el mismo hallazgo ya documentado y aceptado para el cartel de obra
  (`2026-08-10-hyprland-obra-cartel`, ver `CLAUDE.md` "Color y contraste" de Hyprland). No es una
  mejora nueva de esta tarea ni un riesgo nuevo que introduzca: es el mismo hallazgo de siempre,
  medido ahora con la variable correcta aislada.

El gate del arnés compara solo el delta pareado contra un margen fijo de 0,3, igual para las dos
dianas, sin escalón ni caso especial por AA.

**La calibración se remidió con el método pareado (Ronda de arreglo 3) y queda confirmada, no
adivinada.** La única justificación de haber bajado la intensidad del prototipo (`0.30`/`0.13`) a
`0.04`/`0.017` era aquella caída de ~1,5 en `.hero-mail` medida en la Ronda 1 — con el mismo método
hover-vs-sin-hover que infló el número de `.obra-abrir` en 2,6 puntos (ver nota en el registro de
implementación de la Task 5). Si ese 1,5 también hubiera sido un artefacto de método, la intensidad
del charco se habría recortado al 13% de lo que aprobó Aoshi a cambio de nada. Se remidió el
prototipo, un punto intermedio y la calibración actual, los tres con el método pareado (ratón fijo,
única diferencia la visibilidad del `<canvas>`), y el prototipo SÍ falla — la caída es real, no un
artefacto de método:

| Punto | centro / mitad de radio | delta `.hero-mail` (rango observado) | delta `.obra-abrir` (rango observado) | ¿Cabe en el margen de 0,3 con holgura real? |
|---|---|---|---|---|
| Prototipo | `0.30·pot` / `0.13·pot` | **[1,229, 1,525]** (2 corridas) | [0,002, 0,128] | **NO** — `.hero-mail` lo excede 4-5 veces |
| Intermedio | `0.16·pot` / `0.07·pot` | **[0,203, 0,426]** (2 corridas) | [−0,021, 0,119] | **NO** — el peor caso de `.hero-mail` (0,40–0,43) ya SUPERA 0,3, no "roza" |
| **Actual (final)** | `0.04·pot` / `0.017·pot` | **[−0,09, 0,11]** (15 corridas: 9 de la Ronda 2 + 6 de la Ronda 3) | [−0,09, 0,07] | **SÍ**, con holgura real (el peor caso, 0,11, deja casi 3x de margen hasta 0,3) |

Por la regla de la coordinación (el valor final es el más alto de los tres cuyo delta quepa dentro
del margen con holgura real): el prototipo no cabe, el intermedio no cabe, así que **la
calibración final se queda en `0.04·pot` / `0.017·pot` — sin cambios respecto a la Ronda 1**. No es
que la evidencia original estuviera mal (aunque el MÉTODO con el que se obtuvo sí lo estaba): la
conclusión resultó ser la misma con el método correcto, y ahora está confirmada con tres puntos
medidos, no con una comparación de dos escenas de DOM distintas. El radio no se tocó en ningún
punto de esta curva.

**Correcciones de método acumuladas** (ver cabecera de `scripts/measure-cursor-luz.py` para el
detalle completo, seis puntos): el texto de las dianas no es un hex fijo, se lee el color
computado real del nodo que de verdad pinta el glifo visible en cada estado; separar glifo de
fondo por igualdad/distancia de color falla por el antialias de fuentes — se apaga el glifo por
CSS y se fotografía el fondo desnudo; la mano del cursor y el trazo del canto en el borde de la
caja son artefactos de la medida — se excluyen por geometría/recorte de padding; una ventana de
muestreo corta no cubre el ciclo de brillo del shader — se amplió a 16,8s; el peor píxel de cada
fotograma se elige por menor contraste, no por mayor luminancia; y el efecto del charco se mide
por PAR con el resto del estado (hover, color) fijo, no comparando dos escenas de DOM distintas.

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
Metodología corregida frente al borrador del brief en seis puntos (color de texto no es un hex
fijo, separación glifo/fondo por color falla por antialias, la mano del cursor y el canto del
charco contaminan la caja de borde, una ventana corta no cubre el ciclo del shader, el peor píxel
se elige por menor contraste y no por mayor luminancia, y el efecto del charco se mide por PAR con
el resto del estado fijo) — detalle completo en la cabecera de `scripts/measure-cursor-luz.py`.

Calibración final de `src/components/hyprCursor.ts`: centro del charco `0.30·pot → 0.04·pot`,
mitad de radio `0.13·pot → 0.017·pot` (radio sin tocar). A los números de partida del prototipo el
charco causaba una caída de contraste de ~1,5 en `.hero-mail` (3,0:1 encendido); calibrado, la
caída queda en ~0,2–0,3 (encendido ~4,2–4,3:1 contra ~4,45–4,5:1 apagado, dos ejecuciones
consecutivas de la ventana completa). `.obra-abrir` no depende del charco: es el mismo techo de
brillo del shader ya documentado y aceptado para el cartel de obra, no un riesgo de este
dispositivo.

> **SUPERADO por la Ronda de arreglo 2 (ver `## Color y contraste` y el registro más abajo).** El
> párrafo original de esta entrada daba aquí el bajo contraste de `.obra-abrir` como "~1,3–1,6:1" —
> ese número salía del método hover-vs-sin-hover, luego desacreditado por comparar dos escenas de
> DOM distintas. Medido con el método pareado, el contraste real de `.obra-abrir` en hover es
> **3,47–3,63:1** (peor caso con el charco pintado), prácticamente idéntico al 3,47–3,62:1 con el
> canvas oculto — la conclusión de fondo (no depende del charco, es el techo de brillo del shader)
> se mantiene, pero el número concreto era el equivocado.

Arnés completo: `python3 scripts/measure-cursor-luz.py --base http://localhost:4173` → `0 fallos`
(dos ejecuciones consecutivas). `npm run build` y `npm run lint` en verde.

> **Nota (actualizada en la Ronda de arreglo 3):** el "~1,5 de caída en `.hero-mail`" de este
> párrafo se midió apartando el ratón para el baseline "apagado" -- el mismo método que la Ronda 2
> encontró inflado para `.obra-abrir`. La Ronda 2 dejó abierta la sospecha de que este número
> también estuviera inflado; la Ronda 3 remidió el PROTOTIPO (`0.30`/`0.13`) con el método pareado
> y confirmó que la caída es real: delta `[1,23, 1,53]`, cuatro a cinco veces el margen de 0,3.
> La calibración final NO cambia por esto (sigue en `0.04`/`0.017`, con delta pareado
> `[-0,09, 0,11]` en 15 corridas) -- pero ahora está confirmada con el método correcto, no
> heredada de una medida con el método malo. Detalle completo, con los tres puntos de la curva, en
> `## Color y contraste` y en la entrada de la Ronda de arreglo 3 más abajo.

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

Remedido con las correcciones: `.hero-mail` sin cambios sustanciales (~4,22–4,24:1 encendido,
sigue por encima del objetivo).

> **SUPERADO por la Ronda de arreglo 2 (ver más abajo).** El párrafo original de esta entrada decía
> aquí que ".obra-abrir cambia por completo... el charco MEJORA el contraste... no lo empeora". Esa
> conclusión estaba mal: seguía comparando "encendido" (ratón puesto, texto en `--color-paper`)
> contra "apagado" (ratón apartado, texto vuelto a `--haze`) — dos escenas de DOM distintas, no el
> efecto del charco aislado. El ~4,0:1 que salía era casi entero el cambio de color del relevo del
> cartel, no el charco. La medida correcta (método pareado, con el hover fijo y el texto en el
> MISMO color en las dos condiciones) está en la Ronda de arreglo 2: el efecto del charco sobre
> `.obra-abrir` es prácticamente nulo (delta en banda estrecha alrededor de 0), y el titular sigue
> por debajo de AA en hover — no por una mejora ni por el charco, sino por el mismo techo de brillo
> del shader ya documentado para el cartel de obra.

Arnés completo, cinco ejecuciones consecutivas: `python3 scripts/measure-cursor-luz.py --base
http://localhost:4173` → `0 fallos` en las cinco, con números estables (no una coincidencia de una
sola corrida). `npm run build` y `npm run lint` en verde. La calibración de `hyprCursor.ts`
(`0.04`/`0.017`) NO se tocó en esta ronda -- la evidencia de `.hero-mail` ya la justificaba y seguía
justificándola tras el arreglo.

**Ronda de arreglo 2 (2026-08-19) — el Crítico 2 seguía abierto + dos hallazgos nuevos.** La Ronda
1 corrigió CÓMO se leía el color, pero no que "encendido" (ratón puesto) y "apagado" (ratón
apartado) seguían siendo dos escenas de DOM distintas en `.obra-abrir`: apartar el ratón deshace
`relevo()` y el texto vuelve a `--haze`, así que la mejora de ~1,4:1 a ~4,0:1 que reportaba la
Ronda 1 era casi entera el cambio de color del relevo, no el charco — el gate de esa diana pasaba
con ~2,9 de holgura fabricada.

Corregido con el método pareado exigido por el re-revisor: `contraste_pareado()` mantiene el ratón
FIJO en el mismo punto durante toda la medida (nunca se mueve, nunca se aparta), así que el texto
queda en el MISMO color en las dos condiciones comparadas. La única diferencia entre condiciones es
la visibilidad del `<canvas>` del cursor (`style.visibility`, no el estado del DOM); cada par toma
dos capturas seguidas (canvas oculto, canvas visible) casi en el mismo fotograma del shader, y 42
pares se intercalan a lo largo de ~16,8s. Aplicado a las DOS dianas por coherencia (no solo
`.obra-abrir`).

Dos hallazgos nuevos del mismo re-revisor, corregidos de paso:

- **Asercion 3 ("charco rancio tras desplazar")** fallaba 1 de cada 6 corridas con `pot=0,0507`
  contra un umbral de `0,05` — la misma clase de umbral-mas-fino-que-el-ruido ya corregida en el
  gate de contraste (regla en `CLAUDE.md`). Subida la espera de 400ms a 900ms y el umbral de 0,05 a
  `POT_RANCIO_MAXIMO = 0,15` (3x el único fallo medido), con el número justificado en el propio
  comentario del código.
- **Docstring de la cabecera del arnés** seguía afirmando que el titular "pinta `--haze` siempre, no
  cambia con el hover" — refutado por el propio arnés 350 líneas más abajo desde la Ronda 1.
  Corregido.
- **Menor:** `punto_diana` (el centro del `<h2>` real) se calculaba con un `bounding_box()` leído
  ANTES de `scroll_into_view_if_needed()` — coordenadas potencialmente rancias, aunque no mordía en
  la práctica. Corregido: scroll primero, `bounding_box()` después.

**Delta pareado del charco por diana, rango real observado en siete ejecuciones consecutivas** (no
el mejor tramo — el rango completo, incluyendo la corrida con el delta más ancho):

| Diana | Delta (canvas oculto − visible) | Peor contraste con charco | Peor contraste sin charco (mismo DOM) |
|---|---|---|---|
| `.hero-mail` | **[−0,08, 0,08]** | 4,21–4,27:1 | 4,27–4,29:1 |
| `.obra-abrir` | **[−0,09, 0,07]** | 3,47–3,63:1 | 3,47–3,62:1 |

Las dos bandas de delta son estrechas, centradas en 0 y muy por debajo del margen de 0,3: el efecto
real del charco sobre las dos dianas es prácticamente nulo, no solo sobre `.obra-abrir`.

> **SUPERADO por la Ronda de arreglo 3 (ver más abajo).** El párrafo original de esta entrada
> especulaba aquí que la caída de ~1,5 atribuida al charco contra el prototipo (0,30/0,13) "estaba
> medida con el mismo método hover-vs-sin-hover que infló el número de `.obra-abrir`, así que
> probablemente también estaba inflada — no se ha medido el prototipo con el método pareado". Esa
> sospecha quedó cerrada en la Ronda de arreglo 3: se remidió el PROTOTIPO con el método pareado y
> la caída resultó ser real, no un artefacto de método — delta `[1,23, 1,53]`, cuatro a cinco veces
> el margen de 0,3. La calibración final no cambia (sigue en `0.04`/`0.017`), pero la lectura
> correcta es que el número original del prototipo era fiable, no que estuviera inflado.

Arnés completo, **siete ejecuciones consecutivas reales** (no una selección del mejor tramo):
`python3 scripts/measure-cursor-luz.py --base http://localhost:4173` → `0 fallos` en las siete.
`npm run build` y `npm run lint` en verde. La calibración de `hyprCursor.ts` (`0.04`/`0.017`, radio
sin tocar) NO se tocó en esta ronda.

**Ronda de arreglo 3 (2026-08-19) — remedir el prototipo, cerrar la sospecha de la Ronda 2.** La
Ronda 2 dejó una nota sin resolver: si la caída de ~1,5 en `.hero-mail` que justificó bajar la
intensidad del charco (`0.30`/`0.13` → `0.04`/`0.017`) se había medido con el mismo método
hover-vs-sin-hover que infló el número de `.obra-abrir` en 2,6 puntos, esa caída también podía
estar inflada — y la calibración final habría recortado la luz al 13% de lo aprobado por Aoshi sin
motivo real.

Ruling de la coordinación: remedir el prototipo (`0.30`/`0.13`) y un punto intermedio
(`0.16`/`0.07`) con el método pareado ya construido en la Ronda 2, y quedarse con el valor más alto
de los tres cuyo delta quepa dentro del margen de 0,3 con holgura real. El radio no se toca en
ningún punto.

Resultado (tabla completa también en `## Color y contraste`): el prototipo falla de forma
contundente (`.hero-mail` delta 1,23–1,53, cuatro a cinco veces el margen) y el punto intermedio
también falla (`.hero-mail` delta hasta 0,40–0,43, por encima de 0,3 sin ambigüedad — no roza el
límite, lo supera). Solo la calibración actual (`0.04`/`0.017`) cabe con holgura real. **La
calibración final no cambia respecto a la Ronda 1.** Es un resultado bueno, no un error: confirma
que la decisión de bajar la intensidad fue correcta incluso con el método malo que la originó, y
ahora queda respaldada por tres puntos medidos con el método bueno en vez de por una comparación de
dos escenas de DOM distintas.

Comandos y salida literal (mismo host, dos puertos: 4173 se vio interferido de forma intermitente
por otro proceso ajeno a este worktree sirviendo en el mismo puerto -- las medidas finales se
repitieron en el puerto 4599, dedicado, verificando antes y después de cada medida que el bundle
sirviendo coincidía con el fichero fuente):

```
$ sed -i "s/(0.04 \* pot)/(0.30 * pot)/" src/components/hyprCursor.ts   # y 0.017 -> 0.13
$ npm run build && npx vite preview --port 4599 &
$ python3 delta_only.py http://localhost:4599
.hero-mail: delta [1.229, 1.525] pot=0.993 texto=rgb(255, 90, 52)
.obra-abrir: delta [0.002, 0.128] pot=1.000 texto=rgb(255, 234, 230)
# repetido:
.hero-mail: delta [1.237, 1.508] pot=0.997 texto=rgb(255, 90, 52)
.obra-abrir: delta [0.005, 0.128] pot=1.000 texto=rgb(255, 234, 230)

$ sed -i "s/(0.30 \* pot)/(0.16 * pot)/" src/components/hyprCursor.ts   # y 0.13 -> 0.07
$ npm run build
$ python3 delta_only.py http://localhost:4599
.hero-mail: delta [0.210, 0.426] pot=0.997 texto=rgb(255, 90, 52)
.obra-abrir: delta [-0.020, 0.099] pot=1.000 texto=rgb(255, 234, 230)
# (primera corrida de este punto, con el arnes en 4173 antes de aislar en 4599: [0.203, 0.399] /
# [-0.021, 0.119] -- misma conclusion, delta max de .hero-mail por encima de 0.3 en las dos)

$ git checkout -- src/components/hyprCursor.ts   # vuelve a 0.04/0.017, la calibracion final
$ npm run build && npx vite preview --port 4599 &
$ python3 scripts/measure-cursor-luz.py --base http://localhost:4599    # x6, todas 0 fallos
```

`delta_only.py` es un script auxiliar de esta ronda (fuera del repo, en el scratchpad de la sesión)
que llama directamente a `contraste_pareado()` para las dos dianas sin correr las otras seis
aserciones del arnés -- más rápido para explorar la curva. Las seis corridas finales de
verificación SÍ son el arnés completo (`scripts/measure-cursor-luz.py`), no el script auxiliar.

Arnés completo, **seis ejecuciones consecutivas reales** en el puerto aislado (4599), con la
calibración final (`0.04`/`0.017`, sin cambios): `0 fallos` en las seis. `npm run build` y
`npm run lint` en verde. `git status` limpio en `src/components/hyprCursor.ts` -- la calibración
que queda commiteada es la misma que ya estaba desde la Ronda 1, no hace falta un commit de código
para este fichero en esta ronda.

**Task 6 (2026-08-19) — verificacion visual y no-regresion de Vice.** Build de produccion servido
en un puerto aislado (`npx vite preview --port 4599`, node v22.22.3 via `nvm use 22.22.3`; el node
del PATH es v18 y no compila `tsc`).

Capturas reales, con la sonda `window.__hyprCursor__.pot()` comprobada por encima de 0.95 antes de
cada disparo (helper `esperar_pot_asentada()` copiado de la cabecera del arnes) para no fotografiar
el charco a medio encender:

- `t6-hypr-obra.png` (1440x900, `?theme=hyprland`, raton sobre `.obra-abrir`, `pot=0.969`): el
  charco se ve como una franja de luz mas calida recortada dentro de la fila `EchoPlan` (01/05),
  con corte neto en el borde superior e inferior de la fila -- las filas 02-05 debajo quedan a
  oscuras, sin contaminacion. El punto de la mano (circulo blanco de 3.2px con anillo oscuro) es
  visible sobre el titulo, en el punto exacto donde se coloco el raton. El canto del elemento en
  `--l1` se aprecia como el borde rojizo fino que enmarca la fila completa.
  ruta: `/tmp/claude-0/-home-aoshi-proyectos-portfolio-aoshi/7b237084-3ab1-432b-b565-af338b2b6e1b/scratchpad/t6-hypr-obra.png`
- `t6-hypr-correo.png` (1440x900, `?theme=hyprland`, raton sobre `.hero-mail`, `pot=0.976`): el
  charco es mas discreto que en la fila de obra (la caja de `.hero-mail` es mas pequena, radio
  minimo 120px), visible como un aclarado suave alrededor del texto del correo con el mismo
  recuadro `--l1` ciñendose al ancho del enlace, no a la fila entera. El punto de la mano se ve
  con nitidez sobre el signo `@`.
  ruta: `/tmp/claude-0/-home-aoshi-proyectos-portfolio-aoshi/7b237084-3ab1-432b-b565-af338b2b6e1b/scratchpad/t6-hypr-correo.png`
- `t6-hypr-reposo.png` (1440x900, `?theme=hyprland`, raton sobre `.hero-kick`, texto corrido,
  `pot=0.0016`): no hay ningun encendido visible -- la caja del kicker no tiene ni glow ni
  recuadro, indistinguible de la misma captura sin el raton encima. Confirma en imagen lo que ya
  medía la asercion 2 del arnes.
  ruta: `/tmp/claude-0/-home-aoshi-proyectos-portfolio-aoshi/7b237084-3ab1-432b-b565-af338b2b6e1b/scratchpad/t6-hypr-reposo.png`
- `t6-hypr-movil.png` (390x844, `?theme=hyprland`): pagina identica a como se veria sin el modulo
  cargado -- no hay lienzo ni artefacto de cursor, coherente con la asercion 5 del arnes (el modulo
  no se descarga en movil, `matchMedia("(hover: hover) and (pointer: fine)")` no matchea).
  ruta: `/tmp/claude-0/-home-aoshi-proyectos-portfolio-aoshi/7b237084-3ab1-432b-b565-af338b2b6e1b/scratchpad/t6-hypr-movil.png`
- `t6-vice.png` (1440x900, `?theme=vice`, raton sobre el enlace de correo): el cursor de Vice sigue
  siendo su propia marca de sincronismo (reticula circular con cruz, en el color de acento de
  Vice), sin ningun rastro del charco de Hyprland. Comprobado tambien por DOM:
  `document.querySelector('.hypr-cursor-canvas') !== null` da `false` con `?theme=vice`.
  ruta: `/tmp/claude-0/-home-aoshi-proyectos-portfolio-aoshi/7b237084-3ab1-432b-b565-af338b2b6e1b/scratchpad/t6-vice.png`

**No-regresion de Vice:**

- `python3 scripts/verify.py` -> `TODO OK -- 12 fallos conocidos, 0 nuevos (verify-baseline.json)`,
  codigo de salida 0.
- `python3 scripts/measure-obra-rail.py --url "http://localhost:4599/?theme=vice"` (nota: el flag
  correcto de este arnes es `--url`, no `--base` como decia el paso 2 del plan; corregido al
  ejecutar) -> geometria medida `distance: 5760`, `pin_budget: 5040`, exactamente los valores
  documentados en `CLAUDE.md` (la trampa de que el pin reserva menos scroll que el recorrido
  lateral). El carril no se ha movido.
- `python3 scripts/measure-cursor-luz.py --base http://localhost:4599` (septima ejecucion,
  contando las seis de la Ronda de arreglo 3): `0 fallos`. Deltas de contraste
  `.hero-mail [-0.05, 0.08]`, `.obra-abrir [-0.05, 0.03]`, dentro de las bandas ya documentadas.

Divergencias respecto a lo planeado: ninguna en codigo. El unico ajuste fue de comando
(`measure-obra-rail.py` usa `--url`, el plan traia `--base` de otro arnes por error de copiado).

Arnés completo y verify.py verdes, capturas miradas una por una. `npm run build` y `npm run lint`
en verde (Task 3-4). Criterio de aceptación del spec cerrado en los siete puntos: 1 (build/lint) y
2/3/4 (capturas, red movil, reduced motion, arnes tarea 1) y 6 (Vice intacto, verify.py + rail +
cursor propio) verificados aqui; 5 (contraste) y 7 (destroy/consola) verificados en las tareas
anteriores y confirmados de nuevo por el arnes en esta pasada.
