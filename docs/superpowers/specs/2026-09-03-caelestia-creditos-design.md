# Spec de Caelestia — Créditos: el gestor de paquetes

Estado: pendiente de plan
Fecha: 2026-09-04
Plan: `docs/superpowers/plans/2026-09-03-caelestia-creditos.md`
Agenda de maquetado: `docs/superpowers/plans/2026-09-03-caelestia-creditos-maquetado.md`
Alcance: la **fase B4** de las seis del rediseño de Caelestia — la escena `#credits` dentro del
workspace. Toca un módulo nuevo de componente y el bloque `:root[data-theme="caelestia"]` de
`src/themes/themes.css`.

**`src/components/credits.ts` no se bifurca por tema.** Ese fichero construye el DOM que comparten
los tres temas y la presentación la decide el CSS colgando de `[data-theme]`; ese contrato se
respeta. Lo que B4 necesita del componente —el cruce contra las obras, el resumen de cuatro/cinco,
el estado «Sin obra publicada», el recuento derivado por grupo— **ya está escrito ahí** y se usa tal
cual. Ver `## Contenido: leído, no copiado`.

**Vice no se toca** (cerrado el 2026-08-05). **Hyprland no se toca**: su catastro del stack
(`2026-08-10-hyprland-stack-catastro-design.md`, rama `worktree-hyprland-stack-catastro`, sin
fusionar) es un dispositivo distinto y **su gesto queda vetado aquí explícitamente** — ver
`## Lo que NO es`. Las fases A, B1, B2 y B3 están cerradas y **tampoco se tocan**. El fondo es de B1
y B4 lo hereda sin tocarlo.

Rescatado al repo desde el acompañante visual (`.superpowers/` está en `.gitignore`):

| fichero | qué es |
|---|---|
| `2026-09-03-caelestia-creditos-maqueta.html` | la maqueta viva de la bandeja (M2–M7) |
| `2026-09-03-caelestia-creditos-extremos.html` | M4: la ficha contra sus cinco cardinalidades |
| `2026-09-03-caelestia-creditos-figuras.py` | el generador de las 23 figuras, con sus seis gates |
| `2026-09-03-caelestia-creditos-figuras.js` | su salida (`FIG23`, `FIG23S`, `FIG23N`, `FIG23R`, `FIGCIRC`) |
| `2026-09-03-caelestia-creditos-cabecera.png` | la cabecera, ya con el territorio en monoespaciada |

Las dos maquetas necesitan `figuras23.js`, `icons.js` y `gsap.min.js` servidos a su lado (rutas
`/files/…`). El primero se regenera con `python3 …-figuras.py`; los otros dos son los del proyecto.

---

## Por qué

Medido sobre el build de producción servido (`npm run build && npx vite preview`,
`?theme=caelestia`), en la ventana de **1412 × 748** que impone el carril de workspaces:

| | antes | después |
|---|---|---|
| scroll interno de la escena a 1440×900 | **758 / 748** — 10 px | 748 / 748 — ninguno |
| rótulos de grupo **pintados** | **0 de 4** (los cuatro existen en el DOM) | 4 de 4 |
| ancho muerto al canto derecho | **424 px · 30 %** | 48 px · 3,4 % |
| tecnologías en pantalla sin desplazar | 23 de 23 | 23 de 23 |
| scroll interno a 390×844 | **846 / 692** — 154 px, 3 filas fuera de la ventana | sin cambio (fuera de alcance, ver M8) |

Tres defectos. Dos son de la ley de la fase A —*un espacio de trabajo no se desplaza, se cambia*—
y el tercero es el que más engaña: **los cuatro rótulos de territorio existían en el DOM y no
pintaba ninguno.** Contar nodos no es contar lo que se ve, y esa confusión es el modo de fallo
central de esta fase: aparece otras cuatro veces más abajo.

---

## La decisión de partida: cada escena es una aplicación

Es la tesis heredada de la fase A y la que ordena las cinco: el tema no es un juego de tokens, es
**un escritorio**, y cada escena es el programa que un escritorio abriría para contestar esa
pregunta. B1 es el escritorio presentándose (`whoami`). B2 es `neofetch`: qué máquina eres. B3 es
el gestor de archivos. **B4 es el gestor de paquetes**: qué hay instalado en esta máquina.

De ahí sale todo lo demás sin inventar nada. Un gestor de paquetes no lista adjetivos: enseña
**paquetes**, agrupados por origen, y al señalar uno cuenta qué es y dónde se usa. La escena tiene
exactamente ese dato y ninguna otra escena lo tiene.

## La composición: la bandeja

