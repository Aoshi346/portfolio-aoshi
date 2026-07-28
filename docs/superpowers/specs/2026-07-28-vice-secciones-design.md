# Vice City — remodelación de cuatro secciones

Fecha: 2026-07-28 · Estado: aprobado, pendiente de plan de implementación
Rama base: `main` (`7cbb60f`)

Spec anterior: `docs/superpowers/specs/2026-07-24-vice-city-design.md`
Bitácora del rediseño anterior: `docs/superpowers/notes/2026-07-28-vice-city-bitacora.md`

## Contexto

El tema Vice City está construido y mergeado. Esta sesión no lo rehace: corrige cuatro
defectos concretos que el usuario detectó mirando el sitio, y actualiza el contenido de
"Quién es", que se había quedado desfasado.

Los cuatro defectos, con su causa:

1. **El nombre del hero se lee dentro de un cuadro borroso.** No es un artefacto: es
   `.hero-surface` en Vice (`themes.css:72`), un panel de `--color-ink` al 88% con
   `blur(10px)`. Está a esa opacidad **por culpa del vídeo de barras de test** que sirve
   hoy `public/media/vice-hero.*`: contra franjas SMPTE puras hizo falta el 88% para que
   el gate de contraste midiera algo. Con el vídeo real bastará mucho menos.
2. **El acompañamiento del hero desaparece de golpe al scrollear.** Sí hay tween, pero los
   tres bloques `[data-hero-fade]` salen a la vez en el primer 28% del recorrido
   (`vice.choreography.ts:95`), y el zoom arranca en 0.12, casi solapado.
3. **"Quién es" no llena la pantalla** — el contenido termina a los ~620px de 900 — y su
   motion son tres `fade+slide` genéricos.
4. **La obra deja vacío el 35% derecho** (solo la marca de agua del ordinal) y no reacciona
   al cursor. **Los créditos** dejan vacía la mitad inferior derecha: la lista va en una
   columna estrecha y el detalle se esconde en un panel pequeño.

La sección de contacto no se toca.

## Decisiones (no re-litigar)

| Decisión | Elección |
|---|---|
| Fondo del nombre en el hero | **Viñeta radial** anclada al título, sin bordes rectos |
| Salida del hero | Escalonada por bloques; el zoom empieza cuando el acompañamiento ya se fue |
| Lado derecho de la obra | **Galería**: captura principal grande + dos miniaturas |
| Cartela de la galería | **Cartela de rodaje**: toma + timecode, perforación, marcas de encuadre |
| Organización del stack | **Cuatro departamentos**, 16 filas, todas con descripción |
| Tratamiento del stack | **Bloque de cartel** (billing block), no rodillo con perforación |
| Focos en "Quién es" | **Tres**, no dos |
| Registro del copy | Primera persona, presente, hechos concretos — nunca eslogan |

### Por qué el bloque de cartel y no las otras dos

Se maquetaron los tres tratamientos y se miraron montados. El de **bobina y perforación**
(cabecera de rollo, pietaje numerado, marca de cambio de bobina) funcionaba y ataba la
sección a la cartela de proyectos, pero era el más cargado. El de **hoja de rodaje** tenía
un defecto que solo apareció al montarlo: con las descripciones alineadas a la derecha, las
líneas largas se partían en dos y las guías de puntos quedaban a alturas distintas. Se
corrigió con columna fija, pero seguía dejando demasiado aire entre nombre y descripción.

El **bloque de cartel** es el único donde ningún elemento se descoloca, y la barra vertical
hace el mismo trabajo que la guía de puntos sin el ruido.

Consecuencia aceptada: es tan compacto que la sección deja de llenar los 900px. Hay que
decidir en implementación si se agranda la tipografía o si esta sección deja de ser de
altura completa.

### Por qué la organización por departamentos

La lista pasa de 12 a 16 entradas. En una sola columna plana, la primera columna repetía
"Frontend" catorce veces sin aportar nada. Agrupar por departamento elimina esa
repetición, es como se organizan los créditos reales, y el conteo por grupo dice de un
vistazo dónde hay más peso.

Se descartó la rejilla 2×2 por un defecto medido: los grupos son de tamaños desiguales
(5, 3, 5, 3) y dejan huecos irregulares. Se descartó "seis protagonistas y reparto" porque
relega diez tecnologías a etiquetas mudas.

## Contenido definitivo

Todo vive en `src/data/content.ts`. Textos aprobados literalmente por el usuario:
**no reescribirlos**.

### Hero

- `identity.subheadline` → **"De la base de datos a la pantalla."**
  Sustituye a "Uso Python, React y Django para llevar datos reales a interfaces reales",
  rechazada por genérica. No repite el rótulo `identity.role` que va justo encima.

### Quién es

- `aboutCopy[0]` → **"Estudio Ingeniería de Sistemas y llevo cinco años construyendo
  software."**
- `aboutCopy[1]` → **"Pienso mejor cuando el problema es real: un flujo de aprobaciones que
  nadie sigue, unas cuentas en tres monedas que no cuadran. Eso es lo que hay debajo."**

