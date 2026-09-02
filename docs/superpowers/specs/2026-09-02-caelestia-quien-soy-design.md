# Spec de Caelestia — Quién soy: la ficha del sistema es la salida de `neofetch`

Estado: pendiente de plan
Fecha: 2026-09-02
Alcance: la **fase B2** de las seis del rediseño de Caelestia — la escena `#about` dentro del
workspace. Toca `src/sections/about.ts` (un bloque aditivo nuevo), el bloque
`:root[data-theme="caelestia"]` de `src/themes/themes.css` y un gesto nuevo en
`src/themes/caelestia.choreography.ts`.

**Vice no se toca** (cerrado el 2026-08-05). **Hyprland no se toca.** `shaderBackground.ts` es
compartido y no se modifica. La fase A (el shell) está cerrada y **tampoco se toca**: esta fase vive
dentro de la ventana. **El fondo es de B1 y B2 lo hereda sin tocarlo** — ver `## El fondo`.

---

## Por qué

Medido sobre el build de producción, en la ventana de **1412 × 748** que impone el carril de
workspaces:

| | antes | después |
|---|---|---|
| alto del contenido | 475 px | **637 px** |
| aire sin usar arriba / abajo | **152 / 121** | **55 / 56** |
| líneas del nombre | **3** («Aoshi / Blanco / Sanz») | **1** |
| líneas de «Disponible para proyectos» | **2** | 1 |
| desborde de la ventana | ninguno | ninguno |

El defecto no era que no cupiera: es que la maquetación repartía todo el sobrante en dos bandas
muertas a los cantos mientras estrangulaba la columna de la ficha a **129 px útiles** dentro de una
tarjeta de 235. Es la misma maquetación de una página que se desplaza, puesta en una ventana
apaisada que no se desplaza.

> El spec de B1 registraba 443 / 189 / 116 para esta escena. La medida de esta sesión da
> **475 / 152 / 121**: mismo diagnóstico, número distinto porque aquella se tomó antes de que las
> fuentes variables terminaran de asentar. Los 475 son los buenos.

---

## La decisión de partida: cada escena es una aplicación

Viene dada de la fase A y no se reabre. El workspace no contiene una sección: contiene un programa.
Título es el escritorio desnudo, Obra será un gestor de archivos, Créditos un gestor de paquetes,
Fundido un compositor de mensaje.

**Quién soy es la salida de `neofetch`** — el comando que un escritorio de Linux ejecuta para decir
qué máquina es esta. B1 abre con `whoami`, que pregunta *quién eres*; `neofetch` pregunta *qué
máquina eres*. Es la continuación del mismo chiste, no su repetición.

**Se descartaron dos composiciones, ambas construidas y comparadas en vivo dentro del sitio real:**

- **A · ficha y especificaciones** (retrato y nombre en un panel de 480 px a la izquierda,
  especificaciones clave/valor a la derecha). Era la que mejor usaba la ventana —aire 68 / 68— y la
  que menos riesgo tenía. Se descarta porque no jerarquiza: rol, base, ahora y estudios pesan lo
  mismo, y el gate de este proyecto es una reclutadora no técnica decidiendo en dos segundos.
- **B · «Acerca de este equipo»** (diálogo centrado, retrato grande, nombre a tamaño de cartel y
  cuatro celdas debajo). Llegó a estar bien resuelta —panel real con superficie y contorno, insignia
  de estado a caballo del canto superior— pero conserva la forma del defecto que B2 viene a quitar:
  aire 136 / 153.

La crítica de UX del proyecto recomendaba **B** y descartaba `neofetch` por su audiencia: leer
jerarquía en una salida de terminal exige conocer la convención. **Ese argumento se acepta como
diagnóstico y se resuelve por diseño, no por descarte** — ver la sección siguiente.

---

## La desviación: el nombre no va en monoespaciada

Es la pieza que hace propia esta salida y la que responde a la objeción de UX.

