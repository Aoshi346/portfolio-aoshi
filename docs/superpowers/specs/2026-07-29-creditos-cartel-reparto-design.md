# "Con que construyo" como cartel de reparto — diseno

Fecha: 2026-07-29
Estado: **IMPLEMENTADO y mergeado a `main`** (merge `5211743`, 29-jul-2026)
Alcance: escena `[data-scene="credits"]` en el tema Vice
Traspaso de origen: `.docs/HANDOFF-creditos-cartel.md`
Plan de ejecucion: `docs/superpowers/plans/2026-07-29-creditos-cartel-reparto.md`
(las ocho tareas cerradas; alli estan las divergencias respecto a lo planificado)

> Este documento recoge el diseno tal como quedo, con dos enmiendas posteriores
> al gate visual marcadas en su sitio: el reparto pasa de seis bloques a cuatro
> (seccion 3.1) y el punto separador se mueve detras del nombre anterior
> (seccion 4.3). Lo demas se implemento como estaba escrito.

---

## 1. Objetivo

Sustituir la presentacion actual de la seccion (lista agrupada a la izquierda +
panel de detalle a la derecha) por el bloque de creditos del pie de un cartel de
cine: tipografia condensada, versalitas, todo centrado, sin recuadros ni panel
lateral. La seccion deja de ser una interfaz y pasa a ser una pieza tipografica.

Lo que hay implementado hoy funciona y no esta roto: es el punto de partida a
sustituir. **Su comportamiento de datos se conserva integro**, en particular que
una tecnologia sin proyecto publicado oculta el bloque "Aparece en" entero en vez
de rellenarlo con una frase generica.

Solo cambia Vice. Hyprland y Caelestia siguen presentando el mismo DOM como
pildoras, sin tocar.

---

## 2. Decisiones cerradas

Las cuatro decisiones que el traspaso dejaba abiertas, resueltas contra mockups
en el companion visual:

| # | Decision | Resultado |
|---|---|---|
| 1 | Donde vive la frase de cada tecnologia | **Pie de cartel a dos alturas** |
| 2 | Que pasa en movil | **Disposicion D**: misma composicion, interlineado 2.7 |
| 3 | Como se marca lo interactivo | **Friso de marcas al pie**, la activa se enciende |
| 4 | La tipografia condensada | **Pathway Gothic One** como token `--font-billing` |

Ademas se cerraron dos decisiones de contenido que surgieron por el camino:

| # | Decision | Resultado |
|---|---|---|
| 5 | Ampliar el stack | **23 tecnologias** (12 actuales + 11 nuevas) |
| 6 | Donde se declara lo transversal | **Campo nuevo `tooling`**, no visible en la ficha de obra |

### 2.1 Pie de cartel a dos alturas

Bajo el bloque de reparto, una zona de **altura reservada fija** con dos
renglones de jerarquia distinta:

1. La frase de la tecnologia, en `--font-body` (Manrope) ligera.
2. `Aparece en` + los proyectos, en `--font-billing`, en ambar, en versalitas.

Al cambiar de tecnologia no se mueve nada. Cuando `usedIn` esta vacio el segundo
renglon pasa a `visibility: hidden` — **no** `display: none` — para que la altura
no colapse y el cartel no de un salto.

Se descartaron: subir "Aparece en" al cartel como bloque de reparto (obligaba a
mostrar "sin proyecto publicado" de forma visible, que es justo el defecto por el
que se descarto la matriz) y una cartela fija bajo el cartel (reintroducia la
logica de lista + ficha que esta direccion venia a eliminar).

### 2.2 Friso de marcas al pie

Los nombres del cartel van **limpios, sin iconos**: meter una marca delante de
cada nombre convierte la linea de reparto en una lista con vinetas, que es
exactamente lo que esta direccion elimina.

