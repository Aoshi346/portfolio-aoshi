import type { Theme } from "./types";

/** Atardecer de neon: tipografia de cartel, cero redondeo, motion con peso. */
export const viceTheme: Theme = {
  id: "vice",
  label: "Vice City",
  themeColor: "#150726",
  /*
   * Passion One 900: alternativa libre mas cercana a Pricedown, cuya licencia
   * gratuita prohibe incrustarla como webfont. Manrope cubre lead y cuerpo.
   * Pathway Gothic One es la condensada del cartel de reparto (token
   * `--font-billing` en themes.css), y solo se usa ahi.
   *
   * Este href y el `fontHrefs.vice` del script inline de `index.html` van
   * SIEMPRE a la par: el inline es quien pide las fuentes antes del primer
   * pintado, asi que tocar solo uno no rompe nada visible — degrada la carga
   * a la via lenta en silencio, que es peor que un error.
   */
  fontHref:
    "https://fonts.googleapis.com/css2?family=Passion+One:wght@900&family=Manrope:wght@200;300;400;600;700&family=Pathway+Gothic+One&display=swap",
  motion: { style: "cinematic", ease: "expo.out", duration: 1.15, stagger: 0.07 },
  /*
   * Serigrafia de cartel, no bruma. El backdrop de video servia el fixture
   * sintetico de barras SMPTE (`public/media/vice-hero.*`), cuyas franjas de
   * color primario puro obligaban a tapar hero y contacto con un scrim casi
   * opaco solo para poder medir contraste. La bruma generativa que lo
   * sustituyo (`viceHaze`) resolvio eso: base propia, oscura, de brillo
   * acotado, capaz de responder al scroll.
   *
   * Este es el capitulo siguiente, no una vuelta atras: la bruma seguia
   * siendo atmosfera — algo que el fondo *representaba* detras del texto. La
   * serigrafia (`viceInk`) deja de representar y pasa a ser la materia: el
   * fondo es el pliego de papel sobre el que el cartel de Vice estaria
   * impreso a dos tintas, con su trama, su rasqueta y su desregistro. El tema
   * ya hablaba en clave de cartel (Passion One, tipografia de reparto); el
   * fondo ahora es literalmente eso.
   */
  async mountBackground(container) {
    const { mountViceInk } = await import("../backgrounds/viceInk");
    return mountViceInk(container);
  },
  async choreography() {
    const { viceChoreography } = await import("./vice.choreography");
    return viceChoreography;
  },
};
