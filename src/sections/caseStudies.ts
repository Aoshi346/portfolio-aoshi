import { caseStudies } from "../data/content";
import { createCaseStudyPanel } from "../components/caseStudyPanel";
import { el } from "../utils/dom";

export function createCaseStudies(): HTMLElement {
  const heading = el("div", "mx-auto max-w-3xl px-6 pb-4 pt-32 md:px-0", [
    el("p", "font-mono text-sm uppercase tracking-[0.3em] text-accent", ["Casos de estudio"]),
    el("h2", "mt-4 max-w-xl text-balance font-display text-4xl font-bold md:text-6xl", [
      "Problemas reales, no ejercicios de portfolio.",
    ]),
  ]);
  heading.setAttribute("data-reveal", "fade-up");

  return el("section", "relative border-t border-paper/10", [
    heading,
    ...caseStudies.map((caseStudy, index) => createCaseStudyPanel(caseStudy, index)),
  ]);
}
