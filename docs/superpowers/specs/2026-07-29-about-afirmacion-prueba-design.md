# "Quien es" en Vice — afirmacion y prueba

> Spec de diseno. Escrito el 2026-07-29 tras un brainstorm con companion visual y dos
> especialistas (`especialista-ux-ui`, `especialista-animaciones`) trabajando en paralelo
> sobre el mismo brief. Todo numero de este documento esta medido contra el codigo, no
> deducido. La frase "no se ha tocado `src/`" era cierta al escribirlo y ya no lo es:
> ver el registro de implementacion al final.

Estado: **implementado** — mergeado a `main` desde `design/about-afirmacion-prueba`
(worktree aparte). No lleva plan en `docs/superpowers/plans/`: se implemento
directamente desde este spec por decision del usuario, asi que
`check_spec_plan_consistency` no tiene casillas que cruzar. **Lo que sustituye al
plan es el registro de implementacion del final**, que dice en que se desvio la
realidad de lo aprobado aqui y por que; si los dos se contradicen, manda el
registro.

## Encargo

Remodelar `[data-scene="about"]` **solo en el tema Vice**. Decision del usuario:
composicion, misma informacion, cero aire muerto, que se lea como un plano. Autorizado
re-agrupar datos y reescribir rotulos; vetado inventar informacion.

## Diagnostico — por que la composicion actual no funciona

Medido, no opinado:

1. **Los delays del gesto se gastan fuera de pantalla.** Con `start: "top 78%"` a
   1440x900, cuando arrancan los tweens la franja de cifras esta ~330px por debajo del
   pliegue y el track ~410px. Los delays de 0.35s y 0.5s se consumen antes de que el
   bloque sea visible: el usuario ve el fotograma final, no el gesto. En movil el track
   queda ~900px bajo el pliegue.
2. **El ancla del trigger esta calibrada contra algo que se mueve.**
   `:root[data-theme="vice"] [data-scene]` lleva `padding-top: calc(6rem + 3rem + 6.5vh)`
   = **202,5px a 1440x900** (`themes.css:129-132`), y la seccion es `min-h-screen
   justify-center`, asi que el contenido arranca en `padding + (altoDisponible -
   altoContenido)/2`. Con el contenido actual (~420px) el primer pixel util cae en
   **924px: 24px por debajo del pliegue**. El desplazamiento varia con el alto del
   contenido, la tipografia y el viewport.
3. **Inversion de jerarquia.** La cifra mide 54,4px a 1440 y el nombre 32px. Lo mas
   grande de una seccion titulada "Quien es" son cuatro numeros que no significan nada
   leidos sin su rotulo. La jerarquia de **movimiento** estaba invertida igual: el bloque
   de mayor amplitud del gesto eran las cifras (34px), no el nombre.
4. **Falta el escalon tipografico intermedio.** Un registro de cartel y siete tamanos
   apinados entre 0,6 y 0,85rem; nada en la franja 1,0-1,6rem. La sensacion de vacio no
   es falta de contenido: es contenido que no reclama espacio.
5. **El aire real es horizontal.** A 1440 el track se parte en dos columnas de 434px y la
   linea mas larga mide ~340px: cada `.about-item` deja 200-280px de fondo vacio a su
   derecha, cuatro veces.
6. **Ritmo plano.** Las bandas del cuerpo estan separadas por 48px iguales. Separacion
   uniforme = ausencia de agrupacion.
7. **Redundancia.** Tres de los ocho tokens de ficha + cifras se leen dos veces en el
   mismo encuadre: "Universidad Santa Maria" (`dt` Estudia + item de educacion), "2021"
   (cifra + periodo) y "10.º semestre" (cifra + el mismo periodo).
8. **La ficha actual ya ES una tarjeta de reparto** (retrato + nombre + rol + estado):
   about no compite con creditos en el futuro, le esta robando el gesto ahora.
9. **`backdrop-filter: blur(6px)` en movimiento.** El parallax de la ficha va de
   `top bottom` a `bottom top` (~1800px de scroll) invalidando el blur cada frame encima
   del canvas WebGL, a cambio de 39px de recorrido total imperceptible.
10. **Densidad tirada.** `experience[0].description` existe en `content.ts:96-98` y
    `about.ts` no lo pinta.

## Direccion elegida — "Afirmacion y prueba"

Cada cosa que Aoshi dice saber hacer, unida por un conector a lo concreto que la
sostiene. **Cambia el eje de la seccion de "cuanto llevo" a "que he hecho"**, que es el
terreno donde un perfil junior gana en vez de perder.

