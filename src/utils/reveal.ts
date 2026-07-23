import type { MotionProfile } from "../themes/types";

/**
 * Parte el texto de un elemento en spans por caracter, agrupados por palabra
 * para que el salto de linea siga siendo natural. Se hace a mano en vez de con
 * SplitText (plugin) para no atar el redisenio a la disponibilidad del plugin.
 */
function splitToChars(target: HTMLElement): HTMLElement[] {
  const text = target.textContent ?? "";
  target.textContent = "";

  const chars: HTMLElement[] = [];
  const words = text.split(" ");

  words.forEach((word, wordIndex) => {
    const wordSpan = document.createElement("span");
    wordSpan.className = "inline-block whitespace-nowrap";

    for (const character of word) {
      const charSpan = document.createElement("span");
      charSpan.className = "inline-block";
      charSpan.textContent = character;
      wordSpan.append(charSpan);
      chars.push(charSpan);
    }

    target.append(wordSpan);
    // Espacio real entre palabras: permite que la linea rompa donde toca.
    if (wordIndex < words.length - 1) target.append(document.createTextNode(" "));
  });

  return chars;
}

/**
 * Cablea los reveals de GSAP ScrollTrigger sobre el DOM ya montado. GSAP entra
 * por import dinamico para no pesar el bundle inicial; sin JS el contenido
 * queda visible igual (mejora progresiva).
 *
 * El `motion` lo aporta el tema activo: el ritmo tambien cambia entre temas.
 */
export async function initScrollReveal(root: HTMLElement, motion: MotionProfile): Promise<void> {
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  const [{ default: gsap }, { ScrollTrigger }] = await Promise.all([
    import("gsap"),
    import("gsap/ScrollTrigger"),
  ]);
  gsap.registerPlugin(ScrollTrigger);

  // Tipografia cinetica: los caracteres suben y se ensamblan al entrar.
  root.querySelectorAll<HTMLElement>("[data-reveal='chars']").forEach((target) => {
    const chars = splitToChars(target);
    gsap.from(chars, {
      yPercent: 118,
      opacity: 0,
      duration: motion.duration,
      ease: motion.ease,
      stagger: motion.stagger * 0.35,
      scrollTrigger: {
        trigger: target,
        start: "top 88%",
        toggleActions: "play none none reverse",
      },
    });
  });

  root.querySelectorAll<HTMLElement>("[data-reveal='fade-up']").forEach((target) => {
    gsap.from(target, {
      y: 48,
      opacity: 0,
      duration: motion.duration,
      ease: motion.ease,
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
      duration: motion.duration * 1.1,
      ease: motion.ease,
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
      duration: motion.duration * 0.7,
      ease: motion.ease,
      stagger: motion.stagger,
      scrollTrigger: {
        trigger: group,
        start: "top 85%",
        toggleActions: "play none none reverse",
      },
    });
  });

  // Scroll-scrub sutil sobre los ordinales gigantes de cada escena:
  // desplazamiento contenido para que se lea como profundidad, no como ruido.
  root.querySelectorAll<HTMLElement>("[data-reveal='ordinal']").forEach((target) => {
    gsap.to(target, {
      yPercent: -12,
      ease: "none",
      scrollTrigger: {
        trigger: target.closest("section") ?? target,
        start: "top bottom",
        end: "bottom top",
        scrub: 0.6,
      },
    });
  });

  // Parallax por capas: el elemento se desplaza a una fraccion de la velocidad
  // de scroll, marcada por data-parallax-speed (0-1, por defecto 0.3).
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