Cuatro bandas de la misma altura, una por territorio, con el rótulo al canto izquierdo sobre una
calle de 158 px. Dentro de cada banda, una hilera de módulos fijos de 142 px con las piezas
centradas. Las 23 están siempre en pantalla; ninguna se descubre desplazando.

- **El tamaño no codifica nada.** Todas las piezas miden lo mismo (88 px de lado; un único valor
  en todo el DOM). Se probaron las dos varas posibles y **las dos mienten**: con vara global,
  Herramientas se infla porque `tooling` está en los cinco proyectos; con vara por territorio,
  JavaScript y C —una obra— salen tan grandes como Git —cinco—. Una escala que en cualquiera de
  sus dos formas dice lo contrario del dato no es jerarquía, es ruido.
- **El filete de cada banda llega sólo hasta su última pieza**, así que su largo *es* la masa del
  territorio: ocho módulos en Interfaz, cinco en las otras tres. Dice el recuento sin escribir el
  número.
- **El módulo es fijo, no proporcional.** Se descartó dar `span 2` a las piezas con más obras:
  en Lenguajes el tope es 1 obra, así que las tres primeras se llevarían celdas de 284 px —más
  anchas que las de React, que tiene 2— y el ancho diría «esto importa» donde el dato dice lo
  contrario.
- Las columnas arrancan en **x = 301 en las cuatro bandas**, y los cuatro rótulos caen a **0 px**
  del centro vertical de su banda.

## Las 23 figuras

Cada tecnología tiene su propia figura de Material 3, ninguna repetida, agrupadas por familia
(cóncavas de 5–12 lóbulos en Interfaz, convexas de 3–7 en Backend, convexas de 8–12 en Lenguajes,
cóncavas de 13–18 en Herramientas). Morfar es la identidad declarada del tema, no un adorno.

Se generan con `…-figuras.py`, **240 vértices todas**: un `polygon()` sólo interpola con otro del
mismo número de puntos, y con distinto el navegador corta de golpe sin error ni aviso (la trampa de
B2). El generador lleva seis gates: 23 figuras, 23 únicas, 240 vértices, dispersión de área
< 0,5 %, relieve mínimo ≥ 6 %, anisotropía < 1,25.

Tres fallos encadenados costó igualar los tamaños, y ninguno era de diseño:

1. Normalizar por `max|x|` usa el **radio**, no la semianchura, y las figuras de lóbulos impares
   no están centradas: JavaScript medía 90,4 px y Git 102 — un 13,7 % de diferencia entre dos
   piezas que debían ser idénticas. Se arregla normalizando **el vano** de cada eje y recentrando.
2. Las familias de canto recto tienen suelos de área distintos (hexágono 3,00; cuadrado 3,147),
   así que **no existe un área común alcanzable** y el solucionador las aplanaba a círculos
   (relieve 0,3 %). Se arregla usando **una sola familia armónica** para las 23.
3. En figuras cóncavas de 3–4 lóbulos la cintura queda por dentro del canto y el icono se salía
   por los brazos. Se arregla acotando el icono por el **radio inscrito**, no por la caja.

Resultado: **0,0 % de dispersión** en área, ancho y alto dentro de cada familia.

## La selección: rozar elige (M5)

No hace falta pulsar. `mouseenter`, `focus` y `click` hacen lo mismo, para que el teclado llegue
adonde llega el ratón. Al elegir, **la cabecera se releva en el sitio** —96 px fijos, nada más se
mueve— con barridos de `clip-path`, la figura tocada se ablanda a su variante suave, crece un 7 %
y pasa a `--cae-primary`, y las demás **bajan su tinta, nunca su fondo**.

Ese matiz importa: `--cae-elev-1` es **exactamente** `--cae-surface-container`, así que apagar el
relleno de las figuras las borra contra el fondo de la ventana. Se apaga la tinta.

Holgura al rozar contra los filetes de banda: **22,5 px en reposo, 19,2 px rozando**. Por eso el
lado es 88 y no 96 — con 96, el 7 % de crecida llevaba el canto superior a tocar el filete anterior.

## La ficha y el cruce (M4)

La cabecera lleva la marca recortada a la figura, el nombre en Fraunces
(`--cae-display-axes-cartel`), el `detail` en Fraunces itálica, el territorio en monoespaciada y,
**en la misma línea inicial al canto derecho**, el cruce «Aparece en». Comparte renglón con el
nombre porque es lo que contesta.

Se probó debajo de la primera banda y **se montaba encima de GSAP, Electron y GTK4**: esa banda
ocupa los ocho módulos, ahí abajo no hay línea inicial libre.

`content.ts` tiene **cinco cardinalidades y no más** — 5 (Git), 4 (Claude Code), 3 (TypeScript),
2 (React) y 0 (siete piezas). **No hay ninguna tecnología con exactamente una obra.** Las cinco
están en `…-extremos.html`, con un botón que devuelve el estado anterior para ver los defectos dar
rojo. Los dos que salieron:

