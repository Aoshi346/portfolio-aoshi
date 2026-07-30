# HANDOFF — el ritmo del carril horizontal de obra (Vice)

> **RELEVADO el 2026-07-30 por `.docs/HANDOFF-obra-rail-ritmo-ejecucion.md`.** El encargo de
> este documento (medir antes de tocar) esta cumplido: los numeros viven en
> `docs/superpowers/specs/2026-07-30-obra-rail-ritmo-design.md` y el instrumento en
> `scripts/measure-obra-rail.py`. Dos de las sospechas de la seccion "Pistas" salieron
> confirmadas (la 1 y la 4), una se reformulo (la 2: no es retardo, es que el carril no
> aterriza en ningun sitio) y la 3 resulto ser 1440px por transicion, no ~1150 por pieza.
> Se conserva por su seccion de trampas de medicion, que sigue vigente.

> Brief para una sesion nueva. Escrito el 2026-07-29 al cerrar el rediseno de "Quien es".
> Todo numero de aqui esta medido contra el codigo o el navegador, no deducido. Lo que no
> esta medido se dice como sospecha, no como hecho.

## El encargo

El desplazamiento horizontal de la seccion de proyectos **funciona**: no hay bug que
arreglar. Lo que falla es el **ritmo**. La sensacion del usuario, literal: "va bien, pero
siento que el timing no es perfecto".

Eso significa que el trabajo NO es de correccion, es de afinado, y que el primer paso no
es tocar codigo: es **conseguir describir con numeros qué se siente mal**. Un encargo de
ritmo sin medida previa acaba en tanteo.

## Donde vive

- `src/themes/vice.choreography.ts` — toda la coreografia de Vice, en gestos numerados.
  - `scene3Slate()` — monta el carril. Es el punto de entrada del encargo.
  - `buildSlate()` — la entrada de cada una de las cinco cartelas, encadenada al carril.
  - `obraTriggerIds(index)` — ids fijos por escena, para poder matarlos.
- `src/sections/obra/projectScene.ts` — la plantilla de escena, instanciada una vez por
  proyecto. Las cinco escenas de obra son la MISMA plantilla, no cinco ficheros.
- `src/main.ts` — compone las escenas dentro de `[data-obra-track]`, dentro de
  `[data-obra-rail]`.
- `src/style.css` y `src/themes/themes.css` — geometria del carril y de las cartelas.
- `src/data/content.ts` — `caseStudies`, que es lo que define cuantas escenas hay.

## Como esta montado hoy (medido)

```
[data-obra-rail]   pin: true, start "top top", end "+=distance()"
  [data-obra-track]  x: 0 -> -distance(),  ease: "none",  scrub: 1
    5 x [data-scene="obra"]
```

- `distance() = max(track.scrollWidth - window.innerWidth, 0)`. **Reserva ~5760px de
  recorrido de scroll** para el pin.
- `ease: "none"` y `scrub: 1`: el mapeo scroll -> desplazamiento lateral es **lineal**, con
  1s de suavizado de scrub.
- `end` y el destino son **funciones**, no numeros, con `invalidateOnRefresh: true`: se
  recalculan en cada refresh (resize, fuentes, imagenes que acaban de cargar). Eso ya
  arreglo que el carril se quedara corto o se pasara de largo.
- El reparto por breakpoint lo hace `gsap.matchMedia()`, no un `if` con
  `matchMedia().matches`: por encima de 901px hay carril horizontal, por debajo no.
  Respetalo — cruzar el breakpoint con un `if` deja el pin colgado.
- Las cartelas se encadenan al tween `horizontal` (se le pasa a `buildSlate`), asi que su
  ritmo depende del del carril. Un cambio en el carril las mueve todas.

## Pistas, NO conclusiones

Sospechas razonables sobre de donde puede venir la sensacion de mal ritmo. Ninguna esta
verificada — la sesion nueva las confirma o las descarta **midiendo**, no razonando:

1. **El `ease: "none"` es lineal de punta a punta.** Cinco escenas recorridas a velocidad
   constante no tienen acentos: ni entrada, ni salida, ni pausa sobre cada pieza. Puede que
   lo que se percibe como "timing" sea en realidad ausencia de articulacion.
2. **`scrub: 1` es un segundo de inercia.** Suaviza, pero tambien mete retardo entre lo que
   hace el dedo y lo que hace la pantalla, y ese retardo se nota mas cuanto mas largo es el
   recorrido. Convive ademas con la inercia propia de Lenis (`duration: 1.15`): son DOS
   suavizados encadenados.
