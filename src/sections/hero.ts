import { identity } from "../data/content";
import { el } from "../utils/dom";
import type { HeroSceneHandle } from "../three/heroScene";

export function createHero(): HTMLElement {
  const canvasHost = el(
    "div",
    "pointer-events-none absolute inset-0 -z-10 opacity-0 transition-opacity duration-1000",
  );
  canvasHost.setAttribute("aria-hidden", "true");
  canvasHost.setAttribute("data-parallax", "");
  canvasHost.dataset.parallaxSpeed = "0.4";

  const section = el(
    "section",
    "relative flex min-h-screen flex-col justify-center overflow-hidden px-6 md:px-12",
    [
      canvasHost,
      el("p", "font-mono text-sm uppercase tracking-[0.3em] text-accent", [identity.role]),
      el(
        "h1",
        "mt-6 max-w-4xl text-balance font-display text-6xl font-bold leading-[0.95] md:text-8xl",
        [identity.headline],
      ),
      el("p", "mt-8 max-w-xl text-lg text-paper/70 md:text-xl", [identity.subheadline]),
      el("div", "mt-16 flex items-center gap-3 text-xs uppercase tracking-[0.3em] text-paper/40", [
        el("span", "block h-px w-8 bg-paper/40", []),
        "Desplázate",
      ]),
    ],
  );

  let sceneHandle: HeroSceneHandle | null = null;

  void import("../three/heroScene").then(({ mountHeroScene }) => {
    sceneHandle = mountHeroScene(canvasHost);
    requestAnimationFrame(() => canvasHost.classList.remove("opacity-0"));
  });

  window.addEventListener("beforeunload", () => sceneHandle?.destroy(), { once: true });

  return section;
}
