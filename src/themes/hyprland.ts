import type { Theme } from "./types";

/** Cian/verde sobre negro: geometrica, bordes minimos, motion seco y rapido. */
export const hyprlandTheme: Theme = {
  id: "hyprland",
  label: "Hyprland",
  themeColor: "#05070a",
  fontHref:
    "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@500&display=swap",
  motion: { ease: "power4.out", duration: 0.8, stagger: 0.05 },
  async mountBackground(container) {
    const { mountHyprGradient } = await import("../backgrounds/hyprGradient");
    return mountHyprGradient(container);
  },
};
