import type { Theme } from "./types";

/**
 * El escritorio: un shell Material You 3 cuyo color y esquema los gobierna el
 * reloj del visitante. Ver
 * `docs/superpowers/specs/2026-08-20-caelestia-escritorio-design.md`.
 */
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