Descartada explicitamente una linea de tiempo / diagrama de Gantt: un eje de cinco anos
con "escribiendo codigo desde 2021" como barra completa **lee como cinco anos de
experiencia profesional**, cuando lo que hay es un estudiante en 10.º semestre con una
pasantia. El grafico afirmaria algo que los datos no dicen. Por el mismo motivo **la cifra
"2021 · Desde" desaparece de la seccion**.

### Elemento firma

**El conector que se traza.** En reposo es un munon al 22% de su longitud: la afirmacion
esta ahi, sin sostener. Al pasar el raton la linea se dibuja hasta el final y la punta
aterriza. El vinculo *se hace* delante del visitante, que es exactamente lo que el bloque
afirma. Toda la audacia de la seccion se gasta ahi; lo demas se calla.

### Metafora

**About = documento de ANTES; creditos = cartel de DESPUES.** Los dos especialistas
llegaron a esta tesis por separado. About cede el registro de cartel a la seccion de
creditos. El cursor sigue siendo la unica marca de sincronismo.

## Composicion — desktop >=1024px

```
[retrato 150x188]  QUIEN ES ─────────────────
                   AOSHI
                   BLANCO SANZ            (contorno)
                   [Disponible] Rol · Base · Freelancer

                   Llevo datos reales a interfaces que la gente usa todos los dias.

EN QUE ME ENFOCO                    Cada afirmacion, con lo que la sostiene.
─────────────────────────────────────────────────────────────────────────
DATOS A GRAN      ──────◆   Telefonica Venezuela · Pasantia B2C
ESCALA                      Herramientas internas para el equipo de conocimiento
                            al cliente, con foco en datos de campanas a gran escala.
─────────────────────────────────────────────────────────────────────────
INTERFACES QUE    ──────◆   1 de 5 repositorios publicos, en produccion
AGUANTAN                    Estado complejo sin romperse: lo que esta desplegado
                            sigue funcionando.
─────────────────────────────────────────────────────────────────────────
DESARROLLADOR     ──────◆   Ingenieria de Sistemas · 10.º semestre
FULL STACK                  Universidad Santa Maria, en curso.
─────────────────────────────────────────────────────────────────────────

TRAYECTORIA                              (nota, alineada abajo)
Pasante B2C ... Telefonica Venezuela     La mayoria de mis repositorios
Ago 2025 — May 2026                      son privados. Aqui estan los
Herramientas internas...                 publicos que mejor muestran
Universidad Santa Maria                  como pienso y que construyo.
Ingenieria de Sistemas, en curso
```

- Cabecera: `grid-template-columns: 150px 1fr`, `gap: 0 34px`, `align-items: end`.
- Pareja: `grid-template-columns: 1fr 88px 1fr`, `align-items: center`, `padding: 22px 0`,
  separadas por hairline de `rgb(255 244 232 / .08)`.
- Pie: `grid-template-columns: 1.15fr 0.85fr`, `gap: 0 46px`, con hairline superior.

### 860-1024px

Cabecera con retrato a 120x150 y nombre a `clamp(3.4rem, 6vw, 4.6rem)`. Parejas a
`1fr 64px 1fr`. Pie a una sola columna con la nota debajo de Trayectoria.

### Movil 390x844

El conector horizontal no sobrevive. La pareja **se apila** y el conector **se vuelve
vertical**: baja por el margen izquierdo desde la afirmacion hasta la prueba, con el rombo
abajo. **Trazado entero desde el primer frame** — en tactil no hay hover, asi que el gesto
sobrevive como forma aunque desaparezca como animacion.

Retrato 96x120, nombre 2,5rem, lead 1,3rem, afirmacion en Pathway Gothic 1,15rem
(el contorno a ese tamano pierde legibilidad), pie a una columna.

## Contenido — que se dice y donde

Regla de reparto: **cada dato vive una sola vez en el plano.**

| Dato | Vive en | Sale de |
|---|---|---|
| Nombre | Cabecera, display | — |
| Disponible para proyectos | Cabecera, chip magenta | — |
| Rol, Base, Ahora (`Freelancer`) | Cabecera, fila de meta en linea | el `<dl>` vertical |
| `aboutCopy[0]` | Lead, 1,9rem peso 200 | — |
| `focusAreas[0].title` | Afirmacion 1 | la columna "Enfoque" del pie |
| `experience[0]` (org + rol + `description`) | Prueba 1 | — |
| `focusAreas[1].title` | Afirmacion 2 | la columna "Enfoque" del pie |
| `5 publicos` + `1 en produccion` | Prueba 2 | la franja de cifras |
| `identity.role` | Afirmacion 3 | — (se repite a proposito con la meta: es la unica reaparicion aceptada, porque una es dato de ficha y otra es afirmacion) |
| `education[0]` + `10.º semestre` | Prueba 3 | la franja de cifras |
| `experience[0]` completo con periodo | Pie, Trayectoria | — |
| `education[0]` | Pie, Trayectoria | — |
| `aboutCopy[1]` | Pie, nota | — |
| **`2021 · Desde`** | **eliminado de la seccion** | insinuaba antiguedad |
| **`education[1]` (100 Days of Code, Udemy)** | **eliminado de la seccion** | decision del usuario |