| | antes | después |
|---|---|---|
| alto del cruce con 3 obras | **111 px** en una cabecera de 96 — se salía 15 | 51 px, un renglón de 400 en un hueco de 420 |
| «Sin obra publicada» | **1,80:1 de noche · 2,34:1 a las 09:00** | 8,05:1 · 5,93:1 |

El primero se arregla pasando el cruce de **pila a hilera** con punto medio: los tres títulos siguen
escritos, ninguno se resume. El segundo, **subiendo la tinta**: apagarla para decir «esto pesa
menos» es la misma opacidad recalibrada que ya falló en B1, y no es un caso raro —son **7 de las 23
piezas, el 30 %**.

Con cuatro o cinco obras no se listan los títulos («Los cinco proyectos»). **No es una decisión de
B4**: es la regla que `credits.ts::textoCruce` ya tiene escrita, y la ficha nueva la usa sin
bifurcar por tema.

Ensanchar el cruce hasta 420 px no aplasta la columna del medio: medido en las 23, el mínimo es
**808 px** y el detalle más largo mide 389. Solape: **0 px**.

## La entrada de escena: la instalación (M6)

Sin terminal tecleada — sería la tercera después de B1 y B2, y está vetada. Las 23 entran como
**círculos idénticos** —paquetes sin abrir— y cada una morfa a su figura mientras crece desde 0,66
y se endereza 6°. La onda va **por territorios**: cada familia arranca 190 ms detrás de la anterior,
y el nombre de cada pieza entra cuando su figura ya paró. Cierra en ~1,6 s.

Las clases hacen el trabajo y GSAP sólo decide cuándo. **Cada nodo suelta su animación en
`animationend`** (`animation: none`): con `fill: both`, `transform` y `clip-path` se quedan
congelados en el último fotograma y **le ganan al `:hover`** — el morfado al rozar no ocurría, sin
error ninguno.

## Las 24 horas (M7)

La escena se mide en las 24 posiciones del reloj, **55 pares de tinta y fondo por hora** —nombre,
detalle, territorio, epígrafe, cruce, los cuatro rótulos de banda, los 23 iconos contra su propia
figura y los 23 nombres— y en los **dos** estados de la ficha, con obra y sin ella.

- Peor par de las 24 horas: **5,73:1** («nombre Git», a las 08:00).
- Iconos: **6,78:1** de noche, **6,04:1** a las 09:00.
- **Ninguno de los 1.320 pares baja de AA.**

Los iconos van todos en una sola tinta. Los 23 logotipos de marca traen colores ajenos a la rueda
OkLCH del tema, y con ellos el peor caso caía a **2,53:1** a las 09:00.

## Movil (M8) — fuera de alcance, con la deuda escrita

**B4 no maqueta a 390**, igual que B1 y B2, y se dice aquí explícitamente para que no quede
implícito.

La bandeja pide **1316 px de ancho útil** (calle de 158 + ocho módulos de 142); a 390 hay 362.
No es un ajuste de márgenes: es otra composición.

Y el estado de hoy a 390 **ya está roto**, antes de B4 y sin que B4 lo empeore: la escena tiene
**154 px de scroll interno** (846 / 692) y **tres filas fuera de la ventana**. Es decir, la ley de
la fase A tampoco se cumple en móvil.

**Recomendación para el plan: no lo arregle B4.** B1, B2, B3 y B4 comparten exactamente el mismo
problema —maquetación pensada para una página que se desplaza, metida en una ventana fija— y
arreglarlo cuatro veces por separado produce cuatro soluciones distintas para un solo problema.
Merece una fase transversal de móvil, después de B5.

## Contenido: leído, no copiado

Las 23 tecnologías, sus `detail`, los cuatro rótulos de grupo y los cinco títulos de obra salen de
`src/data/content.ts`. **Ningún dato derivado inventado**: el cruce se calcula contra `stack` **y**
`tooling` —el mismo cruce que hace `toEntry`—, el recuento por grupo es `items.length`, y el
resumen de cuatro/cinco es `textoCruce`. Todo eso ya existe en `credits.ts`.

## Lo que NO es

1. **No es el catastro de Hyprland.** Allí el stack es un reparto proporcional de territorio con
   una chispa recorriendo raíles. Aquí no hay reparto proporcional —el tamaño no codifica— ni
   recorrido: las 23 están quietas y el ratón elige.
2. **No es una tercera terminal tecleada.** B1 teclea `whoami`, B2 es `neofetch`. La entrada de B4
   es una instalación de paquetes, que no escribe nada.
