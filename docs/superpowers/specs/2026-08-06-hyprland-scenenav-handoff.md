# Selección de escenas de Hyprland — handoff para retomar el brainstorm

Estado: en diseño
Fecha: 2026-08-06
Alcance: solo el tema Hyprland — el disparador (`.scene-nav-trigger`) y la cortinilla de índice
(`.scene-index`) que hoy comparten los tres temas. **Vice no se toca** (terminado). Caelestia
queda fuera salvo que se pida explícitamente al retomar esto.

Este documento **no es un spec cerrado** — es la continuación de una sesión de brainstorming
interrumpida antes de elegir dirección. Retómalo con `superpowers:brainstorming`, el mismo
companion visual, y los mismos agentes (`especialista-ux-ui`, `especialista-animaciones`,
pineados a Sonnet) que se usaron en la sesión del hero (spec de referencia:
`docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md` — mismo patrón de trabajo,
mismos hallazgos a tener en cuenta, ver más abajo).

## Por qué

El disparador de Hyprland hoy es una pastilla genérica: caja con radio 5px, borde falso vía
`box-shadow`, sin dispositivo propio — contradice la identidad de Ascua ("luz con canto", radio 0
en todo salvo la navegación, que es la única excepción ya documentada en el spec del tema). La
cortinilla que abre (`.scene-index`, panel a pantalla completa con las 5 escenas) es **hoy
idéntica en estructura y skin en los tres temas** — Vice solo le quita la caja al disparador y le
añade una marca de registro, pero el panel en sí (telón oscuro, `clip-path` de fundido, filas
numeradas) nunca se re-skinea por tema. Aoshi: "ya Vice usa ese selector de sección, me gustaría
que la cortinilla cambie para Hyprland" — quiere que dejen de sentirse como el mismo componente
vestido igual.

## Decisiones ya tomadas en esta sesión

1. **Alcance: solo Hyprland.** Ni Vice (cerrado) ni el CSS/TS base compartido se tocan — mismo
   patrón que el hero: nodos/reglas nuevas acotadas a `[data-theme="hyprland"]`, todo lo demás
   intacto. Ver la sección "Restricciones" más abajo para el motivo exacto por el que esto importa
   más aquí que en el hero.
2. **Motivación confirmada**: "se siente genérico/plantilla" + la cortinilla necesita dejar de ser
   el telón compartido.
3. **Estructura abierta**: Aoshi pidió explícitamente explorar **otro patrón de interacción**, no
   solo un reskin del telón actual (opción descartada: "mismo patrón, piel propia" — la more
   conservadora de las dos ofrecidas). Esto implica tocar lógica de `sceneNav.ts`
   (comportamiento), no solo CSS.

## El componente actual — lo que hay que conocer antes de tocar nada

- `src/components/sceneNav.ts` (252 líneas): construye el disparador (`<button
  class="scene-nav-trigger">`) y el panel (`<div class="scene-index" role="dialog"
  aria-modal="true">`) para los TRES temas desde una sola función (`mountSceneNav`), llamada una
  vez en `main.ts` independientemente del tema activo.
- `src/components/sceneNav.destino.ts`: calcula el destino de scroll de cada fila (`destinationFor`),
  con un caso especial para "obra" (el carril pineado de Vice reserva scroll extra — en
  Hyprland/Caelestia el carril no está pineado, así que el término da 0 y el destino es
  simplemente el borde de la sección).