### Rotulos

- "En que me enfoco" se conserva como cabecera del bloque de parejas (ahora es literal).
- La columna "Enfoque" del pie **se oculta en Vice**: las parejas SON el enfoque, y
  mantener las dos produce la duplicacion que este rediseno viene a quitar.
- `dt` "Ahora" se funde con el chip: `Freelancer` + `Disponible`.

### Cambios en `src/data/content.ts`

1. **`education` se queda con un solo elemento.** El bootcamp de Udemy sale. El `map` de
   educacion de `about.ts` hay que revisarlo: con un array de uno, cualquier logica que
   asuma varios sobra.
2. **`stats` deja de renderizarse en Vice** (no se borra: los otros dos temas la usan).
3. No se anaden campos nuevos. La direccion elegida **no** necesita fechas numericas —
   eso era requisito del eje temporal, que queda descartado.

## Estructura DOM — el punto mas delicado

`about.ts` lo comparten los tres temas. Hyprland y Caelestia visten el mismo DOM como
widgets de interfaz. **Reparto propuesto:**

| Nodo | Vice | Hyprland / Caelestia |
|---|---|---|
| `[data-card]` (avatar, nombre, estado, `<dl>`) | **se reutiliza**, re-estilado como cabecera horizontal | sin cambios |
| `[data-line]` (2 lineas de copy) | `aboutCopy[0]` como lead; `aboutCopy[1]` al pie | sin cambios |
| `[data-stats]` | `display: none` | sin cambios (conserva `scene-surface`) |
| `[data-track]` | se reutiliza; la columna "Enfoque" oculta | sin cambios |
| **`[data-focus-pairs]` (NUEVO)** | visible, es el bloque firma | `display: none` |

Solo se anade **un** subarbol nuevo, y se envia oculto por defecto: `display: none` en la
regla base y visible solo bajo `:root[data-theme="vice"]`. Es el patron aditivo estricto.

**Riesgo declarado:** las tres afirmaciones y las tres pruebas son contenido que solo Vice
muestra, asi que viajan en el DOM de los tres temas sin usarse en dos de ellos. Es el
precio de no bifurcar `about.ts` por tema. Alternativa rechazada: construir el subarbol
condicionalmente segun `data-theme`, porque el tema se sortea por visita y se cambia sin
recargar.

### Restricciones que NO se tocan

- **`scene-surface` se queda en `.about-card`, `.about-stats` y las dos
  `.about-track-col`.** No es decorativo: en Caelestia el fondo es un shader animado y sin
  superficie el texto cae por debajo de 3:1 / 4.5:1, medido con el arnes de contraste.
  Ocultar `[data-stats]` en Vice no afecta a los otros dos temas.
- **`data-reveal="fade-up"` se queda** en la seccion: Hyprland y Caelestia no definen
  coreografia propia y sin el atributo entrarian sin animar.
- **Los rotulos en acento usan `--color-accent-legible`**, no el accent puro (3,29:1
  medido sobre el degradado de Caelestia).

## Coreografia

### Reglas generales que salen de este trabajo

1. **Ningun trigger de entrada de Vice se ancla a `[data-scene]`.** Se ancla al primer
   nodo de contenido. 202,5px de esa caja son padding y el centrado anade un
   desplazamiento variable. (`scene5Contact` compensa hoy el mismo bug a mano con un
   `"top 68%"` empirico: merece la misma correccion, fuera del alcance de este encargo.)
2. **Cero `gsap.from`.** Los cuatro actuales (`vice.choreography.ts:433, 443, 462, 474`)
   desaparecen. `fromTo` con los dos extremos escritos a mano y `Array.from(...)` para
   colecciones vivas. Motivo doble: `from` deduce un extremo leyendo el estado de reposo
   del DOM, y este rediseno cambia ese estado de reposo.
3. **Sin fallbacks al contenedor.** Los dos actuales
   (`figures.length > 0 ? figures : stats`, `items.length > 0 ? items : track`) se borran.
4. **Timelines, no tweens sueltos.** Cuatro tweens independientes hacen que la reversa
   colapse simultanea en vez de ser el inverso del montaje: un `delay` se consume al final
   del recorrido inverso.
