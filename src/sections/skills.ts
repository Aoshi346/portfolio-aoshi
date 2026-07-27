import { createCredits } from "../components/credits";
import { el } from "../utils/dom";

/**
 * "Con qué construyo": los creditos finales de una pelicula. Un solo DOM
 * (`createCredits`, `src/components/credits.ts`) para los tres temas — la
 * presentacion (creditos de cine en Vice, pildoras en Hyprland/Caelestia) la
 * decide el CSS colgado de `[data-theme]` en `themes/themes.css`, nunca una
 * ramificacion aqui.
 */
export function createSkills(): HTMLElement {
  const section = el(
    "section",
    "credits relative flex min-h-screen flex-col justify-center px-6 py-24 md:px-12",
    [el("h2", "hero-kick", ["Con qué construyo"]), createCredits()],
  );
  section.setAttribute("data-scene", "credits");
  return section;
}
