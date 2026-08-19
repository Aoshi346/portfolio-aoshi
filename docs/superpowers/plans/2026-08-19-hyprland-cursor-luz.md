# La luz de mano — plan de implementación

> **Para ejecutores agénticos:** SUB-SKILL OBLIGATORIA: usa `superpowers:subagent-driven-development`
> (recomendada) o `superpowers:executing-plans` para ejecutar este plan tarea a tarea. Los pasos
> usan casillas (`- [ ]`) para el seguimiento.

**Objetivo:** dar al tema Hyprland un cursor propio que no dibuja un objeto sino que ilumina: un
charco de luz recortado al elemento pulsable bajo el puntero, más un punto caliente que marca la
mano.

**Arquitectura:** un módulo nuevo `src/components/hyprCursor.ts` con el mismo contrato que
`viceCursor.ts` (función de montaje que devuelve un handle con `destroy()`), un solo `<canvas>` a
pantalla completa y un solo `requestAnimationFrame`. La lista blanca de `cursor: none` vive en
`themes.css` bajo `:root[data-theme="hyprland"]` y solo aplica cuando el JS ha añadido
`.hypr-cursor-ready`. La puerta de montaje se añade en `src/main.ts` junto a la de Vice.

**Stack:** Vite + TypeScript estricto + Canvas 2D. **Sin GSAP** en este módulo: la interpolación es
un lerp por fotograma sobre un único número y meter una librería de timelines para eso sería peor.

**Spec:** `docs/superpowers/specs/2026-08-19-hyprland-cursor-luz-design.md`

## Restricciones globales

- **Vice no se toca.** `src/components/viceCursor.ts` se lee como contrato; no se edita ni una
  línea. El bloque `Cursor propio de Vice` de `themes.css` (líneas 6117-6150) tampoco.
- **Caelestia no se toca.** No recibe cursor propio; se comprueba que sigue igual.
- **`src/data/content.ts` no cambia.** Este dispositivo no escribe ni un carácter en pantalla.
- **Cero `any`.** `strict` está activo; usar `unknown` con guardas si hace falta.
- **Cero `console.log`.** Solo `console.error` justificado.
- **Sin `gsap.from`** (no aplica aquí, pero la regla sigue vigente en el repo).
- **Cero emojis** en código, docs y commits.
- **Nada de texto, números, etiquetas ni hex en pantalla.** Es el motivo por el que murieron las
  tres direcciones de la ronda anterior.
- Tokens de Hyprland, literales, de `themes.css`: `--void #0b0404`, `--text #ffeae6`,
  `--l1 #ff5a34`, `--l2 #e01d3c`, `--l3 #ffa03c`, `--catch #ffd9cc`.
- Verificación siempre contra el **build de producción servido** (`npx vite preview --port 4173`),
  nunca contra `npm run dev`: el HMR corrompe las medidas de layout y de ScrollTrigger.
- El tema se sortea por visita: **siempre** `?theme=hyprland` en las URLs de verificación.

---

## Estructura de ficheros

| Fichero | Responsabilidad |
|---|---|
| `src/components/hyprCursor.ts` | **Crear.** Todo el dispositivo: estado del puntero, resolución de zona, bucle de pintado, handle `destroy()`. |
| `src/themes/themes.css` | **Modificar.** Bloque nuevo al final: lista blanca de `cursor: none` y el estilo del lienzo. No se toca ningún bloque existente. |
| `src/main.ts` | **Modificar.** Puerta de montaje del cursor de Hyprland junto a la de Vice, y la llamada a `destroy()` en el `pagehide` que ya existe. |
| `scripts/measure-cursor-luz.py` | **Crear.** Arnés Playwright independiente: estados, apagado en zona nativa, no-montaje en móvil y con movimiento reducido, limpieza, y contraste por glifo. |

---

### Task 1: el arnés, antes que el módulo

En este repo no hay tests unitarios: cada dispositivo tiene su arnés Playwright en `scripts/`, y el
arnés se escribe **antes** para que empiece en rojo por la razón correcta.

**Ficheros:**
- Crear: `scripts/measure-cursor-luz.py`

**Interfaces:**
- Consume: nada.
- Produce: el ejecutable `python3 scripts/measure-cursor-luz.py --base http://localhost:4173`, que
  sale **0** sin fallos y **1** con al menos uno. Las tareas 3, 4 y 5 lo usan como puerta.