5. **Sin pin y sin scrub.** La escalera de `refreshPriority` queda **intacta**: hero 2,
   carril de obra 1, resto 0. `cinemaChrome` no se toca: mide contra `scene.parentElement`
   solo si es `.pin-spacer`, y about no se fija.
6. **El parallax de la ficha muere.** Se elimina `vice-about-parallax`. Con la ficha
   quieta, el `backdrop-filter` se compone una vez y se cachea.

### Timelines

Los cinco ids actuales (`vice-about-card`, `-lines`, `-stats`, `-track`, `-parallax`)
desaparecen. Quedan dos, matados defensivamente por id al montar.

**T1 — `vice-about-head`**
`trigger: '.about-head'` (la cabecera, primer nodo de contenido) · `start: "top 86%"` ·
`toggleActions: "play none none reverse"`

| pos | destino | desde | hasta | dur | ease | stagger |
|---|---|---|---|---|---|---|
| 0.00 | retrato | `scale: 0.90, opacity: 0, clipPath: "inset(0 0 20% 0)"` | `scale: 1, opacity: 1, clipPath: "inset(0 0 0% 0)"` | 0.52 | `power3.out` | — |
| 0.06 | nombre por caracteres | `yPercent: 118, opacity: 0` | `yPercent: 0, opacity: 1` | 0.72 | `power3.out` | 0.028 |
| 0.40 | chip de estado | `y: 12, opacity: 0` | `y: 0, opacity: 1` | 0.40 | `power2.out` | — |
| 0.44 | items de meta (rol/base/ahora) | `y: 10, opacity: 0` | `y: 0, opacity: 1` | 0.40 | `power2.out` | 0.05 |
| 0.56 | lead (mascara `.about-line`) | `yPercent: 105, opacity: 0` | `yPercent: 0, opacity: 1` | 0.62 | `power3.out` | — |

Fin: **1,18s**. `start: "top 86%"` deja ~126px de contenido visible al disparar, con
espacio para que el retrato (188px) entre entero antes de que el nombre termine.

**T2 — `vice-about-pairs`**
`trigger: '[data-focus-pairs]'` · `start: "top 88%"` ·
`toggleActions: "play none none reverse"`

| pos | destino | desde | hasta | dur | ease | stagger |
|---|---|---|---|---|---|---|
| 0.00 | cabecera del bloque + su hairline | `scaleX: 0` | `scaleX: 1`, origen `0% 50%` | 0.50 | `power2.inOut` | — |
| 0.14 | afirmaciones (3) | `x: -14, opacity: 0` | `x: 0, opacity: 1` | 0.42 | `power2.out` | 0.09 |
| 0.22 | conectores (3) | `scaleX: 0` | `scaleX: 0.22`, origen `0% 50%` | 0.36 | `power2.out` | 0.09 |
| 0.26 | pruebas (3) | `x: 16, opacity: 0` | `x: 0, opacity: 1` | 0.42 | `power2.out` | 0.09 |
| 0.62 | items del pie | `x: -18, opacity: 0` | `x: 0, opacity: 1` | 0.42 | `power2.out` | 0.045 |
| 0.78 | nota (mascara) | `yPercent: 105, opacity: 0` | `yPercent: 0, opacity: 1` | 0.62 | `power3.out` | — |

Fin: **1,40s**, contados desde que el bloque esta a ~108px del pliegue.

**Nota critica:** el conector entra a `scaleX: 0.22`, **no a 1**. Ese 0.22 es su estado de
reposo y el punto de partida del hover. Si el tween lo dejara en 1, el hover no tendria
recorrido y el elemento firma dejaria de existir.

**`description` no lleva tween propio.** Viaja dentro de su bloque de prueba. Un tween
propio le sumaria su `x` al del padre y entraria desde -32px mientras los demas entran
desde -16px: no rompe, pero se ve.

## Capa de hover — un solo gesto

**El vinculo se traza.** Disparado en `.pair` (`mouseenter`/`mouseleave`), aplicado en
nodos hijos que ninguna timeline anima:

| elemento | de | a | dur | ease |
|---|---|---|---|---|
| conector `.ln` | `scaleX: 0.22` | `scaleX: 1` + `box-shadow: 0 0 10px rgb(255 209 102 / .55)` | 340ms | `cubic-bezier(.25,.8,.25,1)` |
| punta `.hd` | `rotate(45deg) scale(0.3)`, `opacity: 0` | `rotate(45deg) scale(1)`, `opacity: 1` | 240ms, **delay 140ms** | `cubic-bezier(.2,1.5,.4,1)` |
| afirmacion | contorno 1px `rgb(255 244 232 / .85)`, relleno transparente | relleno `--color-accent`, contorno transparente; `translateX(3px)` | 240ms | — |
| prueba | `translateX(0)`, titular `--color-accent`, detalle `--dim` | `translateX(5px)`, los dos a `--color-paper` | 300ms | `cubic-bezier(.2,.7,.2,1)` |

