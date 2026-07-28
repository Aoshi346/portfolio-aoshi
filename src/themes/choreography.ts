import type { MotionProfile } from "./types";

export type Gsap = typeof import("gsap").default;
export type ScrollTriggerApi = typeof import("gsap/ScrollTrigger").ScrollTrigger;

export interface ChoreographyContext {
  gsap: Gsap;
  ScrollTrigger: ScrollTriggerApi;
  /** Raiz sobre la que buscar los ganchos `data-*`. */
  root: HTMLElement;
  motion: MotionProfile;
}

/**
 * Coreografia completa de un tema. Sustituye a las recetas genericas por
 * atributo: un gesto propio por seccion, no el mismo fade en todas partes.
 */
export type Choreography = (context: ChoreographyContext) => void;
