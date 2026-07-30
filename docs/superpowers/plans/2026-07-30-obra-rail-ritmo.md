# Ritmo del carril de obra — plan de implementación

> **Para agentes:** SUB-SKILL OBLIGATORIA: usa `superpowers:subagent-driven-development`
> (recomendada) o `superpowers:executing-plans` para ejecutar tarea a tarea. Los pasos usan
> casillas (`- [ ]`) para el seguimiento.

**Objetivo:** sustituir el tween lineal único del carril de obra de Vice por una timeline
maestra con reposos y tránsitos con ease, y meter dentro las entradas de cartela para que
dejen de correr en su propio reloj.

**Arquitectura:** hoy hay dos relojes — el carril avanza en scroll (`scrub`) y las cartelas en
tiempo real (`duration` + `toggleActions`), acopladas solo por el disparo de
`containerAnimation`. Pasa a haber uno: una `gsap.timeline()` fijada al pin, con nueve
segmentos alternos (reposo/tránsito), y cada cartela como sub-timeline añadida en una posición
absoluta de esa maestra. `containerAnimation` desaparece del camino horizontal.

**Stack:** Vite 8, TypeScript estricto, GSAP 3 + ScrollTrigger, Lenis. Sin framework, sin
Three.js, sin framework de test.

## Spec

`docs/superpowers/specs/2026-07-30-obra-rail-ritmo-design.md`. Léelo entero antes de empezar:
contiene el dimensionado tween por tween y los cuatro puntos de re-verificación.

## Restricciones globales

Copiadas literales del spec y de `CLAUDE.md`. Aplican a **todas** las tareas.

- **Cero `gsap.from`.** Ya causó tres regresiones. Siempre `fromTo` con los dos extremos
  escritos a mano, y `Array.from(...)` para colecciones vivas.
- **Cero `any`.** `strict` está activo; usar `unknown` + guards.
- **Cero `console.log`** en código de producción.
- **Cero emojis** en código, docs y commits.
- `end` y todos los destinos son **funciones**, nunca números fijos, con
  `invalidateOnRefresh: true`.
- La escalera de `refreshPriority` no cambia: hero 2, carril 1, resto 0.
- `gsap.matchMedia()` con `(min-width: 901px) and (prefers-reduced-motion: no-preference)`
  para el carril, y `(max-width: 900px), (prefers-reduced-motion: reduce)` para la pila.
  Nunca un `if` con `matchMedia().matches`.
- Nada anclado a `[data-scene]` ni a un nodo con `display: contents`.
- Todo módulo de tema devuelve un handle con `destroy()`, llamado en `pagehide`.
- Un `transform` inline de GSAP gana siempre a una regla CSS de hover.

## Constantes del dimensionado

Van juntas en un solo bloque en `src/themes/vice.choreography.ts`, cerca de `scene3Slate`.
Todas en **unidades de timeline**, donde 1 unidad = un tránsito.

```ts
/** Un transito completo de una pieza a la siguiente. Unidad base de la timeline. */
const OBRA_TRANSIT = 1;
/** Reposo entre transitos, y en los dos bordes. 0.45 del transito (spec 2026-07-30). */
const OBRA_REST = 0.45;
/**
 * Px de scroll por px de innerWidth y por unidad de timeline. Con 5 obras esto da
 * 3.5 x innerWidth de presupuesto (5040px a 1440), frente a los 5760 de antes.
 */
const OBRA_SCROLL_PER_UNIT = 0.56;
/**
 * `scrub: 0.5`, no 1. Medido: el reposo solo se siente como reposo si el asentamiento
 * del scrub es mas corto que la meseta. Con scrub 1 (956ms de asentamiento) y una
 * meseta de 563ms, el carril se pasa el reposo entero recuperando retardo y la pieza
 * que peor se posa se queda en 147 px/s. Con 0.5 (480ms) baja a 18 px/s.
 */
const OBRA_SCRUB = 0.5;
```

