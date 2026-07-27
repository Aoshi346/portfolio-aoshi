import type { Choreography, Gsap, ScrollTriggerApi } from "./choreography";

/** Id fijo del ScrollTrigger del zoom: permite matarlo si la funcion se re-ejecuta. */
const HERO_ZOOM_TRIGGER_ID = "vice-hero-zoom";

/**
 * Timeline de entrada (sin scrollTrigger, por eso no la mata `ScrollTrigger.getById`).
 * Se guarda a nivel de modulo para poder matarla si `scene1Title` se re-ejecutara,
 * evitando que quede corriendo sobre spans de caracteres ya destruidos por el
 * siguiente `splitChars`.
 */
let introTimeline: ReturnType<Gsap["timeline"]> | null = null;

/**
 * Parte el texto en spans por caracter, agrupados por palabra para que la
 * linea siga rompiendo donde toca. A mano en vez de con SplitText para no
 * atar el redisenio a la disponibilidad del plugin.
 */
function splitChars(target: HTMLElement): HTMLElement[] {
  const text = target.textContent ?? "";
  target.textContent = "";
  const chars: HTMLElement[] = [];
  const words = text.split(" ");

  words.forEach((word, index) => {
    const wordSpan = document.createElement("span");
    wordSpan.className = "inline-block overflow-hidden whitespace-nowrap align-bottom";
    for (const character of word) {
      const charSpan = document.createElement("span");
      charSpan.className = "inline-block";
      charSpan.textContent = character;
      wordSpan.append(charSpan);
      chars.push(charSpan);
    }
    target.append(wordSpan);
    if (index < words.length - 1) target.append(document.createTextNode(" "));
  });

  return chars;
}

/**
 * Gesto 1 — Titulo de apertura: el nombre se monta y luego te atraviesa.
 *
 * El estado "pre-animacion" (opacity:1, scale:1.08, blur) ya lo fija de forma
 * SINCRONA `prepareHeroIntro` en `utils/reveal.ts`, antes de que este modulo
 * siquiera se cargue (import dinamico -> hueco async). Lo unico que hace este
 * gesto es partir el texto (sincrono, no depende de fuentes) y montar encima
 * la entrada + el zoom de salida.
 *
 * El tween de salida usa `fromTo` con los valores de partida escritos a mano
 * (scale:1, opacity:1), nunca leidos del DOM en el instante del render: leer
 * del DOM fue la causa de la regresion original (ver docs/superpowers/sdd),
 * cuando la CSS de `.js-intro` todavia no se habia retirado y GSAP capturaba
 * opacity:0 como punto de partida, animando de 0 a 0 para siempre.
 */
function scene1Title(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const hero = root.querySelector<HTMLElement>('[data-scene="hero"]');
  const name = root.querySelector<HTMLElement>("[data-hero-name]");
  if (!hero || !name) return;

  // Defensivo: si esta funcion se llamara dos veces (hoy no ocurre: el tema se
  // elige una sola vez por carga), no dejar un trigger huerfano acumulandose.
  ScrollTrigger.getById(HERO_ZOOM_TRIGGER_ID)?.kill();
  // La timeline de entrada no tiene scrollTrigger propio, asi que
  // `ScrollTrigger.getById` no la alcanza: hay que matarla a mano.
  introTimeline?.kill();

  const chars = splitChars(name);
  const fading = Array.from(root.querySelectorAll<HTMLElement>("[data-hero-fade]"));

  gsap.set(chars, { yPercent: 115 });
  gsap.set(fading, { opacity: 0, y: 24 });

  const intro = gsap.timeline();
  introTimeline = intro;
  // Empuje de camara: lento y sostenido, da el aire de plano de apertura.
  intro.to(name, { scale: 1, filter: "blur(0px)", duration: 2.4, ease: "power2.out" }, 0);
  // La duracion percibida la manda el stagger, no el easing: con expo.out el
  // 96% del recorrido se gastaba en 250 ms y la entrada se leia instantanea.
  intro.to(chars, { yPercent: 0, duration: 1.0, ease: "power3.out", stagger: 0.075 }, 0.25);
  intro.to(fading, { opacity: 1, y: 0, duration: 0.9, ease: "power2.out", stagger: 0.14 }, 1.5);

  const exit = gsap.timeline({
    scrollTrigger: {
      id: HERO_ZOOM_TRIGGER_ID,
      trigger: hero,
      start: "top top",
      end: "+=150%",
      pin: true,
      scrub: 1,
    },
  });
  // El acompanamiento se va primero: si todo se arrastra a la vez, se ve roto.
  exit.to(fading, { opacity: 0, y: -30, ease: "none", duration: 0.28 }, 0);
  // fromTo, no to(): el valor de partida va escrito a mano, no leido del DOM.
  exit.fromTo(
    name,
    { scale: 1, opacity: 1 },
    { scale: 9, opacity: 0, ease: "power2.in", duration: 1 },
    0.12,
  );
}

