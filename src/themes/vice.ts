import type { Theme } from "./types";

/** Atardecer de neon: tipografia de cartel, cero redondeo, motion con peso. */
export const viceTheme: Theme = {
  id: "vice",
  label: "Vice City",
  themeColor: "#150726",
  fontHref:
    "https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap",
  motion: { ease: "expo.out", duration: 1.15, stagger: 0.07 },
  async mountBackground(container) {
    const { mountViceSunset } = await import("../backgrounds/viceSunset");
    return mountViceSunset(container);
  },
};
