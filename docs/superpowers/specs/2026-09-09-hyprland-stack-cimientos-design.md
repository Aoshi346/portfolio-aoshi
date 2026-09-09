# Los cimientos — "Stack" en Hyprland deja de ser un catastro y pasa a ser tres areas sobre un suelo

Estado: implementado
Plan: `docs/superpowers/plans/2026-09-09-hyprland-stack-cimientos.md`
Fecha: 2026-09-09
Alcance: **solo el tema Hyprland**. `[data-scene="credits"]` (la escena que el selector llama
"Stack" y cuyo rotulo interior es "Con que construyo"). Modulo nuevo
`src/components/hyprStackCimientos.ts`, bloque nuevo en `src/themes/themes.css` bajo
`:root[data-theme="hyprland"]`, el gesto 4 de `src/themes/hypr.choreography.ts` (que se retira y se
sustituye), la puerta de montaje en `src/main.ts`, el arnes nuevo `scripts/measure-cimientos.py`
(que sustituye a `measure-catastro.py`) y el marcador de Hyprland en `scripts/verify.py`.
**Vice no se toca** (cerrado el 2026-08-05). **Caelestia no se toca**: se comprueba que su bandeja
sigue identica. **`src/components/credits.ts` NO se toca en esta fase** (ver `## Restricciones de
DOM`). **`src/data/content.ts` no cambia**: toda cadena sale literal de `skillGroups`, incluido el
rotulo del suelo.

Prototipo aprobado por Aoshi el 2026-09-09, medido y con los numeros de este documento:
`.superpowers/brainstorm/2887426-1788976871/content/cimientos-a2.html` (escritorio) y
`cimientos-a2-movil.html` (movil). Lo aprobo tras ver la A original y pedir un cambio: que los
lenguajes base no fueran a tamano de cartel.

Nace del repaso de Hyprland del 2026-09-09 (fallo dictado 2 de 4): *"la seccion de Stack no se ve
nada bien; rediseno con buena jerarquia, diseno, animaciones y organizacion"*. Aoshi eligio
**partir de cero** (no corregir el catastro) y, entre tres mensajes posibles, **"dominio con
evidencia debajo, donde la evidencia son los lenguajes"**.

---

## Diagnostico — por que el catastro se retira

Medido sobre el build servido en `?theme=hyprland`, 1440x900 y 390x844, el 2026-09-09.

1. **El reparto vertical parece roto.** Los nombres se esparcen por el alto de cada columna con
   `justify-content: space-between`: "Python" arriba, un hueco, "Django", otro hueco, "Node.js".
   Con tres cuerpos distintos encima (23/20/15 px) la columna se lee como un fallo de maquetacion,
   no como una jerarquia.
2. **La jerarquia no se explica.** TypeScript sale mas grande que React y nadie sabe por que: el
   dato que la genera (en cuantas obras aparece) no esta impreso. Vera lo marco en el gate del
   catastro y se acepto como tension.
3. **Cuatro capas de texto pequeno compiten:** rotulo de area, friso de 23 marcas a 14 px (cinco
   de ellas ilegibles a ese tamano, tambien anotado por Vera), los nombres, y la franja de detalle
   al pie con su "Aparece en".
4. **El gesto no existe en reposo.** El spec de Ascua prometio a esta escena el "encendido en
   cadena como lamparas"; en pantalla es una rejilla estatica.
5. **El dato que sostenia todo es mas fino de lo que el catastro daba a entender.** Cruzando
   `stack` y `tooling` de `caseStudies`: TypeScript aparece en 3 obras, React y Python en 2, nueve
   tecnologias en 1, y **siete en ninguna** (Tailwind CSS, Node.js, MySQL, HTML, CSS, C++, n8n).
   Las cuatro transversales (Git, GitHub, Claude Code, Gemini CLI) estan en 4-5 obras porque
   `tooling` existe para eso — el propio `content.ts` dice que *"Git no separa un proyecto de
   otro"*. Una jerarquia por recuento de obras deja un tercio de los nombres huerfanos y no puede
   sostener una escena.
6. **Es el mismo envase que la placa.** Vera ya dictamino en el gate del catastro que "Quien soy" y
   "Stack" compartian caja, borde y `x=102`: *"el interior cambia de gramatica; el envase no cambia
   de nada"*.

## Direcciones descartadas en esta sesion, y por que

| Direccion | Motivo |
|---|---|
| Corregir el catastro (mismo dispositivo, mejor ejecucion) | Aoshi eligio partir de cero. |
| Mensaje "amplitud ordenada" (los 23 siempre visibles, el area como estructura) | Es la tesis del catastro; se retira con el. |
| Mensaje "evidencia por obras" (tecnologia -> obra, puente hacia Obra) | Siete tecnologias sin obra publica y las transversales en todas: el cruce no da para ordenar 23 nombres. Aoshi lo cerro: *"no hay necesidad de poner las obras, la evidencia es los lenguajes"*. |
| Lectura 1: los lenguajes arriba y su ecosistema debajo (TypeScript sostiene React, Next.js, Vite...) | Exige inventar el mapeo lenguaje -> framework, que no existe en `content.ts`. Aoshi eligio la lectura 2. |
| B, "la ladera en filas": tres filas por area que se encienden de abajo arriba | Construida y ensenada junto a A. Aoshi eligio A. |
| Lenguajes base a 89,85 px como cartel al pie | Primera version de A. Aoshi: *"no pongas lenguajes base asi"*. Gritaban mas que todo lo demas. |
| Lenguajes base como cuarta columna | Vuelve a cuatro columnas iguales (el catastro) y pierde la idea de "debajo". |
| Cada lenguaje bajo la columna que sostiene | Mismo mapeo inventado que la lectura 1; Backend y Herramientas se quedarian sin lenguaje debajo. |