## Cómo se prueba aquí

Este proyecto **no tiene framework de test**. El ciclo rojo-verde es de medida:

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
npm run preview -- --port 4173 &            # dejar corriendo
python3 scripts/measure-obra-rail.py        # los numeros, en el build de produccion
python3 scripts/verify.py                   # baseline: 12 fallos aceptados, sale 0
```

Trampas ya pagadas, no las repitas:

- **Medir en el build de producción, nunca en `dev`**: el HMR de Vite corrompe las medidas
  de ScrollTrigger y miente en los dos sentidos.
- **Nada de `page.screenshot()` para medir ritmo**: bloquea el compositor y adelanta la
  timeline.
- **`verify.py` cae con "Execution context was destroyed" si editas mientras corre.**
  Correrlo solo.
- **`free -h` antes de lanzar el arnés**: con menos de ~3GB libres el navegador muere a
  mitad. No es una regresión, es presión de memoria.
- Siempre `?theme=vice`: el tema se sortea por visita.

## Estructura de ficheros

Todo el cambio vive en **un fichero**, porque toda la coreografía de Vice vive en uno y
partirla ahora sería un refactor que nadie pidió.

- Modificar: `src/themes/vice.choreography.ts` — `buildSlate()` (635-753) y `scene3Slate()`
  (767-847)
- Modificar: `scripts/measure-obra-rail.py` — añadir la métrica de cartela entera
- Modificar: `docs/superpowers/specs/2026-07-30-obra-rail-ritmo-design.md` — registro de
  implementación, al final

---

### Tarea 1: El instrumento mide la cartela entera, no solo el lead

Hoy `measure-obra-rail.py` marca "entrada lista" cuando la opacidad del `.lead` llega a 0.99.
En el diseño nuevo el lead cierra al 52% de la ventana y la galería al 90%, así que medir solo
el lead haría el gate inalcanzable por construcción. Esta tarea va primero porque **sin ella no
hay forma de saber si las siguientes funcionan**.

**Ficheros:**
- Modificar: `scripts/measure-obra-rail.py`

**Interfaces:**
- Produce: cada entrada de `por_pieza` gana `adelanto_cartela_ms` y `adelanto_cartela_px`,
  calculados sobre la opacidad de `[data-gallery]` en vez de la del `.lead`. Las claves
  `adelanto_entrada_ms` / `adelanto_entrada_px` se conservan y pasan a llamarse en el
  informe "adelanto del lead".

- [x] **Paso 1: comprobar que el muestreador ya recoge la galería**

`SAMPLER` ya empuja `gal:` en cada fotograma (`gals.map(op)`). No hace falta tocarlo.
Verifícalo leyendo el bloque `SAMPLER` antes de seguir.

- [x] **Paso 2: calcular el cierre de la cartela entera en `analyse()`**

Junto al bloque que calcula `entry_done`, añadir:

```python
        # Cierre de la cartela ENTERA: la galeria es el ultimo elemento de la
        # entrada (posicion 0.56 + duracion 0.34 = 0.90 de la ventana). El `.lead`
        # cierra al 52%, asi que medir solo por el lead subestima el acoplamiento.
        slate_done = None
        for s in samples:
            v = s["gal"][i]
            if v is not None and v >= 0.99:
                slate_done = s["t"]
                break

        slate_ms = None
        slate_px = None
        if slate_done is not None and cross is not None and i > 0:
            slate_ms = cross["t"] - slate_done
            slate_px = abs(slate_ms / 1000.0 * real_speed)
```

- [x] **Paso 3: publicar las dos métricas**

En el `per_scene.append({...})`, añadir junto a las que ya hay:

```python
                "adelanto_cartela_ms": round(slate_ms, 1) if slate_ms is not None else None,
                "adelanto_cartela_px": round(slate_px, 1) if slate_px is not None else None,