El nombre ocupa el sitio donde `neofetch` imprime el título de la distribución, y es **lo único que
no va en monoespaciada**: Fraunces con `--cae-display-axes-cartel` (`opsz 144 · wght 900 · SOFT 0 ·
WONK 1`), 3,35 rem, `white-space: nowrap`. Un registro de terminal con una sola línea de serif a
tamaño de cartel.

Con eso la escena tiene un primero indiscutible, que es exactamente lo que la convención de terminal
—donde todas las líneas pesan igual— no da por sí sola.

**El token no es nuevo:** `--cae-display-axes-cartel` lo introduce B1. Los ejes del shell
(`--cae-display-axes`, `opsz 9`) no se tocan: ahí el texto se lee a 15–30 px y necesita el dibujo de
texto. Es la lección de B1: **`opsz` se elige por el tamaño al que se lee.**

**La fila «Nombre» desaparece.** Con el nombre a tamaño de cartel, una fila que lo repita dice dos
veces lo mismo.

---

## La composición

```
~ $ neofetch▌

   ┌──────────┐        Aoshi Blanco Sanz              <- Fraunces, opsz 144
   │          │        aoshi@caelestia │ ● Disponible para proyectos
   │  retrato │        ─────────────────                <- del largo exacto del host
   │ squircle │        Llevo datos reales a interfaces que la gente usa todos los días.
   │          │
   └──────────┘        Rol            Desarrollador Full Stack
                       Base           Caracas, Venezuela
                       Ahora          Freelancer
                                      Desde 2021
                       Enfoque        Datos a gran escala · Interfaces que aguantan
                                      Que la consulta siga siendo rápida con volumen real
                                      Estado complejo sin romperse en producción
                       Último puesto  Pasante B2C Conocimiento al Cliente · Telefónica Venezuela
                                      Ago 2025 — May 2026
                       Estudia        Ingeniería de Sistemas
                                      Universidad Santa María · 2021 — presente (10.º semestre)

                       ■ ■ ■ ■ ■ ■ ■ ■ ■                 <- los tokens de la hora

~ $ ▌
```

Dos columnas, `312px 1fr`, separadas 4,25 rem, centradas verticalmente, con la caja limitada a
1180 px de ancho dentro de la ventana de 1412.

### El orden de los campos

**Rol · Base · Ahora · Enfoque · Último puesto · Estudia.** Es el orden de quien lee un perfil: la
experiencia antes que los estudios, y el enfoque justo detrás de la identidad porque es lo que
diferencia. No es el orden en el que los campos viven en `content.ts`.

### La frase

`aboutCopy[0]` —«Llevo datos reales a interfaces que la gente usa todos los días.»— va bajo el
filete, en **Hanken Grotesk**, y es lo único en la fuente de texto. Entre el nombre en Fraunces y los
campos en monoespaciada, marca que **esto lo dice una persona y no el sistema**. Sin ella la escena
solo enumeraba datos.

### El filete se mide, no se estima

`neofetch` imprime el subrayado del **largo exacto** de `usuario@host`. Aquí igual: se mide con
`document.createRange()` + `selectNodeContents()` sobre el texto y la entrada hace crecer el filete
hasta ese número. Medido: **filete 170 px, texto 170 px**.

**Nunca con la caja del elemento**: un `<p>` de bloque devuelve el ancho de la columna, no el del
texto. Es la trampa que B1 ya pagó con su justificación.

### El prompt vuelve

Al terminar la salida, la terminal **devuelve el prompt**: un `~ $ ▌` latiendo abajo a la izquierda.
No es relleno — es lo que hace una terminal de verdad, y cierra la escena por abajo. Con él, el aire
pasa de 83 / 82 a **55 / 56**.

---

## El retrato

Es **el logotipo de la distribución**: ocupa el sitio donde `neofetch` pone el logo. 288 px,
recortado con un **squircle** — la superelipse |x|⁴ + |y|⁴ = 1, la forma de icono de Material 3.

Se descartaron, ambas conmutables en la maqueta: el **círculo** (correcto y mudo: no dice Material 3
ni dice escritorio) y el **festón de 12 lóbulos** en reposo (su lóbulo cóncavo muerde la silueta de
la cara y se lee como recorte mal hecho).

