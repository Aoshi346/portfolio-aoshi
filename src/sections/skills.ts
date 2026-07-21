import { skillGroups } from "../data/content";
import { el } from "../utils/dom";

const GROUP_SCALE = ["text-3xl md:text-5xl", "text-2xl md:text-4xl", "text-xl md:text-3xl"];

function createSkillGroup(group: (typeof skillGroups)[number], index: number): HTMLElement {
  const titleScale = GROUP_SCALE[index] ?? GROUP_SCALE[GROUP_SCALE.length - 1];

  const items = el(
    "div",
    "flex flex-wrap gap-2",
    group.items.map((item) =>
      el("span", "rounded-full border border-paper/15 px-4 py-1.5 text-sm text-paper/70", [item]),
    ),
  );

  return el("div", "flex flex-col gap-4", [
    el("h3", `font-display font-bold text-paper ${titleScale}`, [group.label]),
    items,
  ]);
}

export function createSkills(): HTMLElement {
  const heading = el("div", "mx-auto max-w-3xl px-6 pb-12 md:px-0", [
    el("p", "font-display text-sm uppercase tracking-[0.3em] text-accent", ["Stack"]),
    el("h2", "mt-4 max-w-xl text-balance font-display text-4xl font-bold md:text-6xl", [
      "Lo que usa según el peso del problema.",
    ]),
  ]);
  heading.setAttribute("data-reveal", "fade-up");

  const groups = el(
    "div",
    "mx-auto flex max-w-3xl flex-col gap-10 px-6 md:px-0",
    skillGroups.map((group, index) => createSkillGroup(group, index)),
  );
  groups.setAttribute("data-reveal", "stagger");

  return el("section", "border-t border-paper/10 py-32", [heading, groups]);
}