```

- [x] **Paso 4: imprimirlas**

En `main()`, sustituir la línea de impresión por pieza por:

```python
                print(f"    pieza {ps['pieza']}: lead {ps['adelanto_entrada_px']} px antes, "
                      f"cartela entera {ps['adelanto_cartela_px']} px antes, "
                      f"permanencia {ps['permanencia_ms']} ms")
```

- [x] **Paso 5: correr contra el código ACTUAL y guardar la línea base**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run preview -- --port 4173 &
sleep 3
python3 scripts/measure-obra-rail.py --json /tmp/rail-antes.json
```

Esperado: `lead` entre 938 y 995 px a velocidad lenta, y `cartela entera` en un valor **menor**
(la galería cierra después que el lead, así que le queda menos recorrido). Anota los dos.
Si `cartela entera` sale `None` en todas las piezas, la galería no llega a opacidad 1 en la
ventana muestreada: revisa el `SAMPLER` antes de seguir.

- [x] **Paso 6: commit**

```bash
git add scripts/measure-obra-rail.py
git commit -m "test(obra): medir tambien el cierre de la cartela entera

El instrumento marcaba 'entrada lista' con la opacidad del .lead. En el diseno
nuevo el lead cierra al 52% de la ventana y la galeria al 90%, asi que el lead
solo no describe cuando la pieza aterriza montada."
```

---

### Tarea 2: La timeline maestra, con las cartelas dentro

Es la tarea grande y es **atómica a propósito**: `containerAnimation` exige un contenedor
lineal, así que en cuanto la maestra deja de serlo, las cartelas tienen que estar ya dentro.
Partirla deja el carril roto entre commits.

**Ficheros:**
- Modificar: `src/themes/vice.choreography.ts:606-847`

**Interfaces:**
- Consume: `splitChars(target: HTMLElement): HTMLElement[]` (línea 30), `Gsap`,
  `ScrollTriggerApi`.
- Produce:
  - `slateParts(scene: HTMLElement): SlateParts` — busca los nodos una sola vez.
  - `buildSlateStack(gsap: Gsap, scene: HTMLElement, ids: string[]): void` — el camino
    vertical de hoy, con los `gsap.from` convertidos a `fromTo`.
  - `buildSlateRail(gsap: Gsap, scene: HTMLElement, master: gsap.core.Timeline, index: number): void`
    — añade la sub-timeline de la cartela a la maestra.
  - `slateWindow(index: number): { at: number; len: number }`
  - `parallaxWindow(index: number): { at: number; len: number }`

- [x] **Paso 1: añadir el bloque de constantes**

Pégalo justo encima de `obraTriggerIds` (línea 606). Es el bloque completo de la sección
"Constantes del dimensionado" de este plan, con sus comentarios.

- [x] **Paso 2: extraer `slateParts`**

Sustituye las seis búsquedas sueltas de dentro de `buildSlate` por:

```ts
interface SlateParts {
  ordinal: HTMLElement | null;
  title: HTMLElement | null;
  lead: HTMLElement | null;
  meta: HTMLElement | null;
  masks: HTMLElement[];
  gallery: HTMLElement | null;
}

/** Los nodos animables de una cartela. Se buscan una vez y se reparten. */
function slateParts(scene: HTMLElement): SlateParts {
  return {
    ordinal: scene.querySelector<HTMLElement>("[data-ord]"),
    title: scene.querySelector<HTMLElement>("[data-title]"),
    lead: scene.querySelector<HTMLElement>(".lead"),
    meta: scene.querySelector<HTMLElement>("[data-meta]"),
    // Array.from: `querySelectorAll` devuelve una coleccion viva.
    masks: Array.from(scene.querySelectorAll<HTMLElement>("[data-mask]")),
    gallery: scene.querySelector<HTMLElement>("[data-gallery]"),
  };
}
```

- [x] **Paso 3: las ventanas de la cartela y del parallax**