Se descartó "…construyendo software **fuera de clase**": el editor de texto en C está
etiquetado como proyecto académico y WatchDog salió de un curso, así que el matiz se
contradecía con la obra de más abajo.

- `stats` → `2021 Desde` · **`10.º Semestre`** (era 9.º) · **`5 Proyectos`** (era 4) ·
  `1 En producción`
- `experience[0].period` → **"Ago 2025 — May 2026"** (la pasantía terminó)
- **Campo nuevo** `identity.currentStatus` → **"Freelancer"**. Hoy la ficha deriva el campo
  "Ahora" de `experience[0].organization` (`about.ts:21`); con la pasantía cerrada eso
  quedaría desactualizado por construcción. El dato pasa a ser explícito.
- `identity.availability` → **"Abierto a oportunidades"**, se mantiene. Confirmado que
  convive con "Freelancer" en el campo "Ahora".
- `focusAreas` → **tres** entradas (eran dos). Equilibra con las tres de trayectoria, que
  era parte de por qué la columna derecha se veía corta:

  | Título | Detalle |
  |---|---|
  | Que aguante el volumen | Una consulta sobre miles de filas tiene que seguir tardando lo mismo |
  | Que no se rompa | El estado complejo es donde fallan las interfaces, y donde más cuidado pongo |
  | Que no haya que repetirlo | Si un proceso se hace igual cada semana, lo automatizo |

### Obra

- `caseStudies[echoplan].period` → **"Ago 2025 — May 2026"** (hoy dice "Ago 2025 — hoy")

### Stack

`skillGroups` gana una entrada en Frontend y un grupo nuevo:

| Grupo | Tecnología | slug | Detalle |
|---|---|---|---|
| Frontend | GSAP | `gsap` | Las animaciones de scroll y las transiciones que hacen que la interfaz se sienta viva. |
| Automatización e IA | n8n | `n8n` | Encadeno procesos que si no habría que repetir a mano cada semana. |
| Automatización e IA | Claude Code | `claude` | Lo uso a diario para revisar y refactorizar sin perder el control del código. |
| Automatización e IA | Gemini | `googlegemini` | Para contrastar enfoques cuando estoy decidiendo cómo montar algo. |

Los cuatro slugs existen en el paquete `simple-icons` instalado — verificado en
`node_modules/simple-icons/icons/`. Hay que registrarlos en `src/utils/icons.ts`, que
lanza si falta un slug.

**"n8n" se escribe en minúscula.** `.credit-name` aplica `text-transform:
var(--display-transform)`, que en Vice es `uppercase`. Necesita exención.

## Diseño por sección

Principio que no cambia: **un solo DOM semántico para los tres temas**. La presentación la
decide el CSS bajo `[data-theme]`. Nunca ramificar el marcado por tema desde TypeScript.

### 1 · Hero

**Composición.** El panel rectangular desaparece. En su lugar, una mancha elíptica centrada
en el nombre que se disuelve hacia los bordes: sin borde recto, sin máscara de degradado
sobre una caja. El resto de la composición (rótulo, nombre, frase, esquinas) no cambia.

**Restricción dura.** `check_contrast_wcag` excluye del gate cualquier texto cuyo fondo
muestreado no sea sólido, y `verify.py:453` **falla si una escena no consigue medir ni un
elemento**. El núcleo de la viñeta tiene que quedar lo bastante sólido bajo el nombre para
que la desviación típica del muestreo siga por debajo del umbral. La opacidad se decide
**midiendo**, no a ojo, y contra el fixture SMPTE que sirve hoy, que es el caso más hostil.

**Motion.** El acompañamiento sale escalonado, en orden: esquinas → frase → rótulo, cada
bloque con su desfase. El zoom del nombre arranca **después**, no solapado. El recorrido
del pin se alarga de `+=150%` a `+=220%` para que quepan las dos fases sin atropellarse, y
el fondo acompaña con un empuje leve para que se mueva el plano entero y no solo el texto.

Se mantienen las dos capas anti-carrera que documenta la bitácora: estado inicial fijado de
forma **síncrona** antes de cablear el zoom, y `fromTo` con el valor de partida escrito en
el código, nunca leído del DOM.

### 2 · Quién es

**Composición.** Rejilla a altura completa. La ficha crece (avatar a 74px) y la
disponibilidad pasa a píldora con pulso. Las cifras suben de tamaño y se enmarcan entre dos
filetes. Trayectoria y foco pasan a **línea de tiempo** con hitos: punto relleno para lo
cerrado o en marcha, hueco para lo que sigue en curso. Es información, no adorno — la
pasantía terminó y los estudios no.

**Motion.** Gesto propio, no tres fades genéricos: la ficha se revela por máscara vertical,
las líneas encadenan de verdad, y las cifras entran después con su propio desfase.

### 3 · Obra

**Composición.** La captura principal ocupa la mitad derecha; dos miniaturas debajo. El
texto se queda en la mitad izquierda y respira.

El ordinal gigante queda sin sitio: hoy vive arriba a la derecha, que es justo donde ahora
va la captura. Pasa a sangrar por el borde izquierdo, detrás del título. Se probó abajo a
la izquierda y cruzaba el texto de "Problema", que se leía sucio.

