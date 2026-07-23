import { identity } from "../data/content";
import { el } from "../utils/dom";

/**
 * Apertura. Copy minimo y suelo de conversion garantizado: nombre, rol y
 * contacto quedan legibles al instante en los tres temas — nada del hero
 * depende de que el shader o las animaciones hayan cargado.
 *
 * El layout concreto lo decide el tema (themes.css): Vice lo centra para el
 * gesto de atravesar el nombre, los demas lo alinean a la izquierda.
 */
export function createHero(): HTMLElement {
  const eyebrow = el("p", "font-mono text-[0.7rem] uppercase tracking-[0.4em] text-accent", [
    identity.role,
  ]);
  eyebrow.setAttribute("data-hero-fade", "");

  const name = el("h1", "display-xl mt-5 text-[clamp(3rem,12vw,10.5rem)]", [identity.name]);
  name.setAttribute("data-hero-name", "");
  name.setAttribute("data-reveal", "chars");

  const line = el("p", "hero-line mt-8 max-w-xl text-lg leading-relaxed text-paper/70 md:text-xl", [
    identity.subheadline,
  ]);
  line.setAttribute("data-hero-fade", "");

  const email = el(
    "a",
    "font-mono text-sm text-paper underline decoration-accent decoration-2 underline-offset-8 transition-colors duration-300 hover:text-accent",
    [identity.email],
  );
  email.href = `mailto:${identity.email}`;

  const github = el(
    "a",
    "font-mono text-sm text-paper/60 transition-colors duration-300 hover:text-accent",
    ["GitHub"],
  );
  github.href = identity.github;
  github.target = "_blank";
  github.rel = "noopener noreferrer";

  const contact = el("div", "hero-contact mt-10 flex flex-wrap items-center gap-x-8 gap-y-3", [
    email,
    github,
  ]);
  contact.setAttribute("data-hero-fade", "");

  const surface = el("div", "hero-surface", [eyebrow, name, line, contact]);
  const inner = el("div", "hero-inner relative w-full", [surface]);

  const scrollCue = el(
    "div",
    "hero-cue absolute bottom-10 left-6 flex items-center gap-3 font-mono text-[0.65rem] uppercase tracking-[0.35em] text-paper/40 md:left-12",
    [el("span", "block h-px w-8 bg-paper/40", []), "Desplázate"],
  );
  scrollCue.setAttribute("data-hero-fade", "");

  const section = el(
    "section",
    "hero relative flex min-h-screen flex-col justify-center overflow-hidden px-6 py-24 md:px-12",
    [inner, scrollCue],
  );
  section.setAttribute("data-hero", "");

  return section;
}