3. **No tiene scroll interno**, ni 10 px.
4. **No apaga tinta para jerarquizar.** Ni en el estado vacío, ni en las piezas sin obra, ni en el
   territorio.

## Los gates

Ocho familias, todas vistas **dar rojo contra el fallo exacto que dicen cazar** antes de aceptarse:

| # | qué vigila | se vio roja con |
|---|---|---|
| 1 | la escena no tiene scroll interno (`scrollHeight === clientHeight`) | el estado de partida: 758 / 748 |
| 2 | las 23 piezas están dentro de la caja de la escena | — |
| 3 | los 4 rótulos de territorio **se pintan** (`getClientRects().length > 0`) | el estado de partida: 4 en el DOM, 0 pintados |
| 4 | 23 figuras distintas, 240 vértices, misma área/ancho/alto | las tres iteraciones del generador |
| 5 | contraste de los 55 pares en las 24 horas y en los dos estados de la ficha | el territorio en `--cae-outline`: rojo en las 24 |
| 6 | el cruce cabe en los 96 px de cabecera en las 23 piezas | TypeScript: 111 px, se salía 15 |
| 7 | la ficha se releva al rozar sin pulsar, y el teclado llega a lo mismo | — |
| 8 | movimiento reducido salta la entrada al estado aterrizado | — |

El arnés será `scripts/measure-caelestia-creditos.py`, y su fila va a la tabla de
`.claude/rules/verification.md`.

## Trampas de medición pagadas en esta sesión — que no se repitan

1. **El contenedor de la escena es transparente.** Leer su `backgroundColor` devuelve
   `rgba(0,0,0,0)` y el contraste sale **contra negro**: 11,11:1 donde lo real era 8,05. Hay que
   subir por el árbol hasta el primer ancestro opaco.
2. **Una sonda que sólo mira el estado seleccionado no mide los demás.** La de contraste hacía
   hover en Git y daba verde con «Sin obra publicada» roto a 1,80:1, porque ese nodo no existía
   mientras medía. Lo demostró el sabotaje, no el razonamiento. Ahora recorre los dos estados.
3. **Una maqueta escalada no contesta a móvil.** `transform: scale` sobre un escritorio de 1412 no
   cambia el viewport: a 390 daba «23 de 23 piezas dentro de la caja, sin desborde» con piezas de
   18 px y dianas de 22. Hay que medir con el viewport de verdad, o contra el sitio real.
4. **Un CSS puede declarar una familia y no usarla nunca.** `.hd-banner p` (0,1,1) le ganaba a
   `.hd-figname` (0,1,0): el territorio pedía monoespaciada y se pintaba en Fraunces itálica,
   obedeciendo sólo el tracking y las versalitas. Ni `tsc` ni `eslint` ven esto; sólo se ve leyendo
   el **estilo computado**. Y no basta con repetir la familia: hay que apagar también `font-style`
   y los ejes heredados.
5. **CSS muerto: no se cuenta en el fichero, se le pregunta al DOM vivo.** Cinco reglas
   (`.m5-sub`, `.b-fila-rot p`, `.hd-cruce b`, `.hd-cruce em`, `.b-key*`) tenían **cero nodos
   pintados**. Es la misma confusión que el defecto de partida, un nivel más abajo.
6. **Una regla que se escribe y cuyo elemento no se añade al DOM parece el arreglo.** `.b-fig-in`
   se dio por bueno un rato; lo que de verdad hizo visibles las figuras pequeñas fue subir el
   relleno a `--cae-outline`.
7. **Cargar `/files/*.html` en crudo no manda charset** y el navegador cae a latin-1: las capturas
   salían con mojibake que no existe en el visor. Un `<meta charset>` en el fragmento lo zanja.
8. **Las capturas perturban GSAP** bajo headless + swiftshader (ya anotado en B3): en las capturas
   del roce el titular sale cortado a media palabra, y medido a 1,8 s los tres `clip-path` cierran
   en `inset(0px 0% 0px 0px)` con el texto entero dentro. No es un defecto que perseguir.

## Preguntas abiertas para el plan

1. **El hueco al pie derecho: 28,1 %.** Las tres bandas de cinco dejan tres módulos libres cada
   una. Con el cruce ya en la línea inicial, no queda un candidato natural que meter ahí.
   **Recomendación: aceptarlo** como el canto irregular de un 8/5/5/5 y dejarlo escrito como
   decisión, no como deuda. Repartir las bandas de otra forma cuesta la alineación de columnas.
2. **Móvil**, según `## Movil (M8)`: fuera de alcance en B4, fase transversal después de B5.
3. Los gates 2, 7 y 8 aún no se han visto dar rojo. Antes de aceptarlos, sabotearlos.
