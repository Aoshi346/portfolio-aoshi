import { identity } from "../data/content";
import { el } from "../utils/dom";

export function createFooter(): HTMLElement {
  const year = new Date().getFullYear();

  const links = [
    { label: identity.email, href: `mailto:${identity.email}` },
    { label: "GitHub", href: identity.github },
  ].map(({ label, href }) => {
    const link = el("a", "text-sm text-paper/60 transition-colors hover:text-accent", [
      label,
    ]) as HTMLAnchorElement;
    link.href = href;
    if (href.startsWith("http")) {
      link.target = "_blank";
      link.rel = "noreferrer";
    }
    return link;
  });

  return el("footer", "flex flex-col items-center gap-4 border-t border-paper/10 px-6 py-10 text-center md:flex-row md:justify-between md:px-12", [
    el("p", "text-sm text-paper/40", [`© ${year} ${identity.name}`]),
    el("div", "flex items-center gap-6", links),
  ]);
}
