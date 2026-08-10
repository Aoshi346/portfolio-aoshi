# El catastro — "Con qué construyo" en Hyprland deja de ser una lista y pasa a ser un reparto de territorio

Estado: pendiente de plan
Fecha: 2026-08-10
Alcance: **solo el tema Hyprland**. `[data-scene="credits"]` (`src/sections/skills.ts`,
`src/components/credits.ts`, `src/style.css`, `src/themes/themes.css`,
`src/themes/hypr.choreography.ts`, `scripts/verify.py`). **Vice no se toca** (cerrado el
2026-08-05). **Caelestia no se toca**: se comprueba que sigue idéntico.
Contenido: **`src/data/content.ts` no cambia**. Toda cadena sale literal de ese fichero, y la
jerarquía nueva se deriva de datos que ya estaban ahí sin cruzar.

Prototipo aprobado por Aoshi, medido y con los números de este documento:
`.superpowers/brainstorm/2892129-1786377307/content/catastro-v2.html`.

---

## Diagnóstico — por qué la composición actual no funciona

Medido sobre el sitio real en `?theme=hyprland`, desktop 1440×900 y móvil 390×844.

1. **Dos paneles translúcidos apilados.** `.credits-list` y `.credits-panel` conservan el
   `border-radius: var(--radius-card)` y el `backdrop-filter` de la base compartida
   (`src/style.css`). Es el look de tarjeta de Caelestia, y Ascua se construye sobre filetes de
   1px y radio 0. Las píldoras del cruce (`.credits-used-item`, `border-radius: 999px`) son el
   mismo problema.
2. **Desktop desperdicia 340px.** El contenido para en x=1100 de 1440.
3. **La causa y el efecto no comparten golpe de vista.** Se apunta un nombre en la lista y lo
   que cambia es un panel que está en otro bloque de la página.
4. **En móvil el panel está por encima de la lista.** Se toca un nombre y lo que cambia queda
   fuera de pantalla — y en táctil no hay hover, así que ese es el único modo de uso real. La
   sección mide 1134px y se corta.
5. **La prosa borra los grupos.** `themes.css:4377-4405` ya convirtió la lista en párrafo
   (`display: inline`, nombres separados por `/`). Los cuatro rótulos existen pero flotan sobre
   un río de nombres: el ojo no puede medir cuánto hay en cada área. Para una sección que va de
   áreas, esto es peor que las píldoras que sustituyó.
6. **23 nombres del mismo tamaño y la misma cara.** Cero jerarquía.
7. **23 marcas reales de las que se ve una.** Están en el bundle y en el DOM, apagadas con un
   `display: none` en la base compartida que solo Vice enciende.
8. **La promesa incumplida.** El spec de Ascua le asignó a esta escena el "encendido en cadena
   como lámparas". Hoy el realce es un cambio de color.

## Lo que ya está pagado (auditoría de coste, medida sobre `dist/`)

Esto condiciona el diseño, así que va antes que él:

- Bundle JS inicial: 71,65 KB crudo / **27,74 KB gzip**. GSAP, ScrollTrigger, Lenis y los
  módulos de tema van en `import()` diferido; no entran ahí.
- Los 23 SVG de `simple-icons` pesan **30 117 bytes exactos**, inlineados como literales por
  Vite. Son el **42% del JS inicial en crudo** (~45% del gzip). **Ese coste ya se paga hoy**,
  con o sin rediseño.
- La sección monta hoy **181 nodos, 23 botones, 23 marcas (con `display:none`), 48 nodos SVG
  internos y 69 listeners**.
- CSS: hoja única de 117,14 KB crudo / **19,76 KB gzip** para los tres temas. No se puede
  diferir el de Hyprland: llega entero al first paint aunque el visitante caiga en Vice.

**Consecuencia de diseño:** encender las 23 marcas cuesta **cero bytes y cero nodos**. Es una
línea de CSS. Lo que hay que presupuestar no es su existencia, es su animación.

## Dirección elegida — el catastro

Cuatro **parcelas** contiguas que se reparten el encuadre entero, sin hueco entre ellas,
separadas por linderos de 1px en `--rule` y cerradas por un perímetro exterior de 1px.
**El ancho de cada parcela es proporcional a cuántas tecnologías contiene** (8/5/5/5 sobre 23).

Por qué esta forma dice territorio y no atmósfera:

