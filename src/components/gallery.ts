import type { GalleryShot } from "../data/content";
import { el } from "../utils/dom";

/**
 * Galeria horizontal arrastrable, estilo collage. Usa Pointer Events (no
 * eventos de raton sueltos) para funcionar igual con raton, dedo o lapiz.
 *
 * Resolucion del conflicto arrastre horizontal vs scroll vertical (Lenis):
 * en touch/lapiz el eje del gesto NO se decide hasta que el movimiento supera
 * `DRAG_AXIS_THRESHOLD` px. Si en ese momento el desplazamiento es mas
 * vertical que horizontal, este modulo se aparta del todo: nunca llama
 * `preventDefault` ni captura el puntero, asi que el scroll de la pagina (con
 * la inercia de Lenis) sigue intacto. Solo si es mas horizontal se fija el eje
 * a "x", se captura el puntero y desde ahi se hace scroll manual del carril.
 * Con raton el eje se fija a "x" de inmediato: no hay ambiguedad posible (la
 * rueda del raton, no el arrastre con el boton pulsado, es el gesto vertical
 * de esta pagina). `touch-action: pan-y` en `.gallery-track` (style.css)
 * completa esto: le dice al navegador que el pan vertical nativo sigue
 * disponible y que el horizontal queda bajo control manual de este modulo.
 */
const DRAG_AXIS_THRESHOLD = 6;

export function createGallery(shots: GalleryShot[]): HTMLElement {
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const track = el(
    "div",
    "gallery-track",
    shots.map((shot) => {
      const image = el("img", "gallery-img");
      image.src = shot.src;
      image.alt = shot.caption;
      image.loading = "lazy";
      image.decoding = "async";

      const fallback = el("span", "gallery-fallback", ["Imagen pendiente"]);
      fallback.setAttribute("aria-hidden", "true");

      const figure = el("figure", "gallery-item", [
        image,
        fallback,
        el("figcaption", "gallery-caption", [shot.caption]),
      ]);

      // Los assets reales llegan en la Task 11; hasta entonces la imagen
      // falla su carga. El fallback visual se muestra en su lugar, pero el
      // <img> se queda en el DOM (solo `opacity: 0`, nunca
      // `display:none`/`visibility:hidden`): asi el lector de pantalla sigue
      // anunciando el `alt` real de la pieza, no un hueco vacio.
      image.addEventListener("error", () => {
        image.classList.add("is-broken");
        figure.setAttribute("data-broken", "");
      });

      return figure;
    }),
  );
  track.setAttribute("data-gallery-track", "");
  track.tabIndex = 0;
  track.setAttribute("role", "group");
  track.setAttribute(
    "aria-label",
    "Capturas del proyecto. Se desplaza en horizontal: arrastra, o usa las flechas del teclado.",
  );

  const bar = el("div", "gallery-bar", [el("i", "", [])]);
  bar.setAttribute("data-gallery-bar", "");
  bar.setAttribute("aria-hidden", "true");

  const gallery = el("div", "gallery", [track, bar]);
  gallery.setAttribute("data-gallery", "");

  // --- Arrastre con Pointer Events -----------------------------------------
  let pointerId: number | null = null;
  let axis: "x" | "y" | null = null;
  let originX = 0;
  let originY = 0;
  let originScroll = 0;

  function lockToXAxis(event: PointerEvent): void {
    axis = "x";
    track.classList.add("is-dragging");
    track.setPointerCapture(event.pointerId);
  }

  track.addEventListener("pointerdown", (event: PointerEvent) => {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    pointerId = event.pointerId;
    originX = event.clientX;
    originY = event.clientY;
    originScroll = track.scrollLeft;
    // Con raton no hay gesto vertical competidor: fijar el eje de inmediato.
    axis = event.pointerType === "mouse" ? "x" : null;
    if (axis === "x") lockToXAxis(event);
  });

  track.addEventListener("pointermove", (event: PointerEvent) => {
    if (pointerId === null || event.pointerId !== pointerId) return;
    const dx = event.clientX - originX;

    if (axis === null) {
      const dy = event.clientY - originY;
      if (Math.abs(dx) < DRAG_AXIS_THRESHOLD && Math.abs(dy) < DRAG_AXIS_THRESHOLD) return;
      if (Math.abs(dy) >= Math.abs(dx)) {
        // Gesto mas vertical que horizontal: se abandona el seguimiento de
        // este puntero. Nunca se llamo `preventDefault` ni `setPointerCapture`,
        // asi que el scroll vertical (Lenis) no se entera de que esto paso.
        pointerId = null;
        return;
      }
      lockToXAxis(event);
    }

    if (axis === "x") {
      track.scrollLeft = originScroll - dx;
      event.preventDefault();
    }
  });

  function endDrag(event: PointerEvent): void {
    if (event.pointerId !== pointerId) return;
    track.classList.remove("is-dragging");
    pointerId = null;
    axis = null;
  }
  track.addEventListener("pointerup", endDrag);
  track.addEventListener("pointercancel", endDrag);

  // --- Teclado --------------------------------------------------------------
  // El arrastre no puede ser la unica via: quien navega con tabulador debe
  // poder recorrer las imagenes. El contenedor desbordado con `tabIndex=0` ya
  // responde a las flechas nativamente en la mayoria de navegadores, pero se
  // fija aqui de forma explicita para no depender de ese detalle de
  // implementacion y dar un paso de scroll consistente entre navegadores.
  track.addEventListener("keydown", (event: KeyboardEvent) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    const direction = event.key === "ArrowRight" ? 1 : -1;
    track.scrollBy({
      left: track.clientWidth * 0.82 * direction,
      behavior: prefersReducedMotion ? "auto" : "smooth",
    });
    event.preventDefault();
  });

  // --- Barra de progreso ------------------------------------------------------
  const indicator = bar.firstElementChild as HTMLElement;
  function updateBar(): void {
    const maxScroll = Math.max(1, track.scrollWidth - track.clientWidth);
    const ratio = Math.max(14, (track.clientWidth / track.scrollWidth) * 100);
    indicator.style.width = `${ratio.toFixed(1)}%`;
    indicator.style.marginLeft = `${((track.scrollLeft / maxScroll) * (100 - ratio)).toFixed(1)}%`;
  }
  track.addEventListener("scroll", updateBar, { passive: true });
  updateBar();

  return gallery;
}
