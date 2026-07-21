/**
 * Wire GSAP ScrollTrigger reveals onto elements already present in the DOM.
 * GSAP/ScrollTrigger load via dynamic import so they never sit in the main
 * bundle; content stays fully visible without JS (progressive enhancement).
 */
export async function initScrollReveal(root: HTMLElement): Promise<void> {
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  const [{ default: gsap }, { ScrollTrigger }] = await Promise.all([
    import("gsap"),
    import("gsap/ScrollTrigger"),
  ]);
  gsap.registerPlugin(ScrollTrigger);

  root.querySelectorAll<HTMLElement>("[data-reveal='fade-up']").forEach((target) => {
    gsap.from(target, {
      y: 48,
      opacity: 0,
      duration: 0.9,
      ease: "power3.out",
      scrollTrigger: {
        trigger: target,
        start: "top 85%",
        toggleActions: "play none none reverse",
      },
    });
  });

  root.querySelectorAll<HTMLElement>("[data-reveal='stagger']").forEach((group) => {
    gsap.from(Array.from(group.children), {
      y: 24,
      opacity: 0,
      duration: 0.7,
      ease: "power2.out",
      stagger: 0.08,
      scrollTrigger: {
        trigger: group,
        start: "top 85%",
        toggleActions: "play none none reverse",
      },
    });
  });

  ScrollTrigger.refresh();
}
