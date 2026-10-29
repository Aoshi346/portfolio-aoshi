import type { Theme } from "../themes/types";

/**
 * Carga GSAP y ScrollTrigger por import dinamico (no pesan en el bundle
 * inicial) y entrega el DOM ya montado a la coreografia del tema.
 *
 * Corre tambien con `prefers-reduced-motion: reduce`: la coreografia de
 * Caelestia no es solo movimiento, monta la maquetacion del shell (ver
 * `themes/types.ts`), y reduce ella misma su propio movimiento. Saltarsela
 * dejaba la pagina apilada en vertical con las pastillas de la barra sin
 * efecto visible; el spec pide que el cambio de workspace sea instantaneo, no
 * inexistente.
 */
export async function initScrollReveal(
  root: HTMLElement,
  theme: Theme,
): Promise<void> {
  const { default: gsap } = await import("gsap");
  const { ScrollTrigger } = await import("gsap/ScrollTrigger");
  gsap.registerPlugin(ScrollTrigger);

  const choreography = await theme.choreography();
  choreography({ gsap, ScrollTrigger, root, motion: theme.motion });
  ScrollTrigger.refresh();
}