/** Ids fijos de los ScrollTrigger del gesto 2: permiten matarlos si la funcion se re-ejecuta. */
const ABOUT_TRIGGER_IDS = ["vice-about-card", "vice-about-lines", "vice-about-stats", "vice-about-track"];

/** Gesto 2 — Subtitulado: la ficha entra y las lineas suben encadenadas. */
function scene2Card(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const about = root.querySelector<HTMLElement>('[data-scene="about"]');
  if (!about) return;

  // Defensivo, igual que en `scene1Title`: si esta funcion se llamara dos
  // veces no dejar triggers huerfanos ni relleno de pin duplicado.
  for (const id of ABOUT_TRIGGER_IDS) ScrollTrigger.getById(id)?.kill();

  const base = { trigger: about, start: "top 78%", toggleActions: "play none none reverse" } as const;
  const card = about.querySelector<HTMLElement>("[data-card]");
  const lines = Array.from(about.querySelectorAll<HTMLElement>("[data-line] > *"));
  const stats = about.querySelector<HTMLElement>("[data-stats]");
  const track = about.querySelector<HTMLElement>("[data-track]");

  if (card) {
    gsap.from(card, {
      x: -34,
      opacity: 0,
      duration: 0.9,
      ease: "power3.out",
      scrollTrigger: { ...base, id: ABOUT_TRIGGER_IDS[0] },
    });
  }
  gsap.from(lines, {
    yPercent: 105,
    opacity: 0,
    duration: 0.85,
    ease: "power3.out",
    stagger: 0.12,
    scrollTrigger: { ...base, id: ABOUT_TRIGGER_IDS[1] },
  });
  if (stats) {
    gsap.from(stats, {
      y: 16,
      opacity: 0,
      duration: 0.8,
      ease: "power2.out",
      delay: 0.35,
      scrollTrigger: { ...base, id: ABOUT_TRIGGER_IDS[2] },
    });
  }
  if (track) {
    gsap.from(track, {
      y: 18,
      opacity: 0,
      duration: 0.9,
      ease: "power2.out",
      delay: 0.5,
      scrollTrigger: { ...base, id: ABOUT_TRIGGER_IDS[3] },
    });
  }
}

/** Ids fijos del gesto 3, parametrizados por indice: puede haber varias escenas de obra. */
function obraTriggerIds(index: number): string[] {
  return [
    `vice-obra-ord-${index}`,
    `vice-obra-title-${index}`,
    `vice-obra-lead-${index}`,
    `vice-obra-meta-${index}`,
    `vice-obra-mask-${index}`,
    `vice-obra-gallery-${index}`,
  ];
}

/** Gesto 3 — Cartela: el ordinal cae, el titulo aterriza seco, el texto barre. */
function scene3Slate(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  root.querySelectorAll<HTMLElement>('[data-scene="obra"]').forEach((scene, index) => {
    const ids = obraTriggerIds(index);
    // Defensivo, igual que en los gestos 1 y 2: matar triggers huerfanos si
    // esta funcion se re-ejecutara.
    for (const id of ids) ScrollTrigger.getById(id)?.kill();

    const trigger = {
      trigger: scene,
      start: "top 76%",
      toggleActions: "play none none reverse",
    } as const;
    const ordinal = scene.querySelector<HTMLElement>("[data-ord]");
    const title = scene.querySelector<HTMLElement>("[data-title]");
    const lead = scene.querySelector<HTMLElement>(".lead");
    const meta = scene.querySelector<HTMLElement>("[data-meta]");
    const masks = Array.from(scene.querySelectorAll<HTMLElement>("[data-mask]"));
    const gallery = scene.querySelector<HTMLElement>("[data-gallery]");

    if (ordinal) {
      gsap.from(ordinal, {
        y: -70,
        scale: 1.35,
        opacity: 0,
        duration: 0.7,
        ease: "expo.out",
        scrollTrigger: { ...trigger, id: ids[0] },
      });
    }
    if (title) {
      gsap.from(title, {
        y: 46,
        opacity: 0,
        duration: 0.7,
        ease: "expo.out",
        delay: 0.08,
        scrollTrigger: { ...trigger, id: ids[1] },
      });
    }
    if (lead) {
      gsap.from(lead, {
        y: 20,
        opacity: 0,
        duration: 0.6,
        ease: "power2.out",
        delay: 0.16,
        scrollTrigger: { ...trigger, id: ids[2] },
      });
    }
    if (meta) {
      gsap.from(meta, {
        y: 14,
        opacity: 0,
        duration: 0.6,
        ease: "power2.out",
        delay: 0.24,
        scrollTrigger: { ...trigger, id: ids[3] },
      });
    }
    // La mascara barre de izquierda a derecha, desfasada entre columnas.
    if (masks.length > 0) {
      gsap.from(masks, {
        clipPath: "inset(0 100% 0 0)",
        duration: 0.9,
        ease: "power3.out",
        stagger: 0.1,
        delay: 0.32,
        scrollTrigger: { ...trigger, id: ids[4] },
      });
    }
    if (gallery) {
      gsap.from(gallery, {
        y: 22,
        opacity: 0,
        duration: 0.8,
        ease: "power2.out",
        delay: 0.48,
        scrollTrigger: { ...trigger, id: ids[5] },
      });
    }
  });
}

