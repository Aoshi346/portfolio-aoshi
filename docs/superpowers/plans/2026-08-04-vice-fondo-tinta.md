# Tinta de cartel — plan de implementación

> **Para quien ejecute esto:** SUB-SKILL OBLIGATORIA: usa `superpowers:subagent-driven-development`
> (recomendado) o `superpowers:executing-plans` para ir tarea a tarea. Los pasos usan casillas
> (`- [ ]`) y hay que marcarlas **en el momento**, no al final (regla del proyecto:
> `.claude/rules/speckit-progress-tracking.md`).

**Objetivo:** sustituir el fondo generativo de Vice por una serigrafía a dos tintas tramada en
semitono, con el scroll moviendo el balance entre las planchas.

**Arquitectura:** un módulo nuevo `src/backgrounds/viceInk.ts` sobre `mountShaderBackground`, el
mismo motor que ya usan los otros dos temas. `themes/vice.ts` cambia su import diferido. Cero
dependencias nuevas, cero ficheros de asset: todo se genera en el fragmento.

**Stack:** Vite 8 + TypeScript estricto + WebGL crudo + arneses de Playwright en `scripts/`.

**Prototipo de referencia:** `.superpowers/brainstorm/3762734-1785873008/content/fondos-vice.html`,
composición `print`. **Está aprobado y medido** — no lo rediseñes al portarlo. Lo que este plan
añade sobre él es la integración, el techo verificado en el sitio real y el muaré.

## Restricciones globales

- **Node 22 para construir.** `source ~/.nvm/nvm.sh && nvm use 22` antes de `npm run build`.
- **Medir en el build de producción**, nunca en `npm run dev`: el HMR corrompe ScrollTrigger.
  Servir con `npx vite preview --port 4173`.
- **El puerto 5173 es de OTRO proyecto del usuario** (`Decision-Maker/frontend`, escuchando solo
  en IPv6). No tocarlo, no matarlo, y no usar `localhost` para verificar — usar `127.0.0.1`.
- **Siempre `?theme=vice`**: el tema se sortea por visita.
- **Cero `any`.** `strict` está activo; `unknown` + guards.
- **El módulo devuelve un handle con `destroy()`** que se llama en `pagehide`.
- **`prefers-reduced-motion` degrada el viaje, nunca la función.**
- **Cero emojis** en código, commits y documentación.
- **Un commit por tarea**, con `tipo(scope): descripción`.
- **Cuidado con los backticks** al escribir GLSL dentro de un template literal de JS. Ya rompió el
  prototipo dos veces: un comentario que citaba `min(...)` entre comillas invertidas cerraba la
  cadena, y el error que salía era `Unexpected identifier 'min'`, que no apunta al sitio.

## Ficheros

| Fichero | Responsabilidad |
|---|---|
| `src/backgrounds/viceInk.ts` | **Nuevo.** El fragmento y el montaje. Lee el progreso de `window`. |
| `src/backgrounds/shaderBackground.ts` | Solo si la Tarea 5 concluye que el paso de trama debe escalar con el `devicePixelRatio` real: hoy el DPR se acota a 1.5 y el módulo no lo expone. |
| `src/themes/vice.ts` | Cambiar el import diferido y reescribir el comentario de cabecera. |
| `src/backgrounds/viceHaze.ts` | **Se borra**, pero solo en la Tarea 8, con todo verde. |
| `src/themes/themes.css` | Solo si el gate de contraste obliga a recalibrar `--nav-dim`. |
| `src/style.css` | Revisar `.bg-theme::before` y `::after` de Vice: se calibraron contra el fixture SMPTE y sobrevivieron al shader por inercia. |
| `scripts/measure-bg-luma.py` | **Nuevo.** El techo de brillo, medido sobre el fondo aislado en el sitio real. |
| `scripts/verify.py` | El gate del backdrop de Vice comprueba canvas presente y sin video/poster; sigue valiendo. Confirmar, no reescribir a ciegas. |

---

### Tarea 1: El arnés del techo de brillo, antes que el fondo

El instrumento va primero: sin él, "se ve oscuro" es una opinión.

