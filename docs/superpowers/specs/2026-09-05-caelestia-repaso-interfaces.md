# Caelestia — repaso de interfaces con Aoshi (registro de sesión)

Estado: implementado
Fecha: 2026-09-05 y 2026-09-06
Rama: `fix/repaso-interfaces` desde `main` (`70efa64`), fusionada en `main` con `--no-ff` (`1c246eb`). Sin push.
Tipo: registro de una sesión de corrección dictada, no un spec de diseño. No lleva plan: cada
fallo se trató como una unidad (reformular, reproducir, arreglar, gate, commit).

---

## Qué fue esta sesión

Aoshi recorrió Caelestia escena por escena, en el sitio real, y dictó lo que no le gustaba. El
protocolo por fallo: reformularlo (tema, escena, ancho, hora), reproducirlo contra el build de
producción servido (nunca `npm run dev`), comprobar si chocaba con una decisión ya aceptada
(móvil fuera de alcance en B1-B4, marcadores «CAPTURA PENDIENTE», P1 de B4, BLOCKs de Vera),
comprobar qué arnés tendría que haberlo cazado (y arreglar también el instrumento), delegar la
edición a un subagente Sonnet con lista de ficheros permitidos, verificar (build, lint, arnés de
la escena, captura real, `verify.py`) y commitear `fix(scope): ...`. **Cuando el «fallo» era en
realidad un cambio de diseño, se paró y se dijo**: así nacieron el rediseño de la tarjeta «Ahora
mismo» (spec propio, `2026-09-05-caelestia-ahora-mismo-design.md`) y el dino como juguete
(adenda en `2026-09-04-caelestia-fundido-design.md`).

## Los nueve fallos dictados y su arreglo

| # | Escena | Lo que dictó Aoshi | Causa real | Arreglo | Commit |
|---|---|---|---|---|---|
| 1 | Título | «Los esqueletos se ven de una» al cargar; el nombre asoma detrás de la terminal `whoami` | Nada ocultaba el hero hasta que llegaba el chunk de coreografía (`.js-intro` es solo de Vice): ventana de 307-2900 ms pintado entero | Clase `js-cae-entrada` en `main.ts` (con tope de 3 s) y `visibility: hidden` acotado en `themes.css`; `montarEntrada` escribe los estados iniciales con `gsap.set` y descubre | `667405a` |
| 2 | Shell | La notificación «Disponible para proyectos» salta a los 900 ms de cargar | `primerAviso` en `caelestiaShell.ts`, pensado en la fase A antes de que existiera la entrada de Título | Se quita; el toast solo abre en `caelestia:esquema` real. Gate 8 del arnés de hora invertido | `de1c8e6` |
| 3 | Título | El nombre se traza detrás de la terminal antes de que esta se vaya | Orden de la timeline: trazo antes de la salida de la terminal | La terminal se va del todo (paso 4) y después se traza (paso 5). Gate nuevo: firma y trazo no pintados antes del «arranque», trazo nunca con la terminal visible | `b9f288c` |
| 4 | Shell | La barra y el dock aparecen de golpe | Decisión de la fase A («el shell ya está puesto»), que Aoshi reabre | Entrada CSS (`caeShellBaja`/`caeShellSube`, 12 px, 0,4 s) bajo `no-preference`; el dock usa `translate` para no pisar su `transform` | `e9aae9c` |
| 5 | Obra | El cajón deja 60 px de aire por columna, 89 px de ventana vacía y un filete que chirría | Rejilla con huecos fijos y `outline` de 1 px con radio 18 | El cajón llena la ventana (`container-type: size`, `100cqh`), captura a la altura del cajón, prosa 14 px en una columna, sin filete, radio 16. Tres vueltas hasta que Aoshi lo dio por bueno | `c1017b9`, `01cf188` |
| 6 | Obra | «Proyecto privado de empresa» se lee con letras separadas | Mono mayúsculas con tracking 0,12 em | Voz de los valores de metadatos: Hanken 13 px, caja normal, sin tracking | `c1017b9` |
| 7 | Obra y Stack | Zustand sin icono y la C con un icono que no es el hexágono | simple-icons no trae Zustand y su C es otra marca | C y Zustand desde Devicon Plain (MIT), inlineados en `src/assets/icons/`, Zustand pasado por svgo (44 KB a 5,4 KB gzip) | `7a46a0e` |
| 8 | Obra | El cajón no tiene relieve y el texto hace un fundido plano al elegir | Pintaba `--cae-elev-1`, el mismo color que la ventana | Hoja en `--cae-elev-2` con sombra por esquema; relevo del texto por capas; el título ablanda Fraunces 800 a 640 al aterrizar (proxy `fontVariationSettings`) | `b7c4ca1` |
| 9 | Shell | Quitar la chapa «Disponible» de la barra; el reloj se queda | La disponibilidad ya vive en la tarjeta del hero | `.cae-avail` fuera del DOM y del CSS; gate del arnés de hora: la barra no lleva `.cae-avail` | `eb9b0f4` |

Además, por petición: las escenas 4 y 5 pasan a llamarse **Stack** y **Contacto** (blurb «Hablemos de
tu proyecto»), en `content.ts` (`ec67a2d`).

