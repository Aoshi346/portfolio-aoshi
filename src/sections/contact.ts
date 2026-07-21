import { identity } from "../data/content";
import { el } from "../utils/dom";

export function createContact(): HTMLElement {
  const emailLink = el(
    "a",
    "break-words font-display text-2xl font-bold text-paper transition-[color,letter-spacing] duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] hover:text-accent hover:tracking-wide sm:text-4xl md:text-7xl",
    [identity.email],
  ) as HTMLAnchorElement;
  emailLink.href = `mailto:${identity.email}`;

  const githubLink = el(
    "a",
    "group/gh inline-flex items-center gap-1.5 text-lg text-paper/70 underline-offset-4 transition-colors duration-300 ease-out hover:text-accent hover:underline",
    [
      "Ver perfil de GitHub",
      el(
        "span",
        "inline-block transition-transform duration-300 ease-[cubic-bezier(0.19,1,0.22,1)] group-hover/gh:translate-x-1",
        ["→"],
      ),
    ],
  ) as HTMLAnchorElement;
  githubLink.href = identity.github;
  githubLink.target = "_blank";
  githubLink.rel = "noreferrer";

  const section = el(
    "section",
    "flex min-h-[70vh] flex-col items-start justify-center gap-8 border-t border-paper/10 px-6 py-32 md:px-0",
    [
      el("p", "mx-auto w-full max-w-3xl font-mono text-sm uppercase tracking-[0.3em] text-accent", [
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
