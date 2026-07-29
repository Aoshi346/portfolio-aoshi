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

  // El telefono como enlace `tel:`: desde el movil se marca de un toque. Como
  // texto suelto obligaba a copiarlo a mano, que es fricción justo en el punto
  // donde alguien decide contactar.
  const phone = el("a", "contacto-phone", [identity.phone]) as HTMLAnchorElement;
  phone.href = `tel:${identity.phone.replace(/[^+\d]/g, "")}`;

  const github = el("a", "contacto-github", ["GitHub"]) as HTMLAnchorElement;
  github.href = identity.github;
  github.target = "_blank";
  github.rel = "noopener noreferrer";

  const linkedin = el("a", "contacto-github", ["LinkedIn"]) as HTMLAnchorElement;
  linkedin.href = identity.linkedin;
  linkedin.target = "_blank";
  linkedin.rel = "noopener noreferrer";

  // Mismo envoltorio compartido que el hero (`.hero-surface`, ver
  // src/sections/hero.ts): un solo DOM para los tres temas. Caelestia ya lo
  // viste como tarjeta Material You (themes.css); Vice le anade ademas un
  // scrim propio medible (hallazgo I-1 de la revision final: sin el, el
  // gate de contraste no lograba muestrear NINGUN elemento de esta escena
  // sobre el video).
  // Linea de apoyo entre el titulo y la accion: `identity.availability` ya
  // existe en content.ts y aqui es donde de verdad decide alguien si escribe.
  // No es copy nuevo, es contenido real que estaba sin usar en esta escena.
  const status = el("p", "contacto-status", [identity.availability]);

  const surface = el("div", "hero-surface", [
    el("p", "hero-kick", ["Contacto"]),
    el("h2", "display-xl mt-3 text-[clamp(2rem,6vw,4rem)]", ["Hablemos"]),
    status,
    // La coreografia anima ESTE envoltorio, no el enlace: si animara el
    // enlace, el `transform` inline que deja GSAP ganaria siempre al
    // `translateY` del hover declarado en themes.css y el CTA se quedaria
    // sin gesto al pasar el raton.
    el("p", "contacto-cta mt-8", [email]),
  ]);

  const section = el(
    "section",
    "contacto relative flex min-h-screen flex-col items-center justify-center px-6 py-24 text-center md:px-12",
    [
      surface,
      el("div", "hero-corner contacto-corner", [phone, linkedin, github]),
    ],
  );
  section.setAttribute("data-scene", "contacto");
  return section;
}
