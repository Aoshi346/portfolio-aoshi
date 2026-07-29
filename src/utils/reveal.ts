import "lenis/dist/lenis.css";
import type { MotionProfile, Theme } from "../themes/types";

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
  /*
   * Umbral por defecto de GSAP (500 ms / 33 ms), NO `lagSmoothing(0)`.
   *
   * Desactivarlo del todo — que es lo que suele copiarse de los ejemplos de
   * Lenis — hace que, tras un paron del hilo principal, GSAP aplique TODO el
   * tiempo transcurrido en un solo fotograma. Medido aqui: la compilacion del
   * shader de fondo bloquea lo suficiente como para que el leader de apertura
   * (1,62 s de timeline) se consumiera entero de una vez y la pantalla
   * saltara directa al hero.
   *
   * Con el umbral puesto, un fotograma que tarde mas de 500 ms se contabiliza
   * como 33 ms: las animaciones se retrasan en vez de evaporarse. Lenis sigue
   * yendo igual de fino — el suavizado solo actua en paradas anomalas, no en
   * el fotograma normal.
   */
  gsap.ticker.lagSmoothing(500, 33);

  wireFocusScroll(lenis);
}

/** Margen sobre el elemento enfocado, para que no quede pegado al borde ni
 *  debajo de la barra de orientacion de Vice. */
const FOCUS_OFFSET = -120;

/**
 * Al tabular, el navegador desplaza el scroll por su cuenta con un salto seco
 * que NO pasa por Lenis. Como la posicion de las escenas con `pin` la calcula
 * ScrollTrigger a partir del scroll que conoce Lenis, ese salto las deja a
 * medio asentar: el elemento enfocado cae dentro del viewport segun su
 * `getBoundingClientRect()`, pero lo que se pinta es una pantalla casi vacia.
 *
 * Retomamos el desplazamiento con Lenis para que vuelva a haber una sola
 * fuente de verdad del scroll y ScrollTrigger reciba su `update()`.
 */
function wireFocusScroll(lenis: { scrollTo: (target: HTMLElement, options: { offset: number; duration: number }) => void }): void {
  document.addEventListener("focusin", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    /*
     * Solo foco de TECLADO. `focusin` tambien dispara al hacer clic con el
     * raton, y eso convertia cada clic en un salto de scroll: pulsar una fila
     * de los creditos desplazaba la pagina 412px y sacaba el panel de detalle
     * fuera del encuadre — medido — dejando a la vista una franja vacia. Es
     * decir, el arreglo del salto al tabular habia creado un bug peor con el
     * raton, que es como se usa la seccion el 99% de las veces.
     *
     * `:focus-visible` es exactamente esta distincion, resuelta por el
     * navegador: es falso cuando el foco viene de un clic.
     */
    if (!target.matches(":focus-visible")) return;

    /*
     * Y aun con teclado, solo si el elemento no se ve entero. Tabular entre
     * dos filas contiguas ya visibles no debe mover nada: el salto solo tiene
     * sentido cuando el foco se va fuera del encuadre, que es el caso que
     * este manejador vino a resolver.
     */
    const box = target.getBoundingClientRect();
    if (box.top >= 0 && box.bottom <= window.innerHeight) return;

    lenis.scrollTo(target, { offset: FOCUS_OFFSET, duration: 0.5 });
  });
}

/**
 * Fija de forma SINCRONA el estado inicial del hero y retira `.js-intro` en
 * cuanto GSAP esta disponible, sin esperar a `document.fonts.ready` ni a
 * ningun timeout. Esa espera era la causante de que el nombre del hero
 * quedara invisible varios segundos (ver style.css): mientras `.js-intro`
 * siga puesta, `[data-hero-name]` tiene `opacity: 0` por CSS.
 *
 * Deja el nombre en un estado "pre-animacion" (visible pero desenfocado y
 * escalado) en vez de saltar directamente al estado final: la coreografia
 * propia del tema (`theme.choreography`, Vice) monta su gesto de entrada
 * encima de este punto de partida.
 */
function prepareHeroIntro(gsap: Gsap, root: HTMLElement): void {
  const name = root.querySelector<HTMLElement>("[data-hero-name]");
  if (!name) {
    document.documentElement.classList.remove("js-intro");
    return;
  }

  const fading = Array.from(root.querySelectorAll<HTMLElement>("[data-hero-fade]"));
  gsap.set(fading, { opacity: 0, y: 24 });
  gsap.set(name, { opacity: 1, scale: 1.08, filter: "blur(7px)" });
  document.documentElement.classList.remove("js-intro");
}

/**
 * Cablea los reveals de GSAP ScrollTrigger sobre el DOM ya montado. GSAP entra
 * por import dinamico para no pesar el bundle inicial; sin JS el contenido
 * queda visible igual (mejora progresiva).
 *
 * El tema activo aporta el ritmo (`motion`) y, opcionalmente, una coreografia
 * propia. Un tema con coreografia la usa en exclusiva: mezclarla con las
 * recetas genericas de aqui abajo haria que dos timelines peleen por el mismo
 * elemento. Los temas sin coreografia siguen con las recetas por atributo.
 */
export async function initScrollReveal(root: HTMLElement, theme: Theme): Promise<void> {
  const motion = theme.motion;
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) return;

  /*
   * El core de GSAP se pide SOLO, sin esperar a ScrollTrigger. Lo unico que
   * hace falta para retirar `.js-intro` y pintar el nombre del hero es
   * `prepareHeroIntro`, que no usa ScrollTrigger para nada — y ese nombre es
   * el elemento LCP de la pagina. Pedirlos juntos metia 17.5 kB gzip de
   * ScrollTrigger en el camino critico del primer pintado del titular, para
   * algo que no se necesita hasta que el usuario scrollea.
   *
   * La peticion de ScrollTrigger arranca inmediatamente despues, asi que no se
   * pierde paralelismo real: solo se deja de BLOQUEAR el hero con ella.
   */
  const { default: gsap } = await import("gsap");
  const scrollTriggerModule = import("gsap/ScrollTrigger");

  if (motion.style === "cinematic") {
    prepareHeroIntro(gsap, root);
  }

  const { ScrollTrigger } = await scrollTriggerModule;
  gsap.registerPlugin(ScrollTrigger);

  if (motion.style === "cinematic") {
    await initSmoothScroll(gsap, ScrollTrigger);
  }

  if (theme.choreography) {
    const choreography = await theme.choreography();
    choreography({ gsap, ScrollTrigger, root, motion });
    ScrollTrigger.refresh();
    return;
  }

  root.querySelectorAll<HTMLElement>("[data-reveal='chars']").forEach((target) => {
    revealHeadline(gsap, target, motion);
  });

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

  ScrollTrigger.refresh();
}
