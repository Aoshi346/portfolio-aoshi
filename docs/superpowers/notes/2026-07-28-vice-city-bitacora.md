# Bitácora del rediseño de Vice City

> **Qué es esto.** El registro de trabajo que se llevó durante la ejecución del
> rediseño, conservado a propósito. No documenta cómo funciona el código —para
> eso están el spec y el plan— sino **qué se rompió, por qué, y qué riesgos se
> aceptaron a sabiendas**. Es lo que evita que quien toque esto en el futuro
> repita los mismos errores.
>
> Lo más útil está en las secciones de abajo, no en la lista de tareas:
> - **Bloqueos de merge**: material provisional que no puede llegar a producción.
> - **Avisos**: el patrón de fallo que se repitió cuatro veces (toda tarea que
>   reescribe una sección compartida rompe otro tema).
> - **Lección sobre el arnés**: cómo demostrar que una aserción sirve de verdad.
> - **Riesgos residuales aceptados**, con su razonamiento.
>
> Escrito durante la sesión del 27–28 de julio de 2026. Los hashes de commit
> son de la rama `design/redesign-cinematic-themes`, mergeada a `main` en
> `4187de5`.

Plan: `docs/superpowers/plans/2026-07-24-vice-city.md`
Spec de diseño: `docs/superpowers/specs/2026-07-24-vice-city-design.md`
Rama: `design/redesign-cinematic-themes`
Base de la rama (pre-plan): `0c053f2` (checkpoint del prototipo)

## Tareas del plan

- Task 1: completa (commits 0c053f2..d2e23c0, revision limpia tras un arreglo)
- Task 2: completa (commit 9564805, revision limpia a la primera, sin hallazgos)
- Task 3: completa (commit 0fb644f, revision limpia a la primera, un hallazgo Menor)
- Task 4: completa (commits aa297fa, e81ea66, 0be2bf3). Necesito dos intentos de
  arreglo para la asercion de fuentes; ver la leccion de abajo.
- Task 5: completa (commits 06011fa, c151457). La revision fallo el spec: el
  implementador borro tres funciones donde el brief mandaba borrar dos, y la de
  mas dejaba el nombre del hero invisible 3 s en cada carga. Arreglado y
  verificado por medicion de opacidad en el tiempo (1 desde los 300 ms).
- Task 6: completa (commits c973ecd, 47cba56, e2c874a). Hero con gesto GTA
  funcionando (nombre 1344px -> 3164px al scrollear). La revision fallo el spec
  por una regresion en Caelestia; ademas yo encontre mirando la captura un
  defecto de contraste que ni la revision ni el arnes vieron. Ambos arreglados.
- Task 7: completa (commits 810a931, f8072f9, 1ad9836). Seccion "Quien es" con
  ficha, cifras y trayectoria a dos columnas: resuelve la queja del usuario de
  que el lado derecho se veia vacio. La revision encontro que `aboutCopy` ya
  existia en content.ts y quedo huerfano mientras about.ts duplicaba su texto a
  mano; arreglado. El copy de "En que me enfoco" se movio a `focusAreas` en
  content.ts. **PENDIENTE DE DECISION DEL USUARIO**: al consolidar se acorto
  `aboutCopy` de tres frases a dos. Lo eliminado (semestre y pasantia) ahora se
  muestra troceado en la ficha y la trayectoria, pero era texto suyo.
- Task 8: completa (commits 49ae0e9, 24d652f, 8c02c3a). Cartela de obra y galeria
  arrastrable con Pointer Events, accesible por teclado. La revision encontro que
  la exencion del gate de contraste, anadida para una marca de agua decorativa,
  se habia hecho sobre `aria-hidden`, que NO significa decorativo: bastaba anadir
  ese atributo para silenciar el gate. Acotada a un marcador `data-decorative`.
  Anadido ademas el gate del placeholder de galeria.
