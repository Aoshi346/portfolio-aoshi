import { education, experience } from "../data/content";
import { el } from "../utils/dom";

function createExperienceItem(item: (typeof experience)[number]): HTMLElement {
  const node = el(
    "div",
    "flex flex-col gap-1 border-l border-paper/15 pl-6 transition-colors duration-300 ease-out hover:border-accent/50",
    [
      el("p", "font-mono text-xs uppercase tracking-[0.2em] text-paper/40", [item.period]),
      el("h3", "font-display text-xl font-bold md:text-2xl", [item.role]),
      el("p", "text-sm text-paper/60", [item.organization]),
      el("p", "mt-1 max-w-md text-base text-paper/70", [item.description]),
    ],
  );
  node.setAttribute("data-stagger-item", "");
  return node;
}

function createEducationItem(item: (typeof education)[number]): HTMLElement {
  const node = el(
    "div",
    "flex flex-col gap-1 border-l border-paper/15 pl-6 transition-colors duration-300 ease-out hover:border-accent/50",
    [
      el("p", "font-mono text-xs uppercase tracking-[0.2em] text-paper/40", [item.period]),
      el("h3", "font-display text-xl font-bold md:text-2xl", [item.degree]),
      el("p", "text-sm text-paper/60", [item.institution]),
    ],
  );
  node.setAttribute("data-stagger-item", "");
  return node;
}

export function createExperience(): HTMLElement {
  const heading = el("div", "mx-auto max-w-3xl px-6 pb-12 md:px-0", [
    el("p", "font-mono text-sm uppercase tracking-[0.3em] text-accent", [
      "Experiencia y educación",
    ]),
  ]);
  heading.setAttribute("data-reveal", "fade-up");

  const columns = el("div", "mx-auto grid max-w-3xl gap-12 px-6 md:grid-cols-2 md:px-0", [
    el("div", "flex flex-col gap-8", [
      el("p", "text-sm text-paper/40", ["Experiencia"]),
      ...experience.map(createExperienceItem),
    ]),
    el("div", "flex flex-col gap-8", [
      el("p", "text-sm text-paper/40", ["Educación"]),
      ...education.map(createEducationItem),
    ]),
  ]);
  columns.setAttribute("data-reveal", "stagger");

  return el("section", "border-t border-paper/10 py-32", [heading, columns]);
}