---

## Direccion elegida — los cimientos

Dos estratos y nada mas, dentro del margen de `5vw`:

- **Arriba, lo que construye:** tres columnas, una por area de `skillGroups` (Interfaz 8, Backend y
  datos 5, Herramientas 5), de ancho proporcional a su recuento, separadas por linderos verticales
  de 1 px. En cada una, el rotulo del area y sus tecnologias apiladas con icono y nombre, todas del
  mismo cuerpo. **No hay jerarquia entre tecnologias**: la evidencia no es un recuento, es el suelo.
- **Abajo, lo que lo sostiene:** una linea de brasa de 2 px, el rotulo literal "Lenguajes base", y
  los cinco lenguajes (JavaScript, HTML, CSS, C, C++) en una linea, con icono, un cuerpo por encima
  de las columnas. Es el cuarto grupo de `skillGroups`, el que en el catastro era una parcela mas:
  aqui es el suelo del que crecen las otras tres.

### Por que dice "dominio con evidencia" sin escribirlo

La composicion es la frase: tres cosas que construye, apoyadas en cinco cosas que sabe. La linea de
brasa es la unica pieza en `--l1` en reposo, y separa los dos estratos como un suelo separa un
edificio de su cimiento. Quien la lea no cuenta nada: ve que lo de arriba descansa en lo de abajo.

### Elemento firma — el suelo se enciende primero

La entrada la manda el suelo: la linea de brasa se traza de izquierda a derecha y, a su paso, los
cinco lenguajes se encienden; solo despues crecen las tres columnas desde esa linea. Es el
"encendido en cadena" que Ascua prometio a esta escena, con un orden que lleva significado: primero
el cimiento, luego lo construido.

### La ley de la seccion

> Nada se presenta ni se retira por opacidad. Las cosas se **recortan** (`clip-path`), se
> **encienden** (cambian de color) o se **trazan**. El acento `--l1` significa "activo" y en reposo
> solo lo lleva la linea del suelo; `--l3` significa "apuntado" y solo vive mientras hay puntero o
> foco sobre un nombre.

### No colisiona con ningun dispositivo del tema

| Escena | Dispositivo | Gramatica de movimiento |
|---|---|---|
| hero | el lomo | corte de mascara |
| about | la placa | celdas que llegan desde el borde mas cercano |
| obra | el cartel | barra de brasa que suelta letras por columnas; relevo; Flip |
| **credits** | **los cimientos** | **el suelo se traza y enciende; las columnas crecen por recorte vertical** |
| contacto | la cinta | inundacion lateral a sangre |

Lo que se parece y por que no es lo mismo: el cartel tambien traza una barra de brasa, pero la
suya cruza el cartel entero y suelta letras a su paso; aqui la linea es el suelo, se queda, y lo
que suelta son cinco nombres enteros. Y no hay bandas a sangre (Contacto), ni cuatro columnas
iguales (el catastro), ni una pila de cuatro estratos (descartada en el catastro por chocar con
Contacto): son dos estratos dentro del margen.

---

## Composicion

Numeros del prototipo `cimientos-a2.html`, medidos con Playwright el 2026-09-09 sobre un encuadre
de contenido de **1294 px** (equivale al ancho de contenido a 1440 con margenes de `5vw`). Al
portar, **las proporciones mandan sobre los pixeles**.

### Escritorio (>= 1200 px)

```
 CON QUE CONSTRUYO                                                          rotulo 12px --l1
                                                                            + 40 de aire
 INTERFAZ                    | BACKEND Y DATOS   | HERRAMIENTAS             rotulos 12px --haze
 [ic] React                  | [ic] Python       | [ic] Git                 filas de 34px,
 [ic] Next.js                | [ic] Django       | [ic] GitHub              paso 42px
 [ic] TypeScript             | [ic] Node.js      | [ic] n8n
 [ic] Tailwind CSS           | [ic] MySQL        | [ic] Claude Code
 [ic] Vite                   | [ic] RxDB         | [ic] Gemini CLI
 [ic] GSAP                   |                   |
 [ic] Electron               |                   |
 [ic] GTK4                   |                   |
        517px                       323px               323px               columnas 367px alto
                                                                            + 48px de aire
 ────────────────────────────────────────────────────────────────────────── suelo 2px --l1
 LENGUAJES BASE   Interfaces con estado complejo.                           rotulo + frase (hover)
 [ic] JavaScript  [ic] HTML  [ic] CSS  [ic] C  [ic] C++                     37,9px, 45px de alto
```

