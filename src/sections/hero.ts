import { identity } from "../data/content";
import { el } from "../utils/dom";

/**
 * Apertura. Suelo de conversion garantizado: nombre, rol y contacto legibles
 * al instante, sin depender de que el video o las animaciones hayan cargado.
 * El layout concreto lo decide el tema (themes.css).
 */
export function createHero(): HTMLElement {
  const eyebrow = el("p", "hero-kick", [identity.role]);
  eyebrow.setAttribute("data-hero-fade", "");

  const name = el("h1", "display-xl mt-4 text-[clamp(2.8rem,11vw,9.5rem)]", [identity.name]);
  name.setAttribute("data-hero-name", "");

  const lead = el("p", "lead mx-auto mt-5 max-w-[32ch] text-paper/85", [identity.subheadline]);
  lead.setAttribute("data-hero-fade", "");

  const location = el("span", "", [identity.location]);

  const email = el("a", "hero-mail", [identity.email]);
  email.href = `mailto:${identity.email}`;

  const corner = el("div", "hero-corner", [location, email]);
  corner.setAttribute("data-hero-fade", "");

  const section = el(
    "section",
    "hero relative flex min-h-screen flex-col justify-center overflow-hidden px-6 py-24 md:px-12",
    [eyebrow, name, lead, corner],
  );
  section.setAttribute("data-scene", "hero");

  return section;
}
