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
      luz.addColorStop(0, `rgb(255 160 60 / ${(0.04 * pot).toFixed(3)})`);
      luz.addColorStop(0.45, `rgb(255 90 52 / ${(0.017 * pot).toFixed(3)})`);
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