| Pieza | Valor |
|---|---|
| Rejilla de columnas | `grid-template-columns: minmax(240px, 8fr) minmax(240px, 5fr) minmax(240px, 5fr)`; medido 517 / 323 / 323 con calle de 64 px (32 a cada lado del lindero) |
| Lindero | 1 px `--rule`, de la altura de la columna mas alta (367 px); **sin perimetro exterior, sin tapa ni suelo** (la leccion del gate del catastro: un envase identico al de la placa) |
| Rotulo de area | Instrument Sans 600, versalitas, `--t-1` 12 px, tracking 0,18 em (2,16 px medidos), `--haze` |
| Fila de tecnologia | icono 20 px `--haze` + nombre Bricolage 600 `--t-4` 28,43 px `--text`, `letter-spacing: -0.032em`; caja de 34 px, paso de 42 px (rejilla de 8) |
| Aire entre el pie de las columnas y el suelo | **48 px exactos**. No hay ninguna linea reservada entre medias (ver `## La frase al rozar`) |
| Suelo | 2 px `--l1`, del ancho del contenido |
| Rotulo del suelo | "Lenguajes base", mismo tratamiento que los de area, 22 px bajo la linea |
| Lenguajes | icono 20 px `--haze` + nombre Bricolage 600 `--t-5` 37,9 px `--text`, en una linea, separados por 0,55 em; caja de 45 px |
| Altura util de la escena | del rotulo al pie de los lenguajes, **568 px**: cabe en 900 con aire arriba y abajo |

El icono es el de `simple-icons` que ya inlinea `src/utils/icons.ts` para los 23 slugs, monocromo,
hereda `currentColor`. Cuesta cero bytes: ya esta en el bundle desde el catastro.

### Movil (<= 820 px)

Prototipo `cimientos-a2-movil.html` a 390x844, alto total **865 px** (el catastro medía 1007 y el
dispositivo anterior 1134 y se cortaba).

- Las tres columnas se apilan como filas: rotulo arriba, tecnologias en **rejilla de dos columnas**
  (icono 16 px + nombre `--t-3` 21,33 px), filete de 1 px `--rule` entre areas. Nunca flujo de
  palabras: el flujo reintroduce la prosa que borra los grupos (defecto 5 del diagnostico del
  catastro).
- Margenes de `5vw` (20 px a 390). El catastro fijaba calles de 26 px porque tenia un rectangulo de
  borde duro casi a sangre; aqui no hay borde, asi que el margen del tema vale.
- El suelo a 2 px, el rotulo debajo, y los cinco lenguajes fluyendo a `--t-3` 21,33 px con icono
  16 px en las lineas que hagan falta (dos a 390).
- La frase al tocar vive en una linea fija de 48 px bajo el rotulo del suelo (dos lineas a 16 px).
  En reposo es un hueco. **Aoshi lo acepto a sabiendas**: la alternativa (pintar la frase bajo el
  nombre tocado) empuja la lista 20 px, y en este tema nada se mueve al apuntar.
- Diana tactil de cada nombre >= 44 px de alto (la fila mide 34 y lleva 5 px de relleno arriba y
  abajo).

### Tableta (821-1199 px)

Las tres columnas con el mismo `minmax(240px, Nfr)`: a 821 px caben (240 x 3 + 2 calles de 32). Los
lenguajes se quedan en una linea hasta que no quepan y entonces parten. No hay tercer breakpoint:
si el arnes mide un desborde en este tramo, se ajusta la calle, no se anade un `@media`.

---

## Tipografia

Escalones **discretos** por `@media`, nunca `clamp()` continuo sobre tokens de escala (regla "Never
Do" de `CLAUDE.md`). Todos los tamanos son tokens `--t-*` de la escala cerrada del tema.

| Elemento | < 821 | >= 821 |
|---|---|---|
| Rotulo de seccion ("Con que construyo") | `--t-1` | `--t-1` |
| Rotulo de area y del suelo | `--t-1` | `--t-1` |
| Nombre de tecnologia | `--t-3` 21,33 | `--t-4` 28,43 |
| Lenguaje base | `--t-3` 21,33 | `--t-5` 37,9 |
| Frase `detail` | `--t-2` 16 | `--t-3` 21,33 |

La frase `detail` va en **Instrument Serif italica** (`--font-said`): es la unica cara reservada
del tema y esta reservada exactamente a esto, frases en primera persona, y cada `detail` de
`skillGroups` lo es ("Donde aprendi a pensar en memoria y punteros."). Es la primera vez que esa
voz aparece en esta escena; el catastro no la usaba porque leia `detail` como texto de ficha.

**Una sola talla para los 23 nombres.** El catastro daba tres cuerpos por recuento de obras; este
spec renuncia a esa jerarquia porque el dato no la sostiene (diagnostico 5). La jerarquia es entre
estratos, no entre nombres.

---

## Color y contraste

Tokens de Hyprland. `--text` #ffeae6 para los nombres, `--haze` #b18c86 para rotulos e iconos,
`--rule` #3d1c1c para linderos y filetes, `--l1` #ff5a34 solo para el suelo (y el rotulo de
seccion, como en todas las escenas), `--l3` #ffa03c solo para el nombre apuntado, `--catch`
#ffd9cc para la frase `detail`.