### El roce del retrato: morfa

Caelestia se define a sí misma como **«a fluid, morphing shell»** y su configuración expone un
parámetro `deformScale`. Morfar es su identidad, así que al rozar el retrato **la figura se convierte
en otra figura con nombre de Material 3** —squircle → «12-sided cookie»— en **0,62 s**,
`cubic-bezier(0.34, 0.02, 0.16, 1)`. El festón, que en reposo se leía como recorte roto, en
movimiento se lee como lo que es.

El anillo de azufre de 6 px **sigue la figura** durante todo el recorrido: es un envoltorio con el
mismo `clip-path`, porque **un `outline` no obedece a un `clip-path`**.

**Las cuatro figuras se generan con el mismo número de puntos (240).** Un `polygon()` solo interpola
con otro si cuentan igual; con distinto número el navegador no morfa, **corta**. Los polígonos y su
generador quedan en `2026-09-02-caelestia-quien-soy-figuras.py`.

| figura | fórmula | n | a | s |
|---|---|---|---|---|
| círculo | superelipse | pot 2 | — | — |
| squircle | superelipse | pot 4 | — | — |
| 12-sided cookie | r(θ) = 1 + a·cos(nθ) + s·cos(2nθ) | 12 | −0.058 | 0.012 |
| 4-leaf clover | ídem | 4 | 0.265 | −0.045 |

---

## La insignia de disponibilidad

Sube a la **línea de identidad**, junto a `aoshi@caelestia`, separada por un filete de un píxel: deja
de ser la última fila del listado y pasa a ser lo segundo que se lee después del nombre. **Lo que la
hace segunda parada es el sitio, no el color.**

**Se dice como lo dice el sistema**: punto de azufre y texto en `on-surface-variant`, exactamente lo
que hacen `.cae-avail` y `.cae-dot` en la barra del shell. Una pastilla rellena —que es lo que tuvo
en una versión intermedia— es un dialecto distinto para la misma frase, y además le peleaba el primer
plano al nombre.

Va en el **ancla (azufre)**, el único color del tema que no gira con la hora: una señal de estado
tiene que decir lo mismo a las 09:00 y a las 03:00.

El punto **respira** con periodo de 2,4 s, solo en opacidad (1 → 0.45 → 1). Una versión intermedia
llevaba además un halo (`box-shadow`) y era lo que la hacía parecer adorno.

---

## La entrada: se teclea el comando

Con el shell ya montado —barra, dock y ventana— lo único que se anima es la salida.

| t (s) | qué pasa | propiedades | duración · easing |
|---|---|---|---|
| 0,00 | el cursor espera, parpadeando dos veces | `opacity` | 0,085 s ×4, lineal |
| 0,34 | se teclea `neofetch`, 8 caracteres | texto por caracteres | 0,44 s, lineal |
| 0,78 | Enter | `opacity` 1 → 0,2 → 1 | 0,04 s, `power1.inOut` |
| 0,86 | entra el retrato, el logotipo de la distro | `opacity` 0 → 1, `scale` 1,06 → 1 | 0,55 s, `power2.out` |
| 1,05 | **el nombre se descubre de izquierda a derecha** | `clip-path: inset(0 100% 0 0)` → `inset(0 0% 0 0)` | 0,72 s, `power2.inOut` |
| 1,45 | `aoshi@caelestia` | `opacity`, `x` −6 → 0 | 0,28 s, `power2.out` |
| 1,60 | el filete crece hasta el largo del host | `width` 0 → 170 px | 0,42 s, `power2.inOut` |
| 1,85 | los campos, uno a uno, como una salida que se imprime | `opacity`, `x` −6 → 0 | 0,22 s c/u, escalonados 70 ms |
| 2,45 | la tira de color cierra, como en el `neofetch` de verdad | `opacity`, `scaleX` 0,2 → 1 | 0,18 s c/u, escalonados 35 ms |
| fin | **el prompt vuelve y late** | `opacity`, `repeat: -1`, `yoyo` | 0,55 s |