## Los dos cambios de diseño que salieron de aquí

- **La tarjeta «Ahora mismo»** (spec y plan propios; fusionada en `630d249`). Brainstorming en el
  visual companion con nueve maquetas; Aoshi eligió orden «quién, qué hace, estado», la figura
  viva como acento y «Full Stack Developer» a 27 px. Vera 6,6 (BLOCK residual, sin P0 propio),
  Lidia 6,4. Detalle en su spec.
- **El dino de Contacto es un juguete** (adenda en el spec de B5; fusiones `8cdd535`, `2c4458d`,
  `b0f58b5`, y `4fcdd42`). Salta al pulsar, mira al cursor, y arrastrarlo es un **vistazo** a otra
  hora que se deshace al soltar. El troquel gira con la hora del vistazo, con muelle. Y desde
  `4fcdd42` **el fondo generativo sigue el vistazo**: el motor de color publica la hora efectiva y
  el fondo la escucha.

## Errores cometidos en la sesión (para no repetirlos)

1. **Medir a 1412x748 de viewport.** Esa es la ventana INTERIOR con página a 1440x900; fijarla
   como viewport encoge el panel a 596 px. Una vuelta entera del cajón de Obra se tiró por esto.
   Memoria `ventana-de-caelestia-no-es-el-viewport`.
2. **`calc(100cqh - 40px)`** restaba el padding dos veces: `cqh` ya lo excluye.
3. **Commitear con `verify.py` en rojo y decir que estaba en verde.** El commit `eb9b0f4` afirma
   «verify.py (0 nuevos)» y salía 1: el spec de la tarjeta decía `pendiente de plan` en el árbol
   principal mientras el worktree ya lo había pasado a `en ejecucion` con un plan de 34 pasos a
   cero. Se corrigió en `e1f30fc`/`364aaf5`. **Un spec y su plan viven en la misma rama.**
4. **Subagentes que se paran «esperando» un proceso de fondo.** Pierden el monitor y hay que
   reanimarlos. Orden que funciona: esperar POR PID dentro del mismo comando Bash, con timeout
   de 600 s, y no terminar el turno hasta acabar.
5. **Subagentes que levantan previews por su cuenta** (4184, 4173, 4195 huérfano apuntando a un
   worktree borrado, sirviendo `dist` viejo). Puerto fijo en el brief, matar por PID, nunca `pkill -f`.
6. **OOM-kill del kernel** con tres arneses de Playwright y varias sesiones a la vez (carga 14 en
   8 núcleos). Un arnés cada vez; si algo cae con `ERR_CONNECTION_REFUSED`, el preview murió:
   relevantarlo, no buscar el fallo en el código.
7. **`.claude/` está en `.gitignore`**: un `git add` de `verification.md` aborta la cadena de
   commit. Se edita igual (documentación local), no se commitea.
8. **El primer gate `entrada` acusaba coreografía legítima** (el trazo dibujándose, el
   cross-fade de la firma). Se acotó a «antes del arranque». Un gate que da rojo contra lo
   correcto es tan malo como uno que da verde contra lo roto.
9. **El hook `__CAE_SET_MINUTOS__` no llegaba al fondo ni al reloj de la barra** (leían
   `new Date()` por su cuenta). Lidia reportó «el titular se pierde de noche» con una captura a
   las 19:42 reales forzadas a 23:00: shell de noche sobre fondo de día, un estado que ningún
   visitante puede ver. Desde `4fcdd42` el fondo sigue la hora efectiva y el artefacto desaparece;
   el reloj de la barra sigue mostrando la hora real a propósito (es el reloj del visitante).
10. **Los críticos no cazaron la regresión de 1366x768** (se les dijo que no la repitieran porque
    ya estaba vista): la cazó mirar la captura. La tarjeta nueva medía 49 px más y pisaba el
    «2021» por 22 px; la vieja dejaba 27 de aire. Arreglada con `@media (max-height: 800px)` y
    gate `tarjeta_portatil` con contexto propio a 1366x768.

## Lo que queda abierto (no es de esta sesión, pero conviene saberlo)

- **Sin push.** `main` está en `1c246eb` localmente.
- **Deuda registrada de la tarjeta:** escala tipográfica fuera de rejilla 4/8 (6.ª recurrencia
  del proyecto), la tabla estudios/trabajo sin rótulo (P1 de Lidia desde B1), la pastilla
  «Disponible para proyectos» parece botón y es inerte (P2). Cambiarlas es decisión de Aoshi.
- **Edge del troquel:** su figura de reposo se lee al montar; si el viewport cruza los 640 px y
  después se arrastra el dino, gira la figura del otro tamaño hasta recargar.
- **Lo que ya estaba abierto antes:** las nueve capturas reales de Obra (B3, marcadores
  «CAPTURA PENDIENTE»), los dos P1 de producto de Stack (B4), los BLOCK residuales de Vera, y
  las tres aserciones de contraste del arnés de Obra que fallaban antes de B5 por su propio
  instrumento (`bg=rgba(0, 0, 0, 0)`).