- Task 9: completa (commit 31b806f). Revision APROBADA A LA PRIMERA, sin
  hallazgos Criticos ni Importantes. Creditos de cine en Vice y pildoras en
  Hyprland/Caelestia desde el mismo DOM. Arreglo de un fallo preexistente del
  arnes: el barrido de scroll etiquetaba mal las escenas al haber cinco, asi que
  las dos escenas de obra median siempre la segunda. El revisor lo reprodujo por
  su cuenta y concluyo que era cobertura redundante, NO un defecto no detectado:
  ambas escenas usan el mismo componente y los mismos tokens. No invalida
  verificaciones anteriores.
- Task 10: completa (commits 11cbd02, 264b856, 9b77ac7, ce140fb). Contacto,
  letterbox, barra de orientacion y la capa de atenuacion del fondo, que mejoro
  la legibilidad de TODAS las secciones interiores (hero y contacto a plena luz,
  el resto al 62%). La revision encontro que la barra tapaba texto en ventana
  baja (1440x600): arreglado reservando el espacio del cromo en el padding de
  las cinco escenas, verificado en 32 combinaciones de altura y escena.
  Saldadas dos deudas: `.hero-mail` con scrim de `color-mix` (era el ultimo
  acento puro, y la Task 11 va a cambiar el video que hoy lo exime del gate), y
  borrado el codigo muerto `contact.ts` y `nav.ts`, que tenian `rel="noreferrer"`
  sin `noopener`.
  RIESGO RESIDUAL ACEPTADO: con un elemento fijo en `top:0` sobre contenido que
  scrollea libremente, el padding desplaza el punto de solape pero no lo elimina;
  en transito el texto pasa por detras de la barra. Se acepta porque la barra es
  un HUD con su propio scrim y el texto se lee como "detras", no como recortado.
  Eliminarlo exigiria `scroll-snap`, que interferiria con el pin del hero.

## Hallazgos menores acumulados

- `scripts/verify.py`: la constante `MOBILE` esta definida sin usar. La Task 12
  anade las aserciones de movil que la consumen. Si al llegar a la Task 12 sigue
  sin usarse, retirarla.
- `src/themes/vice.ts`: el stub no-op de `mountBackground` duplica la forma de
  `NOOP_HANDLE` de `shaderBackground.ts`. La Task 3 sustituye el stub entero,
  asi que la duplicacion desaparece sola. Verificar que asi sea.
- `eslint.config.js` no define `argsIgnorePattern`, asi que un parametro con
  prefijo de guion bajo (`_container`) da error de lint en vez de quedar exento.
  No es de la Task 1 pero volvera a morder en cuanto una tarea escriba una firma
  con un parametro sin usar. Decidir en la revision final si se corrige.

## Correccion intercalada tras la Task 4 (plan aparte, aprobado por el usuario)

Plan: `/root/.claude/plans/stateful-dancing-dragon.md`
Commits: `4f4237e`, `3ebf0a6`, `9834ded`. Revision limpia, un hallazgo Menor.

Motivo: el usuario pidio ver el resultado real antes de seguir. La inspeccion
visual encontro tres defectos que el arnes NO detectaba con 14 aserciones en
verde. Leccion de fondo: las aserciones verdes no sustituyen a mirar la pagina.

1. **Nombre del hero invisible en Vice** (`opacity: 0`). Carrera entre la regla
   CSS de `.js-intro` y el tween con scrub de `wireHeroZoom`, que capturaba ese 0
   como valor de partida y animaba de 0 a 0. Arreglado fijando el estado inicial
   de forma sincrona antes de cablear el zoom, y con `fromTo` de valor explicito.
   Verificado con la carga de fuentes retrasada 5 s (cuatro veces el timeout de
   1200 ms del codigo): la opacidad se mantiene en 1. La carrera esta eliminada,
   no solo hecha improbable.
2. **Monoespaciada superviviente en Vice.** El marcado traia `font-mono` a pelo y
   `style.css` define un `--font-mono` global, asi que Vice caia en la mono del
   sistema. Arreglado apuntando `--font-mono` a Manrope en el bloque de Vice y
   limpiando `experience.ts`, que NINGUNA tarea del plan toca.