3. **5760px para cinco piezas** son ~1150px de scroll por pieza. Si el usuario siente que
   "cuesta", puede ser distancia, no curva.
4. **Las cartelas encadenadas** pueden estar entrando en un punto del recorrido lateral que
   no coincide con el momento en que su pieza esta realmente centrada en pantalla.
5. **El primer y el ultimo tramo** son los sospechosos habituales en un carril fijado: la
   entrada al pin y la salida suelen ser donde el ritmo se rompe.

## Constraints que NO se tocan

Todas salieron de una regresion real y estan razonadas en comentarios del codigo:

- **La escalera de `refreshPriority`: hero 2, carril de obra 1, resto 0**, descendente
  segun el orden del documento. No es decoracion. Medido: sin la prioridad del carril, la
  barra de orientacion anunciaba "05 · Fundido" con el carril ocupando la pantalla entera;
  y si el carril se refrescara antes que el hero, situaria su inicio 1605px antes de tiempo
  y quedaria fijado encima de "Quien es". **Si anades un pin, entra en la escalera.**
- **Cero `gsap.from`.** Deduce un extremo leyendo el DOM y ya causo tres regresiones.
  `fromTo` con los dos extremos a mano, `Array.from(...)` para colecciones vivas.
- **Un `transform` inline de GSAP gana siempre a una regla CSS.** Si un nodo recibe tween,
  su hover se anima en un hijo o en un envoltorio.
- **`invalidateOnRefresh` y los `end`/destino como funcion se quedan.** Volver a numeros
  fijos reintroduce el carril corto/largo al cambiar el ancho del track.
- **`gsap.matchMedia()` para el reparto por breakpoint**, no un `if`.
- **`prefers-reduced-motion`:** `initScrollReveal` hace early-return y ni importa GSAP. Lo
  que deba morir con `reduce` va en GSAP; lo que deba sobrevivir, en CSS con su propia
  media query.
- **Limpieza:** todo modulo de tema devuelve un handle con `destroy()`, llamado en
  `pagehide`. Borrar programa y buffers de WebGL, cancelar rAF, matar timelines.
- **`display: contents` borra la caja**, asi que ni una timeline ni un ScrollTrigger pueden
  anclarse a ese nodo: un rect a cero se mide en `top = 0` del documento y el trigger
  dispara al cargar, sin error ni aviso.
- **Ningun trigger de entrada de Vice se ancla a `[data-scene]`**: esa caja lleva 202,5px
  de padding de tema a 1440x900 y las escenas van centradas, asi que el primer pixel util
  puede caer bajo el pliegue. Anclar al primer nodo de contenido.

## Trampas de medicion — las de ritmo son las peores

Estas son las que aplican DIRECTAMENTE a este encargo. Leerlas antes de medir:

- **`page.screenshot()` en headless PERTURBA GSAP:** bloquea el compositor y la timeline
  salta hacia delante. **Para medir ritmo no sirven las capturas.** Muestrea
  `tl.progress()` desde dentro de la pagina; para fotogramas concretos, `tl.pause()` mas
  `tl.progress(x)`.
- **Verifica en el build de produccion, NUNCA en `dev`**, cualquier cosa de ScrollTrigger:
  el HMR de Vite corrompe sus medidas y miente en los dos sentidos. `npm run build` y
  `npm run preview`.
- **Lenis sigue desplazando despues de `scrollTo`/`scrollIntoView`.** Replica
  `_scroll_to_and_settle()` de `scripts/verify.py`: rueda simulada y espera a que
  `window.scrollY` deje de cambiar. Un `scrollTo` mueve el scroll nativo pero **no** el
  target interno de Lenis. Esta trampa se piso DOS veces en la sesion anterior, la segunda
  despues de haberla arreglado en el arnes.
- **Con `--use-gl=swiftshader` el rAF va lentisimo** y las animaciones parecen ir por
  detras del raton o quedarse cortas. Eso es el headless, no el codigo. Para depurar layout
  sin ese coste, bloquea el shader: `page.route("**/viceHaze*", r => r.abort())`.
- **A/B antes que hipotesis.** Si sospechas de un modulo, bloquealo con `page.route(...)` y
  vuelve a medir. Descarta o confirma en un minuto, sin tocar codigo.
- **Para comparar contra `HEAD` usa `git worktree add`, NUNCA `git stash`.** Un
  `stash --include-untracked` ya se llevo por delante una sesion entera.
