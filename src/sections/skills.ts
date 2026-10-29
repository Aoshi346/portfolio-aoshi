import { el } from "../utils/dom";

/**
 * "Con qué construyo": los creditos finales de una pelicula. La seccion solo
 * trae el titulo; las piezas las monta la bandeja de Caelestia
 * (`caelestiaCreditosBandeja.ts`) leyendo `skillGroups` en `content.ts`.
 */
export function createSkills(): HTMLElement {
  const section = el(
    "section",
    "credits relative flex min-h-screen flex-col justify-center px-6 py-24 md:px-12",
    [el("h2", "hero-kick", ["Con qué construyo"])],
  );
  section.setAttribute("data-scene", "credits");
  return section;
}