3. **Gate de assets sinteticos** anadido al arnes. Ver bloqueos de merge abajo.

Hallazgo Menor pendiente: el detector de monoespaciada del arnes ignora los
elementos `position: fixed` con hijos mixtos (`offsetParent` es null y no son
hoja). Hoy no afecta porque `--font-mono` de Vice ya apunta a Manrope, pero
`src/components/themeSignature.ts` quedaria fuera de vigilancia.

## AVISO PARA LAS TASKS 7-10 (leer antes de despachar cada una)

**Patron confirmado dos veces: toda tarea que reescribe una seccion compartida
rompe algo de otro tema.** Las secciones son un DOM unico para los tres temas;
quien las reescribe pensando solo en Vice se lleva por delante a Caelestia o a
Hyprland.

- La Task 4 toco `themes.css` (compartido) y dejo a Vice cayendo en la
  monoespaciada del sistema.
- La Task 6 reescribio `hero.ts` y elimino el envoltorio `.hero-surface`, que
  Caelestia necesita para su tarjeta Material You. Su CSS quedo sin nada a lo
  que aplicarse y el hero de Caelestia paso a ser texto suelto sobre un
  degradado. Arreglado en `47cba56` devolviendo el envoltorio para los tres
  temas y neutralizandolo desde el bloque de Vice.
- La misma Task 6 fijo a mano el crema de Vice en `.hero-corner`, compartido por
  los tres temas. En Caelestia, que es CLARO, el contraste era de 1.09:1 sobre
  4.5:1 exigido: texto practicamente invisible. Arreglado en `e2c874a` sacando
  el color del token con `color-mix`.

Regla para las tareas 7-10 (about, obra, creditos, contacto):
1. Antes de borrar un envoltorio o una clase por "huerfana", comprobar que
   ningun bloque `[data-theme]` de OTRO tema la usa.
2. Cero colores escritos a mano en CSS compartido: siempre del token.
3. Capturar y MIRAR los tres temas, no solo Vice.

El arnes ya tiene un gate de contraste WCAG AA que corre en los tres temas
(commit `e2c874a`) y desde `1ad9836` recorre tambien las secciones que quedan
POR DEBAJO DEL PLIEGUE, desplazandose a cada escena. Demostrado: con el gate
viejo un texto a 1.04:1 bajo el pliegue daba `TODO OK`; el ampliado lo caza.
Limites conocidos y declarados: no evalua texto sobre video ni sobre los
degradados de shader, porque el fondo no es un color solido; esos casos salen
como SKIP, no como PASS.

Acoplamiento de orden a vigilar en `scripts/verify.py`: el barrido de scroll del
gate de contraste debe devolver la pagina al tope al terminar. Si no, rompe las
aserciones posteriores que asumen scroll 0 (visibilidad del nombre del hero y
email en el primer viewport). Ya paso una vez durante el desarrollo.

## OBLIGACION PARA LA TASK 6 (leer antes de despacharla)

La Task 5 RETIRO las dos capas del arreglo de la carrera del hero
(`prepareHeroIntro` / `wireHeroZoom`), siguiendo la instruccion explicita de su
brief: el gesto del hero pasa a la coreografia de Vice en la Task 6.

Consecuencia: ahora mismo la visibilidad del nombre a scroll 0 depende SOLO de
la red de seguridad de `main.ts` (regla CSS mas un timeout), no de GSAP. Eso
basta mientras la coreografia del hero este vacia. **En cuanto la Task 6 vuelva
a crear un timeline con scrub sobre el nombre, la carrera vuelve** salvo que
reimplante las dos capas dentro de `vice.choreography.ts`:

1. Fijar el estado inicial (`opacity: 1`) de forma SINCRONA antes de cablear el
   zoom. Lo asincrono (el split del texto, que espera a las fuentes) va despues.