Las 23 marcas van juntas en un friso al pie del cartel, monocromas y apagadas
(`opacity: .26`), separadas por un filete — donde un cartel de cine pone los
logos de estudio y distribuidora. **La marca de la tecnologia activa se enciende
en ambar.** Eso le da funcion ademas de decoracion: es una segunda senal de
seleccion que no depende del hover, lo que cubre parte de la afordancia tactil.

### 2.3 Movil: disposicion D

La composicion del cartel se mantiene en 390px — nombres seguidos, renglones que
se parten. El unico cambio es el **interlineado a 2.7**, que es el minimo exacto
con el que el area pulsable de cada nombre alcanza 44px sin que las filas se
pisen.

Medidas reales tomadas del DOM en el companion, no estimadas:

| Alternativa | Alto en 390px | Pantallas de 844px | Objetivo tactil |
|---|---|---|---|
| **D · elegida** | 867px | 1.0 | **44px** |
| A · cartel integro, cuerpo menor | 751px | 0.9 | 28px |
| B · un nombre por linea | 1623px | 1.9 | 45px |
| C · vuelta a la lista actual | 1619px | 1.9 | 46px |

Apilar los nombres duplica la altura de la seccion, en una pagina que ya tiene
dos zonas fijadas (hero y obra). D cuesta 116px sobre A y cabe en una pantalla.

**Correccion al traspaso:** el handoff cita "44px (WCAG 2.5.5)" como si fuera el
minimo exigible. SC 2.5.5 Target Size es **nivel AAA**; el requisito **AA** es SC
2.5.8 Target Size (Minimum) de WCAG 2.2, que pide **24x24 px**. La alternativa A
con sus 28px ya cumplia AA. Se elige D porque el proyecto se marca el liston AAA,
no porque A fuera un incumplimiento.

### 2.4 Tipografia: Pathway Gothic One

El mockup usaba Oswald mas `transform: scaleX(.88)`. Ese `scaleX` **no condensa,
aplasta**: adelgaza los trazos verticales y deja intactos los horizontales.

Pathway Gothic One ya viene dibujada estrecha, asi que **el `scaleX` desaparece
del diseno**. Es una gotica de rotulo, el genero de letra de los carteles de cine
de los ochenta, y esta mucho menos vista que Oswald.

Contrapartida aceptada: **un solo peso (400)**. No hay 500 para engordar el
nombre activo, asi que el realce lo lleva entero el color ambar.

Se midio si una condensada mas estrecha ahorraba altura en movil: **12px entre la
mas estrecha y la mas ancha de las cuatro candidatas**. Irrelevante. La eleccion
es por el dibujo de la letra, no por metrica.

---

## 3. Contenido final

### 3.1 Los 23 nombres, por bloque

**Enmienda del 29-jul-2026, despues del gate visual.** El corte original eran
seis bloques de 6/5/5/2/3/2. Tres bloques de dos y tres nombres se leian como
sobras en un cartel, y seis rotulos ambar hacian que la mitad de la pieza fueran
etiquetas. Se cerro sobre mockup vivo (`.superpowers/brainstorm/37462-1785364143`,
`bloques-cartel-v2.html`) con tres variantes y las mismas 23 tecnologias.

| Bloque | Tecnologias |
|---|---|
| Interfaz | React · Next.js · TypeScript · Tailwind CSS · Vite · GSAP · Electron · GTK4 |
| Backend y datos | Python · Django · Node.js · MySQL · RxDB |
| Lenguajes base | JavaScript · HTML · CSS · C · C++ |
| Herramientas | Git · GitHub · n8n · Claude Code · Gemini CLI |

**Por que 8/5/5/5 y no 6/5/5/7.** La consolidacion obvia era fundir los tres
bloques pequenos en uno de siete, pero el rotulo resultante mentiria: Electron y
GTK4 no son herramientas con las que se trabaja, son aquello con lo que se
construye la interfaz, al mismo nivel que React. "Interfaz" cubre web y
escritorio sin forzar nada, y deja un "Herramientas" honesto donde las cinco
entradas si son cosas con las que se trabaja. De paso dice algo que el corte
anterior no decia: que hay interfaz en web *y* en escritorio nativo.