- **El arnes necesita RAM.** Con menos de ~3GB libres el navegador muere a mitad con
  *execution context was destroyed*: es presion de memoria, no una regresion. `free -h`
  antes de lanzarlo.

## Estado del arnes

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"   # Node del sistema es viejo; Vite 8 exige >=20
npm run build && npm run lint
python3 scripts/verify.py
npm run preview   # y verificar SIEMPRE con ?theme=vice
```

- `scripts/verify.py` tiene una mitad **sin navegador** (deriva de la documentacion y
  coherencia spec/plan) que corre en segundos, y otra con navegador real.
- Los fallos aceptados viven en `scripts/verify-baseline.json`: **hoy 12**, todos rellenos
  de imagen en `public/media/`. El arnes sale **0** mientras la ejecucion coincida con esa
  lista, y **1** si aparece uno nuevo O si arreglas uno sin quitarlo de ahi. Regenerar con
  `python3 scripts/verify.py --update-baseline`.
- `README.md` esta en `DOC_FILES`, asi que el gate documental lo vigila.
- Al cerrar, el spec necesita una linea `Estado:` del vocabulario cerrado (`en diseno`,
  `pendiente de plan`, `en ejecucion`, `implementado`, `descartado`), y si cita un plan, sus
  casillas tienen que concordar.

## Metodo que funciono en la sesion anterior

No es burocracia: cada paso evito un error concreto.

1. **`superpowers:brainstorming` con companion visual.** Mockups **vivos y servidos**,
   nunca capturas ni artifacts. Es preferencia establecida del usuario, no una opcion.
   Para un encargo de RITMO esto importa el doble: un mockup estatico no puede mostrar
   timing. Los mockups tienen que **moverse**.
2. **`especialista-animaciones` y `especialista-ux-ui` en paralelo sobre el mismo brief**, y
   despues **convergencia**. El usuario quiere **opciones que los DOS firmen, no un ranking
   con descartes** — rechazo el formato podio tres veces. Cuando los dos coinciden en un
   defecto, deja de ser opinion y toca cambiar la composicion; cuando solo lo dice uno, se
   discute.
3. **No tocar `src/` hasta que el usuario elija direccion.**
4. **Spec en `docs/superpowers/specs/`** con la coreografia dimensionada tween por tween
   (posicion, extremos, duracion, ease, stagger) ANTES de implementar. Y al terminar, un
   **registro de implementacion** al final del spec diciendo en que se desvio la realidad y
   por que: sin el, el spec miente. En la sesion anterior se desvio en once puntos.
5. **Worktree aparte para implementar** (`git worktree add`), y merge a `main` al final.
6. **Gate final: `lidia-naive-tester` (flujo) y `vera-art-director` (ejecucion visual).**
   Los dos con memoria historica cross-version; leen su `memory.md` antes de actuar. En la
   sesion anterior encontraron un P0 que yo no habia visto y tres bugs propios.

### Modelo — pinealo SIEMPRE

- Brainstorm, convergencia de especialistas y decisiones de diseno: **modelo top**.
- Implementacion (CSS, reescritura acotada de una funcion ya dimensionada): **Sonnet**.
- **Los subagentes HEREDAN el modelo de la sesion**: un fan-out sin pinear desde una sesion
  top **factura todo a tarifa top**. Pasa `model:` en cada `Agent`/`Task`/`Workflow` salvo
  que la subtarea exija el top.
- Escalar, no habitar: consulta arriba puntualmente, no por costumbre.

## Cosas que quedaron abiertas y NO son de este encargo

Por si aparecen de paso; no las metas en el alcance sin decirlo:

- El sitio **no tiene navegacion ni un solo enlace en "Quien es"**, y hay ~8600px de scroll
  hasta el `mailto:`. Es el hallazgo que el naive test puso por encima de todo: "me
  convenciste y no me dejaste actuar". Decision de producto.
- `.about-pair` no es enfocable, asi que su gesto firma no existe para teclado ni tactil.
  Lo marcaron los dos criticos. Va junto con la decision del chip de disponibilidad como
  enlace: las dos meten la seccion en el orden de tabulacion por primera vez.
- El retrato es un avatar de GitHub hot-linked: se rompe si la red del visitante bloquea
  ese dominio.
- `scene5Contact` compensa a mano el bug del ancla en `[data-scene]` con un `"top 68%"`
  empirico. Merece la misma correccion que se aplico en about.
- **Sin deploy.** El repo ya es publico: https://github.com/Aoshi346/portfolio-aoshi