2. El tween del zoom con `fromTo` y el valor de partida ESCRITO EN EL CODIGO,
   nunca leido del DOM en el instante del render.

La asercion de visibilidad del arnes lo vigila. Si la Task 6 la rompe, hay que
arreglar el codigo, NO debilitar la asercion.

Segunda nota para las tareas 6-9: la Task 5 no necesito `kill()` porque su
coreografia esta vacia y el tema se elige una sola vez por carga, sin ciclo de
desmontaje. En cuanto se anadan ScrollTriggers y timelines reales, hay que
volver a aplicar el patron de limpieza.

## BLOQUEOS DE MERGE (no mergear a main sin resolverlos)

- **Media sintetica en `public/media/`.** La Task 3 commiteo `vice-poster.webp`,
  `vice-hero.webm` y `vice-hero.mp4` generados localmente con ffmpeg (poster de
  color solido, video de barras de test). La descarga de los assets reales la
  bloqueo el clasificador del entorno. Son fixtures, NO contenido.
  - El unico rastro de que son provisionales esta en el mensaje del commit
    `0fb644f`. En el arbol de trabajo no hay ninguna senal: los nombres de
    archivo son los definitivos y no hay comentario ni marcador.
  - Riesgo concreto: el sitio se ve "correcto" con ellos (hay video, se
    reproduce, el arnes pasa), asi que pueden llegar a produccion sin que nadie
    lo note.
  - **La Task 11 DEBE sustituirlos** por los assets reales.
  - **Gate YA ANADIDO** en `scripts/verify.py` (commit `9834ded`): falla por
    defecto mientras los fixtures esten presentes, y se silencia con el flag
    `--allow-fixture-assets` durante el desarrollo. Con el tema vice, el arnes
    da hoy 14/17 y los 3 fallos son este gate: es lo esperado, no una regresion.
    La Task 11 lo apaga sustituyendo los ficheros.
  - Fragilidad conocida del gate: identifica los fixtures por una lista fija de
    tres hashes sha256. Si se regenerasen con otra semilla de ffmpeg, los hashes
    quedarian obsoletos y el gate daria un verde falso. Se eligio asi a
    proposito, frente a una heuristica de "parece sintetico", para no dar falsos
    positivos con video legitimo de franjas de color.
  - ffmpeg 6.1.1 esta instalado en `/usr/bin/ffmpeg`: la Task 11 no esta
    bloqueada por dependencias de sistema.

- **Placeholder "IMAGEN PENDIENTE" en la galeria de obra.** Las imagenes de
  `/media/obra/*.webp` no existen (dan 404 real), asi que las tarjetas muestran
  ese texto. Es un fallback honesto, pero es placeholder visible en una seccion
  publicada. Gate anadido en `8c02c3a`: falla por defecto, se silencia con
  `--allow-gallery-placeholder`. **La Task 11 lo resuelve** con las capturas
  reales del usuario.

- **Flags de desarrollo del arnes** (ambos activos por defecto, es decir, el
  arnes falla si no se pasan mientras el estado provisional siga ahi):
  `--allow-fixture-assets` (video y poster sinteticos) y
  `--allow-gallery-placeholder` (imagenes de obra ausentes). Cuando la Task 11
  termine, el arnes debe pasar SIN NINGUNO de los dos.

## LECCION: como verificar una asercion del arnes

Aprendido en la Task 4, tras dos intentos fallidos. Aplicarlo al resto del plan.

Para dar por buena una asercion nueva NO basta con anadir una comprobacion falsa
que busque un valor inventado: eso solo demuestra que `check()` funciona. Hay que
**romper la causa real** y ver FAIL. Ejemplo del error cometido: se anadio una
asercion que buscaba `"NonExistentFont"`, dio FAIL, y se dio por demostrado. Al
romper de verdad la carga de fuentes (`fontHref` a un dominio que no resuelve),
las tres aserciones seguian en OK.