**Cartela.** El cromo de navegador (tres puntos tipo semáforo) se sustituye por una cartela
de rodaje: tira superior con **toma y timecode**, perforación de película por los dos
costados y marcas de encuadre de cámara en las cuatro esquinas. Esquinas rectas, coherente
con `--radius-card: 3px`.

**Hover.** Hoy la sección no reacciona al cursor. Las cartelas se elevan, el borde pasa a
acento y ganan sombra. La fila de metadatos recibe un barrido de subrayado. El ordinal hace
paralaje leve.

**Riesgo.** La rejilla nueva va **bajo `[data-theme="vice"]`**; Hyprland y Caelestia
conservan la suya. Es la tarea con más probabilidad de romper otro tema.

### 4 · Con qué construyo

**Composición.** Cuatro departamentos (Frontend, Backend, Otras herramientas, Automatización
e IA). Cada uno se anuncia centrado entre dos filetes; sus filas van apretadas debajo, con
icono, nombre en display y una barra vertical fina separando el nombre de su descripción.
La fila activa enciende su barra en acento.

**Un DOM, tres temas.** El detalle se añade al marcado compartido como tercera pieza de la
fila. En Vice se muestra y `.credits-panel` se oculta; en Hyprland y Caelestia el detalle se
oculta y el panel sigue funcionando como hoy. `credits.ts` no ramifica por tema: sigue
montando lista, detalle y panel siempre, y el CSS decide.

Se conservan la accesibilidad ya construida (`<button>` real, `aria-pressed`,
`aria-controls`, panel `aria-live`) y el estado inicial con la primera entrada
seleccionada.

## Restricciones que no se tocan

- Limpieza de GSAP: `ScrollTrigger.getById(...)?.kill()` por gesto, timelines sin trigger
  matadas a mano. Con ScrollTriggers reales en cinco escenas esto deja de ser opcional.
- Guards de `prefers-reduced-motion`.
- Cero `any`; `unknown` + guards.
- Cero colores escritos a mano en CSS compartido: siempre del token o `color-mix()` sobre
  un token. Esta regla ya rompió el contraste de `.hero-corner` una vez (1.09:1 en
  Caelestia).
- Los gates de fixtures (`--allow-fixture-assets`) y de galería
  (`--allow-gallery-placeholder`) siguen fallando por defecto. No silenciarlos.

## Riesgos

**El patrón de fallo confirmado cuatro veces.** Toda tarea que reescribe una sección
compartida rompe algo en otro tema. Las cuatro secciones de este spec son compartidas.
Mitigación obligatoria por tarea: antes de borrar un envoltorio o clase por "huérfana",
comprobar que ningún bloque `[data-theme]` de otro tema la usa; y capturar y **mirar** los
tres temas, no solo Vice.

**El arnés verde no basta.** Hubo 14 aserciones en verde mientras el nombre del autor era
invisible en pantalla. Cada tarea se cierra mirando capturas reales, no leyendo el
resultado del arnés.

**La viñeta contra el gate de contraste.** Es el riesgo técnico principal. Si al aflojar el
scrim la escena del hero deja de medir elementos, el gate falla — correctamente. Se resuelve
ajustando la viñeta, nunca debilitando la aserción.

**Altura de la sección de créditos.** El bloque de cartel entra holgado en 900px pero deja
aire abajo. En ventanas bajas puede pasar lo contrario. Decidir en implementación.

## Verificación

1. `npm run build` (tsc + vite) sin errores y `npm run lint` limpio. Node 22 obligatorio.
2. `python3 scripts/verify.py` con `--allow-fixture-assets --allow-gallery-placeholder`
   en verde para **los tres temas**.
3. Capturas reales de navegador en 1440×900 y 390×844, **en los tres temas**, por tarea.
4. Aserciones nuevas del arnés, cada una demostrada **en rojo rompiendo su causa real**
   antes de darla por buena — comprobar un valor inventado no vale:
   - El acompañamiento del hero sale **en orden**: medir la opacidad de los tres bloques en
     varios puntos del scrub y comprobar el desfase, no solo que acaben en cero.
   - El nombre del hero sigue visible a scroll 0 (ya existe; no debe romperse).
   - `.credit` expone su detalle en Vice y lo oculta en Hyprland/Caelestia; el panel, al
     revés.
   - Los cuatro slugs nuevos resuelven en `getIconMarkup` sin lanzar.
5. `prefers-reduced-motion: reduce`: sin coreografía, sin letterbox. La galería sigue
   navegable y los créditos siguen respondiendo — son contenido, no decoración.
6. Anti-mock: `grep -rE "lorem|placeholder|mockData" src/` vacío.

## Fuera de alcance

- La sección de contacto.
- Sustituir los assets provisionales (vídeo de barras, capturas de galería). Sigue siendo
  requisito de merge a producción, pero no es trabajo de este spec.
- Metáfora estructural propia para Hyprland y Caelestia.
- El ritmo vertical de la sección de skills en Hyprland y Caelestia, y extender la firma
  monoespaciada de Hyprland. Ambos siguen aparcados a conciencia.
