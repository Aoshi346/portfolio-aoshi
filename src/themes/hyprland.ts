import type { Theme } from "./types";

/** Ascua: luz emisiva de canto duro sobre negro con sesgo rojo. */
export const hyprlandTheme: Theme = {
  id: "hyprland",
  label: "Hyprland",
  themeColor: "#0b0404",
  fontHref:
    "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap",
  motion: { style: "snap", ease: "power3.out", duration: 0.9, stagger: 0.07 },
  async mountBackground(container) {
    // Se cambia a mountHyprEmber en la tarea 3, cuando el modulo exista.
    const { mountHyprGradient } = await import("../backgrounds/hyprGradient");
    return mountHyprGradient(container);
  },
};