- **Particiona, no decora.** Un catastro no coloca objetos sobre un fondo: reparte una
  superficie finita. No queda "fuera de las parcelas". Eso es la tesis de producto — el mensaje
  son las cuatro áreas — dicha por geometría y no por un rótulo que lo anuncia.
- **El área ES el dato.** Interfaz mide 450px y Herramientas 281px porque hay 8 y 5. La
  jerarquía la carga la superficie, no el cuerpo de letra.
- **Tiene borde, no niebla.** Filete de 1px, radio 0, perímetro cerrado: el vocabulario literal
  del tema. Una atmósfera no se mide con una regla; un lindero sí.

### No colisiona con ningún dispositivo ya usado

| Escena | Dispositivo | Gramática de movimiento |
|---|---|---|
| hero | el lomo | corte de máscara |
| obra | el cartel | crecimiento / tamaño |
| quién soy | la placa | llegada y cuña de tinta (geometría, al apuntar) |
| **con qué construyo** | **el catastro** | **corriente y destello (luz, en la entrada)** |
| contacto | las bandas | inundación lateral de un área |

El catastro comparte con la placa el filete de 1px porque **el tema entero se construye sobre
él**, igual que Vice comparte tinta entre el cartel y el carril. Se distinguen en que la placa
es una rejilla heterogénea de celdas ancladas arriba y el catastro es **una sola partición en
cuatro con anchos derivados del dato**, cuya unidad es la columna entera. El perímetro cerrado
es además la oposición deliberada a las bandas, que van a sangre.

### Elemento firma — el amojonamiento

Cada parcela lleva, bajo su cabecera, un friso de sus marcas reales a 14px en `--haze`: sus
mojones. Ocho marcas juntas frente a cinco es una **textura de densidad** que refuerza el ancho
de la parcela — dos señales de lo mismo, que es como se construye una jerarquía que se lee sin
leer.

Al apuntar, la marca elegida sube a `--l1` y a escala 1,28 **y las demás bajan a opacidad
0,42**: se realza quitando, no añadiendo. Nunca con `filter` ni `box-shadow`, que es la línea
roja con un shader a pantalla completa corriendo detrás.

## Composición

### Desktop 1440×900

Márgenes de `5vw` = 72px → catastro de **1296px**, con perímetro de 1px.

```
 ┌──────────────────────────────────────────────────────────────┐
 │ con qué construyo                                            │  74 + 40 de aire
 ├─────────────────┬──────────┬──────────┬───────────────────────┤
 │ INTERFAZ     8  │ BACKEND 5│ LENGUAJ.5│ HERRAMIENTAS       5  │  cabecera 54
 ├─────────────────┼──────────┼──────────┼───────────────────────┤
 │ ▪▪▪▪▪▪▪▪        │ ▪▪▪▪▪    │ ▪▪▪▪▪    │ ▪▪▪▪▪                 │  mojones 36
 ├─────────────────┼──────────┼──────────┼───────────────────────┤
 │ React           │ Python   │ JavaScript│ Git                  │
 │ Next.js         │          │           │                      │  nombres
 │ TypeScript      │ Django   │ HTML      │ GitHub               │  REPARTIDOS
 │ …               │ …        │ …         │ …                    │  por el alto
 ├─────────────────┼──────────┼──────────┼───────────────────────┤
 │ ⬛ React        │ ⬛ Python │ ⬛ JavaSc.│ ⬛ Git                │  franja 126
 │ Interfaces con… │ …        │ …         │ …                    │  (altura FIJA)
 │ APARECE EN  EchoPlan │ HyprFinance                            │
 └─────────────────┴──────────┴──────────┴───────────────────────┘
     450px          281px      281px      281px
```

- **Los nombres se reparten por el alto de la parcela** (`justify-content: space-between`), no
  se amontonan arriba. Sin esto, las tres parcelas de 5 dejan un agujero visible al pie y el
  recuento se dice dos veces (ancho *y* alto). Repartidos, la segunda señal pasa a ser
  **densidad**: Interfaz apretada, Herramientas con aire.
- **La franja tiene altura fija (126px)**, no mínima. Medido en el prototipo: los cuatro pies
  cierran a la misma cota (752px los cuatro). Con altura mínima, la parcela cuyo cruce ocupa
  más líneas sube su pie y el rectángulo deja de cerrar.
