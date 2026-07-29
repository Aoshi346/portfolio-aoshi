import { el } from "../utils/dom";

/**
 * Barra de progreso propia de Vice, a la derecha, en sustitucion de la del
 * navegador (que `style.css` oculta solo bajo `[data-theme="vice"]`).
 *
 * Es un indicador, no un control: no se arrastra. Esa decision es deliberada
 * — el recorrido tiene escenas con `pin` y `scrub`, asi que un pulgar
 * arrastrable daria saltos de scroll que rompen los gestos a medio camino, y
 * reimplementar el arrastre nativo bien (teclado, rueda sobre la barra,
 * accesibilidad) es reescribir un control que el navegador ya sabe hacer.
 * Por eso, ademas, va marcada `aria-hidden`: la informacion real de posicion
 * la da la barra de orientacion de arriba, con texto.
 *
 * El progreso se lee del scroll del documento en el ticker de rAF, no con un
 * listener de `scroll`: en Vice el scroll lo conduce Lenis y el evento nativo
 * llega desincronizado del fotograma que se esta pintando.
 */
export interface ScrollRailHandle {
  destroy: () => void;
}

export function mountScrollRail(host: HTMLElement): ScrollRailHandle {
  const thumb = el("div", "scroll-rail-thumb", []);
  const rail = el("div", "scroll-rail", [thumb]);
  rail.setAttribute("aria-hidden", "true");
  host.append(rail);

  /*
   * El alto desplazable solo cambia en eventos discretos (resize, y los `pin`
   * de ScrollTrigger al reservar su recorrido), nunca fotograma a fotograma.
   * Leer `scrollHeight` en cada rAF obliga al navegador a tener el layout al
   * dia 60 veces por segundo para devolver un valor que casi nunca ha
   * cambiado. Se cachea y se refresca por evento.
   */
  let scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const refreshScrollable = (): void => {
    scrollable = document.documentElement.scrollHeight - window.innerHeight;
  };
  const resizeObserver = new ResizeObserver(refreshScrollable);
  resizeObserver.observe(document.documentElement);
  // Los pines cambian el alto del documento sin redimensionar <html>, asi que
  // el observer no los ve: la coreografia avisa por evento tras su refresh.
  window.addEventListener("scrollrail:refresh", refreshScrollable, { passive: true });

  let frameId = 0;
  let lastProgress = -1;

  const tick = (): void => {
    frameId = requestAnimationFrame(tick);

    const progress = scrollable > 0 ? Math.min(Math.max(window.scrollY / scrollable, 0), 1) : 0;
    // Escribir en el DOM solo cuando el valor cambia de verdad: con el scroll
    // parado esto evita invalidar estilos 60 veces por segundo.
    if (Math.abs(progress - lastProgress) < 0.0005) return;
    lastProgress = progress;
    thumb.style.transform = `scaleY(${progress})`;
  };
  frameId = requestAnimationFrame(tick);

  return {
    destroy() {
      cancelAnimationFrame(frameId);
      resizeObserver.disconnect();
      window.removeEventListener("scrollrail:refresh", refreshScrollable);
      if (rail.parentNode === host) host.removeChild(rail);
    },
  };
}