/** Id fijo del gesto 4: permite matarlo si la funcion se re-ejecuta. */
const CREDITS_TRIGGER_ID = "vice-credits-roll";

/**
 * Gesto 4 — Creditos: ruedan al entrar y SE DETIENEN. Un rodillo perpetuo
 * seria imposible de usar (la seccion es interactiva: hover/foco cambian el
 * panel de detalle), asi que el ScrollTrigger solo dispara la entrada una
 * vez por scroll, `toggleActions` incluido — nunca un loop.
 */
function scene4Credits(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const roll = root.querySelector<HTMLElement>("[data-credit-roll]");
  if (!roll) return;

  // Defensivo, igual que en los gestos 1 a 3: matar el trigger huerfano si
  // esta funcion se re-ejecutara.
  ScrollTrigger.getById(CREDITS_TRIGGER_ID)?.kill();

  gsap.from(roll.children, {
    y: 34,
    opacity: 0,
    duration: 0.7,
    ease: "power3.out",
    stagger: 0.07,
    scrollTrigger: {
      id: CREDITS_TRIGGER_ID,
      trigger: roll,
      start: "top 80%",
      toggleActions: "play none none reverse",
    },
  });
}

/** Id fijo por escena: permite matar cada ScrollTrigger si la funcion se re-ejecuta. */
function chromeTriggerId(index: number): string {
  return `vice-chrome-${index}`;
}

/**
 * Gesto 5 — Recursos globales de lenguaje de cine: la barra de orientacion
 * dice donde estas, el letterbox entra solo durante la obra ("esto es la
 * pelicula") y el atenuador de fondo baja la luz fuera de hero/contacto para
 * que el texto largo de las secciones intermedias no compita con el video.
 */
function cinemaChrome(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const bars = Array.from(document.querySelectorAll<HTMLElement>("[data-letterbox]"));
  const now = document.querySelector<HTMLElement>(".rail-now");
  const dim = document.querySelector<HTMLElement>("[data-dim]");
  const scenes = Array.from(root.querySelectorAll<HTMLElement>("[data-scene]"));
  const labels: Record<string, string> = {
    hero: "Título",
    about: "Ficha",
    obra: "Cartela",
    credits: "Créditos",
    contacto: "Fundido",
  };
  /** Solo hero y contacto a plena luz; el resto atenuado para que el texto lea. */
  const brightScenes = new Set(["hero", "contacto"]);

  scenes.forEach((scene, index) => {
    // Defensivo, igual que en los gestos 1 a 4: matar el trigger huerfano si
    // esta funcion se re-ejecutara.
    ScrollTrigger.getById(chromeTriggerId(index))?.kill();

    const kind = scene.dataset.scene ?? "";
    ScrollTrigger.create({
      id: chromeTriggerId(index),
      trigger: scene,
      start: "top 50%",
      end: "bottom 50%",
      onToggle: (self) => {
        if (!self.isActive) return;
        if (now) {
          now.textContent = `${String(index + 1).padStart(2, "0")} · ${labels[kind] ?? ""}`;
        }
        // Las franjas entran solo durante la obra: dicen "esto es la pelicula".
        gsap.to(bars, { height: kind === "obra" ? "6.5vh" : "0vh", duration: 0.45, ease: "power3.out" });
        if (dim) {
          gsap.to(dim, {
            opacity: brightScenes.has(kind) ? 0 : 0.62,
            duration: 0.6,
            ease: "power2.out",
          });
        }
      },
    });
  });
}

export const viceChoreography: Choreography = ({ gsap, ScrollTrigger, root }) => {
  scene1Title(gsap, ScrollTrigger, root);
  scene2Card(gsap, ScrollTrigger, root);
  scene3Slate(gsap, ScrollTrigger, root);
  scene4Credits(gsap, ScrollTrigger, root);
  cinemaChrome(gsap, ScrollTrigger, root);
};