**Coste asumido:** "IA" pierde rotulo propio. Separado se leia como postura
deliberada; se acepta perderlo porque queda junto a lo que de verdad se le
parece y porque no compensaba un bloque de dos nombres.

**Objecion descartada con medida:** se apunto que ocho nombres partirian en dos
lineas en escritorio. Es falso — el contenedor real da 766px y la fila de ocho
ocupa 620px, y a 1024 y 900px de ventana baja a 539 y 478 por el clamp del
cuerpo. Medido con `prefers-reduced-motion`, en escritorio el reparto son
exactamente cuatro lineas de 8/5/5/5.

`n8n` se escribe en minuscula: lleva excepcion a la versalita del cartel, porque
asi se escribe la marca.

Once nombres son nuevos: siete que pidio el usuario (Next.js, Node.js, Git,
GitHub, n8n, Claude Code, Gemini CLI) y cuatro propuestos tras revisar los
`stack` reales de `caseStudies`, que ya se usaron en proyectos publicados y no
estaban en la seccion (GSAP, RxDB, Electron, GTK4).

**Zustand queda fuera.** Aparece en el stack de HyprFinance, pero no existe en
`simple-icons` y `getIconMarkup()` lanza excepcion con un slug desconocido. El
friso exige una marca por nombre. Entra solo si se dibuja un SVG a mano.

### 3.2 Frases

Todas cortas y de longitud parecida: la zona del pie tiene altura reservada, y
frases de longitud dispar obligarian a reservar hueco para la mas larga y
dejarlo medio vacio casi siempre.

Las doce existentes se acortan; las once nuevas se escriben ya cortas.

| Tecnologia | Frase |
|---|---|
| React | Interfaces con estado complejo. |
| Next.js | Para apps con rutas y render en servidor. |
| TypeScript | Tipado en todo lo que escribo. |
| Tailwind CSS | Maquetacion rapida y consistente. |
| Vite | Mi bundler por defecto. |
| GSAP | Las animaciones y las transiciones. |
| Python | Automatizacion, datos y APIs. |
| Django | Backend robusto: ORM, admin y auth. |
| Node.js | JavaScript fuera del navegador. |
| MySQL | Donde persisto los datos. |
| RxDB | Datos locales en el navegador. |
| JavaScript | Base de todo lo que corre en el navegador. |
| HTML | Estructura semantica antes que nada. |
| CSS | Lo que no cubre Tailwind, lo escribo a mano. |
| C | Donde aprendi a pensar en memoria y punteros. |
| C++ | Sistemas y aplicaciones nativas. |
| Electron | Aplicaciones de escritorio con tecnologia web. |
| GTK4 | Interfaces nativas en C. |
| Git | Control de versiones en todo lo que hago. |
| GitHub | Donde publico y comparto el codigo. |
| n8n | Automatizo tareas repetitivas entre servicios. |
| Claude Code | Asistente en terminal para escribir y revisar codigo. |
| Gemini CLI | Consultas rapidas desde la terminal. |

Coste aceptado: la frase de React era la unica que nombraba Telefonica, el dato
mas concreto de la seccion. No se pierde — "Aparece en" lleva a EchoPlan y la
ficha de EchoPlan dice "Sistema interno · Telefonica Venezuela" — pero queda a un
paso de distancia.

### 3.3 Cruce tecnologia -> proyectos

Corregido por el usuario respecto de lo que decia el traspaso.