```ts
/**
 * Ventana de la entrada de la cartela `index` dentro de la timeline maestra, en
 * unidades de timeline. Arranca al 35% de su transito y cierra 0.10 reposos
 * DESPUES de que la pieza quede encuadrada: la cartela se monta con la pieza, no
 * 950px antes como hacia el reloj de pared.
 *
 * La pieza 0 es un caso aparte: esta encuadrada desde que el pin engancha, asi
 * que su entrada ocupa el reposo de cabeza.
 */
function slateWindow(index: number): { at: number; len: number } {
  if (index === 0) return { at: 0, len: OBRA_REST * 0.8 };
  const base = OBRA_REST + (index - 1) * (OBRA_TRANSIT + OBRA_REST);
  return {
    at: base + 0.35 * OBRA_TRANSIT,
    len: 0.65 * OBRA_TRANSIT + 0.1 * OBRA_REST,
  };
}

/**
 * El parallax de la galeria cubre TAMBIEN el reposo, a proposito: mientras el
 * track esta quieto la captura sigue derivando unos pixeles con el dedo, asi que
 * la meseta nunca se lee como que la pagina se ha colgado. Es la mitigacion del
 * riesgo principal de un carril con reposos.
 */
function parallaxWindow(index: number): { at: number; len: number } {
  if (index === 0) return { at: 0, len: OBRA_REST };
  const base = OBRA_REST + (index - 1) * (OBRA_TRANSIT + OBRA_REST);
  const at = base + 0.35 * OBRA_TRANSIT;
  return { at, len: base + OBRA_TRANSIT + OBRA_REST - at };
}
```

- [x] **Paso 4: renombrar el camino vertical a `buildSlateStack` y matar los `gsap.from`**

Renombra `buildSlate` a `buildSlateStack`, quítale el parámetro `container` (ahora siempre es
la pila) y deja el `trigger` fijo en `{ trigger: scene, start: "top 76%", toggleActions: "play none none reverse" }`.
Convierte los cinco `gsap.from` a `fromTo` con los dos extremos a mano:

```ts
  if (p.ordinal) {
    gsap.fromTo(
      p.ordinal,
      { y: -70, scale: 1.35, opacity: 0 },
      { y: 0, scale: 1, opacity: 1, duration: 0.7, ease: "expo.out",
        scrollTrigger: { ...trigger, id: ids[0] } },
    );
  }
  if (p.lead) {
    gsap.fromTo(
      p.lead,
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.6, ease: "power2.out", delay: 0.16,
        scrollTrigger: { ...trigger, id: ids[2] } },
    );
  }
  if (p.meta) {
    gsap.fromTo(
      p.meta,
      { y: 14, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.6, ease: "power2.out", delay: 0.24,
        scrollTrigger: { ...trigger, id: ids[3] } },
    );
  }
  if (p.masks.length > 0) {
    gsap.fromTo(
      p.masks,
      { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0% 0 0)", duration: 0.9, ease: "power3.out", stagger: 0.1,
        delay: 0.32, scrollTrigger: { ...trigger, id: ids[4] } },
    );
  }
  if (p.gallery) {
    gsap.fromTo(
      p.gallery,
      { x: 46, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.85, ease: "power3.out", delay: 0.42,
        scrollTrigger: { ...trigger, id: ids[5] } },
    );
  }
```

El título sigue con `composeTitle(gsap, p.title, trigger, ids[1], 0.08)` y el parallax vertical
se queda como está (`yPercent -4 -> 4`, `scrub: 1`, ids[6]): la pila no está en el alcance.

- [x] **Paso 5: escribir `buildSlateRail`**

