import { el } from "../utils/dom";

export interface ViceCursorHandle {
  destroy: () => void;
}

/*
 * Cursor propio de Vice: la marca de sincronismo con que los montadores
 * alineaban cabeza y cola de bobina. Circulo fino con cruz, FIJA — nunca gira.
 *
 * Reparto de senales, que es la decision de fondo de todo este modulo:
 *
 *   `pointer`  -> lo sustituye este cursor. Es el unico glifo cuyo mensaje
 *                 ("esto se pulsa") la marca dice mejor que el nativo.
 *   `grab` / `grabbing` (`.gallery-track`) -> se quedan NATIVOS. Son la unica
 *                 pista de que la galeria se arrastra, y asi sobreviven a que
 *                 este modulo no cargue.
 *   I-beam en texto -> NATIVO. Ocultarlo quita la senal de que se selecciona.
 *   Enlaces externos (`target="_blank"`) -> NATIVOS. Abren pestana nueva: la
 *                 certeza de "esto es un enlace real" no se toca.
 *
 * El CSS se apoya en que `cursor` solo se hereda cuando el elemento NO declara
 * el suyo. `.gallery-track` declara `grab` y los `<a>` reciben `pointer` de la
 * hoja del navegador, asi que el `cursor: none` del lienzo no les llega: hay
 * que optar por ellos uno a uno. Eso convierte la regla en lista blanca de
 * verdad — un pulsable nuevo conserva su glifo nativo mientras nadie lo apunte.
 */

// Zonas donde manda el navegador y este cursor se apaga.
const NATIVE_ZONE = '.gallery-track, a[target="_blank"], p, li, dd, dt, figcaption, blockquote';
// Pulsables que este cursor sustituye. El enlace externo queda fuera aposta.
const PRESSABLE = 'button, a[href]:not([target="_blank"])';

// Doce filas de creditos seguidas darian doce destellos por segundo al
// barrerlas, y cada uno cortaria al anterior a media animacion.
const BURN_COOLDOWN_MS = 350;

// Suavizado de la marca. El punto de clic NO usa esto: se escribe directo en
// el manejador, porque un punto que va detras del raton hace fallar el clic.
const MARK_SMOOTHING = 0.15;
const PRESS_SMOOTHING = 0.34;

// Escalas sobre el tamano de reposo (circulo 16px, brazos 9px).
const SCALE_IDLE = 1;
const SCALE_HOVER = 1.875; // 16px -> 30px
const SCALE_PRESS = 1.44; // el golpe seco de la claqueta, sin rebote
const ARM_HOVER = 2.6; // los brazos llegan justo al borde del circulo
const ARM_PRESS = 1.45;

