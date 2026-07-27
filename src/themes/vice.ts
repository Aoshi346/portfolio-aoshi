import type { Theme } from "./types";

/** Atardecer de neon: tipografia de cartel, cero redondeo, motion con peso. */
export const viceTheme: Theme = {
  id: "vice",
  label: "Vice City",
  themeColor: "#150726",
  // Passion One 900: la alternativa libre mas cercana a Pricedown (la fuente
  // real de GTA), cuya licencia gratuita prohibe incrustarla como webfont.
  fontHref:
    "https://fonts.googleapis.com/css2?family=Passion+One:wght@700;900&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap",
  motion: { style: "cinematic", ease: "expo.out", duration: 1.15, stagger: 0.07 },
  async mountBackground(container) {
    const { mountCinematicBackdrop } = await import("../backgrounds/cinematicBackdrop");
    return mountCinematicBackdrop(container, {
      poster: "/media/vice-poster.webp",
      video: { webm: "/media/vice-hero.webm", mp4: "/media/vice-hero.mp4" },
    });
  },
};