```ts
/**
 * Entrada de UNA cartela, acoplada al recorrido. Ya no crea ScrollTriggers: se
 * añade a la timeline maestra en una posicion absoluta, asi que avanza en pixeles
 * de scroll y no en segundos de reloj.
 *
 * `immediateRender: false` en todos los `fromTo`: dentro de una timeline, un
 * `fromTo` aplica su extremo inicial al CREARSE si no se le dice lo contrario, y
 * las cinco cartelas se pintarian de golpe en su estado de entrada al montar.
 */
function buildSlateRail(
  gsap: Gsap,
  scene: HTMLElement,
  master: gsap.core.Timeline,
  index: number,
): void {
  const p = slateParts(scene);
  const { at, len } = slateWindow(index);
  // Fraccion de la ventana -> unidades de timeline.
  const f = (fraction: number): number => fraction * len;

  const tl = gsap.timeline();

  if (p.ordinal) {
    tl.fromTo(
      p.ordinal,
      { y: -70, scale: 1.35, opacity: 0 },
      { y: 0, scale: 1, opacity: 1, duration: f(0.22), ease: "expo.out",
        immediateRender: false },
      f(0),
    );
  }
  if (p.title) {
    const chars = splitChars(p.title);
    tl.fromTo(
      chars,
      { yPercent: 118, opacity: 0, scaleY: 1.28 },
      { yPercent: 0, opacity: 1, scaleY: 1, transformOrigin: "50% 100%",
        duration: f(0.3), ease: "power3.out", stagger: f(0.012),
        immediateRender: false },
      f(0.06),
    );
  }
  if (p.lead) {
    tl.fromTo(
      p.lead,
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: f(0.26), ease: "power2.out", immediateRender: false },
      f(0.26),
    );
  }
  if (p.meta) {
    tl.fromTo(
      p.meta,
      { y: 14, opacity: 0 },
      { y: 0, opacity: 1, duration: f(0.24), ease: "power2.out", immediateRender: false },
      f(0.34),
    );
  }
  if (p.masks.length > 0) {
    tl.fromTo(
      p.masks,
      { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0% 0 0)", duration: f(0.36), ease: "power3.out",
        stagger: f(0.05), immediateRender: false },
      f(0.44),
    );
  }
  if (p.gallery) {
    tl.fromTo(
      p.gallery,
      { x: 46, opacity: 0 },
      { x: 0, opacity: 1, duration: f(0.34), ease: "power3.out", immediateRender: false },
      f(0.56),
    );
  }

  master.add(tl, at);

  if (p.gallery) {
    /*
     * Parallax en su propia ventana, que se solapa con el reposo. `xPercent` y no
     * `x`: la entrada de arriba ya anima `x` sobre este mismo nodo y dos tweens
     * sobre la misma propiedad se pisan.
     */
    const par = parallaxWindow(index);
    master.fromTo(
      p.gallery,
      { xPercent: -3.5 },
      { xPercent: 3.5, duration: par.len, ease: "none", immediateRender: false },
      par.at,
    );
  }
}
```

- [x] **Paso 6: reescribir el cuerpo horizontal de `scene3Slate`**

Sustituye el `gsap.to(track, {...})` y el `scenes.forEach(...)` de la rama
`(min-width: 901px) and (prefers-reduced-motion: no-preference)` por:

```ts
    const hops = scenes.length - 1;
    const travel = (): number => Math.max(track.scrollWidth - window.innerWidth, 0);
    /*
     * Presupuesto de scroll del pin. Ya NO es el recorrido lateral: el recorrido
     * sigue siendo `travel()` (5760px a 1440), pero se consume en menos scroll
     * porque hay mesetas. A 1440 esto da 5040px, 720 menos que antes.
     */
    const budget = (): number =>
      (hops * OBRA_TRANSIT + (hops + 1) * OBRA_REST) *
      OBRA_SCROLL_PER_UNIT *
      window.innerWidth;

    const master = gsap.timeline({
      scrollTrigger: {
        id: "vice-obra-rail",
        trigger: rail,
        pin: true,
        scrub: OBRA_SCRUB,
        start: "top top",
        end: () => `+=${budget()}`,
        invalidateOnRefresh: true,
        anticipatePin: 1,
        // Sin cambio: hero 2, carril 1, resto 0. Ver el comentario largo de abajo.
        refreshPriority: 1,
      },
    });

    // Reposo de cabeza: la pieza 1 deja de estar encuadrada justo en el instante
    // en que el pin engancha, que es lo que la dejaba sin llegada que acentuar.
    master.to({}, { duration: OBRA_REST });

    for (let i = 1; i <= hops; i++) {
      master.fromTo(
        track,
        { x: () => -(i - 1) * window.innerWidth },
        {
          // El ultimo destino se clampa a `travel()` exacto: con barra de scroll o
          // redondeo subpixel, `hops * innerWidth` no coincide con
          // `scrollWidth - innerWidth` y quedaria una franja de la pieza 5 fuera.
          x: () => (i === hops ? -travel() : -i * window.innerWidth),
          duration: OBRA_TRANSIT,
          ease: "power2.inOut",
          immediateRender: false,
        },
      );
      master.to({}, { duration: OBRA_REST });
    }

    scenes.forEach((scene, index) => buildSlateRail(gsap, scene, master, index));
```

Conserva **intacto** el comentario largo de `refreshPriority` que ya está en el fichero: sigue
siendo válido y documenta dos regresiones reales.

- [x] **Paso 7: la rama vertical llama a `buildSlateStack`**

```ts
  obraContext.add("(max-width: 900px), (prefers-reduced-motion: reduce)", () => {
    scenes.forEach((scene, index) => buildSlateStack(gsap, scene, obraTriggerIds(index)));
  });
```

`obraTriggerIds` se queda como está: la pila sigue necesitando sus siete ids. El spec dice que
sobran seis, y es cierto **solo para el camino horizontal**. Anótalo para el registro de
implementación.

- [x] **Paso 8: build y lint**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
```

Esperado: cero errores. Si `tsc` se queja de `gsap.core.Timeline`, el tipo viene de
`Gsap = typeof import("gsap").default`; usa `ReturnType<Gsap["timeline"]>`.

- [x] **Paso 9: medir y comparar contra los objetivos**

```bash
npm run preview -- --port 4173 &
sleep 3
python3 scripts/measure-obra-rail.py --json /tmp/rail-despues.json
```

| métrica | antes | objetivo |
|---|---|---|
| adelanto cartela entera | ~800 px | **≤ 40 px**, y sin dispersión entre las tres velocidades |
| adelanto del lead | 938-995 px | **≤ 260 px** |
| v lateral en el encuadre | 220-245 px/s | **≤ 20 px/s** en las cinco piezas |
| permanencia pieza 5 vs central | 33-40% | paridad |
| `distance` reportado | 5760 | sigue 5760 (el recorrido no cambia) |

El presupuesto del pin no lo imprime el instrumento; compruébalo aparte:

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=swiftshader'])
    pg=b.new_page(viewport={'width':1440,'height':900})
    pg.route('**/viceHaze*', lambda r: r.abort())
    pg.goto('http://localhost:4173/?theme=vice', wait_until='domcontentloaded'); pg.wait_for_timeout(8000)
    print(pg.evaluate('''() => {
      const r=document.querySelector('[data-obra-rail]');
      const sp=r.closest('.pin-spacer')||r;
      return {spacer: Math.round(sp.getBoundingClientRect().height), doc: document.documentElement.scrollHeight};
    }'''))
    b.close()
"
```

Esperado: `spacer` ~5940 (900 de viewport + 5040 de reserva) y `doc` ~11587.

- [x] **Paso 10: commit**