Total: **≈2,6 s**. El barrido del nombre es **el mismo gesto que el titular de B1** (barrido de
tinta): es lo que ata las dos escenas.

**Nunca `gsap.from`**: los dos extremos van escritos a mano en cada paso.

Se descartaron, del catálogo que produjo el especialista de animación: `uname -a` (una sola línea de
texto técnico, sin sitio para el retrato), la ficha que se rellena campo a campo sin terminal (válida
para cualquier tema; el escritorio no aparece), ASCII-art generado del retrato (frágil y caro de
mantener), y el retrato entrando en bloque con todos los campos a la vez (se lee como carga de
página, no como un comando que imprime).

---

## El roce dentro de la ficha

La micro-interacción del tema es **N4, «el fondo se aparta»**, y no se toca. Lo de aquí es lo que
N4 no cubre, y va en **capa local rápida (0,12–0,22 s)** frente a la capa ambiente de N4
(0,7–0,8 s), para que no compitan por la misma atención.

- **Las filas.** La clave vira a azufre en 0,14 s y aparece un `>` delante que **entra deslizando
  5 px** (0,18 s, `cubic-bezier(.2,0,0,1)`) — el prompt marcando la línea que miras. El fondo de la
  fila se tiñe con `surface`. **El valor no se mueve**: lo que responde es la pregunta, no el dato.
- **La tira de color.** El tono se estira (`scaleY` 1,7, origen abajo) y **dice su token y su
  `oklch()` real a esa hora** — p. ej. `--cae-anchor oklch(0.855 0.152 96.0)`. **En reposo no lleva
  rótulo**: los tonos se ven y ya; explicarse en reposo era ruido.
- **La insignia.** El texto sube de `on-surface-variant` a `on-surface`.
- **El retrato.** El morfado descrito arriba.

**Todo el roce va en CSS, no en GSAP.** La entrada escribe transformaciones en línea sobre los
envoltorios `[data-g]`, y **un transform en línea de GSAP gana siempre a una regla CSS**: un hover
sobre el mismo nodo no se vería. Los objetivos del roce son hijos de esos envoltorios, nunca los
envoltorios.

---

## El contenido: leído, no copiado

Todo texto visible sale de `src/data/content.ts`: `identity.name`, `identity.role`,
`identity.location`, `identity.now`, `identity.availability`, `identity.githubAvatar`,
`aboutCopy[0]`, `education[0]`, `experience[0]` y los dos `focusAreas`.

**`Desde 2021` se lee de `stats` por su rótulo, no por su índice** — la misma precaución que ya toma
`statValue()` en `about.ts`, para que reordenar el array mañana no rompa esto en silencio.

**El resto de las cifras de `stats` no se repite aquí.** B1 ya las usa como colofón de su cartel, y
verlas otra vez al cambiar de workspace se lee como un fallo antes que como un refuerzo. La única que
sobrevive es el semestre, y **enterrada dentro del período de estudios**, que es donde ya vive en
`content.ts` (`education[0].period`) y donde aporta un hecho nuevo en vez de repetir una cifra.

En la maqueta esto se cumple **por construcción**: no hay ni una cadena escrita a mano — el contenido
se lee del DOM que el sitio ya pintó, antes de sustituirlo. En la implementación, la regla es la de
siempre: si no está en `content.ts`, no se pinta.

---

## El fondo: B2 no lo toca

Está especificado en B1 (figuras con nombre de Material 3, tres en diagonal más cuatro satélites,
morfando por tramos de la hora) y **B2 lo hereda sin tocarlo**.

Medido en esta escena: la ventana ocupa el **81,5 %** del viewport, la barra y el dock otro **6,1 %**,
y **queda un 12,4 % de fondo a la vista** — 14 px de margen lateral y las dos bandas. Por bueno que
sea el fondo, **aquí apenas asoma**, y el vacío que se percibe está **dentro** de la ventana, no
detrás. Se arregla con el prompt de vuelta, no con el fondo.

Queda anotado, porque se preguntó y se midió: **si la ventana llegara a parecer demasiado dominante,
la palanca no es el fondo sino el tamaño de la ventana**, y eso es fase A, cerrada. Sería otra
conversación, no un parche en B2.

