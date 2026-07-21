import { secondarySkills, skillGroups, type SkillItem } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { getIconMarkup } from "../utils/icons";

function createSkillCard(item: SkillItem): HTMLElement {
  const icon = elFromMarkup("tech-icon h-8 w-8 shrink-0 text-paper/80", getIconMarkup(item.slug));

  const detail = el(
    "p",
    "max-h-0 overflow-hidden text-sm text-paper/60 opacity-0 transition-[max-height,opacity] duration-300 ease-out group-hover:max-h-20 group-hover:opacity-100 group-focus-within:max-h-20 group-focus-within:opacity-100",
    [item.detail],
  );

  const card = el(
    "div",
    "group flex flex-col gap-3 rounded-2xl border border-paper/10 bg-paper/[0.03] p-5 transition-colors duration-300 hover:border-accent/40 focus-within:border-accent/40",
    [
      el("div", "flex items-center gap-3", [
        icon,
        el("span", "font-display text-lg font-semibold text-paper", [item.name]),
      ]),
      detail,
    ],
  );
  card.tabIndex = 0;

  return card;
}

function createSkillGroup(group: (typeof skillGroups)[number]): HTMLElement {
  return el("div", "flex flex-col gap-5", [
    el("h3", "font-mono text-xs uppercase tracking-[0.3em] text-paper/40", [group.label]),
    el(
      "div",
      "grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4",
      group.items.map(createSkillCard),
    ),
  ]);
}

function createSecondarySkills(): HTMLElement {
  return el("div", "flex flex-col gap-4", [
    el("h3", "font-mono text-xs uppercase tracking-[0.3em] text-paper/40", ["Otras herramientas"]),
    el(
      "div",
      "flex flex-wrap gap-2",
      secondarySkills.map((item) =>
        el("span", "rounded-full border border-paper/15 px-4 py-1.5 text-sm text-paper/70", [
          item.name,
        ]),
      ),
    ),
  ]);
}

export function createSkills(): HTMLElement {
  const heading = el("div", "mx-auto max-w-3xl px-6 pb-12 md:px-0", [
    el("p", "font-mono text-sm uppercase tracking-[0.3em] text-accent", ["Stack"]),
    el("h2", "mt-4 max-w-xl text-balance font-display text-4xl font-bold md:text-6xl", [
      "Lo que uso según el peso del problema.",
    ]),
  ]);
  heading.setAttribute("data-reveal", "fade-up");

  const groups = el(
    "div",
    "mx-auto flex max-w-3xl flex-col gap-12 px-6 md:px-0",
    [...skillGroups.map((group) => createSkillGroup(group)), createSecondarySkills()],
  );
  groups.setAttribute("data-reveal", "fade-up");

  return el("section", "border-t border-paper/10 py-32", [heading, groups]);
}