- [x] Crear `scripts/measure-bg-luma.py`. Carga el sitio con `?theme=vice`, **oculta el contenido**
      (`page.add_style_tag` con `#app { visibility: hidden }`) para aislar el fondo, recorre al
      menos 12 posiciones de scroll y mide en cada una el p99.5 de luminancia de la franja
      vertical 0.06–0.74, más el p99.5 del fotograma entero y el píxel más claro.
- [x] Techos: **62** en la franja, **82** en el fotograma, **150** el píxel. Salir 1 si se pasa.
- [x] Correrlo contra `viceHaze` (el fondo actual) y anotar sus números como línea de partida. Si
      el arnés no da verde con el fondo que HOY pasa el gate de contraste, el arnés está mal
      calibrado y hay que arreglarlo antes de seguir.
      Resultado: verde — 12/12 posiciones a 12.21/12.21/12.21 (franja/fotograma/pixel) contra
      techos 62/82/150. Riesgo anotado: swiftshader colapsa el ruido hash/fbm en headless, por lo
      que este numero de linea de partida puede no capturar el peor caso real en GPU real — a
      verificar tambien en browser real en la Tarea 3.
- [x] Usar `executable_path="/usr/bin/google-chrome"`: el chromium propio de Playwright no está
      descargado en esta máquina.
- [x] Commit. (`add4e33`)

### Tarea 2: Portar el fragmento del prototipo

- [x] Crear `src/backgrounds/viceInk.ts` con `mountViceInk(container): BackgroundHandle`.
- [x] Portar el fragmento `print` del prototipo **sin rediseñarlo**: `screenDot` sobre
      `gl_FragCoord`, `regMark`, los dos focos con caída 1.9/1.7, la rasqueta por tinta, el
      balance por scroll y el desregistro fijo.
- [x] Sustituir `ceilingClamp` por la versión de luminancia del spec. **No dejar el `min` por
      canal**: es el bug que este cambio viene a cerrar.
- [x] `uScroll` se sirve como uniforme dinámico leyendo `window.scrollY` contra
      `scrollHeight - innerHeight`, igual que hacía `viceHaze` y por el mismo motivo (el fondo no
      puede depender de Lenis ni de la coreografía).
- [x] `hash`, `noise` y `fbm` **ya los prefija `shaderBackground.ts`** en `NOISE_CHUNK`: no
      duplicarlos.
- [x] Cambiar `mountBackground` en `src/themes/vice.ts` y reescribir su comentario: hoy explica
      por qué se abandonó el vídeo por la bruma, y la historia ya tiene un capítulo más.
- [x] `npm run build` y `npm run lint` verdes.
- [x] Commit. (`0342f12`)

### Tarea 3: El techo, verificado en el sitio real

- [x] Correr `scripts/measure-bg-luma.py` contra el fondo nuevo, a 1440x900 y 390x844.
- [x] Si se pasa: **bajar el brillo en la fuente**, no subir el techo. La palanca correcta por
      orden es (a) los factores de mezcla de las tintas, (b) `LUMA_MAX`, (c) mover el foco ámbar
      —la tinta más luminosa— fuera de la franja del texto. En el prototipo esa tercera fue la que
      cerró el último punto.
      No hizo falta: el fondo ya pasaba con margen (~8 puntos sobre el techo de banda) sin tocar
      ninguna palanca. Lo que sí tuvo un bug real fue el propio arnés de la Tarea 1 (`#app {
      visibility: hidden }` ocultaba también el canvas, hijo de `#app`): la primera corrida daba
      falso verde midiendo `--color-ink` (12.21 constante), no el shader. Corregido a `#app > *:not(.bg-theme):not(.bg-noise)`, techos sin tocar.
- [x] Anotar los números finales en el registro de implementación del spec.
      1440x900: banda 53.75/62, fotograma 53.54/82, pixel 55.75/150.
      390x844: banda 54.01/62, fotograma 53.82/82, pixel 55.25/150.
- [x] Commit. (`096838a`)

### Tarea 4: Contraste y capas de CSS

- [x] Correr `python3 scripts/verify.py --url http://127.0.0.1:4173`. **Solo y sin editar nada**:
      cualquier edición dispara el HMR y se lleva por delante el contexto de la página.
      Resultado: EXIT 0, 12 fallos conocidos de la linea base (assets de galeria/fixtures de
      video, no relacionados), 0 nuevos. Cero fallos de contraste.
