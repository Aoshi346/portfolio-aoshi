import type { CaseStudy } from "../data/content";
import { el } from "../utils/dom";

export function createCaseStudyPanel(caseStudy: CaseStudy, index: number): HTMLElement {
  const ordinal = el("span", "pointer-events-none absolute -top-10 right-0 font-display text-[13rem] font-bold leading-none text-paper/5 md:text-[18rem]", [
    String(index + 1).padStart(2, "0"),
  ]);
  ordinal.setAttribute("data-reveal", "ordinal");
  ordinal.setAttribute("aria-hidden", "true");

  const stackList = el(
    "ul",
    "flex flex-wrap gap-2",
    caseStudy.stack.map((tech) =>
      el("li", "rounded-full border border-paper/15 px-3 py-1 text-xs text-paper/60", [tech]),
    ),
  );

  const footer: (Node | string)[] = [stackList];
  if (caseStudy.link) {
    const link = el("a", "text-sm font-medium text-accent underline-offset-4 hover:underline", [
      `${caseStudy.link.label} →`,
    ]) as HTMLAnchorElement;
    link.href = caseStudy.link.href;
    link.target = "_blank";
    link.rel = "noreferrer";
    footer.push(link);
  } else if (caseStudy.privateProject) {
    footer.push(
      el("span", "text-sm text-paper/40", ["Proyecto privado de empresa · sin repositorio público"]),
    );
  }

  const article = el(
    "article",
    "relative mx-auto flex min-h-[80vh] max-w-3xl flex-col justify-center gap-6 overflow-hidden px-6 py-24 md:px-0",
    [
      ordinal,
      el("p", "font-display text-sm uppercase tracking-[0.3em] text-accent", [caseStudy.tag]),
      el("h3", "max-w-xl text-balance font-display text-4xl font-bold md:text-6xl", [
        caseStudy.title,
      ]),
      el("div", "grid gap-6 md:grid-cols-2", [
        el("div", "flex flex-col gap-2", [
          el("p", "text-xs uppercase tracking-[0.2em] text-paper/40", ["Problema"]),
          el("p", "text-base text-paper/75 md:text-lg", [caseStudy.problem]),
        ]),
        el("div", "flex flex-col gap-2", [
          el("p", "text-xs uppercase tracking-[0.2em] text-paper/40", ["Solución"]),
          el("p", "text-base text-paper/75 md:text-lg", [caseStudy.solution]),
        ]),
      ]),
      el("div", "flex flex-col gap-4 pt-2 md:flex-row md:items-center md:justify-between", footer),
    ],
  );
  article.setAttribute("data-reveal", "fade-up");

  return article;
}