---

## Color y contraste

El contraste **no depende de esta composición**: depende de la paleta, y la paleta es invariante al
matiz por construcción desde la fase A —la claridad de cada rol no se mueve con la hora, así que se
mide una vez y vale para las 1.440 posiciones del reloj.

Los pares que esta escena pinta de verdad, y que por tanto hay que vigilar:

| par | dónde |
|---|---|
| `on-surface` sobre `surface-container` | el nombre, los valores de las filas, la frase |
| `on-surface-variant` sobre `surface-container` | las claves, los detalles, la insignia |
| `primary` sobre `surface-container` | `aoshi@caelestia` y el `~ $` del prompt |
| `anchor` sobre `surface-container` | el punto de la insignia y el `>` del roce |
| `on-surface` sobre `surface` | las filas al roce, que cambian de fondo |

**Vigilar los roles que se pintan, no los teóricos.** Es la lección de la fase A: unos `PARES` que
miraban `on-X`/`X` dejaron al reloj de la barra por debajo de AA cuatro horas al día con el arnés en
verde.

---

## Los gates

El arnés nuevo, `scripts/measure-caelestia-quien-soy.py`, tiene que comprobar al menos:

1. **Cabe.** Alto del contenido y **aire bajo el pie ≥ 0**. Este gate ya cazó dos desbordamientos de
   138 y 142 px en B1.
2. **El nombre no parte.** Una aserción sobre el número de líneas de caja del nombre. Es el defecto
   concreto de esta escena — **hay que verlo dar rojo contra el estado actual (3 líneas) antes de
   fiarse de que da verde**.
3. **El filete mide el largo del host.** `Range` sobre el texto contra el ancho del filete, ±2 px. Si
   se mide con la caja del elemento, da el ancho de la columna y el gate miente.
4. **El morfado interpola.** Muestrear `getComputedStyle(img).clipPath` cuadro a cuadro durante el
   roce: **≥ 4 estados distintos**. Medido: 9 con transición, **2 sin ella** (solo los extremos).
   El umbral es 4 y no 9 a propósito — un umbral pegado a la medida mide la carga de la máquina, no
   el diseño.
5. **Contraste** de los cinco pares de arriba contra el fondo real, barriendo las 24 h, ≥ 4.5:1.
6. **Movimiento reducido.** Con `reduced_motion="reduce"`: escena montada, comando ya escrito, filete
   ya a su ancho, nombre sin recorte, `animation-name: none` en el punto de la insignia.
7. **Anti-mock.** Todo texto visible existe en `content.ts`.
8. **Los ejes del shell no se han movido.** La marca de la barra sigue en `opsz 9`; solo el nombre
   usa `opsz 144`.

**Ningún gate se da por bueno sin haberlo visto dar rojo contra el fallo que dice cazar.** El del
morfado ya se vio en rojo: anulando la transición baja de 9 estados a 2.

---

## Cómo entra en el código

Recomendación del arquitecto del proyecto, aceptada:

- **Bloque aditivo oculto**, la tercera instancia del patrón que ya usan `createPairs()` (Vice) y
  `createPlaca()` (Hyprland) — **no** re-estilar el DOM actual con CSS. El tema se sortea por visita
  y se cambia sin recargar, así que el DOM **no puede construirse según `data-theme`**.
- Coste medido y aceptado: la sección `about` pasa de **≈128 a ≈162 nodos**, un 27 % más. Es
  admisible con tres dispositivos; si apareciera un cuarto, tocaría consolidar en un
  `createSceneDevice()` genérico.
- Ganchos por `data-*`, como el resto del proyecto: `data-ficha="neofetch"` en la raíz,
  `data-ficha-retrato`, `data-ficha-nombre`, `data-ficha-regla`, `data-ficha-fila`,
  `data-ficha-tira`, `data-ficha-prompt`.
