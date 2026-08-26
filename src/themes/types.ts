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
  /**
   * La coreografia de este tema no es SOLO movimiento: tambien monta
   * maquetacion, asi que tiene que correr tambien con
   * `prefers-reduced-motion: reduce`.
   *
   * Por que existe la bandera. `utils/reveal.ts` se saltaba entero el reveal
   * con movimiento reducido, coreografia incluida. Para Vice y Hyprland eso es
   * exactamente lo que se pide: su coreografia solo anima. Para Caelestia no:
   * la suya es quien pone `data-cae-shell="workspaces"`, marca el carril,
   * aisla con `inert` los workspaces inactivos y mueve el carril. Sin ella,
   * Caelestia con `reduce` se quedaba como pagina vertical apilada y las
   * pastillas de la barra no hacian nada visible — y el spec pide que el
   * cambio de workspace sea INSTANTANEO, no inexistente.
   *
   * Es opcional a proposito y solo la declara `caelestia.ts`: al quedar
   * `undefined` en Vice y Hyprland, su ruta por `reveal.ts` no cambia. La
   * reduccion del movimiento la hace entonces la propia coreografia (en
   * Caelestia, `duration: 0`).
   */
  choreographyBuildsLayout?: boolean;
  /** Import dinamico: cada visita descarga un shader, no los tres. */
  mountBackground: (container: HTMLElement) => Promise<BackgroundHandle>;
}