Salida sin retardo y mas corta que la entrada.

**Que trabajo hace:** no es enfasis. La linea corta en reposo dice "esta afirmacion aun no
esta sostenida"; el trazado completo dice "aqui esta la prueba". Y el relleno de la
afirmacion refuerza lo mismo por otra via: pasa de contorno a macizo, de enunciado a
hecho.

### Restricciones de la capa de hover

- **Un transform inline de GSAP gana siempre a una regla CSS.** Las afirmaciones y las
  pruebas reciben `x` de T2, asi que su hover **no puede tocar `transform` en CSS** una vez
  la timeline haya escrito su inline. Implementacion: el `translateX` del hover va en un
  **hijo envoltorio**, no en el nodo que anima GSAP. El conector y la punta no participan
  en ninguna timeline de entrada mas alla de su `scaleX` inicial, y ese tween termina
  escribiendo exactamente `0.22`, que es el reposo — el hover parte de ahi.
- **About no gana ningun elemento enfocable.** No hay enlaces, ni botones, ni `tabindex`.
  La seccion sigue fuera del orden de tabulacion, igual que hoy. La capa de hover es
  **enfatica, no funcional**, asi que no arrastra obligaciones de foco visible ni de
  objetivos de 44px.
- **En tactil no se pierde informacion**, por construccion: el hover no revela ningun dato
  que no este impreso.
- **El cursor de Vice no cambia de estado en about.** La marca de sincronismo ya significa
  "aqui hay algo que hacer" en creditos y en obra; si tambien reacciona a algo que solo se
  ilumina, deja de ser fiable donde importa. Es una decision, no un olvido.

## Vida ambiental

**Una sola cosa se mueve en reposo: el punto del chip de disponibilidad** (`about-blip`,
`style.css:615-631`, 6px, 2s, ya envuelto en `@media (prefers-reduced-motion:
no-preference)`). Se conserva tal cual.

Descartado explicitamente, y conviene que conste: contadores ascendentes en las cifras
("2021" es un ano, no una cantidad), deriva o flotacion ociosa en los bloques de texto,
shimmer permanente, gradientes animados y cualquier parallax. Son las senales mas
identificables de movimiento generado, y compiten con el shader a cambio de cero carga
util. El fondo ya repinta cada frame: `fbm` de 5 octavas x 4 llamadas = ~58 millones de
evaluaciones de ruido por frame a 1440x900 con DPR 1.5.

## Estado de reposo

Es el fotograma que mas tiempo se ve y el que decide. A 1440x900, con la seccion centrada:

- Retrato 150x188 en duotono magenta/ambar, esquina viva, filete interior de 1px.
- Nombre en dos lineas: "AOSHI" macizo, "BLANCO SANZ" en contorno de 1,5px.
- Chip magenta con el punto pulsando, y `Rol · Base · Freelancer` en linea.
- Lead a 1,9rem, peso 200, topado a 22ch.
- Tres parejas: afirmacion en contorno, conector al 22%, prueba en ambar.
- Pie: Trayectoria y nota. Nada mas.
- **En movimiento: solo el punto de 6px.**

**Criterio de aceptacion:** una captura de este fotograma, mirada sin contexto, tiene que
leerse como una ficha acabada, no como una seccion a la espera de animarse. Si al quitar
el movimiento la composicion se cae, la composicion estaba mal y el movimiento la tapaba.

## Escala tipografica

Cinco escalones reales, contra los siete apinados de hoy:

| elemento | tamano | familia |
|---|---|---|
| nombre | `clamp(3.6rem, 6.4vw, 6.4rem)` | Passion One 900 |
| lead (`aboutCopy[0]`) | `clamp(1.35rem, 2.2vw, 1.9rem)` peso 200 | Manrope |
| afirmacion | `clamp(1.5rem, 2.4vw, 2.2rem)` contorno 1px | Passion One 900 |
| prueba (titular) / items del pie | 0,94-1rem peso 600 | Manrope |
| rotulos, meta, detalle | 0,62-0,82rem | Manrope |

Rotulos a `letter-spacing: .28em` (bloque) y `.14em` (meta), bajados del `.2em` actual.

## Color

Reparto **semantico**, no decorativo:

- **Ambar `#ffd166`** — lo medido y cerrado: conectores, titulares de prueba, rotulos,
  reglas.
