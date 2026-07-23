import type { Theme } from "./types";

/** Material You: unico tema claro, muy redondeado, motion blando y amable. */
export const caelestiaTheme: Theme = {
  id: "caelestia",
  label: "Caelestia",
  themeColor: "#f4f0f9",
  fontHref:
    "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@500&display=swap",
  motion: { style: "fluid", ease: "back.out(1.5)", duration: 1.2, stagger: 0.08 },
  async mountBackground(container) {
    const { mountCaelestiaBlobs } = await import("../backgrounds/caelestiaBlobs");
    return mountCaelestiaBlobs(container);
  },
};