| Tecnologia | Aparece en |
|---|---|
| Git, GitHub | EchoPlan, TesisFar, HyprFinance, WatchDog, Editor de texto |
| Claude Code, Gemini CLI | EchoPlan, TesisFar, HyprFinance, WatchDog |
| TypeScript | EchoPlan, TesisFar, HyprFinance |
| React | EchoPlan, HyprFinance |
| Python | EchoPlan, WatchDog |
| Next.js | TesisFar |
| Django, Vite | EchoPlan |
| GSAP, RxDB | HyprFinance |
| JavaScript, Electron | WatchDog |
| C, GTK4 | Editor de texto |
| Tailwind CSS, Node.js, MySQL, HTML, CSS, C++, n8n | — |

Siete de 23 sin proyecto publicado. Eran 11 antes de la correccion del usuario.
Que ese hueco no duela es el merito de la decision 1: en el pie a dos alturas el
hueco es invisible.

### 3.4 Campo `tooling`

Git, GitHub, Claude Code y Gemini CLI **no entran en `caseStudies[].stack`**.
`stack` se pinta literal en la ficha de cada proyecto (`projectScene.ts:52`), y
meterlos ahi alargaria la linea "Stack" con cuatro nombres repetidos identicos en
los cinco proyectos, mezclando con que esta hecho el producto con como se
construyo.

Se anade un campo nuevo `tooling?: string[]` a `CaseStudy`. `credits.ts` cruza
contra `[...stack, ...(tooling ?? [])]`. **La ficha de obra sigue mostrando solo
`stack`** — `tooling` existe como dato y alimenta los creditos, nada mas.

Asimetria aceptada y conocida: el cartel dira que Git aparece en EchoPlan
mientras la ficha de EchoPlan no menciona Git. No es contradiccion (la ficha
lista de que esta hecho el producto; el cartel dice donde se uso), pero conviene
tenerla presente.

Nota editorial que quedo dicha una vez: declarar Claude Code y Gemini CLI en
cuatro proyectos es una afirmacion sobre como se trabaja, y no todo lector la
leera igual. Es decision tomada del usuario, no efecto colateral.

---

## 4. Cambios por archivo

### 4.1 `src/data/content.ts`

- Acortar las doce frases existentes segun 3.2.
- Anadir once entradas nuevas con `name`, `slug`, `detail`.
- Reorganizar en seis grupos segun 3.1. **`skillGroups` pasa a ser la unica
  fuente y contiene los seis bloques**; `secondarySkills` se elimina y su
  contenido se absorbe en el grupo "Lenguajes base". Se puede hacer sin residuo:
  `secondarySkills` solo lo consume `credits.ts` (comprobado con grep sobre
  `src/`), asi que no hay otro llamante que arreglar.
- Anadir `tooling?: string[]` a la interfaz `CaseStudy` y rellenarlo en los cinco
  proyectos segun 3.3.

### 4.2 `src/utils/icons.ts`

Registrar los once slugs nuevos como imports estaticos: `nextdotjs`,
`nodedotjs`, `git`, `github`, `n8n`, `claude`, `googlegemini`, `gsap`, `rxdb`,
`electron`, `gtk`. Los once existen en la version de `simple-icons` instalada
(comprobado). Sin esto `getIconMarkup()` **lanza excepcion en los tres temas**,
no solo en Vice.

### 4.3 `src/components/credits.ts`

Cambios **aditivos**, nunca reorganizacion (restriccion dura 3):

- El cruce pasa a `[...project.stack, ...(project.tooling ?? [])]`.
- Desaparece el import de `secondarySkills` y el `{ label: "Otras herramientas",
  items: secondarySkills }` cosido a mano: `groups` pasa a ser `skillGroups` a
  secas, que ya trae los seis bloques.
- Se anade un nodo nuevo, el friso: `.credits-marks`, con un `<svg>` por
  tecnologia, `aria-hidden="true"` y `data-decorative`. Va como **tercer hijo de
  `.credits-grid`**, hermano de la lista y del panel, para que Hyprland y
  Caelestia lo oculten con una sola regla sin tocar su `flex-wrap`.
- `select()` enciende la marca correspondiente (`.is-active` sobre el `<svg>`) y
  apaga las demas.
