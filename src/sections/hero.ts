import { identity } from "../data/content";
import { el } from "../utils/dom";

/**
 * Apertura. Suelo de conversion garantizado: nombre, rol y contacto legibles
 * al instante, sin depender de que el video o las animaciones hayan cargado.
 * El layout concreto lo decide el tema (themes.css).
 */
export function createHero(): HTMLElement {
  // El valor del atributo declara hacia donde sale cada bloque en el gesto de
  // salida de Vice (`vice.choreography.ts`): lo que esta sobre el nombre se va
  // hacia arriba y lo que esta debajo hacia abajo, de modo que el nombre queda
  // solo en el centro. El selector `[data-hero-fade]` que usan reveal.ts y
  // style.css no distingue valor, asi que los otros dos temas no se enteran.
  const eyebrow = el("p", "hero-kick", [identity.role]);
  eyebrow.setAttribute("data-hero-fade", "up");

  const name = el("h1", "display-xl mt-4 text-[clamp(2.8rem,11vw,9.5rem)]", [identity.name]);
  name.setAttribute("data-hero-name", "");

  const lead = el("p", "lead mx-auto mt-5 max-w-[32ch] text-paper/85", [identity.subheadline]);
  lead.setAttribute("data-hero-fade", "down");

  const location = el("span", "", [identity.location]);

  const email = el("a", "hero-mail", [identity.email]);
  email.href = `mailto:${identity.email}`;

  const corner = el("div", "hero-corner", [location, email]);
  corner.setAttribute("data-hero-fade", "down");

  // Envoltorio comun a los tres temas: Caelestia lo viste como tarjeta
  // Material You (themes.css), Vice y Hyprland lo neutralizan a sangre.
  // El DOM es unico; solo el CSS colgado de [data-theme] decide la piel.
  const surface = el("div", "hero-surface", [eyebrow, name, lead]);

  const section = el(
    "section",
    "hero relative flex min-h-screen flex-col justify-center overflow-hidden px-6 py-24 md:px-12",
    [surface, corner],
  );
  section.setAttribute("data-scene", "hero");

  return section;
}