- [x] **Paso 1: escribir el arnés**

```python
"""Arnes del cursor "luz de mano" de Hyprland.

Cada asercion nace de un fallo real ya pagado en este repo:
  1. El lienzo EXISTE en Hyprland y NO existe en Vice ni en Caelestia. Sin
     esto el arnes sale verde con el cursor apagado: el patron aditivo se ha
     roto cuatro veces en este proyecto por olvidar el caso base.
  2. El charco se enciende sobre un pulsable y NO se enciende sobre texto
     corrido. Es la unica asercion que prueba el reparto de senal.
  3. Tras desplazar con el raton QUIETO, el estado se recalcula. Medido en
     Vice: parado sobre texto tras desplazar, la marca seguia dibujandose
     encima del I-beam.
  4. Con `prefers-reduced-motion: reduce` no hay lienzo en el DOM.
  5. En movil (390x844) el modulo NO se descarga. Se comprueba por red, no
     por inspeccion visual: un modulo cargado y luego oculto sigue costando.
  6. `destroy()` deja el DOM sin lienzo y sin la clase `.hypr-cursor-ready`.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

VIEWPORT_ESCRITORIO = {"width": 1440, "height": 900}
VIEWPORT_MOVIL = {"width": 390, "height": 844}
LIENZO = "canvas.hypr-cursor-canvas"


def abrir(p, base, tema="hyprland", viewport=None, reduced=False):
    navegador = p.chromium.launch(
        headless=True, args=["--no-sandbox", "--use-gl=swiftshader"]
    )
    contexto = navegador.new_context(
        viewport=viewport or VIEWPORT_ESCRITORIO,
        reduced_motion="reduce" if reduced else "no-preference",
    )
    pg = contexto.new_page()
    pg.goto(f"{base}/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(4000)
    return navegador, pg


def hay_lienzo(pg) -> bool:
    return pg.evaluate(f"() => document.querySelector('{LIENZO}') !== null")


def potencia(pg) -> float:
    """Potencia del charco publicada por el modulo. 0 = apagado."""
    return pg.evaluate("() => window.__hyprCursor__ ? window.__hyprCursor__.pot() : -1")


def apuntar(pg, selector):
    caja = pg.locator(selector).first.bounding_box()
    pg.locator(selector).first.scroll_into_view_if_needed()
    pg.wait_for_timeout(600)
    caja = pg.locator(selector).first.bounding_box()
    pg.mouse.move(caja["x"] + caja["width"] * 0.4, caja["y"] + caja["height"] / 2, steps=8)
    pg.wait_for_timeout(500)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()
    fallos = []

    with sync_playwright() as p:
        # 1. presencia por tema
        for tema, espera in (("hyprland", True), ("vice", False), ("caelestia", False)):
            nav, pg = abrir(p, args.base, tema)
            if hay_lienzo(pg) is not espera:
                fallos.append(f"lienzo en {tema}: {hay_lienzo(pg)}, esperado {espera}")
            nav.close()

        nav, pg = abrir(p, args.base, "hyprland")

        # 2. reparto de senal
        apuntar(pg, ".obra-titular, [data-cartel] button, button")
        if potencia(pg) < 0.8:
            fallos.append(f"charco apagado sobre pulsable: pot={potencia(pg)}")
        apuntar(pg, "p")
        if potencia(pg) > 0.05:
            fallos.append(f"charco encendido sobre texto: pot={potencia(pg)}")

        # 3. estado rancio tras desplazar sin mover el raton
        apuntar(pg, "button")
        pg.evaluate("window.scrollBy(0, 900)")
        pg.wait_for_timeout(900)
        pg.mouse.move(720, 450, steps=2)
        pg.wait_for_timeout(400)
        bajo = pg.evaluate(
            "() => { const e = document.elementFromPoint(720, 450);"
            " return e ? (e.closest('button, a[href]:not([target=\"_blank\"])') ? 'pulsable' : 'otro') : 'nada'; }"
        )
        pot = potencia(pg)
        if bajo != "pulsable" and pot > 0.05:
            fallos.append(f"charco rancio tras desplazar: bajo={bajo} pot={pot}")
        nav.close()

        # 4. movimiento reducido
        nav, pg = abrir(p, args.base, "hyprland", reduced=True)
        if hay_lienzo(pg):
            fallos.append("hay lienzo con prefers-reduced-motion: reduce")
        nav.close()

        # 5. movil: el modulo no se descarga
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        contexto = navegador.new_context(
            viewport=VIEWPORT_MOVIL, has_touch=True, is_mobile=True
        )
        pedidos = []
        pg = contexto.new_page()
        pg.on("request", lambda r: pedidos.append(r.url))
        pg.goto(f"{args.base}/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(4000)
        if any("hyprCursor" in u for u in pedidos):
            fallos.append("el modulo del cursor se descarga en movil")
        navegador.close()

        # 6. limpieza
        nav, pg = abrir(p, args.base, "hyprland")
        pg.evaluate("() => window.__hyprCursor__ && window.__hyprCursor__.destroy()")
        pg.wait_for_timeout(300)
        if hay_lienzo(pg):
            fallos.append("destroy() deja el lienzo en el DOM")
        if pg.evaluate("() => document.documentElement.classList.contains('hypr-cursor-ready')"):
            fallos.append("destroy() deja la clase hypr-cursor-ready")
        nav.close()

    for f in fallos:
        print(f"FALLO: {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Paso 2: ejecutar el arnés y comprobar que falla por la razón correcta**

```bash
npm run build && npx vite preview --port 4173 &
sleep 3
python3 scripts/measure-cursor-luz.py --base http://localhost:4173
```

Esperado: **FALLA** con `lienzo en hyprland: False, esperado True` y varios `pot=-1`. Si falla por
un error de Python (import, selector inválido), arreglarlo antes de seguir: el arnés tiene que
fallar por ausencia del módulo, no por estar roto.

- [x] **Paso 3: commit**

```bash
git add scripts/measure-cursor-luz.py
git commit -m "test(hyprland): arnes del cursor luz de mano, en rojo"
```

---

### Task 2: la lista blanca de CSS

Va antes que el módulo a propósito: es la pieza que decide qué señales del sistema se conservan, y
sin ella el módulo pintaría el charco con el cursor nativo encima.

**Ficheros:**
- Modificar: `src/themes/themes.css` (bloque nuevo **al final del fichero**, sin tocar nada existente)

**Interfaces:**
- Consume: la clase `hypr-cursor-ready` en `<html>`, que pone la tarea 3.
- Produce: la clase CSS `.hypr-cursor-canvas` que usa el módulo, y el contrato de qué elementos
  pierden el cursor nativo.

- [x] **Paso 1: añadir el bloque al final de `src/themes/themes.css`**

```css
/* =====================================================================
 * Cursor propio de Hyprland — la luz de mano
 *
 * `.hypr-cursor-ready` la pone el JS SOLO tras montar con exito. Si el
 * modulo no carga, no existe ninguna de estas reglas y el cursor del
 * sistema queda intacto: ni una senal depende del JavaScript.
 *
 * La lista blanca se apoya en que `cursor` solo se hereda cuando el
 * elemento no declara el suyo. `.gallery-track` declara `grab` y los
 * `<a>` reciben `pointer` de la hoja del navegador, asi que el
 * `cursor: none` del lienzo NO les llega — hay que apuntarlos uno a uno.
 *
 * `.scene-nav-trigger` y `.scene-index-row` van escritos A MANO porque
 * `sceneNav` monta fuera de `[data-scene]` (`sceneNav.ts:327-328` cuelga
 * disparador y panel de la raiz). Sin estas dos lineas el cursor "se
 * rompe" en cuanto el puntero sale del contenido.
 * ===================================================================== */

