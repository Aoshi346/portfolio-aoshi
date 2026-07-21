import { identity } from "../data/content";
import { el } from "../utils/dom";

export function createNav(): HTMLElement {
  const initials = el("span", "font-mono text-sm tracking-widest text-paper/80", ["AB"]);

  const githubLink = el("a", "text-sm text-paper/70 transition-colors hover:text-accent", [
    "GitHub",
  ]) as HTMLAnchorElement;
  githubLink.href = identity.github;
  githubLink.target = "_blank";
  githubLink.rel = "noreferrer";

  const contactLink = el(
    "a",
    "rounded-full border border-paper/20 px-4 py-1.5 text-sm text-paper transition-colors hover:border-accent hover:text-accent",
    ["Contacto"],
  ) as HTMLAnchorElement;
  contactLink.href = "#contacto";

  return el("nav", "fixed inset-x-0 top-0 z-50 flex items-center justify-between px-6 py-5 md:px-12", [
    initials,
    el("div", "flex items-center gap-6", [githubLink, contactLink]),
  ]);
}