```bash
git add src/themes/vice.choreography.ts
git commit -m "feat(obra): timeline maestra con reposo, y cartelas acopladas al recorrido

El carril tenia dos relojes: avanzaba en scroll y las cartelas en tiempo real.
Ahora hay uno. Nueve segmentos alternos de reposo y transito con power2.inOut, y
cada cartela como sub-timeline en una posicion absoluta de la maestra.

containerAnimation exige un contenedor lineal (mapea _caScrollDist linealmente),
asi que segmentar el carril obligaba a meter las cartelas dentro: no eran dos
cambios, era uno."
```

---

### Tarea 3: Re-verificar lo que mide contra la distancia del pin

El pin pasa de reservar 5760 px a 5040. Cuatro cosas leen ese número y ninguna se entera sola.
Esta tarea no cambia código salvo que encuentre un fallo.

**Ficheros:**
- Verificar: `src/themes/vice.choreography.ts:901` (trigger de créditos), `:1200`
  (`railBound`), `:846` (`scrollrail:refresh`)

- [x] **Paso 1: la barra de orientación no miente**

Con `?theme=vice` a 1440x900, recorrer el documento entero con rueda simulada y comprobar que
la etiqueta anunciada coincide con la sección en pantalla en las fronteras. La región del
carril se estrecha del 54,1% al 51,3% del documento. El fallo que se busca es el ya conocido:
que anuncie "04 · Créditos" con el carril todavía ocupando la pantalla.

- [x] **Paso 2: el trigger de créditos no dispara con el carril fijado**

`start: "top 80%"` en la línea 901. Comprobar que su `start` en px cae **después** del `end`
del pin del carril:

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=swiftshader'])
    pg=b.new_page(viewport={'width':1440,'height':900})
    pg.route('**/viceHaze*', lambda r: r.abort())
    pg.goto('http://localhost:4173/?theme=vice', wait_until='domcontentloaded'); pg.wait_for_timeout(9000)
    print(pg.evaluate('''() => {
      const ST = window.ScrollTrigger || (window.gsap && window.gsap.core && window.ScrollTrigger);
      if (!ST) return 'ScrollTrigger no expuesto en window: comprobar a mano con markers';
      const rail = ST.getById('vice-obra-rail'), cr = ST.getById('vice-credits-roll');
      return rail && cr ? {railEnd: Math.round(rail.end), creditsStart: Math.round(cr.start),
                           margen: Math.round(cr.start - rail.end)} : 'ids no encontrados';
    }'''))
    b.close()
"
```

Esperado: `margen` positivo. Si sale el aviso de que `ScrollTrigger` no está en `window`
(probable, el bundle es de módulos), hazlo con `markers: true` temporalmente en los dos
triggers y una captura, y **quítalos antes de commitear**.

- [x] **Paso 3: el letterbox enciende y apaga en la frontera correcta**

Fue una regresión real. Recorrer la frontera fin-de-carril / inicio-de-créditos y confirmar
que las barras de `[data-letterbox]` entran durante la obra y salen al pasar a créditos.

- [x] **Paso 4: el arnés completo**

```bash
free -h | awk '/Mem:/{print "RAM libre:", $7}'   # >3GB antes de lanzar
python3 scripts/verify.py
```

Esperado: código de salida 0, con los 12 fallos de fixtures de la línea base y ninguno nuevo.
Si arreglas alguno de la base, quítalo con `--update-baseline` y revisa el diff.

- [x] **Paso 5: comprobar la pila vertical y el reduced-motion**

El camino que no se ha tocado también tiene que seguir vivo:

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=swiftshader'])
    for w,rm in [(1440,'reduce'),(390,'no-preference')]:
        ctx=b.new_context(viewport={'width':w,'height':844 if w==390 else 900}, reduced_motion=rm)
        pg=ctx.new_page(); pg.route('**/viceHaze*', lambda r: r.abort())
        pg.goto('http://localhost:4173/?theme=vice', wait_until='domcontentloaded'); pg.wait_for_timeout(7000)
        n=pg.evaluate('''() => {const s=[...document.querySelectorAll('[data-scene=\"obra\"]')];
          return s.filter(e=>Math.round(e.getBoundingClientRect().left)===Math.round(s[0].getBoundingClientRect().left)).length;}''')
        print(w, rm, '-> piezas apiladas en la misma columna:', n, '(esperado 5)')
        ctx.close()
    b.close()
"
```