.hypr-cursor-ready:root[data-theme="hyprland"] [data-scene] {
  cursor: none;
}

/* Texto: recupera el I-beam que la herencia del lienzo le habia quitado.
 * Ocultarlo borraria la senal de que esto se selecciona y se copia. */
.hypr-cursor-ready:root[data-theme="hyprland"]
  [data-scene]
  :is(p, li, dd, dt, figcaption, blockquote) {
  cursor: auto;
}

/* Opt-in explicito de los pulsables que la luz sustituye. El enlace
 * externo queda fuera aposta: abre pestana nueva y la certeza de "esto es
 * un enlace real" no se toca. `.gallery-track` tampoco entra: su `grab` es
 * la unica pista de que la galeria se arrastra. */
.hypr-cursor-ready:root[data-theme="hyprland"]
  [data-scene]
  :is(button, a[href]:not([target="_blank"])) {
  cursor: none;
}

/* Fuera de las escenas: la navegacion, que monta en la raiz. */
.hypr-cursor-ready:root[data-theme="hyprland"] :is(.scene-nav-trigger, .scene-index-row) {
  cursor: none;
}

.hypr-cursor-canvas {
  position: fixed;
  inset: 0;
  z-index: 70;
  pointer-events: none;
}

/* Cinturon y tirantes: si el modulo llegara a montar bajo movimiento
 * reducido, el lienzo no se pinta igualmente. La puerta real esta en
 * `main.ts`; esto es la red por debajo. */
