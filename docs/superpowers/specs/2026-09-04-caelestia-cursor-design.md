# La gota — el cursor de Caelestia es pigmento de la hora sobre la superficie

Estado: implementado
Plan: `docs/superpowers/plans/2026-09-04-caelestia-cursor.md`
Fecha: 2026-09-04 (spec aprobado y plan escrito el mismo dia)

**Ejecucion, al 2026-09-05:** **las nueve tareas del plan cerradas**, arnes en verde con
**53 aserciones** (`scripts/measure-caelestia-cursor.py`, 8 gates). Cruzadas tambien en verde: el
motor de color de Caelestia (fase A intacta), el cursor de Hyprland (no se ha tocado el de al lado)
y `scripts/verify.py` (12 fallos conocidos de fixtures, 0 nuevos). Las tres dianas miradas a ojo,
de dia y de noche, con el derrame lleno.

**Revision final de rama** (modelo top, modo lectura, con los 11 minors diferidos delante): cinco
hallazgos, los cinco cerrados. Dos importaban de verdad — con movimiento reducido activado DESPUES
de montar la pagina se quedaba sin ningun cursor, y las paginas de Vice y Hyprland del gate 1
corrian sin oyente de consola. Detalle en el `## Registro de implementacion`.

**Fusionado a `main` el 2026-09-05.** Con el merge se aplicaron las dos piezas de documentacion que
no viven en la rama porque `.claude/` esta en `.gitignore`: la fila del arnes en
`.claude/rules/verification.md` y el parrafo en espanol de `.claude/CLAUDE.md`.

El progreso real son **las casillas del plan**, que es lo que cruza `scripts/verify.py`; el detalle
de cada ronda vive en `.superpowers/sdd/2026-09-04-caelestia-cursor/progress.md`, ignorado por git.
Lo que la ejecucion desmintio de este documento esta recogido en el
`## Registro de implementacion` del final.

## Por qué

Tres razones, elegidas por Aoshi antes de esta sesión, y ninguna es "porque los otros dos lo tienen":

1. **Paridad de tema.** Vice tiene la marca de sincronismo (`viceCursor.ts`) y Hyprland la luz de
   mano (`hyprCursor.ts`). Caelestia es el único tema donde el puntero sigue siendo el del sistema.
2. **Descubribilidad del roce.** En Créditos rozar ya elige (`caelestiaCreditosBandeja.ts:203`,
   `mouseenter` → `entrar`), y `lidia-naive-tester` lo dejó como P1 abierto en B4: el gesto no se
   descubre. Un cursor que cambia de estado al entrar en una pieza es la primera pista de que ahí
   pasa algo sin pulsar.
3. **Continuidad del escritorio.** Caelestia finge ser un escritorio completo: barra, dock,
   workspaces, reloj, notificaciones. El puntero es hoy lo único que sigue siendo del sistema
   operativo del visitante dentro de esa ficción.

**Fuera de alcance**, decidido antes de empezar: cargar al cursor con la navegación entre
workspaces. Eso ya lo hacen las pastillas.

## El nudo — dos estados que no pueden ser dos símbolos

El encargo pedía **dos estados distintos**, no una diferencia de grado: uno para la diana que
responde al roce y otro para la que espera un clic. Y el veto heredado de Hyprland dice que **un
cursor no puede tener manual**: ni un carácter, ni un número, ni nada que cruce la página fuera
del elemento apuntado. Las dos cosas tensionan: dos glifos distintos son un vocabulario, y un
vocabulario se aprende.

La resolución, que es la decisión de diseño de todo este documento:

> **Los dos estados no son dos símbolos. Son un mismo gesto disparado en dos momentos.** La diana
> que elige al rozar hace *al llegar* lo que la diana de clic hace *al pulsar*.

El visitante no aprende dos estados. Ve que en Créditos "ya ha pasado" y en Obra "está por pasar".

## Diagnóstico — dos rondas y por qué cayeron tres direcciones

