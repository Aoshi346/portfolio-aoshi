import type { BackgroundHandle } from "../backgrounds/shaderBackground";

/**
 * Ritmo de animacion propio de cada tema: el motion tambien cambia entre
 * temas, no solo el color. Lo consume `utils/reveal.ts`.
 */
export interface MotionProfile {
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
  /** Import dinamico: cada visita descarga un shader, no los tres. */
  mountBackground: (container: HTMLElement) => Promise<BackgroundHandle>;
}