- [x] Si aparecen fallos de contraste, **arreglarlos, no meterlos en la línea base**. Sospechoso
      número uno: `--nav-dim` de Vice. Es un porcentaje calibrado contra una superficie y cambiar
      el fondo lo invalida sin que nadie toque el token — con el vídeo cayó de 5,74:1 a 4,17:1.
      No hizo falta tocarlo: midio 4.74:1-9.63:1 en todas las escenas contra el fondo nuevo — el
      shader de tinta ya paso el techo de brillo con margen (Tarea 3), asi que el telon sigue
      siendo oscuro.
- [x] Revisar `:root[data-theme="vice"] .bg-theme::before` y `::after` en `src/style.css`. El
      `::before` es un lavado magenta-ámbar en `soft-light` al 48% que se puso cuando el fondo era
      un fixture sin color propio. Con dos tintas que ya deciden el color, **la hipótesis de
      partida es retirarlo**; decidir con el gate delante, no a ojo.
      Decidido con evidencia (A/B de pixeles + verify.py con y sin cada regla): `::before`
      retirado (diferencia <0.01/255, mismas 276 comprobaciones de contraste). `::after` se
      mantiene: sin el, "Telefono" en contacto cae de 4.28:1 a 3.67:1 (pasa AA large-text pero con
      mucho menos margen).
- [x] Commit. (`70c4ec4`)

### Tarea 5: Muaré

Es el riesgo propio de esta dirección. Requiere ojo, no solo números.

- [x] Capturar el fondo a `deviceScaleFactor` 1, 1.5 y 2, en reposo y a media travesía.
- [x] Mirar las capturas. Buscar bandas de interferencia, rejillas fantasma y puntos que cambian
      de tamaño de una zona a otra sin motivo.
      Sin muare ni parpadeo en 24 capturas (antes/despues). dsf 1.5 y 2 topan al mismo recorte de
      `shaderBackground.ts` (ratio 1.5) y salen identicos; la diferencia real esta entre DPR 1 (sin
      retina) y cualquier DPR>=1.5, no entre 1.5x y 3x.
- [x] Decidir con esas capturas si el paso se fija en píxeles de búfer o se escala con el
      `devicePixelRatio` real. Recordar que `shaderBackground.ts` acota el DPR a 1.5, así que en
      una pantalla de 3x el punto se ve el doble de grande que en una de 1.5x.
      Decisión: escalar con el ratio buffer/CSS YA RECORTADO (no el DPR crudo) — `pitch = 7.0 *
      (ratio/1.5)`. A ratio=1.5 (caso retina, el mas comun) da pitch=7.0 exacto, preservando la
      calibracion de brillo de las Tareas 2/3 sin tener que re-medirla. `uPixelRatio` anadido a
      `shaderBackground.ts` de forma aditiva (no-op para hyprGradient/caelestiaBlobs).
- [x] Anotar la decisión y su porqué en un comentario del fragmento.
- [x] Commit. (`2e0eb18`)

### Tarea 6: Movimiento reducido

- [x] Comprobar que con `prefers-reduced-motion` se pinta un solo fotograma y no arranca RAF
      (lo da `mountShaderBackground`, pero hay que verlo, no suponerlo).
      Confirmado: dos capturas del canvas con ~1.8s de diferencia, mismo scroll, mismo
      `reduced_motion="reduce"`, son bit a bit idénticas (mismo SHA-256). No hay RAF activo.
- [x] El fotograma estático se pinta en `STATIC_FRAME_TIME = 8.0` **con `uScroll` en su valor de
      ese instante**. Comprobar que ese fotograma es legible y representativo del tema, no un
      extremo del arco donde una sola tinta domina.
      Confirmado en scroll=0 (carga inicial): `balA = mix(0.26, 1.0, 0) = 0.26`, el ámbar no
      desaparece del todo — sampleo de píxeles del canvas aislado (sin overlay de DOM) muestra
      un tinte cálido tenue pero real junto al blob magenta dominante. No es un extremo
      degenerado (100%/0%); no hace falta ajustar `balM`/`balA`.
- [x] Capturas a 1440x900 y 390x844 con `reduced_motion="reduce"`.
- [x] Commit.

### Tarea 7: Limpieza de recursos

