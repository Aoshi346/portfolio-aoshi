import "lenis/dist/lenis.css";
import type { MotionProfile } from "../themes/types";

type Gsap = typeof import("gsap").default;
type ScrollTriggerApi = typeof import("gsap/ScrollTrigger").ScrollTrigger;

/**
 * Parte el texto en spans, agrupados por palabra para que el salto de linea
 * siga siendo natural. Se hace a mano en vez de con SplitText (plugin) para no
 * atar el redisenio a la disponibilidad del plugin.
 *
 * Devuelve los caracteres y las palabras: cada tema anima la unidad que le toca.
 */
function splitText(
  target: HTMLElement,
  masked = false,
): { chars: HTMLElement[]; words: HTMLElement[] } {
  const text = target.textContent ?? "";
  target.textContent = "";

  const chars: HTMLElement[] = [];
  const words: HTMLElement[] = [];
  const parts = text.split(" ");

  parts.forEach((word, wordIndex) => {
    const wordSpan = document.createElement("span");
    // Con mascara, cada palabra recorta lo que sobresale: las letras suben
    // desde "detras" de la linea en vez de aparecer flotando.
    wordSpan.className = masked
      ? "inline-block overflow-hidden whitespace-nowrap align-bottom"
      : "inline-block whitespace-nowrap";

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
 * Scroll con inercia (Lenis). Es lo que separa un scroll de navegador de uno
 * de pieza cinematografica: el zoom del hero se lee muchisimo mejor cuando el
 * scroll tiene peso. Se engancha al ticker de GSAP para no abrir un segundo
 * RAF y se sincroniza con ScrollTrigger.
 */
async function initSmoothScroll(gsap: Gsap, scrollTrigger: ScrollTriggerApi): Promise<void> {
  const { default: Lenis } = await import("lenis");

  const lenis = new Lenis({ duration: 1.15, smoothWheel: true });
  lenis.on("scroll", () => scrollTrigger.update());
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
}

/**
 * Secuencia de entrada de Vice City. El nombre no "aparece": se monta letra a
 * letra desde el centro hacia fuera, estirado y cayendo en su sitio, y el
 * resto del hero entra despues en cascada.
 *
 * Los elementos estan ocultos por CSS (`.js-intro`) hasta que GSAP fija el
 * estado inicial, para que no haya salto entre el pintado y la animacion.
 * main.ts retira la clase por timeout si GSAP no llegara a cargar.
 */
async function playCinematicIntro(gsap: Gsap, root: HTMLElement): Promise<void> {
  const name = root.querySelector<HTMLElement>("[data-hero-name]");
  if (!name) return;

  // Partir el texto antes de que cargue la tipografia mediria mal las letras y
  // la linea saltaria a mitad de animacion. El limite evita colgar la entrada.
  await Promise.race([
    document.fonts.ready,
    new Promise((resolve) => window.setTimeout(resolve, 1200)),
  ]);

  const { chars } = splitText(name, true);
  const fading = Array.from(root.querySelectorAll<HTMLElement>("[data-hero-fade]"));

  gsap.set(chars, { yPercent: 115 });
  gsap.set(name, { scale: 1.08, filter: "blur(7px)" });
  gsap.set(fading, { opacity: 0, y: 24 });
  document.documentElement.classList.remove("js-intro");

  const timeline = gsap.timeline();

  // Empuje de camara sobre el titulo entero: lento y sostenido, es lo que da
  // el aire de plano de apertura.
  timeline.to(name, { scale: 1, filter: "blur(0px)", duration: 2.4, ease: "power2.out" }, 0);

  // La duracion percibida la manda el stagger, no el easing: con expo.out el
  // 96% del recorrido se gastaba en 250 ms y la entrada se leia instantanea.
  timeline.to(
    chars,
    { yPercent: 0, duration: 1.0, ease: "power3.out", stagger: 0.075 },
    0.25,
  );

  timeline.to(
    fading,
    { opacity: 1, y: 0, duration: 0.9, ease: "power2.out", stagger: 0.14 },
    1.5,
  );
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

  const isCinematic = motion.style === "cinematic";

  if (isCinematic) {
    await initSmoothScroll(gsap, ScrollTrigger);
    playCinematicIntro(gsap, root);
  }

  root.querySelectorAll<HTMLElement>("[data-reveal='chars']").forEach((target) => {
    // En cinematic el nombre lo monta la secuencia de entrada, no el scroll.
    if (isCinematic && target.hasAttribute("data-hero-name")) return;
    revealHeadline(gsap, target, motion);
  });

  if (isCinematic) wireHeroZoom(gsap, root);

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