@media (prefers-reduced-motion: reduce) {
  .hypr-cursor-canvas {
    display: none;
  }
}
```

- [x] **Paso 2: comprobar que Vice no se ha movido**

```bash
npm run build
grep -c "vice-cursor-ready" src/themes/themes.css
```

Esperado: build en verde y el `grep` sigue devolviendo **6** (las seis apariciones del bloque de
Vice, intactas). Medido el 2026-08-19: son 6.

- [x] **Paso 3: commit**

```bash
git add src/themes/themes.css
git commit -m "feat(hyprland): lista blanca de cursor para la luz de mano"
```

---

### Task 3: el módulo

**Ficheros:**
- Crear: `src/components/hyprCursor.ts`

**Interfaces:**
- Consume: `.hypr-cursor-canvas` de la tarea 2.
- Produce:
  - `export interface HyprCursorHandle { destroy: () => void }`
  - `export function mountHyprCursor(host: HTMLElement): HyprCursorHandle`
  - Sonda de verificación `window.__hyprCursor__` con `{ pot: () => number; destroy: () => void }`,
    que consume el arnés de la tarea 1.

- [x] **Paso 1: escribir `src/components/hyprCursor.ts`**

```ts
export interface HyprCursorHandle {
  destroy: () => void;
}

/*
 * Cursor propio de Hyprland: no dibuja un objeto, ilumina.
 *
 * El charco de luz existe SOLO dentro de lo que se puede pulsar, recortado a
 * canto vivo por el borde del elemento. Sobre texto corrido no se enciende
 * nada. La lectura es anterior al lenguaje: lo que se ilumina responde.
 *
 * Reparto de senales, identico al ya cerrado en Vice porque el problema es el
 * mismo — sustituir el puntero es legitimo, borrar las otras senales no:
 *
 *   `pointer`  -> lo sustituye esta luz.
 *   `grab` / `grabbing` (`.gallery-track`) -> NATIVOS. Unica pista de que la
 *                 galeria se arrastra.
 *   I-beam en texto -> NATIVO. Ocultarlo quita la senal de que se selecciona.
 *   Enlaces externos (`target="_blank"`) -> NATIVOS. Abren pestana nueva.
 *
 * Diez direcciones cayeron antes que esta. Las tres ultimas (`hyprpicker`,
 * `col.active_border`, `slurp`) eran autenticas y se descartaron por escribir
 * medidas y etiquetas en pantalla: un cursor no puede tener manual. De ahi la
 * regla dura de este modulo — NO se dibuja ni un carater, ni un numero, ni
 * nada que cruce la pagina fuera del elemento apuntado.
 */

// Zonas donde manda el navegador y esta luz se apaga.
const NATIVE_ZONE = '.gallery-track, a[target="_blank"], p, li, dd, dt, figcaption, blockquote';
// Pulsables que esta luz ilumina. El enlace externo queda fuera aposta.
const PRESSABLE = 'button, a[href]:not([target="_blank"])';

// Suavizado de la POTENCIA, no de la posicion. La posicion del puntero se
// escribe sin suavizar: un cursor con inercia miente sobre donde esta el
// raton, y en creditos hay 23 dianas contiguas donde eso se lee como retraso.
const POT_SMOOTHING = 0.22;

// Radio del charco. Lo dicta la altura del elemento, no la seccion: asi una
// fila de creditos de 35px y un titular de 74px reciben la misma ley y se ven
// distintos sin que nadie programe casos por seccion.
const RADIO_FACTOR = 2.4;
const RADIO_MINIMO = 120;
const RADIO_PULSADO = 1.25;

// La mano.
const PUNTO_REPOSO = 3.2;
const PUNTO_PULSADO = 2.4;