- Suelo de ancho `minmax(240px, Nfr)` y tope de proporción 2,2:1. Si `content.ts` desequilibra
  el reparto, se recorta: la proporción es lectura, no aritmética exacta.
- **Los 340px muertos desaparecen por construcción**: el dispositivo ocupa el ancho de
  contenido entero.

### Móvil 390×844

Parcelas apiladas, **calle de 26px a cada lado** — fijada, no derivada del `5vw` del tema: a
390px ese mismo 5vw deja 20px y un rectángulo de borde duro queda casi a sangre.

- **Rejilla de dos columnas** dentro de cada parcela, no flujo de palabras. El flujo
  reintroduce por la puerta de atrás la prosa que borra los grupos, que es el defecto 5 del
  diagnóstico.
- **El friso de mojones solo en la parcela activa**, y a 17px. Con los cuatro frisos a la vez
  son 23 iconos de 14px compitiendo con 23 nombres en 390px de ancho.
- **Solo la parcela activa tiene su franja abierta**, exactamente una en todo momento: la
  altura total no cambia al elegir y nada de lo que hay debajo se mueve.
- Medido en el prototipo: alto **1007px**, calles 26/26, diana táctil **44px**, ningún nombre
  desborda su celda, ninguna lista desborda su parcela. Frente a los **1134px que hoy se
  cortan**.

Coste asumido y consciente: la rejilla de dos columnas cuesta ~120px de alto frente al flujo
(8 nombres ocupan 4 filas donde el flujo metía 3). Se paga porque la alineación vale más que
120px de scroll. La palanca que queda, si algún día hace falta, es plegar los territorios no
activos (~710px) — no se hace ahora porque esconde los 23 nombres tras un toque, y eso es una
decisión de producto.

## Tipografía y jerarquía

Escalones **discretos** por `@container`/`@media`. Nunca `clamp()` continuo sobre tokens de
escala.

| Nivel | Cara / peso | Tamaño | Color |
|---|---|---|---|
| Título de sección | Bricolage 600, caja baja | `--t-5` / `--t-6` ≥820 | `--text` |
| Rótulo de área | Instrument Sans 600, versal, tracking .24em | `--t-1` | `--haze` |
| Recuento de la parcela | Bricolage 600 | `--t-3` | `--l1` |
| Nombre — nivel alto | Bricolage 600 | 23px | `--text` |
| Nombre — nivel medio | Bricolage 600 | 20px | `--text` |
| Nombre — nivel bajo | Bricolage 600 | 15px | `--haze` |
| Detalle (franja) | Instrument Sans 400 | `--t-2` | `--text` 88% |
| "Aparece en" (rótulo) | Instrument Sans 600, versal | `--t-1` | `--haze` |
| Proyecto (cruce) | Instrument Sans 500 | `--t-2` | `--catch` |

Los tres tamaños de nombre están en px porque son los valores medidos en el prototipo; al
implementar se anclan al escalón más cercano de la escala `--t-*` del tema, no se escriben
como literales sueltos.

**La itálica reservada no se usa aquí.** No existe en `content.ts` ninguna frase en primera
persona para esta escena, y escribirla sería contenido disfrazado de diseño.

### La jerarquía sale del dato, y se mide POR PARCELA

La evidencia de cada tecnología es su aparición en `stack` **∪** `tooling` de los proyectos —
exactamente el cruce que `credits.ts` ya hace hoy. El nivel se calcula **contra el máximo de su
propia parcela**, no contra un máximo global.

Por qué por parcela: con vara global, las cinco herramientas caen a cero y **un cuarto del
catastro queda apagado**. `tooling` existe precisamente porque Git, GitHub y las dos CLI están
en todos los proyectos — medirlas contra `stack` las declara vacías siendo lo contrario. Y
comparar entre territorios nunca fue el mensaje de esta escena.

Resultado: Git y GitHub encabezan Herramientas (5 obras), TypeScript encabeza Interfaz (3),
Python encabeza Backend (2). Quedan **7 nombres en el nivel bajo repartidos 1/2/3/1** entre las
cuatro parcelas. Ninguna parcela queda apagada. **Ni una cadena nueva en `content.ts`.**

### Regla de color: el acento no marca rango entre elementos comparables

