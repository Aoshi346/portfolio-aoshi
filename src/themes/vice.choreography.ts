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

export const viceChoreography: Choreography = ({ gsap, ScrollTrigger, root }) => {
  scene1Title(gsap, ScrollTrigger, root);
};
