import type { BackgroundHandle } from "../backgrounds/shaderBackground";
import type { Choreography } from "./choreography";

/**
 * Ritmo de animacion del tema. Lo recibe la coreografia (`ChoreographyContext`).
 */
export interface MotionProfile {
  ease: string;
  duration: number;
  stagger: number;
}

export interface Theme {
  id: string;
  /** Color del chrome del navegador (`<meta name="theme-color">`). */
  themeColor: string;
  /** Hoja de Google Fonts (la pide antes el script inline de `index.html`). */
  fontHref: string;
  motion: MotionProfile;
  /**
   * Coreografia del tema, cargada en diferido. No es SOLO movimiento: tambien
   * monta la maquetacion (pone `data-cae-shell="workspaces"`, marca el carril,
   * aisla con `inert` los workspaces inactivos y mueve el carril), asi que
   * corre tambien con `prefers-reduced-motion: reduce` y es ella quien reduce
   * su propio movimiento (`duration: 0`). Sin ella la pagina se queda apilada
   * en vertical y las pastillas de la barra no hacen nada.
   */
  choreography: () => Promise<Choreography>;
  /** Import dinamico: el shader no pesa en el bundle inicial. */
  mountBackground: (container: HTMLElement) => Promise<BackgroundHandle>;
}