`--l1`/`--l3` significan **encendido** en toda la escena: la luz del lindero, el mojón activo,
el rótulo del territorio al activarse. Usarlos **además** como nivel tipográfico hacía que seis
nombres se leyeran como permanentemente apuntados — un falso hover, detectado en revisión y
corregido en el prototipo.

La primera redacción de esta regla decía "el acento es estado, nunca taxonomía", y se
contradecía con la tabla de arriba, que da `--l1` al recuento de cada parcela. Se corrigió
tras cazar la contradicción al implementar: **lo que no se puede hacer es ordenar con color un
conjunto de elementos comparables entre sí**. Los 23 nombres lo son, y ahí el color mentía. El
recuento no compite con ellos: hay uno por territorio, no es seleccionable y no cambia de
estado nunca, así que su naranja se lee como la cifra del sitio y no como algo encendido.

- **El nivel de una tecnología se dice solo con tipografía** (23/20/15px). Los nombres viven en
  `--text` o `--haze`, nunca en un acento.
- **Entre los nombres, el acento aparece únicamente en lo apuntado.** Liberado, el nombre
  apuntado puede ir a `--l3`, que separa mucho más que el `--catch` pálido que se usaba antes.
- **El recuento de la parcela va en `--l1` en las cuatro cabeceras.** No se enciende solo en la
  abierta: en escritorio las cuatro están siempre abiertas, y hacerlo dependiente del estado
  daría al mismo elemento significados distintos según el ancho de pantalla.
- **En reposo no hay ningún nombre encendido**, tampoco el sembrado inicial. La franja arranca
  **llena** para no dejar un hueco esperando interacción, pero llenar no es encender: en reposo
  todavía no ha pasado nada. Es una aserción, no una intención: `getComputedStyle` de los 23
  nombres, ninguno en un color de acento.

## Movimiento

Curvas del tema: atmosférico **900ms** `cubic-bezier(.16,.84,.28,1)`; cortes **400–500ms**
`cubic-bezier(.7,0,.2,1)`, sin rebote.

### Entrada — "la corriente"

| # | Qué | Empieza (parcela `c`=0..3) | Dur | Curva |
|---|---|---|---|---|
| 1 | El carril se dibuja de arriba abajo | `c*90` | 500 | corte |
| 2 | El rótulo entra con corte de máscara lateral | `c*90 + 140` | 420 | corte |
| 3 | La chispa recorre el carril, velocidad constante | `c*90 + 260` | 620 | lineal |
| 4 | Cada nombre prende al pasar la chispa | `c*90 + 260 + i/(n−1)*620` | 140↑ / 260↓ | corte / atmosf. |
| 5 | Las franjas se posan | 900 | 620 | atmosférico |

**Duración total 1520ms. El mensaje —los cuatro territorios dibujados y rotulados— cierra a los
830ms**; el resto es evidencia llegando.

El orden es el orden del argumento: primero el límite, luego el nombre del sitio, luego lo que
hay dentro, y al final dónde se comprueba. Si los nombres entraran antes que los rótulos, la
escena diría "23 tecnologías agrupadas de alguna manera", que es lo que dice hoy.

**Las cuatro chispas salen escalonadas 90ms y llegan abajo a la vez**, porque las cuatro
parcelas miden lo mismo y la velocidad es constante. Cuatro territorios que prenden en paralelo
lee mejor que cuatro que acaban desordenados. Escalonado de 90ms entre territorios (no los 70
del paso interno del tema): entre territorios se quiere un paso perceptiblemente mayor para que
se lean como cuatro cosas y no como ocho.

**Reparto de coste, que es decisión de arquitectura y no de estilo:** GSAP mueve **13 nodos como
mucho** (4 carriles, 4 rótulos, 4 chispas, las franjas). **Las 23 lámparas las enciende CSS**
con `animation-delay` por nombre — el patrón que el tema ya tiene (`--hypr-d`, `--placa-d`) y
que su propio comentario declara: las clases hacen el trabajo, GSAP solo decide cuándo. En el
pico hay ~7 destellos en vuelo por parcela; como animaciones CSS lo lleva el motor de estilo,
como 28 tweens escribiendo estilo inline por fotograma con un shader detrás, no.

**Trampa que esto abre y hay que cerrar en el mismo sitio:** una `animation` con
`fill-mode: forwards` gana a una `transition` en la cascada y dejaría el apuntado sin color. Es
el primo hermano del "transform inline de GSAP gana a la regla CSS" ya documentado. El
fotograma 100% del `@keyframes` debe ser **idéntico** al valor de reposo, con
`animation-fill-mode: backwards`.

