import { identity } from "../data/content";
import { el } from "../utils/dom";

/**
 * Apertura. Copy minimo y suelo de conversion garantizado: nombre, rol y
 * contacto quedan legibles en el primer viewport en los tres temas, sin
 * depender de que el shader o las animaciones hayan cargado.
 */
export function createHero(): HTMLElement {
  const eyebrow = el("p", "font-mono text-[0.7rem] uppercase tracking-[0.4em] text-accent", [
    identity.role,
  ]);

  const name = el(
    "h1",
    "mt-5 font-display text-[clamp(3rem,12vw,10.5rem)] font-black uppercase leading-[0.84]",
    [identity.name],
  );
  name.setAttribute("data-reveal", "chars");

  const line = el("p", "mt-8 max-w-xl text-lg leading-relaxed text-paper/70 md:text-xl", [
    identity.subheadline,
  ]);
  line.setAttribute("data-reveal", "fade-up");

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

  const contact = el("div", "mt-10 flex flex-wrap items-center gap-x-8 gap-y-3", [email, github]);
  contact.setAttribute("data-reveal", "fade-up");

  const scrollCue = el(
    "div",
    "mt-16 flex items-center gap-3 font-mono text-[0.65rem] uppercase tracking-[0.35em] text-paper/40",
    [el("span", "block h-px w-8 bg-paper/40", []), "Desplázate"],
  );

  return el(
    "section",
    "relative flex min-h-screen flex-col justify-center overflow-hidden px-6 py-24 md:px-12",
    [eyebrow, name, line, contact, scrollCue],
  );
}
