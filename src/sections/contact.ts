import { identity } from "../data/content";
import { el } from "../utils/dom";

export function createContact(): HTMLElement {
  const emailLink = el(
    "a",
    "break-words font-display text-2xl font-bold text-paper hover:text-accent sm:text-4xl md:text-7xl",
    [identity.email],
  ) as HTMLAnchorElement;
  emailLink.href = `mailto:${identity.email}`;

  const githubLink = el(
    "a",
    "text-lg text-paper/70 underline-offset-4 hover:text-accent hover:underline",
    ["Ver perfil de GitHub →"],
  ) as HTMLAnchorElement;
  githubLink.href = identity.github;
  githubLink.target = "_blank";
  githubLink.rel = "noreferrer";

  const section = el(
    "section",
    "flex min-h-[70vh] flex-col items-start justify-center gap-8 border-t border-paper/10 px-6 py-32 md:px-0",
    [
      el("p", "mx-auto w-full max-w-3xl font-display text-sm uppercase tracking-[0.3em] text-accent", [
        "Contacto",
      ]),
      el("div", "mx-auto flex w-full max-w-3xl flex-col gap-6", [
        el("h2", "max-w-2xl text-balance font-display text-4xl font-bold md:text-6xl", [
          "¿Un proyecto en mente? Hablemos.",
        ]),
        emailLink,
        el("div", "flex flex-wrap items-center gap-6 text-paper/60", [
          identity.phone,
          identity.location,
          githubLink,
        ]),
      ]),
    ],
  );
  section.setAttribute("id", "contacto");
  section.setAttribute("data-reveal", "fade-up");

  return section;
}