**Acoplamiento a dejar escrito en el módulo:** el retardo por nombre **es** la posición de la
chispa. Si cambia la altura de fila y no cambia el retardo, el gesto miente — el mismo tipo de
acoplamiento que `OBRA_TRANSIT` con su arnés.

**Móvil:** cuatro ScrollTriggers, uno por parcela (`start: "top 86%"`, `once: true`). Cada
territorio prende al entrar y la chispa salta de estación en estación conforme bajas. **Cero
pins nuevos**: la escalera de `refreshPriority` de Vice no se toca.

### Apuntado — "la toma de corriente"

`:hover`, `:focus-visible` y `.is-active` comparten regla: teclado y táctil entran por la misma
puerta sin una segunda implementación. `credits.ts` ya dispara la selección en `mouseenter`,
`focus` y `click`.

| Qué | Encender | Apagar |
|---|---|---|
| **La luz del lindero viaja** hasta la fila apuntada | `quickTo`, 420ms, `power4.out` | 900ms atmosférico |
| Nombre → `--l3`, y `translateX(6px)` **en el hijo**, nunca en el `<button>` | 420ms corte | 900ms atmosférico |
| Rótulo del área → `--l3` | **900ms atmosférico** | 900ms atmosférico |
| La franja rueda: lo viejo sale por arriba, lo nuevo entra por abajo | 420 / 300ms, solapados | — |
| El friso se aparta: los no elegidos a opacidad 0,42 | 420ms corte | 420ms |

**La luz tiene peso, y esa es la micro-interacción con firma.** No salta a la fila: la lleva un
`quickTo`, así que al recorrer nombres *viaja* por el carril y un salto de Git a Gemini CLI se
ve recorrer. Es la misma idea de la entrada —corriente por un cable— sostenida dentro del
apuntado en vez de abandonada al acabar, y es lo que quita la sensación de estático: hay un
objeto físico moviéndose, no estados relevándose.

**El rótulo del área va lento a propósito, y es el único elemento que rompe el ritmo.** Apuntar
Django no solo enciende Django: calienta despacio "Backend y datos". Lo rápido es la acción, lo
lento es el contexto. Esa es la frase de la escena.

**El rodillo de la franja: los dos nodos van siempre en `position: absolute`.** Cambiar de
absoluto a estático a mitad de gesto desplaza el contenido (un absoluto se posiciona contra la
caja de padding) y pega un tirón justo al terminar. El padding vive en el nodo interior.

**Barrido antes de montar.** Recorriendo nombres rápido llegan varias selecciones dentro de los
420ms del rodillo y los nodos se apilan sin límite. Se matan los tweens y se retira todo lo que
no sea el actual. Verificado con 6 selecciones en 600ms: queda 1 nodo.

**Descartado a propósito:** que el recuento de la cabecera rodase al activarse la parcela. El
número no cambia, así que animarlo miente sobre un cambio que no existe.

### Ambiente

**Ningún bucle nuevo.** El gesto 3 de `hypr.choreography.ts` ya escribe `--bx`/`--by` en
`:root` en cada `onUpdate` del scroll; los cuatro carriles leen esa posición y el más cercano a
la luz sostiene un `--rule` un punto más caliente. Cero rAF nuevos, cero timers, cero nodos.

**Descartada la deriva perpetua de la chispa.** Es barata de ejecutar y cara semánticamente: si
la chispa se mueve siempre, el recorrido de la entrada deja de ser un acontecimiento y el
apuntado compite contra un fondo en movimiento. La chispa vale porque pasa una vez — el mismo
argumento por el que los créditos de Vice ruedan **y se detienen**.

### `prefers-reduced-motion`

La escena completa se lee sin haber interactuado. **Queda**: los 4 carriles enteros, los 4
rótulos, los 23 nombres en su color de reposo, las franjas con su contenido inicial, y el
apuntado funcionando **sin transición** (cambiar de estado no es animar). **Se apaga**: el
dibujo de carriles, el corte de rótulos, la chispa, el destello, los escalonados, el posado y
la lectura de `--bx/--by`.

Regla donde esto se rompe de verdad: **el estado de reposo debe ser el que pasa AA**, nunca un
estado transitorio. El `--haze` al 35% previo al destello no pasa AA sobre el fondo real; es
aceptable solo porque dura <400ms, no existe en `reduce` y ningún nodo reposa ahí.

