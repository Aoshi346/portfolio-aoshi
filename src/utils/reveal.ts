import type { MotionProfile } from "../themes/types";

type Gsap = typeof import("gsap").default;

/**
 * Parte el texto en spans, agrupados por palabra para que el salto de linea
 * siga siendo natural. Se hace a mano en vez de con SplitText (plugin) para no
 * atar el redisenio a la disponibilidad del plugin.
 *
 * Devuelve los caracteres y las palabras: cada tema anima la unidad que le toca.
 */
function splitText(target: HTMLElement): { chars: HTMLElement[]; words: HTMLElement[] } {
  const text = target.textContent ?? "";
  target.textContent = "";

  const chars: HTMLElement[] = [];
  const words: HTMLElement[] = [];
  const parts = text.split(" ");

  parts.forEach((word, wordIndex) => {
    const wordSpan = document.createElement("span");
    wordSpan.className = "inline-block whitespace-nowrap";

    for (const character of word) {
      const charSpan = document.createElement("span");
      charSpan.className = "inline-block";
      charSpan.textContent = character;
      wordSpan.append(charSpan);
      chars.push(charSpan);
    }

    words.push(wordSpan);
    target.append(wordSpan);
    // Espacio real entre palabras: permite que la linea rompa donde toca.
    if (wordIndex < parts.length - 1) target.append(document.createTextNode(" "));
  });

  return { chars, words };
}

/** Tipografia cinetica: cada estilo entra por una unidad y un gesto distintos. */
function revealHeadline(gsap: Gsap, target: HTMLElement, motion: MotionProfile): void {
  const { chars, words } = splitText(target);
  const scrollTrigger = { trigger: target, start: "top 88%", toggleActions: "play none none reverse" };

  if (motion.style === "fluid") {
    // Caelestia: por palabras, enfocando desde el desenfoque con sobre-impulso.
    gsap.from(words, {
      y: 30,
      opacity: 0,
      scale: 0.94,
      filter: "blur(14px)",
      duration: motion.duration,
      ease: motion.ease,
      stagger: motion.stagger,
      scrollTrigger,
    });
    return;
  }

  if (motion.style === "cinematic") {
    // Vice: los caracteres suben estirados, como un cartel que se monta.
    gsap.from(chars, {
      yPercent: 130,
      opacity: 0,
      scaleY: 1.35,
      transformOrigin: "50% 100%",
      duration: motion.duration,
      ease: motion.ease,
      stagger: motion.stagger * 0.3,
      scrollTrigger,
    });
    return;
  }

  // Hyprland: seco, caracter a caracter.
  gsap.from(chars, {
    yPercent: 118,
    opacity: 0,
    duration: motion.duration,
    ease: motion.ease,
    stagger: motion.stagger * 0.35,
    scrollTrigger,
  });
}

/**
 * El gesto firma de Vice City: al hacer scroll el hero queda fijado y el nombre
 * crece hasta atravesar la pantalla, como el titulo de GTA. El resto del hero
 * se desvanece antes para que el nombre mande.
 */
function wireHeroZoom(gsap: Gsap, root: HTMLElement): void {
  const hero = root.querySelector<HTMLElement>("[data-hero]");
  const heroName = root.querySelector<HTMLElement>("[data-hero-name]");
  if (!hero || !heroName) return;

  const fading = Array.from(root.querySelectorAll<HTMLElement>("[data-hero-fade]"));

  const timeline = gsap.timeline({
    scrollTrigger: {
      trigger: hero,
      start: "top top",
      end: "+=150%",
      pin: true,
      scrub: 1,
      anticipatePin: 1,
    },
  });

  if (fading.length > 0) {
    timeline.to(fading, { opacity: 0, y: -30, ease: "none", duration: 0.35 }, 0);
  }
  // La aceleracion (power2.in) es lo que vende el "atravesar": lento al
  // principio, se dispara al final.
  timeline.to(heroName, { scale: 9, opacity: 0, ease: "power2.in", duration: 1 }, 0);
}

/**
 * Cablea los reveals de GSAP ScrollTrigger sobre el DOM ya montado. GSAP entra
 * por import dinamico para no pesar el bundle inicial; sin JS el contenido
 * queda visible igual (mejora progresiva).
 *
 * El `motion` lo aporta el tema activo: el ritmo y las recetas cambian entre temas.
 */
export async function initScrollReveal(root: HTMLElement, motion: MotionProfile): Promise<void> {
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  const [{ default: gsap }, { ScrollTrigger }] = await Promise.all([
    import("gsap"),
    import("gsap/ScrollTrigger"),
  ]);
  gsap.registerPlugin(ScrollTrigger);

  root
    .querySelectorAll<HTMLElement>("[data-reveal='chars']")
    .forEach((target) => revealHeadline(gsap, target, motion));

  if (motion.style === "cinematic") wireHeroZoom(gsap, root);

  root.querySelectorAll<HTMLElement>("[data-reveal='fade-up']").forEach((target) => {
    const scrollTrigger = {
      trigger: target,
      start: "top 85%",
      toggleActions: "play none none reverse",
    };

    if (motion.style === "fluid") {
      gsap.from(target, {
        y: 26,
        opacity: 0,
        scale: 0.97,
        filter: "blur(10px)",
        duration: motion.duration,
        ease: motion.ease,
        scrollTrigger,
      });
      return;
    }

    gsap.from(target, {
      y: motion.style === "cinematic" ? 64 : 40,
      opacity: 0,
      duration: motion.duration,
      ease: motion.ease,
      scrollTrigger,
    });
  });

  root.querySelectorAll<HTMLElement>("[data-reveal='stagger']").forEach((group) => {
    const items = group.querySelectorAll<HTMLElement>("[data-stagger-item]");
    const targets = items.length > 0 ? Array.from(items) : Array.from(group.children);
    const scrollTrigger = {
      trigger: group,
      start: "top 85%",
      toggleActions: "play none none reverse",
    };

    if (motion.style === "fluid") {
      // Los chips no suben: brotan (Material You piensa en superficies que crecen).
      gsap.from(targets, {
        scale: 0.7,
        opacity: 0,
        duration: motion.duration * 0.6,
        ease: motion.ease,
        stagger: motion.stagger,
        scrollTrigger,
      });
      return;
    }

    gsap.from(targets, {
      y: 24,
      opacity: 0,
      duration: motion.duration * 0.7,
      ease: motion.ease,
      stagger: motion.stagger,
      scrollTrigger,
    });
  });

  // Scroll-scrub sobre los ordinales gigantes: profundidad, no ruido.
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

  // Parallax por capas: fraccion de la velocidad de scroll (data-parallax-speed).
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
