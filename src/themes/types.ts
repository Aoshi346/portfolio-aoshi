import type { BackgroundHandle } from "../backgrounds/shaderBackground";
import type { Choreography } from "./choreography";

/**
 * Familia de animacion. No es solo un easing distinto: cada estilo usa recetas
 * propias en `utils/reveal.ts` (que se anima, por que unidad y con que efecto).
 *
 * - `cinematic`: entradas con peso; el hero se atraviesa al hacer scroll (Vice).
 * - `snap`: seco y rapido, caracter a caracter (Hyprland).
 * - `fluid`: por palabras, con desenfoque y sobre-impulso blando (Caelestia).
 */
export type MotionStyle = "cinematic" | "snap" | "fluid";

/**
 * Ritmo de animacion propio de cada tema: el motion tambien cambia entre
 * temas, no solo el color. Lo consume `utils/reveal.ts`.
 */
export interface MotionProfile {
  style: MotionStyle;
  ease: string;
  duration: number;
  stagger: number;
}

export interface Theme {
  id: string;
  /** Nombre visible en la firma del tema (esquina). */
  label: string;
  /** Color del chrome del navegador (`<meta name="theme-color">`). */
  themeColor: string;
  /** Hoja de Google Fonts; solo se carga si el tema sale elegido. */
  fontHref: string;
  motion: MotionProfile;
  /**
   * Coreografia propia del tema, cargada en diferido. Si no la define, se
   * aplican las recetas genericas de `utils/reveal.ts`.
   */
  choreography?: () => Promise<Choreography>;
  /** Import dinamico: cada visita descarga un shader, no los tres. */
  mountBackground: (container: HTMLElement) => Promise<BackgroundHandle>;
}