## Restricciones de DOM — cómo no romper Vice

`credits.ts` monta el mismo DOM en los tres temas y Vice está cerrado. Esto ya se ha pagado
cuatro veces.

- **La lista NO se envuelve por grupo.** `scene4Credits` anima los hijos **directos** de
  `[data-credit-roll]`; un envoltorio por grupo reduciría el escalonado de Vice de 27 a 4. La
  columnización se hace **sin envoltorios**: `credits.ts` escribe en cada hijo dos propiedades
  personalizadas inline (`--skill-col`, `--skill-row`), inertes en Vice y Caelestia porque
  nadie las lee, y Hyprland usa `display: contents` en `.credits-list` para que esos hijos sean
  ítems directos de la rejilla del catastro. Robusto ante cambios de `content.ts`; una batería
  de `:nth-child()` fijada a 8/5/5/5 no lo sería.
- **Las cuatro franjas van fuera de `.credits-list`**, hermanas dentro de `.credits-grid`,
  igual que hoy va `.credits-marks` y por el mismo motivo. Meterlas dentro añadiría 4 huecos al
  escalonado de Vice **aunque estuvieran ocultas**.
- **Todo nodo nuevo nace con `display: none`** en la base compartida de `src/style.css`, y solo
  Hyprland lo enciende.
- **El friso pasa a cuatro filas**, una por parcela. Vice las neutraliza con `display: contents`
  para conservar su `flex-wrap` actual, y eso se verifica con diff de píxeles contra `HEAD`, no
  razonando.
- **`.credit-role` sigue en el DOM oculto por CSS**, no se elimina: es un gate del arnés.
- **La selección pasa a ser una por parcela**, no una global: cuatro franjas, cuatro
  seleccionados a la vez. Es un cambio en `select()`.

### Accesibilidad

- Cada franja es su propia región `aria-live="polite"` con id propio, y los botones de esa
  parcela apuntan ahí con `aria-controls`. Es **mejor que hoy**: el control queda junto a la
  región que modifica.
- El `.credits-panel` compartido sigue existiendo para Vice/Caelestia y en Hyprland va en
  `display: none`, que sí lo saca del árbol de accesibilidad. **Se comprueba en el árbol**:
  dos regiones vivas activas duplicarían el anuncio.
- Anillo de foco propio en `--l3` (el del sistema apenas separa sobre esta tinta). El orden de
  tabulación es el del DOM: `--skill-col`/`--skill-row` colocan, no reordenan.
- Las 23 marcas siguen `aria-hidden` + `data-decorative`. Nunca `aria-hidden` para eximir
  contraste: son dos usos distintos y el código ya lo documenta.
- Diana táctil de 44px en móvil. Con 42 el alto bajaba a 981px, pero recortar el objetivo
  táctil para ganar scroll es el intercambio que no se hace en un móvil.

## Presupuesto

| Recurso | Tope | Cómo |
|---|---|---|
| JS extra | **≤ 3 KB gzip** | No hace falta JS para encender las 23 marcas ni para la entrada (CSS + ScrollTrigger `once:true` ya existente) |
| Nodos DOM | ~181 actuales + 4 parcelas + 4 franjas | Sin marcado extra por icono: pseudo-elementos, no nodos |
| Listeners | los 69 actuales | Si el friso gana hover propio, **delegación** en el contenedor, nunca 46 listeners nuevos |
| Animaciones simultáneas | **12** dentro de la escena | Aserto que impide pasar las 23 lámparas a tweens de GSAP |
| Trabajo continuo | **cero** rAF/scroll nuevos | La entrada dispara una vez; el apuntado es CSS + `quickTo` |
| CSS | medir el delta gzip de `index-*.css` | Hoy 19,76 KB gzip, bloqueante de render para los tres temas |

**Propiedades prohibidas en esta escena**: `filter`, `backdrop-filter` y `box-shadow` con blur
**animados sobre los 23 nodos**, y `width`/`height` animados (usar `transform: scale()`). Hay
un shader WebGL a pantalla completa en rAF continuo detrás; el suelo no está en reposo.
`will-change` acotado al gesto y retirado al acabar: permanente en 23 nodos reserva 23 capas de
compositor toda la vida de la página.