- El CSS vive en `themes.css`, bajo `:root[data-theme="caelestia"]`, en el hueco entre las reglas de
  escena y las del shell — **hoy no existe ni una regla `.about-*` específica de Caelestia**. Y hace
  falta la regla gemela que oculte `.about-card` / `.about-stats` / `.about-track` / `.about-pairs`
  bajo Caelestia, calcada de la que ya hace lo mismo para Hyprland.

Riesgos de regresión que la implementación tiene que comprobar: que Vice e Hyprland siguen intactos
(**captura de los tres temas, no solo build verde** — `tsc` y `eslint` no cazan un selector mal
cerrado), y que el bloque nuevo hereda el `inert` del workspace inactivo.

---

## Lo que queda fuera

- Las escenas **Obra, Créditos y Fundido** (fases B3–B5).
- **El fondo**, que es de B1.
- **Móvil.** Todo lo medido aquí es a 1412 × 748. El carril de workspaces en pantalla estrecha sigue
  siendo una decisión abierta desde la fase A.
- **Las nueve capturas de `public/media/obra/`**, que bloquean B3, no esta fase.

---

## Maquetas

La maqueta viva, con su generador de figuras, queda rescatada al repo porque `.superpowers/` está en
`.gitignore`:

| fichero | qué es |
|---|---|
| `2026-09-02-caelestia-quien-soy-maqueta.html` | el banco: monta la escena **dentro del sitio real** (marco al build de producción), con la entrada, el roce, el conmutador de forma del retrato, el reloj forzado y las lecturas en vivo |
| `2026-09-02-caelestia-quien-soy-figuras.py` | genera los cuatro `polygon()` a 240 puntos y **falla el build** si el literal de CSS lleva una comilla invertida o si las figuras dejan de tener el mismo número de puntos |
| `2026-09-02-caelestia-quien-soy-final.png` | la escena aprobada, en la ventana real |

Para levantarlo: `npm run build && npx vite preview --port 4273` en un worktree, copiar la maqueta a
`dist/` con el generador, y abrir `/b2.html`.

---

## Registro de implementación

Lo que costó, para que no se repita:

- **Una comilla invertida dentro del literal de CSS cierra la plantilla y rompe el script entero.**
  Pasó **dos veces** en una sola sesión (`outline`, `deformScale` escritos entre comillas invertidas
  dentro de un comentario). El síntoma es mudo: la escena se queda con su maquetación vieja y no hay
  nada en pantalla que lo diga — solo el `pageerror` de la consola. Ahora lo comprueba el generador.
- **La ventana no se busca por posición.** Medir contra «la ventana que está en x = 14» daba los
  números de otra escena durante la transición del carril: las tres composiciones devolvían
  443 / 121 / 184, que son los de la escena vieja. La ventana es **la que contiene la escena**
  (`closest()`), que es exacto por construcción. Y dentro de un marco aterriza en **x = 0**, no en los
  14 px de margen de una pestaña normal.
- **Un reintento que se pisa a sí mismo no reintenta.** Reclicar la pastilla del workspace cada
  250 ms reiniciaba la tween del carril en bucle y la ventana no llegaba nunca a su sitio. Un clic
  cada 2 s, y comprobando el rect real, no el `aria-current`.
- **Las capturas no sirven para medir movimiento.** `page.screenshot()` bloquea el compositor y la
  transición salta hacia delante: un fotograma a 220 ms del morfado salía ya terminado. El morfado se
  mide leyendo `getComputedStyle().clipPath` cuadro a cuadro. Y **un `MouseEvent` sintético no
  dispara `:hover`** — hace falta el ratón de verdad de Playwright.
- **La captura y sus coordenadas tienen que salir de la misma pasada.** Medir en una ejecución y
  recortar en otra dejó las anotaciones del diagnóstico **40 px desplazadas** sobre la imagen.
- **Cada maqueta se mira antes de enseñarla.** La primera versión de esta fase reconstruía el shell a
  mano con colores aproximados y una hora inventada; se rechazó entera. La solución no fue afinar la
  imitación: fue **montar la escena dentro del sitio real** y dejar que el shell, el fondo y el motor
  de color fueran los de verdad.