export function mountViceCursor(host: HTMLElement): ViceCursorHandle {
  const controller = new AbortController();
  const { signal } = controller;

  const sync = el("div", "vcursor-sync", []);
  const inner = el("div", "vcursor-inner", []);
  const armH = el("div", "vcursor-arm vcursor-arm-h", []);
  const armV = el("div", "vcursor-arm vcursor-arm-v", []);
  const cue = el("div", "vcursor-cue", []);
  const dot = el("div", "vcursor-dot", []);
  const root = el("div", "vcursor", [sync, inner, armH, armV, cue, dot]);
  root.setAttribute("aria-hidden", "true");
  host.append(root);

  let pointerX = 0;
  let pointerY = 0;
  let markX = 0;
  let markY = 0;
  let scale = SCALE_IDLE;
  let arm = SCALE_IDLE;
  let innerScale = 0;
  let visible = false;
  let onNative = false;
  let pressable: HTMLElement | null = null;
  let pressed = false;
  let lastBurn = Number.NEGATIVE_INFINITY;
  let stale = false;
  let frame = 0;

  const burn = (): void => {
    const now = performance.now();
    if (now - lastBurn < BURN_COOLDOWN_MS) return;
    lastBurn = now;
    // Reinicio de la animacion CSS: quitar la clase no basta si el navegador
    // no ha recalculado estilo entre medias, de ahi la lectura forzada.
    cue.classList.remove("is-burning");
    void cue.offsetWidth;
    cue.style.setProperty("--vcursor-burn", `translate3d(${pointerX}px, ${pointerY}px, 0)`);
    cue.classList.add("is-burning");
  };

  const onMove = (event: PointerEvent): void => {
    if (event.pointerType !== "mouse") return;
    pointerX = event.clientX;
    pointerY = event.clientY;
    visible = true;
    // Punto de clic sin suavizado ni tween: se escribe en el mismo evento.
    dot.style.transform = `translate3d(${pointerX}px, ${pointerY}px, 0)`;
  };

  const resolveZone = (target: Element): void => {
    onNative = target.closest(NATIVE_ZONE) !== null;
    const next = onNative ? null : target.closest<HTMLElement>(PRESSABLE);
    if (next && next !== pressable) burn();
    pressable = next;
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
   * emite ningun evento de puntero: sin esto el estado se queda congelado en
   * el del elemento anterior. Medido: parado sobre texto tras desplazar, la
   * marca seguia dibujandose encima del I-beam. En Vice ademas es la norma y
   * no la excepcion, porque el carril de obra desplaza las cartelas por
   * debajo del cursor mientras este no se mueve.
   *
   * La comprobacion se aplaza al siguiente fotograma en vez de hacerse en el
   * propio evento: `scroll` llega en rafagas y el impacto seria un test de
   * posicion por evento en lugar de uno por fotograma pintado.
   */
  const onScroll = (): void => {
    stale = true;
  };

  const onLeave = (): void => {
    visible = false;
    pressable = null;
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
  document.addEventListener("pointerleave", onLeave, { passive: true, signal });

  const tick = (): void => {
    frame = window.requestAnimationFrame(tick);

    if (stale) {
      stale = false;
      if (visible) {
        const under = document.elementFromPoint(pointerX, pointerY);
        // Fuera de la ventana devuelve null: ahi no hay zona que resolver.
        if (under) resolveZone(under);
      }
    }

    const hovering = pressable !== null;
    const isPressed = pressed && hovering;
    // `aria-pressed` se lee cada fotograma a proposito: `credits.ts` lo cambia
    // en `mouseenter`, que puede llegar despues de nuestro `pointerover`.
    const active = hovering && pressable?.getAttribute("aria-pressed") === "true";

    const targetScale = isPressed ? SCALE_PRESS : hovering ? SCALE_HOVER : SCALE_IDLE;
    const targetArm = isPressed ? ARM_PRESS : hovering ? ARM_HOVER : SCALE_IDLE;
    const smoothing = isPressed ? PRESS_SMOOTHING : MARK_SMOOTHING;

    markX += (pointerX - markX) * MARK_SMOOTHING;
    markY += (pointerY - markY) * MARK_SMOOTHING;
    scale += (targetScale - scale) * smoothing;
    arm += (targetArm - arm) * smoothing;
    innerScale += ((active && !isPressed ? 1.25 : 0) - innerScale) * 0.18;

    const on = visible && !onNative;
    const place = `translate3d(${markX}px, ${markY}px, 0)`;

    sync.style.transform = `${place} scale(${scale})`;
    sync.style.opacity = on ? (hovering ? "0.95" : "0.7") : "0";
    sync.classList.toggle("is-hot", hovering);
    sync.classList.toggle("is-pressed", isPressed);

    inner.style.transform = `${place} scale(${innerScale})`;
    inner.style.opacity = on && innerScale > 0.05 ? "0.55" : "0";

    armH.style.transform = `${place} scaleX(${arm})`;
    armV.style.transform = `${place} scaleY(${arm})`;
    const armOpacity = on ? (hovering ? "0.9" : "0.6") : "0";
    armH.style.opacity = armOpacity;
    armV.style.opacity = armOpacity;

    dot.style.opacity = on ? "1" : "0";
    dot.classList.toggle("is-active", active === true);
  };

  frame = window.requestAnimationFrame(tick);

  // La clase solo se pone tras montar con exito: si este modulo no llega a
  // cargar o revienta antes, el CSS no oculta nada y el cursor del sistema
  // sigue intacto en toda la pagina.
  document.documentElement.classList.add("vice-cursor-ready");

  return {
    destroy: (): void => {
      window.cancelAnimationFrame(frame);
      controller.abort();
      document.documentElement.classList.remove("vice-cursor-ready");
      root.remove();
    },
  };
}