**El contraste se mide contra el fondo real** — el shader `hyprEmber.ts` mas `--bg-fallback` — y
por glifo, con la tecnica de `check_contrast_wcag` de `verify.py`, nunca contra negro plano ni
sobre el viewport entero (la primera medida del cartel sobrestimo el problema por eso). Referencias
ya medidas en el repo: `--haze` sobre tinta 6,81:1, sobre #3a1008 5,54:1; `--l1` sobre tinta
6,61:1. Los iconos son decorativos (`aria-hidden`, `data-decorative`): su suelo es el 3:1 de 1.4.11,
no 4,5. La frase en `--catch` a 21,33 px italica es texto: 4,5:1.

**Aviso heredado:** el techo de brillo del shader que hacia caer el titular del cartel a 3,88:1 en
su peor 0,5 % de fotogramas sigue pendiente de decision de producto, y afecta a todo texto en
`--haze` sobre el fondo real. El arnes de esta fase mide los rotulos y lo anota; no lo arregla.
**Toda medida se toma con el oyente de consola puesto**: la calibracion del cursor se hizo durante
semanas contra una pagina cuya coreografia reventaba con `gsap is not defined` y el shader se leia
mucho mas brillante de lo que le toca.

---

## Movimiento

Los dos regimenes del tema y ninguno mas: **corte** con `--hard` (`cubic-bezier(0.7,0,0.2,1)`) y
**atmosfera** con `--slow` (`cubic-bezier(0.16,0.84,0.28,1)`). Las clases hacen el trabajo y el CSS
marca los tiempos; GSAP/ScrollTrigger solo decide **cuando**, igual que en la placa.

### Entrada — el suelo se enciende primero

| # | Que | Empieza | Dur | Curva |
|---|---|---|---|---|
| 1 | La linea del suelo se traza de izquierda a derecha (`scaleX` 0 -> 1 con `transform-origin: left`) | 0 | 500 | corte |
| 2 | Cada lenguaje se enciende de `--rule` a `--text` (icono de `--rule` a `--haze`) cuando la linea llega a su columna | `x_lenguaje / ancho * 500` | 420 | corte |
| 3 | Cada columna crece del suelo: `clip-path: inset(100% 0 0 0)` -> `inset(0)` | 520 + `c * 90` | 900 | atmosfera |

Total: la ultima columna aterriza a 1600 ms. Los nombres de las columnas nacen ya en su color: lo
que los revela es el recorte, no un encendido, para que la escena tenga **un** encendido (el del
suelo) y no veintitres.

**El disparador es la caja del propio dispositivo, no la seccion.** `ScrollTrigger` con
`trigger: [data-cimientos]`, `start: "top 80%"`, `once: true`, que anade `cimientos-lit`; entra en
la red `net()` de scroll rapido con el mismo umbral; y la limpieza de remonte quita la clase. Es la
leccion del fallo 1 de este mismo repaso (la placa): con el `is-lit` de la seccion a `top 90%`, el
montaje de la placa corria entero con la placa 119 px bajo el pliegue, y nadie lo vio nunca.

### Apuntado — la frase al rozar

Rozar un nombre (o darle foco) lo pasa a `--l3` y escribe su `detail` en la linea del rotulo del
suelo, a la derecha de "LENGUAJES BASE", alineada a su linea base. Aparece por **recorte lateral**
(`clip-path: inset(0 100% 0 0)` -> `inset(0)`, 420 ms corte) y se retira por el mismo camino (900 ms
atmosfera). **Nada se mueve**: la linea del rotulo tiene la altura de la frase desde el principio y
en reposo su mitad derecha esta vacia. Al salir, el nombre vuelve a `--text` en 900 ms atmosfera:
encender es un corte, apagar es enfriarse (misma asimetria que la placa).

**El nombre apuntado nunca se queda encendido.** Es el P0 que once revisiones del catastro no
vieron: la luz del lindero revertia y el nombre no, y tras un barrido quedaban cuatro nombres
acentuados a la vez. Aqui es una asercion del arnes (gate 4), no una intencion.

En movil el toque hace lo mismo y la frase va en la linea fija bajo el rotulo. Un segundo toque
sobre el mismo nombre lo apaga.

### Ambiente

Ninguno. El tema gasta su unico `infinite` en el hero (`hypr-hero-idle 6s`) y esta escena no anade
otro. Con el dispositivo aterrizado, lo unico que se mueve es lo que el visitante toca.

### `prefers-reduced-motion`

Ni `transition: none` a secas ni nada invisible: el suelo y los lenguajes resuelven a su color
final, las columnas a `clip-path: none`, la frase aparece y desaparece sin transicion. El
dispositivo completo se lee sin haber interactuado. Y la guardia alcanza tambien a los
pseudo-elementos, uno por uno, si los hay: `*` dentro de `@media (prefers-reduced-motion)` **no**
los alcanza (pagado en B2 de Caelestia).

### Que esta prohibido

- Cualquier `opacity` que presente o retire contenido.
- Bucles infinitos, `backdrop-filter`, desenfoques, resplandores, sombras, esquinas redondeadas.
- Cualquier `--l1` que no sea el suelo o el rotulo de seccion; cualquier `--l3` sin puntero o foco.
- Monoespaciada, prompts, cursores parpadeantes, badges de terminal.
- Un pin de ScrollTrigger. La escena ocupa una pantalla y no se scrubbea; un pin obligaria a entrar
  en la escalera de `refreshPriority` y no compra nada.