**Ronda 1 — la pieza en la mano.** El cursor como figura de Material 3 Expressive (la misma familia
de 240 vértices de `figurasM3.ts`) en azufre: círculo en reposo, trébol abierto sobre lo pulsable,
hundido a círculo al pulsar o al rozar. Coherente con la identidad declarada del tema (*"a fluid,
morphing shell"*), y rechazada por Aoshi mirándola: **ni el diseño ni el color**. Dos causas que se
ven en la captura: un trébol amarillo de 26px es un pegote sobre cualquier fondo del tema, y el
estado hundido (12px) se leía como cursor apagado, no como "hecho". Y una de fondo: repetía el
vocabulario de las 23 piezas de Créditos, así que sobre la bandeja el cursor era una pieza más.

**Ronda 2 — tres materiales.** Con la misma ventana debajo y pestañas para conmutar:

| | material | por qué cayó o quedó |
|---|---|---|
| **A · la gota** | pigmento de la hora, translúcido, con tensión superficial | **elegida.** Es la única cuyo color *es* el gesto firma del tema (gira con el reloj) y la única que trabaja por material y no por dibujo |
| B · el manículo | la mano que señala de los impresores, en tinta, girando hacia el centro de la diana | la más editorial, casa con el Fraunces itálico de la Obra, pero es un dibujo y un dibujo hay que acertarlo: a 30px se leía como borrón hasta redibujarlo dos veces |
| C · el borde activo | la diana se dibuja su propio borde desde el punto más cercano al ratón, como la ventana con foco del compositor | la más "suya" y la de contraste más fácil, pero es **la diana** la que firma, no el cursor: no cierra la paridad, y un filete de 1-2px vuelve al alambre que Hyprland ya descartó |

**Lo que NO es, y por qué:**

- **No es el charco de luz de Hyprland.** Aquello oscurece o ilumina el fondo *detrás* del texto
  de la diana, con el signo decidido por la luminancia del material. Esto mancha *encima*, con un
  pigmento que tiene color propio, y el pigmento es la tesis del tema. Comparten una cosa a
  propósito, porque es la única forma correcta de hacerla: la posición se escribe sin suavizar.
- **No es el retículo de Vice.** No hay geometría fija ni cruz ni marca de registro.
- **No tiene estela.** Es lo primero que pide una gota y lo primero que se descartó: un rastro de
  gotitas detrás del ratón es atmósfera sin estructura, el tic que este proyecto tiene identificado
  como marca de diseño generado, y además insinúa inercia donde no la hay. **La gota deja huella
  solo donde ha actuado, nunca por donde pasa.**
- **No lleva azufre.** El ancla del tema marca lo accionable (contacto, disponibilidad, foco) y ya
  se midió en B4 que contra `--cae-elev-1` da 1,38:1 de día. La gota lleva `--cae-primary`, que es
  el rol que sí cambia con la hora, y el estado hundido lleva `--cae-on-surface`.

---

## Tesis

> **El cursor de Caelestia es una gota del pigmento de la hora.** Translúcida, con tensión
> superficial, sobre la superficie. Sobre lo que se pulsa se tensa en perla y espera; al pulsar se
> derrama y encharca la diana hasta sus cantos. Sobre lo que elige al rozarlo se derrama al entrar:
> ya está mojado. Sobre texto corrido se apaga y manda el I-beam del sistema.

Tres razones por las que esta y no otra:

1. **El color es el gesto firma del tema hecho puntero.** `--cae-primary` gira los 360 grados en
   24 horas: el visitante de las 09:00 lleva en la mano una gota azul y el de las 21:00 una gota
   distinta. Nada que programar: la gota lee el token.
2. **Lo mojado ya respondió.** Es una lectura anterior al lenguaje, y es la que separa las dos
   afordancias sin dos símbolos: la mancha que llena la diana significa lo mismo en Obra (después
   del clic) y en Créditos (al entrar).
3. **Es material, no dibujo.** Una gota se reconoce por cómo se comporta (se tensa, se derrama,
   refracta, deja cerco), no por su silueta. Eso la hace sobrevivir a cualquier tamaño y a
   cualquier fondo, y es lo que la ronda 1 no tenía.

## Anatomía

Cinco piezas, todas del mismo material:

| pieza | qué es | cuándo existe |
|---|---|---|
| **La perla** | disco de `--cae-primary`, `mix-blend-mode: multiply` de día / `screen` de noche, con un brillo de tensión (elipse de `--cae-surface` arriba a la izquierda) y un **núcleo** de 3px en `--cae-on-surface` que marca la mano | siempre que el puntero esté en zona propia |
| **La lente** | `backdrop-filter` sobre la perla: de día `saturate(1.7) contrast(1.06) blur(0.7px)`, de noche `brightness(1.35) saturate(1.25) blur(0.7px)` | mientras la perla no esté derramada |
| **La sombra** | de día `0 1px 2px` en `--cae-on-surface` al 32% más un canto interior al 12%; de noche un **canto encendido** (`inset 0 0 0 1px` en `primary` mezclado 60% con blanco, canto inferior y halo de 6px al 45%) | igual que la lente |
| **El derrame** | un elemento `.cae-cursor-mancha` sobre la diana, recortado a su caja con el `border-radius` que la diana ya tiene, con un círculo de `--cae-primary` al 22% (día) / 30% (noche) que crece desde el punto del ratón hasta cubrir la caja, `multiply` / `screen` | solo con diana mojada |
| **El cerco** | anillo de 18px, borde 1,4px en `--cae-primary`, que se abre a ×2,1 y se disipa | solo al soltar un clic sobre una diana de clic |

**El derrame es un elemento aparte, no un `background-image` en la diana.** Hyprland pinta su
hueco en línea porque necesita quedar *debajo* del texto y *encima* del fondo propio del elemento.
Aquí la mancha va encima de todo, como pigmento sobre papel: con `multiply` de día oscurece fondo y
texto a la vez y con `screen` de noche los aclara a la vez, y el contraste se mueve poco (lo mide el
gate 6, y ese es el número que decide si esta elección aguanta o si hay que pasar al mecanismo de
Hyprland — ver `## Preguntas abiertas para el plan`). Ventaja que no es menor: **no toca el DOM de
ninguna diana**, así que no hay estado previo que restaurar ni la clase de fallo que la Task 9 de
Hyprland tuvo que resolver.

## Estados

| estado | la perla | la lente y la sombra | el derrame | cuándo |
|---|---|---|---|---|
| **Reposo** | 20px, opacidad 0,42 (0,55 de noche), brillo 0,55 | encendidas | seco | puntero en zona propia sin diana |
| **Perla** | 15px, opacidad 0,95, brillo 0,95, silueta ligeramente asimétrica (`border-radius: 48% 52% 50% 50% / 55% 55% 45% 45%`), **un rebote elástico al posarse** | encendidas | seco | sobre diana de clic |
| **Derrame** | 30px en `--cae-on-surface` al 26% (tinta, no pigmento: sobre la pieza elegida el pigmento es el mismo color que la pieza y desaparece — medido en la ronda 2), sin brillo | apagadas | llenando la diana | pulsando una diana de clic, o dentro de una diana de roce |
| **Cerco** | vuelve a perla | encendidas | se recoge en 0,18 s | al soltar el clic; el anillo dura 0,8 s |
| **Apagada** | opacidad 0, núcleo 0 | — | seco | zona nativa: texto corrido, galería, enlaces externos |
| **Movimiento reducido** | no se monta | — | — | ni módulo ni elementos |
| **Táctil / puntero grueso** | no se monta | — | — | no hay hover que disparar nada |

El rebote de la perla es **un ciclo y corto** (`scale 1.35 0.8 → 0.9 1.1 → 1 1`, 420 ms): es la
curva *expressive* de Material 3 hecha física. Si se repite, es gelatina.

**La posición no se suaviza nunca.** Se escribe en el propio `pointermove`, como en los otros dos
cursores. Lo que se interpola son el tamaño, la opacidad y la silueta (transiciones CSS de 300 ms
sobre `cubic-bezier(.2, 0, 0, 1)`), el derrame (420 ms al llenar, 180 ms al recogerse tras el clic,
300 ms al secarse al salir) y el cerco (800 ms). En Créditos hay 23 dianas contiguas: un cursor con
inercia ahí se lee como retraso.

> **Corregido el 2026-09-05.** Este párrafo decía «GSAP» para el derrame y el cerco. **No hay GSAP
> en este dispositivo**: todo el movimiento son transiciones y una animación CSS, precisamente para
> que el montaje siga siendo síncrono y el módulo no dependa de una librería que carga aparte. Las
> curvas son `cubic-bezier(0.2, 0, 0, 1)`, no `power2.*`. Los tiempos sí eran los correctos.

## Las tres dianas

Medido leyendo el árbol, no supuesto: los tres gestos de roce del tema ya son `<button>`.

| diana | fichero | qué hace el elemento | qué hace la gota |
|---|---|---|---|
| las 23 piezas de Créditos | `caelestiaCreditosBandeja.ts:70` | `mouseenter` → `entrar` (rozar elige; pulsar no añade nada) | **se derrama al entrar** |
| las cinco tarjetas de Obra | `caelestiaObraEditorial.ts:284` | `pointerenter` avisa (se endereza y sube), `click` abre el cajón | perla; se derrama al pulsar; cerco al soltar |
| las pastillas de workspace | `caelestiaShell.ts:52` | `click` cambia de workspace | perla; se derrama al pulsar; cerco al soltar |

**Cómo distingue el módulo las dos familias sin taxonomía nueva:** las 23 piezas llevan
`aria-pressed` (`caelestiaCreditosBandeja.ts:76`, `"false"`/`"true"`) porque *son* botones de
estado; ni las tarjetas ni las pastillas lo llevan. Así que:

```ts
// Pulsables que la gota viste. El enlace externo queda fuera aposta.
const PRESSABLE = 'button, a[href]:not([target="_blank"])';
// De entre ellos, los que ya responden al roce: la gota se derrama al entrar.
const HOVER_SELECT = 'button[aria-pressed]';
// Zonas donde manda el navegador y la gota se apaga.
const NATIVE_ZONE = '.gallery-track, a[target="_blank"], p, li, dd, dt, figcaption, blockquote';
```

`PRESSABLE` y `NATIVE_ZONE` son los mismos de `hyprCursor.ts` y `viceCursor.ts`, literalmente:
el problema es el mismo y la solución cerrada dos veces no se reabre. `HOVER_SELECT` es ARIA que ya
existe, no un `data-*` inventado para el cursor. Si mañana una diana nueva elige al rozar, tendrá
`aria-pressed` porque es lo correcto para ella, y la gota la vestirá sola.

**Ojo con el `figcaption`.** Está en `NATIVE_ZONE` y las piezas de Créditos y las tarjetas de Obra
llevan un `<figcaption>` *dentro* del botón. `closest()` con los dos selectores juntos devuelve el
ancestro **más cercano** que case cualquiera de los dos, no el primero de la lista: es la misma
resolución que Hyprland corrigió para `.credit-group-toggle` dentro de un `<p>`. Con
`target.closest(`${PRESSABLE}, ${NATIVE_ZONE}`)` el `figcaption` gana sobre su botón padre porque
está más cerca del puntero, y la gota se apagaría sobre la leyenda de cada tarjeta. **La resolución
aquí invierte la prioridad para ese caso:** si el nodo nativo más cercano está *dentro* de un
pulsable, manda el pulsable. Es el gate 2 quien lo vigila, con la leyenda de una tarjeta como caso.

## El reparto de señales

Idéntico al cerrado en Vice y en Hyprland, porque el problema es el mismo: sustituir el puntero es
legítimo, borrar las otras señales no.

| señal | quién manda |
|---|---|
| `pointer` | lo sustituye la gota |
| `grab` / `grabbing` de `.gallery-track` | **nativo**: única pista de que la galería se arrastra |
| I-beam sobre texto corrido | **nativo**: ocultarlo quita la señal de que se selecciona |
| enlaces `target="_blank"` (GitHub, LinkedIn en el dock y en las fichas) | **nativo**: abren pestaña nueva |

`cursor` solo se hereda cuando el hijo no declara el suyo, y los `<button>` y los `<a>` traen el
suyo de la hoja del navegador: el `cursor: none` del lienzo **no les llega**. La lista blanca se
apunta uno a uno bajo `.caelestia-cursor-ready:root[data-theme="caelestia"]`, igual que
`themes.css:7973-8125` hace para Vice y `8636-8705` para Hyprland. Un pulsable nuevo conserva su
glifo nativo mientras nadie lo apunte, que es lo que convierte la regla en lista blanca de verdad.

`.caelestia-cursor-ready` **la pone el JS solo tras montar con éxito.** Si el módulo no carga, no
existe ninguna de esas reglas y el puntero del sistema sigue intacto en toda la página.

### Corrección del 2026-09-04 (al escribir el plan) — la lista blanca no puede colgar de `[data-scene]`

El párrafo de arriba daba por bueno el patrón de Vice y Hyprland tal cual, que cuelga de
`[data-scene]`. **Medido en el build servido, en Caelestia eso deja fuera tres de las dianas de
este dispositivo**, dos de ellas del propio spec:

| diana | dónde vive de verdad | ¿dentro de `[data-scene]`? |
|---|---|---|
| las 5 tarjetas de Obra | `.cae-obra-card` → `.cae-obra-row` → `div#obra.obra-rail` → `main` | **no** |
| las 5 pastillas de workspace | `.cae-ws` → `.cae-ws-list` → `header.cae-bar` → `#app` | **no** |
| el dock | `.cae-dock-item` → `.cae-dock` → `#app` | **no** |
| las 23 piezas de Créditos | `.cae-cred-pieza` → … → `section#creditos[data-scene="credits"]` | sí |

La causa: los cinco workspaces son **los hijos directos de `main`**
(`caelestia.choreography.ts:63`, `Array.from(root.children)`), y el de Obra es `div#obra.obra-rail`,
que **no lleva `data-scene`**. El `[data-scene="obra"]` sí existe, anidado dentro, pero es el DOM
genérico de `projectScene.ts` que B3 oculta: mide 0×0. Con la regla colgando de `[data-scene]`, el
puntero del sistema seguiría visible justo encima de las dianas que este cursor existe para vestir.
Es la misma clase de fallo que Hyprland documentó para `.scene-nav-trigger`, pero aquí no toca un
caso raro: toca lo principal.

**La lista blanca cuelga de la raíz**, no de las escenas, y opta hacia fuera:

```css
.caelestia-cursor-ready:root[data-theme="caelestia"] { cursor: none; }
/* Texto corrido recupera su I-beam — salvo el que vive DENTRO de un pulsable
   (la leyenda de una tarjeta de Obra, el nombre de una pieza de Créditos):
   ahí manda el pulsable, igual que en la resolución de zona del módulo. */
.caelestia-cursor-ready:root[data-theme="caelestia"]
  :is(p, li, dd, dt, figcaption, blockquote):not(button *, a[href] *) { cursor: auto; }
/* Enlace externo y galería: nativos. */
.caelestia-cursor-ready:root[data-theme="caelestia"]
  :is(a[target="_blank"], .gallery-track) { cursor: auto; }
```

Sigue siendo lista blanca por el mismo mecanismo (la herencia solo alcanza a quien no declara
`cursor` propio) y sigue sin depender del JS: sin la clase no existe ninguna de las tres reglas.

**Nota de alcance para el arnés:** `.gallery-track` existe en el DOM (5 nodos) pero **es invisible
en Caelestia** — vive en el `projectScene.ts` que B3 oculta. Su línea aquí es preventiva, no
medida: el gate 2 **no puede afirmar que la mide** sin volverse tautológico. Mide lo que sí es
alcanzable: los `p` de Contacto y de «Quién soy», los `a[target="_blank"]` del dock y de la barra de
contacto, la leyenda de una tarjeta y el nombre de una pieza.

**Y `button[aria-pressed]` casa 46 nodos, no 23**: las 23 filas `.credit` del `credits.ts` genérico
también lo llevan, ocultas por `.credits-grid { display: none }`. No es un problema —un nodo oculto
no recibe `pointerover`, así que la familia de roce sigue siendo las 23 piezas visibles— pero ni el
módulo ni el arnés pueden **contar nodos** para decidir nada.

## Color y contraste

La gota vive sobre un fondo cuyo matiz gira con el reloj y cuyo esquema conmuta a las 07:00 y a las
20:00 **sin interpolar**. Todo lo que pinta lee tokens del motor (`--cae-primary`,
`--cae-on-surface`, `--cae-surface`) y el esquema por `[data-cae-esquema]`; el módulo no calcula
ningún color.

**Lo que es invariante por construcción y lo que no.** El núcleo (`on-surface`) y el estado hundido
(`on-surface` al 26%) lo son: `L` fija por rol. **La perla y el derrame no**: `multiply` y `screen`
mezclan el pigmento con lo que hay debajo, y el pigmento pierde dos tercios de croma cuando la marea
pasa por el naranja y el magenta (`chromaScaleAt`). Un cursor calibrado a una sola hora no está
calibrado, así que el gate 6 barre las 24 horas, como hizo B4.

**Dos materiales, uno por esquema.** Medido en la ronda 3: de noche la lente que satura no hace
nada (sobre superficie oscura no hay nada que saturar) y la perla se leía como disco. La noche tiene
material propio: la lente aclara, el brillo baja y pasa al canto, la sombra se vuelve halo. Es la
misma pieza vista con otra luz, no otra pieza.

| | día | noche |
|---|---|---|
| mezcla | `multiply` | `screen` |
| lente | `saturate(1.7) contrast(1.06) blur(.7px)` | `brightness(1.35) saturate(1.25) blur(.7px)` |
| tensión | brillo 0,55 / 0,95 | brillo 0,35 / 0,6 y canto encendido |
| sombra | `0 1px 2px` on-surface 32% | halo 6px primary 45% |
| derrame | primary 22% | primary 20% (calibrado, ver pregunta 4) |

**Lo que hay que medir, no dar por bueno:** el derrame va encima del texto de la diana. Con
`multiply` sobre texto oscuro el texto no cambia y el fondo se oscurece, así que el contraste baja;
con `screen` sobre texto claro, al revés. La leyenda de la tarjeta (`.cae-obra-caption`, Fraunces
itálica 14px) y la pastilla de workspace (12px) son los peores casos y **tienen que aguantar AA en
las 24 horas y los dos esquemas**. Si no, el derrame pasa al mecanismo de Hyprland (`background-image`
en línea, bajo el texto) — es una pregunta para el plan, no para el diseño.

**Medido (Task 7): no hizo falta cambiar de mecanismo, hizo falta calibrar.** El peor caso del
barrido completo es **4,92:1 en "obra 06:30"**, con la opacidad nocturna del derrame en 0,20 y no en
0,30. El detalle, la tabla de la calibración y por qué el mecanismo alternativo habría sido peor
(la tarjeta de Obra lleva un `<img>` que taparía un `background-image`) están en la pregunta 4.

## Movimiento

- Silueta, tamaño y opacidad de la perla: 300 ms, `cubic-bezier(.2, 0, 0, 1)` (*emphasized* de
  MD3, la curva base del tema).
- Rebote al posarse: 420 ms, un ciclo.
- Derrame: 420 ms `power2.out` al llenar; 180 ms al recoger tras el clic, 300 ms al secar al salir.
- Cerco: 800 ms `power2.out`, escala 0,6 → 2,1, opacidad 0,9 → 0.
- Apagado sobre zona nativa: 120 ms lineal.
- `prefers-reduced-motion: reduce`: el módulo no se monta. No hay versión degradada porque todo lo
  que hace este dispositivo *es* movimiento.

## Montaje y arquitectura

`src/main.ts`, la quinta entrada del patrón por tema, con las **tres puertas** antes de descargar
siquiera el módulo:

```ts
if (
  theme.id === "caelestia" &&
  !prefersReducedMotion &&
  window.matchMedia("(hover: hover) and (pointer: fine)").matches
) {
  void import("./components/caelestiaCursor").then(({ mountCaelestiaCursor }) => {
    caeCursorHandle = mountCaelestiaCursor(app);
  });
}
```

En táctil el coste correcto es **cero**, no "cero animación". El módulo devuelve un handle con
`destroy()` que se llama en `pagehide` con los demás. No hay leader ni encendido que tapen la
pantalla en Caelestia, así que se monta en cuanto el shell está montado (después de
`mountCaelestiaShell`, para que las pastillas ya existan).

**Dentro del módulo:**

- Un `div.cae-cursor` (`position: fixed`, `z-index` por encima del shell, `pointer-events: none`,
  `aria-hidden`) con la perla y el núcleo. **DOM, no canvas**: la perla necesita `backdrop-filter`
  y `mix-blend-mode`, que un lienzo 2D no da.
- Un `div.cae-cursor-mancha` (`position: fixed`, `overflow: hidden`, `border-radius` copiado de la
  diana, `pointer-events: none`) con el círculo del derrame dentro. Se coloca sobre la caja de la
  diana mojada y se recoloca por fotograma mientras haya diana, como hace Hyprland con el `rect`.
- Los cercos se crean al soltar y se eliminan al terminar su tween.
- Estado resuelto en `pointerover` (una vez por transición, no sesenta por segundo), posición en
  `pointermove`, `pointerdown`/`pointerup` para el derrame y el cerco, `scroll` marca `stale` y se
  revisa en el siguiente movimiento (Caelestia no tiene scroll de página, pero la ventana sí
  desplaza su contenido y el cajón de la Obra cambia la altura).
- **Cambio de workspace**: la diana bajo un ratón quieto deja de existir cuando el workspace se va
  y el anterior pasa a `inert`. El módulo escucha `caelestia:workspace` y marca `stale`, igual que
  hace con `scroll`.
- `destroy()`: cancela tweens, aborta el `AbortController`, elimina cursor, mancha y cercos vivos,
  quita `.caelestia-cursor-ready` y borra la sonda `__caeCursor__`.

**Sonda de verificación** (`window.__caeCursor__`), consumida solo por el arnés:
`estado()` (`reposo | perla | derrame | apagada`), `diana()` (el elemento mojado o `null`),
`mancha()` (escala actual del derrame, 0-1 normalizada), `destroy()`.

**Conflicto previsto en la fusión:** la fase B5 (Contacto) se está implementando en paralelo y las
dos ramas escriben en el bloque `:root[data-theme="caelestia"]` de `themes.css`. El bloque de este
cursor va **al final** del bloque de Caelestia, con su propio comentario de cabecera, para que el
conflicto sea de adyacencia y no de solape.

## Accesibilidad

- Nada de esto llega al árbol de accesibilidad: `aria-hidden` en los tres elementos.
- El foco de teclado no lo toca: el anillo de foco en azufre de la fase A sigue siendo el de
  `:focus-visible`, y las piezas de Créditos siguen eligiéndose por `focus`.
- Texto corrido conserva el I-beam y la selección.
- Contraste: gate 6, en las 24 horas y los dos esquemas.

## Los gates — `scripts/measure-caelestia-cursor.py`

Contra el build de producción servido (`npm run build && npx vite preview --port 4173`), nunca
contra `npm run dev`. **Con `page.hover()` real**: un `MouseEvent` sintético no dispara `:hover`, y
todo lo que hace este dispositivo ocurre en hover. **Ningún gate se da por bueno sin haberlo visto
dar rojo contra el fallo que dice cazar**: cada uno lleva su sabotaje escrito.

| # | gate | qué mide | sabotaje que tiene que ponerlo en rojo |
|---|---|---|---|
| 1 | presencia por tema | `?theme=caelestia` con puntero fino monta `.cae-cursor` y pone `.caelestia-cursor-ready`; `?theme=vice` y `?theme=hyprland` no; con `pointer: coarse` o `reduced-motion` **no se descarga el chunk** (se vigila la petición de red, no el DOM) | quitar una de las tres puertas de `main.ts` |
| 2 | reparto de señales | sobre `p` la gota está `apagada` y el `cursor` computado es `text`; sobre `a[target="_blank"]` es `pointer` nativo; sobre `.gallery-track` es `grab`; **sobre el `figcaption` de una tarjeta la gota sigue en `perla`** | añadir `figcaption` al `closest()` sin la inversión de prioridad |
| 3 | los dos momentos | hover en una pieza de Créditos → `derrame` y `mancha() > 0.9` **sin ningún clic**; hover en una tarjeta → `perla` y `mancha() === 0`; `mouse.down` → `derrame`; `mouse.up` → `perla` y existe un `.cae-cursor-cerco` que desaparece antes de 1,2 s | cambiar `HOVER_SELECT` por un selector que no case nada |
| 4 | sin inercia | tras `mouse.move(x, y)` y **un** `requestAnimationFrame`, el `transform` del cursor es exactamente `(x, y)`: delta 0 px, no "menor que" | meter un `lerp` en la posición |
| 5 | rancio tras cambiar de workspace | perla sobre una pastilla, cambio de workspace por teclado, ratón quieto: en el siguiente fotograma la diana es `null` y la mancha está seca | quitar la escucha de `caelestia:workspace` |
| 6 | contraste bajo el derrame | por glifo (no viewport), leyenda de tarjeta y texto de pastilla, con la mancha llena, **cada 30 minutos de las 24 horas y en los dos esquemas** (48 muestras × 2 dianas), medido con `__CAE_SET_MINUTOS__`: AA en todas, y la mancha **se nota** (delta de color contra la misma captura sin mancha por encima de un umbral fijado al ver la primera medida) | subir el derrame al 60%; y por el otro lado, ponerlo al 0% |
| 7 | limpieza | `destroy()` deja el DOM sin `.cae-cursor*`, sin la clase en `:root`, sin `__caeCursor__`, y un cerco lanzado justo antes también desaparece | comentar el `remove()` del cerco en `destroy()` |
| 8 | consola | cero `pageerror`, cero `console.error` en todo el barrido | el `gsap` sin desestructurar que ya rompió la coreografía de Hyprland |

El gate 6 hereda la lección del cursor de Hyprland: todos sus números se midieron contra una página
cuya coreografía estaba rota. **Antes de aceptar ningún contraste, la consola en verde.**

El arnés se añade a la tabla de `rules/verification.md`.

## Móvil — fuera de alcance, sin deuda

No hay nada que hacer en táctil: el módulo no se descarga (gate 1). Es el mismo criterio de Vice y
Hyprland y no deja deuda, a diferencia de B1-B4.

## Preguntas abiertas para el plan

1. **Mancha encima o debajo del texto.** El diseño la pone encima con mezcla. Si el gate 6 no
   aguanta AA en algún punto del barrido, el mecanismo pasa a `background-image` en línea en la
   diana (bajo el texto), el patrón de Hyprland, y entonces hay que restaurar el valor previo en
   `destroy()` y al cambiar de diana. Se decide con la primera medida, no antes.
2. **El derrame sobre las piezas de Créditos**: la caja mojada es el `<button>` (88 × 113, con la
   leyenda) con radio 10px (el mismo del anillo de foco), no la figura recortada. Está probado en la
   maqueta y se lee bien; si al implementarlo la figura y el rectángulo se pelean, la alternativa es
   recortar la mancha con el `--fig` de la pieza, que ya está en línea.
3. **`backdrop-filter` en un elemento que se mueve a 60 fps** sobre un lienzo WebGL: en la maqueta
   no cuesta nada, pero la maqueta no lleva el shader. Medir en el build real; si penaliza, la lente
   se queda solo en `perla` (quieta sobre una diana) y se apaga en `reposo`.

   **Medido (Task 5), build de producción bajo swiftshader, moviendo el ratón en diagonal 30
   pasos, mediana/p95 de fotograma en 3s por brazo:**

   | Orden | con lente | sin lente |
   |---|---|---|
   | 1 | 182.8 / 207.9 ms (n=18) | 198.6 / 237.3 ms (n=17) |
   | 2 (invertido) | 175.3 / 217.8 ms (n=19) | 200.1 / 254.9 ms (n=17) |

   Con lente sale entre un 7 % y un 12 % *más rápido* que sin lente en las dos direcciones de
   medida. Ese signo es físicamente inverosímil para trabajo de composición en GPU — un
   `backdrop-filter` no puede hacer que el fotograma vaya más rápido — así que lo que dice el
   resultado no es "la lente no cuesta", dice **que el instrumento no aisló el efecto**: bajo
   swiftshader el tiempo de fotograma lo domina el shader de fondo (~5-6 fps de base), y el coste
   de un `backdrop-filter` sobre un círculo de 15-20px queda por debajo del ruido de esa medida. Un
   resultado negativo en las dos direcciones no confirma que no haya coste; confirma que **esta
   medida no puede zanjar la pregunta en ningún sentido, ni a favor ni en contra**.

   **La decisión de dejar la lente encendida en los tres estados, incluido `reposo`, descansa por
   tanto en un supuesto sin medir**, no en una medida que lo respalde. Sigue siendo el valor por
   defecto correcto porque no hay evidencia de coste — pero la validación en una GPU real (sin
   swiftshader de por medio) queda pendiente y abierta, no cerrada por esta tabla. No se añade la
   regla de apagado mientras tanto: no hay evidencia que la justifique, solo la ausencia de una
   medida que pueda confirmarla o descartarla.
4. **El umbral de "se nota"** del gate 6 se fija al ver la primera medida, y se anota aquí.

   **Medido (Task 7), 2026-09-05, build de producción bajo swiftshader, barrido completo de las 24
   horas en dos mitades foreground (`--mitad 1` 00:00-11:30, `--mitad 2` 12:00-23:30, 30 min de
   paso, `.cae-obra-caption` y `.cae-cred-nom` contra el fondo real):**

   - **Peor delta medio de perceptibilidad: 13,25 en "obra 09:00"** (de las 4 medidas fijas:
     obra/créditos × 09:00/03:00 — todas caen en la primera mitad, por eso la segunda no repite la
     medida). `UMBRAL_NOTA = 6,625` — la MITAD de ese valor, margen explícito frente al ruido del
     compositor y no un umbral pegado a la medida.
   - **Peor contraste AA: 4,06:1 en "obra 06:30"** (mitad 1) y 4,12:1 en "obra 22:00" (mitad 2) —
     **las dos por debajo de 4,5:1**. Las dos peores horas caen de noche (`mix-blend-mode: screen`,
     derrame al 30 % de opacidad). Confirmado con el sabotaje al 0 % (opacidad 0 en las dos reglas,
     día y noche): el mismo recorte a la misma hora sube a **7,42:1** — la caída de 7,42 a 4,06 es
     enteramente atribuible al derrame, no a un fallo de instrumento.

   **Primera lectura: el gate 6 en ROJO, y no por error de medida.** El mecanismo elegido —pintar
   el derrame ENCIMA del texto con `mix-blend-mode`— no aguantaba AA en la franja nocturna. Las dos
   peores horas caían de noche (`screen`, derrame al 30 %).

   **Resuelto el 2026-09-05 recalibrando, sin cambiar de mecanismo.** Antes de rearquitecturar se
   barrió la opacidad nocturna (0,30 / 0,26 / 0,22 / 0,20 / 0,18) contra las horas peores, con la
   misma medida por glifo del arnés. La relación es monótona y limpia:

   | opacidad noche | peor contraste | peor delta |
   |---|---|---|
   | 0,30 | 4,06:1 (obra 06:30) | 26,06 |
   | 0,26 | 4,37:1 | 22,48 |
   | 0,22 | 4,74:1 | 19,25 |
   | **0,20** | **4,92:1** (barrido completo) | **13,25** |
   | 0,18 | 5,12:1 | 15,86 |

   Se elige **0,20** y no 0,22: deja 0,43 de margen sobre AA en vez de 0,24, y el derrame sigue
   notándose al doble del umbral. **De día se queda en 0,22** — no es el mismo número porque no es
   la misma mezcla: `multiply` sobre papel claro oscurece el fondo del texto, `screen` sobre
   superficie oscura lo aclara, y es esto último lo que le come contraste. Reutilizar la cifra
   habría sido la enésima repetición del error que este proyecto ya tiene escrito: *una opacidad se
   calibra contra una superficie, no contra un token*.

   Barrido completo posterior, en verde: **peor 4,92:1 en "obra 06:30"**, peor delta 13,25 en
   "obra 09:00".

   **Por qué NO se aplicó la pregunta abierta 1** (mover el derrame a un `background-image` bajo el
   texto, el patrón de Hyprland): además de innecesaria, habría sido *peor*. Un `background-image`
   se pinta bajo el contenido del elemento, y la tarjeta de Obra tiene un `<img>` como hijo que
   ocupa casi toda su caja — el derrame habría desaparecido justo en la escena donde más se ve. La
   pregunta 1 queda **cerrada**: el derrame se queda encima, con el número calibrado.

   **Sabotajes del gate 6, los dos vistos en rojo:**
   - *AA*: subir la opacidad nocturna de 0,20 a 0,30 devuelve el peor caso a 4,06:1 y el check da
     FAIL. Es el sabotaje que sí aísla el mecanismo. **El del plan (subir `.cae-cursor-gota` a
     0,6) no vale**: toca solo la regla de día, y la regla de noche
     (`:root[data-cae-esquema="noche"] ...`) tiene más especificidad y gana en las horas donde está
     el peor caso.
   - *"se nota"*: opacidad 0 en las dos reglas → delta 0,00 → FAIL.

   **Y una décima aserción tautológica cazada aquí.** Con `--mitad 2` el `check` de perceptibilidad
   salía VERDE sin haber tomado ni una medida: las dos horas de perceptibilidad caen en la primera
   mitad, y el centinela con el que arranca el peor delta (999.0) supera cualquier umbral. Ahora la
   mitad que no cubre esas horas **dice que no las mide**, en vez de afirmar que pasan.

5. **La limpieza de `destroy()`** (Task 8). El gate 7 se vio en rojo por la razón que anticipó el
   Task 4: `destroy()` se llevaba `cursor` y `mancha`, pero los cercos cuelgan de `host` y
   sobrevivían — un nodo huérfano animándose y su temporizador de respaldo de 1200 ms apuntando a
   un nodo sin dueño. Se retiran **a través de `retirarCerco`**, iterando una copia del `Set`,
   porque es lo único que además cancela el temporizador; un `remove()` crudo habría dejado
   pasar la mitad del fallo.


## Trampas ya pagadas en esta sesión

- **Un `let` de nivel superior no está disponible antes de su línea.** Dos maquetas seguidas
  reventaron con `Cannot access 'tl' before initialization` porque una función llamada en la
  inicialización leía una variable declarada más abajo. En la maqueta no se ve nada: el script muere
  en silencio y el cursor no existe. Solo lo cazó escuchar `pageerror` antes de enseñar nada.
- **El pigmento sobre la pieza elegida es invisible.** La pieza elegida de Créditos se pinta con
  `--cae-primary`; una gota de `--cae-primary` encima no se ve, en ningún esquema. Por eso el estado
  hundido lleva tinta (`on-surface`) y no pigmento.
- **Un `MouseEvent` sintético no dispara `:hover`**, y aquí todo pasa en hover: las capturas de
  este documento se tomaron con `page.hover()` real, y el recorrido guiado de la maqueta pone las
  clases a mano por la misma razón (la maqueta no depende de `:hover` en ningún punto).

## Registro de implementación (2026-09-05)

Ejecutado con `superpowers:subagent-driven-development` en el worktree `portfolio-aoshi-cursor`,
rama `design/caelestia-cursor`. Nueve tareas, 17 commits. El registro por rondas vive en
`.superpowers/sdd/2026-09-04-caelestia-cursor/progress.md` (ignorado por git); si se pierde, la
historia de git es el registro que queda.

**Números finales del gate 6** (barrido completo de 24 horas, paso de 30 minutos, dos dianas,
medida por glifo contra el fondo real, build de producción):

- Peor contraste bajo el derrame: **4,92:1 en "obra 06:30"** (AA = 4,5).
- Peor delta medio de perceptibilidad: **13,25 en "obra 09:00"**; umbral `UMBRAL_NOTA = 6,625`,
  fijado en la mitad de la primera medida.
- Mecanismo del derrame: **encima del texto, con mezcla** (`multiply` de día, `screen` de noche).
  La alternativa del diseño —`background-image` bajo el texto, patrón de Hyprland— queda descartada
  con razón medida, no por preferencia: se pinta bajo los hijos del elemento y la tarjeta de Obra
  lleva un `<img>` que la taparía.

### Lo que se desvió del diseño, y por qué

1. **La lista blanca no podía colgar de `[data-scene]`.** Las tarjetas de Obra, las pastillas del
   shell y el dock viven fuera de ese subárbol. Cuelga de la raíz, con una regla de opt-in explícita
   para los pulsables: `<button>` y `<a>` declaran su propio `cursor` en la hoja del navegador, así
   que la herencia nunca los alcanza.
2. **`cursor: auto` no computa a `"text"`.** El navegador devuelve la palabra clave tal cual. El
   texto corrido lleva `cursor: text` literal, lo que diverge de lo que hacen Vice y Hyprland.
3. **La regla de rescate que el plan escribió rompía las dos señales que venía a proteger**: sobre
   un enlace externo pisaba su `pointer` nativo, y sobre `.gallery-track` pisaba su `grab` con una
   especificidad de (0,4,0) contra (0,1,0). Se resolvió borrándola: el elemento que declara su
   propio cursor no necesita rescate, porque la herencia no le llega.
4. **`button[aria-pressed]` casa 46 nodos, no 23.** El corte entre las dos familias sigue siendo
   ese selector, pero el número del spec estaba mal contado.
5. **La opacidad nocturna del derrame bajó de 0,30 a 0,20** tras medir. Es la única recalibración
   de color de toda la ejecución. Ver la pregunta abierta 4.

### Qué instrumento resultó estar roto

Cinco, y es un dato, no un hueco:

1. **El gate del estado rancio era infalsificable.** Chromium dispara `pointerout` sobre el elemento
   mojado en cuanto su escena pasa a `inert`, unos 50 ms antes de que el carril termine: eso sanaba
   el estado por la vía nativa y quitar el listener del módulo no ponía el gate en rojo. Ahora tiene
   dos familias: el mecanismo propio con la sanación nativa suprimida, y el camino del visitante.
2. **Un umbral más fino que el ruido de su instrumento** (`> 0.9` tras una espera fija para una
   transición de 420 ms; medía 0,89). Se arregló haciendo la espera determinista y la aserción
   **más estricta** (`>= 0.99`), no más floja.
3. **Un muestreo del rebote que leía `transform`** cuando la animación mueve la propiedad `scale`
   suelta. Medía siempre lo mismo.
4. **La aserción de perceptibilidad salía verde sin medir nada con `--mitad 2`**: el centinela
   (999.0) supera cualquier umbral y las dos horas de perceptibilidad caen en la primera mitad. Es
   la décima aserción tautológica de esta pista. Ahora dice que no las mide.
5. **El sabotaje de AA del plan no sabotea nada.** Subir `.cae-cursor-gota` a 0,6 toca solo la regla
   de día; la de noche tiene más especificidad y gana justo en las horas del peor caso. El sabotaje
   que sí aísla el mecanismo es subir la opacidad **nocturna** de 0,20 a 0,30, que devuelve el peor
   caso a 4,06:1.

Y un fallo de proceso que costó tres turnos: **los subagentes se van solos a ejecución en segundo
plano**, y su propia parada mata la corrida. El barrido largo hubo que partirlo en dos mitades
detrás de una bandera de CLI para que cupiera en una llamada en primer plano.

### Lo que encontro la revision final de rama (2026-09-05)

Revision adversarial en el modelo mas capaz, en modo lectura, con los 11 minors diferidos delante
para triarlos. Cinco hallazgos, los cinco cerrados antes de fusionar.

1. **Con movimiento reducido activado DESPUES de montar, la pagina se quedaba sin ningun cursor.**
   La guardia de cinturon y tirantes esconde `.cae-cursor`, pero nada revertia el `cursor: none` de
   la raiz ni el opt-in de los pulsables, y la puerta de `main.ts` solo mira AL CARGAR. Era el
   fallo exacto para el perfil al que la guardia dice proteger. Arreglado **acotando la lista
   blanca** a `@media (prefers-reduced-motion: no-preference)`, y no con una regla de rescate: un
   rescate tendria que ganarle en especificidad a la regla que quita el glifo, y al hacerlo le
   ganaria tambien al `cursor: pointer` que cada pulsable declara por su cuenta — el mismo defecto
   que esta rama ya pago dos veces. Acotando, bajo `reduce` esas reglas simplemente no existen y
   cada elemento se queda con lo que ya declaraba (medido: raiz `auto`, pulsable `pointer`).
2. **Las paginas de Vice y Hyprland del gate 1 corrian sin oyente de consola.** Son las unicas de
   todo el arnes que abren esos dos temas, esta rama toca `themes.css` (global) y `main.ts`, y un
   fallo alli habria dejado el gate en VERDE: solo comprueba que `.cae-cursor` NO exista, que es
   justo lo que pasa cuando algo revienta. Es el modo de fallo del `gsap` sin desestructurar de
   Hyprland, que estuvo semanas invisible. Enganchadas a la misma lista que vigila el gate 8.
3. **El clic DERECHO derramaba y dejaba cerco.** Un menu contextual no es una activacion, y el
   cerco esta escrito aqui como la marca de haber SOLTADO un clic sobre una diana de clic: era la
   unica senal del dispositivo disparandose por algo que no ocurrio.
4. **Este mismo documento describia el derrame y el cerco como GSAP.** No lo son. Corregido.
5. La etiqueta del check de AA decia "en las 24 horas" tambien corriendo con `--mitad`.

**Triaje de los 11 minors diferidos:** tres NO eran problema —dos con la premisa falsa (`main()`
si cierra Chromium, porque el bloque vive dentro de `with sync_playwright()`; y el
`void HOVER_SELECT` dejo de existir en el Task 3) y uno que resulta ser lo CORRECTO (que `secar()`
deje quietas las coordenadas de la mancha: la caja tiene que quedarse donde esta mientras la gota
se recoge, o el liquido se recogeria hacia un sitio equivocado)—, siete quedan como deuda anotada
y uno se arreglo (el `z-index: 71` del cerco sin su comentario de escalera).