// El DPR se acota: por encima de 2 el coste de pintado sube sin que se note.
const DPR_MAXIMO = 2;

export function mountHyprCursor(host: HTMLElement): HyprCursorHandle {
  const controller = new AbortController();
  const { signal } = controller;

  const canvas = document.createElement("canvas");
  canvas.className = "hypr-cursor-canvas";
  canvas.setAttribute("aria-hidden", "true");
  const ctx = canvas.getContext("2d");
  // defensive: sin contexto 2D no hay dispositivo posible. Se sale sin montar
  // y sin poner la clase, asi que el cursor del sistema queda intacto.
  if (!ctx) {
    return { destroy: (): void => undefined };
  }
  host.append(canvas);

  let pointerX = 0;
  let pointerY = 0;
  let visible = false;
  let onNative = false;
  let pressable: HTMLElement | null = null;
  let rect: DOMRect | null = null;
  let pressed = false;
  let stale = false;
  let pot = 0;
  let frame = 0;
  let dpr = 1;

  const resize = (): void => {
    dpr = Math.min(window.devicePixelRatio || 1, DPR_MAXIMO);
    canvas.width = Math.floor(window.innerWidth * dpr);
    canvas.height = Math.floor(window.innerHeight * dpr);
    canvas.style.width = `${window.innerWidth}px`;
    canvas.style.height = `${window.innerHeight}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  resize();

  const resolveZone = (target: Element): void => {
    onNative = target.closest(NATIVE_ZONE) !== null;
    pressable = onNative ? null : target.closest<HTMLElement>(PRESSABLE);
    rect = pressable ? pressable.getBoundingClientRect() : null;
  };

  const onMove = (event: PointerEvent): void => {
    if (event.pointerType !== "mouse") return;
    pointerX = event.clientX;
    pointerY = event.clientY;
    visible = true;
    if (stale) {
      stale = false;
      const under = document.elementFromPoint(pointerX, pointerY);
      // Fuera de la ventana devuelve null: ahi no hay zona que resolver.
      if (under) resolveZone(under);
    }
  };

  /*
   * El estado se resuelve en `pointerover`, no en `pointermove`: aquel solo
   * dispara al cambiar de elemento, asi que los `closest()` cuestan una vez
   * por transicion y no sesenta veces por segundo.
   */
  const onOver = (event: PointerEvent): void => {
    if (event.pointerType !== "mouse") return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    resolveZone(target);
  };

  /*
   * Al desplazar la pagina cambia el elemento bajo un raton QUIETO, y eso no
   * emite ningun evento de puntero: sin esto el charco se queda encendido en
   * una fila que ya no esta debajo. La comprobacion se aplaza al siguiente
   * movimiento en vez de hacerse en el propio evento, porque `scroll` llega
   * en rafagas.
   */
  const onScroll = (): void => {
    stale = true;
    if (pressable) rect = pressable.getBoundingClientRect();
  };

  const onLeave = (): void => {
    visible = false;
    pressable = null;
    rect = null;
    onNative = false;
  };

  const onDown = (): void => {
    pressed = true;
  };
  const onUp = (): void => {
    pressed = false;
  };

  window.addEventListener("pointermove", onMove, { passive: true, signal });
  window.addEventListener("pointerover", onOver, { passive: true, signal });
  window.addEventListener("pointerdown", onDown, { passive: true, signal });
  window.addEventListener("pointerup", onUp, { passive: true, signal });
  window.addEventListener("scroll", onScroll, { passive: true, signal });
  window.addEventListener("resize", resize, { passive: true, signal });
  document.addEventListener("pointerleave", onLeave, { passive: true, signal });

  const tick = (): void => {
    frame = window.requestAnimationFrame(tick);
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

    const on = visible && !onNative;
    const meta = on && pressable !== null ? 1 : 0;
    pot += (meta - pot) * POT_SMOOTHING;

    if (!on) return;

    // El rect se relee cada fotograma SOLO mientras hay diana: con el puntero
    // en reposo no se toca el layout.
    if (pressable) rect = pressable.getBoundingClientRect();

    if (rect && pot > 0.01) {
      const radio =
        Math.max(rect.height * RADIO_FACTOR, RADIO_MINIMO) * (pressed ? RADIO_PULSADO : 1);
      // El recorte ES el canto: la luz termina en el filo exacto del elemento.
      ctx.save();
      ctx.beginPath();
      ctx.rect(rect.left, rect.top, rect.width, rect.height);
      ctx.clip();
      const luz = ctx.createRadialGradient(pointerX, pointerY, 0, pointerX, pointerY, radio);
      luz.addColorStop(0, `rgb(255 160 60 / ${(0.3 * pot).toFixed(3)})`);
      luz.addColorStop(0.45, `rgb(255 90 52 / ${(0.13 * pot).toFixed(3)})`);
      luz.addColorStop(1, "rgb(224 29 60 / 0)");
      ctx.fillStyle = luz;
      ctx.fillRect(rect.left, rect.top, rect.width, rect.height);
      ctx.restore();

      // El canto del elemento, encendido a la potencia del charco. Es lo que
      // delimita la zona pulsable.
      ctx.strokeStyle = `rgb(255 90 52 / ${(0.85 * pot).toFixed(3)})`;
      ctx.lineWidth = 1;
      ctx.strokeRect(rect.left + 0.5, rect.top + 0.5, rect.width - 1, rect.height - 1);
    }

    // La mano. El anillo oscuro no es decoracion: garantiza contraste del
    // punto contra cualquier fotograma del shader sin depender del fondo.
    const r = pressed ? PUNTO_PULSADO : PUNTO_REPOSO;
    ctx.fillStyle = "#ffd9cc";
    ctx.beginPath();
    ctx.arc(pointerX, pointerY, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgb(11 4 4 / 0.9)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(pointerX, pointerY, r + 1, 0, Math.PI * 2);
    ctx.stroke();
  };

  frame = window.requestAnimationFrame(tick);

  // La clase solo se pone tras montar con exito: si este modulo no llega a
  // cargar o revienta antes, el CSS no oculta nada y el cursor del sistema
  // sigue intacto en toda la pagina.
  document.documentElement.classList.add("hypr-cursor-ready");

  const destroy = (): void => {
    window.cancelAnimationFrame(frame);
    controller.abort();
    document.documentElement.classList.remove("hypr-cursor-ready");
    canvas.remove();
    delete (window as unknown as { __hyprCursor__?: unknown }).__hyprCursor__;
  };

  // Sonda de verificacion: la consume scripts/measure-cursor-luz.py. No
  // afecta al render.
  (window as unknown as { __hyprCursor__?: { pot: () => number; destroy: () => void } }).
    __hyprCursor__ = { pot: () => pot, destroy };

  return { destroy };
}
```

- [x] **Paso 2: comprobar que compila**

```bash
npm run build && npm run lint
```

Esperado: ambos en verde, cero errores de TypeScript.

- [x] **Paso 3: commit**

```bash
git add src/components/hyprCursor.ts
git commit -m "feat(hyprland): modulo del cursor luz de mano"
```

---

### Task 4: la puerta de montaje

**Ficheros:**
- Modificar: `src/main.ts` (bloque nuevo tras la puerta del cursor de Vice, líneas 172-200; y la
  llamada a `destroy()` en el `pagehide` de las líneas 214-224)

**Interfaces:**
- Consume: `mountHyprCursor` de la tarea 3.
- Produce: nada que consuman otras tareas.

- [x] **Paso 1: añadir la puerta justo debajo del bloque del cursor de Vice**

```ts
/*
 * Cursor propio de Hyprland: la luz de mano. Las mismas tres puertas que
 * Vice — el tema, el perfil de motion y que el puntero sea fino con hover
 * real. En tactil no hay hover que disparar ningun estado, asi que el coste
 * correcto ahi es cero, no "cero animacion".
 *
 * Se monta con retardo, no de inmediato: `hyprIgnition` tapa la pantalla al
 * abrir y debajo no hay nada pulsable. A diferencia del leader de Vice, hoy
 * no emite ningun evento al soltarla, asi que el retardo es fijo. Si algun
 * dia lo emite, esto pasa a escucharlo igual que hace Vice.
 */
let hyprCursorHandle: { destroy: () => void } | null = null;
if (
  theme.id === "hyprland" &&
  !prefersReducedMotion &&
  window.matchMedia("(hover: hover) and (pointer: fine)").matches
) {
  window.setTimeout(() => {
    void import("./components/hyprCursor").then(({ mountHyprCursor }) => {
      hyprCursorHandle = mountHyprCursor(app);
    });
  }, 1800);
}
```

- [x] **Paso 2: añadir el `destroy()` al `pagehide` existente**

En el manejador de `pagehide` (donde ya están `backgroundHandle?.destroy()` y compañía), añadir una
línea:

```ts
    hyprCursorHandle?.destroy();
```

- [x] **Paso 3: build y arnés**

```bash
npm run build && npm run lint
npx vite preview --port 4173 &
sleep 3
python3 scripts/measure-cursor-luz.py --base http://localhost:4173
```

Esperado: **0 fallos**. Si falla `el modulo del cursor se descarga en movil`, la puerta
`(hover: hover) and (pointer: fine)` no está mordiendo — revisar que el contexto del arnés use
`is_mobile=True` y `has_touch=True`.

- [x] **Paso 4: commit**

```bash
git add src/main.ts
git commit -m "feat(hyprland): montar el cursor luz de mano tras el encendido"
```

---

### Task 5: contraste por glifo y calibración

Es el único riesgo real que declara el spec y no se puede cerrar a ojo.

**Ficheros:**
- Modificar: `scripts/measure-cursor-luz.py` (añadir la medida de contraste)
- Modificar: `src/components/hyprCursor.ts` (**solo si la medida lo pide**: bajar las opacidades del
  charco)
- Modificar: `docs/superpowers/specs/2026-08-19-hyprland-cursor-luz-design.md` (apuntar el número)

**Interfaces:**
- Consume: la sonda `window.__hyprCursor__` de la tarea 3.
- Produce: el número de contraste que el spec exige documentar.

- [x] **Paso 1: añadir la medida al arnés**

La medida es **por glifo y contra el fondo real**, no del viewport entero: en el cartel de obra la
medida ancha sobrestimaba el contraste. Se toma una captura con el charco encendido, se recortan
las cajas de los glifos del titular y se calcula el ratio del píxel más claro del fondo contra el
color del texto.

```python
def contraste_por_glifo(pg, selector):
    """Ratio WCAG del texto de la diana contra su propio fondo iluminado.

    Se mide DENTRO de la caja de la diana y con el charco encendido. Medir el
    viewport entero sobrestima el contraste: ya paso en el cartel de obra.
    """
    apuntar(pg, selector)
    caja = pg.locator(selector).first.bounding_box()
    tiro = pg.screenshot(clip=caja)
    from PIL import Image
    import io

    img = Image.open(io.BytesIO(tiro)).convert("RGB")
    pixeles = list(img.getdata())

    def lum(c):
        def canal(v):
            v = v / 255
            return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
        r, g, b = (canal(x) for x in c)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    # El texto es --text #ffeae6; el fondo es todo lo demas. Se coge el peor
    # caso: el pixel de fondo mas claro dentro de la caja.
    texto = lum((255, 234, 230))
    fondo = max(lum(p) for p in pixeles if p != (255, 234, 230))
    claro, oscuro = max(texto, fondo), min(texto, fondo)
    return (claro + 0.05) / (oscuro + 0.05)
```

Y en `main()`, tras las aserciones de reparto de señal:

```python
        for sel in ("button", ".scene-nav-trigger"):
            ratio = contraste_por_glifo(pg, sel)
            print(f"contraste {sel}: {ratio:.2f}:1")
            if ratio < 4.5:
                fallos.append(f"contraste bajo AA en {sel}: {ratio:.2f}:1")
```

- [x] **Paso 2: ejecutar y leer el número**

```bash
python3 scripts/measure-cursor-luz.py --base http://localhost:4173
```

- [x] **Paso 3: calibrar solo si hace falta**

Si alguna diana cae por debajo de 4,5:1, bajar el centro del charco en `hyprCursor.ts` en pasos de
0,04 hasta que cumpla:

```ts
      luz.addColorStop(0, `rgb(255 160 60 / ${(0.26 * pot).toFixed(3)})`);
```

Reconstruir y volver a medir tras cada paso. **No se toca el radio**: la dirección depende de que
el charco cubra el elemento, no de su intensidad.

- [x] **Paso 4: apuntar el número en el spec**

En la sección `## Color y contraste` del spec, sustituir "No está medido todavía" por el ratio
obtenido para cada tipo de diana, y decir contra qué se midió.

- [x] **Paso 5: commit**

```bash
git add scripts/measure-cursor-luz.py src/components/hyprCursor.ts docs/superpowers/specs/2026-08-19-hyprland-cursor-luz-design.md
git commit -m "test(hyprland): contraste por glifo del charco de luz"
```

---

### Task 6: verificación visual y no-regresión de Vice

**Ficheros:**
- Modificar: `docs/superpowers/specs/2026-08-19-hyprland-cursor-luz-design.md` (rellenar
  `## Registro de implementación`)

**Interfaces:**
- Consume: todo lo anterior.
- Produce: el registro que exige el criterio de aceptación del spec.

- [ ] **Paso 1: capturas reales de los tres estados**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for ancho, alto, nombre in ((1440, 900, "escritorio"), (390, 844, "movil")):
        pg = b.new_page(viewport={"width": ancho, "height": alto})
        pg.goto("http://localhost:4173/?theme=hyprland", wait_until="domcontentloaded")
        pg.wait_for_timeout(9000)
        loc = pg.locator("button").first
        loc.scroll_into_view_if_needed(); pg.wait_for_timeout(700)
        caja = loc.bounding_box()
        pg.mouse.move(caja["x"] + caja["width"] * 0.4, caja["y"] + caja["height"] / 2, steps=10)
        pg.wait_for_timeout(700)
        pg.screenshot(path=f"/tmp/cursor-luz-{nombre}.png")
    b.close()
PY
```

**Mirar las capturas, no solo comprobar que existen.** En este proyecto ya ha pasado dos veces que
los arneses salieran verdes con el resultado roto. Lo que hay que ver: el charco recortado **dentro**
de la fila, nada encendido fuera de ella, el punto de la mano donde está el ratón.

- [ ] **Paso 2: Vice intacto**

```bash
python3 scripts/verify.py
python3 scripts/measure-obra-rail.py --base http://localhost:4173
```

Esperado: `verify.py` sale **0** contra su línea base, y el carril de obra de Vice no se mueve.
Además, comprobar a ojo con `?theme=vice` que su cursor sigue siendo la marca de sincronismo.

- [ ] **Paso 3: rellenar el registro del spec y cerrar el estado**

En el spec: `Estado: implementado`, y en `## Registro de implementación` anotar el ratio de
contraste medido, la calibración final del charco si la hubo, y cualquier divergencia respecto a lo
planeado. Cambiar también la línea `Plan:` para quitar el `(pendiente)`.

- [ ] **Paso 4: commit**

```bash
git add docs/superpowers/specs/2026-08-19-hyprland-cursor-luz-design.md
git commit -m "docs(hyprland): cerrar el spec del cursor luz de mano"
```

---

## Auto-revisión del plan

**Cobertura del spec:** las siete secciones normativas del spec tienen tarea. Tesis y anatomía →
tarea 3. Estados → tarea 3 (bucle) y tarea 1 (aserciones). Reparto de señal y la trampa de
`sceneNav` → tarea 2. Color y contraste → tarea 5. Rendimiento y limpieza → tarea 3, verificado en
tarea 1 (asercion 6). Montaje → tarea 4. Criterio de aceptación → sus siete puntos caen en las
tareas 1, 4, 5 y 6.

**Huecos localizados y corregidos al revisar:**
- El spec dejaba abierto si `hyprIgnition` debía emitir un evento. El plan **cierra** la duda por el
  camino barato (retardo fijo de 1800 ms, igual que el que Vice usa tras su leader) y deja escrito
  en el comentario del código qué hacer si algún día lo emite. Cambiar `hyprIgnition` para emitirlo
  habría metido un módulo más en el alcance sin necesidad.
- El arnés necesita `Pillow` para el contraste. **No es dependencia nueva**: ya está instalada
  (12.2.0, comprobado el 2026-08-19) y la usan seis arneses del repo, entre ellos
  `measure-bg-luma.py` y `measure-cartel.py`. No toca el bundle.

**Consistencia de tipos:** `HyprCursorHandle` (tarea 3) coincide con el `{ destroy: () => void }`
que declara `main.ts` (tarea 4). La sonda `window.__hyprCursor__` expone `pot()` y `destroy()`, que
son exactamente los dos nombres que invoca el arnés de la tarea 1. La clase `.hypr-cursor-canvas`
de la tarea 2 es la que asigna el módulo, y el selector `LIENZO` del arnés la usa literal.
