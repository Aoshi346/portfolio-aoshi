import type { Theme } from "./types";

/** Atardecer de neon: tipografia de cartel, cero redondeo, motion con peso. */
export const viceTheme: Theme = {
  id: "vice",
  label: "Vice City",
  themeColor: "#150726",
  // Passion One 900: alternativa libre mas cercana a Pricedown, cuya licencia
  // gratuita prohibe incrustarla como webfont. Manrope cubre lead y cuerpo.
  fontHref:
    "https://fonts.googleapis.com/css2?family=Passion+One:wght@900&family=Manrope:wght@200;300;400;600;700&display=swap",
  motion: { style: "cinematic", ease: "expo.out", duration: 1.15, stagger: 0.07 },
  async mountBackground(container) {
    const { mountCinematicBackdrop } = await import("../backgrounds/cinematicBackdrop");
    return mountCinematicBackdrop(container, {
      poster: "/media/vice-poster.webp",
      video: { webm: "/media/vice-hero.webm", mp4: "/media/vice-hero.mp4" },
    });
  },
  async choreography() {
    const { viceChoreography } = await import("./vice.choreography");
    return viceChoreography;
  },
};