## Verificación

| # | Qué | Criterio |
|---|---|---|
| 1 | `npm run build` + `npm run lint` | Verdes. Nota: el Node del sistema es v18 y `rolldown-vite` necesita ≥20 |
| 2 | Alto de la sección en móvil 390×844 | < 1100px, y **ninguna parcela con `scrollHeight > clientHeight`** |
| 3 | Los cuatro pies cierran a la misma cota en desktop | Idénticos (752px en el prototipo) |
| 4 | Acento en reposo | `getComputedStyle` de los 23 nombres: **ninguno** en `--l1`/`--l3`, en los dos viewports |
| 5 | Duración declarada de la entrada | `tl.duration()` ≤ 1,6s; a `progress(0.546)` los 4 rótulos con `clip-path: inset(0px)` |
| 6 | El gesto ocurre en pantalla | Al disparar el trigger, el último nombre de la parcela más alta cabe en el viewport |
| 7 | Concurrencia | `document.getAnimations().length` en la escena ≤ **12** |
| 8 | Cero reflow | `PerformanceObserver` de `layout-shift` durante la entrada y 20 apuntados: suma 0 |
| 9 | Rodillo bajo barrido rápido | 6 selecciones en 600ms → **1 solo** `.p-strip-in` |
| 10 | Contraste | `check_contrast_wcag` con recorte **ajustado al glifo**, shader **activo**, build de producción. El `--haze` a 15px es el más ajustado: ≥ 4,5:1 o se sube el scrim, nunca se toca el token |
| 11 | Montar / destruir / montar | Tras `destroy()`: cero ScrollTriggers del prefijo, cero clases de estado; al remontar la entrada vuelve entera |
| 12 | Árbol de accesibilidad | Exactamente 4 regiones live; el `.credits-panel` compartido no aparece |
| 13 | Vice y Caelestia idénticos | `verify.py` en los tres temas + `--reduced`, y diff de píxeles contra un **`git worktree`** del commit previo (nunca `git stash`) |
| 14 | Gates de crítica | `lidia-naive-tester` (pregunta abierta: "¿qué te cuenta esta sección?" — verde si responde en términos de áreas) y `vera-art-director` (las capturas de `about` y `credits` lado a lado: debe describir dos dispositivos distintos por iniciativa propia) |

### `scripts/verify.py` — el marcador 2 hay que actualizarlo

La aserción de Hyprland (`.credits-list` en `flex-direction: row` con `.credit-role` oculto)
queda obsoleta: la lista pasa a `display: contents` con los `.credit` como ítems de rejilla. El
spec de Ascua ya partió el marcador en dos por tema; se **actualiza la rama de Hyprland**, no
se relaja ni se borra.

## Direcciones descartadas, y por qué

- **La matriz de cruce** (23 tecnologías × 5 proyectos, un mojón por intersección). Dispersa:
  ~14 marcas en 115 celdas, el 88% del dispositivo vacío — el mismo modo de fallo por el que se
  cayó "temperatura = recencia" en la placa. Además convierte al proyecto en el eje
  protagonista, y esta escena es la de las áreas. Y una tabla de doble entrada lee como hoja de
  cálculo, que es la señal de "herramienta de dev" que Aoshi ya rechazó una vez.
- **Los cimientos** (las cuatro áreas como estratos horizontales por profundidad). Choca de
  frente con dos precedentes cerrados: los estratos verticales ya se descartaron en la placa
  por mentir, y una pila de bandas de borde a borde **es** el dispositivo de contacto. Además
  impone un orden de mérito que el dato no sostiene.
- **Cuatro bandas a sangre con las tecnologías fluyendo dentro.** Descartada por motion: el
  gesto natural de una banda a sangre es la inundación lateral, que es exactamente la firma del
  contacto.
- **Mantener el panel único de detalle**, movido a una columna fija a la derecha. Arregla el
  desperdicio de ancho pero en móvil siguen siendo dos zonas separadas, que es el defecto 4.
- **Medir la jerarquía con vara global** (solo `stack`). Deja un cuarto del catastro apagado y
  declara vacías a las cuatro herramientas que están en todos los proyectos.
- **Rejilla de dos columnas en móvil con diana de 42px.** Bajaba el alto a 981px a costa del
  objetivo táctil.

## Pendiente de decisión

Ninguna. El prototipo está aprobado y medido.