Trampas concretas de la API que causaron el falso verde:
- `getComputedStyle(el).fontFamily` devuelve el valor DECLARADO en CSS, no la
  fuente usada para pintar. Siempre dice "Passion One" aunque no exista.
- `document.fonts.check('900 1rem "X"')` devuelve true si el texto puede pintarse
  con lo disponible, INCLUIDO el fallback del sistema.
- `document.fonts.status === 'loaded'` solo dice que la cola de carga termino,
  con exito o sin el.

Lo que si funciona:
`Array.from(document.fonts).some(f => f.family.includes(nombre) && f.status === 'loaded')`
Sin hoja de estilos de fuentes no hay entradas FontFace en el registro, asi que da
false. Verificado empiricamente en ambos sentidos.

## Contenido definitivo (decidido por el usuario)

Cinco proyectos, aplicados en `0222c0f`, en este orden: EchoPlan, TesisFar,
HyprFinance, Proyecto CiberSeg y el editor de texto en C.

- Sustituyen a los cuatro anteriores; desaparece `campaign-analytics`.
- Los textos los aprobo el usuario literalmente. NO reescribirlos.
- **El usuario autorizo nombrar a Telefonica en EchoPlan.** Hoy su `status` pone
  "Sistema interno de empresa"; debe pasar a nombrar a Telefonica Venezuela,
  para ser coherente con la seccion de experiencia, que ya la nombra abiertamente.
- HyprFinance y EchoPlan son repos PRIVADOS: van sin `link` y con
  `privateProject: true`.
- Las siete imagenes de galeria son RELLENOS honestos generados localmente, no
  capturas reales. El usuario los pidio expresamente mientras consigue las suyas.
  Se detectan por hash en el gate del arnes, que falla por defecto y se silencia
  con `--allow-gallery-placeholder`. **Sustituirlos es requisito de merge.**

Fuentes de los textos: se leyeron los repos del usuario con `gh` (sesion activa
como Aoshi346). Para finance-app el README es la plantilla de Vite en todas las
ramas; la informacion real estaba en `.specify/memory/constitution.md` y en los
specs de sesion. Para CiberSeg la rama util es `develop` (27 commits), no `main`
(2 commits).

## PENDIENTE DE APLICAR (decidido por el usuario, aun no en el codigo)

1. **Anadir LinkedIn al contacto.** URL canonica, sin los parametros de
   seguimiento con los que llego:
   `https://www.linkedin.com/in/aoshi-blanco-sanz-14119b2b7`
   Es el hallazgo de mas impacto de la tester no tecnica: dijo que su ausencia
   es lo unico que la haria escribir por correo en vez de por su flujo habitual.
2. **Renombrar "Proyecto CiberSeg" a "WatchDog"**, que es el nombre real de la
   aplicacion. El enlace del repositorio sigue apuntando a `Proyecto-CiberSeg`,
   que es como se llama el repo.

No se aplicaron en el momento porque el agente en vuelo estaba editando
`contacto.ts` (telefono como enlace `tel:`), que es justo donde va LinkedIn.

## Decisiones de ejecucion

- **Ejecucion EN SERIE, decidida por el usuario.** Un implementador cada vez, y
  su revision cerrada antes de despachar la tarea siguiente. Motivo: mantener
  cada tarea aislada en su propio commit. Se descarto explicitamente solapar la
  revision de la tarea N con la implementacion de la N+1, porque un arreglo de
  la revision de N aterrizaria sobre codigo que N+1 ya toco y el commit del
  arreglo dejaria de ser aislable.
- Paralelizar implementadores no es viable en este plan: las 12 tareas extienden
  `scripts/verify.py`, ocho tocan `src/style.css` y seis tocan
  `src/themes/vice.choreography.ts`. Ademas las tareas 6-10 dependen del
  contrato de coreografia que crea la Task 5.

## Notas de estado

- Vice queda SIN FONDO desde la Task 1 hasta la Task 3 (se retiro `viceSunset.ts`
  y el backdrop cinematografico no existe todavia). Es temporal y esperado.
