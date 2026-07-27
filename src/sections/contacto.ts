import { identity } from "../data/content";
import { el } from "../utils/dom";

/**
 * Cierre del portfolio: donde alguien decide escribir. Suelo de conversion,
 * igual que el hero — email accionable de inmediato, enlace externo con
 * `rel="noopener noreferrer"`.
 */
export function createContacto(): HTMLElement {
  const email = el("a", "contacto-mail", [identity.email]) as HTMLAnchorElement;
  email.href = `mailto:${identity.email}`;

  const github = el("a", "contacto-github", ["GitHub"]) as HTMLAnchorElement;
  github.href = identity.github;
  github.target = "_blank";
  github.rel = "noopener noreferrer";

  // Mismo envoltorio compartido que el hero (`.hero-surface`, ver
  // src/sections/hero.ts): un solo DOM para los tres temas. Caelestia ya lo
  // viste como tarjeta Material You (themes.css); Vice le anade ademas un
  // scrim propio medible (hallazgo I-1 de la revision final: sin el, el
  // gate de contraste no lograba muestrear NINGUN elemento de esta escena
  // sobre el video).
  const surface = el("div", "hero-surface", [
    el("p", "hero-kick", ["Contacto"]),
    el("h2", "display-xl mt-3 text-[clamp(2rem,6vw,4rem)]", ["Hablemos"]),
    el("p", "mt-6", [email]),
  ]);

  const section = el(
    "section",
    "contacto relative flex min-h-screen flex-col items-center justify-center px-6 py-24 text-center md:px-12",
    [
      surface,
      el("div", "hero-corner contacto-corner", [
        el("span", "", [identity.phone]),
        github,
      ]),
    ],
  );
  section.setAttribute("data-scene", "contacto");
  return section;
}
