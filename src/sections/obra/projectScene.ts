import type { CaseStudy } from "../../data/content";
import { el } from "../../utils/dom";

/**
 * Una escena a pantalla completa por proyecto: la obra es la protagonista.
 * El ordinal gigante hace de telon con scrub de scroll; los chips y la
 * superficie usan `--radius-card`, asi que el redondeo cambia con el tema.
 */
export function createProjectScene(project: CaseStudy, index: number): HTMLElement {
  const ordinal = el(
    "span",
    "pointer-events-none absolute right-0 top-[10%] select-none font-display text-[clamp(7rem,26vw,22rem)] font-black leading-none text-paper/[0.06]",
    [String(index + 1).padStart(2, "0")],
  );
  ordinal.setAttribute("aria-hidden", "true");
  ordinal.setAttribute("data-reveal", "ordinal");

  const tag = el("p", "font-mono text-[0.65rem] uppercase tracking-[0.35em] text-accent", [
    project.tag,
  ]);

  const title = el("h2", "display-lg mt-5 max-w-3xl text-[clamp(2.2rem,7vw,5.5rem)]", [
    project.title,
  ]);
  title.setAttribute("data-reveal", "chars");

  const problem = el("div", "", [
    el("p", "font-mono text-[0.65rem] uppercase tracking-[0.3em] text-paper/40", ["Problema"]),
    el("p", "mt-3 text-base leading-relaxed text-paper/70", [project.problem]),
  ]);

  const solution = el("div", "", [
    el("p", "font-mono text-[0.65rem] uppercase tracking-[0.3em] text-paper/40", ["Solución"]),
    el("p", "mt-3 text-base leading-relaxed text-paper/80", [project.solution]),
  ]);

  const body = el("div", "mt-10 grid max-w-4xl gap-8 md:grid-cols-2", [problem, solution]);
  body.setAttribute("data-reveal", "fade-up");

  const chips = el(
    "div",
    "flex flex-wrap gap-2",
    project.stack.map((tech) => {
      const chip = el(
        "span",
        "chip rounded-card border border-line bg-paper/[0.04] px-3 py-1.5 font-mono text-[0.65rem] uppercase tracking-[0.15em] text-paper/70",
        [tech],
      );
      chip.setAttribute("data-stagger-item", "");
      return chip;
    }),
  );
  chips.setAttribute("data-reveal", "stagger");

  const footerChildren: HTMLElement[] = [chips];

  if (project.link) {
    const link = el(
      "a",
      "group/link inline-flex items-center gap-2 font-mono text-sm text-paper transition-colors duration-300 hover:text-accent",
      [
        project.link.label,
        el("span", "transition-transform duration-300 group-hover/link:translate-x-1", ["→"]),
      ],
    );
    link.href = project.link.href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    footerChildren.push(link);
  } else if (project.privateProject) {
    footerChildren.push(
      el("p", "font-mono text-xs uppercase tracking-[0.2em] text-paper/40", [
        "Proyecto privado de empresa",
      ]),
    );
  }

  const footer = el(
    "div",
    "mt-12 flex flex-col gap-6 md:flex-row md:items-center md:justify-between",
    footerChildren,
  );

  const surface = el("div", "scene-surface relative", [tag, title, body, footer]);

  return el(
    "section",
    "scene relative flex min-h-screen flex-col justify-center overflow-hidden border-t border-line px-6 py-24 md:px-12",
    [ordinal, surface],
  );
}