- **Magenta `#ff2e88`** — lo que esta vivo ahora: chip de disponibilidad y su pulso.
- Fondo: dos focos radiales (magenta arriba derecha al 20%, naranja abajo izquierda al
  22%) sobre el degradado, mas una capa de grano SVG al 16% en `mix-blend-mode: overlay`.
  Es lo que hace que Vice se lea como imagen revelada y no como degradado plano.

## prefers-reduced-motion

| capa | comportamiento | como |
|---|---|---|
| entradas T1 y T2 | no existen; todo en su estado final desde el primer pintado | `initScrollReveal` hace early-return antes de importar GSAP, asi que los `fromTo` nunca se crean y nunca se escribe el extremo inicial. Cero codigo |
| **conector** | **dibujado al 22%**, su reposo normal | idem |
| hover | **se conserva, instantaneo** | `@media (prefers-reduced-motion: reduce)` propia, con `transition-duration: .01ms` y sin las traslaciones. Obligatoria: `initScrollReveal` no cubre nada de CSS |
| `about-blip` | sin cambios | ya envuelto en su propia query |

Regla general que sale de aqui: **el movimiento que debe morir con `reduce` va en GSAP; el
que debe sobrevivir va en CSS con su propia media query.**

Reducir movimiento no es quitar la respuesta: el hover conserva sus cambios de color.

## Presupuesto de altura

900 − 405 (202,5 x 2 de padding de tema) = **495px utiles** a 1440x900.

| bloque | alto |
|---|---|
| cabecera (retrato 188 manda) | 188 |
| lead | 46 |
| cabecera del bloque de parejas | 34 |
| 3 parejas (~72 cada una, la primera ~96 por el `description`) | 240 |
| pie | 120 |
| separaciones | 60 |
| **total** | **~688** |

**No cabe en 495.** Decision explicita: **about es escena de dos pantallas en desktop**, y
se compone como tal. Se toma a proposito, no por accidente. El `padding` de 202,5px **no
se toca**: arregla un solape medido de 7,5px entre `.hero-kick` y la barra `.rail` a
1440x600 y esta razonado en 20 lineas de comentario.

Recorte disponible si se quisiera apretar: `.hero-kick` "Quien es" pasa a la fila de
`eyebrow` de la cabecera (ya esta asi en el diseno) y libera los ~86px que hoy ocupa como
titulo suelto mas el margen de la rejilla.