- Todo lo demas se queda: `.credit-role` sigue en el DOM, el panel sigue siendo
  `role="status"` / `aria-live="polite"`, los encabezados de grupo siguen siendo
  hermanos planos dentro de `[data-credit-roll]`.

**Los separadores del cartel no se anaden al DOM.** El punto medio entre nombres
sale de CSS con `.credit:has(+ .credit)::after { content: "·" }`: aparece cuando
detras viene otro credito, asi que el ultimo de cada bloque no lo lleva y tras un
encabezado de grupo no aparece de mas. Cero nodos nuevos, restriccion dura 4
intacta.

**Enmienda del 29-jul-2026: el punto va DETRAS, no delante.** La primera version
era `.credit + .credit::before`, con el punto dentro de la caja del nombre
siguiente, y de ahi salian dos defectos medidos: el subrayado del activo cubria
el punto anterior (19px de hueco entre el borde del boton y la primera letra, se
subrayaba "· NEXT.JS"), y al partir linea en movil la linea abria con el punto,
que se lee como vineta — justo lo que esta direccion elimina.

Detras se arreglan los dos. El artefacto del corte de linea no desaparece, cambia
de lado: la linea que parte cierra con un punto colgando, que en creditos de
cartel es la convencion. No hay version sin artefacto porque el CSS no puede
saber donde va a partir el texto. En escritorio no se ve nunca: son cuatro lineas
de 8/5/5/5 sin ningun corte.

Tres reglas de `style.css` hay que desactivar a mano al reutilizar ese
pseudoelemento, porque la base lo usa para su "+" de afordancia: `opacity` (la
deja a 0 fuera del hover y en la fila activa — sin `opacity: 1` el punto se
maqueta y no se pinta, medido), `font-weight: 700` (Pathway tiene un solo peso,
daria falso negrita) y `margin-left` (se sumaria al padding). `display:
inline-block` en el pseudoelemento corta la propagacion de `text-decoration`,
que si no volveria a alcanzar al punto por el otro lado.

### 4.4 `src/style.css`

Solo lo compartido. El friso se declara aqui como oculto por defecto y lo
enciende Vice, para que Hyprland y Caelestia no tengan que saber que existe.

### 4.5 `src/themes/themes.css` — bloque Vice

- `.credits-grid` pasa a una sola columna centrada: cartel, pie, friso.
- `.credit-group-label` se vuelve el encabezado de bloque del cartel: versalitas,
  `--font-billing`, ambar legible, `display: block` (fuerza el salto de renglon).
- `.credit` pasa a `display: inline` para que los nombres fluyan como un parrafo
  compuesto. Sin `scaleX`.
- El panel se re-skinea como pie a dos alturas: se ocultan `.credits-icon`,
  `.credits-panel-name` y `.credits-panel-role`; se ven `.credits-panel-detail`
  (Manrope ligera) y `.credits-used` (`--font-billing`, ambar).
- `.credits-used[hidden]` en Vice usa `visibility: hidden` con altura reservada,
  no `display: none`.
- `.credit-role` sigue con `display: none` bajo `[data-theme="vice"]`
  (restriccion dura 2).
- Movil: `line-height: 2.7` en el contenedor de nombres y padding horizontal
  minimo en `.credit`. Por encima de 860px, interlineado normal.
- El hover **no puede usar `transform`** sobre `.credit`: recibe la entrada de
  GSAP y el transform inline gana siempre (restriccion dura 6). El realce va por
  color, que ademas es lo unico disponible al tener Pathway un solo peso.

### 4.6 `index.html` y `src/themes/vice.ts`

Alta de la fuente en **los dos sitios**, o degrada a la via lenta en silencio
(restriccion dura 1):

- `fontHrefs.vice` en el script inline de `index.html`.
- `fontHref` en `viceTheme`.

Nueva URL, con Pathway Gothic One anadida a lo que ya se pedia:

