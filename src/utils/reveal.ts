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

  root.querySelectorAll<HTMLElement>("[data-reveal='clip']").forEach((target) => {
    gsap.from(target, {
      clipPath: "inset(0 0 100% 0)",
      opacity: 0,
      duration: 1.1,
      ease: "expo.out",
      scrollTrigger: {
        trigger: target,
        start: "top 85%",
        toggleActions: "play none none reverse",
      },
    });
  });

  root.querySelectorAll<HTMLElement>("[data-reveal='stagger']").forEach((group) => {
    const items = group.querySelectorAll<HTMLElement>("[data-stagger-item]");
    const targets = items.length > 0 ? Array.from(items) : Array.from(group.children);
    gsap.from(targets, {
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

  // Scroll-scrub sutil sobre los números ordinales de los casos de estudio:
  // desplazamiento contenido para que se lea como profundidad, no como ruido.
  root.querySelectorAll<HTMLElement>("[data-reveal='ordinal']").forEach((target) => {
    gsap.to(target, {
      yPercent: -10,
      ease: "none",
      scrollTrigger: {
        trigger: target.closest("section") ?? target,
        start: "top bottom",
        end: "bottom top",
        scrub: 0.6,
      },
    });
  });

  // Parallax sutil por capas: el elemento se desplaza a una fracción de la
  // velocidad de scroll, marcada por data-parallax-speed (0-1, por defecto 0.3).
  root.querySelectorAll<HTMLElement>("[data-parallax]").forEach((target) => {
    const speed = Number(target.dataset.parallaxSpeed ?? "0.3");
    gsap.to(target, {
      yPercent: speed * 20,
      ease: "none",
      scrollTrigger: {
        trigger: target.closest("section") ?? target,
        start: "top bottom",
        end: "bottom top",
        scrub: 0.6,
      },
    });
  });

  ScrollTrigger.refresh();
}