## Verificacion

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"   # Node del sistema es 18; Vite 8 exige >=20
npm run build     # tsc + vite build, cero errores
npm run lint
python3 scripts/verify.py
npm run dev       # http://localhost:5173/?theme=vice
```

- **Screenshot desktop 1440x900 y movil 390x844**, siempre con `?theme=vice` (el tema se
  sortea por visita).
- **Verificar los tres temas**, no solo Vice: el cambio toca DOM compartido.
- `scripts/verify.py` deja **12 fallos preexistentes** (9 rellenos de galeria en
  `public/media/obra/`, 3 ficheros `public/media/vice-*`). Cualquier fallo distinto de
  esos 12 es nuevo.
- **Re-correr `check_contrast_wcag`**: la seccion cambia pesos de texto y superficies.
- **Comprobar que T2 dispara donde debe**: `[data-focus-pairs]` no puede acabar en
  `display: contents` en ningun breakpoint. Un elemento sin caja devuelve un rect a cero y
  ScrollTrigger lo mide en `top = 0` del documento: el trigger dispararia nada mas cargar,
  sin error ni warning.
- **Verificar en el build de produccion**, no en dev, cualquier fallo de layout o de
  ScrollTrigger: el HMR de Vite corrompe sus medidas.
- Para medir ritmo, muestrear `tl.progress()` desde dentro de la pagina:
  `page.screenshot()` en headless perturba GSAP.
- Gate final: `lidia-naive-tester` (flujo) y `vera-art-director` (ejecucion visual).

## Decisiones abiertas

Ninguna bloquea la implementacion.

1. **La tercera pareja** usa `identity.role` como afirmacion y la carrera como prueba.
   Reagrupa dos datos existentes sin inventar nada. Alternativa viva: quedarse en dos
   parejas, o que el usuario escriba un tercer `focusArea` real.
2. **El chip de disponibilidad como enlace a contacto** queda levantado y **no resuelto**.
   Seria util para una reclutadora, pero mete la seccion en el orden de tabulacion por
   primera vez, exige 44px de objetivo (hoy el chip mide ~11px de alto) y crea un segundo
   CTA a mitad de pagina que compite con el de contacto. Es decision de producto.

## Implementacion

- **En worktree aparte.** `design/creditos-cartel` tiene 8 ficheros modificados sin
  commitear de otra sesion; no se construye encima de un arbol sucio ajeno.
- Modelo: el trabajo es mecanico (CSS, reestructura acotada de `about.ts`, reescritura de
  `scene2Card` con la coreografia ya dimensionada arriba). **Baja a Sonnet.**
- Ficheros afectados: `src/sections/about.ts`, `src/style.css`, `src/themes/themes.css`,
  `src/themes/vice.choreography.ts` (384-484), `src/data/content.ts` (`education`).

## Estilo

TypeScript strict, cero `any`, cero emojis. Comentarios en espanol **sin tildes**, densos,
que expliquen POR QUE y no QUE, y que incluyan la medicion que motivo la decision.

---

## Registro de implementacion

Anadido despues de implementar y de pasar el gate de QA. **Lo de arriba es el spec tal
como se aprobo; lo de aqui es en que se desvio la realidad y por que.** Si los dos se
contradicen, manda esta seccion.

Implementado en `design/about-afirmacion-prueba` (worktree aparte, como pedia el spec).
Gate: `lidia-naive-tester` 7,4 ("Algo Claro", contactaria con reservas) y
`vera-art-director` 6,65 sobre un umbral de 7,5 (BLOCK). Los hallazgos que bloqueaban se
arreglaron y se re-midieron; el gate NO se ha vuelto a pasar sobre la version corregida.

### Desviaciones respecto del spec

| punto del spec | lo que se hizo | por que |
|---|---|---|
| `education[0]` vive en la prueba 3 **y** en el pie | se oculta del pie (`data-item="education"`) | montada la escena, el grado y la universidad se leian dos veces en el mismo encuadre, a 300px. Era el defecto #7 del diagnostico reapareciendo — el spec se contradecia a si mismo |
| rotulo "En que me enfoco" se conserva | pasa a "Que hago · con que lo respaldo" | el naive test: no describia lo que encabeza, sonaba heredado |
| nota "Cada afirmacion, con lo que la sostiene" bajo el rotulo | **eliminada** | era el texto menos legible de la seccion (10,88px, peso 300, opacidad 0,55; no se leia en movil). El rotulo nuevo hace su trabajo |
| prueba 2 = `focusAreas[1].detail` | cifra + stack real (`skillGroups`) | `detail` parafraseaba su propio titulo: no probaba, repetia. El stack aporta un hecho nuevo y ademas es el dato por el que filtra una reclutadora |
| el tween del conector acaba en `scaleX: 0.22` | el tween lleva el ENVOLTORIO a 1 y el CSS mantiene el hijo en 0.22 | un transform inline de GSAP gana siempre a una regla CSS. Con los dos en el mismo nodo, el hover se quedaba sin recorrido. Los dos `scaleX` se multiplican, asi que lo visible sigue siendo el 22% |
| la ficha conserva superficie y el blur se cachea | pierde borde, fondo y `backdrop-filter` | es un encabezado, no una tarjeta. Muerto el parallax, no hay nada que difuminar |
| grano SVG al 16% en `mix-blend-mode: overlay` | **eliminado** | medido: desviacion tipica 0,77 y 1,14 sobre 255 (0,4% de modulacion). `overlay` sobre luminancia del 8% es casi la identidad. Costaba una capa compuesta a pantalla completa que fuerza stacking context sobre el canvas WebGL |
| movil: afirmacion en Pathway Gothic 1,15rem | 1,5rem, y el titular de la prueba pasa a paper | a 1,15rem contra un titular ambar, el ambar ganaba: la prueba se leia antes que la afirmacion y la tesis de la seccion quedaba invertida en el viewport mayoritario |
| hover: prueba y titular pasan los dos a `--color-paper` | el titular conserva el ambar; solo sube el detalle | la fila enfocada era la unica NO dorada entre dos vecinas doradas. Enfocar la hacia retroceder |
| sin tope de medida (escena a sangre) | `max-width: 1180px` en `.about-grid` | 596px vacios a 1440 (44% del ancho util) y 1206px a 1920 (65%), con la mitad superior en medida corta y la inferior a sangre. Decision del usuario entre tres opciones |
| altura estimada ~688px | **1210px medidos** | la estimacion se quedo corta en un 76%. Sigue siendo escena de dos pantallas, que era la decision; pero el presupuesto de altura del spec no sirve como referencia |

### Anadidos que el spec no contemplaba

Salieron del gate de QA y ninguno estaba previsto:

1. **La afirmacion se alinea a la derecha desde 860px.** Es el arreglo del unico P0. El
   spec cuidaba la longitud del conector (0.22) y el problema era su ORIGEN: con la
   afirmacion en bandera izquierda habia 279, 192 y 180px de su ultima letra al munon, y
   solo 80px constantes del munon a la prueba. Opticamente el conector pertenecia a la
   prueba y la direccion de la relacion quedaba invertida justo en el estado que mas
   tiempo se ve. Alineada a la derecha: 16px en las tres y eje vertical comun.
2. **`align-items: baseline` en la pareja, no `center`.** Centrar centraba el BLOQUE de la
   prueba, no su primera linea, asi que el conector apuntaba a la descripcion con un
   desfase que variaba con el numero de lineas (15/11/11px medidos). Con linea de base, 1px
   y deja de depender del contenido.
3. **Contorno en `em` (0.028em)**, no en px. Como fraccion del em iba del 1,63% al 4,17%
   segun el breakpoint: un rango de 2,6x para un motivo declarado UNICO, y se veia.
4. **Seis escalones tipograficos de verdad.** El spec declaraba cinco y salieron diez,
   porque estaban escritos como decimales rem inventados uno a uno. Fuera 15,04 / 12,48 /
   10,88, que estaban a menos del 3% de su vecino.
5. **Columna del conector a 88px desde 860**, no desde 1024: quedaba una banda de 164px de
   viewports con el munon a 14,08px, que es el defecto que el comentario del codigo decia
   haber arreglado.
6. **Movil:** el trazo acaba EN la prueba y el rombo aterriza sobre su titulo (desfase 0
   medido) en vez de colgar al final de la descripcion apuntando a nada; y la nota va
   despues de "Trayectoria" (`order`), con zona de seguridad para el sello de tema, con el
   que solapaba 2,7px.
7. **Cabecera apilada por debajo de 640px.** Con el retrato al lado, el nombre se quedaba
   con 230px y "BLANCO SANZ" a 2,5rem mide 245: se salia.
8. **Duotono con particion casi neta** (25% / 62%). Con las paradas en los extremos, el
   centro de la cara caia en hue 11 sat 0,73 —el naranja turbio de la mezcla— justo donde
   va el ojo.
9. **`<img>` declara 150x188**, no 50x50: se pintaba a 188px y el layout saltaba al cargar.

### Bugs propios cazados verificando, no leyendo

Los tres se vieron en captura o en medida, ninguno leyendo el codigo:

- `.about-head-main` se quedaba en el `display: contents` de la regla base, asi que sus
  tres hijos se convertian en celdas de la rejilla de la cabecera: el chip y la fila de
  meta caian en la **columna del retrato**.
- El tope de 96px del retrato y su override de 640px tenian la misma especificidad, asi
  que ganaba el ultimo del fichero y el retrato media 96px tambien a 1440. Reatado a
  `max-width: 639px` para que el orden deje de importar.
- Una comprobacion ad-hoc con `window.scrollTo` dio por reales dos fallos de cromo que no
  existian. Con rueda simulada pasan. **Nunca medir scroll en este repo sin replicar
  `_scroll_to_and_settle()`.**

### Efecto colateral en el arnes

Al crecer about, el documento paso de ~12000 a 12414px y dos aserciones de cromo empezaron
a fallar. No era una regresion: la muestra al 45% usaba `scrollTo` crudo mas 1200ms fijos
justo despues de una tanda de rueda simulada — la desincronizacion de Lenis que documenta
el docstring de `_scroll_to_and_settle`. Latente desde antes; solo hacia falta un documento
algo mas largo para cruzar el limite. Corregido en `scripts/verify.py` (commit aparte).

### Decisiones abiertas, al cierre

1. ~~La tercera pareja~~ — **resuelta**: se queda con `identity.role` como afirmacion y la
   carrera como prueba. Es la unica reaparicion aceptada del plano.
2. **El chip de disponibilidad como enlace a contacto** — sigue abierta, sin resolver. Es
   decision de producto.
3. **NUEVA: `.about-pair` no es enfocable**, asi que el elemento firma de la seccion no
   existe para teclado ni para tactil. Lo marcaron los DOS criticos. El spec lo decidio a
   proposito (el hover no revela ningun dato que no este impreso, y la auditoria confirma
   que no es violacion WCAG), pero conviene saber que para una parte grande del publico el
   conector es solo una raya. Reconsiderarlo va junto con la decision 2: las dos meten la
   seccion en el orden de tabulacion por primera vez.
4. **NUEVA, fuera del alcance de este encargo:** el sitio no tiene navegacion ni un solo
   enlace en "Quien es", y hay ~8600px de scroll hasta el `mailto:`. Es el hallazgo que el
   naive test puso por encima de todo: "me convenciste y no me dejaste actuar". No es un
   defecto de esta seccion, pero se resuelve o no se resuelve fuera de ella.