```
https://fonts.googleapis.com/css2?family=Passion+One:wght@900&family=Manrope:wght@200;300;400;600;700&family=Pathway+Gothic+One&display=swap
```

Token nuevo `--font-billing: "Pathway Gothic One", sans-serif`, usado **solo en
el cartel**. `--font-display` sigue con Passion One y `--font-body` con Manrope,
sin tocar: `scripts/verify.py` lo comprueba y ninguno puede resolver a
monoespaciada.

### 4.7 `src/themes/vice.choreography.ts`

`scene4Credits` anima los hijos DIRECTOS de `[data-credit-roll]`, que siguen
siendo los encabezados y los creditos en plano. El escalonado se conserva.

- El friso es hermano de la lista, no hijo, asi que no entra en ese escalonado:
  necesita su propia entrada.
- **`gsap.from` esta prohibido** (restriccion dura 5): `fromTo` con los dos
  extremos escritos a mano.
- Materializar colecciones con `Array.from(...)`: pasar una `HTMLCollection` viva
  fue el detonante de dos de las tres regresiones documentadas.

---

## 5. Accesibilidad — invariantes

- Cada tecnologia sigue siendo un `<button>` real, enfocable con Tab, con
  `aria-pressed` y `aria-controls` apuntando al contenedor de detalle.
- El contenedor de detalle sigue siendo `role="status"` con `aria-live="polite"`.
- Objetivo tactil 44px en movil via interlineado 2.7 (ver 2.3). En escritorio el
  hover manda y el objetivo no aplica igual.
- Las marcas del friso son decorativas puras: `aria-hidden` + `data-decorative`.
  Nunca `aria-hidden` para eximir del gate de contraste.
- `wireFocusScroll` (`src/utils/reveal.ts`) no se toca: solo actua con
  `:focus-visible` y solo si el elemento no se ve entero (restriccion dura 7).
- Todo gesto respeta `prefers-reduced-motion`. Ojo: `initScrollReveal` hace
  early-return con reduced-motion, asi que cualquier motion que baje a CSS
  necesita su propia media query.

---

## 6. Criterios de aceptacion

1. `npm run build` y `npm run lint` en verde.
2. `python3 scripts/verify.py` deja **exactamente los 12 fallos preexistentes**
   (9 rellenos de galeria en `public/media/obra/` y 3 ficheros
   `public/media/vice-*`). Cualquier fallo distinto es una regresion nueva.
3. Contraste AA remedido con `check_contrast_wcag`: el cartel prescinde del scrim
   de `.credits-list`, asi que **no se da por hecho**.
4. Verificacion visual en 1440x900 y 390x844, con `?theme=vice`.
5. Hyprland y Caelestia siguen renderizando su lista de pildoras sin cambios
   visibles.
6. Las siete tecnologias sin proyecto ocultan "Aparece en" sin que el cartel de
   un salto de altura.
7. El friso enciende la marca de la tecnologia activa.
8. Cero errores de consola. Sin `console.log`.

Notas de medicion, del traspaso: `page.screenshot()` en headless perturba las
animaciones (GSAP salta hacia delante); para medir ritmo, muestrear desde dentro
con `setInterval` sobre `tl.progress()`. Para depurar, bloquear el shader con
`page.route("**/viceHaze*", r => r.abort())`.

---

## 7. Puntos abiertos

1. **Zustand.** Fuera por falta de icono. Entra si se decide dibujar el SVG.
2. **Nombres de bloque.** "Escritorio", "Herramientas" e "IA" son propuesta mia.
3. **Frase de React.** Si se prefiere conservar la mencion a Telefonica como
   excepcion larga, esa linea fijara sola la altura reservada del pie.

---

## 8. Fuera de alcance

- Hyprland y Caelestia.
- La seccion de obra, salvo anadir `tooling` al tipo sin mostrarlo.
- Los 12 fallos preexistentes de `verify.py`.
- Borrar `public/media/vice-*` (pendiente de decision del usuario).