- Un `hover` por CSS `transform` sobre el nombre: si algun dia el nombre recibe un transform de
  GSAP, el inline gana siempre. El apuntado es color y recorte, no desplazamiento.

---

## Restricciones de DOM — como no romper Vice ni Caelestia

**Modulo propio, DOM propio, y el generico se oculta entero.** Es el patron que Caelestia dejo
probado dos veces (B3 con `projectScene.ts`, B4 con `credits.ts`): `hyprStackCimientos.ts` construye
su propio arbol a partir de `skillGroups` y lo monta como hermano de `.credits` dentro de
`[data-scene="credits"]`; `themes.css` oculta `.credits` entero bajo Hyprland (`display: none`) y
oculta `[data-cimientos]` en Vice y Caelestia desde la hoja **base**, no desde cada tema — el
patron aditivo se ha roto cuatro veces por olvidar el `display: none` de base.

**`credits.ts` no se toca en esta fase.** Hoy construye, para los tres temas, las parcelas, franjas,
frisos y conmutadores de grupo del catastro (comentario *"El catastro de Hyprland"* en el propio
fichero), que Vice y Caelestia ocultan por CSS. Tras esta fase esos nodos quedan muertos en los tres
temas. **Retirarlos es una tarea aparte**, posterior a que esta escena este TERMINADA, porque toca
el fichero que comparten los tres temas y el friso de Vice anima los hijos directos de
`[data-credit-roll]`: se hace con `git worktree` contra `main` y con `verify.py` en Vice antes y
despues, nunca a la vez que el rediseno. Queda anotado como deuda con nombre, no como olvido.

**Lo que se retira de Hyprland:**

- El gesto 4 de `hypr.choreography.ts` ("la corriente": carril, rotulo, chispa, nombres, franjas)
  y su sonda `window.__hyprSkills` / `__hyprSkillTimers`. En su lugar, el disparador de
  `cimientos-lit` y su entrada en `net()`.
- El bloque `EL CATASTRO` de `themes.css` bajo `:root[data-theme="hyprland"]` (de `.credits-grid`
  a `.credit-group-toggle`, unas 700 lineas) mas su `@media` de movil. Se sustituye por el bloque
  `LOS CIMIENTOS`, que se espera del orden de 200 lineas.
- `scripts/measure-catastro.py` (sus diez aserciones miden un dispositivo que ya no existe) y las
  tres aserciones de `verify.py` que comprueban `.credits-list { display: contents }` y la columna
  de rejilla de cada `.credit` bajo Hyprland. Se sustituyen por `measure-cimientos.py` y por un
  marcador nuevo: bajo Hyprland `.credits` no se pinta y `[data-cimientos]` si.

**`data-scene` no se toca**: es como el sitio marca sus cinco secciones y como la coreografia las
recorre. El modulo monta dentro de la escena, nunca la sustituye.

**Todo el CSS nuevo bajo `:root[data-theme="hyprland"]`** salvo el `display: none` de base de
`[data-cimientos]`.

### Accesibilidad