- [x] Comprobar que `destroy()` libera programa, búferes y RAF y que se llama en `pagehide`.
      Confirmado por lectura de código: `viceInk.ts` no envuelve nada — a diferencia de
      `viceHaze.ts` (que tenía su propio listener `pointermove` que limpiar), `viceInk.ts`
      solo lee `window.scrollY` desde una función pura (`readProgress`) que
      `mountShaderBackground` invoca en su propio `draw()`, modelo *pull*, sin
      `addEventListener` propio. La garantía de `mountShaderBackground` (borra buffer,
      shaders, programa, `WEBGL_lose_context`, cancela RAF, desconecta observers) basta.
      `src/main.ts:196-205` llama `backgroundHandle?.destroy()` en `pagehide`
      (no `beforeunload`) de forma incondicional.
- [x] Navegar y volver varias veces midiendo el número de contextos WebGL vivos. Cero fugas.
      12 ciclos de navegación real (`page.goto` → fondo montado → `page.goto("about:blank")`,
      que dispara `pagehide` de verdad) más un ciclo de `page.reload()`: siempre exactamente
      1 `<canvas>` en el DOM tras cada montaje, sin acumulación. Consola sin avisos de
      "too many active WebGL contexts" ni `CONTEXT_LOST_WEBGL` no intencionado (solo ruido
      de rendimiento de swiftshader, "GPU stall due to ReadPixels"). No se encontró fuga;
      no se tocó código. Detalle completo en
      `.superpowers/sdd/2026-08-04-vice-fondo-tinta/task-7-report.md`.
- [x] Commit.

### Tarea 8: Retirar `viceHaze`

**Solo con todo lo anterior en verde.** Dejar un fondo muerto en el repo es la deuda que este
proyecto ya arrastró con los fixtures `vice-hero.*` durante una semana.

- [x] Borrar `src/backgrounds/viceHaze.ts`.
- [x] Buscar y actualizar todas sus menciones: `src/themes/themes.css` (dos comentarios),
      `scripts/measure-obra-rail.py` (la ruta que bloquea para el A/B), `.claude/rules/verification.md`,
      `CLAUDE.md`, `MEMORY.md`, `.ai/memory.md`. `check_docs_references()` falla si sobrevive
      alguna.
      `.claude/rules/verification.md`/`CLAUDE.md`/`MEMORY.md` ya no citaban `viceHaze` (limpio).
      themes.css y measure-obra-rail.py actualizados a viceInk; tambien se encontro y actualizo
      `.docs/CURSOR-VICE.md` y `scripts/verify.py` (mismo patron). `.ai/memory.md` re-fechado a
      pasado, no borrado (registro historico).
- [x] `shaderBackground.ts` **se queda**: lo usan `caelestiaBlobs` y `hyprGradient`. Confirmado
      intacto, no aparece en el diff de esta tarea.
- [x] Comprobar que Hyprland y Caelestia siguen intactos (captura de los dos).
      Capturas 1440x900, canvas activo en ambos, 0 errores de consola.
- [x] Commit. (`7a3c631`)

### Tarea 9: Gates finales

- [x] `npm run build` y `npm run lint` verdes.
- [x] `scripts/verify.py` verde contra su línea base, sin fallos nuevos.
- [x] Capturas reales de las cinco escenas a 1440x900 y 390x844 con `?theme=vice`, cero errores
      de consola.
- [x] Actualizar `PROGRESS.json` conforme se avanza, no al final. <!-- el PROGRESS.json de la raiz
      pertenece a un plan distinto ya cerrado (Remotion, descartado); no se pisa, ver task-9-report.md -->
- [x] Escribir el registro de implementación al final del spec: los números finales de luminancia,
      la decisión de muaré y cualquier divergencia respecto a este plan.
- [x] Poner el spec en `Estado: implementado`.
- [!] **→ PEDIR REVISIÓN A AOSHI** sobre el sitio real, moviéndose, antes de proponer el merge.
      Es la lección del intento anterior: se enseñaron capturas durante toda una tarde y lo que
      decidió el rechazo fue verlo scrollear. <!-- fuera de alcance de la Tarea 9 mecanica: lo
      hace el controlador de la sesion directamente con Aoshi -->
- [!] Gate `lidia-naive-tester` y `vera-art-director`. <!-- fuera de alcance de la Tarea 9 mecanica -->
