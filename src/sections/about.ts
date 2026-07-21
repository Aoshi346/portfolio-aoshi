import { aboutCopy, identity } from "../data/content";
import { el } from "../utils/dom";

export function createAbout(): HTMLElement {
  const avatar = el("img", "h-16 w-16 rounded-full border border-paper/15 md:h-20 md:w-20", []);
  avatar.setAttribute("src", identity.githubAvatar);
  avatar.setAttribute("alt", identity.name);
  avatar.setAttribute("loading", "lazy");
  avatar.setAttribute("decoding", "async");
  avatar.setAttribute("width", "80");
  avatar.setAttribute("height", "80");

  const paragraphs = el(
    "div",
    "flex flex-col gap-5",
    aboutCopy.map((paragraph) => el("p", "max-w-2xl text-lg text-paper/75 md:text-xl", [paragraph])),
  );

  const section = el(
    "section",
    "mx-auto flex max-w-3xl flex-col gap-10 px-6 py-32 md:flex-row md:items-start md:px-0",
    [
      el("div", "flex shrink-0 flex-col items-start gap-4", [
        avatar,
        el("p", "text-sm text-paper/40", [identity.location]),
      ]),
      el("div", "flex flex-col gap-6", [
        el("p", "font-display text-sm uppercase tracking-[0.3em] text-accent", ["Quién es"]),
        paragraphs,
      ]),
    ],
  );
  section.setAttribute("data-reveal", "fade-up");

  return section;
}