- Cada nombre es un `<button type="button">` con `aria-pressed` (la frase mostrada es un estado
  seleccionable, como las piezas de Caelestia); asi el cursor de Hyprland lo trata como pulsable
  y el teclado llega a lo mismo que el raton. Foco visible: `outline: 2px solid var(--l1)` con
  `outline-offset: -2px` — **el mismo canto que Aoshi ha dictado como fallo 3 del repaso** ("el
  recuadro naranja"), asi que este punto se cierra con la decision de ese fallo, no aqui.
- La linea de la frase es una region `aria-live="polite"`: al apuntar no se mueve el foco y el
  lector anuncia la frase.
- Los iconos llevan `aria-hidden` y `data-decorative`.
- Los rotulos de area son `<h3>` bajo el `<h2>` "Con que construyo" que ya pone `skills.ts`.

---

## Presupuesto

- JS: modulo nuevo con `import()` diferido bajo `theme.id === "hyprland"`, como `obraCartel.ts`;
  no entra en el bundle inicial. Objetivo: <= 3 KB gzip.
- CSS: la hoja es unica para los tres temas y llega entera al first paint. Retirar ~700 lineas del
  catastro y anadir ~200 deja la hoja mas ligera de lo que esta.
- DOM: 23 botones, 23 iconos SVG, 4 rotulos, 3 linderos, 1 suelo, 1 linea de frase. Menos de la
  mitad de los 181 nodos que montaba el catastro.

---

## Los gates — `scripts/measure-cimientos.py`

Cada uno nace de un fallo real de esta pista o de otra, y **ninguno se acepta sin haberlo visto
dar rojo contra el fallo que dice cazar** (trece instrumentos rotos llevan pagados en este
proyecto). Contra el build de produccion servido, nunca `npm run dev`. Con oyente de consola en
todas las paginas, incluidas las de Vice y Caelestia.

1. **Los cimientos se VEN en Hyprland.** Sin esto los demas gates se autoanulan: un nodo con
   `display: none` no desborda ni descuadra. Y `.credits` (el generico) **no** se pinta bajo
   Hyprland.
2. **Los cimientos no existen en Vice ni en Caelestia** (comprobados por separado, no con un `AND`).
   Y la bandeja de Caelestia sigue con sus 23 piezas.
3. **La entrada se ve.** Con la seccion encendida (`is-lit`) y `[data-cimientos]` entero bajo el
   pliegue, tras 1500 ms el suelo sigue a `scaleX(0)` y las columnas recortadas; con el
   dispositivo al 80 %, aterriza todo. Anclado a estado, nunca a cronometro: el `setTimeout` de
   esta sandbox llega con cientos de ms de retraso bajo `swiftshader`. Es la asercion que a la
   placa le falto durante un mes.
4. **Ningun nombre lleva acento en reposo, y el apuntado se apaga al salir.** Se barre por las tres
   columnas con `hover()` real (un `MouseEvent` sintetico **no** dispara `:hover`) y al final
   ninguno de los 23 esta en `--l3`. Es el P0 del catastro.
5. **La frase no mueve nada.** `getBoundingClientRect()` del suelo y de los cinco lenguajes antes y
   despues de rozar cinco nombres: identicos al pixel. En movil, ademas, la altura de la escena no
   cambia al tocar.
6. **La frase es literal.** El texto que aparece al rozar cada uno de los 23 es exactamente su
   `detail` de `skillGroups`, y en reposo la linea esta vacia. Cero cadenas que no esten en
   `content.ts` en todo `[data-cimientos]` (los rotulos incluidos).
7. **Nada desborda su caja** en 390, 821, 1024, 1200 y 1440 — medido sobre nodos renderizados,
   contra el `getBoundingClientRect()` del contenedor, **no** con `scrollWidth`/`scrollHeight`
   (mienten con un `transform` dentro de un `overflow: clip`, pagado en B6).
8. **Los tres pies de columna y el suelo**: el suelo esta a 48 px del pie de la columna mas alta, y
   las tres columnas nacen a la misma cota.
9. **Tallas en la escala**: el `font-size` computado de todo lo que pinta texto en
   `[data-cimientos]` cae en un `--t-*`.
10. **Contraste contra el fondo real**, por glifo, con el shader activo: nombres (`--text`),
    rotulos (`--haze`), frase (`--catch`) y el nombre apuntado (`--l3`) sobre el fondo muestreado
    alrededor de su `rect`. Los iconos contra 3:1. Detras de `--contraste`, como en el cartel: mide
    tambien un hallazgo de producto abierto (el techo de brillo) y no puede dejar el semaforo de
    geometria en rojo permanente.
11. **Movimiento reducido**: sin lienzo de entrada, suelo y lenguajes en su color final, columnas
    sin recorte, y la frase sin transicion; y la guardia alcanza a cada pseudo-elemento.
12. **Diana tactil >= 44 px** en movil, medida solo sobre nombres visibles.
13. **Consola**: cero errores y cero `context lost` en las tres paginas (Hyprland, Vice,
    Caelestia). Sin oyente en Vice y Caelestia, un fallo global en `themes.css` deja el gate en
    verde (pagado en el cursor de Caelestia).

Y en `verify.py`: el marcador de Hyprland pasa a comprobar que `.credits` no se pinta y
`[data-cimientos]` si; los dos marcadores de Vice y Caelestia no cambian. `verify.py` debe salir
con 0 fallos nuevos sobre `verify-baseline.json`.

---

## Criterios de aceptacion

- `npm run build` y `npm run lint` en verde.
- `scripts/measure-cimientos.py`: 0 fallos, con cada gate visto en rojo contra su sabotaje antes.
- `python3 scripts/verify.py` con codigo 0 contra su linea base.
- `measure-placa.py`, `measure-cartel.py` y `measure-cursor-luz.py` siguen en verde: la escena es
  vecina de la placa y del cartel, y sus 23 botones son dianas nuevas del cursor.
- Capturas reales en 390x844, 821x1024 y 1440x900 con `?theme=hyprland`, en reposo, a media
  entrada y con un nombre apuntado, con el oyente de consola puesto.
- Vice y Caelestia **identicos** a `main`, comprobado con `git worktree` (nunca `git stash`).
- Revision de Aoshi **en el sitio real** por tailnet, no sobre capturas.
- Gates `lidia-naive-tester` y `vera-art-director` (umbral 7,5/10). Vera lleva marcando
  "envase identico a la placa" y "el dato de la jerarquia no esta impreso": los dos desaparecen por
  construccion, y se le pide que lo confirme o lo desmienta.

---

## Pendiente de decision

- **El canto naranja del foco y del cursor** sobre los 23 botones: lo decide el fallo 3 del repaso,
  que es de todo el tema y no de esta escena.
- **Las siluetas del selector de escenas** dibujan el catastro: lo cubre el fallo 4 del repaso,
  que Aoshi pidio dejar para el final.
- **Retirar los nodos muertos del catastro de `credits.ts`**: tarea aparte, posterior a que esta
  escena este TERMINADA (ver `## Restricciones de DOM`).

---

## Registro de implementacion

### La tabla de contraste final (gate 10, tras la ronda de arreglo del sesgo)

Peor caso de cada par en 24 fotogramas sobre el shader real, con `.cim-nombre` (React) apuntado
para que la frase (`--catch`) este viva:

| Par | Peor caso medido | Piso |
|---|---|---|
| nombre `--text` | 9,66:1 | 4,5 |
| rotulo `--haze` | 5,81:1 | 4,5 |
| lenguaje `--text` | 15,60:1 | 4,5 |
| icono decorativo `--haze` | 6,53:1 | 3,0 (decorativo) |
| apuntado `--l3` | 9,66:1 | 4,5 |
| frase `--catch` | 9,30:1 | 4,5 |

Ninguno cae bajo su piso. `.cim-rot` (rotulo, `--haze`) era el candidato mas probable a tocar el
techo de brillo conocido del shader de Hyprland y aguanta 5,81:1, mas de un punto por encima del
4,5 exigido: a diferencia del cartel, este dispositivo no roza ese techo.

### El sesgo del gate de contraste, y su direccion real

El calculo original de `gate_10_contraste_fondo_real` hacia un viaje luminancia -> gris (gamma
plana 2,2) -> luminancia (formula exacta por tramos) antes de calcular el ratio final, y ese viaje
no cierra: las dos curvas no son inversas exactas entre si. La revision de la ronda de arreglo dijo
que el viaje **inflaba** el ratio — y eso es falso en esta escena concreta. Comprobado
aritmeticamente con las mismas 24 muestras pasadas por las dos formulas (script
`compara_gate10.py`, fuera del repo): a media luminancia (L≈0,5) el viaje SUBESTIMA la luminancia
recuperada, lo que si inflaria el ratio si el fondo viviera ahi. Pero el fondo real de este gate
(`peor_lum`) vive casi negro, entre 0,003 y 0,04, y en ese rango el viaje hace lo contrario:
SOBRESTIMA la luminancia recuperada (a L=0,0035 el viaje devuelve ~0,0070, el doble) porque el
tramo lineal bajo 0,04045 de la curva exacta no es el mismo tramo que el de una gamma 2,2 plana.
Con el fondo sobrestimado, el ratio calculado saliá mas BAJO que el real: el calculo viejo era
**conservador**, no optimista, en los seis pares medidos (diferencias entre +0,36 y +0,91 puntos,
todas a favor del nuevo calculo, ningun par cambia de lado respecto a su piso). La diferencia que
importa retener: no es "quitamos un sesgo que favorecia al gate", es "quitamos una conversion cuyo
sesgo cambia de signo segun el tramo de luminancia y por eso no se puede corregir con una
constante" — la primera frase es falsa para esta escena, la segunda es la que motivo el fix.

### Las medidas de la maquetacion

- **Columnas**: 550 / 344 / 344 px a 1440px de ancho de contenedor — razon 1,6 : 1 : 1, el 8/5/5
  del spec, sobre un contenedor real de **1238px** (no los 1296px del prototipo aprobado: 1238px
  es el ancho real de la escena compartida con Vice/Caelestia, y el propio spec manda que las
  proporciones pesen mas que los pixeles absolutos).
- **Suelo**: a 48px exactos por debajo del pie de la columna mas alta, y las tres columnas nacen a
  la misma cota (mismo `top`).
- **Movil**: alto de la escena 1184px, con las tres areas y los cinco lenguajes base alcanzables
  porque en Hyprland el documento se desplaza (no hay scroll interno que perseguir, al reves que en
  los workspaces de Caelestia).

### Lo que el catastro se llevo por delante

1662 lineas borradas en total: 797 de `themes.css` (el bloque `Hyprland: el catastro`), 526 de
`scripts/measure-catastro.py` (borrado entero) y 339 de `src/themes/hypr.choreography.ts` (los
gestos 4 "la corriente" y 5 "el apuntado"). Vice y Caelestia quedaron **identicos** a `main`,
comprobado por `git worktree` (nunca `git stash`): el hash `sha1` del `outerHTML` de
`[data-scene="credits"]` bajo los dos temas coincide entre esta rama y `main` (`d489e05`).

### `verify.py` SI invocaba el arnes del catastro como subproceso

Al contrario de lo que dice `rules/verification.md` ("un solo `subprocess`... son arneses Playwright
independientes"), `scripts/verify.py` llevaba una funcion `check_catastro_measure()` que lanzaba
`measure-catastro.py` como subproceso desde su flujo normal (`if theme == "hyprland" and not
reduced: ...`). Se retiro junto con el arnes (y el import `subprocess`, que quedaba sin uso). El
arnes nuevo, `measure-cimientos.py`, NO se engancha a `verify.py`: sigue el patron real del
proyecto, independiente y lanzado a mano, tal como describe `rules/verification.md`.

### `gsap` sale del destructuring de `hyprChoreography`

Al retirar los gestos 4 y 5 (los unicos que creaban tweens de GSAP en la coreografia de Hyprland),
la firma de la funcion paso de `({ gsap, ScrollTrigger, root })` a `({ ScrollTrigger, root })` y se
dejo un comentario de aviso exactamente en ese punto. Es la forma precisa del fallo ya pagado en
este tema: sin la palabra en el destructuring, `tsc` y `eslint` pasan igual (el identificador
`gsap` existe como global en los tipos), pero el chunk construido revienta con `gsap is not
defined` en cuanto `reveal.ts` llama a la coreografia — el fallo que dejo la seccion de creditos sin
sus gestos durante semanas sin que nada lo avisara salvo la consola del navegador.

### El arnes del cursor quedaba ciego, y como se dejo

`scripts/measure-cursor-luz.py` no llegaba ni a dar un recuento: su diana `PULSABLE_FONDO =
".credit"` (la UNICA diana OCLUIDA del arnes — la que ejercita el mecanismo de `background-image`
en vez del de lienzo, porque un ancestro opaco se interpone entre ella y el lienzo del hueco) quedo
oculta bajo Hyprland (`display: none` en `.credits-grid`, commit `ffb62ca`, tarea 2 de este mismo
plan) sin que el arnes se actualizara. `scroll_into_view_if_needed()` sobre un nodo invisible no
falla con un mensaje: se cuelga en un timeout de ~30s sin imprimir ningun recuento.

La correccion NO sustituye la diana — los cimientos no tienen fondo propio detras de sus nombres,
asi que `.cim-nombre` no vale como reemplazo, y hacerlo dejaria a la familia "ilumina" (la unica
ocluida) sin representante real, ablandando el gate por la puerta de atras. En vez de eso se anadio
`_diana_pinta()`, que comprueba `display`/`visibility`/`opacity` computados y el
`getBoundingClientRect()` de la diana ANTES de tocarla; si no se pinta, el arnes anade un fallo
explicito (que cita el commit y la fecha del cambio que la dejo ciega, y deja escrito que la
familia ocluida necesita una diana nueva) y salta solo esa diana con `continue`, dejando correr el
resto del arnes hasta su recuento final. No se recalibro nada de `hyprCursor.ts`, ningun piso ni
umbral del cursor.

### Los gates vistos en rojo antes de aceptarse

| Gate(s) | Fallo visto | Salida resumida |
|---|---|---|
| 1, 2, 13 | Tarea 1: contra el catastro vivo | 4 fallos: `[data-cimientos]` no se ve, `.credits-grid` se pinta (x2 anchos) |
| 7, 8, 9, 12 | Tarea 2: antes del modulo | 11 fallos: "no existe `[data-cimientos]`" por gate y por ancho |
| 3 (paso A y B) | Tarea 4: entrada sin disparo | 4 fallos: todo pintado desde el reposo, sin disparo bajo el pliegue |
| 3 paso B (ronda 1) | Tarea 4: sabotaje `colsAbiertas===4` | 2 fallos: agota la fecha limite de 6000ms con la ultima lectura real (3/3, 5/5) |
| 4, 5, 6 | Tarea 5: antes del apuntado | 11 fallos: frase vacia al rozar (x5 escritorio + 1 movil), 0 `aria-pressed` (x5) |
| 4, 5, 6 (ronda hibrida) | Tarea 5: Enter de teclado apaga el nombre que Tab acaba de encender | 1 fallo: `TypeScript` queda `aria-pressed=false` tras Enter |
| 11 | Tarea 6: sin guardia de `reduce` | 2 fallos: 33 nodos con transicion/animacion viva bajo `reduce` |
| 10 | Tarea 7, ronda 1: sesgo del viaje RGB (visto por comparacion pareada, no por rojo binario) | tabla comparada, ningun par cambia de lado |

Cada familia se vio dar rojo contra el fallo exacto que dice cazar antes de aceptar su gate en
verde, siguiendo la regla del proyecto de no aceptar instrumentos sin sabotear primero.

### Las dos rondas de arreglo, y que las provoco

1. **Tarea 4, ronda 1**: el paso B de `gate_3_la_entrada_se_ve` se titulaba "anclado a ESTADO,
   nunca a cronometro" y su punto de corte real era `pg.wait_for_timeout(2500)` fijo — un
   cronometro con solo 900ms de margen sobre el peor caso real de la coreografia (1600ms). Se
   sustituyo por un sondeo asincrono dentro de la pagina con una fecha limite de FALLO (6000ms),
   nunca de espera.
2. **Tarea 5, ronda 1**: `ultimoPuntero`, una sola variable compartida por los 23 botones,
   quedaba rancia entre modalidades — un toque la dejaba en `"touch"` y no la resetean ni `focus`
   ni `blur`, asi que un Enter de teclado sobre un nombre que el propio Tab acababa de encender lo
   apagaba en el acto. Arreglo: `clic()` ignora las activaciones de teclado leyendo
   `event.detail === 0` (la senal que el motor pone en el `MouseEvent` sintetico de Enter/Espacio),
   en vez de fiarse de la historia acumulada en `ultimoPuntero`.

### Lo que queda abierto

- **El canto naranja del cursor** sobre los pulsables (fallo 3 del repaso de Hyprland): reproducido
  otra vez sobre estos 23 botones nuevos; es de todo el tema, no de esta escena, y esta pendiente
  de decision (ver `## Pendiente de decision`).
- **Las siluetas del selector de escenas** que dibujan el catastro (fallo 4 del repaso): Aoshi pidio
  dejarlo para el final; sigue sin tocar.
- **La limpieza de los nodos muertos de `credits.ts`**: tarea aparte, posterior a que la escena
  este TERMINADA.
- **La diana ocluida del arnes del cursor** (`measure-cursor-luz.py`): falla explicito con la nueva
  guarda `_diana_pinta()`, pero la familia "ilumina" sigue sin una diana ocluida real que medir —
  encargo pendiente para quien retome el cursor de Hyprland.