- Contenido real (`src/data/content.ts:394`, `sceneIndex`): 5 entradas con `id`/`label`/`blurb` —
  Título, Quién es, Obra, Créditos, Fundido (nombres de cine, ya con el hallazgo de "Fundido no
  comunica contacto" resuelto vía el `blurb`).
- **Comportamiento de accesibilidad ya resuelto y probado en los tres temas** (no reinventar salvo
  que el nuevo patrón lo exija de verdad):
  - Foco atrapado dentro del panel mientras está abierto (`Tab`/`Shift+Tab` cicla entre filas).
  - `Esc` cierra y devuelve el foco al disparador.
  - Clic fuera del panel y del disparador cierra.
  - Bloqueo de scroll con doble cerrojo (`overflow: hidden` + evento `scene-nav:toggle` que
    `initSmoothScroll`/Lenis escucha, porque `overflow` solo no basta cuando Lenis está montado —
    ver comentario en el archivo, con la medición que lo prueba).
  - La escena "actual" se detecta con `IntersectionObserver` (no con la coreografía de Vice, que
    no existe en Hyprland/Caelestia) y pinta el número/nombre en el propio disparador
    (`"03 · Obra"`), que se convierte en el botón "Cerrar" mientras el panel está abierto.
- CSS compartido: `themes.css:3858-4230` aprox. (grep `scene-nav-trigger`/`scene-index` para la
  ubicación exacta al retomar, puede haber cambiado). Vice tiene su propio bloque de overrides
  (línea ~3935) que quita la caja del disparador y añade la marca de registro (cruz en anillo,
  `currentColor`). Hyprland hoy solo tiene 4 líneas propias (línea ~2125): fondo semitransparente
  del disparador porque flota directo sobre el fondo generativo sin `.scene-surface` de por medio.

## Restricciones que no aplicaban igual en el hero — leer antes de tocar CSS

La revisión final de la rama del hero (ver el spec del hero, sección "Revisión final de toda la
rama") encontró 3 Críticos por reglas añadidas a clases **compartidas por más de una escena**
(`.hero-kick`, `.lead`) sin acotar a `[data-scene="hero"]`. Este componente es un caso **todavía
más expuesto** al mismo error: `.scene-nav-trigger` y `.scene-index` no son compartidas entre
escenas de un mismo tema — son compartidas entre **los tres temas completos**, y el disparador
vive fuera del árbol de cualquier escena (`root.append(trigger)` en `mountSceneNav`, ver el
comentario de cabecera del archivo: "vive FUERA de `.cinema-chrome`"). Cualquier regla nueva sin
`:root[data-theme="hyprland"]` en el selector se filtra a Vice y Caelestia inmediatamente — no hay
un `[data-scene="hero"]` equivalente que lo contenga por accidente, así que el margen de error es
menor, no mayor.

Si el nuevo patrón de interacción necesita nodos DOM nuevos en `sceneNav.ts` (que es TypeScript
compartido por los tres temas, igual que `hero.ts`), seguir el mismo patrón que ya validó el hero:
nodos nuevos con `display: none` por defecto en `style.css` (o donde corresponda), reactivados
solo bajo `[data-theme="hyprland"]`.

## Las tres direcciones exploradas en el companion — ninguna elegida todavía

Prototipo (no comiteado, gitignored, probablemente ya limpiado por el harness al cerrar el
servidor — reconstruir si hace falta consultarlo): `scenenav-directions.html`, tres `<div
class="stage">` con un botón "Abrir/cerrar" cada uno.

**A · El carrete** — un rail lateral que entra desde el borde derecho de la pantalla (ancho fijo,
~340px), con la página quedando parcialmente visible detrás (atenuada con un scrim, no tapada del
todo). Las cinco filas entran escalonadas desde la derecha, con un filete de 2px a la izquierda de
cada fila que se enciende en hover/actual. El menos "modal" de los tres — nunca pierdes de vista
dónde estabas.

**B · El corte** — sigue siendo pantalla completa (mismo patrón que hoy, más fiel al `role="dialog"
aria-modal="true"` actual), pero la apertura es una cuña diagonal dura (el mismo lenguaje del
"haz" que ya vive en el fondo del hero y en el resto de Ascua) en vez de un fundido genérico de
`clip-path`. Las filas se encienden en cadena, reutilizando el vocabulario que ya usa el reparto de
créditos (`.credit` con lamps encendiéndose una a una). El más "cine" de los tres, el que menos
cambia la interacción actual.

**C · La ficha** — el propio disparador crece en su sitio (esquina superior derecha, `top:14px;
right:14px`) hasta convertirse en el panel, sin tapar nunca el resto de la pantalla. El más
discreto/contenido — pero es el que más se aleja de "índice de escenas que quieres ver de un
vistazo completo" y el que más dudas de usabilidad puede generar en espacios estrechos (móvil
especialmente: una ficha de 300×270px anclada a una esquina en 390px de ancho hay que probarla,
no asumirla).

Ninguna fue descartada ni aprobada — quedaron a medio comparar cuando se decidió cortar la sesión
aquí. Ideas sueltas que surgieron pero no se llegaron a materializar en mockup, por si sirven de
punto de partida:

- Mezclar A y B: rail lateral (estructura de A) pero con el corte diagonal duro de B como gesto de
  entrada del rail entero, no solo de las filas.
- Para C específicamente, probar primero en mockup el comportamiento a 390px de ancho antes de
  seguir invirtiendo en esa dirección — es la que más riesgo de usabilidad tiene sin haberla visto
  en mobile.

## Cómo retomar

1. `superpowers:brainstorming` — no hace falta repetir las preguntas de alcance/motivación (ya
   resueltas arriba), pero sí seguir el flujo desde "proponer 2-3 enfoques" en adelante: mostrar
   de nuevo las tres direcciones (reconstruir el mockup si no sobrevivió) o proponer variaciones
   nuevas si Aoshi prefiere partir de cero.
2. Compañero visual (`scripts/start-server.sh --project-dir /home/aoshi/proyectos/portfolio-aoshi
   --open`), igual que en la sesión del hero.
3. Una vez elegida/refinada una dirección: `especialista-ux-ui` (accesibilidad — el foco atrapado,
   Esc, bloqueo de scroll ya funcionan, pero un patrón nuevo como A o C puede necesitar ajustes;
   comportamiento en móvil especialmente para C) y `especialista-animaciones` (timing, si se
   reutilizan `--hard`/`--slow` o hace falta justificar algo nuevo), pineados a Sonnet, en
   paralelo — mismo patrón que en la sesión del hero.
4. Escribir el spec de diseño en `docs/superpowers/specs/`, autorrevisión, aprobación de Aoshi
   sobre el documento escrito.
5. `superpowers:writing-plans` → plan de implementación.
6. Implementación — recomendado `superpowers:subagent-driven-development` en un worktree aislado,
   igual que el hero, **con especial atención a la revisión final de rama** dado el mayor riesgo
   de fuga a Vice/Caelestia descrito arriba en "Restricciones".