- [x] **Paso 6: commit si hubo arreglos, si no seguir** — sin arreglos: los cuatro
  puntos leen dinamicamente `ScrollTrigger.getById("vice-obra-rail")` (railBound,
  refresco de la barra) o dependen del `onToggle` de escenas adyacentes (creditos,
  letterbox), ninguno tiene el numero 5760/5040 quemado. Sin commit de codigo.

```bash
git add -A && git commit -m "fix(obra): <lo que se rompio> tras acortar el pin"
```

---

### Tarea 4: Registro de implementación y cierre del spec

**Ficheros:**
- Modificar: `docs/superpowers/specs/2026-07-30-obra-rail-ritmo-design.md`

- [x] **Paso 1: rellenar el registro**

Sustituir la sección "Registro de implementación" por lo que pasó de verdad: en qué se desvió
la realidad del dimensionado y por qué. Como mínimo van estas dos, que ya se saben:

- `obraTriggerIds` no se reduce: la pila vertical sigue necesitando sus siete ids. El spec
  decía que sobraban seis y eso solo vale para el camino horizontal.
- El objetivo de M2 se partió en dos (cartela entera y `.lead`) porque el instrumento medía
  el lead y el dimensionado hace que cierre al 52% de la ventana.

Añade las que aparezcan al implementar. **Sin este registro el spec miente.**

- [x] **Paso 2: cambiar el `Estado:`**

De `pendiente de plan` a `implementado`. Vocabulario cerrado: `en diseno`,
`pendiente de plan`, `en ejecucion`, `implementado`, `descartado`. `verify.py` lo comprueba, y
también comprueba que las casillas de este plan estén todas marcadas si el spec dice
`implementado`.

- [x] **Paso 3: marcar todas las casillas de este plan**

En vivo, según se hacen. No en bloque al final: ticar de golpe pasos que nadie siguió uno a
uno falsifica el registro en vez de completarlo.

- [x] **Paso 4: gate documental**

```bash
python3 scripts/verify.py
```

Esperado: `[docs] estado de specs y planes` en verde y salida 0.

- [x] **Paso 5: commit**

```bash
git add docs/superpowers/
git commit -m "docs(obra): registro de implementacion del ritmo del carril"
```

---

## Gate final antes de merge

No es opcional y no lo hace quien implementó:

1. **Captura real** desktop 1440x900 y móvil 390x844, con `?theme=vice`, sobre el build de
   producción. Cero errores de consola, cero avisos de WebGL context lost.
2. `lidia-naive-tester` — flujo, desde la butaca de una reclutadora no técnica.
3. `vera-art-director` — ejecución visual. Los dos leen su `memory.md` antes de actuar.
4. Merge del worktree a `main`.

## Auto-revisión de este plan

- **Cobertura del spec:** timeline maestra (T2 p6), entrada de cartela dimensionada (T2 p5),
  parallax sin scrub propio y cubriendo el reposo (T2 p5), `scrub` 0.5 y `end` nuevo (T2 p6),
  cero `gsap.from` (T2 p4 y p5), los cuatro puntos de re-verificación (T3), registro y
  `Estado:` (T4). El fix de reduced-motion ya está en `main` (`dcc7998`).
- **Sin placeholders:** cada paso lleva el código o el comando literal.
- **Consistencia de tipos:** `slateParts`/`SlateParts`, `buildSlateStack`, `buildSlateRail`,
  `slateWindow`, `parallaxWindow`, `OBRA_TRANSIT`, `OBRA_REST`, `OBRA_SCROLL_PER_UNIT`,
  `OBRA_SCRUB` se usan con el mismo nombre en todas las tareas.
