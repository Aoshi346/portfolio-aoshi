import type { Theme } from "./types";

/**
 * El escritorio: un shell Material You 3 cuyo color y esquema los gobierna el
 * reloj del visitante. Ver
 * `docs/superpowers/specs/2026-08-20-caelestia-escritorio-design.md`.
 */
export const caelestiaTheme: Theme = {
  id: "caelestia",
  label: "Caelestia",
  /*
   * Semilla del cromo del navegador: la aplica `themes/index.ts` antes de que
   * cargue `caelestia.color.ts`, que a partir de ahi la corrige por hora
   * (`CROMO_DIA` / `CROMO_NOCHE`). El lavanda anterior era de la paleta vieja
   * y ya no existe en ningun token. Se siembra con el valor DIURNO porque el
   * esquema claro cubre 13 de las 24 horas.
   */
  themeColor: "#f8f8f8",
  /*
   * Fraunces es el display, y sus ejes van escritos a mano en `themes.css`
   * (`--cae-display-axes`): con `opsz` a 9 los remates se afilan, con SOFT a 0
   * desaparece el redondeo y WONK a 1 activa las formas alternativas torcidas.
   * Hanken Grotesk cubre el cuerpo y Martian Mono las etiquetas.
   *
   * Este href y el `fontHrefs.caelestia` del script inline de `index.html` van
   * SIEMPRE a la par: el inline es quien pide las fuentes antes del primer
   * pintado, asi que tocar solo uno degrada la carga a la via lenta en
   * silencio, que es peor que un error.
   */
  fontHref:
    "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1&family=Hanken+Grotesk:wght@100..900&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=swap",
  motion: { style: "fluid", ease: "back.out(1.5)", duration: 1.2, stagger: 0.08 },
  async choreography() {
    const { caelestiaChoreography } = await import("./caelestia.choreography");
    return caelestiaChoreography;
  },
  /*
   * La coreografia de Caelestia monta el shell (carril, `inert`,
   * `data-cae-shell`), no solo lo anima: tiene que correr tambien con
   * movimiento reducido, reduciendo ella misma su propio movimiento. Ver
   * `types.ts`. Vice y Hyprland no declaran esta bandera.
   */
  choreographyBuildsLayout: true,
  async mountBackground(container) {
    const { mountCaelestiaFiguras } = await import("../backgrounds/caelestiaFiguras");
    return mountCaelestiaFiguras(container);
  },
};
